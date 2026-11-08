# samplesのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `samples/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MULTITHREADING` | n if (!UNITY && !(ZTEST && BOARD_NATIVE_SIM)) | 直接指定なし |  | `vendor/sdk-nrf-bm/samples/Kconfig:10-13` |
| `GEN_SW_ISR_TABLE` | n if !MULTITHREADING | 直接指定なし |  | `vendor/sdk-nrf-bm/samples/Kconfig:14-18` |
| `PARTITION_MANAGER_ENABLED` | n | 直接指定なし |  | `vendor/sdk-nrf-bm/samples/Kconfig:19-20` |

## `samples/bluetooth/ble_bms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_BMS" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/Kconfig:9-12` |
| `SAMPLE_QWR_MEM_BUFF_SIZE` | 512 | 直接指定なし | int "QWR memory buffer size" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/Kconfig:13-16` |
| `SAMPLE_BLE_BMS_PEERS_TO_DELETE_ON_DISCONNECT_MAX` | 10 | 直接指定なし | int "Maximum number of peers to delete upon a peer disconnect" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/Kconfig:17-20` |
| `SAMPLE_BLE_BMS_USE_AUTHORIZATION_CODE` | y | 直接指定なし | bool "Use authorization code" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/Kconfig:21-24` |
| `SAMPLE_BLE_BMS_AUTHORIZATION_CODE` | "ABCD" | 直接指定なし | string "Authorization code" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/Kconfig:25-32` |

## `samples/bluetooth/ble_cgms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_CGMS" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:9-12` |
| `SAMPLE_QWR_MEM_BUFF_SIZE` | 512 | 直接指定なし | int "QWR memory buffer size" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:13-16` |
| `SAMPLE_GLUCOSE_MEAS_INTERVAL` | 1 | 直接指定なし | int "Fastest possible communication interval" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:21-24` |
| `SAMPLE_GLUCOSE_CONCENTRATION_INC` | 10 | 直接指定なし | int "Glucose concentration increment on button press" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:25-30` |
| `SAMPLE_GLUCOSE_CONCENTRATION_DEC` | 5 | 直接指定なし | int "Glucose concentration increment on button press" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:31-36` |
| `SAMPLE_GLUCOSE_CONCENTRATION_MAX` | 800 | 直接指定なし | int "Maximum glucose concentration (mg/dL)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:37-40` |
| `SAMPLE_GLUCOSE_CONCENTRATION_MIN` | 5 | 直接指定なし | int "Minimum glucose concentration (mg/dL)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/Kconfig:41-44` |

## `samples/bluetooth/ble_hids_keyboard/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_HIDS_KB" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hids_keyboard/Kconfig:9-12` |
| `SAMPLE_BLE_HIDS_REPORT_FIFO_SIZE` | 10 | 直接指定なし | int "Report FIFO size" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hids_keyboard/Kconfig:13-20` |

## `samples/bluetooth/ble_hids_mouse/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_HIDS_MOUSE" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hids_mouse/Kconfig:9-16` |

## `samples/bluetooth/ble_hrs/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_HRS" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:9-12` |
| `SAMPLE_BATTERY_LEVEL_MEAS_INTERVAL` | 2000 | 直接指定なし | int "Battery level measurement interval (ms)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:15-20` |
| `SAMPLE_BATTERY_LEVEL_MIN` | 81 | 直接指定なし | int "Minimum simulated battery level (%)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:21-26` |
| `SAMPLE_BATTERY_LEVEL_MAX` | 100 | 直接指定なし | int "Maximum simulated battery level (%)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:27-32` |
| `SAMPLE_BATTERY_LEVEL_INCREMENT` | 1 | 直接指定なし | int "Simulated battery level increment/decrement (%)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:33-39` |
| `SAMPLE_HEART_RATE_MEAS_INTERVAL` | 1000 | 直接指定なし | int "Heart rate measurement interval (ms)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:44-49` |
| `SAMPLE_HEART_RATE_MIN` | 140 | 直接指定なし | int "Minimum simulated heart rate (bpm)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:50-55` |
| `SAMPLE_HEART_RATE_MAX` | 300 | 直接指定なし | int "Maximum simulated heart rate (bpm)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:56-61` |
| `SAMPLE_HEART_RATE_INCREMENT` | 10 | 直接指定なし | int "Simulated heart rate increment/decrement (bpm)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:62-68` |
| `SAMPLE_RR_INTERVAL_MEAS_INTERVAL` | 300 | 直接指定なし | int "RR interval measurement interval (ms)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:73-78` |
| `SAMPLE_RR_INTERVAL_MIN` | 100 | 直接指定なし | int "Minimum simulated RR interval (in 1/1024 sec units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:79-85` |
| `SAMPLE_RR_INTERVAL_MAX` | 500 | 直接指定なし | int "Maximum simulated RR interval (in 1/1024 sec units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:86-92` |
| `SAMPLE_RR_INTERVAL_INCREMENT` | 1 | 直接指定なし | int "Simulated RR interval increment/decrement (in 1/1024 sec units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:93-100` |
| `SAMPLE_SENSOR_CONTACT_DETECTED_INTERVAL` | 5000 | 直接指定なし | int "Sensor contact detected toggle interval (ms)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/Kconfig:105-110` |

## `samples/bluetooth/ble_hrs_central/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_HRS_C" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/Kconfig:9-12` |
| `SAMPLE_USE_TARGET_PERIPHERAL_NAME` | y | 直接指定なし | bool "Use target peripheral name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/Kconfig:13-16` |
| `SAMPLE_TARGET_PERIPHERAL_NAME` | "nRF_BM_HRS" | if SAMPLE_USE_TARGET_PERIPHERAL_NAME | string "Target peripheral name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/Kconfig:19-22` |
| `SAMPLE_USE_TARGET_PERIPHERAL_ADDR` | 未宣言 | 直接指定なし | bool "Use target peripheral address" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/Kconfig:25-27` |
| `SAMPLE_TARGET_PERIPHERAL_ADDR` | 0x78E7F806C5D8 | if SAMPLE_USE_TARGET_PERIPHERAL_ADDR | range 0x0 0xffffffffffff; hex "Target peripheral address" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/Kconfig:30-34` |

## `samples/bluetooth/ble_lbs/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_LBS" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_lbs/Kconfig:9-16` |

## `samples/bluetooth/ble_nus/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_NUS" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:9-12` |
| `SAMPLE_NUS_UART_IRQ_PRIO` | 5 | 直接指定なし | range 2 7; int "NUS UART IRQ priority" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:13-20` |
| `SAMPLE_NUS_UART_PARITY` | 未宣言 | if you want to call into SoftDevice from the interrupt driver. | bool "Bluetooth LE UART use parity" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:23-25` |
| `SAMPLE_NUS_LPUARTE` | 未宣言 | if you want to call into SoftDevice from the interrupt driver. | bool "NUS Low Power UARTE" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:26-28` |
| `SAMPLE_NUS_UART_HWFC` | y | !SAMPLE_NUS_LPUARTE; if you want to call into SoftDevice from the interrupt driver. | bool "NUS UART use HWFC" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:33-37` |
| `SAMPLE_NUS_UART_RX_BUF_SIZE` | 128 if SAMPLE_NUS_LPUARTE; 1 | if you want to call into SoftDevice from the interrupt driver. | int "NUS UART receive buffer size" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/Kconfig:38-48` |

## `samples/bluetooth/ble_nus_central/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_NUS_C" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:9-12` |
| `SAMPLE_NUS_UART_IRQ_PRIO` | 5 | 直接指定なし | range 2 7; int "NUS UART IRQ priority" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:13-20` |
| `SAMPLE_NUS_CENTRAL_UART_RX_BUF_SIZE` | 128 if SAMPLE_NUS_CENTRAL_LPUARTE; 1 | if you want to call into SoftDevice from the interrupt driver. | int "NUS UART receive buffer size" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:23-29` |
| `SAMPLE_USE_TARGET_PERIPHERAL_NAME` | y | if you want to call into SoftDevice from the interrupt driver. | bool "Use target peripheral name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:30-33` |
| `SAMPLE_NUS_CENTRAL_LPUARTE` | 未宣言 | if you want to call into SoftDevice from the interrupt driver. | bool "NUS Client Low Power UARTE" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:34-36` |
| `SAMPLE_TARGET_PERIPHERAL_NAME` | "nRF_BM_NUS" | if you want to call into SoftDevice from the interrupt driver.; if SAMPLE_USE_TARGET_PERIPHERAL_NAME | string "Target peripheral name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:39-42` |
| `SAMPLE_USE_TARGET_PERIPHERAL_ADDR` | 未宣言 | if you want to call into SoftDevice from the interrupt driver. | bool "Use target peripheral address" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:45-47` |
| `SAMPLE_TARGET_PERIPHERAL_ADDR` | 0x78E7F806C5D8 | if you want to call into SoftDevice from the interrupt driver.; if SAMPLE_USE_TARGET_PERIPHERAL_ADDR | range 0x0 0xffffffffffff; hex "Target peripheral address" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/Kconfig:50-54` |

## `samples/bluetooth/ble_pwr_profiling/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "Nordic_Power_Profiling" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:9-12` |
| `SAMPLE_BLE_PWR_PROFILING_CONN_ADVERTISING_TIMEOUT` | 3000 | 直接指定なし | range 0 18000; int "Connectable advertising timeout (10 ms units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:13-17` |
| `SAMPLE_BLE_PWR_PROFILING_CONN_ADVERTISING_INTERVAL` | 160 | 直接指定なし | range 32 16384; int "Connectable advertising interval (0.625 ms units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:18-22` |
| `SAMPLE_BLE_PWR_PROFILING_NONCONN_ADVERTISING_TIMEOUT` | 6000 | 直接指定なし | range 0 18000; int "Non-connectable advertising timeout (10 ms units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:23-27` |
| `SAMPLE_BLE_PWR_PROFILING_NONCONN_ADVERTISING_INTERVAL` | 1600 | 直接指定なし | range 32 16384; int "Non-connectable advertising interval (0.625 ms units)" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:28-32` |
| `SAMPLE_BLE_PWR_PROFILING_NOTIF_CONNECTION_TIMEOUT` | 10000 | 直接指定なし | int "Notification connection timeout" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:33-38` |
| `SAMPLE_BLE_PWR_PROFILING_CHAR_VALUE_LEN` | 20 | 直接指定なし | int "Size of characteristic value" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:39-42` |
| `SAMPLE_BLE_PWR_PROFILING_LED` | 未宣言 | 直接指定なし | bool "Power profiling LED" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/Kconfig:43-49` |

## `samples/bluetooth/ble_radio_notification/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_Radio_Ntf" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_radio_notification/Kconfig:9-12` |
| `SAMPLE_BLE_RADIO_NOTIFICATION_DISTANCE_US` | 800 | 直接指定なし | range 50 5500; int "Distance between the active notification signal and start of radio event preparation" | `vendor/sdk-nrf-bm/samples/bluetooth/ble_radio_notification/Kconfig:13-21` |

## `samples/bluetooth/peripheral_nfc_pairing/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_Nordic_NFC_pairing" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/bluetooth/peripheral_nfc_pairing/Kconfig:9-16` |

## `samples/boot/mcuboot_recovery_entry/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BLE_DEVICE_NAME` | "nRF_BM_Entry" | 直接指定なし | string "Device name" | `vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_entry/Kconfig:9-16` |

## `samples/peripherals/lpuarte/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_LPUARTE_DATA_LEN_MAX` | 128 | 直接指定なし | int "Maximum UARTE data length" | `vendor/sdk-nrf-bm/samples/peripherals/lpuarte/Kconfig:9-14` |
| `SAMPLE_LPUARTE_PARITY` | 未宣言 | 直接指定なし | bool "UARTE parity" | `vendor/sdk-nrf-bm/samples/peripherals/lpuarte/Kconfig:15-19` |
| `SAMPLE_LPUARTE_IRQ_PRIO` | 5 if SOFTDEVICE; 3 | 直接指定なし | range 2 7; int "LPUARTE IRQ priority" | `vendor/sdk-nrf-bm/samples/peripherals/lpuarte/Kconfig:20-28` |
| `SAMPLE_LPUARTE_INIT_LED` | 未宣言 | if you want to call into SoftDevice from the interrupt driver. | bool "LED indicating if application has been initialized" | `vendor/sdk-nrf-bm/samples/peripherals/lpuarte/Kconfig:31-37` |

## `samples/peripherals/ppi/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_TIMER_IRQ_PRIO` | 3 | 直接指定なし | range 2 7; int "Timer IRQ priority" | `vendor/sdk-nrf-bm/samples/peripherals/ppi/Kconfig:9-16` |
| `SAMPLE_LED_BLINK_INTERVAL_MS` | 500 | 直接指定なし | int "LED blink interval in milliseconds" | `vendor/sdk-nrf-bm/samples/peripherals/ppi/Kconfig:17-26` |

## `samples/peripherals/pwm/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_PWM_IRQ_PRIO` | 3 | 直接指定なし | range 2 7; int "PWM IRQ priority" | `vendor/sdk-nrf-bm/samples/peripherals/pwm/Kconfig:9-16` |
| `SAMPLE_PWM_PLAYBACK_COUNT` | 1 | 直接指定なし | int "PWM playback count" | `vendor/sdk-nrf-bm/samples/peripherals/pwm/Kconfig:17-23` |
| `SAMPLE_PWM_VALUE_REPEATS` | 150 | 直接指定なし | int "PWM value repeats" | `vendor/sdk-nrf-bm/samples/peripherals/pwm/Kconfig:24-33` |

## `samples/peripherals/timer/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_PERIODIC_TIMER_INTERVAL_MS` | 500 | 直接指定なし | int "Timeout interval of periodic timer" | `vendor/sdk-nrf-bm/samples/peripherals/timer/Kconfig:9-12` |
| `SAMPLE_HELLO_TIMER_DURATION_MS` | 1000 | 直接指定なし | int "First timeout duration of oneshot timer" | `vendor/sdk-nrf-bm/samples/peripherals/timer/Kconfig:13-16` |
| `SAMPLE_WORLD_TIMER_DURATION_MS` | 2000 | 直接指定なし | int "Second timeout duration of oneshot timer" | `vendor/sdk-nrf-bm/samples/peripherals/timer/Kconfig:17-20` |
| `SAMPLE_BYE_TIMER_DURATION_MS` | 4000 | 直接指定なし | int "Third timeout duration of oneshot timer" | `vendor/sdk-nrf-bm/samples/peripherals/timer/Kconfig:21-28` |

## `samples/peripherals/uarte/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_UARTE_DATA_LEN_MAX` | 128 | 直接指定なし | int "maximum UARTE data length" | `vendor/sdk-nrf-bm/samples/peripherals/uarte/Kconfig:9-14` |
| `SAMPLE_UARTE_HWFC` | 未宣言 | 直接指定なし | bool "UARTE HWFC" | `vendor/sdk-nrf-bm/samples/peripherals/uarte/Kconfig:15-19` |
| `SAMPLE_UARTE_PARITY` | 未宣言 | 直接指定なし | bool "UARTE parity" | `vendor/sdk-nrf-bm/samples/peripherals/uarte/Kconfig:20-24` |
| `SAMPLE_UARTE_IRQ_PRIO` | 5 if SOFTDEVICE; 3 | 直接指定なし | range 2 7; int "UARTE IRQ priority" | `vendor/sdk-nrf-bm/samples/peripherals/uarte/Kconfig:25-33` |

## `samples/subsys/fs/bm_zms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SAMPLE_BM_ZMS_SECTOR_SIZE` | 1024 | 直接指定なし | int "Sector size" | `vendor/sdk-nrf-bm/samples/subsys/fs/bm_zms/Kconfig:9-12` |
| `SAMPLE_BM_ZMS_ITERATIONS_MAX` | 2 | 直接指定なし | int "Number of iterations in total" | `vendor/sdk-nrf-bm/samples/subsys/fs/bm_zms/Kconfig:13-16` |
| `SAMPLE_BM_ZMS_ITERATIONS_DELETE_INTERVAL` | 1 | 直接指定なし | int "Number of iterations between each delete" | `vendor/sdk-nrf-bm/samples/subsys/fs/bm_zms/Kconfig:17-26` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
