# Ruby メソッド索引: numeric-text

[能力と互換性](ruby-first-capabilities.md)を先に読みます。C の引数列は argc 分岐・固定位置参照を示し、CRuby の厳密な arity 検査を保証しません。型・範囲・block・戻り値と副作用は各実装範囲を参照してください。C の登録 table と動的登録、mrblib の def/alias を合わせた一覧です。条件付き機能は [構成](compile-macros.md)に依存します。

## Integer

Integer/Float の数値は通常 instance 操作です。Math は条件付き module の関数群、String.new は class の入口、String の他の列は instance 操作です。Integer の +,-,*,/,比較等は VM の専用 opcode でも処理されるため、C table だけが全演算の実行経路ではありません。String の helper __ljust_rjust_argcheck も Ruby から呼べる実装で、visibility を保護に使えません。

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `[]` | C: `c_integer_bitref` | argc == 1 | 常時 | `vendor/mrubyc/src/c_numeric.c:48-56` |
| `+@` | C: `c_integer_positive` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_numeric.c:62-65` |
| `-@` | C: `c_integer_negative` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_numeric.c:71-75` |
| `**` | C: `c_integer_power` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:81-98` |
| `%` | C: `c_integer_mod` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:104-123` |
| `&` | C: `c_integer_and` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:129-133` |
| `\|` | C: `c_integer_or` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:139-143` |
| `^` | C: `c_integer_xor` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:149-153` |
| `~` | C: `c_integer_not` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_numeric.c:159-163` |
| `<<` | C: `c_integer_lshift` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:184-188` |
| `>>` | C: `c_integer_rshift` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:194-198` |
| `+` | C: `c_integer_plus` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:204-209` |
| `-` | C: `c_integer_minus` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:215-220` |
| `>=` | C: `c_integer_gt_eq` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/c_numeric.c:226-231` |
| `abs` | C: `c_integer_abs` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/c_numeric.c:237-242` |
| `to_i` | C: `c_ineffect` | 0 / c_ineffect は no-op | 常時 | `vendor/mrubyc/src/c_numeric.c:1-541` |
| `clamp` | C: `c_numeric_clamp` | argc != 2 | 常時 | `vendor/mrubyc/src/c_numeric.c:251-279` |
| `to_f` | C: `c_integer_to_f` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:286-290` |
| `chr` | C: `c_integer_chr` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_numeric.c:334-370` |
| `inspect` | C: `c_integer_inspect` | 0..1（base は 2..36） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_numeric.c:376-401` |
| `to_s` | C: `c_integer_inspect` | 0..1（base は 2..36） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_numeric.c:376-401` |
| `times` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/numeric.rb:14-14` |
| `upto` | mrblib: `Ruby def` | max, &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/numeric.rb:24-24` |
| `downto` | mrblib: `Ruby def` | min, &block | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/numeric.rb:34-34` |

## Float

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `+@` | C: `c_float_positive` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:446-449` |
| `-@` | C: `c_float_negative` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:455-459` |
| `**` | C: `c_float_power` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT; if MRBC_USE_MATH | `vendor/mrubyc/src/c_numeric.c:466-476` |
| `abs` | C: `c_float_abs` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:483-488` |
| `to_i` | C: `c_float_to_i` | 位置引数参照なし | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:494-498` |
| `to_f` | C: `c_ineffect` | 0 / c_ineffect は no-op | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:1-541` |
| `clamp` | C: `c_numeric_clamp` | argc != 2 | if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_numeric.c:251-279` |
| `inspect` | C: `c_float_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_FLOAT; if MRBC_USE_STRING | `vendor/mrubyc/src/c_numeric.c:505-516` |
| `to_s` | C: `c_float_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_FLOAT; if MRBC_USE_STRING | `vendor/mrubyc/src/c_numeric.c:505-516` |

## Math

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `acos` | C: `c_math_acos` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:52-55` |
| `acosh` | C: `c_math_acosh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:60-63` |
| `asin` | C: `c_math_asin` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:68-71` |
| `asinh` | C: `c_math_asinh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:76-79` |
| `atan` | C: `c_math_atan` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:84-87` |
| `atan2` | C: `c_math_atan2` | 参照位置 1,2（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:92-95` |
| `atanh` | C: `c_math_atanh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:100-103` |
| `cbrt` | C: `c_math_cbrt` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:108-111` |
| `cos` | C: `c_math_cos` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:116-119` |
| `cosh` | C: `c_math_cosh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:124-127` |
| `erf` | C: `c_math_erf` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:132-135` |
| `erfc` | C: `c_math_erfc` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:140-143` |
| `exp` | C: `c_math_exp` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:148-151` |
| `hypot` | C: `c_math_hypot` | 参照位置 1,2（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:156-159` |
| `ldexp` | C: `c_math_ldexp` | 参照位置 1,2（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:164-176` |
| `log` | C: `c_math_log` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:181-184` |
| `log10` | C: `c_math_log10` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:189-192` |
| `log2` | C: `c_math_log2` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:197-200` |
| `sin` | C: `c_math_sin` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:205-208` |
| `sinh` | C: `c_math_sinh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:213-216` |
| `sqrt` | C: `c_math_sqrt` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:221-224` |
| `tan` | C: `c_math_tan` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:229-232` |
| `tanh` | C: `c_math_tanh` | 参照位置 1（数の検査なし） | if MRBC_USE_FLOAT && MRBC_USE_MATH | `vendor/mrubyc/src/c_math.c:237-240` |

## String

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_string_new` | case 0: / case 1: | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:782-805` |
| `+` | C: `c_string_add` | 参照位置 1（数の検査なし） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:811-820` |
| `*` | C: `c_string_mul` | 参照位置 1（数の検査なし） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:827-849` |
| `size` | C: `c_string_size` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:856-865` |
| `length` | C: `c_string_size` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:856-865` |
| `bytesize` | C: `c_string_bytesize` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:871-874` |
| `to_i` | C: `c_string_to_i` | 0..1（base は 2..36） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:880-894` |
| `to_s` | C: `c_string_to_s` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:917-923` |
| `<<` | C: `c_string_append` | 参照位置 1（数の検査なし） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:929-954` |
| `[]` | C: `c_string_slice` | 1（index/Range）または2（index,length） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1031-1054` |
| `[]=` | C: `c_string_insert` | argc == 2 / argc == 3 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1079-1210` |
| `b` | C: `c_ineffect` | 0 / c_ineffect は no-op | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1-2558` |
| `clear` | C: `c_string_clear` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1229-1232` |
| `chomp` | C: `c_string_chomp` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1216-1223` |
| `chomp!` | C: `c_string_chomp_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1238-1243` |
| `dup` | C: `c_string_dup` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1249-1254` |
| `empty?` | C: `c_string_empty` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1260-1263` |
| `getbyte` | C: `c_string_getbyte` | 参照位置 1（数の検査なし） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1269-1284` |
| `setbyte` | C: `c_string_setbyte` | argc != 2 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1290-1312` |
| `index` | C: `c_string_index` | argc == 1 / argc == 2 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1318-1358` |
| `inspect` | C: `c_string_inspect` | 0（class 表示への委譲で argc を渡す場合あり） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1364-1415` |
| `ord` | C: `c_string_ord` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1421-1453` |
| `byteslice` | C: `c_string_byteslice` | 1（index/Range）または2（index,length） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1060-1073` |
| `slice` | C: `c_string_slice` | 1（index/Range）または2（index,length） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1031-1054` |
| `slice!` | C: `c_string_slice_self` | argc == 1 / argc == 2 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1459-1520` |
| `split` | C: `c_string_split` | argc >= 2 / argc == 0 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1526-1644` |
| `lstrip` | C: `c_string_lstrip` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1650-1657` |
| `lstrip!` | C: `c_string_lstrip_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1663-1668` |
| `rstrip` | C: `c_string_rstrip` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1674-1681` |
| `rstrip!` | C: `c_string_rstrip_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1687-1692` |
| `strip` | C: `c_string_strip` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1698-1705` |
| `strip!` | C: `c_string_strip_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1711-1716` |
| `to_sym` | C: `c_string_to_sym` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1722-1727` |
| `intern` | C: `c_string_to_sym` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:1722-1727` |
| `tr` | C: `c_string_tr` | 2（from,to） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2157-2166` |
| `tr!` | C: `c_string_tr_self` | 2（from,to） | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2172-2183` |
| `start_with?` | C: `c_string_start_with` | argc == 1 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2189-2205` |
| `end_with?` | C: `c_string_end_with` | argc == 1 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2211-2228` |
| `include?` | C: `c_string_include` | argc == 1 | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2234-2243` |
| `bytes` | C: `c_string_bytes` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2249-2262` |
| `upcase` | C: `c_string_upcase` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2268-2273` |
| `upcase!` | C: `c_string_upcase_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2278-2283` |
| `downcase` | C: `c_string_downcase` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2289-2294` |
| `downcase!` | C: `c_string_downcase_self` | 位置引数参照なし | if MRBC_USE_STRING | `vendor/mrubyc/src/c_string.c:2300-2305` |
| `to_f` | C: `c_string_to_f` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_FLOAT | `vendor/mrubyc/src/c_string.c:901-910` |
| `encoding` | C: `c_string_encoding` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2312-2316` |
| `valid_encoding?` | C: `c_string_valid_encoding` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2322-2351` |
| `ascii_only?` | C: `c_string_ascii_only` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2357-2370` |
| `chars` | C: `c_string_chars` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2376-2396` |
| `reverse` | C: `c_string_reverse` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2402-2442` |
| `reverse!` | C: `c_string_reverse_self` | 位置引数参照なし | if MRBC_USE_STRING; if MRBC_USE_STRING_UTF8 | `vendor/mrubyc/src/c_string.c:2448-2488` |
| `each_byte` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:16-16` |
| `each_char` | mrblib: `Ruby def` | 位置引数0（yield は別） | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:28-28` |
| `ljust` | mrblib: `Ruby def` | width, padding = ' ' | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:40-40` |
| `rjust` | mrblib: `Ruby def` | width, padding = ' ' | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:55-55` |
| `each_line` | mrblib: `Ruby def` | rs = "\n", chomp: false | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:70-70` |
| `__ljust_rjust_argcheck` | mrblib: `Ruby def` | width, padding | mrblib 常時 / 依存 C API は構成次第 | `vendor/mrubyc/mrblib/string.rb:89-89` |

[調査索引へ戻る](../README.md)
