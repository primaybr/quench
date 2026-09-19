---
name: leakguard
version: 1.0.2
description: Environment, path, and context isolation discipline. Prevents agents from leaking local host paths, drive letters, user profile directories, internal machine identities, credentials, and cross-project tools into public code, commits, and documentation.
---

# leakguard

> Environment, path, and context isolation discipline for AI agents.

AI models possess no intrinsic boundary between their prompt context, their host execution environment, and the repository files they produce. Left unconstrained, models leak local filesystem paths (`C:\Users\...`, `F:\...`), private usernames, authentication tokens, and foreign tool names from sibling projects or global system prompts directly into public documentation, configuration files, and git commits.

leakguard defines non-negotiable isolation gates and sanitization protocols to ensure all generated code, documentation, and commit messages remain hermetic, clean, and portable.

---

## The Rule Tiers

### Hard Gates (Non-Negotiable Invariants)
- **Zero Local Drive Leaks:** Never write absolute host drive letters (`C:\`, `F:\`, `/Users/`, `/home/`) into tracked files.
- **Zero Cross-Project Context Bleed:** Never bleed names, custom MCP tools, internal scripts, or private APIs from sibling projects or global prompts into project documentation or code.
- **Zero Secret Exposure:** Never commit or output bearer tokens, personal access tokens (`ghp_*`, `sk-*`), or database URIs with plain credentials.
- **Universal Forward Slashes:** Always use forward slashes `/` in file paths within documentation and cross-platform scripts.

### Purpose Gates (Contextual Justifications)
- **Local Troubleshooting In Chat:** Explicit host paths provided by the user may be referenced solely in transient chat replies to debug local execution errors, never committed to repository files.

---

## Protocol 1 - Path Neutralization & Generic Placeholders

Local paths break repository portability, expose private directory structures, and leak usernames.

### The Replacement Hierarchy

When referencing paths in documentation, installation guides, or configuration templates, apply this order of precedence:

1. **Relative Paths (Preferred):**
   ```
   ./config/settings.json
   scripts/validate.py
   ```
2. **Standard Environment Variables:**
   ```
   $PROJECT_ROOT/config
   $REPO_ROOT/scripts
   %USERPROFILE%/.config
   ```
3. **Canonical Documentation Placeholders:**
   Use neutral, standardized placeholders:
   ```
   /path/to/<project>
   /path/to/quench
   ~/.config/<tool>/
   ```

### Prohibited vs Allowed Patterns

<!-- leakguard:ignore-start -->
| Pattern | Status | Replacement |
|---------|--------|-------------|
| `D:\project` or `C:\project` | FORBIDDEN | `/path/to/<project>` or `./` |
| `C:\Users\username\...` | FORBIDDEN | `~/.config/...` or `%USERPROFILE%` |
| `/home/username/work/...` | FORBIDDEN | `/path/to/<project>` |
| `/path/to/quench` | ALLOWED | (Approved documentation placeholder) |
| `~/.gemini/config/` | ALLOWED | (Standard user configuration directory) |
<!-- leakguard:ignore-end -->

---

## Protocol 2 - Hermetic Project Isolation & Anti-Context Bleed

Agents operate with complex context: global system instructions, developer rules, available MCP servers, and multi-project workspaces. A critical failure mode is **context bleed**: hallucinating or transplanting private tools, scripts, or project names from one workspace into another.

### The Hermetic Boundary Invariant

Every repository must be strictly self-contained.

Before documenting or recommending any tool, function, script, or workflow:

1. **Verify Local Existence:** Does this tool, script, or package exist in this repository's package manifest, configuration, or codebase?
2. **Check Global Prompt Contamination:** Is this tool only present in your global system prompt or local environment? If so, never prescribe it in public project documentation or shared rules.
3. **Check Sibling Project Contamination:** Does this name belong to another workspace or private project? Never mention sibling projects unless explicitly directed by the user.

### Examples of Context Bleed

- **Wrong:** Documenting an internal MCP tool (e.g. a private cache lookup or scraping daemon) inside an open-source library that has no such dependency.
- **Right:** Prescribing standard language features, open-source dependencies, or repository-defined scripts.
- **Wrong:** Referencing private corporate repository names, internal URLs, or team identifiers in public commit messages.
- **Right:** Keeping commit messages and documentation scoped strictly to the public repository artifacts.

---

## Protocol 3 - Secret & Credential Redaction

Accidental secret leakage in commits is irreversible once pushed to public remotes without destructive history rewrites.

### Scanned Token Signatures

- GitHub Personal Access Tokens (`ghp_[A-Za-z0-9]{36}`)
- GitHub Fine-Grained Tokens (`github_pat_[A-Za-z0-9_]{82}`)
- OpenAI / LLM API Keys (`sk-[A-Za-z0-9_-]{20,}`)
- Anthropic API Keys (`sk-ant-[A-Za-z0-9_-]{20,}`)
- AWS Access Key IDs (`AKIA[A-Z0-9]{16}`)
- AWS Secret Access Key assignments (`aws_secret... = <40-char value>`)
- Stripe live/test keys (`sk_live_...`, `pk_live_...`, `rk_live_...`)
- Slack API tokens (`xoxb-...`, `xoxp-...`, `xoxa-...`)
- Twilio Account SIDs (`AC[a-f0-9]{32}`)
- Twilio Auth Token inline assignments (`TWILIO_AUTH_TOKEN = '...'`)
- SendGrid API keys (`SG.[A-Za-z0-9]{67}`)
- GCP service account private_key fragments (`"private_key": "-----BEGIN ... PRIVATE KEY-----"`)
- Raw Bearer tokens in prose or config (`Bearer <20+ chars>`)
- Generic API key assignments (`api_key = <20+ chars>`)
- Database URLs containing embedded passwords (`postgres://user:password@host/db`) <!-- leakguard:ignore-line -->
- Common `.env` secret assignments (`DB_PASSWORD=`, `SECRET_KEY=`, `JWT_SECRET=`, `APP_KEY=`, `AUTH_SECRET=`) with real non-placeholder values
- Private LAN IP addresses (`192.168.x.x`, `10.x.x.x`, RFC 1918 ranges)
- Localhost URLs pointing to non-generic application paths

### Redaction Pattern

Always sanitize secrets before writing documentation, tests, or examples:
<!-- leakguard:ignore-start -->
```
# Wrong:
DATABASE_URL="postgres://postgres:secret123@localhost:5432/app"
API_KEY="sk-abc1234567890abcdef1234567890"

# Right:
DATABASE_URL="postgres://user:password@localhost:5432/dbname"
API_KEY="sk-your-api-key-here"
```
<!-- leakguard:ignore-end -->

---

## Protocol 4 - Pre-Commit Diff & Commit Message Audit

Before executing `git commit` or writing release notes:

1. **Inspect Diffs:** Run `git diff --staged` and scan for:
   - Drive letters (`[A-Za-z]:/`)
   - Host usernames (`Users/`, `/home/`)
   - Private environment or project names
   - Unredacted credentials
2. **Commit Message Sanitization Gate:**
   - Commit messages are public and permanent in git history.
   - When fixing or removing a leak, NEVER mention the leaked secret, host path, or private project in the commit message (e.g. writing "remove secret XYZ" or "remove private-tool" permanently leaks the secret or name into git logs).
   - State the action generically: "remove external project references" or "sanitize sensitive credentials".
   - Enforce automated commit-msg hooks (`.githooks/commit-msg`) that reject any commit message containing host paths, tokens, or foreign project identifiers.
3. **Automated Validation:** Execute repository validation tools (`python scripts/validate.py`).

---

## Protocol 5 - Portable Path Formatting

Different operating systems handle file paths differently. Windows accepts forward slashes in almost all programming languages and shells, while Linux and macOS fail on backslashes.

- Always write file paths in documentation, shell scripts, and cross-platform configurations using forward slashes `/`.
- In Windows-specific documentation where backslashes are required for illustration, use generic placeholders (`C:\path\to\file`).
- Never mix backslashes and forward slashes in the same path string (`C:/path\to/project`).

---

## References

- [Leak Patterns](./references/leak-patterns.md) - Detailed catalog of path leaks, context bleed patterns, and remediation guides.
