# AGENTS.md

Devin / Codex / Claude Code など、このリポジトリで作業するすべての AI エージェントと人間が守るルールです。

## 1. main ブランチ

- GitHub のルールセットにより、`main` への直接 push、force push、削除、PR なしのマージは拒否されます。
- `<agent>/<short>` ブランチで作業し、PR を作成します。
- ルールセットは承認 0 件でのマージを許可するため、エージェントは PR をマージしません。
- ルールセットやブランチ保護を変更しません。
- 作業前に `git branch --show-current` を確認し、`main` では作業しません。
- 誤って `main` にコミットした場合は push も reset もせず、新しいブランチに移して報告します。

## 2. 言語と書式

- ドキュメント、Issue、Pull Request のタイトルと本文、コミットメッセージは日本語で書きます。コード、識別子、ファイル名は英語のままにします。
- 日本語の文章を書いたら、推敲スキル「yomiyasu」で読みやすさを整えてください（後述）。
- `docs/` は GitHub Pages で公開するサイト専用です。内部文書は `docs/` に置きません。内部文書が必要になった時点で、`README.md` や `RESEARCH.md` などの置き場を別途定め、`doc/` のような紛らわしい名前は使いません。

## 3. 外部リポジトリ（vendor/）

- `vendor/` の外部コードは shallow submodule として管理し、ファイルを直接編集しません。`.gitmodules` の `shallow = true` を維持します。
- submodule や依存を追加・更新するときは「vendor-update」スキルに従います。
- 上流への Issue・PR・push・コメントは人間の承認を得てから行います。

## 4. エージェントスキル

- リポジトリ固有のスキルは `.agents/skills/<name>/` に置きます。vendor 内のスキルはコピーせず、`.agents/skills/<name>` からのシンボリックリンクにします。
- Claude Code は `.claude/skills/` しか読まないため、`.claude/skills/<name>` → `../../.agents/skills/<name>` のリンクも必ず作ります。スキルを追加・改名・削除したら、リンクも同じ PR で直します。CI の `agent-docs` ワークフローがリンクの解決を検査します。Windows で clone するときは、シンボリックリンクを有効にします（`git config core.symlinks true` と、開発者モードか管理者権限）。
- 個人用の設定はコミットしません（`CLAUDE.local.md`、`.claude/settings.local.json`、`AGENTS.override.md` は gitignore 済み）。

| スキル | 使う場面 |
|---|---|
| `yomiyasu` | 日本語文書の推敲（`vendor/yomiyasu` へのリンク） |
| `vendor-update` | 依存関係の変更履歴、採否、ライセンス、回帰テストの確認 |
| `document-structure` | 文書の意味単位による分割、公開サイトと内部文書の区別、索引・旧リンク・証拠の保持 |

## 5. yomiyasu（日本語推敲スキル）

`vendor/yomiyasu` にある、AI が生成した日本語を読みやすく整えるスキルです。意味と条件を保ったまま、不自然な比喩、曖昧な主述関係、不要な装飾を直します。

- 呼び出し方: `/yomiyasu`、`$yomiyasu:yomiyasu`（Codex 系）、`yomiyasu:yomiyasu`（Claude Code）。依頼の文に「yomiyasu で」と書いても呼べます。
- 用途: 日本語のドキュメントや Issue・PR の説明文の推敲。
- 検査ツールは Python の標準ライブラリだけで動き、外部へ通信しません。
  - `python3 .agents/skills/yomiyasu/scripts/yomiyasu_lint.py <file>`: AI の文章に多い表現の候補を出します。
  - `python3 .agents/skills/yomiyasu/scripts/yomiyasu_check.py run --source <原文> --final <最終稿>`: 推敲の前後を比べ、数値・否定・主述が変わっていないかを確かめます。記録は git 最上位の `.yomiyasu/` に残ります（gitignore 済み）。
- 自動フックの `yomiyasu_hook.py` は各開発者の個人設定でだけ有効化し、リポジトリにはコミットしません。

## 6. 作業の進め方

- 自明でない作業は調査して深い計画を立ててから着手します。計画はリポジトリにコミットせず、チャットで共有します。
- 変更は小さく、主題ごとにまとめます。
- `docs/` は公開サイト専用です。公開サイトのファイル以外を置きません。
- 文書の根拠に、VM や個人環境のパスを書きません。リポジトリ内のファイル、CI の成果物、公開 URL を示します。
- 検証結果は、実行した commit、入力とバイナリ、変更した写しの範囲を示します。確認していないことを確認済みと書きません。
- 完了報告では、依頼と計画の各項目を変更・検証・未確認に照らし合わせます。CI の合否とログを確認し、未実施の試験を実施済みとは書きません。

## 7. 確認コマンド

```sh
git submodule update --init --depth 1   # submodule の取得
python3 .github/scripts/check-skills.py  # 指示とスキルの一覧・名前・リンクを検査
python3 -m unittest discover -s tests/check-skills  # スキル検査のテスト
tools/mrubyc-wasm/check.sh              # emsdk 環境で Ruby compile・Wasm smoke test
python3 .agents/skills/yomiyasu/scripts/yomiyasu_lint.py <file>  # 日本語文書の候補検査
python3 -m json.tool .devin/wiki.json >/dev/null  # DeepWiki 設定の JSON 検査
git diff --check                        # 空白エラーの検査
```

変更した対象の検査を実行します。コマンドが成功することと、意味・見え方・実機動作の確認は区別します。
