# Release Checklist

Before publishing:

- [ ] Confirm repository URL is `https://github.com/nightboy87/skilltopo` or update it.
- [ ] Confirm author name is `nightboy87 / Emile Jiang`.
- [ ] Run `pytest`.
- [ ] Run `skilltopo validate examples/skills`.
- [ ] Run `skilltopo eval evals/skilltopo_50_seed.yaml --skills examples/skills --json`.
- [ ] Confirm no private paths, API keys, or third-party original skill content exist.
- [ ] Create GitHub repository.
- [ ] Push initial commit.
- [ ] Tag `v0.2.1`.
