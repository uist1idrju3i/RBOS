#include <errno.h>
#include <hal/nrf_gpio.h>
#include <nrfx_timer.h>
#include <helpers/nrfx_gppi.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include "runtime.h"
#include "rbos_fixture.h"

LOG_MODULE_REGISTER(rbos_saturation, CONFIG_RBOS_LOG_LEVEL);
BUILD_ASSERT(RBOS_FIXTURE_PIN == NRF_GPIO_PIN_MAP(1, 11), "Review fixture pin before changing it");
BUILD_ASSERT(!IS_ENABLED(CONFIG_RBOS_PERIPHERAL_EXERCISE), "Fixture owns sw0 subscription");
BUILD_ASSERT(!IS_ENABLED(CONFIG_RBOS_RETENTION_FIXTURE), "Run A7 fixtures separately");

static nrfx_timer_t timer = NRFX_TIMER_INSTANCE(NRF_TIMER21);
static nrfx_gppi_handle_t connection;
static uint32_t output_task;
static bool connected, timer_initialized, holding, started, pulse, waiting, finished;
static uint32_t source, token, phase, generated, initial_level;
static volatile uint32_t interrupts, measured, accepted, latest;
static int64_t deadline;
static struct rbos_event_stats before;
static const char *const phases[] = { "coalesce", "drop", "full" };

void rbos_fixture_disconnect(void)
{
	if (connected) {
		nrfx_gppi_conn_disable(connection);
		nrfx_gppi_conn_free(nrfx_timer_compare_event_address_get(&timer, NRF_TIMER_CC_CHANNEL0),
			output_task, connection);
		connected = false;
	}
	if (timer_initialized) {
		nrfx_timer_uninit(&timer);
		timer_initialized = false;
	}
	holding = false;
	finished = true;
}

static void fail(const char *reason)
{
	LOG_ERR("a7 error=%s", reason);
	rbos_fixture_disconnect();
}

int rbos_fixture_connect(uint32_t task_address)
{
	if (timer_initialized || finished) return -EBUSY;
	nrfx_timer_config_t config = NRFX_TIMER_DEFAULT_CONFIG(NRF_TIMER_BASE_FREQUENCY_GET(timer.p_reg));
	config.bit_width = NRF_TIMER_BIT_WIDTH_32;
	int result = nrfx_timer_init(&timer, &config, NULL);
	if (result) return result;
	timer_initialized = true;
	nrfx_timer_extended_compare(&timer, NRF_TIMER_CC_CHANNEL0, nrfx_timer_us_to_ticks(&timer, 1000),
		NRF_TIMER_SHORT_COMPARE0_STOP_MASK, false);
	result = nrfx_gppi_conn_alloc(nrfx_timer_compare_event_address_get(&timer, NRF_TIMER_CC_CHANNEL0),
		task_address, &connection);
	if (result) {
		rbos_fixture_disconnect();
		return result;
	}
	connected = true;
	output_task = task_address;
	nrfx_gppi_conn_enable(connection);
	return 0;
}

void rbos_fixture_begin(uint32_t pin, uint32_t generation)
{
	source = pin;
	token = generation;
	started = true;
	LOG_INF("a7 setup pin=%u timer=21 path=port capacity=%u", pin, RBOS_EVENT_QUEUE_CAPACITY);
}

void rbos_fixture_edge(uint32_t pin, uint32_t level, bool was_accepted)
{
	if (!started || finished || pin != source) return;
	++measured;
	accepted += was_accepted;
	latest = level;
}

void rbos_fixture_irq(void)
{
	if (started && !finished) ++interrupts;
}

bool rbos_fixture_holds_events(void)
{
	return holding;
}

static bool fill(uint32_t count)
{
	for (uint32_t i = 0; i < count; ++i) {
		struct rbos_event event = { .type = RBOS_EVENT_COMPLETION,
			.source = i, .value = 0xa7, .generation = token };
		if (!rbos_event_post(&event)) return false;
	}
	return true;
}

static void launch(void)
{
	nrf_timer_event_clear(timer.p_reg, NRF_TIMER_EVENT_COMPARE0);
	nrfx_timer_clear(&timer);
	pulse = true;
	deadline = k_uptime_get() + 1000;
	nrfx_timer_enable(&timer);
}

static void next_phase(void)
{
	++phase;
	generated = interrupts = measured = accepted = 0;
	waiting = false;
	if (phase == ARRAY_SIZE(phases)) {
		LOG_INF("a7 done phases=3");
		rbos_fixture_disconnect();
	}
}

void rbos_fixture_delivery(uint32_t pin, uint32_t level, uint32_t count)
{
	if (pin != source || !started || finished) return;
	struct rbos_event_stats stats;
	rbos_event_snapshot(&stats);
	if (!waiting || phase == 1 || interrupts != 5 || count != 5 || level != latest || stats.pending) {
		fail("delivery");
		return;
	}
	LOG_INF("a7 delivery phase=%s via=ruby level=%u count=%u pending=%u",
		phases[phase], level, count, stats.pending);
	next_phase();
}

static void complete(void)
{
	struct rbos_event_stats after;
	rbos_event_snapshot(&after);
	if (interrupts != 5 || measured != 5 || accepted != (phase == 1 ? 0 : 5) || latest != (initial_level ^ 1u) ||
	    nrf_gpio_pin_read(source) != latest ||
	    after.pending != (phase == 0 ? 1 : RBOS_EVENT_QUEUE_CAPACITY) ||
	    after.overflow - before.overflow != (phase == 1 ? 5 : 0) ||
	    after.coalesced - before.coalesced != (phase == 1 ? 0 : 4)) {
		fail("counters");
		return;
	}
	LOG_INF("a7 phase=%s generated=%u irq=%u accepted=%u before_pending=%u after_pending=%u before_overflow=%u after_overflow=%u before_coalesced=%u after_coalesced=%u initial_level=%u final_level=%u",
		phases[phase], generated, interrupts, accepted, before.pending, after.pending,
		before.overflow, after.overflow, before.coalesced, after.coalesced, initial_level, latest);
	holding = false;
	if (phase == 1) {
		struct rbos_event event;
		for (uint32_t i = 0; i < RBOS_EVENT_QUEUE_CAPACITY; ++i) {
			if (!rbos_event_take(&event) || event.type != RBOS_EVENT_COMPLETION ||
			    event.source != i || event.generation != token || event.value != 0xa7 || event.count != 1) {
				fail("newest_drop_fifo");
				return;
			}
		}
		if (rbos_event_take(&event)) { fail("extra_event"); return; }
		LOG_INF("a7 delivery phase=drop via=none level=%u count=0 pending=0", latest);
		next_phase();
	} else {
		waiting = true;
		deadline = k_uptime_get() + 1000;
	}
}

void rbos_fixture_poll(void)
{
	if (!started || finished) return;
	if (waiting) {
		if (k_uptime_get() > deadline) fail("delivery_timeout");
		return;
	}
	if (!holding) {
		rbos_event_snapshot(&before);
		if (before.pending) { fail("not_empty"); return; }
		holding = true;
		initial_level = nrf_gpio_pin_read(source);
		if (phase == 1) {
			if (!fill(RBOS_EVENT_QUEUE_CAPACITY)) { fail("prefill"); return; }
			rbos_event_snapshot(&before);
		}
		launch();
		return;
	}
	if (pulse && nrf_timer_event_check(timer.p_reg, NRF_TIMER_EVENT_COMPARE0)) {
		nrf_timer_event_clear(timer.p_reg, NRF_TIMER_EVENT_COMPARE0);
		nrfx_timer_disable(&timer);
		++generated;
		pulse = false;
	}
	if (k_uptime_get() > deadline || measured > generated) { fail("irq_timeout_or_extra"); return; }
	if (pulse || measured != generated) return;
	if (phase == 2 && generated == 1) {
		if (!fill(RBOS_EVENT_QUEUE_CAPACITY - 1)) { fail("prefill"); return; }
		rbos_event_snapshot(&before);
	}
	if (generated == 5) complete();
	else launch();
}
