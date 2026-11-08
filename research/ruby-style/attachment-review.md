# Ruby らしさに関する主張の照合

外部 AI の説明は調査の入口としてだけ使い、出典にはしませんでした。採否は一次資料・固定 guide・VM の実行結果で判断します。「未確認」は誤りと断定する意味ではありません。

| 主張の種類 | 判定と採用範囲 |
|---|---|
| 人間中心、programmer の楽しさ・負担軽減 | 採用。[Ruby 公式 About](https://www.ruby-lang.org/en/about/)と [Matz 対談](https://www.artima.com/articles/the-philosophy-of-ruby)に根拠。全員の好みが一致するとはしない |
| 自然さ、関数型と命令型のバランス | 採用。公式 About の説明。純粋関数型だけが Ruby らしい、とは読まない |
| 読みやすさ・一貫性を短さより優先 | guide の推奨として採用。高い「意味密度」の客観的尺度や、短いほど上級という主張は採用しない |
| block・map/select/reject/reduce が意図を示す | 意図の表現として採用。ただし固定 VM で reduce/inject は不可。明示 block を用いる対応表へ限定 |
| `&:active?` はそのまま使える | 不採用。Symbol#to_proc idiom は今回失敗。CRuby の一般例を mruby/c の保証へ移さない |
| guard clause、modifier if/unless、`||=` / `&&=`、safe navigation | guide と probe で限定採用。false の cache、複雑な modifier 条件、nil と失敗の混同に留保 |
| Ruby 3 で本格導入された `case ... in` | 条件付き。Ruby 2.7 で導入・3.0 で一部安定化した経緯は [公式 3.0 発表](https://www.ruby-lang.org/en/news/2020/12/25/ruby-3-0-0-released/)を参照。今回の array/hash 成功を全 pattern の互換性へ拡張しない |
| MINASWAN の標語がコードの読み手への配慮へ直接結びつく | 確認保留。標語と技術的要件は別。今回参照した一次資料では、この因果を支持する根拠を確認できず、必須コード規則へ転記しない |
| Larry Wall の三大美徳が Ruby community にも深く浸透している | 確認保留。Perl に由来する説明を、Ruby community の広い実態として転記する根拠を確認できない |
| RuboCop が広く普及し、layout 規則が読解速度を向上させる | guide と linter の関係だけ採用。[guide](https://github.com/rubocop/ruby-style-guide/blob/72ea4198d617e5c3db425cb3806b68b71dcc129f/README.adoc)は community guide。普及率・速度の定量的裏付けは未調査。公式の唯一の standard とも扱わず、今回は導入しない |
| snake_case / CamelCase / `?` / `!` | 慣習として採用。`!` は常に破壊的、すべての破壊的 method に必要、という一般化はしない |
| Principle of Least Surprise が Matz 自身の絶対原則 | 修正。対談で本人は、他者がそう呼び始めたことと、背景知識による驚きの差を説明。誰に対しても驚きゼロとは言っていない |
| Ruby の設計は過度な直交性を避ける | 採用。対談は過度な直交性を疑い、使いやすさとの選択を説明している。そこから導いた独自標語の実在まで保証しない |
| harmony / Okonomi が確立した厳密な Ruby 設計規約 | 不採用。この綴り・定義・帰属を確かめる一次根拠を今回確認できず、標語を追加しない |
| while の利用が極めて少ない、layout 規則で semicolon を無効化する | 頻度の根拠は未確認。guide の semicolon を避ける推奨と構文可否を区別する。while と semicolon を含む probe は実行できた |
| interface を先に考えるべきという特定人物の格言 | 帰属は不採用。今回確認できない引用を残さず、API 契約先行は RBOS の設計判断として記載 |
| Ruby の高階機能・mixin・例外を mruby/c にも適用する | 制限付きで採用。今回の狭い成功例と、未実装 opcode・visibility・closure lifetime の制約を併記 |

短い表現を禁止するのではなく、文脈・意味・実装を確かめずに権威づけしないのが結論です。参照した資料の版とライセンスは [原則](principles.md)、実行の反証例は [probe](capability-probes.md)に集約します。

[調査索引へ戻る](../README.md)
