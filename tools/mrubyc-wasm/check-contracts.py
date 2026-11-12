#!/usr/bin/env python3
"""Check public API inventory and run positive Wasm suites with mandatory PASS lines."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "research/implementation/api-contracts.json"
FIELDS = ("arguments", "returns", "keywords", "effects", "waiting", "busy", "cancellation", "cleanup", "reuse")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def public_surface(root):
    methods = set()
    for path in (root / "sig").glob("*.rbs"):
        klass = None
        for line in path.read_text().splitlines():
            match = re.fullmatch(r"class (\w+)", line)
            if match:
                klass = match[1]
            match = re.match(r"\s*def (self\.)?([^:]+):", line)
            if match:
                methods.add(klass + ("." if match[1] else "#") + match[2])
            match = re.match(r"\s*alias (\S+) (\S+)", line)
            if match:
                methods.add(klass + "#" + match[1])
    return methods


def validate(inventory, root=ROOT, surface=None):
    require(inventory["schema"] == 1, "Unknown inventory schema")
    cases = {case["id"]: case for case in inventory["cases"]}
    suites = {suite["name"]: suite for suite in inventory["suites"]}
    require(len(cases) == len(inventory["cases"]) and len(suites) == len(inventory["suites"]),
            "Duplicate test case/suite")
    for case in cases.values():
        require(case["scope"] in ("host", "host_wasm"), "Unknown test scope")
        require(case["marker"] and case["marker"] in (root / case["file"]).read_text(),
                "Missing test assertion marker: " + case["id"])
    for suite in suites.values():
        require(suite["required_pass"] and suite["bytecode"], "Suite has no completion criteria")
        source = "\n".join((root / "tests/mruby" / (name + ".rb")).read_text()
                           for name in suite["bytecode"])
        if suite["name"] == "button_lifetime":
            source += (root / "tests/mruby/button_lifetime_worker.rb").read_text()
        if suite["name"] == "peripherals":
            source += (root / "firmware/ruby/peripherals.rb").read_text()
        for marker in suite["required_pass"]:
            require(marker.startswith("PASS: ") and marker in source, "Missing suite PASS: " + marker)
    documented = set()
    for contract in inventory["contracts"]:
        defaults = inventory["defaults"][contract["class"]]
        resolved = defaults | contract
        require(all(isinstance(resolved.get(field), str) and resolved[field].strip() for field in FIELDS),
                "Incomplete API contract: " + str(contract["methods"]))
        for field in ("abnormal", "lifetime"):
            require(defaults[field] and all(case in cases for case in defaults[field]),
                    "Missing abnormal/lifetime tests: " + contract["class"])
        require(defaults["hardware"], "Missing real-DK-only inventory")
        require(contract["suites"] and all(suite in suites for suite in contract["suites"]), "Unknown suite")
        for method in contract["methods"]:
            require(method not in documented, "Duplicate API contract: " + method)
            documented.add(method)
    surface = public_surface(root) if surface is None else surface
    require(documented == surface, "API/RBS inventory mismatch: " + str(sorted(documented ^ surface)))
    public_names = {method.replace(".", "#") for method in surface}
    public_classes = {method.split("#")[0] for method in public_names}
    internal = inventory["internal_classes"]
    require(all(internal.values()) and all(inventory["internal_methods"].values()),
            "Internal classes/methods need a rationale")
    for path in (root / "src/rbos").glob("*.c"):
        source = path.read_text()
        classes = dict(re.findall(r'(\w+)\s*=\s*mrbc_define_class\([^,]+,\s*"(\w+)"', source))
        for klass in classes.values():
            require(klass in public_classes or klass in internal, "Class missing RBS/contract: " + klass)
        for variable, method in re.findall(r'mrbc_define_method\([^,]+,\s*(\w+),\s*"([^"]+)"', source):
            require(variable in classes, "Unresolved binding class: " + variable)
            klass = classes[variable]
            name = klass + "#" + method
            require(klass in internal or name in public_names or name in inventory["internal_methods"],
                    "Binding missing RBS/contract: " + name)
    for path in (root / "src/rbos").glob("*.rb"):
        source = path.read_text()
        klass = re.search(r"^class (\w+)", source, re.M)
        require(klass is not None, "Ruby API wrapper needs an explicit class")
        require(len(re.findall(r"^class (\w+)", source, re.M)) == 1,
                "Use one explicit API class per Ruby wrapper")
        for method in re.findall(r"^\s*(?:def|alias) ([\w!?]+)", source, re.M):
            name = klass[1] + "#" + method
            require(name in public_names or name in inventory["internal_methods"], "Ruby method missing contract: " + name)
    return len(documented)


def check_log(text, required_pass):
    errors = []
    for marker in required_pass:
        if marker not in text.splitlines():
            errors.append("Missing required " + marker)
    if re.search(r"Exception\(|Uncaught task exception|FAIL:|p2 error=|RBOS fatal:|Fatal error:", text):
        errors.append("Unexpected runtime failure")
    return errors


def run_suites(inventory, build):
    results = {}
    for suite in inventory["suites"]:
        log = build / (suite["name"] + "-check.log")
        command = ["node", str(build / "runner.js")] + [str(build / (name + ".mrb")) for name in suite["bytecode"]]
        try:
            result = subprocess.run(command, capture_output=True, text=True, errors="replace", timeout=30)
            output = result.stdout + result.stderr
            errors = check_log(output, suite["required_pass"])
            if result.returncode:
                errors.append("Runner exit " + str(result.returncode))
        except subprocess.TimeoutExpired:
            output, errors = "", ["Wasm suite deadline exceeded"]
        log.write_text(output)
        print(output, end="", file=sys.stderr)
        results[suite["name"]] = {"status": "FAIL" if errors else "PASS", "errors": errors}
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, default=INVENTORY)
    parser.add_argument("--run", type=Path, help="Compiled Wasm runner directory")
    args = parser.parse_args(argv)
    try:
        inventory = json.loads(args.inventory.read_text())
        count = validate(inventory)
        suites = run_suites(inventory, args.run.resolve()) if args.run else {}
        status = "FAIL" if any(suite["status"] != "PASS" for suite in suites.values()) else "PASS"
        report = {"status": status, "api_count": count, "suites": suites,
                  "completion": {"implementation": "PASS", "host_wasm": status if args.run else "NOT_RUN",
                                 "bm_build": "NOT_EVALUATED", "real_hardware": "NOT_RUN"}}
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {"status": "FAIL", "error": str(error)}
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
