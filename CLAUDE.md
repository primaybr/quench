# quench (dogfooding)

This repo uses its own rules. The imports below load them live, so edits apply to
the next Claude Code session with no copy to refresh. Do not paste rule text here.

- `rules/AGENTS.md`: the user-facing always-on rules (edit `skills/<name>/SKILL.md` first).
- `AGENTS.md`: instructions for working on this repo only.

@rules/AGENTS.md
@AGENTS.md

Full protocols load on demand from `skills/<name>/SKILL.md`.
Before finishing a change, run `python scripts/validate.py` (the same gate as the pre-commit hook).
