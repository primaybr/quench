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


class _GlobalFixture:
    """A throwaway quench-like source repo tagged v1, plus empty clone and Claude dirs."""

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


@unittest.skipUnless(shutil.which('git'), "git not available")
class TestUpdateGlobal(_GlobalFixture, unittest.TestCase):
    def test_hook_not_installed_when_release_lacks_auto_update(self):
        # This fixture's clone has no scripts/quench.py, like a release older than the feature
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("auto-update: not available", res.stdout)
        self.assertFalse((self.claude / 'settings.json').exists())

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


class _HookFixture(_GlobalFixture):
    """Fixture whose clone has a CLI that supports the auto-update hook."""

    def setUp(self):
        super().setUp()
        # A clone whose CLI supports --auto (this repo's current scripts)
        (self.src / 'scripts').mkdir()
        for name in ('quench.py', 'validate.py'):
            shutil.copy(SCRIPTS_DIR / name, self.src / 'scripts' / name)
        git('add', '-A', cwd=self.src)
        git('commit', '-q', '-m', 'cli', cwd=self.src)
        git('tag', 'v1.0.0', cwd=self.src)
        git('tag', '-f', 'v1', cwd=self.src)
        self.next_minor = 1

    def settings(self) -> dict:
        import json
        return json.loads((self.claude / 'settings.json').read_text(encoding='utf-8'))

    def our_hooks(self):
        entries = self.settings().get('hooks', {}).get('SessionStart', [])
        return [h for e in entries for h in e['hooks'] if 'update --global --auto' in h['command']]

    def run_auto(self, interval='0'):
        env = dict(os.environ, QUENCH_AUTO_UPDATE_INTERVAL=interval)
        cmd = [sys.executable, str(self.home / 'scripts' / 'quench.py'), 'update', '--global', '--auto',
               '--home', str(self.home)]
        return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)

    def release(self, text, version=None):
        """Publish a release the way release.yml does: a vX.Y.Z tag, then move v1."""
        write(self.src / 'rules' / 'AGENTS.md', text)
        git('commit', '-q', '-am', text.strip(), cwd=self.src)
        if version is None:
            version = f'v1.{self.next_minor}.0'
            self.next_minor += 1
        git('tag', version, cwd=self.src)
        git('tag', '-f', 'v1', cwd=self.src)
        return version


@unittest.skipUnless(shutil.which('git'), "git not available")
class TestAutoUpdateHook(_HookFixture, unittest.TestCase):
    """The SessionStart hook that installs new releases automatically."""

    def test_hook_installed_once_and_settings_preserved(self):
        import json
        write(self.claude / 'settings.json', json.dumps({
            'theme': 'dark',
            'hooks': {'SessionStart': [{'hooks': [{'type': 'command', 'command': 'echo mine'}]}]}}))
        self.run_update('--auto-update')
        res = self.run_update()
        self.assertIn("auto-update: already enabled", res.stdout)
        self.assertEqual(self.settings()['theme'], 'dark')
        self.assertEqual(len(self.our_hooks()), 1)
        commands = [h['command'] for e in self.settings()['hooks']['SessionStart'] for h in e['hooks']]
        self.assertIn('echo mine', commands)
        self.assertIn(f'--home "{self.home.as_posix()}"', self.our_hooks()[0]['command'])

    def test_no_auto_update_removes_only_our_hook(self):
        import json
        write(self.claude / 'settings.json', json.dumps({'theme': 'dark'}))
        self.run_update('--auto-update')
        res = self.run_update('--no-auto-update')
        self.assertIn("auto-update: disabled", res.stdout)
        self.assertEqual(self.settings(), {'theme': 'dark'})

    def test_invalid_settings_left_unchanged(self):
        write(self.claude / 'settings.json', "{ not json")
        res = self.run_update('--auto-update')
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("could not parse", res.stdout)
        self.assertEqual((self.claude / 'settings.json').read_text(encoding='utf-8'), "{ not json")

    def test_hook_command_runs_and_installs_new_release(self):
        self.run_update('--auto-update')
        self.release("# rules v1.1\n")
        cmd = self.our_hooks()[0]['command']
        env = dict(os.environ, QUENCH_AUTO_UPDATE_INTERVAL='0')
        # shell=True on purpose: this checks the exact command string Claude Code hands to a
        # shell. It is built only from this test's own temp paths, so there is no untrusted input.
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("quench updated v1.0.0 -> v1.1.0", res.stdout)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1.1\n")

    def test_auto_is_silent_when_nothing_changed(self):
        self.run_update('--auto-update')
        res = self.run_auto()
        self.assertEqual((res.returncode, res.stdout), (0, ''))

    def test_auto_is_throttled(self):
        self.run_update('--auto-update')
        self.run_auto()                     # stamps the check
        self.release("# rules v1.2\n")
        res = self.run_auto(interval='3600')
        self.assertEqual(res.stdout, '')
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1\n")
        res = self.run_auto(interval='0')
        self.assertIn("quench updated v1.0.0 -> v1.1.0", res.stdout)

    def test_auto_never_fails_the_session(self):
        self.run_update('--auto-update')
        git('remote', 'set-url', 'origin', str(self.tmp / 'gone'), cwd=self.home)
        res = self.run_auto()
        self.assertEqual((res.returncode, res.stdout), (0, ''))
        write(self.home / 'rules' / 'AGENTS.md', "# local edit\n")   # dirty clone
        git('remote', 'set-url', 'origin', str(self.src), cwd=self.home)
        self.release("# rules v1.3\n")
        res = self.run_auto()
        self.assertEqual((res.returncode, res.stdout), (0, ''))
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# local edit\n")


@unittest.skipUnless(shutil.which('git'), "git not available")
class TestAutoUpdateSafety(_HookFixture, unittest.TestCase):
    """Opt-in, no downgrades, and a reviewable commit range (re-analysis of v1.8.0, item 3/4)."""

    def test_off_by_default(self):
        res = self.run_update()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("auto-update: off (opt in with --auto-update)", res.stdout)
        self.assertFalse((self.claude / 'settings.json').exists())

    def test_plain_rerun_keeps_existing_hook(self):
        self.run_update('--auto-update')
        res = self.run_update()
        self.assertIn("already enabled", res.stdout)
        self.assertEqual(len(self.our_hooks()), 1)

    def test_flags_are_mutually_exclusive(self):
        res = self.run_update('--auto-update', '--no-auto-update')
        self.assertEqual(res.returncode, 2)

    def test_update_message_shows_version_and_commit_range(self):
        self.run_update('--auto-update')
        before = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=self.home, capture_output=True, text=True).stdout.strip()
        version = self.release("# rules v1.1\n")
        res = self.run_auto()
        after = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=self.home, capture_output=True, text=True).stdout.strip()
        self.assertIn(f"quench updated v1.0.0 -> {version}", res.stdout)
        self.assertIn(f"commits {before[:12]}..{after[:12]}", res.stdout)

    def test_backwards_moved_tag_is_not_installed(self):
        self.run_update('--auto-update')
        self.release("# rules v1.1\n")
        self.run_auto()                                  # now on v1.1.0
        # v1 moved back to the v1.0.0 commit, e.g. an old-line hotfix tagged by mistake
        git('tag', '-f', 'v1', 'v1.0.0', cwd=self.src)
        res = self.run_auto()
        self.assertIn("not downgrading", res.stdout)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1.1\n")

    def test_recorded_version_survives_retagging(self):
        """After a history rewrite the old HEAD has no tags; the recorded version still guards."""
        self.run_update('--auto-update')
        self.release("# rules v1.1\n")
        self.run_auto()                                  # records v1.1.0
        git('tag', '-d', 'v1.1.0', cwd=self.src)         # the old commit loses its tag
        git('fetch', '--quiet', '--prune', '--prune-tags', '--force', 'origin', cwd=self.home)
        git('tag', '-f', 'v1', 'v1.0.0', cwd=self.src)
        res = self.run_auto()
        self.assertIn("not downgrading", res.stdout)

    def test_untagged_target_is_not_installed(self):
        self.run_update('--auto-update')
        write(self.src / 'rules' / 'AGENTS.md', "# unreleased\n")
        git('commit', '-q', '-am', 'unreleased', cwd=self.src)
        git('tag', '-f', 'v1', cwd=self.src)             # v1 moved to a commit with no release tag
        res = self.run_auto()
        self.assertIn("untagged commit", res.stdout)
        self.assertEqual((self.home / 'rules' / 'AGENTS.md').read_text(encoding='utf-8'), "# rules v1\n")


if __name__ == '__main__':
    unittest.main()
