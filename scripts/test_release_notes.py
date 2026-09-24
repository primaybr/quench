#!/usr/bin/env python3
"""Tests for scripts/release_notes.py (tag/version check and CHANGELOG extraction)."""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import release_notes as rn

CHANGELOG = """# CHANGELOG

## [1.8.0] 2026-10-01 - Faster Scans

### Added
- Thing one.

---

## [1.7.1] 2026-09-25

### Fixed
- Thing two.

## [1.7.0] 2026-09-24

### Added
- Older.
"""


class TestReleaseNotes(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='quench-rel-'))
        (self.root / 'CHANGELOG.md').write_text(CHANGELOG, encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def set_version(self, v):
        (self.root / 'pyproject.toml').write_text(
            f'[build-system]\nrequires = []\n\n[project]\nname = "quench"\nversion = "{v}"\n', encoding='utf-8')

    def test_section_with_title(self):
        self.set_version('1.8.0')
        title, notes = rn.build_release('v1.8.0', self.root)
        self.assertEqual(title, 'v1.8.0 - Faster Scans')
        self.assertEqual(notes, "### Added\n- Thing one.\n")

    def test_section_without_title_uses_tag(self):
        self.set_version('1.7.1')
        title, notes = rn.build_release('v1.7.1', self.root)
        self.assertEqual(title, 'v1.7.1')
        self.assertIn('Thing two.', notes)
        self.assertNotIn('Older.', notes)

    def test_last_section_runs_to_end(self):
        self.set_version('1.7.0')
        _, notes = rn.build_release('v1.7.0', self.root)
        self.assertEqual(notes, "### Added\n- Older.\n")

    def test_tag_must_match_pyproject(self):
        self.set_version('1.7.1')
        with self.assertRaisesRegex(rn.ReleaseError, 'does not match pyproject.toml version 1.7.1'):
            rn.build_release('v1.8.0', self.root)

    def test_missing_section_fails(self):
        self.set_version('1.9.0')
        with self.assertRaisesRegex(rn.ReleaseError, r"no '## \[1.9.0\]' section"):
            rn.build_release('v1.9.0', self.root)

    def test_floating_and_malformed_tags_rejected(self):
        for tag in ('v1', 'v1.7', '1.7.0', 'v1.7.0-beta'):
            with self.subTest(tag=tag), self.assertRaises(rn.ReleaseError):
                rn.version_from_tag(tag)

    def test_version_read_only_from_project_table(self):
        text = '[tool.other]\nversion = "9.9.9"\n\n[project]\nversion = "1.2.3"\n'
        self.assertEqual(rn.pyproject_version(text), '1.2.3')

    def test_cli_writes_files(self):
        self.set_version('1.8.0')
        notes, title = self.root / 'n.md', self.root / 't.txt'
        rc = rn.main(['v1.8.0', '--notes-out', str(notes), '--title-out', str(title), '--root', str(self.root)])
        self.assertEqual(rc, 0)
        self.assertEqual(title.read_text(encoding='utf-8'), 'v1.8.0 - Faster Scans\n')
        self.assertIn('Thing one.', notes.read_text(encoding='utf-8'))

    def test_current_repo_release_is_consistent(self):
        """The repo's own pyproject version must have a CHANGELOG section."""
        version = rn.pyproject_version((REPO_ROOT / 'pyproject.toml').read_text(encoding='utf-8'))
        title, notes = rn.build_release('v' + version, REPO_ROOT)
        self.assertTrue(title.startswith('v' + version))
        self.assertTrue(notes.strip())


if __name__ == '__main__':
    unittest.main()
