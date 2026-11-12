import unittest
import test_temperature


class NRFButtonTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_irq_pin_generation_and_retryable_cleanup(self):
        headers = {
            "board-config.h": "",
            "mrubyc.h": "typedef struct TCB mrbc_tcb;\n",
            "zephyr/devicetree.h": """#define DT_ALIAS(n) n
#define DT_PROP_(n,p) DT_##n##_##p
#define DT_PROP(n,p) DT_PROP_(n,p)
#define DT_sw0_pin 45
#define DT_sw1_pin 41
#define DT_sw2_pin 40
#define DT_sw3_pin 4
#define DT_sw0_active_low 1
#define DT_sw1_active_low 1
#define DT_sw2_active_low 1
#define DT_sw3_active_low 1
""",
            "zephyr/kernel.h": "#define BUILD_ASSERT(c,m) _Static_assert(c,m)\n",
            "zephyr/irq.h": "unsigned int irq_lock(void);\nvoid irq_unlock(unsigned int);\n#define ISR_DIRECT_DECLARE(fn) int fn(void)\n",
            "bm/bm_irq.h": """#define GPIOTE20_0_IRQn 218
#define GPIOTE30_0_IRQn 268
void connect_irq(unsigned int, int (*)(void));
#define BM_IRQ_DIRECT_CONNECT(n,p,fn,f) do { _Static_assert((p)==7 && (f)==0,"IRQ priority"); connect_irq(n,fn); } while(0)
""",
            "nrfx_gpiote.h": """#ifndef TEST_GPIOTE_H
#define TEST_GPIOTE_H
#include <stdint.h>
#include <stdbool.h>
typedef struct { uint32_t PIN_CNF[32]; } NRF_GPIO_Type;
NRF_GPIO_Type *nrf_gpio_pin_port_decode(uint32_t *);
uint32_t nrf_gpio_pin_read(uint32_t);
void nrf_gpio_cfg_input(uint32_t,int);
void nrf_gpio_cfg_default(uint32_t);
#define NRF_GPIO_PIN_PULLUP 1
#define NRF_GPIOTE20 20
#define NRF_GPIOTE30 30
#define NRFX_GPIOTE_TRIGGER_TOGGLE 3
typedef uint32_t nrfx_gpiote_pin_t;
typedef int nrfx_gpiote_trigger_t;
typedef void (*handler_t)(nrfx_gpiote_pin_t,nrfx_gpiote_trigger_t,void *);
typedef struct { int id; bool initialized; } nrfx_gpiote_t;
#define NRFX_GPIOTE_INSTANCE(n) { .id = n }
typedef struct { int trigger; uint8_t *p_in_channel; } nrfx_gpiote_trigger_config_t;
typedef struct { handler_t handler; void *p_context; } nrfx_gpiote_handler_config_t;
typedef struct { nrfx_gpiote_trigger_config_t *p_trigger_config;
                 nrfx_gpiote_handler_config_t *p_handler_config; } nrfx_gpiote_input_pin_config_t;
bool nrfx_gpiote_init_check(nrfx_gpiote_t *);
int nrfx_gpiote_init(nrfx_gpiote_t *,int);
int nrfx_gpiote_channel_alloc(nrfx_gpiote_t *,uint8_t *);
int nrfx_gpiote_channel_free(nrfx_gpiote_t *,uint8_t);
int nrfx_gpiote_input_configure(nrfx_gpiote_t *,uint32_t,const nrfx_gpiote_input_pin_config_t *);
int nrfx_gpiote_pin_uninit(nrfx_gpiote_t *,uint32_t);
void nrfx_gpiote_trigger_enable(nrfx_gpiote_t *,uint32_t,bool);
void nrfx_gpiote_trigger_disable(nrfx_gpiote_t *,uint32_t);
void nrfx_gpiote_irq_handler(nrfx_gpiote_t *);
#endif
""",
        }
        program = r'''#include <assert.h>
#include <string.h>
#include <nrfx_gpiote.h>
#include "button.h"
#include "rbos/event_queue.h"
static struct rbos_event_queue queue;
static NRF_GPIO_Type ports[3];
static handler_t callbacks[96];
static unsigned int lock_depth, allocations, free_calls, uninit_calls;
static int failure, expected_instance, pending_pin;
static int (*vectors[2])(void);
unsigned int irq_lock(void) { return lock_depth++; }
void irq_unlock(unsigned int previous) { assert(lock_depth==previous+1); lock_depth=previous; }
void connect_irq(unsigned int irq, int (*fn)(void)) {
  assert(lock_depth && (irq==218 || irq==268)); vectors[irq==268]=fn;
}
NRF_GPIO_Type *nrf_gpio_pin_port_decode(uint32_t *pin) {
  unsigned int port=*pin/32; *pin%=32; return &ports[port];
}
uint32_t nrf_gpio_pin_read(uint32_t pin) { (void)pin; return 0; }
void nrf_gpio_cfg_input(uint32_t pin,int pull) { assert(pull==1); ports[pin/32].PIN_CNF[pin%32]=9; }
void nrf_gpio_cfg_default(uint32_t pin) { ports[pin/32].PIN_CNF[pin%32]=0; }
bool nrfx_gpiote_init_check(nrfx_gpiote_t *i) { return i->initialized; }
int nrfx_gpiote_init(nrfx_gpiote_t *i,int priority) {
  assert(lock_depth && priority==7 && i->id==expected_instance);
  if (failure==1) return -1; i->initialized=true; return 0;
}
int nrfx_gpiote_channel_alloc(nrfx_gpiote_t *i,uint8_t *channel) {
  assert(lock_depth && i->id==expected_instance);
  if (failure==2) return -1; *channel=0; ++allocations; return 0;
}
int nrfx_gpiote_channel_free(nrfx_gpiote_t *i,uint8_t channel) {
  (void)i; assert(lock_depth && channel==0 && allocations); ++free_calls;
  if (failure==5) return -1; --allocations; return 0;
}
int nrfx_gpiote_input_configure(nrfx_gpiote_t *i,uint32_t pin,const nrfx_gpiote_input_pin_config_t *c) {
  assert(i->id==expected_instance && c->p_trigger_config->trigger==3);
  assert(*c->p_trigger_config->p_in_channel==0 && !c->p_handler_config->p_context);
  callbacks[pin]=c->p_handler_config->handler;
  ports[pin/32].PIN_CNF[pin%32]=99;
  return failure==3 ? -1 : 0;
}
int nrfx_gpiote_pin_uninit(nrfx_gpiote_t *i,uint32_t pin) {
  (void)i; assert(lock_depth); ++uninit_calls;
  if (failure==4) return -1; callbacks[pin]=0; nrf_gpio_cfg_default(pin); return 0;
}
void nrfx_gpiote_trigger_enable(nrfx_gpiote_t *i,uint32_t pin,bool irq) {
  (void)i; assert(lock_depth && irq && callbacks[pin]);
}
void nrfx_gpiote_trigger_disable(nrfx_gpiote_t *i,uint32_t pin) { (void)i;(void)pin; assert(lock_depth); }
void nrfx_gpiote_irq_handler(nrfx_gpiote_t *i) {
  assert(i->id==expected_instance && callbacks[pending_pin]); callbacks[pending_pin](pending_pin,3,0);
}
enum rbos_status rbos_nrf_pin_validate(void *context,uint32_t pin) {
  (void)context; return pin<96 ? RBOS_OK : RBOS_INVALID_PIN;
}
bool rbos_event_post(const struct rbos_event *event) { return rbos_event_queue_push(&queue,event); }
bool rbos_event_take(struct rbos_event *event) { return rbos_event_queue_pop(&queue,event); }
void rbos_event_snapshot(struct rbos_event_stats *s) {
  *s=(struct rbos_event_stats){queue.size,queue.overflow,queue.coalesced};
}
int main(void) {
  expected_instance=20;
  assert(rbos_nrf_button_watch(0,96,1)==RBOS_INVALID_PIN);
  assert(rbos_nrf_button_watch(0,73,1)==RBOS_UNSUPPORTED);
  for (failure=1; failure<=3; ++failure) {
    ports[1].PIN_CNF[13]=42;
    assert(rbos_nrf_button_watch(0,45,1)!=RBOS_OK);
    assert(!allocations && !rbos_nrf_button_owns(45) && ports[1].PIN_CNF[13]==42);
  }
  failure=0;
  assert(rbos_nrf_button_watch(0,45,7)==RBOS_OK && allocations==1);
  assert(rbos_nrf_button_owns(45));
  assert(rbos_nrf_button_watch(0,45,8)==RBOS_BUSY);
  pending_pin=45; vectors[0](); vectors[0]();
  struct rbos_event event;
  assert(rbos_nrf_event_take(0,&event) && event.source==45 && event.value==0 && event.count==2 && event.generation==7);
  assert(rbos_nrf_button_unwatch(0,45,8)==RBOS_IO_ERROR && allocations==1);
  failure=4;
  assert(rbos_nrf_button_unwatch(0,45,7)==RBOS_IO_ERROR && allocations==1);
  failure=5;
  assert(rbos_nrf_button_unwatch(0,45,7)==RBOS_IO_ERROR && allocations==1);
  unsigned int already_uninitialized=uninit_calls;
  failure=0;
  assert(rbos_nrf_button_unwatch(0,45,7)==RBOS_OK && !allocations);
  assert(uninit_calls==already_uninitialized && !rbos_nrf_button_owns(45));
  expected_instance=30;
  assert(rbos_nrf_button_watch(0,4,9)==RBOS_OK);
  pending_pin=4; vectors[1]();
  assert(rbos_nrf_event_take(0,&event) && event.source==4 && event.generation==9);
  assert(rbos_nrf_button_unwatch(0,4,9)==RBOS_OK && !allocations && !lock_depth);
  assert(free_calls>=4);
}
'''
        self.compile_and_run(headers, program, ["src/platform/nrf/button.c", "src/rbos/event_queue.c"],
                             ["-I", str(test_temperature.ROOT / "src/platform/nrf"),
                              "-I", str(test_temperature.ROOT / "firmware/src"),
                              "-Wno-misleading-indentation"])
