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

from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    yaml = None


def parse_simple_action_yaml(text: str) -> Dict[str, Any]:
    """Zero-dependency fallback parser for action.yml."""
    data: Dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            i += 1
            continue

        indent = len(line) - len(line.lstrip())
        if indent == 0 and ':' in stripped:
            key, val = stripped.split(':', 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if val:
                data[key] = val
                i += 1
            else:
                i += 1
                if key == 'inputs':
                    inputs_map: Dict[str, Any] = {}
                    while i < len(lines):
                        iline = lines[i]
                        istripped = iline.strip()
                        if not istripped or istripped.startswith('#'):
                            i += 1
                            continue
                        iindent = len(iline) - len(iline.lstrip())
                        if iindent == 0:
                            break
                        if iindent == 2 and ':' in istripped:
                            inp_key = istripped.split(':', 1)[0].strip()
                            inp_dict: Dict[str, Any] = {}
                            i += 1
                            while i < len(lines):
                                pline = lines[i]
                                pstripped = pline.strip()
                                if not pstripped or pstripped.startswith('#'):
                                    i += 1
                                    continue
                                pindent = len(pline) - len(pline.lstrip())
                                if pindent <= 2:
                                    break
                                if ':' in pstripped:
                                    pk, pv = pstripped.split(':', 1)
                                    pk = pk.strip()
                                    pv = pv.strip().strip("'\"")
                                    if pv.lower() == 'true':
                                        inp_dict[pk] = True
                                    elif pv.lower() == 'false':
                                        inp_dict[pk] = False
                                    else:
                                        inp_dict[pk] = pv
                                i += 1
                            inputs_map[inp_key] = inp_dict
                        else:
                            i += 1
                    data['inputs'] = inputs_map
                elif key == 'branding':
                    branding_map: Dict[str, Any] = {}
                    while i < len(lines):
                        bline = lines[i]
                        bstripped = bline.strip()
                        if not bstripped or bstripped.startswith('#'):
                            i += 1
                            continue
                        bindent = len(bline) - len(bline.lstrip())
                        if bindent == 0:
                            break
                        if bindent == 2 and ':' in bstripped:
                            bk, bv = bstripped.split(':', 1)
                            branding_map[bk.strip()] = bv.strip().strip("'\"")
                        i += 1
                    data['branding'] = branding_map
                elif key == 'runs':
                    runs_map: Dict[str, Any] = {}
                    while i < len(lines):
                        rline = lines[i]
                        rstripped = rline.strip()
                        if not rstripped or rstripped.startswith('#'):
                            i += 1
                            continue
                        rindent = len(rline) - len(rline.lstrip())
                        if rindent == 0:
                            break
                        if rindent == 2 and ':' in rstripped:
                            rk, rv = rstripped.split(':', 1)
                            rk = rk.strip()
                            rv = rv.strip().strip("'\"")
                            if rk == 'steps':
                                steps: List[Dict[str, Any]] = []
                                i += 1
                                current_step: Dict[str, Any] | None = None
                                multiline_key: str | None = None
                                multiline_lines: List[str] = []
                                multiline_indent = 0
                                while i < len(lines):
                                    sline = lines[i]
                                    sstripped = sline.strip()
                                    if not sstripped or sstripped.startswith('#'):
                                        if multiline_key:
                                            multiline_lines.append('')
                                        i += 1
                                        continue
                                    sindent = len(sline) - len(sline.lstrip())
                                    if sindent <= 2 and not sstripped.startswith('-'):
                                        break
                                    if multiline_key:
                                        if sindent >= multiline_indent:
                                            multiline_lines.append(sline[multiline_indent:] if len(sline) >= multiline_indent else sstripped)
                                            i += 1
                                            continue
                                        else:
                                            if current_step is not None:
                                                current_step[multiline_key] = '\n'.join(multiline_lines) + '\n'
                                            multiline_key = None
                                            multiline_lines = []
                                    if sstripped.startswith('- '):
                                        if current_step is not None:
                                            steps.append(current_step)
                                        current_step = {}
                                        content = sstripped[2:].strip()
                                        if ':' in content:
                                            sk, sv = content.split(':', 1)
                                            current_step[sk.strip()] = sv.strip().strip("'\"")
                                        i += 1
                                    elif ':' in sstripped:
                                        sk, sv = sstripped.split(':', 1)
                                        sk = sk.strip()
                                        sv = sv.strip()
                                        if sv == '|':
                                            multiline_key = sk
                                            multiline_lines = []
                                            if i + 1 < len(lines):
                                                next_l = lines[i + 1]
                                                multiline_indent = len(next_l) - len(next_l.lstrip())
                                            else:
                                                multiline_indent = sindent + 2
                                            i += 1
                                        elif sv == '' and i + 1 < len(lines) and len(lines[i+1]) - len(lines[i+1].lstrip()) > sindent:
                                            submap: Dict[str, Any] = {}
                                            i += 1
                                            while i < len(lines):
                                                subl = lines[i]
                                                substr = subl.strip()
                                                if not substr or substr.startswith('#'):
                                                    i += 1
                                                    continue
                                                subind = len(subl) - len(subl.lstrip())
                                                if subind <= sindent:
                                                    break
                                                if ':' in substr:
                                                    subk, subv = substr.split(':', 1)
                                                    submap[subk.strip()] = subv.strip().strip("'\"")
                                                i += 1
                                            if current_step is not None:
                                                current_step[sk] = submap
                                        else:
                                            if current_step is not None:
                                                current_step[sk] = sv.strip("'\"")
                                            i += 1
                                    else:
                                        i += 1
                                if current_step is not None:
                                    if multiline_key:
                                        current_step[multiline_key] = '\n'.join(multiline_lines) + '\n'
                                    steps.append(current_step)
                                runs_map['steps'] = steps
                            else:
                                runs_map[rk] = rv
                                i += 1
                        else:
                            i += 1
                    data['runs'] = runs_map
        else:
            i += 1
    return data


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
            try:
                cls.parsed = yaml.safe_load(cls.content)
            except Exception:
                cls.parsed = None
        else:
            cls.parsed = None

        if cls.parsed is None:
            cls.parsed = parse_simple_action_yaml(cls.content)

    def test_01_action_file_exists(self):
        """action.yml must exist at repository root."""
        self.assertTrue(self.action_file.is_file(), "action.yml missing from repo root")
        self.assertGreater(len(self.content), 0, "action.yml is empty")

    def test_02_valid_yaml_structure(self):
        """action.yml must parse as a valid YAML mapping."""
        self.assertIsNotNone(self.parsed, "Failed to parse action.yml structure")
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

    def test_10_zero_dependency_parser_equivalence(self):
        """When PyYAML is available, verify fallback parser output matches PyYAML."""
        if yaml is None:
            self.skipTest("PyYAML is not installed; skipping parser equivalence comparison")

        yaml_parsed = yaml.safe_load(self.content)
        fallback_parsed = parse_simple_action_yaml(self.content)

        self.assertEqual(fallback_parsed['name'], yaml_parsed['name'])
        self.assertEqual(fallback_parsed['description'], yaml_parsed['description'])
        self.assertEqual(list(fallback_parsed['inputs'].keys()), list(yaml_parsed['inputs'].keys()))
        self.assertEqual(fallback_parsed['runs']['using'], yaml_parsed['runs']['using'])
        self.assertEqual(len(fallback_parsed['runs']['steps']), len(yaml_parsed['runs']['steps']))
        if 'branding' in yaml_parsed:
            self.assertEqual(fallback_parsed.get('branding'), yaml_parsed.get('branding'))

    def test_11_branding_metadata(self):
        """action.yml must specify valid branding icon and color for GitHub Marketplace."""
        self.assertIn('branding', self.parsed, "Missing 'branding' key for Marketplace listing")
        branding = self.parsed['branding']
        self.assertIn('icon', branding, "Missing 'icon' in branding metadata")
        self.assertIn('color', branding, "Missing 'color' in branding metadata")
        self.assertEqual(branding['icon'], 'shield')
        self.assertIn(branding['color'], ['blue', 'purple', 'green', 'gray-dark', 'red'])


if __name__ == '__main__':
    unittest.main()
