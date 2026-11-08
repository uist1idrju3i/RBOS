# Ruby 能力の小さな実行確認

2026-11-09 JST、既存 Wasm runner と固定 mrbc を使用しました。RBOS 基点は `181af4ed5fffcb97d77539321a843d478a142efb`。文書だけの調査 branch 上で実行し、fixture は ignored 領域に置き tests/ へ追加していません。

- mruby/c: `434bccd609f2a3e90d6bb95c458621898bc6a508`
- mruby/mrbc: `831da26b9021de0369d17b71b5667e2941a1a32d`、4.0.0 (2026-04-20)
- emcc: 6.0.12、Node: v24.21.0
- build 条件: [check.sh](../../tools/mrubyc-wasm/check.sh)、[exception hook](../../tools/mrubyc-wasm/runner_config.h)、vendor 既定 Float=2/Math=0/UTF8=0/INT64 無効、MAX_VM_COUNT=32。NO_TIMER は emscripten HAL の設定。

`tools/mrubyc-wasm/check.sh` は正常・空・複数 task と既存異常系を全て通過しました。upstream 由来 compiler warnings は残ります。以下は mrbc で compile した別々の入力を `node runner.js file.mrb`（timeout 8秒）で実行した結果です。

| 入力名 | Ruby 入力 | phase / exit | 出力 |
|---|---|---|---|
| normal | `def f(x:, y: 2); x+y; end; raise "kw" unless f(x: 3)==5; p [1,2,3].map {\|x\| x*2}; p Proc.new {\|x\| x+1}.call(4); case [1,2]; in [a,b]; p a+b; end` | run / 0 | [2, 4, 6]<br>5<br>3 |
| bytes | `p "あ".length; p [2,3,2].count(2); p 2147483647 + 1` | run / 2 | Exception(vm_id=1): Unsupported int64 (set MRBC_INT64 in vm_config) (NotImplementedError)<br>Failed to load bytecode: .yomiyasu/mrubyc-deep/bytes.mrb |
| lambda | `p ->(x) {x+1}.call(1)` | run / 1 | Exception(vm_id=1): Unimplemented opcode (0x61) found (Exception)<br>Uncaught task exception (scheduler status 2) |
| classvar | `class Example; @@n=1; end` | run / 1 | Exception(vm_id=1): Unimplemented opcode (0x1c) found (Exception)<br>	in Example'<br>Uncaught task exception (scheduler status 2) |
| nestedconst | `class Example; end; Example::N=1` | run / 1 | Exception(vm_id=1): Unimplemented opcode (0x20) found (Exception)<br>Uncaught task exception (scheduler status 2) |
| undef | `class Example; def x; 1; end; undef x; end` | run / 1 | Exception(vm_id=1): Unimplemented opcode (0x6e) found (Exception)<br>	in Example'<br>Uncaught task exception (scheduler status 2) |
| fiber | `p Fiber.new {1}` | run / 1 | Exception(vm_id=1): uninitialized constant Fiber (NameError)<br>Uncaught task exception (scheduler status 2) |
| enumerator | `p [1,2].each` | run / 1 | Exception(vm_id=1): no block given (yield) (Exception)<br>	in each'<br>Uncaught task exception (scheduler status 2) |
| math | `p Math.sin(0)` | run / 1 | Exception(vm_id=1): uninitialized constant Math (NameError)<br>Uncaught task exception (scheduler status 2) |
| text-count | `p "あ".length; p [2,3,2].count(2)` | run / 0 | 3<br>3 |
| runtime-overflow | `n=2147483647; p n+1` | run / 0 | -2147483648 |
| private | `class Example; private; def secret; 123; end; end; p Example.new.secret` | run / 0 | 123 |

`bytes` は compiler の定数畳込みにより int64 literal が必要となり、実行前の load で拒否されました。`runtime-overflow` は変数経由なので load は成功し、この Wasm binary では wrap しました。signed overflow の C 最適化・nRF toolchain 全体について wrap を保証する結果ではありません。整数範囲を binding と Ruby で規定します。

`text-count` は UTF-8 の「あ」が既定で length=3、count(2) が配列全長3を返すことを確認しました。`normal` は keyword、Enumerable、Proc.new、array pattern を含みます。`private` の結果からも Ruby の visibility を認可に使えません。その他の未実装 opcode と class 不在は別の失敗経路です。

## 入力・binary の同定

| 対象 | SHA-256 |
|---|---|
| runner.js | `0d7b54e3e62732d52ffc09333cd1604d57a20a142f4ed671b2100d9089a0f564` |
| runner.wasm | `61f7879ee7983ad456e527d5808d43843f080dd6a775d5dfe37a3b3e5a130fbb` |
| vendor と生成済み写しの mrblib.c（両方同値） | `98d29946cf214ae602b138d6d8d9f80d14c3f41b5bb0d62de1c13d902bc3b87e` |

committed mrblib.c は RITE0400、4281 bytes、header の宣言サイズと一致し、今回固定 compiler で再生成した C 配列と hash が一致しました。mrblib/*.rb の索引だけを新機能として数え、古い blob を未確認のまま対応済みとしたものではありません。byte 列の根拠: `vendor/mrubyc/src/mrblib.c:1-274`。

nRF 実機、UTF8/INT64/Math を有効にした別 binary、全 method・全 opcode、参照 cycle の増分計測は未検証です。これらの短い実行成功は firmware の IRQ/timing/security の検証を代替しません。

[調査索引へ戻る](../README.md)
