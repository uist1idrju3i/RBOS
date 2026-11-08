# C API の所有権と binding の実例

宣言全体は [値・class・例外・symbol](c-api-values.md)、[container](c-api-collections.md)、[VM・allocator・console・rrt0](c-api-runtime.md)。ここでは API を「C の構造体コピーでも参照が増える」と誤解しないための規則にまとめます。C API は mruby の mrb_* API とは別です。

## value と寿命

EMPTY/NIL/FALSE/TRUE/INTEGER/FLOAT/SYMBOL/CLASS/MODULE は refcount の対象外で、OBJECT/PROC/ARRAY/STRING/RANGE/HASH/EXCEPTION は対象です。内部 unwind/break/return 型は利用者の値として組み立てません。FIXNUM は INTEGER と同値です。refcount は uint16_t、incref/decref は assertion で 0/0xffff を検査します。根拠: `vendor/mrubyc/src/value.h:1-800`。

| API / family | 入力と戻り値の所有権 |
|---|---|
| integer/float/nil/boolean/symbol の value macro | 即値。型の生成と field 参照を区別。refcount の増減不要 |
| mrbc_incref / decref / decref_empty | 対象型にだけ作用。decref_empty は型を EMPTY にもする。通常の decref 後の C copy を使用しない |
| SET_RETURN / SET_*_RETURN | 古い v[0] を解放して置換。SET_RETURN は自動 incref しない |
| GET_ARG、mrbc_arg と型別/default 付き取得 | 原引数の借用、または scalar。型別取得の失敗時は vm の例外も確認し直ちに戻る |
| mrbc_instance_new | native data 付き object の所有分1を返す。追加領域の resource 解放は destructor で行う |
| instance_setiv / instance_getiv | set は入力を incref、get も結果を incref。get は borrowed getter ではない |
| define_class/module/under、define_method | class/method は persistent な登録。raw_alloc_no_free を使う経路があり、task ごとに繰返し定義する用途ではない |
| mrbc_get_class_by_name / find_method | 登録済み class/IREP 等を借用。mrbc_find_method は caller の method struct に情報を写す |

出典: `vendor/mrubyc/src/value.h:1-800`、`vendor/mrubyc/src/value.c:1-783`、`vendor/mrubyc/src/class.c:1-643`。destructor は builtin class には同じ方法で設定できません。IRQ で destructor が走る構成も作りません。

## container API ごとの移譲

| API | 規則 |
|---|---|
| array_new/hash_new/string_new/string_new_cstr | 新しい value の所有分1。string_new は src bytes をコピー |
| string_new_alloc | allocator で確保した buf を引き取る。stack/const/DMA 所有 buffer を渡さない |
| array_set/push/unshift/insert | value を構造体コピーし、incref しない。成功後の所有分を container へ移す。借用引数なら先に incref |
| array_push_m | source の複数 element を memcpy、incref しない。二つの container で持つなら element ごとの追加参照が必要 |
| array_get/get_p、hash_get/get_p/search/search_by_id | 借用。値 copy でも incref されない。resize/clear/delete 後の pointer は使わない |
| array_pop/shift/remove、hash_remove/remove_by_id | 除去した値の所有分が caller に移る。hash の key は内部で decref |
| hash_set | key/value の所有分を移す。既存の key/value を解放し構造体代入する |
| array_dup/uniq、hash_dup | 新しい container を返し、共有 element には参照を追加。deep copy ではない |
| array_divide | tail の値を新 container へ移動し、source を短縮する。新 container の所有分を caller が管理 |
| string_dup/add | 新しい String を返す。append/replace/clear は既存 String を変更する |
| range_new | first/last を copy するが incref しない。両端の所有分を range へ渡す |
| range_first/last と *_p | 借用。container の寿命以上に保持しない |
| proc_new | 新 Proc を返す。block は self を incref、IREP/callinfo は VM の文脈に依存。外部 callback に無期限保存しない |
| kv_set | value を移譲。kv_get と iterator は借用。instance/global wrapper の incref の有無と混同しない |
| *_delete / clear / delete_data / delete_handle | delete は直接 destructor を呼ぶ低層 API。通常 value は decref。delete_handle は element の参照を減らさない特殊操作 |
| resize、compare、index、size、include、minmax、*_i_* | scalar は所有分なし。pointer/iterator は対象 container の借用。比較・探索も user object/状態に依存し得る |

実装の根拠: `vendor/mrubyc/src/c_array.c:1-1406`、`vendor/mrubyc/src/c_hash.c:1-747`、`vendor/mrubyc/src/c_string.c:1-2558`、`vendor/mrubyc/src/c_range.c:1-206`、`vendor/mrubyc/src/c_range.h:1-107`、`vendor/mrubyc/src/c_proc.c:1-142`、`vendor/mrubyc/src/keyvalue.c:1-406`。

## その他の C API

| API / family | 規則と注意 |
|---|---|
| set_const/set_class_const/set_global | kv_set 経由の移譲。get_const/get_class_const/get_global は借用 pointer。table は VM ごとの隔離ではない |
| str_to_symid | str を index に保持する経路があり寿命を保つ。symbol_new は新規名を no_free 領域へコピー。symid_to_str/search の返却は借用、解放しない |
| exception_new | value の所有分1。len=0 の非空 message は借用し、len>0 はコピー。new_alloc は buffer を引き取る |
| raise/raisef、clear_exception | vm の例外状態を更新。raise 後の C 制御は自動 longjmp ではなく return/cleanup を自分で行う |
| mrbc_send | C method のみを同期呼出しできる BETA API。Ruby method へは NotImplementedError。引数は作業 register に移され、戻り値は caller の所有分。空き register と VM 文脈が必要 |
| load_mrb/irep_pool_value | bytecode の永続寿命と RAM 上の IREP を区別。pool の String は string_new でコピーして所有分を返し、数値は即値、非対応型は例外と nil |
| raw_alloc/calloc/realloc/free | raw buffer の確保・再確保・解放。realloc 後の旧 pointer を使わない。no_free は個別回収できる通常 allocation と混同しない |
| alloc/free_all、set/get/clear_vm_id | VMID 構成に依存。no-op macro/libc 代替もある。参照 cycle の一般的な tracing GC ではない |
| alloc_statistics / profiling | caller の構造体へ scalar を出力。pool/libc と PROF option で利用可否・値が異なる |
| init/cleanup、vm_open/begin/run/end/close、TCB/task 制御、mutex | VM/TCB の状態と寿命を変える API。単なる value の refcount だけでは資源管理できない。[lifecycle](scheduler-lifecycle.md)参照 |
| console/printf と各 formatter | 入力 value/bytes は借用。asprintf/vasprintf の char** は buffer の確保・拡張があり caller が後始末。printf の全 libc format 互換とは仮定しない |

根拠: `vendor/mrubyc/src/global.c:1-258`、`vendor/mrubyc/src/symbol.c:1-478`、`vendor/mrubyc/src/error.c:1-355`、`vendor/mrubyc/src/class.c:1-643`、`vendor/mrubyc/src/load.c:1-440`、`vendor/mrubyc/src/alloc.h:1-160`、`vendor/mrubyc/src/console.c:1-989`、`vendor/mrubyc/src/rrt0.c:1-1585`。全 API の failure injection・OOM・繰返し leak 試験は未実施です。

## binding の最小 pattern

借用 String をそのまま返す例です。device I/O はここへ直接埋めず backend に委譲します。

```c
static void c_echo(mrbc_vm *vm, mrbc_value v[], int argc)
{
  if (argc != 1 || mrbc_type(v[1]) != MRBC_TT_STRING) {
    mrbc_raise(vm, MRBC_CLASS(ArgumentError), "expected one String");
    return;
  }
  mrbc_value result = v[1];
  mrbc_incref(&result);
  SET_RETURN(result);
}
```

新しい String を作って返す場合は生成した所有分を SET_RETURN へ移し、その後に同じ分を decref しません。array_push へ借用引数を渡す場合も incref が必要です。keyword の DELETE、native resource の解放、system-task 認可、正常/空/誤型/OOM の Ruby 試験は [既存 C API](c-api.md)と [binding skill](../../.agents/skills/ruby-api-binding/SKILL.md)を参照してください。この例を新 API として登録・実行したわけではありません。

[調査索引へ戻る](../README.md)
