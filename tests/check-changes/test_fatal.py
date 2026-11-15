import unittest
import test_temperature


class FatalTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_halt_reboot_deadline_and_timer_failure(self):
        headers = {
            'board-config.h': '#define BOARD_PIN_LED_0 71\n#define BOARD_LED_ACTIVE_STATE 0\n',
            'hal/nrf_gpio.h': 'void nrf_gpio_cfg_output(unsigned);\nvoid nrf_gpio_pin_write(unsigned,unsigned);\n',
            'bm/bm_timer.h': '''#include <stddef.h>
struct bm_timer { void (*handler)(void *); };
#define BM_TIMER_MODE_SINGLE_SHOT 1
#define BM_TIMER_MS_TO_TICKS(ms) (ms)
int bm_timer_init(struct bm_timer *,int,void (*)(void *));
int bm_timer_start(struct bm_timer *,unsigned,void *);
''',
            'zephyr/kernel.h': '''#define ARG_UNUSED(x) (void)(x)
#define CODE_UNREACHABLE __builtin_unreachable()
''',
            'zephyr/fatal.h': '''#define K_ERR_KERNEL_PANIC 1
_Noreturn void k_fatal_halt(unsigned);
''',
            'zephyr/logging/log_ctrl.h': 'void test_panic(void);\n#define LOG_PANIC() test_panic()\n',
            'zephyr/sys/printk.h': 'int printk(const char *,...);\n',
            'zephyr/sys/reboot.h': '#define SYS_REBOOT_COLD 0\n_Noreturn void sys_reboot(int);\n',
            'mrubyc.h': 'int mrbc_hal_flush(int);\n_Noreturn void mrbc_hal_abort(const char *);\n',
        }
        program = r'''
#include <assert.h>
#include <setjmp.h>
#include <bm/bm_timer.h>
#include "mrubyc.h"
static jmp_buf target;
static int init_error, start_error, block_log, flushes, panics, stopped, rebooted, halted, armed;
static struct bm_timer *deadline;
static int led_configured, led_on;
void nrf_gpio_cfg_output(unsigned pin) { assert(pin==71); led_configured=1; }
void nrf_gpio_pin_write(unsigned pin,unsigned value) { assert(pin==71 && led_configured && value==0); led_on=1; }
int bm_timer_init(struct bm_timer *timer,int mode,void (*handler)(void *)) {
  assert(mode==1 && led_on); timer->handler=handler; deadline=timer; return init_error;
}
int bm_timer_start(struct bm_timer *timer,unsigned ticks,void *ctx) {
  assert(timer==deadline && ticks==100 && !ctx); armed=1; return start_error;
}
_Noreturn void sys_reboot(int type) { assert(type==0); ++rebooted; longjmp(target,1); }
_Noreturn void k_fatal_halt(unsigned type) { assert(type==1 && stopped); ++halted; longjmp(target,1); }
void rbos_wdt_stop(void) { assert(led_on); ++stopped; }
int mrbc_hal_flush(int fd) { assert(fd==2); assert(CONFIG_RBOS_FATAL_REBOOT ? armed : stopped); ++flushes; return 0; }
int printk(const char *fmt,...) { assert(fmt); return 0; }
void test_panic(void) { ++panics; if (block_log) deadline->handler(NULL); }
int main(void) {
  if (!setjmp(target)) mrbc_hal_abort(NULL);
  assert(flushes==1 && panics==1);
  if (CONFIG_RBOS_FATAL_REBOOT) {
    assert(rebooted==1 && !halted && !stopped);
    block_log=1;
    if (!setjmp(target)) mrbc_hal_abort("blocked log");
    assert(rebooted==2 && panics==2);
    init_error=-1;
    if (!setjmp(target)) mrbc_hal_abort("timer init error");
    assert(rebooted==3 && flushes==2);
    init_error=0; start_error=-1;
    if (!setjmp(target)) mrbc_hal_abort("timer start error");
    assert(rebooted==4 && flushes==2);
  } else {
    assert(halted==1 && stopped==1 && !rebooted && !armed);
  }
}
'''
        for reboot in (0, 1):
            self.compile_and_run(headers, program, ['firmware/src/fatal.c'],
                                 [f'-DCONFIG_RBOS_FATAL_REBOOT={reboot}', '-DCONFIG_RBOS_FATAL_FLUSH_MS=100'])
