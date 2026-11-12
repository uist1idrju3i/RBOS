import unittest
import test_temperature


class ResourceProbeTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_exhaustion_payload_copy_recovery_and_bounded_probe(self):
        headers = {
            "mrubyc.h": "typedef struct TCB mrbc_tcb;\n",
            "bm/bm_scheduler.h": """#include <stddef.h>
typedef void (*bm_scheduler_fn_t)(void *, size_t);
int bm_scheduler_defer(bm_scheduler_fn_t, void *, size_t);
int bm_scheduler_process(void);
""",
            "zephyr/logging/log.h": "#define LOG_MODULE_REGISTER(...)\n#define LOG_INF(...)\n",
        }
        program = r'''#include <assert.h>
#include <errno.h>
#include <string.h>
#include <bm/bm_scheduler.h>
int rbos_resources_probe(void);
static struct { bm_scheduler_fn_t fn; unsigned char data[64]; size_t length; } queue[80];
static int used, capacity = 4, fault, processed;
int bm_scheduler_defer(bm_scheduler_fn_t fn, void *data, size_t length) {
  if (fault == 3) return -EFAULT;
  if (used == capacity || (fault == 4 && processed)) return -ENOMEM;
  queue[used].fn = fn;
  queue[used].length = length;
  if (length) memcpy(queue[used].data, data, length);
  if (fault == 1 && length) ++queue[used].data[0];
  ++used;
  return 0;
}
int bm_scheduler_process(void) {
  ++processed;
  for (int i = 0; i < used; ++i)
    if (fault != 2) queue[i].fn(queue[i].data, queue[i].length);
  used = 0;
  return 0;
}
int main(void) {
  assert(rbos_resources_probe() == 0 && used == 0);
  for (fault = 1; fault <= 4; ++fault) {
    processed = 0;
    assert(rbos_resources_probe() == -EIO && used == 0);
  }
  fault = 0;
  capacity = 80;
  assert(rbos_resources_probe() == 0 && used == 0);
}
'''
        self.compile_and_run(headers, program, ["firmware/src/resource_probe.c"],
                             ["-I", str(test_temperature.ROOT / "firmware/src")])
