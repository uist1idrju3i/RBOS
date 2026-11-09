#include <string.h>
#include <bm/bluetooth/ble_adv.h>
#include <bm/softdevice_handler/nrf_sdh.h>
#include <bm/softdevice_handler/nrf_sdh_ble.h>
#include <zephyr/logging/log.h>
#include "runtime.h"

LOG_MODULE_REGISTER(rbos_ble, CONFIG_RBOS_LOG_LEVEL);
BLE_ADV_DEF(advertising);

static void on_ble_event(const ble_evt_t *evt, void *context)
{
	ARG_UNUSED(context);
	if (evt->header.evt_id == BLE_GAP_EVT_CONNECTED) LOG_INF("BLE connected");
	if (evt->header.evt_id == BLE_GAP_EVT_DISCONNECTED) LOG_INF("BLE disconnected");
}
NRF_SDH_BLE_OBSERVER(rbos_ble, on_ble_event, NULL, USER_LOW);

static void on_adv_event(struct ble_adv *adv, const struct ble_adv_evt *evt)
{
	ARG_UNUSED(adv);
	if (evt->evt_type == BLE_ADV_EVT_ERROR) LOG_ERR("Advertising error %#x", evt->error.reason);
}

int rbos_ble_init(void)
{
	int err = nrf_sdh_enable_request();
	if (err) return err;
	err = nrf_sdh_ble_enable(CONFIG_NRF_SDH_BLE_CONN_TAG);
	if (err) return err;
	ble_gap_conn_sec_mode_t security;
	BLE_GAP_CONN_SEC_MODE_SET_NO_ACCESS(&security);
	uint32_t result = sd_ble_gap_device_name_set(&security, "RBOS", 4);
	if (result) return -EIO;
	struct ble_adv_config config = {
		.conn_cfg_tag = CONFIG_NRF_SDH_BLE_CONN_TAG,
		.evt_handler = on_adv_event,
		.adv_data = {
			.name_type = BLE_ADV_DATA_FULL_NAME,
			.flags = BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE,
		},
	};
	result = ble_adv_init(&advertising, &config);
	if (result) return -EIO;
	result = ble_adv_start(&advertising, BLE_ADV_MODE_FAST);
	return result ? -EIO : 0;
}
