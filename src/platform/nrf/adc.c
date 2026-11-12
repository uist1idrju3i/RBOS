#include <errno.h>
#include <bm/bm_irq.h>
#include <cmsis_core.h>
#include <nrfx_saadc.h>
#include <zephyr/kernel.h>
#include <zephyr/irq.h>
#include "adc.h"

enum { CALIBRATED = 1, DONE = 2, STOPPED = 4, BAD_SAMPLE = 8 };
static nrf_saadc_value_t buffer[1] __aligned(4);
static struct {
  bool owned;
  bool sampling;
  bool stopping;
  uint32_t token;
  unsigned int events;
  int16_t raw;
} state;

BUILD_ASSERT(NRFX_IRQ_NUMBER_GET(NRF_SAADC) == 213);
BUILD_ASSERT(NRFX_SAADC_REF_INTERNAL_VALUE == 900);
BUILD_ASSERT(sizeof(nrf_saadc_value_t) == sizeof(int16_t));

static bool foreground(void)
{
  return !__get_IPSR() && !__get_PRIMASK() && !__get_BASEPRI() && !__get_FAULTMASK();
}

static void event_handler(const nrfx_saadc_evt_t *event)
{
  if (!state.owned) return;
  if (event->type == NRFX_SAADC_EVT_CALIBRATEDONE) {
    if (state.sampling || (state.events & CALIBRATED)) state.events |= BAD_SAMPLE;
    state.events |= CALIBRATED;
  }
  if (event->type == NRFX_SAADC_EVT_DONE) {
    if (!state.sampling || (state.events & DONE)) state.events |= BAD_SAMPLE;
    state.events |= DONE;
    if (event->data.done.p_buffer != buffer || event->data.done.size != 1)
      state.events |= BAD_SAMPLE;
    else state.raw = buffer[0];
  }
}

ISR_DIRECT_DECLARE(saadc_irq)
{
  if (!state.owned) return 0;
  /* nrfx does not notify its client when calibration is stopped before END. */
  bool stopped = nrf_saadc_event_check(NRF_SAADC, NRF_SAADC_EVENT_STOPPED);
  nrfx_saadc_irq_handler();
  if (stopped) state.events |= STOPPED;
  return 0;
}

uint32_t rbos_nrf_uptime_ms(void *context)
{
  (void)context;
  return k_uptime_get_32();
}

static void release(void)
{
  nrfx_saadc_uninit();
  state.owned = false;
  state.events = 0;
}

enum rbos_status rbos_nrf_adc_start(void *context, enum rbos_adc_input input, uint32_t token)
{
  (void)context;
  if (!foreground() || !token) return RBOS_IO_ERROR;
  nrfx_analog_input_t pin;
  switch (input) {
  case RBOS_ADC_DVDD: pin = NRFX_ANALOG_INTERNAL_DVDD; break;
  case RBOS_ADC_AVDD: pin = NRFX_ANALOG_INTERNAL_AVDD; break;
  case RBOS_ADC_VDD: pin = NRFX_ANALOG_INTERNAL_VDD; break;
  default: return RBOS_IO_ERROR;
  }
  if (state.owned || nrfx_saadc_init_check()) return RBOS_BUSY;
  BM_IRQ_DIRECT_CONNECT(NRFX_IRQ_NUMBER_GET(NRF_SAADC), 7, saadc_irq, 0);
  if (nrfx_saadc_init(7)) return RBOS_IO_ERROR;
  state.owned = true;
  state.token = token;
  state.events = 0;
  state.sampling = false;
  state.stopping = false;
  nrfx_saadc_channel_t channel = NRFX_SAADC_DEFAULT_CHANNEL_SE(pin, 0);
  channel.channel_config.gain = NRF_SAADC_GAIN1_4;
  int result = nrfx_saadc_channels_config(&channel, 1);
  if (!result) result = nrfx_saadc_simple_mode_set(1, NRF_SAADC_RESOLUTION_12BIT,
                                                  NRF_SAADC_OVERSAMPLE_DISABLED, event_handler);
  if (!result) result = nrfx_saadc_buffer_set(buffer, 1);
  if (!result) result = nrfx_saadc_offset_calibrate(event_handler);
  if (result) {
    release();
    return RBOS_IO_ERROR;
  }
  return RBOS_OK;
}

void rbos_nrf_adc_cancel(void *context, uint32_t token)
{
  (void)context;
  if (!foreground() || !state.owned || state.token != token || state.stopping) return;
  unsigned int key = irq_lock();
  state.stopping = true;
  bool quiescent = (state.events & (DONE | CALIBRATED | STOPPED)) != 0;
  irq_unlock(key);
  if (!quiescent) nrfx_saadc_abort();
}

enum rbos_status rbos_nrf_adc_poll(void *context, uint32_t token, struct rbos_adc_sample *sample)
{
  (void)context;
  /* An invalid caller must not accidentally declare a live DMA terminal. */
  if (!foreground() || !sample) return RBOS_PENDING;
  if (!state.owned || state.token != token) return RBOS_IO_ERROR;
  unsigned int key = irq_lock();
  unsigned int events = state.events;
  int16_t raw = state.raw;
  irq_unlock(key);
  if (state.stopping) {
    if (!(events & (DONE | CALIBRATED | STOPPED))) return RBOS_PENDING;
    release();
    return RBOS_TIMEOUT;
  }
  if ((events & BAD_SAMPLE) && (events & (DONE | CALIBRATED))) {
    release();
    return RBOS_IO_ERROR;
  }
  if (!state.sampling && (events & CALIBRATED)) {
    key = irq_lock();
    state.events = 0;
    state.sampling = true;
    irq_unlock(key);
    if (nrfx_saadc_mode_trigger()) {
      release();
      return RBOS_IO_ERROR;
    }
    return RBOS_PENDING;
  }
  if (state.sampling && (events & DONE)) {
    release();
    if (events & BAD_SAMPLE) return RBOS_IO_ERROR;
    *sample = (struct rbos_adc_sample){ raw, 3600000, 12 };
    return RBOS_OK;
  }
  if (events & STOPPED) {
    release();
    return RBOS_IO_ERROR;
  }
  return RBOS_PENDING;
}
