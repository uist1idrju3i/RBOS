#include <limits.h>
#include <bm/bm_timer.h>
#include <zephyr/kernel.h>
#include <zephyr/fatal.h>
#include <zephyr/logging/log_ctrl.h>
#include <zephyr/sys/printk.h>
#include "mrubyc.h"
#include "runtime.h"

static struct bm_timer tick_timer;
static uint64_t last_ms;
static uint32_t last_cycle;
static struct rbos_tick_stats ticks = { .min_us = UINT_MAX };
static unsigned int irq_depth;
static unsigned int outer_key;
static char line[128];
static size_t line_used;

static void tick_handler(void *context)
{
	ARG_UNUSED(context);
	uint32_t cycle = k_cycle_get_32();
	uint32_t interval = k_cyc_to_us_floor32(cycle - last_cycle);
	last_cycle = cycle;
	if (interval < ticks.min_us) ticks.min_us = interval;
	if (interval > ticks.max_us) ticks.max_us = interval;
	uint64_t now = k_ticks_to_ms_floor64(k_uptime_ticks());
	uint64_t elapsed = now - last_ms;
	if (elapsed > 1) ++ticks.catchups;
	while (last_ms < now) {
		mrbc_tick();
		++last_ms;
	}
}

void rbos_tick_snapshot(struct rbos_tick_stats *stats)
{
	unsigned int key = irq_lock();
	*stats = ticks;
	irq_unlock(key);
}

void mrbc_hal_init(void)
{
	last_ms = k_ticks_to_ms_floor64(k_uptime_ticks());
	last_cycle = k_cycle_get_32();
	if (bm_timer_init(&tick_timer, BM_TIMER_MODE_REPEATED, tick_handler) ||
	    bm_timer_start(&tick_timer, BM_TIMER_MS_TO_TICKS(1), NULL)) {
		mrbc_hal_abort("Cannot start Ruby tick\n");
	}
}

void mrbc_hal_disable_irq(void)
{
	/* BASEPRI 0x40 masks NVIC 2+, leaving SoftDevice priorities 0/1 active. */
	unsigned int key = irq_lock();
	if (irq_depth++ == 0) outer_key = key;
}

void mrbc_hal_enable_irq(void)
{
	if (irq_depth == 0) mrbc_hal_abort("Unbalanced Ruby IRQ unlock\n");
	if (--irq_depth == 0) irq_unlock(outer_key);
}

void mrbc_hal_idle_cpu(void)
{
	rbos_maintenance(false);
	k_cpu_idle();
}

int mrbc_hal_flush(int fd)
{
	ARG_UNUSED(fd);
	if (line_used) {
		printk("%.*s", (int)line_used, line);
		line_used = 0;
	}
	return 0;
}

int mrbc_hal_write(int fd, const void *buf, int nbytes)
{
	if (nbytes < 0 || (nbytes && !buf)) return -1;
	const char *bytes = buf;
	for (int i = 0; i < nbytes; ++i) {
		line[line_used++] = bytes[i];
		if (bytes[i] == '\n' || line_used == sizeof(line)) mrbc_hal_flush(fd);
	}
	return nbytes;
}

_Noreturn void mrbc_hal_abort(const char *message)
{
	mrbc_hal_flush(2);
	printk("RBOS fatal: %s", message ? message : "Ruby abort\n");
	LOG_PANIC();
	k_fatal_halt(K_ERR_KERNEL_PANIC);
	CODE_UNREACHABLE;
}
