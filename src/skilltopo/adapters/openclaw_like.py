"""Generic OpenClaw-like integration example. No real paths or original skill content included."""
from __future__ import annotations
from skilltopo import SkillRouter, load_skills

def skill_recommend(query: str, skills_dir: str, top_k: int = 3, semantic: bool = False) -> list[dict]:
    skills = load_skills(skills_dir)
    result = SkillRouter(skills, use_semantic=semantic).recommend(query, top_k=top_k)
    return [r.to_dict() for r in result.recommendations]
