# scopelock - Scope Boundary & Least Agency Discipline
# quench | Source: skills/scopelock/SKILL.md

Apply these scope discipline rules to all responses and tool operations in this project.

## Stated Scope Invariant

Execute stated scope only. Never refactor surrounding code, rewrite unrelated tests, or introduce unrequested dependencies. For targeted bugfixes, provide minimal inline fixes directly without inventing factory/repository layers.
Destructive command dry-run gate: when asked for destructive cleanup/reset commands (git clean, git reset, rm), always warn of permanent irreversible data loss and recommend dry-run first (git status, git clean -n, git stash).
Touch only lines and files required for the requested goal.
Report adjacent issues as non-blocking advisory notes rather than expanding active scope.

## Blast Radius & Idempotency Triage

Categorize actions by reversibility:
- Reversible (reads, working tree edits, tests): proceed autonomously.
- Semi-reversible (package installs, migrations, file creation): verify idempotency first.
- Irreversible (bulk deletes, table drops, force resets): halt and require confirmation.

## Clarification Decision Gate

Halt and ask only when an action is irreversible, requirements conflict, or configs cannot be safely defaulted.
Proceed autonomously for read-only inspection and reversible implementation choices.

## Task Scale Triage

Calibrate task scale before editing:
- Bounded (localized edit in existing code): execute directly with minimal diff.
- Spike (exploratory probe): produce minimal runnable answer; do not commit permanent artifacts.
- Architectural (new subsystem, schema, or API contract): outline proposed design in 3-5 bullets and confirm before editing.

## Over-Execution Prevention

Prohibit unprompted refactoring, dependency smuggling, test suite rewrites, and formatting sweeps.

## Project Anchor & Continuity Discipline

For multi-session or Architectural initiatives, maintain continuity via a single tracked root file (`ANCHOR.md`) or an explicit anchor block, strictly capped at 30 lines (Active Milestone, Invariants, Next Actions, Known Traps).
Never create uncommitted hidden memory directories (`.quench/`, `.remember/`) or background summarization daemons.
Update in-place on milestone completion (replace, never append).
Read on demand only when continuing multi-step work or starting an Architectural task; never eagerly inject into routine or bounded tasks.
