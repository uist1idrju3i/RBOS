import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "tools/bm-build/simulate-spinner.py"
SPEC = importlib.util.spec_from_file_location("spinner_model", SCRIPT)
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


class SpinnerModelTests(unittest.TestCase):
    def test_current_and_comparisons(self):
        for first in ("a", "b"):
            with self.subTest(first=first):
                current = model.simulate(10, 10, 110000, first)
                self.assertEqual(current["max_min_ratio"], 10)
                self.assertEqual(current["a_b_ratio"], 10 if first == "a" else 0.1)
                self.assertEqual(current["service_calls"], 10000)
                for quantum, sleep_ms in ((1, 10), (10, 9), (10, None)):
                    result = model.simulate(quantum, sleep_ms, 110000, first)
                    self.assertEqual(result["a_ticks"], 55000)
                    self.assertEqual(result["b_ticks"], 55000)
                    self.assertEqual(result["a_b_ratio"], 1)

    def test_strict_wake_deadline_and_budget_loss(self):
        self.assertEqual(model.simulate(10, 10, 10)["service_calls"], 0)
        self.assertEqual(model.simulate(10, 10, 11)["service_calls"], 1)
        self.assertEqual(model.simulate(10, 9, 10)["service_calls"], 1)
        result = model.simulate(10, 10, 22)
        self.assertEqual((result["a_ticks"], result["b_ticks"]), (20, 2))
        self.assertEqual(model.simulate(255, 1000, 1)["a_ticks"], 1)

    def test_empty_and_invalid_inputs(self):
        result = model.simulate(10, 10, 0)
        self.assertEqual(result["a_ticks"] + result["b_ticks"], 0)
        self.assertIsNone(result["a_b_ratio"])
        self.assertIsNone(result["max_min_ratio"])
        for args in ((0, 10, 1), (256, 10, 1), (10, 0, 1), (10, 1001, 1),
                     (10, 10, -1), (10, 10, 1, "c")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                model.simulate(*args)

    def test_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--ticks", "0"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MODEL ONLY", result.stdout)
        self.assertIn("default first=b quantum=1 sleep_ms=10", result.stdout)
        self.assertIn("Y first=b", result.stdout)
        result = subprocess.run([sys.executable, str(SCRIPT), "--ticks", "-1"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("ticks must be nonnegative", result.stderr)
