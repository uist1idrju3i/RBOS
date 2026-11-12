#include <stddef.h>
#include <cmsis_core.h>
#include <nrf_error.h>
#include <nrf_sdm.h>
#include <nrf_soc.h>
#include "backend.h"
#if defined(CONFIG_RBOS_GPIO)
#include "gpio.h"
#include "button.h"
#endif
#if defined(CONFIG_NRFX_SAADC)
#include "adc.h"
#endif

#if !defined(CONFIG_SOFTDEVICE_S115) || !CONFIG_SOFTDEVICE_S115
#error "The temperature backend requires S115"
#endif

static enum rbos_status temperature_read(void *context, int32_t *quarter_celsius)
{
  (void)context;
  if (!quarter_celsius || __get_IPSR() || __get_PRIMASK() ||
      __get_BASEPRI() || __get_FAULTMASK()) return RBOS_IO_ERROR;
  uint8_t enabled = 0;
  if (sd_softdevice_is_enabled(&enabled) != NRF_SUCCESS || !enabled) return RBOS_IO_ERROR;
  int32_t measured;
  if (sd_temp_get(&measured) != NRF_SUCCESS) return RBOS_IO_ERROR;
  *quarter_celsius = measured;
  return RBOS_OK;
}

const struct rbos_backend *rbos_nrf_backend(void)
{
  static const struct rbos_backend backend = {
#if defined(CONFIG_RBOS_GPIO)
    .pin_lookup = rbos_nrf_pin_lookup, .pin_validate = rbos_nrf_pin_validate,
    .gpio_configure = rbos_nrf_gpio_configure, .gpio_read = rbos_nrf_gpio_read,
    .gpio_write = rbos_nrf_gpio_write,
    .button_watch = rbos_nrf_button_watch, .button_unwatch = rbos_nrf_button_unwatch,
    .event_take = rbos_nrf_event_take, .event_stats = rbos_nrf_event_stats,
#endif
    .temperature_read = temperature_read,
#if defined(CONFIG_NRFX_SAADC)
    .uptime_ms = rbos_nrf_uptime_ms, .adc_start = rbos_nrf_adc_start,
    .adc_poll = rbos_nrf_adc_poll, .adc_cancel = rbos_nrf_adc_cancel,
#endif
  };
  return &backend;
}
