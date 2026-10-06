# quench repository - agent instructions

For agents working on this repo. Not shipped to users: user-facing rules live in
`rules/AGENTS.md` and `adapters/`. Kilo loads this file automatically; `CLAUDE.md` imports it.

## Repository & Ecosystem Invariants

- **Canonical Source of Truth:** `skills/<name>/SKILL.md`. Always edit skills first, then extract to rules.
- **Skill Frontmatter:** Only `name`, `version`, `description`. Never include `trigger` (rules-only field).
- **Rules Extraction:** When a skill changes, update `rules/AGENTS.md` with a compact always-on summary.
- **Adapter Parity:** Sync every skill across all 11 adapters (antigravity, cursor, copilot, kilo, cline, windsurf, claude, generic, aider, zed, junie). Never allow adapter drift.
- **Skill Versioning & Documentation:** Whenever modifying any skill, always increment its frontmatter `version` (`skills/<name>/SKILL.md`), record the changes in `CHANGELOG.md`, and update version tables in `README.md`.
- **Version Increment Cadence:** Advance patch and minor releases using single-digit increments (`1.9.1` -> `1.9.2` up to `1.9.9`). Never use two-digit components (do not use `1.10.0`). `1.9.9` is the last 1.x release: the next release after it is `2.0.0`, and any change that must break 1.x users waits for it.
- **Major Release Readiness (2.0.0):** The release tooling derives the floating tag from the pushed tag (`v2` for `v2.x.y`), and `DEFAULT_GLOBAL_REF` in `scripts/quench.py` follows the running version's major. A 1.x global install keeps following `v1` and is told, never forced, to opt in with `quench update --global --ref v2`. At 2.0.0: update README `@v1` and `~/.quench` text to `v2`, keep `v1` as the 1.x maintenance line, and bump `JSON_SCHEMA_VERSION` in `scripts/validate.py` only if the `--format json` keys change.
- **Adapter Parity Gate:** When a rule is sharpened in a skill, add a marker phrase to `PARITY_MARKERS` in `scripts/validate.py` so a partial backport across adapters fails Gate 3.
- **Releasing & Version Synchronization:** Always bump the version simultaneously across all three source locations: `pyproject.toml`, root `quench.py` (`__version__`), and `scripts/quench.py` (`VERSION`, `__version__`), as well as test assertions (`test_packaging.py`, `test_cli_e2e.py`) and README version pins. Rename `## [Unreleased]` in `CHANGELOG.md` to `## [X.Y.Z] YYYY-MM-DD` (optionally followed by `- Title`, which becomes the release title), commit, then `git tag vX.Y.Z` and push the branch and tag. `.github/workflows/release.yml` checks the tag against `pyproject.toml`, runs the tests, moves `v1`, and publishes the GitHub Release from that CHANGELOG section. Never move `v1` by hand.
- **GitHub Action Marketplace Metadata (`action.yml`):** In `action.yml`, `branding.icon` strictly requires a Feather icon name (e.g. `shield`), never a file path (`icon.png` is used only in `plugin.json` for plugin ecosystems); `name:` must not collide with existing GitHub organization or user names (e.g. `@Quench`), requiring multi-word titles such as `Quench Action`.
- **Hermetic Boundary:** Never reference external private tools or sibling projects in repository rules or documentation.
