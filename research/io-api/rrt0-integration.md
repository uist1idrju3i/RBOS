# MPIG の待機を rrt0 と両立させる設計案

ここは **RBOS の提案と実装前の検証条件**です。MPIG の待機契約、既存 VM の動作、将来の backend を区別します。根拠は [MPIG の serial API](serial-buses.md)、[scheduler lifecycle](../mrubyc/scheduler-lifecycle.md)、[HAL と IRQ](../mrubyc/hal-porting.md)です。

## 同期 API と VM 全体の停止は別

UART#read / gets / flush は呼出し側が待つ契約です。一方、rrt0 は Ruby task を切り替える scheduler なので、単一 C method が driver 完了まで spin / blocking syscall を続けると、他の Ruby task や BM の foreground 処理が進まなくなる可能性があります。tick が届くだけで C method の途中から別 Ruby task を安全に実行できる、と仮定しません。

nrfx の参照 source は [hal_nordic 固定版](https://github.com/zephyrproject-rtos/hal_nordic/tree/1acb428a205bad58f3dfd4e38f2d1663bb784ba1)。[nrfx_twim.h](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/drivers/include/nrfx_twim.h) は NULL handler なら blocking、TX-RX / TX-TX は nonblocking のみと説明します。[nrfx_spim.h](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/drivers/include/nrfx_spim.h) にも handler による blocking 切替があります。MPIG の repeated start を、都合のよい blocking mode へ黙って置き換えることはできません。

## 候補となる分解

| 段階 | 提案する責任 | 未実装の条件 |
|---|---|---|
| 開始 | 共有 C binding が argc / 型 / 値域 / 権限を確認。backend が instance と DMA buffer を保持し request を開始 | request handle の形式、queue 上限、busy の表現、OOM 時の復旧 |
| 待機 | Ruby wrapper が完了状態を問い合わせ、未完了なら sleep_ms 等で譲る。または system/owner task が要求を処理し、安全な foreground 経路で待機 task を起こす | interval・latency の測定。Task.pass だけの高速 polling を常態化しない。起床 API の具体化 |
| IRQ 完了 | native の bounded event に結果を保存する。Ruby 呼出し・allocation/refcount・raise・Mutex/task 操作はしない | event overflow、メモリ順序、cancel 後の遅延 event、世代番号 |
| foreground 完了 | 結果・転送長・error を確定し、Ruby 値の生成と exception 化を実施 | DMA 解放の順序、待機 task 終了・VM ID 再利用への対策 |
| 終了・cancel | peripheral / buffer / lock を解放し、transaction の途中状態を復旧 | timeout と hardware 完了の race、CS / STOP の復旧、task 破棄時の扱い |

二つの待機案を同時に実装済みとするものではありません。native method 内で単に task を suspend して C stack を保持したり、mrbc_run を再帰呼出ししたりする案は採用しません。開始・確認・完了に分けるか、VM の正式な再開経路を設計してから実装します。

## bus / buffer / error の契約

- 一つの physical instance の init・mode・進行中転送には一つの owner を決めます。[serial box](nrf54l15-mapping.md)を protocol 別の独立 instance として二重取得しません。
- I2C の write + repeated-start + read、SPI の CS assert + transfer + deassert を transaction として排他します。個々の byte ごとの lock では意味を保てません。
- UART の bytes_available と read の間に別 reader が消費する場合があるため、単独 owner / reservation / 再確認のいずれかを設計します。「確認したので必ず nonblocking」と一般化しません。
- String の内部 pointer を使う DMA は、Ruby の値・byte 列・native buffer の寿命を分けて保持します。RRAM 上の const bytecode がそのまま DMA buffer に適するとは仮定しません。[C API ownership](../mrubyc/c-api-ownership.md)に従います。
- MPIG の UART#write の戻りを「全 byte の物理送信完了」へ勝手に強めず、flush の完了と分けます。I2C の short read / count、SPI write の nil も維持します。
- timeout / cancel / scan / event callback を加えるなら RBOS 拡張と表示します。ArgumentError / RangeError 等の標準由来の失敗と、busy / NAK / timeout / permission の backend 失敗を整理し、根 Exception で一括処理しません。追加の exception hierarchy は未設計です。

## 実装時に必要な試験

Wasm fake backend で通常・空データ・短い転送・不正引数・失敗・timeout・cancel を制御できることを受け入れ条件にします。待機中に別 task の counter と BM foreground 相当処理が進み、queue / buffer が上限を守り、同一 instance への競合と task 終了後の event が安全であることも確認します。これらの fake API・試験は今回追加していません。

nRF 実機では S115 有効時の IRQ priority、DMA alignment / RAM、GPIO 電気特性、実効周波数、I2C repeated start、SPI dummy zero、UART flush、CPU 負荷・latency・消費電力を確認します。既存 [Wasm scheduler 検査](../../tools/mrubyc-wasm/README.md)の成功は、この未実装 I/O の保証にはなりません。

[調査の入口](overview.md) / [調査索引へ戻る](../README.md)
