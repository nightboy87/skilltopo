from __future__ import annotations
import json
from skilltopo import SkillRouter, load_skills

def recommend_for_agent(query: str, skills_dir: str, top_k: int = 3, semantic: bool = False) -> str:
    skills = load_skills(skills_dir)
    result = SkillRouter(skills, use_semantic=semantic).recommend(query, top_k=top_k)
    return json.dumps(result.to_dict(), ensure_ascii=False)
