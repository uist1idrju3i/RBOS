---
layout: page
title: 開発・参加
---
{% include nav.html %}

## 開発方針

文書、Issue、PR、コミットは日本語で書きます。識別子、ファイル名、コード中のコメントは英語です。main へ直接 push せず、作業ブランチから PR を作ります。vendor は固定した submodule として扱い、直接編集しません。

参加前に [AGENTS.md](https://github.com/uist1idrju3i/RBOS/blob/main/AGENTS.md) と [調査索引](https://github.com/uist1idrju3i/RBOS/blob/main/research/README.md)を確認してください。提案では採用方針、調査した版、試験した範囲と未確認の項目を分けて示します。

## Ruby を Wasm で検査する

mruby-wasm CI は、固定した mruby 4.0.0 の mrbc と mruby/c の emscripten HAL を使います。複数 task、sleep_ms、priority、pass、Mutex、join/value、例外を smoke test で実行します。未捕捉例外や読み込み失敗を成功扱いしないことも確認します。

emsdk 6.0.12 の環境と必要な host tools を用意し、RBOS のルートで実行します。

```sh
git submodule update --init --depth 1 vendor/mruby vendor/mrubyc
tools/mrubyc-wasm/check.sh
```

`tests/mruby/` は実行試験、将来の `src/**/*.rb` は compile 検査の対象です。Wasm で nRF の IRQ・BLE・消費電力を再現するものではありません。セットアップと試験範囲は [検査手順](https://github.com/uist1idrju3i/RBOS/blob/main/tools/mrubyc-wasm/README.md)を参照してください。

## Ruby class・method を追加する

製品開発者の Ruby を支える API は、RBOS 開発者が共有 C binding に一度だけ実装する方針です。登録入口は `rbos_define_classes(backend)`、共有実装は `src/rbos/`、backend の契約は `include/rbos/backend.h` に置きます。Wasm は fake backend、将来の nRF build は実機 backend を使います。現在の登録処理は空で、device operation はまだありません。

引数・型・範囲、値の所有権、エラーと例外、特権操作の caller 検査を揃え、Ruby から試験します。新しい script は compile だけでなく、実行対象への追加も必要です。

- [Ruby API 追加 skill](https://github.com/uist1idrju3i/RBOS/blob/main/.agents/skills/ruby-api-binding/SKILL.md)
- [製品 Ruby の書き方 ruby-idiomatic](https://github.com/uist1idrju3i/RBOS/blob/main/.agents/skills/ruby-idiomatic/SKILL.md)
- [周辺機器の契約 io-api-guideline](https://github.com/uist1idrju3i/RBOS/blob/main/.agents/skills/io-api-guideline/SKILL.md)
- [版と公開準備 semver](https://github.com/uist1idrju3i/RBOS/blob/main/.agents/skills/semver/SKILL.md)
- [利用者向けの変更履歴](https://github.com/uist1idrju3i/RBOS/blob/main/CHANGELOG.md)
- [C と Ruby の値・所有権](https://github.com/uist1idrju3i/RBOS/blob/main/research/mrubyc/c-api.md)
- [共有の登録入口](https://github.com/uist1idrju3i/RBOS/blob/main/src/rbos/bindings.c)

## ライセンス

RBOS 本体と mruby/c は BSD-3-Clause、host compiler の mruby は MIT、sdk-nrf-bm は LicenseRef-Nordic-5-Clause、MCUboot は Apache-2.0 です。RBOS のライセンスで依存先の条件を置き換えることはできません。Nordic の IC に関する利用条件、著作権表示、再配布条件を確認してください。

原文と依存関係ごとの注意点は [ライセンス調査](https://github.com/uist1idrju3i/RBOS/blob/main/research/licenses.md) と [RBOS LICENSE](https://github.com/uist1idrju3i/RBOS/blob/main/LICENSE)にあります。

## このサイトの公開

公開ファイルは `docs/` にあります。GitHub の Settings → Pages で **Deploy from a branch / main /docs** を選ぶと、組み込み Jekyll で公開できます。Pages の有効化は管理者が行います。独自の deploy workflow、Wasm、browser playground はこのサイトに含めていません。
