# A2 の host / Wasm 証拠

[調査索引へ戻る](../../README.md)

[設計](../a2-p3-design.md)、[脅威モデル](../a2-p3-authentication.md)、[暗号評価](../../openblink/hmac-evaluation.md)の一時試作を保存したものです。製品や CI から自動的に呼ばれるコードではありません。危険性を再現するための fixture を製品へ組み込まないでください。

## 入力と再現

基準 RBOS は `460224d91df9bb89f479a97f76b1919d32737c65`、文書を保存する branch の基点は main `d298e62`。両者の firmware/src・共有 src・固定 mruby/c/SDK に差分はありませんでした。mruby/c は release4.0.0 `434bccd609f2a3e90d6bb95c458621898bc6a508`、mrbc は4.0.0 `831da26b9021de0369d17b71b5667e2941a1a32d`、emsdk は7.0.0です。source/binary の照合値は [provenance.json](provenance.json)へ保存します。

emsdk を有効にし、repository root で次を実行します。既存の共通 Wasm suite が compiler と autogen 済み mruby/c を準備します。生成物は research に書かず git 管理外の作業領域へ置きます。

```sh
tools/mrubyc-wasm/check.sh
bash research/implementation/a2-p3-evidence/run-wasm.sh
```

| 試作 | source / 入力 | 記録・制約 |
|---|---|---|
| sudo 意味論 | [sudo_probe.c](sudo_probe.c)、[cases](sudo_cases.rb)、[child](sudo_child.rb)、[raise](sudo_raise.rb)、[victim](sudo_victim.rb)、[config](sudo_config.h)、[HAL](hal.h) | [sudo.log](sudo.log)。認証は文字列 fixture で HMAC ではない。明示 yield と模擬 tick であり実時間 IRQ 試験ではない |
| C supervisor | [c_system_probe.c](c_system_probe.c)、[normal](c_system.rb)、[spin](c_spin.rb)、[sleep](c_sleep.rb)、[block](c_block.rb)、[error](c_error.rb)、[empty](c_empty.rb)、[config](c_system_config.h) | [c-system.log](c-system.log)。`--wrap=mrbc_vm_run`。compiler instrumentation が C 関数呼出し境界から決定的な模擬 IRQ を挿入。固定 source は未編集 |
| HMAC | [hmac_host.c](hmac_host.c) | [hmac-host.log](hmac-host.log)、[stack](hmac-stack.tsv)。x86 host software PSA、RFC 4231。nRF stack/CRACEN ではない |
| 先行 Task wrapper 調査 | [task_registry_probe.c](task_registry_probe.c)、[priority](priority.rb)、[trusted](trusted.rb)、[untrusted](untrusted.rb) | [task-wrapper.log](task-wrapper.log)。TCB storage を明示再利用した stale handle 試験。現 firmware で Ruby だけから allocator 再利用が起きた証拠ではない |

HAL の quantum は10 tick。C supervisor の25 tick 監視閾値は模擬条件であり firmware の設定値ではありません。初回は監視閾値5 tick が quantum より短く spin の assertion に失敗し、25へ修正しました。native blocking fixture は80 tick。timer の生存だけで feed せず foreground heartbeat の鮮度を見ることを検査します。空 program と例外の際は scheduler から C に戻ることを検査しており、常駐 C event loop 自体の完成を示しません。

Wasm compile は既存 upstream/生成 header に49警告、今回の fixture 独自の警告は0でした。C/H の build copy は固定 vendor と一致しました。最初の sudo 試作では MRBC_NO_TIMER の Task.pass/timeslice 条件で timeout し、timer-style の条件へ分離しました。一般の捕捉 closure 全体の寿命を保証する試験ではありません。

## HMAC host の再現条件

外部コードは [OpenBlink 固定 SHA](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3)の wrapper/header と [Mbed TLS 固定 SHA](https://github.com/nrfconnect/sdk-mbedtls/tree/5bb86aeae32420e4f537e5cc390f7219a1bcf500)です。外部 source はこの evidence に含めていません。wrapper は BSD-3-Clause / Copyright 2025 ViXion Inc.。harness の既知値は [RFC 4231](https://www.rfc-editor.org/rfc/rfc4231.html)に基づきます。

Mbed TLS の通常 host 設定で tests/programs を無効にして mbedcrypto を build します。wrapper の Zephyr logging は [include shim](logging_shim/zephyr/logging/log.h)に置換し、wrapper source 自体は変更しません。[run-host.sh](run-host.sh)に OpenBlink checkout、Mbed TLS checkout、build 済み libmbedcrypto.a の3引数を渡すと再実行できます。cc は `-O2 -fstack-usage`、PSA header と内部 library include を使い、harness・wrapper・libmbedcrypto・pthread を link します。最初の Mbed TLS build は SDK 内部 header の include が不足したため include 条件を修正しました。host 用の手順であり BM build ではありません。

host harness が destroy する PSA handle は試験を継続するための cleanup であり、元 wrapper に cleanup があることの証拠にはしません。MAC を比較する harness の memcmp も、製品 verify の定数時間性の証拠ではありません。

## 未確認

BM の wrap/link/LTO、実時間上限、実機 IRQ・WDT・BLE、KMU、CRACEN は未確認です。runtime log から機密値や個人環境の絶対パスを取り除く目的で数値を加工していません。stack 表だけは compiler 出力の source 絶対パスを省き、関数名・値・分類を転記しました。
