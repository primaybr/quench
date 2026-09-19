# quench - Multi-Tool Installation Guide

quench skills are authored in Antigravity SKILL.md format (the canonical source),
then compiled into adapter files for every major AI tool.

The rule: **one source of truth, many adapters**.
Edit `skills/<name>/SKILL.md` - adapters are generated from it, never the other way.

---

## Adapter Files (What Gets Generated)

| File | Target Tool(s) |
|------|---------------|
| `adapters/cursor/.cursorrules` | Cursor AI |
| `adapters/cursor/.cursor/rules/steel-mind.mdc` | Cursor AI (modular) |
| `adapters/copilot/.github/copilot-instructions.md` | GitHub Copilot |
| `adapters/cline/.clinerules/steel-mind.md` | Cline |
| `adapters/windsurf/.windsurfrules` | Windsurf |
| `adapters/claude/CLAUDE.md` | Claude.ai Projects |
| `adapters/generic/system-prompt.md` | ChatGPT, Replit, any paste-in tool |
| `adapters/aider/CONVENTIONS.md` | Aider |
| `adapters/zed/.zedprompts/steel-mind.md` | Zed AI |
| `adapters/junie/.junie/rules/steel-mind.md` | JetBrains Junie |
| `adapters/copilot/.github/copilot-instructions.md` | GitHub Copilot |

---

## Installation per Tool

### Antigravity (native - best experience)
```jsonc
// ~/.gemini/config/skills.json
{
  "entries": [{ "path": "/path/to/quench/skills" }]
}
```
Or per-project: copy `skills/steel-mind/` into your project's `.agents/skills/`.

### Cursor AI
```bash
# Option A - single file (simpler)
cp adapters/cursor/.cursorrules /your-project/.cursorrules

# Option B - modular rules (recommended for Cursor 0.42+)
cp adapters/cursor/.cursor/rules/steel-mind.mdc /your-project/.cursor/rules/
```

### GitHub Copilot
```bash
cp adapters/copilot/copilot-instructions.md /your-project/.github/copilot-instructions.md
```

### Cline
```bash
cp adapters/cline/steel-mind.md /your-project/.clinerules/steel-mind.md
```

### Windsurf
```bash
cp adapters/windsurf/.windsurfrules /your-project/.windsurfrules
```

### Claude.ai Projects
1. Open Claude.ai -> Projects -> your project -> Project Knowledge
2. Upload `adapters/claude/CLAUDE.md` as a knowledge file

### ChatGPT / Replit / Any paste-in tool
1. Open `adapters/generic/system-prompt.md`
2. Copy the contents
3. Paste into Custom Instructions / System Prompt field

### Aider
```bash
cp adapters/aider/CONVENTIONS.md /your-project/CONVENTIONS.md
# Aider reads this automatically as context
```

### Zed AI
```bash
cp adapters/zed/steel-mind.md /your-project/.zedprompts/steel-mind.md
```

### JetBrains Junie
```bash
cp adapters/junie/steel-mind.md /your-project/.junie/rules/steel-mind.md
```

---

## What the Adapters Contain

All adapters distill the same 7 protocols from `skills/steel-mind/SKILL.md`:
1. Anti-Slop Lexicon
2. Platform Grounding
3. Tool Use Discipline
4. Epistemic Integrity
5. Output Integrity Gates
6. Context Economy
7. Encoding and File Write Hygiene

The Antigravity SKILL.md is the full reference with all detail.
Adapters are condensed for tools with tighter context budgets.
