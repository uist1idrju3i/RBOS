#ifndef RBOS_BACKEND_H
#define RBOS_BACKEND_H

#include <stdint.h>
#include "rbos/event_queue.h"

enum rbos_status {
  RBOS_OK,
  RBOS_IO_ERROR,
  RBOS_BUSY,
  RBOS_TIMEOUT,
  RBOS_PENDING,
  RBOS_INVALID_PIN,
  RBOS_RESERVED_PIN,
  RBOS_UNSUPPORTED,
};

enum rbos_adc_input { RBOS_ADC_DVDD, RBOS_ADC_AVDD, RBOS_ADC_VDD };

struct rbos_adc_sample {
  int32_t raw;
  int32_t full_scale_uv;
  uint8_t bits;
};

struct rbos_backend {
  void *context;
  /* Lookup and validation do not configure or access GPIO registers. */
  enum rbos_status (*pin_lookup)(void *context, const char *label, uint32_t *pin);
  enum rbos_status (*pin_validate)(void *context, uint32_t pin);
  enum rbos_status (*gpio_configure)(void *context, uint32_t pin, uint32_t mode);
  enum rbos_status (*gpio_read)(void *context, uint32_t pin, uint32_t *level);
  enum rbos_status (*gpio_write)(void *context, uint32_t pin, uint32_t level);
  /* Watch/unwatch are synchronous and IRQ-serialized. Failed watch owns nothing;
     successful unwatch guarantees no further producer for this generation. */
  enum rbos_status (*button_watch)(void *context, uint32_t pin, uint32_t generation);
  enum rbos_status (*button_unwatch)(void *context, uint32_t pin, uint32_t generation);
  bool (*event_take)(void *context, struct rbos_event *event);
  void (*event_stats)(void *context, struct rbos_event_stats *stats);
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
