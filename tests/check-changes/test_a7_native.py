from pathlib import Path
import unittest

import test_temperature

ROOT = Path(__file__).resolve().parents[2]
COMMON = {
    "mrubyc.h": "typedef struct TCB mrbc_tcb;\n",
    "zephyr/devicetree.h": """#include <stdint.h>
extern uint8_t peer_bytes[4096];
#define DT_ALIAS(n) n
#define DT_NODELABEL(n) n
#define DT_PROP(n,p) 43
#define DT_REG_ADDR(n) ((uintptr_t)peer_bytes)
#define DT_REG_SIZE(n) 4096
""",
    "zephyr/kernel.h": """#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <hal/nrf_gpio.h>
#define BUILD_ASSERT(c,m) _Static_assert(c,m)
#define IS_ENABLED(c) (c)
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define __aligned(n) __attribute__((aligned(n)))
int64_t k_uptime_get(void);
""",
    "zephyr/logging/log.h": """#define LOG_MODULE_REGISTER(...)
void test_log(const char *, ...);
#define LOG_INF(...) test_log(__VA_ARGS__)
#define LOG_ERR(...) test_log(__VA_ARGS__)
""",
    "hal/nrf_gpio.h": """#pragma once
#include <stdint.h>
typedef struct { uint32_t PIN_CNF[32]; } NRF_GPIO_Type;
NRF_GPIO_Type *nrf_gpio_pin_port_decode(uint32_t *);
void nrf_gpio_cfg_input(uint32_t,int);
uint32_t nrf_gpio_pin_read(uint32_t);
#define NRF_GPIO_PIN_PULLUP 1
#define NRF_GPIO_PIN_MAP(p,n) ((p)*32+(n))
""",
}
DEFINES = ["-I", str(ROOT / "firmware/include"), "-I", str(ROOT / "firmware/src")]


class A7NativeTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_retention_seed_and_read_only_verify(self):
        headers = dict(COMMON, **{
            "zephyr/sys/crc.h": "#include <stddef.h>\n#include <stdint.h>\nuint32_t crc32_ieee(const uint8_t *, size_t);\n",
            "bm/storage/bm_storage.h": """#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#define BM_STORAGE_EVT_WRITE_RESULT 1
struct bm_storage { int initialized; };
struct bm_storage_evt { int id, result; uint32_t addr; size_t len; void *ctx; };
struct bm_storage_config { void (*evt_handler)(struct bm_storage_evt *); const void *api; uintptr_t addr; size_t size; };
extern const int bm_storage_sd_api;
int bm_storage_init(struct bm_storage *, const struct bm_storage_config *);
int bm_storage_read(const struct bm_storage *, uint32_t, void *, uint32_t);
int bm_storage_write(const struct bm_storage *, uint32_t, const void *, uint32_t, void *);
""",
        })
        program = r'''
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include "SOURCE"
uint8_t peer_bytes[4096];
static uint8_t flash[32];
static unsigned writes, errors, successes;
static int init_error, write_error, read_error, level;
static int64_t now;
static NRF_GPIO_Type port;
const int bm_storage_sd_api;
int64_t k_uptime_get(void) { return now; }
NRF_GPIO_Type *nrf_gpio_pin_port_decode(uint32_t *p) { *p %= 32; return &port; }
void nrf_gpio_cfg_input(uint32_t p,int pull) { port.PIN_CNF[p%32] = pull; }
uint32_t nrf_gpio_pin_read(uint32_t p) { return level; }
uint32_t crc32_ieee(const uint8_t *p, size_t n) {
  uint32_t crc = ~0u;
  while(n--) { crc ^= *p++; for(unsigned i=0;i<8;++i) crc = (crc>>1) ^ ((crc&1)?0xedb88320u:0); }
  return ~crc;
}
void test_log(const char *format,...) {
  if (!strncmp(format,"p5 error=",9)) ++errors;
  else { assert(!strncmp(format,"p5 mode=",8)); ++successes; }
}
int bm_storage_init(struct bm_storage *s,const struct bm_storage_config *c) {
  assert(c->size==4096 && c->api==&bm_storage_sd_api && c->evt_handler==event_handler);
  return init_error;
}
int bm_storage_read(const struct bm_storage *s,uint32_t addr,void *dst,uint32_t len) {
  assert(addr==0 && len==32); memcpy(dst,flash,len); return read_error;
}
int bm_storage_write(const struct bm_storage *s,uint32_t addr,const void *src,uint32_t len,void *ctx) {
  assert(CONFIG_RBOS_RETENTION_SEED && addr==0 && len==32 && ctx==&storage && src==sentinel);
  ++writes; return write_error;
}
static void reset(void) {
  pending=completed=finished=false; result=0; now=0; writes=errors=successes=0;
  init_error=write_error=read_error=level=0; memset(flash,0,sizeof(flash));
  memset(peer_bytes,0,sizeof(peer_bytes)); port.PIN_CNF[11]=99;
}
static void finish_write(int status) {
  struct bm_storage_evt e = { .id=1,.result=status,.addr=0,.len=32,.ctx=&storage };
  event_handler(&e);
}
static void ready(void) {
  rbos_retention_start(); memcpy(flash,sentinel,sizeof(flash));
  if(CONFIG_RBOS_RETENTION_SEED) finish_write(0);
}
int main(void) {
  reset(); ready(); rbos_retention_poll(); assert(successes==1 && !errors && finished);
  assert(writes==(CONFIG_RBOS_RETENTION_SEED?1:0)); assert(port.PIN_CNF[11]==99);
  rbos_retention_poll(); assert(successes==1);
  reset(); rbos_retention_start(); if(CONFIG_RBOS_RETENTION_SEED) finish_write(0);
  rbos_retention_poll(); assert(errors==1 && !successes);
  reset(); ready(); flash[0]^=1; rbos_retention_poll(); assert(errors==1 && !successes);
  reset(); ready(); peer_bytes[0]^=1; rbos_retention_poll(); assert(errors==1 && !successes);
  reset(); init_error=-1; rbos_retention_start(); assert(errors==1 && !writes);
  reset(); ready(); read_error=-1; rbos_retention_poll(); assert(errors==1 && !successes);
  if(CONFIG_RBOS_RETENTION_SEED) {
    reset(); level=1; rbos_retention_start(); assert(errors==1 && !writes);
    reset(); write_error=-1; rbos_retention_start(); assert(errors==1 && writes==1);
    reset(); rbos_retention_start(); rbos_retention_poll(); assert(!errors && !finished);
    now=10001; rbos_retention_poll(); assert(errors==1 && !successes);
    reset(); rbos_retention_start(); finish_write(-1); rbos_retention_poll(); assert(errors==1);
  }
}
'''.replace("SOURCE", str(ROOT / "firmware/src/retention_fixture.c"))
        flags = ["-DCONFIG_RBOS_RETENTION_FIXTURE=1", "-DCONFIG_RBOS_RETENTION_NONCE=0x1234abcd",
                 "-DCONFIG_BM_STORAGE_BACKEND_SD=1", "-DCONFIG_SETTINGS=0", "-DCONFIG_BM_ZMS=0",
                 "-DCONFIG_RBOS_SATURATION_FIXTURE=0"]
        # The fixture header uses defined(), as generated Kconfig does.
        flags.remove("-DCONFIG_RBOS_SATURATION_FIXTURE=0")
        headers["zephyr/kernel.h"] += "\n#define CONFIG_RBOS_SATURATION_FIXTURE 0\n"
        for seed in (0, 1):
            with self.subTest(seed=seed):
                self.compile_and_run(headers, program, [], DEFINES + flags + [f"-DCONFIG_RBOS_RETENTION_SEED={seed}"])

    def test_saturation_real_queue_and_failures(self):
        headers = dict(COMMON, **{
            "nrfx_timer.h": """#include <stdint.h>
#include <stdbool.h>
typedef struct { bool event; } NRF_TIMER_Type;
extern NRF_TIMER_Type fake_timer;
#define NRF_TIMER21 (&fake_timer)
typedef struct { NRF_TIMER_Type *p_reg; } nrfx_timer_t;
typedef struct { int bit_width; } nrfx_timer_config_t;
#define NRFX_TIMER_INSTANCE(n) { .p_reg=n }
#define NRFX_TIMER_DEFAULT_CONFIG(n) { .bit_width=0 }
#define NRF_TIMER_BASE_FREQUENCY_GET(n) 16000000
#define NRF_TIMER_BIT_WIDTH_32 32
#define NRF_TIMER_CC_CHANNEL0 0
#define NRF_TIMER_EVENT_COMPARE0 0
#define NRF_TIMER_SHORT_COMPARE0_STOP_MASK 1
int nrfx_timer_init(nrfx_timer_t *,const nrfx_timer_config_t *,void *);
void nrfx_timer_uninit(nrfx_timer_t *);
void nrfx_timer_extended_compare(nrfx_timer_t *,int,uint32_t,int,bool);
uint32_t nrfx_timer_us_to_ticks(nrfx_timer_t *,uint32_t);
uint32_t nrfx_timer_compare_event_address_get(nrfx_timer_t *,int);
void nrfx_timer_clear(nrfx_timer_t *);
void nrfx_timer_enable(nrfx_timer_t *);
void nrfx_timer_disable(nrfx_timer_t *);
void nrf_timer_event_clear(NRF_TIMER_Type *,int);
bool nrf_timer_event_check(NRF_TIMER_Type *,int);
""",
            "helpers/nrfx_gppi.h": """#include <stdint.h>
typedef unsigned nrfx_gppi_handle_t;
int nrfx_gppi_conn_alloc(uint32_t,uint32_t,nrfx_gppi_handle_t *);
void nrfx_gppi_conn_enable(nrfx_gppi_handle_t);
void nrfx_gppi_conn_disable(nrfx_gppi_handle_t);
void nrfx_gppi_conn_free(uint32_t,uint32_t,nrfx_gppi_handle_t);
""",
        })
        program = r'''
#include <assert.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include "SOURCE"
NRF_TIMER_Type fake_timer;
static struct rbos_event_queue queue;
static unsigned level, logs, errors, allocation, enables, frees;
static bool enabled, powered;
static int timer_error, gppi_error;
static int64_t now;
int64_t k_uptime_get(void) { return now; }
uint32_t nrf_gpio_pin_read(uint32_t pin) { return level; }
void test_log(const char *format,...) {
  ++logs; if(!strncmp(format,"a7 error=",9)) ++errors;
  va_list args; va_start(args,format); vfprintf(stderr,format,args); va_end(args); fputc('\n',stderr);
}
int nrfx_timer_init(nrfx_timer_t *t,const nrfx_timer_config_t *c,void *cb) { return timer_error; }
void nrfx_timer_uninit(nrfx_timer_t *t) { enabled=powered=false; }
void nrfx_timer_extended_compare(nrfx_timer_t *t,int cc,uint32_t ticks,int shorts,bool irq) {
  assert(ticks==1000 && shorts==1 && !irq);
}
uint32_t nrfx_timer_us_to_ticks(nrfx_timer_t *t,uint32_t us) { return us; }
uint32_t nrfx_timer_compare_event_address_get(nrfx_timer_t *t,int cc) { return 0x1234; }
void nrfx_timer_clear(nrfx_timer_t *t) {}
void nrfx_timer_enable(nrfx_timer_t *t) { assert(!enabled && !powered); enabled=powered=true; ++enables; }
void nrfx_timer_disable(nrfx_timer_t *t) { assert(powered); enabled=powered=false; }
void nrf_timer_event_clear(NRF_TIMER_Type *t,int cc) { t->event=false; }
bool nrf_timer_event_check(NRF_TIMER_Type *t,int cc) { return t->event; }
int nrfx_gppi_conn_alloc(uint32_t event,uint32_t task,nrfx_gppi_handle_t *h) {
  assert(event==0x1234 && task==0x5678); if(gppi_error) return gppi_error; *h=7; ++allocation; return 0;
}
void nrfx_gppi_conn_enable(nrfx_gppi_handle_t h) { assert(h==7 && allocation); }
void nrfx_gppi_conn_disable(nrfx_gppi_handle_t h) { assert(h==7 && allocation); }
void nrfx_gppi_conn_free(uint32_t event,uint32_t task,nrfx_gppi_handle_t h) {
  assert(event==0x1234 && task==0x5678 && h==7 && allocation); --allocation; ++frees;
}
bool rbos_event_post(const struct rbos_event *e) { return rbos_event_queue_push(&queue,e); }
bool rbos_event_take(struct rbos_event *e) { return !rbos_fixture_holds_events() && rbos_event_queue_pop(&queue,e); }
void rbos_event_snapshot(struct rbos_event_stats *s) {
  *s=(struct rbos_event_stats){queue.size,queue.overflow,queue.coalesced};
}
static void reset(void) {
  rbos_fixture_disconnect(); memset(&queue,0,sizeof(queue));
  connected=timer_initialized=holding=started=pulse=waiting=finished=false;
  source=token=phase=generated=initial_level=interrupts=measured=accepted=latest=0;
  level=logs=errors=allocation=enables=frees=0; now=0; timer_error=gppi_error=0;
}
static void setup(void) { assert(!rbos_fixture_connect(0x5678)); rbos_fixture_begin(43,1); }
int main(void) {
  reset(); rbos_fixture_poll(); assert(!logs && !enabled);
  setup(); assert(allocation==1);
  for(unsigned i=0;i<100 && !finished;++i) {
    rbos_fixture_poll();
    if(enabled) {
      level^=1; enabled=false; fake_timer.event=true;
      rbos_fixture_irq();
      struct rbos_event e={.type=RBOS_EVENT_BUTTON,.source=43,.value=level,.generation=1};
      bool ok=rbos_event_post(&e); rbos_fixture_edge(43,level,ok);
    }
    rbos_fixture_poll();
    struct rbos_event e, delivered={0};
    while(rbos_event_take(&e)) if(e.type==RBOS_EVENT_BUTTON) delivered=e;
    if(delivered.count) rbos_fixture_delivery(delivered.source,delivered.value,delivered.count);
  }
  assert(finished && !errors && logs==8 && enables==15 && frees==1 && !allocation);
  assert(queue.size==0 && queue.overflow==5 && queue.coalesced==8);
  reset(); timer_error=-1; assert(rbos_fixture_connect(0x5678)==-1 && !allocation);
  reset(); gppi_error=-1; assert(rbos_fixture_connect(0x5678)==-1 && !timer_initialized);
  reset(); setup(); rbos_fixture_poll(); now=1001; rbos_fixture_poll(); assert(errors==1 && !allocation);
  reset(); setup(); struct rbos_event e={.type=RBOS_EVENT_COMPLETION}; rbos_event_post(&e);
  rbos_fixture_poll(); assert(errors==1 && !allocation);
  reset(); setup(); rbos_fixture_delivery(43,1,5); assert(errors==1 && !allocation);
}
'''.replace("SOURCE", str(ROOT / "firmware/src/saturation_fixture.c"))
        self.compile_and_run(headers, program, ["src/rbos/event_queue.c"], DEFINES + [
            "-DCONFIG_RBOS_SATURATION_FIXTURE=1", "-DCONFIG_RBOS_PERIPHERAL_EXERCISE=0",
            "-DCONFIG_RBOS_RETENTION_FIXTURE=0"])
