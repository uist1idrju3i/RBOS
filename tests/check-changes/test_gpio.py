import unittest
import test_temperature


class GPIOTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_pin_grammar_overflow_and_mode_combinations(self):
        headers = {"mrubyc.h": """#include <stdint.h>
typedef struct VM mrbc_vm;
typedef struct Value mrbc_value;
typedef int mrbc_vtype;
typedef int32_t mrbc_int_t;
"""}
        program = r'''#include <assert.h>
#include <string.h>
#include "rbos/gpio.h"
int main(void) {
  uint32_t pin = 123, mode = 123;
  assert(rbos_pin_parse("P1.13", 5, &pin) && pin == 45);
  assert(rbos_pin_parse("P2.09", 5, &pin) && pin == 73);
  assert(rbos_pin_parse("P134217727.31", 13, &pin) && pin == UINT32_MAX);
  const char *bad[] = { "", "P", "P1.", "P1.32", "P-1.0", "P1.-1", "P1.000",
    "P1.13 ", " P1.13", "p1.13", "P134217728.0", "P9999999999999.0", "P1x.13" };
  for (unsigned int i = 0; i < sizeof(bad)/sizeof(*bad); ++i) {
    pin = 123;
    assert(!rbos_pin_parse(bad[i], strlen(bad[i]), &pin) && pin == 123);
  }
  assert(!rbos_pin_parse("P1.13\0", 6, &pin));
  assert(!rbos_pin_parse(NULL, 4, &pin));
  assert(!rbos_pin_parse("P1.13", 5, NULL));
  for (uint32_t request = 0; request < 128; ++request) {
    uint32_t base = request & 7;
    bool valid = base && !(base & (base - 1)) && !(request & ~63u) &&
      (request & 24) != 24 && (!(request & 4) || request == 4) &&
      (!(request & 32) || base == 2);
    mode = 123;
    assert(rbos_gpio_mode(0, request, &mode) == valid);
    assert(mode == (valid ? request : 123));
  }
  assert(rbos_gpio_mode(1 | 8, 16, &mode) && mode == (1 | 16));
  assert(rbos_gpio_mode(2 | 32 | 8, 16, &mode) && mode == (2 | 32 | 16));
  assert(rbos_gpio_mode(2 | 8, 32, &mode) && mode == (2 | 8 | 32));
  assert(rbos_gpio_mode(1 | 8, 1, &mode) && mode == 1);
  assert(!rbos_gpio_mode(1, 32, &mode));
  assert(!rbos_gpio_mode(1, 1, NULL));
}
'''
        self.compile_and_run(headers, program, ["src/rbos/gpio.c"])

    def test_generation_aware_ring(self):
        self.compile_and_run({}, "", ["src/rbos/event_queue.c", "tools/mrubyc-wasm/test_event_queue.c"])
