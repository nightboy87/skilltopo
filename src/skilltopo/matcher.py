from __future__ import annotations

import re
from .models import KeywordMatch

DEFAULT_GLOBAL_NEGATIVE_KEYWORDS = [
    "外卖", "订餐", "点餐", "歌曲", "音乐", "播放音乐",
    "food delivery", "order food", "song", "music",
]

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())

def query_length(query: str) -> int:
    return len(re.sub(r"\s+", "", query or ""))

def dynamic_threshold(query: str) -> float:
    n = query_length(query)
    if n <= 6:
        return 0.25
    if n <= 15:
        return 0.20
    return 0.15

def _find_non_overlapping_terms(query: str, terms: list[str]) -> list[str]:
    q = normalize_text(query)
    selected: list[tuple[int, int, str]] = []
    for term in sorted(set(t for t in terms if t), key=lambda x: len(x), reverse=True):
        t = normalize_text(term)
        start = q.find(t)
        if start < 0:
            continue
        end = start + len(t)
        if any(not (end <= s or start >= e) for s, e, _ in selected):
            continue
        selected.append((start, end, term))
    selected.sort(key=lambda item: item[0])
    return [term for _, _, term in selected]

def matched_terms(query: str, terms: list[str]) -> list[str]:
    return _find_non_overlapping_terms(query, terms)

def keyword_match(query: str, keywords: list[str], keyword_weights: dict[str, float] | None = None) -> KeywordMatch:
    weights = keyword_weights or {}
    hits = matched_terms(query, keywords)
    score = 0.0
    for term in hits:
        score += float(weights.get(term, weights.get(normalize_text(term), 1.0)))
    return KeywordMatch(score=score, matched_terms=hits)

def negative_match(query: str, negative_keywords: list[str]) -> KeywordMatch:
    hits = matched_terms(query, negative_keywords)
    return KeywordMatch(score=float(len(hits)), excluded_terms=hits)
