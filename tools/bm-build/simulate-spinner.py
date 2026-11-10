"""Idealized timer-path model, not a VM run or hardware evidence.

Model rrt0.c's strict wake deadline (mrbc_tick, mrbc_sleep_ms), fresh
dispatch budget (mrbc_run), and equal-priority tail insertion. Assume
1 ms ticks, immediate preemption at tick boundaries, two equally fast
always-ready spinners, and zero-time priority-0 service followed by sleep.
Exclude instruction cost, IRQ latency, BLE work, and counter logging.
"""

import argparse


def simulate(quantum, service_ms, ticks, first="a"):
    if not 1 <= quantum <= 255:
        raise ValueError("quantum must be in 1..255")
    if service_ms is not None and not 1 <= service_ms <= 1000:
        raise ValueError("service_ms must be in 1..1000 or None")
    if ticks < 0:
        raise ValueError("ticks must be nonnegative")
    if first not in ("a", "b"):
        raise ValueError("first must be a or b")

    ready = [first, "b" if first == "a" else "a"]
    counts = {"a": 0, "b": 0}
    remaining = 0
    deadline = service_ms
    services = 0
    for tick in range(1, ticks + 1):
        if remaining == 0:
            remaining = quantum
        counts[ready[0]] += 1
        remaining -= 1
        wake = deadline is not None and deadline < tick
        if remaining == 0 or wake:
            ready.append(ready.pop(0))
            remaining = 0
        if wake:
            services += 1
            deadline = tick + service_ms

    low, high = sorted(counts.values())
    return {
        "a_ticks": counts["a"],
        "b_ticks": counts["b"],
        "service_calls": services,
        "a_b_ratio": counts["a"] / counts["b"] if counts["b"] else None,
        "max_min_ratio": high / low if low else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=110000)
    args = parser.parse_args()
    if args.ticks < 0:
        parser.error("ticks must be nonnegative")
    print("MODEL ONLY: zero service cost; 1 ms ticks; not hardware evidence")
    for first in ("a", "b"):
        for name, quantum, service in (("current", 10, 10), ("X", 1, 10), ("Y", 10, 9)):
            result = simulate(quantum, service, args.ticks, first)
            print(f"{name} first={first} quantum={quantum} sleep_ms={service}: {result}")


if __name__ == "__main__":
    main()
