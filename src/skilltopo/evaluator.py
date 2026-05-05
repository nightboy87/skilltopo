from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from .loader import load_skills
from .router import SkillRouter

@dataclass
class EvalCaseResult:
    query: str
    expected: str | None
    predicted: str | None
    rank: int | None
    passed: bool
    recommendations: list[str]
    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

def load_eval_cases(path: str | Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    cases = data.get("test_cases", data if isinstance(data, list) else [])
    if not isinstance(cases, list):
        raise ValueError("Eval file must contain a 'test_cases' list")
    return cases

def evaluate(eval_path: str | Path, skills_path: str | Path, top_k: int = 3,
             use_semantic: bool = False, semantic_model: str | None = None,
             semantic_cache_path: str | None = None) -> dict[str, Any]:
    router = SkillRouter(load_skills(skills_path), use_semantic=use_semantic,
                         semantic_model=semantic_model or "paraphrase-multilingual-MiniLM-L12-v2",
                         semantic_cache_path=semantic_cache_path)
    cases = load_eval_cases(eval_path)
    results: list[EvalCaseResult] = []
    false_positive = no_match_total = no_match_correct = unsafe_recommendation = 0
    reciprocal_sum = 0.0
    p1_sum = p3_sum = 0
    for case in cases:
        query = str(case.get("query", ""))
        expected_raw = case.get("expected")
        expected = None if expected_raw in (None, "null", "None", "") else str(expected_raw)
        route = router.recommend(query, top_k=top_k)
        names = [r.skill for r in route.recommendations]
        predicted = names[0] if names else None
        rank = names.index(expected) + 1 if expected in names else None
        passed = (predicted == expected) if expected is not None else (predicted is None)
        if expected is None:
            no_match_total += 1
            if predicted is None:
                no_match_correct += 1
            else:
                false_positive += 1
                if route.recommendations and route.recommendations[0].risk_level in {"high", "critical"}:
                    unsafe_recommendation += 1
        else:
            if predicted == expected:
                p1_sum += 1
            if expected in names[:3]:
                p3_sum += 1
            if rank:
                reciprocal_sum += 1.0 / rank
        results.append(EvalCaseResult(query, expected, predicted, rank, passed, names))
    n = len(results) or 1
    positives = sum(1 for r in results if r.expected is not None) or 1
    metrics = {
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "accuracy_at_1": sum(1 for r in results if r.passed) / n,
        "precision_at_1": p1_sum / positives,
        "precision_at_3": p3_sum / positives,
        "mrr": reciprocal_sum / positives,
        "no_match_accuracy": (no_match_correct / no_match_total) if no_match_total else None,
        "false_positive_rate": (false_positive / no_match_total) if no_match_total else None,
        "unsafe_recommendation_rate": (unsafe_recommendation / no_match_total) if no_match_total else None,
        "semantic_enabled": use_semantic,
        "semantic_available": router.semantic_available if use_semantic else False,
    }
    return {"metrics": metrics, "cases": [r.to_dict() for r in results]}
