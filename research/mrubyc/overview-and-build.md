# mruby/c のバージョン、ビルド、バイトコード

[Ruby-first の能力と制約](ruby-first-capabilities.md)から method 索引へ進めます。全命令は [opcode 比較](opcode-compatibility.md)、上流 Makefile/HAL/sample/test は [実行手順と棚卸し](tests-and-samples.md)、公式資料との相違は [照合記録](official-document-comparison.md)へ分離しました。小さな Wasm 実行結果は [能力確認](capability-probes.md)にあります。

## 固定する組み合わせ

mruby/c は小さい VM と限定したクラス群を提供する mruby の別実装です。README の RAM 比較値は代表値で、RBOS のヒープ上限を保証する値ではありません。出典: `vendor/mrubyc/README.md:7-19`。

| 項目 | 調査値 | 出典 |
|---|---|---|
| `MRUBYC_VERSION` | `4.0.0` | `vendor/mrubyc/mrblib/global.rb:13` |
| `MRUBY_VERSION` | `4.0.0` | 同 `vendor/mrubyc/mrblib/global.rb:12` |
| `RUBY_VERSION` | `4.0` | 同 `vendor/mrubyc/mrblib/global.rb:11` |
| 読み込む RITE 版 | `0400` | `vendor/mrubyc/src/load.c:30-34,77-86` |

RBOS の設計では **vendor/mruby 4.0.0 の mrbc**（831da26b9021de0369d17b71b5667e2941a1a32d）を host tool として固定します。生成物は [const 配列](../dfu/embedded-bytecode.md)として firmware に結合します。Ruby のホスト実行系、mrbc、mruby/c VM は別の部品です。OpenBlink の RITE0300 配列や、Task 文書にある RITE0300 の例をそのまま使わず、対象版で再コンパイルします。根拠: `vendor/mrubyc/doc/task_class.md:50-69`、`vendor/mrubyc/src/load.c:77-86`。

## 上流のホスト向け手順

以下は **mruby/c 上流のサンプルを調べる手順**であり、RBOS のボード向けビルド手順ではありません。必要な C コンパイラ、make、Ruby、mrbc を事前に用意し、mrbc のバージョンを記録します。

```sh
make -C vendor/mrubyc
mrbc -o user.mrb user.rb
vendor/mrubyc/sample_c/sample_scheduler user.mrb
```

上流は top-level `make` で `src/libmrubyc.a` とサンプルを生成します。出典: `vendor/mrubyc/doc/compile.md:1-27,86-99`。この調査では上記を実行していません。自動生成ヘッダを作り直す `make autogen` は Unicode データの取得を伴うことがあるため、再現用ビルドでは入力とハッシュも固定します。同 `vendor/mrubyc/doc/compile.md:29-74`、`vendor/mrubyc/src/Makefile:168-175`。

## C サンプルの使い分け

| ファイル | 目的 |
|---|---|
| `sample_include.c` | 内蔵 bytecode を使う最小構成 |
| `sample_include_bytecode.c` / `.rb` | Ruby を C 配列として組み込む参照例 |
| `sample_no_scheduler.c` | rrt0 を使わず単独 VM の lifecycle を扱う |
| `sample_scheduler.c` | bytecode から task を作り rrt0 で動かす |
| `sample_concurrent.c` | 複数 `.mrb` から task を作り同時実行する |
| `sample_myclass.c` | C でクラスとメソッドを定義する |

出典: `vendor/mrubyc/doc/compile.md:11-27`、`vendor/mrubyc/sample_c/sample_concurrent.c:41-70`、`vendor/mrubyc/sample_c/sample_include_bytecode.c:1-13`。特に `sample_concurrent` はスケジューラを使わない例ではなく、`mrbc_init` → `mrbc_create_task` → `mrbc_run` の例です。

## 文書の対象

| 上流文書 | RBOS で確認する内容 |
|---|---|
| `doc/task_class.md` | Ruby の Task API、停止・再開・優先度 |
| `doc/How_to_make_your_own_HAL.md` | 自作 HAL を指定してライブラリを作る方法 |
| `doc/c_KeywordArgument.md` | keyword の必須・任意・残余・解放 |
| `doc/compile.md` | ホストビルド、生成物、mrbc の利用 |
| `doc/test.md` | ホスト側の回帰試験 |

各文書全体を参照し、実際の仕様との違いはヘッダと実装で補います。HAL の関数契約は文書だけでは揃わないため、[HAL 移植](hal-porting.md)へ分離します。

## 実装前に固定するもの

- mrbc 配布物の版・ハッシュ・入手方法と、対応するホスト OS。
- bytecode の最大サイズ、許可する形式、機能フラグの組み合わせ。
- 自動生成ファイルの更新方法と、生成に使う Ruby・Unicode データ。
- 「コンパイルできる」と「対象 VM がロード・実行できる」を分けた CI 試験。

これらは RBOS の未実装要件です。バイトコードの署名や権限制御はコンパイラ版の固定だけでは成立しません。

## vendor 追加の採否

mruby は旧版からの bump ではなく新規追加です。変更点の根拠は `vendor/mruby/doc/mruby4.0.md:1-155,347-367`。RITE0400 の compiler と mrbc 専用 build 設定（`vendor/mruby/build_config/mrbc.rb:1-10`）を採用します。

| 分類 | 採否と対応 |
|---|---|
| 破壊的変更 | 旧 C API 名や presym 設定の変更は mruby runtime 側。firmware の mruby/c API と混同しない |
| security | codegen、loader、bigint、IO 等の修正が列挙される。固定 compiler を使い、mruby/c に同じ修正が入ったとは扱わない |
| 新機能・option・既定値 | pattern matching、新 opcode、ROM method table、mruby-task 等がある。compiler 版だけで mruby/c の全機能対応とはせず、実行試験を要求。mruby runtime/gem は採用しない |
| license | MIT。新規追加であり旧 mruby 版との差はない。許諾文を保持 |

独立 MCUboot の削除は実行版を独自更新するためではなく、SDK の west manifest に一本化するためです。旧 vendor の c1d2d128a001a97db3ccfd66be524c0232094df6 と新しい参照 SHA は異なり、差分全体の互換性を確認済みとはしません。SDK 更新時に manifest revision と署名設定を再評価します。

[調査索引へ戻る](../README.md)
