#!/usr/bin/env python3
"""
quench CLI - Unified zero-dependency command line interface for quench.

Commands:
  quench init     Initialize quench in any project repository.
  quench check    Run the 5-gate Quench validation engine on any target directory.
  quench update   Update installed Quench rules/adapters from source templates.
                  With --global: follow the latest release in ~/.quench and wire Claude Code.
  quench status   Inspect target directory for active adapters and git hooks.
  quench eval     Run automated adversarial evaluation runner against 12 scenarios.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Ensure scripts dir is on sys.path so validate can be imported
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate

VERSION = "quench 1.7.0"
__version__ = "1.7.0"

# ---------------------------------------------------------------------------
# Tool Adapter Definitions & Mappings
# ---------------------------------------------------------------------------

ADAPTER_MAP: Dict[str, Dict] = {
    'cursor': {
        'label': 'Cursor AI rules (.cursorrules, .cursor/rules/)',
        'files': [
            (Path('adapters/cursor/.cursorrules'), Path('.cursorrules')),
            (Path('adapters/cursor/.cursor/rules/steel-mind.mdc'), Path('.cursor/rules/steel-mind.mdc')),
            (Path('adapters/cursor/.cursor/rules/plaincast.mdc'), Path('.cursor/rules/plaincast.mdc')),
            (Path('adapters/cursor/.cursor/rules/leakguard.mdc'), Path('.cursor/rules/leakguard.mdc')),
            (Path('adapters/cursor/.cursor/rules/precision-output.mdc'), Path('.cursor/rules/precision-output.mdc')),
        ],
        'detection': [Path('.cursorrules'), Path('.cursor/rules')],
    },
    'copilot': {
        'label': 'GitHub Copilot instructions (.github/copilot-instructions.md)',
        'files': [
            (Path('adapters/copilot/copilot-instructions.md'), Path('.github/copilot-instructions.md')),
        ],
        'detection': [Path('.github/copilot-instructions.md'), Path('copilot-instructions.md')],
    },
    'kilo': {
        'label': 'Kilo Code rules (kilo.jsonc, .kilo/rules/)',
        'files': [
            (Path('adapters/kilo/kilo.jsonc'), Path('kilo.jsonc')),
            (Path('adapters/kilo/.kilo/rules/steel-mind.md'), Path('.kilo/rules/steel-mind.md')),
            (Path('adapters/kilo/.kilo/rules/plaincast.md'), Path('.kilo/rules/plaincast.md')),
            (Path('adapters/kilo/.kilo/rules/leakguard.md'), Path('.kilo/rules/leakguard.md')),
            (Path('adapters/kilo/.kilo/rules/precision-output.md'), Path('.kilo/rules/precision-output.md')),
        ],
        'detection': [Path('kilo.jsonc'), Path('.kilo/rules')],
    },
    'cline': {
        'label': 'Cline rules (.clinerules/)',
        'files': [
            (Path('adapters/cline/.clinerules/steel-mind.md'), Path('.clinerules/steel-mind.md')),
            (Path('adapters/cline/.clinerules/plaincast.md'), Path('.clinerules/plaincast.md')),
            (Path('adapters/cline/.clinerules/leakguard.md'), Path('.clinerules/leakguard.md')),
            (Path('adapters/cline/.clinerules/precision-output.md'), Path('.clinerules/precision-output.md')),
        ],
        'detection': [Path('.clinerules')],
    },
    'windsurf': {
        'label': 'Windsurf rules (.windsurfrules)',
        'files': [
            (Path('adapters/windsurf/.windsurfrules'), Path('.windsurfrules')),
        ],
        'detection': [Path('.windsurfrules')],
    },
    'claude': {
        'label': 'Claude.ai project knowledge (CLAUDE.md)',
        'files': [
            (Path('adapters/claude/CLAUDE.md'), Path('CLAUDE.md')),
        ],
        'detection': [Path('CLAUDE.md')],
    },
    'generic': {
        'label': 'Generic system prompt (system-prompt.md)',
        'files': [
            (Path('adapters/generic/system-prompt.md'), Path('system-prompt.md')),
        ],
        'detection': [Path('system-prompt.md')],
    },
    'aider': {
        'label': 'Aider conventions (CONVENTIONS.md)',
        'files': [
            (Path('adapters/aider/CONVENTIONS.md'), Path('CONVENTIONS.md')),
        ],
        'detection': [Path('CONVENTIONS.md')],
    },
    'zed': {
        'label': 'Zed AI prompts (.zedprompts/)',
        'files': [
            (Path('adapters/zed/.zedprompts/steel-mind.md'), Path('.zedprompts/steel-mind.md')),
            (Path('adapters/zed/.zedprompts/plaincast.md'), Path('.zedprompts/plaincast.md')),
            (Path('adapters/zed/.zedprompts/leakguard.md'), Path('.zedprompts/leakguard.md')),
            (Path('adapters/zed/.zedprompts/precision-output.md'), Path('.zedprompts/precision-output.md')),
        ],
        'detection': [Path('.zedprompts')],
    },
    'junie': {
        'label': 'JetBrains Junie rules (.junie/rules/)',
        'files': [
            (Path('adapters/junie/.junie/rules/steel-mind.md'), Path('.junie/rules/steel-mind.md')),
            (Path('adapters/junie/.junie/rules/plaincast.md'), Path('.junie/rules/plaincast.md')),
            (Path('adapters/junie/.junie/rules/leakguard.md'), Path('.junie/rules/leakguard.md')),
            (Path('adapters/junie/.junie/rules/precision-output.md'), Path('.junie/rules/precision-output.md')),
        ],
        'detection': [Path('.junie/rules'), Path('.junie')],
    },
    'antigravity': {
        'label': 'Antigravity agent rules (.agents/rules/AGENTS.md)',
        'files': [
            (Path('adapters/antigravity/.agents/rules/AGENTS.md'), Path('.agents/rules/AGENTS.md')),
        ],
        'detection': [Path('.agents/rules/AGENTS.md')],
    },
    'rules': {
        'label': 'Universal rules extract (AGENTS.md)',
        'files': [
            (Path('rules/AGENTS.md'), Path('AGENTS.md')),
        ],
        'detection': [Path('AGENTS.md'), Path('rules/AGENTS.md')],
    },
}

SUPPORTED_TOOLS = list(ADAPTER_MAP.keys()) + ['all']


def prompt_for_tool() -> str:
    """Prompt user interactively to select an adapter."""
    print("\nSelect a Quench tool adapter to initialize:")
    items = list(ADAPTER_MAP.items())
    for idx, (name, info) in enumerate(items, 1):
        print(f"  {idx:2d}) {name:<12} - {info['label']}")
    all_idx = len(items) + 1
    print(f"  {all_idx:2d}) {'all':<12} - Install all adapters")
    print()

    rules_idx = 1
    for i, (name, _) in enumerate(items, 1):
        if name == 'rules':
            rules_idx = i
            break

    try:
        raw = input(f"Choose [1-{all_idx}] (default: {rules_idx} [rules]): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)

    if not raw:
        return 'rules'

    if raw.isdigit():
        choice = int(raw)
        if 1 <= choice <= len(items):
            return items[choice - 1][0]
        if choice == all_idx:
            return 'all'

    raw_lower = raw.lower()
    if raw_lower in ADAPTER_MAP or raw_lower == 'all':
        return raw_lower

    print(f"Invalid selection '{raw}'. Defaulting to 'rules'.")
    return 'rules'


def copy_adapter_files(
    tool_name: str,
    quench_root: Path,
    target: Path,
    force: bool = False
) -> Tuple[int, List[str]]:
    """Copy template files for a given adapter into the target project."""
    tools_to_install = list(ADAPTER_MAP.keys()) if tool_name == 'all' else [tool_name]
    copied: List[str] = []

    for t in tools_to_install:
        info = ADAPTER_MAP[t]
        for src_rel, dst_rel in info['files']:
            src = quench_root / src_rel
            dst = target / dst_rel
            if not src.exists():
                print(f"Warning: Source template missing: {src_rel}")
                continue
            if dst.exists() and not force:
                print(f"  Skipped (already exists): {dst_rel} (use --force to overwrite)")
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied.append(dst_rel.as_posix())
            action_desc = "Overwritten" if dst.exists() and force else "Installed"
            print(f"  {action_desc}: {dst_rel.as_posix()}")

    return len(copied), copied


def install_git_hooks(quench_root: Path, target: Path, force: bool = False) -> Tuple[int, List[str]]:
    """Install git pre-commit and commit-msg hooks into the target project."""
    installed: List[str] = []
    source_hooks_dir = quench_root / '.githooks'
    if not source_hooks_dir.exists():
        print("Warning: Source .githooks directory not found in Quench installation.")
        return 0, installed

    hook_names = ['pre-commit', 'commit-msg']
    target_git = target / '.git'
    target_git_hooks = target_git / 'hooks'
    target_githooks = target / '.githooks'

    target_githooks.mkdir(parents=True, exist_ok=True)
    if target_git.is_dir():
        target_git_hooks.mkdir(parents=True, exist_ok=True)

    for name in hook_names:
        src = source_hooks_dir / name
        if not src.exists():
            continue

        # Target .githooks/ copy
        dst_githooks = target_githooks / name
        if not (dst_githooks.exists() and not force):
            shutil.copy2(src, dst_githooks)
            try:
                os.chmod(dst_githooks, os.stat(dst_githooks).st_mode | 0o755)
            except OSError:
                pass
            installed.append(dst_githooks.relative_to(target).as_posix())

        # Target .git/hooks/ copy if .git directory exists
        if target_git.is_dir():
            dst_git = target_git_hooks / name
            if not (dst_git.exists() and not force):
                shutil.copy2(src, dst_git)
                try:
                    os.chmod(dst_git, os.stat(dst_git).st_mode | 0o755)
                except OSError:
                    pass
                rel_git_path = dst_git.relative_to(target).as_posix()
                if rel_git_path not in installed:
                    installed.append(rel_git_path)

    # Configure core.hooksPath if git is initialized
    if target_git.is_dir():
        try:
            subprocess.run(
                ['git', 'config', 'core.hooksPath', '.githooks'],
                cwd=str(target),
                capture_output=True,
                check=False
            )
        except OSError:
            pass

    return len(installed), installed


def _refuse_source_repo(target: Path, command: str) -> bool:
    """Return True (after printing why) if target is the quench source repo itself.

    The source repo's CLAUDE.md and kilo.jsonc read rules/AGENTS.md live. Copying
    adapter templates over them would replace live rules with a stale snapshot.
    """
    if target.resolve() != REPO_ROOT.resolve():
        return False
    print(f"Refusing 'quench {command}' on the quench source repo: its CLAUDE.md and kilo.jsonc "
          "load rules/AGENTS.md live and need no copies. Target another project directory.")
    return True


def cmd_init(args: argparse.Namespace) -> int:
    """Handle the 'quench init' command."""
    target = Path(args.target).resolve()
    if _refuse_source_repo(target, 'init'):
        return 1
    target.mkdir(parents=True, exist_ok=True)
    tool = args.tool

    if not tool:
        if sys.stdin.isatty():
            tool = prompt_for_tool()
        else:
            print("Non-interactive session: defaulting to adapter 'rules'.")
            tool = 'rules'

    tool = tool.lower()
    if tool not in SUPPORTED_TOOLS:
        print(f"Error: Unknown tool '{tool}'. Supported options: {', '.join(SUPPORTED_TOOLS)}")
        return 1

    print(f"Initializing Quench ({tool}) in: {target}")
    count, _ = copy_adapter_files(tool, REPO_ROOT, target, force=args.force)

    if args.hooks:
        print("Installing Git validation hooks...")
        h_count, h_installed = install_git_hooks(REPO_ROOT, target, force=args.force)
        for h in h_installed:
            print(f"  Configured hook: {h}")

    print(f"\nQuench initialization complete. {count} file(s) configured.")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Handle the 'quench check' command."""
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Error: Target path does not exist: {target}")
        return 1

    print(f"Running Quench validation engine on: {target}")
    if args.fix:
        print("Auto-fix mode: ENABLED")
    if args.paths_only:
        print("Mode: Paths and secret leaks only")
    private_terms = validate.load_private_terms(getattr(args, 'private_term', None))
    if private_terms:
        # Count only: printing the terms would leak them into CI logs.
        print(f"Private terms: {len(private_terms)} configured")

    report = validate.scan_repository(target, check_paths_only=args.paths_only, auto_fix=args.fix,
                                      private_terms=private_terms)
    print(f"\nScanned {report.files_scanned} files across repository.")

    if report.passed:
        print("\n[PASS] All validation gates passed with zero violations.")
        return 0
    else:
        print(f"\n[FAIL] Found {len(report.violations)} violation(s):\n")
        validate.print_violations(report, target)
        print("\nPlease resolve all violations before committing.")
        return 1


# ---------------------------------------------------------------------------
# Global install: a stable clone that follows a release tag, wired into Claude Code
# ---------------------------------------------------------------------------

DEFAULT_REPO_URL = 'https://github.com/primaybr/quench'
DEFAULT_GLOBAL_REF = 'v1'
GLOBAL_IMPORT_RE = re.compile(r'^@(?P<path>.+[/\\]rules[/\\]AGENTS\.md)\s*$')


def _default_global_home() -> Path:
    return Path(os.environ.get('QUENCH_HOME') or (Path.home() / '.quench'))


def _default_claude_dir() -> Path:
    # Claude Code honours CLAUDE_CONFIG_DIR; fall back to ~/.claude
    return Path(os.environ.get('CLAUDE_CONFIG_DIR') or (Path.home() / '.claude'))


def _git(args: List[str], cwd: Optional[Path] = None, timeout: Optional[float] = None) -> subprocess.CompletedProcess:
    # GIT_TERMINAL_PROMPT=0: never wait for credentials (the update hook runs unattended)
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    return subprocess.run(['git', *args], cwd=str(cwd) if cwd else None, env=env, timeout=timeout,
                          capture_output=True, text=True, encoding='utf-8', errors='replace')


def _same_path(a: str, b: Path) -> bool:
    a = a[4:] if a.startswith('\\\\?\\') else a  # Windows junction targets may carry \\?\
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(str(b)))


def _link_target(path: Path) -> Optional[str]:
    """Return where a symlink or Windows junction points, or None if path is not a link."""
    is_junction = getattr(os.path, 'isjunction', lambda _p: False)(path)
    if path.is_symlink() or is_junction:
        try:
            return os.readlink(path)
        except OSError:
            return None
    return None


def _make_dir_link(link: Path, target: Path) -> None:
    """Create a directory link: a junction on Windows (no admin needed), a symlink elsewhere."""
    if os.name == 'nt':
        res = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)],
                             capture_output=True, text=True)
        if res.returncode != 0:
            raise OSError(res.stderr.strip() or res.stdout.strip())
    else:
        os.symlink(target, link, target_is_directory=True)


def _sync_global_clone(home: Path, repo_url: str, ref: str, timeout: Optional[float] = None) -> Tuple[bool, str]:
    """Clone or update the stable clone at home and check out ref. Returns (ok, message)."""
    if not (home / '.git').exists():
        if home.exists() and any(home.iterdir()):
            return False, f"{home} exists and is not a git clone; move it or pass --home."
        home.parent.mkdir(parents=True, exist_ok=True)
        res = _git(['clone', '--quiet', repo_url, str(home)])
        if res.returncode != 0:
            return False, f"git clone failed: {res.stderr.strip()}"
    else:
        dirty = _git(['status', '--porcelain', '--untracked-files=no'], cwd=home)
        if dirty.returncode != 0:
            return False, f"{home} is not a usable git clone: {dirty.stderr.strip()}"
        if dirty.stdout.strip():
            return False, (f"{home} has local changes; refusing to overwrite them. "
                           "Commit, stash or discard them, then run again.")
        # --force moves floating tags such as v1 to their new release commit
        res = _git(['fetch', '--quiet', '--tags', '--force', 'origin'], cwd=home, timeout=timeout)
        if res.returncode != 0:
            return False, f"git fetch failed: {res.stderr.strip()}"

    res = _git(['-c', 'advice.detachedHead=false', 'checkout', '--quiet', '--detach', ref], cwd=home)
    if res.returncode != 0:
        return False, f"git checkout {ref} failed: {res.stderr.strip()}"
    # Name the exact release (v1.6.3), not the floating tag (v1) that points at it
    exact = _git(['describe', '--tags', '--exact-match', '--match', 'v[0-9]*.[0-9]*.[0-9]*'], cwd=home)
    if exact.returncode == 0:
        return True, exact.stdout.strip()
    return True, _git(['describe', '--tags', '--always'], cwd=home).stdout.strip()


def _wire_claude_rules(home: Path, claude_dir: Path) -> str:
    """Make ~/.claude/CLAUDE.md import home/rules/AGENTS.md, without touching other content."""
    rules = home / 'rules' / 'AGENTS.md'
    claude_md = claude_dir / 'CLAUDE.md'
    text = claude_md.read_text(encoding='utf-8') if claude_md.exists() else ''
    for line in text.splitlines():
        m = GLOBAL_IMPORT_RE.match(line.strip())
        if m:
            if _same_path(os.path.expanduser(m.group('path')), rules):
                return f"rules: already imported in {claude_md}"
            return (f"rules: {claude_md} already imports quench rules from {m.group('path')}; "
                    "left unchanged (edit that line to switch to the stable clone)")
    claude_dir.mkdir(parents=True, exist_ok=True)
    # Prefer a ~/ path: it is what Claude Code documents for home imports, and it keeps
    # spaces in the user folder name (common on Windows) out of the import line.
    try:
        import_path = '~/' + rules.resolve().relative_to(Path.home().resolve()).as_posix()
    except ValueError:
        import_path = rules.as_posix()
    warning = ''
    if ' ' in import_path:
        warning = f" (warning: the path contains a space; if /memory does not list it, move the clone with --home)"
    block = ("\n# quench rules (managed by 'quench update --global')\n"
             f"@{import_path}\n")
    with open(claude_md, 'a', encoding='utf-8', newline='\n') as f:
        f.write(block if text.endswith('\n') or not text else '\n' + block)
    return f"rules: added import of {import_path} to {claude_md}{warning}"


def _wire_claude_skills(home: Path, claude_dir: Path) -> List[str]:
    """Link each home/skills/<name> into claude_dir/skills/<name>; never replace real folders."""
    skills_dir = claude_dir / 'skills'
    skills_dir.mkdir(parents=True, exist_ok=True)
    notes = []
    for skill in sorted(p for p in (home / 'skills').iterdir() if (p / 'SKILL.md').is_file()):
        link = skills_dir / skill.name
        current = _link_target(link)
        if current is not None and _same_path(current, skill):
            notes.append(f"skill {skill.name}: already linked")
            continue
        if current is not None:
            notes.append(f"skill {skill.name}: {link} links to {current}; left unchanged")
            continue
        if link.exists():
            notes.append(f"skill {skill.name}: {link} is a real folder; left unchanged")
            continue
        try:
            _make_dir_link(link, skill)
            notes.append(f"skill {skill.name}: linked")
        except OSError as e:
            notes.append(f"skill {skill.name}: could not link ({e})")
    return notes


# Identifies the SessionStart hook this command manages inside ~/.claude/settings.json
AUTO_HOOK_MARKER = 'update --global --auto'
AUTO_STAMP_NAME = 'quench-auto-update-stamp'
AUTO_FETCH_TIMEOUT = 20  # seconds; the hook must never hold up session start for long


def _auto_update_interval() -> float:
    try:
        return float(os.environ.get('QUENCH_AUTO_UPDATE_INTERVAL', 24 * 3600))
    except ValueError:
        return 24 * 3600


def _hook_command(home: Path, ref: str) -> str:
    python = Path(sys.executable).resolve().as_posix()
    script = (home / 'scripts' / 'quench.py').as_posix()
    cmd = f'"{python}" "{script}" {AUTO_HOOK_MARKER} --home "{home.as_posix()}"'
    return cmd if ref == DEFAULT_GLOBAL_REF else f'{cmd} --ref {ref}'


def _is_our_hook(entry: dict) -> bool:
    return any(AUTO_HOOK_MARKER in str(h.get('command', '')) for h in entry.get('hooks', []) if isinstance(h, dict))


def _load_settings(settings_path: Path) -> Tuple[Optional[dict], str]:
    if not settings_path.exists():
        return {}, ''
    try:
        data = json.loads(settings_path.read_text(encoding='utf-8'))
    except (ValueError, OSError) as e:
        return None, f"could not parse {settings_path} ({e}); left unchanged"
    if not isinstance(data, dict):
        return None, f"{settings_path} is not a JSON object; left unchanged"
    return data, ''


def _set_auto_hook(claude_dir: Path, home: Path, ref: str, enable: bool) -> str:
    """Install (enable=True) or remove the SessionStart auto-update hook in settings.json."""
    settings_path = claude_dir / 'settings.json'
    data, error = _load_settings(settings_path)
    if data is None:
        return f"auto-update: {error}"
    hooks = data.get('hooks') if isinstance(data.get('hooks'), dict) else {}
    entries = [e for e in hooks.get('SessionStart', []) if isinstance(e, dict)]
    others = [e for e in entries if not _is_our_hook(e)]
    wanted = {'matcher': 'startup',
              'hooks': [{'type': 'command', 'command': _hook_command(home, ref), 'timeout': 60}]}
    new_entries = others + [wanted] if enable else others
    if new_entries == entries:
        return "auto-update: " + ("already enabled" if enable else "not enabled")
    if new_entries:
        hooks['SessionStart'] = new_entries
    else:
        hooks.pop('SessionStart', None)
    if hooks:
        data['hooks'] = hooks
    else:
        data.pop('hooks', None)
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    if enable:
        return f"auto-update: enabled (SessionStart hook in {settings_path}, checks at most once a day)"
    return f"auto-update: disabled (hook removed from {settings_path})"


def _auto_update(home: Path, ref: str) -> None:
    """Hook entry point: quietly move the clone to the latest release, at most once per interval.

    Prints one line only when the release changed (SessionStart output is shown to Claude)
    and never fails the session: every problem is swallowed and retried after the interval.
    """
    stamp = home / '.git' / AUTO_STAMP_NAME
    if not stamp.parent.is_dir():
        return
    try:
        if time.time() - stamp.stat().st_mtime < _auto_update_interval():
            return
    except OSError:
        pass
    try:
        stamp.touch()  # before fetching, so an offline machine does not retry every session
        before = _git(['rev-parse', 'HEAD'], cwd=home, timeout=10).stdout.strip()
        ok, now = _sync_global_clone(home, DEFAULT_REPO_URL, ref, timeout=AUTO_FETCH_TIMEOUT)
        after = _git(['rev-parse', 'HEAD'], cwd=home, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return
    if ok and after != before:
        print(f"quench updated to {now}; its rules and skills apply from the next session.")


def cmd_update_global(args: argparse.Namespace) -> int:
    """Handle 'quench update --global': follow a release tag and wire Claude Code to it."""
    home = Path(args.home).expanduser().resolve() if args.home else _default_global_home().resolve()
    claude_dir = Path(args.claude_dir).expanduser() if args.claude_dir else _default_claude_dir()

    if args.auto:
        _auto_update(home, args.ref)
        return 0

    print(f"Updating global quench clone: {home} (ref {args.ref})")
    ok, message = _sync_global_clone(home, args.repo, args.ref)
    if not ok:
        print(f"Error: {message}")
        return 1
    print(f"  checked out: {message}")

    if args.no_claude:
        return 0
    if not (home / 'rules' / 'AGENTS.md').is_file() or not (home / 'skills').is_dir():
        print(f"Error: {home} has no rules/AGENTS.md or skills/; is --repo a quench repository?")
        return 1
    print(f"Wiring Claude Code: {claude_dir}")
    print(f"  {_wire_claude_rules(home, claude_dir)}")
    for note in _wire_claude_skills(home, claude_dir):
        print(f"  {note}")
    clone_cli = home / 'scripts' / 'quench.py'
    supports_auto = clone_cli.is_file() and "add_argument('--auto'" in clone_cli.read_text(encoding='utf-8', errors='replace')
    if not args.no_auto_update and not supports_auto:
        # An older release would reject --auto with exit code 2, which blocks Claude Code
        # sessions, so any existing hook is removed rather than left pointing at it.
        _set_auto_hook(claude_dir, home, args.ref, enable=False)
        print(f"  auto-update: not available in {message}; hook not installed")
        args.no_auto_update = True
    else:
        print(f"  {_set_auto_hook(claude_dir, home, args.ref, enable=not args.no_auto_update)}")
    if args.no_auto_update:
        print("\nDone. New Claude Code sessions use this release; re-run after each release to update.")
    else:
        print("\nDone. New Claude Code sessions use this release, and new releases install automatically "
              "(checked at most once a day). Opt out with --no-auto-update.")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    """Handle the 'quench update' command."""
    if getattr(args, 'global_', False):
        return cmd_update_global(args)
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Error: Target path does not exist: {target}")
        return 1
    if _refuse_source_repo(target, 'update'):
        return 1

    print(f"Checking for installed Quench adapters in: {target}")
    detected: List[str] = []
    for tool_name, info in ADAPTER_MAP.items():
        if any((target / p).exists() for p in info['detection']):
            detected.append(tool_name)

    if not detected:
        print("No installed Quench adapters detected.")
        print("Run 'quench init' to install an adapter.")
        return 0

    print(f"Found active adapter(s): {', '.join(detected)}")
    total_refreshed = 0
    for tool_name in detected:
        count, _ = copy_adapter_files(tool_name, REPO_ROOT, target, force=True)
        total_refreshed += count

    print(f"\nQuench update complete. Refreshed {total_refreshed} file(s) across {len(detected)} adapter(s).")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Handle the 'quench status' and 'quench info' commands."""
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Error: Target path does not exist: {target}")
        return 1

    print(f"Quench Status: {target}")
    detected: List[Tuple[str, List[str]]] = []
    for tool_name, info in ADAPTER_MAP.items():
        matching = [p.as_posix() for p in info['detection'] if (target / p).exists()]
        if matching:
            detected.append((tool_name, matching))

    print("Active Adapters:")
    if detected:
        for tool_name, paths in detected:
            print(f"  - {tool_name:<12} (found: {', '.join(paths)})")
    else:
        print("  none detected (run 'quench init' to install)")

    # Git hooks status
    git_dir = target / '.git'
    git_hooks_dir = git_dir / 'hooks'
    githooks_dir = target / '.githooks'
    active_hooks: List[Tuple[str, List[str]]] = []
    for h in ['pre-commit', 'commit-msg']:
        found_in = []
        if (githooks_dir / h).exists():
            found_in.append(f".githooks/{h}")
        if (git_hooks_dir / h).exists():
            found_in.append(f".git/hooks/{h}")
        if found_in:
            active_hooks.append((h, found_in))

    print("Git Hooks:")
    if active_hooks:
        for h, locations in active_hooks:
            print(f"  - {h:<12} (installed: {', '.join(locations)})")
    else:
        print("  none installed (run 'quench init --hooks' to install)")

    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    """Handle the 'quench eval' command."""
    import eval_adversarial

    eval_argv: List[str] = []
    if args.input_path:
        eval_argv.extend(['--input', args.input_path])
    elif args.self_test:
        eval_argv.append('--self-test')
    else:
        eval_argv.append('--self-test')

    if args.json_output:
        eval_argv.append('--json')

    return eval_adversarial.main(eval_argv)


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="quench",
        description="quench - Zero-dependency AI agent rules and behavioral hardening toolkit",
    )
    parser.add_argument('-v', '--version', action='version', version=VERSION)

    subparsers = parser.add_subparsers(dest='command', help='Sub-commands')

    # init
    p_init = subparsers.add_parser('init', help='Initialize quench rules/adapters in a project')
    p_init.add_argument('-t', '--tool', choices=SUPPORTED_TOOLS, help='Tool adapter to initialize')
    p_init.add_argument('-d', '--target', default='.', help='Target project directory (default: current dir)')
    p_init.add_argument('--hooks', action='store_true', help='Install git pre-commit and commit-msg hooks')
    p_init.add_argument('-f', '--force', action='store_true', help='Overwrite existing files')

    # check
    p_check = subparsers.add_parser('check', help='Run validation engine on a directory')
    p_check.add_argument('-d', '--target', default='.', help='Directory to validate (default: current dir)')
    p_check.add_argument('--fix', action='store_true', help='Automatically fix plaincast and path issues')
    p_check.add_argument('--paths-only', action='store_true', help='Only check path leaks and secrets')
    p_check.add_argument('--private-term', action='append', default=[], metavar='TERM',
                         help='Private tool/project name to flag as context bleed (repeatable; '
                              'also read from $QUENCH_PRIVATE_TERMS and $QUENCH_PRIVATE_TERMS_FILE)')

    # update
    p_update = subparsers.add_parser('update', help='Update existing installed adapters from source templates')
    p_update.add_argument('-d', '--target', default='.', help='Target project directory (default: current dir)')
    p_update.add_argument('--global', dest='global_', action='store_true',
                          help='Update the stable global clone (default ~/.quench or $QUENCH_HOME) to the '
                               'latest release and wire it into Claude Code (~/.claude)')
    p_update.add_argument('--ref', default=DEFAULT_GLOBAL_REF,
                          help=f'With --global: tag or branch to follow (default: {DEFAULT_GLOBAL_REF}, the latest 1.x release)')
    p_update.add_argument('--home', help='With --global: location of the stable clone')
    p_update.add_argument('--repo', default=DEFAULT_REPO_URL, help='With --global: repository to clone')
    p_update.add_argument('--claude-dir', help='With --global: Claude Code config dir (default ~/.claude or $CLAUDE_CONFIG_DIR)')
    p_update.add_argument('--no-claude', action='store_true', help='With --global: update the clone only')
    p_update.add_argument('--no-auto-update', action='store_true',
                          help='With --global: do not install (or remove) the Claude Code hook that '
                               'installs new releases automatically, at most once a day')
    # Internal: run by that SessionStart hook. Throttled, silent unless a new release was installed.
    p_update.add_argument('--auto', action='store_true', help=argparse.SUPPRESS)

    # status / info
    p_status = subparsers.add_parser('status', aliases=['info'], help='Inspect target directory for Quench rules and hooks')
    p_status.add_argument('-d', '--target', default='.', help='Target project directory (default: current dir)')

    # eval
    p_eval = subparsers.add_parser('eval', help='Run automated adversarial evaluation runner against 12 scenarios')
    p_eval.add_argument('--self-test', action='store_true', default=False, help='Run built-in baseline and compliant fixtures (default)')
    p_eval.add_argument('--input', dest='input_path', help='Path to JSON/JSONL completions file to evaluate')
    p_eval.add_argument('--json', dest='json_output', action='store_true', help='Output machine-readable JSON results')

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == 'init':
        return cmd_init(args)
    elif args.command == 'check':
        return cmd_check(args)
    elif args.command == 'update':
        return cmd_update(args)
    elif args.command in ('status', 'info'):
        return cmd_status(args)
    elif args.command == 'eval':
        return cmd_eval(args)
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
