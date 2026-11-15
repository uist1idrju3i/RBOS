# コンパイル時に結合する bytecode

## 初期構成

この文書は初期設計の記録です。現在は const 配列の生成・結合機構があり、host/Wasm と四 profile の build による確認は [P4/A1 の受け入れ記録](../implementation/p4-host-acceptance.md)を参照してください。[2026-11-15 の照合](../implementation/session-plan-review.md)は当時の履歴です。将来の ZMS 保存については[直接参照と寿命の再確認](zms-direct-execution.md)に分けました。初期の firmware DFU 方針は変更していません。

2026-11-08 JST の更新方針では、vendor/mruby の mrbc 4.0.0 で Ruby をコンパイルし、const 配列として firmware に結合します。storage へ保存せず、RAM への全体コピーも行いません。更新は firmware single-bank DFU のみです。BLE 転送・保存・reload は [将来計画](../openblink/future-support.md)へ移します。

## 生成と結合

mrbc の `-B<symbol>` は const uint8_t の C 配列を生成します。出典: `vendor/mruby/mrbgems/mruby-bin-mrbc/tools/mrbc/mrbc.c:35-49`、`vendor/mruby/src/dump.c:951-975`（生成処理は同ファイルの mrb_dump_irep_cfunc）。次は vendor/mruby 内で実行する計画例で、RBOS の build target はまだありません。

```sh
MRUBY_CONFIG=build_config/mrbc.rb ruby minirake
bin/mrbc -Bsystem_bytecode -o system_bytecode.c system.rb
```

mrbc 専用設定: `vendor/mruby/build_config/mrbc.rb:1-10`。入力 Ruby、compiler SHA、生成オプション、生成物 hash を記録し、生成した C を app に link する設計とします。

## 参照するものと RAM に置くもの

| 対象 | 固定 mruby/c の処理 |
|---|---|
| 入力 | mrbc_create_task が mrbc_load_mrb に渡し、RITE0400 を検査 |
| 命令・catch table | irep.inst は入力内を参照。VM 命令ポインタも同領域を指す |
| pool | irep.pool は入力内を参照 |
| IREP と補助表 | IREP、symbol ID、pool offset、子 IREP pointer は allocator から RAM に確保 |
| symbol 文字列 | 通常は入力を参照。flag_permanence == 1 なら no-free RAM にコピー |
| Ruby String | pool の使用時に mrbc_string_new で object とデータを RAM に作る |
| 実行状態 | TCB、VM、register、stack、Ruby object は RAM が必要 |

出典: `vendor/mrubyc/src/rrt0.c:229-275`、`vendor/mrubyc/src/load.c:75-90,131-258,272-342,398-412`、`vendor/mrubyc/src/vm.c:2648-2660`、`vendor/mrubyc/src/c_string.c:64-99`、`vendor/mrubyc/src/symbol.c:167-196,221-233`。全体コピー不要と RAM 不要は別です。

loader は const 入力を読み、新規 IREP/補助表だけを書き換えます。free 対象も IREP で、入力 blob を解放しません。出典: `vendor/mrubyc/src/load.c:131-258,350-362`。VM も命令を読み出します。`vendor/mrubyc/src/vm.c:3300-3335`。したがって、読み出し可能な RRAM の const blob を保持して実行する構成は可能と判断します。実機の link 配置・動作は未確認です。

## alignment と寿命

整数変換は設定によって直接 dereference と byte ごとの読み出しを切り替え、double は64-bit alignment の設定も参照します。出典: `vendor/mrubyc/src/value.h:603-757`。先頭を整列しても内部 field 全てが整列するとは限りません。nRF54L15 の unaligned access 条件と macro を照合して決めます。

const 配列は RRAM の読み出し専用 section に配置し map で確認します。symbol/method を含む全ての参照がなくなるまで入力を保持します。初期は firmware と同じ寿命です。DFU は再起動して独立 loader で行い、旧 VM が参照中の blob を更新しません。

## 未実施の受け入れ条件

以下は初期の未実施一覧です。現在は固定 compiler・const の正常/空/拒否/OOM 終了・String 不変を host_wasm、FLASH 内の非 writable section と byte 一致を bm_build で検査しています。IREP・symbol・String 等も空・製品 Button で Wasm 計測済みです。実機の pointer/alignment、RAM high-water、OOM 後の復旧、DFU と、FLASH `PT_LOAD` が RWE である点は [Phase B の残件](../implementation/p4-host-acceptance.md#phase-b-に残す確認)です。下記を実機まで完了したものとは扱いません。

- 固定 compiler 生成の RITE0400 が対象 VM で動く。
- map/debugger で RRAM 配置と全体コピーの不在を確認する。
- IREP、symbol、String、register の RAM を別々に測る。
- String 変更で const blob が変わらないことを確認する。
- 不正 RITE、OOM、task 作成失敗を扱う。未検証の外部 bytecode は初期に読み込まない。

[調査索引へ戻る](../README.md)
