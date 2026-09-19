# leakguard - Path, Environment & Context Sanitization
# quench | Source: skills/leakguard/SKILL.md

Apply these isolation rules to all responses and file writes in this project.

## Path Neutralization

Never output or commit host drive letters (`C:\`, `F:\`) or user profiles (`Users/`, `/home/`).
Always use generic placeholders (`/path/to/<project>`, `~/.config/<tool>/`) or relative paths.
Never mix forward and backward slashes in paths; use `/` universally across all platforms.

## Hermetic Project Isolation

Maintain hermetic project isolation: never leak private tools, MCP names, internal APIs,
or sibling project names from the host environment into repository files, docs, or commits.
Every repository must be self-contained; only reference tools and dependencies defined locally.

## Secret Redaction

Never commit or output authentication tokens (`ghp_*`, `github_pat_*`, `sk-*`, `bearer *`)
or database connection strings with embedded passwords.
Use environment variables for all secrets.

## Commit Message Hygiene

Never name leaked tokens, host paths, or private project names in commit messages or PR descriptions.
State fixes generically ("sanitize credentials", "remove external project references").
