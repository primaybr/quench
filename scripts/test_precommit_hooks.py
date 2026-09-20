#!/usr/bin/env python3
"""
Unit and Integration Test Suite for Quench Pre-Commit Framework Configuration.
Verifies .pre-commit-hooks.yaml structure, schema, hook definitions, stages, and execution.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate

HOOKS_FILE = REPO_ROOT / '.pre-commit-hooks.yaml'

VALID_PRECOMMIT_STAGES = {
    'commit',
    'pre-commit',
    'pre-merge-commit',
    'pre-push',
    'push',
    'commit-msg',
    'post-commit',
    'post-checkout',
    'post-merge',
    'post-rewrite',
    'manual',
}


def parse_simple_yaml_hooks(text: str) -> List[Dict[str, Any]]:
    """Zero-dependency fallback parser for simple pre-commit hooks YAML format."""
    hooks: List[Dict[str, Any]] = []
    current_hook: Dict[str, Any] | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        if stripped.startswith('- '):
            if current_hook is not None:
                hooks.append(current_hook)
            current_hook = {}
            line_content = stripped[2:].strip()
        else:
            line_content = stripped

        if ':' in line_content:
            key, val = line_content.split(':', 1)
            key = key.strip()
            val = val.strip()

            if val.startswith('[') and val.endswith(']'):
                items = [item.strip().strip("'\"") for item in val[1:-1].split(',') if item.strip()]
                parsed_val: Any = items
            elif val.lower() == 'true':
                parsed_val = True
            elif val.lower() == 'false':
                parsed_val = False
            elif (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                parsed_val = val[1:-1]
            else:
                parsed_val = val

            if current_hook is not None:
                current_hook[key] = parsed_val

    if current_hook is not None:
        hooks.append(current_hook)

    return hooks


def load_hooks_data() -> List[Dict[str, Any]]:
    """Load hooks data using PyYAML if installed, falling back to zero-dependency parser."""
    content = HOOKS_FILE.read_text(encoding='utf-8')
    try:
        import yaml
        data = yaml.safe_load(content)
        if isinstance(data, list):
            return data
    except ImportError:
        pass
    return parse_simple_yaml_hooks(content)


class TestPrecommitHooksConfig(unittest.TestCase):
    """Test suite for .pre-commit-hooks.yaml configuration."""

    def test_file_exists(self):
        """Verify that .pre-commit-hooks.yaml exists at repository root."""
        self.assertTrue(HOOKS_FILE.exists(), f"Missing {HOOKS_FILE}")
        self.assertTrue(HOOKS_FILE.is_file(), f"{HOOKS_FILE} is not a file")

    def test_file_hygiene(self):
        """Verify encoding, line endings, and lack of BOM."""
        raw = HOOKS_FILE.read_bytes()
        self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), "File contains UTF-8 BOM")
        self.assertNotIn(b'\r\n', raw, "File contains CRLF line endings")

        content = raw.decode('utf-8')
        report = validate.ValidationReport()
        validate.validate_plaincast(HOOKS_FILE, content, report)
        self.assertTrue(report.passed, f"Plaincast violations: {[str(v) for v in report.violations]}")

        report_leak = validate.ValidationReport()
        validate.validate_path_leaks(HOOKS_FILE, content, report_leak)
        self.assertTrue(report_leak.passed, f"Leakguard violations: {[str(v) for v in report_leak.violations]}")

    def test_yaml_structure(self):
        """Verify YAML parses into a non-empty list of dictionaries."""
        hooks = load_hooks_data()
        self.assertIsInstance(hooks, list, "Root YAML element must be a list")
        self.assertEqual(len(hooks), 2, "Expected exactly 2 hook definitions")

    def test_hook_ids_unique(self):
        """Verify all hook IDs are unique and present."""
        hooks = load_hooks_data()
        ids = [h.get('id') for h in hooks]
        self.assertEqual(len(ids), len(set(ids)), "Hook IDs must be unique")
        self.assertIn('quench-check', ids)
        self.assertIn('quench-commit-msg', ids)

    def test_quench_check_hook(self):
        """Verify structure and values of quench-check hook."""
        hooks = load_hooks_data()
        hook = next((h for h in hooks if h.get('id') == 'quench-check'), None)
        self.assertIsNotNone(hook, "quench-check hook not found")

        self.assertEqual(hook.get('name'), 'quench-check')
        self.assertEqual(
            hook.get('description'),
            'Run Quench 5-gate integrity engine against repository files'
        )
        self.assertEqual(hook.get('entry'), 'python scripts/quench.py check')
        self.assertEqual(hook.get('language'), 'python')
        self.assertEqual(hook.get('stages'), ['pre-commit'])
        self.assertIs(hook.get('pass_filenames'), False)
        self.assertIs(hook.get('always_run'), True)

    def test_quench_commit_msg_hook(self):
        """Verify structure and values of quench-commit-msg hook."""
        hooks = load_hooks_data()
        hook = next((h for h in hooks if h.get('id') == 'quench-commit-msg'), None)
        self.assertIsNotNone(hook, "quench-commit-msg hook not found")

        self.assertEqual(hook.get('name'), 'quench-commit-msg')
        self.assertEqual(
            hook.get('description'),
            'Validate commit message against plaincast typography and leakguard rules'
        )
        self.assertEqual(hook.get('entry'), 'python scripts/validate.py --check-commit-msg')
        self.assertEqual(hook.get('language'), 'python')
        self.assertEqual(hook.get('stages'), ['commit-msg'])

    def test_hook_stages_validity(self):
        """Verify that declared hook stages are valid pre-commit framework stages."""
        hooks = load_hooks_data()
        for hook in hooks:
            stages = hook.get('stages', [])
            self.assertIsInstance(stages, list, f"Hook {hook.get('id')} stages must be a list")
            self.assertTrue(len(stages) > 0, f"Hook {hook.get('id')} must declare at least one stage")
            for stage in stages:
                self.assertIn(stage, VALID_PRECOMMIT_STAGES, f"Invalid stage '{stage}' in hook {hook.get('id')}")

    def test_referenced_scripts_exist(self):
        """Verify that script files referenced in entry points exist in repository."""
        hooks = load_hooks_data()
        for hook in hooks:
            entry = hook.get('entry', '')
            tokens = entry.split()
            script_tokens = [t for t in tokens if t.endswith('.py')]
            for script_rel in script_tokens:
                script_path = REPO_ROOT / script_rel
                self.assertTrue(script_path.exists(), f"Entry script {script_rel} not found on disk")

    def test_quench_check_execution(self):
        """Smoke test executing quench-check entry command."""
        cmd = [sys.executable, str(REPO_ROOT / 'scripts' / 'quench.py'), 'check']
        proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"quench check failed with stderr: {proc.stderr}")
        self.assertIn('All validation gates passed', proc.stdout)

    def test_quench_commit_msg_clean_execution(self):
        """Smoke test executing quench-commit-msg entry with a valid commit message."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tf:
            tf.write('feat: add pre-commit framework integration\n\nValid commit body text.\n')
            temp_path = tf.name

        try:
            cmd = [sys.executable, str(REPO_ROOT / 'scripts' / 'validate.py'), '--check-commit-msg', temp_path]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f"Clean commit message failed: {proc.stderr}\n{proc.stdout}")
            self.assertIn('Commit message is clean', proc.stdout)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_quench_commit_msg_dirty_execution(self):
        """Smoke test executing quench-commit-msg entry with an invalid commit message containing banned char."""
        # Use chr() to construct em-dash dynamically so the test source file contains only clean ASCII
        banned_char = chr(0x2014)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tf:
            tf.write(f"feat: update rules{banned_char}with banned dash\n")
            temp_path = tf.name

        try:
            cmd = [sys.executable, str(REPO_ROOT / 'scripts' / 'validate.py'), '--check-commit-msg', temp_path]
            proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0, "Dirty commit message should be rejected")
            self.assertIn('Commit rejected', proc.stdout)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_zero_dependency_fallback_parser_equivalence(self):
        """Verify that zero-dependency fallback parser produces same results as PyYAML."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed in environment")

        content = HOOKS_FILE.read_text(encoding='utf-8')
        pyyaml_data = yaml.safe_load(content)
        fallback_data = parse_simple_yaml_hooks(content)
        self.assertEqual(pyyaml_data, fallback_data)


if __name__ == '__main__':
    unittest.main()
