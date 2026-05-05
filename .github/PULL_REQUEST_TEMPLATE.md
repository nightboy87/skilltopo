## Summary

Describe the change in one or two sentences.

## Type of change

- [ ] Documentation
- [ ] Bug fix
- [ ] Routing or scoring behavior
- [ ] Metadata schema or validation
- [ ] Evaluation cases
- [ ] Integration example
- [ ] Packaging or CI

## Scope and safety checklist

- [ ] This change keeps keyword-first routing as the default.
- [ ] Semantic matching remains optional.
- [ ] This change does not execute skills or grant permissions.
- [ ] This change does not include private paths, credentials, tokens, private logs, private skill libraries, or proprietary prompts.
- [ ] Third-party content is synthetic, original, or explicitly licensed for inclusion.
- [ ] Safety warnings and attribution are not weakened.

## Verification

Run the relevant commands and paste the result summary:

```bash
pytest
skilltopo validate examples/skills
skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json
```

## Documentation

- [ ] README updated if user-facing behavior changed.
- [ ] README.zh-CN updated if user-facing behavior changed.
- [ ] docs updated if integration, metadata, or safety guidance changed.
- [ ] CHANGELOG updated if release-facing behavior changed.
