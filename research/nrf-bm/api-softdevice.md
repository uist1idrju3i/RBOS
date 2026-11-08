# SoftDevice handlerの公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `nrf_sdh.h`

`vendor/sdk-nrf-bm/include/bm/softdevice_handler/nrf_sdh.h:1-283`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nrf_sdh_disable_request`、`nrf_sdh_enable_request`、`nrf_sdh_evts_poll`、`nrf_sdh_is_suspended`、`nrf_sdh_observer_ready`、`nrf_sdh_resume`、`nrf_sdh_suspend` |
| struct・enum・typedef・callback | `nrf_sdh_stack_evt_handler_t`、`nrf_sdh_stack_evt_observer`、`nrf_sdh_state_evt`、`nrf_sdh_state_evt_handler_t`、`nrf_sdh_state_evt_observer` |
| enum 値・event 定数 | `NRF_SDH_STACK_EVT_OBSERVER`、`NRF_SDH_STATE_EVT_BLE_ENABLED`、`NRF_SDH_STATE_EVT_DISABLED`、`NRF_SDH_STATE_EVT_DISABLE_PREPARE`、`NRF_SDH_STATE_EVT_ENABLED`、`NRF_SDH_STATE_EVT_ENABLE_PREPARE`、`NRF_SDH_STATE_EVT_OBSERVER` |
| 定義 macro | `H_NRF_SDH_OBSERVER_PRIO_HIGHEST_HIGHEST`、`H_NRF_SDH_OBSERVER_PRIO_HIGH_HIGH`、`H_NRF_SDH_OBSERVER_PRIO_LOWEST_LOWEST`、`H_NRF_SDH_OBSERVER_PRIO_USER_LOW_USER_LOW`、`H_NRF_SDH_OBSERVER_PRIO_USER_USER`、`NRF_SDH_STACK_EVT_OBSERVER`、`NRF_SDH_STATE_EVT_OBSERVER`、`PRIO_LEVEL_IS_VALID`、`PRIO_LEVEL_ORD` |

## `nrf_sdh_ble.h`

`vendor/sdk-nrf-bm/include/bm/softdevice_handler/nrf_sdh_ble.h:1-125`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nrf_sdh_ble_conn_handle_get`、`nrf_sdh_ble_enable`、`nrf_sdh_ble_evt_to_str`、`nrf_sdh_ble_idx_get`、`nrf_sdh_ble_sd_ram_usage_get` |
| struct・enum・typedef・callback | `nrf_sdh_ble_evt_handler_t`、`nrf_sdh_ble_evt_observer` |
| enum 値・event 定数 | `BLE_EVT_LEN_MAX`、`NRF_SDH_BLE_EVT_BUF_SIZE` |
| 定義 macro | `NRF_SDH_BLE_EVT_BUF_SIZE`、`NRF_SDH_BLE_OBSERVER` |

## `nrf_sdh_info.h`

`vendor/sdk-nrf-bm/include/bm/softdevice_handler/nrf_sdh_info.h:1-85`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nrf_sdh_info_unique_str_get`、`nrf_sdh_info_version_get` |
| struct・enum・typedef・callback | `nrf_sdh_info_unique_str`、`nrf_sdh_info_version` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `nrf_sdh_soc.h`

`vendor/sdk-nrf-bm/include/bm/softdevice_handler/nrf_sdh_soc.h:1-79`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nrf_sdh_soc_evt_to_str` |
| struct・enum・typedef・callback | `nrf_sdh_soc_evt_handler_t`、`nrf_sdh_soc_evt_observer` |
| enum 値・event 定数 | なし |
| 定義 macro | `NRF_SDH_SOC_OBSERVER` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
