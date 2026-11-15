#include <zephyr/kernel.h>
#include "runtime.h"
#include "supervisor.h"
#include "rbos/watchdog.h"

static bool enabled;
static bool running;
static int64_t next_poll;
#if CONFIG_RBOS_WDT
static int64_t last_feed;
#endif

int rbos_supervisor_start(void)
{
	enabled = false;
#if CONFIG_RBOS_WDT
	int result = rbos_wdt_start();
	if (result) return result;
	last_feed = k_uptime_get();
#endif
	next_poll = k_uptime_get();
	enabled = true;
	return 0;
}

void rbos_supervisor_poll(bool idle)
{
	if (!enabled || running) return;
	int64_t now = k_uptime_get();
	if (now < next_poll) return;
	running = true;
	next_poll = now + CONFIG_RBOS_SERVICE_INTERVAL_MS;
#if CONFIG_RBOS_FAULT_WDT
	while (1) { k_cpu_idle(); }
#endif
	rbos_maintenance(idle);
#if CONFIG_RBOS_WDT
	int64_t completed = k_uptime_get();
	if (completed >= last_feed && completed - last_feed < CONFIG_RBOS_WDT_TIMEOUT_MS) {
		rbos_wdt_feed();
		last_feed = completed;
	}
#endif
	running = false;
}

int __real_mrbc_vm_run(mrbc_vm *vm);

int __wrap_mrbc_vm_run(mrbc_vm *vm)
{
	int result = __real_mrbc_vm_run(vm);
	rbos_supervisor_poll(false);
	return result;
}
