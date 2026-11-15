import importlib.util
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('allocation_checker', ROOT / 'tools/mrubyc-wasm/check-allocations.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class AllocationInventoryTests(unittest.TestCase):
    def result(self, command, **kwargs):
        operation, point = command[-2:]
        count = next(len(case['points']) for case in self.table['cases'] if case['operation'] == operation)
        if point == '0':
            return subprocess.CompletedProcess(command, 0,
                f'PASS: binding allocation control {operation} allocations={count}\n', '')
        return subprocess.CompletedProcess(command, 1,
            f'PASS: binding OOM {operation} allocation={point} watches=0\n',
            'Fatal error: Out of memory.\n')

    def setUp(self):
        self.table = json.loads((ROOT / 'tools/mrubyc-wasm/allocation-cases.json').read_text())

    def test_all_controls_and_fatal_points_run(self):
        with mock.patch.object(checker.subprocess, 'run', side_effect=self.result) as run:
            with mock.patch('builtins.print'):
                checker.check(Path('fixture'))
        self.assertEqual(run.call_count, 18)

    def test_empty_missing_or_wrong_exit_output_is_rejected(self):
        for result in (subprocess.CompletedProcess([], 0, '', ''),
                       subprocess.CompletedProcess([], 73, '', 'Fatal error: Out of memory.\n')):
            with self.subTest(result=result), mock.patch.object(checker.subprocess, 'run', return_value=result):
                with self.assertRaises(AssertionError):
                    checker.check(Path('fixture'))

    def test_timeout_is_not_a_fatal_pass(self):
        with mock.patch.object(checker.subprocess, 'run', side_effect=subprocess.TimeoutExpired([], 15)):
            with self.assertRaises(subprocess.TimeoutExpired):
                checker.check(Path('fixture'))
