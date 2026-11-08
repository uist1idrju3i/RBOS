# 設定とメモリ管理

## vm_config.h の既定値

出典は `vendor/mrubyc/src/vm_config.h:19-153` です。値のない define とコメントアウトされた候補を区別します。

| macro | 既定・状態 | 用途 |
|---|---|---|
| `MAX_VM_COUNT` | 5 | 同時 VM 数。`MRBC_MAX_VM_COUNT` ではない |
| `MAX_REGS_SIZE` | 110 | VM の既定 register 数 |
| `MAX_SYMBOLS_COUNT` | 255 | symbol 数 |
| `MRBC_ALLOC_24BIT` | 有効 | pool 内のサイズ管理。16BIT への変更は相互関係を確認 |
| `MRBC_USE_FLOAT` | 2 | 0:なし、1:float、2:double |
| `MRBC_USE_MATH` | 0 | Math |
| `MRBC_USE_STRING` | 1 | String |
| `MRBC_USE_STRING_UTF8` | 0 | 文字単位の UTF-8 操作 |
| `MRBC_USE_UNICODE_CASE` | 0 | BMP Unicode 大小変換。UTF8 が前提、約 5 KB 増の注記 |
| `MRBC_LITTLE_ENDIAN` | endian 未指定時に有効 | byte order |
| `MRBC_BIG_ENDIAN` | 未指定 | 代替 endian |
| `MRBC_REQUIRE_32BIT_ALIGNMENT` | 無効 | 32-bit 整列要件 |
| `MRBC_REQUIRE_64BIT_ALIGNMENT` | 有効 | 64-bit 整列要件 |
| `MRBC_DEBUG` | NDEBUG がなければ有効 | debug 処理 |
| `MRBC_NO_TIMER` | 無効 | timer を使わない構成 |
| `MRBC_CONVERT_CRLF` | 無効 | console 改行変換 |
| `MRBC_INT64` | 無効 | 64-bit integer |
| `MRBC_SUPPORT_OP_EXT` | 無効 | 拡張 opcode 対応 |
| `MRBC_ALLOC_LIBC` | 無効 | 内蔵 allocator の代わりに libc |
| `MRBC_EXCEPTION_CALL_NEST_LEVEL` | コメント上の既定 8 | 例外の出力深さ |
| `MRBC_INSTANCE_DESTRUCTOR` | 既定 1、定義は class.h | destructor |
| `MRBC_OUT_OF_MEMORY()` | カスタマイズ候補 | 既定はエラー出力・abort |
| `MRBC_ABORT_BY_EXCEPTION(vm)` | カスタマイズ候補 | 致命的例外時の動作 |

追加の既定は `MRBC_SCHEDULER_EXIT=0`（`vendor/mrubyc/src/rrt0.c:28-29`）、`MRBC_TASK_NAME_LEN=15`（`vendor/mrubyc/src/rrt0.h:64-66`）、`MRBC_INSTANCE_DESTRUCTOR=1`（`vendor/mrubyc/src/class.h:36-37`）です。`MRBC_ALLOC_VMID` や `MRBC_USE_ALLOC_PROF` は allocator の条件付き機能で、vm_config.h の既定有効項目ではありません。出典: `vendor/mrubyc/src/alloc.h:45-90`。

RBOS の初期案は Float を 1 にし、必要のない Math/Unicode 機能を増やさず、実用スクリプトでレジスタ・symbol・VM 数を決めることです。これは推奨であり、確定した構成ではありません。

## ヒープの契約

`mrbc_init(void *heap_ptr, unsigned int size)` へ利用者が用意した pool を渡します。allocator は `mrbc_init_alloc(void *ptr, unsigned int size)` で初期化され、4-byte 整列とサイズ上限を検査します。サイズの上限は `MRBC_ALLOC_MEMSIZE_T` に依存するため、ソースの古い「max 64KB」というコメントだけで 24-bit 構成の上限を判断しません。出典: `vendor/mrubyc/src/alloc.c:446-478`。

pool は TCB、register、VM のデータ、Ruby object 等の予算になります。RRAM の const bytecode とは別に、C の stack、BLE 等のバッファを全て pool だけで賄えるとは限りません。TCB と register の確保は `vendor/mrubyc/src/rrt0.c:203-218`、メモリ構成は [全体設計](../architecture/overview.md)を参照してください。

`mrbc_alloc_statistics(struct MRBC_ALLOC_STATISTICS *ret)` は total、used、free、fragmentation を返します。`MRBC_USE_ALLOC_PROF` では initial/max/min を記録する構造体もあります。出典: `vendor/mrubyc/src/alloc.h:35-55,90-100`。タスク数だけではなく、最大スクリプトのロード、例外、再ロード、繰り返し API 呼出の前後で記録します。

## 破棄と将来の再ロード

初期は firmware 埋め込みで、動的再ロードは将来の OpenBlink 範囲です。

`mrbc_cleanup()` は allocator、VM、symbol の cleanup と task queue の初期化を行います。出典: `vendor/mrubyc/src/rrt0.c:845-856`。外部 DMA、timer、BLE callback、native API の handle まで自動解放する保証ではありません。

設計案は、callback の停止、task 終了、native resource の解放、VM cleanup の順序を定め、古い VM ID を権限表から消すことです。bytecode の参照が残る間は入力領域を書き換えず、保存更新と実行を排他します。実機での再ロード試験は未実施です。

[調査索引へ戻る](../README.md)
