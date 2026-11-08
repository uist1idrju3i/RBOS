# C API 索引: values

[所有権と binding 規約](c-api.md)、[API ごとの移譲規則](c-api-ownership.md)を併読してください。宣言を網羅する索引であり、内部 inline も含みます。引数・戻り値の型は原宣言、field は header 全体、条件は [macro 索引](compile-macros.md)を参照します。

## value.h

型・layout: `RBasic`、`RClass`、`RObject`、`VM`。 `vendor/mrubyc/src/value.h:1-800`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `int mrbc_compare(const mrbc_value *v1, const mrbc_value *v2)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:514-514` |
| `mrbc_int_t mrbc_atoi(const char *s, int base)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:515-515` |
| `int mrbc_strcpy(char *dest, int destsize, const char *src)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:516-516` |
| `void mrbc_format_float(char *buf, int bufsiz, mrbc_float_t flo)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/value.h:517-517` |
| `mrbc_int_t mrbc_val_i(struct VM *vm, const mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:518-518` |
| `mrbc_int_t mrbc_val_i2(struct VM *vm, const mrbc_value *val, mrbc_int_t default_value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:519-519` |
| `double mrbc_val_f(struct VM *vm, const mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:520-520` |
| `double mrbc_val_f2(struct VM *vm, const mrbc_value *val, double default_value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:521-521` |
| `const char *mrbc_val_s(struct VM *vm, const mrbc_value *val)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:522-522` |
| `const char *mrbc_val_s2(struct VM *vm, const mrbc_value *val, const char *default_value)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:523-523` |
| `mrbc_int_t mrbc_to_i(struct VM *vm, mrbc_value v[], int argc, mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:524-524` |
| `mrbc_float_t mrbc_to_f(struct VM *vm, mrbc_value v[], int argc, mrbc_value *val)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:525-525` |
| `char *mrbc_to_s(struct VM *vm, mrbc_value v[], int argc, mrbc_value *val)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:526-526` |
| `mrbc_value *mrbc_arg(struct VM *vm, mrbc_value v[], int argc, int n)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:527-527` |
| `mrbc_int_t mrbc_arg_i(struct VM *vm, mrbc_value v[], int argc, int n)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:528-528` |
| `mrbc_int_t mrbc_arg_i2(struct VM *vm, mrbc_value v[], int argc, int n, mrbc_int_t default_value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:529-529` |
| `mrbc_float_t mrbc_arg_f(struct VM *vm, mrbc_value v[], int argc, int n)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:530-530` |
| `mrbc_float_t mrbc_arg_f2(struct VM *vm, mrbc_value v[], int argc, int n, mrbc_float_t default_value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:531-531` |
| `const char *mrbc_arg_s(struct VM *vm, mrbc_value v[], int argc, int n)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:532-532` |
| `const char *mrbc_arg_s2(struct VM *vm, mrbc_value v[], int argc, int n, const char *default_value)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/value.h:533-533` |
| `int mrbc_arg_b(struct VM *vm, mrbc_value v[], int argc, int n)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:534-534` |
| `int mrbc_arg_b2(struct VM *vm, mrbc_value v[], int argc, int n, int default_value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/value.h:535-535` |
| `static inline void mrbc_incref(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/value.h:546-547` |
| `static inline void mrbc_decref(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/value.h:561-562` |
| `static inline void mrbc_decref_empty(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/value.h:579-580` |
| `static inline void mrbc_delete(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/value.h:591-592` |

関連 macro: `GET_ARG`、`GET_ARY_ARG`、`GET_FLOAT_ARG`、`GET_INT_ARG`、`GET_STRING_ARG`、`GET_TT_ARG`、`MRBC_ARG`、`MRBC_ARG_B`、`MRBC_ARG_F`、`MRBC_ARG_I`、`MRBC_ARG_S`、`MRBC_INIT_OBJECT_HEADER`、`MRBC_INIT_OBJECT_HEADER_DI`、`MRBC_ISNUMERIC`、`MRBC_KW_ARG`、`MRBC_KW_ARG_decl1`、`MRBC_KW_ARG_decl2`、`MRBC_KW_DELETE`、`MRBC_KW_DELETE_decl`、`MRBC_KW_DICT`、`MRBC_KW_END`、`MRBC_KW_ISVALID`、`MRBC_KW_MANDATORY`、`MRBC_KW_MANDATORY_decl1`、`MRBC_PTR_TO_UINT32`、`MRBC_TO_F`、`MRBC_TO_FLOAT`、`MRBC_TO_I`、`MRBC_TO_INT`、`MRBC_TO_S`、`MRBC_VAL_F`、`MRBC_VAL_I`、`MRBC_VAL_S`、`MRBC_arg_choice`、`MRBC_each`、`MRBC_each1`、`MRBC_each10`、`MRBC_each11`、`MRBC_each12`、`MRBC_each13`、`MRBC_each14`、`MRBC_each15`、`MRBC_each16`、`MRBC_each17`、`MRBC_each18`、`MRBC_each19`、`MRBC_each2`、`MRBC_each20`、`MRBC_each21`、`MRBC_each22`、`MRBC_each23`、`MRBC_each24`、`MRBC_each25`、`MRBC_each26`、`MRBC_each27`、`MRBC_each28`、`MRBC_each29`、`MRBC_each3`、`MRBC_each30`、`MRBC_each4`、`MRBC_each5`、`MRBC_each6`、`MRBC_each7`、`MRBC_each8`、`MRBC_each9`、`MRBC_each_sel`、`SET_BOOL_RETURN`、`SET_FALSE_RETURN`、`SET_FLOAT_RETURN`、`SET_INT_RETURN`、`SET_NIL_RETURN`、`SET_RETURN`、`SET_TRUE_RETURN`、`mrbc_fixnum`、`mrbc_fixnum_value`、`mrbc_set_fixnum`。

## boxing_no.h

型・layout: `RArray`、`RBasic`、`RClass`、`RException`、`RHash`、`RInstance`、`RObject`、`RProc`、`RRange`、`RString`。 `vendor/mrubyc/src/boxing_no.h:1-122`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `static inline void mrbc_set_integer(mrbc_value *p, mrbc_int_t n)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:81-82` |
| `static inline void mrbc_set_float(mrbc_value *p, mrbc_float_t d)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:87-88` |
| `static inline void mrbc_set_nil(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:93-94` |
| `static inline void mrbc_set_true(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:98-99` |
| `static inline void mrbc_set_false(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:103-104` |
| `static inline void mrbc_set_bool(mrbc_value *p, int n)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:108-109` |
| `static inline void mrbc_set_symbol(mrbc_value *p, mrbc_sym sym_id)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:113-114` |
| `static inline void mrbc_set_tt(mrbc_value *p, mrbc_vtype type)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_no.h:119-120` |

関連 macro: `mrbc_bool_value`、`mrbc_false_value`、`mrbc_float`、`mrbc_float_value`、`mrbc_immediate_value`、`mrbc_immediate_value1`、`mrbc_immediate_value2`、`mrbc_integer`、`mrbc_integer_value`、`mrbc_nil_value`、`mrbc_symbol`、`mrbc_symbol_value`、`mrbc_true_value`、`mrbc_type`。

## boxing_nan.h

型・layout: `RArray`、`RBasic`、`RClass`、`RException`、`RHash`、`RInstance`、`RObject`、`RProc`、`RRange`、`RString`。 `vendor/mrubyc/src/boxing_nan.h:1-183`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `static inline void mrbc_set_integer(mrbc_value *p, mrbc_int_t n)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:139-140` |
| `static inline void mrbc_set_float(mrbc_value *p, mrbc_float_t d)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:145-146` |
| `static inline void mrbc_set_nil(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:150-151` |
| `static inline void mrbc_set_true(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:155-156` |
| `static inline void mrbc_set_false(mrbc_value *p)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:160-161` |
| `static inline void mrbc_set_bool(mrbc_value *p, int n)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:165-166` |
| `static inline void mrbc_set_symbol(mrbc_value *p, mrbc_sym sym_id)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:172-173` |
| `static inline void mrbc_set_tt(mrbc_value *p, mrbc_vtype type)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/boxing_nan.h:178-179` |

関連 macro: `mrbc_bool_value`、`mrbc_false_value`、`mrbc_float`、`mrbc_float_value`、`mrbc_immediate_value`、`mrbc_immediate_value1`、`mrbc_immediate_value2`、`mrbc_integer`、`mrbc_integer_value`、`mrbc_nil_value`、`mrbc_symbol`、`mrbc_symbol_value`、`mrbc_true_value`、`mrbc_type`。

## class.h

型・layout: `IREP`、`MRBC_DEFINE_METHOD_LIST`、`RBuiltinClass`、`RBuiltinNoMethodClass`、`RClass`、`RInstance`、`RKeyValueHandle`、`RMethod`、`VM`。 `vendor/mrubyc/src/class.h:1-350`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_class *mrbc_traverse_class_tree(mrbc_class *cls, mrbc_class *nest_buf[], int *nest_idx)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:232-232` |
| `mrbc_class *mrbc_traverse_class_tree_skip(mrbc_class *nest_buf[], int *nest_idx)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:233-233` |
| `mrbc_class *mrbc_define_class(struct VM *vm, const char *name, mrbc_class *super)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:234-234` |
| `mrbc_class *mrbc_define_class_under(struct VM *vm, const mrbc_class *outer, const char *name, mrbc_class *super)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:235-235` |
| `mrbc_class *mrbc_define_module(struct VM *vm, const char *name)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:236-236` |
| `mrbc_class *mrbc_define_module_under(struct VM *vm, const mrbc_class *outer, const char *name)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:237-237` |
| `void mrbc_define_method(struct VM *vm, mrbc_class *cls, const char *name, mrbc_func_t cfunc)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:238-238` |
| `mrbc_value mrbc_instance_new(struct VM *vm, mrbc_class *cls, int size)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/class.h:239-239` |
| `void mrbc_instance_delete(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:240-240` |
| `void mrbc_instance_setiv(mrbc_value *obj, mrbc_sym sym_id, mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:241-241` |
| `mrbc_value mrbc_instance_getiv(mrbc_value *obj, mrbc_sym sym_id)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/class.h:242-242` |
| `void mrbc_instance_clear_vm_id(mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:243-243` |
| `int mrbc_obj_is_kind_of(const mrbc_value *obj, const mrbc_class *tcls)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/class.h:244-244` |
| `mrbc_class *mrbc_find_method(mrbc_method *r_method, mrbc_class *cls, mrbc_sym sym_id)` | 登録済み情報の借用/出力 | `vendor/mrubyc/src/class.h:245-245` |
| `mrbc_class *mrbc_get_class_by_name(const char *name)` | 登録済み情報の借用/出力 | `vendor/mrubyc/src/class.h:246-246` |
| `mrbc_value mrbc_send(struct VM *vm, mrbc_value *v, int argc, mrbc_value *recv, const char *method_name, int n_params, ...)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/class.h:247-247` |
| `int mrbc_run_mrblib(const void *bytecode)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/class.h:249-249` |
| `void mrbc_init_class(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:250-250` |
| `static inline void mrbc_define_destructor( mrbc_class *cls, void (*destructor)(mrbc_value *) )` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:293-294` |
| `static inline mrbc_value * mrbc_instance_getiv_p(mrbc_value *obj, mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/class.h:310-311` |
| `return mrbc_kv_get( &obj->instance->ivar, sym_id )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/class.h:312-312` |
| `static inline void mrbc_define_method_list(struct VM *vm, mrbc_class *cls, const struct MRBC_DEFINE_METHOD_LIST list[], int list_size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/class.h:340-341` |

関連 macro: `MRBC_CLASS`、`MRBC_INSTANCE_DATA_PTR`、`mrbc_class_object`。

## error.h

型・layout: `RClass`、`RException`、`VM`。 `vendor/mrubyc/src/error.h:1-80`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `mrbc_value mrbc_exception_new(struct VM *vm, struct RClass *exc_cls, const void *message, int len)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/error.h:63-63` |
| `mrbc_value mrbc_exception_new_alloc(struct VM *vm, struct RClass *exc_cls, const void *message, int len)` | 生成/移動/incref 済みの所有分。nil 等即値の場合あり | `vendor/mrubyc/src/error.h:64-64` |
| `void mrbc_exception_delete(mrbc_value *value)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:65-65` |
| `void mrbc_raise(struct VM *vm, struct RClass *exc_cls, const char *msg)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:66-66` |
| `void mrbc_raisef(struct VM *vm, struct RClass *exc_cls, const char *fstr, ...)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:67-67` |
| `void mrbc_clear_exception(struct VM *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:68-68` |
| `void mrbc_print_exception(const mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:69-69` |
| `void mrbc_print_vm_exception(const struct VM *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/error.h:70-70` |

関連 macro: `mrbc_israised`。

## global.h

型・layout: header を参照。 `vendor/mrubyc/src/global.h:1-52`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_init_global(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/global.h:33-33` |
| `int mrbc_set_const(mrbc_sym sym_id, mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/global.h:34-34` |
| `int mrbc_set_class_const(const mrbc_class *cls, mrbc_sym sym_id, mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/global.h:35-35` |
| `mrbc_value *mrbc_get_const(mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/global.h:36-36` |
| `mrbc_value *mrbc_get_class_const(const mrbc_class *cls, mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/global.h:37-37` |
| `void mrbc_get_all_class_const(const mrbc_class *cls, mrbc_value *ret)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/global.h:38-38` |
| `int mrbc_set_global(mrbc_sym sym_id, mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/global.h:39-39` |
| `mrbc_value *mrbc_get_global(mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/global.h:40-40` |
| `void mrbc_global_clear_vm_id(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/global.h:41-41` |
| `void mrbc_debug_dump_const(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/global.h:42-42` |
| `void mrbc_debug_dump_global(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/global.h:43-43` |

関連 macro: なし。

## symbol.h

型・layout: `VM`。 `vendor/mrubyc/src/symbol.h:1-94`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_cleanup_symbol(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/symbol.h:41-41` |
| `mrbc_sym mrbc_str_to_symid(const char *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:42-42` |
| `const char *mrbc_symid_to_str(mrbc_sym sym_id)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/symbol.h:43-43` |
| `mrbc_sym mrbc_search_symid(const char *str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:44-44` |
| `void mrbc_separate_nested_symid(mrbc_sym sym_id, mrbc_sym *id1, mrbc_sym *id2)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/symbol.h:46-46` |
| `mrbc_value mrbc_symbol_new(struct VM *vm, const char *str)` | 即値 symbol（名前は persistent） | `vendor/mrubyc/src/symbol.h:47-47` |
| `void mrbc_debug_dump_symbol(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/symbol.h:48-48` |
| `void mrbc_symbol_statistics(int *total_used)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/symbol.h:49-49` |
| `static inline const char * mrbc_symbol_cstr(const mrbc_value *v)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/symbol.h:58-59` |
| `return mrbc_symid_to_str(v->sym_id)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:60-60` |
| `static inline int mrbc_is_nested_symid(mrbc_sym sym_id)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:71-72` |
| `return mrbc_str_to_symid(str)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:82-82` |
| `return mrbc_symid_to_str(sym_id)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/symbol.h:86-86` |

関連 macro: `MRBC_SYM`。

[調査索引へ戻る](../README.md)
