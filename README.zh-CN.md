# SkillTopo

[English README](README.md)

**SkillTopo** 是一个面向文件化 Agent（智能体）技能系统的轻量级技能路由与技能拓扑层。

它的目标不是替代 Agent，也不是做一个复杂训练系统，而是帮助 Agent 在一组可复用技能中更稳地完成：选哪个技能、技能如何排序、哪些技能可以组成工作流、哪些输入不应该触发技能、推荐结果是否可解释和可回归测试。

这个项目适合小到中等规模的技能库，比如个人或团队维护的几十到几百个技能。它借鉴了 SkillSynth 论文里的“场景-技能图”思想，但默认实现不依赖大规模 LLM（大语言模型）推断，也不需要训练。

## 这个项目包含什么

SkillTopo 提供：

- 关键词优先的技能推荐；
- 可选的 `sentence-transformers` 语义匹配；
- 负向关键词过滤；
- 短查询 / 长查询动态阈值；
- 技能优先级加权；
- 技能链 / 工作流推荐；
- 技能元数据校验；
- 推荐效果评估指标；
- 方便其他 Agent 集成的 JSON 输出；
- 面向 Hermes/OpenClaw 类系统的通用集成示例。

这个仓库**不包含**任何第三方项目的原始技能内容、本地路径结构、私有配置、API Key（接口密钥）或真实用户技能库。

## 为什么是“关键词优先”

纯语义匹配看起来高级，但在技能路由里经常不稳。

例如，“读论文”和“看代码文档”在语义向量里都可能像“文档处理”，但它们应该进入完全不同的技能。

所以 SkillTopo 的基本原则是：

> 关键词是主信号，语义匹配只是辅助信号。

## 安装

基础安装：

```bash
pip install git+https://github.com/nightboy87/skilltopo.git
```

如果要启用语义匹配：

```bash
pip install "skilltopo[semantic]"
```

本地开发：

```bash
git clone https://github.com/nightboy87/skilltopo.git
cd skilltopo
pip install -e ".[dev]"
```

## 快速使用

推荐技能：

```bash
skilltopo recommend "代码崩了" --skills examples/skills
```

输出 JSON：

```bash
skilltopo recommend "代码崩了" --skills examples/skills --json
```

启用语义匹配：

```bash
skilltopo recommend "帮我找几篇关于 Agent 评估的论文" \
  --skills examples/skills \
  --semantic \
  --json
```

校验技能元数据：

```bash
skilltopo validate examples/skills
```

运行评估集：

```bash
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```

推荐技能链：

```bash
skilltopo workflow "读一篇论文并整理成知识卡片" --skills examples/skills --json
```

导出技能拓扑图：

```bash
skilltopo graph examples/skills --json
```

生成技能元数据模板：

```bash
skilltopo template new-skill-name
```

## 推荐算法

如果命中关键词：

```text
final = 0.60 + min(关键词权重总和 * 0.10, 0.30)
        + 0.05 * 语义分数
        + 0.05 * 技能优先级
```

如果没有命中关键词：

```text
final = min(0.30 * 语义分数 + 0.05 * 技能优先级, 0.35)
```

动态阈值：

```text
短查询  <= 6 字符：0.25
中等查询 <= 15 字符：0.20
长查询   > 15 字符：0.15
```

语义匹配默认关闭。只有传入 `--semantic` 才会启用。如果用户没有安装 `sentence-transformers`，或模型加载失败，系统会自动降级为纯关键词匹配。

## 技能元数据示例

```yaml
name: systematic-debugging
description: Diagnose code, runtime, test, and environment failures.
keywords: [debug, error, crash, 代码, 报错, 崩了, 跑不起来]
keyword_weights:
  debug: 1.0
  error: 0.9
  crash: 0.9
  代码: 0.6
  报错: 1.0
  崩了: 1.0
  跑不起来: 1.0
negative_keywords: [food delivery, song, 外卖, 歌曲]
priority: 0.8
risk_level: medium
requires_confirmation: false
preconditions:
  - The user reports an error, crash, failed test, or runtime failure.
postconditions:
  - A root cause, next diagnostic step, or fix plan is produced.
workflow_edges:
  next: [code-review, test-runner]
```

## 支持哪些技能来源

SkillTopo 可以读取：

1. 独立的 `.yaml` / `.yml` 技能元数据文件；
2. 带 YAML frontmatter（前置元数据）的 `SKILL.md`；
3. 包含多个技能文件的嵌套目录。

对于 `SKILL.md`，SkillTopo 会优先读取顶层字段，也支持：

```yaml
metadata:
  skilltopo:
    keywords: [...]
```

同时提供兼容性兜底：

```yaml
metadata:
  hermes:
    keywords: [...]
```

## 评估指标

内置评估器会输出：

- `accuracy_at_1`：第一推荐命中率；
- `precision_at_1`：Top 1 精确率；
- `precision_at_3`：Top 3 精确率；
- `mrr`：平均倒数排名；
- `no_match_accuracy`：无技能场景识别正确率；
- `false_positive_rate`：误推荐率；
- `unsafe_recommendation_rate`：高风险技能误推荐率。

## 开源协议和作者标注

SkillTopo 使用 **Apache License 2.0（阿帕奇许可证 2.0）**。

你可以修改、分发、商用，但必须保留版权声明、许可证和 NOTICE 文件中的作者来源标注。

作者：**nightboy87 / Emile Jiang**  
Copyright 2026 Emile Jiang (nightboy87)

## 项目状态

当前版本：`v0.2.0-alpha`。

这是 alpha（早期）版本。它适合作为技能路由和技能拓扑管理的基础层，但不要把它当成执行危险操作前的唯一安全措施。对于删除文件、发送外部消息、审批、付款、改生产数据等高风险行为，必须额外加入人工确认和权限控制。
