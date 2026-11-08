# RBOS

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/uist1idrju3i/RBOS)

## 概要

RBOS は Ruby のバイトコードを実行する組み込み OS を目指すプロジェクトです。
mruby/c の VM と rrt0 task scheduler を中核に、Nordic nRF54L15-DK 上で動く構成を検討しています。

## 現状

**研究段階であり、RBOS の実装はまだありません。**
SDK のビルド、実機動作、DFU、性能・消費電力は本リポジトリでは未検証です。
調査済みの仕様、設計案、未確認事項を [research/README.md](research/README.md) に分けて記録しています。

## 目標/特徴

- mruby/c の task 機能を使った Ruby プログラムのマルチタスク実行。
- C の native class を介した周辺機器へのアクセス。
- 信頼された system task と user task の権限分離。
- NCS Bare Metal、MCUboot、BLE MCUmgr による **single-bank DFU**。
- mruby 4.0.0 の mrbc で生成した const bytecode の firmware 結合と RRAM からの実行。
- OpenBlink 対応は将来計画。初期の bytecode 更新は firmware DFU のみ。

いずれも目標・採用方針です。firmware A/B と bytecode A/B は採用しません。
根拠と制約は [判断記録](research/architecture/decisions.md)を参照してください。

## 対象ハードウェア

対象は Nordic Semiconductor **nRF54L15-DK** です。
主 target は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` を予定しています。
central は使わないため SoftDevice は **S115 に固定**します。
工事設計認証番号 `220-JP8930` は総務省の DB で nRF54L15 DK の1件と照合しました（2026-11-08）。[照合結果と確認範囲](research/hardware/nrf54l15-dk.md)を参照してください。RBOS 全体の認証や任意の無線設定の適法性を保証するものではありません。
出典、GPIO、書き込み上の注意は [ボード調査](research/hardware/nrf54l15-dk.md)にまとめています。

## アーキテクチャ概要

MCUboot が main application または独立した BLE firmware loader を起動する構成です。
main application は Bare Metal 上の mruby/c VM、HAL、native class と Ruby task から成ります。
slot1 は firmware loader 用で、旧 main application を保持する A/B slot ではありません。
メモリマップと根拠は [構成概要](research/architecture/overview.md)を参照してください。

## リポジトリ構成

| 場所 | 内容 |
|---|---|
| `research/` | 実装準備の調査・判断・未確認事項 |
| `tools/mrubyc-wasm/` | host mrbc と emscripten HAL の共通検査スクリプト |
| `tests/mruby/` | task・Mutex・例外の Ruby smoke test |
| `vendor/` | shallow submodule で固定した外部資材 |
| `.agents/skills/` | 開発支援スキル |
| `.github/`、`tests/check-skills/` | skill の一覧とリンクを検査する CI・テスト |

submodule の URL は [.gitmodules](.gitmodules) に記録しています。

| submodule | 上流 | 主なライセンス |
|---|---|---|
| `vendor/mrubyc` | [mrubyc/mrubyc](https://github.com/mrubyc/mrubyc) | BSD-3-Clause |
| `vendor/sdk-nrf-bm` | [nrfconnect/sdk-nrf-bm](https://github.com/nrfconnect/sdk-nrf-bm) | LicenseRef-Nordic-5-Clause |
| `vendor/mruby` | [mruby/mruby](https://github.com/mruby/mruby)（4.0.0、host mrbc） | MIT |
| `vendor/yomiyasu` | [nanaism/yomiyasu](https://github.com/nanaism/yomiyasu) | MIT |

MCUboot は独立 vendor ではなく、sdk-nrf-bm の west manifest が import する NCS の依存として取得します。

版とライセンスの根拠は [調査索引](research/README.md)と [ライセンス調査](research/licenses.md)を参照してください。

## 取得方法

```sh
git clone --recurse-submodules --shallow-submodules https://github.com/uist1idrju3i/RBOS.git
cd RBOS
```

取得済みの checkout で submodule を初期化する場合:

```sh
git submodule update --init --depth 1
```

RBOS のビルド手順は未整備です。SDK の環境構築案は [SDK 調査](research/nrf-bm/setup-and-build.md)にありますが、動作確認済みの RBOS 手順ではありません。

## ドキュメント

- [公開サイト](https://uist1idrju3i.github.io/RBOS/)（Pages 有効化後に利用可能）。公開用ファイルは [docs/](docs/) にあります。Settings → Pages で Deploy from a branch、main /docs を指定します。

- [調査索引・固定版・判断履歴](research/README.md)
- [段階的な移植計画](research/implementation/porting-plan.md)
- [実装前チェックリスト](research/implementation/checklist.md)
- [開発ルール](AGENTS.md)

## 開発への参加

まず [AGENTS.md](AGENTS.md) を確認してください。
文書、Issue、PR、コミットは日本語、識別子とソースコード中のコメントは英語で記述します。
main に直接 push せず、作業ブランチから PR を作ります。vendor のファイルは直接編集しません。
仕様の提案では、根拠となる固定版、確認した範囲、未検証の事項を併記してください。

## 開発 / CI

mruby/c が scheduler を担い、製品開発者は Ruby を主に書いて RBOS を使えることを目指します。通常は C の編集を不要にし、DeviceTree などで board を設定する方針です。API を追加する RBOS 開発者は [Ruby API 追加手順](.agents/skills/ruby-api-binding/SKILL.md)を参照してください。

製品 Ruby の書き方は [ruby-idiomatic](.agents/skills/ruby-idiomatic/SKILL.md)、周辺機器 API の契約は [io-api-guideline](.agents/skills/io-api-guideline/SKILL.md)、版と公開準備は [semver](.agents/skills/semver/SKILL.md)にまとめています。利用者向けの変更は [CHANGELOG](CHANGELOG.md)に記録します。

`mruby-wasm` CI は mruby 4.0.0 の mrbc で smoke scripts と将来の `src/**/*.rb` を compile し、smoke scripts を mruby/c の emscripten HAL で実行します。未捕捉例外の検出も検査します。
emsdk 6.0.12 の環境を読み込めば、ローカルでも `tools/mrubyc-wasm/check.sh` を実行できます。必要なツール・試験範囲は [検査手順](tools/mrubyc-wasm/README.md)を参照してください。
Nordic の実機動作を検証する CI ではありません。

## ライセンス

RBOS は [BSD-3-Clause](LICENSE) です。
外部資材にはそれぞれのライセンスが適用され、RBOS のライセンスで一括して再許諾するものではありません。
Nordic 向け利用条件、著作権表示、第三者コードの扱いは [ライセンス調査](research/licenses.md)と各資材の原文を確認してください。
