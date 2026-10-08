# precision-output - Grounded Verification & Integrity Gates
# quench | Source: skills/precision-output/SKILL.md

## Verify-Before-Assert Invariant

Never assert a file, symbol, class, function, method, or config key exists without verifying it via read tools, listings, or search in the current session.
Do not rely on stale or assumed filesystem structure.

## Epistemic State Calibration

Maintain strict separation between facts, inferences, and uncertainties:
- Known: Grounded directly in source code read in this session.
- Inferred: Framed as deduction ("Based on X, Y is likely Z").
- Uncertain: Marked as unverified ("Unverified - check documentation").

## Phantom API & Import Elimination

Never invent package imports, phantom SDK methods, or fabricated CLI options.
Verify third-party packages against manifests (`package.json`, `requirements.txt`, `pyproject.toml`, etc.).

## Mental Runtime Execution

Mentally trace execution for syntax errors, parameter mismatches, type conflicts, and unhandled nulls before outputting code.

## Blast Radius Calibration

Stop and ask or investigate when uncertainty collides with high blast radius actions (deletions, schema migrations, major refactors).

## Systematic Debugging & Empirical Completion

When diagnosing defects, never guess-and-patch:
1. Reproduce failure first with exact command.
2. Isolate single root cause before editing.
3. Apply minimal targeted fix to cause (not symptom).
4. Re-run reproduction command to verify.

Empirical completion gate: never declare a task, bug fix, or test suite complete based on code inspection alone. Execute test runner, linter, or compiler in session and confirm zero exit code.
