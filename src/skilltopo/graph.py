from __future__ import annotations
from .models import Skill

def build_graph(skills: list[Skill]) -> dict:
    nodes = [{"id": s.name, "description": s.description, "risk_level": s.risk_level, "priority": s.priority} for s in skills]
    edges, seen = [], set()
    for skill in skills:
        for target in skill.workflow_edges.get("next", []):
            key = (skill.name, target, "next")
            if key not in seen:
                seen.add(key); edges.append({"source": skill.name, "target": target, "type": "next"})
        for chain in skill.workflow_chains:
            for source, target in zip(chain, chain[1:]):
                key = (source, target, "chain")
                if key not in seen:
                    seen.add(key); edges.append({"source": source, "target": target, "type": "chain"})
    return {"nodes": nodes, "edges": edges}
