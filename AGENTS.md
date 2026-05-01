# AGENTS.md

## Project overview

SkillTopo is a lightweight, keyword-first skill routing and skill topology layer for file-based agent skill systems.

It helps agents select, rank, explain, and compose reusable skills from explicit metadata.

SkillTopo is designed for small-to-medium personal or team skill libraries, especially systems where skills are stored as local files with metadata, such as Markdown-based skill folders, YAML skill definitions, or similar agent skill libraries.

SkillTopo is not a full agent framework, not a permission system, and not a replacement for host-agent safety checks.

Author: Emile Jiang (nightboy87)  
Project homepage: https://github.com/nightboy87/skilltopo  
License: Apache License 2.0

---

## Core design principles

1. Keyword-first routing is the default.
2. Semantic matching is optional.
3. Skill metadata should be explicit, inspectable, and version-controlled.
4. Recommendation results should be explainable.
5. Risk information should be surfaced, not hidden.
6. Skill routing should stay separate from host-agent execution.
7. The project must remain lightweight by default.
8. The repository must not include private skills, private paths, secrets, or copied third-party skill content.

---

## What this project does

SkillTopo provides:

- skill recommendation from natural language queries;
- keyword-first matching;
- optional semantic matching through `sentence-transformers`;
- negative keyword filtering;
- dynamic thresholding;
- skill priority weighting;
- risk metadata;
- workflow chain recommendation;
- skill graph export;
- metadata validation;
- evaluation commands;
- JSON output for agent integration;
- generic integration examples for Hermes-like, OpenClaw-like, and other file-based agent skill systems.

---

## What this project does not do

SkillTopo does not:

- execute skills;
- grant permissions;
- replace human confirmation;
- replace a host agent's safety layer;
- manage secrets;
- connect to private services by default;
- include third-party original skill files;
- include real user skill libraries;
- include private local paths;
- include copied Hermes/OpenClaw/Claude Code skill content.

---

## Repository boundaries

This repository may include:

- SkillTopo source code;
- synthetic example skills;
- metadata schema examples;
- evaluation fixtures;
- generic adapter examples;
- documentation;
- tests;
- release notes.

This repository must not include:

- API keys;
- tokens;
- passwords;
- private endpoints;
- internal company paths;
- real user skill libraries;
- copied third-party original skill contents;
- copied host-agent private configurations;
- local machine-specific configuration;
- production data;
- private logs;
- proprietary prompts;
- non-redistributable model files.

When adding examples, use synthetic examples only.

---

## Installation

Basic install:

```bash
pip install skilltopo
```

Local development install:

```bash
pip install -e ".[dev]"
```

Install optional semantic matching support:

```bash
pip install -e ".[semantic]"
```

The default installation should remain lightweight and should not require `sentence-transformers`, `torch`, or model downloads.

---

## Common CLI commands

Recommend skills:

```bash
skilltopo recommend "代码崩了" --skills examples/skills --json
```

Recommend skills with optional semantic matching:

```bash
skilltopo recommend "帮我找几篇关于 Agent 评估的论文" --skills examples/skills --semantic --json
```

Validate skill metadata:

```bash
skilltopo validate examples/skills
```

Run the seed evaluation set:

```bash
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```

Recommend workflow chains:

```bash
skilltopo workflow "读一篇论文并整理成知识卡片" --skills examples/skills --json
```

Export skill topology graph:

```bash
skilltopo graph examples/skills --json
```

---

## Development checks

Before changing routing logic, matching logic, metadata loading, workflow recommendation, or evaluation code, run:

```bash
pytest
skilltopo validate examples/skills
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```

Changes to scoring behavior should update:

- tests;
- evaluation expectations if needed;
- README examples if output behavior changes;
- metadata schema documentation if fields change;
- changelog entries.

Do not silently change routing behavior without tests.

---

## Routing behavior

The core routing policy is:

1. Apply negative keyword filtering first.
2. Match explicit keywords and trigger terms.
3. Apply keyword weights.
4. Add optional semantic score only when semantic mode is enabled.
5. Add skill priority as a small ranking signal.
6. Apply dynamic thresholds based on query length.
7. Return top-k recommendations with explanation fields.
8. Surface risk metadata and confirmation requirements.

Keyword matching should remain the primary signal.

Semantic matching should assist recall, not dominate explicit keyword routing.

---

## Semantic matching policy

Semantic matching is optional.

Do not make `sentence-transformers` a hard dependency unless the project intentionally changes its default installation policy.

When semantic matching is unavailable, SkillTopo should gracefully fall back to keyword-only routing.

Semantic mode must not require network access after model dependencies are available locally.

---

## Metadata guidance

Skill metadata should be explicit and readable.

A skill may include fields such as:

- `name`
- `description`
- `aliases`
- `keywords`
- `keyword_weights`
- `negative_keywords`
- `priority`
- `risk_level`
- `requires_confirmation`
- `input_types`
- `output_types`
- `preconditions`
- `postconditions`
- `workflow_chains`
- `workflow_edges`
- `examples`

Prefer small, maintainable metadata over large opaque prompts.

Do not add metadata fields that cannot be validated or explained.

---

## Risk and safety rules

SkillTopo is not a permission system.

Do not treat a recommendation as authorization to execute a skill.

Host agents must apply their own safety checks before execution.

High-risk or irreversible actions must require explicit user confirmation.

Examples of high-risk actions include:

- deleting files;
- modifying production systems;
- sending external messages;
- making payments;
- approving workflows;
- accessing credentials;
- exposing secrets;
- changing master data;
- touching privacy-sensitive records;
- running destructive shell commands.

SkillTopo may surface `risk_level` and `requires_confirmation`, but the host agent remains responsible for enforcement.

---

## Integration guidance for agents

Use SkillTopo as a separate recommendation layer.

Recommended integration flow:

1. Load local skill metadata.
2. Pass the user query to SkillTopo.
3. Inspect returned `recommendations`.
4. Review `score`, `matched_terms`, `reason`, `risk_level`, and `requires_confirmation`.
5. Select a skill or workflow candidate.
6. Apply host-agent safety policy.
7. Ask for user confirmation when needed.
8. Load or execute the selected skill through the host agent's own mechanism.

Do not modify a host agent's core skill loader as the first integration step.

Prefer a standalone adapter or wrapper.

---

## Expected JSON output usage

Agents should prefer `--json` output for integration.

Recommended fields to inspect:

- `query`
- `recommendations`
- `skill`
- `score`
- `matched_terms`
- `reason`
- `risk_level`
- `requires_confirmation`
- `workflow`
- `no_match_reason`

Do not rely on human-readable CLI output for automated integration.

---

## Testing expectations

Unit tests should cover:

- keyword matching;
- negative keyword filtering;
- dynamic thresholds;
- priority scoring;
- metadata loading;
- metadata validation;
- workflow chain recommendation;
- CLI JSON output;
- evaluation metrics.

Evaluation sets should include:

- positive examples;
- negative examples;
- ambiguous queries;
- colloquial Chinese queries;
- English queries;
- workflow queries;
- safety-sensitive queries.

Do not claim broad accuracy from a small seed evaluation set.

Use wording such as "seed evaluation" or "internal test set" unless a larger benchmark is added.

---

## Documentation expectations

When changing user-facing behavior, update relevant documentation:

- `README.md`
- `README.zh-CN.md`
- `docs/`
- examples
- changelog

Documentation should be clear enough for both humans and code agents.

Keep installation, CLI usage, metadata examples, integration examples, and safety boundaries easy to find.

---

## Coding style

Keep the project simple.

Prefer readable Python over clever abstractions.

Avoid unnecessary dependencies.

Avoid framework lock-in.

Keep core logic independent from Hermes, OpenClaw, Claude Code, or any specific host agent.

Adapters should be examples, not hard dependencies.

---

## License and attribution

SkillTopo is released under Apache License 2.0.

Commercial use, modification, distribution, and private use are allowed under the license terms.

Copyright, license, and NOTICE attribution must be retained.

Do not remove attribution to:

Emile Jiang (nightboy87)

Project homepage:

https://github.com/nightboy87/skilltopo

---

## Instructions for code agents modifying this repository

Before editing:

1. Read `README.md`.
2. Read `README.zh-CN.md` if Chinese context is needed.
3. Read this `AGENTS.md`.
4. Inspect `examples/skills`.
5. Inspect `evals/skilltopo_50_seed.yaml`.
6. Run tests after changes.

When modifying:

1. Keep default mode keyword-only.
2. Keep semantic mode optional.
3. Do not add private paths or private data.
4. Do not add copied third-party skill contents.
5. Do not weaken attribution requirements.
6. Do not remove safety warnings.
7. Do not expand project scope into a full agent framework.
8. Do not make destructive execution part of SkillTopo core.

After modifying:

1. Run `pytest`.
2. Run metadata validation.
3. Run the seed evaluation.
4. Update documentation if behavior changes.
5. Keep release notes accurate.

Recommended verification commands:

```bash
pytest
skilltopo validate examples/skills
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```
