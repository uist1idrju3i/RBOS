# 公式文書・Wiki と固定 source の照合

## 基準

2026-11-09 JST に公式 mrubyc/mrubyc Wiki を取得しました。Wiki HEAD は `a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80`。本文7ページ（Home、About、How works、How compile、Executing、compiler version table、README）と Sidebar を確認しました。license は Wiki 側にも存在し、本文の転載ではなく要約と照合結果を記載します。

source の基準は mruby/c `434bccd609f2a3e90d6bb95c458621898bc6a508`、compiler は mruby 4.0.0。Wiki の revision と VM の revision は別です。リンクは Wiki の固定 revision を指定しています。

| 公式資料 | 記載 | 固定 source との差と判断 |
|---|---|---|
| [About](https://github.com/mrubyc/mrubyc/wiki/About-mruby-c/a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80) | 小メモリ向け mruby VM の別実装 | README と整合。CRuby 全機能を搭載する説明ではない |
| [How works](https://github.com/mrubyc/mrubyc/wiki/How-mruby-c-works/a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80) | header/IREP/pool/debug の概要、未記入の節もある | 詳細な lifetime は loader と VM 実装を優先 |
| [How compile](https://github.com/mrubyc/mrubyc/wiki/How-to-compile-mruby-c/a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80) | library は src、旧実行名 mrubyc/mrubyc_concurrent/mrubyc_sample | 固定 Makefile は build directory と sample_*。Wiki の旧コマンドを新規手順に採用しない |
| [Executing](https://github.com/mrubyc/mrubyc/wiki/Executing-bytecode/a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80) | opcode/operand の説明。古い LOADI/JMP の例 | 固定版は LOADI8=0x03、JMP=0x26。operand の説明と opcode 数値を分けて参照 |
| [compiler version](https://github.com/mrubyc/mrubyc/wiki/mruby-compiler-version-vs-mruby-c-vm/a16b16a21fc00f87b4c4ca1eaf3b59803e68cf80) | 表は mruby 3.4 / RITE0300 まで | 固定版の global.rb/load.c/mrblib.c は 4.0.0/RITE0400。表の未掲載を 4.0 非対応の証拠にしない |
| compile.md | host make/autogen、HAL と Unicode 生成 | 現行 Makefile と照合。UnicodeData.txt は同梱され、生成規則はローカル入力。毎回 network download するとは限らない |
| task_class.md | Task API と RITE0300 の旧配列例 | Ruby API は method table と照合し、配列は 4.0.0 mrbc で再生成 |
| c_KeywordArgument.md | 必須/任意/残余と cleanup | 現行 value.h と照合。MRBC_KW_OPTIONAL を作らず ISVALID/default と DELETE を使う |
| test.md | make test と make test_full | 固定 Makefile の網羅 target は test_all。test_full は存在しない |

固定 source の根拠: `vendor/mrubyc/README.md:1-39`、`vendor/mrubyc/src/Makefile:1-178`、`vendor/mrubyc/src/opcode.h:1-249`、`vendor/mrubyc/src/load.c:1-440`、`vendor/mrubyc/src/mrblib.c:1-274`、`vendor/mrubyc/mrblib/global.rb:1-14`、`vendor/mrubyc/doc/compile.md:1-99`、`vendor/mrubyc/doc/task_class.md:1-244`、`vendor/mrubyc/doc/c_KeywordArgument.md:1-134`、`vendor/mrubyc/doc/test.md:1-29`、`vendor/mrubyc/Makefile:1-155`。

公式 Wiki の Ruby VM 節は未完成で、全 class/method/arity・opcode 実装・OOM/ownership を説明し尽くしていません。今回の索引は固定 source で補っています。Wiki や README の小さな RAM 使用例は、RBOS の SD と native buffer を含む RAM 予算の証明ではありません。

全 method の CRuby/mruby runtime との総当たり比較、上流最新 commit との全差分確認、外部 peripheral-interface guide の全機器実装は未実施です。今回 vendor の更新はしていません。

[調査索引へ戻る](../README.md)
