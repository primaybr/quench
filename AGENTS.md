# quench repository - agent instructions

For agents working on this repo. Not shipped to users: user-facing rules live in
`rules/AGENTS.md` and `adapters/`. Kilo loads this file automatically; `CLAUDE.md` imports it.

## Repository & Ecosystem Invariants

- **Canonical Source of Truth:** `skills/<name>/SKILL.md`. Always edit skills first, then extract to rules.
- **Skill Frontmatter:** Only `name`, `version`, `description`. Never include `trigger` (rules-only field).
- **Rules Extraction:** When a skill changes, update `rules/AGENTS.md` with a compact always-on summary.
- **Adapter Parity:** Sync every skill across all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie). Never allow adapter drift.
- **Skill Versioning & Documentation:** Whenever modifying any skill, always increment its frontmatter `version` (`skills/<name>/SKILL.md`), record the changes in `CHANGELOG.md`, and update version tables in `README.md`.
- **Hermetic Boundary:** Never reference external private tools or sibling projects in repository rules or documentation.
