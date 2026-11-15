from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class SupervisorTests(unittest.TestCase):
    def test_deadline_initialization_and_reentry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'mrubyc.h').write_text('#include <stdint.h>\ntypedef struct mrbc_vm { int value; } mrbc_vm;\n')
            # Both runtime.h and supervisor.h include the VM header.
            (root / 'mrubyc.h').write_text('#ifndef TEST_VM_H\n#define TEST_VM_H\n' +
                (root / 'mrubyc.h').read_text() + '#endif\n')
            harness = root / 'test.c'
            harness.write_text('''
#include <assert.h>
#include <stdint.h>
#include "supervisor.h"
static int64_t now;
static unsigned calls, idle_calls, depth;
int64_t k_uptime_get(void) { return now; }
int __real_mrbc_vm_run(mrbc_vm *vm) { (void)vm; return 7; }
void rbos_maintenance(bool idle) {
  assert(depth++ == 0);
  ++calls;
  if (idle) ++idle_calls;
  now += 20;
  rbos_supervisor_poll(!idle);
  --depth;
}
int main(void) {
  now = 100;
  assert(__wrap_mrbc_vm_run(0) == 7);
  rbos_supervisor_poll(true);
  assert(calls == 0);
  rbos_supervisor_start();
  rbos_supervisor_poll(false);
  assert(calls == 1 && idle_calls == 0);
  now = 109;
  rbos_supervisor_poll(true);
  assert(calls == 1);
  now = 110;
  rbos_supervisor_poll(true);
  assert(calls == 2 && idle_calls == 1);
  now = 1000000;
  rbos_supervisor_poll(false);
  assert(calls == 3);
  now = 1000009;
  rbos_supervisor_poll(false);
  assert(calls == 3);
  now = INT64_C(4294967296);
  rbos_supervisor_poll(false);
  assert(calls == 4 && depth == 0);
  return 0;
}
''')
            binary = root / 'supervisor'
            result = subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                '-DCONFIG_RBOS_SERVICE_INTERVAL_MS=10', '-I' + str(root),
                '-I' + str(ROOT / 'tools/mrubyc-wasm/supervisor_include'),
                '-I' + str(ROOT / 'firmware/src'), '-I' + str(ROOT / 'include'),
                str(harness), str(ROOT / 'firmware/src/supervisor.c'), '-o', str(binary)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            subprocess.run([str(binary)], check=True, timeout=10)
