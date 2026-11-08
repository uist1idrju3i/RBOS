# Bluetooth servicesのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `subsys/bluetooth/services/ble_bas/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_BAS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE | bool "Battery service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_bas/Kconfig:6-10` |

## `subsys/bluetooth/services/ble_bas_client/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_BAS_CLIENT` | 未宣言 | SOFTDEVICE_CENTRAL; NRF_SDH_BLE; BLE_DB_DISCOVERY; BLE_GATT_QUEUE | select EXPERIMENTAL; bool "Bluetooth LE battery service client [EXPERIMENTAL]" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_bas_client/Kconfig:7-16` |

## `subsys/bluetooth/services/ble_bms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_BMS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE; BLE_QWR | select EXPERIMENTAL; bool "Bond management service [EXPERIMENTAL]" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_bms/Kconfig:6-12` |

## `subsys/bluetooth/services/ble_cgms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_CGMS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE; BLE_GATT_QUEUE; BLE_RACP | select EXPERIMENTAL; bool "Continuous glucose monitoring service [EXPERIMENTAL]" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_cgms/Kconfig:6-13` |
| `BLE_CGMS_DB_RECORDS_MAX` | 100 | if BLE_CGMS | int "Number of records that can be stored in the database" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_cgms/Kconfig:16-23` |

## `subsys/bluetooth/services/ble_dis/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_DIS` | 未宣言 | SOFTDEVICE | bool "Device Information service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:6-9` |
| `BLE_DIS_MANUFACTURER_NAME` | "Nordic Semiconductor" | if BLE_DIS | string "Manufacturer name" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:12-17` |
| `BLE_DIS_MODEL_NUMBER` | SOC | if BLE_DIS | string "Model number" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:18-23` |
| `BLE_DIS_SERIAL_NUMBER` | 未宣言 | if BLE_DIS | string "Serial number" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:24-28` |
| `BLE_DIS_HW_REVISION` | 未宣言 | if BLE_DIS | string "Hardware revision" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:29-33` |
| `BLE_DIS_FW_REVISION` | 未宣言 | if BLE_DIS | string "Firmware revision" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:34-38` |
| `BLE_DIS_SW_REVISION` | 未宣言 | if BLE_DIS | string "Software revision" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:39-43` |
| `BLE_DIS_SYSTEM_ID` | 未宣言 | if BLE_DIS | bool "Include System ID characteristic" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:44-48` |
| `BLE_DIS_SYSTEM_ID_OUI` | 未宣言 | BLE_DIS_SYSTEM_ID; if BLE_DIS | range 0 0xFFFFFF # 3 bytes; hex "Organizationally unique ID" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:49-53` |
| `BLE_DIS_SYSTEM_ID_MID` | 未宣言 | BLE_DIS_SYSTEM_ID; if BLE_DIS | range 0 0xFFFFFFFFFF # 5 bytes; hex "Manufacturer unique ID" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:54-58` |
| `BLE_DIS_PNP_ID` | 未宣言 | if BLE_DIS | bool "Include Plug and Play ID characteristic" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:59-63` |
| `BLE_DIS_PNP_VID_SRC` | 1 | if BLE_DIS; if BLE_DIS_PNP_ID | range 1 2; hex "PnP vendor ID source" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:66-70` |
| `BLE_DIS_PNP_VID` | 0 | if BLE_DIS; if BLE_DIS_PNP_ID | range 0 0xFFFF; hex "PnP vendor ID" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:71-75` |
| `BLE_DIS_PNP_PID` | 0 | if BLE_DIS; if BLE_DIS_PNP_ID | range 0 0xFFFF; hex "PnP product ID" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:76-80` |
| `BLE_DIS_PNP_VER` | 1 | if BLE_DIS; if BLE_DIS_PNP_ID | range 0 0xFFFF; hex "PnP product version" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:81-85` |
| `BLE_DIS_REGULATORY_CERT` | 未宣言 | if BLE_DIS | bool "Include IEEE regulatory certifications" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:88-90` |
| `BLE_DIS_REGULATORY_CERT_LIST` | 未宣言 | if BLE_DIS; if BLE_DIS_REGULATORY_CERT | range 0 0xFFFFFFFFFFFFFFFF # 8 bytes, 1 byte per entry; hex "Regulatory certification list" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_dis/Kconfig:93-96` |

## `subsys/bluetooth/services/ble_hids/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_HIDS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE | bool "HID service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:6-10` |
| `BLE_HIDS_BOOT_MOUSE` | 未宣言 | if BLE_HIDS | bool "Add boot mouse input characteristic" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:13-17` |
| `BLE_HIDS_BOOT_KEYBOARD` | 未宣言 | if BLE_HIDS | bool "Add boot keyboard characteristics" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:18-22` |
| `BLE_HIDS_PROTOCOL_MODE_REPORT` | 未宣言 | if BLE_HIDS | bool "Report" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:27-29` |
| `BLE_HIDS_PROTOCOL_MODE_BOOT` | 未宣言 | if BLE_HIDS | bool "Boot" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:30-32` |
| `BLE_HIDS_DEFAULT_PROTOCOL_MODE` | 0 if BLE_HIDS_PROTOCOL_MODE_BOOT; 1 if BLE_HIDS_PROTOCOL_MODE_REPORT | if BLE_HIDS | int | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:35-39` |
| `BLE_HIDS_INPUT_REPORT_MAX_NUM` | 10 | if BLE_HIDS | range 0 10; int "Number of input reports" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:40-46` |
| `BLE_HIDS_INPUT_REPORT_MAX_LEN` | 0 if (BLE_HIDS_INPUT_REPORT_MAX_NUM = 0); 8 | if BLE_HIDS | int "Maximum input report length" if (BLE_HIDS_INPUT_REPORT_MAX_NUM != 0) | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:47-51` |
| `BLE_HIDS_OUTPUT_REPORT_MAX_NUM` | 10 | if BLE_HIDS | range 0 10; int "Number of output reports" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:52-58` |
| `BLE_HIDS_OUTPUT_REPORT_MAX_LEN` | 0 if (BLE_HIDS_OUTPUT_REPORT_MAX_NUM = 0); 1 | if BLE_HIDS | int "Maximum output report length" if (BLE_HIDS_OUTPUT_REPORT_MAX_NUM != 0) | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:59-63` |
| `BLE_HIDS_FEATURE_REPORT_MAX_NUM` | 10 | if BLE_HIDS | range 0 10; int "Number of feature reports" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:64-70` |
| `BLE_HIDS_FEATURE_REPORT_MAX_LEN` | 0 if (BLE_HIDS_FEATURE_REPORT_MAX_NUM = 0); 2 | if BLE_HIDS | int "Maximum feature report length" if (BLE_HIDS_FEATURE_REPORT_MAX_NUM != 0) | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:71-75` |
| `BLE_HIDS_MAX_CLIENTS` | 1 | if BLE_HIDS | range 1 NRF_SDH_BLE_PERIPHERAL_LINK_COUNT; int "Maximum HID clients" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:76-84` |

- choice（prompt "Default HID protocol mode"; depends on BLE_HIDS_BOOT_KEYBOARD &#124;&#124; BLE_HIDS_BOOT_MOUSE）: `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:23-33`

## `subsys/bluetooth/services/ble_hrs/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_HRS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE; BLE_CONN_PARAMS_AUTO_ATT_MTU | bool "Heart rate service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hrs/Kconfig:6-11` |
| `BLE_HRS_MAX_BUFFERED_RR_INTERVALS` | 20 | if BLE_HRS | int "Size of RR Interval buffers" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hrs/Kconfig:14-21` |

## `subsys/bluetooth/services/ble_hrs_client/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_HRS_CLIENT` | 未宣言 | SOFTDEVICE_CENTRAL; NRF_SDH_BLE; BLE_DB_DISCOVERY; BLE_GATT_QUEUE | bool "Bluetooth LE Heart Rate Service client" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hrs_client/Kconfig:7-15` |
| `BLE_HRS_CLIENT_RR_INTERVALS_MAX_COUNT` | 20 | if BLE_HRS_CLIENT | int "Maximum number of RR intervals per HRM notification" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hrs_client/Kconfig:18-28` |

## `subsys/bluetooth/services/ble_lbs/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_LBS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE | bool "Nordic LED Button Service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_lbs/Kconfig:7-11` |

## `subsys/bluetooth/services/ble_mcumgr/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_MCUMGR` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE; BLE_CONN_PARAMS; NCS_BM_MCUMGR | bool "MCUmgr service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_mcumgr/Kconfig:7-13` |

## `subsys/bluetooth/services/ble_nus/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_NUS` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE; BLE_QWR | bool "Nordic UART service" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_nus/Kconfig:6-11` |

## `subsys/bluetooth/services/ble_nus_client/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_NUS_CLIENT` | 未宣言 | SOFTDEVICE_CENTRAL; NRF_SDH_BLE; BLE_DB_DISCOVERY; BLE_GATT_QUEUE | select EXPERIMENTAL; bool "Nordic UART service client [EXPERIMENTAL]" | `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_nus_client/Kconfig:6-15` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
