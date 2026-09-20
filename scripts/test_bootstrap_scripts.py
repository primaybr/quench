#!/usr/bin/env python3
"""
Test Suite for Quench Remote Bootstrap Installers
Verifies scripts/install.sh (POSIX sh) and scripts/install.ps1 (PowerShell)
for parameter parsing, argument handling, encoding, and file installations.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
INSTALL_SH = SCRIPTS_DIR / 'install.sh'
INSTALL_PS1 = SCRIPTS_DIR / 'install.ps1'

# Find system bash and powershell
BASH_BIN = shutil.which('bash') or shutil.which('sh')
PWSH_BIN = shutil.which('powershell') or shutil.which('pwsh')


class TestBootstrapHygiene(unittest.TestCase):
    """Hygiene and Plaincast adherence for bootstrap scripts."""

    def test_install_sh_no_bom_and_lf(self):
        self.assertTrue(INSTALL_SH.is_file(), "scripts/install.sh must exist")
        raw = INSTALL_SH.read_bytes()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), "install.sh must not start with UTF-8 BOM")
        self.assertNotIn(b'\r\n', raw, "install.sh must have strictly LF line endings")

    def test_install_ps1_no_bom_and_lf(self):
        self.assertTrue(INSTALL_PS1.is_file(), "scripts/install.ps1 must exist")
        raw = INSTALL_PS1.read_bytes()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), "install.ps1 must not start with UTF-8 BOM")
        self.assertNotIn(b'\r\n', raw, "install.ps1 must have strictly LF line endings")

    def test_install_sh_plaincast(self):
        content = INSTALL_SH.read_text(encoding='utf-8')
        # Check no em-dash
        self.assertNotIn('\u2014', content, "install.sh must not contain em-dashes")
        self.assertNotIn('\u2013', content, "install.sh must not contain en-dashes")
        # Check straight quotes only
        for cq in ['\u2018', '\u2019', '\u201c', '\u201d']:
            self.assertNotIn(cq, content, f"install.sh contains curly quote: {cq!r}")

    def test_install_ps1_plaincast(self):
        content = INSTALL_PS1.read_text(encoding='utf-8')
        # Check no em-dash
        self.assertNotIn('\u2014', content, "install.ps1 must not contain em-dashes")
        self.assertNotIn('\u2013', content, "install.ps1 must not contain en-dashes")
        # Check straight quotes only
        for cq in ['\u2018', '\u2019', '\u201c', '\u201d']:
            self.assertNotIn(cq, content, f"install.ps1 contains curly quote: {cq!r}")


@unittest.skipIf(not BASH_BIN, "bash or sh not available in environment")
class TestInstallSh(unittest.TestCase):
    """Execution and argument handling for scripts/install.sh."""

    def _init_git_repo(self, target: Path):
        subprocess.run(
            ['git', 'init'],
            cwd=str(target),
            capture_output=True,
            check=True
        )

    def test_help_flag(self):
        cmd = [BASH_BIN, str(INSTALL_SH), '--help']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertIn("Remote Bootstrap Installer", res.stdout)
        self.assertIn("--tool", res.stdout)
        self.assertIn("--target", res.stdout)

    def test_unknown_option_fails(self):
        cmd = [BASH_BIN, str(INSTALL_SH), '--invalid-flag-xyz']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Unknown option", res.stderr)

    def test_unknown_tool_fails(self):
        cmd = [BASH_BIN, str(INSTALL_SH), '--tool', 'invalid_tool_name']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Unknown tool", res.stderr)

    def test_install_cursor(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'cursor',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertIn("Quench initialization complete", res.stdout)

            self.assertTrue((target / '.cursorrules').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'steel-mind.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'plaincast.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'leakguard.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'precision-output.mdc').is_file())

    def test_install_copilot(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'copilot',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            copilot_file = target / '.github' / 'copilot-instructions.md'
            self.assertTrue(copilot_file.is_file())
            self.assertGreater(copilot_file.stat().st_size, 0)

    def test_install_rules(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'rules',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            agents_file = target / 'AGENTS.md'
            self.assertTrue(agents_file.is_file())
            self.assertGreater(agents_file.stat().st_size, 0)

    def test_install_all(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'all',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / '.cursorrules').is_file())
            self.assertTrue((target / '.github' / 'copilot-instructions.md').is_file())
            self.assertTrue((target / 'kilo.jsonc').is_file())
            self.assertTrue((target / '.clinerules' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.windsurfrules').is_file())
            self.assertTrue((target / 'CLAUDE.md').is_file())
            self.assertTrue((target / 'system-prompt.md').is_file())
            self.assertTrue((target / 'CONVENTIONS.md').is_file())
            self.assertTrue((target / '.zedprompts' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.junie' / 'rules' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.agents' / 'rules' / 'AGENTS.md').is_file())
            self.assertTrue((target / 'AGENTS.md').is_file())

    def test_hooks_installation(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)
            cmd = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'rules',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix(),
                '--hooks'
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / '.githooks' / 'pre-commit').is_file())
            self.assertTrue((target / '.githooks' / 'commit-msg').is_file())
            self.assertTrue((target / '.git' / 'hooks' / 'pre-commit').is_file())
            self.assertTrue((target / '.git' / 'hooks' / 'commit-msg').is_file())

    def test_force_flag_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            target_file = target / 'AGENTS.md'
            target_file.write_text("custom user content", encoding='utf-8')

            # Without --force: should skip
            cmd1 = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'rules',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res1.returncode, 0)
            self.assertIn("Skipped (already exists)", res1.stdout)
            self.assertEqual(target_file.read_text(encoding='utf-8'), "custom user content")

            # With --force: should overwrite
            cmd2 = [
                BASH_BIN, str(INSTALL_SH),
                '--tool', 'rules',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix(),
                '--force'
            ]
            res2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res2.returncode, 0)
            self.assertIn("Overwritten: AGENTS.md", res2.stdout)
            self.assertNotEqual(target_file.read_text(encoding='utf-8'), "custom user content")

    def test_pipe_execution(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            sh_content = INSTALL_SH.read_text(encoding='utf-8')
            cmd = [
                BASH_BIN, '-s', '--',
                '--tool', 'rules',
                '--target', target.as_posix(),
                '--source', REPO_ROOT.as_posix()
            ]
            res = subprocess.run(cmd, input=sh_content, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / 'AGENTS.md').is_file())


@unittest.skipIf(not PWSH_BIN, "powershell or pwsh not available in environment")
class TestInstallPs1(unittest.TestCase):
    """Execution and parameter handling for scripts/install.ps1."""

    def _init_git_repo(self, target: Path):
        subprocess.run(
            ['git', 'init'],
            cwd=str(target),
            capture_output=True,
            check=True
        )

    def test_help_flag(self):
        cmd = [PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1), '-Help']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertIn("Remote Bootstrap Installer", res.stdout)
        self.assertIn("-Tool", res.stdout)
        self.assertIn("-Target", res.stdout)

    def test_unknown_tool_fails(self):
        cmd = [
            PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
            '-Tool', 'invalid_tool_name'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("Unknown tool", res.stdout + res.stderr)

    def test_install_cursor(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'cursor',
                '-Target', str(target),
                '-Source', str(REPO_ROOT)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertIn("Quench initialization complete", res.stdout)

            self.assertTrue((target / '.cursorrules').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'steel-mind.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'plaincast.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'leakguard.mdc').is_file())
            self.assertTrue((target / '.cursor' / 'rules' / 'precision-output.mdc').is_file())

    def test_install_copilot(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'copilot',
                '-Target', str(target),
                '-Source', str(REPO_ROOT)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            copilot_file = target / '.github' / 'copilot-instructions.md'
            self.assertTrue(copilot_file.is_file())
            self.assertGreater(copilot_file.stat().st_size, 0)

    def test_install_rules(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'rules',
                '-Target', str(target),
                '-Source', str(REPO_ROOT)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            agents_file = target / 'AGENTS.md'
            self.assertTrue(agents_file.is_file())
            self.assertGreater(agents_file.stat().st_size, 0)

    def test_install_all(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            cmd = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'all',
                '-Target', str(target),
                '-Source', str(REPO_ROOT)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / '.cursorrules').is_file())
            self.assertTrue((target / '.github' / 'copilot-instructions.md').is_file())
            self.assertTrue((target / 'kilo.jsonc').is_file())
            self.assertTrue((target / '.clinerules' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.windsurfrules').is_file())
            self.assertTrue((target / 'CLAUDE.md').is_file())
            self.assertTrue((target / 'system-prompt.md').is_file())
            self.assertTrue((target / 'CONVENTIONS.md').is_file())
            self.assertTrue((target / '.zedprompts' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.junie' / 'rules' / 'steel-mind.md').is_file())
            self.assertTrue((target / '.agents' / 'rules' / 'AGENTS.md').is_file())
            self.assertTrue((target / 'AGENTS.md').is_file())

    def test_hooks_installation(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            self._init_git_repo(target)
            cmd = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'rules',
                '-Target', str(target),
                '-Source', str(REPO_ROOT),
                '-Hooks'
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / '.githooks' / 'pre-commit').is_file())
            self.assertTrue((target / '.githooks' / 'commit-msg').is_file())
            self.assertTrue((target / '.git' / 'hooks' / 'pre-commit').is_file())
            self.assertTrue((target / '.git' / 'hooks' / 'commit-msg').is_file())

    def test_force_flag_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            target_file = target / 'AGENTS.md'
            target_file.write_text("custom user content", encoding='utf-8')

            # Without -Force: should skip
            cmd1 = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'rules',
                '-Target', str(target),
                '-Source', str(REPO_ROOT)
            ]
            res1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res1.returncode, 0)
            self.assertIn("Skipped (already exists)", res1.stdout)
            self.assertEqual(target_file.read_text(encoding='utf-8'), "custom user content")

            # With -Force: should overwrite
            cmd2 = [
                PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1),
                '-Tool', 'rules',
                '-Target', str(target),
                '-Source', str(REPO_ROOT),
                '-Force'
            ]
            res2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res2.returncode, 0)
            self.assertIn("Overwritten: AGENTS.md", res2.stdout)
            self.assertNotEqual(target_file.read_text(encoding='utf-8'), "custom user content")

    def test_scriptblock_invocation(self):
        """Simulates irm | iex with scriptblock parameter passing."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            t_str = str(target).replace('\\', '/')
            r_str = str(REPO_ROOT).replace('\\', '/')
            ps1_str = str(INSTALL_PS1).replace('\\', '/')
            ps_code = f"& ([scriptblock]::Create([System.IO.File]::ReadAllText('{ps1_str}'))) -Tool rules -Target '{t_str}' -Source '{r_str}'"
            cmd = [PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', ps_code]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / 'AGENTS.md').is_file())

    def test_env_variables_fallback(self):
        """Tests falling back to environment variables QUENCH_TOOL and QUENCH_TARGET."""
        with tempfile.TemporaryDirectory() as td:
            target = Path(td)
            env = os.environ.copy()
            env['QUENCH_TOOL'] = 'copilot'
            env['QUENCH_TARGET'] = str(target)
            env['QUENCH_SOURCE'] = str(REPO_ROOT)
            cmd = [PWSH_BIN, '-ExecutionPolicy', 'Bypass', '-NoProfile', '-File', str(INSTALL_PS1)]
            res = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertTrue((target / '.github' / 'copilot-instructions.md').is_file())


if __name__ == '__main__':
    unittest.main()
