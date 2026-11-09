#include <string.h>
#include <bm/bm_scheduler.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/logging/log_ctrl.h>
#include "runtime.h"

LOG_MODULE_REGISTER(rbos_runtime, CONFIG_RBOS_LOG_LEVEL);
K_THREAD_STACK_DECLARE(z_main_stack, CONFIG_MAIN_STACK_SIZE);
K_KERNEL_STACK_ARRAY_DECLARE(z_interrupt_stacks, CONFIG_MP_MAX_NUM_CPUS, CONFIG_ISR_STACK_SIZE);
static uint8_t *main_painted_end;
static mrbc_tcb *system_task;
static unsigned int pool_max;
static unsigned int idle_count;
static unsigned int service_count;
static int64_t last_stats;

void rbos_stack_paint(void)
{
	uintptr_t sp = __get_PSP();
	uint8_t *base = (uint8_t *)K_THREAD_STACK_BUFFER(z_main_stack);
	/* Leave the current frame and compiler spills untouched. */
	if (sp > (uintptr_t)base + 256) {
		main_painted_end = (uint8_t *)(sp - 256);
		memset(base, 0xaa, main_painted_end - base);
	}
}

static unsigned int stack_used(const uint8_t *base, size_t size, const uint8_t *end)
{
	const uint8_t *p = base;
	while (p < end && *p == 0xaa) ++p;
	return size - (p - base);
}

void rbos_maintenance(bool service)
{
	if (service) ++service_count;
	else ++idle_count;
	bm_scheduler_process();
	for (int i = 0; i < 4; ++i) {
		if (!log_process()) break;
	}
	struct MRBC_ALLOC_STATISTICS pool;
	mrbc_alloc_statistics(&pool);
	if (pool.used > pool_max) pool_max = pool.used;
	int64_t now = k_uptime_get();
	if (now - last_stats < CONFIG_RBOS_STATS_INTERVAL_MS) return;
	last_stats = now;
	struct rbos_tick_stats ticks;
	rbos_tick_take_interval(&ticks);
	const uint8_t *main_base = (uint8_t *)K_THREAD_STACK_BUFFER(z_main_stack);
	const uint8_t *isr_base = (uint8_t *)K_KERNEL_STACK_BUFFER(z_interrupt_stacks[0]);
	unsigned int main_used = stack_used(main_base, CONFIG_MAIN_STACK_SIZE,
		main_painted_end ? main_painted_end : main_base);
	unsigned int isr_used = stack_used(isr_base, CONFIG_ISR_STACK_SIZE,
		isr_base + CONFIG_ISR_STACK_SIZE);
	LOG_INF("stats tick_us=%u..%u catchups=%u ticks=%u pool=%u/%u main=%u isr=%u idle=%u service=%u",
		ticks.min_us, ticks.max_us, ticks.catchups, ticks.count, pool_max, pool.total,
		main_used, isr_used, idle_count, service_count);
}

static void system_service(mrbc_vm *vm, mrbc_value v[], int argc)
{
	if (!system_task || vm != &system_task->vm) {
		mrbc_raise(vm, MRBC_CLASS(RuntimeError), "System task only");
		return;
	}
	if (argc != 0) {
		mrbc_raise(vm, MRBC_CLASS(ArgumentError), "Expected no arguments");
		return;
	}
	rbos_maintenance(true);
	SET_INT_RETURN(CONFIG_RBOS_SERVICE_INTERVAL_MS);
}

void rbos_system_define(void)
{
	mrbc_class *cls = mrbc_define_class(NULL, "RBOSSystem", NULL);
	mrbc_define_method(NULL, cls, "service", system_service);
}

void rbos_system_set_task(mrbc_tcb *task)
{
	system_task = task;
}
