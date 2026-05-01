# Hermes-like Integration

This document describes a generic integration pattern only. It does not assume any real Hermes path or include any original Hermes skill content.

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
