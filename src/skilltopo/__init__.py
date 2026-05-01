"""SkillTopo: keyword-first skill routing and topology layer."""

from .models import Recommendation, RouteResult, Skill
from .router import SkillRouter, skill_recommend, workflow_recommend
from .loader import load_skills, validate_skills

__all__ = [
    "Skill", "Recommendation", "RouteResult", "SkillRouter",
    "load_skills", "validate_skills", "skill_recommend", "workflow_recommend",
]

__version__ = "0.2.0-alpha"
