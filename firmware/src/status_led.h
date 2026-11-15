#ifndef RBOS_STATUS_LED_H
#define RBOS_STATUS_LED_H

#include <stdbool.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>

static inline void rbos_status_led(bool active)
{
	nrf_gpio_cfg_output(BOARD_PIN_LED_0);
	nrf_gpio_pin_write(BOARD_PIN_LED_0, active ? BOARD_LED_ACTIVE_STATE : !BOARD_LED_ACTIVE_STATE);
}

#endif
