# CHANGELOG

All notable changes to quench are documented here.
Format: [version] date - description

## [1.6.0] 2026-09-21

### Added
- Automated Adversarial Evaluation Runner (`scripts/eval_adversarial.py` and `quench eval` CLI subcommand):
  - Zero-dependency testing engine validating LLM completions against 12 canonical adversarial scenarios across all 4 disciplines:
    - `steel-mind`: SM-01 (Sycophancy induction), SM-02 (Invented citations), SM-03 (Silver lining compulsion).
    - `plaincast`: PC-01 (Emoji injection), PC-02 (Em dash and curly quotes), PC-03 (Unicode arrows and checkmarks).
    - `leakguard`: LG-01 (Host drive paths), LG-02 (Private MCP tool bleed), LG-03 (Token exposure).
    - `precision-output`: PO-01 (Phantom SDK methods), PO-02 (Unverified config keys), PO-03 (Hallucinated CLI flags).
  - Built-in canonical fixtures:
    - 12 failing baseline completions mirroring default LLM failure modes (100% failure detection).
    - 12 hardened compliant completions satisfying 100% of binary compliance rules (12/12 pass rate).
  - CLI `quench eval` with `--self-test` (default), `--input <path>` (supports JSON and JSONL completions), and `--json` for CI automation.
  - Generates a clean ASCII scorecard detailing scenario IDs, disciplines, rule pass/total counts, and descriptions.
- Comprehensive Evaluation Test Suite (`scripts/test_eval_adversarial.py`):
  - 11 unit tests verifying scenario loading, baseline failure detection, compliant completion passes, rule violation messages, CLI invocations, and external file parsing.
  - Overall test suite expanded from 115 to 126 tests with 100% pass rate.

---

## [1.5.9] 2026-09-21

### Changed
- Resolved Redundancy Map candidates (R-01 through R-04) from the Adversarial Test Suite:
  - R-01 (`steel-mind` / `precision-output`): Consolidated phantom API and manifest cross-referencing to `precision-output` as the canonical owner; streamlined `steel-mind: Output Integrity` to a concise reference pointer.
  - R-02 (`steel-mind` / `precision-output`): Consolidated duplicate definitions of the three epistemic states (Known, Inferred, Uncertain) to `precision-output`; `steel-mind: Epistemic Integrity` focuses cleanly on confidence calibration, version qualification, and blast-radius stop/proceed gating.
  - R-03 (`steel-mind` / `leakguard`): Replaced redundant hermetic tool isolation checklist item in `steel-mind Protocol 5` with direct reference to `leakguard Protocol 2`.
  - R-04 (`steel-mind`): Consolidated duplicate file read/overwrite invariants in `steel-mind: Tool Use Discipline` ("read before write" and "never overwrite unread files") into a single unified rule: `Before any file write or overwrite: read current content in the active session first.`
- Token budget reduction:
  - `rules/AGENTS.md` streamlined with tighter phrasing across all four disciplines.
  - Synchronized all trims across all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie) maintaining strict adapter parity.
- CLI & Packaging consistency:
  - Aligned dual module attributes by defining `__version__ = "1.5.9"` across both `quench.py` and `scripts/quench.py`.
  - Hardened `scripts/test_packaging.py` import precedence so root `quench.py` is tested deterministically under test runner discovery.
  - Bumped project version to 1.5.9 in `pyproject.toml`, `scripts/quench.py`, `quench.py`, and test suites.

---

## [1.5.8] 2026-09-20

### Added
- Resolved adversarial gap proposals across skill definitions and synced to all 11 adapters:
  - G-01 (`steel-mind`): Added `Cadence Self-Check Gate` (prose of 5+ sentences where 4+ fall within a 5-word band triggers rewriting at least 2 sentences).
  - G-02 (`plaincast`): Evaluated and closed - bold-first list spam is already covered by existing protocol.
  - G-03 (`steel-mind` / `leakguard`): Evaluated and closed - path separator mixing is already covered by existing invariants.
  - G-04 (`steel-mind`): Added explicit activation gate for code review comments and PR descriptions to check software subjects for false agency verbs ("tries", "wants", "hopes", "attempts", "believes", "expects").
  - G-05 (`steel-mind`): Added `PowerShell Write Quick-Test` verifying `[System.IO.File]::WriteAllText` with `UTF8Encoding $false` on any generated PowerShell write.
- Synced all rule additions across `rules/AGENTS.md` and all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie).

### Fixed
- False-positive calibration across Rust, Ruby, and Monorepo corpora (tokio-rs/tokio, sinatra/sinatra, vercel/turbo - 6,900+ files cloned):
  - **Localhost URL pattern** (`scripts/validate.py`):
    - In `vercel/turbo`, 41 violations were flagged for standard local dev URLs like `localhost:3000/api`, `localhost:9090/graph`, `localhost:3002/stripe` appearing in example documentation and test fixtures.
    - Fix: Extended the negative lookahead of the localhost regex to exclude common development API path prefixes (`api`, `graphql`, `graph`, `webhook`, `stripe`, `health`, `docs`, `metrics`, `mf-manifest`, `mf-`). Private service URLs remain flagged.
    - Re-scanned `turbo` (2,501 files): all validation gates passed with 0 violations.
    - `tokio` (41 text files) and `sinatra` (24 text files) passed with 0 violations.

---

## [1.5.7] 2026-09-20

### Fixed
- Gate 2 (leakguard) false-positive calibration via real open-source corpus testing
  (shadcn-ui/ui, fastai/fastai, cli/cli - 1,430 files scanned total):

  **Private LAN IP address pattern** (`scripts/validate.py`):
  - Previous regex `\b(?:192\.168\.|10\.|172\...)[\\d.]+` matched three-part semver
    version strings (`10.0.0`, `10.4.14`) in `package.json` and `pnpm-lock.yaml`
    files, producing 1,486 false positives in shadcn-ui alone.
  - Fix: Rewrote the 10.x.y.z arm to require all four octets with per-octet range
    validation (`0-255`). Also added a negative lookbehind for version-prefix
    characters (`>=<~^'"@`) to suppress matches inside dependency version
    constraints.
  - The 192.168 and 172.16-31 arms also upgraded to four-octet form for consistency.

  **Unix home directory path pattern**:
  - `/home/runner/work` and `/Users/runner/work` appeared extensively in GitHub
    Actions workflow testdata fixtures and CI log snapshots in the cli/cli repo,
    generating 133 false positives. The `runner` user is an ephemeral GitHub Actions
    CI agent, not a developer personal home directory.
  - Fix: Added `/home/runner/` and `/Users/runner/` to `WHITELISTED_PATH_SUBSTRINGS`.

<!-- leakguard:ignore-start -->
- **True positive confirmed** during calibration: cli/cli `eval-prompts.yml` contains
  `/Users/williammartin/work` (a real developer username) in 4 locations - correctly
  flagged by the scanner as a genuine Unix home directory leak (not suppressed).
<!-- leakguard:ignore-end -->

### Changed
- Token budget trim of `rules/AGENTS.md` and monolithic adapter files:
  - `rules/AGENTS.md` reduced from 8,635 bytes to 6,293 bytes (~1,573 tokens, down from ~2,160).
  - Trimmed: Context Economy verbosity, Structural Cadence illustrative parentheticals,
    redundant precision-output epistemic state restatement (R-02 from adversarial analysis),
    redundant phantom-API line (R-01).
  - Applied same trims to: `adapters/antigravity/.agents/rules/AGENTS.md`,
    `adapters/copilot/copilot-instructions.md`, `adapters/generic/system-prompt.md`,
    `adapters/windsurf/.windsurfrules`.
  - Adapters with compact modular format (aider) and adapter-specific concise form (claude) unchanged.

### Test results
- All 114 tests pass across all 6 suites (test_validate, test_cli_e2e, test_precommit_hooks,
  test_packaging, test_action_yml, test_bootstrap_scripts) with zero regressions.
- Fixed leakguard self-scan false positives: adversarial-test-suite.md intentional
  bad-output fixtures (fake API keys, private tool names) and the CHANGELOG true-positive
  citation now wrapped in leakguard:ignore-start/end blocks. These are test data, not leaks.

---

## [1.5.6] 2026-09-20

### Added
- Adversarial test suite document (`skills/precision-output/references/adversarial-test-suite.md`):
  - 10 adversarial prompts (3 per skill discipline, plus an extra precision-output case given its blast radius).
  - Full analysis per prompt: baseline LLM failure mode, firing Quench rule, and binary compliance test.
  - Coverage gap analysis: 5 genuine gaps identified (G-01 through G-05) across cadence detection,
    bold-first list monotony, path separator mixing, false agency in code review, and BOM write elicitation.
  - Redundancy map: 4 rule overlaps identified as consolidation candidates for the next AGENTS.md trim.
- Gap proposals added as commented TODO blocks to skill files:
  - `skills/steel-mind/SKILL.md`: gaps G-01 (cadence self-check gate), G-04 (agency activation note),
    and G-05 (BOM write quick test).
  - `skills/plaincast/SKILL.md`: gap G-02 (bold-first bullet adversarial prompt proposal).

---

## [1.5.5] 2026-09-20

### Added
- Official Pre-Commit Framework Support (`.pre-commit-hooks.yaml`):
  - Integrates Quench into standard pre-commit workflows with `quench-check` and `quench-commit-msg` hooks.
  - Added `scripts/test_precommit_hooks.py` validating manifest structure, hook definitions, and stage bindings.
- Python Packaging & Global CLI (`pyproject.toml`):
  - PEP 517 / PEP 621 packaging with `setuptools>=61.0` and zero runtime dependencies.
  - Installs global `quench` command directly on system `$PATH` via `pipx install git+https://github.com/primaybr/quench.git` or `pip install -e .`.
  - Refined `quench.py` to support module importing without circular namespace collisions.
  - Added `scripts/test_packaging.py` testing packaging metadata, module loading, and CLI entrypoint wiring.
- Reusable GitHub Action (`action.yml`):
  - Composite action enabling external repositories to run Quench integrity scans with `uses: primaybr/quench@master`.
  - Configurable inputs for `target`, `fix`, and `paths-only`.
  - Added `scripts/test_action_yml.py` validating action schema, inputs, and composite execution steps.
- Standalone Remote Bootstrap Installers (`scripts/install.sh`, `scripts/install.ps1`):
  - Portable POSIX sh script supporting one-liner installation (`curl -fsSL ... | bash -s -- --tool cursor`).
  - Native Windows PowerShell script written strictly in UTF-8 without BOM (`irm ... | iex`).
  - Added `scripts/test_bootstrap_scripts.py` verifying argument handling, source discovery, and cross-platform installation behaviors.
- Validation engine adjustments (`scripts/validate.py`):
  - Automatically ignores `test_*.py` test suites during repository scans to prevent false positives on synthetic test fixtures.

---

## [1.5.4] 2026-09-20

### Added
- Interactive Quench CLI (`scripts/quench.py` and top-level runner `quench.py`):
  - Zero-dependency unified command line interface built with Python 3 stdlib.
  - `quench init`: Interactive or scripted initialization across 12 adapter targets (`cursor`, `copilot`, `kilo`, `cline`, `windsurf`, `claude`, `generic`, `aider`, `zed`, `junie`, `antigravity`, `rules`, or `all`). Supports `--target`, `--force`, and `--hooks`.
  - `quench check`: Repository verification across all 5 gates with `--fix` and `--paths-only` options.
  - `quench update`: Automatic detection and refreshing of installed adapters from upstream templates.
  - `quench status` / `info`: Inspection of active adapters, configured rules, and git hook status.
  - Global `--version` / `-v` flag reporting `quench 1.5.4`.
- External Contributor Sanity Check Suite (`scripts/test_cli_e2e.py`):
  - End-to-end integration tests using isolated temporary directories and fresh git repositories.
  - Comprehensive coverage for single, modular, and full adapter initialization.
  - Verification of git pre-commit and commit-msg hooks and execution permissions.
  - Validation engine pass/fail detection on clean projects, synthetic violations, and auto-fix capabilities.
  - Status detection and adapter updating workflows.
  - Wired into `scripts/test_validate.py` and CI workflow `.github/workflows/validate.yml`.
- Validation engine adjustments (`scripts/validate.py`):
  - Gate 3 parity check scoped to repositories containing `adapters/` source tree, ensuring clean validation of consumer repositories.
  - Added `test_cli_e2e.py` to `IGNORE_FILES`.

---

## [1.5.3] 2026-09-19

### Added
- `skills/precision-output/SKILL.md` (v1.0.0):
  - Hallucination prevention, epistemic integrity, and verification-before-assertion gates
  - Protocol 1: Verify-Before-Assert Invariant (Existence Gate)
  - Protocol 2: The Three Epistemic States (Known, Inferred, Uncertain)
  - Protocol 3: Phantom API & Import Elimination (Manifest Cross-Referencing)
  - Protocol 4: Execution Grounding & Mental Runtime Simulation
  - Protocol 5: Clean Refusal & Blast Radius Calibration
- Reference documentation for precision-output:
  - `skills/precision-output/references/verification-checklist.md`: Pre-assertion checklist for agents before outputting code or claims
  - `skills/precision-output/references/hallucination-catalog.md`: Taxonomy of phantom APIs, fabricated flags, and memory drift traps
- Full adapter parity across all 11 adapters:
  - New modular adapter files:
    - `adapters/cursor/.cursor/rules/precision-output.mdc`
    - `adapters/kilo/.kilo/rules/precision-output.md`
    - `adapters/cline/.clinerules/precision-output.md`
    - `adapters/zed/.zedprompts/precision-output.md`
    - `adapters/junie/.junie/rules/precision-output.md`
  - Updated `adapters/kilo/kilo.jsonc` to include `.kilo/rules/precision-output.md`
  - Appended precision-output section to all consolidated adapters:
    - `adapters/antigravity/.agents/rules/AGENTS.md`
    - `adapters/cursor/.cursorrules`
    - `adapters/copilot/copilot-instructions.md`
    - `adapters/windsurf/.windsurfrules`
    - `adapters/claude/CLAUDE.md` (section 11)
    - `adapters/generic/system-prompt.md`
    - `adapters/aider/CONVENTIONS.md`
- Always-on rule extraction:
  - Added `## precision-output: Grounded Verification & Integrity Gates` section to `rules/AGENTS.md`
- Validation engine parity update (`scripts/validate.py`):
  - Added the 5 new modular adapter paths to `REQUIRED_ADAPTERS` in Gate 3 parity check
- Documentation updates:
  - `README.md`: Added `precision-output` (v1.0.0) to skills table and architecture tree
  - `INSTALL.md`: Added `precision-output` installation copy commands and adapter coverage matrix

---

## [1.5.2] 2026-09-19

### Added
- CI badge in `README.md` (GitHub Actions Validate workflow status badge)
- Gate 2 extended secret patterns (5 new categories):
  - Slack API tokens (`xoxb-`, `xoxp-`, `xoxa-` prefixes)
  - Twilio Account SIDs (`AC[a-f0-9]{32}`)
  - Twilio Auth Token inline assignments
  - SendGrid API keys (`SG.[A-Za-z0-9]{67}`)
  - GCP service account private_key fragments
- Gate 2 auto-fix (`--fix` flag now also repairs local drive path violations):
  - `validate_path_leaks` gains `auto_fix: bool = False` parameter
  - Local drive/home path matches replaced with `/path/to/<project>` in-place
  - Secret/token matches flagged with `(manual rotation required)` but NOT auto-replaced
  - `scan_repository` wires Gate 2 fixes alongside existing Gate 1 fixes
- 9 new unit tests (7 in `TestLeakguardCloudPatterns`, 2 in `TestGate2AutoFix`)
- `skills/leakguard/SKILL.md` (v1.0.2): Protocol 3 updated with new token signatures
- `INSTALL.md`: leakguard install instructions added for all 11 adapters

### Changed
- README skills table: leakguard version updated to 1.0.2
- INSTALL.md adapter install blocks: leakguard `cp` lines added for Cursor (mdc), Cline, Kilo, Zed, Junie

---

## [1.5.1] 2026-09-19

### Added
- Expanded Gate 2 secret scanner in `scripts/validate.py` with 10 new pattern categories:
  - Anthropic API Keys (`sk-ant-` prefix)
  - AWS Access Key IDs (`AKIA[A-Z0-9]{16}`)
  - AWS Secret Access Key inline assignments
  - Stripe live/test/restricted keys (`sk_live_`, `pk_live_`, `rk_live_`, `rk_test_`)
  - Raw Bearer token strings in documentation or config
  - Generic API key assignments (`api_key = <value>`)
  - Database connection URIs with embedded credentials (postgres, mysql, mongodb, redis, mssql)
  - `.env` secret assignment bleed for common variable names (`DB_PASSWORD`, `SECRET_KEY`, `JWT_SECRET`, `APP_KEY`, `AUTH_SECRET`)
  - Private LAN IP addresses (`192.168.x.x`, `10.x.x.x`, RFC 1918 ranges)
  - Localhost URLs with non-generic application paths
- 8 new unit tests in `TestLeakguardExtendedPatterns` (30 total, up from 22)
- `skills/leakguard/SKILL.md` (v1.0.1): expanded Protocol 3 scanned token signatures list to match all new engine patterns
- `skills/leakguard/references/leak-patterns.md`: wrapped DB URI example block with `leakguard:ignore` markers

### Changed
- Versioning scheme: patch digit (last position) increments from 0 through 9 before the minor digit advances

---

## [1.5.0] 2026-09-19


### Added
- `skills/leakguard/SKILL.md` (v1.0.0):
  - Environment, path, and context isolation discipline
  - Protocol 1: Path Neutralization & Generic Placeholders (host path neutralization hierarchy)
  - Protocol 2: Hermetic Project Isolation & Anti-Context Bleed (preventing private environment tools, sibling project names, and internal prompts from leaking into public code and docs)
  - Protocol 3: Secret & Credential Redaction (API keys, PATs, database connection strings)
  - Protocol 4: Pre-Commit Diff & Staging Audit
  - Protocol 5: Portable Path Formatting (universal forward slashes)
- `skills/leakguard/references/leak-patterns.md`:
  - Reference catalog detailing path leaks, context bleed vectors, credential exposures, and remediation procedures
- `skills/steel-mind/SKILL.md` (v1.1.0):
  - Protocol 5: Added Hermetic Project Isolation integrity gate (verifying tools and dependencies exist in current repository)
  - Protocol 6: Generic subagent delegation and cache guidance
- `skills/steel-mind/references/slop-taxonomy.md`:
  - Added Category 9: Context Bleed and Boundary Violations
- `rules/AGENTS.md`:
  - Added always-on compact extract for `leakguard`
  - Enforced hermetic project boundaries across repository invariants
- Multi-Tool Adapter Parity:
  - Synchronized `leakguard` across all 11 adapters (Antigravity, Cursor, Copilot, Kilo, Cline, Windsurf, Claude, Generic, Aider, Zed, Junie)
- Validation Engine & Pre-Commit Hook:
  - Added Cross-Project Context Bleed detection to Gate 2 in `scripts/validate.py`
  - Added `test_cross_project_bleed_detected` to unit test suite

### Security & Sanitization
- Purged all occurrences of external project names and private tool references across git history using `git-filter-repo`

---

## [1.4.0] 2026-09-19

### Added
- Repository Validation Engine (`scripts/validate.py`):
  - Zero-dependency verification engine using Python 3 standard library
  - Gate 1 (Plaincast Character Boundary): Enforces strict ASCII keyboard boundary, detects banned emojis, typographic dashes, curly quotes, Unicode ellipsis, and zero-width characters with optional `--fix` auto-repair
  - Gate 2 (Leakguard & Path Sanitization): Detects hardcoded local workspace drive paths, user profile folders, absolute home paths, and accidental secret token leaks
  - Gate 3 (Multi-Tool Adapter Parity): Verifies presence of all 11 adapters and ensures bidirectional synchronization with active skills and `rules/AGENTS.md`
  - Gate 4 (Skill Frontmatter Schema): Validates YAML schema on all skills (requires `name`, SemVer `version`, `description`; rejects illegal fields like `trigger`)
  - Gate 5 (Hygiene & Encoding): Enforces UTF-8 encoding without BOM and rejects CRLF line endings
- Pre-commit Automation (`.githooks/pre-commit`, `scripts/install-hooks.py`):
  - Added git pre-commit hook executing `scripts/validate.py` before any commit
  - Added installer utility configuring `core.hooksPath` to `.githooks`
- Unit Test Suite (`scripts/test_validate.py`):
  - 16 test cases verifying each validation gate against clean and dirty fixtures, path leaks, and auto-fix behavior

### Security & Sanitization
- Purged local path references across repository git history using `git-filter-repo`
- Replaced absolute host drive paths in documentation with standardized `/path/to/quench` placeholders

---

## [1.3.0] 2026-09-19

### Added
- `skills/steel-mind/SKILL.md` (v1.1.0):
  - Formally introduced Rule Tiers: Hard Gates (non-negotiable invariants) and Purpose Gates (techniques requiring functional justification)
  - Protocol 8: Structural Cadence & Syntactic Integrity (cadence uniformity prevention, bimodal burstiness trap mitigation, sentence opener diversity, elimination of trailing participial tack-ons, and removal of negative parallelisms)
  - Protocol 9: Semantic Grounding & Agency Discipline (elimination of false agency in inanimate software artifacts, removal of compulsive silver linings from technical findings, and copula avoidance puffery replacement)
- `skills/steel-mind/references/slop-taxonomy.md`:
  - Added Category 7: Cadence and Syntactic Tells
  - Added Category 8: Semantic Fallacies and False Agency
- `skills/plaincast/SKILL.md` (v1.1.0):
  - Protocol 9: Punctuation Density & List Restraint (colon and semicolon density gating, bold-first list spam avoidance)
- `rules/AGENTS.md`:
  - Synchronized always-on compact extracts for structural cadence, false agency, colon restraint, and list spam avoidance
- Synchronized all 11 adapters across the repository:
  - Antigravity (`adapters/antigravity/.agents/rules/AGENTS.md`)
  - Cursor (`.cursorrules`, `.cursor/rules/*.mdc`)
  - GitHub Copilot (`copilot-instructions.md`)
  - Kilo Code (`.kilo/rules/`)
  - Cline (`.clinerules/`)
  - Windsurf (`.windsurfrules`)
  - Claude.ai (`CLAUDE.md`)
  - Generic System Prompt (`system-prompt.md`)
  - Aider (`CONVENTIONS.md`)
  - Zed AI (`.zedprompts/`)
  - JetBrains Junie (`.junie/rules/`)

---

## [1.2.0] 2026-09-19

### Added
- `adapters/kilo/` - Kilo Code adapter (free, popular VS Code AI coding extension)
  - `kilo.jsonc` - project config file referencing both rule files via `instructions` array
  - `.kilo/rules/steel-mind.md` - behavior tempering rules
  - `.kilo/rules/plaincast.md` - text normalization rules
  - Supports global install via `~/.config/kilo/kilo.jsonc`
- `INSTALL.md` updated with Kilo Code section and updated adapter coverage table

### Fixed
- All adapters now include both steel-mind and plaincast content (previously plaincast
  was missing from all adapter files)
- Added modular plaincast files for tools supporting separate rule files:
  Cursor (.mdc), Cline (.clinerules), Zed (.zedprompts), JetBrains Junie (.junie/rules)

---

## [1.1.0] 2026-09-19

### Added
- `plugin.json` - quench is now a proper Antigravity plugin, installable via plugins.json
- `rules/AGENTS.md` - compact always-on rules file compiled from all skills
  - steel-mind protocols 1-6 distilled into injected rules (anti-slop, platform,
    tool discipline, epistemic integrity, output integrity, context economy)
  - plaincast text normalization rules (emoji, em dash, curly quotes, ellipsis,
    invisible characters, Unicode symbols, all-caps, bold inflation)
- `CHANGELOG.md` - this file

### Changed
- `skills/steel-mind/SKILL.md` - removed invalid `trigger: model_decision` frontmatter field
  (trigger is a rules-only field; skills use progressive disclosure via description)
- `skills/plaincast/SKILL.md` - same frontmatter fix
- `README.md` - updated to explain skills vs rules architecture, plugin installation

### Architecture clarification
Skills and rules are two separate loading mechanisms:
- Skills (SKILL.md): progressive disclosure - agent reads the description and decides
  to load the full content when relevant. Used for deep reference material.
- Rules (AGENTS.md): always-on - injected into every context window automatically,
  silently, without agent decision or announcement. Used for behavioral disciplines.

quench uses both: SKILL.md files are the canonical source of truth and full
reference. rules/AGENTS.md is the compact always-on extract that the agent
operates under every session without thinking about it.

---

## [1.0.0] 2026-09-19

### Added
- `skills/steel-mind/SKILL.md` - AI behavior tempering discipline
  - Protocol 1: Anti-slop lexicon (14 banned constructs with positive replacements)
  - Protocol 2: Platform grounding (Windows paths, BOM encoding, file locking)
  - Protocol 3: Tool use discipline (surgeon's checklist for destructive ops)
  - Protocol 4: Epistemic integrity (3 knowledge states, confidence calibration)
  - Protocol 5: Output integrity gates (verify before assert)
  - Protocol 6: Context economy (subagent delegation, compression, clean stop)
  - Protocol 7: Encoding and file write hygiene (safe write patterns per language)
- `skills/steel-mind/references/slop-taxonomy.md` - full slop pattern catalog
- `skills/steel-mind/references/platform-traps.md` - OS and DB failure modes
- `skills/steel-mind/references/tool-discipline-checklist.md` - pre-flight checklist
- `skills/plaincast/SKILL.md` - text normalization discipline
  - Protocol 1: Emoji prohibition with rationale
  - Protocol 2: Dash discipline (8 Unicode dash variants catalogued)
  - Protocol 3: Quote discipline (16 Unicode quote variants with replacements)
  - Protocol 4: Ellipsis discipline (U+2026 vs three periods)
  - Protocol 5: Invisible and space characters (10 variants)
  - Protocol 6: Arrows, bullets, symbols (with ASCII replacements)
  - Protocol 7: Heading and structure discipline
  - Protocol 8: Numerals and units
  - Quick self-check (9-point mental scan)
  - Explicit exception conditions
- `skills/plaincast/references/character-taxonomy.md` - full Unicode table with Python normalization script
- `skills/plaincast/references/why-it-matters.md` - 10 contexts x concrete pipeline failures
- `skills/plaincast/references/style-guide-comparison.md` - AP, Chicago, Microsoft, Google positions
- `adapters/` - multi-tool adapter files for Cursor, Copilot, Cline, Windsurf, Claude.ai,
  generic (ChatGPT/Replit), Aider, Zed, JetBrains Junie
- `INSTALL.md` - multi-tool installation guide
- `README.md` - project overview
- `.gitignore` - OS, editor, temp file exclusions
- `.gitattributes` - enforces LF line endings for all text files
