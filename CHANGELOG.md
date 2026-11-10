# 変更履歴

利用者に影響する変更を日本語で記録します。[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) と [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)に従います。RBOS の増分と公開手順は [semver skill](.agents/skills/semver/SKILL.md)を参照してください。

## [Unreleased]

### Added

- P1 の30分 DK 負荷試験と OOM/abort 試験に向け、STRESS/OOM profile、自己検査後の常時 ready spinner、保持割当て fault task、CI artifact を追加しました。統計の末尾には区間内の BM scheduler drain 最大経過時間を出力します。実機試験の完了記録ではありません。
- P1 の CI debug image による利用者の DK 自己検査、BLE 接続・切断後の再広告、区間 tick 統計と stack/pool 観測値を記録しました。範囲 erase の通常更新と、未確認の ERASE_NONE・release 実機等を区別しています。
- BM firmware に mruby/c scheduler、BLE 広告、system task による保守処理と統計出力を追加しました。Ruby は build 時に vendor の mruby から作った mrbc で組み込み、P1 の scheduler self-test を実行します。
- nRF54L15 DK の S115・MCUboot 向けに、版 0.1.0 の最小 firmware を追加しました。UARTE に版を表示し、LED0 を点灯します。
- debug は SDK の開発用署名鍵を使い、release はリポジトリ外の署名鍵を必須とします。
- release の build は、MCUboot の既定鍵と公開鍵が同じ鍵を、ファイル名を変えていても拒否します。
- firmware の debug/release build を検査する CI と、Environment `release` の Secret で署名する手動 release workflow を追加しました。

### Fixed

- P1 の tick 統計を区間ごとにリセットし、区間内の mruby/c tick 回数を表示するようにしました。生成 bytecode の形式検査と、P1 self-test・VM source の依存関係を CI に追加しました。
- CI artifact の保存が実装済みだった P0・P6 のチェックリストと振り返りを訂正しました。通常 CI の7日間の保存と、正式 release の証拠の長期保管を区別しました。
- nRF54L15-DK の準備手順に、利用者報告の初回 KMU 準備、通常更新、LED・console・loader 入口の実機結果を記録しました。BM workspace 内での build、macOS の VCOM 設定、正しい期待 log を追記しました。erase なしの初回準備と DFU 後の新 image 起動は未確認です。試験用 v0.1.1 は未 commit の写しで、公開版の追加ではありません。

[Unreleased]: https://github.com/uist1idrju3i/RBOS/commits/main/
