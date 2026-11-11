# P1 の振り返り

[段階計画](porting-plan.md)の P1「mruby/c を OS の中核として動かす」の実装を振り返ります。基準 commit は `bb6e99b`、初期実装は `92341ee2f340afcb8c630d845367b3b3592d1c9d` です。対象は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` だけです。

初期 P1 の build・Wasm 検査は `bb6e99b` の変更を commit 前の作業木で実行しました。生成 banner の commit は親の `92341ee2f340` です。P0 比較の基準は `da063c210a4a37469093098e14e4fb78cd068c05`。[build 再現手順](bm-build.md)に入力、容量、map の帰属方法を記録しました。当初の文書化では保存済み app map/ELF/log を再解析し、DK 証拠だけを追記した PR #27 では build・Wasm 検査を再実行しませんでした。後の追加実装・再検証は closeout 節に分けます。

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

当初 actionlint 1.7.12 が報告した未知 runner 診断は、closeout で `.github/actionlint.yaml` の `self-hosted-runner.labels` に `ubuntu-26.04` を登録して解消しました。ignore は使いません。これは lint の既知 label 設定であり、workflow の実行先を self-hosted に変えるものではありません。

P1 の GitHub Actions も成功しています。PR #26 は firmware の [run 42651713702](https://github.com/uist1idrju3i/RBOS/actions/runs/42651713702)、mruby-wasm の [run 42651713756](https://github.com/uist1idrju3i/RBOS/actions/runs/42651713756) を含む12 checks 成功。main push `ff4c23e` の [firmware run 42714459863](https://github.com/uist1idrju3i/RBOS/actions/runs/42714459863) が下記 DK image の出所です。実機証拠を記録した [PR #27](https://github.com/uist1idrju3i/RBOS/pull/27) の head `382bee6` は9 passed / 0 failed / 2 skipped（文書変更で build/test を省略）。[agent-docs run 42832468038](https://github.com/uist1idrju3i/RBOS/actions/runs/42832468038) も成功しました。この履歴は、closeout の新しい stress/oom variant の remote CI 成功を示すものではありません。

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
   stats tick_us=<min>..<max> catchups=<count> ticks=<count> pool=<used_max>/<total> main=<bytes> isr=<bytes> idle=<count> service=<count> drain_us=<max>
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

この旧 log 時点では DK の abort/OOM と Mutex fault、二度目の BLE 接続、slow 広告180秒後の停止、queue drain 時間と高負荷時の資源上限は未確認でした。後述の利用者 log で OOM、再接続、stress の drain 観測値を追加しました。認可拒否は P3、release 実機・ERASE_NONE 更新は P5、保存データの前後比較は P5/P6 が担当します。

### P1 closeout の追加実装と判定

この追記は `37c995e`（計装・profile）、`6819755`（Wasm fault・pool 探索）、`776f42a`（checker・capture）を対象とします。実機 log の追記時には再実行しなかった build/Wasm 検査を、その後の実装時に実行しました。今回の方針採用を、新たな DK 証拠とは扱いません。

| 項目 | 実装・検証 | 未確認の境界 |
|---|---|---|
| drain_us | `firmware/src/runtime.c:41-44,62-65` で各 bm_scheduler_process の経過 µs を測り、区間最大を出力後 reset。追加 DK stress log の最大は144 µs | IRQ の中断を含む。drain の上限を制限する機構ではない |
| stress/oom | Kconfig choice と `firmware/stress.conf` / `oom.conf`、CMake の task 選択。四 pristine build は warning/error 0。DK stress/OOM の利用者 log を追加 | 当初の230秒は未達。後述の BLE 修正後400秒は PASS、OOM の fatal も確認済み。fairness は未決 |
| CI artifacts | `.github/workflows/firmware.yml` の四 variant が `firmware-evidence-<variant>-<sha>` に production.hex・SHA256SUMS 等を保存。鍵は含めない | PR #29 の14 checks と firmware run `42851188661` は成功。release 鍵検査と debug 限定 workspace 保存は維持 |
| Mutex fault | Wasm で owner 終了後の locked/waiter 停止、Task#raise の ensure 解放、middle busy 中の inversion、非 owner unlock の assert exit 1 を確認 | BM debug/release の差は前処理・map 照合。DK の fault は未実施 |
| pool 最小値 | `tools/mrubyc-wasm/check.sh --pool-min` の1 KiB単位探索で10 KiB（10240 B）が自己検査 PASS、9 KiB は OOM。既存 toolchain/cache で31秒 | opt-in。system.rb は compile のみ。firmware の必要量ではない |
| log checker | `tools/bm-build/check-dk-log.py`、実 log と合成失敗例、CLI、capture PTY を含む unittest 全27件成功 | macOS の port/zsh は未確認。spinner は直前 timestamp による推定 |

Wasm32 と ARM の pointer はともに4 Bであり、ホスト Node の64 bit pointer との差ではありません。固定 VM の64 bit alignment 設定は共通でも ABI・配置が異なります。Wasm は MAX_VM_COUNT=32、firmware は8。Wasm の探索は coordinator と二 worker だけを実行し、BM system task、BLE/SoftDevice、BM timer/maintenance を含みません。10 KiB を DK の pool 予算へ転用しません。

旧 P1 log の checker は selftest PASS、stats 13行 / 120.000229秒、catchups 最大0、初回以降9999..10001 ticksでした。完全未接続窓は930..1040 µs、完全接続窓は936..1049 µs / 30.000064秒、BLE event 間は35.386579秒で、境界2窓を除外しました。pool は11560/65536 B、main/ISR は688/560 B。旧 log に drain_us はなく未計測です。[capture と判定手順](dk-provisioning.md#macos-で-p1-stress-log-を採る)で、以下の追加結果も同じ定義で判定します。

### 利用者の stress/OOM 証拠と5分条件

利用者の決定で、P1 stress の条件を30分から5分へ変更しました。条件は両 spinner の開始後、接続境界をまたがない stats 窓の合計300秒です。連続接続時間や capture 全体の長さとは区別します。当初の checker は速度差を WARN としていましたが、X 採用後は2倍超を FAIL にします。以下の旧 checker 出力は当時の判定を保存したもので、旧偏り log は現在の checker では FAIL です。

利用者が iPhone の nRF Connect を central として採取した `dk-stress-20261111-003711.log` を [stress fixture](../../tests/check-changes/stress-capture.txt)に保存しました。image は `3d1fd598c609`。旧 image の断片が boot marker と同じ行にありますが、checker は最後の boot だけを判定します。

| 観測 | 結果と限界 |
|---|---|
| stats | 32行、先頭から末尾まで310.100190秒。catchups=0、初回以降10001..10006 ticks |
| jitter | 完全接続窓922..1063 µs、23窓 / 230.067537秒。境界8窓を除外。先頭の875..1109 µsは開始不明の初回窓なので比較から除外 |
| drain / 資源 | drain 最大144 µs、pool 最大標本15436/65536 B、main 720 B、ISR 560 B。瞬間 peak や使用上限の証明ではない |
| 保守 | service 90.651828..90.778885回/秒。stats 差分の idle は0回/秒で、常時 ready 負荷中は idle 待ちを期待しない |
| BLE | event 間の接続合計309.571336秒。切断8回のうち最初の7回は接続から約40.1秒、約20 ms後に再接続。最後の切断は約28.7秒後で、その後の再接続は記録なし |
| spinner | a は約3.8万、b は約37.5万 iteration / 10秒。counter の modulo 差分でも約10倍の偏りが継続。a/b と速い側/遅い側を checker に追加 |
| 受け入れ | 完全接続かつ負荷中の窓は230.067537秒で、300秒未達の FAIL。総 log が5分を超えたことだけでは完了にしない |

DK OOM は利用者の [OOM fixture](../../tests/check-changes/oom-capture.txt)で、同じ image `3d1fd598c609` の `OOM: start` → `RBOS fatal: Ruby pool exhausted` を確認しました。OOM checker は PASS。旧 boot の先頭 stats 断片は除外し、新 boot の fatal 前には stats がないため pool は未計測です。この時点では [checklist](checklist.md#p1-vm-と時間)の OOM だけを完了にしました。stress 再試験と slow 広告停止の追加証拠は次節に記録します。DK Mutex fault は未実施です。

### BLE 応答修正後の DK 証拠

利用者は PR #29 の [firmware run 42851188661](https://github.com/uist1idrju3i/RBOS/actions/runs/42851188661) の `firmware-evidence-stress-f85c2fbe54567f9b6d05dfab5c83825488781c50` を DK に書き込み、二つの log を採取しました。banner は両方 `f85c2fbe5456` です。利用者報告の `production.hex` SHA-256 は `8c0e162ab28375cfb46c6487515c5c49a3253361f8049c71ca2eed66fbfb5867`、更新方式は ERASE_RANGES_TOUCHED_BY_FIRMWARE。今回は binary の再取得・hash 再計算や実機操作をせず、保存 log を checker で解析しました。識別番号がないことを検査し、改行を LF に統一した fixture を保存しました。

`dk-stress-20261111-022419.log` は [連続接続 fixture](../../tests/check-changes/stress-connected-capture.txt)です。PHY は2M要求（tx/rx=0x02）と完了 status=0x00、DLE は251要求→有効27、ATT MTU は rx=293要求を記録しました。有効 MTU の結果値はこの log にはありません。stress の既定条件で exit 0、切断なし。最初の stats を除いた40窓が全て完全接続かつ spinner 負荷中です。

```text
PASS: stress; app 0.1.0 / f85c2fbe5456; RBOS 0.1.0+0
| Item | Result |
|---|---|
| Stats | 41 lines; 400.122214 s (first to last) |
| Catchups max | 0 |
| Ticks after first | 10002..10004 |
| Fully disconnected tick_us | unmeasured (0 complete windows) |
| Fully connected tick_us | 920..1064; 40 windows / 400.122214 s |
| BLE connected | 407.480376 s event-to-event; 0 boundary windows excluded |
| Pool sampled peak (B) | 15428 / 65536 (23.54126%) |
| main max | 696 |
| isr max | 560 |
| drain_us max | 60 |
| idle / s | 0.0..0.0 |
| service / s | 90.760782..90.787789 |
| Spinner a | 41 progress lines; estimated max gap 10.004321 s; delta 37597.232325..37748.459962 / stats interval; mean 3767.416422 / s |
| Spinner b | 41 progress lines; estimated max gap 10.004321 s; delta 373596.853765..374110.496027 / stats interval; mean 37384.477734 / s |
| Fully connected under spinner load | 400.122214 / 300 s required |
| Spinner a/b; max/min | 0.100775; 9.923107 |

| BLE event | Uptime (s) | Line |
|---|---|---|
| fast_advertising | 0.035376 | 12 |
| connected | 2.646475 | 24 |
NOTE: Ignored 1 pre-boot line(s), counting any residue before the selected marker; original line numbers retained
NOTE: Spinner times use preceding timestamps (quantized); time after the final timestamp is unobservable
WARN: Spinner rate imbalance exceeds 2x (a/b=0.101; max/min=9.923)
NOTE: First stats excluded from jitter/rates; BLE boundary windows excluded from jitter.
```

`dk-stress-20261111-023156.log` は [再接続・広告停止 fixture](../../tests/check-changes/stress-reconnect-capture.txt)です。二度目の接続に成功し、両切断は reason=0x13でした。これは remote user terminated、ここでは iPhone 側による終了です（`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/ble_hci.h:74`）。最後の切断102.890137秒→fast→slow 112.880452秒→`ble_adv: Idle` 292.847109秒で、slow から179.966657秒、約180秒の停止を確認しました。checker は Idle を event 表に列挙しないため、fixture の129行目も照合しています。

この二本目は接続 stress の300秒条件を試す log ではなく、既定の stress checker は exit 1です。条件を下げた PASS で置き換えず、実際の出力を保存します。

```text
FAIL: stress; app 0.1.0 / f85c2fbe5456; RBOS 0.1.0+0
| Item | Result |
|---|---|
| Stats | 29 lines; 280.088142 s (first to last) |
| Catchups max | 0 |
| Ticks after first | 10002..10007 |
| Fully disconnected tick_us | 942..1040; 18 windows / 180.054945 s |
| Fully connected tick_us | 920..1064; 7 windows / 70.024438 s |
| BLE connected | 86.838918 s event-to-event; 3 boundary windows excluded |
| Pool sampled peak (B) | 15436 / 65536 (23.553467%) |
| main max | 688 |
| isr max | 560 |
| drain_us max | 148 |
| idle / s | 0.0..0.0 |
| service / s | 90.442994..90.778812 |
| Spinner a | 29 progress lines; estimated max gap 10.007292 s; delta 37408.421472..37786.176928 / stats interval; mean 3768.156668 / s |
| Spinner b | 29 progress lines; estimated max gap 10.007292 s; delta 372091.470746..374689.360159 / stats interval; mean 37410.487731 / s |
| Fully connected under spinner load | 70.024438 / 300 s required |
| Spinner a/b; max/min | 0.100725; 9.928061 |

| BLE event | Uptime (s) | Line |
|---|---|---|
| fast_advertising | 0.035345 | 12 |
| connected | 5.891271 | 24 |
| fast_advertising | 13.011859 | 33 |
| disconnected | 13.011963 | 34 |
| slow_advertising | 23.013189 | 38 |
| connected | 23.171911 | 39 |
| fast_advertising | 102.890033 | 69 |
| disconnected | 102.890137 | 70 |
| slow_advertising | 112.880452 | 74 |
ERROR: Fully-connected stats coverage too short under spinner load: 70.024 s < 300.000 s
NOTE: Ignored 1 pre-boot line(s), counting any residue before the selected marker; original line numbers retained
NOTE: Spinner times use preceding timestamps (quantized); time after the final timestamp is unobservable
WARN: Spinner rate imbalance exceeds 2x (a/b=0.101; max/min=9.928)
NOTE: First stats excluded from jitter/rates; BLE boundary windows excluded from jitter.
```

旧約40.1秒の切断周期は、S115 応答を追加した #29 の後には再観測されませんでした。前後比較から応答追加によって周期切断が止まったと推定します。ただし旧 log に reason がなく、どの未応答手順が原因だったかは確定できません。この時点では BLE が安定しても約1:9.9の偏りが残り、P1 の公平性判断は保留でした。後述の X/Y 比較でこの判断を終えました。

### BLE 手順応答の欠落と修正範囲

修正前の `firmware/common.conf` は BLE_ADV だけを有効にし、`ble.c` の observer は接続・切断だけを記録していました。SDH の `vendor/sdk-nrf-bm/subsys/softdevice_handler/nrf_sdh_ble.c:370-399` は event を取得して observer に配送するだけで、PHY・data length・MTU に自動応答しません。S115 API は明示的な reply を要求します（`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/ble_gap.h:122-125`、`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/ble_gatts.h:96-97`）。DLE の NULL が「自動」なのは API 呼出し時の値の選択であり、未呼出しの自動応答ではありません（同 `ble_gap.h:2044-2078`）。

SDK の peripheral sample と同じ `CONFIG_BLE_CONN_PARAMS=y` を採用しました（`vendor/sdk-nrf-bm/samples/bluetooth/ble_lbs/prj.conf:19-20`）。PHY は `vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/phy_mode.c:29-52,106-115,156-158`、data length は同 `data_length.c:32-56,92-107,180-183`、MTU は同 `att_mtu.c:54-88,158-160` が応答します。library の observer は HIGH で登録され、USER_LOW の RBOS observer より先に処理します。

S115 は peripheral と data length update を選択します（`vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:33-37`）。応答三機能は library の既定で有効です（`vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:76-99,130-159`）。今回は GAP 接続間隔の自発的な再交渉だけを無効にし、MTU=23、data length=27 の既定を維持します。能動的な PHY/DLE/MTU 開始も有効にせず、peer の要求に応答します。生成 `.config` で三機能を確認しました。

SYS_ATTR_MISSING は library が処理しないため、保存した bond がない現在の構成では `sd_ble_gatts_sys_attr_set(handle, NULL, 0, 0)` を呼びます。SDK sample の `vendor/sdk-nrf-bm/samples/bluetooth/ble_lbs/src/main.c:70-77` と S115 API の `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/ble_gatts.h:724-739` に従います。security parameters は sample 同様に pairing 非対応を返信し（同 sample `:58-68`）、security information は保存鍵なしを返信します（同 S115 `ble_gap.h:1950-1976`）。

`ble.c` は切断 reason を hex で出し、PHY/DLE/MTU 要求、PHY/DLE 完了、SYS_ATTR_MISSING、security 要求、GATTS timeout を INF で記録します。reply error は ERR、library は WARN 以上で、packet ごとの log は追加しません。要求が届いた場合の応答欠落は修正しましたが、旧 log に要求・reason がないため、どの手順が切断を起こしたかは未検証です。

[Bluetooth Core の LL response timeout](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/low-energy-controller/link-layer-specification.html)は40秒で接続喪失とします。S115 の reason 定義は `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/ble_hci.h:63,93` の connection timeout=0x08 / LMP response timeout=0x22です。ただし公開 SDK は S115 の binary 内部実装を含みません。未応答が実際にどの timeout を起こしたかは、修正後 DK の request・reply error・reason、必要なら無線 trace で識別します。MTU 応答 API も GATT timeout 後は再接続まで新しい GATT 手順を許さないと明記し、自動復旧を保証しません（同 S115 `ble_gatts.h:823-851`）。

### 同 priority spinner の偏りと Wasm 調査

BM の到達経路は `firmware/src/main.c:27-35` の system priority=0、`runtime.c:78-80` の service sleep、`hal/hal.c:19-34,46-54` の1 ms timer です。旧設定は1 ms tick / 10 tick timeslice、新既定は1 tickです。`MRBC_NO_TIMER` は BM では未定義です。

固定 `vendor/mrubyc/src/rrt0.c:61-90` は同 priority を末尾に挿入します。tick は実行中 task の残り timeslice を減らし、sleep の起床で preemption flag を立てます（同 `:145-185`）。起床条件は期限を超えた tick なので、`sleep_ms 10` は通常約11 ticks後の起床です（同 `:163-183,509-524`）。実行から戻った RUNNING task は同 priority の末尾へ移り（同 `:421-433`）、再 dispatch 時は残り時間を保存せず timeslice を設定値に戻します（同 `:352-374`）。system が sleep した後は ready queue 先頭の spinner が走ります。

したがって、system の約11 ms周期と旧10 ms quantum が同じ位相を保つと、一方が約10 ms、他方が約1 msで preempt される並びを繰り返せます。当時は service 約90.7回/秒と約10倍の差に整合する候補とし、後述の X/Y 比較で裏付けました。dispatch trace 自体は未採取です。旧 round robin 自己検査は両方の進行だけを確認していましたが、今回は進捗比の検査も追加しました。

実際の `firmware/ruby/stress/spinner_a.rb` / `spinner_b.rb` と、priority=0・`sleep_ms 10` の system 相当 task を Wasm runner で31000 ticks以上実行しました。標準の10 ms tick unit では各 spinner の10000 tickごとの count が1563 / 3125 / 4687、1 ms override でも2842 / 5683 / 8524と両者一致し、a/b=1.000でした。標準 runner の service は15500回、1 ms override は2819回です。偏りを再現しなかったので、依頼どおり Wasm repro test は追加しません。

Wasm HAL は `vendor/mrubyc/hal/emscripten/hal.h:28-30,49-54` で MRBC_NO_TIMER を有効にします。rrt0 の同 `:375-385` は命令単位の擬似 slice を終えてから一度だけ tick するため、BM の「10 ms slice の途中で timer が高優先 task を起こす」経路を通りません。1 ms tick unit に変えてもこの差は残り、Wasm の均等性は BM 仮説の反証にはなりません。

当初は1 tick quantum を DK で比較する方針としました。下記の実験を経て quantum だけを既定1へ変更し、service sleep 10 msと vendor 実装は維持します。上流への連絡は別途承認を得ます。

### X/Y 比較と1 tick の採用

利用者の DK log は image `7217cb685dd2`、firmware CI run `42869985805` の比較 artifact に対応します。X は quantum=1 / service sleep=10 ms、Y は10 / 9 msです。fixture は [X](../../tests/check-changes/stress-x-capture.txt) と [Y](../../tests/check-changes/stress-y-capture.txt) に保存しました。

| 項目 | X | Y |
|---|---|---|
| production.hex SHA-256 | `09ee14be587d6cd1f7ecd8189218b1d5b8925bf6373e9ed8317ff4ef45f114fc` | `7a10b9a4af9996a95ef90d96a9134c7e63275b1b8d3ee4e7f6f74190b8b13d02` |
| 現 checker `--profile stress` | PASS | PASS |
| a/b | 1.005919 | 1.005926 |
| a / b 平均毎秒 | 20624.873040 / 20503.513638 | 20687.565084 / 20565.697788 |
| 合計毎秒 | 41128.386678 | 41253.262872 |
| 完全接続 stats 窓 | 400.142051秒 | 380.184999秒 |
| 接続中 tick_us / catchups | 920..1065 / 0 | 920..1065 / 0 |
| drain 最大 / service 毎秒 | 60 µs / 約90.8 | 148 µs / 約99.7 |

X に切断はなく、Y は28.358234秒に reason=0x13（remote user terminated）で切断し、32.182286秒に再接続しました。旧 `f85c2fbe5456` は a/b=0.100775、合計約41151/sです。X は合計約41128/sで、この観測では大きな throughput 低下を示しませんが、厳密な性能上限の保証ではありません。

両案の公平性改善は、11 tick周期と10 tick quantum の位相固定仮説を実機で裏付けます。ただし dispatch trace 自体は未採取です。利用者は周期の組合せに依存しない X を採用しました。比較専用 overlay と CI matrix は除去し、debug/release/stress の quantum を既定1に統一します。host モデルは非実機の対照として維持します。

追加した自己検査は、常時 ready な同 priority worker の1秒間の差分が互いに2倍以内かを判定します。BM では1 ms timer による preemption を通ります。Wasm は MRBC_NO_TIMER の別経路であり、その成功だけでは BM を保証しません。新既定 image の DK 実行は次節に記録します。

### 新既定 image の最終 DK 確認と P1 完了判定

利用者が image `ef8514585aa2` を DK に書き込み、`dk-stress-20261111-204332.log` を採取しました。[firmware CI run 43013287420](https://github.com/uist1idrju3i/RBOS/actions/runs/43013287420) の `firmware-evidence-stress-ef8514585aa2e8b1d17d4c5e11fe281e9f1f0d24` に対応し、`production.hex` の SHA-256 は `fe263a152d87ae2a589f4ecd179edf43eedcf55da2092fc6a7b2f3cc58cea67a`、更新方式は ERASE_RANGES_TOUCHED_BY_FIRMWARE です。書込みは利用者が実施し、エージェントは操作していません。

[最終 log fixture](../../tests/check-changes/stress-final-capture.txt) と [checker 出力全文](../../tests/check-changes/stress-final-report.txt)を保存しました。`--profile stress` は PASS。自己検査10項目は `same-priority fairness` を含め全 PASS、切断なし、完全接続窓400.140059秒、tick 920..1064 µs、catchups=0、drain 最大70 µsでした。a/b=1.014307、a=20505.085196/s、b=20215.856468/s、service 約90.8/s。pool 標本最大15452/65536 B、main/ISR 688/560 Bです。PHY 2M の要求・完了 status=0x00、data length 251の要求・27への更新、ATT MTU rx=293の要求を記録し、応答修正版で接続が継続しました。MTU reply の成功結果そのものは log に出ないため、要求と接続継続の観測と区別します。

新既定で追加自己検査と5分 stress の実機確認がそろったため、過去の OOM、再接続・広告停止、Wasm Mutex fault の証拠と合わせ、承認済み closeout 条件に対して **P1 完了**と判定します。厳密な資源上限・一般的な進行保証・完全な IRQ 予約表は引き続き未確認です。release 実機・ERASE_NONE は P5、保存データ保持は P5/P6 の担当であり、P2〜P6 の完了は主張しません。

## 判明したリスクと blocker

実機の基本自己検査と短時間の接続試験は利用者報告で確認しました。残る制約は以下のとおりです。全項目が DK で障害として発生したという意味ではありません。

| リスク・境界 | 現在の事実と根拠 |
|---|---|
| timer 周期と ms の差 | SYS_CLOCK_TICKS_PER_SEC=31250、BM_TIMER_MS_TO_TICKS(1)=31、名目992 µs。HAL は絶対 uptime の whole ms に追従して mrbc_tick を0回以上呼ぶ。遅れを切り捨てる上限はなく、catch-up が長くなる可能性は未計測（`firmware/src/hal/hal.c:19-53`） |
| 保守の drain は無制限 | log_process は最大4回だが、bm_scheduler_process は queue が空になるまで callback を実行。新規 event や長い callback を含む実行時間に上限なし（`firmware/src/runtime.c:37-46`、`vendor/sdk-nrf-bm/lib/bm_scheduler/bm_scheduler.c:53-72`）。SCHED と512 Bの queue は確認済み。修正後の DK 接続 stress は最大60 µs、再接続 log は148 µsを観測したが、実行時間の上限保証ではない |
| service の認可は VM pointer のみ | `firmware/src/runtime.c:68-79` は保存した system task の VM pointer と比較。生成・破棄の lifecycle に結び付いた権限管理ではなく、拒否例も実機未試験。P3 で扱う |
| system task の優先度・停止を制限しない | priority 0 で生成するが、一般 Ruby task が Task.get で参照して priority= / suspend 等を呼ぶ API に caller 制限なし。自己検査では system task を変更していない。P3 の課題（`vendor/mrubyc/src/rrt0.c:914-943,1044-1069,1120-1135`） |
| pool の観測漏れ | pool_max は保守時の alloc_statistics の標本最大値。保守間に確保・解放した peak は拾わない（`firmware/src/runtime.c:48-50`） |
| stack scan の余裕 | main stack は現在 SP より256 B下まで paint。未塗布領域を使用済みとして数える保守的な値で、厳密な最大深さではない。ISR は INIT_STACKS を使用（`firmware/src/runtime.c:18-33`、`firmware/common.conf`） |
| abort 後の復旧 | LOG_PANIC 後に k_fatal_halt。app の自動 reboot / watchdog 復旧は未実装。OOM/fatal 経路は実機未試験（`firmware/src/hal/hal.c:96-103`） |
| RAM 予算 | debug 約83 KB（83,600 B、81.6 KiB）/ 237 KiB、34.45%。pool 64 KiB と main stack 8 KiB を静的予約済みだが、残量を将来 I/O/queue に無条件に使える保証ではない |
| 広告を必ず開始する | 起動時に利用者の選択なしで広告し、切断後も再開する。電力・公開範囲の制御は未設計。ただし無期限の「常時広告」ではない。両 `.config` の timeout は fast 1000、slow 18000（10 ms単位、10秒→180秒→idle）。`firmware/src/ble.c`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/ble_adv.c:108-118,181-232,393-428` が根拠 |
| release 鍵 | `firmware/sysbuild.cmake` の検査は変更なし。build に外部試験鍵を使用しただけで、量産鍵の管理・DK への移行・DFU を検証したものではない |

**mutex owner 終了と priority inversion（固定版の事実、規約採用済み）**

Ruby の Task#terminate は `mrbc_terminate_task()` を呼びます（`vendor/mrubyc/src/rrt0.c:1155-1169`）。同関数は task を DORMANT queue に移し preemption flag を立てるだけで、mutex の lock 状態を変えないと明記されています（同 `:645-664`）。通常終了でも scheduler の終了分岐は DORMANT 化と VM 終了・join 待ちの通知で、mutex 解放はありません（同 `:387-419`）。VM finalizer にも mutex の走査・unlock はありません（`vendor/mrubyc/src/vm.c:357-390`）。

共有 Mutex object が残る場合、owner が保持したまま終了しても lock と owner TCB の参照は自動解除されません。後続 task は MUTEX 待ちに入り、終了した owner の代わりに非 owner が正常な unlock をすることもできません。`mrbc_mutex_lock` の待機処理は同 `rrt0.c:717-751`、unlock の owner 検査と所有移譲は同 `:761-803` です。この状態は closeout の Wasm fault test でも確認しました。ensure 解放、非 owner unlock の構成別の差、同 priority 制約は [採用済み Mutex 規約](../mrubyc/task-scheduler.md#rbos-の-mutex-利用規約採用)を正本とします。

priority inheritance もありません。lock 待ちで変更するのは待機 task の state/reason/mutex と preemption flag だけで、owner の priority を引き上げません。unlock も所有移譲と起床だけです（同 `:717-803`）。`priority_preemption` への代入は初期化、再開、明示的な priority 変更の三箇所だけ（同 `:232,334,582-585`）でした。待機 queue を priority 順に選ぶ処理（同 `:55-90`）は、owner を昇格させる inheritance とは異なります。低優先 owner が中優先 ready task に妨げられる inversion の時間は未測定です。

## P2 への改善提案

以下の提案は利用者承認により採用しました。反映先と未実装・未検証を区別します。P1 の実機受け入れを済ませずに P2 完了とはしません。

1. **採用**: P1 の stress/oom profile、drain_us、checker・capture を実装。利用者の決定で stress を30分から完全接続窓5分へ変更しました。[checklist P1](checklist.md#p1-vm-と時間)は OOM、stress、再接続・広告停止に加え、X/Y 比較による公平性の採用判断も完了しました。
2. **採用**: [checklist P2](checklist.md#p2-native-api-と資源) と [porting-plan P2](porting-plan.md#p2-native-class-と値の規約) に共通引数 helper、Wasm fake の正常・無引数・nil・誤型・境界・driver failure、固定長 ring / newest drop / overflow counter / pin ごとの Button coalescing と count を記録。実装は P2 です。
3. **採用**: P2 checklist・計画に native API ごとの map と stack/pool 増分記録を追加。瞬間 peak 捕捉と paint margin 校正の検討も checklist に残しました。現在の標本統計を厳密な上限へ読み替えません。
4. **採用**: `tests/mruby/mutex_*.rb` と check.sh で Wasm fault を実行済み。[scheduler 文書](../mrubyc/task-scheduler.md#rbos-の-mutex-利用規約採用)に ensure 解放・保持 task の terminate 禁止・同 priority・非 owner unlock 禁止を規定し、製品 Ruby の skill から参照。inversion が問題と実測された場合だけ RBOS Mutex / 上流提案を再検討し、上流への連絡は別途承認を得ます。
5. **採用**: checklist・porting-plan の P3 に自己だけの Task 操作、system task 保護、system task による watchdog kick、debug halt / release flush 後 reboot を割当て。広告の開始・停止条件は P5、長時間回復試験は P6。方針のみで、認可・watchdog・release reboot は未実装です。

## checklist と porting-plan への追記候補

次の候補も採用して両文書に反映しました。完了印は証拠の範囲に限ります。stress の時間条件だけは、前述の利用者の決定で5分へ変更しました。

- **採用 / checklist P1**: Mutex fault＋規約は Wasm の証拠で [x]。DK fault 完了とはしません。
- **採用 / checklist P1**: 境界を除いた jitter・drain_us は修正後400秒 stress、abort は oom profile の利用者証拠で [x]。fairness 判断は [ ]。
- **採用 / checklist P2**: native API ごとの map と stack/pool 差を [ ] で追加。
- **採用 / checklist P3**: system task・他 task の priority=/suspend/terminate/raise 拒否試験を [ ] で明示。
- **採用 / porting-plan P3/P5/P6**: watchdog・fatal 回復は P3、広告条件は P5、長時間実機試験は P6。release image / ERASE_NONE は P5、保存データ保持は P5/P6 に移しました。

[調査索引へ戻る](../README.md)
