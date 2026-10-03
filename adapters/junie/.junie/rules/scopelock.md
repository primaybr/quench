# scopelock - Scope Boundary & Least Agency Discipline
# quench | JetBrains Junie rules

## Stated Scope Invariant
Execute stated scope only. Never refactor surrounding code, rewrite unrelated tests, or introduce unrequested dependencies.
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
