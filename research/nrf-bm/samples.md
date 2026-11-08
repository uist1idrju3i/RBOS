# 全 samples と RBOS の試験への対応

固定版の README.rst を持つ 27 samples を列挙します。全 sample の製品動作を Ruby から再現する約束ではありません。公開機能の設定・buffer・event は対応する component 文書で扱い、sample 固有の設定宣言は [Kconfig 一覧](kconfig-samples.md)へ分けます。

「候補」は sample の資料を RBOS/S115 統合に利用する意味です。全 sample の同一 S115/MCUboot target での build 成功を確認した意味ではありません。README、sample.yaml、prj.conf、board ごとの条件を実際の build 前に確認します。central samples は対象外です。

| sample（samples/ 以下） | 実演内容 | S115/RBOS | 転用する試験・backend の設計例 | 根拠 |
|---|---|---|---|---|
| `bluetooth/ble_bms` | bond 削除要求・authorization の BMS | 候補 | bond 管理の承認と peer manager | `vendor/sdk-nrf-bm/samples/bluetooth/ble_bms/README.rst:1-125` |
| `bluetooth/ble_cgms` | Continuous Glucose profile、measurement・record 管理 | 候補 | profile と sensor 入力を分離 | `vendor/sdk-nrf-bm/samples/bluetooth/ble_cgms/README.rst:1-93` |
| `bluetooth/ble_hids_keyboard` | HID keyboard の report と pairing | 候補 | hid_report_send と権限 | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hids_keyboard/README.rst:1-106` |
| `bluetooth/ble_hids_mouse` | HID mouse、boot/report mode | 候補 | hid_report_send と report map | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hids_mouse/README.rst:1-102` |
| `bluetooth/ble_hrs` | heart rate と battery、接続・bonding | 候補 | heart_rate_update、LESC foreground 処理 | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs/README.rst:1-101` |
| `bluetooth/ble_hrs_central` | Heart Rate/Battery client、探索・受信 | 対象外（central） | S115 初期 API に採用しない | `vendor/sdk-nrf-bm/samples/bluetooth/ble_hrs_central/README.rst:1-76` |
| `bluetooth/ble_lbs` | BLE LED write と button notification | 候補 | GPIO/button backend と BLE を接続 | `vendor/sdk-nrf-bm/samples/bluetooth/ble_lbs/README.rst:1-84` |
| `bluetooth/ble_nus` | UART と BLE NUS の双方向 bridge | 候補 | ble_uart_write/subscribe と buffer | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus/README.rst:1-132` |
| `bluetooth/ble_nus_central` | central 側 NUS client、UART bridge | 対象外（central） | client/discovery を採用しない | `vendor/sdk-nrf-bm/samples/bluetooth/ble_nus_central/README.rst:1-137` |
| `bluetooth/ble_pwr_profiling` | advertising/接続通信時の電力測定 | 候補 | 省電力・idle の評価手順、API 本体ではない | `vendor/sdk-nrf-bm/samples/bluetooth/ble_pwr_profiling/README.rst:1-201` |
| `bluetooth/ble_radio_notification` | radio active/inactive の IRQ 通知 | 候補 | native timing の記録、Ruby 直呼出しはしない | `vendor/sdk-nrf-bm/samples/bluetooth/ble_radio_notification/README.rst:1-69` |
| `bluetooth/hello_softdevice` | SD enable/disable の最小構成 | 候補 | platform 起動・状態 event | `vendor/sdk-nrf-bm/samples/bluetooth/hello_softdevice/README.rst:1-66` |
| `bluetooth/peripheral_nfc_pairing` | NFC tag を使う BLE OOB pairing | 候補 | NFC/LESC の資源・security 統合 | `vendor/sdk-nrf-bm/samples/bluetooth/peripheral_nfc_pairing/README.rst:1-186` |
| `boot/mcuboot_recovery_entry` | BLE MCUmgr と boot mode による recovery 入口 | 候補 | 特権 dfu_request と loader | `vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_entry/README.rst:1-89` |
| `boot/mcuboot_recovery_retention` | retention boot mode による recovery 再起動 | 候補 | boot reason/retention の所有 | `vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_retention/README.rst:1-52` |
| `nfc/record_text_t2t` | NDEF text を Type 2 Tag で提示 | 候補 | nfc_payload_set と buffer 寿命 | `vendor/sdk-nrf-bm/samples/nfc/record_text_t2t/README.rst:1-160` |
| `nfc/record_text_t4t` | NDEF text を Type 4 Tag で提示 | 候補 | tag file/payload と read/write event | `vendor/sdk-nrf-bm/samples/nfc/record_text_t4t/README.rst:1-161` |
| `peripherals/buttons` | button の debounce と event | 候補 | button_subscribe と ISR→foreground | `vendor/sdk-nrf-bm/samples/peripherals/buttons/README.rst:1-71` |
| `peripherals/leds` | nrfx による LED GPIO 出力 | 候補 | gpio_write と論理 pin | `vendor/sdk-nrf-bm/samples/peripherals/leds/README.rst:1-63` |
| `peripherals/lpuarte` | REQ/RDY を使う低消費電力 UART | 候補 | uart_open/read/write、追加 2 pin | `vendor/sdk-nrf-bm/samples/peripherals/lpuarte/README.rst:1-91` |
| `peripherals/ppi` | hardware event→task の PPI/DPPI 接続 | 候補 | 内部 driver 機構。SD の予約 channel は避ける | `vendor/sdk-nrf-bm/samples/peripherals/ppi/README.rst:1-65` |
| `peripherals/pwm` | nrfx PWM の波形出力 | 候補 | pwm_config/start/stop、sequence buffer | `vendor/sdk-nrf-bm/samples/peripherals/pwm/README.rst:1-153` |
| `peripherals/timer` | BM timer の single-shot と周期 callback | 候補 | timer_start/stop、tick と分離 | `vendor/sdk-nrf-bm/samples/peripherals/timer/README.rst:1-63` |
| `peripherals/uarte` | nrfx UARTE の送受信 | 候補 | UART driver、DMA・overflow・abort | `vendor/sdk-nrf-bm/samples/peripherals/uarte/README.rst:1-65` |
| `subsys/fs/bm_zms` | key-value・counter・長い array の保存と削除 | 候補 | settings_get/set と GC・空き容量 | `vendor/sdk-nrf-bm/samples/subsys/fs/bm_zms/README.rst:1-103` |
| `subsys/shell/bm_uarte` | UARTE shell の初期化と foreground 処理 | 候補 | 管理口、shell_process の機会 | `vendor/sdk-nrf-bm/samples/subsys/shell/bm_uarte/README.rst:1-57` |
| `subsys/storage/bm_storage` | storage instance、write/erase 完了 event、SD/RRAM backend | SD backend のみ候補 | storage_read/write、非同期完了 | `vendor/sdk-nrf-bm/samples/subsys/storage/bm_storage/README.rst:1-97` |

## 共通の読み方

各 sample の CMakeLists/prj.conf は必要な SDK 機能を示す最小例で、RBOS 全体の最終設定ではありません。example の無制限 loop、assert、demo 用 security、button による bond 全削除をそのまま製品へコピーしません。UART、button/LED、timer、NFC は一つずつ動作しても同時統合で衝突し得ます。

P0 は recovery と hello_softdevice、P1 は timer/buttons と foreground 進行、P2 は LED/NUS/LBS、P3 は BMS/LESC、P4 は const bytecode、P5 は recovery/署名・電源断、P6 は power profiling と長時間接続を組み合わせる設計案です。sample を通すことだけで Ruby の所有権・task 破棄・権限境界の試験を代替しません。

latest の MDS/SPI/SPI manager/radio_test は固定版に含めません。[版比較](version-comparison.md)を参照してください。SDK build、flash、BLE/NFC/電力の実測は今回行っていません。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
