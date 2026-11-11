# 実装前チェックリストとリスク

チェックは、完了の証拠がある項目だけに入れます。証拠がない項目は空のままにします。方針は [判断記録](../architecture/decisions.md)、実施順は [段階計画](porting-plan.md)を参照してください。

## P0: 環境と target

- [x] NCS/toolchain v3.3.0、BM v2.0.1、全 module SHA を固定する。[modules.txt](../../tools/bm-build/modules.txt) と `check-workspace.sh` で照合します。
- [x] S115 target で recovery sample の build/flash を確認する。利用者が 2026-11-09 JST に起動 log と `Advertising as nRF_BM_Entry` を確認しました。nRF Connect Device Manager Android から Boot Mode=1 の reset を送り、MCUboot の再起動後に `BLE MCUmgr sample started` と `Advertising as FL_12345` を確認し、loader への切り替えも成功しました（[実機結果](dk-provisioning.md#記録表)）。
- [x] central 不使用・S115 固定の構成を維持する。`firmware/CMakeLists.txt` が他の board target を拒否し、build の `.config` で S115 だけが有効でした。
- [x] board revision、配線、認証番号を実物・公的資料で照合する。利用者が PCA10156 revision 1.0.0、`220-JP8930` と LED0 / BUTTON0 / TXD1 の背面印字を照合しました。配線の確認範囲はこの三つの pin です（[実機結果](dk-provisioning.md#記録表)）。
- [ ] erase/recover と通常 flash を分け、保存データの扱いを記録する。全体 erase なし・鍵の再準備なしで v0.1.1 の起動は確認しましたが、書き込み前後の保存データは実機で比較していません。
- [x] RBOS の CMake、Kconfig、sysbuild、board overlay、署名設定の最小構成を作る。
- [x] release/debug と秘密鍵の配置を分離する。release の鍵の検査は五つの拒否例で build の失敗を確認しました。
- [x] 全 module SHA、map、compiler 版を集める手順と script を作る。
- [x] map 等の成果物を CI の artifact として保存する。[workflow](../../.github/workflows/firmware.yml) と [収集 script](../../tools/bm-build/collect-evidence.sh) が `zephyr.map`、`.config`、`build_info.yml`、tool/compiler のバージョン、`SHA256SUMS` を `firmware-evidence-<variant>-<sha>` に7日間保存し、`.pem` と `keyfile.json` を除外します。[実行例](https://github.com/uist1idrju3i/RBOS/actions/runs/42620432714)の `firmware-evidence-debug-6d09bd5068f26c65258d9ed3da3d66ac6c84670a` は利用者が DK 書き込みに使用しました。正式 release の証拠の長期保管は、この項目の対象外です。
- [x] clean な workspace で build を再現する。同じ host の二回の debug build が byte 単位で一致しました。別 host は未確認です。
- [x] DK 上で LED、console、loader 入口を確認する。LED0 点灯、`RBOS 0.1.0+0`、BUTTON0 + RESET による `nRF_BM_MCUmgr` の広告と RESET による RBOS への復帰を利用者が確認しました（[実機結果](dk-provisioning.md#記録表)）。
- [x] 新しい DK の初回準備（erase と KMU への鍵の書き込み）を通常の書き込みと分けて手順にする。[DK の準備](dk-provisioning.md)。
- [ ] erase なしで KMU に鍵を書く手順（`x-provision-keys`）を実機で確かめる。
- [x] 同じ commit の CI とローカルの build で、debug の成果物の hash が一致することを確かめる。commit `5664b86` で app、loader、SoftDevice、`production.hex` が一致しました（[CI の実行](https://github.com/uist1idrju3i/RBOS/actions/runs/42528666949)）。

2026-11-09 JST の利用者報告を受け、P0 の受け入れ条件は満たしたと判断します（[判定の根拠](retrospective-P0.md#p0-の受け入れ判定)）。保存データの維持や erase なしの初回準備まで確認したという意味ではなく、未確認の項目は空欄のまま残します。

出典: [SDK 環境](../nrf-bm/setup-and-build.md)、[build 再現手順](bm-build.md)、[DK の準備](dk-provisioning.md)、[P0 の振り返り](retrospective-P0.md)、[ハードウェア](../hardware/nrf54l15-dk.md)。

## P1: VM と時間

- [x] vendor/mruby 4.0.0 の mrbc build・再配布方法を決める。binary は再配布せず、configure 時にコピーから `build_config/mrbc.rb` で build。`firmware/cmake/mrubyc.cmake` と [host mrbc の記録](bm-build.md#host-mrbc-と-bytecode)参照。
- [x] RITE0400 の正常・不正 bytecode の検査を作る。`tools/mrubyc-wasm/check.sh` の正常・空 Ruby・誤 version/magic/size、`tools/bm-build/check-bytecode.py` の build-time 検査、`tests/check-changes/test_bytecode.py` の拒否例を実行。`bb6e99b` の変更を含む作業木で Wasm exit 0、unittest 全12件 OK（[検査記録](retrospective-P1.md)）。
- [x] MAX_VM_COUNT、register、symbol、float、string/debug 設定を固定する。両 variant の rrt0 compile command を前処理して MAX_VM_COUNT=8、MAX_REGS_SIZE=110、MAX_SYMBOLS_COUNT=255、MRBC_USE_FLOAT=2（double）、MRBC_USE_STRING=1 を確認。debug は MRBC_DEBUG 有効、release は VM source のみ NDEBUG=1 / MRBC_DEBUG 無効。`firmware/Kconfig`、`firmware/cmake/mrubyc.cmake`、`vendor/mrubyc/src/vm_config.h:18-79,122-125` が根拠です。
- [ ] pool と IREP 等の追加確保、C stack、割り込み stack の上限を測定する。下記の実機観測値はありますが、IREP の個別量・瞬間 peak・高負荷時の上限は未測定です。
- [x] P1 自己検査で stack/pool の観測値を記録する。利用者の CI debug 実機 log は pool 最大標本11560/65536 B（17.6%）、main paint scan 688/8192 B、ISR 560/2048 B。main は256 Bの未塗布余裕を含み、厳密な使用上限ではありません（[実機結果と統計の意味](retrospective-P1.md)）。
- [x] tick、同 priority の巡回、sleep、mutex、suspend/resume を確認する。`firmware/ruby/selftest/` の全 PASS を利用者の DK log で確認。`PASS: workers joined` と `PASS: idle wakeup` も確認しました（[実機結果](retrospective-P1.md)）。
- [x] BLE 接続中の tick callback 間隔を測る。完全接続区間936..1049 µs、接続前930..1040 µs、全行 catchups=0。tick は約10000回/10秒。境界混在区間は比較から除外しました（[区間の根拠](retrospective-P1.md)）。
- [x] BLE の接続・切断後の再広告、二度目の接続、slow 広告180秒後の停止を確認する。image `f85c2fbe5456` の利用者 log で二接続と remote 終了 reason=0x13を確認。最後の切断102.890137秒→slow 112.880452秒→Idle 292.847109秒が証拠です（[修正後の実機結果](retrospective-P1.md#ble-応答修正後の-dk-証拠)）。
- [x] mruby/c の結合後に debug/release を build し、P0 からの map の増分を記録する。[部品別表と集計方法](bm-build.md#p1-の-build-結果と-map-比較)に app の FLASH/RAM 差を記録。debug は +82,444 / +78,152 B、release は +71,444 / +77,920 B でした。
- [x] Mutex owner 終了・例外・優先度差の fault test を Wasm で実行し、利用規約を文書化する。`6819755` の `tests/mruby/mutex_*.rb` と `tools/mrubyc-wasm/check.sh` が owner 終了後の保持、ensure 解放、inversion、非 owner unlock の assertion を確認しました。[採用済み規約](../mrubyc/task-scheduler.md#rbos-の-mutex-利用規約採用)参照。実機の fault 試験は未実施です。
- [x] 二つの常時 ready task の負荷中に、BLE の完全接続 stats 窓の合計5分（300秒）を満たし、境界を除いた jitter と `drain_us` 最大値を保存する。利用者の決定で30分から5分へ変更しました。image `f85c2fbe5456` の [利用者 log](../../tests/check-changes/stress-connected-capture.txt) は当時の stress 条件で PASS（現在は公平性で FAIL）。完全接続400.122214秒、切断なし、tick 920..1064 µs、catchups=0、drain 最大60 µsです。旧 log の230.067537秒未達とは分けて記録します。
- [x] 同 priority spinner の公平性を比較し方針を決める。image `7217cb685dd2` の X/Y は a/b=1.005919 / 1.005926で stress PASS。利用者は X（quantum 1 tick、service sleep 10 ms）を既定に採用しました。checker は2倍超を FAIL とし、自己検査にも同基準を追加しました。[証拠と採用理由](retrospective-P1.md#xy-比較と1-tick-の採用)参照。
- [x] 公平性自己検査を含む新既定 image を DK で確認する。`ef8514585aa2` は自己検査10項目が全 PASS、a/b=1.014307、完全接続400.140059秒で stress PASS。tick 920..1064 µs、catchups=0、drain 最大70 µs、pool 標本最大15452/65536 B、main/ISR 688/560 Bでした。[最終 log と checker 全文](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)参照。
- [x] `oom` profile で DK の OOM/abort 経路を確認する。利用者の image `3d1fd598c609` は `OOM: start` → `RBOS fatal: Ruby pool exhausted` を出し、[実 capture fixture](../../tests/check-changes/oom-capture.txt)を OOM checker で PASS と確認しました。fatal 前の stats はなく pool 上限は未計測です。
- [ ] idle と deferred event が常時 ready の task に妨げられないようにする。DK の idle wakeup は PASS。stress の二 spinner と BLE の同時負荷でも service 約90.7回/秒と drain 最大144 µsを確認しました。queue の上限と一般的な進行保証は未確認です。
- [x] SoftDevice priority 0/1 と GRTC channel0 を予約する。静的確認: 両 app の ZERO_LATENCY_IRQS=y / ZERO_LATENCY_LEVELS=1、3 priority bits、BASEPRI=0x40（NVIC 2以上を mask）。`firmware/src/hal/hal.c` は SDK の irq_lock と bm_timer のみを使い、直接 GRTC/channel を操作しません。bm_timer は `k_timer` を経由し、SDK の channel0 予約を維持（[根拠と確認の境界](retrospective-P1.md#達成と未達)）。
- [ ] peripheral、DPPI、IRQ の完全な予約表を対象 SoftDevice の仕様と照合する。
- [ ] SDH 配送 model と SD RAM usage、BM queue の容量と drain 時間を .config/map/実測で確認する。両 app の `.config` は SCHED、BM_SCHEDULER_BUF_SIZE=512。修正後の DK 接続 stress では drain 最大60 µs、再接続 log では148 µsを観測しましたが、一般的な上限と SD RAM の実測は未確認です。[SDK 調査](../nrf-bm/component-catalog.md)参照。

実機の証拠は旧自己検査・OOM・BLE 検査・X/Y 比較に加え、新既定 `ef8514585aa2` の最終 log です。Wasm Mutex、DK OOM、再接続・広告停止、新既定での公平性自己検査と5分 stress がそろい、承認済み closeout 条件に対して **P1 完了**と判定します。[最終結果と限界](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)を参照してください。未チェックの一般的な進行保証・厳密な資源上限・完全な予約表の課題は残します。release 実機・ERASE_NONE・保存データ検証は P5/P6 が担当します。通常更新は ERASE_RANGES_TOUCHED_BY_FIRMWARE です。

出典: [scheduler](../mrubyc/task-scheduler.md)、[設定とメモリ](../mrubyc/configuration-and-memory.md)、[IRQ](../nrf-bm/softdevice-and-interrupts.md)。

## P2: native API と資源

- [ ] console を UARTE/RTT/BLE のどれにするか決め、pin の共有を確認する。
- [ ] native API を追加するたびに、P1 と同じ map 分類と stack/pool 観測方法で増分を記録する。瞬間 peak の捕捉や paint margin の校正は別に検証し、標本値を厳密な上限と呼ばない。
- [ ] 共有 C API の argc/type/range 検査を共通 helper に集約し、return/raise・参照カウントの規約を実装する。Wasm fake で正常・引数なし・nil・誤型・境界・driver failure を試す。
- [ ] ISR event queue を固定長 ring とし、overflow 時は newest を drop して stats に overflow counter を出す。Button edge は pin ごとに coalesce し、count を保持する。承認済みの設計であり、実装・試験は未完了です。
- [ ] application/shell UARTE30 の重複、NFC TIMER24、GRTC 予約、各 callback の実行 context を照合する。
- [ ] bonding を採用する場合、初期 BLE でも BM_ZMS/SD backend と peer partition の予算を確保する。

## P3: system task と信頼境界

- [ ] user VM に許す peripheral の範囲を決める。
- [ ] system Ruby の信頼元、権限付与、破棄、ID 再利用を定義する。
- [ ] 特権 API の全 callback に認可検査を入れる。
- [ ] debug API と system-only API を分離する。
- [ ] retention 入口（boot mode）へ移る要求を書く API を特権操作に限る。
- [ ] user VM の priority=/suspend/terminate/raise は自己にだけ許可し、他 task・system task への操作を拒否する認可試験を作る。system task は user から変更不能にする。現行 Task API にはこの制限がなく、P3 で実装します。
- [ ] system task が watchdog を kick する。fatal 時は debug は現在どおり halt、release は log flush 後に reboot する。承認済みの回復方針であり、watchdog と release reboot は未実装です。

出典: [C API](../mrubyc/c-api.md)、[OpenBlink 参照と制限](../openblink/api-binding-patterns.md)。

## P4・P5: 埋め込みと firmware 更新

- [ ] 固定 mrbc で const C 配列を生成し、入力と生成物 hash を記録する。
- [ ] RRAM 配置、alignment、symbol 等を含む参照の寿命を確認する。
- [ ] 全体 RAM コピーなしで正常・空・不正形式・OOM を検査する。
- [ ] String 変更で const blob が書き換わらないことを確認する。
- [ ] bytecode 更新を firmware 再build と DFU のみに限定する。
- [ ] firmware single-bank の GPIO/reset/retention 入口を確認する。
- [ ] app/loader/installer の容量と署名済み成果物を確認する。
- [ ] 固有 ED25519 key と KMU provisioning を用意する。
- [ ] P5: release 鍵で準備した DK に release image を書き込み、起動と通常更新を確認する。
- [ ] P5: ERASE_NONE 更新を実機で検証する。現在の成功例は ERASE_RANGES_TOUCHED_BY_FIRMWARE だけです。
- [ ] P5: 広告の開始・停止・再開条件を実装し、DFU と復旧の入口を照合する。P1 の既存 timeout 観測とは分ける。
- [x] release の鍵の検査で、SDK の既定鍵を名前でなく公開鍵の比較で拒否する。改名した既定鍵の拒否と、`root-*.pem` という名前の新しい鍵の受け入れを build で確認しました。
- [ ] BOOTCONF lock 前に復旧手順と製造時の消去条件を確認する。
- [ ] 切断、不正署名、容量超過、各 write 時の電源断を試す。
- [ ] MCUmgr の OPEN default と必要 command の許可、retention clipboard の CRC/寿命・容量を確認する。[管理機能](../nrf-bm/mcumgr.md)参照。

出典: [bytecode 埋め込み](../dfu/embedded-bytecode.md)、[DFU](../dfu/single-bank-dfu.md)、[MCUboot の境界](../dfu/mcuboot.md)。

## P6: 品質と公開

- [ ] toolchain container の利用条件・digest を確定する。
- [x] emscripten HAL の Ruby 検査 CI を実装する。[検査手順と実機試験の境界](../../tools/mrubyc-wasm/README.md)を明記する。
- [ ] map/size、stack/pool 使用量、長時間試験ログを保存する。
- [ ] P5 の更新・storage 設計に対し、保存データが更新前後で保持されることを P6 の実機試験で検証・保存する。通常更新の起動成功だけを保持の証拠にしない。
- [x] firmware build の成果物と SHA256SUMS を CI artifact に残す。[P0 の証拠](#p0-環境と-target)と同じ7日間の保存を確認しました。正式 release の証拠の長期保管まで完了したという意味ではありません。
- [ ] third-party notice、署名鍵を含まない成果物、再配布条件を確認する。
- [ ] 日本語文書、英語のコードコメント、skill/link 検査を CI で維持する。

出典: [ライセンス](../licenses.md)、`AGENTS.md:20-29,58-69`。

## 主なリスク

| リスク | 影響 | 確認・軽減案 |
|---|---|---|
| 常時 ready の VM と BM scheduler | storage/BLE の遅延処理が進まない | foreground service の実行点を P1 で作る |
| native callback の長時間実行 | tick flag だけでは即時中断できない | callback を短くし、長い I/O は非同期化 |
| app RAM 237 KiB と参考 stack/heap | 単純流用で予算不足 | image ごとに map と high-water を測る |
| const bytecode の RAM 見積もり | 全体コピー不要でも IREP/String 等は消費 | map と pool 統計で確認 |
| VM ID だけの権限 | 再利用・子 task で漏れる可能性 | lifecycle に結び付けた認可試験 |
| 将来の OpenBlink 保存 | 電源断時の program 消失 | 採用時に保存・認証・fallback を再設計 |
| single-bank firmware 更新中断 | main app が起動不能 | 独立 loader の recovery を試験 |
| dummy key / BOOTCONF lock | 不正更新または開発復旧困難 | release gate と製造手順を分離 |
| vendor/online latest の差 | 手順・API の不一致 | 固定 SHA と版付き資料を優先 |

表の影響は設計上のリスク評価で、RBOS で発生を観測した障害ではありません。根拠となる実装・容量は上記の各調査文書に示しています。

[調査索引へ戻る](../README.md)
