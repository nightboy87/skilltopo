# Design Notes

SkillTopo is built around a practical constraint: small-to-medium agent skill systems do not need the full cost of large-scale skill graph construction.

The default design is:

1. explicit skill metadata;
2. keyword-first matching;
3. optional semantic assistance;
4. negative keyword filtering;
5. dynamic thresholds;
6. workflow edges and workflow chains;
7. evaluation as a first-class feature.

## Why not pure semantic matching?

Pure semantic matching can confuse different skills that share broad domains, such as papers, documents, code files, and summaries. SkillTopo keeps semantic matching as an optional assistive signal, not the primary signal.

## Why workflow chains?

The project is inspired by the idea that agent execution can be viewed as scenario-skill-scenario transitions. In this lightweight implementation, scenario nodes are represented by explicit `preconditions` and `postconditions`, while skill composition is represented by `workflow_edges` and `workflow_chains`.

## Scope

SkillTopo is a router and topology helper. It is not an execution sandbox, permission system, replacement for human approval, or full agent framework.
