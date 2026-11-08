# Ruby メソッド索引: objects

[能力と互換性](ruby-first-capabilities.md)を先に読みます。C の引数列は argc 分岐・固定位置参照を示し、CRuby の厳密な arity 検査を保証しません。型・範囲・block・戻り値と副作用は各実装範囲を参照してください。C の登録 table と動的登録、mrblib の def/alias を合わせた一覧です。条件付き機能は [構成](compile-macros.md)に依存します。

## Object

Object.new と継承 class の new は instance を作る入口です。include/extend/attr_reader/attr_accessor/constants 等は class/module 文脈に依存します。C table は CRuby の singleton method table と同じ分離ではなく、receiver の型を C 実装が判定する場合があります。private/public/protected は no-op です。Exception.new と Proc.new は class receiver、message/call は instance の操作です。attr_reader(:x) は x、attr_accessor(:x) は x と x= を生成します。これら利用者が付ける名前は固定登録名の件数に含めません。根拠: `vendor/mrubyc/src/c_object.c:490-573`。

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_object_new` | 任意個を initialize へ転送 | 常時 | `vendor/mrubyc/src/c_object.c:110-114` |
| `!` | C: `c_object_not` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:120-123` |
| `!=` | C: `c_object_neq` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:129-133` |
| `<=>` | C: `c_object_compare` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:139-143` |
| `==` | C: `c_object_equal2` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:149-153` |
| `===` | C: `c_object_equal3` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:159-170` |
| `class` | C: `c_object_class` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:176-183` |
| `dup` | C: `c_object_dup` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:189-203` |
| `block_given?` | C: `c_object_block_given` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:209-228` |
| `is_a?` | C: `c_object_kind_of` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:234-242` |
| `kind_of?` | C: `c_object_kind_of` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_object.c:234-242` |
| `nil?` | C: `c_object_nil` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:248-251` |
| `p` | C: `c_object_p` | argc == 0 / argc == 1 | if !defined(MRBC_NO_STDIO) | `vendor/mrubyc/src/c_object.c:258-279` |
| `print` | C: `c_object_print` | 任意個（順に出力） | if !defined(MRBC_NO_STDIO) | `vendor/mrubyc/src/c_object.c:287-293` |
| `puts` | C: `c_object_puts` | 任意個（0個なら改行） | if !defined(MRBC_NO_STDIO) | `vendor/mrubyc/src/c_object.c:301-311` |
| `raise` | C: `c_object_raise` | argc == 0 / argc == 1 / argc == 2 | 常時 | `vendor/mrubyc/src/c_object.c:325-378` |
| `attr_reader` | C: `c_object_attr_reader` | 任意個の名前 | 常時 | `vendor/mrubyc/src/c_object.c:530-543` |
| `attr_accessor` | C: `c_object_attr_accessor` | 任意個の名前 | 常時 | `vendor/mrubyc/src/c_object.c:549-573` |
| `include` | C: `c_object_include` | 任意個の module | 常時 | `vendor/mrubyc/src/c_object.c:579-613` |
| `extend` | C: `c_object_include` | 任意個の module | 常時 | `vendor/mrubyc/src/c_object.c:579-613` |
| `constants` | C: `c_object_constants` | argc >= 1 | 常時 | `vendor/mrubyc/src/c_object.c:619-646` |
| `public` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/c_object.c:1-1008` |
| `private` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/c_object.c:1-1008` |
| `protected` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/c_object.c:1-1008` |
| `sprintf` | C: `c_object_sprintf` | format + 可変個 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:653-781` |
| `printf` | C: `c_object_printf` | format + 可変個 | if MRBC_USE_STRING; if !defined(MRBC_NO_STDIO) | `vendor/mrubyc/src/c_object.c:788-793` |
| `inspect` | C: `c_object_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:800-803` |
| `to_s` | C: `c_object_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:800-803` |
| `object_id` | C: `c_object_object_id` | 位置引数参照なし | if defined(MRBC_DEBUG) | `vendor/mrubyc/src/c_object.c:385-389` |
| `instance_methods` | C: `c_object_instance_methods` | argc >= 1 | if defined(MRBC_DEBUG) | `vendor/mrubyc/src/c_object.c:397-429` |
| `instance_variables` | C: `c_object_instance_variables` | 位置引数参照なし | if defined(MRBC_DEBUG) | `vendor/mrubyc/src/c_object.c:435-452` |
| `memory_statistics` | C: `c_object_memory_statistics` | argc == 0 | if defined(MRBC_DEBUG); if !defined(MRBC_ALLOC_LIBC) | `vendor/mrubyc/src/c_object.c:459-484` |
| `sleep` | 動的 C: `c_sleep` | 0..1（なしなら suspend、秒 Integer/Float） | rrt0 初期化時 | `vendor/mrubyc/src/rrt0.c:1508-1508`、`vendor/mrubyc/src/rrt0.c:859-890` |
| `sleep_ms` | 動的 C: `c_sleep_ms` | 1（ms Integer） | rrt0 初期化時 | `vendor/mrubyc/src/rrt0.c:1509-1509`、`vendor/mrubyc/src/rrt0.c:899-906` |
| `loop` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/object.rb:14-14` |

print_memstat/print_memory_pool/dump_const/dump_global/dump_symbol/pqall の mrbc_define_method は source comment 内の登録例で、初期化時の実行ではありません。既定 Ruby method として数えず、対応する C 診断 API と区別しました。根拠: `vendor/mrubyc/src/alloc.c:1044-1068`、`vendor/mrubyc/src/global.c:183-190,234-241`、`vendor/mrubyc/src/symbol.c:440-447`、`vendor/mrubyc/src/rrt0.c:1514-1522`。

## NilClass

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `to_i` | C: `c_nil_to_i` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:865-868` |
| `to_a` | C: `c_nil_to_a` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:874-877` |
| `to_h` | C: `c_nil_to_h` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_object.c:883-886` |
| `to_f` | C: `c_nil_to_f` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_object.c:893-896` |
| `inspect` | C: `c_nil_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:904-912` |
| `to_s` | C: `c_nil_to_s` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:918-926` |

## TrueClass

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `inspect` | C: `c_true_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:956-964` |
| `to_s` | C: `c_true_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:956-964` |

## FalseClass

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `inspect` | C: `c_false_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:986-994` |
| `to_s` | C: `c_false_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_object.c:986-994` |

## Proc

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_proc_new` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_proc.c:96-106` |
| `call` | C: `c_proc_call` | 任意個を block へ転送 | 常時 | `vendor/mrubyc/src/c_proc.c:112-131` |

## Symbol

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `all_symbols` | C: `c_symbol_all_symbols` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/symbol.c:369-381` |
| `inspect` | C: `c_symbol_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/symbol.c:388-405` |
| `to_s` | C: `c_symbol_to_s` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/symbol.c:411-419` |
| `id2name` | C: `c_symbol_to_s` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/symbol.c:411-419` |
| `to_sym` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/symbol.c:1-478` |

## Exception

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_exception_new` | argc == 1 | 常時 | `vendor/mrubyc/src/error.c:258-270` |
| `message` | C: `c_exception_message` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/error.c:276-288` |

[調査索引へ戻る](../README.md)
