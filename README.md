# quench

> The hardening moment. A production-grade Skills ecosystem for AI Agents.

[![Validate](https://github.com/primaybr/quench/actions/workflows/validate.yml/badge.svg)](https://github.com/primaybr/quench/actions/workflows/validate.yml)

Not a prompt pack. Not a jailbreak collection. Not a role-play library.

quench is where raw AI capability gets rapidly cooled into disciplined,
production-hardened behavior - specific treatments, real failure modes,
grounded techniques.

Each skill here is born from real production failures, real platform pitfalls,
and real lessons - not copied from generic prompt engineering guides.

---

## The Hardening Difference

AI coding assistants naturally drift into failure modes that degrade codebase hygiene, break automated pipelines, and leak environment identities. Quench targets these deterministic failure modes with paired negative constraints and positive replacements:

| Failure Mode | Default LLM Behavior | Quench Hardened Behavior | Discipline |
|---|---|---|---|
| **Conversational Slop** | "Certainly! I'd be happy to help! That's a great question..." | Direct technical substance. Zero filler openers or sign-offs. | `steel-mind` |
| **Phantom APIs** | Hallucinates non-existent methods under pressure. | Mandatory verify-before-assert. Explicit epistemic tagging (`Uncertain`). | `precision-output` |
| **Character Corruption** | Outputs typographic curly quotes, em dashes, Unicode ellipsis. | Strictly standard ASCII keyboard boundary (straight quotes, hyphens, `...`). | `plaincast` |
| **Encoding Traps** | Generates PowerShell `Set-Content -Encoding UTF8` (writes UTF-8 BOM). | Enforces `[System.IO.File]::WriteAllText` with no-BOM constructor. | `steel-mind` |
| **Environment Leaks** | Leaks host paths, Windows drive letters, or secret tokens. | Neutralizes to generic placeholders (`/path/to/<project>`), redacts tokens. | `leakguard` |
| **False Agency** | Claims software "tries", "wants", or "hopes" to execute logic. | Grounded causality: states literal execution, return values, or errors. | `steel-mind` |

---

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| [steel-mind](./skills/steel-mind/SKILL.md) | 1.1.1 | AI behavior tempering: anti-slop, platform grounding, tool discipline, epistemic integrity, structural cadence, and semantic grounding |
| [plaincast](./skills/plaincast/SKILL.md) | 1.1.0 | Text normalization: standard keyboard boundary, no emoji, no em dashes, no curly quotes, colon/list restraint |
| [leakguard](./skills/leakguard/SKILL.md) | 1.0.2 | Environment, path, and context isolation: host path neutralization, hermetic project boundaries, credential redaction |
| [precision-output](./skills/precision-output/SKILL.md) | 1.0.0 | Hallucination prevention: verify-before-assert, three epistemic states, manifest grounding, mental runtime execution |

---

## How It Works: Skills vs Rules

quench uses two distinct loading mechanisms. Understanding this is key to
knowing what runs when.

### Skills (progressive disclosure)

```
skills/<name>/SKILL.md
```

Skills are the **canonical source of truth**. They contain the full protocol
documentation, rationale, examples, and edge cases. Think of them as the
engineering spec.

Skills are **not loaded automatically.** The agent reads each skill's
description and decides to load the full content when it is relevant to the
current task. This is called progressive disclosure - it keeps context windows
lean when a skill is not needed.

Use skills when you want:
- Deep reference material the agent can pull on demand
- Step-by-step procedures for specific workflows
- Rich documentation with examples and exceptions

### Rules (always-on)

```
rules/AGENTS.md
```

Rules are the **compact operational extract** derived from skills. They are
injected into every context window automatically, every session, without any
agent decision or announcement. The agent just operates under them silently,
the way a writer internalizes a style guide without mentioning it.

Use rules when you want:
- Behavioral disciplines that apply to all output without exception
- Zero-overhead enforcement with no activation step
- Transparent operation - no "I am now applying skill X" announcements

### The quench architecture

```
skills/           <- Full reference docs. Authored and maintained here.
  steel-mind/
    SKILL.md      <- Canonical, complete documentation
    references/   <- Supporting deep-dive material
  plaincast/
    SKILL.md
    references/
  leakguard/
    SKILL.md
    references/
  precision-output/
    SKILL.md
    references/

rules/            <- Compiled extract. Always-on. Never edited directly.
  AGENTS.md       <- Single file, loaded every session, derived from skills/
```

**Rule:** Always edit the SKILL.md. Never edit rules/AGENTS.md directly.
When a skill changes, update rules/AGENTS.md to match.

---

## Installation

### 1. Remote One-Liner (Zero-Clone)

Install Quench rules directly into your current project without pre-cloning the repository:

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/primaybr/quench/master/scripts/install.sh | bash -s -- --tool cursor

# Windows (PowerShell)
irm https://raw.githubusercontent.com/primaybr/quench/master/scripts/install.ps1 | iex
```

### 2. Global CLI (pipx / pip)

Install `quench` as a global command on your system `$PATH`:

```bash
pipx install git+https://github.com/primaybr/quench.git
# or within a cloned repository:
pip install -e .
```

Once installed, use `quench` anywhere:

```bash
# Interactive setup: choose an adapter from a numbered menu
quench init

# Direct adapter initialization in a project directory
quench init --tool cursor --target /path/to/project

# Install all adapters and git validation hooks
quench init --tool all --hooks --target /path/to/project

# Validate repository integrity across all 5 gates
quench check --target /path/to/project

# Validate and auto-fix fixable plaincast and path issues
quench check --fix --target /path/to/project

# Inspect active adapters and git hooks status
quench status --target /path/to/project

# Refresh existing installed adapters to latest upstream versions
quench update --target /path/to/project

# Run the automated adversarial evaluation runner (12 scenarios across 4 disciplines)
quench eval

# Evaluate external model completions from JSON/JSONL against adversarial scenarios
quench eval --input completions.jsonl
```

### 3. Pre-Commit Framework Support

If your project uses [pre-commit](https://pre-commit.com), add Quench to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/primaybr/quench
    rev: v1.6.0
    hooks:
      - id: quench-check
      - id: quench-commit-msg
```

### 4. Reusable GitHub Action

Validate pull requests and commits in GitHub Actions CI using the official composite action:

```yaml
- name: Run Quench Validation
  uses: primaybr/quench@master
  with:
    target: .
```

### Antigravity (native - recommended)

**As a plugin (full experience: skills + always-on rules):**

```jsonc
// ~/.gemini/config/plugins.json
{
  "entries": [{ "path": "/path/to/quench" }]
}
```

This registers quench as an Antigravity plugin. On every session:
- `rules/AGENTS.md` is injected automatically (always-on, silent)
- `skills/*/SKILL.md` descriptions are available for on-demand activation

**Skills only (no always-on rules):**

```jsonc
// ~/.gemini/config/skills.json
{
  "entries": [{ "path": "/path/to/quench/skills" }]
}
```

**Per-project (for teams via version control):**

Copy the `.agents/` structure or reference quench via `plugins.json` at the
project root. See [INSTALL.md](./INSTALL.md) for full per-tool instructions.

### Other AI tools

quench ships adapter files for 10 other tools (11 total including Antigravity). See [INSTALL.md](./INSTALL.md):

| Tool | Adapter |
|------|---------|
| Antigravity | `adapters/antigravity/.agents/rules/AGENTS.md` (or native plugin) |
| Cursor AI | `adapters/cursor/.cursorrules` or `.cursor/rules/*.mdc` |
| GitHub Copilot | `adapters/copilot/copilot-instructions.md` |
| Kilo Code | `adapters/kilo/kilo.jsonc` + `.kilo/rules/` |
| Cline | `adapters/cline/.clinerules/` |
| Windsurf | `adapters/windsurf/.windsurfrules` |
| Claude.ai Projects | `adapters/claude/CLAUDE.md` |
| ChatGPT / Replit | `adapters/generic/system-prompt.md` |
| Aider | `adapters/aider/CONVENTIONS.md` |
| Zed AI | `adapters/zed/.zedprompts/` |
| JetBrains Junie | `adapters/junie/.junie/rules/` |

---

## Validation Engine & Integrity Gates

quench includes a zero-dependency repository verification tool (`scripts/validate.py`)
enforcing strict repository quality and cleanliness before commits:

- **Gate 1 (Plaincast Character Boundary):** Flags banned emojis, typographic dashes (em dash, en dash), curly quotes, Unicode ellipsis, and zero-width or invisible characters. Supports `--fix` for automatic conversion to ASCII equivalents.
- **Gate 2 (Leakguard & Path Sanitization):** Scans for hardcoded local drives (`C:`, `F:`, etc.), user profile paths, absolute home directories, and accidental secret leaks (API tokens, PATs).
- **Gate 3 (Multi-Tool Adapter Parity):** Verifies all 11 adapters exist and stay synchronized with active skills.
- **Gate 4 (Skill Frontmatter Schema):** Validates YAML frontmatter on all `skills/*/SKILL.md` files (requires `name`, SemVer `version`, `description`; rejects illegal fields like `trigger`).
- **Gate 5 (Encoding & Line Endings):** Verifies UTF-8 encoding without BOM and rejects CRLF line endings.

### Running Validation

```bash
# Run full validation across the repository
python scripts/validate.py

# Check only for path or secret leaks
python scripts/validate.py --check-paths-only

# Automatically fix plaincast character violations in-place
python scripts/validate.py --fix

# Run unit tests
python scripts/test_validate.py
```

### Git Pre-Commit Hook

Install the repository pre-commit hook to automatically run the validation engine on every commit:

```bash
python scripts/install-hooks.py
```

---

## Philosophy

- Every rule has a grounded reason (no cargo-cult instructions)
- Every prohibition has a positive replacement (no pure negation theater)
- Platform-specific where it matters (Windows is not Linux)
- Skills = full reference. Rules = always-on discipline.
- Anti-slop by design (verified, not just asserted)

---

## Structure

```
quench/
  quench.py                      - Unified CLI runner
  plugin.json                    - Antigravity plugin manifest
  README.md                      - This file
  INSTALL.md                     - Per-tool installation guide
  CHANGELOG.md                   - Version history
  .gitignore
  .gitattributes                 - Enforces LF line endings
  .githooks/
    pre-commit                   - Automated git pre-commit validation hook
    commit-msg                   - Automated git commit-msg validation hook
  scripts/
    quench.py                    - Interactive Quench CLI implementation
    validate.py                  - Zero-dependency repository validation engine
    eval_adversarial.py          - Automated adversarial evaluation runner
    test_validate.py             - Unit test suite for validation engine
    test_cli_e2e.py              - End-to-end contributor sanity suite
    test_eval_adversarial.py     - Adversarial evaluation runner test suite
    install-hooks.py             - Hook installation utility
  skills/
    <skill-name>/
      SKILL.md                   - Full canonical skill documentation
      references/                - Deep-dive reference material
        *.md
  rules/
    AGENTS.md                    - Always-on compact rules (derived from skills)
  adapters/
    antigravity/                 - Antigravity standalone drop-in adapter
    cursor/                      - Cursor AI adapter
    copilot/                     - GitHub Copilot adapter
    cline/                       - Cline adapter
    windsurf/                    - Windsurf adapter
    claude/                      - Claude.ai adapter
    generic/                     - ChatGPT / paste-anywhere adapter
    aider/                       - Aider adapter
    kilo/                        - Kilo Code adapter
    zed/                         - Zed AI adapter
    junie/                       - JetBrains Junie adapter
```
