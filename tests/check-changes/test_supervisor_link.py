import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from bytecode_fixture import make_bytecode_bundle, make_layout_fixture

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('supervisor_link', ROOT / 'tools/bm-build/check-supervisor.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class SupervisorLinkTests(unittest.TestCase):
    def test_real_link_and_no_wrap_control(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = {
                'vm.c': 'int mrbc_vm_run(void) { return 7; }\n',
                'rrt0.c': 'extern int mrbc_vm_run(void); int mrbc_run(void) { return mrbc_vm_run(); }\n',
                'wrap.c': 'extern int __real_mrbc_vm_run(void);\n'
                    'int __wrap_mrbc_vm_run(void) { return __real_mrbc_vm_run(); }\n'
                    '#ifdef CONTROL\nextern int mrbc_vm_run(void);\n'
                    'int __real_mrbc_vm_run(void) { return mrbc_vm_run(); }\n#endif\n',
                'main.c': 'extern int mrbc_run(void); int main(void) { return mrbc_run(); }\n',
            }
            for name, source in files.items():
                (root / name).write_text(source)
            obj = root / 'rrt0.c.obj'
            subprocess.run(['cc', '-O0', '-c', str(root / 'rrt0.c'), '-o', str(obj)], check=True)
            for wrapped in (True, False):
                elf = root / ('wrapped' if wrapped else 'control')
                subprocess.run(['cc', '-O0', *([ '-Wl,--wrap=mrbc_vm_run'] if wrapped else ['-DCONTROL']),
                    str(obj), *(str(root / name) for name in ('vm.c', 'wrap.c', 'main.c')), '-o', str(elf)],
                    check=True)
                if wrapped:
                    report = gate.collect(elf, obj, 'objdump', 'nm')
                    self.assertEqual(gate.verify_route(report), report)
                else:
                    with self.assertRaisesRegex(ValueError, 'does not call __wrap'):
                        gate.collect(elf, obj, 'objdump', 'nm')

    def test_signed_image_and_invalid_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / 'zephyr'
            app.mkdir()
            (app / 'zephyr.map').write_text('fixture\n')
            bundle = root / 'bytecode'
            make_bytecode_bundle(bundle, 'a' * 40)
            make_layout_fixture(bundle, app)
            report = json.loads((root / 'supervisor-link.json').read_text())
            mapping = (app / 'zephyr.map').read_text()
            image = (app / 'zephyr.signed.bin').read_bytes()
            self.assertTrue(gate.verify(report, mapping, image)['rrt0_calls_wrapper'])
            for bad in ({}, dict(report, functions=[]), dict(report, rrt0_vm_relocations=[])):
                with self.assertRaises(ValueError):
                    gate.verify(bad, mapping, image)
            changed = copy.deepcopy(report)
            changed['functions'][0]['sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'differs from signed image'):
                gate.verify(changed, mapping, image)
            with self.assertRaises(ValueError):
                gate.verify(report, mapping, b'')
