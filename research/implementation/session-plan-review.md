# 2026-11-15 実装状況と計画の再確認

**未承認の提案の保存です。実装開始の承認でも、新しい決定でもありません。**

[調査索引](../README.md) / [初版の写し](session-plan-initial.md) / [改訂版の写し](session-plan-revised.md)

## 依頼・経緯・今回の範囲

[出典セッション B](https://app.devin.ai/sessions/3d2a42a786954ce0b1ee961cf57f4d57)は、2026-11-15 に全体計画と実装状況を照合し、今後の計画を作る依頼で始まりました。利用者は初版への回答で「まだ実装には進まず、計画の内容を調整して」を選び、その後「実機テストはある程度をまとめて実施」「手戻りが許容できる範囲で進められる実装」「実機のステップバイステップ計画」「ビルド済み image のチャット受け渡し」を求めました。

改訂版への回答も「このセッションでは深い計画を作成するまでで良いです。」です。最後の `sleep` は実装承認ではありません。原報告の「エージェントのみで進行」は、承認後に実施する作業の分担案として読みます。セッションは計画作成で終了し、五つの決定事項は未決です。

今回の再確認日も 2026-11-15。基準 RBOS は元の計画と同じ `243682c0313d7cedbd86e6d5a35260430452871c`、VERSION は `0.1.4`、image は `0.1.4+0`。会話・回答・shell 記録・初版/改訂版を照合しました。入力の全957イベント（A）/433イベント（B）は構文解析できました。原報告の数値や方式は[ZMS の訂正](../dfu/zms-direct-execution.md)と[圧縮の再測定](../mrubyc/bytecode-compression.md)へ分けています。

履歴の会話と実作業の shell 記録は[セッション証拠](session-evidence.json)に保存しました。これは会話・実行コマンド・結果の抽出であり、イベント全件の生 dump ではありません。内部の思考、通知・利用量・他 repository の初期設定、利用者識別情報は保存対象から除外し、個人環境のパスは置換しました。原添付3件は上記2件と[ZMS 原報告](../dfu/zms-session-original.md)として保持し、本文を現在の知識で書き換えず訂正文を分けました。

## P0〜P6 の照合結果

| 段階 | 今回の判定 | 根拠と留保 |
|---|---|---|
| P0 | 受け入れ判定は完了、全 checklist 完了ではない | [P0 振り返りの実機結果](retrospective-P0.md#実機結果2026-11-09-jst利用者報告)。保存データ保持・erase なし初回準備は未確認。初期節の「未完了」だけを現状と読まない |
| P1 | 承認済み closeout | [最終 DK 確認](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)。400.140059秒の完全接続窓を含む利用者証拠あり。厳密上限は P6、予約/queue は P2、release/ERASE_NONE は P5 に残る |
| P2 | 対象 binding/backend と host/Wasm/build の証拠あり、実機未受け入れ | [P2 振り返り](retrospective-P2.md)と[checklist](checklist.md)。GPIO/Button、温度、三電源 ADC が対象。「コード実装完了」は全 MPIG API 完了の意味ではない |
| P3 | 未完了 | checklist の権限・Task 自己限定・watchdog・release reboot が空欄。既存 system task の登録自体を「未着手」とするのは広すぎる。信頼境界の受け入れが未着手 |
| P4 | 結合機構あり、受け入れ未完了 | `firmware/cmake/mrubyc.cmake` が const 配列と task table を生成し `firmware/src/main.c:29-31` が task を生成。[旧調査](../dfu/embedded-bytecode.md)の「build target はまだない」は歴史的記述。配置・RAM 内訳・空/不正/OOM/String 不変は checklist で未受け入れ |
| P5 | loader 統合と一部入口の利用者証拠あり | [DK 準備](dk-provisioning.md)と checklist。新 image の BLE 更新・release 実機・ERASE_NONE・復旧・データ保持・認証までの完了ではない |
| P6 | CI 基盤の一部あり | checklist の Wasm CI と artifact 保存は完了、container digest・長時間 HIL・厳密上限・notice は未完了。通常 artifact 7日を長期公開保管と混同しない |

原報告の状態表は概ね checklist と整合しますが、「完了」は受け入れ範囲に限り、既存機構と今後の条件を分けました。今回 firmware を再 build したり、元の CI の成功を再実行で確認したわけではありません。過去の CI はセッションログに記録された観測で、現在の検査結果は本変更の検査と別です。

dependabot は shell の `gh pr view` が環境で禁止されていたため、組込み `git_view_pr` で代替しました。2026-11-15 の再確認では [#16 sdk-nrf-bm](https://github.com/uist1idrju3i/RBOS/pull/16)、[#18 mrubyc](https://github.com/uist1idrju3i/RBOS/pull/18)、[#23 mruby](https://github.com/uist1idrju3i/RBOS/pull/23) はいずれも **open**。採否、changelog 全件評価、更新、close は行っていません。

## 初版から改訂版への変更

初版の現状照合と A1〜A6 を土台に、改訂版は実機 fixture の A7、Phase A の依存順、B-1〜B-4 の実機枠、image の受け渡しと出所・hash・初回準備の区別を具体化しました。添付初版を削除せず、改訂版を当時の最終提案として残します。文字化けした「添付��ます」は履歴に残っていますが、意図は image を chat に添付する提案です。

## Phase A: 承認後に先行できる作業案

| 作業 | 内容・検査 | 条件・手戻り |
|---|---|---|
| A1: P4 host/build | RRAM 配置・全体 RAM コピー不在、IREP/symbol/String/register の個別計測、空/不正/OOM/task 生成失敗、String 変更時 blob 不変、入力/compiler/options/hash の証拠 | 比較的低い。map だけを実行時寿命の証明にしない |
| A2: P3 設計 | VM 生成時付与/破棄時失効、caller 認可、Task 操作の自己限定、system 保護、watchdog/debug halt/release reboot を提案 | 決裁前に public 契約を確定しない |
| A3: P3 実装 | A2 承認後に共有 binding と host/Wasm の拒否試験、backend/fake、在庫へ追記 | 中。実機の復旧確認は B-3 |
| A4: P5 app | DEVICEID 由来 `RBOS_XXXX`、広告条件、DLE/MTU、MCUmgr 許可 command、retention CRC/寿命 | 規則・値の承認後。中〜高、実際の BLE 交渉は B-2 |
| A5: P6 host | container 出所/digest/条件、notice、format/引数/権限/overflow の試験 | 低。ただし採否は提案する |
| A6: 依存評価 | 3 PR を vendor-update に従い履歴・採否・license・回帰で個別評価 | 更新・close は別判断 |
| A7: fixture | timer/GPIOTE と外部配線案、保持するデータと観測点、diagnostic/checker の整合 | 中。ring 飽和と安全な信号源は実機で初確認 |

推奨順は **A1→A2→A6→A3→A4→A7→A5**。A3 は A2 の承認待ち、A7 は実機枠直前、A5 は並行可能という提案です。原報告の「main push ごとに四構成」は、PR と CI の成功を前提とする成果物取得案で、CI 実行だけで実機欄は完了しません。

## Phase B: まとめて実施する実機計画案

前提は利用者の flash 承認、同一 SHA の image、VCOM0/1・115200 baud、伏せた `<SN>`、Android Device Manager です。iOS crash は過去の利用者観測であり、全版共通の保証ではありません。以下は未実施です。詳細とコマンドは[改訂版](session-plan-revised.md)および現行の[P2 受け入れ手順](p2-acceptance.md)を併読します。

### B-1: P2（最優先、半日は原報告の見積り）

1. VDD 実測・計測器・許容誤差・電源/負荷/室温を記録し、測定前に `limits.json` の4区間を定める。
2. 同一 commit の debug を範囲 erase で program/reset/capture する。自己検査全 PASS と P2 native setup、LED0、GPIO の物理値を確認する。
3. Button0〜3 の押下/解放を各100 ms超で行い、両レベルの index/level/count を残す。
4. 100巡回ごとの温度・三電源 ADC を3組以上、scheduler_probe の0/16/64 Bを保存する。
5. resources/SD RAM と DTS・config・map を照合し、`check-dk-log.py --profile selftest --json` と `check-p2-log.py --limits limits.json --min-samples 3` を実行する。
6. 契約の診断 image で pin 表現の一致、二重 watch、close 再設定、task 終了後 generation 抑止を検査する。A7 の fixture で飽和と overflow/drop/coalesce を検査する。
7. stress で完全接続窓5分と Button/ADC/温度を並走し、`--profile stress --require-connected 300` と P2 checker を実行する。総 log 長を接続窓の代わりにしない。
8. 条件を満たした項目だけ証拠付きで checklist/retrospective に追記する。fixture がなければ飽和項目は未完了のままにする。

### B-2〜B-4: 更新・回復・長時間

1. **B-2（A4後、1日は見積り）**: debug と正式 release、DFU 用 signed bin を準備。広告名/開始停止再開、BLE upload→検証→新 image 起動、DLE/MTU を記録する。
2. 切断再開・誤署名・容量超過・各 write の電源断、ERASE_NONE、release 鍵での起動/通常更新、BUTTON0+RESET/MCUmgr/retention の入口を確認する。危険な操作は復旧手順と明示承認を先に揃える。
3. storage/peer data は A7 の観測点で前後比較する。bonding を採用した意味ではない。erase なし `x-provision-keys` は別 DK/状態の準備ができた場合に分けて試す。
4. **B-3（A3後、B-2と同枠可）**: system 保護/自己限定の拒否、watchdog kick と回復、release reboot を確認する。原報告の「大部分はhostで済んでいる」は将来の前提で、現時点の実績ではない。
5. **B-4（最後）**: 利用者と長さを決めた BLE 長時間接続、jitter、watchdog、保持、厳密上限を評価する。標本最大を厳密上限とは呼ばない。

不具合時は修正 PR と修正版 image で該当受け入れを取り直す方針案です。

## image のチャット受け渡し案

- 枠ごとに必要な image、基準 SHA、VERSION と image version、variant、SHA-256、対応する evidence と試験項目をチャットへ添える。通常は main CI の `firmware-evidence-<variant>-<sha>` 内の `production.hex` を取り出す。
- artifact の `SHA256SUMS` と添付 image を照合し、flash コマンドは `nrfutil device program --serial-number "<SN>" --firmware production.hex --options chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE` と reset を別に示す。ERASE_NONE 試験ではその条件を明記し、範囲 erase の成功で代用しない。
- 通常 CI artifact は7日。枠の直前に取得する。期限切れなら同 SHA の再実行または基準/差分付きローカル build を区別する。hash は image の識別であって再現 build 一致の証明ではない。
- 正式 release は `firmware-release.yml` と Environment `release` の署名経路を使う。一時試験鍵の PR image と混同しない。初回 provision と通常更新を分け、ERASE_ALL は明示時のみ。秘密鍵・完全な DEVICEID・SN を共有 log に含めない。
- fixture の派生 image は基準 SHA・変更範囲・入力・binary hash を添える。今回 image は作成・添付していない。

## 未決の五項目

1. Phase A の推奨順序で進めてよいか。
2. dependabot を評価して採否を提案するか、固定維持で close を判断するか。
3. `RBOS_XXXX` の4桁生成規則。
4. ring 飽和 fixture を timer/GPIOTE か GPIO 配線にするか。
5. B-1 の実機枠の予定。

会話にはこれらの承認はありません。今回は保存だけを行い、決定事項表・checklist の印・依存版・実装は変えていません。
