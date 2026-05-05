# Hermes-like Integration

This document describes a generic integration pattern only. It does not assume any real Hermes path or include any original Hermes skill content.

For deeper semantic matching performance notes, see [Semantic matching optimization](semantic-matching-optimization.md).

For a runnable synthetic example, see [`examples/integrations/hermes_like`](../examples/integrations/hermes_like/README.md).

```python
import json
from skilltopo import SkillRouter, load_skills

def skill_recommend(query: str, skills_dir: str, top_k: int = 3) -> str:
    skills = load_skills(skills_dir)
    result = SkillRouter(skills, use_semantic=False).recommend(query, top_k=top_k)
    return json.dumps(result.to_dict(), ensure_ascii=False)
```

Recommended prompt rule:

> Before using a specialized skill, call `skill_recommend` with the user's task. Use the returned `matched_terms`, `score`, and `risk_level` to decide whether to open the full skill.

## Optional semantic cache

For host agents that call SkillTopo frequently, precompute skill embeddings:

```bash
skilltopo semantic-cache build \
  --skills examples/skills \
  --output .skilltopo/skill_embeddings.json \
  --json
```

Use that cache during recommendation:

```bash
skilltopo recommend "find papers about agent evaluation" \
  --skills examples/skills \
  --semantic \
  --semantic-cache .skilltopo/skill_embeddings.json \
  --json
```

This cache avoids recomputing every skill embedding. A query embedding still needs the semantic model or a host-provided embedding service. The command does not start a long-running service, execute skills, or grant permissions.
