# 変更履歴

利用者に影響する変更を日本語で記録します。[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) と [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)に従います。RBOS の増分と公開手順は [semver skill](.agents/skills/semver/SKILL.md)を参照してください。

## [Unreleased]

### Added

- P1 closeout 向けに STRESS/OOM profile、二つの常時 ready spinner、保持割当て fault task、四 variant の CI artifact、区間最大の `drain_us` を追加しました。DK 30分 stress と OOM/abort は未実施です。
- 固定 mruby/c の Mutex owner 終了・ensure 解放・priority inversion・非 owner unlock の Wasm fault test と、pool 最小値の任意実行探索を追加しました。自己検査は Wasm 10 KiB で成功、9 KiB で OOM でした。Mutex 利用規約と P2/P3/P5/P6 の担当・検証条件は承認済みの方針として記録し、未実装の項目を区別しました。
- DK console log の自己検査・stress・OOM checker と、macOS の時間制限付き capture 手順を追加しました。BLE 境界を除いた統計、spinner、試験時間を判定します。capture は Linux PTY で検査し、macOS 実機では未確認です。
- P1 の CI debug image による利用者の DK 自己検査、BLE 接続・切断後の再広告、区間 tick 統計と stack/pool 観測値を記録しました。範囲 erase の通常更新と、未確認の ERASE_NONE・release 実機等を区別しています。
- BM firmware に mruby/c scheduler、BLE 広告、system task による保守処理と統計出力を追加しました。Ruby は build 時に vendor の mruby から作った mrbc で組み込み、P1 の scheduler self-test を実行します。
- nRF54L15 DK の S115・MCUboot 向けに、版 0.1.0 の最小 firmware を追加しました。UARTE に版を表示し、LED0 を点灯します。
- debug は SDK の開発用署名鍵を使い、release はリポジトリ外の署名鍵を必須とします。
- release の build は、MCUboot の既定鍵と公開鍵が同じ鍵を、ファイル名を変えていても拒否します。
- firmware の debug/release build を検査する CI と、Environment `release` の Secret で署名する手動 release workflow を追加しました。

### Fixed

- DK log checker は行中の boot marker も認識し、最後の boot だけを判定するようにしました。reset 前の旧 stats や時刻を混ぜず、除外行数と選択を NOTE で知らせます。実 OOM capture を回帰 fixture に追加しました。
- actionlint 設定に `ubuntu-26.04` を登録し、未知 runner の診断を ignore せず検査できるようにしました。P1 の CI 成功記録と build 容量の履歴も更新しました。
- P1 の tick 統計を区間ごとにリセットし、区間内の mruby/c tick 回数を表示するようにしました。生成 bytecode の形式検査と、P1 self-test・VM source の依存関係を CI に追加しました。
- CI artifact の保存が実装済みだった P0・P6 のチェックリストと振り返りを訂正しました。通常 CI の7日間の保存と、正式 release の証拠の長期保管を区別しました。
- nRF54L15-DK の準備手順に、利用者報告の初回 KMU 準備、通常更新、LED・console・loader 入口の実機結果を記録しました。BM workspace 内での build、macOS の VCOM 設定、正しい期待 log を追記しました。erase なしの初回準備と DFU 後の新 image 起動は未確認です。試験用 v0.1.1 は未 commit の写しで、公開版の追加ではありません。

[Unreleased]: https://github.com/uist1idrju3i/RBOS/commits/main/
