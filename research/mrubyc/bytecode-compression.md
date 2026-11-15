# bytecode の minify・圧縮・圧縮メモリの再確認

[調査索引](../README.md) / [ZMS と寿命の訂正](../dfu/zms-direct-execution.md)

## 出典と範囲

2026-11-15 の[セッション A](https://app.devin.ai/sessions/aa5ed531779b4af0920650da7a969077)の追加依頼は、minify と圧縮、mruby/c パッチでの圧縮 bytecode 実行・圧縮メモリ上の実行、Zephyr/組込み環境の zram 相当を公式・コミュニティ・SNS まで調査することです。[原報告](../dfu/zms-session-original.md)を今回再確認し、測定と一次資料で確認できる点だけを分離しました。調査・再測定日は同日。方式の採用・vendor 更新・製品コード変更はしていません。

## minify の確認と再測定

`--remove-lv` は LVAR section を落とします。固定 loader は IREP と END 以外の section を無視します（`vendor/mrubyc/src/load.c:302-325`）。mrblib は既に使っています（`vendor/mrubyc/mrblib/Makefile:48`）。一方、RBOS `firmware/cmake/mrubyc.cmake:57,63,93` の product 生成には未指定です。今回も変更していません。

入力は RBOS `243682c0313d7cedbd86e6d5a35260430452871c` の `src/rbos/*.rb` 全2本と `firmware/ruby/**/*.rb` 全8本。compiler は `mruby 4.0.0 (2026-04-20)`、binary SHA-256 は `b579ddc5e20d094f4985de19039c552954f15b6ecfbbe068390ffc9bf0f6d2ce` です。固定 mruby の source SHA は `831da26b9021de0369d17b71b5667e2941a1a32d`。既存 host binary の build 自体は再実行しておらず、その来歴を hash の一致以上に保証しません。

再現コマンドは各入力について `mrbc -o default.mrb INPUT` と `mrbc --remove-lv -o nolv.mrb INPUT`。続いて Python 標準ライブラリの `zlib.compress(data, 9)` と `lzma.compress(data)`（既定 XZ container）を両方の生成物へ実行しました。zlib は1.2.11。`-g` と `-B` は付けず、C の文字列表現ではなく mrb binary のサイズです。入力・生成物・compiler の全 hash と双方の圧縮結果は[測定データ](bytecode-size-results.json)に保存しました。

| 入力 | 既定 B | remove-lv B | 削減 B | remove-lv → zlib9 B | remove-lv → XZ B |
|---|---:|---:|---:|---:|---:|
| src/rbos/adc.rb | 468 | 416 | 52 | 276 | 336 |
| src/rbos/button.rb | 458 | 427 | 31 | 297 | 352 |
| firmware/ruby/system.rb | 243 | 222 | 21 | 188 | 244 |
| firmware/ruby/peripherals.rb | 1123 | 995 | 128 | 653 | 708 |
| firmware/ruby/selftest/coordinator.rb | 1826 | 1698 | 128 | 973 | 996 |
| firmware/ruby/selftest/worker_a.rb | 383 | 360 | 23 | 289 | 344 |
| firmware/ruby/selftest/worker_b.rb | 383 | 360 | 23 | 289 | 344 |
| firmware/ruby/stress/spinner_a.rb | 371 | 335 | 36 | 277 | 332 |
| firmware/ruby/stress/spinner_b.rb | 371 | 335 | 36 | 278 | 332 |
| firmware/ruby/fault/oom.rb | 192 | 168 | 24 | 154 | 208 |

原報告の `adc.rb 468→416 B` と `416→zlib9 276 B` は再現しました。未完だった `button.rb 458→? B` は **427 B**、削減率は6.8%です。ADC の11.1%を製品全体へ一般化しません。表の10本は profile ごとに選ばれるため、単純合計は firmware の実使用量ではありません。

`-g` を付けないことは debug 情報抑制、method 名の短縮は public API と動的 dispatch の互換性問題です。複数入力の結合は header 分を減らせても task 分離・top-level 実行順を変えます。`-s` は static pool の dump flag で、圧縮方式ではありません。どれも今回適用していません。

## 圧縮保存と圧縮実行は別

| 方式 | 保存・転送 | 実行時 RAM と実装上の境界 |
|---|---|---|
| 圧縮→全体 RAM へ伸張 | 小さくできる | 伸張後 blob と decoder RAM が必要。RAM 節約とは呼べない |
| 圧縮→NVM 実行領域へ伸張 | 転送は小さくできる | blob 全体の RAM は避けられるが、decoder window・I/O buffer・VM heap は必要。圧縮像と伸張像を同時保持すると NVM 総量は増える場合がある |
| IREP 単位に伸張・LRU | 未使用 IREP を遅延できる可能性 | inst/pool/symbol/catch/callinfo の生存参照を追跡し eviction を抑止する必要 |
| block 圧縮＋索引＋cache | ソフトウェアで可能性を検討できる | 命令 fetch、jump、return、catch、pool、symbol の全アクセスを仮想化。既存 mruby/c にその機能はない |
| 命令符号化自体を変更 | 圧縮率の研究対象 | mrbc と VM の双方を変更し、標準 RITE との互換性と全 opcode の検査が必要 |

生 pointer の根拠は `vendor/mrubyc/src/opcode.h:27-103`、`vendor/mrubyc/src/vm.c:156-176,204-260`、`vendor/mrubyc/src/vm.h:87-92` と `vendor/mrubyc/src/load.c:153-157,210-222,398-412`。原報告の「RAMほぼ0」は撤回し、「blob 全体の RAM コピーを避けられる」と訂正します。NVM 書込みは S115 と共存する非同期完了・電源断復旧・認証・書込み寿命も必要です。zlib の host 測定は decoder の BM 移植・転送速度・消費電力の証拠ではありません。

LZ4、heatshrink、miniz、LzmaDec や NCS の nrf_compress は原報告の候補です。BM での build、依存条件、ライセンス、window RAM、速度比較は本リポジトリでは試していません。「少数ファイルで導入できる」ことを採用根拠にはしません。

## Zephyr の一次資料と zram の境界

- [Zephyr v4.3.0 Kconfig.vm](https://github.com/zephyrproject-rtos/zephyr/blob/v4.3.0/kernel/Kconfig.vm#L111-L126) は `if MMU` 内で `DEMAND_PAGING` を定義し、`ARCH_HAS_DEMAND_PAGING` に依存します。MMU のない Cortex-M33 でこの標準 paging 機構は使えません。ただしソフトウェアで特定のデータアクセスを仲介する方式まで「ハード的に不可能」とする根拠ではありません。
- [v4.3.0 の ZMS header](https://github.com/zephyrproject-rtos/zephyr/blob/v4.3.0/include/zephyr/fs/zms.h)には iterator 自体がありません。セッションが読んだのは可変 main の `include/zephyr/kvss/zms.h` でした。今回 [main の固定 SHA 7cd4b562](https://github.com/zephyrproject-rtos/zephyr/blob/7cd4b562b30a9bcd76a7288ad90d5e71dd6f87d2/include/zephyr/kvss/zms.h#L451-L540) を確認。`zms_iter_next` は ID/len と小データのコピーを返す契約で、大きい値は `zms_read` を使います。内部の walk position はあっても、安定した CPU pointer を貸し出す API ではありません。BM の固定 API と混同しません。
- 原報告が挙げた CRAMES、MEMMU、TinyVM、MiniMem は研究・外部候補の履歴です。[MiniMem の当時の参照先](https://github.com/marcel-b-roodt/MiniMem/blob/main/docs/research/004-zram-zswap-architecture.md)は可変 URL で、今回その実装・再現性・M-class Zephyr 対応を独立検証していません。公式・コミュニティ・SNS の網羅性も保証できません。「該当実装は存在しない」「いずれも転用不可」という原報告の断定は未確認として扱います。

圧縮 heap まで透明化する案は bytecode だけより対象が広く、mrbc_value/object の全参照、GC/allocator、native binding も問題になります。実装規模や速度の定量評価は未実施です。現行の非圧縮 const bytecode を基準に、まず minify の profile 別 build/Wasm 回帰と hash を確認する、という順序は提案に留めます。
