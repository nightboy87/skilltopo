from __future__ import annotations

import hashlib
import math
from typing import Iterable
from .models import Skill

DEFAULT_SEMANTIC_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

class SemanticUnavailable(RuntimeError):
    pass

class SemanticMatcher:
    """Lazy sentence-transformers wrapper. Optional by design."""

    def __init__(self, model_name: str = DEFAULT_SEMANTIC_MODEL) -> None:
        self.model_name = model_name
        self._model = None
        self._cache: dict[str, list[float]] = {}
        self.available = False
        self.error: str | None = None

    def load(self) -> bool:
        if self._model is not None:
            return True
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            self._model = SentenceTransformer(self.model_name)
            self.available = True
            return True
        except Exception as exc:  # pragma: no cover
            self.error = str(exc)
            self.available = False
            return False

    def _key(self, text: str) -> str:
        return hashlib.sha256((self.model_name + "\0" + text).encode("utf-8")).hexdigest()

    def embed(self, text: str) -> list[float]:
        if not self.load():
            raise SemanticUnavailable(self.error or "sentence-transformers is unavailable")
        key = self._key(text)
        if key not in self._cache:
            vector = self._model.encode(text, normalize_embeddings=True)  # type: ignore[union-attr]
            self._cache[key] = [float(x) for x in vector]
        return self._cache[key]

    @staticmethod
    def cosine(a: Iterable[float], b: Iterable[float]) -> float:
        av, bv = list(a), list(b)
        dot = sum(x * y for x, y in zip(av, bv))
        na = math.sqrt(sum(x * x for x in av))
        nb = math.sqrt(sum(y * y for y in bv))
        if na == 0 or nb == 0:
            return 0.0
        return max(0.0, min(1.0, (dot / (na * nb) + 1.0) / 2.0))

    def score(self, query: str, skill: Skill) -> float:
        try:
            return self.cosine(self.embed(query), self.embed(skill.semantic_text()))
        except SemanticUnavailable:
            return 0.0
