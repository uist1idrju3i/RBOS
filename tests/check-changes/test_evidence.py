import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class EvidenceTests(unittest.TestCase):
    def test_resource_files_and_key_exclusion(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            build, workspace, output, binaries = (base / name for name in ("build", "workspace", "out", "bin"))
            for path in (build, workspace, binaries):
                path.mkdir()
            files = {
                "firmware/zephyr/.config": 'CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED=y\n'
                    'CONFIG_NRFX_RESERVED_RESOURCES_HEADER="rbos_reserved_resources.h"\nCONFIG_OTHER=123\n',
                "firmware/zephyr/zephyr.dts": "/dts-v1/;\n",
                "firmware/zephyr/zephyr.map": "fixture map\n",
                "mcuboot/zephyr/.config": "CONFIG_SOFTDEVICE=n\n",
                "zephyr/production.hex": ":00000001FF\n",
                "ignored.txt": "not selected\n",
                "secret.pem": "key fixture\n",
                "keyfile.json": "key fixture\n",
            }
            for name, content in files.items():
                path = build / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            (build / "linked.signed.bin").symlink_to(build / "secret.pem")
            fake = '#!/usr/bin/env python3\nimport sys\n'
            fake += f'print({str(ROOT)!r} if sys.argv[1:3] == ["list", "manifest"] else "fixture tool")\n'
            for name in ("west", "arm-zephyr-eabi-gcc", "cmake", "ninja", "nrfutil"):
                path = binaries / name
                path.write_text(fake)
                path.chmod(0o755)
            result = subprocess.run([
                "bash", str(ROOT / "tools/bm-build/collect-evidence.sh"),
                str(workspace), str(build), str(output),
            ], text=True, capture_output=True, env=os.environ | {"PATH": str(binaries) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "firmware/zephyr/zephyr.dts").is_file())
            self.assertTrue((output / "firmware/zephyr/zephyr.map").is_file())
            for name in ("secret.pem", "keyfile.json", "ignored.txt", "linked.signed.bin"):
                self.assertFalse((output / name).exists(), name)
            report = json.loads((output / "resource-configurations.json").read_text())
            self.assertEqual(report, {
                "firmware/zephyr/.config": {
                    "CONFIG_NRF_SDH_DISPATCH_MODEL_SCHED": "y",
                    "CONFIG_NRFX_RESERVED_RESOURCES_HEADER": '"rbos_reserved_resources.h"',
                },
                "mcuboot/zephyr/.config": {"CONFIG_SOFTDEVICE": "n"},
            })
            hashes = (output / "SHA256SUMS").read_text()
            for relative in ("resource-configurations.json", "firmware/zephyr/zephyr.dts"):
                digest = hashlib.sha256((output / relative).read_bytes()).hexdigest()
                self.assertIn(f"{digest}  ./{relative}\n", hashes)
