# SkillTopo

[中文说明](README.zh-CN.md)

**SkillTopo** is a lightweight, keyword-first skill routing and topology layer for file-based agent skill systems.

It helps an agent choose, rank, and compose reusable skills from explicit metadata, without requiring model training or a heavyweight runtime.

SkillTopo is designed for small-to-medium skill libraries, such as personal or team-level agent systems with tens or hundreds of skills. It is inspired by the scenario-skill graph idea from SkillSynth, but it intentionally avoids large-scale LLM-generated pre/postcondition inference in the default implementation.

## What it does

SkillTopo provides:

- keyword-first skill recommendation;
- optional `sentence-transformers` semantic matching;
- negative keyword filtering;
- dynamic thresholding for short and long queries;
- skill priority weighting;
- workflow-chain recommendation;
- skill metadata validation;
- evaluation metrics for routing quality;
- JSON output for integration with other agents;
- generic integration examples for Hermes-like, OpenClaw-like, and other file-based skill systems.

This repository does **not** include original skill content, private paths, private configuration, API keys, or real user skill libraries from third-party projects.

## Why keyword-first?

Pure semantic similarity is often too vague for skill routing. A query about paper reading and a query about code documentation may both look like document tasks to an embedding model, while they should route to different skills.

SkillTopo therefore uses this rule:

> Keywords are the main signal. Semantic similarity is optional assistance.

## Installation

```bash
pip install git+https://github.com/nightboy87/skilltopo.git
```

For semantic matching:

```bash
pip install "skilltopo[semantic] @ git+https://github.com/nightboy87/skilltopo.git"
```

For local development:

```bash
git clone https://github.com/nightboy87/skilltopo.git
cd skilltopo
pip install -e ".[dev]"
```

## Quick start

```bash
skilltopo recommend "code crashed" --skills examples/skills
```

JSON output:

```bash
skilltopo recommend "代码崩了" --skills examples/skills --json
```

Enable semantic matching:

```bash
skilltopo recommend "find papers about agent evaluation" \
  --skills examples/skills \
  --semantic \
  --json
```

Validate metadata:

```bash
skilltopo validate examples/skills
```

Run evaluation:

```bash
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```

Recommend a workflow chain:

```bash
skilltopo workflow "read and summarize an arxiv paper" --skills examples/skills --json
```

Export the skill topology graph:

```bash
skilltopo graph examples/skills --json
```

Generate a metadata template:

```bash
skilltopo template new-skill-name
```

## Scoring model

If keyword score > 0:

```text
final = 0.60 + min(keyword_weight_sum * 0.10, 0.30)
        + 0.05 * semantic_score
        + 0.05 * priority
```

If keyword score == 0:

```text
final = min(0.30 * semantic_score + 0.05 * priority, 0.35)
```

Dynamic threshold:

```text
short query  <= 6 characters: 0.25
medium query <= 15 characters: 0.20
long query    > 15 characters: 0.15
```

Semantic matching is disabled by default. If `--semantic` is used but `sentence-transformers` is unavailable or model loading fails, SkillTopo falls back to keyword-only routing.

## Skill metadata example

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

## Supported metadata sources

SkillTopo can load:

1. standalone `.yaml` / `.yml` files;
2. `SKILL.md` files with YAML frontmatter;
3. nested directories containing skill metadata.

For `SKILL.md`, SkillTopo looks for top-level fields first. It also supports nested metadata under:

```yaml
metadata:
  skilltopo:
    keywords: [...]
```

and a compatible fallback under:

```yaml
metadata:
  hermes:
    keywords: [...]
```

## Evaluation metrics

The evaluator reports:

- `accuracy_at_1`
- `precision_at_1`
- `precision_at_3`
- `mrr`
- `no_match_accuracy`
- `false_positive_rate`
- `unsafe_recommendation_rate`

## License and attribution

SkillTopo is released under the **Apache License 2.0**.

You may use, modify, redistribute, and use it commercially, but you must retain the copyright notice, license, and NOTICE attribution.

Copyright 2026 Emile Jiang (nightboy87).

## Project status

Current version: `v0.2.0-alpha`.

This is an alpha project. Do not use SkillTopo as the only safety layer before executing destructive, irreversible, external-sending, or production-changing actions.
