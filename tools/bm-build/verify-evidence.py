#!/usr/bin/env python3
"""Verify collected BM build evidence; never implies physical-DK acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct

HERE = Path(__file__).resolve().parent
PROFILES = ("debug", "release", "stress", "oom")
IRQS = {213: "saadc_irq", 218: "button_irq20", 268: "button_irq30"}
HEX = r"0x[0-9a-fA-F]+"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def symbol(mapping, name):
    values = re.findall(r"^\s*(" + HEX + r")\s+" + re.escape(name) + r"(?:\s|$)", mapping, re.M)
    require(len(values) == 1, "Missing or ambiguous map symbol: " + name)
    return int(values[0], 16)


def map_sizes(mapping):
    regions = {}
    for name in ("FLASH", "RAM"):
        match = re.search(r"^" + name + r"\s+(" + HEX + r")\s+(" + HEX + r")", mapping, re.M)
        require(match is not None, "Missing memory region: " + name)
        regions[name] = tuple(int(value, 16) for value in match.groups())
    require("Linker script and memory map" in mapping, "Missing output-section map")
    outputs = mapping.split("Linker script and memory map", 1)[1]
    sections = {name: (int(address, 16), int(size, 16)) for name, address, size in re.findall(
        r"^(\S+)(?:[ \t]+|\n[ \t]+)(" + HEX + r")[ \t]+(" + HEX + r")", outputs, re.M)}
    origin, capacity = regions["RAM"]
    ends = [address + size for address, size in sections.values()
            if size and origin <= address < origin + capacity]
    require(bool(ends), "Missing RAM output sections")
    used = {"flash": symbol(mapping, "_flash_used"), "ram": max(ends) - origin}
    require(0 < used["flash"] <= regions["FLASH"][1] and 0 < used["ram"] <= capacity,
            "Output sections exceed memory regions")
    for key, names in {"text": ("text", ".text"), "rodata": ("rodata", ".rodata"),
                       "data": ("datas", ".data"), "bss": ("bss", ".bss"),
                       "noinit": ("noinit", ".noinit")}.items():
        used[key] = next((sections[name][1] for name in names if name in sections), None)
    return used


def image_header(image):
    require(len(image) >= 32, "Truncated image header")
    magic, _, header_size, protected_size, image_size, flags = struct.unpack_from("<IIHHII", image)
    require(magic == 0x96F3B83D, "Wrong MCUboot image magic")
    require(header_size >= 32 and image_size > 0 and
            header_size + image_size + protected_size <= len(image), "Invalid MCUboot image lengths")
    require(flags == 0, "Unexpected encrypted/compressed/non-bootable image flags")
    return struct.unpack_from("<BBHI", image, 20)


def checksums(root):
    require(root.is_dir() and not root.is_symlink(), "Evidence must be a real directory")
    files = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "Symlink in evidence")
        if not path.is_file():
            continue
        require(path.name.lower() != "keyfile.json" and path.suffix.lower() not in
                (".pem", ".key", ".p8", ".p12", ".pfx"), "Forbidden key file in evidence")
        require(not re.search(rb"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----", path.read_bytes()),
                "Private key content in evidence")
        if path.name != "SHA256SUMS" or path.parent != root:
            files.add(path.relative_to(root).as_posix())
    seen = set()
    for line in (root / "SHA256SUMS").read_text().splitlines():
        match = re.fullmatch(r"([a-f0-9]{64}) [ *](.+)", line)
        require(match is not None, "Malformed SHA256SUMS row")
        digest, relative = match.groups()
        path = Path(relative)
        require(not path.is_absolute() and ".." not in path.parts, "Unsafe checksum path")
        name = path.as_posix()
        require(name in files and name not in seen, "Missing/duplicate checksum file: " + name)
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest,
                "Checksum mismatch: " + name)
        seen.add(name)
    require(files == seen, "Unchecksummed files in evidence")
    return len(seen)


def modules(text, manifest=None):
    result = {}
    for row in text.splitlines():
        if not row.strip():
            continue
        fields = row.split()
        require(len(fields) == 3, "Malformed west module row")
        name, path, sha = fields
        if name == "manifest":
            name, sha = "nrf-bm", manifest
        require(name not in result and sha is not None and re.fullmatch(r"[a-f0-9]{40}", sha),
                "Duplicate/invalid module revision")
        result[name] = (path, sha)
    return result


def configuration(text, profile):
    values = {}
    for line in text.splitlines():
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            require(key not in values, "Duplicate configuration")
            values[key] = value
        match = re.fullmatch(r"# (CONFIG_\w+) is not set", line)
        if match:
            require(match[1] not in values, "Duplicate configuration")
            values[match[1]] = "n"
    required = {"CONFIG_SOFTDEVICE_S115": "y", "CONFIG_NRFX_SAADC": "y",
                "CONFIG_NRFX_GPIOTE20": "y", "CONFIG_NRFX_GPIOTE30": "y",
                "CONFIG_NRFX_GPIOTE_NUM_OF_EVT_HANDLERS": "4",
                "CONFIG_LOG_BACKEND_BM_UARTE": "y", "CONFIG_SHELL": "n", "CONFIG_GPIO": "n",
                "CONFIG_BM_ZMS": "n", "CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED": "y",
                "CONFIG_NRFX_RESERVED_RESOURCES_HEADER": '"rbos_reserved_resources.h"',
                "CONFIG_RBOS_PERIPHERAL_EXERCISE": "n" if profile == "oom" else "y"}
    for setting, expected in required.items():
        require(values.get(setting, "n") == expected, "Unexpected configuration: " + setting)
    for key, expected_profile in (("CONFIG_RBOS_TEST_PROFILE_STRESS", "stress"),
                                  ("CONFIG_RBOS_TEST_PROFILE_OOM", "oom"),
                                  ("CONFIG_RBOS_VM_NDEBUG", "release")):
        require(values.get(key, "n") == ("y" if profile == expected_profile else "n"),
                "Wrong profile configuration: " + key)
    require(values.get("CONFIG_SIZE_OPTIMIZATIONS" if profile == "release" else
                       "CONFIG_DEBUG_OPTIMIZATIONS") == "y", "Wrong optimization profile")


def log_sizes(text):
    blocks = re.split(r"Performing build step for ['\"]([^'\"]+)['\"]", text)
    app = [blocks[index + 1] for index in range(1, len(blocks), 2) if blocks[index] == "firmware"]
    require(len(app) == 1, "Missing/ambiguous firmware build-log block")
    sizes = {}
    for name in ("FLASH", "RAM"):
        rows = re.findall(r"^\s*" + name + r":\s+(\d+)\s+(B|KB|MB)\s", app[0], re.M)
        require(len(rows) == 1, "Missing/ambiguous build-log memory row: " + name)
        sizes[name.lower()] = int(rows[0][0]) * {"B": 1, "KB": 1024, "MB": 1024**2}[rows[0][1]]
    return sizes


def verify(root, revision, version, profile, expected_modules, baseline=None, expected_sizes=None):
    count = checksums(root)
    require((root / "rbos-git.txt").read_text().splitlines() == [revision],
            "Source revision mismatch or dirty source tree")
    actual = modules((root / "west-list.txt").read_text(), (root / "manifest-head.txt").read_text().strip())
    require(actual == expected_modules, "Fixed west module paths/revisions mismatch")
    app = root / "firmware/zephyr"
    configuration((app / ".config").read_text(), profile)
    mapping = (app / "zephyr.map").read_text()
    sizes = map_sizes(mapping)
    image = (app / "zephyr.signed.bin").read_bytes()
    require(image_header(image) == version, "Image version mismatch")
    origin = int(re.search(r"^FLASH\s+(" + HEX + r")", mapping, re.M)[1], 16)
    table = symbol(mapping, "_irq_vector_table") - origin
    vectors = {}
    for irq, name in IRQS.items():
        offset = table + irq * 4
        require(0 <= offset <= len(image) - 4, "IRQ vector outside image")
        require(struct.unpack_from("<I", image, offset)[0] == symbol(mapping, name) | 1,
                "IRQ vector mismatch: " + str(irq))
        vectors[str(irq)] = name
    used = log_sizes((root / "build.log").read_text())
    require(all(used[key] == sizes[key] for key in used), "Build-log/map memory mismatch")
    if expected_sizes is not None:
        require(expected_sizes and all(key in sizes and value == sizes[key]
                for key, value in expected_sizes.items()), "Expected memory sizes mismatch")
    delta = None
    if baseline is not None:
        checksums(baseline)
        before = map_sizes((baseline / "firmware/zephyr/zephyr.map").read_text())
        delta = {key: value - before[key] for key, value in sizes.items()
                 if value is not None and before[key] is not None}
    return {"revision": revision, "image_version": list(version), "profile": profile,
            "sha256": hashlib.sha256(image).hexdigest(), "checksummed_files": count,
            "vectors": vectors, "map": sizes, "build_log": used, "map_delta": delta}


def version_tuple(text):
    require(re.fullmatch(r"\d+\.\d+\.\d+\+\d+", text), "Expected version X.Y.Z+TWEAK")
    result = tuple(map(int, re.split(r"[.+]", text)))
    require(all(0 <= value <= 255 for value in result), "Version outside RBOS bounds")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--revision", required=True)
    versions = parser.add_mutually_exclusive_group()
    versions.add_argument("--version")
    versions.add_argument("--version-file", type=Path, default=HERE.parents[1] / "firmware/VERSION")
    parser.add_argument("--profile", choices=PROFILES, help="Omit to require all four profile directories")
    parser.add_argument("--modules", type=Path, default=HERE / "modules.txt")
    parser.add_argument("--baseline", type=Path, help="Verified checksums and map delta, not hardware evidence")
    parser.add_argument("--expected-sizes", type=Path, help="JSON: profile -> memory key -> bytes")
    args = parser.parse_args(argv)
    try:
        require(re.fullmatch(r"[a-f0-9]{40}", args.revision), "Expected a full source SHA")
        if args.version:
            version = version_tuple(args.version)
        else:
            values = dict(re.findall(r"^(VERSION_MAJOR|VERSION_MINOR|PATCHLEVEL|VERSION_TWEAK)\s*=\s*(\d+)\s*$",
                                     args.version_file.read_text(), re.M))
            parts = [values[key] for key in ("VERSION_MAJOR", "VERSION_MINOR", "PATCHLEVEL", "VERSION_TWEAK")]
            version = version_tuple(".".join(parts[:3]) + "+" + parts[3])
        expected_modules = modules(args.modules.read_text())
        expected_sizes = json.loads(args.expected_sizes.read_text()) if args.expected_sizes else {}
        results = {}
        for profile in (args.profile,) if args.profile else PROFILES:
            root = args.evidence if args.profile else args.evidence / ("firmware-evidence-" + profile + "-" + args.revision)
            baseline = args.baseline
            if baseline and not args.profile:
                candidates = list(baseline.glob("firmware-evidence-" + profile + "-*"))
                require(len(candidates) == 1, "Missing/ambiguous baseline profile: " + profile)
                baseline = candidates[0]
            if args.expected_sizes:
                require(profile in expected_sizes, "Missing expected sizes for profile: " + profile)
            results[profile] = verify(root, args.revision, version, profile, expected_modules,
                                      baseline, expected_sizes.get(profile))
        report = {"status": "PASS", "profiles": results,
                  "completion": {"implementation": "NOT_EVALUATED", "host_wasm": "NOT_EVALUATED",
                                 "bm_build": "PASS", "real_hardware": "NOT_RUN"}}
        if "debug" in results:
            debug = results["debug"]["map"]
            report["profile_delta_from_debug"] = {
                profile: {key: value - debug[key] for key, value in result["map"].items()
                          if value is not None and debug[key] is not None}
                for profile, result in results.items()}
    except (OSError, ValueError, KeyError, TypeError, struct.error) as error:
        report = {"status": "FAIL", "error": str(error)}
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
