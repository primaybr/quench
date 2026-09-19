# Platform Traps - OS-Specific Failure Modes Reference

A field guide to platform-specific pitfalls that silently break AI agent
operations. Used by the steel-mind skill.

---

## Windows Traps

### File and Path Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| Backslash in string literals | `"C:\new\file.txt"` - `\n` and `\f` are escape sequences | Use raw strings or forward slashes: `"C:/new/file.txt"` |
| Mixed path separators | `C:\Users/name\file` | Never mix - pick one and use a path library |
| Max path length (260 chars) | `FileNotFoundException` on deep nested paths | Enable long paths in registry or use `\\?\` prefix |
| Reserved filenames | `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9` cannot be used as filenames | Avoid these names in any path segment |
| Trailing dot/space in filenames | `file.txt.` or `file .txt` - Windows strips them silently | Normalize filenames before writing |
| Case-insensitive filesystem | `Config.php` and `config.php` are the same file | Standardize casing; don't rely on case for disambiguation |

### Encoding Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| PowerShell UTF-8 BOM | `Set-Content -Encoding UTF8` writes BOM `EF BB BF` | Use `New-Object System.Text.UTF8Encoding $false` |
| Console output encoding | `chcp` determines console encoding - default is often not UTF-8 | `chcp 65001` or set `[Console]::OutputEncoding` |
| `Get-Content` line ending handling | `Get-Content` returns arrays of lines, stripping line endings | Use `Get-Content -Raw` to preserve raw content |
| CRLF in shell scripts | Scripts created on Windows and run on Linux fail silently | Strip CR: `$content -replace "\`r\`n", "\`n"` |

### Process and Execution Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| Running EXE is locked | `Access denied` / `SharingViolation` when overwriting a running binary | Kill the process/daemon task before rebuilding |
| Non-daemon child process death | Background workers die when parent command task ends | Set `IsDaemon: true` for long-running processes |
| Execution policy blocking scripts | `File cannot be loaded because running scripts is disabled` | Use `pwsh -Command` instead of `.ps1` invocation |
| UAC elevation needed | Silent failure on operations requiring admin rights | Detect and surface the error; don't swallow it |
| Windows Defender scan delay | File appears to write but is temporarily locked by AV scan | Add small retry with backoff for newly written executables |

### PowerShell-Specific

| Trap | Symptom | Fix |
|------|---------|-----|
| `$?` vs `$LASTEXITCODE` | `$?` is true even if external command failed - use `$LASTEXITCODE` | Always check `$LASTEXITCODE -ne 0` after native commands |
| Implicit output capture | Every expression in PowerShell is output - accidental output corrupts pipe | Use `[void]($expr)` or `$null = $expr` to suppress |
| String interpolation with `$` | `"Cost is $100"` tries to expand `$1` | Escape: `"Cost is `$100"` or use single quotes |
| `Set-Location` (cd) scope | Changing directory in a script does not affect the caller's session | Never rely on `cd` side effects across script boundaries |

---

## Linux / macOS Traps

### File and Path Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| Case-sensitive filesystem | `Config.php` != `config.php` - imports fail silently | Standardize all filenames to lowercase |
| Symlink resolution | `realpath` vs `readlink` behavior differs | Use `realpath` for canonical path resolution |
| Executable bit missing | Script fails with `Permission denied` | `chmod +x script.sh` after creating |
| Shebang with CRLF | `#!/usr/bin/env php\r` - interpreter not found | Ensure shebang line is LF only |
| `~` not expanded in scripts | `~/file` in a script passed as argument is not expanded | Use `$HOME/file` or explicit expansion |

### Encoding Traps

| Trap | Symptom | Fix |
|------|---------|-----|
| Locale not set | Non-ASCII chars mangled in scripts | Set `LANG=en_US.UTF-8` and `LC_ALL=en_US.UTF-8` |
| Byte range in `sed`/`awk` | Multi-byte characters split incorrectly | Use tools that understand UTF-8 or process by line |

---

## Cross-Platform Traps

### Git and Version Control

| Trap | Symptom | Fix |
|------|---------|-----|
| `autocrlf=true` on Windows | Git silently converts LF to CRLF on checkout | Set per-repo `.gitattributes` with explicit line ending rules |
| `.gitattributes` not committed | Team members get different line endings | Commit `.gitattributes` with the repo |
| BOM in tracked files | Diff tools show phantom changes | Strip BOM before committing text files |

### Docker and Containers

| Trap | Symptom | Fix |
|------|---------|-----|
| Volume mount path | `C:\path` vs `/path` in docker-compose volumes | Use compose variable substitution for cross-platform paths |
| Line endings in copied scripts | `COPY script.sh` then `RUN ./script.sh` fails on CRLF | Add `RUN sed -i 's/\r//' script.sh` after COPY or fix at source |
| Windows host file locking | Container cannot access files locked by Windows process | Stop the Windows process before the container accesses the file |

---

## Database-Specific Traps (PostgreSQL)

| Trap | Symptom | Fix |
|------|---------|-----|
| Ambiguous column in JOIN | `ERROR: column reference is ambiguous` | Qualify all column references: `table.column` |
| `LIMIT` before `OFFSET` | Some ORMs reverse the order | Always write `LIMIT x OFFSET y` in that order |
| Connection severance | `FATAL: terminating connection due to administrator command` | Implement auto-reconnect outside active transactions |
| `IN` clause with empty array | `WHERE id IN ()` is a syntax error | Check array length before building the query |
| Timezone-naive timestamps | Timestamps stored as local time cause DST bugs | Always store and retrieve as UTC; convert at display layer |
