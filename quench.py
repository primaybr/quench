#!/usr/bin/env python3
"""
quench CLI - Top-level runner
"""
import sys
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent / 'scripts'
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from quench import main

if __name__ == '__main__':
    sys.exit(main())
