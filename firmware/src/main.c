#include <app_version.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/logging/log_ctrl.h>
#include "mrubyc.h"
#include "rbos/bindings.h"
#include "backend.h"
#include "embedded.h"
#include "runtime.h"
#include "supervisor.h"

LOG_MODULE_REGISTER(rbos, CONFIG_RBOS_LOG_LEVEL);
static uint8_t vm_pool[CONFIG_RBOS_VM_POOL_SIZE] __aligned(8);

int main(void)
{
	rbos_stack_paint();
	LOG_INF("RBOS %s", APP_VERSION_EXTENDED_STRING);
	nrf_gpio_cfg_output(BOARD_PIN_LED_0);
	nrf_gpio_pin_write(BOARD_PIN_LED_0, BOARD_LED_ACTIVE_STATE);

	if (rbos_resources_probe()) mrbc_hal_abort("BM scheduler capacity probe failed\n");
	if (rbos_ble_init()) mrbc_hal_abort("BLE initialization failed\n");
	rbos_resources_log();
	mrbc_init(vm_pool, sizeof(vm_pool));
	rbos_define_classes(rbos_nrf_backend());
	for (unsigned int i = 0; i < rbos_task_count; ++i) {
		mrbc_tcb *task = mrbc_create_task(rbos_tasks[i].bytecode, NULL);
		if (!task) mrbc_hal_abort("Cannot create embedded task\n");
		mrbc_set_task_name(task, rbos_tasks[i].name);
	}
	rbos_supervisor_start();
	int status = mrbc_run();
	LOG_INF("Ruby scheduler returned %d; native supervisor continues", status);
	while (1) {
		rbos_supervisor_poll(true);
		k_cpu_idle();
	}
}
