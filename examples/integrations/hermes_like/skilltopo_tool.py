from __future__ import annotations

import argparse
import json

from skilltopo import SkillRouter, load_skills


def recommend(query: str, skills: str, top_k: int = 3, semantic: bool = False) -> dict:
    router = SkillRouter(load_skills(skills), use_semantic=semantic)
    return router.recommend(query, top_k=top_k).to_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description="Minimal Hermes-like SkillTopo adapter.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--skills", required=True)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--semantic", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = recommend(args.query, args.skills, args.top_k, args.semantic)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for rec in result["recommendations"]:
            print(f"{rec['skill']}\t{rec['score']}\t{rec['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
