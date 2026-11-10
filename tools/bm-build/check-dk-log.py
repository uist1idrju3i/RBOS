#!/usr/bin/env python3
"""Check RBOS DK console evidence without echoing raw input or device identifiers."""

import argparse
import json
import math
import re
import sys
from pathlib import Path


PASSES = (
    "concurrent workers", "same-priority round robin", "priority change",
    "suspend", "resume", "mutex with sleeping owner", "workers joined",
    "idle wakeup", "P1 selftest",
)
ANSI = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*?(?:\x07|\x1b\\))")
STAMP = re.compile(r"\[(\d{1,4}):([0-5]\d):([0-5]\d)\.(\d{3})(?:,(\d{3}))?\]")
BOOT = re.compile(r"\*\*\* Booting My Application v([\w.+-]+?)-([0-9a-fA-F]{12}) \*\*\*")
STATS = re.compile(
    r"\bstats tick_us=(\d+)\.\.(\d+) catchups=(\d+) ticks=(\d+) "
    r"pool=(\d+)/(\d+) main=(\d+) isr=(\d+) idle=(\d+) service=(\d+)"
    r"(?: drain_us=(\d+))?\s*$"
)
FIELDS = ("tick_min", "tick_max", "catchups", "ticks", "pool", "pool_total",
          "main", "isr", "idle", "service", "drain_us")
FATAL = re.compile(
    r"RBOS fatal|fatal error|assertion.*fail|assert.*fail|\bassert(?:ion)?(?:\s|:|\()|abort\(\)|Halting system|Kernel panic",
    re.IGNORECASE,
)
OOM_FATAL = "RBOS fatal: Ruby pool exhausted"


def timestamp(line):
    match = STAMP.search(line)
    if not match:
        return None
    h, m, s, ms, us = match.groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000 + int(us or 0) / 1000000


def safe(value):
    """Do not expose long digit sequences even in malicious input-derived fields."""
    if isinstance(value, str):
        return re.sub(r"\d{8,}", "<redacted>", value)
    if isinstance(value, dict):
        return {key: safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe(item) for item in value]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if abs(value) >= 100000000:
            return "<redacted>"
        return round(value, 6) if isinstance(value, float) else value
    return value


def analyze(data, profile="selftest", min_duration=0, stats_interval=10,
            spinner_interval=10, require_connected=0):
    lines = ANSI.sub("", data.decode("utf-8", errors="replace")).splitlines()
    errors, warnings, stats, events, boots, versions = [], [], [], [], [], []
    starts = {key: [] for key in "ab"}
    progress = {key: [] for key in "ab"}
    passed, fatal_lines, oom_starts, oom_fatals = set(), [], [], []
    clock = None
    for number, line in enumerate(lines, 1):
        at = timestamp(line)
        if at is not None:
            if clock is not None and at < clock:
                errors.append("Timestamp moved backwards at line %d" % number)
            clock = at
        match = BOOT.search(line)
        if match:
            boots.append({"version": match[1], "sha": match[2].lower()})
        match = re.search(r"\bRBOS ([0-9][\w.+-]*)", line)
        if match:
            versions.append(match[1])
        if line.strip() in {"PASS: " + item for item in PASSES}:
            passed.add(line.strip()[6:])
        if "FAIL:" in line:
            errors.append("FAIL marker at line %d" % number)
        if FATAL.search(line):
            fatal_lines.append(number)
        if "OOM: start" in line:
            oom_starts.append(number)
        if re.search(re.escape(OOM_FATAL) + r"\s*$", line):
            oom_fatals.append(number)
        if "stats tick_us=" in line:
            match = STATS.search(line)
            if number == 1 and at is None:
                continue
            if not match or at is None or any(len(x) > 10 for x in match.groups() if x is not None):
                errors.append("Malformed or untimed stats at line %d" % number)
            else:
                row = dict(zip(FIELDS, (int(x) if x is not None else None for x in match.groups())))
                row.update(time=at, line=number)
                stats.append(row)
        kind = None
        if "BLE disconnected" in line:
            kind = "disconnected"
        elif "BLE connected" in line:
            kind = "connected"
        elif "ble_adv:" in line and "advertis" in line.lower():
            kind = ("fast_advertising" if "Fast advertising" in line else
                    "slow_advertising" if "Slow advertising" in line else "advertising")
        if kind:
            if at is None:
                errors.append("Untimed BLE event at line %d" % number)
            else:
                events.append({"time": at, "kind": kind, "line": number})
        for key in "ab":
            if "STRESS: spinner %s started" % key in line:
                starts[key].append((clock, number))
            if re.search(r"\bstress %s=\d+\s*$" % key, line):
                progress[key].append((clock, number))

    if len(boots) != 1:
        errors.append("Expected exactly one application boot banner; found %d" % len(boots))
    if not versions:
        errors.append("Missing RBOS version line")
    if profile != "oom":
        for item in PASSES:
            if item not in passed:
                errors.append("Missing PASS: " + item)
        for number in fatal_lines:
            errors.append("Fatal/assert marker at line %d" % number)
        if len(stats) < 2:
            errors.append("Need at least two stats lines")
    else:
        if len(oom_starts) != 1 or len(oom_fatals) != 1:
            errors.append("Need one OOM start followed by one exact pool-exhaustion fatal")
        elif oom_starts[0] >= oom_fatals[0]:
            errors.append("Pool-exhaustion fatal precedes OOM start")
        boundary = oom_fatals[0] if oom_fatals else len(lines) + 1
        if any(number < boundary for number in fatal_lines):
            errors.append("Unexpected fatal/assert before pool-exhaustion fatal")
        stats = [row for row in stats if row["line"] < boundary]

    span = stats[-1]["time"] - stats[0]["time"] if len(stats) >= 2 else 0
    if span < min_duration:
        errors.append("Stats timeline too short: %.3f s < %.3f s" % (span, min_duration))
    for row in stats:
        if row["catchups"]:
            errors.append("Nonzero catchups at line %d" % row["line"])
        if row["tick_min"] > row["tick_max"] or not 0 < row["pool_total"] >= row["pool"]:
            errors.append("Invalid stats range at line %d" % row["line"])
    jitter = {key: {"windows": 0, "duration_s": 0, "tick_us_min": None, "tick_us_max": None}
              for key in ("disconnected", "connected")}
    rates = {key: [] for key in ("idle", "service")}
    transitions = [event for event in events if event["kind"] in jitter]
    excluded = 0
    for previous, row in zip(stats, stats[1:]):
        dt = row["time"] - previous["time"]
        if dt <= 0:
            errors.append("Non-increasing stats timestamp at line %d" % row["line"])
            continue
        if dt > stats_interval * 1.5:
            errors.append("Stats gap %.3f s at line %d" % (dt, row["line"]))
        if abs(row["ticks"] - dt * 1000) > dt * 10:
            errors.append("Ticks outside +/-1%% at line %d" % row["line"])
        for key in rates:
            delta = row[key] - previous[key]
            if delta < 0:
                errors.append("%s counter decreased at line %d" % (key, row["line"]))
            else:
                rates[key].append(delta / dt)
        changes = [event for event in transitions if previous["time"] <= event["time"] <= row["time"]]
        if changes:
            excluded += 1
            continue
        state = "disconnected"
        for event in transitions:
            if event["time"] < previous["time"]:
                state = event["kind"]
        window = jitter[state]
        window["windows"] += 1
        window["duration_s"] += dt
        window["tick_us_min"] = min(row["tick_min"] if window["tick_us_min"] is None else window["tick_us_min"], row["tick_min"])
        window["tick_us_max"] = max(row["tick_max"] if window["tick_us_max"] is None else window["tick_us_max"], row["tick_max"])
    if stats and profile != "oom" and clock is not None and clock - stats[-1]["time"] > stats_interval * 1.5:
        errors.append("Stats stopped before the final timestamp")
    connected = jitter["connected"]["duration_s"]
    if connected < require_connected:
        errors.append("Fully-connected stats coverage too short: %.3f s < %.3f s" % (connected, require_connected))
    ble_duration, connected_at = 0, None
    end = clock or 0
    for event in transitions:
        if event["kind"] == "connected":
            if connected_at is not None:
                errors.append("Duplicate BLE connect at line %d" % event["line"])
            connected_at = event["time"]
        elif connected_at is not None:
            ble_duration += event["time"] - connected_at
            connected_at = None
    if connected_at is not None:
        ble_duration += end - connected_at

    spinner_report = {}
    if profile == "stress":
        warnings.append("Spinner times use preceding timestamps (quantized); time after the final timestamp is unobservable")
        for key in "ab":
            samples = starts[key] + progress[key]
            samples.sort(key=lambda item: item[1])
            if len(starts[key]) != 1 or not progress[key]:
                errors.append("Missing spinner %s start/progress" % key)
            if samples and any(at is None for at, _ in samples):
                errors.append("No timestamp anchor for spinner %s" % key)
            valid = [at for at, _ in samples if at is not None]
            gaps = [b - a for a, b in zip(valid, valid[1:])]
            if valid:
                gaps.append(end - valid[-1])
            if starts[key] and progress[key] and progress[key][0][1] < starts[key][0][1]:
                errors.append("Spinner %s progress precedes start" % key)
            maximum = max(gaps, default=0)
            if maximum > spinner_interval * 2.1:
                errors.append("Spinner %s stalled: estimated gap %.3f s" % (key, maximum))
            spinner_report[key] = {"progress_lines": len(progress[key]), "max_gap_s": maximum}
    peak = {key: max((row[key] for row in stats if row[key] is not None), default=None)
            for key in ("pool", "main", "isr", "drain_us")}
    totals = sorted({row["pool_total"] for row in stats})
    if len(totals) > 1:
        errors.append("Pool capacity changed within the log")
    peak["pool_total"] = totals[0] if len(totals) == 1 else None
    peak["pool_percent"] = peak["pool"] * 100 / totals[0] if len(totals) == 1 and totals[0] else None
    return safe({
        "status": "FAIL" if errors else "PASS", "profile": profile,
        "boot": boots[0] if boots else None, "rbos_version": versions[0] if versions else None,
        "stats_lines": len(stats), "stats_duration_s": span, "stats_interval_s": stats_interval,
        "catchups_max": max((row["catchups"] for row in stats), default=None),
        "ticks_after_first": {"min": min((row["ticks"] for row in stats[1:]), default=None),
                              "max": max((row["ticks"] for row in stats[1:]), default=None)},
        "jitter": jitter, "boundary_windows_excluded": excluded,
        "fully_connected_duration_s": connected, "ble_connected_duration_s": ble_duration,
        "peaks": peak, "rates_per_s": {key: {"min": min(values), "max": max(values)} if values else None
                                            for key, values in rates.items()},
        "spinners": spinner_report, "events": events, "errors": errors, "warnings": warnings,
        "oom": {"start_line": oom_starts[0] if oom_starts else None,
                "fatal_line": oom_fatals[0] if oom_fatals else None},
    })


def human(report):
    boot = report["boot"] or {"version": "missing", "sha": "missing"}
    output = ["%s: %s; app %s / %s; RBOS %s" % (
        report["status"], report["profile"], boot["version"], boot["sha"], report["rbos_version"]),
        "| Item | Result |", "|---|---|",
        "| Stats | %s lines; %s s (first to last) |" % (report["stats_lines"], report["stats_duration_s"])]
    output.append("| Catchups max | %s |" % report["catchups_max"])
    ticks = report["ticks_after_first"]
    if ticks["min"] is not None:
        output.append("| Ticks after first | %s..%s |" % (ticks["min"], ticks["max"]))
    for key, window in report["jitter"].items():
        output.append("| Fully %s tick_us | %s..%s; %s windows / %s s |" % (
            key, window["tick_us_min"], window["tick_us_max"], window["windows"], window["duration_s"]) if window["windows"]
            else "| Fully %s tick_us | unmeasured (0 complete windows) |" % key)
    output.append("| BLE connected | %s s event-to-event; %s boundary windows excluded |" % (
        report["ble_connected_duration_s"], report["boundary_windows_excluded"]))
    peak = report["peaks"]
    output.append("| Pool sampled peak (B) | %s / %s (%s%%) |" % (
        peak["pool"], peak["pool_total"], peak["pool_percent"]) if peak["pool"] is not None
        else "| Pool sampled peak (B) | unmeasured |")
    for key in ("main", "isr", "drain_us"):
        output.append("| %s max | %s |" % (key, peak[key] if peak[key] is not None else "unmeasured"))
    for key, value in report["rates_per_s"].items():
        output.append("| %s / s | %s |" % (key, "%s..%s" % (value["min"], value["max"]) if value else "unavailable"))
    for key, value in report["spinners"].items():
        output.append("| Spinner %s | %s |" % (key, value))
    if report["events"]:
        output += ["", "| BLE event | Uptime (s) | Line |", "|---|---|---|"]
        output += ["| %s | %s | %s |" % (event["kind"], event["time"], event["line"])
                   for event in report["events"]]
    output += ["ERROR: " + item for item in report["errors"]]
    output += ["NOTE: " + item for item in report["warnings"]]
    if report["profile"] != "oom":
        output.append("NOTE: First stats excluded from jitter/rates; BLE boundary windows excluded from jitter.")
    return "\n".join(output)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "Invalid arguments; use --help\n")


def seconds(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("Expected finite nonnegative seconds")
    return result


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("log", type=Path, metavar="LOG")
    parser.add_argument("--profile", choices=("selftest", "stress", "oom"), default="selftest")
    parser.add_argument("--min-duration", type=seconds, default=0, metavar="SECONDS")
    parser.add_argument("--require-connected", type=seconds, default=0, metavar="SECONDS",
                        help="Minimum fully-connected stats-window coverage")
    parser.add_argument("--stats-interval", type=seconds, default=10, metavar="SECONDS",
                        help="Stats interval (Kconfig default: 10 s)")
    parser.add_argument("--spinner-interval", type=seconds, default=10, metavar="SECONDS")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of Markdown")
    args = parser.parse_args(argv)
    if args.stats_interval == 0 or args.spinner_interval == 0:
        parser.error("Intervals must be positive")
    try:
        data = args.log.read_bytes()
    except OSError:
        parser.exit(2, "Cannot read input log\n")
    report = analyze(data, args.profile, args.min_duration, args.stats_interval,
                     args.spinner_interval, args.require_connected)
    print(json.dumps(report, ensure_ascii=True, indent=2) if args.json else human(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
