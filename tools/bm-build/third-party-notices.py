#!/usr/bin/env python3
"""Collect image notices from linked inputs; not a file-level legal audit."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
CATALOG = json.loads((HERE / "third-party-components.json").read_text())["components"]
IMAGES = {"firmware": "app", "firmware_loader": "loader", "mcuboot": "MCUboot", "installer": "installer"}
DISTRIBUTIONS = {"app-update": ["app", "loader"],
                 "initial-installation": list(IMAGES.values()) + ["S115"]}
S115 = "components/softdevice/nrf54l/s115/s115_nrf54l15_10.0.1_softdevice.hex"
ARCHIVE = r"[^\s()]+\.a\([^()]+\)"
HEADER = """THIRD_PARTY_NOTICES

app update and initial installation images: see third-party/inventory.json.
Mbed TLS and Mbed TLS-derived Oberon files: Apache-2.0 is selected, not GPL.
This selection does not relicense Nordic-5-Clause Oberon files.
Inventory is based on map contributions and LTO link inputs, not a complete
file-level license audit. Final compliance for every object is unverified.
Host mrbc, emsdk and build tools are not redistributed in these images.
"""


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def linked(mapping):
    require("Linker script and memory map" in mapping, "Missing linker output map")
    output = mapping.split("Linker script and memory map", 1)[1]
    members = set()
    section = ""
    for line in output.splitlines():
        if line and not line[0].isspace():
            section = line.split()[0]
        if section.startswith((".debug", ".zdebug", ".comment", ".ARM.attributes", ".gnu.attributes", ".gnu_debug")):
            continue
        for size, member in re.findall(r"0x[0-9a-fA-F]+\s+(0x[0-9a-fA-F]+)\s+(" + ARCHIVE + r")", line):
            if int(size, 16):
                members.add(member)
    # LTO merges input sections: preserve the map's selected plugin inputs too.
    if ".ltrans" in output:
        inputs = mapping.split("Discarded input sections", 1)[0]
        members.update(re.findall(r"(" + ARCHIVE + r")(?:\s*\n)?[^\n]*symbol from plugin", inputs))
    require(members, "No linked archive contributions")
    return sorted(members)


def classify(member, image, mrubyc_objects):
    if member.startswith("app/libapp.a("):
        if image == "MCUboot":
            return "mcuboot"
        if image in ("loader", "installer"):
            return "sdk-nrf-bm"
        return "mrubyc" if member.split("(")[1][:-1] in mrubyc_objects else None
    if member.startswith("zephyr/"):
        return "zephyr"
    for prefix, component in (("modules/hal_nordic/", "nrfx"), ("modules/mcuboot/", "mcuboot"),
                              ("modules/nrf-bm/", "sdk-nrf-bm"), ("modules/zcbor/", "zcbor")):
        if member.startswith(prefix):
            return component
    if member.startswith("modules/nrf/"):
        if "/core/nrf_oberon/" in member:
            return "oberon-psa"
        if "libmbedcrypto_base.a" in member:
            return "mbedtls"
        return "sdk-nrf"
    if member.split("(")[0].endswith("/libgcc.a"):
        return "libgcc"
    if "/picolibc/" in member and "/libc.a(" in member:
        return "picolibc"
    raise ValueError("Unclassified linked archive: " + member)


def selections(root, mrubyc_objects):
    selected = {}
    for directory, image in IMAGES.items():
        mapping = root / directory / "zephyr/zephyr.map"
        for member in linked(mapping.read_text()):
            component = classify(member, image, mrubyc_objects)
            if component:
                selected.setdefault(component, {}).setdefault(image, []).append(member)
    require("mrubyc" in selected, "Missing linked mruby/c")
    selected["s115"] = {"S115": [S115]}
    return selected


def render(inventory, root):
    text = HEADER
    for component in inventory["components"]:
        text += "\n== " + component["id"] + " / " + component["license"] + " ==\n"
        text += "Images: " + ", ".join(component["applies_to"]) + "\n"
        for source in component["sources"]:
            text += "\n--- " + source["root"] + "/" + source["path"] + " ---\n"
            text += (root / source["copy"]).read_text() + "\n"
    return text


def source_location(component, item):
    return item[0].split(":", 1) if ":" in item[0] else (component["root"], item[0])


def hex_memory(path):
    memory, base = {}, 0
    for line in path.read_text().splitlines():
        require(line.startswith(":"), "Invalid Intel HEX")
        row = bytes.fromhex(line[1:])
        require(len(row) == row[0] + 5 and sum(row) % 256 == 0, "Invalid HEX checksum/length")
        address, kind, data = int.from_bytes(row[1:3], "big"), row[3], row[4:-1]
        if kind == 0:
            for offset, value in enumerate(data):
                key = base + address + offset
                require(key not in memory or memory[key] == value, "Conflicting HEX data")
                memory[key] = value
        elif kind in (2, 4):
            require(len(data) == 2, "Invalid HEX address record")
            base = int.from_bytes(data, "big") << (4 if kind == 2 else 16)
        else:
            require(kind in (1, 3, 5), "Unsupported HEX record")
    require(memory, "Empty HEX image")
    return memory


def hex_regions(path):
    memory = hex_memory(path)
    groups = []
    for address in sorted(memory):
        if not groups or address != groups[-1][-1] + 1:
            groups.append([])
        groups[-1].append(address)
    return [{"start": group[0], "size": len(group),
             "sha256": digest(bytes(memory[a] for a in group))} for group in groups]


def verify_s115(component, root):
    require(component["hex_path"] == S115 and component["regions"], "Missing S115 input")
    for filename in ("softdevice.signed.hex", "production.hex"):
        memory = hex_memory(root / filename)
        for region in component["regions"]:
            data = bytes(memory[a] for a in range(region["start"], region["start"] + region["size"]))
            require(digest(data) == region["sha256"], "S115 payload mismatch: " + filename)


def collect(repo, workspace, build, out, toolchain):
    modules = {}
    for row in (HERE / "modules.txt").read_text().splitlines():
        name, path, _ = row.split()
        modules[name] = workspace / path
    roots = modules | {"mrubyc": repo / "vendor/mrubyc", "toolchain": toolchain}
    objects = sorted(path.name + ".obj" for path in (roots["mrubyc"] / "src").glob("*.c"))
    require(objects, "Missing mruby/c sources")
    selected = selections(build, objects)
    target = out / "third-party"
    target.mkdir()
    inventory = {"schema": 1, "audit": "unverified", "mrubyc_objects": objects,
                 "distributions": DISTRIBUTIONS,
                 "maps": {}, "components": []}
    for directory in IMAGES:
        path = directory + "/zephyr/zephyr.map"
        inventory["maps"][path] = digest((build / path).read_bytes())
    for name, evidence in sorted(selected.items()):
        policy = CATALOG[name]
        source_root = roots[policy["root"]]
        revision = (subprocess.check_output(["git", "-C", str(source_root), "rev-parse", "HEAD"], text=True).strip()
                    if policy["root"] != "toolchain" else "bundle-911f4c5c26")
        component = {"id": name, "license": policy["license"], "root": policy["root"],
                     "revision": revision, "applies_to": sorted(evidence), "map_evidence": evidence, "sources": []}
        if name == "s115":
            component["hex_sha256"] = digest((source_root / S115).read_bytes())
            component["hex_path"] = S115
            component["regions"] = hex_regions(source_root / S115)
            verify_s115(component, build)
        for index, item in enumerate(policy["files"]):
            license_root, license_path = source_location(policy, item)
            data = (roots[license_root] / license_path).read_bytes()
            content = b"".join(data.splitlines(keepends=True)[item[1] - 1:item[2]]) if len(item) == 3 else data
            require(content.strip(), "Empty license: " + item[0])
            relative = f"third-party/licenses/{name}/{index}.txt"
            destination = out / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
            component["sources"].append({"root": license_root, "path": license_path, "sha256": digest(data), "lines": item[1:],
                                         "copy": relative, "copy_sha256": digest(content)})
        inventory["components"].append(component)
    (target / "inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (out / "THIRD_PARTY_NOTICES").write_text(render(inventory, out))


def verify(root):
    inventory = json.loads((root / "third-party/inventory.json").read_text())
    require(inventory["schema"] == 1 and inventory["audit"] == "unverified", "Invalid notice inventory")
    require(inventory["distributions"] == DISTRIBUTIONS, "Wrong notice distribution scope")
    expected = selections(root, inventory["mrubyc_objects"])
    components = inventory["components"]
    require([c["id"] for c in components] == sorted(expected), "Missing/duplicate notice component")
    require(set(inventory["maps"]) == {d + "/zephyr/zephyr.map" for d in IMAGES}, "Missing notice maps")
    for path, sha in inventory["maps"].items():
        require(digest((root / path).read_bytes()) == sha, "Notice map hash mismatch")
    for component in components:
        name = component["id"]
        policy = CATALOG[name]
        require(re.fullmatch(r"[a-f0-9]{40}|bundle-911f4c5c26", component["revision"]), "Invalid source revision")
        require(component["license"] == policy["license"] and component["root"] == policy["root"], "Wrong notice license")
        require(component["map_evidence"] == expected[name] and component["applies_to"] == sorted(expected[name]),
                "Notice applicability mismatch")
        if name == "s115":
            verify_s115(component, root)
        sources = component["sources"]
        require(len(sources) == len(policy["files"]), "Missing required license/NOTICE: " + name)
        for index, (source, item) in enumerate(zip(sources, policy["files"])):
            license_root, license_path = source_location(policy, item)
            require(source["root"] == license_root and source["path"] == license_path and source["lines"] == item[1:] and
                    source["copy"] == f"third-party/licenses/{name}/{index}.txt", "Wrong license source")
            data = (root / source["copy"]).read_bytes()
            require(data.strip() and digest(data) == source["copy_sha256"], "Missing/changed license: " + name)
            require(re.fullmatch(r"[a-f0-9]{64}", source["sha256"]), "Invalid license SHA")
            if not source["lines"]:
                require(source["sha256"] == source["copy_sha256"], "License source hash mismatch")
    require((root / "THIRD_PARTY_NOTICES").read_text() == render(inventory, root), "Notice text mismatch")
    return {"components": len(components), "audit": "unverified"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("build", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("compiler", type=Path)
    args = parser.parse_args()
    toolchain = next(parent for parent in args.compiler.resolve().parents
                     if (parent / "arm-zephyr-eabi/share/licenses/gcc/COPYING.RUNTIME").is_file())
    collect(args.repo, args.workspace, args.build, args.out, toolchain)
    verify(args.out)
    print("Third-party notices: PASS (file-level legal audit unverified)")


if __name__ == "__main__":
    main()
