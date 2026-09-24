#!/usr/bin/env python3
"""
Tests for 'quench update --global': a stable clone that follows a release tag and is
wired into Claude Code (global CLAUDE.md import plus one link per skill).

Every test uses a throwaway local source repo, clone location and Claude config dir,
so no network access is needed and the real ~/.claude is never touched.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
QUENCH = SCRIPTS_DIR / 'quench.py'


def git(*args, cwd):
    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@example.com', *args],
                   cwd=str(cwd), check=True, capture_output=True)


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


@unittest.skipUnless(shutil.which('git'), "git not available")
class TestUpdateGlobal(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='quench-global-')).resolve()
        self.src = self.tmp / 'src'
        self.home = self.tmp / 'home'
        self.claude = self.tmp / 'claude'
        write(self.src / 'rules' / 'AGENTS.md', "# rules v1\n")
        for name in ('alpha', 'beta'):
            write(self.src / 'skills' / name / 'SKILL.md', f"---\nname: {name}\ndescription: d\n---\n")
        write(self.src / 'skills' / 'notaskill' / 'README.md', "no SKILL.md here\n")
        git('init', '-q', cwd=self.src)
        git('add', '-A', cwd=self.src)
        git('commit', '-q', '-m', 'one', cwd=self.src)
        git('tag', 'v1', cwd=self.src)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_update(self, *extra, user_home=None):
        cmd = [sys.executable, str(QUENCH), 'update', '--global', '--home', str(self.home),
               '--repo', str(self.src), '--claude-dir', str(self.claude), *extra]
        # A fake user home makes the ~/ import form deterministic on every OS
        fake_home = str(user_home or self.tmp)
        env = dict(os.environ, HOME=fake_home, USERPROFILE=fake_home)
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)

    def claude_md(self) -> str:
        return (self.claude / 'CLAUDE.md').read_text(encoding='utf-8')

    def import_line(self) -> str:
        return '@~/home/rules/AGENTS.md'

    def test_import_uses_absolute_path_outside_home(self):
        other_home = self.tmp / 'elsewhere'
        other_home.mkdir()
        res = self.run_update(user_home=other_home)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn('@' + (self.home / 'rules' / 'AGENTS.md').as_posix(), self.claude_md().splitlines())

    def test_reports_exact_release_not_floating_tag(self):
        git('tag', 'v1.2.3', cwd=self.src)
        res = self.run_update()
        self.assertIn("checked out: v1.2.3", res.stdout)

    def test_fresh_install_clones_and_wires_claude(self):
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1\n")
        self.assertIn(self.import_line(), self.claude_md().splitlines())
        for name in ('alpha', 'beta'):
            skill_md = self.claude / 'skills' / name / 'SKILL.md'
            self.assertTrue(skill_md.is_file(), f"{name} not linked")
            self.assertEqual(skill_md.resolve(), (self.home / 'skills' / name / 'SKILL.md').resolve())
        self.assertFalse((self.claude / 'skills' / 'notaskill').exists())

    def test_rerun_is_idempotent(self):
        self.run_update()
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(self.claude_md().splitlines().count(self.import_line()), 1)
        self.assertIn("already imported", res.stdout)
        self.assertIn("alpha: already linked", res.stdout)

    def test_follows_moved_release_tag(self):
        self.run_update()
        write(self.src / 'rules' / 'AGENTS.md', "# rules v1.1\n")
        git('commit', '-q', '-am', 'two', cwd=self.src)
        git('tag', '-f', 'v1', cwd=self.src)
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1.1\n")
        # the linked skill now reads the updated clone without relinking
        self.assertTrue((self.claude / 'skills' / 'alpha' / 'SKILL.md').is_file())

    def test_existing_claude_md_content_is_preserved(self):
        write(self.claude / 'CLAUDE.md', "# My global notes\nPrefer tabs.")
        self.run_update()
        text = self.claude_md()
        self.assertTrue(text.startswith("# My global notes\nPrefer tabs.\n"))
        self.assertIn(self.import_line(), text.splitlines())

    def test_existing_import_from_another_clone_is_left_alone(self):
        other = '@' + (self.tmp / 'devclone' / 'rules' / 'AGENTS.md').as_posix()
        write(self.claude / 'CLAUDE.md', other + "\n")
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(self.claude_md(), other + "\n")
        self.assertIn("left unchanged", res.stdout)

    def test_link_to_another_clone_is_not_replaced(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        import quench
        elsewhere = self.tmp / 'devclone' / 'skills' / 'beta'
        write(elsewhere / 'SKILL.md', "dev beta\n")
        (self.claude / 'skills').mkdir(parents=True)
        quench._make_dir_link(self.claude / 'skills' / 'beta', elsewhere)
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("beta: ", res.stdout)
        self.assertEqual((self.claude / 'skills' / 'beta' / 'SKILL.md').read_text(encoding='utf-8'), "dev beta\n")
        self.assertTrue((self.claude / 'skills' / 'alpha' / 'SKILL.md').is_file())

    def test_real_folder_is_not_replaced(self):
        write(self.claude / 'skills' / 'alpha' / 'SKILL.md', "my own alpha\n")
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual((self.claude / 'skills' / 'alpha' / 'SKILL.md').read_text(encoding='utf-8'), "my own alpha\n")
        self.assertIn("alpha: ", res.stdout)
        self.assertIn("real folder; left unchanged", res.stdout)
        self.assertTrue((self.claude / 'skills' / 'beta' / 'SKILL.md').is_file())

    def test_local_changes_in_clone_are_refused(self):
        self.run_update()
        write(self.home / 'rules' / 'AGENTS.md', "# my local edit\n")
        res = self.run_update()
        self.assertEqual(res.returncode, 1)
        self.assertIn("local changes", res.stdout)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# my local edit\n")

    def test_no_claude_updates_clone_only(self):
        res = self.run_update('--no-claude')
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertTrue((self.home / 'rules' / 'AGENTS.md').is_file())
        self.assertFalse(self.claude.exists())

    def test_non_git_home_is_refused(self):
        write(self.home / 'something.txt', "not a clone\n")
        res = self.run_update()
        self.assertEqual(res.returncode, 1)
        self.assertIn("not a git clone", res.stdout)
        self.assertTrue((self.home / 'something.txt').is_file())

    def test_unknown_ref_fails_cleanly(self):
        res = self.run_update('--ref', 'v99')
        self.assertEqual(res.returncode, 1)
        self.assertIn("checkout v99 failed", res.stdout)


if __name__ == '__main__':
    unittest.main()
