# Metadata Schema

Required fields:

```yaml
name: string
description: string
```

Recommended fields:

```yaml
keywords: list[string]
keyword_weights: map[string, float]
negative_keywords: list[string]
aliases: list[string]
priority: float # 0.0 - 1.0
risk_level: low | medium | high | critical
requires_confirmation: bool
input_types: list[string]
output_types: list[string]
preconditions: list[string]
postconditions: list[string]
workflow_chains: list[list[string]]
workflow_edges:
  next: list[string]
examples:
  positive:
    - query: string
      expected: string
  negative:
    - query: string
      expected: null
```

## Weighting guidance

- Core intent words: `1.0`
- Strong synonyms: `0.8 - 0.9`
- Supporting words: `0.6 - 0.7`
- Broad generic words: `0.4 - 0.6`

Avoid giving generic words too much weight. For example, `code` or `文件` can appear in many different skills.
