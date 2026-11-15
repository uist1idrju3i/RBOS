#include <errno.h>
#include <stdbool.h>
#include <ble_gap.h>
#include <bm/bluetooth/services/ble_mcumgr.h>
#include <zephyr/mgmt/mcumgr/mgmt/callbacks.h>
#include <zephyr/retention/bootmode.h>
#include <zephyr/sys/reboot.h>
#include "mcumgr_reset.h"

static uint16_t connected_handle = BLE_CONN_HANDLE_INVALID;
static uint16_t reset_handle = BLE_CONN_HANDLE_INVALID;
static bool pending;
static bool notification_sent;
static bool disconnected;
static bool disconnect_requested;

static enum mgmt_cb_return reset_hook(uint32_t event, enum mgmt_cb_return previous,
                                    int32_t *rc, uint16_t *group, bool *abort_more,
                                    void *data, size_t size)
{
	(void)group;
	(void)data;
	(void)size;
	if (event != MGMT_EVT_OP_OS_MGMT_RESET) return MGMT_CB_OK;
	if (previous != MGMT_CB_OK) return previous;
	*abort_more = true;
	if (pending || connected_handle == BLE_CONN_HANDLE_INVALID) {
		*rc = MGMT_ERR_EBUSY;
	} else if (bootmode_set(BOOT_MODE_TYPE_BOOTLOADER)) {
		*rc = MGMT_ERR_EUNKNOWN;
	} else {
		reset_handle = connected_handle;
		pending = true;
		notification_sent = false;
		disconnected = false;
		disconnect_requested = false;
		*rc = MGMT_ERR_EOK;
	}
	return MGMT_CB_ERROR_RC;
}

static struct mgmt_callback reset_callback = {
	.callback = reset_hook,
	.event_id = MGMT_EVT_OP_OS_MGMT_RESET,
};

int rbos_mcumgr_init(void)
{
	struct ble_mcumgr_config config = {
		.sec_mode = BLE_MCUMGR_CONFIG_SEC_MODE_DEFAULT,
	};
	if (ble_mcumgr_init(&config)) return -EIO;
	mgmt_callback_register(&reset_callback);
	return 0;
}

void rbos_mcumgr_connected(uint16_t handle)
{
	connected_handle = handle;
}

void rbos_mcumgr_disconnected(uint16_t handle)
{
	if (handle == connected_handle) connected_handle = BLE_CONN_HANDLE_INVALID;
	if (pending && handle == reset_handle) disconnected = true;
}

void rbos_mcumgr_notification_sent(uint16_t handle)
{
	if (pending && handle == reset_handle) notification_sent = true;
}

void rbos_mcumgr_poll(void)
{
	if (!pending) return;
	if (disconnected) {
		pending = false;
		sys_reboot(SYS_REBOOT_WARM);
		return;
	}
	if (!notification_sent || disconnect_requested) return;
	uint32_t result = sd_ble_gap_disconnect(reset_handle,
		BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION);
	if (result == NRF_SUCCESS) disconnect_requested = true;
}
