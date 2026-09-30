#!/usr/bin/env python3
"""
Tests for the .quenchignore feature (load_quench_ignore, _matches_ignore, scan_repository,
quench init template, and validate.py --no-ignore CLI flag).
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate
from validate import _matches_ignore, load_quench_ignore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_git_repo(root: Path) -> None:
    """Initialise a bare git repo, add all files, and make an initial commit."""
    import os
    env_extra = {'GIT_AUTHOR_NAME': 'test', 'GIT_AUTHOR_EMAIL': 'test@test.invalid',
                 'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 'test@test.invalid'}
    env = {**os.environ, **env_extra}
    devnull = subprocess.DEVNULL

    def _run(*cmd, use_env=False):
        subprocess.run(list(cmd), stdout=devnull, stderr=devnull,
                       env=(env if use_env else None), check=True)

    _run('git', 'init', str(root))
    _run('git', '-C', str(root), 'config', 'user.email', 'test@test.invalid')
    _run('git', '-C', str(root), 'config', 'user.name', 'test')
    _run('git', '-C', str(root), 'add', '-A')
    _run('git', '-C', str(root), 'commit', '-m', 'init', use_env=True)


# ---------------------------------------------------------------------------
# Unit tests for load_quench_ignore
# ---------------------------------------------------------------------------

class TestLoadQuenchIgnore(unittest.TestCase):

    def test_load_empty(self):
        """No .quenchignore -> returns empty frozenset."""
        with tempfile.TemporaryDirectory() as tmp:
            result = load_quench_ignore(Path(tmp))
        self.assertEqual(result, frozenset())

    def test_load_patterns(self):
        """Parses comments, blank lines, and three real patterns correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.quenchignore').write_text(
                "# this is a comment\n"
                "\n"
                "vendor/\n"
                "*.min.js\n"
                "dist/\n",
                encoding='utf-8',
            )
            result = load_quench_ignore(root)
        self.assertEqual(result, frozenset({'vendor/', '*.min.js', 'dist/'}))


# ---------------------------------------------------------------------------
# Unit tests for _matches_ignore
# ---------------------------------------------------------------------------

class TestMatchesIgnore(unittest.TestCase):

    def test_matches_dir_pattern(self):
        """Trailing-slash pattern matches any file inside that directory."""
        self.assertTrue(
            _matches_ignore(Path('vendor/foo/bar.md'), frozenset(['vendor/']))
        )

    def test_matches_glob_extension(self):
        """Glob pattern matches on the bare filename even in a subdirectory."""
        self.assertTrue(
            _matches_ignore(Path('src/app.min.js'), frozenset(['*.min.js']))
        )

    def test_no_match(self):
        """A plain source file does not match vendor/ or *.min.js."""
        self.assertFalse(
            _matches_ignore(Path('src/main.py'), frozenset(['vendor/', '*.min.js']))
        )


# ---------------------------------------------------------------------------
# Integration tests using scan_repository
# ---------------------------------------------------------------------------

class TestScanRespectIgnore(unittest.TestCase):

    def _make_fixture(self, tmp: str) -> Path:
        """Create a minimal repo with a clean file and a violating file under vendor/."""
        root = Path(tmp)
        (root / 'src').mkdir()
        (root / 'src' / 'main.md').write_text("# Hello world\n", encoding='utf-8')
        (root / 'vendor').mkdir()
        # em-dash character triggers a plaincast violation
        (root / 'vendor' / 'lib.md').write_text("# Library \u2014 note\n", encoding='utf-8')
        return root

    def test_scan_respects_ignore(self):
        """vendor/ in .quenchignore -> zero violations, only src/main.md scanned."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_fixture(tmp)
            (root / '.quenchignore').write_text("vendor/\n", encoding='utf-8')
            _make_git_repo(root)
            report = validate.scan_repository(root)
        self.assertEqual(len(report.violations), 0, report.violations)
        self.assertEqual(report.files_scanned, 1)

    def test_scan_no_ignore_flag(self):
        """no_ignore=True bypasses .quenchignore so vendor/lib.md is scanned and fails."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._make_fixture(tmp)
            (root / '.quenchignore').write_text("vendor/\n", encoding='utf-8')
            _make_git_repo(root)
            report = validate.scan_repository(root, no_ignore=True)
        self.assertEqual(len(report.violations), 1, report.violations)


# ---------------------------------------------------------------------------
# Integration test: quench init writes .quenchignore template
# ---------------------------------------------------------------------------

class TestQuenchInitWritesTemplate(unittest.TestCase):

    def test_quench_init_writes_template(self):
        """quench init on a new dir creates .quenchignore with the expected header."""
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'quench.py'), 'init',
                 '--tool', 'generic', '--target', tmp],
                capture_output=True, text=True,
            )
            ignore_path = Path(tmp) / '.quenchignore'
            self.assertTrue(ignore_path.exists(), 'Expected .quenchignore to be created')
            content = ignore_path.read_text(encoding='utf-8')
            self.assertIn('# .quenchignore', content)


# ---------------------------------------------------------------------------
# CLI test: validate.py --no-ignore exits 1 on the violating fixture
# ---------------------------------------------------------------------------

class TestCliNoIgnoreFlag(unittest.TestCase):

    def test_cli_no_ignore_flag(self):
        """validate.py --root <dir> --no-ignore exits 1 when vendor/ contains violations."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'src').mkdir()
            (root / 'src' / 'main.md').write_text("# Hello world\n", encoding='utf-8')
            (root / 'vendor').mkdir()
            (root / 'vendor' / 'lib.md').write_text("# Library \u2014 note\n", encoding='utf-8')
            (root / '.quenchignore').write_text("vendor/\n", encoding='utf-8')
            _make_git_repo(root)

            result = subprocess.run(
                [sys.executable, str(SCRIPTS_DIR / 'validate.py'),
                 '--root', str(root), '--no-ignore'],
                capture_output=True, text=True,
            )
        self.assertEqual(result.returncode, 1,
                         f"Expected exit 1 but got {result.returncode}\n{result.stdout}\n{result.stderr}")


if __name__ == '__main__':
    unittest.main()
