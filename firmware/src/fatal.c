#include <bm/bm_timer.h>
#include <zephyr/kernel.h>
#include <zephyr/fatal.h>
#include <zephyr/logging/log_ctrl.h>
#include <zephyr/sys/printk.h>
#include <zephyr/sys/reboot.h>
#include "mrubyc.h"
#include "rbos/watchdog.h"
#include "status_led.h"

#if CONFIG_RBOS_FATAL_REBOOT
static struct bm_timer fatal_deadline;

static void fatal_reboot(void *context)
{
	ARG_UNUSED(context);
	sys_reboot(SYS_REBOOT_COLD);
}
#endif

_Noreturn void mrbc_hal_abort(const char *message)
{
	rbos_status_led(true);
#if CONFIG_RBOS_FATAL_REBOOT
	if (bm_timer_init(&fatal_deadline, BM_TIMER_MODE_SINGLE_SHOT, fatal_reboot) ||
	    bm_timer_start(&fatal_deadline, BM_TIMER_MS_TO_TICKS(CONFIG_RBOS_FATAL_FLUSH_MS), NULL))
		sys_reboot(SYS_REBOOT_COLD);
#else
	rbos_wdt_stop();
#endif
	mrbc_hal_flush(2);
	printk("RBOS fatal: %s", message ? message : "Ruby abort\n");
	LOG_PANIC();
#if CONFIG_RBOS_FATAL_REBOOT
	sys_reboot(SYS_REBOOT_COLD);
#else
	k_fatal_halt(K_ERR_KERNEL_PANIC);
#endif
	CODE_UNREACHABLE;
}
