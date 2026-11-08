# Bare Metal 向け HAL 移植

## 上流が要求する接点

自作 HAL の指定は `MRBC_USE_HAL` を使います。上流の手順は `vendor/mrubyc/doc/How_to_make_your_own_HAL.md:27-38` です。ただし同文書は主にビルド方法であり、実装契約は `vendor/mrubyc/hal/minimal.h:1-55` と各 HAL のヘッダから確認します。

| 接点 | 必要な役割 | RBOS の案 |
|---|---|---|
| `MRBC_TICK_UNIT` | tick の ms 単位 | 初期 1 ms、測定後確定 |
| `MRBC_TIMESLICE_TICK_COUNT` | 一回の実行時間片 | 初期 10 tick |
| `mrbc_hal_init()` | HAL 初期化 | timer を一度だけ開始 |
| `mrbc_hal_disable_irq()` | queue 等の排他 | tick と共有データを守り、SoftDevice の優先度 0/1 は妨げない |
| `mrbc_hal_enable_irq()` | 排他解除 | 元の割り込み状態へ戻す。入れ子対応 |
| `mrbc_hal_idle_cpu()` | 実行 task がないときの待機 | BM イベントを処理し、適切な待機 API を呼ぶ |
| `int mrbc_hal_write(int fd, const void *buf, int nbytes)` | console 出力 | UARTE、上限付きバッファ |
| `int mrbc_hal_flush(int fd)` | 出力の flush | 未完了出力の方針を定義 |
| `void mrbc_hal_abort(const char *s)` | 致命エラー | ログと安全な停止・再起動方針 |

API と互換名 `hal_*` の出典: `vendor/mrubyc/hal/zephyr/hal.h:48-90`。右列は未実装の設計案です。空の abort macro は、本番の異常処理の代わりにはしません。

## 参照 HAL の違い

| HAL | 実装の特徴 | 出典 |
|---|---|---|
| POSIX | signal/timer で tick、signal mask による排他、write/flush、abort | `vendor/mrubyc/hal/posix/hal.c:1-156`、`vendor/mrubyc/hal/posix/hal.h:58-111` |
| Zephyr | k_timer、irq_lock、必要時の scheduler lock、入れ子 count、write/flush/abort | `vendor/mrubyc/hal/zephyr/hal.c:35-160` |
| minimal | 必要な macro と出力 API の雛形。timer 無しでは idle で tick を進める例 | `vendor/mrubyc/hal/minimal.h:1-55` |

Zephyr HAL の `k_msleep` や thread scheduler 操作を、BM の HAL にそのまま残す方針にはしません。利用可能な BM API と初期化順を確認して実装します。`MRBC_NO_TIMER` は実時間 timer の代わりに VM 実行回数で時間片を模擬するため、BLE や sleep の実時間要件を満たす根拠にはなりません。出典: `vendor/mrubyc/src/rrt0.c:371-387`。

## timer と割り込み

bm_timer は GRTC を使います。system timer が使う GRTC channel0 / GRTC_2_IRQn を別用途に横取りしません。1 ms の周期 callback で `mrbc_tick()` を呼ぶ案を最初に評価します。bm_timer の最小 timeout は約 152 μs なので、1 ms は数値上は範囲内ですが実測精度は未確認です。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:8-34`、`vendor/sdk-nrf-bm/include/bm/bm_timer.h:30-45,87-102`。

排他は実行中の IRQ 状態を保存し、最後の解除だけで元へ戻す設計にします。SoftDevice IRQ は zero-latency で、通常の `irq_lock` では mask されません。tick callback の priority と、queue を変更する呼出元を全て整理してから実装します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nrf_sdh.rst:23-28`、`vendor/mrubyc/hal/zephyr/hal.c:75-108`。

## イベント処理と CPU 待機

BM の `bm_scheduler_process()` は main loop で定期的に呼ぶ必要があります。一方 `mrbc_run()` は通常戻りません。idle hook だけに event drain を置くと、runnable task が存在する間は callback が止まるリスクがあります。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_scheduler.rst:35-37`、`vendor/mrubyc/src/rrt0.c:349-425`。

設計候補は、必ず実行機会を持つ C 側の実行区切りか、権限付きシステムタスクのイベント処理 API です。後者では高優先度 task の占有を制限し、イベント処理が Ruby の例外で止まらないようにします。vendor を直接編集せず実現できる範囲を P1 で検証し、追加の scheduler 接点が必要なら別途設計判断とします。

idle の WFE / SoftDevice 待機 API は候補であり、確認済みの完成手順ではありません。割り込み発生と待機の間の取りこぼし、将来の storage 完了通知、console 未送信の扱いを実機で確認します。

## 受け入れ条件

- tick の二重開始・二重供給がない。周期・jitter・wraparound を記録する。
- 排他の入れ子、ISR からの呼出、SoftDevice 有効時の BLE 継続を試験する。
- 常時 runnable な task がいても BM イベントが進む。
- no-task 時だけでなく、sleep 復帰（将来は storage 完了）で待機解除できる。
- console の長い出力や致命エラーが割り込みを永久に止めない。

全項目未実施です。[実装計画](../implementation/porting-plan.md)で順序を定めます。

[調査索引へ戻る](../README.md)
