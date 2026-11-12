#include <limits.h>
#include "rbos/adc.h"

enum rbos_status rbos_adc_start(struct rbos_adc *adc, enum rbos_adc_input input)
{
  if (input < RBOS_ADC_DVDD || input > RBOS_ADC_VDD) return RBOS_IO_ERROR;
  if (adc->active) return RBOS_BUSY;
  const struct rbos_backend *b = adc->backend;
  if (!b || !b->uptime_ms || !b->adc_start || !b->adc_poll || !b->adc_cancel ||
      adc->token == UINT32_MAX) return RBOS_IO_ERROR;
  ++adc->token;
  adc->started = b->uptime_ms(b->context);
  enum rbos_status status = b->adc_start(b->context, input, adc->token);
  if (status != RBOS_OK) return status == RBOS_PENDING ? RBOS_IO_ERROR : status;
  adc->active = true;
  adc->ready = false;
  adc->stopping = false;
  adc->status = RBOS_PENDING;
  return RBOS_OK;
}

void rbos_adc_cancel(struct rbos_adc *adc, uint32_t token)
{
  if (!adc->active || token != adc->token || adc->stopping) return;
  if (adc->ready) {
    adc->active = false;
    return;
  }
  adc->stopping = true;
  adc->status = RBOS_TIMEOUT;
  adc->backend->adc_cancel(adc->backend->context, token);
}

void rbos_adc_service(struct rbos_adc *adc)
{
  if (!adc->active) return;
  const struct rbos_backend *b = adc->backend;
  if ((uint32_t)(b->uptime_ms(b->context) - adc->started) >= RBOS_ADC_TIMEOUT_MS)
    rbos_adc_cancel(adc, adc->token);
  if (!adc->active || adc->ready) return;
  struct rbos_adc_sample sample;
  enum rbos_status status = b->adc_poll(b->context, adc->token, &sample);
  if (status == RBOS_PENDING) return;
  if (adc->stopping) {
    adc->active = false;
    return;
  }
  if (status == RBOS_OK) {
    if (sample.raw < INT16_MIN || sample.raw > INT16_MAX ||
        sample.full_scale_uv <= 0 || sample.bits < 8 || sample.bits > 16)
      status = RBOS_IO_ERROR;
    else adc->sample = sample;
  }
  adc->status = status;
  adc->ready = true;
}

enum rbos_status rbos_adc_take(struct rbos_adc *adc, uint32_t token,
                               struct rbos_adc_sample *sample)
{
  if (!sample || !adc->active || token != adc->token) return RBOS_IO_ERROR;
  if (adc->stopping) return RBOS_TIMEOUT;
  if (!adc->ready) return RBOS_PENDING;
  adc->active = false;
  if (adc->status == RBOS_OK) *sample = adc->sample;
  return adc->status;
}
