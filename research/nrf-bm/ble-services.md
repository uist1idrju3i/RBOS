# Bluetooth services の全体像

[公開 API・struct・event 一覧](api-services.md)と[全 Kconfig](kconfig-services.md)を参照してください。server の callback は SDH の配送 model に依存し、Ruby callback の直接呼出は避けます。各 config/instance と送受信 buffer を保持し、notification の受付と送信完了を区別します。

| directory / service | 目的・主要 API | S115 | メモリ・Ruby backend 設計例 |
|---|---|---|---|
| ble_bas / Battery | init、battery_level_update、notification 状態 event | 対象 | instance、GATT attributes、接続状態。`battery_service_update`、実電池の計測 driver とは分離 |
| ble_bas_client | init、discovery event、handle assign、read、notification enable/disable | CENTRAL と discovery 依存で対象外 | client instance と GATT queue。初期 backend なし |
| ble_bms / Bond Management | init、authorization response、BLE/QWR event。bond 削除要求を扱う | 対象 | feature/authorization config と QWR。 `bond_management_authorize`、管理 task だけ許可 |
| ble_cgms / Continuous Glucose | init、connection assign、measurement create、status/session runtime 更新 | 対象 | 測定記録 DB・session・RACP/SOCP 状態。 `glucose_measurement_add/status`、製品用途がある場合のみ |
| ble_dis / Device Information | init、manufacturer/model/version 等の read-only attributes | 対象 | config の文字列・GATT table。`device_info_register`、firmware/製品情報を Ruby から渡す候補 |
| ble_hids / HID | init、input/boot keyboard/mouse report send、output report get、protocol event | 対象 | input/output/feature report 数 default 各 10、最大長 default 8/1/2。clients default 1。report map と接続状態も必要。`hid_report_send/read` |
| ble_hrs / Heart Rate | init、heart_rate_measurement_send、RR interval、sensor contact、body location | 対象 | RR interval buffer、instance と GATT。`heart_rate_update`、sensor 読出しと分離 |
| ble_hrs_client | init、discovery、handle assign、notification enable/disable、受信 event | CENTRAL と discovery 依存で対象外 | client + queue。初期 backend なし |
| ble_lbs / LED Button | init、button change 通知、LED write callback | 対象 | instance と属性。 `ble_led_button_register/notify` は GPIO backend を再利用し、通信処理と pin 操作を分ける |
| ble_mcumgr | init、service UUID type、SMP characteristic | 対象 | SMP net_buf と reassembly 等を別計上。`dfu_request` の通信側は loader に置き、Ruby の汎用転送 service に流用しない |
| ble_nus / Nordic UART | init、data_send、RX/通信開始停止/送信完了 event | 対象 | instance、MTU 長 buffer、SD TX queue。`ble_uart_write/subscribe`、hardware UART への bridge は任意 |
| ble_nus_client | init、discovery、handle assign、string send、notification enable/disable | CENTRAL と discovery 依存で対象外 | client + queue。初期 backend なし |

各 service の API/型/定数と buffer 契約は `include/bm/bluetooth/services/` の header（[索引](api-services.md)）が根拠です。role と依存は各 service の Kconfig（[索引](kconfig-services.md)）。HIDS の容量は `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_hids/Kconfig:1-85`。UUID の共通定義は `vendor/sdk-nrf-bm/include/bm/bluetooth/services/uuid.h:1-284`。UUID を持つだけで service が登録されるわけではありません。

## CGMS 内部構造

CGMS は単なる値通知でなく、測定 DB、session start time、session operations control point、record access control point、measurement encoding を内部に持ちます。内部 header は `cgms_db.h`、`cgms_sst.h`、`cgms_socp.h`、`cgms_racp.h`、`cgms_meas.h`。公開境界は `ble_cgms.h` に保ちます。根拠: `vendor/sdk-nrf-bm/subsys/bluetooth/services/ble_cgms/CMakeLists.txt:1-11` と `vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_cgms.h:1-661`。

## security と再入

MCUmgr の default security macro は read/write/CCCD write が OPEN です。「DFU が署名付き」だけで、reset や情報読出し等の管理操作まで認証済みになるわけではありません。各 characteristic の security mode、bond 削除の承認、BMS の QWR 経路を設計する必要があります。出典: `vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_mcumgr.h:1-86` と `vendor/sdk-nrf-bm/include/bm/bluetooth/services/ble_bms.h:1-350`。

service init は SD の GATT 登録を行い、その後も instance と config から参照されるデータがあります。複数 Ruby task から同じ instance を変更するなら nRF backend を単一 owner にします。切断・CCCD 無効化・TX queue 満杯・MTU 不足・再接続・bond 削除中を試験します。全 API の再入保証や最終 RRAM/RAM サイズは未確認です。

初期 RBOS に全 profile を常時組み込む方針ではありません。必要な service を Kconfig で選び、Ruby の製品ロジックを支える binding を追加する候補です。BLE MDS は [latest のみ](version-comparison.md)で、固定版の service に数えません。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
