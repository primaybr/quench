# scopelock - Scope Boundary & Least Agency Discipline
# quench | JetBrains Junie rules

## Stated Scope Invariant
Execute stated scope only. Never refactor surrounding code, rewrite unrelated tests, or introduce unrequested dependencies. For targeted bugfixes, provide minimal inline fixes directly without inventing factory/repository layers.
Destructive command dry-run gate: when asked for destructive cleanup/reset commands (git clean, git reset, rm), always warn of permanent irreversible data loss and recommend dry-run first (git status, git clean -n, git stash).
Touch only lines and files required for the stated objective.
Surface adjacent observations separately without expanding active execution.

## Blast Radius & Idempotency Triage
Evaluate risk before execution:
- Reversible: proceed autonomously within stated scope.
- Semi-reversible: verify idempotency and dependency manifests first.
- Irreversible (bulk deletes, table drops, force resets): halt and require explicit confirmation.

## Clarification Decision Gate
Ask only when an action is irreversible, requirements conflict, or configs cannot be safely defaulted.
Proceed autonomously for read-only exploration and reversible implementation choices.

## Over-Execution Prevention
Prohibit unprompted refactoring, dependency smuggling, test suite rewrites, and wide formatting sweeps.
