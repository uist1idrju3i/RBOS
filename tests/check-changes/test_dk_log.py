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
        self.assertEqual(tuple(items) + ("P1 selftest",),
                         dk_log.PASSES[:2] + ("same-priority fairness",) + dk_log.PASSES[2:])

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

    def test_stress_acceptance_defaults(self):
        self.assert_fails(synthetic("stress", connected=True), "under spinner load", profile="stress")
        report = dk_log.analyze(synthetic("stress", end=310, connected=True), profile="stress")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["stress_connected_duration_s"], 300)
        self.assertEqual(report["required_connected_duration_s"], 300)
        self.assertEqual(dk_log.analyze(synthetic("stress"), profile="stress", require_connected=0)["errors"], [])
        data = synthetic("stress", end=330, connected=True).replace(
            b"STRESS: spinner a started\nSTRESS: spinner b started\n", b"")
        data = b"\n".join(line for line in data.split(b"\n")
                          if not re.search(rb"stress [ab]=(?:10|20|30|40|50)$", line))
        data = data.replace(b"stress a=60", b"STRESS: spinner a started\nSTRESS: spinner b started\nstress a=60")
        report = self.assert_fails(data, "under spinner load", profile="stress")
        self.assertEqual(len(report["errors"]), 1)

    def test_spinner_rates_wrap_and_imbalance(self):
        counts = {10: 999990, 20: 10, 30: 30, 40: 50, 50: 70, 60: 90}
        data = re.sub(rb"stress ([ab])=(\d+)",
                      lambda match: b"stress " + match[1] + b"=%d" % counts[int(match[2])],
                      synthetic("stress"))
        report = dk_log.analyze(data, profile="stress", require_connected=0)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["spinners"]["a"]["mean_per_s"], 2)
        self.assertEqual(report["spinners"]["a"]["intervals"][0]["delta"], 20)
        self.assertEqual(report["spinner_a_b_ratio"], 1)
        for stopped in (b"a", b"b"):
            zeroed = re.sub(rb"stress " + stopped + rb"=\d+", b"stress " + stopped + b"=0", data)
            report = dk_log.analyze(zeroed, profile="stress", require_connected=0)
            self.assertTrue(any("Spinner rate imbalance" in error for error in report["errors"]))
            self.assertEqual(report["spinner_a_b_ratio"], 0 if stopped == b"a" else None)
        self.assert_fails(data.replace(b"stress a=999990", b"stress a=1000000", 1), "Invalid spinner", profile="stress")
        report = dk_log.analyze(synthetic("stress", end=20).replace(b"stress b=20\n", b""),
                                profile="stress", require_connected=0)
        self.assertEqual(report["errors"], [])
        self.assertIsNone(report["spinner_a_b_ratio"])
        self.assertIsNone(report["spinners"]["b"]["mean_per_s"])
        self.assertTrue(any("rates unavailable" in note for note in report["warnings"]))

    def test_real_stress_capture(self):
        path = Path(__file__).with_name("stress-capture.txt")
        report = self.assert_fails(path.read_bytes(), "under spinner load", profile="stress")
        self.assertAlmostEqual(report["stress_connected_duration_s"], 230.067537)
        self.assertEqual(report["jitter"]["connected"]["tick_us_min"], 922)
        self.assertEqual(report["jitter"]["connected"]["tick_us_max"], 1063)
        self.assertEqual(report["peaks"]["drain_us"], 144)
        self.assertTrue(0.09 < report["spinner_a_b_ratio"] < 0.11)
        self.assertGreater(report["spinner_imbalance_ratio"], 9)
        result = subprocess.run([sys.executable, str(CHECKER), str(path), "--profile", "stress"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("ERROR: Spinner rate imbalance", result.stdout)
        self.assertIn("230.067537 / 300 s required", result.stdout)
        report = dk_log.analyze(path.read_bytes(), profile="stress", require_connected=230)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("Spinner rate imbalance", report["errors"][0])

    def test_ble_reply_stress_capture(self):
        path = Path(__file__).with_name("stress-connected-capture.txt")
        data = path.read_bytes()
        report = dk_log.analyze(data, profile="stress")
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("Spinner rate imbalance", report["errors"][0])
        self.assertEqual(report["boot"]["sha"], "f85c2fbe5456")
        self.assertAlmostEqual(report["stress_connected_duration_s"], 400.122214)
        self.assertFalse(any(event["kind"] == "disconnected" for event in report["events"]))
        self.assertEqual(report["jitter"]["connected"]["tick_us_min"], 920)
        self.assertEqual(report["jitter"]["connected"]["tick_us_max"], 1064)
        self.assertEqual(report["peaks"], {"pool": 15428, "main": 696, "isr": 560, "drain_us": 60,
                                           "pool_total": 65536, "pool_percent": 23.54126})
        self.assertAlmostEqual(report["spinner_a_b_ratio"], 0.100775)
        result = subprocess.run([sys.executable, str(CHECKER), str(path), "--profile", "stress"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL: stress", result.stdout)
        self.assertIn("ERROR: Spinner rate imbalance", result.stdout)

    def test_ble_reconnect_capture(self):
        data = Path(__file__).with_name("stress-reconnect-capture.txt").read_bytes()
        report = self.assert_fails(data, "under spinner load", profile="stress")
        self.assertEqual(len(report["errors"]), 2)
        self.assertAlmostEqual(report["stress_connected_duration_s"], 70.024438)
        self.assertEqual(sum(event["kind"] == "connected" for event in report["events"]), 2)
        self.assertEqual(sum(event["kind"] == "disconnected" for event in report["events"]), 2)
        self.assertEqual(data.count(b"BLE disconnected reason=0x13"), 2)
        self.assertIn(b"[00:01:52.880,452] <inf> ble_adv: Slow advertising", data)
        self.assertIn(b"[00:04:52.847,109] <inf> ble_adv: Idle", data)
        diagnostic = dk_log.analyze(data, profile="stress", require_connected=0)
        self.assertEqual(len(diagnostic["errors"]), 1)
        self.assertIn("Spinner rate imbalance", diagnostic["errors"][0])

    def test_fair_spinner_captures(self):
        for variant, ratio, duration, drain in [("x", 1.005919, 400.142051, 60),
                                                ("y", 1.005926, 380.184999, 148)]:
            with self.subTest(variant=variant):
                path = Path(__file__).with_name(f"stress-{variant}-capture.txt")
                data = path.read_bytes()
                report = dk_log.analyze(data, profile="stress")
                self.assertEqual(report["errors"], [])
                self.assertEqual(report["boot"]["sha"], "7217cb685dd2")
                self.assertAlmostEqual(report["spinner_a_b_ratio"], ratio)
                self.assertAlmostEqual(report["stress_connected_duration_s"], duration)
                self.assertEqual(report["peaks"]["drain_us"], drain)
                self.assertEqual(data.count(b"BLE disconnected reason=0x13"), variant == "y")
                result = subprocess.run([sys.executable, str(CHECKER), str(path), "--profile", "stress"],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertIn("PASS: stress", result.stdout)

    def test_fairness_boundary(self):
        data = synthetic("stress")
        for multiplier, passed in [(2, True), (3, False)]:
            scaled = re.sub(rb"stress a=(\d+)",
                            lambda match: b"stress a=%d" % (int(match[1]) * multiplier), data)
            report = dk_log.analyze(scaled, profile="stress", require_connected=0)
            self.assertEqual(not report["errors"], passed)

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
        self.assert_fails(synthetic("oom").replace(b"OOM: start\nRBOS fatal: Ruby pool exhausted",
                                                  b"RBOS fatal: Ruby pool exhausted\nOOM: start"),
                          "precedes OOM start", profile="oom")

    def test_real_oom_capture(self):
        path = Path(__file__).with_name("oom-capture.txt")
        report = dk_log.analyze(path.read_bytes(), profile="oom")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["boot"]["sha"], "3d1fd598c609")
        self.assertEqual(report["stats_lines"], 0)
        self.assertEqual(report["peaks"]["pool"], None)
        self.assertEqual(report["oom"], {"start_line": 13, "fatal_line": 14})
        self.assertEqual(report["events"][0]["line"], 12)
        self.assertTrue(any("Ignored 1 pre-boot line(s)" in note for note in report["warnings"]))
        self.assertFalse(any("Detected 2 boots" in note for note in report["warnings"]))
        result = subprocess.run([sys.executable, str(CHECKER), str(path), "--profile", "oom"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS: oom", result.stdout)
        self.assertIn("NOTE: Ignored 1 pre-boot line(s)", result.stdout)

    def test_last_boot_only(self):
        for profile in ("selftest", "stress", "oom"):
            for marker in (b"", b"*** Booting MCUboot vtest ***\n"):
                with self.subTest(profile=profile, marker=marker):
                    old = marker + synthetic(profile) + b"FAIL: old boot\n"
                    current = marker + synthetic(profile).replace(b"abcdef123456", b"123abc456def")
                    report = dk_log.analyze(old + current, profile=profile, require_connected=0)
                    self.assertEqual(report["errors"], [])
                    self.assertEqual(report["boot"]["sha"], "123abc456def")
                    self.assertEqual(report["stats_lines"], 0 if profile == "oom" else 6)
                    self.assertTrue(any("Detected 2 boots" in note for note in report["warnings"]))
                    if profile != "oom":
                        self.assert_fails(old + current.replace(b"PASS: P1 selftest\n", b""),
                                          "Missing PASS: P1 selftest", profile=profile)
                    else:
                        self.assert_fails(old + current.replace(b"RBOS fatal: Ruby pool exhausted", b""),
                                          "exact pool-exhaustion fatal", profile=profile)
        self.assert_fails(synthetic() + b"*** Booting MCUboot vtest ***", "boot banner")
        report = dk_log.analyze(real_log() + synthetic())
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["boot"]["sha"], "abcdef123456")
        self.assertEqual(report["events"], [])

    def test_midline_app_boot_and_original_line_numbers(self):
        data = b"FAIL: old boot\n" + stamp(100).encode() + b" stats tick_us=9" + synthetic("oom")
        report = dk_log.analyze(data, profile="oom")
        self.assertEqual(report["errors"], [])
        self.assertTrue(any("Ignored 2 pre-boot line(s)" in note for note in report["warnings"]))
        self.assertEqual(report["oom"], {"start_line": 4, "fatal_line": 5})
        self.assert_fails(data.replace(b"pool exhausted", b"bad pool"), "Unexpected fatal/assert", profile="oom")

    def test_garbage_crlf_ansi_and_partial_first_line(self):
        data = b"partial \xff\xfe\r" + b"\x1b[32m" + real_log().replace(b"\n", b"\r\n") + b"\x1b[0m"
        self.assertEqual(dk_log.analyze(data)["errors"], [])
        self.assertEqual(dk_log.analyze(b"stats tick_us=9\r" + real_log())["status"], "PASS")
        self.assertEqual(dk_log.analyze(b"\x1b]0;title\x1b\\" + real_log() + b"\x1b]0;end\x1b\\")["status"], "PASS")

    def test_empty_headers(self):
        self.assert_fails(b"", "boot banner")
        self.assert_fails(synthetic().replace(b"RBOS 0.1.0+0", b""), "Missing RBOS")

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
                command = command.replace("duration=420", "duration=1")
                command = command.replace('log="dk-stress-$(date +%Y%m%d-%H%M%S).log"', "log=" + shlex.quote(str(log)))
                command = command.replace("--profile stress --min-duration 300 --require-connected 300",
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
