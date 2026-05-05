# SkillTopo 语义匹配优化与 Agent 集成实践

本文整理一次把 SkillTopo 集成到 Hermes-like Agent（类 Hermes 智能体）环境时的语义匹配优化探索。它不是核心默认架构变更，而是一套可选集成模式，适合本地长期运行的 Agent（智能体）宿主。

SkillTopo 的默认原则不变：

> 关键词是主信号，语义匹配只是辅助信号。

## 适用场景

这套方案适合：

- 技能库规模达到几十到几百个技能；
- 用户输入经常是口语化表达；
- 宿主 Agent（智能体）会频繁调用技能推荐；
- 本地环境可以长期运行一个轻量 embedding（向量表示）服务；
- 团队愿意维护技能元数据、口语化关键词和 workflow_chains（工作流链）。

不适合：

- 每次调用都冷启动的短生命周期脚本；
- 只需要 keyword-only（仅关键词）匹配的小技能库；
- 不希望安装 `sentence-transformers` 的轻量部署；
- 需要把推荐结果直接当作执行授权的系统。

## 问题 1：subprocess JSON 传递 Unicode

在宿主 Agent（智能体）通过 subprocess（子进程）调用 Python 代码时，直接把 JSON（数据交换格式）拼进命令字符串，容易触发 Unicode（统一字符编码）转义问题。

错误示例：

```python
import json
import subprocess

data = {"query": "发文件到飞书"}
code = f"import json; data = json.loads('{json.dumps(data)}'); print(data)"
result = subprocess.run(["python3", "-c", code], capture_output=True)
```

更稳的做法是把 JSON payload（负载）先做 Base64（基础64编码）包装：

```python
import base64
import json

data = {"query": "发文件到飞书"}
encoded = base64.b64encode(json.dumps(data, ensure_ascii=False).encode("utf-8")).decode("ascii")

code = (
    "import base64, json; "
    f"data = json.loads(base64.b64decode('{encoded}').decode('utf-8'))"
)
```

结论：

- 不要把复杂 JSON 直接拼进 `python -c` 命令字符串。
- Base64（基础64编码）适合作为 subprocess（子进程）边界上的简单传输包装。
- 更好的长期方案是避免命令字符串传参，改用标准输入、临时文件或本地服务接口。

## 问题 2：语义匹配的冷启动成本

`sentence-transformers` 会加载 embedding（向量表示）模型。如果每个技能、每次请求都在 subprocess（子进程）里重新加载模型，性能会崩。

真实测试里还发现一个容易误判的问题：首次使用默认模型 `paraphrase-multilingual-MiniLM-L12-v2` 时，环境可能需要从 Hugging Face（模型托管平台）下载模型并加载权重。一次 Windows（视窗操作系统）隔离环境测试中，首次语义推荐耗时约 `400.9s`；模型已下载后的新进程加载仍可能需要几十秒；同一进程内热查询约 `0.06-0.10s`。

这不是 SkillTopo 卡死，而是语义模型下载和加载成本。使用者应该预期：

- 首次 `--semantic` 可能很慢；
- 无网络或 Hugging Face（模型托管平台）访问受限时，模型可能不可用；
- 想要稳定低延迟，应先构建语义缓存，并在宿主 Agent（智能体）里复用常驻进程或本地 embedding（向量表示）服务；
- 默认 keyword-only（仅关键词）模式不会触发模型下载。

一次探索中的现象：

| 方案 | 第一次查询 | 后续查询 | 主要问题 |
| --- | ---: | ---: | --- |
| 逐个计算 embedding（向量表示） | 约 1260 秒 | 约 1260 秒 | 模型反复加载 |
| 预计算缓存 + subprocess | 约 42 秒 | 约 13 秒 | 每次仍要加载查询模型 |
| 预计算缓存 + HTTP API | 约 15 秒 | 约 0.16 秒 | 需要维护本地服务 |

结论：

- 语义匹配不能靠短生命周期 subprocess（子进程）硬扛。
- 技能 embedding（向量表示）应该预计算并缓存。
- 查询 embedding（向量表示）应该由长期运行的本地服务计算。

## 推荐架构

```text
用户查询
  |
  v
SkillTopo 路由器
  |
  +-- keyword match（关键词匹配）
  |
  +-- semantic match（语义匹配）
        |
        v
     本地 embedding HTTP API（向量超文本传输接口）
        |
        v
     已加载的 sentence-transformers（句向量模型库）模型
        |
        v
     已缓存的技能 embeddings（向量表示）
```

职责拆分：

- SkillTopo core（核心）：加载技能元数据、关键词匹配、负向关键词过滤、动态阈值、排序、解释结果。
- Embedding service（向量服务）：保持模型常驻，只负责把文本转成 embedding（向量表示）。
- Cache builder（缓存构建器）：当技能元数据变更时，重新生成技能 embedding（向量表示）缓存。
- Host Agent（宿主智能体）：决定是否启用语义匹配，并在高风险技能前执行自己的确认策略。

## 正式缓存命令

SkillTopo 0.2.1 提供正式的语义缓存构建命令：

```bash
skilltopo semantic-cache build \
  --skills examples/skills \
  --output .skilltopo/skill_embeddings.json \
  --json
```

该命令会读取技能元数据，计算每个技能的 semantic_text（语义文本）hash（哈希值）和 embedding（向量表示），并写入 JSON（数据交换格式）缓存。

推荐时可以通过 `--semantic-cache` 使用这个缓存：

```bash
skilltopo recommend "find papers about agent evaluation" \
  --skills examples/skills \
  --semantic \
  --semantic-cache .skilltopo/skill_embeddings.json \
  --json
```

这样可以避免每次推荐都重新计算全部技能 embedding（向量表示）。但 query（查询）embedding（向量表示）仍然需要模型或宿主提供的 embedding（向量表示）服务。

它不会：

- 启动 HTTP API（超文本传输接口）服务；
- 管理端口或后台进程；
- 执行任何技能；
- 绕过宿主 Agent（智能体）的确认和权限策略。

本地常驻 embedding（向量表示）服务仍然只是集成示例，见 `examples/integrations/hermes_like/`。

## 本地 embedding 服务示例

这是示意代码，不是 SkillTopo 默认运行时。

```python
from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


@app.post("/embed")
def embed():
    texts = request.json["texts"]
    embeddings = model.encode(texts)
    return jsonify({"embeddings": embeddings.tolist()})


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": True})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
```

部署建议：

- 生产或长期本地环境优先使用 supervisor（进程管理器）、Docker（容器）或宿主系统服务。
- WSL（Windows 子系统 Linux）环境不一定支持 systemd（系统服务管理器），不要把 systemd 当成唯一方案。
- 健康检查可以存在，但不要在开源示例里写死个人路径、个人用户名或私有目录。

## 语义权重的边界

探索中发现，无关键词命中时，过低的语义权重会导致合理结果被动态阈值过滤。

原公式：

```text
final = min(0.30 * semantic_score + 0.05 * priority, 0.35)
```

探索公式：

```text
final = min(0.50 * semantic_score + 0.10 * priority, 0.60)
```

这不应该被理解为“语义权重永远设 50%”。更准确的结论是：

- keyword-only（仅关键词）是默认稳定路径；
- semantic（语义）适合提高口语化输入的召回；
- 无关键词命中时，语义分数必须足够高才有意义；
- 权重调整必须进入评估集，不能只凭几个正例改默认公式。

如果要把这个策略推进为 SkillTopo 正式能力，必须补充：

- 正例、负例、口语化查询和混淆查询；
- semantic on/off（语义开关）对比；
- false_positive_rate（误推荐率）变化；
- unsafe_recommendation_rate（高风险技能误推荐率）变化；
- README（说明文档）中的评分公式同步更新。

## workflow_chains 是显式经验

工作流推荐不是纯算法问题。比如“写一篇公众号文章”可能需要先做研究、翻译或创意构思，再进入写作技能。这个判断来自技能作者的实战经验，不能指望 embedding（向量表示）自动还原。

推荐元数据：

```yaml
name: article-writing
keywords: [写文章, 公众号文章, 长文, 内容创作]
workflow_chains:
  - [in-depth-research, article-writing]
  - [translation, article-writing]
  - [workflow-planning, article-writing]
```

结论：

- workflow_chains（工作流链）是把隐性经验外化成显性元数据。
- 没有 workflow_chains（工作流链），系统只能猜；猜错很正常。
- 技能作者应该为高频任务补充链路，而不是把全部压力交给语义相似度。

## 口语化关键词

用户通常不会说“请执行 creative-ideation 技能”。他们会说：

- 做个新项目
- 帮我整理一下思路
- 代码崩了
- 找一篇论文
- 写详细计划

技能元数据应该覆盖这些表达：

```yaml
name: creative-ideation
keywords: [ideation, 创意构思, 项目创意, 做个新项目, 新项目, 项目想法]
keyword_weights:
  ideation: 1.0
  做个新项目: 0.9
  新项目: 0.8
priority: 0.8
```

建议做法：

1. 从真实失败查询中提取口语化表达。
2. 把高频表达加入 `keywords`。
3. 给强触发表达配置 `keyword_weights`。
4. 把每个失败查询加入 evals（评估集）。
5. 每次改权重后重新运行评估。

## 与隐性知识的关系

从 Polanyi（波兰尼）的 Tacit Knowledge（隐性知识）视角看，技能路由系统里有两类知识。

显性知识：

- 技能名称；
- 关键词；
- 负向关键词；
- 优先级；
- 风险等级；
- 输入输出类型；
- workflow_chains（工作流链）；
- 评估用例。

隐性知识：

- 什么表达在真实任务里意味着某个技能；
- 哪些技能应该先后组合；
- 哪些相似输入其实不该路由到同一技能；
- 什么分数足以推荐，什么分数只适合提示；
- 高风险技能什么时候必须停下来确认。

隐性知识难以外化，是因为它依赖上下文、经验和失败反馈。解决办法不是把所有判断都交给 LLM（大语言模型），而是把可外化的部分持续沉淀为元数据和评估集。

可执行机制：

- 用 `keywords` 固化常见表达；
- 用 `negative_keywords` 固化误触发边界；
- 用 `workflow_chains` 固化技能组合经验；
- 用 `risk_level` 和 `requires_confirmation` 暴露风险；
- 用 evals（评估集）固化回归测试；
- 用 `matched_terms` 和 `reason` 暴露推荐解释。

## 开源边界

不要提交：

- 私有技能内容；
- 真实用户技能库；
- 本机绝对路径；
- 私有服务地址；
- API Key（接口密钥）；
- token（令牌）；
- 个人 cron（定时任务）标识；
- 第三方项目的原始技能文件。

可以提交：

- 合成技能示例；
- 通用适配器；
- 抽象部署说明；
- 不含私有路径的示例代码；
- 评估方法和指标；
- 失败案例的脱敏描述。

## 后续路线

短期：

1. 为 Hermes-like Agent（类 Hermes 智能体）补充通用集成文档。
2. 为高频示例技能补充 workflow_chains（工作流链）。
3. 扩展口语化中文查询评估集。
4. 对比 keyword-only（仅关键词）和 semantic（语义）模式的评估指标。

中期：

1. 增加可选 embedding cache（向量缓存）构建命令。
2. 增加本地 embedding HTTP API（向量超文本传输接口）示例。
3. 增加缓存失效策略，例如基于技能元数据 hash（哈希值）。
4. 在文档中明确语义服务不是默认依赖。

长期：

1. 自动从失败查询中生成候选关键词。
2. 为 workflow_chains（工作流链）提供覆盖率检查。
3. 为高风险技能增加更严格的评估维度。
4. 提供多宿主 Agent（智能体）集成示例。
