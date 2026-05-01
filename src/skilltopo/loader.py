from __future__ import annotations

from pathlib import Path
from typing import Any
import yaml
from .models import Skill

class SkillMetadataError(ValueError):
    pass

def _ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value]
    return [str(value)]

def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}

def _extract_frontmatter(text: str) -> dict[str, Any] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = idx
            break
    if end is None:
        return None
    data = yaml.safe_load("\n".join(lines[1:end])) or {}
    return data if isinstance(data, dict) else None

def _merge_nested_metadata(data: dict[str, Any]) -> dict[str, Any]:
    merged = dict(data)
    metadata = _ensure_dict(data.get("metadata"))
    nested = _ensure_dict(metadata.get("skilltopo")) or _ensure_dict(metadata.get("hermes"))
    for key, value in nested.items():
        merged.setdefault(key, value)
    return merged

def parse_skill(data: dict[str, Any], source_path: str | None = None) -> Skill:
    data = _merge_nested_metadata(data)
    name = str(data.get("name") or data.get("skill") or "").strip()
    description = str(data.get("description") or "").strip()
    if not name:
        raise SkillMetadataError(f"Missing required field 'name' in {source_path or '<memory>'}")
    if not description:
        raise SkillMetadataError(f"Missing required field 'description' in {source_path or name}")
    priority = max(0.0, min(1.0, float(data.get("priority", 0.5))))
    return Skill(
        name=name,
        description=description,
        keywords=_ensure_list(data.get("keywords")),
        keyword_weights={str(k): float(v) for k, v in _ensure_dict(data.get("keyword_weights")).items()},
        negative_keywords=_ensure_list(data.get("negative_keywords")),
        aliases=_ensure_list(data.get("aliases")),
        priority=priority,
        risk_level=str(data.get("risk_level", "low")),
        requires_confirmation=bool(data.get("requires_confirmation", False)),
        input_types=_ensure_list(data.get("input_types")),
        output_types=_ensure_list(data.get("output_types")),
        preconditions=_ensure_list(data.get("preconditions")),
        postconditions=_ensure_list(data.get("postconditions")),
        workflow_chains=[list(map(str, chain)) for chain in (data.get("workflow_chains") or [])],
        workflow_edges={str(k): _ensure_list(v) for k, v in _ensure_dict(data.get("workflow_edges")).items()},
        examples=_ensure_dict(data.get("examples")),
        source_path=source_path,
        raw=data,
    )

def load_skill_file(path: str | Path) -> Skill:
    p = Path(path)
    if p.name == "SKILL.md" or p.suffix.lower() == ".md":
        data = _extract_frontmatter(p.read_text(encoding="utf-8"))
        if data is None:
            raise SkillMetadataError(f"No YAML frontmatter found in {p}")
    else:
        loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if not isinstance(loaded, dict):
            raise SkillMetadataError(f"Expected YAML mapping in {p}")
        data = loaded
    return parse_skill(data, source_path=str(p))

def iter_skill_files(path: str | Path) -> list[Path]:
    p = Path(path)
    if p.is_file():
        return [p]
    files: list[Path] = []
    for pattern in ("*.yaml", "*.yml", "**/SKILL.md"):
        files.extend(sorted(p.glob(pattern)))
    seen, result = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result

def load_skills(path: str | Path) -> list[Skill]:
    skills, errors = [], []
    for file in iter_skill_files(path):
        try:
            skills.append(load_skill_file(file))
        except Exception as exc:
            errors.append(f"{file}: {exc}")
    if errors and not skills:
        raise SkillMetadataError("No valid skills loaded:\n" + "\n".join(errors))
    return skills

def validate_skills(path: str | Path) -> tuple[list[Skill], list[str]]:
    skills, errors, names = [], [], set()
    for file in iter_skill_files(path):
        try:
            skill = load_skill_file(file)
            if skill.name in names:
                errors.append(f"Duplicate skill name: {skill.name} ({file})")
            names.add(skill.name)
            if not skill.keywords:
                errors.append(f"Skill has no keywords: {skill.name} ({file})")
            if skill.risk_level not in {"low", "medium", "high", "critical"}:
                errors.append(f"Invalid risk_level for {skill.name}: {skill.risk_level}")
            skills.append(skill)
        except Exception as exc:
            errors.append(f"{file}: {exc}")
    return skills, errors
