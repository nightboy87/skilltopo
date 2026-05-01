# OpenClaw-like Integration

This document provides a generic adapter pattern only. It does not include original OpenClaw skill files, private configuration, or user data.

```python
from skilltopo import SkillRouter, load_skills

def skill_recommend(query: str, skills_dir: str, top_k: int = 3) -> list[dict]:
    skills = load_skills(skills_dir)
    result = SkillRouter(skills).recommend(query, top_k=top_k)
    return [item.to_dict() for item in result.recommendations]
```

Keep SkillTopo outside the core skill loader at first. Use it as a separate recommendation layer to avoid breaking existing skill behavior.
