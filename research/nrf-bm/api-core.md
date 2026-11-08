# I/O・イベント・診断の公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `bm_buttons.h`

`vendor/sdk-nrf-bm/include/bm/bm_buttons.h:1-160`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_buttons_deinit`、`bm_buttons_disable`、`bm_buttons_enable`、`bm_buttons_init`、`bm_buttons_is_pressed` |
| struct・enum・typedef・callback | `bm_buttons_active_state`、`bm_buttons_config`、`bm_buttons_evt_type`、`bm_buttons_handler_t`、`bm_buttons_pin_pull` |
| enum 値・event 定数 | `BM_BUTTONS_ACTIVE_HIGH`、`BM_BUTTONS_ACTIVE_LOW`、`BM_BUTTONS_PIN_NOPULL`、`BM_BUTTONS_PIN_PULLDOWN`、`BM_BUTTONS_PIN_PULLUP`、`BM_BUTTONS_PRESS`、`BM_BUTTONS_RELEASE` |
| 定義 macro | `BM_BUTTONS_DETECTION_DELAY_MIN_US` |

## `bm_gpiote.h`

`vendor/sdk-nrf-bm/include/bm/bm_gpiote.h:1-46`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_gpiote_instance_get` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `bm_irq.h`

`vendor/sdk-nrf-bm/include/bm/bm_irq.h:1-81`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `BM_IRQ_DIRECT_CONNECT`、`BM_IRQ_OFFSET`、`BM_IRQ_SET_PRIORITY`、`IS_ZERO_LATENCY` |

## `bm_scheduler.h`

`vendor/sdk-nrf-bm/include/bm/bm_scheduler.h:1-83`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_scheduler_defer`、`bm_scheduler_process` |
| struct・enum・typedef・callback | `bm_scheduler_event`、`bm_scheduler_fn_t` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `bm_timer.h`

`vendor/sdk-nrf-bm/include/bm/bm_timer.h:1-120`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_timer_init`、`bm_timer_start`、`bm_timer_stop` |
| struct・enum・typedef・callback | `bm_timer`、`bm_timer_mode`、`bm_timer_timeout_handler_t` |
| enum 値・event 定数 | `BM_TIMER_MODE_REPEATED`、`BM_TIMER_MODE_SINGLE_SHOT` |
| 定義 macro | `BM_TIMER_MIN_TIMEOUT_TICKS`、`BM_TIMER_MIN_TIMEOUT_US`、`BM_TIMER_MS_TO_TICKS`、`BM_TIMER_US_TO_TICKS` |

## `bm_lpuarte.h`

`vendor/sdk-nrf-bm/include/bm/drivers/bm_lpuarte.h:1-204`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `bm_lpuarte_init`、`bm_lpuarte_rx_abort`、`bm_lpuarte_rx_buffer_set`、`bm_lpuarte_rx_enable`、`bm_lpuarte_tx`、`bm_lpuarte_tx_abort`、`bm_lpuarte_tx_in_progress`、`bm_lpuarte_uninit` |
| struct・enum・typedef・callback | `bm_lpuarte`、`bm_lpuarte_config`、`bm_lpuarte_rx_state` |
| enum 値・event 定数 | `RX_ACTIVE`、`RX_IDLE`、`RX_OFF`、`RX_PREPARE`、`RX_TO_IDLE`、`RX_TO_OFF` |
| 定義 macro | なし |

## `sensorsim.h`

`vendor/sdk-nrf-bm/include/bm/sensorsim.h:1-98`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `sensorsim_init`、`sensorsim_measure` |
| struct・enum・typedef・callback | `sensorsim_cfg`、`sensorsim_state` |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `backend_bm_uarte.h`

`vendor/sdk-nrf-bm/include/bm/shell/backend_bm_uarte.h:1-11`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `shell_backend_bm_uarte_get_ptr`、`shell_backend_bm_uarte_rx_ready` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `nrf_error.h`

`vendor/sdk-nrf-bm/include/nrf_error.h:1-91`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `NRF_ERROR_BUSY`、`NRF_ERROR_CONN_COUNT`、`NRF_ERROR_DATA_SIZE`、`NRF_ERROR_FORBIDDEN`、`NRF_ERROR_INTERNAL`、`NRF_ERROR_INVALID_ADDR`、`NRF_ERROR_INVALID_DATA`、`NRF_ERROR_INVALID_FLAGS`、`NRF_ERROR_INVALID_LENGTH`、`NRF_ERROR_INVALID_PARAM`、`NRF_ERROR_INVALID_STATE`、`NRF_ERROR_NOT_FOUND`、`NRF_ERROR_NOT_SUPPORTED`、`NRF_ERROR_NO_MEM`、`NRF_ERROR_NULL`、`NRF_ERROR_RESOURCES`、`NRF_ERROR_SDM_BASE_NUM`、`NRF_ERROR_SOC_BASE_NUM`、`NRF_ERROR_SOFTDEVICE_NOT_ENABLED`、`NRF_ERROR_STK_BASE_NUM`、`NRF_ERROR_SVC_HANDLER_MISSING`、`NRF_ERROR_TIMEOUT`、`NRF_SUCCESS` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
