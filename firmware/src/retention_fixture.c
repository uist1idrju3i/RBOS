#include <string.h>
#include <stddef.h>
#include <hal/nrf_gpio.h>
#include <bm/storage/bm_storage.h>
#include <zephyr/devicetree.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <zephyr/sys/crc.h>
#include "rbos_fixture.h"

LOG_MODULE_REGISTER(rbos_retention, CONFIG_RBOS_LOG_LEVEL);
#define STORAGE DT_NODELABEL(storage0_partition)
#define PEER DT_NODELABEL(peer_manager_partition)
BUILD_ASSERT(CONFIG_RBOS_RETENTION_NONCE != 0, "Set a unique nonzero trial nonce in both images");
BUILD_ASSERT(IS_ENABLED(CONFIG_BM_STORAGE_BACKEND_SD), "Fixture requires SoftDevice storage");
BUILD_ASSERT(!IS_ENABLED(CONFIG_SETTINGS) && !IS_ENABLED(CONFIG_BM_ZMS), "Not settings/ZMS retention");
BUILD_ASSERT(DT_REG_SIZE(STORAGE) == 4096 && DT_REG_SIZE(PEER) == 4096, "Review partition layout");
BUILD_ASSERT(!IS_ENABLED(CONFIG_RBOS_SATURATION_FIXTURE), "Run A7 fixtures separately");

static struct bm_storage storage;
static uint32_t sentinel[8] __aligned(16);
static uint32_t peer_before;
static volatile bool pending, completed;
static volatile int result;
static int64_t deadline;
static bool finished;

static uint32_t peer_digest(void)
{
	return crc32_ieee((const uint8_t *)(uintptr_t)DT_REG_ADDR(PEER), DT_REG_SIZE(PEER));
}

static void event_handler(struct bm_storage_evt *event)
{
	if (!pending || event->id != BM_STORAGE_EVT_WRITE_RESULT || event->ctx != &storage ||
	    event->addr != 0 || event->len != sizeof(sentinel)) {
		result = -1;
	} else {
		result = event->result;
	}
	completed = true;
}

static void fail(const char *reason)
{
	LOG_ERR("p5 error=%s", reason);
	finished = true;
}

static bool verify(void)
{
	uint32_t actual[8];
	if (bm_storage_read(&storage, 0, actual, sizeof(actual)) ||
	    memcmp(actual, sentinel, sizeof(actual))) {
		fail("sentinel_missing_or_corrupt");
		return false;
	}
	return true;
}

void rbos_retention_start(void)
{
	struct bm_storage_config config = { .evt_handler = event_handler, .api = &bm_storage_sd_api,
		.addr = DT_REG_ADDR(STORAGE), .size = DT_REG_SIZE(STORAGE) };
	if (bm_storage_init(&storage, &config)) { fail("init"); return; }
	sentinel[0] = 0x52424f53;
	sentinel[1] = 1;
	sentinel[2] = CONFIG_RBOS_RETENTION_NONCE;
	sentinel[3] = 0xa7a7a7a7;
	sentinel[4] = 0x13579bdf;
	sentinel[5] = 0x2468ace0;
	sentinel[6] = 32;
	sentinel[7] = crc32_ieee((const uint8_t *)sentinel, sizeof(sentinel) - sizeof(uint32_t));
	peer_before = peer_digest();
	if (IS_ENABLED(CONFIG_RBOS_RETENTION_SEED)) {
		uint32_t pin = DT_PROP(DT_ALIAS(sw1), pin);
		uint32_t local = pin;
		NRF_GPIO_Type *port = nrf_gpio_pin_port_decode(&local);
		uint32_t saved = port->PIN_CNF[local];
		nrf_gpio_cfg_input(pin, NRF_GPIO_PIN_PULLUP);
		bool seed = nrf_gpio_pin_read(pin) == 0;
		port->PIN_CNF[local] = saved;
		if (!seed) { fail("seed_requires_held_button1"); return; }
		pending = true;
		deadline = k_uptime_get() + 10000;
		if (bm_storage_write(&storage, 0, sentinel, sizeof(sentinel), &storage)) fail("write_submit");
	}
}

void rbos_retention_poll(void)
{
	if (finished) return;
	if (pending) {
		if (!completed) {
			if (k_uptime_get() > deadline) fail("write_timeout");
			return;
		}
		if (result) { fail("write_result"); return; }
		pending = false;
	}
	if (!verify()) return;
	uint32_t peer_after = peer_digest();
	if (peer_before != peer_after) { fail("peer_changed"); return; }
	LOG_INF("p5 mode=%s nonce=%08x sentinel=%08x peer_before=%08x peer_after=%08x verified=1 writes=%u",
		IS_ENABLED(CONFIG_RBOS_RETENTION_SEED) ? "seed" : "verify", CONFIG_RBOS_RETENTION_NONCE,
		sentinel[7], peer_before, peer_after, IS_ENABLED(CONFIG_RBOS_RETENTION_SEED) ? 1 : 0);
	finished = true;
}
