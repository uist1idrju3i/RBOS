import unittest
import test_temperature


class ADCAdapterTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run
    def test_nrfx_adapter_mapping_calibration_irq_stop_and_dma(self):
        headers = {
            "cmsis_core.h": """#include <stdint.h>
extern uint32_t mask;
static inline uint32_t __get_IPSR(void) { return mask; }
static inline uint32_t __get_PRIMASK(void) { return 0; }
static inline uint32_t __get_BASEPRI(void) { return 0; }
static inline uint32_t __get_FAULTMASK(void) { return 0; }
""",
            "bm/bm_irq.h": """#define BM_IRQ_OFFSET 2
#define BM_IRQ_DIRECT_CONNECT(n,p,fn,f) \\
_Static_assert((n) == 213 && (p) == 7 && (f) == 0, "IRQ mapping"); \\
vector = fn
""",
            "zephyr/kernel.h": """#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define BUILD_ASSERT(c) _Static_assert(c, #c)
#define __aligned(n) __attribute__((aligned(n)))
static inline uint32_t k_uptime_get_32(void) { return 123; }
static inline unsigned int irq_lock(void) { return 0; }
static inline void irq_unlock(unsigned int key) { (void)key; }
""",
            "zephyr/irq.h": """#define ISR_DIRECT_DECLARE(fn) static int fn(void)
""",
            "nrfx_saadc.h": """#ifndef TEST_NRFX_H
#define TEST_NRFX_H
#include <stdbool.h>
#include <stdint.h>
#define NRFX_IRQ_NUMBER_GET(p) 213
#define NRF_SAADC ((void *)1)
#define NRFX_SAADC_REF_INTERNAL_VALUE 900
typedef int16_t nrf_saadc_value_t;
typedef enum { NRFX_ANALOG_INTERNAL_VDD = 128, NRFX_ANALOG_INTERNAL_AVDD = 130,
               NRFX_ANALOG_INTERNAL_DVDD = 131 } nrfx_analog_input_t;
enum { NRF_SAADC_GAIN1_4 = 4, NRF_SAADC_RESOLUTION_12BIT = 12,
       NRF_SAADC_OVERSAMPLE_DISABLED = 0, NRF_SAADC_EVENT_STOPPED = 9 };
enum { NRFX_SAADC_EVT_CALIBRATEDONE = 1, NRFX_SAADC_EVT_DONE = 2 };
typedef struct { int type; struct { struct { nrf_saadc_value_t *p_buffer;
                                           uint16_t size; } done; } data; } nrfx_saadc_evt_t;
typedef void (*nrfx_saadc_event_handler_t)(const nrfx_saadc_evt_t *);
typedef struct { struct { int gain; } channel_config;
                 nrfx_analog_input_t pin_p; int channel_index; } nrfx_saadc_channel_t;
#define NRFX_SAADC_DEFAULT_CHANNEL_SE(pin,index) \\
  { .channel_config = { .gain = 1 }, .pin_p = pin, .channel_index = index }
bool nrfx_saadc_init_check(void);
int nrfx_saadc_init(uint8_t priority);
void nrfx_saadc_uninit(void);
int nrfx_saadc_channels_config(const nrfx_saadc_channel_t *, uint32_t);
int nrfx_saadc_simple_mode_set(uint32_t, int, int, nrfx_saadc_event_handler_t);
int nrfx_saadc_buffer_set(nrf_saadc_value_t *, uint16_t);
int nrfx_saadc_offset_calibrate(nrfx_saadc_event_handler_t);
int nrfx_saadc_mode_trigger(void);
void nrfx_saadc_abort(void);
bool nrf_saadc_event_check(void *, int);
void nrfx_saadc_irq_handler(void);
#endif
""",
        }
        program = r'''#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <nrfx_saadc.h>
#include "rbos/backend.h"
uint32_t mask;
static int failure, releases, aborts, stopped, pending, count, pin, triggers;
static bool initialized, dma;
static int16_t *target;
static nrfx_saadc_event_handler_t handler;
static int (*vector)(void);
bool nrfx_saadc_init_check(void) { return initialized; }
int nrfx_saadc_init(uint8_t priority) {
  assert(priority == 7 && !initialized);
  if (failure == 1) return -1;
  initialized = true;
  return 0;
}
void nrfx_saadc_uninit(void) {
  assert(initialized && !dma);
  initialized = false;
  ++releases;
}
int nrfx_saadc_channels_config(const nrfx_saadc_channel_t *channel, uint32_t size) {
  assert(size == 1 && channel->channel_index == 0 && channel->channel_config.gain == 4);
  pin = channel->pin_p;
  return failure == 2 ? -1 : 0;
}
int nrfx_saadc_simple_mode_set(uint32_t channels, int bits, int over,
                               nrfx_saadc_event_handler_t callback) {
  assert(channels == 1 && bits == 12 && over == 0 && callback);
  handler = callback;
  return failure == 3 ? -1 : 0;
}
int nrfx_saadc_buffer_set(int16_t *buffer, uint16_t size) {
  assert(size == 1 && ((uintptr_t)buffer % 4) == 0);
  target = buffer;
  return failure == 4 ? -1 : 0;
}
int nrfx_saadc_offset_calibrate(nrfx_saadc_event_handler_t callback) {
  assert(callback == handler);
  if (failure == 5) return -1;
  dma = true;
  return 0;
}
int nrfx_saadc_mode_trigger(void) {
  ++triggers;
  assert(!dma);
  if (failure == 6) return -1;
  dma = true;
  return 0;
}
void nrfx_saadc_abort(void) { ++aborts; assert(dma); }
bool nrf_saadc_event_check(void *reg, int event) {
  assert(reg == NRF_SAADC && event == NRF_SAADC_EVENT_STOPPED);
  return stopped;
}
void nrfx_saadc_irq_handler(void) {
  stopped = 0;
  if (pending) {
    nrfx_saadc_evt_t event = { .type = pending,
      .data.done = { .p_buffer = target, .size = count } };
    handler(&event);
  }
}
static void fire(int type, int stop, int size, int16_t raw) {
  dma = false;
  pending = type;
  stopped = stop;
  count = size;
  *target = raw;
  assert(vector() == 0);
}
'''
        # Keep the real static IRQ wrapper visible, without changing vendor code.
        from pathlib import Path
        source = Path(__file__).resolve().parents[2] / "src/platform/nrf/adc.c"
        program += f'\n#include "{source}"\n'
        program += r'''
int main(void) {
  struct rbos_adc_sample out = { .raw = 123 };
  assert(rbos_nrf_uptime_ms(0) == 123);
  assert(rbos_nrf_adc_start(0, -1, 1) == RBOS_IO_ERROR);
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 0) == RBOS_IO_ERROR);
  mask = 1;
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 1) == RBOS_IO_ERROR);
  mask = 0;
  initialized = true;
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 1) == RBOS_BUSY);
  initialized = false;
  for (failure = 1; failure <= 5; ++failure) {
    assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 1) == RBOS_IO_ERROR);
    assert(!initialized && !dma);
  }
  assert(releases == 4);
  failure = 0;
  const int pins[] = { 131, 130, 128 };
  for (int input = 0; input < 3; ++input) {
    assert(rbos_nrf_adc_start(0, input, input + 1) == RBOS_OK && pin == pins[input]);
    assert(rbos_nrf_adc_start(0, input, 5) == RBOS_BUSY);
    assert(rbos_nrf_adc_poll(0, input + 1, &out) == RBOS_PENDING && out.raw == 123);
    fire(NRFX_SAADC_EVT_CALIBRATEDONE, 1, 0, 0);
    assert(rbos_nrf_adc_poll(0, input + 1, &out) == RBOS_PENDING && dma);
    fire(NRFX_SAADC_EVT_DONE, 0, 1, -1);
    assert(rbos_nrf_adc_poll(0, input + 1, &out) == RBOS_OK);
    assert(out.raw == -1 && out.bits == 12 && out.full_scale_uv == 3600000);
    assert(!initialized && !dma);
    out.raw = 123;
  }
  assert(triggers == 3);
  /* Calibration abort: STOPPED arrives without CALIBRATEDONE or DONE callback. */
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 10) == RBOS_OK);
  rbos_nrf_adc_cancel(0, 9);
  assert(aborts == 0 && dma);
  rbos_nrf_adc_cancel(0, 10);
  rbos_nrf_adc_cancel(0, 10);
  assert(aborts == 1 && dma);
  assert(rbos_nrf_adc_poll(0, 10, &out) == RBOS_PENDING && initialized);
  assert(rbos_nrf_adc_start(0, RBOS_ADC_AVDD, 11) == RBOS_BUSY);
  fire(0, 1, 0, 0);
  assert(rbos_nrf_adc_poll(0, 10, &out) == RBOS_TIMEOUT && !initialized && out.raw == 123);
  assert(vector() == 0); /* Late pending IRQ after release is harmless. */
  assert(rbos_nrf_adc_start(0, RBOS_ADC_AVDD, 11) == RBOS_OK);
  assert(rbos_nrf_adc_poll(0, 10, &out) == RBOS_IO_ERROR && dma);
  fire(NRFX_SAADC_EVT_CALIBRATEDONE, 1, 0, 0);
  rbos_nrf_adc_cancel(0, 11); /* Completed calibration wins the DMA-stop race. */
  assert(aborts == 1);
  assert(rbos_nrf_adc_poll(0, 11, &out) == RBOS_TIMEOUT && !initialized);
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 12) == RBOS_OK);
  fire(NRFX_SAADC_EVT_CALIBRATEDONE, 1, 0, 0);
  assert(rbos_nrf_adc_poll(0, 12, &out) == RBOS_PENDING);
  rbos_nrf_adc_cancel(0, 12);
  assert(aborts == 2 && dma);
  fire(NRFX_SAADC_EVT_DONE, 1, 0, 0);
  assert(rbos_nrf_adc_poll(0, 12, &out) == RBOS_TIMEOUT && !initialized);
  /* Wrong DMA size must not expose an unwritten sample. */
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 13) == RBOS_OK);
  fire(NRFX_SAADC_EVT_CALIBRATEDONE, 1, 0, 0);
  assert(rbos_nrf_adc_poll(0, 13, &out) == RBOS_PENDING);
  fire(NRFX_SAADC_EVT_DONE, 0, 0, 0);
  assert(rbos_nrf_adc_poll(0, 13, &out) == RBOS_IO_ERROR && out.raw == 123);
  assert(rbos_nrf_adc_start(0, RBOS_ADC_VDD, 14) == RBOS_OK);
  fire(NRFX_SAADC_EVT_CALIBRATEDONE, 1, 0, 0);
  failure = 6;
  assert(rbos_nrf_adc_poll(0, 14, &out) == RBOS_IO_ERROR && !initialized);
}
'''
        self.compile_and_run(headers, program, [])
