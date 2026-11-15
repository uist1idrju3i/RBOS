# P4 の host/build 受け入れ記録（A1）

[調査索引](../README.md) / [段階計画](porting-plan.md#p4-const-bytecode-の生成結合) / [checklist](checklist.md#p4p5-埋め込みと-firmware-更新)

## 対象と判定

2026-11-15 に、固定 mruby 4.0.0 / mruby/c 4.0.0 の const bytecode を対象に確認しました。[P4 の受け入れ条件](porting-plan.md#p4-const-bytecode-の生成結合)のうち、実装・host/Wasm・BM build の証拠を整理した記録です。P4 全体や実機の受け入れ完了は宣言しません。

| 区分 | A1 で確認した範囲 | 判定の限界 |
|---|---|---|
| implementation | const 生成・結合、manifest、配置検査、試験の実装 | code の存在と試験在庫。実機動作とは分ける |
| host_wasm | 正常・空・拒否・OOM 終了、参照の寿命、String 不変、RAM 分類 | emsdk 7.0.0。ARM の測定ではない |
| bm_build | debug/release/stress/oom の manifest・ELF 配置・image 照合 | compile/link と成果物の検査。VM の実行ではない |
| real_hardware | 今回は NOT_RUN | pointer、high-water、復旧、DFU 等は Phase B |

## 試験と PR の対応

| PR | 内容 | 試験・証拠の区分 |
|---|---|---|
| [#45](https://github.com/uist1idrju3i/RBOS/pull/45) | const の正常・空、String 変更、producer 削除後の symbol/method、誤 header、VM ID 枯渇、OOM | `test_bytecode.c` と `check.sh`。implementation / host_wasm |
| [#46](https://github.com/uist1idrju3i/RBOS/pull/46) | 非空 catch table の範囲と rescue/ensure の実行 | Ruby の PASS、C の範囲検査。implementation / host_wasm |
| [#47](https://github.com/uist1idrju3i/RBOS/pull/47) | 全 product task・ADC/Button・vendor mrblib の manifest | `test_bytecode_manifest.py`、collect/verify。implementation / bm_build |
| [#48](https://github.com/uist1idrju3i/RBOS/pull/48) | 実 task 一覧、profile 切替時の残存物除去、同版 mrbc 差替え依存、CI の submodule 取得 | CMake 回帰試験、四 profile evidence。implementation / bm_build |
| [#49](https://github.com/uist1idrju3i/RBOS/pull/49) | emsdk 7.0.0 固定と既存試験・mutation の再実行 | [更新記録](../mrubyc/emsdk-7-update.md)。host_wasm |
| [#50](https://github.com/uist1idrju3i/RBOS/pull/50) | FLASH 内・非 writable section・byte 一致、最小 report、空 fixture の RAM 計測、ELF32 ARM 回帰試験 | `test_bytecode_layout.py`、四 profile verifier、`test_ram.c`。implementation / host_wasm / bm_build |
| 本 PR | 製品 Button の RAM 計測と本記録 | 空・Button を別プロセスで6段階計測。implementation / host_wasm |

試験の入口は [check.sh](../../tools/mrubyc-wasm/check.sh)、[const harness](../../tools/mrubyc-wasm/test_bytecode.c)、[RAM harness](../../tools/mrubyc-wasm/test_ram.c)、[Python 試験](../../tests/check-changes/test_bytecode_layout.py)です。正常系だけでなく、空入力、header/size 不正、OOM の exit と診断、必須 PASS の欠落も照合します。任意の破損 bytecode 全般を安全に拒否できるという主張ではありません。

## P4 受け入れ条件と checklist の対応

次の表は [P4 計画](porting-plan.md#p4-const-bytecode-の生成結合)と [P4・P5 checklist](checklist.md#p4p5-埋め込みと-firmware-更新)を対応付けます。複数の区分を含む項目は、実機の部分を残して unchecked を維持します。

| 条件・項目 | 対応する試験・記録 | PR | 区分と状態 |
|---|---|---|---|
| 固定 mrbc、const 配列、入力・生成物 hash | manifest の版・binary hash・argv・入力・生成 C・bytecode・在庫、改ざん拒否 | #47/#48 | implementation / bm_build 確認済み。checklist を checked |
| RRAM 配置・alignment・symbol 等を含む参照の寿命 | ELF32/64 gate、子 IREP/catch/pool の const 内参照、producer 削除後の使用 | #45/#46/#50 | host_wasm / bm_build 確認済み。real_hardware の pointer/alignment は Phase B、unchecked |
| 全体 RAM コピーなしの正常・空・不正形式・OOM | const を直接渡す C harness、runner の header/size 拒否、OOM の exit 1 と診断 | #45/#46/#49 | host_wasm 確認済み。実機 OOM 後の復旧は未確認のため元項目は unchecked |
| String 変更で const blob が不変 | String の内容・長さ、blob 全体の比較、catch table、pool の参照 | #45/#46 と本 PR | host_wasm 確認済み。実機の保証と区別し元項目は unchecked |
| IREP・補助表・String の RAM と alignment macro | 再帰的な要求サイズの集計と allocator 統計。macro の実機採否は別 | #50 と本 PR | host_wasm 計測済み。ARM high-water と macro の実機照合は Phase B |
| storage/BLE 転送/reload を初期には実装しない。更新は再build と DFU | [埋め込み方針](../dfu/embedded-bytecode.md)、現行の生成・link 経路 | #47/#50 | implementation の方針を維持。real_hardware の DFU は Phase B、unchecked |
| firmware single-bank GPIO/reset/retention 入口 | [DK 準備](dk-provisioning.md)と [DFU](../dfu/single-bank-dfu.md)の既存証拠を別途照合 | — | P5。A1 では未評価、元の unchecked を維持 |
| app/loader/installer の容量と署名済み成果物 | 四 profile verifier は app の map/image を検査。全 image の受け入れは別 | #47/#50（app のみ） | bm_build の app 部分を確認。P5 の元項目は unchecked |
| 固有 ED25519 key・KMU provisioning | [署名鍵](signing-keys.md)、DK 準備 | — | P5。A1 では未評価、unchecked |
| release 鍵で DK の起動・通常更新 | release build の成功と実機更新は分ける | — | real_hardware は A1 対象外、unchecked |
| ERASE_NONE 更新 | 既存の ERASE_RANGES_TOUCHED_BY_FIRMWARE の成功と区別 | — | real_hardware は Phase B、unchecked |
| DLE / ATT MTU と DFU 転送速度 | app と独立 loader の交渉を別々に確認する | — | real_hardware は Phase B、unchecked |
| 広告の開始・停止・再開条件 | P1 の観測とは別の P5 受け入れ | — | implementation / real_hardware は A1 対象外、unchecked |
| DEVICEID から RBOS_XXXX の生成 | P5 の規則決定と実装 | — | implementation は A1 対象外、unchecked |
| DK で広告名・複数台識別 | nRF Connect の観測 | — | real_hardware は Phase B、unchecked |
| SDK 既定 release 鍵を公開鍵で拒否 | [既存の鍵検査](signing-keys.md)の build 証拠 | — | bm_build。既存の checked を維持、A1 の新規成果には数えない |
| BOOTCONF lock 前の復旧・製造消去条件 | DK 準備と P5 手順 | — | real_hardware は Phase B、unchecked |
| 切断・不正署名・容量超過・各 write の電源断 | P5 の異常更新試験 | — | real_hardware は Phase B、unchecked |
| MCUmgr OPEN default・許可 command・clipboard | [管理機能](../nrf-bm/mcumgr.md) | — | implementation / real_hardware は A1 対象外、unchecked |

元の複合項目を host の結果だけで完了にせず、checklist に host_wasm / bm_build の確認済み項目を別記しました。P4 の「全体 RAM コピーなし」は、load へ渡す入力が const 配列で、命令・catch・pool がその配列内を参照するという範囲です。不変検査の snapshot は実行用の bytecode コピーではありません。IREP、symbol ID table、register、TCB、String は別途 RAM を消費します。

## 四 profile の CI evidence

対象は PR #50 の head `5abf23667caca6dbf351fa07fa512ae9b457c4fc`、CI の merge ref revision `029fe82bb2d8046301d935600af9e7b2d7918d8c` です。main への merge commit `51ea1157ab650540a546f00c090a25a43ec4977f` と区別します。[run 43704666108 の evidence job 132784528692](https://github.com/uist1idrju3i/RBOS/actions/runs/43704666108/job/132784528692)の JSON 出力で、全 profile の `layout.status=PASS` と総合 `status=PASS` を確認しました。

| profile | manifest blobs / layout symbols | layout | app FLASH（B） | app RAM（B） |
|---|---:|---|---:|---:|
| debug | 8 / 8 | PASS | 140036 | 85536 |
| release | 8 / 8 | PASS | 120280 | 85288 |
| stress | 10 / 10 | PASS | 140836 | 85536 |
| oom | 5 / 5 | PASS | 136412 | 85536 |

これは BM の map/link 使用量であり、後述の Wasm allocator 計測とは別です。verifier の完了区分は `implementation=NOT_EVALUATED`、`host_wasm=NOT_EVALUATED`、`bm_build=PASS`、`real_hardware=NOT_RUN` でした。CI の最終 checks は17 passed / 0 failed / 0 pending / 0 skipped です。oom profile の build は OOM fault の実行成功を意味しません。

署名済み app image の SHA-256 は次のとおりです。

| profile | SHA-256 |
|---|---|
| debug | `c0d6549825d3047545f5b50c7f8bbafa60283b7410dec5cc3b5b0e596e90cb38` |
| release | `06b39c8fcdfabebcfbdb9c73e259db131dbb1f4f4c1dee81255d3003716adbf8` |
| stress | `6239b9569c3490f9db9aaeba44da9289bb40773171b93c799bed1c9fc5831575` |
| oom | `db0d69a0e8d8aad25fa53f43b869afb1fd33249f25f5e5972782c3706c032002` |

artifact は `firmware-evidence-<profile>-029fe82bb2d8046301d935600af9e7b2d7918d8c` と `firmware-verification-029fe82bb2d8046301d935600af9e7b2d7918d8c` です。保持期間は7日なので、失効後は同じ固定入力で再 build し、以前と同一の image と断定せず記録を取り直します。ELF 全体は evidence に含めません。配置 metadata は収集時に ELF から抽出し、verifier は最小 report、map、manifest、署名済み image を照合します。保存していない ELF の section flags を独立再抽出する検査ではありません。

## Wasm の RAM 内訳

測定基点は main `51ea115` に本 PR の harness 変更を含む作業木です。固定 submodule は mruby `831da26b9021de0369d17b71b5667e2941a1a32d`、mruby/c `434bccd609f2a3e90d6bb95c458621898bc6a508`、emsdk は7.0.0です。`check.sh` の製品用 mrbc 引数は変更していません。`src/rbos/button.rb` を選んだ理由は、複数の子 IREP、symbol ID、実際の String literal を含み、native peripheral を動かさず load/begin まで測れるためです。

| 入力 | 入力 Ruby の SHA-256 | const bytecode の長さ / SHA-256 |
|---|---|---|
| `tests/mruby/empty.rb` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | 62 B / `7cd77cd04efda24ae02fb783c073065fd06c2e64939aeb1591d4ca32189ab677` |
| `src/rbos/button.rb` | `d3b1dc2e262054a5110a3e0d248a08b8c1fe53229b5117a88adaab54cb6d20d2` | 458 B / `96fc1c30e43a4bb2bf080994c262a57675f632880e65789550f1ff7b5cc3eea2` |

bytecode の hash は生成 C の配列から抽出した byte 列の値で、C text の hash ではありません。両 fixture は別プロセスで同じ1 MiB pool を初期化します。`baseline=2824 B`、pool 外の static symbol index 配列は2040 Bでした。register は TCB 確保後512 B、TCB は104 Bで、それ以前は0です。次の値は全て Wasm の計測値（B）です。

| fixture | stage | used | IREP_payload | symbol_table_pool | other_payload | allocator_overhead | padding |
|---|---|---:|---:|---:|---:|---:|---:|
| 両方 | init | 2824 | 0 | 0 | 0 | 0 | 0 |
| 両方 | tcb | 3444 | 0 | 0 | 0 | 4 | 0 |
| empty | load | 3488 | 32 | 0 | 0 | 8 | 8 |
| empty | begin | 3508 | 32 | 0 | 16 | 12 | 8 |
| empty | string_new | 3552 | 32 | 0 | 33 | 20 | 27 |
| empty | string_changed | 3592 | 32 | 0 | 65 | 20 | 35 |
| button | load | 3728 | 214 | 22 | 0 | 28 | 24 |
| button | begin | 3748 | 214 | 22 | 16 | 32 | 24 |
| button | string_new | 3808 | 214 | 22 | 63 | 40 | 29 |
| button | string_changed | 3840 | 214 | 22 | 95 | 40 | 29 |

IREP payload は子を再帰的にたどり、管理構造体・pool offset table・子 pointer table を合算します。symbol ID table の要求サイズは `symbol_table_pool` に分け、二重計上しません。`other_payload` は begin の self instance と String object・終端込み buffer です。空 fixture は4 byteの `seed`、Button は実際の34 byteの literal を String 化し、両方に32 byte追記します。String の内容・長さと const blob 全体の不変を照合しました。

`mrbc_alloc_statistics.used` から baseline と要求 payload、使用 block 数に基づく allocator header を差し引いた残りを padding とします。IREP 内 alignment、allocator の丸め・最小 block の余りを含む限定 fixture の残差です。任意の task の未知の割当を自動で分類する方式ではありません。static symbol index は used に足さず、snapshot や Wasm stack も pool の外です。製品 Button の命令自体、watch/wait、IRQ、イベント配送は実行していません。一般の task の peak や ARM の RAM 予算には外挿しません。

`check.sh` は各 fixture の6段階と `PASS: Wasm RAM stages and accounting` を必須化し、不明な fixture は exit 1 と `FAIL: RAM accounting` で拒否することも照合します。分類の詳細は [Wasm 手順](../../tools/mrubyc-wasm/README.md#ram-の段階計測)を参照してください。

## Phase B に残す確認

- 実機の ELF/map と debugger を対応付け、命令・catch・pool・symbol の pointer と firmware 全寿命を確認する。ARM の alignment macro と unaligned access 条件も照合する。
- pool/stack の high-water を、通常・stress・String 変更・イベント待機を含めて実機で測る。Wasm の構造体サイズや pool 値を ARM の値として使わない。
- 実機 OOM の診断・停止/reboot と、その後の資源・再起動復旧を確認する。host の期待する異常終了は復旧の証拠ではない。
- firmware single-bank DFU を実機で行い、旧 VM の参照終了、再起動、署名、異常更新、保存データを確認する。storage backend・BLE bytecode 転送・reload は初期対象に追加しない。
- FLASH の `PT_LOAD` が既存 linker で **RWE** である点を継続課題にする。現在は対象 section の `SHF_WRITE` 不在と FLASH 範囲で判定しており、segment/MPU による実効書込禁止は保証していない。linker/MPU の判断と実機確認を別途行う。

## 再検査

emsdk 7.0.0 の環境で `tools/mrubyc-wasm/check.sh`、`python3 -m unittest discover -s tests/check-changes` を実行します。文書は `check-research.py`、`check-skills.py`、`tests/check-skills`、yomiyasu、`git diff --check` で検査します。BM の再検査は [build 手順](bm-build.md)と [配置 gate](development-gates.md)に従い、四 profile の collect/verify を実行します。

[調査索引へ戻る](../README.md)
