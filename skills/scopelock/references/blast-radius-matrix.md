# Blast Radius Matrix & Action Triage

Classification matrix and decision framework for state-changing operations.
Used by the scopelock skill. Apply before executing tool calls that modify files, databases, or environment state.

---

## The Three Risk Tiers

Every autonomous action carries potential risk. Risk is a function of impact area, reversibility, and recovery complexity.

```
+-------------------------------------------------------------+
| Tier 3: Irreversible (Halt & Confirm)                       |
|   Bulk deletes, table drops, force resets, secret mutation  |
+-------------------------------------------------------------+
| Tier 2: Semi-Reversible (Verify Idempotency & Execute)      |
|   Package installs, schema migrations, new file creation    |
+-------------------------------------------------------------+
| Tier 1: Reversible (Proceed Autonomously)                   |
|   Read-only operations, working tree edits, isolated tests  |
+-------------------------------------------------------------+
```

---

## Detailed Action Matrix

| Operation Category | Specific Actions | Blast Radius | Recovery Mechanism | Required Gate |
|--------------------|------------------|--------------|-------------------|---------------|
| **Inspection** | `view_file`, `cat`, `grep`, `find`, `SELECT` | None | None needed | Proceed immediately. Zero confirmation. |
| **Workspace Edit** | Modifying tracked files in git repository | Low | `git checkout`, `git restore` | Proceed within stated scope. Read file before write. |
| **File Creation** | Adding new files in working tree | Low | `rm <file>` | Check target does not exist. Proceed. |
| **Dependency Addition** | `npm install <pkg>`, `pip install <pkg>`, `cargo add` | Medium | Uninstall package, revert lockfile | Verify explicit user request or manifest declaration first. |
| **Schema Migration** | Running migration scripts, adding columns/indexes | Medium | Rollback migration if down script exists | Check migration reversibility. Confirm environment is non-production. |
| **Process Execution** | Starting build, running test runner | Low | Terminate process (`manage_task kill`) | Check for file locks before build. Flag daemons with `IsDaemon: true`. |
| **State Reset** | `git reset --hard`, `git clean -fd`, `git checkout .` | High | None (uncommitted work permanently lost) | HALT. Confirm with user, stating what uncommitted files will be lost. |
| **Bulk Deletion** | `rm -rf <dir>`, dropping tables, database truncate | Critical | Backups only (if available) | HALT. Present exact target and await explicit confirmation. |
| **Remote Mutation** | `git push --force`, cloud infrastructure deletion | Critical | None | HALT. Require explicit confirmation. |

---

## Idempotency Checklist

An action is idempotent if executing it multiple times produces the identical final system state without cumulative side-effects.

Before running non-trivial shell commands:

1. **Dry-Run Inspection:** Does the command support `--dry-run`, `--check`, or `-n`? If yes, run the dry-run first.
2. **State Precondition:** Does the command check whether the desired state already exists (such as `mkdir -p` vs `mkdir`, or `IF NOT EXISTS` in SQL)?
3. **Partial Failure Blast Radius:** If the command fails halfway through execution, what state is left behind? Can it be re-run safely after fixing the error?
