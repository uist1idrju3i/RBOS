# Bluetooth 共通・peer managerのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `lib/bluetooth/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_GATT_DB_MAX_CHARS` | 6 | 直接指定なし | int "Maximum number of characteristics in a service record (See ble_gatt_db.h)" | `vendor/sdk-nrf-bm/lib/bluetooth/Kconfig:21-28` |

## `lib/bluetooth/ble_adv/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_ADV` | 未宣言 | SOFTDEVICE_PERIPHERAL; NRF_SDH_BLE | select BLE_ADV_DATA; bool "Bluetooth LE Advertising" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:7-12` |
| `BLE_ADV_RESTART_ON_DISCONNECT` | y | if BLE_ADV | bool "Start advertising upon disconnection" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:15-18` |
| `BLE_ADV_USE_ALLOW_LIST` | 未宣言 | if BLE_ADV | bool "Use allow list" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:19-21` |
| `BLE_ADV_EXTENDED_ADVERTISING` | 未宣言 | SOFTDEVICE_EXTENDED_ADVERTISING; if BLE_ADV | bool "Extended advertising" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:22-25` |
| `BLE_ADV_DIRECTED_ADVERTISING` | 未宣言 | if BLE_ADV | bool "Directed advertising" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:26-28` |
| `BLE_ADV_DIRECTED_ADVERTISING_HIGH_DUTY` | y | BLE_ADV_DIRECTED_ADVERTISING; if BLE_ADV | bool "High duty" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:29-33` |
| `BLE_ADV_DIRECTED_ADVERTISING_TIMEOUT` | 100 | BLE_ADV_DIRECTED_ADVERTISING; if BLE_ADV | range 0 18000; int "Directed advertising timeout (10 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:34-39` |
| `BLE_ADV_DIRECTED_ADVERTISING_INTERVAL` | 32 | BLE_ADV_DIRECTED_ADVERTISING; if BLE_ADV | range 32 16384; int "Directed advertising interval (0.625 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:40-45` |
| `BLE_ADV_FAST_ADVERTISING` | y | if BLE_ADV | bool "Fast advertising" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:46-49` |
| `BLE_ADV_FAST_ADVERTISING_TIMEOUT` | 1000 | BLE_ADV_FAST_ADVERTISING; if BLE_ADV | range 0 18000; int "Fast advertising timeout (10 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:50-55` |
| `BLE_ADV_FAST_ADVERTISING_INTERVAL` | 32 | BLE_ADV_FAST_ADVERTISING; if BLE_ADV | range 32 16384; int "Fast advertising interval (0.625 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:56-61` |
| `BLE_ADV_SLOW_ADVERTISING` | y | if BLE_ADV | bool "Slow advertising" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:62-65` |
| `BLE_ADV_SLOW_ADVERTISING_TIMEOUT` | 18000 | BLE_ADV_SLOW_ADVERTISING; if BLE_ADV | range 0 18000; int "Slow advertising timeout (10 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:66-71` |
| `BLE_ADV_SLOW_ADVERTISING_INTERVAL` | 64 | BLE_ADV_SLOW_ADVERTISING; if BLE_ADV | range 32 16384; int "Slow advertising interval (0.625 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:72-77` |
| `BLE_ADV_PRIMARY_PHY_AUTO` | 未宣言 | if BLE_ADV | bool "Auto" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:82-83` |
| `BLE_ADV_PRIMARY_PHY_1MBPS` | 未宣言 | if BLE_ADV | bool "1 Megabit" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:84-85` |
| `BLE_ADV_PRIMARY_PHY_2MBPS` | 未宣言 | if BLE_ADV | bool "2 Megabits" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:86-87` |
| `BLE_ADV_PRIMARY_PHY_CODED` | 未宣言 | if BLE_ADV | bool "Coded" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:88-89` |
| `BLE_ADV_PRIMARY_PHY` | 0x00 if BLE_ADV_PRIMARY_PHY_AUTO; 0x01 if BLE_ADV_PRIMARY_PHY_1MBPS; 0x02 if BLE_ADV_PRIMARY_PHY_2MBPS; 0x04 if BLE_ADV_PRIMARY_PHY_CODED | if BLE_ADV | hex | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:92-98` |
| `BLE_ADV_SECONDARY_PHY_AUTO` | 未宣言 | if BLE_ADV | bool "Auto" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:103-104` |
| `BLE_ADV_SECONDARY_PHY_1MBPS` | 未宣言 | if BLE_ADV | bool "1 Megabit" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:105-106` |
| `BLE_ADV_SECONDARY_PHY_2MBPS` | 未宣言 | if BLE_ADV | bool "2 Megabits" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:107-108` |
| `BLE_ADV_SECONDARY_PHY_CODED` | 未宣言 | if BLE_ADV | bool "Coded" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:109-110` |
| `BLE_ADV_SECONDARY_PHY` | 0x00 if BLE_ADV_SECONDARY_PHY_AUTO; 0x01 if BLE_ADV_SECONDARY_PHY_1MBPS; 0x02 if BLE_ADV_SECONDARY_PHY_2MBPS; 0x04 if BLE_ADV_SECONDARY_PHY_CODED | if BLE_ADV | hex | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:113-123` |
| `BLE_ADV_DATA` | 未宣言 | SOFTDEVICE | bool "Bluetooth LE Advertising data" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:126-129` |

- choice（prompt "Primary PHY"; default BLE_ADV_PRIMARY_PHY_AUTO）: `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:78-90`

- choice（prompt "Secondary PHY"; default BLE_ADV_SECONDARY_PHY_AUTO）: `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:99-111`

## `lib/bluetooth/ble_conn_params/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_CONN_PARAMS` | 未宣言 | SOFTDEVICE; NRF_SDH; NRF_SDH_BLE | bool "Bluetooth LE Connection Parameters" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:6-11` |
| `BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE` | y | if BLE_CONN_PARAMS | bool "Handle GAP connection parameter updates" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:14-17` |
| `BLE_CONN_PARAMS_MIN_CONN_INTERVAL` | 6 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range 6 3200; int "Minimum connection interval (1.25 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:20-27` |
| `BLE_CONN_PARAMS_MAX_CONN_INTERVAL` | 256 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range BLE_CONN_PARAMS_MIN_CONN_INTERVAL 3200; int "Maximum connection interval (1.25 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:28-35` |
| `BLE_CONN_PARAMS_PERIPHERAL_LATENCY` | 0 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range 0 499; int "Peripheral latency" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:36-42` |
| `BLE_CONN_PARAMS_SUP_TIMEOUT` | 100 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range 10 3200; int "Connection supervision timeout (10 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:43-50` |
| `BLE_CONN_PARAMS_MAX_PERIPHERAL_LATENCY_DEVIATION` | 6 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range 0 499; int "Maximum peripheral latency deviation" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:51-57` |
| `BLE_CONN_PARAMS_MAX_SUP_TIMEOUT_DEVIATION` | 400 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | range 0 3190; int "Maximum supervision timeout deviation (10 ms units)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:58-64` |
| `BLE_CONN_PARAMS_NEGOTIATION_RETRIES` | 2 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | int "Number of attempts to negotiate parameters" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:65-70` |
| `BLE_CONN_PARAMS_DISCONNECT_ON_FAILURE` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_GAP_CONN_PARAM_UPDATE | bool "Disconnect upon failure to negotiate configured parameters" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:71-73` |
| `BLE_CONN_PARAMS_AUTO_ATT_MTU` | y | if BLE_CONN_PARAMS | bool "Handle ATT MTU exchanges" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:76-79` |
| `BLE_CONN_PARAMS_ATT_MTU` | NRF_SDH_BLE_GATT_MAX_MTU_SIZE | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_ATT_MTU | int | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:83-87` |
| `NRF_SDH_BLE_GATT_MAX_MTU_SIZE` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_ATT_MTU | int "ATT MTU" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:88-90` |
| `BLE_CONN_PARAMS_INITIATE_ATT_MTU_EXCHANGE` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_ATT_MTU | bool "Initiate ATT MTU exchange on connection" if BLE_CONN_PARAMS_ATT_MTU != 23 | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:91-93` |
| `BLE_CONN_PARAMS_AUTO_DATA_LENGTH` | y | SOFTDEVICE_DATA_LENGTH_UPDATE; if BLE_CONN_PARAMS | bool "Handle data length updates" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:96-100` |
| `BLE_CONN_PARAMS_DATA_LENGTH_TX` | 27 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_DATA_LENGTH | range 27 251; int "Data length TX" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:103-113` |
| `BLE_CONN_PARAMS_DATA_LENGTH_RX` | 27 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_DATA_LENGTH | range 27 251; int "Data length RX" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:114-124` |
| `BLE_CONN_PARAMS_INITIATE_DATA_LENGTH_UPDATE` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_DATA_LENGTH | bool "Initiate data length update on connection" if BLE_CONN_PARAMS_DATA_LENGTH_TX != 27 &#124;&#124;  BLE_CONN_PARAMS_DATA_LENGTH_RX != 27 | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:125-128` |
| `BLE_CONN_PARAMS_AUTO_PHY_UPDATE` | y | if BLE_CONN_PARAMS | bool "Handle PHY mode updates" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:131-133` |
| `BLE_CONN_PARAMS_PHY_AUTO` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | bool "Auto" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:140-141` |
| `BLE_CONN_PARAMS_PHY_1MBPS` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | bool "1 Megabit" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:142-143` |
| `BLE_CONN_PARAMS_PHY_2MBPS` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | bool "2 Megabits" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:144-145` |
| `BLE_CONN_PARAMS_PHY_CODED` | 未宣言 | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | bool "Coded" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:146-147` |
| `BLE_CONN_PARAMS_PHY` | 0x00 if BLE_CONN_PARAMS_PHY_AUTO; 0x01 if BLE_CONN_PARAMS_PHY_1MBPS; 0x02 if BLE_CONN_PARAMS_PHY_2MBPS; 0x04 if BLE_CONN_PARAMS_PHY_CODED | if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | hex | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:150-156` |
| `BLE_CONN_PARAMS_INITIATE_PHY_UPDATE` | 未宣言 | BLE_CONN_PARAMS_AUTO_PHY_UPDATE; if BLE_CONN_PARAMS; if BLE_CONN_PARAMS_AUTO_PHY_UPDATE | bool "Initiate PHY mode update on connection" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:157-160` |

- choice（prompt "Preferred radio PHY mode in connection"; default BLE_CONN_PARAMS_PHY_AUTO）: `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:136-148`

## `lib/bluetooth/ble_conn_state/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_CONN_STATE` | 未宣言 | SOFTDEVICE; NRF_SDH_BLE | select DEPRECATED; bool "Connection state [DEPRECATED]" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_state/Kconfig:6-13` |
| `BLE_CONN_STATE_USER_FLAG_COUNT` | 24 | if BLE_CONN_STATE | range 0 24; int "User flag count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_state/Kconfig:16-26` |

## `lib/bluetooth/ble_db_discovery/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_DB_DISCOVERY` | 未宣言 | SOFTDEVICE_CENTRAL; NRF_SDH_BLE; BLE_GATT_QUEUE | bool "Bluetooth LE database discovery" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_db_discovery/Kconfig:7-12` |
| `BLE_DB_DISCOVERY_MAX_SRV` | 6 | if BLE_DB_DISCOVERY | int "Maximum number of services for discovery" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_db_discovery/Kconfig:15-21` |
| `BLE_DB_DISCOVERY_SRV_DISC_START_HANDLE` | 0x0001 | if BLE_DB_DISCOVERY | range 0x0001 0xFFFF; hex "Attribute handle to start discovery from" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_db_discovery/Kconfig:22-32` |

## `lib/bluetooth/ble_gq/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_GATT_QUEUE` | 未宣言 | SOFTDEVICE; NRF_SDH_BLE | bool "Bluetooth LE GATT Queue" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_gq/Kconfig:6-10` |
| `BLE_GQ_MAX_CONNECTIONS` | 1 | if BLE_GATT_QUEUE | int "Max simultaneous connections" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_gq/Kconfig:13-19` |
| `BLE_GQ_QUEUE_SIZE` | 8 | if BLE_GATT_QUEUE | int "Request queue size (per connection)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_gq/Kconfig:20-27` |
| `BLE_GQ_HEAP_SIZE` | 256 | if BLE_GATT_QUEUE | int "Datapool heap size (bytes)" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_gq/Kconfig:28-38` |

## `lib/bluetooth/ble_qwr/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_QWR` | 未宣言 | SOFTDEVICE; NRF_SDH_BLE | bool "Queued writes" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_qwr/Kconfig:6-10` |
| `BLE_QWR_MAX_ATTR` | 0 | if BLE_QWR | int "Maximum queued writes attributes" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_qwr/Kconfig:13-22` |

## `lib/bluetooth/ble_racp/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_RACP` | 未宣言 | 直接指定なし | bool "Bluetooth LE Record Access Control Point" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_racp/Kconfig:7-9` |

## `lib/bluetooth/ble_radio_notification/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_RADIO_NOTIFICATION` | 未宣言 | SOFTDEVICE | bool "Bluetooth LE Radio Notification" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:6-9` |
| `BLE_RADIO_NOTIFICATION_ON_ACTIVE` | 未宣言 | if BLE_RADIO_NOTIFICATION | bool "On active" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:16-18` |
| `BLE_RADIO_NOTIFICATION_ON_INACTIVE` | 未宣言 | if BLE_RADIO_NOTIFICATION | bool "On inactive" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:19-21` |
| `BLE_RADIO_NOTIFICATION_ON_BOTH` | 未宣言 | if BLE_RADIO_NOTIFICATION | bool "On both active and inactive" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:22-24` |
| `BLE_RADIO_NOTIFICATION_IRQ_PRIO` | 5 | if BLE_RADIO_NOTIFICATION | range 5 7; int "Bluetooth LE Radio Notification IRQ priority" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:27-39` |

- choice（prompt "Radio notification type"; default BLE_RADIO_NOTIFICATION_ON_BOTH）: `vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:12-25`

## `lib/bluetooth/ble_scan/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BLE_SCAN` | 未宣言 | SOFTDEVICE_CENTRAL; NRF_SDH_BLE; BLE_ADV_DATA | bool "Bluetooth LE Scan" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:7-12` |
| `BLE_SCAN_BUFFER_SIZE` | 32 | if BLE_SCAN | int "Scan buffer size" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:15-20` |
| `BLE_SCAN_NAME_MAX_LEN` | 32 | if BLE_SCAN | int "Scan name maximum length" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:21-26` |
| `BLE_SCAN_SHORT_NAME_MAX_LEN` | 32 | if BLE_SCAN | int "Scan short name maximum length" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:27-32` |
| `BLE_SCAN_FILTER` | y | if BLE_SCAN | bool "Scan filter" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:33-38` |
| `BLE_SCAN_NAME_COUNT` | 1 | if BLE_SCAN; if BLE_SCAN_FILTER | int "Scan name count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:41-46` |
| `BLE_SCAN_APPEARANCE_COUNT` | 0 | if BLE_SCAN; if BLE_SCAN_FILTER | int "Scan appearance count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:47-52` |
| `BLE_SCAN_ADDRESS_COUNT` | 0 | if BLE_SCAN; if BLE_SCAN_FILTER | int "Scan address count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:53-58` |
| `BLE_SCAN_SHORT_NAME_COUNT` | 0 | if BLE_SCAN; if BLE_SCAN_FILTER | int "Scan short name count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:59-64` |
| `BLE_SCAN_UUID_COUNT` | 0 | if BLE_SCAN; if BLE_SCAN_FILTER | int "Scan UUID count" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:65-70` |
| `BLE_SCAN_INTERVAL` | 160 | if BLE_SCAN | int "Scanning interval" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:73-78` |
| `BLE_SCAN_DURATION` | 0 | if BLE_SCAN | range 0 65535; int "Scan duration" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:79-86` |
| `BLE_SCAN_WINDOW` | 80 | if BLE_SCAN | int "Scanning window" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:87-92` |
| `BLE_SCAN_PERIPHERAL_LATENCY` | 0 | if BLE_SCAN | int "Scan peripheral latency" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:93-98` |
| `BLE_SCAN_MIN_CONNECTION_INTERVAL` | 6 | if BLE_SCAN | range 6 3200; int "Minimum connection interval" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:99-105` |
| `BLE_SCAN_MAX_CONNECTION_INTERVAL` | 24 | if BLE_SCAN | range 6 3200; int "Maximum connection interval" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:106-112` |
| `BLE_SCAN_SUPERVISION_TIMEOUT` | 3200 | if BLE_SCAN | range 10 3200; int "Scan supervision timeout" | `vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:113-123` |

## `lib/bluetooth/peer_manager/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `PEER_MANAGER` | 未宣言 | SOFTDEVICE; NRF_SDH_BLE; BM_TIMER; BM_ZMS | bool "Peer Manager" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:7-15` |
| `PM_BM_ZMS_SECTOR_SIZE` | 1024 | if PEER_MANAGER | int "BM_ZMS sector size" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:18-21` |
| `PM_MAX_REGISTRANTS` | 3 | if PEER_MANAGER | int "Maximum number of event handlers that can be registered" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:22-25` |
| `PM_FLASH_BUFFERS` | 4 | if PEER_MANAGER | int "Number of internal buffers for non-volatile storage operations" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:26-31` |
| `PM_SERVICE_CHANGED` | y | NRF_SDH_BLE_SERVICE_CHANGED; if PEER_MANAGER | bool "Service changed management for GATT server" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:32-39` |
| `PM_PEER_RANKS` | y | if PEER_MANAGER | bool "Peer rank management" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:40-45` |
| `PM_LESC` | 未宣言 | PSA_WANT_ALG_ECDH; PSA_WANT_GENERATE_RANDOM; PSA_WANT_KEY_TYPE_ECC_KEY_PAIR_GENERATE; PSA_WANT_KEY_TYPE_ECC_KEY_PAIR_IMPORT; PSA_WANT_KEY_TYPE_ECC_KEY_PAIR_EXPORT; PSA_WANT_ECC_SECP_R1_256; (MBEDTLS_PSA_STATIC_KEY_SLOTS && MBEDTLS_PSA_KEY_SLOT_COUNT >= 1) &#124;&#124;  MBEDTLS_ENABLE_HEAP; if PEER_MANAGER | bool "LE Secure Connections (LESC) support" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:46-61` |
| `PM_LESC_GENERATE_NEW_KEYS` | 未宣言 | if PEER_MANAGER; if PM_LESC | bool "Generate new LESC key pair after every pairing attempt" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:64-68` |
| `PM_LESC_PRIVATE_KEY_EXPORT` | 未宣言 | if PEER_MANAGER; if PM_LESC | bool "Export private key for debugging purposes" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:69-74` |
| `PM_RA_PROTECTION` | 未宣言 | if PEER_MANAGER | bool "Protection against repeated pairing attempts" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:77-83` |
| `PM_RA_PROTECTION_TRACKED_PEERS_NUM` | 8 | if PEER_MANAGER; if PM_RA_PROTECTION | int "Maximum number of peers whose authorization status can be tracked" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:86-89` |
| `PM_RA_PROTECTION_MIN_WAIT_INTERVAL` | 4000 | if PEER_MANAGER; if PM_RA_PROTECTION | int "Minimum waiting interval (in ms) before a new pairing attempt can be initiated" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:90-93` |
| `PM_RA_PROTECTION_MAX_WAIT_INTERVAL` | 64000 | if PEER_MANAGER; if PM_RA_PROTECTION | int "Maximum waiting interval (in ms) before a new pairing attempt can be initiated" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:94-97` |
| `PM_RA_PROTECTION_REWARD_PERIOD` | 10000 | if PEER_MANAGER; if PM_RA_PROTECTION | int "Reward period (in ms)" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:98-104` |
| `PM_HANDLER_SEC_DELAY_MS` | 0 | if PEER_MANAGER | int "Delay before starting security" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:107-112` |
| `PM_CONN_STATE_USER_FLAG_COUNT` | 24 | if PEER_MANAGER | range 0 24; int "Connection state user flag count" | `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:113-123` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
