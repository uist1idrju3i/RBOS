from pathlib import Path
import unittest

import test_temperature


ROOT = Path(__file__).resolve().parents[2]


class McumgrResetTests(unittest.TestCase):
    compile_and_run = test_temperature.TemperatureTests.compile_and_run

    def test_open_reset_handoff_notification_disconnect_and_errors(self):
        headers = {
            'mcumgr_reset.h': (ROOT / 'firmware/src/mcumgr_reset.h').read_text(),
            'ble_gap.h': '''#include <stdint.h>
#define BLE_CONN_HANDLE_INVALID 65535
#define BLE_HCI_REMOTE_USER_TERMINATED_CONNECTION 0x13
#define NRF_SUCCESS 0
uint32_t sd_ble_gap_disconnect(uint16_t, uint8_t);
''',
            'bm/bluetooth/services/ble_mcumgr.h': '''
struct ble_mcumgr_config {
  struct {struct {int read, write, cccd_write;} mcumgr_char;} sec_mode;
};
#define BLE_MCUMGR_CONFIG_SEC_MODE_DEFAULT {.mcumgr_char={1,1,1}}
unsigned int ble_mcumgr_init(const struct ble_mcumgr_config *);
''',
            'zephyr/mgmt/mcumgr/mgmt/callbacks.h': '''
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
enum mgmt_cb_return {MGMT_CB_OK, MGMT_CB_ERROR_RC};
enum {MGMT_EVT_OP_OS_MGMT_RESET=1, MGMT_ERR_EOK=0, MGMT_ERR_EUNKNOWN=1, MGMT_ERR_EBUSY=10};
struct mgmt_callback {
  enum mgmt_cb_return (*callback)(uint32_t, enum mgmt_cb_return, int32_t *,
                                 uint16_t *, bool *, void *, size_t);
  uint32_t event_id;
};
void mgmt_callback_register(struct mgmt_callback *);
''',
            'zephyr/retention/bootmode.h': '''
#include <stdint.h>
#define BOOT_MODE_TYPE_BOOTLOADER 1
int bootmode_set(uint8_t);
''',
            'zephyr/sys/reboot.h': '#define SYS_REBOOT_WARM 0\nvoid sys_reboot(int);\n',
        }
        self.compile_and_run(headers, r'''
#include <assert.h>
#include <errno.h>
#include "mcumgr_reset.h"
#include <bm/bluetooth/services/ble_mcumgr.h>
#include <zephyr/mgmt/mcumgr/mgmt/callbacks.h>
#include <zephyr/sys/reboot.h>
static struct mgmt_callback *registered;
static int init_error, boot_error, disconnect_error, boot_writes, disconnects, reboots;
static uint16_t expected_handle;
unsigned int ble_mcumgr_init(const struct ble_mcumgr_config *cfg) {
  assert(cfg->sec_mode.mcumgr_char.read==1);
  assert(cfg->sec_mode.mcumgr_char.write==1);
  assert(cfg->sec_mode.mcumgr_char.cccd_write==1);
  return init_error;
}
void mgmt_callback_register(struct mgmt_callback *cb) {registered=cb;}
int bootmode_set(uint8_t mode) {assert(mode==1); ++boot_writes; return boot_error;}
uint32_t sd_ble_gap_disconnect(uint16_t handle,uint8_t reason) {
  assert(handle==expected_handle && reason==0x13 && boot_writes>0);
  ++disconnects; return disconnect_error;
}
void sys_reboot(int type) {assert(type==SYS_REBOOT_WARM); ++reboots;}
static int request(void) {
  int32_t rc=-1; uint16_t group=0; bool abort_more=false;
  assert(registered->callback(1,MGMT_CB_OK,&rc,&group,&abort_more,NULL,0)==MGMT_CB_ERROR_RC);
  assert(abort_more); return rc;
}
int main(void) {
  init_error=1;
  assert(rbos_mcumgr_init()==-EIO && !registered);
  init_error=0;
  assert(rbos_mcumgr_init()==0 && registered && registered->event_id==1);
  rbos_mcumgr_poll();
  assert(!disconnects && !reboots);
  assert(request()==MGMT_ERR_EBUSY && !boot_writes);
  int32_t rc=123; uint16_t group=0; bool abort_more=false;
  assert(registered->callback(0,MGMT_CB_OK,&rc,&group,&abort_more,NULL,0)==MGMT_CB_OK);
  assert(rc==123 && !abort_more && !boot_writes);
  expected_handle=7;
  rbos_mcumgr_connected(7);
  assert(registered->callback(1,MGMT_CB_ERROR_RC,&rc,&group,&abort_more,NULL,0)==MGMT_CB_ERROR_RC);
  assert(rc==123 && !abort_more && !boot_writes);
  boot_error=-1;
  assert(request()==MGMT_ERR_EUNKNOWN && boot_writes==1);
  rbos_mcumgr_notification_sent(7);
  rbos_mcumgr_poll();
  assert(!disconnects && !reboots);
  boot_error=0;
  assert(request()==0 && boot_writes==2);
  assert(request()==MGMT_ERR_EBUSY && boot_writes==2);
  rbos_mcumgr_poll();
  rbos_mcumgr_notification_sent(8);
  rbos_mcumgr_disconnected(8);
  rbos_mcumgr_poll();
  assert(!disconnects && !reboots);
  rbos_mcumgr_notification_sent(7);
  disconnect_error=1;
  rbos_mcumgr_poll();
  assert(disconnects==1 && !reboots);
  disconnect_error=0;
  rbos_mcumgr_poll();
  assert(disconnects==2 && !reboots);
  rbos_mcumgr_poll();
  assert(disconnects==2 && !reboots);
  rbos_mcumgr_disconnected(7);
  rbos_mcumgr_connected(9);
  rbos_mcumgr_poll();
  assert(reboots==1);
  rbos_mcumgr_poll();
  assert(reboots==1);
  expected_handle=9;
  assert(request()==0);
  rbos_mcumgr_disconnected(9);
  rbos_mcumgr_poll();
  assert(reboots==2 && disconnects==2);
  assert(request()==MGMT_ERR_EBUSY);
}
''', ['firmware/src/mcumgr_reset.c'])
