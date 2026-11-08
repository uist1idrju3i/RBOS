---
name: ruby-idiomatic
description: src/**/*.rb、tests/mruby/、サンプル、文書のコード例など、RBOSの製品向けRubyを書く・変更するときに使う。意図と読みやすさを保ち、固定mruby/cとの互換性をWasmで確認する。
---

# mruby/c で Ruby らしく書く

Ruby-first は、製品利用者が Ruby と board 設定を中心に書けるようにする目標です。CRuby の短い書き方を移すだけでは達成できません。判断の根拠は [原則](../../../research/ruby-style/principles.md)、[可否表](../../../research/ruby-style/idiom-compatibility.md)、[組込み idiom](../../../research/ruby-style/embedded-idioms.md)へ集約しています。C binding は [ruby-api-binding](../ruby-api-binding/SKILL.md)、周辺機器の契約は [io-api-guideline](../io-api-guideline/SKILL.md)の責任です。

## 手順

1. **意図**: 入力、出力、空・未設定・失敗時の結果、許される副作用を先に書きます。正常系を読み下せる形にし、guard clause で例外的な経路を分けます。短さを目的に semicolon や多段の三項演算子へ圧縮しません。
2. **名前**: 変数・method は snake_case、class/module は CamelCase、定数は SCREAMING_SNAKE_CASE。`?` は問い合わせ、`!` は安全な対と比べた危険性を伝えます。全 setter に `!` を付けません。引数の単位・戻り値・例外・待機を説明し、コードコメントは英語にします。
3. **block と iterator**: 変換は map、選別は select/reject、副作用は each、存在確認は any?/all? と意図をそろえます。block を明示し、結果を捨てる map や不要な中間 Array を避けます。件数制御・割当て予算に理由があるなら bounded while も使えます。速度差は測定せずに断言しません。
4. **例外**: 通常の失敗は具体的な StandardError 系で捕捉し、ensure で必要な解放を行います。未実装 opcode の根 Exception を `rescue Exception` で隠して処理を続けません。nil、false、0、空 String の意味を混ぜません。0 は真です。
5. **task と時間**: 待ちは sleep/sleep_ms、役割の並行実行は rrt0 Task を使います。busy-wait で待ちません。単一の長い native call を tick が自動的に中断して他の Ruby task を動かすとは仮定しません。時間・再試行・queue に上限を設けます。
6. **資源**: instance と buffer の owner、Mutex の範囲・取得順・例外時の解放を決めます。必要なら owner task に要求を集めます。hot loop の割当てと refcount cycle を避ける設計にし、共有状態の再利用には寿命・容量を定義します。ISR から Ruby、allocation/refcount、raise、task 操作を行いません。private は認可の境界になりません。
7. **可否の照合**: [固定 mruby/c の対応表](../../../research/ruby-style/idiom-compatibility.md)と変更箇所を照合します。compiler の成功を実行の成功と同一視しません。pattern matching や closure の狭い成功例を全機能へ拡張せず、未確認なら小さい fixture で確かめます。RuboCop は未導入で、CRuby 向け autocorrect を無条件に適用しません。
8. **Wasm 実行**: 正常・空・不正入力を `tests/mruby/` の fixture で検査します。追加 fixture は compile だけでなく [check.sh](../../../tools/mrubyc-wasm/check.sh)の timeout 付き runner 実行へ明示的に追加します。非対応構文を検証する fixture だけは、既存の expect_failure で終了値と診断を照合します。emsdk 環境で `tools/mrubyc-wasm/check.sh` を実行します。

## CRuby の慣用句と mruby/c での選択

各行の右欄は check.sh が実行する fixture です。以下は同一 semantics の機械的な変換表ではなく、固定 VM で試験した使い方です。特に lambda の arity/return と Proc、Fiber と Task は同一ではありません。

| CRuby での書き方・前提 | mruby/c での選択 | 実行 fixture |
|---|---|---|
| `map(&:to_s)` | `map { \|value\| value.to_s }` と block を明示 | [collections](../../../tests/mruby/idiom_collections.rb)、回避対象は [symbol_proc](../../../tests/mruby/idiom_avoid_symbol_proc.rb) |
| blockless Enumerator の chain | each / each_with_index に block を直接渡す | [collections](../../../tests/mruby/idiom_collections.rb) |
| reduce / inject で集計 | 初期値を決め、ローカル accumulator と each を使う | [collections](../../../tests/mruby/idiom_collections.rb) |
| `count(value)` で合致数 | `select { \|item\| item == value }.size`。一時 Array の予算も確認 | [collections](../../../tests/mruby/idiom_collections.rb) |
| lambda / `->` | 短命の通常 block / yield / Proc.new を検討。lambda の意味を必要とする処理は別設計 | [objects](../../../tests/mruby/idiom_objects.rb)、回避対象は [lambda](../../../tests/mruby/idiom_avoid_lambda.rb) |
| class variable や外側からの名前空間付き constant 代入 | instance variable と class 内の constant 定義で責任を限定 | [objects](../../../tests/mruby/idiom_objects.rb) |
| 命名・guard・keyword・mixin | 同じ読みやすさを維持し、未知 keyword の失敗も検査 | [objects](../../../tests/mruby/idiom_objects.rb) |
| false も cache したい値に `||=` | 未設定を nil で表すなら `if cached.nil?` で代入 | [values](../../../tests/mruby/idiom_values.rb) |
| nil receiver に safe navigation | `&.` は利用可能。nil・空・通常値を区別して検査 | [values](../../../tests/mruby/idiom_values.rb) |
| String の長さを表示文字数と見なす | protocol は bytesize / each_byte で扱う。既定では byte 単位 | [values](../../../tests/mruby/idiom_values.rb) |
| 任意精度 Integer に依存する演算 | 既定 int32 に収まる count・単位・積を事前検証。大きい literal を避ける | [values](../../../tests/mruby/idiom_values.rb)、回避対象は [int64](../../../tests/mruby/idiom_avoid_int64.rb) |
| bare rescue による一般的な失敗捕捉 | 通常の引数エラーは ArgumentError 等で捕捉し ensure で解放。根 Exception の opcode エラーは修正する | [resources](../../../tests/mruby/idiom_resources.rb)、根 Exception は [lambda](../../../tests/mruby/idiom_avoid_lambda.rb) |
| Fiber / Time 等を前提にした待機 | rrt0 Task と sleep_ms、共有状態には Mutex。暦時刻・Fiber の代替仕様は保証しない | [resources](../../../tests/mruby/idiom_resources.rb)、複数 task は [scheduler](../../../tests/mruby/scheduler.rb)・[worker_a](../../../tests/mruby/worker_a.rb)・[worker_b](../../../tests/mruby/worker_b.rb) |

非対応機能・visibility・closure lifetime の詳細と出典は [調査の可否表](../../../research/ruby-style/idiom-compatibility.md)を参照します。この表の代替を変更したら、リンク先の assertion と check.sh の実行も同じ PR で更新してください。成功 fixture は結果の検証後に PASS を出し、非対応 fixture は診断の偶然の一致だけで成功扱いしません。

## 完了条件

`tools/mrubyc-wasm/check.sh` が成功し、追加・変更 fixture の PASS と想定失敗の終了値・診断を確認できることが完了条件です。空入力と異常系が未検査なら完了ではありません。製品 Ruby 自体を自動実行しない場合も、同じ振る舞いを小さい fixture で実行してください。既存の src/**/*.rb 自動処理は compile のみです。

Skill や日本語文書を変更した場合は check-skills / unittest / yomiyasu / diff --check も実行します。Wasm の成功と、nRF の IRQ・DMA・RAM・latency・電力の実測を区別して報告します。[既存の実行手順](../../../tools/mrubyc-wasm/README.md)を参照してください。
