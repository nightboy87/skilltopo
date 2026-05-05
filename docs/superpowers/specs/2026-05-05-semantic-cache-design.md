# Semantic Cache Design

## Goal

Add a formal optional semantic cache feature for SkillTopo 0.2.1 without changing the default keyword-first routing behavior.

## Scope

SkillTopo core will provide a cache builder and cache reader for skill embeddings. It will not run a production embedding server, manage processes, pick ports, or execute host-agent skills. Local HTTP embedding service code belongs in `examples/integrations/hermes_like/` as a minimal, synthetic integration example.

## Architecture

- `src/skilltopo/semantic_cache.py` owns cache payload creation, JSON read/write, text hashing, and validation.
- `src/skilltopo/cli.py` exposes `skilltopo semantic-cache build`.
- `examples/integrations/hermes_like/` contains a minimal embedding server and tool wrapper that show how a Hermes-like Agent can call SkillTopo without private paths.
- Unit tests use deterministic fake embedding functions. They do not load `sentence-transformers`, keeping CI lightweight.

## Data Format

The cache JSON stores:

- schema version;
- model name;
- generated timestamp;
- skill count;
- per-skill name, semantic text hash, source path, and embedding vector.

The cache is invalid when the model changes, the skill count changes, or any skill semantic text hash changes.

## Testing

Tests cover deterministic cache building, JSON round trip, cache validation success, and invalidation after skill text changes.
