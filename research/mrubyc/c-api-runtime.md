# C API 索引: runtime

[所有権と binding 規約](c-api.md)、[API ごとの移譲規則](c-api-ownership.md)を併読してください。宣言を網羅する索引であり、内部 inline も含みます。引数・戻り値の型は原宣言、field は header 全体、条件は [macro 索引](compile-macros.md)を参照します。

## alloc.h

型・layout: `MRBC_ALLOC_PROF`、`MRBC_ALLOC_STATISTICS`、`VM`。 `vendor/mrubyc/src/alloc.h:1-160`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_init_alloc(void *ptr, unsigned int size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:66-66` |
| `void mrbc_cleanup_alloc(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:67-67` |
| `void *mrbc_raw_alloc(unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:68-68` |
| `void *mrbc_raw_alloc_no_free(unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:69-69` |
| `void *mrbc_raw_calloc(unsigned int nmemb, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:70-70` |
| `void mrbc_raw_free(void *ptr)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:71-71` |
| `void *mrbc_raw_realloc(void *ptr, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:72-72` |
| `unsigned int mrbc_alloc_usable_size(void *ptr)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/alloc.h:75-75` |
| `void *mrbc_alloc(const struct VM *vm, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:79-79` |
| `void *mrbc_calloc(const struct VM *vm, unsigned int nmemb, unsigned int size)` | raw 所有 buffer / ゼロ初期化。対応する free が必要 | `vendor/mrubyc/src/alloc.h:80-80` |
| `void mrbc_free_all(const struct VM *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:81-81` |
| `void mrbc_set_vm_id(void *ptr, int vm_id)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:82-82` |
| `int mrbc_get_vm_id(void *ptr)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/alloc.h:83-83` |
| `void mrbc_alloc_statistics(struct MRBC_ALLOC_STATISTICS *ret)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:92-92` |
| `void mrbc_alloc_start_profiling(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:93-93` |
| `void mrbc_alloc_stop_profiling(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:94-94` |
| `void mrbc_alloc_get_profiling(struct MRBC_ALLOC_PROF *prof)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:95-95` |
| `void mrbc_alloc_print_statistics(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:96-96` |
| `void mrbc_alloc_print_pool_header(void *pool_header)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:97-97` |
| `void mrbc_alloc_print_memory_block(void *pool_header)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:98-98` |
| `void mrbc_alloc_print_memory_pool(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:99-99` |
| `static inline void mrbc_init_alloc(void *ptr, unsigned int size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:111-111` |
| `static inline void mrbc_cleanup_alloc(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:112-112` |
| `static inline void *mrbc_raw_alloc(unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:113-113` |
| `static inline void *mrbc_raw_alloc_no_free(unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:116-116` |
| `static inline void *mrbc_raw_calloc(unsigned int nmemb, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:119-119` |
| `static inline void mrbc_raw_free(void *ptr)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:122-122` |
| `static inline void *mrbc_raw_realloc(void *ptr, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:125-125` |
| `static inline void mrbc_free(const struct VM *vm, void *ptr)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:137-137` |
| `static inline void * mrbc_realloc(const struct VM *vm, void *ptr, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:140-140` |
| `static inline void *mrbc_alloc(const struct VM *vm, unsigned int size)` | raw 所有 buffer / no_free・realloc の条件あり | `vendor/mrubyc/src/alloc.h:143-143` |
| `static inline void mrbc_free_all(const struct VM *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:146-146` |
| `static inline void mrbc_set_vm_id(void *ptr, int vm_id)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/alloc.h:148-148` |
| `static inline int mrbc_get_vm_id(void *ptr)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/alloc.h:150-150` |

関連 macro: `mrbc_alloc`、`mrbc_free`、`mrbc_free_all`、`mrbc_get_vm_id`、`mrbc_realloc`、`mrbc_set_vm_id`。

## load.h

型・layout: `IREP`。 `vendor/mrubyc/src/load.h:1-52`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `int mrbc_load_mrb(mrbc_vm *vm, const void *bytecode)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/load.h:40-40` |
| `int mrbc_load_irep(mrbc_vm *vm, const void *bytecode)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/load.h:41-41` |
| `void mrbc_irep_free(mrbc_irep *irep)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/load.h:42-42` |
| `mrbc_value mrbc_irep_pool_value(mrbc_vm *vm, int n)` | pool 型による即値/生成 value | `vendor/mrubyc/src/load.h:43-43` |

関連 macro: なし。

## vm.h

型・layout: `CALLINFO`、`IREP`、`IREP_CATCH_HANDLER`、`RClass`、`RHash`、`RProc`、`VM`。 `vendor/mrubyc/src/vm.h:1-251`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_cleanup_vm(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/vm.h:183-183` |
| `mrbc_callinfo *mrbc_push_callinfo(mrbc_vm *vm, mrbc_sym method_id, int reg_offset, int n_args)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/vm.h:184-184` |
| `void mrbc_pop_callinfo(mrbc_vm *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/vm.h:185-185` |
| `mrbc_vm *mrbc_vm_new(int regs_size)` | 新規確保。lifecycle 参照 | `vendor/mrubyc/src/vm.h:186-186` |
| `mrbc_vm *mrbc_vm_open(mrbc_vm *vm)` | caller 提供領域または内部確保。lifecycle 参照 | `vendor/mrubyc/src/vm.h:187-187` |
| `void mrbc_vm_begin(mrbc_vm *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/vm.h:188-188` |
| `void mrbc_vm_end(mrbc_vm *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/vm.h:189-189` |
| `void mrbc_vm_close(mrbc_vm *vm)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/vm.h:190-190` |
| `int mrbc_vm_run(mrbc_vm *vm)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/vm.h:191-191` |
| `static inline mrbc_value * mrbc_get_self( mrbc_vm *vm, mrbc_value *regs )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/vm.h:203-204` |
| `static inline mrbc_sym mrbc_get_callee_symid( const mrbc_vm *vm )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/vm.h:215-216` |
| `static inline const char *mrbc_get_callee_name( const mrbc_vm *vm )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/vm.h:227-228` |
| `return mrbc_symid_to_str( vm->callee_sym_id )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/vm.h:229-229` |
| `static inline int mrbc_c_block_given( mrbc_vm *vm, mrbc_value v[], int argc )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/vm.h:241-242` |

関連 macro: `mrbc_irep_child_irep`、`mrbc_irep_pool_ptr`、`mrbc_irep_symbol_cstr`、`mrbc_irep_symbol_id`、`mrbc_irep_tbl_ireps`、`mrbc_irep_tbl_pools`、`mrbc_irep_tbl_syms`。

## rrt0.h

型・layout: `MrbcTaskReason`、`MrbcTaskState`、`RMutex`、`RTcb`、`VM`。 `vendor/mrubyc/src/rrt0.h:1-156`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_tick(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:114-114` |
| `mrbc_tcb *mrbc_tcb_new(int regs_size, enum MrbcTaskState task_state, int priority)` | 新規確保。lifecycle 参照 | `vendor/mrubyc/src/rrt0.h:115-115` |
| `mrbc_tcb *mrbc_create_task(const void *byte_code, mrbc_tcb *tcb)` | caller 提供 TCB または NULL 時の内部確保。lifecycle 参照 | `vendor/mrubyc/src/rrt0.h:116-116` |
| `int mrbc_delete_task(mrbc_tcb *tcb)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:117-117` |
| `void mrbc_set_task_name(mrbc_tcb *tcb, const char *name)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:118-118` |
| `mrbc_tcb *mrbc_find_task(const char *name)` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/rrt0.h:119-119` |
| `int mrbc_start_task(mrbc_tcb *tcb)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:120-120` |
| `int mrbc_run(void)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:121-121` |
| `void mrbc_sleep_ms(mrbc_tcb *tcb, uint32_t ms)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:122-122` |
| `void mrbc_relinquish(mrbc_tcb *tcb)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:123-123` |
| `void mrbc_change_priority(mrbc_tcb *tcb, int priority)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:124-124` |
| `void mrbc_suspend_task(mrbc_tcb *tcb)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:125-125` |
| `void mrbc_resume_task(mrbc_tcb *tcb)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:126-126` |
| `void mrbc_terminate_task(mrbc_tcb *tcb)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:127-127` |
| `void mrbc_join_task(mrbc_tcb *tcb, const mrbc_tcb *tcb_join)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:128-128` |
| `mrbc_mutex *mrbc_mutex_init(mrbc_mutex *mutex)` | caller 提供領域または内部確保。lifecycle 参照 | `vendor/mrubyc/src/rrt0.h:129-129` |
| `int mrbc_mutex_lock(mrbc_mutex *mutex, mrbc_tcb *tcb)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:130-130` |
| `int mrbc_mutex_unlock(mrbc_mutex *mutex, mrbc_tcb *tcb)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:131-131` |
| `int mrbc_mutex_trylock(mrbc_mutex *mutex, mrbc_tcb *tcb)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/rrt0.h:132-132` |
| `void mrbc_cleanup(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:133-133` |
| `void mrbc_init(void *heap_ptr, unsigned int size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/rrt0.h:134-134` |
| `static inline mrbc_tcb * mrbc_get_tcb( const mrbc_vm *vm )` | 借用 pointer（元の引数/VM/registry の寿命内） | `vendor/mrubyc/src/rrt0.h:147-148` |

関連 macro: なし。

## console.h

型・layout: `RPrintf`、`RPrintfFormat`。 `vendor/mrubyc/src/console.h:1-184`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_putchar(char c)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:77-77` |
| `void mrbc_print_symbol(mrbc_sym sym_id)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:78-78` |
| `void mrbc_nprint(const char *str, int size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:79-79` |
| `void mrbc_printf(const char *fstr, ...)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:80-80` |
| `void mrbc_asprintf(char **buf, int bufsiz, const char *fstr, ...)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:81-81` |
| `void mrbc_snprintf(char *buf, int bufsiz, const char *fstr, ...)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:82-82` |
| `void mrbc_vprintf(const char *fstr, va_list ap)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:83-83` |
| `void mrbc_vasprintf(char **buf, int bufsiz, const char *fstr, va_list ap)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:84-84` |
| `void mrbc_p(const mrbc_value *v)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:85-85` |
| `void mrbc_char_to_s(char *buf, const void *src)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:86-86` |
| `int mrbc_p_sub(const mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:87-87` |
| `int mrbc_puts_sub(const mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:88-88` |
| `int mrbc_print_sub(const mrbc_value *v)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:89-89` |
| `void mrbc_printf_replace_buffer(mrbc_printf_t *pf, char *buf, int size)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:90-90` |
| `int mrbc_printf_main(mrbc_printf_t *pf)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:91-91` |
| `int mrbc_printf_char(mrbc_printf_t *pf, int ch)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:92-92` |
| `int mrbc_printf_bstr(mrbc_printf_t *pf, const char *str, int len, int pad)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:93-93` |
| `int mrbc_printf_int(mrbc_printf_t *pf, mrbc_int_t value, unsigned int base)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:94-94` |
| `int mrbc_printf_bit(mrbc_printf_t *pf, mrbc_int_t value, int bit)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:95-95` |
| `int mrbc_printf_float(mrbc_printf_t *pf, double value)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:96-96` |
| `int mrbc_printf_pointer(mrbc_printf_t *pf, void *ptr)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:97-97` |
| `static inline void mrbc_print(const char *str)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:108-109` |
| `static inline void mrbc_printf_init( mrbc_printf_t *pf, char *buf, int size,                                      const char *fstr )` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:122-124` |
| `static inline void mrbc_printf_clear( mrbc_printf_t *pf )` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:137-138` |
| `static inline void mrbc_printf_end( mrbc_printf_t *pf )` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/console.h:148-149` |
| `static inline int mrbc_printf_len( mrbc_printf_t *pf )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:160-161` |
| `static inline int mrbc_printf_str( mrbc_printf_t *pf, const char *str, int pad )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:176-177` |
| `return mrbc_printf_bstr( pf, str, (str ? strlen(str) : 0), pad )` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/console.h:178-178` |

関連 macro: なし。

## mrubyc.h

型・layout: header を参照。 `vendor/mrubyc/src/mrubyc.h:1-45`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|

関連 macro: なし。

## c_object.h

型・layout: header を参照。 `vendor/mrubyc/src/c_object.h:1-45`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_instance_call_initialize(mrbc_vm *vm, mrbc_value v[], int argc)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_object.h:34-34` |
| `void mrbc_object_inspect(mrbc_vm *vm, mrbc_value v[], int argc)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_object.h:35-35` |

関連 macro: なし。

## c_numeric.h

型・layout: header を参照。 `vendor/mrubyc/src/c_numeric.h:1-31`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `int mrbc_utf8_encode(int32_t codepoint, char *buf)` | scalar/struct copy。iterator 等の参照先は借用 | `vendor/mrubyc/src/c_numeric.h:26-26` |

関連 macro: なし。

## c_math.h

型・layout: header を参照。 `vendor/mrubyc/src/c_math.h:1-30`

| API 宣言 | 戻り値の所有権分類（引数の移譲は所有権文書） | 根拠 |
|---|---|---|
| `void mrbc_init_module_math(void)` | 戻り値なし。引数/VM の変更・解放は所有権文書 | `vendor/mrubyc/src/c_math.h:23-23` |

関連 macro: なし。

[調査索引へ戻る](../README.md)
