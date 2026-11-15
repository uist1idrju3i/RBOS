import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from bytecode_fixture import make_bytecode_bundle, make_layout_fixture


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
            bytecode = make_bytecode_bundle(build / 'firmware/bytecode', 'a' * 40)
            make_layout_fixture(build / 'firmware/bytecode', build / 'firmware/zephyr')
            obj = build / 'firmware/CMakeFiles/app.dir/mrubyc/src/rrt0.c.obj'
            obj.parent.mkdir(parents=True)
            obj.write_bytes(b'rrt0 fixture')
            (build / 'firmware/CMakeCache.txt').write_text(
                f'CMAKE_OBJDUMP:FILEPATH={binaries}/objdump\nCMAKE_NM:FILEPATH={binaries}/nm\n')
            commands = {
                'nm': '0000ae00 00000008 T mrbc_run\n0000ae08 00000008 T __wrap_mrbc_vm_run\n0000ae10 00000008 T mrbc_vm_run\n',
                'objdump': '0000ae00 <mrbc_run>:\n ae00: bl ae08 <__wrap_mrbc_vm_run>\n'
                           '0000ae08 <__wrap_mrbc_vm_run>:\n ae08: bl ae10 <mrbc_vm_run>\n',
            }
            for name, text in commands.items():
                path = binaries / name
                path.write_text('#!/usr/bin/env python3\nimport sys\nprint(' + repr(text) +
                    ' if "-r" not in sys.argv else "00000000 R_ARM_THM_CALL mrbc_vm_run")\n')
                path.chmod(0o755)
            for blob in bytecode['blobs']:
                target = build / 'firmware' / blob['build_output']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((build / 'firmware/bytecode' / blob['generated_c']['path']).read_bytes())
            build_log = base / "build.log"
            build_log.write_text("fixture build memory values\n")
            fake = '#!/usr/bin/env python3\nimport sys\n'
            fake += f'print({str(ROOT)!r} if sys.argv[1:3] == ["list", "manifest"] else "fixture tool")\n'
            for name in ("west", "arm-zephyr-eabi-gcc", "cmake", "ninja", "nrfutil"):
                path = binaries / name
                path.write_text(fake)
                path.chmod(0o755)
            result = subprocess.run([
                "bash", str(ROOT / "tools/bm-build/collect-evidence.sh"),
                str(workspace), str(build), str(output), str(build_log),
            ], text=True, capture_output=True, env=os.environ | {"PATH": str(binaries) + os.pathsep + os.environ["PATH"]})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "firmware/zephyr/zephyr.dts").is_file())
            self.assertTrue((output / "firmware/zephyr/zephyr.map").is_file())
            self.assertTrue((output / 'firmware/bytecode/manifest.json').is_file())
            self.assertTrue((output / 'firmware/bytecode-layout.json').is_file())
            self.assertTrue((output / 'firmware/supervisor-link.json').is_file())
            self.assertFalse((output / 'firmware/zephyr/zephyr.elf').exists())
            self.assertTrue((output / 'firmware/bytecode/generated/rbos_adc_bytecode.c').is_file())
            self.assertTrue((output / 'firmware/bytecode/inputs/src/rbos/adc.rb').is_file())
            self.assertEqual((output / "build.log").read_text(), build_log.read_text())
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
