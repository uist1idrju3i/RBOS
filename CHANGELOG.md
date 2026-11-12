# 変更履歴

利用者に影響する変更を日本語で記録します。[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) と [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)に従います。RBOS の増分と公開手順は [semver skill](.agents/skills/semver/SKILL.md)を参照してください。

## [Unreleased]

### Added

- P2 の共通基盤として、native callback の引数・型・Integer 範囲・backend 失敗の helper と、借用値・生成値の返却処理を追加しました。16件の固定長 event ring は newest drop と pin ごとの Button coalesce を行い、stats に pending・overflow・coalesced を出します。実機の Button producer と Ruby への通知は未接続で、GPIO・温度 API の追加や P2 完了を意味しません。
- 実装計画の P5 に、BLE のデバイス名へシリアル番号由来の識別子を含める項目を追加しました。FICR の DEVICEID をもとに生成する方式で、OpenBlink の実装を参考に新規実装します。実装は未着手です。
- 実装計画の P2 にダイ温度読み出しを追加しました。nRF54L15 の TEMP ペリフェラルを backend にする新規実装で、OpenBlink の Zephyr sensor API 実装は流用しません。API の契約と実装は未着手です。
- 利用者の決定により、P1 の残る資源・進行・予約・SDH 項目は観測値で完了とし、厳密な上限と進行保証を P6、予約表と SD RAM/queue の照合を P2 へ移管しました。Mutex は Wasm 試験と採用規約で十分とし、DK fault 試験は行いません。公平性閾値は2倍を維持し、P5 の DLE/ATT MTU・DFU 速度の実機測定と、一時 overlay/CI image の比較手順を記録しました。
- DK の X/Y 比較で a/b 約1.006を確認し、利用者は周期の組合せに依存しない案 X を採用しました。VM quantum の既定を1 tick、service sleep を従来の10 msとし、比較専用 overlay と CI matrix は削除しました。host モデルは維持します。自己検査に同 priority worker の1秒間の進捗比2倍以内を追加しました。
- P1 closeout 向けに STRESS/OOM profile、常時 ready spinner、保持割当て fault task、四 variant の CI artifact、区間最大の `drain_us` を追加しました。利用者の決定で stress 条件を完全接続窓5分へ変更し、DK OOM/abort と X/Y 接続 stress を確認しました。新既定 image `ef8514585aa2` の DK 自己検査10項目と完全接続400.140059秒の stress も PASS し、承認済み closeout 条件に対して P1 完了と判定しました。最終 log と checker 出力全文を回帰 fixture として保存しました。
- BLE 応答修正後の DK log、checker 出力、CI image と production.hex の hash を記録しました。旧約40.1秒の切断周期は再観測されず、再接続と slow 広告の約180秒後停止も確認しました。前後比較から応答追加の効果と推定しますが、旧切断理由は未確定です。旧偏り log と X/Y log を fixture にし、現在は公平性2倍超を FAIL として検査します。
- 固定 mruby/c の Mutex owner 終了・ensure 解放・priority inversion・非 owner unlock の Wasm fault test と、pool 最小値の任意実行探索を追加しました。自己検査は Wasm 10 KiB で成功、9 KiB で OOM でした。Mutex 利用規約と P2/P3/P5/P6 の担当・検証条件は承認済みの方針として記録し、未実装の項目を区別しました。
- DK console log の自己検査・stress・OOM checker と、macOS の時間制限付き capture 手順を追加しました。BLE 境界を除いた統計、spinner、試験時間を判定します。capture は Linux PTY で検査し、macOS 実機では未確認です。
- P1 の CI debug image による利用者の DK 自己検査、BLE 接続・切断後の再広告、区間 tick 統計と stack/pool 観測値を記録しました。範囲 erase の通常更新と、未確認の ERASE_NONE・release 実機等を区別しています。
- BM firmware に mruby/c scheduler、BLE 広告、system task による保守処理と統計出力を追加しました。Ruby は build 時に vendor の mruby から作った mrbc で組み込み、P1 の scheduler self-test を実行します。
- nRF54L15 DK の S115・MCUboot 向けに、版 0.1.0 の最小 firmware を追加しました。UARTE に版を表示し、LED0 を点灯します。
- debug は SDK の開発用署名鍵を使い、release はリポジトリ外の署名鍵を必須とします。
- release の build は、MCUboot の既定鍵と公開鍵が同じ鍵を、ファイル名を変えていても拒否します。
- firmware の debug/release build を検査する CI と、Environment `release` の Secret で署名する手動 release workflow を追加しました。

### Fixed

- BLE の PHY・data length・ATT MTU 要求に SDK の connection-parameters library で応答し、未保存の system attributes を初期化します。切断 reason と手順の要求・結果を低頻度で記録し、pairing は非対応として応答します。修正後の DK では400秒超の接続中に切断なしを確認しました。
- stress checker の既定条件を spinner 負荷中の完全接続 stats 窓300秒にし、100万で巡回する counter の差分 rate、a/b 比と2倍超の偏りの FAIL を追加しました。利用者の stress/OOM capture を fixture と実機証拠に記録しました。vendor scheduler は変更していません。
- DK log checker は行中の boot marker も認識し、最後の boot だけを判定するようにしました。reset 前の旧 stats や時刻を混ぜず、除外行数と選択を NOTE で知らせます。実 OOM capture を回帰 fixture に追加しました。
- actionlint 設定に `ubuntu-26.04` を登録し、未知 runner の診断を ignore せず検査できるようにしました。P1 の CI 成功記録と build 容量の履歴も更新しました。
- P1 の tick 統計を区間ごとにリセットし、区間内の mruby/c tick 回数を表示するようにしました。生成 bytecode の形式検査と、P1 self-test・VM source の依存関係を CI に追加しました。
- CI artifact の保存が実装済みだった P0・P6 のチェックリストと振り返りを訂正しました。通常 CI の7日間の保存と、正式 release の証拠の長期保管を区別しました。
- nRF54L15-DK の準備手順に、利用者報告の初回 KMU 準備、通常更新、LED・console・loader 入口の実機結果を記録しました。BM workspace 内での build、macOS の VCOM 設定、正しい期待 log を追記しました。erase なしの初回準備と DFU 後の新 image 起動は未確認です。試験用 v0.1.1 は未 commit の写しで、公開版の追加ではありません。

[Unreleased]: https://github.com/uist1idrju3i/RBOS/commits/main/
