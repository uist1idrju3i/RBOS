# A6: Dependabot 3件の個別評価

[研究索引](../README.md)

2026-11-15 に、RBOS `9caba615ef13a4a6ff5533eac55a0c50f6f5f017` を基準として評価しました。評価 branch の gitlink、`.gitmodules`、製品コードは変更していません。3件とも open・未 merge でした。

利用者の追加指示により、mruby/c は正式 release の `release4.0.0`、mruby は正式 release の `4.0.0` に固定します。取得した tag 一覧ではこれらが最新の正式版で、mruby 4.1.0 は rc2 までです。#18・#23 の未 release commit は採用しません。Dependabot 設定と skill の変更は判断待ちで、今回は行いません。

## 推奨

| PR | 推奨 | 理由と再検討条件 |
|---|---|---|
| [#16](https://github.com/uist1idrju3i/RBOS/pull/16) SDK | 見送り | v2.0.1 から v2.0.0 への後退。Wasm/BM が通っても SoftDevice と MCUboot offset の修正を取り消す理由にならない。固定版を維持し、監視する保守系統を別途決める |
| [#18](https://github.com/uist1idrju3i/RBOS/pull/18) mruby/c | 見送り | 正式 release ではないため。既読範囲ではセキュリティ・ensure 修正、mrblib 入力と int64 拒否時点の変更が重要。正式版を評価する際に契約・試験・引用の対応も確認する |
| [#23](https://github.com/uist1idrju3i/RBOS/pull/23) mruby | 見送り | 正式 release ではないため。4.1.0 正式版の公開時に再評価する。既読範囲の Prism・出力先・version 表示・生成命令の変更は、その際の確認点として残す |

PR の close・merge、監視設定の変更はしていません。A2 はこの評価では着手していません。

追加指示を受けた時点で、以下の候補回帰・10入力比較は完了していました。結果を指示前の参考証拠として保存し、その後の候補試験と履歴精読は打ち切りました。結果の良否で release 固定方針を覆すものではありません。

## 対象と履歴の読み方

| 依存 | 固定 SHA → 候補 SHA | 差分 |
|---|---|---|
| sdk-nrf-bm | `51484143c09199e19bccc16fa3b437f7a502a72b` → `e9041d77ec4cb17c383252b868ffb7e2685a9975` | v2.0.1 → v2.0.0、4 commit を取り消す |
| mruby/c | `434bccd609f2a3e90d6bb95c458621898bc6a508` → `5bb8ae6466cc5f8ba87ca8dad4ee4f62b5d4dc14` | 70 commit 追加 |
| mruby | `831da26b9021de0369d17b71b5667e2941a1a32d` → `65d9641377400b59932c452a6c72ada18eaa21e4` | 2,782 commit 追加 |

[全 commit 一覧](a6-vendor-commit-inventory.json)に SHA、親、日付、subject、一次資料 URL を保存しました。GitHub compare をページ分割して取得し、件数・SHA の重複を照合しました。SDK は逆向き compare の「取り消される4件」です。mruby の compare が返す file 一覧は300件上限のため、完全な変更ファイル一覧とは扱いません。

確認の深さは次のとおりです。全件の一覧を保存したことと、全差分の逐行査読は区別します。

- SDK: 対象4件の説明・実差分、v2.0.1 release notes、S115 10.0.1 release notes、manifest、tag と branch の位置を確認。
- mruby/c: 70件の commit message を全読。release/tag 一覧と release4.0.0 以後の範囲を照合し、rrt0、load、alloc、symbol、VM の差分を重点確認。機能・既定値・ライセンスを下表に分類。
- mruby: release/tag 一覧、NEWS の変更概要・security 本文を全読。後半の Issue/PR 列挙は主題別に照合。`doc/` の compile、compiler、mrbconf、language、symbol の差分を重点確認。`mrbc`、RITE header/dump、codegen の ensure・深さ・EXT 制限、`include` の version・compile・irep・ops の変更を確認。7千行超の新 codegen 全体や全 runtime の逐行査読はしていません。
- mruby のその他は subject による自動分類を補助に、runtime/libraries/tests 1,336、merge 800、compiler/bytecode 320、build/CI 251、documentation 75 の主題で整理しました。これは skill の四分類や手動査読の件数ではありません。

mruby/c の基準 tag は release4.0.0、mruby の基準 tag は 4.0.0 です。対象範囲内に追加の release tag はありません。mruby の 4.1.0-rc / rc2 は候補と分岐しており、候補の祖先ではありません（それぞれ候補側752件、tag側4件/9件）。候補を4.1 release と呼びません。公開 release 一覧が空でも、NEWS・commit・tag の一次資料で補いました。

## SDK: 後退の内容と提案の経路

### 四分類

| 分類 | 確認内容・採否 |
|---|---|
| 破壊的変更・必要な対応 | VERSION 2.0.1 → 2.0.0。S115/S145 の10.0.1 → 10.0.0。MCUboot target の `CONFIG_NRF_SDH_LOG_SD_INFO` が SoftDevice partition offset を考慮する修正を取り消す。RBOS がこの logging を有効化すると影響するため、後退は採用しない |
| セキュリティ | 対象 patch notes に security 修正の明記はない。S115 の DRGN-29306（high-duty advertising 後の random delay）修正も取り消す。ビルド成功で無害とは判断しない |
| 新機能・option・既定値 | 候補への移行で追加される新機能はない。PR 本文の shell/sample 等の commit 紹介より、実際の gitlink 間の4件取り消しを優先する。SoftDevice の既定選択も10.0.0へ戻るため見送り |
| ライセンス | SDK の Nordic 5-Clause は変更なし。SoftDevice の license file は版名の変更で内容は同一。Nordic IC 限定利用・binary の逆解析禁止等の条件は存続。条件緩和とは扱わない |

`west.yml` は同一で、NCS v3.3.0 の `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956`、Zephyr `fd9204a02d52630660ce8d729945a4dd743feabf`、MCUboot `fce4dac2e6295cf98bd02a85f7c4254f6102106d` は変わりません。SoftDevice 側の revision は `75a7b53a…` から `8b166995…` に戻ります。署名 algorithm・sysbuild の設定変更は不要でした。四 profile の署名・layout・evidence 検証は通りましたが、実機 DFU の証拠ではありません。

四 profile の実 `.config` はいずれも `CONFIG_NRF_SDH_LOG_SD_INFO` 無効です。offset 修正の有無が影響する logging 経路は今回の構成では動かず、BM の成功でその修正が不要とは判断できません。

一次資料: [SDK の逆向き比較][sdkcompare]、[v2.0.1 release notes][sdkrn]、[S115 release notes][s115rn]、[manifest][west]。

### なぜ Dependabot が古い版を選べるのか

現行設定と現行 updater のコードから、次の経路を確認しました。

1. RBOS の `.gitmodules` は `shallow = true` で、`branch` / `ref` 指定がありません。PR #16 の HEAD `b25f597dcdef31d6d0208e87862a2e8322399592` でも同じでした。
2. [upstream の default branch][sdkrepo] は `main`。取得時の `fa301fdac89c27835f54242db86d622c243593a3` と固定 SHA は分岐し、main 側180件、固定側4件です。v2.0.1 の tag は固定 SHA に peel されますが main の祖先ではありません。
3. [Dependabot の parser/finder][dbsub] と [GitCommitChecker][dbchecker] は指定がない ref を `HEAD` とし、その ref の履歴から候補を得ます。PackageDetailsFetcher は最大500 commit を tag と照合します。現在の main の500件を照合すると、到達する release tag の最大は v2.0.0 で、v2.0.1 はありません。
4. 現在の固定 SHA が候補履歴にない場合は低い仮 version として残り、正規化した tag の最大値 v2.0.0 が選ばれます。SHA の単純な新旧判定で後退を防ぐ処理ではありません。

確認した Dependabot source は `1a0125f11e75859a0957b4d73ea6b8656570b30e` です。この設定・履歴・現行 algorithm は提案と整合します。ただし、PR #16 作成時の updater の版と実行 log は取得できていません。過去の実行原因まで確定したとは扱いません。固定版と default branch が分岐しているという、単純な「最新版 tag」選択では見落とす条件を確認した結果です。

## mruby/c: API と既存の前提

### 四分類

| 分類 | 確認内容・採否 |
|---|---|
| 破壊的変更・必要な対応 | `MRBC_ALLOC_VMID` / `_24BIT`、`mrbc_free_all`、allocation の get/set_vm_id を削除。VM ID の払い出し・返却自体は残る。unsupported int64 の拒否を load 時から literal 使用時へ変更。mrblib に `task_queue.rb` を追加し、現行 manifest に拒否される。更新時は入力在庫・失敗契約・引用の改訂が必要 |
| セキュリティ | CVE-2026-86547 の OP_ENTER が top-level の NULL callinfo を参照する問題を修正。任意 bytecode を渡せる経路の DoS 対策として価値がある。現行製品は埋込み bytecode で、外部 bytecode 受付の安全性を確認したという意味ではない。libc allocator の UAF/OOM 修正は `MRBC_ALLOC_LIBC` 向けで、RBOS の pool allocator と分ける |
| 新機能・option・既定値 | `Task::Queue` / `timeout_ms`、task instance の保持、Task.current/list/join/terminate、ensure/retry/break/return の修正。scheduler hook は既定無効で単一所有、queue の C push は IRQ-safe ではない。RBOS の IRQ queue の代替としては採用しない。allocator statistics に `max_free_size` を追加。正式版の再評価時は P3 と寿命・OOM の試験も確認する |
| ライセンス | BSD-3-Clause と Unicode の license 条件は変更なし。新規 Queue 等も既存の条件内。著作権表示の更新と利用条件の変更を区別した |

一次資料: [全70件の比較][mccompare]、[OP_ENTER 修正][mcsecurity]、[候補の loader][mcload]、[allocator][mcalloc]、[scheduler][mcrrt]。

### PR #45〜#51 の前提との照合

| 前提 | source と Wasm の確認 |
|---|---|
| const blob の直接 load・寿命 | inst/pool は入力を参照し、symbol の add_index は文字列 pointer を保持する。String 変更後も blob が不変、producer 削除後の method/symbol 保持の既存試験が PASS。blob を早く解放してよいという変更ではない |
| symbol | offset 300 → 512 等の内部形式が変化。入力文字列の参照は継続。数値 ID の永続化や異版間共有の根拠にはしない |
| allocator statistics | 既存 used/free 等を維持し `max_free_size` を追加。空・Button の12段階と加算照合が PASS。子 IREP の alignment は pointer 幅に合わせる変更で、Wasm/ARM の値を同一視しない |
| VM ID | allocator の VM-ID 機能削除と VM ID の枯渇検出は別。既存の枯渇拒否試験は PASS。TCB はこの Wasm build で104 → 112 byte |

Wasm の init used は2,824 → 3,080 byte、Button load は3,728 → 3,992 byte、String 変更後は3,840 → 4,104 byteでした。IREP payload 214、symbol table pool 22 byte は同じです。これは host_wasm の限定 fixture の値で、ARM の RAM 使用量・high-water ではありません。

## mruby: RITE0400 と compiler の互換性

### 四分類

| 分類 | 確認内容・採否 |
|---|---|
| 破壊的変更・必要な対応 | Lrama/yacc 系から Prism compiler へ移行。Ruby build 最低版2.7、build target 名、CLI version 表示、dump API、codegen が変化。現行の `build/host/bin/mrbc` と `mruby 4.0.0` の確認条件に合わない。`include/mruby/version.h` の4.0.0/-1だけで互換とは判断しない |
| セキュリティ | NEWS は UAF、OOB、NULL dereference、整数 overflow、parser の深さ等を列挙。host compiler の入力処理修正には関係するが、mruby runtime の修正を製品の mruby/c VM に適用したとは扱わない |
| 新機能・option・既定値 | Prism、深さ制限、build の出所情報・prefix map・size/defines/compile_commands 等を確認。下表のとおり、製品 VM 用の機能と host compiler 用を分けて保留する |
| ライセンス | root MIT は維持。新 compiler の MIT 表示と、Prism `ca15cb3d8b30144b8589e053db24c9be5a204fcf` の MIT 表示が追加。採用して compiler/container を再配布する際は両方の notice を含める。ライセンス上の拒否理由は見つからなかった |

一次資料: [全範囲の比較][mrcompare]、[NEWS][mrnews]、[compiler guide][mrguide]、[build config][mrconfig]、[候補の dump header][mrdump]、[compiler license][mrlicense]、[Prism license][prismlicense]。

| 機能・設定の群 | 採否と再確認条件 |
|---|---|
| Prism / `MRC_TARGET_MRUBYC` | 保留。既存 tool の出力先・version 検査と VM の命令 semantics を揃える変更時に評価。README の opt-in 記述より実際の build/config を優先する |
| `PRISM_DEPTH_MAXIMUM` / `MRC_CODEGEN_LEVEL_MAX` | 候補既定256。従来の大きい parser 上限より抑制的。host build を正式更新するときに維持・境界試験する。今回は依存を採用しない |
| `PM_ARENA_INITIAL_SIZE` / `PM_CONSTANT_POOL_MIN_CAPACITY` | 既定8,192 / 4。小 heap 向け調整は host CLI に不要。device 内 compiler を検討する場合に再評価 |
| `MRC_USE_THREAD_LOCAL`、allocator/stdio/int/float の MRC 設定 | 単一 thread の host CLI なので独自設定を追加しない。mruby/c 向け compiler や組込み compiler を作るときに target 幅とともに再確認 |
| `MRB_USE_C_STACK_CHECK`、GC malloc threshold、symbol 上限、refinements、Unicode/ASCII、regexp・ENV/Process/Signal 等 | mruby runtime の機能。製品 mruby/c に自動導入しない。MRB GC threshold 既定16 MiB を製品 RAM 設定と混同しない |
| `MRUBY_REVISION` / `MRUBY_PLATFORM`、prefix map、defines/compile_commands/size、dump API | compiler 更新時の再現性・観測に有用。現行の manifest 記録は維持し、build target の移行と一緒に検討。CLI 利用のため新 dump C API は未使用 |

### 製品10入力

両 compiler に、製品と同じ `-B<symbol> -o <C file> <Ruby input>` の flags を渡し、const 配列の実 byte を抽出しました。入力 SHA-256 と、生成物の全 SHA-256・長さ・宣言長は[比較データ](a6-vendor-regression.json)にあります。全入力の source hash は一致し、両版とも RITE0400・宣言長一致、生成物の hash は10件とも異なりました。

| 入力 | 固定版 byte | 候補 byte |
|---|---:|---:|
| firmware/ruby/fault/oom.rb | 192 | 192 |
| firmware/ruby/peripherals.rb | 1,123 | 1,128 |
| firmware/ruby/selftest/coordinator.rb | 1,826 | 1,824 |
| firmware/ruby/selftest/worker_a.rb | 383 | 460 |
| firmware/ruby/selftest/worker_b.rb | 383 | 460 |
| firmware/ruby/stress/spinner_a.rb | 371 | 362 |
| firmware/ruby/stress/spinner_b.rb | 371 | 362 |
| firmware/ruby/system.rb | 243 | 271 |
| src/rbos/adc.rb | 468 | 545 |
| src/rbos/button.rb | 458 | 458 |

候補 mrbc で既存の `tests/mruby/bytecode_mutation.rb` を `.mrb` にし、固定版の Wasm runner に渡すと、String 変更の PASS 後に `op_rescue` の `mrbc_type(regs[a]) == MRBC_TT_EXCEPTION` assertion で終了値1になりました。候補 codegen の `gen_ensure` は通常経路でも nil に OP_RESCUE を適用し、固定版 VM は exception のみを仮定しています。mruby/c 候補にはこの対応修正がありますが、2依存同時更新の試験は今回していません。RITE header が同じでも実行互換は保証されません。

## 追加指示前に完了した回帰結果と再現条件

implementation の更新ではなく、host_wasm と bm_build の評価です。`real_hardware=NOT_RUN`。Node v24.22.3、emsdk 7.0.0、BM は NCS v3.3.0 の toolchain を使いました。

### 隔離と一時 commit

各候補は基準から別 worktree を作り、1依存だけ gitlink を変えました。以下は許可された一時 commit で、push せず、評価 branch に含めません。3つの worktree は証拠保存後に削除しました。親と差分は比較データにも残しています。

| 候補 | 一時 commit SHA |
|---|---|
| SDK | `1c98161c1a22b3fd43b6a5b998e5befe7c7f2ec6` |
| mruby/c | `75664e112b1421e68ca381e818abc5db4670da82` |
| mruby | `5ed349491bf6b9dda0ef720a7958d4f49a4bcaac` |

SDK は別 west workspace に全 module の実体を置き、`RBOS_BM_MODULES` / verifier の `--modules` に渡す期待値だけ nrf-bm の候補 SHA へ変更しました。他 module の SHA は同じです。通常 workspace は更新していません。先行する2回の symlink 隔離では CMake の module target が不整合になり、正式比較から除外しました。実体 clone での結果が下表です。mruby は浅い local clone に候補 tree がなかったため、候補 SHA を追加で `--depth 1` fetch してから試験しました。nested Prism も depth 1 で取得しています。

### Wasm・共通検査

警告は `warning:` 行の `[-W…]` ごとの件数です。中断した候補は compile 範囲が異なるため、警告の減少を品質改善とは扱いません。

| 構成 | check.sh 終了値 / PASS 行 | sign-compare / unterminated-string | Python 110件 | skills / 7件 | research |
|---|---|---|---|---|---|
| 固定版 | 0 / 83 | 30 / 117 | OK | OK / OK | 0 error |
| SDK 候補 | 0 / 83（行も同一） | 30 / 117 | OK | OK / OK | 12 error |
| mruby/c 候補 | 1 / 74 | 27 / 123 | 1 failure | OK / OK | 52 error |
| mruby 候補 | 127 / 1 | 0 / 0 | OK | OK / OK | 1 error |

mruby/c の Wasm は `Unexpected failure result: 1 (expected 2 / Unsupported int64 (set MRBC_INT64 in vm_config))` で止まりました。Python は mrblib の `Bytecode manifest: unexpected inputs` です。SDK の research は削除される2.0.1資料の引用等、mruby/c は移動・短縮された API の行範囲、mruby は dump.c の行範囲が原因です。現行固定版の文書を候補に合わせて書き換えて通すことはしていません。

mruby の stock check.sh は host compiler の build 自体は成功し、その後、旧 `build/host/bin/mrbc` 不在で中断しました。独立の10入力比較と BM の呼び出しには実際の `build/mrbc/bin/mrbc` を使用しました。表示は `mrbc RITE0400 (unknown unknown unknown) Parser: Prism-2.1.0` で、製品 CMake の `mruby 4.0.0` 要件には合いません。

### BM 四 profile

`west build --sysbuild` の後、`collect-evidence.sh` と `verify-evidence.py --profile ... --revision ... --modules ...` を実行しました。release は評価専用 Ed25519 鍵で署名しました。秘密鍵は証拠に含めていません。サイズは firmware の map の値で、SoftDevice・loader・installer を合算した総 FLASH ではありません。

| profile | 固定版 FLASH / RAM byte | SDK FLASH / RAM byte | 固定版 / SDK の build・collect・verify |
|---|---:|---:|---|
| debug | 140,036 / 85,536 | 140,036 / 85,536 | 全て PASS |
| release | 120,280 / 85,288 | 120,280 / 85,288 | 全て PASS |
| stress | 140,836 / 85,536 | 140,836 / 85,536 | 全て PASS |
| oom | 136,412 / 85,536 | 136,412 / 85,536 | 全て PASS |

layout は debug/release 8、stress 10、oom 5 symbol が両版で PASS。verifier は clean source、bytecode、署名済み image、module SHA 等も検査しています。SDK の SoftDevice binary は変わるため、アプリの map 一致を image 全体の一致とは呼びません。

mruby/c は四 profile とも `mruby/c mrblib generation failed`、原因は `task_queue.rb` の入力 manifest 拒否でした。mruby は四 profile とも `RBOS_MRBC must be an executable mruby 4.0.0 compiler` で configure 失敗です。いずれも collect/verify とサイズ比較は実施不能（N/A）で、PASS はありません。失敗を回避する製品変更はしていません。

## 証拠・残件

[比較データ](a6-vendor-regression.json)に実行 commit、gitlink 差分、Wasm PASS 行・警告、BM 検証結果、10入力の hash、log の SHA-256 を記録しました。全 commit 一覧と合わせて保存します。実験の生 log と evidence bundle は作業環境にも保持していますが、個人環境のパスを再現手順の根拠にはしていません。

未確認は、候補の実機起動・pointer/alignment・RAM high-water・OOM 復旧・BLE/DFU、2依存以上を同時更新した互換性、歴史的な Dependabot runner の版/log、評価 branch の新しい GitHub CI です。FLASH segment の RWE は本評価で解消していません。[A1 の Phase B 残件](p4-host-acceptance.md)を引き継ぎます。

mruby 4.1.0 の正式版公開時に、mruby/c も含めた正式 release の tag・修正内容・互換性を再評価します。既読の CVE 修正が未 release にあることは残件であり、現固定版の安全性を保証する判断ではありません。今回の未 release 候補の試験を続けたり、release 固定の監視方針を先に変更したりはしません。

[sdkcompare]: https://github.com/nrfconnect/sdk-nrf-bm/compare/e9041d77ec4cb17c383252b868ffb7e2685a9975...51484143c09199e19bccc16fa3b437f7a502a72b
[sdkrn]: https://github.com/nrfconnect/sdk-nrf-bm/blob/51484143c09199e19bccc16fa3b437f7a502a72b/doc/nrf-bm/release_notes/release_notes_2.0.1.rst
[s115rn]: https://github.com/nrfconnect/sdk-nrf-bm/blob/51484143c09199e19bccc16fa3b437f7a502a72b/components/softdevice/nrf54l/s115/doc/s115_10.0.1_release-notes.rst
[west]: https://github.com/nrfconnect/sdk-nrf-bm/blob/e9041d77ec4cb17c383252b868ffb7e2685a9975/west.yml
[sdkrepo]: https://github.com/nrfconnect/sdk-nrf-bm
[dbsub]: https://github.com/dependabot/dependabot-core/tree/1a0125f11e75859a0957b4d73ea6b8656570b30e/git_submodules/lib/dependabot/git_submodules
[dbchecker]: https://github.com/dependabot/dependabot-core/blob/1a0125f11e75859a0957b4d73ea6b8656570b30e/common/lib/dependabot/git_commit_checker.rb
[mccompare]: https://github.com/mrubyc/mrubyc/compare/434bccd609f2a3e90d6bb95c458621898bc6a508...5bb8ae6466cc5f8ba87ca8dad4ee4f62b5d4dc14
[mcsecurity]: https://github.com/mrubyc/mrubyc/commit/625769fe263dacfa1d12c02cf1cc092efcb3d738
[mcload]: https://github.com/mrubyc/mrubyc/blob/5bb8ae6466cc5f8ba87ca8dad4ee4f62b5d4dc14/src/load.c
[mcalloc]: https://github.com/mrubyc/mrubyc/blob/5bb8ae6466cc5f8ba87ca8dad4ee4f62b5d4dc14/src/alloc.c
[mcrrt]: https://github.com/mrubyc/mrubyc/blob/5bb8ae6466cc5f8ba87ca8dad4ee4f62b5d4dc14/src/rrt0.c
[mrcompare]: https://github.com/mruby/mruby/compare/831da26b9021de0369d17b71b5667e2941a1a32d...65d9641377400b59932c452a6c72ada18eaa21e4
[mrnews]: https://github.com/mruby/mruby/blob/65d9641377400b59932c452a6c72ada18eaa21e4/NEWS.md
[mrguide]: https://github.com/mruby/mruby/blob/65d9641377400b59932c452a6c72ada18eaa21e4/doc/internal/compiler.md
[mrconfig]: https://github.com/mruby/mruby/blob/65d9641377400b59932c452a6c72ada18eaa21e4/build_config/mrbc.rb
[mrdump]: https://github.com/mruby/mruby/blob/65d9641377400b59932c452a6c72ada18eaa21e4/mrbgems/mruby-compiler/include/mrc_dump.h
[mrlicense]: https://github.com/mruby/mruby/blob/65d9641377400b59932c452a6c72ada18eaa21e4/mrbgems/mruby-compiler/LICENSE
[prismlicense]: https://github.com/ruby/prism/blob/ca15cb3d8b30144b8589e053db24c9be5a204fcf/LICENSE.md
