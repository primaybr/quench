#!/usr/bin/env python3
"""
quench CLI - Top-level runner
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_scripts_quench = SCRIPTS_DIR / 'quench.py'

if _scripts_quench.is_file():
    _spec = importlib.util.spec_from_file_location('quench_cli', _scripts_quench)
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        main = _mod.main
        for _key in dir(_mod):
            if not _key.startswith('_'):
                globals()[_key] = getattr(_mod, _key)
else:
    def main(argv: list[str] | None = None) -> int:
        print("quench CLI: scripts/quench.py not found.")
        return 1

__version__ = "1.6.3"

if __name__ == '__main__':
    sys.exit(main())
