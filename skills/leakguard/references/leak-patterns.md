# Leak Patterns & Isolation Reference

This document catalogs the primary vectors of environment leaks, path exposure, and context bleed that occur when AI agents generate code and documentation.

---

## 1. Path & Filesystem Leaks

### Failure Mode: Host Drive Letters in Documentation
AI models operating on Windows frequently emit absolute drive paths (`C:\`, `D:\`, `E:\`) into setup guides and configuration templates.

<!-- leakguard:ignore-start -->
```
Wrong:
Add the following entry to your configuration:
{
  "path": "d:/workspace/project"
}

Right:
Add the following entry to your configuration:
{
  "path": "/path/to/project"
}
```
<!-- leakguard:ignore-end -->

### Failure Mode: Windows User Profile Paths
Hardcoded profile paths expose personal usernames, company domain user accounts, and operating system build versions.

<!-- leakguard:ignore-start -->
```
Wrong:
File saved to C:\Users\john_doe\.config\app\settings.json

Right:
File saved to %USERPROFILE%\.config\app\settings.json
or:
File saved to ~/.config/app/settings.json
```
<!-- leakguard:ignore-end -->

### Failure Mode: Mixed Separator Slop
AI models frequently mix forward and backward slashes in a single path string.

<!-- leakguard:ignore-start -->
```
Wrong:
C:\Users\username/projects/app\config.json

Right:
C:/Users/username/projects/app/config.json
or:
C:\Users\username\projects\app\config.json
```
<!-- leakguard:ignore-end -->

---

## 2. Cross-Project Context Bleed & Tool Pollution

### Failure Mode: Leaking Private Environment Tools into Public Projects
When an agent's runtime environment or system prompt contains custom MCP tools or instructions for another project, the agent may hallucinate those tools as dependencies or recommended practices in the current project.

```
Wrong (in a public utility or open-source repo):
"To run secondary queries, use custom_internal_cache_ask which provides 0ms cache hits."

Right:
"To run secondary queries, delegate to a focused research subagent or inspect local documentation."
```

### Failure Mode: Sibling Workspace Contamination
When an agent has access to multiple workspace folders in a single session, domain logic, table names, or module names from Workspace A can bleed into code written for Workspace B.

```
Wrong (in project B):
"Ensure the query joins with internal_crm_customers to populate metadata."

Right:
"Ensure the query joins with the customers table defined in schema.sql."
```

### Failure Mode: Global System Prompt Echo
Agents often echo internal constraints or meta-prompts from their system instructions directly into generated files or documentation comments.

```
Wrong:
// Generated following internal system rule RULE[db_pool_recovery] for PostgreSQL.

Right:
// Implement reconnect logic on severed database handles.
```

---

## 3. Secret & Credential Leaks

### Failure Mode: Hardcoded API Tokens in Fixtures or Documentation
AI agents writing integration tests or documentation examples often generate tokens that match real provider patterns, which triggers secret scanning alerts on public Git hosts.

<!-- leakguard:ignore-start -->
```
Wrong:
const token = "ghp_123456789012345678901234567890123456";

Right:
const token = process.env.GITHUB_TOKEN || "test-placeholder-token";
```
<!-- leakguard:ignore-end -->

### Failure Mode: Database Connection Strings with Credentials
Connection strings in example configuration files or unit tests frequently contain plain text credentials.

<!-- leakguard:ignore-start -->
```
Wrong:
DATABASE_URL="postgres://admin:Password123!@db.internal.corp:5432/prod"

Right:
DATABASE_URL="postgres://user:password@localhost:5432/dbname"
```
<!-- leakguard:ignore-end -->

---

## 4. Remediation Checklist

When an accidental leak occurs in a Git repository:

1. **Immediate Working Tree Fix:** Update the affected file to use neutral placeholders or generic references.
2. **Commit History Rewrite:** Use `git-filter-repo` to purge the leaked string across all historical commits:
   ```bash
   git filter-repo --replace-text replacements.txt --force
   ```
3. **Remote Force-Push:** Update the remote repository with sanitized history (`git push --force origin <branch>`).
4. **Credential Invalidation:** If an actual API token or password was exposed, immediately revoke and rotate the secret at the provider. Do not assume history rewriting alone secures an exposed credential.
5. **Gate Validation:** Add pattern detection to repository validation engines (e.g. `scripts/validate.py`) to prevent recurrence.
