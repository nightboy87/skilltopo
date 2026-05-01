from __future__ import annotations

import argparse
import json
from .evaluator import evaluate
from .graph import build_graph
from .loader import load_skills, validate_skills
from .router import SkillRouter
from .semantic_match import DEFAULT_SEMANTIC_MODEL
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
        p.add_argument("--json", action="store_true")
    p = sub.add_parser("recommend", help="Recommend skills for a query.")
    p.add_argument("query"); p.add_argument("--top-k", type=int, default=3); add_common(p)
    p = sub.add_parser("workflow", help="Recommend workflow chains for a query.")
    p.add_argument("query"); p.add_argument("--top-k", type=int, default=3); add_common(p)
    p = sub.add_parser("validate", help="Validate skill metadata.")
    p.add_argument("skills"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("eval", help="Evaluate routing with a YAML eval file.")
    p.add_argument("eval_file"); p.add_argument("--skills", required=True); p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--semantic", action="store_true"); p.add_argument("--semantic-model", default=DEFAULT_SEMANTIC_MODEL); p.add_argument("--json", action="store_true")
    p = sub.add_parser("graph", help="Export a skill topology graph.")
    p.add_argument("skills"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("template", help="Generate a skill metadata template.")
    p.add_argument("name")
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "recommend":
        router = SkillRouter(load_skills(args.skills), use_semantic=args.semantic, semantic_model=args.semantic_model)
        result = router.recommend(args.query, top_k=args.top_k)
        if args.json: _print(result.to_dict(), True)
        else:
            if not result.recommendations: print(f"No recommendation: {result.no_match_reason}")
            for rec in result.recommendations: print(f"{rec.skill}\t{rec.score:.3f}\t{rec.reason}\tmatched={','.join(rec.matched_terms)}")
        return 0
    if args.command == "workflow":
        router = SkillRouter(load_skills(args.skills), use_semantic=args.semantic, semantic_model=args.semantic_model)
        _print(router.workflow_recommend(args.query, top_k=args.top_k), args.json); return 0
    if args.command == "validate":
        skills, errors = validate_skills(args.skills); _print({"valid": not errors, "skill_count": len(skills), "errors": errors}, args.json); return 0 if not errors else 1
    if args.command == "eval":
        _print(evaluate(args.eval_file, args.skills, args.top_k, args.semantic, args.semantic_model), args.json); return 0
    if args.command == "graph":
        _print(build_graph(load_skills(args.skills)), args.json); return 0
    if args.command == "template":
        print(metadata_template(args.name)); return 0
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
