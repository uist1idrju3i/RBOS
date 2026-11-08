# Ruby メソッド索引: tasks

[能力と互換性](ruby-first-capabilities.md)を先に読みます。C の引数列は argc 分岐・固定位置参照を示し、CRuby の厳密な arity 検査を保証しません。型・範囲・block・戻り値と副作用は各実装範囲を参照してください。C の登録 table と動的登録、mrblib の def/alias を合わせた一覧です。条件付き機能は [構成](compile-macros.md)に依存します。

## Task

Task.get/current/list/name_list/create は class 呼出しに使います。priority/name/suspend/pass 等には class receiver なら現在 task、instance receiver なら対象 task を選ぶ処理があり、全 method が同じ receiver 規則ではありません。join/value/run/rewind は対象 instance の lifecycle と合わせて [詳細](scheduler-lifecycle.md)を参照してください。new に相当する入口は Task.create です。

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `get` | C: `c_task_get` | argc == 0 | 常時 | `vendor/mrubyc/src/rrt0.c:919-944` |
| `current` | C: `c_task_get` | argc == 0 | 常時 | `vendor/mrubyc/src/rrt0.c:919-944` |
| `list` | C: `c_task_list` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:952-969` |
| `name_list` | C: `c_task_name_list` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:977-993` |
| `name=` | C: `c_task_set_name` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/rrt0.c:1001-1019` |
| `name` | C: `c_task_name` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1028-1040` |
| `priority=` | C: `c_task_set_priority` | 参照位置 1（数の検査なし） | 常時 | `vendor/mrubyc/src/rrt0.c:1049-1072` |
| `priority` | C: `c_task_priority` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1080-1091` |
| `status` | C: `c_task_status` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1099-1116` |
| `suspend` | C: `c_task_suspend` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1125-1136` |
| `resume` | C: `c_task_resume` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1144-1151` |
| `terminate` | C: `c_task_terminate` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1159-1170` |
| `raise` | C: `c_task_raise` | argc == 0 | 常時 | `vendor/mrubyc/src/rrt0.c:1179-1204` |
| `join` | C: `c_task_join` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1212-1220` |
| `value` | C: `c_task_value` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1228-1241` |
| `pass` | C: `c_task_pass` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1249-1255` |
| `create` | C: `c_task_create` | argc >= 1 / argc >= 2 | 常時 | `vendor/mrubyc/src/rrt0.c:1263-1298` |
| `run` | C: `c_task_run` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1306-1314` |
| `rewind` | C: `c_task_rewind` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1322-1330` |

## Mutex

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `new` | C: `c_mutex_new` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1370-1375` |
| `lock` | C: `c_mutex_lock` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1382-1389` |
| `unlock` | C: `c_mutex_unlock` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1396-1403` |
| `try_lock` | C: `c_mutex_trylock` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1410-1414` |
| `locked?` | C: `c_mutex_locked` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1421-1425` |
| `owned?` | C: `c_mutex_owned` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1432-1436` |

## VM

| method | 実装 | 引数数・形式 / argc 分岐 | 構成条件 | 根拠 |
|---|---|---|---|---|
| `tick` | C: `c_vm_tick` | 位置引数参照なし | 常時 | `vendor/mrubyc/src/rrt0.c:1457-1460` |

[調査索引へ戻る](../README.md)
