# P1 の振り返り

[段階計画](porting-plan.md)の P1「mruby/c を OS の中核として動かす」の実装を振り返ります。基準 commit は `bb6e99b`、初期実装は `92341ee2f340afcb8c630d845367b3b3592d1c9d` です。対象は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` だけです。

P1 の build・Wasm 検査は `bb6e99b` の変更を commit 前の作業木で実行しました。生成 banner の commit は親の `92341ee2f340` です。P0 比較の基準は `da063c210a4a37469093098e14e4fb78cd068c05`。[build 再現手順](bm-build.md)に入力、容量、map の帰属方法を記録しました。当初の文書化では保存済み app map/ELF/log を再解析しました。今回の実機証拠の追記では build・Wasm 検査を再実行していません。

## 達成と未達

追記: 利用者が main `ff4c23ef63a2f5a38bb9361e6c569ce88e954e3f` の CI debug image を DK で実行しました。エージェントは flash/reset を行っていません。以下の build・Wasm 記録は履歴として残し、実機結果を後段に分けます。

mrbc を vendor のコピーから作り、mruby/c、共有 binding、BM HAL、system task と三つの selftest task を結合しました。const bytecode は RRAM に置き、build 時に header/size を検査します。保守処理は system task と HAL idle の共通経路です。BLE は接続可能な名前 `RBOS` の広告だけで、独自 GATT service はありません。

| P1 の受け入れ項目 | build / Wasm の証拠 | DK の実機結果 |
|---|---|---|
| 二つ以上の task の同時実行 | coordinator と二 worker、`PASS: concurrent workers` | 同じ PASS を確認 |
| 同 priority の巡回 | 同 priority の両 counter が進み `PASS: same-priority round robin` | 同じ PASS を確認 |
| priority 変更 | getter と counter の進行差、`PASS: priority change` | 同じ PASS を確認 |
| sleep | coordinator/worker の sleep と再開を上記 selftest で確認 | selftest 成功。厳密な sleep 応答時間は未測定 |
| mutex | sleep を含む lock 内の共有 counter、`PASS: mutex with sleeping owner` | 同じ PASS を確認 |
| suspend/resume | 停止中の counter 不変と再開、`PASS: suspend` / `PASS: resume` | 両 PASS を確認 |
| idle wakeup | worker join 後の sleep、`PASS: idle wakeup` | PASS。常設 system task も動くので全 VM が停止した試験とは異なる |
| BLE 接続中の tick jitter | min/max、catchups、tick count の区間計装を実装 | 完全接続区間936..1049 µs、catchups=0 |
| stack/pool 最大使用量 | main/ISR の paint scan、pool の観測最大値を実装 | main 688 B、ISR 560 B、pool 11560/65536 B。標本・paint の限界あり |

P1 の受け入れ項目に対する自己検査・BLE 接続中の区間統計・stack/pool の観測値が実機でもそろいました。ただし、資源使用量の厳密な上限、常時 ready task と BLE の負荷試験、長時間安定性まで検証したものではありません。Wasm は firmware-only class、BM timer/IRQ、SoftDevice を動かさず、system.rb は compile だけです。

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

**DK の追試手順（下記の利用者報告で一回実施）**

1. P1 source を含む SHA の firmware CI を成功させ、`firmware-evidence-debug-<sha>` の `production.hex`、SHA256SUMS、app `.config` と map を保存します。artifact の SHA を記録し、旧 P0 artifact と取り違えないようにします。CI の保存物は `tools/bm-build/collect-evidence.sh` 参照。
2. SDK debug 公開鍵で準備済みの DK を使います。初回準備や release 用 DK との鍵交換は[別手順](dk-provisioning.md)です。この P1 試験に全体 erase や再 provision を混ぜません。通常の書き込み例は次のとおりです。`<SN>` は手元の DK の値で、共有ログには残しません。

   ```sh
   nrfutil device program --serial-number "<SN>" --firmware "<artifact>/production.hex" \
     --options chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE
   nrfutil device reset --serial-number "<SN>"
   ```

   P0 と今回の成功例は範囲 erase を許した更新です。全体 erase と鍵の再 provision は行っていません。ERASE_NONE の更新成功や保存データの維持は未確認です。
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

   統計周期の既定は10秒です。tick_us/catchups/ticks は irq_lock 下で読取り・reset する区間値、pool は起動後の最大標本、main/isr はその時点の paint scan 値、idle/service は累積回数です。tick_us は callback 間隔で、mrbc_tick 一回ごとの間隔ではありません。catchups は1 callbackで複数 msを処理した回数、ticks は mrbc_tick 呼出数です。tick の全分布や厳密な ISR 遅延はこの一行では得られません。pool/stack も起動直後と接続中・切断後で記録し、異常・FAIL・停止を含めて結果を残します。

**利用者による DK の実機結果**

出所は [firmware CI run 42714459863](https://github.com/uist1idrju3i/RBOS/actions/runs/42714459863)（main push、`ff4c23ef63a2f5a38bb9361e6c569ce88e954e3f`）の artifact `firmware-evidence-debug-ff4c23ef63a2f5a38bb9361e6c569ce88e954e3f` です。利用者は SHA256SUMS を全件検証しました。`production.hex` の SHA-256 は `c3f12d0296e3022d3d164014b119a4c51f21a9e2c90400ee033df77277c086f6`。上の範囲 erase の program と reset が成功し、鍵の再 provision・全体 erase はありません。

実際に利用者が成功を報告したコマンドは次のとおりです。識別番号は `<SN>` に置き換えています。

```sh
nrfutil device program --serial-number "<SN>" --firmware production.hex \
  --options chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE
nrfutil device reset
```

| 項目 | 証拠 | 結果 |
|---|---|---|
| 起動・自己検査 | 下記の banner と全 PASS 行 | debug image で成功 |
| 接続前の callback 間隔 | 20〜70秒の完全未接続区間 | 合わせて930..1040 µs |
| 完全接続区間 | 接続77.275秒、切断112.662秒。90/100/110秒の stats | 合わせて936..1049 µs。80/120秒は境界混在で除外 |
| tick accounting | 全行 catchups=0、初回9965、以後9999〜10001 ticks | 約10000回/10秒。初回は timer 初期化からの短い区間 |
| pool / stack | 全行 pool=11560/65536、main=688、isr=560 | 観測最大値。pool 約17.6%、stack は688/8192 B と560/2048 B |
| idle / service | 累積 counter の差分 | 完全接続区間 idle 約1124回/秒、接続前は約1180回/秒。service は908回/約10秒（初回905） |
| SCHED との共存 | artifact の SCHED 設定と接続・切断処理、service の継続 | この短時間試験で進行。queue drain 上限・常時 ready worker と BLE 同時負荷は未測定 |
| 切断後の広告 | 112.662秒 fast、122.656秒 slow | 再広告成功。二度目の接続は記録なし |

統計の意味は `firmware/src/hal/hal.c:19-43` と `firmware/src/runtime.c:18-60` で照合しました。tick_us は 1 MHz cycle counter で測った bm_timer callback 入口間隔で、mrbc_tick 自体の間隔ではありません。min/max/catchups/ticks は irq_lock 下で snapshot/reset する区間値です。表示は約10秒ごとですが境界は snapshot の時点で、初回は起動直後からの完全な10秒ではありません。名目周期は `floor(31250/1000)=31 ticks=992 µs`（`vendor/sdk-nrf-bm/include/bm/bm_timer.h:35-40`）。絶対 uptime の whole ms を追うため、callback 回数と ticks は異なります。

pool の分子は保守時に標本化した起動後の used 最大値、分母は pool total です。main/isr は毎回 paint を scan して得る使用 byte 数で、paint が残す過去の使用痕跡を含む high-water の推定値です。別の max 変数で累積する値ではなく、0xaa と同じ値の書込みなどを識別できません。main は現在 SP 下の256 B余裕を塗らず使用済みとして数え、ISR は INIT_STACKS の paint を使います。artifact の app `.config:46,62` は main 8192 B / ISR 2048 B、`firmware/common.conf:5-6` も main サイズと INIT_STACKS を指定します。IREP の個別量や瞬間 pool peak、資源使用の厳密な上限はこの値から分かりません。

idle/service は reset しない起動後の保守呼出し回数です。idle は `mrbc_hal_idle_cpu` が保守を呼び、その後 k_cpu_idle に入る回数（`firmware/src/hal/hal.c:69-73`）で、hardware IRQ 数やCPU使用率ではありません。切断をまたぐ区間では約1271回/秒、最後の未接続区間は約1220回/秒であり、「常に1.1〜1.2k回/秒」とは限りません。

以下は利用者が採取した log の原文です。

```text
*** Booting MCUboot v2.3.0-dev-fce4dac2e629 ***
*** Using nRF Connect SDK Bare Metal v2.0.1-51484143c091 ***
I: Starting bootloader
I: Booting main application
I: Bootloader chainload address offset: 0xa000
I: Image version: v0.1.0
I: Jumping to the first image slot
*** Booting My Application v0.1.0-ff4c23ef63a2 ***
*** Using nRF Connect SDK Bare Metal v2.0.1-51484143c091 ***
[00:00:00.008,947] <inf> nrf_sdh: SoftDevice forward address: 0x163800
[00:00:00.025,739] <inf> rbos: RBOS 0.1.0+0
[00:00:00.035,381] <inf> ble_adv: Fast advertising
PASS: concurrent workers
PASS: same-priority round robin
PASS: priority change
PASS: suspend
PASS: resume
PASS: mutex with sleeping owner
PASS: workers joined
PASS: idle wakeup
PASS: P1 selftest
[00:00:10.000,691] <inf> rbos_runtime: stats tick_us=932..1038 catchups=0 ticks=9965 pool=11560/65536 main=688 isr=560 idle=12510 service=905
[00:00:10.032,636] <inf> ble_adv: Slow advertising
[00:00:20.001,016] <inf> rbos_runtime: stats tick_us=931..1039 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=24329 service=1813
[00:00:30.000,794] <inf> rbos_runtime: stats tick_us=932..1038 catchups=0 ticks=9999 pool=11560/65536 main=688 isr=560 idle=36166 service=2721
[00:00:40.000,729] <inf> rbos_runtime: stats tick_us=932..1038 catchups=0 ticks=10001 pool=11560/65536 main=688 isr=560 idle=47956 service=3629
[00:00:50.001,080] <inf> rbos_runtime: stats tick_us=933..1038 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=59782 service=4537
[00:01:00.001,432] <inf> rbos_runtime: stats tick_us=931..1039 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=71595 service=5445
[00:01:10.000,792] <inf> rbos_runtime: stats tick_us=930..1040 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=83382 service=6353
[00:01:17.275,544] <inf> rbos_ble: BLE connected
[00:01:20.001,144] <inf> rbos_runtime: stats tick_us=930..1048 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=95065 service=7261
[00:01:30.001,496] <inf> rbos_runtime: stats tick_us=936..1049 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=106308 service=8169
[00:01:40.000,859] <inf> rbos_runtime: stats tick_us=937..1048 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=117555 service=9077
[00:01:50.001,208] <inf> rbos_runtime: stats tick_us=937..1048 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=128792 service=9985
[00:01:52.662,024] <inf> ble_adv: Fast advertising
[00:01:52.662,123] <inf> rbos_ble: BLE disconnected
[00:02:00.001,560] <inf> rbos_runtime: stats tick_us=932..1048 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=141499 service=10893
[00:02:02.656,241] <inf> ble_adv: Slow advertising
[00:02:10.000,920] <inf> rbos_runtime: stats tick_us=931..1040 catchups=0 ticks=10000 pool=11560/65536 main=688 isr=560 idle=153700 service=11801
```

未確認なのは abort/OOM と認可拒否、release image の実機起動、二度目の BLE 接続、slow 広告180秒後の停止、保存データの前後比較、ERASE_NONE 更新、mutex owner 終了と inversion、queue drain 時間と長時間・高負荷時の資源上限です。この debug の一回の記録だけで完了にはしません。

## 判明したリスクと blocker

実機の基本自己検査と短時間の接続試験は利用者報告で確認しました。残る制約は以下のとおりです。全項目が DK で障害として発生したという意味ではありません。

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

1. 今回の短時間試験に続き、常時 ready の worker と BLE の同時負荷・長時間接続を試す。queue drain の最大時間も計測する案を比較する。
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
