#include <stddef.h>
#include <cmsis_core.h>
#include <nrf_error.h>
#include <nrf_sdm.h>
#include <nrf_soc.h>
#include "backend.h"

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
  static const struct rbos_backend backend = { .temperature_read = temperature_read };
  return &backend;
}
