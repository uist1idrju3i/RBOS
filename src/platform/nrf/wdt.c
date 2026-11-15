#include <errno.h>
#include <nrfx_wdt.h>
#include <hal/nrf_reset.h>
#include <zephyr/logging/log.h>
#include "rbos/watchdog.h"

LOG_MODULE_REGISTER(rbos_wdt, CONFIG_RBOS_LOG_LEVEL);

static nrfx_wdt_t watchdog = NRFX_WDT_INSTANCE(NRF_WDT30);
static nrfx_wdt_channel_id channel;
static bool started;

int rbos_wdt_start(void)
{
	if (nrf_wdt_started_check(watchdog.p_reg)) return -EBUSY;
	nrfx_wdt_config_t config = NRFX_WDT_DEFAULT_CONFIG;
	config.reload_value = CONFIG_RBOS_WDT_TIMEOUT_MS;
#if !CONFIG_RBOS_FATAL_REBOOT
	BUILD_ASSERT(NRFX_WDT_HAS_STOP, "Debug fatal halt requires a stoppable watchdog");
	config.behaviour |= NRF_WDT_BEHAVIOUR_STOP_ENABLE_MASK;
#endif
	int result = nrfx_wdt_init(&watchdog, &config, NULL, NULL);
	if (result) return result;
	result = nrfx_wdt_channel_alloc(&watchdog, &channel);
	if (result) return result;
	nrfx_wdt_enable(&watchdog);
	started = true;
	return 0;
}

void rbos_wdt_feed(void)
{
	if (started) nrfx_wdt_channel_feed(&watchdog, channel);
}

void rbos_wdt_stop(void)
{
#if !CONFIG_RBOS_FATAL_REBOOT
	if (started) {
		(void)nrfx_wdt_stop(&watchdog);
		started = false;
	}
#endif
}

void rbos_reset_reason_log(void)
{
	uint32_t reason = nrf_reset_resetreas_get(NRF_RESET);
	LOG_INF("reset reason=0x%08x", (unsigned int)reason);
	nrf_reset_resetreas_clear(NRF_RESET, reason);
}
