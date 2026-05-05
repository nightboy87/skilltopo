from __future__ import annotations

import argparse
import json
import sys
from .evaluator import evaluate
from .graph import build_graph
from .loader import load_skills, validate_skills
from .router import SkillRouter
from .semantic_cache import build_semantic_cache, save_semantic_cache
from .semantic_match import DEFAULT_SEMANTIC_MODEL, SemanticUnavailable
from .templates import metadata_template

def _print(data, as_json: bool = False) -> None:
    if as_json or not isinstance(data, str):
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skilltopo", description="Keyword-first skill routing and topology layer.")
    sub = parser.add_subparsers(dest="command", required=True)
    def add_common(p):
        p.add_argument("--skills", required=True, help="Path to a skill metadata file or directory.")
        p.add_argument("--semantic", action="store_true", help="Enable optional sentence-transformers semantic matching.")
        p.add_argument("--semantic-model", default=DEFAULT_SEMANTIC_MODEL)
        p.add_argument("--semantic-cache", help="Path to a precomputed semantic cache JSON file.")
        p.add_argument("--json", action="store_true")
    p = sub.add_parser("recommend", help="Recommend skills for a query.")
    p.add_argument("query"); p.add_argument("--top-k", type=int, default=3); add_common(p)
    p = sub.add_parser("workflow", help="Recommend workflow chains for a query.")
    p.add_argument("query"); p.add_argument("--top-k", type=int, default=3); add_common(p)
    p = sub.add_parser("validate", help="Validate skill metadata.")
    p.add_argument("skills"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("eval", help="Evaluate routing with a YAML eval file.")
    p.add_argument("eval_file"); p.add_argument("--skills", required=True); p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--semantic", action="store_true"); p.add_argument("--semantic-model", default=DEFAULT_SEMANTIC_MODEL)
    p.add_argument("--semantic-cache", help="Path to a precomputed semantic cache JSON file.")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("graph", help="Export a skill topology graph.")
    p.add_argument("skills"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("template", help="Generate a skill metadata template.")
    p.add_argument("name")
    p = sub.add_parser("semantic-cache", help="Build or inspect optional semantic matching caches.")
    cache_sub = p.add_subparsers(dest="semantic_cache_command", required=True)
    p = cache_sub.add_parser("build", help="Build a semantic embedding cache for skill metadata.")
    p.add_argument("--skills", required=True, help="Path to a skill metadata file or directory.")
    p.add_argument("--output", required=True, help="Output cache JSON path.")
    p.add_argument("--semantic-model", default=DEFAULT_SEMANTIC_MODEL)
    p.add_argument("--json", action="store_true")
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "recommend":
        router = SkillRouter(
            load_skills(args.skills),
            use_semantic=args.semantic,
            semantic_model=args.semantic_model,
            semantic_cache_path=args.semantic_cache,
        )
        result = router.recommend(args.query, top_k=args.top_k)
        if args.json: _print(result.to_dict(), True)
        else:
            if not result.recommendations: print(f"No recommendation: {result.no_match_reason}")
            for rec in result.recommendations: print(f"{rec.skill}\t{rec.score:.3f}\t{rec.reason}\tmatched={','.join(rec.matched_terms)}")
        return 0
    if args.command == "workflow":
        router = SkillRouter(
            load_skills(args.skills),
            use_semantic=args.semantic,
            semantic_model=args.semantic_model,
            semantic_cache_path=args.semantic_cache,
        )
        _print(router.workflow_recommend(args.query, top_k=args.top_k), args.json); return 0
    if args.command == "validate":
        skills, errors = validate_skills(args.skills); _print({"valid": not errors, "skill_count": len(skills), "errors": errors}, args.json); return 0 if not errors else 1
    if args.command == "eval":
        _print(
            evaluate(
                args.eval_file,
                args.skills,
                args.top_k,
                args.semantic,
                args.semantic_model,
                args.semantic_cache,
            ),
            args.json,
        ); return 0
    if args.command == "graph":
        _print(build_graph(load_skills(args.skills)), args.json); return 0
    if args.command == "template":
        print(metadata_template(args.name)); return 0
    if args.command == "semantic-cache":
        if args.semantic_cache_command == "build":
            skills = load_skills(args.skills)
            try:
                cache = build_semantic_cache(skills, model_name=args.semantic_model)
            except SemanticUnavailable as exc:
                print(
                    "Semantic cache build requires optional semantic support. "
                    "Install semantic support with: pip install \"skilltopo[semantic]\". "
                    f"Reason: {exc}",
                    file=sys.stderr,
                )
                return 2
            save_semantic_cache(cache, args.output)
            summary = {
                "cache_path": args.output,
                "model_name": cache["model_name"],
                "skill_count": cache["skill_count"],
                "schema_version": cache["schema_version"],
            }
            _print(summary, args.json); return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
