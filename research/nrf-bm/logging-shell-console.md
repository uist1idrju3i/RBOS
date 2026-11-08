# console・logging・shell を混同しない

全設定は [I/O Kconfig](kconfig-core.md)、console driver は [drivers](drivers.md)、標準 pin と instance は [board](board-integration.md)へ分けています。

| 経路 | component・機能 | context・メモリ・制約 | Ruby backend 候補 |
|---|---|---|---|
| console | stdout/printk hook、BM_UARTE_CONSOLE | blocking TX。既定 instance は UARTE20。logging と共有する分岐があり、console を別 driver として二重 init しない | mruby/c HAL の `console_write/flush`。Ruby の puts を結ぶ候補 |
| logging backend | subsys/logging/backends の BM UARTE backend | default BUFFER_SIZE=200。実装に log output buffer と TX copy buffer の二つがあり、配列 payload 合計 400 bytes。priority default 5。deferred/immediate/panic は出力の粒度が異なる | `log_write(level,message)`、内部診断。全ログを Ruby heap に蓄えない |
| shell backend | subsys/shell/backends の BM UARTE transport、`shell_backend_bm_uarte_get_ptr` | EXPERIMENTAL、SHELL_MINIMAL。RX double buffer default 128 + ring 128 bytes、TX buffer と状態が別。main で shell_process が必要 | 管理 console の任意機能。`diagnostics_command` は権限付き。未認証の対話口を常時有効にしない |

出典: `vendor/sdk-nrf-bm/drivers/console/console_bm_uarte.c:1-100`、`vendor/sdk-nrf-bm/subsys/logging/backends/log_backend_bm_uarte.c:1-112` と `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:1-54`、`vendor/sdk-nrf-bm/subsys/shell/backends/bm_uarte.c:1-202` と `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:1-54`、`vendor/sdk-nrf-bm/include/bm/shell/backend_bm_uarte.h:1-11`。shell の foreground 処理の実例は `vendor/sdk-nrf-bm/samples/subsys/shell/bm_uarte/src/main.c:1-72` です。

## 処理機会と IRQ

deferred log は出力を生成しただけでは drain が保証されません。foreground の処理機会、panic 時の同期経路、ログ詰まりを評価します。shell の transport も RX が溜まるだけでは command を実行しません。rrt0 の idle だけに管理処理を置かないようにします。

console と logging は BM_IRQ_DIRECT_CONNECT を使いますが、固定版 shell backend は IRQ_DIRECT_CONNECT を直接使い nrfx の config にも priority を渡します。Zephyr の offset と nrfx init 後の NVIC 設定まで含む実効 priority は、同じ数字の BM macro と同一と決めません。ここで実機の誤動作や bug を確認したものではなく、統合時の照合項目です。出典: 上記各 C 実装。

## pin と所有権

board の既定では application UART と shell がどちらも UARTE30 の同じ pin を使います。MCUmgr UART の利用も含め一つの peripheral に複数 driver を同時 init しないよう構成を決めます。console/log は UARTE20 ですが pin の CTS・flow control も合わせて確認します。出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:1-126`。

出力長が tick/BLE 処理を妨げないこと、非 ASCII と改行、並行出力、RX overflow、debug 無効時の RRAM 減、fault 内で進行することは未試験です。Ruby API の正常系だけでなく、出力先が詰まる場合を backend fake と実機の両方で確認します。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
