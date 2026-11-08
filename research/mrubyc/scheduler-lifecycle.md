# rrt0 の状態遷移と VM lifecycle

基本の Task/Mutex API は [task scheduler](task-scheduler.md)、全登録名は [method 索引](methods-tasks.md)、C 宣言は [runtime API](c-api-runtime.md)へ分離しています。

| 状態 | queue と入口/出口 |
|---|---|
| DORMANT=0 | 未起動/終了。create/start、Ruby run/rewind、delete の対象条件を区別 |
| READY=2 | priority_preemption の昇順 queue。同順位では末尾へ挿入 |
| RUNNING=3 | ready queue の先頭を実行。slice/明示 pass/状態変更で切替 |
| WAITING=4 | reason SLEEP/MUTEX/JOIN。sleep の期限・unlock・対象 task の終了で ready へ |
| SUSPENDED=8 | resume まで停止。待機理由を持つ task の suspend/resume は reason も追跡 |

queue は dormant/ready/waiting/suspended の4本で、RUNNING は独立 queue ではありません。既定 priority=128、name 長=15。根拠: `vendor/mrubyc/src/rrt0.h:1-156`、`vendor/mrubyc/src/rrt0.c:1-1585`。

## tick と timeslice

HAL の TICK_UNIT × TIMESLICE_TICK_COUNT が基準ですが、native C method の途中を VM が即座に中断するものではありません。mrbc_tick は timeslice と起床待機を処理し preemption flag を設定します。MRBC_NO_TIMER は opcode 実行単位で slice を模擬し tick を進める別経路です。Wasm の時間・公平性を nRF の wall-clock jitter の測定結果にしません。根拠: `vendor/mrubyc/src/rrt0.c:1-1585` と `vendor/mrubyc/hal/emscripten/hal.h:1-95`。

priority は小さい数を先に実行し、同順位が巡回します。sleep_ms は tick の端数を切上げます。常時 ready の高 priority task がある場合の低 priority task・idle・backend service の進行は、rrt0 の存在だけでは保証されません。HAL の idle だけに通信処理を置かず、RBOS 側の処理機会を設計します。

## 作成・終了・再利用

1. mrbc_init は allocator、class/mrblib、global/symbol、HAL と task 機能を準備する。mrblib は VM の初期化用 bytecode として先に実行される。
2. mrbc_tcb_new は sizeof(TCB)+sizeof(value)×regs_size を確保する。create_task は VM ID 割当・load・begin・queue 登録を行う。
3. run は VM の戻り値 0（preempt）、1（正常終了）、2（例外）を扱う。終了 task を DORMANT に移し、非 permanence task は vm_end を実行する。
4. join 待機を解除する。value は返却 register を利用するため対象の破棄・rewind・再実行より前に必要な値を保持する。
5. delete_task は DORMANT 以外を拒否し vm_close を行う。TCB の外部確保分や native handle が自動的に全て free されると考えない。
6. mrbc_cleanup は allocator/VM/symbol と task queue の全体 cleanup。個別 user task の安全な終了操作や DMA/BLE callback 停止の代わりではない。

根拠: `vendor/mrubyc/src/rrt0.c:1-1585`、`vendor/mrubyc/src/vm.c:1-3336`、`vendor/mrubyc/src/class.c:1-643`。VM ID は bitmap で MAX_VM_COUNT に制限され、close 後に再利用されます。DORMANT になっただけで ID が返却されたとは限りません。上限超過・load 失敗時は caller が確保した TCB と native resource の後始末も確認します。

## 例外・mutex と trust boundary

vm_end は未捕捉例外を hook または print/decref へ渡します。MRBC_SCHEDULER_EXIT=1 でも waiting/suspended が残れば終了条件を満たしません。run の返却と task 個別の成功を混同せず、RBOS runner は例外 hook でも失敗を記録しています。根拠: `vendor/mrubyc/src/vm.c:1-3336`、`vendor/mrubyc/src/rrt0.c:1-1585`、[Wasm runner](../../tools/mrubyc-wasm/README.md)。

mutex は owner と待機 task を持ちます。recursive lock の Ruby 経路は assertion を含むため CRuby ThreadError 互換を保証しません。priority inversion、owner terminate、待機 task の破棄、他 owner の unlock と ID 再利用は試験項目です。mutex があることは、VM を IRQ と foreground から再入可能にする保証ではありません。根拠: `vendor/mrubyc/src/rrt0.c:1-1585`。

Task.list/get/terminate/raise 等が upstream にあるので、Ruby を主役にしても非特権 code へ全 Task 権限をそのまま渡しません。[権限設計](../openblink/api-binding-patterns.md)で lifecycle と caller の権限を結びます。scheduler の最悪遅延・全遷移・実機 IRQ 同時性は未測定です。

[調査索引へ戻る](../README.md)
