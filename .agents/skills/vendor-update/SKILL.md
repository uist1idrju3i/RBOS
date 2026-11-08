---
name: vendor-update
description: RBOSの依存（vendor/のshallow submodule）を追加・更新し、変更履歴、採否、ライセンス、回帰を確認するときに使う。
---

# vendor-update（依存関係の更新）

application、library、依存を更新するときは、対象の変更履歴とライセンスを確認し、更新前後の結果を比べます。Dependabot は未導入なので、更新は手動で確認します。

## 対象と変更履歴の参照先

| 依存 | 現在値の確認方法 | 変更履歴の参照先 | 更新の検知 |
|---|---|---|---|
| yomiyasu | `git -C vendor/yomiyasu rev-parse HEAD` と `.gitmodules` | `nanaism/yomiyasu` の release と変更履歴 | 手動確認 |
| mrubyc | `git -C vendor/mrubyc rev-parse HEAD` と `.gitmodules` | `mrubyc/mrubyc` の release と変更履歴 | 手動確認 |
| sdk-nrf-bm | `git -C vendor/sdk-nrf-bm rev-parse HEAD` と `.gitmodules` | `nrfconnect/sdk-nrf-bm` の tag と west workspace の変更 | 手動確認 |
| sdk-mcuboot | `git -C vendor/sdk-mcuboot rev-parse HEAD` と `.gitmodules` | `nrfconnect/sdk-mcuboot` の tag（`ncs-v*`）と変更履歴 | 手動確認 |

新しい固定値を追加するときは、同じ PR で監視方法も決めます。

## 更新手順

1. 作業ブランチで、更新前の基準を記録します。`git submodule status`、関係するビルドやテストの結果、ライセンス表示を残します。
2. 更新前後のバージョンの間にある変更履歴をすべて読みます。履歴が shallow clone に含まれない場合は必要な範囲を fetch するか、upstream の compare/release ページで補います。`.gitmodules` の `shallow = true` は維持します。
3. 変更点を次の四つに分けて記録します。新機能、新しい option・設定項目、既定値の変更は採否と理由を判断します。役立つものは同じ変更で採用し、見送る場合は理由と再確認の条件を記録します。
   - 破壊的な変更と、こちらで必要な対応
   - セキュリティ修正と対象範囲
   - 新機能、新しい option・設定項目、既定値の変更と採否の理由
   - ライセンスまたはライセンス条件の変更
4. 更新します。submodule は `git -C vendor/<name> fetch --depth 1 origin <tag-or-commit>` の後に、peel した commit を checkout します。`.gitmodules` の shallow 設定を残します。
5. 更新後に回帰テストを行い、更新前の基準と比較します。現時点では `git submodule status`、`python3 .github/scripts/check-skills.py`、`python3 -m unittest discover -s tests/check-skills` を実行し、OS のビルドや実機検証がある場合はその結果も記録します。
6. PR 本文に、依存ごとの旧版 → 新版、変更履歴リンク、四分類の記録、新機能・option・設定項目・既定値の採否と理由、回帰テストの比較結果を記載します。結果を確認した後に人間がマージします。

## 更新を止める条件と完了の確認

- shallow clone で履歴が不足したら、対象の tag・commit の範囲だけ取得します。差分を読めない状態で「変更なし」としません。
- ライセンス根拠が得られない、vendor 内を直接編集する必要がある、設定差の理由を説明できない場合は、解決または未確認として報告するまで採用を確定しません。
- 完了時は、変更履歴の四分類、更新前後の `git submodule status`、実行した検査とログ、未検証の項目を分けて報告します。
