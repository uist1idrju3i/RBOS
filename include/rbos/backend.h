#ifndef RBOS_BACKEND_H
#define RBOS_BACKEND_H

#include <stdint.h>

enum rbos_status {
  RBOS_OK,
  RBOS_IO_ERROR,
  RBOS_BUSY,
  RBOS_TIMEOUT,
  RBOS_PENDING,
};

enum rbos_adc_input { RBOS_ADC_DVDD, RBOS_ADC_AVDD, RBOS_ADC_VDD };

struct rbos_adc_sample {
  int32_t raw;
  int32_t full_scale_uv;
  uint8_t bits;
};

struct rbos_backend {
  void *context;
  /* Borrow the output until return, and write it only on RBOS_OK. */
  enum rbos_status (*temperature_read)(void *context, int32_t *quarter_celsius);
  uint32_t (*uptime_ms)(void *context);
  /* A failed start owns no resources. Never retain caller output pointers. */
  enum rbos_status (*adc_start)(void *context, enum rbos_adc_input input, uint32_t token);
  /* PENDING retains DMA ownership; any terminal status guarantees quiescence.
     Only OK writes the output. Calls and cancellation run in foreground. */
  enum rbos_status (*adc_poll)(void *context, uint32_t token, struct rbos_adc_sample *sample);
  /* Nonblocking. Keep polling until STOP is acknowledged; never reuse early. */
  void (*adc_cancel)(void *context, uint32_t token);
};

#endif
