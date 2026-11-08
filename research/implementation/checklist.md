# 実装前チェックリストとリスク

以下は未実施の作業です。完了済みの証拠がない項目にチェックを入れません。方針は [判断記録](../architecture/decisions.md)、実施順は [段階計画](porting-plan.md)を参照してください。

## P0: 環境と target

- [ ] NCS/toolchain v3.3.0、BM v2.0.1、全 module SHA を固定する。
- [ ] S115 target で recovery sample の build/flash を確認する。
- [ ] S145/central、多接続が必要か決める。
- [ ] board revision、配線、認証番号を実物・公的資料で照合する。
- [ ] erase/recover と通常 flash を分け、保存データの扱いを記録する。

出典: [SDK 環境](../nrf-bm/setup-and-build.md)、[ハードウェア](../hardware/nrf54l15-dk.md)。

## P1: VM と時間

- [ ] mruby 4.0.0 の mrbc 入手・再配布方法を決める。
- [ ] RITE0400 の正常・不正 bytecode の検査を作る。
- [ ] MAX_VM_COUNT、register、symbol、float、string/debug 設定を固定する。
- [ ] pool と bytecode buffer、C stack、割り込み stack の上限を測定する。
- [ ] tick、同 priority の巡回、sleep、mutex、suspend/resume を確認する。
- [ ] priority inversion、mutex owner 終了時の方針を決める。
- [ ] idle と deferred event が常時 ready の task に妨げられないようにする。
- [ ] SoftDevice priority 0/1 と GRTC channel0 を予約する。
- [ ] peripheral、DPPI、IRQ の完全な予約表を対象 SoftDevice の仕様と照合する。

出典: [scheduler](../mrubyc/task-scheduler.md)、[設定とメモリ](../mrubyc/configuration-and-memory.md)、[IRQ](../nrf-bm/softdevice-and-interrupts.md)。

## P2・P3: native API と信頼境界

- [ ] console を UARTE/RTT/BLE のどれにするか決め、pin の共有を確認する。
- [ ] argc/type/range、return/raise、参照カウントの共通規約を決める。
- [ ] ISR event をコピーする queue と overflow policy を決める。
- [ ] user VM に許す Task 操作と peripheral の範囲を決める。
- [ ] system Ruby の信頼元、権限付与、破棄、ID 再利用を定義する。
- [ ] 特権 API の全 callback に認可検査を入れる。
- [ ] debug API と system-only API を分離する。
- [ ] user task による他 task の停止・例外送信と拒否動作を試す。

出典: [C API](../mrubyc/c-api.md)、[OpenBlink 参照と制限](../openblink/api-binding-patterns.md)。

## P4・P5: 更新と保存

- [ ] `.mrb` 最大長、header、digest、RITE、commit state を固定する。
- [ ] bm_zms/raw の採否と storage0 の sector 構成を決める。
- [ ] peer manager 領域と更新領域が衝突しないことを確認する。
- [ ] async 完了前の buffer 解放、二重更新、callback 再入を防ぐ。
- [ ] 無効・不在時の組み込み default と診断を用意する。
- [ ] BLE `.mrb` の protocol、host tool、認証・pairing を決める。
- [ ] firmware single-bank の GPIO/reset/retention 入口を確認する。
- [ ] app/loader/installer の容量と署名済み成果物を確認する。
- [ ] 固有 ED25519 key と KMU provisioning を用意する。
- [ ] BOOTCONF lock 前に復旧手順と製造時の消去条件を確認する。
- [ ] 切断、不正署名、容量超過、各 write 時の電源断を試す。

出典: [bytecode 保存](../dfu/bytecode-storage.md)、[DFU](../dfu/single-bank-dfu.md)、[MCUboot の境界](../dfu/mcuboot.md)。

## P6: 品質と公開

- [ ] toolchain container の利用条件・digest を確定する。
- [ ] host test、build CI、HIL の責務を分ける。
- [ ] map/size、stack/pool 使用量、長時間試験ログを保存する。
- [ ] third-party notice、署名鍵を含まない成果物、再配布条件を確認する。
- [ ] 日本語文書、英語のコードコメント、skill/link 検査を CI で維持する。

出典: [ライセンス](../licenses.md)、`AGENTS.md:20-29,58-69`。

## 主なリスク

| リスク | 影響 | 確認・軽減案 |
|---|---|---|
| 常時 ready の VM と BM scheduler | storage/BLE の遅延処理が進まない | foreground service の実行点を P1 で作る |
| native callback の長時間実行 | tick flag だけでは即時中断できない | callback を短くし、長い I/O は非同期化 |
| app RAM 237 KiB と参考 stack/heap | 単純流用で予算不足 | image ごとに map と high-water を測る |
| storage0 4 KiB | `.mrb` と GC の余白不足 | compile 実測から partition を再設計 |
| VM ID だけの権限 | 再利用・子 task で漏れる可能性 | lifecycle に結び付けた認可試験 |
| single-copy 更新中断 | user program の消失 | 無効判定 + 内蔵 default + 再転送 |
| single-bank firmware 更新中断 | main app が起動不能 | 独立 loader の recovery を試験 |
| dummy key / BOOTCONF lock | 不正更新または開発復旧困難 | release gate と製造手順を分離 |
| vendor/online latest の差 | 手順・API の不一致 | 固定 SHA と版付き資料を優先 |

表の影響は設計上のリスク評価で、RBOS で発生を観測した障害ではありません。根拠となる実装・容量は上記の各調査文書に示しています。

[調査索引へ戻る](../README.md)
