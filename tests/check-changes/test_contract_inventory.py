import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("contract_inventory", ROOT / "tools/mrubyc-wasm/check-contracts.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ContractInventoryTests(unittest.TestCase):
    def setUp(self):
        self.inventory = json.loads(checker.INVENTORY.read_text())

    def test_inventory_covers_all_public_rbs_methods(self):
        self.assertEqual(checker.validate(self.inventory), len(checker.public_surface(ROOT)))

    def test_new_rbs_api_and_removed_contract_fail(self):
        with self.assertRaisesRegex(ValueError, "API/RBS inventory mismatch"):
            checker.validate(self.inventory, surface=checker.public_surface(ROOT) | {"GPIO#undocumented"})
        self.inventory["contracts"].pop()
        with self.assertRaisesRegex(ValueError, "API/RBS inventory mismatch"):
            checker.validate(self.inventory)

    def test_new_c_api_cannot_skip_rbs_and_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            shutil.copytree(ROOT / "src/rbos", root / "src/rbos")
            for name in ("sig", "tests", "firmware"):
                (root / name).symlink_to(ROOT / name, target_is_directory=True)
            path = root / "src/rbos/gpio_binding.c"
            path.write_text(path.read_text() + '\nmrbc_define_method(NULL, gpio_class, "undocumented", callback);\n')
            with self.assertRaisesRegex(ValueError, "Binding missing RBS/contract"):
                checker.validate(self.inventory, root)

    def test_missing_lifetime_keyword_contract_or_assertion_fails(self):
        for field in ("lifetime", "keywords"):
            bad = copy.deepcopy(self.inventory)
            bad["defaults"]["Temperature"][field] = [] if field == "lifetime" else ""
            with self.subTest(field=field), self.assertRaises(ValueError):
                checker.validate(bad)
        self.inventory["cases"][0]["marker"] = "nonexistent assertion"
        with self.assertRaisesRegex(ValueError, "Missing test assertion"):
            checker.validate(self.inventory)

    def test_missing_worker_pass_or_substring_match_fails(self):
        markers = ["PASS: fixture", "PASS: worker"]
        self.assertTrue(checker.check_log("PASS: fixture\n", markers))
        self.assertTrue(checker.check_log("PASS: fixture suffix\nPASS: worker\n", markers))
        self.assertEqual(checker.check_log("PASS: fixture\nPASS: worker\n", markers), [])

    def test_failure_after_pass_is_not_accepted(self):
        for marker in ("Exception(vm_id=1)", "Uncaught task exception", "FAIL:",
                       "p2 error=bad", "RBOS fatal: bad", "Fatal error: bad"):
            self.assertTrue(checker.check_log("PASS: fixture\n" + marker, ["PASS: fixture"]), marker)

    def test_exit_zero_without_pass_and_timeout_fail(self):
        inventory = {"suites": [self.inventory["suites"][0]]}
        with tempfile.TemporaryDirectory() as directory:
            for result in (subprocess.CompletedProcess([], 0, "", ""),
                           subprocess.TimeoutExpired([], 30)):
                with mock.patch.object(checker.subprocess, "run") as run:
                    if isinstance(result, Exception):
                        run.side_effect = result
                    else:
                        run.return_value = result
                    reports = checker.run_suites(inventory, Path(directory))
                    self.assertEqual(reports["native_helpers"]["status"], "FAIL")
