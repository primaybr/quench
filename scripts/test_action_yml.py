#!/usr/bin/env python3
"""
Unit test suite for action.yml reusable composite GitHub Action.
Verifies required keys, input definitions, composite syntax, and step commands.
"""

import sys
import unittest
from pathlib import Path

# Add scripts directory to sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import yaml
except ImportError:
    yaml = None


class TestActionYaml(unittest.TestCase):
    """Test suite validating repository action.yml composite action definition."""

    @classmethod
    def setUpClass(cls):
        cls.action_file = REPO_ROOT / 'action.yml'
        if not cls.action_file.exists():
            raise FileNotFoundError(f"action.yml not found at {cls.action_file}")
        cls.raw_bytes = cls.action_file.read_bytes()
        cls.content = cls.raw_bytes.decode('utf-8')
        if yaml is not None:
            cls.parsed = yaml.safe_load(cls.content)
        else:
            cls.parsed = None

    def test_01_action_file_exists(self):
        """action.yml must exist at repository root."""
        self.assertTrue(self.action_file.is_file(), "action.yml missing from repo root")
        self.assertGreater(len(self.content), 0, "action.yml is empty")

    def test_02_valid_yaml_structure(self):
        """action.yml must parse as a valid YAML mapping."""
        self.assertIsNotNone(yaml, "PyYAML module is required for parsing action.yml")
        self.assertIsInstance(self.parsed, dict, "Root of action.yml must be a mapping/dict")

    def test_03_required_top_level_keys(self):
        """action.yml must contain required keys: name, description, inputs, runs."""
        required_keys = ['name', 'description', 'inputs', 'runs']
        for key in required_keys:
            self.assertIn(key, self.parsed, f"Missing required top-level key: '{key}'")

    def test_04_metadata_exact_values(self):
        """Action name and description must match project specification."""
        self.assertEqual(self.parsed['name'], 'quench-action')
        expected_desc = (
            'Run Quench defensive integrity harness (plaincast, leakguard, parity, hygiene) on repository files'
        )
        self.assertEqual(self.parsed['description'].strip(), expected_desc)

    def test_05_inputs_specification(self):
        """Inputs target, fix, and paths-only must be defined with proper defaults."""
        inputs = self.parsed.get('inputs', {})
        self.assertIsInstance(inputs, dict, "inputs must be a mapping")

        expected_inputs = {
            'target': {
                'desc': 'Target directory to scan',
                'default': '.',
            },
            'fix': {
                'desc': 'Automatically fix plaincast typography and generic path leaks',
                'default': 'false',
            },
            'paths-only': {
                'desc': 'Only check for path leaks and credentials',
                'default': 'false',
            },
        }

        for input_name, spec in expected_inputs.items():
            self.assertIn(input_name, inputs, f"Missing input: '{input_name}'")
            inp = inputs[input_name]
            self.assertIn('description', inp, f"Missing description for input '{input_name}'")
            self.assertEqual(inp['description'].strip(), spec['desc'])
            self.assertIn('default', inp, f"Missing default for input '{input_name}'")
            actual_default = str(inp['default']).lower()
            expected_default = str(spec['default']).lower()
            self.assertEqual(actual_default, expected_default)

    def test_06_composite_run_syntax(self):
        """Runs section must use composite and specify valid steps."""
        runs = self.parsed.get('runs', {})
        self.assertIsInstance(runs, dict, "runs must be a mapping")
        self.assertEqual(runs.get('using'), 'composite', "runs.using must be 'composite'")

        steps = runs.get('steps')
        self.assertIsInstance(steps, list, "runs.steps must be a list")
        self.assertGreaterEqual(len(steps), 2, "runs.steps must have at least 2 steps")

        # Composite syntax rule: every step with 'run' must specify 'shell'
        for idx, step in enumerate(steps):
            if 'run' in step:
                self.assertIn(
                    'shell', step,
                    f"Composite action step {idx} with 'run' is missing required 'shell' key"
                )

    def test_07_setup_python_step(self):
        """Action must include a step to set up Python."""
        steps = self.parsed['runs']['steps']
        setup_step = None
        for step in steps:
            uses = step.get('uses', '')
            if 'setup-python' in uses:
                setup_step = step
                break

        self.assertIsNotNone(setup_step, "Missing step with uses: actions/setup-python")
        self.assertIn('with', setup_step, "setup-python step missing 'with' parameters")
        self.assertIn('python-version', setup_step['with'], "setup-python missing python-version")

    def test_08_quench_check_step(self):
        """Action must execute quench.py check with input flags."""
        steps = self.parsed['runs']['steps']
        quench_step = None
        for step in steps:
            run_cmd = step.get('run', '')
            if 'quench.py' in run_cmd and 'check' in run_cmd:
                quench_step = step
                break

        self.assertIsNotNone(quench_step, "Missing step executing quench.py check")
        run_text = quench_step['run']

        # Verifying step command invokes python ${{ github.action_path }}/quench.py check
        expected_cmd = 'python ${{ github.action_path }}/quench.py check'
        self.assertIn(
            expected_cmd, run_text,
            f"Expected command '{expected_cmd}' not found in run step:\n{run_text}"
        )

        # Verifying inputs are referenced
        self.assertIn('inputs.target', run_text, "Step command does not reference inputs.target")
        self.assertIn('inputs.fix', run_text, "Step command does not reference inputs.fix")
        self.assertIn('inputs.paths-only', run_text, "Step command does not reference inputs.paths-only")

        # Verifying CLI flags are constructed
        self.assertIn('--target', run_text, "Step command does not pass --target flag")
        self.assertIn('--fix', run_text, "Step command does not handle --fix flag")
        self.assertIn('--paths-only', run_text, "Step command does not handle --paths-only flag")

    def test_09_plaincast_and_hygiene(self):
        """action.yml must comply with Plaincast and hygiene standards."""
        # No UTF-8 BOM
        self.assertFalse(
            self.raw_bytes.startswith(b'\xef\xbb\xbf'),
            "action.yml must not start with UTF-8 BOM"
        )
        # No CRLF line endings
        self.assertNotIn(
            b'\r\n', self.raw_bytes,
            "action.yml must use LF line endings, not CRLF"
        )
        # No em-dashes
        self.assertNotIn('\u2014', self.content, "action.yml contains em-dash")
        # No curly quotes
        for bad_quote in ['\u2018', '\u2019', '\u201c', '\u201d']:
            self.assertNotIn(bad_quote, self.content, f"action.yml contains curly quote {repr(bad_quote)}")


if __name__ == '__main__':
    unittest.main()
