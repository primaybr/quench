# leakguard - Path, Environment & Context Sanitization
# quench | JetBrains Junie rules

## Path Neutralization
Never output host drive letters (`C:\`, `F:\`) or user profiles (`Users/`, `/home/`).
Use generic placeholders (`/path/to/<project>`, `~/.config/<tool>/`) or relative paths.
Never mix forward and backward slashes in paths; use `/` universally across all platforms.

## Hermetic Project Isolation
Maintain hermetic project isolation: never leak private tools, MCP names, internal APIs,
or sibling project names from the host environment into repository files or commits.
Every repository must be self-contained; only reference tools and dependencies defined locally.

## Secret Redaction
Never commit or output authentication tokens (`ghp_*`, `github_pat_*`, `sk-*`, `bearer *`)
or database connection strings with embedded passwords.
Sanitize all secrets to environment variables.

## Commit Message Hygiene
Never name leaked tokens, host paths, or private project names in commit messages or PR descriptions.
State fixes generically ("sanitize credentials", "remove external project references").
