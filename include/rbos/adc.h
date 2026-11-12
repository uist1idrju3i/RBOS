#ifndef RBOS_ADC_H
#define RBOS_ADC_H

#include <stdbool.h>
#include "rbos/backend.h"

#define RBOS_ADC_TIMEOUT_MS 100u

struct rbos_adc {
  const struct rbos_backend *backend;
  uint32_t token;
  uint32_t started;
  bool active;
  bool stopping;
  bool ready;
  enum rbos_status status;
  struct rbos_adc_sample sample;
};

enum rbos_status rbos_adc_start(struct rbos_adc *adc, enum rbos_adc_input input);
void rbos_adc_service(struct rbos_adc *adc);
void rbos_adc_cancel(struct rbos_adc *adc, uint32_t token);
enum rbos_status rbos_adc_take(struct rbos_adc *adc, uint32_t token,
                               struct rbos_adc_sample *sample);

#endif
