# ZMS 内 bytecode の直接参照: セッションの再確認

[調査索引](../README.md) / [圧縮・minify](../mrubyc/bytecode-compression.md)

## 対象と証拠の境界

調査・再確認日は 2026-11-15。[出典セッション A](https://app.devin.ai/sessions/aa5ed531779b4af0920650da7a969077)の依頼は、OpenBlink が ZMS から RAM へコピーする理由、先頭アドレス取得と不連続配置の仮説、代替案の深い調査です。追加依頼の圧縮・圧縮メモリは上記の別文書に分けました。[添付原報告の写し](zms-session-original.md)は誤りも含む履歴で、本書を訂正として併読します。

RBOS の再確認基準は `243682c0313d7cedbd86e6d5a35260430452871c`。依存は[索引の固定版](../README.md#資料の版)の mruby/c `434bccd`、sdk-nrf-bm `5148414` です。ソースを読んだ確認であり、ZMS resolver の実装、実機実行、電源断試験は行っていません。現在の[埋め込み方式](embedded-bytecode.md)と決定事項は変更しません。

## OpenBlink がコピーしている経路

再確認した OpenBlink は [`6d22b676d2cf4bc599a7709ecebaa1b890af9e3a`](https://github.com/OpenBlink/openblink-demo-nrf/tree/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a)。既存索引の固定 SHA と一致します。ただしセッション A の startup log は main の fetch 成功を記録するだけで HEAD の SHA を出していません。したがって「当該セッションもこの SHA を見た」とまでは確定できません。以下の行は今回この固定版で再確認しました。

- [`mrubyc_vm.c:137-165`](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L137-L165): 4016 B の二つの stack buffer にロードして task を生成。上限は [`blink.h:21`](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/blink.h#L21)。合計8032 Bで、厳密には8 KiBではありません。
- [`load_bytecode:203-237`](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L203-L237) → [`blink_load:60-63`](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/blink.c#L60-L63) → [`storage_read_hist:86-94`](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/storage.c#L86-L94) → `zms_read_hist`。全体コピーはソースから確認できます。

これは実装の事実であり、作者がこの構成を選んだ理由の確認ではありません。RAM buffer は寿命と安定したアドレスを与えますが、RAM コピーが必須という mruby/c の仕様はありません。

## 固定 BM 実装で確認したこと

| 主張 | 一次ソースとの照合 |
|---|---|
| 公開の data address getter がない | `vendor/sdk-nrf-bm/include/bm/fs/bm_zms.h` の API を確認。read は呼出側 buffer へコピーする契約 |
| 1 record は sector 内で連続 | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms.c:2101-2168` は長さを `sector_size - 5 * ate_size` 以下かつ `UINT16_MAX` 以下に制限。`:750-761` が data write を起動。境界不足は sector を進める。複数 write の集合全体が連続する保証ではない |
| 小 record は ATE 内 | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms_priv.h:49-79` は packed 16 B、data は8 B。通常の mrb は8 Bより大きい |
| BM の物理アドレス | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms.c:404-407,1999-2005` は sector-relative offset と `fs->offset` を storage base に使う |
| S115 有効でも read は直接参照 | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/bm_storage_sd.c:404-410` は `memcpy(storage->addr + src)`。RRAM 側は `vendor/sdk-nrf-bm/subsys/storage/bm_storage/rram/bm_storage_rram.c:101-108` の `nrfx_rramc_buffer_read` |
| VM が入力内を参照し続ける | `vendor/mrubyc/src/load.c:131-258` の inst/pool、`vendor/mrubyc/src/vm.c:156-160,204-260` の callinfo、`vendor/mrubyc/src/vm.h:87-92` の pool pointer |
| GC は pointer の寿命を壊しうる | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms.c:1462-1621` は live record をコピーし旧 sector を再利用。mount と write の GC dispatch は `:1944-1947,2193-2195`。他 ID の write も無関係ではない |

BM で有効な ATE を得た場合、8 B超の record の候補アドレスは `fs->offset + sector_number * fs->sector_size + ate.offset` です。ただし式だけでは安全な resolver にはなりません。ATE の CRC8/cycle、最新性、削除、領域と長さ、整列、read 完了、data CRC、VM と書込みの排他を検査する必要があります。

## 原報告からの重要な訂正

1. **「SYMS は symid へ変換後不要」→ 誤り。** `vendor/mrubyc/src/load.c:210-222` は通常 `sym_str = (char *)p` を渡します。`vendor/mrubyc/src/symbol.c:167-182,221-233` は非 builtin symbol の文字列ポインタを保持します。`flag_permanence == 1` のコピー経路は例外です。task が止まっただけで入力を上書きしてよいとは限らず、symbol/method/IREP を含め全参照を破棄する reset 手順が要ります。
2. **「cache が最新 ATE を保持」→ ID ごとの確実な索引ではない。** hash bucket の開始位置です。`vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms.c:295-303,322-385,1415-1455,2242-2288` は衝突と走査を扱います。cache の ID を一度確認するだけでは足りません。128×8 B = 1024 B は既定 cache サイズを有効化した場合の配列だけの値です。既定では無効（`vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:17-28`）。
3. **「id/len/RITE 検査なら CRC8 は実質不要」→ 撤回。** 元の走査は CRC8 と sector cycle を検証します（`vendor/sdk-nrf-bm/subsys/fs/bm_zms/bm_zms.c:946-954`）。magic は header の識別であって整合性・安全性・認証の代わりではありません。data CRC も完全 read 時の検査（`:2308-2320`）を直接参照では迂回します。
4. **「差分はアドレス取得だけ」「約80行」→ 未測定の実装見積り。** 上の寿命・整合性・排他が未実装です。RRAM で読めることは ZMS 直接実行の実機合格ではありません。CPU が Ruby 命令をネイティブ実行する意味の XIP でもなく、VM が RRAM 上の命令データを読む意味です。
5. **「電源断でも旧プログラムは失われない」→ 無条件には保証しない。** data→ATE の順序と CRC による無効 record 除外は実装上の対策です。GC・clear・erase・生存参照・破損も含む復旧は本リポジトリでは試していません。raw の magic 最後書込みだけでも旧像保持は保証されません。
6. **「OpenBlink の offset は常に CPU 絶対アドレス」→ backend 条件付き。** Zephyr の `fs.offset` は flash device 内 offset です。OpenBlink の固定版 `storage.c:33-59` は `FIXED_PARTITION_OFFSET` を使います。CPU mapping base は driver/SoC ごとに照合が必要で、BM の base の扱いをそのまま一般化しません。

## 方式比較: いずれも未承認

| 案 | 利点 | 必須の条件・残るリスク |
|---|---|---|
| 共有 ZMS の内部 ATE を解決 | 新 partition 不要 | 全 writer/GC と VM の調停。毎 write 後の pointer 差替えだけでは実行状態を保てない |
| bytecode 専用 ZMS | 設定値 write と GC を分離 | 全 VM 参照を破棄して更新。内部構造への依存と CRC/cycle 検査。cache 無効/衝突時の走査 |
| raw bm_storage + header | 固定位置で寿命を管理しやすい | commit・検証・容量・復旧・更新頻度の設計。既存の A/B 不採用を勝手に変えない |
| 上流へ address/pin API を提案 | 保守性の改善候補 | 保持中 GC の契約も必要。外部への投稿は承認が必要。今回は投稿していない |

原報告は専用 ZMS を主案、raw を最小案として推奨しました。これは採用決定ではありません。[将来の OpenBlink 対応](../openblink/future-support.md)の再検討資料として残します。残る試験は resolver の正常・空・削除・破損・衝突・GC・電源断、SYMS を含む寿命、RRAM 対 RAM の性能です。
