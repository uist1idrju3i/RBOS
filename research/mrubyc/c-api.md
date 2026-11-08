# Ruby と C の値の受け渡し

全宣言の索引は [値・class・例外・symbol](c-api-values.md)、[container](c-api-collections.md)、[runtime](c-api-runtime.md)。[API ごとの所有権](c-api-ownership.md)と binding の実例を併読してください。ここは最初に読む契約と設計案に絞ります。

## クラス・モジュール・メソッド

以下の宣言が固定版に存在します。出典: `vendor/mrubyc/src/class.h:234-246`。

```c
mrbc_class *mrbc_define_class(struct VM *vm, const char *name, mrbc_class *super);
mrbc_class *mrbc_define_class_under(struct VM *vm, const mrbc_class *outer,
                                  const char *name, mrbc_class *super);
mrbc_class *mrbc_define_module(struct VM *vm, const char *name);
mrbc_class *mrbc_define_module_under(struct VM *vm, const mrbc_class *outer,
                                   const char *name);
void mrbc_define_method(struct VM *vm, mrbc_class *cls, const char *name,
                        mrbc_func_t cfunc);
mrbc_class *mrbc_get_class_by_name(const char *name);
mrbc_value mrbc_instance_new(struct VM *vm, mrbc_class *cls, int size);
void mrbc_instance_setiv(mrbc_value *obj, mrbc_sym sym_id, mrbc_value *v);
mrbc_value mrbc_instance_getiv(mrbc_value *obj, mrbc_sym sym_id);
```

`mrbc_instance_new` の size は追加 native data のサイズです。setiv/getiv は内部で incref するので、取得結果を所有するか、返却へ移すかを整理します。存在しない instance variable は nil です。出典: `vendor/mrubyc/src/class.c:298-368`。

class を作るだけでは system-task 専用になりません。全ての特権 callback の入口で caller VM を確認する設計が必要です。[OpenBlink の権限パターン](../openblink/api-binding-patterns.md)を参照してください。

## 引数・戻り値

native callback の基本形は `void callback(mrbc_vm *vm, mrbc_value v[], int argc)` です。`v[0]` は receiver と戻り値、位置引数は `v[1]` 以降です。出典: `vendor/mrubyc/src/value.h:197-263`、`vendor/mrubyc/sample_c/sample_myclass.c:1-80`。

| API | 役割・注意 |
|---|---|
| `GET_ARG(n)` | `v[n]` の値。型・argc 検査はしない |
| `GET_INT_ARG(n)` | integer の union field。Float を整数変換する API ではない |
| `mrbc_integer(value)` / `mrbc_float(value)` | 値からの取り出し。生成ではない |
| `mrbc_integer_value(n)` / `mrbc_float_value(vm,n)` | 値を生成 |
| `SET_RETURN(value)` | 古い v[0] を decref して代入。自動 incref はしない |
| `SET_INT_RETURN(n)` / `SET_FLOAT_RETURN(n)` | 数値を戻す |
| `SET_NIL_RETURN()` / `SET_BOOL_RETURN(n)` | nil / boolean を戻す |
| `SET_TRUE_RETURN()` / `SET_FALSE_RETURN()` | true / false を戻す |

出典: `vendor/mrubyc/src/value.h:175-263`。GET 系には非推奨の注記があります。新しい `mrbc_arg` / `mrbc_arg_i` / `mrbc_arg_f` / `mrbc_arg_s` / `mrbc_arg_b` と default 付き版も存在します。出典: 同 `vendor/mrubyc/src/value.h:525-536`。RBOS は argc、型、範囲を明示的に規定して、成功と入力エラーを分離する案です。

## 文字列・配列・Hash

| 生成 API | 対応ヘッダ |
|---|---|
| `mrbc_string_new(mrbc_vm *vm, const void *src, int len)` | `vendor/mrubyc/src/c_string.h:61-62` |
| `mrbc_string_new_cstr(mrbc_vm *vm, const char *src)` | 同 `vendor/mrubyc/src/c_string.h:91-94` |
| `mrbc_array_new(mrbc_vm *vm, int size)` | `vendor/mrubyc/src/c_array.h:56-68` |
| `mrbc_hash_new(mrbc_vm *vm, int size)` | `vendor/mrubyc/src/c_hash.h:70-79` |

文字列を binary blob として使う場合は NUL 終端ではなく size で扱います。`mrbc_string_new_alloc` は所有するバッファの扱いが異なるので、stack 上や DMA 再利用予定の領域を渡さない設計にします。各 setter/getter がコピーするのか参照を持つのかを実装で確認してから使用します。

## 所有権とエラー

`mrbc_incref(mrbc_value *v)` と `mrbc_decref(mrbc_value *v)` は参照カウントを操作し、ゼロで型別の削除関数を呼びます。出典: `vendor/mrubyc/src/value.h:546-572`。単なる C の構造体コピーは参照カウントを増やしません。

実装時は各値を「借用」「所有」「戻り値へ移譲」に分類します。借用引数を `SET_RETURN` で返す場合は必要な参照を確保し、生成した値を戻した後に同じ所有分を再度 decref しないようにします。container への追加時は API ごとの ownership を確認し、解放漏れと二重解放の両方を試験します。

例外 API は `void mrbc_raise(struct VM *vm, struct RClass *exc_cls, const char *msg)` と `mrbc_raisef(..., const char *fstr, ...)` です。出典: `vendor/mrubyc/src/error.h:66-67`。例外を設定した後の C 処理を継続しないよう、資源の解放と return を明記します。容量不足を無視して不完全な戻り値を使う設計にはしません。

## keyword 引数

| macro | 契約 |
|---|---|
| `MRBC_KW_ARG(a,b)` | keyword 値を取り出す |
| `MRBC_KW_MANDATORY(a)` | 必須値を検査。不足は ArgumentError |
| `MRBC_KW_ISVALID(a)` | 省略の有無を判定。任意値の既定値は自分で設定 |
| `MRBC_KW_END()` | 余分な keyword を拒否 |
| `MRBC_KW_DICT(dict)` | 残りを Hash として受ける |
| `MRBC_KW_DELETE(a,b,dict)` | 取り出した値を cleanup |

出典: `vendor/mrubyc/doc/c_KeywordArgument.md:1-132`、`vendor/mrubyc/src/value.h:427-449`。`MRBC_KW_OPTIONAL` は存在せず、任意引数は ISVALID で扱います。途中でエラーになっても DELETE を通る制御にします。keyword が正しくても値の型や GPIO 範囲は別に検査します。

## RBOS の API 試験

通常値、引数なし、nil、型違い、境界外、巨大な配列、埋め込み NUL、未知 keyword、storage busy、非特権 VM、終了済み VM を対象にします。戻り値と例外の契約を Ruby 側から検証し、ヒープ統計を比較して繰り返し呼出時の漏れを調べます。これらは未実施の実装要件です。

[調査索引へ戻る](../README.md)
