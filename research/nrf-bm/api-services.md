# Bluetooth servicesの公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `ble_bas.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_bas.h:1-227`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_bas_battery_level_update`、`ble_bas_init` |
| struct・enum・typedef・callback | `battery_lvl_char`、`battery_report_ref`、`ble_bas`、`ble_bas_config`、`ble_bas_evt`、`ble_bas_evt_handler_t`、`ble_bas_evt_type`、`error`、`sec_mode` |
| enum 値・event 定数 | `BLE_BAS_EVT_ERROR`、`BLE_BAS_EVT_NOTIFICATION_DISABLED`、`BLE_BAS_EVT_NOTIFICATION_ENABLED` |
| 定義 macro | `BLE_BAS_BATTERY_LEVEL_LAST`、`BLE_BAS_CONFIG_SEC_MODE_DEFAULT`、`BLE_BAS_DEF` |

## `ble_bas_client.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_bas_client.h:1-264`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_bas_client_bl_notif_disable`、`ble_bas_client_bl_notif_enable`、`ble_bas_client_bl_read`、`ble_bas_client_handles_assign`、`ble_bas_client_init`、`ble_bas_client_on_ble_evt`、`ble_bas_on_db_disc_evt` |
| struct・enum・typedef・callback | `battery`、`ble_bas_client`、`ble_bas_client_config`、`ble_bas_client_evt`、`ble_bas_client_evt_handler_t`、`ble_bas_client_evt_type`、`ble_bas_client_handles`、`discovery_complete`、`error` |
| enum 値・event 定数 | `BLE_BAS_CLIENT_EVT_BATT_NOTIFICATION`、`BLE_BAS_CLIENT_EVT_BATT_READ_RESP`、`BLE_BAS_CLIENT_EVT_DISCOVERY_COMPLETE`、`BLE_BAS_CLIENT_EVT_ERROR` |
| 定義 macro | `BLE_BAS_CLIENT_DEF` |

## `ble_bms.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_bms.h:1-350`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_bms_auth_response`、`ble_bms_init`、`ble_bms_on_ble_evt`、`ble_bms_on_qwr_evt` |
| struct・enum・typedef・callback | `auth`、`ble_bms`、`ble_bms_auth_code`、`ble_bms_auth_status`、`ble_bms_config`、`ble_bms_ctrlpt`、`ble_bms_evt`、`ble_bms_evt_handler_t`、`ble_bms_evt_type`、`ble_bms_features`、`ble_bms_op`、`ctrlpt_char`、`error`、`feature_char`、`sec_mode` |
| enum 値・event 定数 | `BLE_BMS_AUTH_STATUS_ALLOWED`、`BLE_BMS_AUTH_STATUS_DENIED`、`BLE_BMS_AUTH_STATUS_PENDING`、`BLE_BMS_EVT_AUTH`、`BLE_BMS_EVT_BOND_DELETE_ALL`、`BLE_BMS_EVT_BOND_DELETE_ALL_EXCEPT_REQUESTING`、`BLE_BMS_EVT_BOND_DELETE_REQUESTING`、`BLE_BMS_EVT_ERROR`、`BLE_BMS_OP_DEL_ALL_BONDS_ON_SERVER_BR_LE`、`BLE_BMS_OP_DEL_ALL_BONDS_ON_SERVER_BR_ONLY`、`BLE_BMS_OP_DEL_ALL_BONDS_ON_SERVER_LE_ONLY`、`BLE_BMS_OP_DEL_ALL_BUT_ACTIVE_BOND_BR_LE`、`BLE_BMS_OP_DEL_ALL_BUT_ACTIVE_BOND_BR_ONLY`、`BLE_BMS_OP_DEL_ALL_BUT_ACTIVE_BOND_LE_ONLY`、`BLE_BMS_OP_DEL_BOND_REQ_DEVICE_BR_LE`、`BLE_BMS_OP_DEL_BOND_REQ_DEVICE_BR_ONLY`、`BLE_BMS_OP_DEL_BOND_REQ_DEVICE_LE_ONLY`、`BLE_BMS_OP_NONE` |
| 定義 macro | `BLE_BMS_ALL_BONDS_BR`、`BLE_BMS_ALL_BONDS_BR_AUTH_CODE`、`BLE_BMS_ALL_BONDS_BR_LE`、`BLE_BMS_ALL_BONDS_BR_LE_AUTH_CODE`、`BLE_BMS_ALL_BONDS_LE`、`BLE_BMS_ALL_BONDS_LE_AUTH_CODE`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_BR`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_BR_AUTH_CODE`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_BR_LE`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_BR_LE_AUTH_CODE`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_LE`、`BLE_BMS_ALL_EXCEPT_REQUESTING_DEVICE_LE_AUTH_CODE`、`BLE_BMS_AUTH_CODE_MAX_LEN`、`BLE_BMS_CONFIG_SEC_MODE_DEFAULT`、`BLE_BMS_CTRLPT_MAX_LEN`、`BLE_BMS_DEF`、`BLE_BMS_OPCODE_NOT_SUPPORTED`、`BLE_BMS_OPERATION_FAILED`、`BLE_BMS_REQUESTING_DEVICE_BR`、`BLE_BMS_REQUESTING_DEVICE_BR_AUTH_CODE`、`BLE_BMS_REQUESTING_DEVICE_BR_LE`、`BLE_BMS_REQUESTING_DEVICE_BR_LE_AUTH_CODE`、`BLE_BMS_REQUESTING_DEVICE_LE`、`BLE_BMS_REQUESTING_DEVICE_LE_AUTH_CODE` |

## `ble_cgms.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_cgms.h:1-661`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_cgms_conn_handle_assign`、`ble_cgms_init`、`ble_cgms_meas_create`、`ble_cgms_on_ble_evt`、`ble_cgms_srt_set`、`ble_cgms_update_status` |
| struct・enum・typedef・callback | `ble_cgms`、`ble_cgms_calib`、`ble_cgms_char_handles`、`ble_cgms_config`、`ble_cgms_evt`、`ble_cgms_evt_handler_t`、`ble_cgms_evt_type`、`ble_cgms_feature`、`ble_cgms_meas`、`ble_cgms_racp`、`ble_cgms_rec`、`ble_cgms_sensor_annunc`、`ble_cgms_status`、`ble_socp_rsp`、`error`、`feature_char`、`meas_char`、`racp_char`、`sec_mode`、`socp_char`、`srt_char`、`sst_char`、`status_char` |
| enum 値・event 定数 | `BLE_CGMS_EVT_ERROR`、`BLE_CGMS_EVT_NOTIFICATION_DISABLED`、`BLE_CGMS_EVT_NOTIFICATION_ENABLED`、`BLE_CGMS_EVT_START_SESSION`、`BLE_CGMS_EVT_STOP_SESSION`、`BLE_CGMS_EVT_WRITE_COMM_INTERVAL` |
| 定義 macro | `BLE_CGMS_CALIBS_NB_MAX`、`BLE_CGMS_CONFIG_SEC_MODE_DEFAULT`、`BLE_CGMS_CRC_LEN`、`BLE_CGMS_DATA_MAX_LEN_CALC`、`BLE_CGMS_DEF`、`BLE_CGMS_FEATURE_LEN`、`BLE_CGMS_FEAT_CALIBRATION_SUPPORTED`、`BLE_CGMS_FEAT_CGM_QUALITY_SUPPORTED`、`BLE_CGMS_FEAT_CGM_TREND_INFORMATION_SUPPORTED`、`BLE_CGMS_FEAT_DEVICE_SPECIFIC_ALERT_SUPPORTED`、`BLE_CGMS_FEAT_E2E_CRC_SUPPORTED`、`BLE_CGMS_FEAT_GENERAL_DEVICE_FAULT_SUPPORTED`、`BLE_CGMS_FEAT_HYPER_ALERTS_SUPPORTED`、`BLE_CGMS_FEAT_HYPO_ALERTS_SUPPORTED`、`BLE_CGMS_FEAT_LOW_BATTERY_DETECTION_SUPPORTED`、`BLE_CGMS_FEAT_MULTIPLE_BOND_SUPPORTED`、`BLE_CGMS_FEAT_MULTIPLE_SESSIONS_SUPPORTED`、`BLE_CGMS_FEAT_PATIENT_HIGH_LOW_ALERTS_SUPPORTED`、`BLE_CGMS_FEAT_RATE_OF_INCREASE_DECREASE_ALERTS_SUPPORTED`、`BLE_CGMS_FEAT_SENSOR_MALFUNCTION_DETECTION_SUPPORTED`、`BLE_CGMS_FEAT_SENSOR_RESULT_HIGH_LOW_DETECTION_SUPPORTED`、`BLE_CGMS_FEAT_SENSOR_TEMPERATURE_HIGH_LOW_DETECTION_SUPPORTED`、`BLE_CGMS_FEAT_SENSOR_TYPE_ERROR_DETECTION_SUPPORTED`、`BLE_CGMS_FLAGS_QUALITY_PRESENT`、`BLE_CGMS_FLAG_TREND_INFO_PRESENT`、`BLE_CGMS_MAX_CALIB_LEN`、`BLE_CGMS_MEAS_LEN_MAX`、`BLE_CGMS_MEAS_LOC_AST`、`BLE_CGMS_MEAS_LOC_CONTROL`、`BLE_CGMS_MEAS_LOC_EAR`、`BLE_CGMS_MEAS_LOC_FINGER`、`BLE_CGMS_MEAS_LOC_NOT_AVAIL`、`BLE_CGMS_MEAS_LOC_SUB_TISSUE`、`BLE_CGMS_MEAS_REC_LEN_MAX`、`BLE_CGMS_MEAS_REC_LEN_MIN`、`BLE_CGMS_MEAS_REC_PER_NOTIF_MAX`、`BLE_CGMS_MEAS_TYPE_ART_BLOOD`、`BLE_CGMS_MEAS_TYPE_ART_PLASMA`、`BLE_CGMS_MEAS_TYPE_CAP_BLOOD`、`BLE_CGMS_MEAS_TYPE_CAP_PLASMA`、`BLE_CGMS_MEAS_TYPE_CONTROL`、`BLE_CGMS_MEAS_TYPE_FLUID`、`BLE_CGMS_MEAS_TYPE_UNDET_BLOOD`、`BLE_CGMS_MEAS_TYPE_UNDET_PLASMA`、`BLE_CGMS_MEAS_TYPE_VEN_BLOOD`、`BLE_CGMS_MEAS_TYPE_VEN_PLASMA`、`BLE_CGMS_RACP_PENDING_OPERANDS_MAX`、`BLE_CGMS_SOCP_LEN`、`BLE_CGMS_SOCP_OPERAND_MAX`、`BLE_CGMS_SRT_LEN`、`BLE_CGMS_SST_LEN`、`BLE_CGMS_STATUS_DEVICE_BATTERY_LOW`、`BLE_CGMS_STATUS_DEVICE_SPECIFIC_ALERT`、`BLE_CGMS_STATUS_FLAGS_CALTEMP_OCT_PRESENT`、`BLE_CGMS_STATUS_FLAGS_STATUS_OCT_PRESENT`、`BLE_CGMS_STATUS_FLAGS_WARNING_OCT_PRESENT`、`BLE_CGMS_STATUS_GENERAL_DEVICE_FAULT`、`BLE_CGMS_STATUS_LEN`、`BLE_CGMS_STATUS_SENSOR_MALFUNCTION`、`BLE_CGMS_STATUS_SENSOR_TYPE_INCORRECT_FOR_DEVICE`、`BLE_CGMS_STATUS_SESSION_STOPPED` |

## `ble_dis.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_dis.h:1-70`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_dis_init` |
| struct・enum・typedef・callback | `ble_dis_config`、`device_info_char`、`sec_mode` |
| enum 値・event 定数 | なし |
| 定義 macro | `BLE_DIS_CONFIG_SEC_MODE_DEFAULT` |

## `ble_hids.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_hids.h:1-807`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_hids_boot_kb_inp_rep_send`、`ble_hids_boot_mouse_inp_rep_send`、`ble_hids_init`、`ble_hids_inp_rep_send`、`ble_hids_on_ble_evt`、`ble_hids_outp_rep_get` |
| struct・enum・typedef・callback | `ble_hids`、`ble_hids_boot_keyboard_input_report`、`ble_hids_boot_mouse_input_report`、`ble_hids_char_id`、`ble_hids_client_context`、`ble_hids_config`、`ble_hids_evt`、`ble_hids_evt_handler_t`、`ble_hids_evt_type`、`ble_hids_input_report`、`ble_hids_link_ctx_storage`、`ble_hids_rep_char`、`ble_hids_rep_map_config`、`ble_hids_report_config`、`ble_hids_report_type`、`boot_kb_inp_rep_char`、`boot_kb_outp_rep_char`、`boot_mouse_inp_rep_char`、`char_auth_read`、`char_write`、`ctrl_point_char`、`error`、`flags`、`hid_info_char`、`hid_information`、`notification`、`protocol_mode_char`、`report_map_char`、`sec_mode` |
| enum 値・event 定数 | `BLE_HIDS_EVT_BOOT_MODE_ENTERED`、`BLE_HIDS_EVT_ERROR`、`BLE_HIDS_EVT_HOST_EXIT_SUSP`、`BLE_HIDS_EVT_HOST_SUSP`、`BLE_HIDS_EVT_NOTIF_DISABLED`、`BLE_HIDS_EVT_NOTIF_ENABLED`、`BLE_HIDS_EVT_REPORT_MODE_ENTERED`、`BLE_HIDS_EVT_REPORT_READ`、`BLE_HIDS_EVT_REP_CHAR_WRITE`、`BLE_HIDS_REPORT_TYPE_FEATURE`、`BLE_HIDS_REPORT_TYPE_INPUT`、`BLE_HIDS_REPORT_TYPE_OUTPUT`、`BLE_HIDS_REPORT_TYPE_RESERVED` |
| 定義 macro | `BLE_HIDS_BOOT_KB_INPUT_REPORT_MAX_SIZE`、`BLE_HIDS_BOOT_KB_OUTPUT_REPORT_MAX_SIZE`、`BLE_HIDS_BOOT_MOUSE_INPUT_REPORT_MAX_SIZE`、`BLE_HIDS_CONFIG_SEC_MODE_DEFAULT_KEYBOARD`、`BLE_HIDS_CONFIG_SEC_MODE_DEFAULT_MOUSE`、`BLE_HIDS_DEF`、`BLE_HIDS_LINK_CTX_SIZE`、`CTX_DATA_POOL_SIZE` |

## `ble_hrs.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_hrs.h:1-319`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_hrs_body_sensor_location_set`、`ble_hrs_conn_params_evt`、`ble_hrs_heart_rate_measurement_send`、`ble_hrs_init`、`ble_hrs_rr_interval_add`、`ble_hrs_rr_interval_buffer_is_full`、`ble_hrs_sensor_contact_detected_update`、`ble_hrs_sensor_contact_supported_set` |
| struct・enum・typedef・callback | `ble_hrs`、`ble_hrs_config`、`ble_hrs_evt`、`ble_hrs_evt_handler_t`、`ble_hrs_evt_type`、`bsl_char`、`error`、`hrm_char`、`sec_mode` |
| enum 値・event 定数 | `BLE_HRS_EVT_ERROR`、`BLE_HRS_EVT_NOTIFICATION_DISABLED`、`BLE_HRS_EVT_NOTIFICATION_ENABLED` |
| 定義 macro | `BLE_HRS_BODY_SENSOR_LOCATION_CHEST`、`BLE_HRS_BODY_SENSOR_LOCATION_EAR_LOBE`、`BLE_HRS_BODY_SENSOR_LOCATION_FINGER`、`BLE_HRS_BODY_SENSOR_LOCATION_FOOT`、`BLE_HRS_BODY_SENSOR_LOCATION_HAND`、`BLE_HRS_BODY_SENSOR_LOCATION_OTHER`、`BLE_HRS_BODY_SENSOR_LOCATION_WRIST`、`BLE_HRS_CONFIG_SEC_MODE_DEFAULT`、`BLE_HRS_DEF` |

## `ble_hrs_client.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_hrs_client.h:1-268`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_hrs_client_handles_assign`、`ble_hrs_client_hrm_notif_disable`、`ble_hrs_client_hrm_notif_enable`、`ble_hrs_client_init`、`ble_hrs_client_on_ble_evt`、`ble_hrs_on_db_disc_evt` |
| struct・enum・typedef・callback | `ble_hrs_client`、`ble_hrs_client_config`、`ble_hrs_client_evt`、`ble_hrs_client_evt_handler_t`、`ble_hrs_client_evt_type`、`ble_hrs_handles`、`ble_hrs_measurement`、`discovery_complete`、`error` |
| enum 値・event 定数 | `BLE_HRS_CLIENT_EVT_DISCOVERY_COMPLETE`、`BLE_HRS_CLIENT_EVT_ERROR`、`BLE_HRS_CLIENT_EVT_HRM_NOTIFICATION` |
| 定義 macro | `BLE_HRS_CLIENT_DEF` |

## `ble_lbs.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_lbs.h:1-182`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_lbs_init`、`ble_lbs_on_ble_evt`、`ble_lbs_on_button_change` |
| struct・enum・typedef・callback | `ble_lbs`、`ble_lbs_config`、`ble_lbs_evt`、`ble_lbs_evt_type`、`error`、`lbs_button_char`、`lbs_evt_handler_t`、`lbs_led_char`、`led_write`、`sec_mode` |
| enum 値・event 定数 | `BLE_LBS_EVT_ERROR`、`BLE_LBS_EVT_LED_WRITE` |
| 定義 macro | `BLE_LBS_CONFIG_SEC_MODE_DEFAULT`、`BLE_LBS_DEF`、`BLE_UUID_LBS_BASE`、`BLE_UUID_LBS_BUTTON_CHAR`、`BLE_UUID_LBS_LED_CHAR`、`BLE_UUID_LBS_SERVICE` |

## `ble_mcumgr.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_mcumgr.h:1-86`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_mcumgr_init`、`ble_mcumgr_service_uuid_type` |
| struct・enum・typedef・callback | `ble_mcumgr_config`、`mcumgr_char`、`sec_mode` |
| enum 値・event 定数 | なし |
| 定義 macro | `BLE_MCUMGR_CHARACTERISTIC_UUID`、`BLE_MCUMGR_CHARACTERISTIC_UUID_SUB`、`BLE_MCUMGR_CONFIG_SEC_MODE_DEFAULT`、`BLE_MCUMGR_SERVICE_UUID`、`BLE_MCUMGR_SERVICE_UUID_SUB` |

## `ble_nus.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_nus.h:1-235`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_nus_data_send`、`ble_nus_init`、`ble_nus_on_ble_evt` |
| struct・enum・typedef・callback | `ble_nus`、`ble_nus_config`、`ble_nus_evt`、`ble_nus_evt_handler_t`、`ble_nus_evt_type`、`error`、`nus_rx_char`、`nus_tx_char`、`rx_data`、`sec_mode` |
| enum 値・event 定数 | `BLE_NUS_EVT_COMM_STARTED`、`BLE_NUS_EVT_COMM_STOPPED`、`BLE_NUS_EVT_ERROR`、`BLE_NUS_EVT_RX_DATA`、`BLE_NUS_EVT_TX_RDY` |
| 定義 macro | `BLE_NUS_CONFIG_SEC_MODE_DEFAULT`、`BLE_NUS_DEF`、`BLE_NUS_MAX_DATA_LEN`、`BLE_NUS_MAX_DATA_LEN_CALC`、`BLE_NUS_UUID_BASE`、`BLE_UUID_NUS_RX_CHARACTERISTIC`、`BLE_UUID_NUS_SERVICE`、`BLE_UUID_NUS_TX_CHARACTERISTIC` |

## `ble_nus_client.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_nus_client.h:1-288`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_nus_client_handles_assign`、`ble_nus_client_init`、`ble_nus_client_on_ble_evt`、`ble_nus_client_on_db_disc_evt`、`ble_nus_client_string_send`、`ble_nus_client_tx_notif_disable`、`ble_nus_client_tx_notif_enable` |
| struct・enum・typedef・callback | `ble_nus_client`、`ble_nus_client_config`、`ble_nus_client_evt`、`ble_nus_client_evt_handler_t`、`ble_nus_client_evt_type`、`ble_nus_client_handles`、`disconnected`、`discovery_complete`、`error`、`tx_data` |
| enum 値・event 定数 | `BLE_NUS_CLIENT_EVT_DISCONNECTED`、`BLE_NUS_CLIENT_EVT_DISCOVERY_COMPLETE`、`BLE_NUS_CLIENT_EVT_ERROR`、`BLE_NUS_CLIENT_EVT_TX_DATA` |
| 定義 macro | `BLE_NUS_CLIENT_DEF`、`BLE_NUS_CLIENT_MAX_DATA_LEN`、`BLE_NUS_CLIENT_MAX_DATA_LEN_CALC`、`BLE_NUS_UUID_BASE`、`BLE_UUID_NUS_RX_CHARACTERISTIC`、`BLE_UUID_NUS_SERVICE`、`BLE_UUID_NUS_TX_CHARACTERISTIC` |

## `uuid.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/services/uuid.h:1-284`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `BLE_CCCD_VALUE_LEN`、`BLE_CHAR_ALERT_LEVEL_HIGH_ALERT`、`BLE_CHAR_ALERT_LEVEL_MILD_ALERT`、`BLE_CHAR_ALERT_LEVEL_NO_ALERT`、`BLE_SRV_ENCODED_REPORT_REF_LEN`、`BLE_UUID_ALERT_CATEGORY_ID_BIT_MASK_CHAR`、`BLE_UUID_ALERT_CATEGORY_ID_CHAR`、`BLE_UUID_ALERT_LEVEL_CHAR`、`BLE_UUID_ALERT_NOTIFICATION_CONTROL_POINT_CHAR`、`BLE_UUID_ALERT_NOTIFICATION_SERVICE`、`BLE_UUID_ALERT_STATUS_CHAR`、`BLE_UUID_BATTERY_LEVEL_CHAR`、`BLE_UUID_BATTERY_SERVICE`、`BLE_UUID_BLOOD_PRESSURE_FEATURE_CHAR`、`BLE_UUID_BLOOD_PRESSURE_MEASUREMENT_CHAR`、`BLE_UUID_BLOOD_PRESSURE_SERVICE`、`BLE_UUID_BMS_CTRLPT`、`BLE_UUID_BMS_FEATURE`、`BLE_UUID_BMS_SERVICE`、`BLE_UUID_BODY_SENSOR_LOCATION_CHAR`、`BLE_UUID_BOOT_KEYBOARD_INPUT_REPORT_CHAR`、`BLE_UUID_BOOT_KEYBOARD_OUTPUT_REPORT_CHAR`、`BLE_UUID_BOOT_MOUSE_INPUT_REPORT_CHAR`、`BLE_UUID_CGM_FEATURE`、`BLE_UUID_CGM_MEASUREMENT`、`BLE_UUID_CGM_SERVICE`、`BLE_UUID_CGM_SESSION_RUN_TIME`、`BLE_UUID_CGM_SESSION_START_TIME`、`BLE_UUID_CGM_SPECIFIC_OPS_CTRLPT`、`BLE_UUID_CGM_STATUS`、`BLE_UUID_CSC_FEATURE_CHAR`、`BLE_UUID_CSC_MEASUREMENT_CHAR`、`BLE_UUID_CURRENT_TIME_CHAR`、`BLE_UUID_CURRENT_TIME_SERVICE`、`BLE_UUID_CYCLING_SPEED_AND_CADENCE`、`BLE_UUID_DATE_TIME_CHAR`、`BLE_UUID_DAY_DATE_TIME_CHAR`、`BLE_UUID_DAY_OF_WEEK_CHAR`、`BLE_UUID_DEVICE_INFORMATION_SERVICE`、`BLE_UUID_DST_OFFSET_CHAR`、`BLE_UUID_EXACT_TIME_256_CHAR`、`BLE_UUID_EXTERNAL_REPORT_REF_DESCR`、`BLE_UUID_FIRMWARE_REVISION_STRING_CHAR`、`BLE_UUID_GLUCOSE_FEATURE_CHAR`、`BLE_UUID_GLUCOSE_MEASUREMENT_CHAR`、`BLE_UUID_GLUCOSE_MEASUREMENT_CONTEXT_CHAR`、`BLE_UUID_GLUCOSE_SERVICE`、`BLE_UUID_HARDWARE_REVISION_STRING_CHAR`、`BLE_UUID_HEALTH_THERMOMETER_SERVICE`、`BLE_UUID_HEART_RATE_CONTROL_POINT_CHAR`、`BLE_UUID_HEART_RATE_MEASUREMENT_CHAR`、`BLE_UUID_HEART_RATE_SERVICE`、`BLE_UUID_HID_CONTROL_POINT_CHAR`、`BLE_UUID_HID_INFORMATION_CHAR`、`BLE_UUID_HUMAN_INTERFACE_DEVICE_SERVICE`、`BLE_UUID_IEEE_REGULATORY_CERTIFICATION_DATA_LIST_CHAR`、`BLE_UUID_IMMEDIATE_ALERT_SERVICE`、`BLE_UUID_INTERMEDIATE_CUFF_PRESSURE_CHAR`、`BLE_UUID_INTERMEDIATE_TEMPERATURE_CHAR`、`BLE_UUID_IPSP_SERVICE`、`BLE_UUID_LINK_LOSS_SERVICE`、`BLE_UUID_LN_CONTROL_POINT_CHAR`、`BLE_UUID_LN_FEATURE_CHAR`、`BLE_UUID_LN_LOCATION_AND_SPEED_CHAR`、`BLE_UUID_LN_NAVIGATION_CHAR`、`BLE_UUID_LN_POSITION_QUALITY_CHAR`、`BLE_UUID_LOCAL_TIME_INFORMATION_CHAR`、`BLE_UUID_LOCATION_AND_NAVIGATION_SERVICE`、`BLE_UUID_MANUFACTURER_NAME_STRING_CHAR`、`BLE_UUID_MEASUREMENT_INTERVAL_CHAR`、`BLE_UUID_MODEL_NUMBER_STRING_CHAR`、`BLE_UUID_NEW_ALERT_CHAR`、`BLE_UUID_NEXT_DST_CHANGE_SERVICE`、`BLE_UUID_OTS_FEATURES`、`BLE_UUID_OTS_LF`、`BLE_UUID_OTS_OACP`、`BLE_UUID_OTS_OBJECT_CHANGED`、`BLE_UUID_OTS_OBJECT_FIRST_CREATED`、`BLE_UUID_OTS_OBJECT_ID`、`BLE_UUID_OTS_OBJECT_LAST_MODIFIED`、`BLE_UUID_OTS_OBJECT_NAME`、`BLE_UUID_OTS_OBJECT_PROPERTIES`、`BLE_UUID_OTS_OBJECT_SIZE`、`BLE_UUID_OTS_OBJECT_TYPE`、`BLE_UUID_OTS_OLCP`、`BLE_UUID_OTS_SERVICE`、`BLE_UUID_PHONE_ALERT_STATUS_SERVICE`、`BLE_UUID_PLX_CONTINUOUS_MEAS`、`BLE_UUID_PLX_FEATURES`、`BLE_UUID_PLX_SERVICE`、`BLE_UUID_PLX_SPOT_CHECK_MEAS`、`BLE_UUID_PNP_ID_CHAR`、`BLE_UUID_PROTOCOL_MODE_CHAR`、`BLE_UUID_RECORD_ACCESS_CONTROL_POINT_CHAR`、`BLE_UUID_REFERENCE_TIME_INFORMATION_CHAR`、`BLE_UUID_REFERENCE_TIME_UPDATE_SERVICE`、`BLE_UUID_REMOVABLE_CHAR`、`BLE_UUID_REPORT_CHAR`、`BLE_UUID_REPORT_MAP_CHAR`、`BLE_UUID_REPORT_REF_DESCR`、`BLE_UUID_RINGER_CONTROL_POINT_CHAR`、`BLE_UUID_RINGER_SETTING_CHAR`、`BLE_UUID_RSC_FEATURE_CHAR`、`BLE_UUID_RSC_MEASUREMENT_CHAR`、`BLE_UUID_RUNNING_SPEED_AND_CADENCE`、`BLE_UUID_SCAN_INTERVAL_WINDOW_CHAR`、`BLE_UUID_SCAN_PARAMETERS_SERVICE`、`BLE_UUID_SCAN_REFRESH_CHAR`、`BLE_UUID_SC_CTRLPT_CHAR`、`BLE_UUID_SENSOR_LOCATION_CHAR`、`BLE_UUID_SERIAL_NUMBER_STRING_CHAR`、`BLE_UUID_SERVICE_REQUIRED_CHAR`、`BLE_UUID_SOFTWARE_REVISION_STRING_CHAR`、`BLE_UUID_SUPPORTED_NEW_ALERT_CATEGORY_CHAR`、`BLE_UUID_SUPPORTED_UNREAD_ALERT_CATEGORY_CHAR`、`BLE_UUID_SYSTEM_ID_CHAR`、`BLE_UUID_TEMPERATURE_MEASUREMENT_CHAR`、`BLE_UUID_TEMPERATURE_TYPE_CHAR`、`BLE_UUID_TIME_ACCURACY_CHAR`、`BLE_UUID_TIME_SOURCE_CHAR`、`BLE_UUID_TIME_UPDATE_CONTROL_POINT_CHAR`、`BLE_UUID_TIME_UPDATE_STATE_CHAR`、`BLE_UUID_TIME_WITH_DST_CHAR`、`BLE_UUID_TIME_ZONE_CHAR`、`BLE_UUID_TX_POWER_LEVEL_CHAR`、`BLE_UUID_TX_POWER_SERVICE`、`BLE_UUID_UNREAD_ALERT_CHAR` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
