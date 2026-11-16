#!/usr/bin/env python3
"""Validate fixture observations; this does not certify hardware acceptance."""
import argparse
import json
from pathlib import Path
import re


PHASES = ("coalesce", "drop", "full")
NUMBER = r"(0|[1-9][0-9]*)"
FIELDS = ("generated", "irq", "accepted", "before_pending", "after_pending",
          "before_overflow", "after_overflow", "before_coalesced", "after_coalesced",
          "initial_level", "final_level")
PHASE = re.compile(r"a7 phase=(coalesce|drop|full)" + "".join(
    rf" {name}={NUMBER}" for name in FIELDS))
DELIVERY = re.compile(r"a7 delivery phase=(coalesce|drop|full) via=(ruby|none)"
                      rf" level={NUMBER} count={NUMBER} pending={NUMBER}")
RETENTION = re.compile(r"p5 mode=(seed|verify) nonce=([0-9a-f]{8}) sentinel=([0-9a-f]{8})"
                       r" peer_before=([0-9a-f]{8}) peer_after=([0-9a-f]{8}) verified=1 writes=(0|1)")


def records(data, prefix):
    lines = re.sub(r"\x1b\[[0-9;]*m", "", data.decode("utf-8", errors="replace")).splitlines()
    result = []
    for line in lines:
        if re.search(r"\b(?:FAIL:|RBOS fatal:|Exception\(|ASSERTION FAIL|ZEPHYR FATAL ERROR)", line):
            raise ValueError("fatal diagnostic")
        match = re.search(rf"\b{prefix}(?:\s|$)", line)
        if match:
            result.append(line[match.start():].strip())
    return result


def saturation(data):
    lines = records(data, "a7")
    if len(lines) != 8 or lines[0] != "a7 setup pin=43 timer=21 path=port capacity=16" or lines[-1] != "a7 done phases=3":
        raise ValueError("missing, duplicate or malformed setup/phase/done records")
    overflow = coalesced = 0
    previous_level = 0
    for index, name in enumerate(PHASES):
        match = PHASE.fullmatch(lines[1 + 2 * index])
        delivery = DELIVERY.fullmatch(lines[2 + 2 * index])
        if not match or match[1] != name or not delivery or delivery[1] != name:
            raise ValueError("missing, duplicate, out-of-order or malformed phase/delivery")
        values = dict(zip(FIELDS, map(int, match.groups()[1:])))
        if any(value > 0xffffffff for value in values.values()):
            raise ValueError("counter out of range")
        expected = dict(zip(FIELDS, (5, 5, 0 if name == "drop" else 5,
            0 if name == "coalesce" else 16, 1 if name == "coalesce" else 16,
            overflow, overflow + (5 if name == "drop" else 0),
            coalesced, coalesced + (0 if name == "drop" else 4), previous_level, previous_level ^ 1)))
        if values != expected:
            raise ValueError(f"{name}: generation/IRQ/queue/level mismatch")
        if delivery.groups()[1:] != ("none" if name == "drop" else "ruby",
                str(expected["final_level"]), "0" if name == "drop" else "5", "0"):
            raise ValueError(f"{name}: delivery mismatch")
        overflow = expected["after_overflow"]
        coalesced = expected["after_coalesced"]
        previous_level ^= 1
    return {"status": "PASS", "scope": "fixture log only; not product IN/hardware acceptance", "phases": 3}


def retention(seed, verify):
    observations = []
    for mode, data in (("seed", seed), ("verify", verify)):
        lines = records(data, "p5")
        match = RETENTION.fullmatch(lines[0]) if len(lines) == 1 else None
        if not match or match[1] != mode or match[2] == "00000000" or match[4] != match[5] or match[6] != ("1" if mode == "seed" else "0"):
            raise ValueError(f"{mode}: missing, duplicate, malformed or mismatched retention record")
        observations.append(match.groups()[1:5])
    if observations[0] != observations[1]:
        raise ValueError("image A/B nonce, sentinel or peer digest mismatch")
    return {"status": "PASS", "scope": "storage0 sentinel and peer CRC32 only; not bonding/settings"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("saturation", "retention"))
    parser.add_argument("logs", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        if len(args.logs) != (1 if args.mode == "saturation" else 2):
            raise ValueError("saturation needs one log; retention needs image A and B logs")
        data = [path.read_bytes() for path in args.logs]
        result = saturation(*data) if args.mode == "saturation" else retention(*data)
    except (ValueError, OSError) as error:
        result = {"status": "FAIL", "error": str(error)}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
