# C API 索引: collections

[所有権と binding 規約](c-api.md)、[API ごとの移譲規則](c-api-ownership.md)を併読してください。宣言を網羅する索引であり、内部 inline も含みます。引数・戻り値の型は原宣言、field は header 全体、条件は [macro 索引](compile-macros.md)を参照します。

## c_array.h

型・layout: `RArray`。 `vendor/mrubyc/src/c_array.h:1-123`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_array_new(mrbc_vm *vm, int size)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:56-56` |
| `void mrbc_array_delete(mrbc_value *ary)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_array.h:57-57` |
| `void mrbc_array_clear_vm_id(mrbc_value *ary)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_array.h:58-58` |
| `int mrbc_array_resize(mrbc_value *ary, int size)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:59-59` |
| `int mrbc_array_set(mrbc_value *ary, int idx, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:60-60` |
| `mrbc_value mrbc_array_get(const mrbc_value *ary, int idx)` | 借用 value copy（incref なし） | `vendor/mrubyc/src/c_array.h:61-61` |
| `mrbc_value *mrbc_array_get_p(const mrbc_value *ary, int idx)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_array.h:62-62` |
| `int mrbc_array_push(mrbc_value *ary, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:63-63` |
| `int mrbc_array_push_m(mrbc_value *ary, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:64-64` |
| `mrbc_value mrbc_array_pop(mrbc_value *ary)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:65-65` |
| `int mrbc_array_unshift(mrbc_value *ary, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:66-66` |
| `mrbc_value mrbc_array_shift(mrbc_value *ary)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:67-67` |
| `int mrbc_array_insert(mrbc_value *ary, int idx, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:68-68` |
| `mrbc_value mrbc_array_remove(mrbc_value *ary, int idx)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:69-69` |
| `void mrbc_array_clear(mrbc_value *ary)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_array.h:70-70` |
| `int mrbc_array_compare(const mrbc_value *v1, const mrbc_value *v2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:71-71` |
| `void mrbc_array_minmax(mrbc_value *ary, mrbc_value **pp_min_value, mrbc_value **pp_max_value)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_array.h:72-72` |
| `mrbc_value mrbc_array_dup(mrbc_vm *vm, const mrbc_value *ary)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:73-73` |
| `mrbc_value mrbc_array_divide(mrbc_vm *vm, mrbc_value *src, int pos)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:74-74` |
| `int mrbc_array_index(const mrbc_value *ary, const mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:75-75` |
| `mrbc_value mrbc_array_uniq(mrbc_vm *vm, const mrbc_value *ary)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_array.h:76-76` |
| `int mrbc_array_uniq_self(mrbc_value *ary)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:77-77` |
| `static inline int mrbc_array_size(const mrbc_value *ary)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:84-85` |
| `static inline int mrbc_array_include(const mrbc_value *ary, const mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_array.h:97-98` |
| `static inline void mrbc_array_delete_handle(mrbc_value *ary)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_array.h:106-107` |

関連 macro: なし。

## c_hash.h

型・layout: `RHash`、`RHashIterator`。 `vendor/mrubyc/src/c_hash.h:1-154`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_hash_new(mrbc_vm *vm, int size)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_hash.h:70-70` |
| `void mrbc_hash_delete(mrbc_value *hash)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_hash.h:71-71` |
| `mrbc_value *mrbc_hash_search(const mrbc_value *hash, const mrbc_value *key)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_hash.h:72-72` |
| `mrbc_value *mrbc_hash_search_by_id(const mrbc_value *hash, mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_hash.h:73-73` |
| `int mrbc_hash_set(mrbc_value *hash, mrbc_value *key, mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:74-74` |
| `mrbc_value mrbc_hash_get(const mrbc_value *hash, const mrbc_value *key)` | 借用 value copy（incref なし） | `vendor/mrubyc/src/c_hash.h:75-75` |
| `mrbc_value *mrbc_hash_get_p(const mrbc_value *hash, const mrbc_value *key)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_hash.h:76-76` |
| `mrbc_value mrbc_hash_remove(mrbc_value *hash, const mrbc_value *key)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_hash.h:77-77` |
| `mrbc_value mrbc_hash_remove_by_id(mrbc_value *hash, mrbc_sym sym_id)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_hash.h:78-78` |
| `void mrbc_hash_clear(mrbc_value *hash)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_hash.h:79-79` |
| `int mrbc_hash_compare(const mrbc_value *v1, const mrbc_value *v2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:80-80` |
| `mrbc_value mrbc_hash_dup(mrbc_vm *vm, mrbc_value *src)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_hash.h:81-81` |
| `static inline int mrbc_hash_size(const mrbc_value *hash)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:88-88` |
| `static inline void mrbc_hash_clear_vm_id(mrbc_value *hash)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_hash.h:96-96` |
| `static inline int mrbc_hash_resize(mrbc_value *hash, int size)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:104-105` |
| `return mrbc_array_resize(hash, size * 2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:106-106` |
| `static inline mrbc_hash_iterator mrbc_hash_iterator_new( const mrbc_value *v )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:122-123` |
| `static inline int mrbc_hash_i_has_next( mrbc_hash_iterator *ite )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_hash.h:135-136` |
| `static inline mrbc_value *mrbc_hash_i_next( mrbc_hash_iterator *ite )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_hash.h:143-144` |

関連 macro: なし。

## c_string.h

型・layout: `RString`。 `vendor/mrubyc/src/c_string.h:1-142`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_string_new(mrbc_vm *vm, const void *src, int len)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_string.h:61-61` |
| `mrbc_value mrbc_string_new_alloc(mrbc_vm *vm, void *buf, int len)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_string.h:62-62` |
| `void mrbc_string_delete(mrbc_value *str)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_string.h:63-63` |
| `void mrbc_string_clear(mrbc_value *str)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_string.h:64-64` |
| `void mrbc_string_clear_vm_id(mrbc_value *str)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_string.h:65-65` |
| `mrbc_value mrbc_string_dup(mrbc_vm *vm, mrbc_value *s1)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_string.h:66-66` |
| `mrbc_value mrbc_string_add(mrbc_vm *vm, const mrbc_value *s1, const mrbc_value *s2)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_string.h:67-67` |
| `int mrbc_string_append(mrbc_value *s1, const mrbc_value *s2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:68-68` |
| `int mrbc_string_append_cbuf(mrbc_value *s1, const void *s2, int len2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:69-69` |
| `int mrbc_string_index(const mrbc_value *src, const mrbc_value *pattern, int offset)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:70-70` |
| `int mrbc_string_strip(mrbc_value *src, int mode)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:71-71` |
| `int mrbc_string_chomp(mrbc_value *src)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:72-72` |
| `int mrbc_string_upcase(mrbc_value *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:73-73` |
| `int mrbc_string_downcase(mrbc_value *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:74-74` |
| `int mrbc_string_utf8_size(const char *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:75-75` |
| `int mrbc_string_char_size(const char *str, int len)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:76-76` |
| `int mrbc_string_chars2bytes(mrbc_value *src, int off, int idx)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:77-77` |
| `int mrbc_string_bytes2chars(const mrbc_value *src, int byte_index)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:78-78` |
| `static inline mrbc_value mrbc_string_new_cstr(mrbc_vm *vm, const char *src)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_string.h:91-92` |
| `return mrbc_string_new(vm, src, (src ? strlen(src) : 0))` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:93-93` |
| `static inline int mrbc_string_compare(const mrbc_value *v1, const mrbc_value *v2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:100-101` |
| `static inline int mrbc_string_size(const mrbc_value *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:114-115` |
| `static inline char * mrbc_string_cstr(const mrbc_value *v)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_string.h:122-123` |
| `static inline int mrbc_string_append_cstr(mrbc_value *s1, const char *s2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:134-135` |
| `return mrbc_string_append_cbuf( s1, s2, strlen(s2) )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_string.h:136-136` |

関連 macro: なし。

## c_range.h

型・layout: `RRange`。 `vendor/mrubyc/src/c_range.h:1-107`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_range_new(mrbc_vm *vm, mrbc_value *first, mrbc_value *last, int flag_exclude)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_range.h:55-55` |
| `void mrbc_range_delete(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_range.h:56-56` |
| `void mrbc_range_clear_vm_id(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_range.h:57-57` |
| `int mrbc_range_compare(const mrbc_value *v1, const mrbc_value *v2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_range.h:58-58` |
| `static inline mrbc_value mrbc_range_first(const mrbc_value *v)` | 借用 value copy（incref なし） | `vendor/mrubyc/src/c_range.h:66-67` |
| `static inline mrbc_value *mrbc_range_first_p(const mrbc_value *v)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_range.h:74-75` |
| `static inline mrbc_value mrbc_range_last(const mrbc_value *v)` | 借用 value copy（incref なし） | `vendor/mrubyc/src/c_range.h:82-83` |
| `static inline mrbc_value *mrbc_range_last_p(const mrbc_value *v)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/c_range.h:90-91` |
| `static inline int mrbc_range_exclude_end(const mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_range.h:98-99` |

関連 macro: なし。

## c_proc.h

型・layout: `CALLINFO`、`IREP`、`RProc`、`VM`。 `vendor/mrubyc/src/c_proc.h:1-73`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_proc_new(struct VM *vm, void *irep, uint8_t b_or_m)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/c_proc.h:61-61` |
| `void mrbc_proc_delete(mrbc_value *val)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_proc.h:62-62` |
| `void mrbc_proc_clear_vm_id(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_proc.h:63-63` |

関連 macro: なし。

## keyvalue.h

型・layout: `RKeyValue`、`RKeyValueHandle`、`RKeyValueIterator`、`VM`。 `vendor/mrubyc/src/keyvalue.h:1-168`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_kv_handle *mrbc_kv_new(struct VM *vm, int size)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/keyvalue.h:85-85` |
| `int mrbc_kv_init_handle(struct VM *vm, mrbc_kv_handle *kvh, int size)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:86-86` |
| `void mrbc_kv_delete(mrbc_kv_handle *kvh)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/keyvalue.h:87-87` |
| `void mrbc_kv_delete_data(mrbc_kv_handle *kvh)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/keyvalue.h:88-88` |
| `void mrbc_kv_clear_vm_id(mrbc_kv_handle *kvh)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/keyvalue.h:89-89` |
| `int mrbc_kv_resize(mrbc_kv_handle *kvh, int size)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:90-90` |
| `int mrbc_kv_set(mrbc_kv_handle *kvh, mrbc_sym sym_id, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:91-91` |
| `mrbc_value *mrbc_kv_get(mrbc_kv_handle *kvh, mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/keyvalue.h:92-92` |
| `int mrbc_kv_append(mrbc_kv_handle *kvh, mrbc_sym sym_id, mrbc_value *set_val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:93-93` |
| `int mrbc_kv_reorder(mrbc_kv_handle *kvh)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:94-94` |
| `int mrbc_kv_remove(mrbc_kv_handle *kvh, mrbc_sym sym_id)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:95-95` |
| `void mrbc_kv_clear(mrbc_kv_handle *kvh)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/keyvalue.h:96-96` |
| `void mrbc_kv_dup(const mrbc_kv_handle *src, mrbc_kv_handle *dst)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/keyvalue.h:97-97` |
| `static inline int mrbc_kv_size(const mrbc_kv_handle *kvh)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:105-106` |
| `static inline mrbc_kv_iterator mrbc_kv_iterator_new( const mrbc_kv_handle *h )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:122-123` |
| `static inline int mrbc_kv_i_is_first( const mrbc_kv_iterator *ite )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:135-136` |
| `static inline int mrbc_kv_i_has_next( const mrbc_kv_iterator *ite )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/keyvalue.h:143-144` |
| `static inline mrbc_kv *mrbc_kv_i_get( mrbc_kv_iterator *ite )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/keyvalue.h:151-152` |
| `static inline mrbc_kv *mrbc_kv_i_next( mrbc_kv_iterator *ite )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/keyvalue.h:159-160` |

関連 macro: `MRBC_KVH_INITIALIZER`。

[調査索引へ戻る](../README.md)
