# storage・filesystem・MCUmgrの公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `bm_zms.h`

`vendor/sdk-nrf-bm/include/bm/fs/bm_zms.h:1-315`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_zms_active_sector_free_space`、`bm_zms_calc_free_space`、`bm_zms_clear`、`bm_zms_delete`、`bm_zms_get_data_length`、`bm_zms_mount`、`bm_zms_read`、`bm_zms_read_hist`、`bm_zms_write` |
| struct・enum・typedef・callback | `__packed`、`bm_zms_evt`、`bm_zms_evt_handler_t`、`bm_zms_evt_type`、`bm_zms_fs`、`bm_zms_fs_config`、`bm_zms_init_flags` |
| enum 値・event 定数 | `BM_ZMS_EVT_CLEAR`、`BM_ZMS_EVT_DELETE`、`BM_ZMS_EVT_MOUNT`、`BM_ZMS_EVT_NONE`、`BM_ZMS_EVT_WRITE` |
| 定義 macro | なし |

## `img_mgmt.h`

`vendor/sdk-nrf-bm/include/bm/mgmt/mcumgr/grp/img_mgmt/img_mgmt.h:1-399`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `img_mgmt_active_image`、`img_mgmt_active_slot`、`img_mgmt_error_rsp`、`img_mgmt_my_version`、`img_mgmt_read_info`、`img_mgmt_reset_upload`、`img_mgmt_slot_in_use`、`img_mgmt_state_any_pending`、`img_mgmt_state_confirm`、`img_mgmt_state_flags`、`img_mgmt_state_set_pending`、`img_mgmt_ver_str`、`img_mgmt_vercmp` |
| struct・enum・typedef・callback | `img_mgmt_err_code_t`、`img_mgmt_id_upload_t`、`img_mgmt_state`、`img_mgmt_upload_action`、`img_mgmt_upload_req` |
| enum 値・event 定数 | `IMG_MGMT_ERR_ACTIVE_SLOT_NOT_KNOWN`、`IMG_MGMT_ERR_CURRENT_VERSION_IS_NEWER`、`IMG_MGMT_ERR_FLASH_AREA_DEVICE_NULL`、`IMG_MGMT_ERR_FLASH_CONFIG_QUERY_FAIL`、`IMG_MGMT_ERR_FLASH_CONTEXT_ALREADY_SET`、`IMG_MGMT_ERR_FLASH_CONTEXT_NOT_SET`、`IMG_MGMT_ERR_FLASH_ERASE_FAILED`、`IMG_MGMT_ERR_FLASH_OPEN_FAILED`、`IMG_MGMT_ERR_FLASH_READ_FAILED`、`IMG_MGMT_ERR_FLASH_WRITE_FAILED`、`IMG_MGMT_ERR_HASH_NOT_FOUND`、`IMG_MGMT_ERR_IMAGE_ALREADY_PENDING`、`IMG_MGMT_ERR_IMAGE_CONFIRMATION_DENIED`、`IMG_MGMT_ERR_IMAGE_SETTING_TEST_TO_ACTIVE_DENIED`、`IMG_MGMT_ERR_INVALID_FLASH_ADDRESS`、`IMG_MGMT_ERR_INVALID_HASH`、`IMG_MGMT_ERR_INVALID_IMAGE_DATA_OVERRUN`、`IMG_MGMT_ERR_INVALID_IMAGE_HEADER`、`IMG_MGMT_ERR_INVALID_IMAGE_HEADER_MAGIC`、`IMG_MGMT_ERR_INVALID_IMAGE_TOO_LARGE`、`IMG_MGMT_ERR_INVALID_IMAGE_VECTOR_TABLE`、`IMG_MGMT_ERR_INVALID_LENGTH`、`IMG_MGMT_ERR_INVALID_OFFSET`、`IMG_MGMT_ERR_INVALID_PAGE_OFFSET`、`IMG_MGMT_ERR_INVALID_SLOT`、`IMG_MGMT_ERR_INVALID_TLV`、`IMG_MGMT_ERR_NO_FREE_MEMORY`、`IMG_MGMT_ERR_NO_FREE_SLOT`、`IMG_MGMT_ERR_NO_IMAGE`、`IMG_MGMT_ERR_NO_TLVS`、`IMG_MGMT_ERR_OK`、`IMG_MGMT_ERR_TLV_INVALID_SIZE`、`IMG_MGMT_ERR_TLV_MULTIPLE_HASHES_FOUND`、`IMG_MGMT_ERR_UNKNOWN`、`IMG_MGMT_ERR_VERSION_GET_FAILED`、`IMG_MGMT_ID_UPLOAD_STATUS_COMPLETE`、`IMG_MGMT_ID_UPLOAD_STATUS_ONGOING`、`IMG_MGMT_ID_UPLOAD_STATUS_START` |
| 定義 macro | `H_IMG_MGMT_`、`IMG_MGMT_DATA_SHA_LEN`、`IMG_MGMT_ID_CORELIST`、`IMG_MGMT_ID_CORELOAD`、`IMG_MGMT_ID_ERASE`、`IMG_MGMT_ID_FILE`、`IMG_MGMT_ID_SLOT_INFO`、`IMG_MGMT_ID_STATE`、`IMG_MGMT_ID_UPLOAD`、`IMG_MGMT_STATE_F_ACTIVE`、`IMG_MGMT_STATE_F_CONFIRMED`、`IMG_MGMT_STATE_F_PENDING`、`IMG_MGMT_STATE_F_PERMANENT`、`IMG_MGMT_SWAP_TYPE_NONE`、`IMG_MGMT_SWAP_TYPE_PERM`、`IMG_MGMT_SWAP_TYPE_REVERT`、`IMG_MGMT_SWAP_TYPE_TEST`、`IMG_MGMT_SWAP_TYPE_UNKNOWN`、`IMG_MGMT_UPLOAD_ACTION_RC_RSN`、`IMG_MGMT_UPLOAD_ACTION_SET_RC_RSN`、`IMG_MGMT_VER_MAX_STR_LEN` |

## `img_mgmt_write.h`

`vendor/sdk-nrf-bm/include/bm/mgmt/mcumgr/grp/img_mgmt/img_mgmt_write.h:1-40`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `img_mgmt_write_in_progress` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `BM_H_IMG_MGMT_WRITE_` |

## `ble_rmem.h`

`vendor/sdk-nrf-bm/include/bm/storage/ble_rmem.h:1-33`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `ble_rmem_adv_name_get` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `BLE_RMEM_MAX_NAME_SIZE` |

## `bm_rmem.h`

`vendor/sdk-nrf-bm/include/bm/storage/bm_rmem.h:1-111`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_rmem_clear`、`bm_rmem_crc32_verify`、`bm_rmem_crc32_write`、`bm_rmem_data_get`、`bm_rmem_data_write`、`bm_rmem_init`、`bm_rmem_init_empty` |
| struct・enum・typedef・callback | `bm_retained_clipboard_ctx`、`bm_rmem_data_desc` |
| enum 値・event 定数 | なし |
| 定義 macro | `BM_RMEM_TLV_TYPE_BLE_NAME`、`BM_RMEM_TLV_TYPE_CRC_32` |

## `bm_storage.h`

`vendor/sdk-nrf-bm/include/bm/storage/bm_storage.h:1-359`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_storage_erase`、`bm_storage_evt_dispatch`、`bm_storage_init`、`bm_storage_is_busy`、`bm_storage_nvm_info_get`、`bm_storage_read`、`bm_storage_uninit`、`bm_storage_write` |
| struct・enum・typedef・callback | `bm_storage`、`bm_storage_api`、`bm_storage_config`、`bm_storage_evt`、`bm_storage_evt_handler_t`、`bm_storage_evt_type`、`bm_storage_info`、`erase`、`flags`、`init`、`is_busy`、`read`、`uninit`、`write` |
| enum 値・event 定数 | `BM_STORAGE_EVT_ERASE_RESULT`、`BM_STORAGE_EVT_WRITE_RESULT` |
| 定義 macro | なし |

## `bm_storage_backends.h`

`vendor/sdk-nrf-bm/include/bm/storage/bm_storage_backends.h:1-41`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `bm_installs.h`

`vendor/sdk-nrf-bm/subsys/bm_installs/include/bm_installs.h:1-88`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_installs_get_image_data`、`bm_installs_init`、`bm_installs_is_valid`、`bm_installs_read` |
| struct・enum・typedef・callback | `bm_installs`、`bm_installs_image`、`bm_installs_image_indexes` |
| enum 値・event 定数 | `BM_INSTALLS_IMAGE_INDEX_COUNT`、`BM_INSTALLS_IMAGE_INDEX_FIRMWARE_LOADER`、`BM_INSTALLS_IMAGE_INDEX_SOFTDEVICE` |
| 定義 macro | `BM_INSTALLS_PADDING_SIZE` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
