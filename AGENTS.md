# quench repository - agent instructions

For agents working on this repo. Not shipped to users: user-facing rules live in
`rules/AGENTS.md` and `adapters/`. Kilo loads this file automatically; `CLAUDE.md` imports it.

## Repository & Ecosystem Invariants

- **Canonical Source of Truth:** `skills/<name>/SKILL.md`. Always edit skills first, then extract to rules.
- **Skill Frontmatter:** Only `name`, `version`, `description`. Never include `trigger` (rules-only field).
- **Rules Extraction:** When a skill changes, update `rules/AGENTS.md` with a compact always-on summary.
- **Adapter Parity:** Sync every skill across all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie). Never allow adapter drift.
- **Skill Versioning & Documentation:** Whenever modifying any skill, always increment its frontmatter `version` (`skills/<name>/SKILL.md`), record the changes in `CHANGELOG.md`, and update version tables in `README.md`.
- **Version Increment Cadence:** Advance patch and minor releases using single-digit increments (`1.9.1` -> `1.9.2` up to `1.9.9`). Never jump to two-digit increments (e.g. do not use `1.10.0`).
- **Releasing & Version Synchronization:** Always bump the version simultaneously across all three source locations: `pyproject.toml`, root `quench.py` (`__version__`), and `scripts/quench.py` (`VERSION`, `__version__`), as well as test assertions (`test_packaging.py`, `test_cli_e2e.py`) and README version pins. Rename `## [Unreleased]` in `CHANGELOG.md` to `## [X.Y.Z] YYYY-MM-DD` (optionally followed by `- Title`, which becomes the release title), commit, then `git tag vX.Y.Z` and push the branch and tag. `.github/workflows/release.yml` checks the tag against `pyproject.toml`, runs the tests, moves `v1`, and publishes the GitHub Release from that CHANGELOG section. Never move `v1` by hand.
- **GitHub Action Marketplace Metadata (`action.yml`):** In `action.yml`, `branding.icon` strictly requires a Feather icon name (e.g. `shield`), never a file path (`icon.png` is used only in `plugin.json` for plugin ecosystems); `name:` must not collide with existing GitHub organization or user names (e.g. `@Quench`), requiring multi-word titles such as `Quench Action`.
- **Hermetic Boundary:** Never reference external private tools or sibling projects in repository rules or documentation.
