# Ruby メソッド索引: collections

[能力と互換性](ruby-first-capabilities.md)を先に読みます。C の引数列は argc 分岐・固定位置参照を示し、CRuby の厳密な arity 検査を保証しません。型・範囲・block・戻り値と副作用は各実装範囲を参照してください。C の登録 table と動的登録、mrblib の def/alias を合わせた一覧です。条件付き機能は [構成](compile-macros.md)に依存します。

## Array

new は class receiver、他は通常 instance receiver の API です。count は size/length の別名で、値や block による絞込みではありません。Enumerable の collect/map/each_with_index は Array へ include されるため、その3件は末尾の module 節に一度だけ記録します。破壊版の ! と非破壊版、戻り値 self/nil/新配列は同一視しません。

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_array_new` | argc == 0 / argc == 1 / argc == 2 | 常時 | `vendor/mrubyc/src/c_array.c:601-646` |
| `+` | C: `c_array_add` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:652-677` |
| `-` | C: `c_array_difference` | 任意個の Array | 常時 | `vendor/mrubyc/src/c_array.c:909-931` |
| `[]` | C: `c_array_get` | argc == 1 / argc == 2 | 常時 | `vendor/mrubyc/src/c_array.c:683-809` |
| `at` | C: `c_array_get` | argc == 1 / argc == 2 | 常時 | `vendor/mrubyc/src/c_array.c:683-809` |
| `[]=` | C: `c_array_set` | argc == 2 / argc == 3 | 常時 | `vendor/mrubyc/src/c_array.c:815-894` |
| `<<` | C: `c_array_push` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:1054-1058` |
| `clear` | C: `c_array_clear` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:900-903` |
| `difference` | C: `c_array_difference` | 任意個の Array | 常時 | `vendor/mrubyc/src/c_array.c:909-931` |
| `deconstruct` | C: `c_array_deconstruct` | argc != 0 | 常時 | `vendor/mrubyc/src/c_array.c:1284-1293` |
| `delete_at` | C: `c_array_delete_at` | argc == 1 | 常時 | `vendor/mrubyc/src/c_array.c:937-945` |
| `empty?` | C: `c_array_empty` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:951-956` |
| `size` | C: `c_array_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:962-967` |
| `length` | C: `c_array_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:962-967` |
| `count` | C: `c_array_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:962-967` |
| `include?` | C: `c_array_include` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:973-976` |
| `&` | C: `c_array_and` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:982-997` |
| `\|` | C: `c_array_or` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:1003-1026` |
| `first` | C: `c_array_first` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1032-1037` |
| `last` | C: `c_array_last` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1043-1048` |
| `push` | C: `c_array_push` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:1054-1058` |
| `pop` | C: `c_array_pop` | argc == 0 / argc == 1 | 常時 | `vendor/mrubyc/src/c_array.c:1064-1086` |
| `shift` | C: `c_array_shift` | argc == 0 / argc == 1 | 常時 | `vendor/mrubyc/src/c_array.c:1102-1134` |
| `unshift` | C: `c_array_unshift` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_array.c:1092-1096` |
| `dup` | C: `c_array_dup` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1140-1143` |
| `min` | C: `c_array_min` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1149-1163` |
| `max` | C: `c_array_max` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1169-1183` |
| `minmax` | C: `c_array_minmax` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1189-1207` |
| `uniq` | C: `c_array_uniq` | 0、block は NotImplementedError | 常時 | `vendor/mrubyc/src/c_array.c:1213-1224` |
| `uniq!` | C: `c_array_uniq_self` | 0、block は NotImplementedError | 常時 | `vendor/mrubyc/src/c_array.c:1230-1241` |
| `reverse` | C: `c_array_reverse` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1247-1262` |
| `reverse!` | C: `c_array_reverse_self` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_array.c:1268-1279` |
| `inspect` | C: `c_array_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_array.c:1300-1321` |
| `to_s` | C: `c_array_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_array.c:1300-1321` |
| `join` | C: `c_array_join` | argc == 0 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_array.c:1347-1357` |
| `all?` | mrblib: `Ruby def` | *pattern, &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:17-17` |
| `any?` | mrblib: `Ruby def` | *pattern, &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:48-48` |
| `collect!` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:79-79` |
| `map!` | mrblib alias: `alias collect!` | 元メソッドと同じ | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:87-87` |
| `delete_if` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:92-92` |
| `each` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:107-107` |
| `each_index` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:119-119` |
| `index` | mrblib: `Ruby def` | *val, &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:131-131` |
| `find_index` | mrblib alias: `alias index` | 元メソッドと同じ | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:154-154` |
| `none?` | mrblib: `Ruby def` | ... | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:159-159` |
| `reject!` | mrblib: `Ruby def` | &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:166-166` |
| `reject` | mrblib: `Ruby def` | &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:175-175` |
| `reverse_each` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:182-182` |
| `select` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:194-194` |
| `filter` | mrblib alias: `alias select` | 元メソッドと同じ | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:208-208` |
| `select!` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:213-213` |
| `filter!` | mrblib alias: `alias select!` | 元メソッドと同じ | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:227-227` |
| `sort!` | mrblib: `Ruby def` | &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:232-232` |
| `sort` | mrblib: `Ruby def` | &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/array.rb:257-257` |

## Hash

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_hash_new` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:330-334` |
| `[]` | C: `c_hash_get` | argc != 1 | 常時 | `vendor/mrubyc/src/c_hash.c:340-350` |
| `[]=` | C: `c_hash_set` | argc != 2 | 常時 | `vendor/mrubyc/src/c_hash.c:356-368` |
| `__except` | C: `c_hash_except_keys` | argc != 1 | 常時 | `vendor/mrubyc/src/c_hash.c:432-462` |
| `__pat_values` | C: `c_hash_pat_values` | argc != 1 | 常時 | `vendor/mrubyc/src/c_hash.c:397-425` |
| `clear` | C: `c_hash_clear` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:374-377` |
| `deconstruct_keys` | C: `c_hash_deconstruct_keys` | argc != 1 | 常時 | `vendor/mrubyc/src/c_hash.c:383-390` |
| `dup` | C: `c_hash_dup` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:468-473` |
| `delete` | C: `c_hash_delete` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:479-488` |
| `empty?` | C: `c_hash_empty` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:494-499` |
| `fetch` | C: `c_hash_fetch` | argc < 1 / argc > 2 / argc == 2 | 常時 | `vendor/mrubyc/src/c_hash.c:643-667` |
| `has_key?` | C: `c_hash_has_key` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:505-510` |
| `has_value?` | C: `c_hash_has_value` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_hash.c:516-530` |
| `key` | C: `c_hash_key` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_hash.c:536-555` |
| `keys` | C: `c_hash_keys` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:561-573` |
| `size` | C: `c_hash_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:579-584` |
| `length` | C: `c_hash_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:579-584` |
| `count` | C: `c_hash_size` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:579-584` |
| `merge` | C: `c_hash_merge` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_hash.c:590-603` |
| `merge!` | C: `c_hash_merge_self` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_hash.c:609-619` |
| `to_h` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/c_hash.c:1-747` |
| `values` | C: `c_hash_values` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_hash.c:625-637` |
| `inspect` | C: `c_hash_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_hash.c:674-711` |
| `to_s` | C: `c_hash_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_hash.c:674-711` |
| `each` | mrblib: `Ruby def` | &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/hash.rb:17-17` |

## Range

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `===` | C: `c_range_equal3` | 1（比較対象） | 常時 | `vendor/mrubyc/src/c_range.c:114-131` |
| `first` | C: `c_range_first` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_range.c:137-141` |
| `last` | C: `c_range_last` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_range.c:147-151` |
| `exclude_end?` | C: `c_range_exclude_end` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_range.c:158-162` |
| `inspect` | C: `c_range_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_range.c:170-188` |
| `to_s` | C: `c_range_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_range.c:170-188` |
| `each` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/range.rb:14-14` |

## Enumerable

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `collect` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/enum.rb:15-15` |
| `map` | mrblib alias: `alias collect` | 元メソッドと同じ | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/enum.rb:22-22` |
| `each_with_index` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/enum.rb:27-27` |

[調査索引へ戻る](../README.md)
