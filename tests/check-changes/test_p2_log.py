import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("p2_log", ROOT / "tools/bm-build/check-p2-log.py")
p2_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p2_log)


def fixture():
    lines = ["PASS: P2 native setup", "resources sched_bytes=512 sched_header=12 service_ms=10 sd_ram=5000"]
    lines += [f"scheduler_probe payload={size} accepted=4 delivered=5 exhausted=1 recovered=1" for size in (0, 16, 64)]
    lines += [f"button index={index} level={level} count=1" for index in range(4) for level in (0, 1)]
    lines += ["temperature c=25\nadc rail=dvdd raw=1024 volts=0.9\nadc rail=avdd raw=1024 volts=0.9\nadc rail=vdd raw=3413 volts=3.0"] * 3
    return ("\n".join(lines) + "\n").encode()


class P2LogTests(unittest.TestCase):
    limits = {"temperature_c": [20, 30], "dvdd_v": [0.8, 1.0], "avdd_v": [0.8, 1.0], "vdd_v": [2.9, 3.1]}

    def test_repeatability_bounds_and_incomplete_accuracy(self):
        self.assertEqual(p2_log.analyze(fixture(), self.limits)["status"], "PASS")
        self.assertEqual(p2_log.analyze(fixture())["status"], "INCOMPLETE")
        self.assertEqual(p2_log.analyze(fixture(), self.limits)["completion"]["real_hardware"], "INCOMPLETE")

    def test_missing_failure_bad_count_voltage_and_duplicate_probe(self):
        variants = [
            fixture().replace(b"PASS: P2 native setup", b""),
            fixture().replace(b"button index=3 level=0 count=1", b""),
            fixture().replace(b"count=1", b"count=0"),
            fixture().replace(b"volts=3.0", b"volts=3.5"),
            fixture().replace(b"raw=1024", b"raw=32768"),
            fixture().replace(b"recovered=1", b"recovered=0"),
            fixture().replace(b"sd_ram=5000", b"sd_ram=0"),
            fixture() + b"p2 error=driver failed\n",
            fixture() + b"resources sched_bytes=bad\n",
            fixture().replace(b"sd_ram=5000", b"sd_ram=5000 trailing"),
            fixture().replace(b"recovered=1", b"recovered=1 trailing"),
            fixture() + b"Exception(vm_id=1): unexpected\n",
            fixture() + b"RBOS fatal: unexpected\n",
            fixture() + b"temperature c=1e999\n",
            fixture() + b"adc rail=vdd raw=0 volts=nan\n",
            fixture() + b"button index=7 level=1 count=1\n",
            fixture() + b"scheduler_probe payload=0 accepted=4 delivered=5 exhausted=1 recovered=1\n",
            fixture().replace(b"temperature c=25\n", b"", 1),
        ]
        for data in variants:
            with self.subTest(data=data[-80:]):
                self.assertEqual(p2_log.analyze(data, self.limits)["status"], "FAIL")

    def test_last_boot_does_not_reuse_old_peripheral_evidence(self):
        data = b"*** Booting My Application v1 ***\n" + fixture()
        data += b"*** Booting My Application v2 ***\nPASS: P2 native setup\n"
        self.assertEqual(p2_log.analyze(data, self.limits)["status"], "FAIL")

    def test_invalid_bounds_rejected(self):
        for limits in ({}, {**self.limits, "vdd_v": [3, 2]}, {**self.limits, "dvdd_v": [float('nan'), 1]},
                       {**self.limits, "avdd_v": [True, 1]}):
            with self.assertRaises(ValueError):
                p2_log.validate_limits(limits)
