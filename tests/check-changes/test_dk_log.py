import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest

if sys.platform.startswith("linux"):
    import pty
    import termios


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/bm-build/check-dk-log.py"
PROCEDURE = ROOT / "research/implementation/dk-provisioning.md"
spec = importlib.util.spec_from_file_location("dk_log", CHECKER)
dk_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dk_log)


def real_log():
    document = (ROOT / "research/implementation/retrospective-P1.md").read_text()
    return next(block.encode() for block in re.findall(r"```text\n(.*?)```", document, re.S)
                if "*** Booting My Application" in block and "stats tick_us=" in block)


def stamp(second):
    return "[%02d:%02d:%02d.000,000]" % (second // 3600, second // 60 % 60, second % 60)


def synthetic(profile="selftest", end=60, progress_end=None, connected=False):
    lines = ["*** Booting My Application v0.1.0-abcdef123456 ***",
             stamp(0) + " <inf> rbos: RBOS 0.1.0+0"]
    if profile == "oom":
        return ("\n".join(lines + ["OOM: start", "RBOS fatal: Ruby pool exhausted"]) + "\n").encode()
    lines += ["PASS: " + item for item in dk_log.PASSES]
    if connected:
        lines.append(stamp(1) + " <inf> rbos_ble: BLE connected")
    if profile == "stress":
        lines += ["STRESS: spinner a started", "STRESS: spinner b started"]
    for second in range(10, end + 1, 10):
        lines.append(stamp(second) + " <inf> rbos_runtime: stats tick_us=930..1040 "
                     "catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 "
                     "idle=%d service=%d drain_us=42" % (second * 1200, second * 91))
        if profile == "stress" and (progress_end is None or second <= progress_end):
            lines += ["stress a=%d" % second, "stress b=%d" % second]
    return ("\n".join(lines) + "\n").encode()


class LogTests(unittest.TestCase):
    def assert_fails(self, data, marker, **kwargs):
        report = dk_log.analyze(data, **kwargs)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(marker in item for item in report["errors"]), report["errors"])
        return report

    def test_real_p1(self):
        report = dk_log.analyze(real_log())
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["boot"], {"version": "0.1.0", "sha": "ff4c23ef63a2"})
        self.assertEqual(report["stats_lines"], 13)
        for state, bounds in [("connected", (936, 1049)), ("disconnected", (930, 1040))]:
            window = report["jitter"][state]
            self.assertEqual((window["tick_us_min"], window["tick_us_max"]), bounds)
        self.assertEqual(report["boundary_windows_excluded"], 2)
        self.assertAlmostEqual(report["fully_connected_duration_s"], 30.000064)
        self.assertAlmostEqual(report["ble_connected_duration_s"], 35.386579)
        self.assertEqual(report["peaks"]["drain_us"], None)
        self.assertEqual(report["peaks"]["pool"], 11560)

    def test_pass_inventory_tracks_coordinator(self):
        coordinator = (ROOT / "firmware/ruby/selftest/coordinator.rb").read_text()
        items = []
        for call in re.findall(r"check\((.*?)\)", coordinator, re.S):
            strings = re.findall(r'"([^"]+)"', call)
            if strings:
                items.append(strings[-1])
        self.assertEqual(tuple(items) + ("P1 selftest",), dk_log.PASSES)

    def test_missing_each_pass(self):
        for item in dk_log.PASSES:
            with self.subTest(item=item):
                self.assert_fails(real_log().replace(("PASS: " + item + "\n").encode(), b""), "Missing PASS: " + item)

    def test_fail_fatal_assert(self):
        for line in (b"FAIL: bad", b"RBOS fatal: bad", b"ZEPHYR FATAL ERROR 4",
                     b"ASSERTION FAIL [condition]", b"Assertion failed", b"abort()"):
            with self.subTest(line=line):
                self.assert_fails(real_log() + line, "marker")

    def test_catchup_and_ticks(self):
        self.assert_fails(real_log().replace(b"catchups=0", b"catchups=1", 1), "Nonzero catchups at line")
        self.assert_fails(real_log().replace(b"ticks=10000", b"ticks=9000", 1), "Ticks outside")
        report = dk_log.analyze(real_log().replace(b"ticks=9965", b"ticks=1", 1))
        self.assertEqual(report["status"], "PASS")

    def test_gap_and_duration(self):
        data = b"\n".join(line for line in real_log().splitlines() if not line.startswith(b"[00:00:20."))
        self.assert_fails(data, "Stats gap")
        self.assert_fails(real_log(), "Stats timeline too short", min_duration=1800)
        self.assert_fails(real_log(), "Fully-connected stats coverage too short", require_connected=31)

    def test_stress_success_and_stall(self):
        report = dk_log.analyze(synthetic("stress", connected=True), profile="stress", min_duration=50,
                                require_connected=50)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["spinners"]["a"]["progress_lines"], 6)
        self.assert_fails(synthetic("stress", progress_end=20), "Spinner a stalled", profile="stress")
        self.assert_fails(synthetic("stress").replace(b"STRESS: spinner b started", b""),
                          "Missing spinner b", profile="stress")
        data = b"\n".join(line for line in synthetic("stress").splitlines()
                           if line not in (b"stress b=30", b"stress b=40", b"stress b=50", b"stress b=60"))
        report = self.assert_fails(data, "Spinner b stalled", profile="stress")
        self.assertFalse(any("Spinner a stalled" in error for error in report["errors"]))

    def test_oom(self):
        report = dk_log.analyze(synthetic("oom"), profile="oom")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["peaks"]["pool"], None)
        self.assert_fails(synthetic("oom").replace(b"RBOS fatal: Ruby pool exhausted", b""),
                          "exact pool-exhaustion fatal", profile="oom")
        self.assert_fails(synthetic("oom").replace(b"Ruby pool exhausted", b"Ruby pool exhausted extra"),
                          "exact pool-exhaustion fatal", profile="oom")
        data = synthetic() + b"OOM: start\nRBOS fatal: Ruby pool exhausted\n"
        report = dk_log.analyze(data, profile="oom")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["peaks"]["pool"], 11560)
        self.assert_fails(b"RBOS fatal: Ruby pool exhausted\nOOM: start\n" + synthetic(),
                          "precedes OOM start", profile="oom")

    def test_garbage_crlf_ansi_and_partial_first_line(self):
        data = b"partial \xff\xfe\r" + b"\x1b[32m" + real_log().replace(b"\n", b"\r\n") + b"\x1b[0m"
        self.assertEqual(dk_log.analyze(data)["errors"], [])
        self.assertEqual(dk_log.analyze(b"stats tick_us=9\r" + real_log())["status"], "PASS")
        self.assertEqual(dk_log.analyze(b"\x1b]0;title\x1b\\" + real_log() + b"\x1b]0;end\x1b\\")["status"], "PASS")

    def test_empty_headers_and_reboots(self):
        self.assert_fails(b"", "boot banner")
        self.assert_fails(synthetic().replace(b"RBOS 0.1.0+0", b""), "Missing RBOS")
        self.assert_fails(synthetic() + synthetic(), "boot banner")

    def test_malformed_zero_capacity_and_counter_reset(self):
        self.assert_fails(synthetic().replace(b"drain_us=42", b"drain_us=bad", 1), "Malformed")
        self.assert_fails(synthetic().replace(b"11560/65536", b"0/0"), "Invalid stats range")
        self.assert_fails(synthetic().replace(b"idle=24000", b"idle=0"), "counter decreased")

    def test_interval_override(self):
        data = synthetic().decode()
        for second in range(60, 0, -10):
            data = data.replace(stamp(second), stamp(second * 2))
        data = data.replace("ticks=10000", "ticks=20000").encode()
        self.assertEqual(dk_log.analyze(data, stats_interval=20)["errors"], [])
        self.assert_fails(data, "Stats gap")

    def test_cli_json_privacy_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.log"
            identifier = "12345" * 2
            path.write_bytes(real_log() + ("\nJ-Link serial: " + identifier).encode())
            result = subprocess.run([sys.executable, str(CHECKER), str(path), "--json"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "PASS")
            self.assertNotIn(identifier, result.stdout + result.stderr)
            path.write_bytes(real_log().replace(b"ticks=10000", identifier.encode()))
            result = subprocess.run([sys.executable, str(CHECKER), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertNotIn(identifier, result.stdout + result.stderr)
            for args in ([], [str(path), "--profile", identifier], [str(path), "--stats-interval", "0"],
                         [str(path), "--min-duration", "nan"], [str(path), "--min-duration", "-1"],
                         [str(path), "--spinner-interval", "inf"], [str(path / "missing")]):
                result = subprocess.run([sys.executable, str(CHECKER), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn(identifier, result.stdout + result.stderr)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux PTY check; macOS remains unverified")
    def test_documented_capture_pipeline(self):
        master, slave = pty.openpty()
        try:
            with tempfile.TemporaryDirectory() as directory:
                log = Path(directory) / "capture.log"
                command = next(line for line in PROCEDURE.read_text().splitlines()
                               if line.startswith("port='/dev/cu.usbmodem<PORT>';"))
                command = command.replace("port='/dev/cu.usbmodem<PORT>'", "port=" + shlex.quote(os.ttyname(slave)))
                command = command.replace("duration=1860", "duration=1")
                command = command.replace('log="dk-stress-$(date +%Y%m%d-%H%M%S).log"', "log=" + shlex.quote(str(log)))
                command = command.replace("--profile stress --min-duration 1800 --require-connected 1800",
                                          "--profile selftest --min-duration 10")
                started = time.monotonic()
                process = subprocess.Popen(command, shell=True, executable="/bin/bash", cwd=ROOT,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                try:
                    deadline = started + 2
                    while time.monotonic() < deadline:
                        attrs = termios.tcgetattr(slave)
                        if not attrs[3] & (termios.ICANON | termios.ECHO) and attrs[2] & termios.CLOCAL:
                            break
                        time.sleep(0.01)
                    else:
                        self.fail("stty did not configure the opened PTY fd")
                    self.assertEqual(attrs[4], termios.B115200)
                    payload = b"partial \xff\r" + real_log().replace(b"\n", b"\r\n")
                    remaining = memoryview(payload)
                    while remaining:
                        remaining = remaining[os.write(master, remaining):]
                    stdout, stderr = process.communicate(timeout=5)
                    self.assertEqual(process.returncode, 0, stderr.decode(errors="replace"))
                    self.assertEqual(log.read_bytes(), payload)
                    self.assertIn(payload, stdout)
                    self.assertIn(b"PASS: selftest", stdout)
                    self.assertLess(time.monotonic() - started, 5)
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate()
        finally:
            os.close(master)
            os.close(slave)


if __name__ == "__main__":
    unittest.main()
