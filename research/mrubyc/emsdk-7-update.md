# emsdk 7.0.0 の更新評価

2026-11-15、Wasm 検査の固定版を 6.0.12 から 7.0.0 に更新しました。比較の RBOS 入力は `b022f40` で、C/Ruby、vendor、mrbc、runner の flags は変更していません。Node は両方とも v24.22.3 です。BM firmware の toolchain は対象外です。

## 一次資料と確認範囲

[Emscripten の ChangeLog](https://github.com/emscripten-core/emscripten/blob/7.0.0/ChangeLog.md)の 6.0.12 より後、7.0.0 までを全件確認しました。中間 release は 6.0.13 のみです。以下の2表は、その全16項目の採否です。7.0.0 の見出しには `in development` が残っていますが、取得対象は SDK の release tag `7.0.0` です。

[SDK の compare](https://github.com/emscripten-core/emsdk/compare/6.0.12...7.0.0)も、全7 commit の説明と差分を確認しました。SDK tag の commit は `1693ce7359fc9694f198694f902a2cc061239b86`、取得する通常版 toolchain の revision は `6afbd83493d647051772d491124187d4e9a0cda9` です。可変の `latest` は使いません。

### Emscripten 6.0.13

| 変更 | RBOS への影響・採否 |
|---|---|
| Windows の `.bat` / `.ps1` launcher 削除 | Linux CI と shell 手順を維持。Windows native launcher への移行は対象外 |
| `MEMORY64=2` 非推奨 | 未使用。現行 wasm32 を維持。64-bit 化を検討するときに再評価 |
| `FS.filesystems` 削除、`MEMFS` の直接参照と明示 export | 独自 JS による参照なし。`NODERAWFS` を維持し、新たな export は追加しない |
| libpng 1.6.58 → 1.6.59 | libpng port を link していないため追加採用なし |
| pointer 変換時の `wasmExports` が継承を利用、列挙には `for...in` | `MEMORY64`・2 GiB 超の設定・独自 export 列挙なし。将来該当する JS を追加するときに対応 |

### Emscripten 7.0.0

| 変更 | RBOS への影響・採否 |
|---|---|
| `EMCC_ONLY_FORCED_STDLIBS` 削除、代替は `-nostdlib` | 旧変数も `-nostdlib` も未使用。既定の標準 library link を維持 |
| side module に builtins/profile を直接 link、共通実装を `libemcc` に分離 | side module 未使用。`-nostdlib` の明示 library 一覧もないので `-lemcc` を手動追加しない |
| profile runtime 分離、`MAIN_MODULE=1` の不要な `default.profraw` を抑制 | profiling・coverage・main module 設定なし。既定の linker 更新を採用し、不要な profiling flag は追加しない |
| pipe 容量64 KiB、満杯の非 blocking write は `EAGAIN`、blocking は当面無制限 | Wasm 内の pipe を使う fixture はない。Node filesystem と既存 I/O 試験を維持 |
| 同時 compile/link の `.dwo` / `.json` 出力名が `<output>-<input>` に変更 | split DWARF・time trace 未使用。将来これらの artifact を収集するときに命名を確認 |
| libc++ / libc++abi / libunwind / compiler-rt を LLVM 23.1.3 へ更新、C++ の推移的 include 削減 | C build と runtime 更新を採用。C++ を compile しないため互換用 `_LIBCPP_KEEP_TRANSITIVE_INCLUDES_LLVM23` は追加しない |
| WasmFS OPFS の pthread access handle 変更、read-only open 中の unlink/rename は `EIO` | WasmFS・OPFS・pthread は未使用。ブラウザー storage を導入するときに再評価 |
| mimalloc を 3.6.1 へ更新 | `-sMALLOC=mimalloc` は未指定。既定 allocator を維持し、allocator 切替は採用しない |
| `SIDE_MODULE=1` の `--whole-archive` 動作を復元、`-shared` は native archive 動作を維持 | dynamic linking は未使用。現行の単一実行 module を維持 |
| 直接 JS-to-JS 参照の依存を自動検出、間接参照・C/C++ には引き続き `__deps` | 独自 JS library はない。新たな shim や `__deps` は追加しない |
| 既定 browser 下限を Chrome 93 / Firefox 92 / Safari 15.4 へ引上げ | `ENVIRONMENT=node` を維持。browser 配信の互換性は今回の検証に含めない |

### SDK の7 commit

| commit | 内容・採否 |
|---|---|
| `8f685c26ee9f` | Node nightly の取得を `download_file()` 経由へ変更し、`EMSDK_USE_CURL` に対応。通常版の Node を使うため nightly の追加取得はしない |
| `fb4a37016394` | Chrome download に対応。Node 専用検査なので Chrome は取得しない |
| `1c9a998ee5dd` | Chrome 対応コードの lint 修正。SDK script の更新に含める |
| `3b3963d86a5c` | Chrome 取得時の Node PATH と空白入り path を修正。Chrome 利用は引き続き見送る |
| `35659964bc27` | 6.0.13 を公開。ChangeLog を上表で確認。7.0.0 が全試験を通過したため、この版への fallback は実行しない |
| `d7b4130688bf` | `tot` 判定から `DEPS.tagged-release` のみの commit を除外。固定 tag を使うため `tot` は採用しない |
| `1693ce7359fc` | 7.0.0 の release metadata・Bazel module/revisions と `libemcc` cache 一覧を更新。固定版の取得を採用し、未使用の Bazel は導入しない |

## 採用とライセンス

今回採用するのは固定 toolchain と標準 runtime/linker の更新です。追加の optional flag が必要になる利用形態はありません。`ASYNCIFY`、`NODERAWFS`、`ENVIRONMENT=node`、既存の assertion・stack・null-write 検査を維持します。Wasm は毎回 compile/link し直し、版をまたいで object を再利用しません。host mrbc の cache は Emscripten を使わないため変更しません。

旧版からの破壊的変更に関わる API/flag は上表のとおり未使用です。確認した ChangeLog に CVE の明記はありません。これは脆弱性がないことの保証ではなく、libpng や browser storage の修正を RBOS の security 対応実績とも扱いません。

SDK は [MIT](https://github.com/emscripten-core/emsdk/blob/7.0.0/LICENSE)、Emscripten は [MIT / Illinois-NCSA の二重ライセンス](https://github.com/emscripten-core/emscripten/blob/7.0.0/LICENSE)です。この2つの LICENSE は旧 tag と byte 単位で一致しました。同梱 component の全 license ファイルを個別比較したものではありません。

## 回帰と生成物の比較

同じ作業領域・入力で旧版と新版の `tools/mrubyc-wasm/check.sh` を実行し、両方とも終了値0、全80行の `PASS:` が同じ順序・内容でした。

| 項目 | 旧版 | 7.0.0 |
|---|---:|---:|
| emcc commit | `5488e0871d46d19a3209988190fa6a653126256f` | `777e6e5db7b4990bcaeb1b9998ed642cc84e6629` |
| `-Wsign-compare` | 20 | 20 |
| `-Wunterminated-string-initialization` | 78 | 78 |
| `runner.js` | 200773 B | 199088 B（−1685 B） |
| `runner.wasm` | 555782 B | 555774 B（−8 B） |
| `test-bytecode.js` | 75853 B | 75017 B（−836 B） |
| `test-bytecode.wasm` | 475178 B | 475170 B（−8 B） |

警告は既存の vendor code 由来で、新しい種類・件数の増加はありません。警告を抑制する変更や vendor の編集はしていません。size は今回の Node 用 build の観測値であり、firmware の size や一般的な高速化率ではありません。

PR #45/#46 の mutation も、作業ファイルを変えない写しで7.0.0を使って再実行しました。IREP mutation は catch table 対応後の `check_irep()` 呼び出しに合わせています。

| mutation | 検出した診断（全て exit 1） |
|---|---|
| const blob を書き換える | `FAIL: const bytecode blob changed` |
| String の変更を削除 | `Bytecode String mutation missing` |
| IREP instruction pointer を blob 外へ変更 | `FAIL: IREP instructions/catch table outside const blob` |
| producer task を実行しない | `FAIL: retained symbol does not reference producer blob` |
| OOM の期待 message を変更 | `Unexpected failure result: 1` |
| rescue を削除 | `FAIL: const task execution failed` |
| ensure の処理を削除 | `Bytecode ensure missing` |
| 非空 catch table を持つ処理を削除 | `FAIL: const fixture has no catch table` |
| instructions を blob 内に残し catch table を blob 外へ変更 | `FAIL: IREP instructions/catch table outside const blob` |

7.0.0 の失敗がなかったため、6.0.13 の実行・fallback は不要でした。旧 capability probe の日付・compiler・runner hash は歴史的な測定条件として維持しています。今回の成功で過去の全 probe を新版で再測定したことにはしません。browser、Windows、macOS、BM build、実機動作は今回未検証です。

[調査索引へ戻る](../README.md)
