#include <app_version.h>
#include <board-config.h>
#include <hal/nrf_gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/logging/log_ctrl.h>
#include "mrubyc.h"
#include "rbos/bindings.h"
#include "embedded.h"
#include "runtime.h"

LOG_MODULE_REGISTER(rbos, CONFIG_RBOS_LOG_LEVEL);
static uint8_t vm_pool[CONFIG_RBOS_VM_POOL_SIZE] __aligned(8);
static const struct rbos_backend backend;

int main(void)
{
	rbos_stack_paint();
	LOG_INF("RBOS %s", APP_VERSION_EXTENDED_STRING);
	nrf_gpio_cfg_output(BOARD_PIN_LED_0);
	nrf_gpio_pin_write(BOARD_PIN_LED_0, BOARD_LED_ACTIVE_STATE);

	if (rbos_ble_init()) mrbc_hal_abort("BLE initialization failed\n");
	rbos_resources_log();
	mrbc_init(vm_pool, sizeof(vm_pool));
	rbos_define_classes(&backend);
	rbos_system_define();
	for (unsigned int i = 0; i < rbos_task_count; ++i) {
		mrbc_tcb *task = mrbc_create_task(rbos_tasks[i].bytecode, NULL);
		if (!task) mrbc_hal_abort("Cannot create embedded task\n");
		mrbc_set_task_name(task, rbos_tasks[i].name);
		if (i == 0) {
			rbos_system_set_task(task);
			/* rrt0 sorts lower numeric priorities first (rrt0.c:q_insert_task). */
			mrbc_change_priority(task, 0);
		}
	}
	int status = mrbc_run();
	LOG_ERR("Ruby scheduler returned %d", status);
	mrbc_hal_abort("Ruby scheduler stopped\n");
}
