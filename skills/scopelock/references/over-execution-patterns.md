# Over-Execution Patterns & Catalog

Catalog of scope expansion failure modes in LLM coding assistants and autonomous agents.
Used by the scopelock skill.

---

## The Intent-to-Execution Gap

The intent-to-execution gap describes the divide between a user's literal prompt and an agent's speculative interpretation of that prompt. When an instruction is terse or underspecified, unhardened models routinely over-execute by:

1. Guessing missing requirements without stating assumptions.
2. Expanding the boundary of authorized files to include stylistic preferences.
3. Adding defensive boilerplate or speculative features that were never requested.

---

## Pattern Catalog

### 1. Unprompted Architectural Refactoring

- **Trigger:** "Fix the null pointer on line 32 of auth.py."
- **Failure Mode:** The agent notices that auth.py uses an older pattern or lacks dependency injection, and rewrites the entire file or splits it into multiple classes.
- **Consequence:** Massive diff, broken git history blame, conflicts with in-flight team branches, regression risk in unrelated codepaths.
- **Grounded Correction:** Fix the null check on line 32. Preserve the existing structure. If the architecture has structural debt, note it as an advisory observation at the end of the response.

### 2. Dependency Smuggling

- **Trigger:** "Parse this timestamp string into ISO format."
- **Failure Mode:** The agent installs `moment`, `date-fns`, or `arrow` instead of using the standard library or an already-installed date library.
- **Consequence:** Bloated lockfile, supply chain risk, license incompatibility, team convention violation.
- **Grounded Correction:** Inspect project manifests first. Use the standard library or existing dependencies. Never introduce a new package without explicit user confirmation.

### 3. Test Suite Escalation

- **Trigger:** "Add a test case for invalid email input."
- **Failure Mode:** The agent rewrites the existing test suite, replaces `unittest` with `pytest`, or modifies assertions in existing tests that happen to fail due to local environment differences.
- **Consequence:** Masked regressions, altered test contracts, broken CI configurations.
- **Grounded Correction:** Add the single requested test case. Do not alter existing passing or failing tests unless explicitly instructed.

### 4. Premature Generalization

- **Trigger:** "Make the CSV exporter handle semicolons."
- **Failure Mode:** The agent builds a pluggable dialect parser supporting TSV, pipe-delimited, XML, JSONL, and streaming buffers with abstract factory classes.
- **Consequence:** Over-engineered code that is harder to maintain and introduces unnecessary complexity.
- **Grounded Correction:** Add semicolon support to the CSV exporter. Keep the abstraction level proportional to the request.

### 5. Multi-Turn Cascading Drift

- **Trigger:** Multi-step autonomous agent workflow trying to fix a broken build.
- **Failure Mode:** Step 1 encounters a lint warning. Step 2 runs a global linter auto-fix. Step 3 encounters syntax changes. Step 4 edits tsconfig.json. Step 5 edits webpack config. The agent is now debugging build tooling completely disconnected from the user's original objective.
- **Consequence:** Total derailment of the session, wasted context window, corrupted configuration files.
- **Grounded Correction:** At each step, compare the current blocker against the primary objective. If resolving the blocker requires leaving the primary task domain, halt and surface the blocker to the user.
