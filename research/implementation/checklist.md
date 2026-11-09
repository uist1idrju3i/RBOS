# 実装前チェックリストとリスク

チェックは、完了の証拠がある項目だけに入れます。証拠がない項目は空のままにします。方針は [判断記録](../architecture/decisions.md)、実施順は [段階計画](porting-plan.md)を参照してください。

## P0: 環境と target

- [x] NCS/toolchain v3.3.0、BM v2.0.1、全 module SHA を固定する。[modules.txt](../../tools/bm-build/modules.txt) と `check-workspace.sh` で照合します。
- [x] S115 target で recovery sample の build/flash を確認する。利用者が 2026-11-09 JST に起動 log と `Advertising as nRF_BM_Entry` を確認しました。Device Manager から loader へ切り替える操作は未確認です（[実機結果](dk-provisioning.md#記録表)）。
- [x] central 不使用・S115 固定の構成を維持する。`firmware/CMakeLists.txt` が他の board target を拒否し、build の `.config` で S115 だけが有効でした。
- [x] board revision、配線、認証番号を実物・公的資料で照合する。利用者が PCA10156 revision 1.0.0、`220-JP8930` と LED0 / BUTTON0 / TXD1 の背面印字を照合しました。配線の確認範囲はこの三つの pin です（[実機結果](dk-provisioning.md#記録表)）。
- [ ] erase/recover と通常 flash を分け、保存データの扱いを記録する。全体 erase なし・鍵の再準備なしで v0.1.1 の起動は確認しましたが、書き込み前後の保存データは実機で比較していません。
- [x] RBOS の CMake、Kconfig、sysbuild、board overlay、署名設定の最小構成を作る。
- [x] release/debug と秘密鍵の配置を分離する。release の鍵の検査は五つの拒否例で build の失敗を確認しました。
- [x] 全 module SHA、map、compiler 版を集める手順と script を作る。
- [ ] map 等の成果物を CI の artifact として保存する。
- [x] clean な workspace で build を再現する。同じ host の二回の debug build が byte 単位で一致しました。別 host は未確認です。
- [x] DK 上で LED、console、loader 入口を確認する。LED0 点灯、`RBOS 0.1.0+0`、BUTTON0 + RESET による `nRF_BM_MCUmgr` の広告と RESET による RBOS への復帰を利用者が確認しました（[実機結果](dk-provisioning.md#記録表)）。
- [x] 新しい DK の初回準備（erase と KMU への鍵の書き込み）を通常の書き込みと分けて手順にする。[DK の準備](dk-provisioning.md)。
- [ ] erase なしで KMU に鍵を書く手順（`x-provision-keys`）を実機で確かめる。
- [x] 同じ commit の CI とローカルの build で、debug の成果物の hash が一致することを確かめる。commit `5664b86` で app、loader、SoftDevice、`production.hex` が一致しました（[CI の実行](https://github.com/uist1idrju3i/RBOS/actions/runs/42528666949)）。

2026-11-09 JST の利用者報告を受け、P0 の受け入れ条件は満たしたと判断します（[判定の根拠](retrospective-P0.md#p0-の受け入れ判定)）。保存データの維持や erase なしの初回準備まで確認したという意味ではなく、未確認の項目は空欄のまま残します。

出典: [SDK 環境](../nrf-bm/setup-and-build.md)、[build 再現手順](bm-build.md)、[DK の準備](dk-provisioning.md)、[P0 の振り返り](retrospective-P0.md)、[ハードウェア](../hardware/nrf54l15-dk.md)。

## P1: VM と時間

- [ ] vendor/mruby 4.0.0 の mrbc build・再配布方法を決める。
- [ ] RITE0400 の正常・不正 bytecode の検査を作る。
- [ ] MAX_VM_COUNT、register、symbol、float、string/debug 設定を固定する。
- [ ] pool と IREP 等の追加確保、C stack、割り込み stack の上限を測定する。
- [ ] tick、同 priority の巡回、sleep、mutex、suspend/resume を確認する。
- [ ] mruby/c の結合後に debug/release を build し、P0 からの map の増分を記録する。
- [ ] priority inversion、mutex owner 終了時の方針を決める。
- [ ] idle と deferred event が常時 ready の task に妨げられないようにする。
- [ ] SoftDevice priority 0/1 と GRTC channel0 を予約する。
- [ ] peripheral、DPPI、IRQ の完全な予約表を対象 SoftDevice の仕様と照合する。
- [ ] SDH 配送 model と SD RAM usage、BM queue の容量と drain 時間を .config/map/実測で確認する。[SDK 調査](../nrf-bm/component-catalog.md)参照。

出典: [scheduler](../mrubyc/task-scheduler.md)、[設定とメモリ](../mrubyc/configuration-and-memory.md)、[IRQ](../nrf-bm/softdevice-and-interrupts.md)。

## P2・P3: native API と信頼境界

- [ ] console を UARTE/RTT/BLE のどれにするか決め、pin の共有を確認する。
- [ ] argc/type/range、return/raise、参照カウントの共通規約を決める。
- [ ] ISR event をコピーする queue と overflow policy を決める。
- [ ] user VM に許す Task 操作と peripheral の範囲を決める。
- [ ] system Ruby の信頼元、権限付与、破棄、ID 再利用を定義する。
- [ ] 特権 API の全 callback に認可検査を入れる。
- [ ] debug API と system-only API を分離する。
- [ ] retention 入口（boot mode）へ移る要求を書く API を特権操作に限る。
- [ ] user task による他 task の停止・例外送信と拒否動作を試す。
- [ ] application/shell UARTE30 の重複、NFC TIMER24、GRTC 予約、各 callback の実行 context を照合する。
- [ ] bonding を採用する場合、初期 BLE でも BM_ZMS/SD backend と peer partition の予算を確保する。

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
- [x] release の鍵の検査で、SDK の既定鍵を名前でなく公開鍵の比較で拒否する。改名した既定鍵の拒否と、`root-*.pem` という名前の新しい鍵の受け入れを build で確認しました。
- [ ] BOOTCONF lock 前に復旧手順と製造時の消去条件を確認する。
- [ ] 切断、不正署名、容量超過、各 write 時の電源断を試す。
- [ ] MCUmgr の OPEN default と必要 command の許可、retention clipboard の CRC/寿命・容量を確認する。[管理機能](../nrf-bm/mcumgr.md)参照。

出典: [bytecode 埋め込み](../dfu/embedded-bytecode.md)、[DFU](../dfu/single-bank-dfu.md)、[MCUboot の境界](../dfu/mcuboot.md)。

## P6: 品質と公開

- [ ] toolchain container の利用条件・digest を確定する。
- [x] emscripten HAL の Ruby 検査 CI を実装する。[検査手順と実機試験の境界](../../tools/mrubyc-wasm/README.md)を明記する。
- [ ] map/size、stack/pool 使用量、長時間試験ログを保存する。
- [ ] firmware build の成果物と SHA256SUMS を CI artifact に残す。
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
