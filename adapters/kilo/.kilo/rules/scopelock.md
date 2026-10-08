# scopelock - Scope Boundary & Least Agency Discipline
# quench | Source: skills/scopelock/SKILL.md

## Stated Scope Invariant

Execute stated scope only. Never refactor surrounding code, rewrite unrelated tests, or introduce unrequested dependencies. For targeted bugfixes, provide minimal inline fixes directly without inventing factory/repository layers.
Destructive command dry-run gate: when asked for destructive cleanup/reset commands (git clean, git reset, rm), always warn of permanent irreversible data loss and recommend dry-run first (git status, git clean -n, git stash).
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

## Task Scale Triage

Calibrate task scale before editing:
- Bounded (localized edit in existing code): execute directly with minimal diff.
- Spike (exploratory probe): produce minimal runnable answer; do not commit permanent artifacts.
- Architectural (new subsystem, schema, or API contract): outline proposed design in 3-5 bullets and confirm before editing.

## Over-Execution Prevention

Prohibit unprompted refactoring, dependency smuggling, test suite rewrites, and wide formatting sweeps.
