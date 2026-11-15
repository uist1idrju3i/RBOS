# A2 / P3：C の管理処理と user-only mruby/c

[調査索引へ戻る](../README.md)

## 現在の方針と状態

2026-11-15 の利用者判断は「重要な操作は C に実装する」「mruby/c の VM は1つだけ」です。ここでは **mruby/c の実行環境は一つ、その上では user Ruby だけを実行し、特権を持つ system Ruby は置かない**構成と解釈します。通常の複数 Ruby Task を廃止する判断ではありません。Task まで一つに制限する場合は別の API 変更です。

これは設計と一時試作の記録です。製品コード、設定、vendor は未変更です。Ver 1 のバイトコードは C と一緒に firmware へ埋め込みます。HMAC と外部転送の認証は将来の課題です。[脅威モデルと認証候補](a2-p3-authentication.md)、[操作一覧](a2-p3-privileged-inventory.md)、[証拠と再現](a2-p3-evidence/README.md)を併読してください。

Ruby の TCB/VM は既に複数作れますが、定数・global は共有です（`vendor/mrubyc/src/global.c:29-43`）。二重 compile による複数実行環境の検討は、利用者の追加指示により中止しました。

## 現在 system がしていること

| 現在の処理 | C へ移す場合 | 根拠 |
|---|---|---|
| `system.rb` は service → sleep を反復し、例外を表示して再試行 | Ruby loop をなくし、foreground の native 周期処理にする | `firmware/ruby/system.rb:1-8` |
| main は全 task を生成し、先頭を system と登録して priority 0 にする | user task だけを生成。先頭特別扱い・system pointer を廃止する候補 | `firmware/src/main.c:26-41` |
| service は caller 検査後に `rbos_maintenance(true)` を呼ぶ | native supervisor が直接呼ぶ。Ruby method lookup を使わない | `firmware/src/runtime.c:101-121` |
| maintenance は BM scheduler、binding 後処理、最大4回の log、pool/stack/tick/queue 診断 | 同じ foreground 処理を再利用し、実行時間・再入・周期を検証する | `firmware/src/runtime.c:63-99` |
| idle も maintenance を呼ぶ | ready task がない場合の補助経路として維持 | `firmware/src/hal/hal.c:69-73` |
| tick は elapsed ms 分の `mrbc_tick()` を呼ぶ | 短い IRQ 処理と due/health 状態更新。foreground 全処理は呼ばない | `firmware/src/hal/hal.c:19-35` |
| 起動 LED・BLE 初期化は既に C | C owner に集約。WDT・release reboot は今後実装 | `firmware/src/main.c:18-25`、`firmware/src/ble.c:73-95`、`firmware/src/hal/hal.c:96-103` |

現在の system Ruby は WDT を feed していません。release fatal もまだ halt です。移行と同時に「実装済み」へ読み替えないでください。

## mrbc_run が戻らない問題

| 候補 | 固定版での判定 | 根拠・試作結果 |
|---|---|---|
| `mrbc_run()` の前後だけに C 処理を置く | 不十分。ready/wait/suspend task が続く限り外の main loop に戻らない | `vendor/mrubyc/src/rrt0.c:347-433` |
| HAL idle だけで管理処理を行う | 不十分。常時 ready の Ruby がいると実行されない | 同 `:353-362`、証拠 `c-system.log` の idle-only |
| timer preemption | Ruby が yield しない loop でも VM から rrt0 には戻せる。ただし outer main には戻らない | 同 `:145-180,368-385`、`vendor/mrubyc/src/vm.c:3307-3328`、spin 試作 |
| `mrbc_run_step()` を BM で使う | そのままは不可。`__EMSCRIPTEN__` 限定で header に汎用 step API なし | `vendor/mrubyc/src/rrt0.c:436-500`、`vendor/mrubyc/src/rrt0.h:114-134` |
| `MRBC_SCHEDULE_TIMER` 系 hook | 固定 vendor tree には該当名なし。存在する前提で設計しない | `rrt0.c:347-433`、`vendor/mrubyc/src/vm_config.h:120-151`、tree 全体の文字列検索0件 |
| BM scheduler に timer event を積むだけ | 不十分。`bm_scheduler_process()` を foreground から呼ぶ必要がある | `vendor/sdk-nrf-bm/lib/bm_scheduler/bm_scheduler.c:22-73` |
| link wrapper で VM quantum の復帰を受ける | **Wasm で成立**。`--wrap=mrbc_vm_run` で復帰後に native maintenance。idle も併用 | [試作 C](a2-p3-evidence/c_system_probe.c)、[runner](a2-p3-evidence/run-wasm.sh)、spin/idle-only の対照試験 |

### パッチなしの実装候補

main は一度 `mrbc_run()` に入り、`mrbc_vm_run` の link wrapper が quantum 復帰後に期限到来を確認して C の supervisor を回します。startup の mrblib 実行中には supervisor を動かさず、再入させず、Ruby/Proc を呼び返しません。main の外側で単純な `while` を回す案とは異なります。

試作では Wasm linker の wrap と compiler instrumentation を使いました。instrumentation は無変更の VM に決定的な模擬 IRQ を挿入する試験専用で、製品案の一部ではありません。常時 ready の無限 loop から30回の native service に到達し、idle-only 条件では service が0回のままでした。空・例外・sleep・通常入力も実行しました。

BM の linker wrap、LTO による迂回の有無、最終 ELF の call site は未検証です。実装時には build artifact と回帰試験で wrapper が実際に呼ばれることを確認します。upstream 専用 hook ではないため、この結合条件を保守する必要があります。

### 遅延上限と WDT

**この方式だけで厳密な遅延上限を保証したとはいえません。** VM は opcode の後で preemption flag を確認するので、長い native callback や処理の重い一 opcode を途中で止められません（`vendor/mrubyc/src/vm.c:3173-3308`）。BM scheduler の drain も queue が空になるまで回り、callback の最悪時間と流入率を含む上限は未証明です（`bm_scheduler.c:53-73`）。

tick IRQ は `bm_timer` → `k_timer` の expiry 経路です（`vendor/sdk-nrf-bm/lib/bm_timer/bm_timer.c:30-50`）。固定 Zephyr の [timer expiry 契約](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/include/zephyr/kernel.h#L1853-L1861)も system clock interrupt context を指定します。IRQ 内で Ruby、VM 再入、BLE foreground drain、任意 log/allocator 処理は行いません。

WDT は IRQ が来たという理由だけでは feed せず、foreground の完了 heartbeat と期限を確認する案です。試作では native callback 内で模擬 tick を80回進め、VM が戻らず、foreground heartbeat が古くなると feed を55回見送ることを確認しました。試作の25 tick 閾値と10 tick quantum は試験条件であり、製品値や実時間ではありません。初回は閾値を5 tick にして通常 quantum より短くしてしまい assertion が失敗したため、条件を修正しました。

全 user task が進んでいることと、C supervisor が進むことも別です。必要なら製品で重要な user 処理の heartbeat を追加します。全 user task の終了・空入力時にも、C を継続するか fail/reboot にするかを決めます。現 main は scheduler return を fatal にしています。試作は return の検出だけで、継続運転の実装ではありません。

## C policy に残すもの

| 対象 | Ver 1 で守る範囲 |
|---|---|
| shared Ruby の再定義 | user 間の不具合は残るが、C supervisor は Ruby method を lookup しない。user の `RBOSSystem.service` 再定義を実行しても C 管理処理の権限にはならないことを fake pin policy で再現 |
| GPIO | DT allowlist、console/SD 予約、system LED の予約、mode/range/busy 検査。system pin は class method の直接 pin 指定からも拒否 |
| ADC/Button | request/subscription identity、token/generation、busy、timeout、解放と DMA 寿命。TCB ごとの完全 sandbox を新設する前提にはしない |
| BLE/boot/storage/WDT | raw 操作を Ruby 非公開にする。将来 Ruby から要求を受けるなら native の限定要求として定義し、user callback に管理権限を与えない |
| Task API | system TCB はなくなるので、他 task 変更は user 間の干渉になる。Ver 1 で全 mutation を自己限定にする必然性は下がる。pool/VM ID 枯渇、mutex owner 終了、priority 飢餓、stale/native handle の型・寿命は残る |

現在の pin と lease 検査の根拠は [GPIO/Button](gpio-button-api.md)、[ADC](adc-api.md)、[資源予約](resource-reservations.md)。C policy も native memory の完全な隔離ではなく、不具合の被害範囲を狭めるためのものです。

## 以前の未承認 A2 案への影響

元の番号は [以前の未承認案](a2-p3-evidence/a2-initial-proposal.md)です。旧案を実装済みの契約とは扱いません。

| 旧番号 | 新方針での扱い |
|---|---|
| 1 system の信頼元 | image 内の C と policy が管理主体。system Ruby role は不要 |
| 2 registry | role/capability registry は Ver 1 では不要。lease・handle の lifetime 管理は別に残る |
| 3 子 task | 全て user。権限継承の仕組みを作らない |
| 4 DORMANT/run/rewind | system 権限の失効は不要。要求の取消し・解放・再利用検査は残す |
| 5 system の監督範囲 | native supervisor が必要な故障検出・回復を担当 |
| 6 user の Task API | user 同士の干渉として再評価。全制限の実装を前提にしない |
| 7 Task method の上書き | role 認可用の一括 wrapper は不要。型・寿命の不具合修正とは分ける |
| 8 peripheral allowlist | 維持。system 用 pin を C で予約する |
| 9 WDT backend | 維持。nrfx backend/fake を評価。実機は未確認 |
| 10 kick 条件 | Ruby system 進行ではなく native foreground の完了・期限 |
| 11 timeout | 維持。実測後に決め、debug halt/sleep の条件も確認 |
| 12 release fatal | bounded flush → reboot 方針を維持。未実装 |
| 13 reset reason | native 起動 log の案を維持。実機未確認 |
| 14 debug API | release 非登録の範囲を再評価。厳格な runtime 認可とは分ける |
| 15 拒否契約 | C policy が拒否したら backend を動かさず、既存例外契約に合わせる |
| 16 PR 分割 | role registry → native supervisor・C policy・WDT/回復と試験へ組み替える候補 |

## Ruby API・版管理・試験への影響

`RBOSSystem.service` を無条件に呼べる native service に変更するのは避けます。native 管理を Ruby の定義に依存させないためです。未登録にするか、移行用に管理処理を起こさない互換入口を残すかは、公開済み契約と移行手順を確認して決めます。根拠は `firmware/README.md:29` と `runtime.c:101-121` です。

実装 PR では `system.rb` と task manifest の先頭規約、selftest の期待件数、四 profile の manifest/配置 gate、Wasm fixture、BM log checker の service/idle 統計を揃えます（`firmware/cmake/mrubyc.cmake:29-44`、`tools/mrubyc-wasm/check.sh:64-105`、`tests/check-changes/test_bytecode_manifest.py`）。counter の名称だけを引き継いで同じ意味と扱わないでください。

削除は [semver skill](../../.agents/skills/semver/SKILL.md)の「少なくとも1回の MINOR 猶予」に従います。0.x の非互換変更は次の MINOR、1.0 以降なら MAJOR です。互換の内部変更だけならそれを理由に増分しません。現在は `firmware/VERSION` が0.1.4であり、利用者の「Ver 1」と SemVer 1.0.0 は同義ではありません。将来の実装 PR で CHANGELOG の Changed/Deprecated/Removed と移行方法を記録します。今回は調査文書のみなので VERSION/CHANGELOG は変更しません。

受け入れには Wasm の正常・空・例外・常時 ready・native 停滞・user 間干渉、BM 四 profile build と wrap call site、実機の tick/foreground 遅延、BLE 接続中負荷、WDT の期限超過回復、LED 予約、log flush/reboot/reset reason が必要です。**今回の BM build・実機・WDT・BLE の追加検証は未実施です。**
