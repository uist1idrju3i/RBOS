import json
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
notices = runpy.run_path(str(ROOT / "tools/bm-build/third-party-notices.py"))
MEMBERS = ["app/libapp.a(vm.c.obj)", "zephyr/libzephyr.a(kernel.c.obj)",
           "modules/nrf-bm/lib/example.a(sdk.c.obj)", "modules/mcuboot/libboot.a(boot.c.obj)",
           "modules/nrf/security.a(nordic.c.obj)", "modules/hal_nordic/libnrfx.a(nrfx.c.obj)",
           "modules/nrf/subsys/nrf_security/src/core/nrf_oberon/libpsa_core.a(psa.c.obj)",
           "modules/nrf/subsys/nrf_security/src/libmbedcrypto_base.a(mbed.c.obj)",
           "modules/zcbor/libzcbor.a(cbor.c.obj)", "/toolchain/picolibc/libc.a(memcpy.o)",
           "/toolchain/libgcc.a(div.o)"]


def prepare(build, workspace, toolchain):
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / ".git").write_text("gitdir: " + str(ROOT / ".git") + "\n")
    modules = {name: workspace / path for name, path, _ in
               (row.split() for row in (ROOT / "tools/bm-build/modules.txt").read_text().splitlines())}
    for policy in notices["CATALOG"].values():
        if policy["root"] == "mrubyc":
            continue
        for item in policy["files"]:
            license_root, license_path = notices["source_location"](policy, item)
            source = toolchain if license_root == "toolchain" else modules[license_root]
            target = source / license_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text((policy["root"] + "/" + item[0] + " fixture license\n") * 32)
    for directory in notices["IMAGES"]:
        path = build / directory / "zephyr/zephyr.map"
        path.parent.mkdir(parents=True, exist_ok=True)
        text = path.read_text() if path.exists() else "Linker script and memory map\n"
        text += "\n".join(f" .text.fixture 0xa800 0x10 {member}" for member in MEMBERS) + "\n"
        path.write_text(text)
    hex_data = ":0100000042BD\n:00000001FF\n"
    source = modules["nrf-bm"] / notices["S115"]
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(hex_data)
    for name in ("softdevice.signed.hex", "production.hex"):
        (build / name).write_text(hex_data)


def bundle(root):
    workspace, toolchain = root.parent / "sources", root.parent / "toolchain"
    prepare(root, workspace, toolchain)
    notices["collect"](ROOT, workspace, root, root, toolchain)


def inventory(root):
    return json.loads((root / "third-party/inventory.json").read_text())
