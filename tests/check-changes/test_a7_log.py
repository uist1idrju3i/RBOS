import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/bm-build/check-a7-log.py"
spec = importlib.util.spec_from_file_location("a7_log", SCRIPT)
a7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a7)


def fixture():
    lines = ["a7 setup pin=43 timer=21 path=port capacity=16"]
    for phase, values, delivery in (
        ("coalesce", (5, 5, 5, 0, 1, 0, 0, 0, 4, 0, 1), "ruby level=1 count=5"),
        ("drop", (5, 5, 0, 16, 16, 0, 5, 4, 4, 1, 0), "none level=0 count=0"),
        ("full", (5, 5, 5, 16, 16, 5, 5, 4, 8, 0, 1), "ruby level=1 count=5"),
    ):
        lines.append(f"a7 phase={phase}" + "".join(f" {key}={value}" for key, value in zip(a7.FIELDS, values)))
        lines.append(f"a7 delivery phase={phase} via={delivery} pending=0")
    return ("\n".join(lines + ["a7 done phases=3"]) + "\n").encode()


def retention(mode):
    return (f"p5 mode={mode} nonce=1234abcd sentinel=23456789 peer_before=00000000 peer_after=00000000 verified=1 writes={int(mode == 'seed')}\n").encode()


class A7LogTests(unittest.TestCase):
    def test_saturation_and_uart_prefix(self):
        self.assertEqual(a7.saturation(fixture())["status"], "PASS")
        log = b"\n".join(b"\x1b[0m[00:00:01] <inf> rbos_saturation: " + line for line in fixture().splitlines())
        self.assertEqual(a7.saturation(log)["status"], "PASS")

    def test_missing_duplicate_malformed_and_extra(self):
        lines = fixture().splitlines(keepends=True)
        for index in range(len(lines)):
            for data in (b"".join(lines[:index] + lines[index + 1:]),
                         b"".join(lines[:index] + [lines[index]] + lines[index:]),
                         b"".join(lines[:index] + [lines[index].rstrip() + b" trailing\n"] + lines[index + 1:])):
                with self.subTest(index=index, data=data), self.assertRaises(ValueError):
                    a7.saturation(data)
        for data in (b"", fixture() + b"a7 error=driver\n", fixture() + b"RBOS fatal: test\n"):
            with self.assertRaises(ValueError):
                a7.saturation(data)

    def test_each_counter_and_delivery_mismatch(self):
        for key in a7.FIELDS:
            for value in (b"999", b"4294967296", b"-1", b"01", b"nan"):
                data = re.sub(rb"\b" + key.encode() + rb"=[0-9]+", key.encode() + b"=" + value, fixture(), count=1)
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    a7.saturation(data)
        for old, new in ((b"via=ruby", b"via=none"), (b"count=5", b"count=4"),
                         (b"pending=0\na7 phase=drop", b"pending=1\na7 phase=drop")):
            with self.assertRaises(ValueError):
                a7.saturation(fixture().replace(old, new, 1))

    def test_retention_normal_and_rejections(self):
        seed, verify = retention("seed"), retention("verify")
        self.assertEqual(a7.retention(seed, verify)["status"], "PASS")
        for first, second in ((b"", verify), (seed, b""), (seed * 2, verify), (seed, verify * 2),
                (verify, seed), (seed, verify.replace(b"writes=0", b"writes=1")),
                (seed, verify.replace(b"1234abcd", b"00000000")),
                (seed, verify.replace(b"23456789", b"23456788")),
                (seed, verify.replace(b"peer_after=00000000", b"peer_after=00000001")),
                (seed, verify + b"p5 error=corrupt\n"), (seed, verify + b"RBOS fatal: test\n"),
                (seed, verify.replace(b"verified=1", b"verified=0")),
                (seed, verify.replace(b"\n", b" trailing\n"))):
            with self.subTest(first=first, second=second), self.assertRaises(ValueError):
                a7.retention(first, second)

    def test_cli_errors_and_success(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "uart.log"
            path.write_bytes(fixture())
            for args, status in ((["saturation", str(path)], 0), (["retention", str(path)], 1),
                    (["saturation", str(path) + ".missing"], 1), (["retention", str(path), str(path)], 1)):
                result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True)
                self.assertEqual(result.returncode, status, result.stdout + result.stderr)
