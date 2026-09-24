# quench (dogfooding)

This repo uses its own rules. The import below loads `rules/AGENTS.md` live, so
edits to the rules apply to the next Claude Code session with no copy to refresh.
Do not paste rule text here; edit `skills/<name>/SKILL.md`, then `rules/AGENTS.md`.

@rules/AGENTS.md

Full protocols load on demand from `skills/<name>/SKILL.md`.
Before finishing a change, run `python scripts/validate.py` (the same gate as the pre-commit hook).
