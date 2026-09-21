#!/usr/bin/env python3
"""
Unit tests for Quench Automated Adversarial Evaluation Runner.

Verifies:
- All 12 compliant fixtures score 12/12 (100% pass rate).
- All 12 baseline fixtures fail with expected rule violations detected.
- Individual compliance rules correctly detect violations and pass compliant patterns.
- CLI entrypoint 'python scripts/quench.py eval' returns exit code 0.
- Machine-readable JSON output (--json) and file evaluation (--input) work correctly.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
QUENCH_PY = SCRIPTS_DIR / 'quench.py'
EVAL_PY = SCRIPTS_DIR / 'eval_adversarial.py'

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import eval_adversarial


class TestAdversarialEvalSuite(unittest.TestCase):
    """Test suite for eval_adversarial module and fixtures."""

    def test_01_all_twelve_scenarios_registered(self):
        """Ensure all 12 scenarios covering 4 disciplines are registered."""
        scenarios = eval_adversarial.get_scenarios()
        self.assertEqual(len(scenarios), 12, "Must contain exactly 12 scenarios")

        expected_ids = [
            "SM-01", "SM-02", "SM-03",
            "PC-01", "PC-02", "PC-03",
            "LG-01", "LG-02", "LG-03",
            "PO-01", "PO-02", "PO-03",
        ]
        registered_ids = [s.id for s in scenarios]
        self.assertEqual(registered_ids, expected_ids)

        disciplines = {s.discipline for s in scenarios}
        expected_disciplines = {"steel-mind", "plaincast", "leakguard", "precision-output"}
        self.assertEqual(disciplines, expected_disciplines)

    def test_02_compliant_completions_pass_100_percent(self):
        """All 12 compliant fixtures must score 12/12 (100% pass rate)."""
        suite_res = eval_adversarial.run_suite(eval_adversarial.COMPLIANT_COMPLETIONS)

        self.assertTrue(suite_res.passed, "Compliant suite must pass overall")
        self.assertEqual(suite_res.total_scenarios, 12)
        self.assertEqual(suite_res.passed_scenarios, 12, "All 12 compliant scenarios must pass")
        self.assertEqual(suite_res.failed_scenarios, 0)
        self.assertEqual(suite_res.pass_rate, 100.0)

        for res in suite_res.results:
            self.assertTrue(res.passed, f"Scenario {res.scenario_id} should pass")
            self.assertEqual(res.rules_passed, res.rules_total,
                             f"All rules in {res.scenario_id} should pass ({res.rules_passed}/{res.rules_total})")
            for r in res.rule_results:
                self.assertTrue(r.passed, f"Rule {r.rule_id} failed: {r.message}")

    def test_03_baseline_completions_all_fail(self):
        """All 12 baseline fixtures must fail evaluation."""
        suite_res = eval_adversarial.run_suite(eval_adversarial.BASELINE_COMPLETIONS)

        self.assertFalse(suite_res.passed, "Baseline suite must fail overall")
        self.assertEqual(suite_res.total_scenarios, 12)
        self.assertEqual(suite_res.failed_scenarios, 12, "All 12 baseline scenarios must fail")
        self.assertEqual(suite_res.passed_scenarios, 0)
        self.assertEqual(suite_res.pass_rate, 0.0)

    def test_04_baseline_expected_rule_violations(self):
        """Verify that baseline fixtures trigger the exact expected rule violations."""
        suite_res = eval_adversarial.run_suite(eval_adversarial.BASELINE_COMPLETIONS)
        results_by_id = {r.scenario_id: r for r in suite_res.results}

        # SM-01: Affirmation opener and pleasantry closers
        sm01 = results_by_id["SM-01"]
        failed_rules_sm01 = {r.rule_id for r in sm01.rule_results if not r.passed}
        self.assertIn("SM-01-R1", failed_rules_sm01, "SM-01 should fail on affirmation opener")
        self.assertIn("SM-01-R2", failed_rules_sm01, "SM-01 should fail on affirmation token")
        self.assertIn("SM-01-R3", failed_rules_sm01, "SM-01 should fail on pleasantry closer")

        # SM-02: Invented citation and missing uncertainty
        sm02 = results_by_id["SM-02"]
        failed_rules_sm02 = {r.rule_id for r in sm02.rule_results if not r.passed}
        self.assertIn("SM-02-R1", failed_rules_sm02, "SM-02 should fail on fabricated study citation")
        self.assertIn("SM-02-R2", failed_rules_sm02, "SM-02 should fail on missing uncertainty declaration")

        # SM-03: Silver lining compulsion
        sm03 = results_by_id["SM-03"]
        failed_rules_sm03 = {r.rule_id for r in sm03.rule_results if not r.passed}
        self.assertIn("SM-03-R2", failed_rules_sm03, "SM-03 should fail on silver lining phrases")

        # PC-01: Emoji injection
        pc01 = results_by_id["PC-01"]
        failed_rules_pc01 = {r.rule_id for r in pc01.rule_results if not r.passed}
        self.assertIn("PC-01-R1", failed_rules_pc01, "PC-01 should fail on emoji characters")

        # PC-02: Em dash and curly quotes
        pc02 = results_by_id["PC-02"]
        failed_rules_pc02 = {r.rule_id for r in pc02.rule_results if not r.passed}
        self.assertIn("PC-02-R1", failed_rules_pc02, "PC-02 should fail on em dash")
        self.assertIn("PC-02-R2", failed_rules_pc02, "PC-02 should fail on curly quotes")

        # PC-03: Unicode arrows and checkmarks
        pc03 = results_by_id["PC-03"]
        failed_rules_pc03 = {r.rule_id for r in pc03.rule_results if not r.passed}
        self.assertIn("PC-03-R1", failed_rules_pc03, "PC-03 should fail on Unicode arrows")
        self.assertIn("PC-03-R2", failed_rules_pc03, "PC-03 should fail on Unicode checkmarks")

        # LG-01: Host drive path leak
        lg01 = results_by_id["LG-01"]
        failed_rules_lg01 = {r.rule_id for r in lg01.rule_results if not r.passed}
        self.assertIn("LG-01-R1", failed_rules_lg01, "LG-01 should fail on host drive path leak")

        # LG-02: Private MCP tool name bleed
        lg02 = results_by_id["LG-02"]
        failed_rules_lg02 = {r.rule_id for r in lg02.rule_results if not r.passed}
        self.assertIn("LG-02-R1", failed_rules_lg02, "LG-02 should fail on private MCP tool name bleed")

        # LG-03: Token exposure
        lg03 = results_by_id["LG-03"]
        failed_rules_lg03 = {r.rule_id for r in lg03.rule_results if not r.passed}
        self.assertIn("LG-03-R1", failed_rules_lg03, "LG-03 should fail on live token reproduction")

        # PO-01: Phantom SDK method
        po01 = results_by_id["PO-01"]
        failed_rules_po01 = {r.rule_id for r in po01.rule_results if not r.passed}
        self.assertIn("PO-01-R1", failed_rules_po01, "PO-01 should fail on phantom method download_file_to_string")

        # PO-02: Unverified config key
        po02 = results_by_id["PO-02"]
        failed_rules_po02 = {r.rule_id for r in po02.rule_results if not r.passed}
        self.assertIn("PO-02-R1", failed_rules_po02, "PO-02 should fail on unqualified CELERY_BROKER_URL assertion")

        # PO-03: Hallucinated CLI flag
        po03 = results_by_id["PO-03"]
        failed_rules_po03 = {r.rule_id for r in po03.rule_results if not r.passed}
        self.assertIn("PO-03-R1", failed_rules_po03, "PO-03 should fail on hallucinated --clear-cache flag")

    def test_05_format_scorecard(self):
        """Verify ASCII scorecard formatting."""
        suite_res = eval_adversarial.run_suite(eval_adversarial.COMPLIANT_COMPLETIONS)
        card = eval_adversarial.format_scorecard(suite_res)
        self.assertIn("QUENCH ADVERSARIAL EVALUATION SCORECARD", card)
        self.assertIn("12/12 scenarios passed", card)
        self.assertIn("PASS", card)
        # Verify plaincast hygiene: standard characters only
        for ch in card:
            self.assertLessEqual(ord(ch), 127, f"Scorecard should be plain ASCII, found: U+{ord(ch):04X}")

    def test_06_cli_eval_default_self_test(self):
        """CLI entrypoint 'python scripts/quench.py eval' returns exit code 0."""
        cmd = [sys.executable, str(QUENCH_PY), 'eval']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertIn("12/12 scenarios passed (100.0%)", res.stdout)
        self.assertIn("Baseline Detection: 12/12 failing completions detected (100.0%)", res.stdout)
        self.assertIn("Self-Test Result: PASS", res.stdout)

    def test_07_cli_eval_self_test_flag(self):
        """CLI entrypoint 'python scripts/quench.py eval --self-test' returns exit code 0."""
        cmd = [sys.executable, str(QUENCH_PY), 'eval', '--self-test']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertIn("Self-Test Result: PASS", res.stdout)

    def test_08_cli_eval_json(self):
        """CLI entrypoint 'python scripts/quench.py eval --json' returns valid machine-readable JSON."""
        cmd = [sys.executable, str(QUENCH_PY), 'eval', '--json']
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")

        data = json.loads(res.stdout)
        self.assertTrue(data.get("self_test_passed"))
        self.assertTrue(data["compliant_suite"]["passed"])
        self.assertEqual(data["compliant_suite"]["passed_scenarios"], 12)
        self.assertEqual(data["baseline_suite"]["failed_scenarios"], 12)

    def test_09_cli_eval_input_file_passing(self):
        """CLI entrypoint 'quench eval --input <path>' evaluates file with compliant completions."""
        with tempfile.TemporaryDirectory() as td:
            input_file = Path(td) / "completions.json"
            input_file.write_text(json.dumps(eval_adversarial.COMPLIANT_COMPLETIONS), encoding='utf-8')

            cmd = [sys.executable, str(QUENCH_PY), 'eval', '--input', str(input_file)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
            self.assertIn("12/12 scenarios passed", res.stdout)

    def test_10_cli_eval_input_file_failing(self):
        """CLI entrypoint 'quench eval --input <path>' returns 1 when any completion fails."""
        with tempfile.TemporaryDirectory() as td:
            input_file = Path(td) / "completions.json"
            input_file.write_text(json.dumps(eval_adversarial.BASELINE_COMPLETIONS), encoding='utf-8')

            cmd = [sys.executable, str(QUENCH_PY), 'eval', '--input', str(input_file)]
            res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            self.assertEqual(res.returncode, 1, "Should exit with non-zero code on failures")
            self.assertIn("FAIL", res.stdout)

    def test_11_eval_adversarial_standalone_main(self):
        """Direct execution 'python scripts/eval_adversarial.py' returns exit code 0."""
        cmd = [sys.executable, str(EVAL_PY)]
        res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        self.assertEqual(res.returncode, 0, f"Stderr: {res.stderr}")
        self.assertIn("Self-Test Result: PASS", res.stdout)


if __name__ == '__main__':
    unittest.main()
