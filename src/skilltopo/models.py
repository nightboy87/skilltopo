from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Skill:
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    keyword_weights: dict[str, float] = field(default_factory=dict)
    negative_keywords: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    priority: float = 0.5
    risk_level: str = "low"
    requires_confirmation: bool = False
    input_types: list[str] = field(default_factory=list)
    output_types: list[str] = field(default_factory=list)
    preconditions: list[str] = field(default_factory=list)
    postconditions: list[str] = field(default_factory=list)
    workflow_chains: list[list[str]] = field(default_factory=list)
    workflow_edges: dict[str, list[str]] = field(default_factory=dict)
    examples: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    source_path: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def semantic_text(self) -> str:
        parts: list[str] = [self.name, self.description]
        parts.extend(self.aliases)
        parts.extend(self.keywords)
        parts.extend(self.input_types)
        parts.extend(self.output_types)
        parts.extend(self.preconditions)
        parts.extend(self.postconditions)
        for rows in self.examples.values():
            for row in rows or []:
                q = row.get("query") if isinstance(row, dict) else None
                if q:
                    parts.append(str(q))
        return "\n".join(str(p) for p in parts if p)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class KeywordMatch:
    score: float
    matched_terms: list[str] = field(default_factory=list)
    excluded_terms: list[str] = field(default_factory=list)

@dataclass
class Recommendation:
    skill: str
    score: float
    keyword_score: float
    semantic_score: float
    priority: float
    threshold: float
    matched_terms: list[str] = field(default_factory=list)
    reason: str = ""
    risk_level: str = "low"
    requires_confirmation: bool = False
    workflow_chains: list[list[str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for key in ("score", "keyword_score", "semantic_score", "priority", "threshold"):
            data[key] = round(float(data[key]), 4)
        return data

@dataclass
class RouteResult:
    query: str
    recommendations: list[Recommendation] = field(default_factory=list)
    no_match_reason: str | None = None
    semantic_enabled: bool = False
    semantic_available: bool = False
    global_negative_terms: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "recommendations": [r.to_dict() for r in self.recommendations],
            "no_match_reason": self.no_match_reason,
            "semantic_enabled": self.semantic_enabled,
            "semantic_available": self.semantic_available,
            "global_negative_terms": self.global_negative_terms,
        }
