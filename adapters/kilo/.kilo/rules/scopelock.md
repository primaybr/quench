# scopelock - Scope Boundary & Least Agency Discipline
# quench | Source: skills/scopelock/SKILL.md

## Stated Scope Invariant

Execute stated scope only. Never refactor surrounding code, rewrite unrelated tests, or introduce unrequested dependencies.
Touch only lines and files required for the requested goal.
Surface adjacent issues as separate advisory observations; do not expand the active changeset unprompted.

## Blast Radius & Idempotency Triage

Categorize state mutations before execution:
- Reversible: proceed autonomously within stated scope.
- Semi-reversible: verify idempotency and dependency manifests before running.
- Irreversible (bulk deletions, table drops, force resets): halt and require explicit confirmation.

## Clarification Decision Gate

Ask for clarification only when actions are irreversible, requirements conflict fundamentally, or required configs cannot be safely defaulted.
Proceed autonomously for read-only exploration and reversible edits.

## Over-Execution Prevention

Prohibit unprompted refactoring, dependency smuggling, test suite rewrites, and wide formatting sweeps.
