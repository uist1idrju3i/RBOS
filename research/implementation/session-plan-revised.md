> **履歴資料（2026-11-15）**: [出典セッション](https://app.devin.ai/sessions/3d2a42a786954ce0b1ee961cf57f4d57)の添付原報告です。以下は当時の主張・提案であり、現在の確認結果や承認ではありません。[再確認と訂正](session-plan-review.md)を先に読んでください。原文の誤り・未完の値も履歴として残しています。個人環境の絶対パスのみ `<checkout>/` に置換しました。今回の依頼は会話・ログ・報告の再確認と保存です。この写しでは新しい検証を行っていません。

> A7 の現在の承認済み設計と B-1/B-2 の手順は [A7 fixture](a7-fixtures.md)を参照してください。以下の提案・確認事項は当時の原文です。

# RBOS 実装状況の照合と今後の計画（2026-11-15 改訂）

対象: uist1idrju3i/RBOS main `243682c`（firmware 0.1.4+0）
照合方法: `research/implementation/porting-plan.md`・`checklist.md`・各 retrospective と、firmware/src・src/rbos・src/platform/nrf・tests・tools・CI の実態、最新 main の CI 結果を突き合わせました。本書は計画の共有用で、リポジトリへはコミットしません。

方針（利用者指示 2026-11-15）: 実機テストはまとめて実施する。手戻りが許容できる範囲で、エージェントが進められる実装を先行する。本書は次の三部構成です。

1. 現状の照合（短く）
2. 手戻り許容範囲の実装計画（エージェントのみで進行）
3. まとめて行う実機テストの手順と、ビルド済み image のチャット受け渡し

## 1. 現状の照合

| 段階 | 状態 | 残り |
|---|---|---|
| P0 | 完了 | 保存データ比較、`x-provision-keys`（erase なし初回準備）の2項目 |
| P1 | 完了（承認済み closeout） | 厳密上限→P6、予約表・SD RAM/queue→P2、release 実機・ERASE_NONE→P5 |
| P2 | コード実装完了・実機受け入れ未実施 | `real_hardware` 全項目（GPIO 電位、Button IRQ/飽和、温度実時間、ADC 精度、5分 stress、SD RAM/queue 余裕） |
| P3 | 未着手 | 権限モデル、caller 検査、system task 保護、watchdog、release reboot |
| P4 | 結合機構は実装済み、受け入れ条件は未検証 | RRAM 配置確認、RAM 個別計測、空/不正/OOM/String 不変の試験 |
| P5 | loader 統合・DK 入口確認済み | app 側: デバイス名、広告条件、DLE/MTU、鍵・ERASE_NONE・実機 DFU、MCUmgr 認証 |
| P6 | CI 基盤は存在 | container 決定、長時間 HIL、厳密上限、保存データ検証、notice |
| 横断 | — | dependabot 3件（#16 sdk-nrf-bm、#18 mrubyc、#23 mruby）の採否 |

## 2. 手戻り許容範囲の実装計画（Phase A）

基準: host/Wasm/build/CI で検証できる実装を先行し、実機でしか分からない部分（IRQ 実挙動・精度・BLE/tick・実時間）は Phase B でまとめて確認します。実機で不具合が出た場合の修正（手戻り）は許容とし、その分だけ実機枠を温めます。各項目は独立した PR とし、main への push ごとに四構成の evidence が CI に残るため、どの時点でも試験 image を切り出せます。

### A1. P4 受け入れの host/build 側（小・先行推奨）

- map で const blob の RRAM 配置と全体 RAM コピー不在を確認し、IREP/symbol/String/register の RAM を個別に計測して `research/implementation/` に記録。
- 空 Ruby・不正 RITE・OOM・task 作成失敗の host/Wasm 拒否試験と、String 変更で blob 不変の試験を追加。
- 生成物（入力 .rb・mrbc 版・オプション・hash）を evidence の対象へ追加。
- 手戻りリスク: 低。実機依存はなく、失敗しても host で再現・修正できる。

### A2. P3 設計（文書 + 決裁）

- `research/implementation/p3-design.md`（仮）に権限モデルを提案: VM 生成時に付与・破棄時に失効する権限オブジェクト、特権 method の caller 検査、`Task.create`/terminate/raise/priority=/suspend の自己限定、system task の保護、watchdog kick、debug halt/release reboot 経路。
- 未決の判断は一つずつ、選択肢・推奨・根拠を添えて利用者に確認します（api-contracts の方針どおり、まとめて投げません）。
- 手戻りリスク: 設計なので実機待ちなし。

### A3. P3 実装（A2 承認後）

- caller 検査と拒否試験を共有 binding + host/Wasm で実装。system task への `priority=` 等の拒否試験を在庫（api-contracts.json）に追加。
- watchdog kick（system task）と release reboot は BM backend + host fake で実装。実機の復旧確認は Phase B。
- 手戻りリスク: 中。mruby/c の Task API 挙動に依存するが、Wasm fault test の枠組みがある。

### A4. P5 の app 側実装（実機不要な部分）

- `RBOS_XXXX` デバイス名: FICR DEVICEID 64-bit から4桁を生成。多項式・seed・表記・長さ上限は利用者に決定を確認してから実装。
- 広告の開始・停止・再開条件を実装（DFU 入口・電力・復旧と整合させる設計を先に提示）。
- DLE/ATT MTU の設定値を候補と根拠つきで提示し、決定後に Kconfig/コードへ反映。
- MCUmgr の許可 command・retention clipboard の CRC/寿命の設計。
- 手戻りリスク: 中〜高。実機の BLE 交渉と広告挙動は Phase B で検証するため、修正前提で進める。

### A5. P6 の host 側

- toolchain container（配布元・digest・利用条件）の調査と採否の提案。
- third-party notice と再配布条件の棚卸し。
- host での mrbc format・native 引数・権限・queue overflow の試験拡充。
- 手戻りリスク: 低。

### A6. dependabot PR の棚卸し

- #16/#18/#23 を `vendor-update` skill の手順（changelog・採否・ライセンス・回帰）で個別評価し、採否を提案。現行固定版を維持する場合も明記して close 判断を仰ぐ。
- 手戻りリスク: 低。評価だけなら実機不要。

### A7. 実機試験 fixture の準備（Phase B の前提）

- ring 飽和を deterministic に作る fixture image: GPIOTE の timer 駆動 edge 生成 or GPIO 出力→入力配線の二案を設計し、安全な信号源として利用者と選ぶ。
- P5 データ保持試験: 更新前後で残すべきデータ（MCUboot/loader 設定、peer data、settings）の観測点を設計。必要なら試験用の最小 storage 書き込みを試験 image に入れる。
- P2 `check-p2-log.py` と fixture 側の診断行を fixture image 用に拡張。
- 手戻りリスク: 中。実機 fixture 自体が Phase B で初めて動く。

### Phase A の順序（推奨）

1. A1（P4 host 側）→ A2（P3 設計、決裁待ちを他作業で埋める）→ A6（dependabot 棚卸し）
2. A3（P3 実装）→ A4（P5 app 側）
3. A7（実機 fixture）を実機枠の直前に完了させる
4. A5 は空き時間で進める

## 3. まとめて行う実機テストの計画（Phase B）

Phase B は利用者の DK 作業枠に分割し、各枠で必要な image をあらかじめチャットで受け渡します。前提: VCOM 設定（JLinkExe `vcom enable` + Board Configurator VCOM0/1、115200 baud）、iOS ではなく Android の Device Manager を使う（iOS app の crash 既知）、`<SN>` は共有 log に書かない。

### B-1: P2 実機受け入れ（最優先）

必要 image: `debug`、`stress`（同一 commit の CI evidence、またはローカル build）

1. 試験前の記録: VDD 実測値・計測器・許容誤差・電源/負荷/室温 → `limits.json` に4区間を記入。
2. `debug` を `ERASE_RANGES_TOUCHED_BY_FIRMWARE` で program → reset → capture。
3. 自己検査全 PASS と `PASS: P2 native setup` を確認。LED0 点灯・`GPIO.read`/`write` の物理一致。
4. Button0..3 を押下・解放各100 ms超。`button index=… level=… count=…` を両レベルで確認。
5. 100巡回ごとの `temperature c=…`・`adc rail=… raw=… volts=…` を3組以上保存。
6. `scheduler_probe` 3行（payload 0/16/64 B）を保存。
7. `resources` と SD RAM log・生成 DTS・`.config`・map を照合。
8. `python3 tools/bm-build/check-dk-log.py debug.log --profile selftest --json` と `check-p2-log.py debug.log --limits limits.json --min-samples 3`。
9. IRQ・寿命: contract の Ruby 例を診断 task と置き換えた build で `45`/`"P1.13"`/`:sw0` の一致・二重 watch・close 後再設定・task 終了後の generation 抑止を確認。
10. ring 飽和 fixture image（A7）で newest drop・coalesce・最新 level・overflow/coalesced counter を確認。
11. `stress` image で完全接続窓5分 + Button 操作と反復 ADC/温度を並走 → `check-dk-log.py --profile stress --require-connected 300` + `check-p2-log.py`。
12. 完了時: checklist の空欄へ証拠を転記し、retrospective-P2 を受け入れ完了に更新する PR を出す。

所要目安: 半日（log 採取 + checker + 記録）。

### B-2: P5 実機受け入れ（A4 完了後）

必要 image: `debug`（DFU 試験用 app signed bin 含む）、`release`（firmware-release.yml、利用者の Environment secret）

1. `RBOS_XXXX` 広告名を nRF Connect で確認（複数台識別に使えるか記録）。
2. 広告の開始・停止・再開条件の実動作を確認。
3. debug app signed bin を BLE MCUmgr で upload → 転送・検証・起動（DLE/MTU 実測を記録）。
4. 誤署名・切断再開・容量超過・各 write 中の電源断を試す（fault injection）。
5. `ERASE_NONE` での更新を実機で検証。
6. release 鍵で準備した DK（または erase + KMU 再 provision）で release image の起動・通常更新を確認。
7. 三入口（BUTTON0+RESET、MCUmgr reset、retention）の動作確認。
8. storage/peer data が意図せず消えないことを確認（A7 の観測点）。
9. `x-provision-keys` の erase なし初回準備を別 DK/状態で確認できれば P0 の空欄も埋める。

所要目安: 1日（DFU 試行と fault injection が変動する）。

### B-3: P3 実機確認（B-2 と同じ枠で可）

- 認可拒否の実機動作（system task 保護・自己限定）、watchdog kick、release reboot 経路の確認。大部分は host/Wasm で済んでいるため、実機は最小の確認。

### B-4: P6 実機受け入れ（最後）

- 長時間 BLE 接続（目標は利用者と決める）、timer jitter、watchdog 復旧、保存データ保持の実機検証、厳密上限の評価。

### Phase B の依存関係

- B-1 は A7 の ring 飽和 fixture に依存（fixture なしでも B-1 の大半は実施可能だが、飽和項目は残る）。
- B-2 は A4（デバイス名・広告条件・DLE/MTU）に依存。
- B-3 は A3 に依存。
- どの枠も「main の安定 commit の CI evidence」か「実機枠向けに切った専用 build」で image を用意する。

## 4. ビルド済み image のチャット受け渡し計画

### 受け渡し単位

実機枠ごとに一つのメッセージへ以下をまとめて添付します。

| 添付物 | 用途 |
|---|---|
| `production.hex` | DK への書き込み対象（app + loader + SoftDevice 結合済み） |
| app の署名済み `*.bin`（DFU 枠のみ） | BLE MCUmgr upload 用 |
| `keyfile.json`（初回 provision が必要な場合のみ） | KMU への公開鍵 provision。debug 鍵由来であることを明記し、release image には流用しない |
| `SHA256SUMS`（evidence 由来） | 照合用 |

### メッセージに含める情報

- 対象 commit の SHA と image 版（VERSION と image の `X.Y.Z+TWEAK`）。
- 各 image の SHA-256 と照合方法（evidence の `SHA256SUMS` 全件照合か、chat 添付の個別 hash か）。
- 書き込みコマンドの雛形: `nrfutil device program --serial-number "<SN>" --firmware production.hex --options chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE` + `nrfutil device reset --serial-number "<SN>"`。
- 初回 provision が必要な場合だけ `x-provision-keys` の手順を分けて記載（`ERASE_ALL` は明示時のみ）。
- 注意: `<SN>`・秘密鍵・完全な device ID を共有 log に含めない。

### image の出所

- 原則として main commit の CI artifact（`firmware-evidence-<variant>-<sha>`）由来の `production.hex` を添付します。CI で build したものを受け渡すことで、evidence との hash 一致がそのまま照合になり、ローカル build との差異を排除します。
- CI artifact の保存期間は7日です。実機枠の直前に evidence をダウンロードして `production.hex` を取り出し、chat に添付します。期限切れの場合は同 commit の CI を再実行するか、ローカル build（hash 照合つき）で代替します。
- release image は `firmware-release.yml`（workflow_dispatch、Environment `release` の secret）でしか作らず、PR の一時試験鍵 build とは明確に区別します。

### ローカル build の扱い

- 実機 fixture（A7 の試験 image）など CI に無い派生 image はローカル build を添付し、SHA-256 と基準 commit・差分を明記します。ローカル build の hash は「試した image の識別情報」であり、再現性の証拠とは区別します（dk-provisioning.md の既存の扱いと同じ）。

## 5. 利用者に確認したい決定事項

1. Phase A の順序: 推奨（A1→A2→A6→A3→A4→A7→A5）で進めてよいか。
2. dependabot PR の採否: 評価して提案するか、固定版維持で close するか。
3. P5 デバイス名: `RBOS_XXXX` の4桁生成規則（A4 着手時に選択肢を提示）。
4. ring 飽和 fixture: timer 駆動 GPIOTE（配線不要）か GPIO 出力→入力配線か（A7 で提示）。
5. 実機枠の予定: B-1 の目安時期。fixture と image を揃える時点を合わせたい。

## 6. 記録の注意点

- 実機項目は `real_hardware` として `implementation`/`host_wasm`/`bm_build` と分離して記録します。
- 標本値を厳密な上限と呼びません。確認していないことを確認済みと書きません。
- 手戻りが発生した場合: 実機で見つかった問題は新しい修正 PR とし、受け入れ記録はその修正 image で取り直します。

[調査索引へ戻る](../README.md)
