> **履歴資料（2026-11-15）**: [出典セッション](https://app.devin.ai/sessions/3d2a42a786954ce0b1ee961cf57f4d57)の添付原報告です。以下は当時の主張・提案であり、現在の確認結果や承認ではありません。[再確認と訂正](session-plan-review.md)を先に読んでください。原文の誤り・未完の値も履歴として残しています。個人環境の絶対パスのみ `<checkout>/` に置換しました。今回の依頼は会話・ログ・報告の再確認と保存です。この写しでは新しい検証を行っていません。

# RBOS 実装状況の照合と今後の計画（2026-11-15）

対象: uist1idrju3i/RBOS main `243682c`（firmware 0.1.4+0）
照合方法: `research/implementation/porting-plan.md`・`checklist.md`・各 retrospective と、firmware/src・src/rbos・src/platform/nrf・tests・tools・CI の実態、最新 main の CI 結果を突き合わせました。本書は計画の共有用で、リポジトリへはコミットしません。

## 1. 段階ごとの現状

### P0: BM の再現可能な基盤（完了・残2項目）

受け入れ判定済み（retrospective-P0）。checklist の空欄は2件です。

- 書き込み前後の保存データの実機比較（P5/P6 へ継続課題）
- erase なしの KMU 鍵書き込み `x-provision-keys` の実機確認

### P1: mruby/c を OS の中核（完了・承認済み closeout）

mruby/c+rrt0、BM HAL、BLE 広告・接続応答修正、自己検査、stress/oom profile、公平性の採用（案 X: quantum 1 tick）まで実機証拠あり。利用者決定により4項目は観測値で完了とし、以下へ移管済みです。

- 厳密な資源上限・進行保証 → P6
- 完全な予約表・SD RAM/queue 照合 → P2（下記の通り一部未了）
- release 実機・ERASE_NONE → P5、保存データ保持 → P5/P6

### P2: native class と値の規約（コード実装完了・実機受け入れは未実施）

実装済みです（main `8096c28` 以降の四構成 evidence と `p2-gate-results.json` で `bm_build: PASS`、`real_hardware: NOT_RUN`）。

- 共有 native 基盤（argc/type/range/keyword 検査、借用/生成値の返却規約）
- 固定長 event ring（16件、newest drop、pin/generation ごと coalesce、stats 出力）
- GPIO（Integer/String/DT Symbol pin、物理値、mode、予約 pin 保護、RBS）
- Button（GPIOTE20/30 producer、`poll`/`wait`/`each_event`/`pressed?`/`close`、generation/lease 回収）
- `Temperature.read`（S115 `sd_temp_get`、Float °C、keyword 拒否を含む契約検査）
- `ADC.internal(:dvdd/:avdd/:vdd)`（nrfx_saadc、IRQ213→mailbox→foreground、busy 拒否、協調待機、STOPPED 捕捉）
- BM preflight、api-contracts.json 在庫検査（公開25 API）、四構成 evidence verifier（map_delta 記録込み）
- console は UARTE20 維持、UARTE30/shell/NFC 無効、bonding 非対応

未完了（全て `real_hardware` 側で、DK が必要です）。

- 実機の GPIO 電位・Button IRQ/coalesce・ring 飽和（deterministic な信号源が必要）
- `sd_temp_get` の実時間・精度・他 task/BLE/tick への影響
- SAADC の実機精度（VDD 実測値との比較、DVDD/AVDD 妥当性、入力切替・反復）
- IRQ 競合、SD RAM/queue 余裕、stack/pool 瞬間 peak、BLE 接続中5分 stress（P2 条件）
- 予約表の実機競合検査（静的照合は済み）
- map 増分は記録済みだが stack/pool の API ごとの個別観測は未実施（checklist 空欄のまま）

### P3: system task と権限（未着手）

コード上の現状: `RBOSSystem.service` の認可は「保存した system task の VM pointer との比較」のみ。priority=/suspend/terminate/raise に caller 制限なし。watchdog・release reboot 経路は未実装（fatal は halt）。

### P4: const bytecode の生成・結合（機構は実装済み、受け入れ条件は未検証）

- 実装済み: 固定 mruby 4.0.0 の mrbc で `-B` 生成した const 配列を `embedded.c` 経由で link、`check-bytecode.py` が build-time に RITE0400/形式を検査。rrt0 は入力 blob を RRAM から直接参照する設計（load.c 根拠）。
- 未検証: map/debugger での RRAM 配置確認、IREP/symbol/String/register の RAM 個別計測、String 変更で blob 不変の確認、空/不正/OOM/task 作成失敗の受け入れ試験、生成物 hash 記録の一部。

### P5: firmware DFU（loader 統合済み、app 側は未着手）

- 実装済み: sysbuild で `BM_FIRMWARE_LOADER_BT_MCUMGR=y`（debug/release 両方）、DK で loader 入口（BUTTON0+RESET → `nRF_BM_MCUmgr` 広告）を確認済み。release は公開鍵比較で SDK 既定鍵を拒否。
- 未着手/未確認: single-bank DFU の実機 E2E、DLE/ATT MTU の決定と転送速度測定（現 app は 251 要求に 27 で応答）、`RBOS_XXXX` デバイス名（FICR DEVICEID）、広告の開始/停止/再開条件、固有 ED25519 鍵・KMU provisioning・IRoT・installer 更新手順、release DK 起動・ERASE_NONE、MCUmgr 認証・retention CRC/寿命、切断/誤署名/電源断の fault injection、storage/peer data 保持。

### P6: CI と長時間試験（基盤あり、長期試験は未実施）

- 実装済み: firmware.yml（preflight + 四構成 + evidence）、mruby-wasm.yml、agent-docs.yml、CodeQL。最新 main（243682c）は要求 check 全 PASS（docs-only のため build 系 job は changes 判定で skip、設計どおり）。
- 未着手: toolchain container の digest/利用条件、長時間 HIL（BLE 長接続・jitter・watchdog・DFU 電源断）、厳密な上限評価、保存データ保持検証、third-party notice/再配布条件、正式 release 証拠の長期保管。

### 横断事項

- dependabot の submodule bump が3件 open のまま: #16 sdk-nrf-bm、#18 mrubyc、#23 mruby。採否は `vendor-update` skill の手続きが必要。
- Float 無効 VM は固定 mruby/c の `boxing_no.h` 問題で全体 build 不可（binding の拒否 guard のみ host 検査）。Float 無効構成を約束しない方針は既に契約に反映済み。
- Wasm の idle hook が実 scheduler の service に届かない不具合は修正済み（task 終了/VM ID 再利用の寿命試験が有効）。

## 2. 今後の計画案

作業は「利用者の DK 操作が必要な実機受け入れ」と「エージェントだけで進められる設計・実装・host 検証」に分かれます。後者を並行して進め、前者は利用者の実機作業枠にまとめて依頼する構成を推奨します。

### Phase A（エージェントのみで完結可能、DK 不要）

**A1. P4 受け入れの host/build 側（小規模）**
- map で const blob の RRAM 配置と全体 RAM コピー不在を確認し、IREP/symbol/String/register の RAM を個別計測して記録。
- 空 Ruby・不正 RITE・OOM・task 作成失敗の host/Wasm 拒否試験、String 変更で blob 不変の試験を追加。
- 生成物（入力 .rb・mrbc 版・オプション・生成物 hash）を evidence に含める。

**A2. P3 の設計（文書 + 決裁）**
- system/user bytecode の区別、権限オブジェクトの生成・破棄・ID 再利用、特権 method の caller 検査、Task 操作の自己限定と system task 保護、watchdog kick、debug halt/release reboot の設計を `research/implementation/` に提案。
- 未決の判断は一つずつ選択肢つきで利用者に確認（api-contracts の方針どおり）。

**A3. P3 の実装（設計承認後）**
- caller 検査と拒否試験を host/Wasm で実装。watchdog kick と release reboot は BM 向け backend + host fake で実装し、実機検証は Phase B へ。

**A4. P5 の app 側実装（実機不要な部分）**
- `RBOS_XXXX` デバイス名の FICR DEVICEID 生成（多項式・seed・表記・長さ上限は利用者に決定を確認）。
- 広告の開始/停止/再開条件の実装。
- DLE/ATT MTU の設定値決定（候補と根拠を利用者に提示）。
- MCUmgr command 許可と retention clipboard の設計。

**A5. P6 の host 側**
- toolchain container の digest/配布元/利用条件の調査と採否提案。
- third-party notice と再配布条件の棚卸し。
- host での mrbc format・native 引数・権限・queue overflow 試験の拡充。

**A6. dependabot PR の棚卸し**
- #16/#18/#23 を `vendor-update` skill で個別評価し、採否を提案（pinned 版と差分の changelog・採否・回帰）。

### Phase B（利用者の DK 操作が必要）

**B1. P2 実機受け入れ**（p2-acceptance.md どおり）
- 事前に4つの許容区間（温度/DVDD/AVDD/VDD）を記録 → debug image の自己検査・Button 操作・3組以上の反復測定・`scheduler_probe` 3行・SD RAM log 照合 → `check-p2-log.py --limits`。
- ring 飽和の deterministic fixture、close/終了/再作成、stress image の5分 BLE 接続 + Button/ADC 並走。
- 完了時に checklist の空欄へ証拠を転記し retrospective-P2 を受け入れ完了へ更新。

**B2. P5 実機受け入れ**
- release 鍵で準備した DK の release image 起動、ERASE_NONE 更新、single-bank DFU E2E、誤署名・切断・電源断・容量超過、三つの起動入口、installer 更新、storage/peer data 保持、`RBOS_XXXX` 広告確認、DLE/MTU 実測。

**B3. P6 実機受け入れ**
- 長時間 BLE 接続・timer jitter・watchdog・DFU 電源断 fault injection、厳密な上限評価、保存データ保持検証。

### 推奨順序

1. A1（P4 host 側。小さく、P2 実機待ちの間に完了可能）
2. A2（P3 設計。決裁が続くため早めに開始）
3. A6（dependabot 棚卸し。放置中のため軽量に評価）
4. A3（P3 実装）→ A4（P5 app 側）
5. 利用者の DK 枠が取れた時点で B1（P2 実機受け入れ）— P2 完了が以降の信頼基盤
6. A5 → B2 → B3

根拠: B1 は利用者の時間を必要とする唯一のブロッキング項目で、早めにまとめて依頼する方が効率的。A2 は承認待ち時間を他作業で埋められる。P5 の app 側実装（A4）は B2 の前提。P4 の残りは host でほぼ完結し、完了すれば「段階完了」が一つ増やせる。

## 3. 利用者に確認したい決定事項

1. **次の着手先**: 上記推奨順序で進めるか、P2 実機受け入れ（B1）を優先して日程を決めるか。
2. **dependabot PR の扱い**: #16/#18/#23 を vendor-update 手順で評価・採否するか、現行固定版を維持して close するか。
3. **P3 の権限モデル方向**（設計着手時に個別確認予定）: VM 生成時に付与し破棄時に失効する権限オブジェクト方式が第一候補。
4. **P5 のデバイス名**: `RBOS_XXXX` の4桁生成規則（FICR DEVICEID 64-bit の畳み込み方法・表記）を P5 着手時に決裁。

## 4. 記録の注意点

- 実機項目は `real_hardware` として `implementation`/`host_wasm`/`bm_build` と分離して記録する（development-gates.md の四段階）。
- 標本値（pool 標本最大15452 B 等）を厳密な上限と呼ばない。
- 未検証事項を確認済みと書かない（AGENTS.md の完了報告基準）。

[調査索引へ戻る](../README.md)
