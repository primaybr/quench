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

## Over-Execution Prevention

Prohibit unprompted refactoring, dependency smuggling, test suite rewrites, and formatting sweeps.
