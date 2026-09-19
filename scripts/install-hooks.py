#!/usr/bin/env python3
"""
Install git pre-commit hook for quench repository.
Configures git to use .githooks directory for repository hooks.
"""

import os
import subprocess
import sys
from pathlib import Path


def install_hooks() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    git_dir = repo_root / '.git'
    hook_file = repo_root / '.githooks' / 'pre-commit'

    if not git_dir.exists():
        print("Error: .git directory not found. Not a git repository.")
        return 1

    if not hook_file.exists():
        print(f"Error: Hook script not found at {hook_file}")
        return 1

    # Set executable permissions on Unix/macOS
    if os.name != 'nt':
        try:
            mode = os.stat(hook_file).st_mode
            os.chmod(hook_file, mode | 0o755)
        except Exception as e:
            print(f"Warning: Could not set executable permission: {e}")

    # Configure git core.hooksPath
    try:
        subprocess.run(
            ['git', 'config', 'core.hooksPath', '.githooks'],
            cwd=str(repo_root),
            check=True
        )
        print("Successfully configured git core.hooksPath -> .githooks")
        print("Pre-commit hook is now active for all commits.")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to configure git hooks path: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(install_hooks())
