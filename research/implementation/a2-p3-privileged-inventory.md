# RBOS の権限対象一覧

[調査索引へ戻る](../README.md)

これは C/user-only 方針を選ぶ前の棚卸しです。以下の S/O 提案には旧 system Ruby 構成を前提とするものが含まれます。現在の判断は [A2 設計](a2-p3-design.md)を優先し、role registry や厳格な全 Task 認可を Ver 1 の実装義務とは扱いません。S は native の信頼された管理処理にも適用します。以下の「今回」は先行の静的棚卸しを指します。

## 要約

現行の RBOS 独自 Ruby API で system caller を照合するのは `RBOSSystem.service` です。Task の他 task 操作、共有 method・定数の変更には、その保護がありません。GPIO/ADC/Button の引数・pin・lease 検査はありますが、system/user の認可とは別です。

管理権限が必要なのは、他 task の制御、信頼された Ruby 定義の変更、boot/更新、共有永続領域、無線構成、WDT/回復方針、権限付与です。温度・電源電圧の取得や、許可された pin・自分の要求の操作まで一律に system 専用にする必要はありません。

初期方針は「bytecode も firmware に含めて DFU」。独立した bytecode 転送・ZMS 保存・reload は将来検討であり、P3〜P6 の実装確約ではありません。factory reset も、今回確認した RBOS 段階計画には独立した実装項目がなく、OpenBlink の実装を参考として掲載します。

### 読み方・範囲

- 対象は RBOS `460224d91df9bb89f479a97f76b1919d32737c65`、mruby/c `434bccd609f2a3e90d6bb95c458621898bc6a508`。
- 「なし」は system/user の caller 認可がない意味です。型・busy・所有権等の検査の有無は別に記します。
- 「Ruby 非公開」は Ruby の直接入口がない意味で、信頼された native 内部呼出しにも検査があるという意味ではありません。
- 推奨の **S**＝system 専用、**O**＝user でも可（自分自身の範囲）、**U**＝user でも可、**N**＝Ruby に公開しない。これは提案であり承認済み実装ではありません。
- S は特定 TCB だけという意味でなく、native 管理処理・認証済み loader・製造手順を含む信頼された管理経路です。N でも内部実行主体は信頼する必要があります。
- 同じ理由・保護を持つ API は一行にまとめています。組み込みの算術・文字列等の一般演算は対象外ですが、共有状態の変更は独立項目にしています。
- 根拠の略記：B=`src/rbos/`、F=`firmware/src/`、M=`vendor/mrubyc/src/`、I=`research/implementation/`、D=`research/dfu/`、N=`research/nrf-bm/`、SDK=`vendor/sdk-nrf-bm/`。API 名未定の項目を実在する Ruby method としては扱いません。

## 1. 現行の RBOS 独自 Ruby API：全登録と Ruby wrapper

| 操作名 | 状態 | 現在の保護 | 特権との関係・理由 | 推奨 | 根拠 |
|---|---|---|---|---|---|
| `RBOSSystem.service` | 実装済み | caller 検査あり：登録 TCB の VM と一致 | BM scheduler、I/O 後処理、log を進める管理入口 | S | F/runtime.c:63-115 |
| `Temperature.read` | 実装済み | なし。型・引数・backend context 検査 | 温度取得。S115 の正規経路を使うため、通常利用に管理権限不要 | U | B/bindings.c:8-23、src/platform/nrf/backend.c:19-29 |
| `Temperature.new` | 実装済み | なし。ただし常に TypeError | 作成不可の入口。管理者用 constructor ではない | U（拒否を維持） | B/bindings.c:26-36 |
| `GPIO.new`、`GPIO.setmode`、`GPIO#setmode` | 実装済み | なし。許可 pin・mode・Button busy 検査 | 共有 pin の方向・電気特性を変更。他 task との調停が必要 | O：割当 pin のみ | B/gpio_binding.c:64-100,130-162,212-227 |
| `GPIO.read_at`、`GPIO#read`、`GPIO.high_at?`、`GPIO.low_at?`、`GPIO#high?`、`GPIO#low?` | 実装済み | なし。許可 pin 検査 | 許可 pin の読取りは通常利用。秘密・保護対象 pin は公開範囲外 | U：公開 pin のみ | B/gpio_binding.c:164-190,220-226、src/platform/nrf/gpio.c:32-49,69-75 |
| `GPIO.write_at`、`GPIO#write` | 実装済み | なし。pin・level・Button busy 検査 | 他 task の出力や安全表示を変更できる | O：割当 pin のみ | B/gpio_binding.c:192-208,223-227、src/platform/nrf/gpio.c:78-85 |
| `Button.new` | 実装済み | なし。監査済み Button pin、二重 claim、枯渇検査 | GPIOTE channel と pin を占有するが通常の入力用途 | O：割当 pin/購読のみ | B/button.c:70-103 |
| `Button#poll`、`#wait`、`#each_event`、`#pressed?` | 実装済み | なし。native は subscription identity 検査 | 自分の購読の取得・待機。Proc は caller task で動く | O：自分の購読のみ | B/button.c:52-67,117-143、B/button.rb:1-17 |
| `Button#close` | 実装済み | なし。subscription identity・解除結果検査 | pin/channel を解放。他人の購読を強制解除させない | O | B/button.c:18-26,106-115 |
| `Button.stats` | 実装済み | なし。型・引数検査 | 共有 queue の件数・overflow の読取り。権限変更ではない | U：公開診断値として | B/button.c:146-161 |
| `ADC.internal` | 実装済み | なし。`:dvdd/:avdd/:vdd` 限定 | 電源計測用 object の生成 | U | B/adc_binding.c:31-58 |
| `ADC#read_raw`、`#read_voltage`、`#read` | 実装済み | なし。下層の request identity・busy 検査 | SAADC は共有・排他だが通常計測。要求単位に制限する | O | B/adc.rb:1-23、B/adc_binding.c:71-150 |
| `ADC.new` | 実装済み | なし。ただし入力不足／外部 ADC 未対応で拒否 | 未対応 API。管理権限で有効になるわけではない | U（拒否を維持） | B/adc_binding.c:60-64 |
| `ADC#__start`、`#__poll`、`#__finish`、`#__measure` | 実装済み | なし。native は request identity・token 検査 | 内部 wrapper 用だが Ruby から呼べる。取消しは自己要求に限定すべき | O：内部入口も同じ認可 | B/adc_binding.c:71-150、B/adc.rb:12-23、I/api-contracts.json:7-11 |
| `RBOSADCRequest.new`、`RBOSButtonSubscription.new` | 実装済み | なし。ただし常に TypeError | native lease の偽造防止。一般生成 API にしない | N：現在は拒否入口のみ存在 | B/adc_binding.c:66-69,156-164、B/button.c:164-177 |

**現状との差**：GPIO の共有表に TCB owner はなく、ADC/Button も TCB ごとの caller 制限ではなく lease identity を使っています。O は現在保証される task 隔離ではありません。object の他 task への譲渡を許すかも別途決める必要があります。現行 GPIO は LED0..3 を公開しており、まだ system LED は予約していません（I/resource-reservations.md:26-29）。

## 2. mruby/c：Task・同期・診断

Task の class 呼出しと instance 呼出しは同じ callback に登録されます。class 呼出しが自己対象でも、instance は他 TCB を指定できます。

| 操作名 | 状態 | 現在の保護 | 特権との関係・理由 | 推奨 | 根拠 |
|---|---|---|---|---|---|
| `Task.priority=`／instance `priority=` | 実装済み | なし。0..255 検査だけ | 他 task の実行順・飢餓に影響 | O、他 task は S。自己の許可優先度帯は要判断 | M/rrt0.c:1049-1072、I/porting-plan.md:76 |
| `Task.suspend`／instance `suspend` | 実装済み | なし | 他 task の進行を停止できる | O、他 task は S | M/rrt0.c:1125-1136、I/porting-plan.md:76 |
| `Task.terminate`／instance `terminate` | 実装済み | なし | 他 task を強制終了。Ruby ensure を保証しない | O、他 task は S | M/rrt0.c:653-663,1159-1170、I/porting-plan.md:76 |
| instance `Task#raise` | 実装済み | なし | 対象 VM の例外を置換し sleep を解除 | O、他 task は S | M/rrt0.c:1179-1204、I/porting-plan.md:76 |
| `Task#resume` | 実装済み | なし | 他 task を再開。停止中の自己は呼び出せない | S。user に委譲する対象・権限は要判断 | M/rrt0.c:1144-1151 |
| `Task#run`、`#rewind` | 実装済み | なし。DORMANT 検査だけ | 他 task の再始動・実行状態初期化。旧権限を再利用させない | S を既定。自分が生成した子への委譲は未決 | M/rrt0.c:1306-1330 |
| `Task.name=`／instance `name=` | 実装済み | なし | 他 task の検索名や診断を変更できる | O、他 task は S。名前を認証キーにしない | M/rrt0.c:1001-1019 |
| `Task.create` | 実装済み | なし | bytecode 実行、TCB/VM/IREP と共有 pool を消費 | U：上限・入力検査、子は常に user。system 生成は S | M/rrt0.c:1263-1298、I/porting-plan.md:72-79 |
| `Task.get`、`.current`、`.list`、`.name_list` | 実装済み | なし | 他 task の発見・handle 取得 | U を基本。system handle の可視性は要判断。取得だけで変更を許可しない | M/rrt0.c:919-993 |
| `Task.name`、`.priority`／instance `name`、`priority`、`status` | 実装済み | なし | 読取情報。古い handle の lifetime 検査は別途必要 | U：公開する task 情報に限る | M/rrt0.c:1028-1040,1080-1116 |
| `Task#value` | 実装済み | なし。DORMANT 検査だけ | 対象 task の戻り値 object を取得。秘密や lease の流出になり得る | O：自分／明示的に共有した結果。他 task は S | M/rrt0.c:1228-1241 |
| `Task#join` | 実装済み | なし | 待つ側だけを WAITING にする。対象を止める操作ではない | U：有効 handle・待機方針を検査 | M/rrt0.c:673-689,1212-1220 |
| `Task.pass`、Object の `sleep`、`sleep_ms` | 実装済み | caller の TCB を使う。role 検査なし | 自分の実行を譲る／待つ | O | M/rrt0.c:859-906,1249-1255,1508-1509 |
| `Mutex.new/#lock/#unlock/#try_lock/#locked?/#owned?` | 実装済み | unlock に TCB owner 検査あり。system role 検査なし | 通常の task 間同期。管理 lock と無制限に共有しない | U：自分たちの mutex。unlock は owner のみ | M/rrt0.c:717-786,1370-1449 |
| `VM.tick` | 実装済み | なし | tick の読取り。clock の変更ではない | U | M/rrt0.c:1457-1467 |
| Object の `p/print/puts/printf` | 実装済み | なし | 共有 console を消費し、秘密の出力先にもなる | U：出力量制限。log 設定変更とは区別 | M/c_object.c:825-843、F/hal/hal.c:75-94 |
| Object の `memory_statistics` | 実装済み（MRBC_DEBUG 時） | なし | 全 pool の診断。印字も行う | S/debug 専用を推奨。匿名化した数値の一般公開は要判断 | M/c_object.c:459-479,849-855 |
| Object の `object_id/instance_methods/instance_variables` | 実装済み（MRBC_DEBUG 時） | なし | 内部 identity や共有定義の調査 | S/debug 専用を推奨 | M/c_object.c:381-456,849-852 |
| `Symbol.all_symbols`、Object の `constants` | 実装済み | なし | 全体の symbol・定数名を列挙 | U：名前を秘密にしない。列挙制限を認証の代用にしない | M/symbol.c:369-380,428、M/c_object.c:619-645 |
| `Proc.new/#call`、`yield` | 実装済み | role 検査なし | Proc は独立した権限主体ではなく caller VM で動く | U。ただし system が未信頼 Proc を実行するのは S 相当の委譲判断 | M/c_proc.c:96-130 |
| Object の `raise` | 実装済み | caller VM に例外を設定 | `Task#raise` と違い他 VM を選択しない | O | M/c_object.c:325-378 |
| Object の `new/dup` | 実装済み | なし。追加 native data を一般には持たない | 通常 object は非特権。Task/native handle の偽造には使わせない | U：native handle 型は別途拒否・検証 | M/c_object.c:110-114,189-197 |

固定版で独立した Kernel class の登録は見つかりませんでした。Kernel 相当の `raise`・出力等は Object、sleep は rrt0 から Object に登録されます。Ruby の `system/exec/eval/reboot/exit` 等を実在する RBOS 管理 API としては列挙しません。

`Symbol.all_symbols` は debug 限定ではありません。MRBC_DEBUG に依存する Object の調査用 method と区別しています。

## 3. Ruby の定義変更・共有状態：独立した権限対象

| 操作名 | 状態 | 現在の保護 | 特権との関係・理由 | 推奨 | 根拠 |
|---|---|---|---|---|---|
| 共有 class の `def`、class method の定義・再定義（OP_DEF/TDEF/SDEF） | 実装済み | role/caller 認可なし。一部 class は flag_nomethod で拒否 | system task が後で呼ぶ処理や認可 wrapper を置換できる | 保護 class は S。user 自身の定義は O としたいが所有境界は未実装 | M/vm.c:2975-3048、M/class.c:415-463 |
| `alias`（OP_ALIAS） | 実装済み | なし | 既存 callback の別名化・method 差替え経路 | 保護 class は S、user 自身の定義は O | M/vm.c:3057-3079 |
| `class/module` の生成・再オープン | 実装済み | role 認可なし | 共通定数表の class を再利用し、その定義を変更可能 | 保護 class は S、user 自身の定義は O | M/vm.c:2832-2941 |
| 定数の定義・再代入（OP_SETCONST） | 実装済み | なし | `RBOSSystem` 等の名前の参照先や共有設定を変更できる | system/共有定数は S。user 定数の所有境界は要設計 | M/vm.c:755-768、M/global.c:57-82 |
| global 代入（OP_SETGV）、共有 object の String/Array/Hash・ivar 更新 | 実装済み | role 認可なし | 定数名を固定しても、参照先の可変状態を変更できる | O。system の信頼状態は Ruby に共有しない | M/vm.c:632-637,646-674、M/global.c:153-167、M/c_array.c:1367-1398、M/c_hash.c:720-746、M/c_string.c:2497-2553 |
| Object の `attr_reader/attr_accessor` | 実装済み | なし | native 関数から共有 class に method を追加する別経路 | 保護 class は S、user 自身の定義は O | M/c_object.c:530-572 |
| Object の `include/extend` | 実装済み | なし | method 探索対象の super chain を変更 | 保護 class は S、user 自身の定義は O | M/c_object.c:579-613,833-834 |
| Object の `public/private/protected` | 実装済み | c_ineffect（実質 no-op） | private 指定や `__` 命名では API を隠せない | U：認可の手段として使わない | M/c_object.c:836-838 |
| `String#to_sym/#intern`、symbol を増やす動的定義 | 実装済み | role 認可なし | 全体の symbol table・pool を消費する | U：資源上限が必要 | M/c_string.c:2529-2530、M/symbol.c:156-185 |

これは「全ての def に管理者認証を要求する」という提案ではありません。**信頼された共有定義の変更と、user が普通に自分の class を書くことを区別する必要がある**という一覧です。現行の共有 class 空間では、その区別を caller TCB 検査だけで保証できません。前回の Wasm 再現結果もこの問題を示しています。

## 4. 現行 native / C の管理操作

| 操作名 | 状態 | 現在の保護 | 特権との関係・理由 | 推奨 | 根拠 |
|---|---|---|---|---|---|
| `rbos_system_set_task` | 実装済み | Ruby 非公開 | system caller の基準を変更する最上位の操作 | N：起動管理のみ | F/runtime.c:118-121、F/main.c:29-37 |
| `rbos_system_define`、`rbos_define_classes`、各 `rbos_*_define` | 実装済み | Ruby 非公開 | native callback・class・内部 lease 型を登録／初期化 | N | F/runtime.c:112-116、B/bindings.c:31-40、B/adc_binding.c:153-165、B/button.c:169-183 |
| `mrbc_init/mrbc_cleanup`、`mrbc_cleanup_vm` | 実装済み | Ruby 非公開 | 共通 pool・global/class・VM 管理全体の初期化／破棄 | N | M/rrt0.c:845-852,1479-1510、M/vm.c:197-200 |
| `mrbc_tcb_new/mrbc_create_task/mrbc_start_task/mrbc_delete_task`、`mrbc_vm_begin/end/close` | 実装済み | C は Ruby 非公開。create/run 等には上記 Ruby 入口あり | lifetime・VM ID 再利用・実行権限に関係 | N：Ruby には認可済み wrapper のみ | M/rrt0.c:203-272,323-339、M/vm.c:336-412 |
| `mrbc_change_priority/suspend_task/resume_task/terminate_task/wakeup_task/set_task_name` | 実装済み | C 自体は role 検査なし。直接は Ruby 非公開 | 任意 TCB の状態を変更できる | N：Ruby 入口では対象認可 | M/rrt0.c:282-306,533-663 |
| `mrbc_load_mrb`、`mrbc_run_mrblib`、`mrbc_define_method/class`、`mrbc_set_const/class_const/global` | 実装済み | 直接は Ruby 非公開。対応 opcode 等は上表 | code のロード・共通定義の変更 | N | M/load.c:303-325、M/class.c:215-233,274-295,593-615、M/global.c:57-82,153-167 |
| `rbos_maintenance`、`bm_scheduler_process`、`rbos_bindings_service/button_service/adc_service` | 実装済み | Ruby の直接入口なし。service は caller 検査、idle と通常 I/O からも実行 | SD deferred 処理、期限・解放、配送、log の進行 | N：native が管理。system TCB だけから実行されるわけではない | F/runtime.c:63-98、F/hal/hal.c:69-73、B/adc_binding.c:16-21,89,124 |
| `rbos_event_post/take/snapshot`、`rbos_event_queue_push/pop` | 実装済み | Ruby 非公開。IRQ lock／型・generation 等は下層で検査 | 他 task 向け event の投入・消費・統計 | N：生の投入・消費は渡さない | F/runtime.c:22-43、B/event_queue.c:8-43、B/button.c:29-49 |
| `rbos_resources_probe` | 実装済み | Ruby 非公開。main が SD/VM 起動前に実行 | scheduler queue を枯渇させる自己検査 | N：起動前／試験専用 | F/resource_probe.c:18-44、F/main.c:23-24 |
| `rbos_stack_paint`、`rbos_resources_log`、`rbos_tick_take_interval`、pool/stack 統計 | 実装済み | Ruby 非公開 | stack 塗り潰し・統計リセットは内部、公開用 read-only snapshot とは別 | N：必要な診断だけ別 API | F/runtime.c:38-61,75-97、F/resources.c:43-50、F/hal/hal.c:37-44 |
| `mrbc_debug_dump_const/global/symbol`、`mrbc_alloc_print_statistics`、`mrbc_alloc_print_pool_header` | 実装済み（条件付き debug 機能） | Ruby 非公開 | 共有定数・global の値や allocator の内部を出力 | N：製品での詳細 dump は公開しない | M/global.c:190-258、M/symbol.c:447-478、M/alloc.c:1051-1075 |
| `mrbc_hal_init`、tick handler、`mrbc_tick`、IRQ disable/enable | 実装済み | Ruby 非公開 | 時間基盤・割込み制御。SD の予約優先度を壊せない | N | F/hal/hal.c:19-67、F/resources.c:12-41 |
| `mrbc_hal_idle_cpu` | 実装済み | Ruby 非公開 | 保守処理と CPU idle。user sleep と同義ではない | N | F/hal/hal.c:69-73 |
| `mrbc_hal_write/flush`、`log_process/LOG_PANIC` | 実装済み | 直接は Ruby 非公開。通常出力は Object から利用 | 共有出力・ログ配送。panic は回復経路に関係 | N：通常出力 wrapper は U | F/hal/hal.c:75-101、F/runtime.c:72-74 |
| `mrbc_hal_abort` → `k_fatal_halt` | 実装済み | Ruby 非公開 | 全体停止。現時点では release もこの halt 経路 | N | F/hal/hal.c:96-103、F/main.c:39-41 |
| 起動 LED の `nrf_gpio_cfg_output/nrf_gpio_pin_write` | 実装済み | Ruby 非公開 | 起動状態の表示。現在は後で一般 GPIO に引き渡す | N：P3 の system 表示は下表 | F/main.c:20-21、I/resource-reservations.md:29 |
| `rbos_nrf_gpio_configure/read/write`、pin lookup/validate | 実装済み | 直接は Ruby 非公開。許可 pin・busy 検査 | 電気特性と共有 pin の制御 | N：許可 pin の Ruby wrapper を利用 | src/platform/nrf/gpio.c:22-85 |
| `rbos_gpio_claim/release/unclaim`、`rbos_nrf_button_watch/unwatch` | 実装済み | Ruby 非公開。pin/generation 検査 | pin・GPIOTE channel の割当／解放 | N：Button lease に限定 | B/gpio_binding.c:64-84、src/platform/nrf/button.c:59-123 |
| `rbos_adc_start/cancel/take/service`、`rbos_nrf_adc_start/poll/cancel` | 実装済み | Ruby 非公開。token・状態・context 検査 | SAADC、IRQ、DMA、校正、STOPPED 確認 | N：要求単位の Ruby wrapper を利用 | B/adc.c:4-66、src/platform/nrf/adc.c:24-153 |
| `rbos_ble_init` → SD enable、device name、advertising init/start | 実装済み | Ruby 非公開 | device 全体の無線構成・接続受付 | N：将来の設定 wrapper は S | F/ble.c:73-95 |
| `on_ble_event` → sys attrs／pairing 拒否／bond 不在の応答 | 実装済み | Ruby 非公開 | 接続の security・GATT 状態を決める | N | F/ble.c:12-65 |
| RADIO/CLOCK/TEMP/RRAMC、SD/MPSL 予約 timer/IRQ/DPPI の直接操作 | SDK に機能あり、RBOS は予約・利用制限を実装済み | Ruby 非公開、build assertions・許可 pin 制限 | 無線・時刻・NVM を破壊する。system でも無制限に触ってよいものではない | N：正規 SD/BM API と予約規約のみ | I/resource-reservations.md:15-28,35-45、F/resources.c:12-41 |

## 5. 計画・SDK 結合・将来候補

「計画のみ」は RBOS の Ruby/native 管理 API として未実装の意味です。SDK に既に関数がある場合は区別して記します。

| 操作名 | 状態 | 現在の保護 | 特権が必要な理由 | 推奨 | 根拠 |
|---|---|---|---|---|---|
| system LED の表示変更（API 名未定） | 計画のみ | なし。現 GPIO は LED0..3 を一般公開 | 故障・DFU・安全状態を user に偽装させない | S。対象 LED の番号も要決定 | I/porting-plan.md:79、I/resource-reservations.md:26-29 |
| system role/capability の付与・失効、TCB registry／generation 更新 | 計画のみ | Ruby 非公開の設計。現行は system_task pointer のみ | 認可そのものを決定 | N | I/porting-plan.md:72-79、I/checklist.md:85-90、F/runtime.c:118-121 |
| runtime 昇格／HMAC 検証・鍵管理 | 検討中・未実装（計画のみ、採否未決） | 入口なし | 鍵の生成・provision・失効、権限付与を user に任せない | 鍵管理 N、操作承認 S。一般 HMAC 計算まで S とする必要はない | I/porting-plan.md:72-79、research/openblink/hmac-authentication.md:5-27、今回までの検討 |
| WDT 初期化・timeout/channel 設定・kick | 計画のみ | Ruby 非公開、RBOS WDT 未実装 | 回復を無効化したり、停止を隠したりできる | 設定 N、kick は S | I/porting-plan.md:77、I/checklist.md:91 |
| fatal 時の log flush → release reboot／debug halt | 計画のみ（halt は実装済み） | Ruby 非公開 | 回復方針・全 task の寿命を決める | N | I/porting-plan.md:77、F/hal/hal.c:96-103 |
| 通常 reboot／reset（`sys_reboot` 等の wrapper、名前未定） | RBOS wrapper は計画のみ | Ruby 非公開、入口なし | 全 task と接続を終了 | S：安全停止を経由 | I/porting-plan.md:77、N/mcumgr.md:13,37 |
| `dfu_request(reason)`、`bootmode_set(BOOT_MODE_TYPE_BOOTLOADER)`＋reset | 計画のみ。候補名で Ruby API 未確定 | Ruby 非公開、app 入口なし | 独立 loader へ切替、実行中 app を停止 | S：内部 boot mode write は N | N/mcumgr.md:35-41、D/single-bank-dfu.md:12-21 |
| GPIO/reset-pin／無効 image による loader 起動 | SDK 結合済み。三入口の受入試験は計画 | Ruby 非公開。物理入力・boot 検証 | 可用性と復旧に関係。Ruby 認可の外側 | N：物理・boot policy | firmware/sysbuild.conf:1-2、D/single-bank-dfu.md:12-21、I/porting-plan.md:106 |
| MCUmgr image upload・`img_mgmt_write_image_data`、application 上書き | SDK loader 実装・sysbuild 結合済み。RBOS 運用認証は計画 | Ruby 非公開。署名検証と transport 認証は別。default OPEN | firmware と全 bytecode を交換 | S：認証済み管理 transport、native loader | SDK/applications/firmware_loader/ble_mcumgr/prj.conf:20-47、SDK/subsys/mgmt/mcumgr/grp/img_mgmt/src/bm_img_mgmt.c:157-195、N/ble-services.md:28 |
| MCUmgr image info/state/slot info、`image_info()` 候補 | SDK に実装。Ruby wrapper は計画のみ | Ruby 非公開。command 認証は要設計 | 版などの read-only 情報と install 制御を分ける | U：公開用の版・状態だけ。状態変更は S | N/mcumgr.md:12,38、SDK/applications/firmware_loader/ble_mcumgr/prj.conf:34-35 |
| MCUmgr OS reset、echo、params、bootloader info | SDK loader に設定あり。権限設計は計画 | Ruby 非公開。既定 transport は OPEN | reset は全体変更。echo/info は同等の特権ではない | reset S、公開情報 U、raw 診断は要判断 | SDK/applications/firmware_loader/ble_mcumgr/prj.conf:36-40、N/mcumgr.md:13,41 |
| installer による SoftDevice／firmware loader 更新 | SDK に実装。RBOS 実機受入は計画 | Ruby 非公開、署名・boot 経路 | app より下位の更新・復旧経路を変更 | N：認証済み製造／更新経路のみ | D/single-bank-dfu.md:25-37、I/porting-plan.md:101,106 |
| `bm_installs_write/invalidate`、flash map／install metadata 設定 | SDK に実装。RBOS の一般 API はなし | Ruby 非公開。SDK header も非公開用途と明記 | boot 対象・位置・長さ・整合性を壊せる | N | N/mcumgr.md:15,19、N/storage-and-fs.md:14 |
| ED25519 署名鍵の生成・署名・KMU 公開鍵 provisioning／失効・BOOTCONF/debug 保護 | build/準備手順あり。製造・失効・復旧の完成は計画 | Ruby 非公開。host／製造操作 | image trust root。誤設定で不正更新や復旧不能 | N：製造管理。秘密署名鍵を device Ruby に渡さない | D/single-bank-dfu.md:44-46、I/checklist.md:116-117 |
| BLE 広告の開始・停止・再開、device name 変更 | 固定名・開始は実装済み。運用条件・`RBOS_XXXX` は計画 | Ruby 非公開 | 接続性・電力・製品識別を全体で変更 | S：native owner に集約 | F/ble.c:73-95、I/porting-plan.md:96-104、I/checklist.md:112-115 |
| BLE DLE/MTU/接続パラメータ・security policy | 現 app は event 記録／pairing 拒否。P5 tuning は計画 | Ruby 非公開 | 無線・buffer・認証・他接続へ影響 | S：設定は native policy。状態取得は U 候補 | F/ble.c:23-59、I/porting-plan.md:96,104 |
| `dfu_name_set`、MCUmgr flat name settings の書換え | SDK に機能、RBOS wrapper は計画のみ | Ruby 非公開。transport 認証は別途 | loader の識別と app/loader 間情報を書換え | S | N/mcumgr.md:14,39-41、N/storage-and-fs.md:12-13 |
| `bm_rmem_*`／`boot_handoff_write/read`・retention clear | SDK に機能、RBOS API は計画のみ | Ruby 非公開。CRC は認証ではない | reboot を跨ぐ boot/loader への指示・引継ぎ | N：必要な要求だけ S wrapper | N/storage-and-fs.md:12,18 |
| `bm_storage_init/uninit/read/write/erase/is_busy` | SDK に機能、app の一般 storage API は計画のみ | Ruby 非公開 | 物理範囲・partition・書換え寿命・実行中 blob に影響 | N：raw address API は渡さない | SDK/include/bm/storage/bm_storage.h:232-325、N/storage-and-fs.md:7-10,24 |
| `bm_zms_mount/clear`、GC・領域／容量／cache 設定 | SDK に機能、RBOS 保存採用は将来検討 | Ruby 非公開 | 全 key、寿命、参照中 bytecode に影響 | N：保守要求が必要なら S | SDK/include/bm/fs/bm_zms.h:165-181、D/zms-direct-execution.md:24-30 |
| `bm_zms_write/delete`、`settings_set/delete` 候補 | 計画のみ（SDK ZMS は実装済み） | Ruby 非公開 | 永続共有 key・peer・system program の保護が必要 | system 領域 S、user 名前空間 O。分割未決 | N/storage-and-fs.md:11,24、SDK/include/bm/fs/bm_zms.h:205-221 |
| `bm_zms_read/read_hist`、free-space/status、`settings_get` 候補 | 計画のみ（SDK ZMS は実装済み） | Ruby 非公開 | 読取りでも secret・他 task データは保護。全走査の負荷もある | O：自己 key。匿名化した使用量は U、raw 履歴は N | N/storage-and-fs.md:11,30、SDK/include/bm/fs/bm_zms.h:241-262 |
| bonding の追加、peer DB 読書き／全 peer 削除・BMS authorize | 将来検討。今回は bonding 非採用 | Ruby 非公開、現 app は pairing 拒否 | 他 peer の資格情報・接続 trust を変更 | 管理は S、raw key/DB は N | I/checklist.md:81、F/ble.c:48-55、N/ble-services.md:9,28 |
| 外部 bytecode の受信・chunk/offset/再送・commit | 将来検討。P4/P5 の初期範囲外 | Ruby 非公開、RBOS 経路なし | 実行 code・保存領域・認証対象を変更 | S：user program でも管理された install 経路 | I/porting-plan.md:88,98、research/openblink/future-support.md:3-15,27-35 |
| bytecode 認証・trust class 決定・load/reload、全 VM 停止・再作成、default 復旧 | 将来検討。const の起動 load は実装済み | 動的管理は Ruby 非公開。現起動は table 先頭を system 登録 | 全 task・共有 symbol/method・blob lifetime を変更 | S／native 内部 N。自己申告 role を受け付けない | F/main.c:29-37、research/openblink/future-support.md:13-15,27-35、D/embedded-bytecode.md:40 |
| log level/backend 変更、debug/shell 管理入口 | 公開範囲は計画のみ。現在の log は native、shell は無効 | Ruby 管理 API なし | 情報漏えい、console 独占、障害診断の改変 | 設定・詳細 debug は S/N、公開用 read-only 状態は U 候補 | I/checklist.md:88、F/resources.c:13-15、F/runtime.c:94-97 |
| reset reason の起動時記録（`hwinfo_get_reset_cause` 等） | 計画のみ：未承認 A2 案 #13 | Ruby 非公開、RBOS 未接続 | 障害診断。read-only 値と記録の消去を区別する | 当初は N。公開用の読取りは U 候補、clear は S/N | 前回の未承認 A2 案 #13、参照実装 O2 src/app/init.c:59-75 |
| P6 fault injection、故意の停止／WDT starvation／OOM／DFU 電源断試験 | 計画のみ（既存の host fake/自己検査は一部実装済み） | 製品 Ruby API なし | 全体停止やデータ破壊を意図的に起こす | N：試験環境・debug 専用。一般 allocation 自体を管理者専用にはしない | I/porting-plan.md:110-119、I/checklist.md:123-131 |

P6 の map/size・ログ収集、CI、文書検査などは開発作業であり、device の特権コマンドではありません。独自 BLE service の追加例も SDK 調査にありますが、P3〜P6 で全 service を実装する計画とは扱いません。

## 6. OpenBlink の参照例：system 専用と単なる管理処理を区別

O1 は [openblink-demo-mdbt50q-db-40](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3)、O2 は [openblink-demo-nrf](https://github.com/OpenBlink/openblink-demo-nrf/tree/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a)。いずれも固定 SHA の checkout を読みました。根拠は各 repository の相対パスです。

| 操作名 | 状態 | 現在の保護 | 特権との関係・理由 | RBOS での推奨 | 根拠 |
|---|---|---|---|---|---|
| O1 `LED.set(part: :LED3, ...)` | OpenBlink にのみある | caller 検査あり：VM ID。LED1/2 は不要 | system 専用表示の具体例 | S | O1 src/api/led.c:78-94 |
| O1 `api_api_set_systemtask/check_systemtask` | OpenBlink にのみある | Ruby 非公開。登録の HMAC 検証は TODO | system identity の設定・照合 | N。認証済み登録と lifetime 管理が必要 | O1 src/api/api.c:47-67 |
| O1 `Blink.req_reload?`、`api_blink_check_normality` | OpenBlink にのみある | req_reload? に system caller 検査なし。呼出 VM の watchdog flag を更新 | health report と WDT の仕組み。system 専用ではない | user health report O、最終 WDT kick S | O1 src/api/blink.c:165-171,188-205 |
| O2 `LED.set` の LED1/2/3 | OpenBlink にのみある | なし。O1 の system 判定は存在しない | 同じ API 名でも版で保護が異なる | system 用に割り当てた LED だけ S | O2 src/api/led.c:78-92 |
| O2 `Blink.lock/unlock` | OpenBlink にのみある | system caller 検査なし。Zephyr mutex の操作 | VM restart を妨げられる。Ruby TCB の owner 制御と同一ではない | N：必要なら期限付き install lease を別設計 | O2 src/api/blink.c:39-44,69-88 |
| O2 `Blink.req_reload?` | OpenBlink にのみある | なし。deprecated で常に false | 現版では管理操作を起こさない | U：互換 API の要否は別問題 | O2 src/api/blink.c:55-58 |
| O2 `blink_store/delete`、`storage_write/delete`、`app_mrubyc_vm_restart` | OpenBlink にのみある | Ruby 非公開。storage/restart mutex は認証ではない | bytecode 保存・削除・全 task の停止／再生成 | S、raw storage と停止内部は N | O2 src/app/blink.c:73-95、src/app/storage.c:117-147、src/app/mrubyc_vm.c:97-142 |
| O2 BLE event の store/reload/reboot dispatch | OpenBlink にのみある | Ruby 非公開。dispatch 自体に system TCB 認可なし | 外部から program と稼働状態を変更 | S：transport 認証を別途検査 | O2 src/app/comm.c:55-87 |
| O2 `init_reboot` | OpenBlink にのみある | Ruby 非公開。storage mutex 待機あり | 全体 reboot | S wrapper／native 内部 N | O2 src/app/init.c:108-123 |
| O2 `init_factory_reset` | OpenBlink にのみある。RBOS の独立実装計画は未決 | Ruby 非公開 | 両 bytecode slot と全 bond を削除 | S：物理確認・認証・消去範囲の決定が必要 | O2 src/app/init.c:134-147 |

## 判断が必要な点

1. system LED の割当、user pin の task 間所有、lease の譲渡をどうするか。
2. user に見せる task 情報・戻り値と、子 task の再開・再実行の委譲範囲をどうするか。自己 `priority=` の上限も別の判断です。
3. 一般の user Ruby に class 定義を許しつつ、信頼された共有定義をどう守るか。sudo/HMAC の前にこの境界が必要です。
4. storage の system/user key 分割、transport 認証、debug 情報の一般公開範囲。これらは「全部 system 専用」にする以外の選択肢があります。

## 確認範囲

コード・設定・計画の静的な棚卸しです。今回、Wasm 試験や BM build、実機、BLE の認証試験、外部管理 command の網羅的な実行試験はしていません。SDK の全 optional 機能を RBOS の実装済み command として数えていません。tracked file・vendor は変更していません。
