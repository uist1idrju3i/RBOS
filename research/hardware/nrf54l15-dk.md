# nRF54L15-DK

## 対象と確認範囲

開発対象は Nordic Semiconductor nRF54L15-DK です。SDK v2.0.1 は nRF54L15 DK を対象に含め、同じ DK で nRF54L10/05 を模擬する target も用意します。RBOS は 15 を使います。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:11-19`。

工事設計認証番号 **220-JP8930** は利用者から提示された値です。本リポジトリでは総務省のデータベースとの照合を実施していません。[技術基準適合証明等を受けた機器の検索](https://www.tele.soumu.go.jp/giteki/SearchServlet?pageID=js01)で、実機の表示、製品型番、適用条件を確認してください。認証番号の記載を、RBOS 全体の認証取得や任意の無線設定の適法性の保証とは扱いません。

主 target は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot`。central が必要なら `bm_nrf54l15dk/nrf54l15/cpuapp/s145_softdevice/mcuboot` を評価します。出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/board.yml:1-68`、`vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:24-34`。

SoC の CPU・無線・メモリの製品仕様は [Nordic の nRF54L15 製品ページ](https://www.nordicsemi.com/Products/nRF54L15)、ボードの配線・デバッグ接続は [DK 製品ページ](https://www.nordicsemi.com/Products/Development-hardware/nRF54L15-DK)を一次資料とします。RBOS の実効メモリは製品の総量ではなく、[SDK の領域配置](../architecture/overview.md)から見積もります。

## GPIO の対応

SDK の識別子は 0 起点です。OpenBlink の `led1` 等を同じ物理ピン番号と解釈しません。

| SDK の識別子 | GPIO |
|---|---|
| `BOARD_PIN_BTN_0` | P1.13 |
| `BOARD_PIN_BTN_1` | P1.09 |
| `BOARD_PIN_BTN_2` | P1.08 |
| `BOARD_PIN_BTN_3` | P0.04 |
| `BOARD_PIN_LED_0` | P2.09 |
| `BOARD_PIN_LED_1` | P1.10 |
| `BOARD_PIN_LED_2` | P2.07 |
| `BOARD_PIN_LED_3` | P1.14 |

出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:24-51`。LED は `GPIO_ACTIVE_HIGH` です。ボタンの有効レベルや pull は実際の buttons 設定と実機で確認し、LED の有効レベルから推測しません。

## UART と競合

| 用途 | peripheral | ピン |
|---|---|---|
| console / logger | UARTE20 | TX P1.04、CTS P1.07 |
| アプリ UART / shell | UARTE30 | TX P0.00、RX P0.01、RTS P0.02、CTS P0.03 |
| LPUARTE | UARTE21 | TX P1.11、RX P1.12、REQ P0.04、RDY P1.14 |

出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:54-117`。REQ は button3、RDY は LED3 と共有されます。UART と shell が同じ UARTE30 を使う構成も競合するため、同時利用を設計で禁止または切り替えます。

## 書き込みと RRAM

公式導入手順は DK 接続と SEGGER J-Link の導入を含みます。書き込みは SDK の `west flash` / nRF Util の runner に合わせます。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/install_nrf_bm.rst:15-28`、`vendor/sdk-nrf-bm/doc/nrf-bm/sample/intro/program_sample.rst:1-42`。RBOS の専用ビルド target はまだありません。

RRAM への書き込みは、消去単位・program 単位・wear 単位を bm_storage の情報から取得する設計にします。一般的な外付け NOR flash と同じ消去前提に固定しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:63-106`。

IRoT の BOOTCONF をロックした場合、ブート領域の再書き込みには全消去が必要です。nRF Util device 2.15.0 以上、または Recover の注意があります。全消去は storage を含むデータの喪失を伴う運用として扱います。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:49-75`。実機での復旧経路は未確認です。

[調査索引へ戻る](../README.md)
