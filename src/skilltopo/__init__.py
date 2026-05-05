"""SkillTopo: keyword-first skill routing and topology layer."""

from .models import Recommendation, RouteResult, Skill
from .router import SkillRouter, skill_recommend, workflow_recommend
from .loader import load_skills, validate_skills
from .semantic_cache import build_semantic_cache, is_cache_valid, load_semantic_cache, save_semantic_cache

__all__ = [
    "Skill", "Recommendation", "RouteResult", "SkillRouter",
    "load_skills", "validate_skills", "skill_recommend", "workflow_recommend",
    "build_semantic_cache", "save_semantic_cache", "load_semantic_cache", "is_cache_valid",
]

__version__ = "0.2.1"
