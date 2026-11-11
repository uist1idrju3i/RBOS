# タスクとスケジューリング

全登録名は [Task/Mutex/VM 索引](methods-tasks.md)、状態遷移、VM ID 再利用、cleanup と例外の補足は [lifecycle](scheduler-lifecycle.md)を参照してください。

## 実行モデル

rrt0 は ready queue の先頭の VM を実行し、実行可能なまま時間片を使い切ったタスクを同優先度の後尾へ戻します。queue は `priority_preemption` の昇順で、数値が小さいほど高優先度です。**優先度付きラウンドロビンであり、全優先度へ均等な CPU 時間を配る方式ではありません**。出典: `vendor/mrubyc/src/rrt0.c:55-91,339-425`。

`mrbc_tick()` は時刻を進め、時間片を減らし、sleep 待ちを ready に戻し、`flag_preemption` を設定します。VM は命令実行の境界でフラグを見ます。C callback は直接呼び出されるため、長い C 処理をネイティブなタスク切替で中断する仕組みではありません。出典: `vendor/mrubyc/src/rrt0.c:146-181`、`vendor/mrubyc/src/vm.c:1403-1404,3307-3312`。

高優先度タスクが待機しなければ低優先度が進まない可能性があります。Ruby のシステムタスクも適切に sleep / pass する設計とし、C API は非同期化または時間上限を設けます。この時間上限は未測定です。

## 状態と待機理由

RBOS の BM quantum は `CONFIG_RBOS_TIMESLICE_TICK_COUNT=1`（1 ms tick）を既定にします。system の service sleep は10 msのままです。高優先度 task に preempt されると末尾へ戻り、再 dispatch で予算をリセットする固定実装では、旧10 tick quantum と約11 tickの起床周期が偏りを作り得ます（`vendor/mrubyc/src/rrt0.c:352-374,421-433`）。DK の X/Y 比較で双方の公平性改善が確認され、利用者は周期の組合せに依存しない1 tickを採用しました。[証拠と限界](../implementation/retrospective-P1.md#xy-比較と1-tick-の採用)を参照してください。長い native call の中断を保証する方針ではありません。

| 状態 | 値 | 意味 |
|---|---:|---|
| `TASKSTATE_DORMANT` | `0x00` | 停止・実行終了 |
| `TASKSTATE_READY` | `0x02` | 実行可能 |
| `TASKSTATE_RUNNING` | `0x03` | 実行中 |
| `TASKSTATE_WAITING` | `0x04` | sleep・mutex・join 待ち |
| `TASKSTATE_SUSPENDED` | `0x08` | 明示的な中断 |

理由は `TASKREASON_SLEEP=1`、`MUTEX=2`、`JOIN=4`。C の既定は priority 128、READY、名前長 15 です。出典: `vendor/mrubyc/src/rrt0.h:45-66`。suspend と待機理由は別に保持され、resume 後も元の待機が残る場合があります。出典: `vendor/mrubyc/src/rrt0.c:621-640`。

## Ruby の Task API

上流の分類に沿ってまとめます。名前なしの `get` など、自タスクに作用する呼び方と他タスクの object に作用する呼び方を試験で分けます。

| メソッド | 意味・注意 | 出典（`vendor/mrubyc/doc/task_class.md`） |
|---|---|---|
| `Task.create(byte_code, regs_size=nil)` | 新規 task は DORMANT。既定 register 数は MAX_REGS_SIZE。実行には run | `vendor/mrubyc/doc/task_class.md:50-61` |
| `Task.list` | 停止中を含む Task の配列 | `vendor/mrubyc/doc/task_class.md:78-80` |
| `Task.name_list` | タスク名の配列 | `vendor/mrubyc/doc/task_class.md:82-84` |
| `run` | create 済みで停止中の task を実行 | `vendor/mrubyc/doc/task_class.md:104-106` |
| `rewind` | 停止中 task を初期化して実行 | `vendor/mrubyc/doc/task_class.md:108-111` |
| `name=` / `name` | 名前の設定・取得。自タスクは Task.name でも指定 | `vendor/mrubyc/doc/task_class.md:113-119` |
| `current` / `get` / `get(name)` | 自タスクまたは指定名。名前がなければ nil | `vendor/mrubyc/doc/task_class.md:121-127` |
| `join` | 指定タスクの終了を待つ | `vendor/mrubyc/doc/task_class.md:129-157` |
| `priority=` / `priority` | 0〜255。0 が最高 | `vendor/mrubyc/doc/task_class.md:159-165` |
| `status` | READY / WAITING / SUSPENDED / DORMANT、待機理由も文字列化 | `vendor/mrubyc/doc/task_class.md:167-170` |
| `suspend` | 指定 task を中断。Task.suspend は自タスク | `vendor/mrubyc/doc/task_class.md:172-174` |
| `resume` | 中断を解除 | `vendor/mrubyc/doc/task_class.md:176-178` |
| `terminate` | task を終了 | `vendor/mrubyc/doc/task_class.md:180-214` |
| `raise(Exception=RuntimeError)` | 他タスクへ例外を送る | `vendor/mrubyc/doc/task_class.md:216-219` |
| `pass` | 自タスクの実行機会を譲る | `vendor/mrubyc/doc/task_class.md:221-223` |
| `value` | 終了時の値を返す | `vendor/mrubyc/doc/task_class.md:225-244` |

Ruby の `Task.create` と C の `mrbc_create_task(..., NULL)` は初期状態が違います。Task の API 公開を許すと、利用者コードもタスク操作を行えます。RBOS では管理 API の許可範囲を別途設計します。Ruby Task の登録は `vendor/mrubyc/src/rrt0.c:1333-1360` を確認対象にします。

## C API の一覧

ヘッダの公開宣言は `vendor/mrubyc/src/rrt0.h:114-136` です。以下は署名を保った分類です。

```c
void mrbc_init(void *heap_ptr, unsigned int size);
void mrbc_cleanup(void);
mrbc_tcb *mrbc_tcb_new(int regs_size, enum MrbcTaskState task_state, int priority);
mrbc_tcb *mrbc_create_task(const void *byte_code, mrbc_tcb *tcb);
int mrbc_start_task(mrbc_tcb *tcb);
int mrbc_delete_task(mrbc_tcb *tcb);
int mrbc_run(void);
void mrbc_tick(void);
void mrbc_set_task_name(mrbc_tcb *tcb, const char *name);
mrbc_tcb *mrbc_find_task(const char *name);
void mrbc_sleep_ms(mrbc_tcb *tcb, uint32_t ms);
void mrbc_relinquish(mrbc_tcb *tcb);
void mrbc_change_priority(mrbc_tcb *tcb, int priority);
void mrbc_suspend_task(mrbc_tcb *tcb);
void mrbc_resume_task(mrbc_tcb *tcb);
void mrbc_terminate_task(mrbc_tcb *tcb);
void mrbc_join_task(mrbc_tcb *tcb, const mrbc_tcb *tcb_join);
mrbc_mutex *mrbc_mutex_init(mrbc_mutex *mutex);
int mrbc_mutex_lock(mrbc_mutex *mutex, mrbc_tcb *tcb);
int mrbc_mutex_unlock(mrbc_mutex *mutex, mrbc_tcb *tcb);
int mrbc_mutex_trylock(mrbc_mutex *mutex, mrbc_tcb *tcb);
void pq(const mrbc_tcb *p_tcb);
void pqall(void);
```

`mrbc_get_tcb(const mrbc_vm *vm)` は inline 変換です。同ヘッダ `vendor/mrubyc/src/rrt0.h:141-150`。実装には `mrbc_wakeup_task(mrbc_tcb *tcb)` もありますが、上記公開宣言群には含まれません。出典: `vendor/mrubyc/src/rrt0.c:535-563`。呼び出し可能な公開 API をバージョンごとに確認します。

`create` は VM ID 割当やロード失敗で NULL、`start` は DORMANT 以外なら -1、`delete` は DORMANT 以外なら -1 を返します。delete は VM を close しますが、その関数だけで TCB の解放が完了すると仮定しません。出典: `vendor/mrubyc/src/rrt0.c:229-275,324-338`。NULL を確認する前に `tcb->vm` に触れないことを RBOS の必須条件とします。

## Mutex と終了処理

Ruby 側には `Mutex.new/lock/unlock/try_lock/locked?/owned?` が登録されています。出典: `vendor/mrubyc/src/rrt0.c:1444-1449`。

- C lock は再帰取得なら 1。競合時は呼出 task を WAITING に移します。
- unlock は未 lock で 1、所有者以外なら 2。一つの待機 task に所有を移します。
- trylock は成功 0、失敗 1。
- **terminate は mutex の lock 状態を解除しません**。停止後の資源回収を設計します。

出典: `vendor/mrubyc/src/rrt0.c:648-665,698-832`。優先度継承はありません。lock 待機処理は owner の priority を変更しません（同 `:717-749`）。デッドロック検出も保証しません。

Ruby の `lock` と `unlock` は成功時 self、`try_lock` は bool、`locked?` は lock 状態、`owned?` は自タスク所有を返します。再帰 lock・非所有者 unlock の処理はコメント上の ThreadError ではなく **assert** です。assert 無効時も通常の Ruby 例外になると仮定しません。出典: `vendor/mrubyc/src/rrt0.c:1382-1436`。

### RBOS の Mutex 利用規約（採用）

利用者承認済みの製品 Ruby 規約です。実機の fault 試験完了を意味しません。

- 必ず `lock` の直後から `begin … ensure unlock end` で保護します。
- lock を保持する可能性がある task を terminate してはいけません。terminate は ensure による解放を保証しません。
- 同じ Mutex を共有する task は同じ priority にします。優先度継承を前提にしません。
- 非 owner の unlock は禁止します。終了済み owner の代わりに unlock する回復処理も書きません。

非 owner の C unlock は2を返し、Ruby binding は assert します（`vendor/mrubyc/src/rrt0.c:761-767,1396-1403`）。固定構成での違いは次のとおりです。

| 構成 | 非 owner unlock の結果 |
|---|---|
| Wasm（assert 有効） | C assert → Emscripten abort、プロセス exit 1。Ruby の ThreadError ではなく、`RBOS fatal` 行も出ない。BM kernel はなく k_panic は通らない |
| BM debug（assert 有効） | Picolibc `__assert_no_args` → libc abort → k_panic →標準 fatal handler → system halt。`mrbc_hal_abort` を通らず、`RBOS fatal` 行は出ない |
| BM release（NDEBUG） | assert が消え、戻り値2を黙って無視する。lock は保持されたまま、Ruby 例外も出ない |

debug/release は実際の compile command の前処理と debug map で照合しました。`firmware/prj_release.conf:2` と `firmware/cmake/mrubyc.cmake:58-60` が VM source に NDEBUG を設定します。BM の停止経路は固定 Zephyr の [Picolibc assert](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/lib/libc/picolibc/assert.c#L24-L30)、[libc abort](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/lib/libc/common/source/stdlib/abort.c#L10-L15)、[fatal handler](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/kernel/fatal.c#L21-L45)が根拠です。実機で assertion を発火させた証拠ではありません。

挙動を固定する Wasm 試験は [owner 終了](../../tests/mruby/mutex_terminated.rb)、[例外と ensure](../../tests/mruby/mutex_ensure.rb)、[priority inversion](../../tests/mruby/mutex_inversion.rb)、[非 owner unlock の想定失敗](../../tests/mruby/mutex_non_owner.rb)です。[check.sh](../../tools/mrubyc-wasm/check.sh) は PASS 欠落・FAIL・異常な終了値を拒否します。

優先度継承は現時点で追加しません。規約の下でも inversion が実測上の問題になった場合だけ、RBOS 側の Mutex または上流への提案を再検討します。上流への連絡は、その時点で利用者の承認を得ます。

## tick と idle の移植条件

POSIX は既定 4 ms × 3 tick、Zephyr HAL は 1 ms × 10 tick です。RBOS の初期案は 1 ms × 10 とし、BLE と遅延を測定して決定します。出典: `vendor/mrubyc/hal/posix/hal.h:30-43`、`vendor/mrubyc/hal/zephyr/hal.h:48-53`。

ready がなければ `mrbc_hal_idle_cpu()` を呼びます。`MRBC_SCHEDULER_EXIT=1` の場合だけ、ready/waiting/suspended が全て空なら戻ります。既定は 0 です。出典: `vendor/mrubyc/src/rrt0.c:28-29,352-361`。BM イベント処理を idle だけに置くと、常時 runnable な Ruby task がいるときに進まないため、[HAL の設計](hal-porting.md)で扱います。

[調査索引へ戻る](../README.md)
