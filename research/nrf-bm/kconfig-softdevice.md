# SoftDevice handlerのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `subsys/softdevice/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SOFTDEVICE` | 未宣言 | ZERO_LATENCY_IRQS | imply NRF_SDH; bool "SoftDevice is present" | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:8-12` |
| `SOFTDEVICE_PERIPHERAL` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:13-15` |
| `SOFTDEVICE_CENTRAL` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:16-18` |
| `SOFTDEVICE_DATA_LENGTH_UPDATE` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:19-21` |
| `SOFTDEVICE_EXTENDED_ADVERTISING` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:22-24` |
| `SOFTDEVICE_QOS_CHANNEL_SURVEY_REPORT` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:25-27` |
| `SOFTDEVICE_S115` | 未宣言 | SOC_SERIES_NRF54L; if SOFTDEVICE | select SOFTDEVICE_PERIPHERAL; select SOFTDEVICE_DATA_LENGTH_UPDATE; bool "s115 SoftDevice" | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:33-38` |
| `SOFTDEVICE_S145` | 未宣言 | SOC_SERIES_NRF54L; if SOFTDEVICE | select SOFTDEVICE_PERIPHERAL; select SOFTDEVICE_CENTRAL; select SOFTDEVICE_EXTENDED_ADVERTISING; select SOFTDEVICE_DATA_LENGTH_UPDATE; bool "s145 SoftDevice" | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:39-46` |
| `SOFTDEVICE_VARIANT_STR` | "s115" if SOFTDEVICE_S115; "s145" if SOFTDEVICE_S145 | if SOFTDEVICE | string | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:49-56` |
| `SOFTDEVICE_SOC_VARIANT_STR` | "nrf54l" if SOC_NRF54L15 &#124;&#124; SOC_NRF54L10 &#124;&#124; SOC_NRF54L05; "nrf54lm" if SOC_NRF54LM20A; "nrf54ls" if SOC_NRF54LS05B; "nrf54lv" if SOC_NRF54LV10A | if SOFTDEVICE | string | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:57-66` |
| `CLOCK_CONTROL` | n if SOFTDEVICE | 直接指定なし |  | `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:71-72` |

- choice（prompt "SoftDevice variant"）: `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:30-47`

## `subsys/softdevice_handler/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `NRF_SDH` | 未宣言 | SOFTDEVICE | bool "SoftDevice handler" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:6-9` |
| `NRF_SDH_BLE` | y | if NRF_SDH | bool "Bluetooth LE events" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:12-15` |
| `NRF_SDH_DISPATCH_MODEL_IRQ` | 未宣言 | if NRF_SDH | bool "Interrupt" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:20-25` |
| `NRF_SDH_DISPATCH_MODEL_SCHED` | 未宣言 | BM_SCHEDULER; if NRF_SDH | bool "Scheduler" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:26-31` |
| `NRF_SDH_DISPATCH_MODEL_POLL` | 未宣言 | if NRF_SDH | bool "Manual (poll)" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:32-37` |
| `NRF_SDH_DISPATCH_MODEL` | 0 if NRF_SDH_DISPATCH_MODEL_IRQ; 1 if NRF_SDH_DISPATCH_MODEL_SCHED; 2 if NRF_SDH_DISPATCH_MODEL_POLL | if NRF_SDH | int | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:40-45` |
| `NRF_SDH_CLOCK_LF_SRC_RC` | 未宣言 | NRF_GRTC_TIMER_SOURCE_LFLPRC; if NRF_SDH | bool "LFRC" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:53-56` |
| `NRF_SDH_CLOCK_LF_SRC_XO` | 未宣言 | $(dt_nodelabel_enabled,lfxo); NRF_GRTC_TIMER_SOURCE_LFXO; if NRF_SDH | bool "LFXO" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:57-60` |
| `NRF_SDH_CLOCK_LF_SRC` | 0 if NRF_SDH_CLOCK_LF_SRC_RC; 1 if NRF_SDH_CLOCK_LF_SRC_XO | if NRF_SDH | int | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:63-67` |
| `NRF_SDH_CLOCK_LF_RC_CTIV` | 16 if NRF_SDH_CLOCK_LF_SRC_RC; 0 | if NRF_SDH | range 1 32 if NRF_SDH_CLOCK_LF_SRC_RC; int "Calibration timer interval (1/4 second units)" if NRF_SDH_CLOCK_LF_SRC_RC | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:68-77` |
| `NRF_SDH_CLOCK_LF_RC_TEMP_CTIV` | 2 if NRF_SDH_CLOCK_LF_SRC_RC; 0 | if NRF_SDH | range 0 33 if NRF_SDH_CLOCK_LF_SRC_RC; int "How often to calibrate if the temperature hasn't changed" if NRF_SDH_CLOCK_LF_SRC_RC | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:78-90` |
| `NRF_SDH_CLOCK_LF_ACCURACY_500_PPM` | 未宣言 | if NRF_SDH | bool "500 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:96-98` |
| `NRF_SDH_CLOCK_LF_ACCURACY_250_PPM` | 未宣言 | if NRF_SDH | bool "250 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:99-101` |
| `NRF_SDH_CLOCK_LF_ACCURACY_150_PPM` | 未宣言 | if NRF_SDH | bool "150 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:102-104` |
| `NRF_SDH_CLOCK_LF_ACCURACY_100_PPM` | 未宣言 | if NRF_SDH | bool "100 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:105-107` |
| `NRF_SDH_CLOCK_LF_ACCURACY_75_PPM` | 未宣言 | if NRF_SDH | bool "75 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:108-110` |
| `NRF_SDH_CLOCK_LF_ACCURACY_50_PPM` | 未宣言 | if NRF_SDH | bool "50 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:111-113` |
| `NRF_SDH_CLOCK_LF_ACCURACY_30_PPM` | 未宣言 | if NRF_SDH | bool "30 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:114-116` |
| `NRF_SDH_CLOCK_LF_ACCURACY_20_PPM` | 未宣言 | if NRF_SDH | bool "20 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:117-119` |
| `NRF_SDH_CLOCK_LF_ACCURACY_10_PPM` | 未宣言 | if NRF_SDH | bool "10 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:120-122` |
| `NRF_SDH_CLOCK_LF_ACCURACY_5_PPM` | 未宣言 | if NRF_SDH | bool "5 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:123-125` |
| `NRF_SDH_CLOCK_LF_ACCURACY_2_PPM` | 未宣言 | if NRF_SDH | bool "2 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:126-128` |
| `NRF_SDH_CLOCK_LF_ACCURACY_1_PPM` | 未宣言 | if NRF_SDH | bool "1 ppm" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:129-130` |
| `NRF_SDH_CLOCK_LF_ACCURACY` | 0 if NRF_SDH_CLOCK_LF_ACCURACY_250_PPM; 1 if NRF_SDH_CLOCK_LF_ACCURACY_500_PPM; 2 if NRF_SDH_CLOCK_LF_ACCURACY_150_PPM; 3 if NRF_SDH_CLOCK_LF_ACCURACY_100_PPM; 4 if NRF_SDH_CLOCK_LF_ACCURACY_75_PPM; 5 if NRF_SDH_CLOCK_LF_ACCURACY_50_PPM; 6 if NRF_SDH_CLOCK_LF_ACCURACY_30_PPM; 7 if NRF_SDH_CLOCK_LF_ACCURACY_20_PPM; 8 if NRF_SDH_CLOCK_LF_ACCURACY_10_PPM; 9 if NRF_SDH_CLOCK_LF_ACCURACY_5_PPM; 10 if NRF_SDH_CLOCK_LF_ACCURACY_2_PPM; 11 if NRF_SDH_CLOCK_LF_ACCURACY_1_PPM; 0 | if NRF_SDH | int | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:133-148` |
| `NRF_SDH_CLOCK_HFINT_CALIBRATION_INTERVAL` | 60 | if NRF_SDH | range 1 255; int "HFINT calibration interval in seconds" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:149-153` |
| `NRF_SDH_CLOCK_HFCLK_LATENCY` | 1500 | if NRF_SDH | range 0 $(UINT16_MAX); int "Ramp-up time of the high-frequency crystal oscillator in microseconds" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:154-158` |
| `NRF_SDH_BLE_CONN_TAG` | 99 | if NRF_SDH; if NRF_SDH_BLE | range 1 255; int "Connection tag" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:165-171` |
| `NRF_SDH_BLE_PERIPHERAL_LINK_COUNT` | 1 | SOFTDEVICE_PERIPHERAL; if NRF_SDH; if NRF_SDH_BLE | range 0 NRF_SDH_BLE_TOTAL_LINK_COUNT; int "Maximum number of peripheral links" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:172-177` |
| `NRF_SDH_BLE_CENTRAL_LINK_COUNT` | 0 | SOFTDEVICE_CENTRAL; if NRF_SDH; if NRF_SDH_BLE | range 0 NRF_SDH_BLE_TOTAL_LINK_COUNT; int "Maximum number of central links" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:178-183` |
| `NRF_SDH_BLE_TOTAL_LINK_COUNT` | 1 | if NRF_SDH; if NRF_SDH_BLE | range 0 2 if SOFTDEVICE_S115; range 0 5 if SOFTDEVICE_S145; range 1 64; int "Maximum number of total concurrent connections" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:184-190` |
| `NRF_SDH_BLE_GAP_EVENT_LENGTH` | 3 | if NRF_SDH; if NRF_SDH_BLE | range 2 3200; int "GAP event length (1.25 ms units)" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:191-198` |
| `NRF_SDH_BLE_GATT_MAX_MTU_SIZE` | 23 | if NRF_SDH; if NRF_SDH_BLE | range 23 $(UINT16_MAX); int "Maximum MTU size" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:199-208` |
| `NRF_SDH_BLE_GATTS_ATTR_TAB_SIZE` | 1408 | if NRF_SDH; if NRF_SDH_BLE | range 248 $(UINT32_MAX); int "Attribute Table size in bytes" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:209-218` |
| `NRF_SDH_BLE_VS_UUID_COUNT` | 0 | if NRF_SDH; if NRF_SDH_BLE | int "Number of vendor-specific UUIDs" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:219-222` |
| `NRF_SDH_BLE_SERVICE_CHANGED` | 未宣言 | if NRF_SDH; if NRF_SDH_BLE | bool "Include the Service Changed characteristic in the Attribute Table" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:223-225` |
| `NRF_SDH_BLE_LOG_SD_RAM_USAGE` | 未宣言 | if NRF_SDH; if NRF_SDH_BLE | bool "Log RAM usage on BLE enable" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:226-233` |
| `NRF_SDH_SOC_RAND_SEED` | y | NRF_SECURITY; MBEDTLS_PSA_CRYPTO_C; if NRF_SDH | bool "Automatically seed SoftDevice random" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:238-245` |
| `NRF_SDH_STR_TABLES` | y | if NRF_SDH | bool "Build string tables for SoftDevice events" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:246-252` |
| `NRF_SDH_LOG_SD_INFO` | 未宣言 | if NRF_SDH | bool "Log SoftDevice information on enable" | `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:253-262` |

- choice（prompt "Dispatch model"; default NRF_SDH_DISPATCH_MODEL_SCHED）: `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:16-38`

- choice（prompt "Low-frequency clock source"; default NRF_SDH_CLOCK_LF_SRC_XO; default NRF_SDH_CLOCK_LF_SRC_RC）: `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:48-61`

- choice（prompt "Clock accuracy"; default NRF_SDH_CLOCK_LF_ACCURACY_500_PPM if NRF_SDH_CLOCK_LF_SRC_RC; default NRF_SDH_CLOCK_LF_ACCURACY_250_PPM）: `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:91-131`

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
