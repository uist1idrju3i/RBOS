# Ruby-first で書けること・書けないこと

基準は mruby/c `434bccd609f2a3e90d6bb95c458621898bc6a508` と mruby 4.0.0 `831da26b9021de0369d17b71b5667e2941a1a32d` です。Ruby が製品ロジックを担当し、C は RBOS の共有 binding/backend に閉じる目標です。CRuby の全標準ライブラリを搭載する目標とは異なります。

## クラス・module と method の索引

| 主題 | 全登録名・引数形式の索引 | 製品での使い方 |
|---|---|---|
| Object、NilClass、TrueClass、FalseClass、Symbol、Proc、Exception | [objects](methods-objects.md) | 通常の object、instance variable、継承、module、例外、block |
| Array、Hash、Range、Enumerable | [collections](methods-collections.md) | 設定・event の整形。iteration は block を明示する |
| Integer、Float、Math、String | [numeric/text](methods-numeric-text.md) | 数値・binary protocol。文字 encoding と桁数を製品仕様にする |
| Task、Mutex、VM、sleep/sleep_ms | [tasks](methods-tasks.md) | rrt0 に task を任せ、共有 peripheral は backend owner へ要求 |

索引は継承分を重複させず、C table、動的登録、mrblib def/alias の 288 登録を記録しました。引数列が argc 条件である C method は、宣言的 arity を持つ CRuby method とは異なります。実装が位置引数を読むだけで個数・型を検査しない場合もあるため、受理可能な任意入力の保証ではありません。

例外の subclass は NoMemoryError、NotImplementedError、StandardError、ArgumentError、IndexError、IOError、NameError、NoMethodError、NoMatchingPatternError、RangeError、RuntimeError、TypeError、ZeroDivisionError。独自 method のない subclass は Exception の new/message 等を継承します。根拠: `vendor/mrubyc/src/error.c:1-355`。Class/Module は value の型として存在しますが、CRuby の全 reflection API や Class.new/Module.new の互換実装を意味しません。`vendor/mrubyc/src/class.c:1-643` と `vendor/mrubyc/src/value.h:1-800`。

## 互換性で間違えやすい点

| 機能 | 固定版でできること・制約 | 根拠 |
|---|---|---|
| method/class/module | def、継承、include、alias、attr_reader/accessor。method_missing の処理もある。private/public/protected は c_ineffect へ登録され、アクセス保護にならない | `vendor/mrubyc/src/c_object.c:1-1008`、`vendor/mrubyc/src/vm.c:1-3336` |
| block/Proc | yield、&block、Proc.new と call、upvar、block return/break。Proc の存在と lambda opcode の対応は別。OP_LAMBDA と OP_CALL は未実装 | `vendor/mrubyc/src/c_proc.c:1-142`、[opcode 一覧](opcode-compatibility.md) |
| keyword | Ruby def の必須/任意 keyword と残余 Hash、C 用 keyword macro がある。keyword の型・長さ・device 範囲は別に検証 | `vendor/mrubyc/doc/c_KeywordArgument.md:1-134`、`vendor/mrubyc/src/vm.c:1-3336` |
| exception | raise/rescue/ensure、例外 object と限定した call trace。終了 task の例外は他 task への自動伝播と考えない | `vendor/mrubyc/src/error.c:1-355`、`vendor/mrubyc/src/rrt0.c:1-1585` |
| pattern matching | MATCHERR と Array#deconstruct/Hash#deconstruct_keys があり、一括して非対応とはいえない。上流 test と生成 opcode ごとに確認 | `vendor/mrubyc/test/pattern_match_test.rb:1-580` |
| class variable 等 | @@ の GETCV/SETCV、明示的な X::CONST= の SETMCNST、undef の UNDEF は未実装 handler。通常 class 内の constant 定義とは区別 | [opcode 一覧](opcode-compatibility.md) |
| Integer | 既定 int32。INT16/INT64 は build 条件。任意精度 Integer/BigInt の自動昇格を想定しない。mrbc の定数畳込みで int64 literal になり load 時に拒否されることもある | `vendor/mrubyc/src/value.h:1-800`、`vendor/mrubyc/src/load.c:1-440`、[実験](capability-probes.md) |
| Float/Math | FLOAT=2 は double、1 は float、0 は無効。Math は既定無効。浮動小数の誤差・NaN/Inf/domain error を製品で規定 | `vendor/mrubyc/src/vm_config.h:1-153`、`vendor/mrubyc/src/c_numeric.c:1-541`、`vendor/mrubyc/src/c_math.c:1-286` |
| String | 既定 byte 単位。UTF8=1 で文字単位の対象操作が変わる。Unicode case は別 option、BMP 対応。CRuby の Encoding object/多 encoding 変換と同義ではない。長さ型は既定 uint16_t | `vendor/mrubyc/src/c_string.h:1-142`、`vendor/mrubyc/src/c_string.c:1-2558`、`vendor/mrubyc/src/vm_config.h:1-153` |
| collections | Array#count は size と同じ C function。CRuby の count(value)/block の件数計算を期待しない。多くの each は block なしで Enumerator を返さない | `vendor/mrubyc/src/c_array.c:1-1406`、`vendor/mrubyc/mrblib/array.rb:1-261` |
| 標準 library | Fiber/Thread、IO/File、Socket、Regexp、Time 等の標準的な class/機能は上記登録表にない。compiler が構文を受け付けても runtime の class/method 不在で失敗し得る | 全 method 索引と `vendor/mrubyc/src/class.c:1-643` |

登録 method と別に、VM は ADD/SUB/MUL/DIV、EQ/LT/LE/GT/GE 等の専用 opcode で数値演算・比較を処理します。Ruby の演算子構文で動くことと、同名の C method entry を reflection/C の mrbc_send から呼べることは同義ではありません。命令と実装範囲は [全 opcode 表](opcode-compatibility.md)で追跡できます。

これは CRuby/mruby の全 method 集合との差分を実行した結果ではありません。登録一覧にない method が必要なら、依存 module、Ruby 実装、共有 binding 追加のどれで補うか決めます。mruby の mrbgem を mruby/c にそのまま link できるとは仮定しません。

## 製品を Ruby のみで書く境界

- 状態機械、設定、通信 payload の組立て、task 間の制御は Ruby へ置く。
- GPIO/I2C/SPI/ADC/BLE 等は、upstream に hardware class が既にあると説明せず RBOS の backend と binding で提供する。
- system-task の許可は native callback で確認する。Ruby の private、class 名、VM ID の数字だけを security boundary にしない。
- register/symbol/heap の上限、native method の非プリエンプト区間、参照 cycle を前提に設計する。

追加手順は [ruby-api-binding skill](../../.agents/skills/ruby-api-binding/SKILL.md)、値の規約は [C API](c-api.md)、資源は [設定とメモリ](configuration-and-memory.md)を参照してください。実機・全 opcode/全 method の総当たりは未検証です。

[調査索引へ戻る](../README.md)
