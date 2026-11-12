#!/usr/bin/env python3
"""P2 の DK 診断 log を検査する。実機未実施を build 成功で代用しない。"""

import importlib.util
import json
import math
from pathlib import Path
import re
import sys

spec = importlib.util.spec_from_file_location("dk_log", Path(__file__).with_name("check-dk-log.py"))
dk_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dk_log)
QUANTITIES = ("temperature_c", "dvdd_v", "avdd_v", "vdd_v")
NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"


def validate_limits(limits):
    if not isinstance(limits, dict) or set(limits) != set(QUANTITIES):
        raise ValueError("Expected exactly four measurement bounds")
    for bounds in limits.values():
        if not isinstance(bounds, list) or len(bounds) != 2 or any(
                type(value) not in (int, float) or not math.isfinite(value) for value in bounds):
            raise ValueError("Expected finite numeric pairs")
        if bounds[0] > bounds[1]:
            raise ValueError("Expected ordered bounds")
    return limits


def latest_boot(data):
    lines = dk_log.ANSI.sub("", data.decode("utf-8", errors="replace")).splitlines()
    start, previous = None, None
    for index, line in enumerate(lines):
        for match in dk_log.BOOT_START.finditer(line):
            kind = match[1]
            if kind == "MCUboot" or previous != "MCUboot":
                start = index, match.start()
            previous = kind
    if start:
        row, column = start
        lines = [lines[row][column:]] + lines[row + 1:]
    return lines


def analyze(data, limits=None, min_samples=3):
    if limits is not None:
        validate_limits(limits)
    lines = latest_boot(data)
    errors = []
    if not any(line.strip() == "PASS: P2 native setup" for line in lines):
        errors.append("Missing P2 native setup")
    probes, resources = {}, []
    buttons = [set() for _ in range(4)]
    samples = {key: [] for key in QUANTITIES}
    for line in lines:
        probe = re.search(r"scheduler_probe payload=(\d+) accepted=(\d+) delivered=(\d+) exhausted=([01]) recovered=([01])", line)
        if probe:
            length, accepted, delivered, exhausted, recovered = map(int, probe.groups())
            if length in probes or length not in (0, 16, 64) or not 0 < accepted <= 64 or delivered != accepted + 1 or not recovered:
                errors.append("Invalid or duplicate scheduler capacity/recovery probe")
            probes[length] = {"accepted": accepted, "exhausted": bool(exhausted)}
        elif "scheduler_probe payload=" in line:
            errors.append("Malformed scheduler probe")
        resource = re.search(r"resources sched_bytes=(\d+) sched_header=(\d+) service_ms=(\d+) sd_ram=(\d+)", line)
        if resource:
            resources.append(tuple(map(int, resource.groups())))
        button = re.fullmatch(r"button index=([0-3]) level=([01]) count=(\d+)", line.strip())
        if button:
            index, level, count = map(int, button.groups())
            if not 0 < count <= 2147483647:
                errors.append("Invalid Button edge count")
            else:
                buttons[index].add(level)
        elif line.strip().startswith("button index="):
            errors.append("Malformed Button event")
        temperature = re.fullmatch(r"temperature c=(" + NUMBER + r")", line.strip())
        if temperature:
            samples["temperature_c"].append(float(temperature[1]))
        elif line.strip().startswith("temperature c="):
            errors.append("Malformed temperature sample")
        adc = re.fullmatch(r"adc rail=(dvdd|avdd|vdd) raw=(-?\d+) volts=(" + NUMBER + r")", line.strip())
        if adc:
            if not -32768 <= int(adc[2]) <= 32767:
                errors.append("Invalid ADC raw range")
            samples[adc[1] + "_v"].append(float(adc[3]))
        elif line.strip().startswith("adc rail="):
            errors.append("Malformed ADC sample")
        if "p2 error=" in line or re.search(r"adc rail=\w+ error=", line) or "Exception(" in line or "RBOS fatal:" in line:
            errors.append("Native diagnostic failure")
    if set(probes) != {0, 16, 64}:
        errors.append("Missing scheduler payload capacity probes")
    if len(resources) != 1 or not (resources[0][0] >= 512 and resources[0][1] > 0 and resources[0][2] > 0 and resources[0][3] > 0):
        errors.append("Missing or invalid SD RAM/BM configuration diagnostics")
    for index, levels in enumerate(buttons):
        if levels != {0, 1}:
            errors.append("Missing physical press/release for Button %d" % index)
    summary = {}
    for key, values in samples.items():
        if len(values) < min_samples or any(not math.isfinite(value) for value in values):
            errors.append("Missing or invalid repeated samples: " + key)
        elif limits and any(value < limits[key][0] or value > limits[key][1] for value in values):
            errors.append("Measurement outside declared bounds: " + key)
        finite = [value for value in values if math.isfinite(value)]
        summary[key] = {"count": len(values), "min": min(finite, default=None), "max": max(finite, default=None)}
    return {
        "status": "FAIL" if errors else "PASS" if limits else "INCOMPLETE",
        "errors": sorted(set(errors)),
        "warnings": [] if limits else ["Measurement bounds not supplied; accuracy not evaluated"],
        "probes": probes, "resources": resources, "samples": summary,
        "scope": "Diagnostic presence, repeatability and supplied bounds only; run the P1 stress checker separately",
    }


def main(argv=None):
    parser = dk_log.Parser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--limits", type=Path, help="Four [minimum,maximum] bounds derived before testing")
    parser.add_argument("--min-samples", type=int, default=3)
    args = parser.parse_args(argv)
    if args.min_samples < 2:
        parser.error("Repeated measurements required")
    try:
        limits = validate_limits(json.loads(args.limits.read_text())) if args.limits else None
        report = analyze(args.log.read_bytes(), limits, args.min_samples)
    except (OSError, ValueError, OverflowError):
        parser.exit(2, "Cannot read log or valid measurement bounds\n")
    print(json.dumps(report, ensure_ascii=True, allow_nan=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
