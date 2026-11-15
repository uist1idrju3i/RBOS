import copy
import hashlib
from pathlib import Path
import runpy
import unittest
import test_temperature

ROOT = Path(__file__).resolve().parents[2]


class WatchdogTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_board_backend_start_feed_stop_and_reset_reason(self):
        headers = {
            'nrfx_wdt.h': '''#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#define NRFX_WDT_HAS_STOP 1
#define NRF_WDT_BEHAVIOUR_STOP_ENABLE_MASK 2
#define NRF_WDT30 ((void *)30)
typedef struct { void *p_reg; } nrfx_wdt_t;
typedef int nrfx_wdt_channel_id;
typedef struct { unsigned behaviour, reload_value; } nrfx_wdt_config_t;
#define NRFX_WDT_DEFAULT_CONFIG {1,2000}
#define NRFX_WDT_INSTANCE(reg) {reg}
#define BUILD_ASSERT(c,m) _Static_assert(c,m)
bool nrf_wdt_started_check(void *);
int nrfx_wdt_init(nrfx_wdt_t *,const nrfx_wdt_config_t *,void *,void *);
int nrfx_wdt_channel_alloc(nrfx_wdt_t *,int *);
void nrfx_wdt_enable(nrfx_wdt_t *);
void nrfx_wdt_channel_feed(const nrfx_wdt_t *,int);
int nrfx_wdt_stop(nrfx_wdt_t *);
''',
            'hal/nrf_reset.h': '''#include <stdint.h>
#define NRF_RESET ((void *)42)
uint32_t nrf_reset_resetreas_get(void *);
void nrf_reset_resetreas_clear(void *,uint32_t);
''',
            'zephyr/logging/log.h': '''extern int logged;
#define LOG_MODULE_REGISTER(...)
#define LOG_INF(fmt,value) do { (void)(value); logged=1; } while(0)
''',
        }
        program = r'''
#include <assert.h>
#include <errno.h>
#include <nrfx_wdt.h>
#include "rbos/watchdog.h"
int logged;
static bool running;
static int init_error, alloc_error, enabled, feeds, stopped;
bool nrf_wdt_started_check(void *p) { assert(p==(void *)30); return running; }
int nrfx_wdt_init(nrfx_wdt_t *p,const nrfx_wdt_config_t *c,void *handler,void *ctx) {
  assert(p->p_reg==(void *)30 && !handler && !ctx);
  assert(c->reload_value==2000);
  assert(c->behaviour==(CONFIG_RBOS_FATAL_REBOOT ? 1u : 3u));
  return init_error;
}
int nrfx_wdt_channel_alloc(nrfx_wdt_t *p,int *channel) { (void)p; *channel=3; return alloc_error; }
void nrfx_wdt_enable(nrfx_wdt_t *p) { (void)p; ++enabled; }
void nrfx_wdt_channel_feed(const nrfx_wdt_t *p,int channel) { (void)p; assert(channel==3); ++feeds; }
int nrfx_wdt_stop(nrfx_wdt_t *p) { (void)p; ++stopped; return 0; }
uint32_t nrf_reset_resetreas_get(void *p) { assert(p==(void *)42); return 0x123; }
void nrf_reset_resetreas_clear(void *p,uint32_t bits) { assert(p==(void *)42 && logged && bits==0x123); }
int main(void) {
  rbos_wdt_feed(); rbos_wdt_stop(); assert(feeds==0 && stopped==0);
  running=true; assert(rbos_wdt_start()==-EBUSY); running=false;
  init_error=-EIO; assert(rbos_wdt_start()==-EIO); init_error=0;
  alloc_error=-ENOMEM; assert(rbos_wdt_start()==-ENOMEM); alloc_error=0;
  assert(enabled==0);
  assert(rbos_wdt_start()==0 && enabled==1);
  rbos_wdt_feed(); assert(feeds==1);
  rbos_wdt_stop();
  assert(stopped==(CONFIG_RBOS_FATAL_REBOOT ? 0 : 1));
  rbos_reset_reason_log(); assert(logged);
}
'''
        for reboot in (0, 1):
            self.compile_and_run(headers, program, ['src/platform/nrf/wdt.c'],
                                 [f'-DCONFIG_RBOS_FATAL_REBOOT={reboot}',
                                  '-DCONFIG_RBOS_WDT_TIMEOUT_MS=2000'])

    def test_signed_evidence_gate(self):
        verify = runpy.run_path(str(ROOT / 'tools/bm-build/check-watchdog.py'))['verify']
        names = ['rbos_wdt_start', 'rbos_wdt_feed', 'rbos_supervisor_poll',
                 'mrbc_hal_abort', 'rbos_reset_reason_log']
        routes = ['bl 0 <nrfx_wdt_init>\nbl 0 <nrfx_wdt_enable>',
                  'b.w 0 <nrfx_wdt_channel_feed>',
                  'bl 0 <rbos_maintenance>\nbl 0 <rbos_wdt_feed>', '', '']
        report = dict(schema=1, instance=30, configuration=dict(CONFIG_RBOS_WDT=1,
                      CONFIG_NRFX_WDT=1, CONFIG_RBOS_WDT_TIMEOUT_MS=2000, CONFIG_RBOS_FATAL_REBOOT=0),
                      functions=[dict(name=n, address=i, size=1, disassembly=d,
                                      sha256=hashlib.sha256(b'x').hexdigest())
                                 for i, (n, d) in enumerate(zip(names, routes))])
        self.assertEqual(verify(report, 'FLASH 0x0', b'xxxxx')['signed_code'], 'PASS')
        for mutate in ('empty', 'bytes', 'route', 'config'):
            broken = copy.deepcopy(report)
            image = b'xxxxx'
            if mutate == 'empty': broken['functions'] = []
            if mutate == 'bytes': image = b'yyyyy'
            if mutate == 'route': broken['functions'][0]['disassembly'] = ''
            if mutate == 'config': broken['configuration']['CONFIG_NRFX_WDT'] = 0
            with self.assertRaises(ValueError):
                verify(broken, 'FLASH 0x0', image)
