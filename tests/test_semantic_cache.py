from __future__ import annotations

from pathlib import Path

from skilltopo import cli
from skilltopo.loader import load_skills
from skilltopo import semantic_cache
from skilltopo.router import SkillRouter
from skilltopo.semantic_cache import (
    build_semantic_cache,
    is_cache_valid,
    load_semantic_cache,
    save_semantic_cache,
)
from skilltopo.semantic_match import SemanticUnavailable


def fake_embed(text: str) -> list[float]:
    return [float(len(text)), float(sum(ord(ch) for ch in text) % 997)]


def test_build_semantic_cache_uses_skill_semantic_text():
    skills = load_skills("examples/skills")

    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)

    assert cache["schema_version"] == 1
    assert cache["model_name"] == "fake-model"
    assert cache["skill_count"] == len(skills)
    assert set(cache["skills"]) == {skill.name for skill in skills}
    first = skills[0]
    assert cache["skills"][first.name]["embedding"] == fake_embed(first.semantic_text())
    assert len(cache["skills"][first.name]["text_hash"]) == 64


def test_semantic_cache_round_trip(tmp_path: Path):
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)
    output = tmp_path / "skill_embeddings.json"

    save_semantic_cache(cache, output)
    loaded = load_semantic_cache(output)

    assert loaded == cache
    assert is_cache_valid(loaded, skills, model_name="fake-model")


def test_semantic_cache_invalidates_when_skill_text_changes(tmp_path: Path):
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)

    changed = list(skills)
    changed[0].description = changed[0].description + " changed"

    assert not is_cache_valid(cache, changed, model_name="fake-model")


def test_semantic_cache_invalidates_when_model_changes():
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)

    assert not is_cache_valid(cache, skills, model_name="other-model")


def test_semantic_cache_cli_builds_cache(tmp_path: Path, monkeypatch):
    def fake_build(skills, model_name, embed_fn=None):
        return build_semantic_cache(skills, model_name=model_name, embed_fn=fake_embed)

    monkeypatch.setattr(semantic_cache, "build_semantic_cache", fake_build)
    monkeypatch.setattr(cli, "build_semantic_cache", fake_build)
    output = tmp_path / "cache.json"

    exit_code = cli.main([
        "semantic-cache",
        "build",
        "--skills",
        "examples/skills",
        "--output",
        str(output),
        "--semantic-model",
        "fake-model",
        "--json",
    ])

    assert exit_code == 0
    cache = load_semantic_cache(output)
    assert cache["model_name"] == "fake-model"
    assert cache["skill_count"] == len(load_skills("examples/skills"))


def test_semantic_cache_cli_reports_missing_optional_dependency(tmp_path: Path, monkeypatch, capsys):
    def fake_build(skills, model_name, embed_fn=None):
        raise SemanticUnavailable("sentence-transformers is unavailable")

    monkeypatch.setattr(cli, "build_semantic_cache", fake_build)
    output = tmp_path / "cache.json"

    exit_code = cli.main([
        "semantic-cache",
        "build",
        "--skills",
        "examples/skills",
        "--output",
        str(output),
    ])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Install semantic support" in captured.err
    assert not output.exists()


def test_router_uses_cached_skill_embeddings(tmp_path: Path):
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)
    output = tmp_path / "cache.json"
    save_semantic_cache(cache, output)

    router = SkillRouter(
        skills,
        use_semantic=True,
        semantic_model="fake-model",
        semantic_cache_path=str(output),
        semantic_query_embed_fn=fake_embed,
    )

    result = router.recommend("zzzzzzzzzz", top_k=3)

    assert result.semantic_enabled is True
    assert result.semantic_available is True
    assert result.recommendations
    assert all(rec.semantic_score > 0 for rec in result.recommendations)


def test_router_disables_invalid_semantic_cache(tmp_path: Path):
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)
    first_name = next(iter(cache["skills"]))
    cache["skills"][first_name]["text_hash"] = "invalid"
    output = tmp_path / "cache.json"
    save_semantic_cache(cache, output)

    router = SkillRouter(
        skills,
        use_semantic=True,
        semantic_model="fake-model",
        semantic_cache_path=str(output),
        semantic_query_embed_fn=fake_embed,
    )

    result = router.recommend("zzzzzzzzzz", top_k=3)

    assert result.semantic_enabled is True
    assert result.semantic_available is False
    assert result.recommendations == []


def test_cli_recommend_accepts_semantic_cache(tmp_path: Path, monkeypatch, capsys):
    skills = load_skills("examples/skills")
    cache = build_semantic_cache(skills, model_name="fake-model", embed_fn=fake_embed)
    output = tmp_path / "cache.json"
    save_semantic_cache(cache, output)

    monkeypatch.setattr("skilltopo.semantic_cache.default_embed_fn", lambda model_name: fake_embed)

    exit_code = cli.main([
        "recommend",
        "zzzzzzzzzz",
        "--skills",
        "examples/skills",
        "--semantic",
        "--semantic-model",
        "fake-model",
        "--semantic-cache",
        str(output),
        "--json",
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"semantic_available": true' in captured.out
    assert '"semantic_score":' in captured.out
