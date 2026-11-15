# vendor の正式 release 監視

mruby・mruby/c・sdk-nrf-bm を正式 release tag に固定し、週1回、新しい正式版を検出します。yomiyasu と GitHub Actions の更新検知は Dependabot を維持します。固定 SHA や submodule の shallow 設定は変更しません。

## ローカルで確認する

```sh
python3 tools/vendor-release-watch.py
python3 tools/vendor-release-watch.py --json vendor-releases.json
```

人が読む要約は標準エラー出力、JSON は標準出力に出します。`--json` は同じ JSON を指定ファイルにも保存します。submodule 本体の checkout は不要です。`.gitmodules` の path/URL と `git ls-tree HEAD` の gitlink SHA を読み、`git ls-remote --tags` の結果と照合します。作業中の submodule の HEAD ではなく、commit 済みの固定値が対象です。

正式版とみなす tag は次の形式だけです。GitHub Releases の公開フラグではなく tag 名で判定します。

| 依存 | tag の形式 |
|---|---|
| mruby | `X.Y.Z` |
| mruby/c | `releaseX.Y` または `releaseX.Y.Z` |
| sdk-nrf-bm | `vX.Y.Z` |

rc・pre 等は除外します。annotated tag は `^{}` の commit SHA、lightweight tag はその SHA と照合します。mruby/c の省略された patch は0として、整数の組で版を比較します。固定 SHA に正式版 tag がなければ終了値1です。通信失敗や tag 不正も「新版なし」とは扱いません。

## CI と issue 通知

`vendor-release-watch` workflow は毎週月曜03:23 UTC と `workflow_dispatch` で動きます。全3依存の固定値を検証できてから、新版の通知を行います。固定値の不正は workflow の失敗になります。

通知には `--update-issues`、`GITHUB_REPOSITORY`、`GITHUB_TOKEN` が必要です。workflow の権限は `contents: read` と `issues: write` のみです。

- 依存ごとの固定 title `依存更新: <name> の正式 release` で、open/closed の既存 issue を検索します。PR は対象外です。
- open issue は本文を更新し、同じ本文なら再書込みしません。closed issue は、本文の表に記録した最新 tag より新しい正式版が出たときだけ再開します。同じ版以下、または記録した版を読み取れない場合は、本文も状態も変更しません。
- 新版がなければ issue を作成・更新しません。既存 issue の自動 close もしません。
- schedule と手動実行は直列化し、同時実行による重複作成を防ぎます。

通知は更新の承認ではありません。変更履歴・互換性・ライセンス・回帰試験を評価し、人が採否を判断します。gitlink の更新や merge は自動化しません。
