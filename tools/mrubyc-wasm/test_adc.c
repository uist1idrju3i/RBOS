#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include "rbos/adc.h"

static uint32_t now, current;
static unsigned int starts, cancels;
static enum rbos_status status, start_status;
static struct rbos_adc_sample measured = { 1024, 3600000, 12 };
static enum rbos_adc_input selected;

static uint32_t uptime(void *context) { (void)context; return now; }
static enum rbos_status start(void *context, enum rbos_adc_input input, uint32_t token)
{
  (void)context;
  ++starts;
  selected = input;
  current = token;
  return start_status;
}
static enum rbos_status poll(void *context, uint32_t token, struct rbos_adc_sample *sample)
{
  (void)context;
  assert(token == current);
  if (status == RBOS_OK) *sample = measured;
  return status;
}
static void cancel(void *context, uint32_t token)
{
  (void)context;
  assert(token == current);
  ++cancels;
}

int main(void)
{
  struct rbos_backend backend = {
    .uptime_ms = uptime, .adc_start = start, .adc_poll = poll, .adc_cancel = cancel,
  };
  struct rbos_adc adc = { .backend = &backend };
  struct rbos_adc_sample output = { 123, 456, 7 };
  assert(rbos_adc_start(&adc, -1) == RBOS_IO_ERROR && starts == 0);
  assert(rbos_adc_start(&adc, 3) == RBOS_IO_ERROR && starts == 0);
  for (enum rbos_adc_input input = RBOS_ADC_DVDD; input <= RBOS_ADC_VDD; ++input) {
    status = RBOS_PENDING;
    assert(rbos_adc_start(&adc, input) == RBOS_OK && selected == input);
    assert(rbos_adc_start(&adc, input) == RBOS_BUSY);
    uint32_t token = adc.token;
    rbos_adc_service(&adc);
    assert(rbos_adc_take(&adc, token, &output) == RBOS_PENDING && output.raw == 123);
    assert(rbos_adc_take(&adc, token + 1, &output) == RBOS_IO_ERROR);
    rbos_adc_cancel(&adc, token + 1);
    assert(cancels == 0);
    status = RBOS_OK;
    rbos_adc_service(&adc);
    assert(rbos_adc_take(&adc, token, &output) == RBOS_OK && output.raw == 1024);
    assert(!adc.active);
    assert(rbos_adc_take(&adc, token, &output) == RBOS_IO_ERROR);
    output.raw = 123;
  }
  const int32_t raw[] = { INT16_MIN, -1, 0, 1, 4095, INT16_MAX, INT16_MIN - 1, INT16_MAX + 1 };
  for (unsigned int i = 0; i < sizeof(raw) / sizeof(*raw); ++i) {
    measured.raw = raw[i];
    assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_OK);
    rbos_adc_service(&adc);
    enum rbos_status expected = i < 6 ? RBOS_OK : RBOS_IO_ERROR;
    output.raw = 123;
    assert(rbos_adc_take(&adc, adc.token, &output) == expected);
    assert(output.raw == (expected == RBOS_OK ? raw[i] : 123));
  }
  measured.raw = 100;
  measured.full_scale_uv = 0;
  assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_OK);
  rbos_adc_service(&adc);
  assert(rbos_adc_take(&adc, adc.token, &output) == RBOS_IO_ERROR);
  measured.full_scale_uv = 3600000;
  for (unsigned int bits = 0; bits < 18; ++bits) {
    measured.bits = bits;
    assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_OK);
    rbos_adc_service(&adc);
    assert(rbos_adc_take(&adc, adc.token, &output) ==
           (bits >= 8 && bits <= 16 ? RBOS_OK : RBOS_IO_ERROR));
  }
  measured.bits = 12;
  for (int failure = RBOS_IO_ERROR; failure <= RBOS_TIMEOUT; ++failure) {
    start_status = failure;
    assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == (enum rbos_status)failure && !adc.active);
    start_status = RBOS_OK;
    status = failure;
    assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_OK);
    rbos_adc_service(&adc);
    output.raw = 123;
    assert(rbos_adc_take(&adc, adc.token, &output) == (enum rbos_status)failure);
    assert(output.raw == 123);
  }
  /* Missing completion, delayed STOP and clock wrap cannot release DMA early. */
  status = RBOS_PENDING;
  now = UINT32_MAX - 50;
  assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_OK);
  uint32_t old = adc.token;
  now += 99;
  rbos_adc_service(&adc);
  assert(adc.active && !adc.stopping);
  ++now;
  rbos_adc_service(&adc);
  assert(adc.active && adc.stopping && cancels == 1);
  rbos_adc_service(&adc);
  rbos_adc_cancel(&adc, old);
  assert(cancels == 1 && rbos_adc_start(&adc, RBOS_ADC_AVDD) == RBOS_BUSY);
  assert(rbos_adc_take(&adc, old, &output) == RBOS_TIMEOUT);
  status = RBOS_OK;
  rbos_adc_service(&adc);
  assert(!adc.active);
  assert(rbos_adc_start(&adc, RBOS_ADC_AVDD) == RBOS_OK && adc.token != old);
  rbos_adc_cancel(&adc, old);
  assert(!adc.stopping && cancels == 1);
  rbos_adc_service(&adc);
  now += RBOS_ADC_TIMEOUT_MS;
  rbos_adc_service(&adc);
  assert(!adc.active); /* Completed but abandoned request is reaped too. */
  adc.token = UINT32_MAX;
  assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_IO_ERROR);
  adc.token = 0;
  backend.adc_cancel = NULL;
  assert(rbos_adc_start(&adc, RBOS_ADC_VDD) == RBOS_IO_ERROR);
  puts("PASS: ADC lifecycle boundaries timeout STOP and generation");
}
