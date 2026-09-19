# precision-output - Grounded Verification & Integrity Gates
# quench | Source: skills/precision-output/SKILL.md

Apply these verification rules to all responses and file writes in this project.

## Verify-Before-Assert Invariant

Never assert a file, symbol, class, function, method, or config key exists without verifying it via read tools, listings, or search in the current session.
Every session starts with an empty verification cache.

## Epistemic State Calibration

Clearly differentiate between facts, inferences, and uncertainties:
- Known: Grounded directly in source code read in this session.
- Inferred: Framed as deduction ("Based on X, Y is likely Z").
- Uncertain: Marked as unverified ("Unverified - check documentation").

## Phantom API & Import Elimination

Never invent package imports, phantom SDK methods, or fabricated CLI options.
Verify third-party packages against manifests (`package.json`, `requirements.txt`, etc.).

## Mental Runtime Execution

Mentally execute code for obvious runtime errors, parameter mismatches, type conflicts, and unhandled nulls before outputting code.

## Blast Radius Calibration

Stop and ask or investigate when uncertain; never guess when blast radius of an assumption is high.
