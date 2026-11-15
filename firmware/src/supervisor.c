#include <zephyr/kernel.h>
#include "runtime.h"
#include "supervisor.h"

static bool enabled;
static bool running;
static int64_t next_poll;

void rbos_supervisor_start(void)
{
	next_poll = k_uptime_get();
	enabled = true;
}

void rbos_supervisor_poll(bool idle)
{
	if (!enabled || running) return;
	int64_t now = k_uptime_get();
	if (now < next_poll) return;
	running = true;
	next_poll = now + CONFIG_RBOS_SERVICE_INTERVAL_MS;
	rbos_maintenance(idle);
	running = false;
}

int __real_mrbc_vm_run(mrbc_vm *vm);

int __wrap_mrbc_vm_run(mrbc_vm *vm)
{
	int result = __real_mrbc_vm_run(vm);
	rbos_supervisor_poll(false);
	return result;
}
