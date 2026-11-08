# Bluetooth 共通・peer managerの公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `ble_adv.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_adv.h:1-380`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_adv_allow_list_reply`、`ble_adv_conn_cfg_tag_set`、`ble_adv_data_update`、`ble_adv_init`、`ble_adv_on_ble_evt`、`ble_adv_peer_addr_reply`、`ble_adv_restart_without_allow_list`、`ble_adv_start`、`ble_adv_stop` |
| struct・enum・typedef・callback | `ble_adv`、`ble_adv_config`、`ble_adv_evt`、`ble_adv_evt_handler_t`、`ble_adv_evt_type`、`ble_adv_mode`、`error` |
| enum 値・event 定数 | `BLE_ADV_EVT_ALLOW_LIST_REQUEST`、`BLE_ADV_EVT_DIRECTED`、`BLE_ADV_EVT_DIRECTED_HIGH_DUTY`、`BLE_ADV_EVT_ERROR`、`BLE_ADV_EVT_FAST`、`BLE_ADV_EVT_FAST_ALLOW_LIST`、`BLE_ADV_EVT_IDLE`、`BLE_ADV_EVT_PEER_ADDR_REQUEST`、`BLE_ADV_EVT_SLOW`、`BLE_ADV_EVT_SLOW_ALLOW_LIST`、`BLE_ADV_MODE_DIRECTED`、`BLE_ADV_MODE_DIRECTED_HIGH_DUTY`、`BLE_ADV_MODE_FAST`、`BLE_ADV_MODE_IDLE`、`BLE_ADV_MODE_SLOW` |
| 定義 macro | `BLE_ADV_DEF` |

## `ble_adv_data.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_adv_data.h:1-317`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_adv_data_appearance_find`、`ble_adv_data_encode`、`ble_adv_data_name_find`、`ble_adv_data_parse`、`ble_adv_data_search`、`ble_adv_data_short_name_find`、`ble_adv_data_uuid_find` |
| struct・enum・typedef・callback | `ble_adv_data`、`ble_adv_data_conn_int`、`ble_adv_data_le_role`、`ble_adv_data_manufacturer`、`ble_adv_data_name_type`、`ble_adv_data_service`、`ble_adv_data_uuid_list`、`srv_list`、`uuid_lists` |
| enum 値・event 定数 | `BLE_ADV_DATA_FULL_NAME`、`BLE_ADV_DATA_NO_NAME`、`BLE_ADV_DATA_ROLE_BOTH_CENTRAL_PREFERRED`、`BLE_ADV_DATA_ROLE_BOTH_PERIPH_PREFERRED`、`BLE_ADV_DATA_ROLE_NOT_PRESENT`、`BLE_ADV_DATA_ROLE_ONLY_CENTRAL`、`BLE_ADV_DATA_ROLE_ONLY_PERIPH`、`BLE_ADV_DATA_SHORT_NAME` |
| 定義 macro | なし |

## `ble_common.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_common.h:1-139`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_gap_conn_sec_mode_equal`、`is_indication_enabled`、`is_notification_enabled` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `ATT_HANDLE_LEN`、`ATT_OPCODE_LEN`、`BLE_GAP_CONN_SEC_MODE_ENC_NO_MITM`、`BLE_GAP_CONN_SEC_MODE_ENC_WITH_MITM`、`BLE_GAP_CONN_SEC_MODE_LESC_ENC_WITH_MITM`、`BLE_GAP_CONN_SEC_MODE_NO_ACCESS`、`BLE_GAP_CONN_SEC_MODE_OPEN`、`BYTES_TO_WORDS` |

## `ble_conn_params.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_conn_params.h:1-243`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_conn_params_att_mtu_get`、`ble_conn_params_att_mtu_set`、`ble_conn_params_data_length_get`、`ble_conn_params_data_length_set`、`ble_conn_params_evt_handler_set`、`ble_conn_params_override`、`ble_conn_params_phy_radio_mode_get`、`ble_conn_params_phy_radio_mode_set` |
| struct・enum・typedef・callback | `ble_conn_params_data_length`、`ble_conn_params_evt`、`ble_conn_params_evt_handler_t`、`ble_conn_params_evt_type`、`error` |
| enum 値・event 定数 | `BLE_CONN_PARAMS_EVT_ATT_MTU_UPDATED`、`BLE_CONN_PARAMS_EVT_DATA_LENGTH_UPDATED`、`BLE_CONN_PARAMS_EVT_ERROR`、`BLE_CONN_PARAMS_EVT_RADIO_PHY_MODE_UPDATED`、`BLE_CONN_PARAMS_EVT_REJECTED`、`BLE_CONN_PARAMS_EVT_UPDATED` |
| 定義 macro | なし |

## `ble_conn_state.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_conn_state.h:1-298`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_conn_state_central_conn_count`、`ble_conn_state_central_handles`、`ble_conn_state_conn_count`、`ble_conn_state_conn_handles`、`ble_conn_state_conn_idx`、`ble_conn_state_encrypted`、`ble_conn_state_for_each_connected`、`ble_conn_state_for_each_set_user_flag`、`ble_conn_state_init`、`ble_conn_state_lesc`、`ble_conn_state_mitm_protected`、`ble_conn_state_periph_handles`、`ble_conn_state_peripheral_conn_count`、`ble_conn_state_role`、`ble_conn_state_status`、`ble_conn_state_user_flag_acquire`、`ble_conn_state_user_flag_get`、`ble_conn_state_user_flag_set`、`ble_conn_state_valid` |
| struct・enum・typedef・callback | `ble_conn_state_conn_handle_list`、`ble_conn_state_status`、`ble_conn_state_user_function_t` |
| enum 値・event 定数 | `BLE_CONN_STATUS_CONNECTED`、`BLE_CONN_STATUS_DISCONNECTED`、`BLE_CONN_STATUS_INVALID` |
| 定義 macro | `BLE_CONN_STATE_MAX_CONNECTIONS`、`BLE_CONN_STATE_USER_FLAG_INVALID` |

## `ble_date_time.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_date_time.h:1-72`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_date_time_decode`、`ble_date_time_encode` |
| struct・enum・typedef・callback | `ble_date_time` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `ble_db_discovery.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_db_discovery.h:1-253`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_db_discovery_init`、`ble_db_discovery_on_ble_evt`、`ble_db_discovery_service_register`、`ble_db_discovery_start` |
| struct・enum・typedef・callback | `ble_db_discovery`、`ble_db_discovery_config`、`ble_db_discovery_evt`、`ble_db_discovery_evt_handler`、`ble_db_discovery_evt_type`、`error` |
| enum 値・event 定数 | `BLE_DB_DISCOVERY_AVAILABLE`、`BLE_DB_DISCOVERY_COMPLETE`、`BLE_DB_DISCOVERY_ERROR`、`BLE_DB_DISCOVERY_SRV_NOT_FOUND` |
| 定義 macro | `BLE_DB_DISCOVERY_DEF` |

## `ble_gatt_db.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_gatt_db.h:1-81`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | `ble_gatt_db_char`、`ble_gatt_db_srv` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `ble_gq.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_gq.h:1-320`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_gq_conn_handle_register`、`ble_gq_item_add`、`ble_gq_on_ble_evt` |
| struct・enum・typedef・callback | `ble_gq`、`ble_gq_evt`、`ble_gq_evt_handler_t`、`ble_gq_evt_type`、`ble_gq_req`、`ble_gq_req_type`、`error`、`gattc_read`、`gattc_srv_disc` |
| enum 値・event 定数 | `BLE_GQ_EVT_ERROR`、`BLE_GQ_REQ_CHAR_DISCOVERY`、`BLE_GQ_REQ_DESC_DISCOVERY`、`BLE_GQ_REQ_GATTC_READ`、`BLE_GQ_REQ_GATTC_WRITE`、`BLE_GQ_REQ_GATTS_HVX`、`BLE_GQ_REQ_NUM`、`BLE_GQ_REQ_SRV_DISCOVERY` |
| 定義 macro | `BLE_GQ_CONN_HANDLE_INIT`、`BLE_GQ_CUSTOM_DEF`、`BLE_GQ_DEF`、`BLE_GQ_PURGE_ARRAY_INIT`、`BLE_GQ_REQ_QUEUE_INIT` |

## `ble_qwr.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_qwr.h:1-235`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_qwr_attr_register`、`ble_qwr_conn_handle_assign`、`ble_qwr_init`、`ble_qwr_on_ble_evt`、`ble_qwr_value_get` |
| struct・enum・typedef・callback | `auth_req`、`ble_qwr`、`ble_qwr_config`、`ble_qwr_evt`、`ble_qwr_evt_handler_t`、`ble_qwr_evt_type`、`error`、`exec_write` |
| enum 値・event 定数 | `BLE_QWR_EVT_AUTH_REQUEST`、`BLE_QWR_EVT_ERROR`、`BLE_QWR_EVT_EXECUTE_WRITE` |
| 定義 macro | `BLE_QWR_DEF`、`BLE_QWR_REJ_REQUEST_ERR_CODE` |

## `ble_racp.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_racp.h:1-141`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_racp_decode`、`ble_racp_encode` |
| struct・enum・typedef・callback | `ble_racp_value`、`racp_opcode`、`racp_operand_filter_type`、`racp_operator`、`racp_response` |
| enum 値・event 定数 | `RACP_OPCODE_ABORT_OPERATION`、`RACP_OPCODE_DELETE_RECS`、`RACP_OPCODE_NUM_RECS_RESPONSE`、`RACP_OPCODE_REPORT_NUM_RECS`、`RACP_OPCODE_REPORT_RECS`、`RACP_OPCODE_RESERVED`、`RACP_OPCODE_RESPONSE_CODE`、`RACP_OPERAND_FILTER_TYPE_FACING_TIME`、`RACP_OPERAND_FILTER_TYPE_TIME_OFFSET`、`RACP_OPERATOR_ALL`、`RACP_OPERATOR_FIRST`、`RACP_OPERATOR_GREATER_OR_EQUAL`、`RACP_OPERATOR_LAST`、`RACP_OPERATOR_LESS_OR_EQUAL`、`RACP_OPERATOR_NULL`、`RACP_OPERATOR_RANGE`、`RACP_OPERATOR_RFU_START`、`RACP_RESPONSE_ABORT_FAILED`、`RACP_RESPONSE_INVALID_OPERAND`、`RACP_RESPONSE_INVALID_OPERATOR`、`RACP_RESPONSE_NO_RECORDS_FOUND`、`RACP_RESPONSE_OPCODE_UNSUPPORTED`、`RACP_RESPONSE_OPERAND_UNSUPPORTED`、`RACP_RESPONSE_OPERATOR_UNSUPPORTED`、`RACP_RESPONSE_PROCEDURE_NOT_DONE`、`RACP_RESPONSE_RESERVED`、`RACP_RESPONSE_SUCCESS` |
| 定義 macro | なし |

## `ble_radio_notification.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_radio_notification.h:1-55`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_radio_notification_init` |
| struct・enum・typedef・callback | `ble_radio_notification_evt_handler_t` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `ble_scan.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_scan.h:1-599`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_scan_all_filter_remove`、`ble_scan_copy_addr_to_sd_gap_addr`、`ble_scan_filter_add`、`ble_scan_filter_get`、`ble_scan_filters_disable`、`ble_scan_filters_enable`、`ble_scan_init`、`ble_scan_is_allow_list_used`、`ble_scan_on_ble_evt`、`ble_scan_params_set`、`ble_scan_start`、`ble_scan_stop` |
| struct・enum・typedef・callback | `addr_filter`、`allow_list_adv_report`、`appearance_filter`、`ble_scan`、`ble_scan_addr_filter`、`ble_scan_appearance_filter`、`ble_scan_config`、`ble_scan_evt`、`ble_scan_evt_handler_t`、`ble_scan_evt_type`、`ble_scan_filter_data`、`ble_scan_filter_match`、`ble_scan_filters`、`ble_scan_name_filter`、`ble_scan_short_name_filter`、`ble_scan_uuid_filter`、`connected`、`connecting_err`、`error`、`filter_match`、`name_filter`、`not_found`、`short_name_filter`、`uuid_filter` |
| enum 値・event 定数 | `BLE_SCAN_EVT_ALLOW_LIST_ADV_REPORT`、`BLE_SCAN_EVT_ALLOW_LIST_REQUEST`、`BLE_SCAN_EVT_CONNECTED`、`BLE_SCAN_EVT_CONNECTING_ERROR`、`BLE_SCAN_EVT_ERROR`、`BLE_SCAN_EVT_FILTER_MATCH`、`BLE_SCAN_EVT_NOT_FOUND`、`BLE_SCAN_EVT_SCAN_TIMEOUT` |
| 定義 macro | `BLE_SCAN_ADDR_FILTER`、`BLE_SCAN_APPEARANCE_FILTER`、`BLE_SCAN_CONN_PARAMS_DEFAULT`、`BLE_SCAN_DEF`、`BLE_SCAN_SCAN_PARAMS_DEFAULT`、`BLE_SCAN_SHORT_NAME_FILTER`、`BLE_SCAN_UUID_FILTER` |

## `nrf_ble_lesc.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/peer_manager/nrf_ble_lesc.h:1-129`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nrf_ble_lesc_init`、`nrf_ble_lesc_keypair_generate`、`nrf_ble_lesc_on_ble_evt`、`nrf_ble_lesc_own_oob_data_generate`、`nrf_ble_lesc_own_oob_data_get`、`nrf_ble_lesc_peer_oob_data_handler_set`、`nrf_ble_lesc_public_key_get`、`nrf_ble_lesc_request_handler` |
| struct・enum・typedef・callback | `nrf_ble_lesc_peer_oob_data_handler` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `peer_manager.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/peer_manager/peer_manager.h:1-812`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `pm_address_resolve`、`pm_allow_list_get`、`pm_allow_list_set`、`pm_conn_exclude`、`pm_conn_handle_get`、`pm_conn_sec_config_reply`、`pm_conn_sec_params_reply`、`pm_conn_sec_status_get`、`pm_conn_secure`、`pm_device_identities_list_set`、`pm_id_addr_get`、`pm_id_addr_set`、`pm_init`、`pm_lesc_public_key_set`、`pm_local_database_has_changed`、`pm_next_peer_id_get`、`pm_peer_count`、`pm_peer_data_app_data_load`、`pm_peer_data_app_data_store`、`pm_peer_data_bonding_load`、`pm_peer_data_bonding_store`、`pm_peer_data_delete`、`pm_peer_data_load`、`pm_peer_data_remote_db_load`、`pm_peer_data_remote_db_store`、`pm_peer_data_store`、`pm_peer_delete`、`pm_peer_id_get`、`pm_peer_id_list`、`pm_peer_new`、`pm_peer_rank_highest`、`pm_peer_ranks_get`、`pm_peers_delete`、`pm_privacy_get`、`pm_privacy_set`、`pm_register`、`pm_sec_is_sufficient`、`pm_sec_params_set` |
| struct・enum・typedef・callback | `pm_peer_id_list_skip` |
| enum 値・event 定数 | `PM_PEER_ID_LIST_ALL_ID`、`PM_PEER_ID_LIST_SKIP_ALL`、`PM_PEER_ID_LIST_SKIP_NO_CAR`、`PM_PEER_ID_LIST_SKIP_NO_ID_ADDR`、`PM_PEER_ID_LIST_SKIP_NO_IRK` |
| 定義 macro | なし |

## `peer_manager_handler.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/peer_manager/peer_manager_handler.h:1-141`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `pm_handler_disconnect_on_insufficient_sec`、`pm_handler_disconnect_on_sec_failure`、`pm_handler_flash_clean`、`pm_handler_flash_clean_on_return`、`pm_handler_on_pm_evt`、`pm_handler_pm_evt_log`、`pm_handler_secure_on_connection`、`pm_handler_secure_on_error` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `peer_manager_types.h`

`vendor/sdk-nrf-bm/include/bm/bluetooth/peer_manager/peer_manager_types.h:1-517`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | `pm_conn_config_req_evt`、`pm_conn_sec_config`、`pm_conn_sec_params_req_evt`、`pm_conn_sec_procedure`、`pm_conn_sec_start_evt`、`pm_conn_sec_status`、`pm_conn_secure_failed_evt`、`pm_conn_secured_evt`、`pm_evt`、`pm_evt_handler_t`、`pm_evt_id`、`pm_failure_evt`、`pm_peer_data_bonding`、`pm_peer_data_id`、`pm_peer_data_local_gatt_db`、`pm_peer_data_op`、`pm_peer_data_update_failed_evt`、`pm_peer_data_update_succeeded_evt` |
| enum 値・event 定数 | `PM_CONN_SEC_PROCEDURE_BONDING`、`PM_CONN_SEC_PROCEDURE_ENCRYPTION`、`PM_CONN_SEC_PROCEDURE_PAIRING`、`PM_EVT_BONDED_PEER_CONNECTED`、`PM_EVT_CONN_CONFIG_REQ`、`PM_EVT_CONN_SEC_CONFIG_REQ`、`PM_EVT_CONN_SEC_FAILED`、`PM_EVT_CONN_SEC_PARAMS_REQ`、`PM_EVT_CONN_SEC_START`、`PM_EVT_CONN_SEC_SUCCEEDED`、`PM_EVT_ERROR_UNEXPECTED`、`PM_EVT_FLASH_GARBAGE_COLLECTED`、`PM_EVT_FLASH_GARBAGE_COLLECTION_FAILED`、`PM_EVT_LOCAL_DB_CACHE_APPLIED`、`PM_EVT_LOCAL_DB_CACHE_APPLY_FAILED`、`PM_EVT_PEERS_DELETE_FAILED`、`PM_EVT_PEERS_DELETE_SUCCEEDED`、`PM_EVT_PEER_DATA_UPDATE_FAILED`、`PM_EVT_PEER_DATA_UPDATE_SUCCEEDED`、`PM_EVT_PEER_DELETE_FAILED`、`PM_EVT_PEER_DELETE_SUCCEEDED`、`PM_EVT_PERIPHERAL_SECURITY_REQ`、`PM_EVT_SERVICE_CHANGED_IND_CONFIRMED`、`PM_EVT_SERVICE_CHANGED_IND_SENT`、`PM_EVT_STORAGE_FULL`、`PM_PEER_DATA_ID_APPLICATION`、`PM_PEER_DATA_ID_BONDING`、`PM_PEER_DATA_ID_CENTRAL_ADDR_RES`、`PM_PEER_DATA_ID_FIRST`、`PM_PEER_DATA_ID_GATT_LOCAL`、`PM_PEER_DATA_ID_GATT_REMOTE`、`PM_PEER_DATA_ID_INVALID`、`PM_PEER_DATA_ID_LAST`、`PM_PEER_DATA_ID_PEER_RANK`、`PM_PEER_DATA_ID_SERVICE_CHANGED_PENDING`、`PM_PEER_DATA_OP_DELETE`、`PM_PEER_DATA_OP_UPDATE` |
| 定義 macro | `PM_CONN_SEC_ERROR_BASE`、`PM_CONN_SEC_ERROR_DISCONNECT`、`PM_CONN_SEC_ERROR_MIC_FAILURE`、`PM_CONN_SEC_ERROR_PIN_OR_KEY_MISSING`、`PM_CONN_SEC_ERROR_SMP_TIMEOUT`、`PM_LOCAL_DB_LEN_OVERHEAD_BYTES`、`PM_PEER_DATA_ID_APPLICATION_V1`、`PM_PEER_DATA_ID_BONDING_V1`、`PM_PEER_DATA_ID_BONDING_V2`、`PM_PEER_DATA_ID_CENTRAL_ADDR_RES_V1`、`PM_PEER_DATA_ID_FIRST_VX`、`PM_PEER_DATA_ID_GATT_LOCAL_V1`、`PM_PEER_DATA_ID_GATT_LOCAL_V2`、`PM_PEER_DATA_ID_GATT_REMOTE_V1`、`PM_PEER_DATA_ID_GATT_REMOTE_V2`、`PM_PEER_DATA_ID_INVALID_VX`、`PM_PEER_DATA_ID_LAST_VX`、`PM_PEER_DATA_ID_PEER_RANK_V1`、`PM_PEER_DATA_ID_SERVICE_CHANGED_PENDING_V1`、`PM_PEER_ID_INVALID`、`PM_PEER_ID_N_AVAILABLE_IDS`、`PM_STORE_TOKEN_INVALID` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
