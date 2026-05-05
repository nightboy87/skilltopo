# Changelog

## v0.2.1

- Added public documentation for semantic matching optimization and Hermes-like Agent integration lessons.
- Documented subprocess JSON Unicode handling, embedding cache patterns, local HTTP embedding service boundaries, semantic scoring risks, workflow_chains usage, and colloquial keyword coverage.
- Added formal `skilltopo semantic-cache build` command for optional skill embedding cache generation.
- Added semantic cache read/write/validation helpers, cached router usage, CLI `--semantic-cache`, and tests.
- Added a synthetic Hermes-like integration example with a minimal embedding server and adapter tool.
- Added Code of Conduct, GitHub issue templates, and pull request template for healthier open source collaboration.
- Updated README documentation links and project version metadata.
- Kept semantic matching optional and keyword-first routing as the default project policy.

## v0.2.0-alpha

- Added real optional semantic matching via `sentence-transformers`.
- Implemented the keyword-first hybrid scoring formula from the exploration notes.
- Added dynamic thresholds for short, medium, and long queries.
- Added negative keyword filtering and global negative rules.
- Added workflow-chain recommendation.
- Added metadata template generation.
- Added `SKILL.md` frontmatter loading.
- Added 50-case seed evaluation set.
- Added bilingual README files.
- Updated attribution to nightboy87 / Emile Jiang.

## v0.1.0-alpha

- Initial clean repository skeleton.
- Keyword-only routing.
- Metadata validation.
- Basic CLI and integration examples.
