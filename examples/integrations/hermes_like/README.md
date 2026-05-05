# Hermes-like Integration Example

This directory contains a minimal, synthetic example for connecting SkillTopo to a Hermes-like Agent host.

It intentionally does not include:

- real Hermes configuration;
- private skill libraries;
- local machine paths;
- credentials, tokens, or API keys;
- copied third-party skill content.

## Build a semantic cache

```bash
skilltopo semantic-cache build \
  --skills examples/skills \
  --output .skilltopo/skill_embeddings.json \
  --json
```

The cache stores skill semantic text hashes and embedding vectors. Rebuild it whenever skill metadata changes.

## Run the optional embedding server

```bash
pip install "skilltopo[semantic]" flask
python examples/integrations/hermes_like/embedding_server.py
```

The server exposes:

- `GET /health`
- `POST /embed` with `{"texts": ["query text"]}`

## Call SkillTopo from a host tool

```bash
python examples/integrations/hermes_like/skilltopo_tool.py \
  --query "code crashed" \
  --skills examples/skills \
  --json
```

For direct SkillTopo CLI usage with a cache:

```bash
skilltopo recommend "find papers about agent evaluation" \
  --skills examples/skills \
  --semantic \
  --semantic-cache .skilltopo/skill_embeddings.json \
  --json
```

Use this as a host-agent adapter pattern, not as an execution permission layer. The host Agent remains responsible for confirmation, permissions, and safety checks.
