#include <app_version.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/logging/log_ctrl.h>

LOG_MODULE_REGISTER(rbos, CONFIG_RBOS_LOG_LEVEL);

int main(void)
{
	LOG_INF("RBOS %s", APP_VERSION_EXTENDED_STRING);
	nrf_gpio_cfg_output(BOARD_PIN_LED_0);
	nrf_gpio_pin_write(BOARD_PIN_LED_0, BOARD_LED_ACTIVE_STATE);

	while (true) {
		log_flush();
		k_busy_wait(1000000);
	}

	return 0;
}
