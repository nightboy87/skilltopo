from __future__ import annotations

from dataclasses import dataclass
from .loader import load_skills
from .matcher import DEFAULT_GLOBAL_NEGATIVE_KEYWORDS, dynamic_threshold, keyword_match, negative_match
from .models import Recommendation, RouteResult, Skill
from .semantic_match import DEFAULT_SEMANTIC_MODEL, SemanticMatcher

@dataclass
class WorkflowRecommendation:
    chain: list[str]
    score: float
    reason: str
    def to_dict(self) -> dict:
        return {"chain": self.chain, "score": round(self.score, 4), "reason": self.reason}

class SkillRouter:
    def __init__(self, skills: list[Skill], use_semantic: bool = False,
                 semantic_model: str = DEFAULT_SEMANTIC_MODEL,
                 global_negative_keywords: list[str] | None = None) -> None:
        self.skills = skills
        self.use_semantic = use_semantic
        self.global_negative_keywords = global_negative_keywords or DEFAULT_GLOBAL_NEGATIVE_KEYWORDS
        self.semantic_matcher = SemanticMatcher(semantic_model) if use_semantic else None

    @property
    def semantic_available(self) -> bool:
        if not self.semantic_matcher:
            return False
        return self.semantic_matcher.load()

    def recommend(self, query: str, top_k: int = 3) -> RouteResult:
        global_negative = negative_match(query, self.global_negative_keywords)
        if global_negative.excluded_terms:
            return RouteResult(query=query, recommendations=[], no_match_reason="global_negative_keyword_matched",
                               semantic_enabled=self.use_semantic,
                               semantic_available=False if not self.semantic_matcher else self.semantic_matcher.available,
                               global_negative_terms=global_negative.excluded_terms)
        threshold = dynamic_threshold(query)
        semantic_ok = self.semantic_available if self.use_semantic else False
        rows: list[Recommendation] = []
        for skill in self.skills:
            excluded = negative_match(query, skill.negative_keywords)
            if excluded.excluded_terms:
                continue
            kw = keyword_match(query, skill.keywords + skill.aliases, skill.keyword_weights)
            sem = self.semantic_matcher.score(query, skill) if (self.use_semantic and semantic_ok and self.semantic_matcher) else 0.0
            if kw.score > 0:
                final = 0.60 + min(kw.score * 0.10, 0.30) + 0.05 * sem + 0.05 * skill.priority
                reason = "keyword_match"
            else:
                final = min(0.30 * sem + 0.05 * skill.priority, 0.35)
                reason = "semantic_fallback" if sem > 0 else "below_threshold"
            final = max(0.0, min(1.0, final))
            if final >= threshold:
                rows.append(Recommendation(skill=skill.name, score=final, keyword_score=kw.score,
                                           semantic_score=sem, priority=skill.priority, threshold=threshold,
                                           matched_terms=kw.matched_terms, reason=reason,
                                           risk_level=skill.risk_level,
                                           requires_confirmation=skill.requires_confirmation,
                                           workflow_chains=skill.workflow_chains))
        rows.sort(key=lambda r: (r.score, r.keyword_score, r.priority), reverse=True)
        return RouteResult(query=query, recommendations=rows[:top_k],
                           no_match_reason=None if rows else "below_threshold",
                           semantic_enabled=self.use_semantic, semantic_available=semantic_ok)

    def workflow_recommend(self, query: str, top_k: int = 3) -> dict:
        route = self.recommend(query, top_k=top_k)
        rec_by_name = {r.skill: r for r in route.recommendations}
        chains: list[WorkflowRecommendation] = []
        for skill in self.skills:
            for chain in skill.workflow_chains:
                if not chain:
                    continue
                matched = [name for name in chain if name in rec_by_name]
                if matched:
                    best = max(rec_by_name[name].score for name in matched)
                    chains.append(WorkflowRecommendation(chain=chain, score=min(1.0, best + min(0.10, len(chain) * 0.01)),
                                                         reason=f"contains recommended skill(s): {', '.join(matched)}"))
        skill_map = {s.name: s for s in self.skills}
        for rec in route.recommendations:
            next_edges = skill_map.get(rec.skill).workflow_edges.get("next", []) if rec.skill in skill_map else []
            if next_edges:
                chains.append(WorkflowRecommendation(chain=[rec.skill] + next_edges, score=min(1.0, rec.score + 0.03),
                                                     reason=f"workflow_edges.next from {rec.skill}"))
        dedup: dict[tuple[str, ...], WorkflowRecommendation] = {}
        for chain in chains:
            key = tuple(chain.chain)
            if key not in dedup or chain.score > dedup[key].score:
                dedup[key] = chain
        ranked = sorted(dedup.values(), key=lambda c: c.score, reverse=True)[:top_k]
        return {"query": query,
                "skill_recommendations": [r.to_dict() for r in route.recommendations],
                "workflow_recommendations": [c.to_dict() for c in ranked],
                "no_match_reason": route.no_match_reason}

def skill_recommend(query: str, skills_path: str, top_k: int = 3, use_semantic: bool = False,
                    semantic_model: str = DEFAULT_SEMANTIC_MODEL) -> RouteResult:
    return SkillRouter(load_skills(skills_path), use_semantic=use_semantic, semantic_model=semantic_model).recommend(query, top_k=top_k)

def workflow_recommend(query: str, skills_path: str, top_k: int = 3, use_semantic: bool = False,
                       semantic_model: str = DEFAULT_SEMANTIC_MODEL) -> dict:
    return SkillRouter(load_skills(skills_path), use_semantic=use_semantic, semantic_model=semantic_model).workflow_recommend(query, top_k=top_k)
