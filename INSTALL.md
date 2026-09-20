# quench - Multi-Tool Installation Guide

quench skills are authored in `skills/*/SKILL.md` (the canonical source of truth).
Always-on rules live in `rules/AGENTS.md` (the compiled extract).
Adapter files for each tool are derived from both.

**The rule:** Edit `skills/*/SKILL.md`. Never edit adapters or rules directly.

---

## Install Options by Experience Level

### Option A - Fast automated CLI (Recommended)

Use the zero-dependency Quench CLI to configure rules and hooks in seconds:

```bash
# Interactive mode (prompts for tool selection)
python quench.py init --target /your-project

# Direct install for a specific tool (e.g. Cursor)
python quench.py init --tool cursor --target /your-project

# Install all adapters and git validation hooks
python quench.py init --tool all --hooks --target /your-project
```

### Option B - Full plugin (recommended for Antigravity)

Gives you both always-on rules AND on-demand skills. Best experience.

```jsonc
// ~/.gemini/config/plugins.json
{
  "entries": [{ "path": "/path/to/quench" }]
}
```

What this loads every session, automatically and silently:
- `rules/AGENTS.md` - steel-mind + plaincast + leakguard + precision-output behavioral disciplines
- `skills/*/SKILL.md` descriptions - available for on-demand deep reference

### Option C - Skills only (Antigravity, no always-on rules)

```jsonc
// ~/.gemini/config/skills.json
{
  "entries": [{ "path": "/path/to/quench/skills" }]
}
```

Skills are loaded on-demand when the agent decides they are relevant.
Use this if you want quench skills available but prefer to control when they activate.

### Option D - Per-project (any team, via version control)

Place at project root for team-wide use - any team member who clones gets the rules:

```
your-project/
  .agents/
    plugins/
      quench/            <- clone quench here, or symlink
        plugin.json
        rules/
          AGENTS.md
        skills/
          steel-mind/
          plaincast/
          leakguard/
          precision-output/
```

---

## Installation per Tool

### Antigravity (native - best experience)
- **Global Plugin (Recommended):** Register quench path in `~/.gemini/config/plugins.json` (see Option A above).
- **Standalone Workspace Drop-in:**
  ```bash
  mkdir -p /your-project/.agents/rules
  cp adapters/antigravity/.agents/rules/AGENTS.md /your-project/.agents/rules/AGENTS.md
  ```

### Cursor AI - single file (simpler)
```bash
cp adapters/cursor/.cursorrules /your-project/.cursorrules
```

### Cursor AI - modular rules (recommended for Cursor 0.42+)
```bash
cp adapters/cursor/.cursor/rules/steel-mind.mdc /your-project/.cursor/rules/
cp adapters/cursor/.cursor/rules/plaincast.mdc   /your-project/.cursor/rules/
cp adapters/cursor/.cursor/rules/leakguard.mdc   /your-project/.cursor/rules/
cp adapters/cursor/.cursor/rules/precision-output.mdc /your-project/.cursor/rules/
```

### GitHub Copilot
```bash
cp adapters/copilot/copilot-instructions.md /your-project/.github/copilot-instructions.md
```

### Cline
```bash
cp adapters/cline/.clinerules/steel-mind.md  /your-project/.clinerules/
cp adapters/cline/.clinerules/plaincast.md   /your-project/.clinerules/
cp adapters/cline/.clinerules/leakguard.md   /your-project/.clinerules/
cp adapters/cline/.clinerules/precision-output.md /your-project/.clinerules/
```

### Windsurf
```bash
cp adapters/windsurf/.windsurfrules /your-project/.windsurfrules
```

### Claude.ai Projects
1. Open Claude.ai -> Projects -> your project -> Project Knowledge
2. Upload `adapters/claude/CLAUDE.md` as a knowledge file

### ChatGPT / Replit / any paste-in tool
1. Open `adapters/generic/system-prompt.md`
2. Copy the contents
3. Paste into Custom Instructions / System Prompt field

### Aider
```bash
cp adapters/aider/CONVENTIONS.md /your-project/CONVENTIONS.md
# Aider reads CONVENTIONS.md automatically as context
```

### Kilo Code
```bash
# Copy the config file to your project root
cp adapters/kilo/kilo.jsonc /your-project/kilo.jsonc

# Copy the rule files
mkdir -p /your-project/.kilo/rules
cp adapters/kilo/.kilo/rules/steel-mind.md /your-project/.kilo/rules/
cp adapters/kilo/.kilo/rules/plaincast.md  /your-project/.kilo/rules/
cp adapters/kilo/.kilo/rules/leakguard.md  /your-project/.kilo/rules/
cp adapters/kilo/.kilo/rules/precision-output.md /your-project/.kilo/rules/
```
The `kilo.jsonc` file references all rule files automatically.
For global rules (all projects): place `kilo.jsonc` at `~/.config/kilo/kilo.jsonc`.

### Zed AI
```bash
cp adapters/zed/.zedprompts/steel-mind.md  /your-project/.zedprompts/
cp adapters/zed/.zedprompts/plaincast.md   /your-project/.zedprompts/
cp adapters/zed/.zedprompts/leakguard.md   /your-project/.zedprompts/
cp adapters/zed/.zedprompts/precision-output.md /your-project/.zedprompts/
```

### JetBrains Junie
```bash
cp adapters/junie/.junie/rules/steel-mind.md  /your-project/.junie/rules/
cp adapters/junie/.junie/rules/plaincast.md   /your-project/.junie/rules/
cp adapters/junie/.junie/rules/leakguard.md   /your-project/.junie/rules/
cp adapters/junie/.junie/rules/precision-output.md /your-project/.junie/rules/
```

---

## What Each Adapter Contains

| Adapter | steel-mind | plaincast | leakguard | precision-output |
|---------|-----------|-----------|-----------|------------------|
| Antigravity `.agents/rules/AGENTS.md` | [x] | [x] | [x] | [x] |
| Cursor `.cursorrules` | [x] | [x] | [x] | [x] |
| Cursor `.cursor/rules/steel-mind.mdc` | [x] | - | - | - |
| Cursor `.cursor/rules/plaincast.mdc` | - | [x] | - | - |
| Cursor `.cursor/rules/leakguard.mdc` | - | - | [x] | - |
| Cursor `.cursor/rules/precision-output.mdc` | - | - | - | [x] |
| GitHub Copilot `copilot-instructions.md` | [x] | [x] | [x] | [x] |
| Cline `.clinerules/steel-mind.md` | [x] | - | - | - |
| Cline `.clinerules/plaincast.md` | - | [x] | - | - |
| Cline `.clinerules/leakguard.md` | - | - | [x] | - |
| Cline `.clinerules/precision-output.md` | - | - | - | [x] |
| Windsurf `.windsurfrules` | [x] | [x] | [x] | [x] |
| Claude.ai `CLAUDE.md` | [x] | [x] | [x] | [x] |
| Generic `system-prompt.md` | [x] | [x] | [x] | [x] |
| Aider `CONVENTIONS.md` | [x] | [x] | [x] | [x] |
| Kilo Code `kilo.jsonc` + `.kilo/rules/` | [x] | [x] | [x] | [x] |
| Zed `.zedprompts/steel-mind.md` | [x] | - | - | - |
| Zed `.zedprompts/plaincast.md` | - | [x] | - | - |
| Zed `.zedprompts/leakguard.md` | - | - | [x] | - |
| Zed `.zedprompts/precision-output.md` | - | - | - | [x] |
| Junie `.junie/rules/steel-mind.md` | [x] | - | - | - |
| Junie `.junie/rules/plaincast.md` | - | [x] | - | - |
| Junie `.junie/rules/leakguard.md` | - | - | [x] | - |
| Junie `.junie/rules/precision-output.md` | - | - | - | [x] |
