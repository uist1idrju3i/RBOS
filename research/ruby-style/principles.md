# Ruby らしさの根拠と RBOS での判断

本調査は後続の `ruby-idiomatic` skill の材料です。今回 skill・RuboCop・製品 API は追加しません。Ruby の思想、community の推奨、固定 mruby/c の制約、RBOS の設計判断を別々に扱います。

## 根拠の強さを分ける

| 根拠 | 読み取れること | 読み取れないこと |
|---|---|---|
| [Ruby 公式 About](https://www.ruby-lang.org/en/about/) | 自然さ、関数型と命令型のバランス、object・block・mixin を重視する設計 | 全 Ruby 実装で全機能が使えるという保証 |
| [Matz 本人の対談（2003）](https://www.artima.com/articles/the-philosophy-of-ruby) | 人間の負担、楽しさ、過度な直交性への留保、least surprise の文脈 | 全読者にとって驚きがないこと、短さだけを最大化すること |
| [Ruby 公式 syntax](https://docs.ruby-lang.org/en/master/syntax_rdoc.html) | CRuby の構文・意味の参照先 | mruby/c 互換性。master は可変であり固定実装の仕様ではない |
| [ruby-style-guide 固定版][guide] | 読みやすさと一貫性のための community 推奨 | 言語仕様、Ruby 作者の命令、全 community の総意 |
| [mruby/c 調査](../mrubyc/ruby-first-capabilities.md)・[今回の実行記録](capability-probes.md) | 固定 source と Wasm 構成での能力・差異 | nRF 実機性能、別構成、未試験の全構文 |

ruby-style-guide は rubocop/ruby-style-guide、commit `72ea4198d617e5c3db425cb3806b68b71dcc129f`（CC BY 3.0）を要約しました。文章・例の丸写しではありません。[ライセンス](../licenses.md)を参照してください。Ruby 公式ページ・対談は 2026-11-08 の参照で、Git commit 固定の資料とは区別します。

## 採用する考え方

1. **読み手に意図を伝える。** 「何をしたいか」を名前と構造で表し、処理の追跡に必要な状態を減らします。文字数や記号の多さを Ruby らしさの点数にしません。
2. **値と object の責任をそろえる。** sensor の電圧、pin の状態、通信 transaction など、利用者の語彙で method を設計します。native driver の全関数をそのまま Ruby へ写す方針ではありません。
3. **適切な抽象度を選ぶ。** collection の変換・選別は block で表現できますが、上限のある受信処理を無理に `map` にしません。副作用だけなら `each`、件数制御や割当て削減が必要なら `while` も選択肢です。速さの優劣は未計測です。
4. **暗黙の約束を増やしすぎない。** `?`、`!`、`nil`、単位、例外、buffer の所有者を API 契約にします。`0` は Ruby では真です。GPIO の整数を条件式へ直接渡さず、MPIG の `high?` 等で意図を表す設計が適します。
5. **実装の境界を隠しすぎない。** 単純に見える `read` でも待機・timeout・cancel・資源競合を定義します。Ruby の読みやすさと、組込み機器の時間・メモリ上限は両方必要です。

1 は公式 About・対談と guide の Introduction、3 は guide の Collections / Flow of Control を踏まえた判断です。2・4・5 の組込み向け具体化は RBOS の設計方針であり、Matz の発言とはしません。実行可能範囲は [対応表](idiom-compatibility.md)へ分離しています。

## 命名・書式・契約

| 項目 | guide の推奨と RBOS への適用 |
|---|---|
| 名前 | 変数・method は `snake_case`、class/module は `CamelCase`、定数は `SCREAMING_SNAKE_CASE`。短すぎる略語より役割を優先 |
| `?` | 真偽を問い合わせる名前。返り値の truthiness と厳密な bool を混同しない。MPIG の `high?` は bool 契約 |
| `!` | 安全な対となる method と比較して危険なものを示す慣習。全破壊的操作へ機械的に付ける規則ではなく、言語が挙動を強制する記号でもない |
| 書式 | 2 spaces、読みやすい空白、短い責任単位。小さくするためだけの一行 class、semicolon 連結、深い三項演算子は避ける |
| 引数 | 必須値は位置引数、意味の取り違えやすい選択肢は keyword を検討。MPIG の標準名・signature を書式好みで変更しない |
| 終了値 | 自然な最終式を利用し、早期終了や cleanup の制御には明示 `return`。`nil`、false、空 String、0 の区別を契約化 |
| コメント | コードの逐語訳ではなく、単位・上限・理由・外部制約を記す。RBOS の文章は日本語、コードコメントは英語。public API は引数、返り値、例外、待機を記載 |
| class/module | 最小の責任と明示的な依存を優先。mixin は共有する振る舞いのために使い、過度な継承・monkey patch・動的 method 生成を初期の標準にしない |

出典は guide の Naming Conventions、Methods、Classes & Modules、Comments、API Documentation です。コメント言語と最小責任の選択は RBOS の運用方針です。`private` を書けてもアクセス制御にはならないことは [privacy probe](capability-probes.md)と既存の [権限に関する制約](../mrubyc/ruby-first-capabilities.md)を参照してください。

## レビューの順序

まず仕様・入出力・失敗時の結果を確認し、その後に読みやすさ、mruby/c 互換性、task の進行、割当て・上限を見ます。可読性の修正で待機 semantics を変えたり、測定なしに block を全廃したりしません。C は共有 binding/backend の実装者が扱い、製品利用者は原則 Ruby と board 設定を書くという [Ruby-first 目標](../../README.md)を維持します。

[添付の主張の照合](attachment-review.md) / [組込み idiom](embedded-idioms.md) / [調査索引へ戻る](../README.md)

[guide]: https://github.com/rubocop/ruby-style-guide/blob/72ea4198d617e5c3db425cb3806b68b71dcc129f/README.adoc
