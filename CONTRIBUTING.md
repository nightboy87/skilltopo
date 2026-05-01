# Contributing

Contributions are welcome, but this project has a strict scope:

- Do not submit private skill libraries.
- Do not submit API keys, private paths, tokens, logs, or credentials.
- Do not copy original skill files from third-party projects unless you have explicit rights to do so.
- Prefer synthetic examples that demonstrate metadata structure and routing behavior.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Adding test cases

Add cases under `evals/`:

```yaml
test_cases:
  - query: "代码崩了"
    expected: systematic-debugging
```

Use `expected: null` for queries that should not route to any skill.
