# allocator・参照 cycle・nRF54L15 の予算

既定値は [configuration](configuration-and-memory.md)、全条件 symbol と定義箇所は [macro 索引](compile-macros.md)。固定値だけから「256 KiB に十分収まる」とは判断しません。

## layout と回収

内蔵 allocator は TLSF/first-fit、pool header、size/flags 付き used block、free-list の next/prev/top と sentinel を持ちます。24-bit/16-bit、FLI/SLI/IGNORE_LSBS、minimum block size、VMID、debug 条件が overhead と容量に影響します。rrt0/VM の小さな allocation も header・丸めが必要です。根拠: `vendor/mrubyc/src/alloc.c:1-1155`。

Ruby heap は refcount で、ゼロで型別 destructor を呼びます。root を走査して参照 cycle を検出する tracing GC はありません。Array/Hash/object が相互参照し全体の外部参照を失っても count が残る構造は回収されません。VMID の free_all や pool 全体 cleanup は条件付きの別機構であり、実行中の一般 cycle collector ではありません。根拠: `vendor/mrubyc/src/value.h:1-800`、`vendor/mrubyc/src/value.c:1-783`、`vendor/mrubyc/src/alloc.c:1-1155`、`vendor/mrubyc/src/vm.c:1-3336`。

String は header+buffer+終端、Array は header+capacity×value、Hash は key/value を並べる buffer、Range は両端 value、instance は header+ivar handle+native data、Proc は self/callinfo/IREP の文脈を持ちます。capacity と stored length を区別し、dup を deep copy とみなしません。根拠: `vendor/mrubyc/src/c_string.h:1-142`、`vendor/mrubyc/src/c_array.h:1-123`、`vendor/mrubyc/src/c_hash.h:1-154`、`vendor/mrubyc/src/c_range.h:1-107`、`vendor/mrubyc/src/class.h:1-350`、`vendor/mrubyc/src/c_proc.h:1-73`。

class/method・動的 symbol の no_free allocation は短命 object の解放と異なります。製品の loop 内で新 class、method、任意の symbol 名を生成し続けない方針にします。根拠: `vendor/mrubyc/src/class.c:1-643`、`vendor/mrubyc/src/symbol.c:1-478`。

## 256 KiB からの見積り順

| 別々に計上するもの | 見積り・計測方法 |
|---|---|
| SD/予約/retention | SDK board の app_ram 境界を正とする。物理 256 KiB 全体を VM pool にしない。[全体メモリ](../architecture/overview.md) |
| C data/bss・stack/IRQ stack | map と high-water。binding/driver queue、BLE/NFC/log buffer を別に確保 |
| TCB + registers | task ごとに sizeof(mrbc_tcb)+regs_size×sizeof(mrbc_value)。値の ABI と Float/debug により sizeof が変わる |
| IREP/pool 補助表 | const bytecode 全体をコピーしなくても RAM 上の metadata は必要。[埋め込み](../dfu/embedded-bytecode.md) |
| 動的 object | 最大 payload、queue に保持する件数、String 連結の一時値、container capacity を考慮 |
| 永続 registry | builtin 初期化、dynamic symbol、class/method/global/constant の増分を測る |
| allocator overhead | header、alignment、fragmentation、minimum block を含める。free 総量だけで最大連続 allocation を保証しない |

根拠: `vendor/mrubyc/src/rrt0.c:1-1585`、`vendor/mrubyc/src/vm.h:1-251`、`vendor/mrubyc/src/load.c:1-440`、`vendor/mrubyc/src/alloc.c:1-1155`。[既存設定](configuration-and-memory.md)の既定 MAX_VM_COUNT=5、REGS=110 を製品の最大同時 task 数の保証とはしません。

mrbc_alloc_statistics の total/used/free/fragmentation と PROF の initial/max/min を、起動後、最大 task/例外発生時、I/O queue 満杯、task 終了後で記録します。cycle のあるケースとないケースを分け、cleanup を呼んで leak を隠しません。libc allocator 構成の値を内蔵 pool と同じ指標と扱わないことも必要です。根拠: `vendor/mrubyc/src/alloc.h:1-160`。

MRBC_USE_FLOAT=1、不要な Math/Unicode/debug を外す構成は候補ですが、製品の数値精度・文字要件・diagnostic を確認して決めます。nRF の sizeof、map、stack、pool 最適値と cycle leak の実測は今回未確認です。Wasm runner の大きな host stack/memory はそのまま採用しません。

[調査索引へ戻る](../README.md)
