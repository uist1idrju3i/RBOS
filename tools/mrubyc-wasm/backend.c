#include <stddef.h>

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

static struct rbos_backend backend = { .temperature_read = temperature_read };

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
