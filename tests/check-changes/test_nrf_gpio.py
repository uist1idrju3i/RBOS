import unittest
import test_temperature


class NRFGPIOTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_dt_labels_physical_levels_modes_and_console_protection(self):
        headers = {
            "mrubyc.h": "#include <stdint.h>\ntypedef struct VM mrbc_vm;\ntypedef struct V mrbc_value;\ntypedef int mrbc_vtype;\ntypedef int32_t mrbc_int_t;\n",
            "board-config.h": """#ifndef BOARD_CONSOLE_UARTE_PIN_TX
#define BOARD_CONSOLE_UARTE_PIN_TX 36
#endif
#define BOARD_CONSOLE_UARTE_PIN_CTS 39
""",
            "zephyr/kernel.h": """#define ARRAY_SIZE(a) (sizeof(a)/sizeof(*(a)))
#define IS_ENABLED(x) (x)
#define CONFIG_GPIO 0
#define CONFIG_LOG_BACKEND_BM_UARTE 1
#define CONFIG_LOG_BACKEND_BM_UARTE_USE_HWFC 1
#define BUILD_ASSERT(c,m) _Static_assert(c,m)
#define STRINGIFY_(x) #x
#define STRINGIFY(x) STRINGIFY_(x)
""",
            "zephyr/devicetree.h": """#define DT_NODELABEL(n) n
#define DT_ALIAS(n) n
#define DT_PROP_(n,p) DT_##n##_##p
#define DT_PROP(n,p) DT_PROP_(n,p)
#define DT_rbos_gpio_pins_port_pin_counts {7,16,11}
#define DT_led0_pin 73
#define DT_led1_pin 42
#define DT_led2_pin 71
#define DT_led3_pin 46
#define DT_button0_pin 45
#define DT_button1_pin 41
#define DT_button2_pin 40
#define DT_button3_pin 4
#define DT_sw0_pin 45
#define DT_sw1_pin 41
#define DT_sw2_pin 40
#define DT_sw3_pin 4
#define DT_FOREACH_CHILD_STATUS_OKAY(n,F) F(led0) F(led1) F(led2) F(led3) F(button0) F(button1) F(button2) F(button3)
#define DT_FOREACH_NODELABEL_VARGS(n,F,arg) F(n,arg)
""",
            "hal/nrf_gpio.h": """#include <stdbool.h>
#include <stdint.h>
typedef int nrf_gpio_pin_pull_t;
enum { NRF_GPIO_PIN_PULLUP=8, NRF_GPIO_PIN_PULLDOWN=16, NRF_GPIO_PIN_NOPULL=0,
NRF_GPIO_PIN_DIR_OUTPUT=2, NRF_GPIO_PIN_DIR_INPUT=1, NRF_GPIO_PIN_INPUT_DISCONNECT=4,
NRF_GPIO_PIN_INPUT_CONNECT=0, NRF_GPIO_PIN_S0D1=32, NRF_GPIO_PIN_S0S1=0, NRF_GPIO_PIN_NOSENSE=0 };
bool nrf_gpio_pin_present_check(uint32_t);
void nrf_gpio_pin_clear(uint32_t);
void nrf_gpio_cfg(uint32_t, int, int, int, int, int);
uint32_t nrf_gpio_pin_read(uint32_t);
void nrf_gpio_pin_write(uint32_t,uint32_t);
""",
        }
        program = r'''#include <assert.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>
#include "rbos/gpio.h"
#include "gpio.h"
static uint32_t level[96];
static int direction, input, pull, drive;
static bool claimed;
bool rbos_nrf_button_owns(uint32_t pin) { return claimed && pin == 42; }
bool nrf_gpio_pin_present_check(uint32_t pin) { return pin < 96; }
void nrf_gpio_pin_clear(uint32_t pin) { level[pin] = 0; }
uint32_t nrf_gpio_pin_read(uint32_t pin) { return level[pin]; }
void nrf_gpio_pin_write(uint32_t pin, uint32_t value) { level[pin] = value; }
void nrf_gpio_cfg(uint32_t pin, int d, int i, int p, int dr, int s) {
  (void)pin; (void)s; direction=d; input=i; pull=p; drive=dr;
}
int main(void) {
  uint32_t pin, value;
  assert(rbos_nrf_pin_lookup(0,"led0",&pin)==RBOS_OK && pin==73);
  assert(rbos_nrf_pin_lookup(0,"sw0",&pin)==RBOS_OK && pin==45);
  assert(rbos_nrf_pin_lookup(0,"button0",&pin)==RBOS_OK && pin==45);
  assert(rbos_nrf_pin_lookup(0,"unknown",&pin)==RBOS_INVALID_PIN);
  assert(rbos_nrf_pin_validate(0,96)==RBOS_INVALID_PIN);
  assert(rbos_nrf_pin_validate(0,48)==RBOS_INVALID_PIN);
  assert(rbos_nrf_pin_validate(0,1)==RBOS_RESERVED_PIN);
  assert(rbos_nrf_pin_validate(0,BOARD_CONSOLE_UARTE_PIN_TX)==RBOS_RESERVED_PIN);
  assert(rbos_nrf_pin_validate(0,BOARD_CONSOLE_UARTE_PIN_CTS)==RBOS_RESERVED_PIN);
  assert(rbos_nrf_gpio_configure(0,42,RBOS_GPIO_OUT|RBOS_GPIO_OPEN_DRAIN|RBOS_GPIO_PULL_UP)==RBOS_OK);
  assert(direction==2 && input==0 && drive==32 && pull==8);
  assert(rbos_nrf_gpio_write(0,42,1)==RBOS_OK);
  assert(rbos_nrf_gpio_read(0,42,&value)==RBOS_OK && value==1);
  assert(rbos_nrf_gpio_write(0,42,2)==RBOS_IO_ERROR);
  assert(rbos_nrf_gpio_configure(0,42,RBOS_GPIO_HIGH_Z)==RBOS_OK && direction==1 && input==4 && pull==0);
  assert(rbos_nrf_gpio_configure(0,42,RBOS_GPIO_IN|RBOS_GPIO_PULL_DOWN)==RBOS_OK && input==0 && pull==16);
  assert(rbos_nrf_gpio_configure(0,42,RBOS_GPIO_IN|RBOS_GPIO_OUT)==RBOS_IO_ERROR);
  claimed=true;
  assert(rbos_nrf_gpio_configure(0,42,RBOS_GPIO_OUT)==RBOS_BUSY);
  assert(rbos_nrf_gpio_write(0,42,1)==RBOS_BUSY);
  assert(rbos_nrf_gpio_read(0,42,&value)==RBOS_OK);
  level[45]=0;
  assert(rbos_nrf_gpio_read(0,45,&value)==RBOS_OK && value==0);
}
'''
        sources = ["src/platform/nrf/gpio.c", "src/rbos/gpio.c"]
        flags = ["-I", str(test_temperature.ROOT / "src/platform/nrf")]
        self.compile_and_run(headers, program, sources, flags)
        self.compile_and_run(headers, program, sources, flags + ["-DBOARD_CONSOLE_UARTE_PIN_TX=73"])
