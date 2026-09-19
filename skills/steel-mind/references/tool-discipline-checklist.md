# Tool Discipline Checklist

Pre-flight checklist for tool operations that modify state.
Used by the steel-mind skill. Apply before any write, execute, or delete.

---

## Pre-Operation Checklist

### Before ANY File Write

- [ ] Have I read the current file content in this session?
- [ ] Am I writing a new file or overwriting an existing one?
- [ ] If overwriting: is the overwrite intentional and scoped to the minimum necessary change?
- [ ] Is the target path correct for the operating system (separators, encoding)?
- [ ] Will the file encoding be correct? (UTF-8 no BOM for most text files)
- [ ] Will the line endings be correct? (LF for scripts/Linux targets)
- [ ] If this is an executable or script: is the file unlocked (not currently running)?

### Before Running a Command

- [ ] Is there a `--dry-run`, `--check`, or `-n` flag available? If yes, use it first.
- [ ] Is the working directory (`Cwd`) correct?
- [ ] Will this command modify files, databases, or external services?
- [ ] Is the command idempotent? (Safe to run twice if it fails midway?)
- [ ] If it spawns a long-running process: is `IsDaemon: true` set?
- [ ] What is the expected output - and what does failure look like?

### Before a Delete Operation

- [ ] Have I verified what will be deleted (exact paths/records)?
- [ ] Is there a backup or is this operation recoverable?
- [ ] Have I checked for dependencies (foreign keys, file references, imports)?
- [ ] Is the blast radius acceptable (how many things break if this is wrong)?

### Before a Database Migration or Schema Change

- [ ] Has the migration been reviewed for reversibility?
- [ ] Is there a down/rollback migration?
- [ ] Are any `NOT NULL` columns being added to tables with existing data?
- [ ] Will this lock tables and affect running queries?
- [ ] Is the test environment tested first before production?

### Before an External API Call (POST / DELETE / PUT)

- [ ] Is the endpoint correct (not accidentally hitting production from a dev environment)?
- [ ] Is the operation idempotent or does it have side effects on the first call only?
- [ ] What happens on failure - is there a retry mechanism?
- [ ] Are credentials scoped correctly (not using production keys in dev)?

---

## Risk Tier Quick Reference

| Operation | Risk | Checklist items required |
|-----------|------|--------------------------|
| Read file | None | None |
| List directory | None | None |
| Search/grep | None | None |
| Create new file | Low | Path correct, encoding correct |
| Append to file | Low | Path correct, file exists |
| Overwrite file | Medium | Read first, minimum scope, encoding |
| Delete file | High | Verify exact target, check dependencies |
| Run read-only command | Low | Correct Cwd |
| Run build command | Medium | Target binary not locked, Cwd correct |
| Run migration | High | Reversible, tested on dev first |
| Run data-modifying script | High | Dry-run first, backup exists |
| External API POST/DELETE | High | Correct environment, idempotency checked |

---

## The One-Sentence Rule

> If you cannot state in one sentence what will change and how to undo it,
> do not proceed until you can.

---

## After an Operation - Verify

- [ ] Did the command exit with code 0 (or expected non-zero)?
- [ ] Does the output match what was expected?
- [ ] If a file was written: does it exist and have the correct size/content?
- [ ] If a migration ran: does the schema reflect the change?
- [ ] If a service was restarted: is it responding?

Do not assume success. Verify the result before reporting completion.
