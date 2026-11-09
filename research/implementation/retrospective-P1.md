# P1 の振り返り

[段階計画](porting-plan.md)の P1「mruby/c を OS の中核として動かす」の実装を振り返ります。基準 commit は `bb6e99b`、初期実装は `92341ee2f340afcb8c630d845367b3b3592d1c9d` です。対象は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` だけです。

P1 の build・Wasm 検査は `bb6e99b` の変更を commit 前の作業木で実行しました。生成 banner の commit は親の `92341ee2f340` です。P0 比較の基準は `da063c210a4a37469093098e14e4fb78cd068c05`。[build 再現手順](bm-build.md)に入力、容量、map の帰属方法を記録しました。今回の文書作業では保存済み app map/ELF/log を再解析し、firmware build と Wasm 検査を再実行していません。

## 達成と未達

mrbc を vendor のコピーから作り、mruby/c、共有 binding、BM HAL、system task と三つの selftest task を結合しました。const bytecode は RRAM に置き、build 時に header/size を検査します。保守処理は system task と HAL idle の共通経路です。BLE は接続可能な名前 `RBOS` の広告だけで、独自 GATT service はありません。

| P1 の受け入れ項目 | build / Wasm の証拠 | DK の実機結果 |
|---|---|---|
| 二つ以上の task の同時実行 | coordinator と二 worker、`PASS: concurrent workers` | 未確認 |
| 同 priority の巡回 | 同 priority の両 counter が進み `PASS: same-priority round robin` | 未確認 |
| priority 変更 | getter と counter の進行差、`PASS: priority change` | 未確認 |
| sleep | coordinator/worker の sleep と再開を上記 selftest で確認 | BM の時間精度・応答は未確認 |
| mutex | sleep を含む lock 内の共有 counter、`PASS: mutex with sleeping owner` | 未確認 |
| suspend/resume | 停止中の counter 不変と再開、`PASS: suspend` / `PASS: resume` | 未確認 |
| idle wakeup | worker join 後の sleep、`PASS: idle wakeup` | 未確認。firmware は常設 system task も動く |
| BLE 接続中の tick jitter | min/max、catchups、tick count の区間計装を実装 | 未計測 |
| stack/pool 最大使用量 | main/ISR の paint scan、pool の観測最大値を実装 | 未計測、厳密な pool peak ではない |

**P1 は未完了です。** Wasm は firmware-only class、BM timer/IRQ、SoftDevice を動かしません。system.rb は Wasm では compile だけです。DK で全項目を検証したという意味にはなりません。

実行した検査は次のとおりです。コマンド中の `<...>` は再実行時の置換値です。

```sh
# BM workspace、NCS v3.3.0 toolchain 環境で実行
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-debug> -p always
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-release> -p always -- \
  -DFILE_SUFFIX=release \
  '-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE="<key-dir>/rbos-release.pem"'
# RBOS checkout、emsdk 環境で実行
source <emsdk>/emsdk_env.sh
tools/mrubyc-wasm/check.sh
python3 -m unittest discover -s tests/check-changes
python3 .github/scripts/check-skills.py
python3 .github/scripts/check-research.py
git diff --check
```

両 pristine build と Wasm checker は exit 0、compiler warning/error は0、unittest は12件 OK、skill/research inventory は0 error、diff の空白検査は出力なしでした。Wasm は既存検査に加えて最後に `PASS: P1 selftest` を出力しました。P1 app は debug FLASH 114,204 B / RAM 83,600 B、release FLASH 98,468 B / RAM 83,360 B です。VM 数8、register 110、symbol 255、Float double、String 有効を両 rrt0 compile command の前処理でも確認しました。debug は MRBC_DEBUG、release は VM source のみ NDEBUG=1 です。

actionlint 1.7.12 は既存の `ubuntu-26.04` を未知の runner label として拒否しました。その診断だけを `-ignore 'label "ubuntu-26\.04" is unknown'` で除外すると両 workflow の検査は成功しました。未修正の診断として残し、無条件に actionlint が通ったとは扱いません。P1 の GitHub Actions 実行結果はこの記録に含めていません。`.github/workflows/firmware.yml` と `mruby-wasm.yml` は main push / PR が対象で、当該 branch push 時には PR がありませんでした。

IRQ 予約は静的に確認しました。両 app の `.config` は ZERO_LATENCY_IRQS=y / ZERO_LATENCY_LEVELS=1、生成 devicetree の priority bits は3です。[Zephyr の irq_lock](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/include/zephyr/arch/arm/asm_inline_gcc.h#L44-L58) と [priority 定義](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/include/zephyr/arch/arm/cortex_m/exception.h#L20-L53)から、BASEPRI は `(1 + 1) << (8 - 3) = 0x40` で NVIC 2以上を mask、SoftDevice の0/1を残します。SDK SHA は `tools/bm-build/modules.txt` と同じです。実機 register を読んだ確認ではありません。

`firmware/src/hal/hal.c:46-66` は irq_lock と bm_timer を使い、app に直接 GRTC 操作はありません。bm_timer は `k_timer_init/start` を使います（`vendor/sdk-nrf-bm/lib/bm_timer/bm_timer.c:40-68`）。SDK 側で timer IRQ の priority を設定しますが、app が channel を再割当てする構成ではありません。GRTC channel0 の system timer 予約と SoftDevice の0/1予約は `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:8-39` が根拠です。

**DK で利用者が行う試験（未実施）**

1. P1 source を含む SHA の firmware CI を成功させ、`firmware-evidence-debug-<sha>` の `production.hex`、SHA256SUMS、app `.config` と map を保存します。artifact の SHA を記録し、旧 P0 artifact と取り違えないようにします。CI の保存物は `tools/bm-build/collect-evidence.sh` 参照。
2. SDK debug 公開鍵で準備済みの DK を使います。初回準備や release 用 DK との鍵交換は[別手順](dk-provisioning.md)です。この P1 試験に全体 erase や再 provision を混ぜません。通常の書き込み例は次のとおりです。`<SN>` は手元の DK の値で、共有ログには残しません。

   ```sh
   nrfutil device program --serial-number "<SN>" --firmware "<artifact>/production.hex" \
     --options chip_erase_mode=ERASE_NONE
   nrfutil device reset --serial-number "<SN>"
   ```

   ERASE_NONE での更新成功はまだ確認していません。書換え制約で失敗したら erase 付きで自動再試行せず、エラーを保存して利用者が判断してください。既存の[通常更新の実機報告](dk-provisioning.md#通常の書き込み)は範囲 erase を許した方法で、ERASE_NONE の成功例ではありません。
3. VCOM を115200 baudで開き、LED0、`RBOS 0.1.0+0`（VERSION を変えた場合はその版）、自己検査の次の行を保存します。ここで示すのは期待値で、DK で得た log ではありません。

   ```text
   PASS: concurrent workers
   PASS: same-priority round robin
   PASS: priority change
   PASS: suspend
   PASS: resume
   PASS: mutex with sleeping owner
   PASS: workers joined
   PASS: idle wakeup
   PASS: P1 selftest
   ```

4. 接続前の stats を数区間採取し、nRF Connect で `RBOS` に接続します。`BLE connected` を確認して数区間維持し、切断後は `BLE disconnected` と再広告を確かめます。広告終了後なら reset して採取し直します。接続直後・切断直後の境界をまたぐ区間は比較から分けます。接続中と未接続で同じ長さの複数区間を保存し、次の形式の tick_us の幅、catchups、ticks を比べてください。

   ```text
   stats tick_us=<min>..<max> catchups=<count> ticks=<count> pool=<used_max>/<total> main=<bytes> isr=<bytes> idle=<count> service=<count>
   ```

   統計周期の既定は10秒です。tick_us/catchups/ticks は irq_lock 下で読取り・reset する区間値、pool/main/isr は起動後の観測最大値、idle/service は累積回数です。tick_us は callback 間隔で、mrbc_tick 一回ごとの間隔ではありません。catchups は1 callbackで複数 msを処理した回数、ticks は mrbc_tick 呼出数です。tick の全分布や厳密な ISR 遅延はこの一行では得られません。pool/stack も起動直後と接続中・切断後で記録し、異常・FAIL・停止を含めて結果を残します。

## 判明したリスクと blocker

実機の不在が P1 受け入れの blocker です。以下は source と設定から分かる制約であり、DK で障害の発生を観測した記録ではありません。

| リスク・境界 | 現在の事実と根拠 |
|---|---|
| timer 周期と ms の差 | SYS_CLOCK_TICKS_PER_SEC=31250、BM_TIMER_MS_TO_TICKS(1)=31、名目992 µs。HAL は絶対 uptime の whole ms に追従して mrbc_tick を0回以上呼ぶ。遅れを切り捨てる上限はなく、catch-up が長くなる可能性は未計測（`firmware/src/hal/hal.c:19-53`） |
| 保守の drain は無制限 | log_process は最大4回だが、bm_scheduler_process は queue が空になるまで callback を実行。新規 event や長い callback を含む実行時間に上限なし（`firmware/src/runtime.c:35-43`、`vendor/sdk-nrf-bm/lib/bm_scheduler/bm_scheduler.c:53-72`）。SCHED と512 Bの queue は両 `.config` で確認、drain 時間は未測定 |
| service の認可は VM pointer のみ | `firmware/src/runtime.c:63-74` は保存した system task の VM pointer と比較。生成・破棄の lifecycle に結び付いた権限管理ではなく、拒否例も実機未試験。P3 で扱う |
| system task の優先度・停止を制限しない | priority 0 で生成するが、一般 Ruby task が Task.get で参照して priority= / suspend 等を呼ぶ API に caller 制限なし。自己検査では system task を変更していない。P3 の課題（`vendor/mrubyc/src/rrt0.c:914-943,1044-1069,1120-1135`） |
| pool の観測漏れ | pool_max は保守時の alloc_statistics の標本最大値。保守間に確保・解放した peak は拾わない（`firmware/src/runtime.c:44-46`） |
| stack scan の余裕 | main stack は現在 SP より256 B下まで paint。未塗布領域を使用済みとして数える保守的な値で、厳密な最大深さではない。ISR は INIT_STACKS を使用（`firmware/src/runtime.c:18-33`、`firmware/common.conf`） |
| abort 後の復旧 | LOG_PANIC 後に k_fatal_halt。app の自動 reboot / watchdog 復旧は未実装。OOM/fatal 経路は実機未試験（`firmware/src/hal/hal.c:96-103`） |
| RAM 予算 | debug 約83 KB（83,600 B、81.6 KiB）/ 237 KiB、34.45%。pool 64 KiB と main stack 8 KiB を静的予約済みだが、残量を将来 I/O/queue に無条件に使える保証ではない |
| 広告を必ず開始する | 起動時に利用者の選択なしで広告し、切断後も再開する。電力・公開範囲の制御は未設計。ただし無期限の「常時広告」ではない。両 `.config` の timeout は fast 1000、slow 18000（10 ms単位、10秒→180秒→idle）。`firmware/src/ble.c`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/ble_adv.c:108-118,181-232,393-428` が根拠 |
| release 鍵 | `firmware/sysbuild.cmake` の検査は変更なし。build に外部試験鍵を使用しただけで、量産鍵の管理・DK への移行・DFU を検証したものではない |

**mutex owner 終了と priority inversion（固定版の事実、方針は未決）**

Ruby の Task#terminate は `mrbc_terminate_task()` を呼びます（`vendor/mrubyc/src/rrt0.c:1155-1169`）。同関数は task を DORMANT queue に移し preemption flag を立てるだけで、mutex の lock 状態を変えないと明記されています（同 `:645-664`）。通常終了でも scheduler の終了分岐は DORMANT 化と VM 終了・join 待ちの通知で、mutex 解放はありません（同 `:387-419`）。VM finalizer にも mutex の走査・unlock はありません（`vendor/mrubyc/src/vm.c:357-390`）。

共有 Mutex object が残る場合、owner が保持したまま終了しても lock と owner TCB の参照は自動解除されません。後続 task は lock 取得で MUTEX 待ちに入り、終了した owner の代わりに非 owner が正常な unlock をすることもできません。`mrbc_mutex_lock` の待機処理は同 `rrt0.c:717-751`、unlock の owner 検査と待機者への所有移譲は同 `:761-803` です。これは静的確認であり、owner 終了の fault test はまだ実行していません。

priority inheritance もありません。lock 待ちで変更するのは待機 task の state/reason/mutex と preemption flag だけで、owner の priority を引き上げません。unlock も所有移譲と起床だけです（同 `:717-803`）。`priority_preemption` への代入は初期化、再開、明示的な priority 変更の三箇所だけ（同 `:232,334,582-585`）でした。待機 queue を priority 順に選ぶ処理（同 `:55-90`）は、owner を昇格させる inheritance とは異なります。低優先 owner が中優先 ready task に妨げられる inversion の時間は未測定です。

## P2 への改善提案

以下は利用者の承認後に採用する提案で、今回の実装・方針変更ではありません。P1 の実機受け入れを済ませずに P2 完了とはしません。

1. 上の DK 手順で P1 の未確認項目を埋め、接続状態・採取時間・image SHA ごとの結果を保存する。queue drain の最大時間も計測する案を比較する。
2. LED/Button/GPIO binding を加える前に、共有 C API の正常・空・誤型・境界・driver failure の試験と、ISR event queue の容量・overflow 方針を決める。
3. pool の瞬間 peak を捕捉する計装と stack margin の校正を検討する。P2 の native 呼出しで現在の83 KBから何が増えるかを同じ map 分類で比較する。
4. mutex owner 終了・例外・優先度差の fault test を host に追加し、終了禁止、自動回復、利用規約などの方針を比較する。上流仕様を今回勝手に変更しない。
5. P3 で Task 操作の認可と service の lifecycle を扱う。広告の開始条件・時間、abort 後の復旧と watchdog は、必要な要件と段階を利用者に確認してから設計する。

## checklist と porting-plan への追記候補

次の候補も未採用です。既存 checklist の完了印は今回得た証拠の範囲に限り、受け入れ条件は変更していません。

- checklist P1: 「mutex owner の終了・例外と、priority inversion の fault test を行う」を追加する。
- checklist P1: 「接続状態の境界を除いた区間 jitter と queue drain の実測結果を保存する」を具体化する。
- checklist P2: 「native API を追加するたびに、同じ方法で map と stack/pool の差を記録する」を追加する。
- checklist P3: 「system task への Task#priority= / suspend / terminate / raise を含む認可試験」を明示する。
- porting-plan: 広告の停止・再開条件、watchdog と fatal 復旧の担当段階を決める。P1 の受け入れを緩める候補ではない。

[調査索引へ戻る](../README.md)
