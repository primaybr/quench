# CHANGELOG

All notable changes to quench are documented here.
Format: [version] date - description

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
