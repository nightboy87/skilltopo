# Security Policy

SkillTopo is a routing and metadata tool. It is not a sandbox, permission system, or final safety layer.

Do not rely on SkillTopo alone before executing:

- file deletion;
- external sending;
- approvals;
- payments;
- credential access;
- production system changes;
- privacy-sensitive operations.

Recommended production pattern:

1. route skill;
2. inspect skill risk level;
3. require confirmation for high-risk skills;
4. enforce external permission checks;
5. log routing and execution decisions.
