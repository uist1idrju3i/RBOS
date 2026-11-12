from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


@unittest.skipUnless(shutil.which("cc"), "Host C compiler required")
class TemperatureTests(unittest.TestCase):
    def compile_and_run(self, headers, program, sources, defines=()):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name, content in headers.items():
                path = base / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            (base / "test.c").write_text(program)
            result = subprocess.run([
                "cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-parameter",
                *defines, "-I", str(base), "-I", str(ROOT / "include"),
                *(str(ROOT / source) for source in sources), str(base / "test.c"),
                "-o", str(base / "test"),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([str(base / "test")], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_s115_context_state_errors_and_output_lifetime(self):
        headers = {
            "cmsis_core.h": """#include <stdint.h>
extern uint32_t ipsr, primask, basepri, faultmask;
static inline uint32_t __get_IPSR(void) { return ipsr; }
static inline uint32_t __get_PRIMASK(void) { return primask; }
static inline uint32_t __get_BASEPRI(void) { return basepri; }
static inline uint32_t __get_FAULTMASK(void) { return faultmask; }
""",
            "nrf_error.h": "#define NRF_SUCCESS 0\n",
            "nrf_sdm.h": "#include <stdint.h>\nuint32_t sd_softdevice_is_enabled(uint8_t *enabled);\n",
            "nrf_soc.h": "#include <stdint.h>\nuint32_t sd_temp_get(int32_t *value);\n",
        }
        program = r"""#include <assert.h>
#include <stdint.h>
#include "rbos/backend.h"
const struct rbos_backend *rbos_nrf_backend(void);
uint32_t ipsr, primask, basepri, faultmask;
static int enabled = 1, state_error, temp_error, queries, readings;
static int32_t sample = -1;
uint32_t sd_softdevice_is_enabled(uint8_t *value) {
  ++queries;
  *value = enabled;
  return state_error;
}
uint32_t sd_temp_get(int32_t *value) {
  ++readings;
  *value = sample;
  return temp_error;
}
int main(void) {
  const struct rbos_backend *backend = rbos_nrf_backend();
  int32_t output = 1234;
  assert(backend == rbos_nrf_backend());
  assert(backend->temperature_read(backend->context, 0) == RBOS_IO_ERROR);
  uint32_t *masks[] = { &ipsr, &primask, &basepri, &faultmask };
  for (unsigned int i = 0; i < 4; ++i) {
    *masks[i] = 1;
    assert(backend->temperature_read(backend->context, &output) == RBOS_IO_ERROR);
    *masks[i] = 0;
  }
  assert(queries == 0 && readings == 0 && output == 1234);
  enabled = 0;
  assert(backend->temperature_read(backend->context, &output) == RBOS_IO_ERROR);
  enabled = 1;
  state_error = 99;
  assert(backend->temperature_read(backend->context, &output) == RBOS_IO_ERROR);
  assert(queries == 2 && readings == 0 && output == 1234);
  state_error = 0;
  temp_error = 99;
  assert(backend->temperature_read(backend->context, &output) == RBOS_IO_ERROR);
  assert(queries == 3 && readings == 1 && output == 1234);
  temp_error = 0;
  const int32_t values[] = { INT32_MIN, -160, -1, 0, 1, 500, INT32_MAX };
  for (unsigned int i = 0; i < sizeof(values)/sizeof(*values); ++i) {
    sample = values[i];
    assert(backend->temperature_read(backend->context, &output) == RBOS_OK);
    assert(output == sample);
  }
  assert(queries == 10 && readings == 8);
}
"""
        self.compile_and_run(headers, program, ["src/platform/nrf/backend.c"],
                             ["-DCONFIG_SOFTDEVICE_S115=1"])

    def test_float_disabled_binding_rejects_before_backend(self):
        headers = {"mrubyc.h": r"""#ifndef FAKE_MRUBYC_H
#define FAKE_MRUBYC_H
#include <stdint.h>
#include <stddef.h>
typedef int32_t mrbc_int_t;
typedef int mrbc_vtype;
enum { MRBC_TT_CLASS, MRBC_TT_INTEGER, MRBC_TT_HASH };
typedef struct { int tt; mrbc_int_t i; } mrbc_value;
typedef struct { const char *error; const char *message; } mrbc_vm;
typedef struct { int unused; } mrbc_class;
typedef void (*callback)(mrbc_vm *, mrbc_value *, int);
#define MRBC_CLASS(name) #name
#define mrbc_type(value) ((value).tt)
#define mrbc_integer(value) ((value).i)
#define MRBC_KW_END() ((mrbc_type(v[argc+1]) == MRBC_TT_HASH && v[argc+1].i) ? \
  (mrbc_raise(vm, "ArgumentError", "unknown keyword"), 0) : 1)
static inline void mrbc_incref(mrbc_value *value) {}
static inline void mrbc_decref(mrbc_value *value) {}
void mrbc_raise(mrbc_vm *vm, const char *error, const char *message);
mrbc_class *mrbc_define_class(mrbc_vm *, const char *, mrbc_class *);
void mrbc_define_method(mrbc_vm *, mrbc_class *, const char *, callback);
#endif
"""}
        program = r"""#include <assert.h>
#include <string.h>
#include "rbos/native.h"
#include "rbos/bindings.h"
static callback read_method, new_method;
void rbos_adc_define(const struct rbos_backend *backend) {}
void rbos_gpio_define(const struct rbos_backend *backend) {}
void rbos_button_define(const struct rbos_backend *backend) {}
static int calls;
static mrbc_class cls;
void mrbc_raise(mrbc_vm *vm, const char *error, const char *message) {
  vm->error = error;
  vm->message = message;
}
mrbc_class *mrbc_define_class(mrbc_vm *vm, const char *name, mrbc_class *parent) {
  assert(strcmp(name, "Temperature") == 0);
  return &cls;
}
void mrbc_define_method(mrbc_vm *vm, mrbc_class *c, const char *name, callback method) {
  assert(c == &cls);
  if (strcmp(name, "read") == 0) read_method = method;
  if (strcmp(name, "new") == 0) new_method = method;
}
static enum rbos_status read_sample(void *context, int32_t *output) {
  ++calls;
  return RBOS_OK;
}
int main(void) {
  static const struct rbos_backend backend = { .temperature_read = read_sample };
  rbos_define_classes(&backend);
  mrbc_vm vm = {0};
  mrbc_value values[2] = { { .tt = MRBC_TT_CLASS }, { .tt = MRBC_TT_INTEGER } };
  read_method(&vm, values, 0);
  assert(strcmp(vm.error, "NotImplementedError") == 0);
  assert(strcmp(vm.message, "Temperature requires Float") == 0);
  read_method(&vm, values, 1);
  assert(strcmp(vm.error, "ArgumentError") == 0);
  values[1].tt = MRBC_TT_HASH;
  values[1].i = 1;
  read_method(&vm, values, 0);
  assert(strcmp(vm.error, "ArgumentError") == 0);
  assert(strcmp(vm.message, "unknown keyword") == 0);
  values[1].i = 0;
  read_method(&vm, values, 0);
  assert(strcmp(vm.error, "NotImplementedError") == 0);
  new_method(&vm, values, 0);
  assert(strcmp(vm.error, "TypeError") == 0);
  assert(calls == 0);
}
"""
        self.compile_and_run(headers, program, ["src/rbos/bindings.c", "src/rbos/native.c"],
                             ["-DMRBC_USE_FLOAT=0"])

    def test_wiring_and_public_signature(self):
        signature = (ROOT / "sig/temperature.rbs").read_text()
        self.assertEqual(signature, "class Temperature\n  def self.read: () -> Float\n"
                                   "  def self.new: (*untyped) -> bot\nend\n")
        cmake = (ROOT / "firmware/CMakeLists.txt").read_text()
        self.assertIn("target_sources(app PRIVATE ../src/platform/nrf/backend.c)", cmake)
        main = (ROOT / "firmware/src/main.c").read_text()
        self.assertLess(main.index("rbos_ble_init()"), main.index("rbos_define_classes(rbos_nrf_backend())"))
        self.assertLess(main.index("mrbc_init("), main.index("rbos_define_classes(rbos_nrf_backend())"))
        shared = (ROOT / "src/rbos/bindings.c").read_text()
        self.assertNotIn("nrf_", shared)
        self.assertNotIn("zephyr", shared)
        self.assertIn("native_helpers temperature ", (ROOT / "tools/mrubyc-wasm/check.sh").read_text())


if __name__ == "__main__":
    unittest.main()
