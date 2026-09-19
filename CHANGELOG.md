# CHANGELOG

All notable changes to quench are documented here.
Format: [version] date - description

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
