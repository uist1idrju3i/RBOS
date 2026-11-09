# 変更履歴

利用者に影響する変更を日本語で記録します。[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) と [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)に従います。RBOS の増分と公開手順は [semver skill](.agents/skills/semver/SKILL.md)を参照してください。

## [Unreleased]

### Added

- nRF54L15 DK の S115・MCUboot 向けに、版 0.1.0 の最小 firmware を追加しました。UARTE に版を表示し、LED0 を点灯します。
- debug は SDK の開発用署名鍵を使い、release はリポジトリ外の署名鍵を必須とします。
- release の build は、MCUboot の既定鍵と公開鍵が同じ鍵を、ファイル名を変えていても拒否します。
- firmware の debug/release build を検査する CI と、Environment `release` の Secret で署名する手動 release workflow を追加しました。

### Fixed

- CI artifact の保存が実装済みだった P0・P6 のチェックリストと振り返りを訂正しました。通常 CI の7日間の保存と、正式 release の証拠の長期保管を区別しました。
- nRF54L15-DK の準備手順に、利用者報告の初回 KMU 準備、通常更新、LED・console・loader 入口の実機結果を記録しました。BM workspace 内での build、macOS の VCOM 設定、正しい期待 log を追記しました。erase なしの初回準備と DFU 後の新 image 起動は未確認です。試験用 v0.1.1 は未 commit の写しで、公開版の追加ではありません。

[Unreleased]: https://github.com/uist1idrju3i/RBOS/commits/main/
