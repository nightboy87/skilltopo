from __future__ import annotations

def metadata_template(name: str) -> str:
    return f"""name: {name}
description: Describe what this skill does and when it should be used.

keywords:
  - keyword-one
  - keyword-two
  - 中文关键词

keyword_weights:
  keyword-one: 1.0
  keyword-two: 0.8
  中文关键词: 1.0

negative_keywords:
  - unrelated query
  - 无关词

aliases: []
priority: 0.5
risk_level: low
requires_confirmation: false
input_types: []
output_types: []
preconditions:
  - Describe when this skill is applicable.
postconditions:
  - Describe the expected state after the skill is used.
workflow_chains: []
workflow_edges:
  next: []
examples:
  positive:
    - query: "example user query"
      expected: {name}
  negative:
    - query: "unrelated user query"
      expected: null
"""
