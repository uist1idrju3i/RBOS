# 上流 test・sample・HAL と build の棚卸し

## build の入口

root Makefile は src/sample_c を sub-make します。src は hal_selector.mk、CFLAGS += -Wall -g、BUILD_DIR=../build、全 VM C source と選択 HAL を使用します。RUBY_INSTALLED を検出して _autogen symbol/class/method/Unicode を作り、mrblib は enum/array/global/hash/numeric/object/range/string の順に mrbc -Bmrblib_bytecode --remove-lv で生成します。根拠: `vendor/mrubyc/Makefile:1-44`、`vendor/mrubyc/src/Makefile:11-31,130-178`、`vendor/mrubyc/mrblib/Makefile:12-51`。

Makefile の明示的な -D 連動は MRBC_USE_STRING_UTF8 と MRBC_USE_UNICODE_CASE。その他の option は CFLAGS/HAL/vm_config の実際の定義を確認します。RUBY_INSTALLED は build ツールの有無であって Ruby feature flag ではありません。Unicode は 16.0.0 の同梱 UnicodeData.txt から生成します。生成済み file だけの存在を compiler 互換の保証にしません。

## C samples と同梱 Ruby 入力

| file | 示すこと | 根拠 |
|---|---|---|
| sample_no_scheduler.c | VM を直接 open/load/begin/run/end/close する単体実行 | `vendor/mrubyc/sample_c/sample_no_scheduler.c:1-84` |
| sample_scheduler.c | rrt0 に bytecode を task として登録し run | `vendor/mrubyc/sample_c/sample_scheduler.c:1-68` |
| sample_concurrent.c | 複数入力を別 task として同時実行 | `vendor/mrubyc/sample_c/sample_concurrent.c:1-70` |
| sample_include.c | C 配列にした bytecode を include して実行 | `vendor/mrubyc/sample_c/sample_include.c:1-29` |
| sample_include_bytecode.c | 上の実行例に埋め込む生成済み C 配列 | `vendor/mrubyc/sample_c/sample_include_bytecode.c:1-13` |
| sample_include_bytecode.rb | 埋め込み配列の Ruby 原稿 | `vendor/mrubyc/sample_c/sample_include_bytecode.rb:1-8` |
| sample_myclass.c | 利用者 class と C callback の登録、値の受け渡し | `vendor/mrubyc/sample_c/sample_myclass.c:1-89` |
| Makefile | sample target と link/build 規則 | `vendor/mrubyc/sample_c/Makefile:1-33` |

この固定版には sample_ruby/ directory はありません。Ruby の sample は sample_c/sample_include_bytecode.rb と mrblib/test にあります。不存在を別版の sample 一覧で埋めてはいません。

## test の全ファイル

| file | 主題 | test_* 定義数 / 例 | 根拠 |
|---|---|---|---|
| 0_runner.rb | CRuby 側の Picotest runner。外部 picoruby-picotest を読み、失敗で exit 1 | 0 /  | `vendor/mrubyc/test/0_runner.rb:1-13` |
| addi_subi_test.rb | 即値の加算・減算 opcode | 2 / test_no_method_error, test_addi_subi | `vendor/mrubyc/test/addi_subi_test.rb:1-25` |
| array_test.rb | 配列の生成、変更、探索、比較と列挙 | 36 / test_sort_integer, test_sort_symbol | `vendor/mrubyc/test/array_test.rb:1-534` |
| bool_test.rb | true/false の論理と変換 | 3 / test_basic, test_negation | `vendor/mrubyc/test/bool_test.rb:1-113` |
| const_test.rb | 定数の定義・検索 | 4 / test_name_error, test_test1 | `vendor/mrubyc/test/const_test.rb:1-56` |
| def_test.rb | method 定義・呼出しと引数 | 0 /  | `vendor/mrubyc/test/def_test.rb:1-7` |
| div_mod_test.rb | 除算・剰余の符号と型 | 2 / test_div, test_mod | `vendor/mrubyc/test/div_mod_test.rb:1-152` |
| exception_test.rb | raise/rescue/ensure と例外の流れ | 8 / test_exception_rescued, test_exception_rescued_with_message | `vendor/mrubyc/test/exception_test.rb:1-81` |
| float_test.rb | Float の計算と変換（build 条件に依存） | 1 / test_clamp | `vendor/mrubyc/test/float_test.rb:1-20` |
| global_test.rb | global variable と共有値 | 1 / test_ruby_engine | `vendor/mrubyc/test/global_test.rb:1-8` |
| hash_test.rb | Hash の key/value、変更と列挙 | 28 / test_constructor, test_pick_value | `vendor/mrubyc/test/hash_test.rb:1-232` |
| integer_test.rb | 整数の演算、比較と変換 | 9 / test_abs, test_chr | `vendor/mrubyc/test/integer_test.rb:1-105` |
| math_test.rb | Math の関数（MATH option に依存） | 1 / test_all | `vendor/mrubyc/test/math_test.rb:1-31` |
| method_missing_test.rb | 未定義 method の dispatch | 1 / test_method_missing | `vendor/mrubyc/test/method_missing_test.rb:1-12` |
| my_alias_test.rb | method の alias | 3 / test_method1, test_method2 | `vendor/mrubyc/test/my_alias_test.rb:1-54` |
| my_block_test.rb | block/yield/Proc、外側変数 | 3 / test_yeald, test_instance_method | `vendor/mrubyc/test/my_block_test.rb:1-63` |
| my_equal3_test.rb | === と case の判定 | 11 / test_fixnum_fixnum, test_fixnum_float | `vendor/mrubyc/test/my_equal3_test.rb:1-100` |
| my_instance_variable_test.rb | instance variable と accessor | 1 / test_all | `vendor/mrubyc/test/my_instance_variable_test.rb:1-38` |
| my_karg_test.rb | 必須・任意・残余 keyword と位置引数の併用 | 6 / test_karg_with_initial_value, test_karg_without_initial_value | `vendor/mrubyc/test/my_karg_test.rb:1-70` |
| my_nested_class_test.rb | 入れ子 class と constant scope | 1 / test_nested | `vendor/mrubyc/test/my_nested_class_test.rb:1-26` |
| my_operator_method_test.rb | 演算子 method の dispatch | 1 / test_defining_operator_methods | `vendor/mrubyc/test/my_operator_method_test.rb:1-38` |
| my_super_test.rb | 継承と super | 9 / test_super_1, test_super_2 | `vendor/mrubyc/test/my_super_test.rb:1-163` |
| nil_class_test.rb | nil の変換と判定 | 2 / test_is_nil, test_nil_to_something | `vendor/mrubyc/test/nil_class_test.rb:1-25` |
| object_test.rb | Object と class/reflection の一部 | 5 / test_alias, test_all | `vendor/mrubyc/test/object_test.rb:1-46` |
| op_basic_test.rb | 基本 opcode の動作 | 9 / test_op_add, test_op_addi | `vendor/mrubyc/test/op_basic_test.rb:1-237` |
| op_method_test.rb | method/block に関わる opcode | 7 / test_plus_minus, test_surplus | `vendor/mrubyc/test/op_method_test.rb:1-85` |
| pattern_match_test.rb | value/array/hash/class/guard 等の pattern matching | 56 / test_value_pattern_with_integer, test_value_pattern_with_string | `vendor/mrubyc/test/pattern_match_test.rb:1-580` |
| range_test.rb | Range の端点・include と列挙 | 2 / test_basic, test_equal3 | `vendor/mrubyc/test/range_test.rb:1-28` |
| sprintf_test.rb | tiny printf の format | 6 / test_c, test_s | `vendor/mrubyc/test/sprintf_test.rb:1-191` |
| string_ljust_rjust_test.rb | 文字列の桁揃えと引数エラー | 10 / test_ljust, test_ljust_id | `vendor/mrubyc/test/string_ljust_rjust_test.rb:1-74` |
| string_split_test.rb | split の separator と limit | 7 / test_string, test_space | `vendor/mrubyc/test/string_split_test.rb:1-111` |
| string_strip_test.rb | strip/lstrip/rstrip と破壊版 | 6 / test_strip, test_strip_bang | `vendor/mrubyc/test/string_strip_test.rb:1-226` |
| string_test.rb | String の生成、byte 操作、比較と変更 | 42 / test_string_new_with_arg, test_string_new_without_arg | `vendor/mrubyc/test/string_test.rb:1-823` |
| string_utf8_test.rb | UTF8 option による文字単位の操作 | 82 / test_size_ascii, test_size_japanese | `vendor/mrubyc/test/string_utf8_test.rb:1-688` |
| symbol_test.rb | symbol の生成・比較・変換 | 6 / test_identity, test_eq | `vendor/mrubyc/test/symbol_test.rb:1-46` |

35 files、test_* 定義は計 371 件です。test 名・定義数は inventory で、実行済み件数ではありません。build 条件や skip で実行される集合は変わります。

## 上流 suite の実行条件

```sh
make docker_build
make test
make test_all
```

root Makefile の test は Darwin なら clang_no_libc、それ以外は gcc_no_libc。test_all は gcc/clang/ARM/MIPS × libc/no_libc の8組です。Docker image、PicoRuby/femtoruby、rake、qemu、picoruby-picotest が前提で、CRuby の 0_runner.rb が別 process の試験を管理します。doc/test.md の test_full と MRBC_LIBC_ALLOC の記載は、そのまま現行 target/option 名として使いません。根拠: `vendor/mrubyc/Makefile:46-155`、`vendor/mrubyc/test/0_runner.rb:1-13`、`vendor/mrubyc/doc/test.md:1-29`。

今回 Docker の upstream suite、cross-target build は実行していません。RBOS の既存 Wasm smoke と追加 probe の結果は [実験記録](capability-probes.md)に分離しました。

## HAL の全 variant

| HAL | context / 選択上の注意 | 根拠 |
|---|---|---|
| minimal | 移植用の macro/function 最小雛形 | `vendor/mrubyc/hal/minimal.h:1-55` |
| posix | signal/timer と host write/flush/abort | `vendor/mrubyc/hal/posix/hal.h:1-116` |
| emscripten | ASYNCIFY、NO_TIMER、scheduler exit。Node と browser の時間モデルを実機と分ける | `vendor/mrubyc/hal/emscripten/hal.h:1-95` |
| esp32 | ESP32 platform timer/critical section | `vendor/mrubyc/hal/esp32/hal.h:1-120` |
| psoc5lp | PSoC の platform timer/IRQ macro | `vendor/mrubyc/hal/psoc5lp/hal.h:1-88` |
| pic24 | PIC24 向け header。selector の legacy 名 PIC24 と実 directory 名は大小を含めて確認 | `vendor/mrubyc/hal/pic24/hal.h:1-92` |
| rp2040 | RP2040 platform timer と IRQ mask | `vendor/mrubyc/hal/rp2040/hal.h:1-90` |
| zephyr | k_timer/irq_lock と thread scheduler 連携。BM に直接転用しない | `vendor/mrubyc/hal/zephyr/hal.h:1-95` |
| stm32 | STM32 platform の timer/console 接点。legacy selector の専用 switch はない | `vendor/mrubyc/hal/stm32/hal.h:1-51` |

hal_selector.mk は MRBC_USE_HAL 指定で include path を加えます。未指定時は POSIX。legacy MRBC_USE_HAL_{POSIX,PSOC5LP,ESP32,PIC24,RP2040,ZEPHYR,EMSCRIPTEN} もあります。新規 BM port は folder を明示し、host HAL の IRQ mask が SD zero-latency を守るという保証に置き換えません。根拠: `vendor/mrubyc/src/hal_selector.mk:1-43`。

[調査索引へ戻る](../README.md)
