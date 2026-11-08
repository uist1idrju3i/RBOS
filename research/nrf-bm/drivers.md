# Bare Metal drivers の用途と制約

API 名は [I/O 索引](api-core.md)、全設定は [Kconfig](kconfig-core.md)を参照してください。以下の backend 名は RBOS の設計例です。

| component | 固定版の機能・API 経路 | S115・実行 context と再入 | RAM/RRAM と RBOS での使い方 |
|---|---|---|---|
| bm_lpuarte | `bm_lpuarte_init`、RX enable/buffer、TX/abort、event callback。nrfx UARTE に REQ/RDY を加えて受信側を起こす | 対象。GPIOTE・timer・UARTE を使う非同期 driver。DMA buffer と instance を処理完了まで維持し、IRQ callback から Ruby へ入らない | `struct bm_lpuarte` と利用者の RX/TX buffer、timer、channel。固定総量は未測定。`uart_open/read/write/cancel` の候補。通常 UART と pin 数・wake latency を比較 |
| clock_control | 独自 C driver/header ではなく Zephyr clock library を amend。SoftDevice 側の clock 制御と外部 driver の組合せ | 対象。SOFTDEVICE 選択時の `CLOCK_CONTROL` default n を無視して直接 HF/LF clock を操作しない | 独自増分は CMake だけでは算出不可。`power_clock_request/release` が必要になった場合の内部機構。利用者へ無制限の clock API を公開しない |
| console | printk/stdout hook を UARTE TX へ接続。独立した BM read API はない | 対象。console IRQ 既定 5、S115 時範囲 5〜7。blocking TX を使うので timer/SD observer 内の長い出力は避ける | 1-byte TX と driver 状態。logging 有効時は instance を共有する分岐あり。`console_write/flush` の候補。共有と同時呼出を backend で直列化 |
| flash | Zephyr `flash_read/write/erase` API の RRAM 実装。read は memcpy、write は `sd_flash_write`、erase は 0xff 書込み | 対象。`SOC_FLASH_NRF_RRAM_BM` は SOFTDEVICE で default y。word alignment と範囲検査あり。Zephyr API の名前だけで bm_storage の完了 event 契約と同一視しない | erase の local buffer 16 bytes。driver・SD の総増分は未測定。`storage_read/write` の低層候補だが、初期 Ruby bytecode は保存しない |

LPUARTE の API・buffer と状態は `vendor/sdk-nrf-bm/include/bm/drivers/bm_lpuarte.h:1-204`、HFXO は default y（SoftDevice 時）、起動が最大 3 ms 延びる記述は `vendor/sdk-nrf-bm/drivers/bm_lpuarte/Kconfig:1-32`。REQ/RDY の手順は `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/lpuarte.rst:1-63` です。

clock の実体が amend のみである根拠は `vendor/sdk-nrf-bm/drivers/clock_control/CMakeLists.txt:1-9`、SOFTDEVICE の clock default は `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:1-72`。console の instance 共有、hook と blocking TX は `vendor/sdk-nrf-bm/drivers/console/console_bm_uarte.c:1-100`、IRQ 条件は `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:1-57`。flash は `vendor/sdk-nrf-bm/drivers/flash/soc_flash_nrf_rram.c:1-220` と `vendor/sdk-nrf-bm/drivers/flash/Kconfig.nrf_rram:1-36` です。

## 周辺 driver との境界

この drivers/ に GPIO/PWM/SPI/I2C/ADC 全ての独自 driver があるわけではありません。nrfx を直接使う場合はアプリが ISR を接続し、BM の NVIC priority と予約資源を守ります。根拠は `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/bm_nrfx.rst:1-25`。nRF54L15-DK の DT node の削除と board-config の役割は [board 統合](board-integration.md)へ分離しています。

driver 内部の同期化は全 API の再入保証ではありません。複数 Ruby task が同一 peripheral を使う場合、instance の所有者、進行中 request、cancel 後の完了 event、buffer の返却を nRF backend で管理します。Ruby の Mutex を IRQ と共有する設計にはしません。

## 導入前に試すこと

- LPUARTE: timeout、相手が RDY を返さない場合、abort、短い RX buffer、REQ/RDY とボタンの pin 競合。
- console/log: 同じ UARTE の二重 init 回避、長文時の task latency、panic 時に進行できること。
- flash/storage: alignment・範囲・busy とエラー伝播、書込み完了の定義、SoftDevice 有効時の挙動。通常 app と loader それぞれで確認。

いずれも未試験です。書込み・更新の採用判断は [storage](storage-and-fs.md) と [DFU](../dfu/single-bank-dfu.md)へつなぎます。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
