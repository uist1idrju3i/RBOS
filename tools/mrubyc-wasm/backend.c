#include <stddef.h>
#include <emscripten.h>

#include "backend.h"

static struct {
  int32_t quarter_celsius;
  enum rbos_status status;
  unsigned int calls;
} temperature = { .quarter_celsius = 100 };

static enum rbos_status temperature_read(void *context, int32_t *quarter_celsius)
{
  (void)context;
  ++temperature.calls;
  if (temperature.status == RBOS_OK) *quarter_celsius = temperature.quarter_celsius;
  return temperature.status;
}

static struct {
  int32_t raw;
  enum rbos_status status;
  uint32_t delay_ms, stop_ms, started, stopped, token;
  unsigned int calls;
  int input;
  int active, cancelling;
} adc = { .raw = 1024 };

static uint32_t uptime_ms(void *context)
{
  (void)context;
  return (uint32_t)emscripten_get_now();
}

static enum rbos_status adc_start(void *context, enum rbos_adc_input input, uint32_t token)
{
  if (adc.active) return RBOS_BUSY;
  adc.active = 1;
  adc.cancelling = 0;
  adc.started = uptime_ms(context);
  adc.token = token;
  adc.input = input;
  ++adc.calls;
  return RBOS_OK;
}

static enum rbos_status adc_poll(void *context, uint32_t token, struct rbos_adc_sample *sample)
{
  if (!adc.active || adc.token != token) return RBOS_IO_ERROR;
  if (adc.cancelling) {
    if ((uint32_t)(uptime_ms(context) - adc.stopped) < adc.stop_ms) return RBOS_PENDING;
    adc.active = 0;
    return RBOS_TIMEOUT;
  }
  if ((uint32_t)(uptime_ms(context) - adc.started) < adc.delay_ms) return RBOS_PENDING;
  adc.active = 0;
  if (adc.status == RBOS_OK)
    *sample = (struct rbos_adc_sample){ adc.raw, 3600000, 12 };
  return adc.status;
}

static void adc_cancel(void *context, uint32_t token)
{
  if (adc.active && adc.token == token && !adc.cancelling) {
    adc.cancelling = 1;
    adc.stopped = uptime_ms(context);
  }
}

void rbos_wasm_adc_configure(int32_t raw, enum rbos_status status, uint32_t delay_ms, uint32_t stop_ms)
{
  adc.raw = raw;
  adc.status = status;
  adc.delay_ms = delay_ms;
  adc.stop_ms = stop_ms;
}

unsigned int rbos_wasm_adc_calls(void) { return adc.calls; }
int rbos_wasm_adc_input(void) { return adc.input; }
int rbos_wasm_adc_active(void) { return adc.active; }

static struct rbos_backend backend = {
  .temperature_read = temperature_read, .uptime_ms = uptime_ms,
  .adc_start = adc_start, .adc_poll = adc_poll, .adc_cancel = adc_cancel,
};

const struct rbos_backend *rbos_wasm_backend(void)
{
  return &backend;
}

void rbos_wasm_temperature_configure(int32_t quarter_celsius, enum rbos_status status)
{
  temperature.quarter_celsius = quarter_celsius;
  temperature.status = status;
}

void rbos_wasm_temperature_available(int available)
{
  backend.temperature_read = available ? temperature_read : NULL;
}

unsigned int rbos_wasm_temperature_calls(void)
{
  return temperature.calls;
}
