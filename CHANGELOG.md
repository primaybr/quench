# CHANGELOG

All notable changes to quench are documented here.
Format: [version] date - description

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
