# style-guide と固定 mruby/c の対応

対象は [原則と固定資料](principles.md)、mruby 4.0.0 compiler と mruby/c `434bccd6…` の既存 Wasm runner です。**OK は表に挙げた入力だけの成功**、差異は CRuby の慣用句をそのまま移せないもの、不可は当該構成での失敗です。一般的な互換保証ではありません。ID はすべて [実行結果・入力・hash](capability-probes.md)へ対応します。

## 言語・collection の idiom

| guide の節 / idiom | 判定・根拠 ID | RBOS での使い分け・代替 |
|---|---|---|
| Source Code Layout / Naming Conventions | OK: `names`、`strings` の名前・indent・構文 | 2 spaces、snake_case、CamelCase。probe の compact な記録形式を製品の書式例にしない |
| Flow of Control / guard clause・modifier if/unless | OK: `guard-case` | 早期終了で通常系の入れ子を減らす。複雑な条件や複数行処理は通常の if |
| case/when・while・times | OK: `guard-case`、`bounded-loop` | 値の分岐と件数制御を明示。無限 loop には別途 yield/待機が必要 |
| Assignment & Comparison / `||=`、`&&=` | OK、意味に注意: `truth-memo` | `||=` は false も置換。false を cache するなら `nil?` で未設定を識別。0・空 String・空 Array は真 |
| safe navigation `&.` | OK: `safe-nav` | nil receiver の短絡。false を nil と同一扱いしない。未定義 method・driver エラーを消す構文ではない |
| Blocks, Procs & Lambdas / `yield`、`Proc.new` | OK: `block-proc` | 短命の block を試験。同一 frame 外へ逃がした closure の全 lifetime は未検証 |
| lambda / `->` | 不可: `lambda` | 未実装 opcode。通常 block / `Proc.new` は使えるが、lambda の arity・return semantics の代用品と断言しない |
| `&:method` / Symbol#to_proc | 不可: `symbol-proc` | 明示 `{ \|item\| item.ready? }` に置換。C と Ruby の block 呼出し経路を確認する |
| Collections / `map`、`select`、`reject` | OK: `collections` | 戻り値が必要な変換・選別に使う。空入力の map/select も確認済み。新しい Array の割当て予算に注意 |
| `all?`、`any?`、`each_with_index`、Hash#each | OK: `collections`、`hash` | 空 collection の all?/any? はそれぞれ true/false。Hash の欠損 key は nil |
| `reduce` / `inject` | 不可: `reduce`、`inject` | `sum-alternative` の明示 accumulator + each。空入力の初期値も決める |
| block を省いた Enumerator chaining | 不可: `enumerator`、`each-no-block` | Enumerator 定数なし、each は block 不在で例外。block を直接渡す |
| count(value) | 差異: `count` | `[1,2,1].count(1)` は 3。合致数には select + size または明示 loop を選び、割当てを比較 |
| Methods / default・keyword 引数 | OK: `keyword` | default と未知 keyword の ArgumentError を確認。全 forwarding・`**nil` 等まで検証したわけではない |
| Classes & Modules / attr_accessor・include・super | OK: `names`、`mixin` | 小さな責任と共有する振る舞いを表す。include 可能というだけで多用は勧めない |
| visibility | 差異: `privacy` | private method を外から呼べる。system-task 側の native 権限検査が必要 |
| Exceptions / begin-rescue-ensure | OK/差異: `ensure`、`standard-rescue` | ensure の cleanup と ArgumentError 捕捉は成功。未実装 opcode の根 Exception は bare rescue の外 |
| Numbers | 差異: `int32`、`int64-literal` | 既定 int32。前者は今回の Wasm で wrap、後者は load 拒否。nRF の C overflow 規則の保証にはしない |
| Strings / interpolation・append・byte 処理 | OK/差異: `strings`、`bytes` | interpolation / String append は成功。UTF-8 の「文字数」と length を同一視しない |
| Percent Literals / `%w`、`%i` | OK: `strings` | 短い同種 literal の列に限定。全 percent 構文を試したわけではない |
| pattern matching | 限定 OK: `pattern-array`、`pattern-hash`、`pattern-miss` | array/hash と不一致例外だけを確認。deconstruct、pin、find pattern 等は未検証。単純 case/if を代替にできる |
| freeze による不変化 | 不可: `freeze` | freeze が未定義。共有物を変更しない設計・所有者の限定は別の約束であり、VM が不変性を保証するものではない |
| Fiber | 不可: `fiber` | [rrt0 Task](../mrubyc/task-scheduler.md)を使う。Fiber と同じ制御構造ではない |

## 実行基盤・文書に関わる節

guide の残りの主題を「使える」と一括扱いしません。書式推奨には VM の可否判定が不要なものもあります。

| guide の節 | 分類と適用範囲 |
|---|---|
| Files | IO 定数は不可: `io`。File/Dir 等の filesystem API は RBOS に未実装。CRuby の open/close block を前提にしない |
| Date & Time | Time は不可: `time`。tick・sleep を暦時刻と見なさない |
| Regular Expressions | Regexp は不可: `regexp`。binary protocol は長さ・byte 値で解析。regex 互換 engine は今回導入しない |
| Classes: Constructors | constructor の責任と副作用の整理は設計規則。`new`・ivar は `names` で限定確認。IO の close/finalizer 規則は未設計 |
| Comments / Comment Annotations / Magic Comments / API Documentation | 説明の正確さと契約の記載を採用。encoding・frozen-string-literal の magic comment が mruby/c の実行を変えるとは主張しない |
| Heredocs | 書式の選択肢。今回実行試験なし。大きい protocol fixture を Ruby literal で保持する RAM/RRAM 費用は別途見積もる |
| Metaprogramming | 初期標準として増やさない。class variable / undef / 名前空間付き constant 代入はそれぞれ `classvar`、`undef`、`outer-const` で不可 |
| Gemfile and Gemspec | host tooling の慣習。RubyGems/Bundler を target 上で使えるという意味ではない |
| Misc / Tools | 意図の明確さ・一貫性を採用。RuboCop は未導入。CRuby 向け autocorrect が VM 非対応構文を作る危険をレビューする |
| Introduction / History / Sources of Inspiration / Contributing / Colophon / License / Spread the Word | 背景・参加・配布の情報。VM 能力の判定対象ではない。ライセンスは保持する |

以上は [ruby-style-guide 固定版](https://github.com/rubocop/ruby-style-guide/blob/72ea4198d617e5c3db425cb3806b68b71dcc129f/README.adoc)の主題別要約です。未掲載の個別推奨を検証済みとはしません。method の全索引、opcode、compile flag は既存の [mruby/c 索引](../mrubyc/ruby-first-capabilities.md)を参照してください。

[組込み idiom](embedded-idioms.md) / [調査索引へ戻る](../README.md)
