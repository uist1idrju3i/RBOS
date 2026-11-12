#ifndef RBOS_NRF_GPIO_H
#define RBOS_NRF_GPIO_H
#include "rbos/backend.h"
enum rbos_status rbos_nrf_pin_lookup(void *, const char *, uint32_t *);
enum rbos_status rbos_nrf_pin_validate(void *, uint32_t);
enum rbos_status rbos_nrf_gpio_configure(void *, uint32_t, uint32_t);
enum rbos_status rbos_nrf_gpio_read(void *, uint32_t, uint32_t *);
enum rbos_status rbos_nrf_gpio_write(void *, uint32_t, uint32_t);
#endif
