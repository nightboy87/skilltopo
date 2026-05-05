from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Any

from .models import Skill
from .semantic_match import DEFAULT_SEMANTIC_MODEL, SemanticMatcher, SemanticUnavailable

SCHEMA_VERSION = 1
EmbeddingFn = Callable[[str], list[float]]


def semantic_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def default_embed_fn(model_name: str = DEFAULT_SEMANTIC_MODEL) -> EmbeddingFn:
    matcher = SemanticMatcher(model_name)

    def embed(text: str) -> list[float]:
        try:
            return matcher.embed(text)
        except SemanticUnavailable:
            raise

    return embed


def build_semantic_cache(
    skills: list[Skill],
    model_name: str = DEFAULT_SEMANTIC_MODEL,
    embed_fn: EmbeddingFn | None = None,
) -> dict[str, Any]:
    embed = embed_fn or default_embed_fn(model_name)
    rows: dict[str, dict[str, Any]] = {}
    for skill in skills:
        text = skill.semantic_text()
        rows[skill.name] = {
            "text_hash": semantic_text_hash(text),
            "source_path": skill.source_path,
            "embedding": [float(x) for x in embed(text)],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "model_name": model_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skills),
        "skills": rows,
    }


def save_semantic_cache(cache: dict[str, Any], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def load_semantic_cache(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Semantic cache must be a JSON object.")
    return data


def is_cache_valid(
    cache: dict[str, Any],
    skills: list[Skill],
    model_name: str = DEFAULT_SEMANTIC_MODEL,
) -> bool:
    if cache.get("schema_version") != SCHEMA_VERSION:
        return False
    if cache.get("model_name") != model_name:
        return False
    if cache.get("skill_count") != len(skills):
        return False
    cached_skills = cache.get("skills")
    if not isinstance(cached_skills, dict):
        return False
    for skill in skills:
        row = cached_skills.get(skill.name)
        if not isinstance(row, dict):
            return False
        if row.get("text_hash") != semantic_text_hash(skill.semantic_text()):
            return False
        embedding = row.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            return False
    return True


class CachedSemanticMatcher:
    """Semantic matcher that reuses cached skill embeddings."""

    def __init__(
        self,
        skills: list[Skill],
        cache_path: str | Path,
        model_name: str = DEFAULT_SEMANTIC_MODEL,
        query_embed_fn: EmbeddingFn | None = None,
    ) -> None:
        self.skills = skills
        self.cache_path = Path(cache_path)
        self.model_name = model_name
        self.query_embed_fn = query_embed_fn or default_embed_fn(model_name)
        self.available = False
        self.error: str | None = None
        self._cache: dict[str, Any] | None = None
        self._query_cache: dict[str, list[float]] = {}

    def load(self) -> bool:
        if self._cache is not None:
            return self.available
        try:
            cache = load_semantic_cache(self.cache_path)
            if not is_cache_valid(cache, self.skills, self.model_name):
                self.error = "semantic cache is missing, stale, or built for a different model"
                self.available = False
                self._cache = cache
                return False
            self._cache = cache
            self.available = True
            return True
        except Exception as exc:
            self.error = str(exc)
            self.available = False
            self._cache = {}
            return False

    def embed_query(self, query: str) -> list[float]:
        if query not in self._query_cache:
            self._query_cache[query] = [float(x) for x in self.query_embed_fn(query)]
        return self._query_cache[query]

    def score(self, query: str, skill: Skill) -> float:
        if not self.load() or not self._cache:
            return 0.0
        row = self._cache["skills"].get(skill.name)
        if not isinstance(row, dict):
            return 0.0
        embedding = row.get("embedding")
        if not isinstance(embedding, list):
            return 0.0
        return SemanticMatcher.cosine(self.embed_query(query), [float(x) for x in embedding])
