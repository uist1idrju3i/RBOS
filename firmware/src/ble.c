#include <string.h>
#include <ble_gatts.h>
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
	uint32_t result = NRF_SUCCESS;
	switch (evt->header.evt_id) {
	case BLE_GAP_EVT_CONNECTED:
		LOG_INF("BLE connected");
		break;
	case BLE_GAP_EVT_DISCONNECTED:
		LOG_INF("BLE disconnected reason=0x%02x", evt->evt.gap_evt.params.disconnected.reason);
		break;
	case BLE_GAP_EVT_PHY_UPDATE_REQUEST:
		LOG_INF("BLE PHY request tx=0x%02x rx=0x%02x",
			evt->evt.gap_evt.params.phy_update_request.peer_preferred_phys.tx_phys,
			evt->evt.gap_evt.params.phy_update_request.peer_preferred_phys.rx_phys);
		break;
	case BLE_GAP_EVT_PHY_UPDATE:
		LOG_INF("BLE PHY update status=0x%02x", evt->evt.gap_evt.params.phy_update.status);
		break;
	case BLE_GAP_EVT_DATA_LENGTH_UPDATE_REQUEST:
		LOG_INF("BLE data length request tx=%u rx=%u",
			evt->evt.gap_evt.params.data_length_update_request.peer_params.max_tx_octets,
			evt->evt.gap_evt.params.data_length_update_request.peer_params.max_rx_octets);
		break;
	case BLE_GAP_EVT_DATA_LENGTH_UPDATE:
		LOG_INF("BLE data length updated tx=%u rx=%u",
			evt->evt.gap_evt.params.data_length_update.effective_params.max_tx_octets,
			evt->evt.gap_evt.params.data_length_update.effective_params.max_rx_octets);
		break;
	case BLE_GATTS_EVT_EXCHANGE_MTU_REQUEST:
		LOG_INF("BLE ATT MTU request rx=%u", evt->evt.gatts_evt.params.exchange_mtu_request.client_rx_mtu);
		break;
	case BLE_GATTS_EVT_SYS_ATTR_MISSING:
		LOG_INF("BLE system attributes missing");
		result = sd_ble_gatts_sys_attr_set(evt->evt.gatts_evt.conn_handle, NULL, 0, 0);
		break;
	case BLE_GAP_EVT_SEC_PARAMS_REQUEST:
		LOG_INF("BLE security parameters requested; pairing unsupported");
		result = sd_ble_gap_sec_params_reply(evt->evt.gap_evt.conn_handle,
			BLE_GAP_SEC_STATUS_PAIRING_NOT_SUPP, NULL, NULL);
		break;
	case BLE_GAP_EVT_SEC_INFO_REQUEST:
		LOG_INF("BLE security information requested; no stored bond");
		result = sd_ble_gap_sec_info_reply(evt->evt.gap_evt.conn_handle, NULL);
		break;
	case BLE_GATTS_EVT_TIMEOUT:
		LOG_INF("BLE GATTS timeout source=%u", evt->evt.gatts_evt.params.timeout.src);
		break;
	default:
		break;
	}
	if (result) LOG_ERR("BLE reply event=0x%04x error=%#x", evt->header.evt_id, result);
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
