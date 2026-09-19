# quench

> The hardening moment. A production-grade Skills ecosystem for AI Agents.

Not a prompt pack. Not a jailbreak collection. Not a role-play library.

quench is where raw AI capability gets rapidly cooled into disciplined,
production-hardened behavior - specific treatments, real failure modes,
grounded techniques.

Each skill here is born from real production failures, real platform pitfalls,
and real lessons - not copied from generic prompt engineering guides.

## Skills

| Skill | Description |
|-------|-------------|
| [steel-mind](./skills/steel-mind/SKILL.md) | AI behavior tempering: anti-slop, platform grounding, tool discipline, epistemic integrity |

## Philosophy

- Every rule has a grounded reason (no cargo-cult instructions)
- Every prohibition has a positive replacement (no pure negation theater)
- Platform-specific where it matters (Windows is not Linux)
- Anti-slop by design (verified, not just asserted)

## Structure

```
quench/
  README.md
  skills/
    <skill-name>/
      SKILL.md                  - Main skill instructions (YAML frontmatter + markdown)
      references/               - Supporting reference material
        *.md
```
