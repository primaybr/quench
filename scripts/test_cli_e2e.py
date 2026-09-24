#!/usr/bin/env python3
"""
End-to-End External Contributor Sanity Suite for quench CLI.

Simulates a fresh external contributor environment outside the Quench repository:
- Isolated temp directories with fresh git repositories
- Verification of adapter initialization (single, modular, all)
- Git hook configuration and executable permissions
- Repository scanning, violation detection, and auto-fix capabilities
- Status inspection and source template update workflows
"""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
QUENCH_PY = SCRIPTS_DIR / 'quench.py'

# Ensure scripts dir is in sys.path
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import quench


class TestQuenchCliE2E(unittest.TestCase):
    """External contributor end-to-end sanity tests."""

    def _init_git_repo(self, target: Path):
        """Initialize a fresh git repository in the target directory."""
        subprocess.run(
            ['git', 'init'],
            cwd=str(target),
            capture_output=True,
            check=True
        )

    def test_01_init_cursor(self):
        """quench init --tool cursor creates .cursorrules and .cursor/rules/*.mdc."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            cmd = [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")

            # Verify .cursorrules
            cursorrules = target / '.cursorrules'
            self.assertTrue(cursorrules.is_file(), ".cursorrules should be created")
            self.assertGreater(cursorrules.stat().st_size, 0)

            # Verify modular rules in .cursor/rules/
            rules_dir = target / '.cursor' / 'rules'
            self.assertTrue(rules_dir.is_dir(), ".cursor/rules directory should exist")
            expected_rules = [
                'steel-mind.mdc',
                'plaincast.mdc',
                'leakguard.mdc',
                'precision-output.mdc',
            ]
            for rule_file in expected_rules:
                rule_path = rules_dir / rule_file
                self.assertTrue(rule_path.is_file(), f"Missing rule file: {rule_file}")
                self.assertGreater(rule_path.stat().st_size, 0)

    def test_02_init_kilo(self):
        """quench init --tool kilo creates kilo.jsonc and .kilo/rules/*.md."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            cmd = [sys.executable, str(QUENCH_PY), 'init', '--tool', 'kilo', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")

            # Verify kilo.jsonc
            kilo_jsonc = target / 'kilo.jsonc'
            self.assertTrue(kilo_jsonc.is_file(), "kilo.jsonc should be created")

            # Verify .kilo/rules/*.md
            rules_dir = target / '.kilo' / 'rules'
            self.assertTrue(rules_dir.is_dir(), ".kilo/rules directory should exist")
            expected_rules = [
                'steel-mind.md',
                'plaincast.md',
                'leakguard.md',
                'precision-output.md',
            ]
            for rule_file in expected_rules:
                rule_path = rules_dir / rule_file
                self.assertTrue(rule_path.is_file(), f"Missing rule file: {rule_file}")
                self.assertGreater(rule_path.stat().st_size, 0)

    def test_03_init_all(self):
        """quench init --tool all installs all adapters."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            cmd = [sys.executable, str(QUENCH_PY), 'init', '--tool', 'all', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")

            # Check key marker files across all adapters
            markers = [
                target / '.cursorrules',
                target / '.cursor' / 'rules' / 'steel-mind.mdc',
                target / 'kilo.jsonc',
                target / '.kilo' / 'rules' / 'steel-mind.md',
                target / '.github' / 'copilot-instructions.md',
                target / '.clinerules' / 'steel-mind.md',
                target / '.windsurfrules',
                target / 'CLAUDE.md',
                target / 'system-prompt.md',
                target / 'CONVENTIONS.md',
                target / '.zedprompts' / 'steel-mind.md',
                target / '.junie' / 'rules' / 'steel-mind.md',
                target / '.agents' / 'rules' / 'AGENTS.md',
                target / 'AGENTS.md',
            ]
            for marker in markers:
                self.assertTrue(marker.is_file(), f"Expected marker not found: {marker}")

    def test_04_init_hooks_and_permissions(self):
        """quench init --hooks installs git hooks and verifies executable permissions."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            cmd = [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--hooks', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")

            # Verify hooks exist in .git/hooks and/or .githooks
            hook_names = ['pre-commit', 'commit-msg']
            for hook_name in hook_names:
                hook_git = target / '.git' / 'hooks' / hook_name
                hook_custom = target / '.githooks' / hook_name
                self.assertTrue(hook_git.is_file(), f"Git hook missing: {hook_git}")
                self.assertTrue(hook_custom.is_file(), f"Githooks template missing: {hook_custom}")

                # Verify permissions
                if os.name != 'nt':
                    mode_git = hook_git.stat().st_mode
                    mode_custom = hook_custom.stat().st_mode
                    self.assertTrue(bool(mode_git & 0o111), f"Hook not executable: {hook_git}")
                    self.assertTrue(bool(mode_custom & 0o111), f"Hook not executable: {hook_custom}")
                else:
                    self.assertTrue(os.access(hook_git, os.R_OK))
                    self.assertTrue(os.access(hook_custom, os.R_OK))

    def test_05_check_clean_initialized_project(self):
        """quench check --target <dir> passes cleanly on newly initialized project."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            # Initialize cursor adapter
            subprocess.run(
                [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--target', str(target)],
                check=True,
                capture_output=True
            )

            # Run quench check
            cmd = [sys.executable, str(QUENCH_PY), 'check', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Check failed on clean project:\n{res.stdout}\n{res.stderr}")
            self.assertIn("[PASS]", res.stdout)

    def test_06_check_detects_synthetic_violations(self):
        """quench check detects intentional violations (emoji, forbidden path, exposed secret)."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            subprocess.run(
                [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--target', str(target)],
                check=True,
                capture_output=True
            )

            # Synthetic violations constructed dynamically
            simulated_emoji = chr(0x1F680)
            simulated_drive = "C" + ":\\Users\\developer\\"
            simulated_secret = "ghp_" + ("1234567890" * 3 + "123456")

            dirty_file = target / 'dirty.md'
            dirty_file.write_text(
                f"# Project Launch {simulated_emoji}\n"
                f"Path: {simulated_drive}\n"
                f"API Key: {simulated_secret}\n",
                encoding='utf-8',
                newline='\n'
            )

            cmd = [sys.executable, str(QUENCH_PY), 'check', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 1, "Check should exit 1 on violations")
            self.assertIn("[FAIL]", res.stdout)
            self.assertIn("plaincast", res.stdout.lower())
            self.assertIn("leakguard", res.stdout.lower())

    def test_07_check_autofix(self):
        """quench check --fix --target <dir> auto-fixes fixable plaincast and path issues."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            subprocess.run(
                [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--target', str(target)],
                check=True,
                capture_output=True
            )

            # Fixable violations: em-dash, curly quotes, local workspace drive path
            em_dash = '\u2014'
            left_quote = '\u201c'
            right_quote = '\u201d'
            local_path = "D" + ":\\quench"

            fixable_file = target / 'notes.md'
            fixable_file.write_text(
                f"Release Notes{em_dash}Final\n"
                f"Status: {left_quote}stable{right_quote}\n"
                f"Location: {local_path}\n",
                encoding='utf-8',
                newline='\n'
            )

            cmd = [sys.executable, str(QUENCH_PY), 'check', '--fix', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')

            fixed_content = fixable_file.read_text(encoding='utf-8')
            # Verify plaincast conversions
            self.assertNotIn(em_dash, fixed_content)
            self.assertIn(' - ', fixed_content)
            self.assertNotIn(left_quote, fixed_content)
            self.assertNotIn(right_quote, fixed_content)
            self.assertIn('"stable"', fixed_content)

            # Verify leakguard path auto-fix
            self.assertNotIn(local_path, fixed_content)
            self.assertIn('/path/to/<project>', fixed_content)

    def test_08_status_detection(self):
        """quench status accurately detects installed adapters and git hooks."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            # Before initialization
            cmd = [sys.executable, str(QUENCH_PY), 'status', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0)
            self.assertIn("none detected", res.stdout)
            self.assertIn("none installed", res.stdout)

            # Initialize cursor with hooks
            subprocess.run(
                [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--hooks', '--target', str(target)],
                check=True,
                capture_output=True
            )

            res_after = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res_after.returncode, 0)
            self.assertIn("cursor", res_after.stdout)
            self.assertIn("pre-commit", res_after.stdout)
            self.assertIn("commit-msg", res_after.stdout)

    def test_09_update_refreshes_modified_adapter(self):
        """quench update successfully refreshes modified adapter files."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)

            subprocess.run(
                [sys.executable, str(QUENCH_PY), 'init', '--tool', 'cursor', '--target', str(target)],
                check=True,
                capture_output=True
            )

            # Modify an installed file
            cursorrules_path = target / '.cursorrules'
            cursorrules_path.write_text("MODIFIED_USER_CONTENT\n", encoding='utf-8', newline='\n')
            self.assertEqual(cursorrules_path.read_text(encoding='utf-8'), "MODIFIED_USER_CONTENT\n")

            # Run quench update
            cmd = [sys.executable, str(QUENCH_PY), 'update', '--target', str(target)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Update failed: {res.stderr}")

            # Check that .cursorrules was refreshed to source template
            source_content = (REPO_ROOT / 'adapters' / 'cursor' / '.cursorrules').read_text(encoding='utf-8')
            refreshed_content = cursorrules_path.read_text(encoding='utf-8')
            self.assertEqual(refreshed_content, source_content)

    def test_10_version_flag(self):
        """quench --version displays 'quench 1.8.0'."""
        cmd = [sys.executable, str(QUENCH_PY), '--version']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0)
        self.assertIn("quench 1.8.0", res.stdout.strip())


if __name__ == '__main__':
    unittest.main()
