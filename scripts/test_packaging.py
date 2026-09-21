#!/usr/bin/env python3
"""
Unit and integration tests for Quench packaging and pyproject.toml configuration.

Validates:
- PEP 517 build-system configuration
- PEP 621 project metadata and zero runtime dependencies
- CLI script entrypoint mapping (quench:main)
- Setuptools module inclusion and package data
- Module importability and entrypoint invocation
- File encoding and hygiene standards (Plaincast / Leakguard)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

# Try standard library tomllib (Python 3.11+) or tomli fallback
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
PYPROJECT_PATH = REPO_ROOT / 'pyproject.toml'
QUENCH_PY = REPO_ROOT / 'quench.py'

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.append(str(SCRIPTS_DIR))
sys.path.insert(0, str(REPO_ROOT))
sys.modules.pop('quench', None)
import quench


class TestPackagingConfiguration(unittest.TestCase):
    """Test suite for pyproject.toml and packaging metadata."""

    @classmethod
    def setUpClass(cls):
        cls.raw_bytes = PYPROJECT_PATH.read_bytes()
        cls.content = cls.raw_bytes.decode('utf-8')
        if tomllib is not None:
            cls.parsed = tomllib.loads(cls.content)
        else:
            cls.parsed = {}

    def test_01_pyproject_file_exists(self):
        """pyproject.toml must exist at the repository root."""
        self.assertTrue(PYPROJECT_PATH.is_file(), "pyproject.toml not found at repo root")

    def test_02_hygiene_and_encoding(self):
        """pyproject.toml must be UTF-8 without BOM, LF only, and Plaincast compliant."""
        self.assertFalse(self.raw_bytes.startswith(b'\xef\xbb\xbf'), "pyproject.toml must not have UTF-8 BOM")
        self.assertNotIn(b'\r\n', self.raw_bytes, "pyproject.toml must use LF line endings, not CRLF")

        # Plaincast checks
        disallowed_chars = {
            '\u2014': 'em-dash',
            '\u2013': 'en-dash',
            '\u2018': 'left-single-quote',
            '\u2019': 'right-single-quote',
            '\u201c': 'left-double-quote',
            '\u201d': 'right-double-quote',
        }
        for char, name in disallowed_chars.items():
            self.assertNotIn(char, self.content, f"Found prohibited character {name} in pyproject.toml")

        # Leakguard path checks (no hardcoded absolute drive paths)
        self.assertIsNone(
            re.search(r'[A-Za-z]:\\[A-Za-z0-9_.-]+', self.content),
            "Found host absolute path leak in pyproject.toml"
        )

    def test_03_build_system(self):
        """Build-system table must configure setuptools>=61.0 and build_meta."""
        if tomllib is None:
            self.skipTest("tomllib not available")

        build_system = self.parsed.get('build-system', {})
        self.assertIn('requires', build_system)
        requires = build_system['requires']
        self.assertTrue(
            any('setuptools>=61.0' in req for req in requires),
            f"setuptools>=61.0 missing in build-system requires: {requires}"
        )
        self.assertEqual(build_system.get('build-backend'), 'setuptools.build_meta')

    def test_04_project_metadata(self):
        """Project metadata table must define name, version 1.6.0, and zero dependencies."""
        if tomllib is None:
            self.skipTest("tomllib not available")

        project = self.parsed.get('project', {})
        self.assertEqual(project.get('name'), 'quench')
        self.assertEqual(project.get('version'), '1.6.0')
        self.assertIn('description', project)
        self.assertGreater(len(project['description']), 0)
        self.assertEqual(project.get('readme'), 'README.md')
        self.assertEqual(project.get('requires-python'), '>=3.8')
        self.assertIn('license', project)

        # Zero runtime dependencies verification
        dependencies = project.get('dependencies')
        self.assertIsNotNone(dependencies, "dependencies key must exist in [project]")
        self.assertEqual(dependencies, [], "Quench requires zero runtime dependencies")

    def test_05_cli_entrypoint(self):
        """CLI entrypoint quench must map to quench:main."""
        if tomllib is None:
            self.skipTest("tomllib not available")

        scripts = self.parsed.get('project', {}).get('scripts', {})
        self.assertIn('quench', scripts, "Missing 'quench' entry in [project.scripts]")
        self.assertEqual(scripts['quench'], 'quench:main')

    def test_06_setuptools_module_and_data(self):
        """Setuptools section must include quench module and package data."""
        if tomllib is None:
            self.skipTest("tomllib not available")

        tool_setuptools = self.parsed.get('tool', {}).get('setuptools', {})
        py_modules = tool_setuptools.get('py-modules') or tool_setuptools.get('py_modules')
        self.assertIsNotNone(py_modules, "py-modules missing in [tool.setuptools]")
        self.assertIn('quench', py_modules)

        package_data = tool_setuptools.get('package-data', {})
        self.assertIn('*', package_data, "Global package-data wildcard pattern missing")
        patterns = package_data['*']
        self.assertTrue(any('adapters' in p for p in patterns), "adapters missing from package-data")
        self.assertTrue(any('rules' in p for p in patterns), "rules missing from package-data")

    def test_07_module_import_and_attributes(self):
        """Root quench module must import cleanly and expose main and metadata."""
        self.assertTrue(hasattr(quench, '__file__'), "quench module has no __file__ attribute")
        self.assertTrue(callable(getattr(quench, 'main', None)), "quench.main is not callable")
        self.assertEqual(getattr(quench, '__version__', None), '1.6.0')

    def test_08_subcommand_execution_via_entrypoint(self):
        """Entrypoint logic must handle --version cleanly without error."""
        cmd = [sys.executable, str(QUENCH_PY), '--version']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Process failed: {res.stderr}")
        self.assertIn("quench", res.stdout.lower())

    def test_09_python_c_import_quench(self):
        """python -c 'import quench; print(quench.__file__)' must succeed cleanly."""
        cmd = [sys.executable, '-c', 'import quench; print(quench.__file__)']
        res = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Import command failed: {res.stderr}")
        self.assertTrue(res.stdout.strip().endswith('quench.py'))


if __name__ == '__main__':
    unittest.main()
