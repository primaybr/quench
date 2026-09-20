#!/usr/bin/env python3
"""
quench CLI - Unified zero-dependency command line interface for quench.

Commands:
  quench init     Initialize quench in any project repository.
  quench check    Run the 5-gate Quench validation engine on any target directory.
  quench update   Update installed Quench rules/adapters from source templates.
  quench status   Inspect target directory for active adapters and git hooks.
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Ensure scripts dir is on sys.path so validate can be imported
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate

VERSION = "quench 1.5.4"

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


def cmd_init(args: argparse.Namespace) -> int:
    """Handle the 'quench init' command."""
    target = Path(args.target).resolve()
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

    report = validate.scan_repository(target, check_paths_only=args.paths_only, auto_fix=args.fix)
    print(f"\nScanned {report.files_scanned} files across repository.")

    if report.passed:
        print("\n[PASS] All validation gates passed with zero violations.")
        return 0
    else:
        print(f"\n[FAIL] Found {len(report.violations)} violation(s):\n")
        for v in report.violations:
            print(f"  {v}")
        print("\nPlease resolve all violations before committing.")
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    """Handle the 'quench update' command."""
    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Error: Target path does not exist: {target}")
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

    # update
    p_update = subparsers.add_parser('update', help='Update existing installed adapters from source templates')
    p_update.add_argument('-d', '--target', default='.', help='Target project directory (default: current dir)')

    # status / info
    p_status = subparsers.add_parser('status', aliases=['info'], help='Inspect target directory for Quench rules and hooks')
    p_status.add_argument('-d', '--target', default='.', help='Target project directory (default: current dir)')

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
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
