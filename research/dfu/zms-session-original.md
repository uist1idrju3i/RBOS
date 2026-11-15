> **履歴資料（2026-11-15）**: [出典セッション](https://app.devin.ai/sessions/aa5ed531779b4af0920650da7a969077)の添付原報告です。以下は当時の主張・提案であり、現在の確認結果や承認ではありません。[再確認と訂正](zms-direct-execution.md)を先に読んでください。原文の誤り・未完の値も履歴として残しています。個人環境の絶対パスのみ `<checkout>/` に置換しました。今回の依頼は会話・ログ・報告の再確認と保存です。この写しでは新しい検証を行っていません。

# ZMS上のRubyバイトコード直接実行・圧縮 — 深掘り調査報告

対象: `uist1idrju3i/RBOS`(NCS Bare Metal, S115, nRF54L15) / 参考実装 `OpenBlink/openblink-demo-nrf`(Zephyr ZMS, NCS v3.3.0)
コミット・プッシュなしの調査のみ。引用は調査時のチェックアウト上のパスと行番号。

---

## 1. 前提の検証：OpenBlinkがRAM展開している本当の理由

### 1.1 現状の処理（OpenBlink）

- `src/app/mrubyc_vm.c:137-139` — `uint8_t bytecode_slot1[BLINK_MAX_BYTECODE_SIZE]` ×2本（`BLINK_MAX_BYTECODE_SIZE = 4016`、`src/app/blink.h:21`）をVMスレッドのスタック上に確保。
- `load_bytecode` (`mrubyc_vm.c:203-237`) → `blink_load` (`src/app/blink.c:60-63`) → `storage_read` → `zms_read` でZMSから**全量コピー**。
- `mrbc_create_task(bytecode_slot1, NULL)` でタスク化（同:164-165）。

### 1.2 なぜバッファが必要か（mruby/cの仕様）

mruby/cは**ロード時にバイトコードをコピーしない**。`vendor/mrubyc/src/load.c`(4.0.0):

- `load_irep_1`: `irep.inst = p;`（:153）、`irep.pool = p;`（:157）— 命令列・プール領域は**元バッファへのポインタ**を保持。
- `vm.c:160` `vm->inst = vm->cur_irep->inst`、callinfo(`vm.h:127`)にも同ポインタが保存・復元される。
- SYMS文字列はロード時にsymidへ変換され以後不要（永続ポインタを残さない）。poolは`OP_LOADL`等で実行中に参照（`load.c:398-` `mrbc_irep_pool_value`）。

→ **バイトコードバッファはタスクの生存期間中、ずっと読み取り可能でなければならない。** OpenBlinkのスタックバッファはこの寿命を担保しているだけであり、「アドレスが分かれば」RAMコピー自体は不要。OpenBlink側のmrubyc 3.4.1も同一構造（`mrubyc/src/load.c:151,155`）。

### 1.3 ユーザーの2つの仮説の判定

| 仮説 | 判定 |
|---|---|
| ZMSに格納された実体の先頭アドレスを取得する手段がない | **正しい**。`bm_zms.h`の全API（mount/write/read/read_hist/get_data_length/clear/delete/calc_free_space/active_sector_free_space）にアドレス返却APIなし。upstream Zephyrの新iterator API(`zms_iter_*`)もid/len/dataのみでアドレスは返さない |
| 不連続な配置になる可能性がある | **誤り**。ZMSは1回のwriteを**1セクター内の連続領域**に書く（`bm_zms.c:750-761` `zms_flash_data_wrt` → 単一`bm_storage_write`）。データがセクターを跨いで分割されることはない。注意点は別の2点：(a) len≦8はATE内部格納（`ZMS_DATA_IN_ATE_SIZE=8`）、(b) **GCでエントリが別セクターへ移動する** |

---

## 2. ZMS実体の直接参照は可能か — **可能**（内部構造を使う）

### 2.1 nRF54L15ではデータはそのままCPUアドレス

- `bm_zms_fs.offset` は**RRAM上の絶対アドレス**（`bm_zms.c:1999` `.addr = fs->offset`、サンプルは`DT_REG_ADDR`を渡す `samples/subsys/fs/bm_zms/src/main.c:14`）。
- 読み出しは両バックエンドとも直接メモリ参照：
  - RRAM backend: `bm_storage_rram.c:104` `nrfx_rramc_buffer_read(dest, storage->addr + src, len)`
  - **SoftDevice(S115) backend: `bm_storage_sd.c:407` `memcpy(dest, UINT_TO_POINTER(storage->addr + src), len)` — SD有効でもreadは直接**
- → RRAMに置かれたZMSデータは**そのままXIP実行可能**。これは現行RBOSの「リンク時埋め込みconst配列をそのまま実行」（`firmware/src/main.c:30` `mrbc_create_task(rbos_tasks[i].bytecode, NULL)`）と同じ性質。差分は「アドレスをどう見つけるか」だけ。

### 2.2 データアドレスの解決方法

アドレス解決式:

```
data_addr = fs->offset + SECTOR_NUM(ate_addr) * fs->sector_size + ate.offset
```

`struct zms_ate`（`bm_zms_priv.h:49-79`、16B `__packed`）: `crc8, cycle_cnt, len, id, {data[8] | offset, data_crc}`

`ate_addr`（最新ATEのZMSアドレス）の取得は2経路：

- **(a) lookup cache 経路（推奨・小さい）**：`CONFIG_BM_ZMS_LOOKUP_CACHE=y`（既定off、RAM 128×8B=1KB）を有効化すると `fs->lookup_cache[hash(id)%SIZE]` が最新ATEアドレスを保持（`bm_zms.c:301` でwrite完了時に更新、mount時にrebuild）。`zms_lookup_cache_pos`（:322-335）は15行のskeetoハッシュで複製容易。fsフィールドは公開。
- **(b) ATE走査経路**：`zms_find_ate_with_id`/`zms_prev_ate`相当を複製（~100-150行、内部構造への依存が大きく脆い）。

ATEの検証：`ate.id == id`、`ate.len != 0`、さらにデータ先頭が `"RITE0400"` であることを確認すればcrc8の再実装は実質不要（loader側も同じマジックを検査 `load.c:75-91`）。キャッシュ衝突時はid不一致で検出→フォールバック要。

→ 必要なのは**「キャッシュ読み＋ATE16Bを読む＋id検証」だけの薄いコード**（~80行）。`bm_storage`呼出しすら不要（全てメモリマップでmemcpy可）。

### 2.3 GCによる移動 — 設計上の本当の制約

- GCが動くのは `bm_zms_write`（領域不足時）と mount時のみ（`bm_zms.c` `zms_gc`）。
- GCは有効エントリを新セクターへコピー → **先に解決したポインタは無効化しうる**。
- **他IDへのwriteでもGCは起きる**。共有インスタンスで小さな設定値を頻繁に書く運用だと、実行中にbytecodeエントリが動く危険がある。
- 対策：
  - **A. bytecode専用のbm_zmsインスタンス（別partition）＋更新はVM停止中のみ** → ポインタ安定。推奨。
  - B. 共有インスタンスで「毎write後に再解決」→ 実行中VMを再起動するしかなく、Ruby状態を失う。非推奨。
- `mrbc_create_task`後もバッファ参照は続くため、解決は**VMタスク生成直前の1回**に限定する設計にする。

### 2.4 整合性

- 直接実行は`bm_zms_read`経路の`CONFIG_BM_ZMS_DATA_CRC`検証を迂回する → VM起動時に`crc32_ieee`をフラッシュ上で小バッファ分割検算するか、`"RITE0400"`チェック＋書込時検証で代替。
- bm_zmsのwriteはdata→ATEの順。電源断時は旧ATEが最新として残り、partial writeはATEのcrc8不一致で無効化される（旧プログラムは失われない）。

### 2.5 OpenBlink側への応用

Zephyr ZMSでも`fs->lookup_cache`は公開フィールド（`zms.h:61`）。nRF52 NVMC/54L RRAMともフラッシュは0x0〜メモリマップで`fs->offset`(=0x145000等)は絶対アドレス。→ **OpenBlinkも同じ手法でXIP可能**（bytecode_slot1/2の8KBスタックを節約できる）。

---

## 3. 代替設計の比較

| 案 | 内容 | 利点 | 懸念 |
|---|---|---|---|
| A. 共有ZMS＋アドレス解決 | 既存fsにbytecodeを格納、cache+ATE解決 | 追加partition不要 | **GCで他のwriteと絡み実行中に移動しうる**。再起動調停必須 |
| B. 専用ZMSインスタンス＋解決 | bytecode専用partition、VM停止中のみ更新 | 安定＋ZMSのGC/CRC/atomicを享受 | priv構造体(ATE/hash)の複製依存、cache有効化 |
| C. raw partition＋独自ヘッダ | 固定オフセットに`{magic,len,crc32}`+data | 最も単純・予測可能・依存なし | commit marker/CRCは自前（~100行）、wear無し（更新低頻度なら問題化しにくい） |
| D. upstreamにAPI追加 | `bm_zms_get_data_addr`相当 | 正当な拡張 | vendor編集不可ルールあり、sdk-nrf-bm取込待ち |

- RBOSの`research/openblink/future-support.md`は「bm_zms単一key vs raw bm_storage」を比較検討中で一致する。直接実行できることを踏まえると：**B（ZMSの利点＋安定運用）を主案、最小実装ならC**を推奨。
- Cを選ぶ場合のcommit手順例：データ書込→`len+crc32`書込→最後に`magic`書込（電源断時はmagicが立たず無効 → 前スロット/出荷デフォルトへフォールバック）。

---

## 4. mrubyバイトコードのminify（追加依頼①）

| 手法 | 効果 | 備考 |
|---|---|---|
| `mrbc --remove-lv`（LVAR除去） | **実測 -11%**（adc.rb 468→416B、button.rb 458→? B） | mruby/cは非IREP sectionをスキップするためLVARは純粋な無駄 |
| `-g`を付けない | DBG section非生成 | defaultでoff |
| メソッド名を短くする | SYMS block縮小 | SYMS文字列はload時symid変換に必須で除去不可 |
| 複数rbを1ファイルに | RITE+ENDヘッダ(~28B)×N本分 | 微少 |
| `-s`(MRB_DUMP_STATIC) | mruby/cでは実益なし | poolはload時コピー元参照のみ |

**発見**: mruby/c自身のmrblib Makefileは`mrbc -Bmrblib_bytecode --remove-lv`を使用（`vendor/mrubyc/mrblib/Makefile:48`）が、**RBOSの`firmware/cmake/mrubyc.cmake:57,63,93`のproduct bytecode生成には`--remove-lv`が付いていない**。付与するだけで~11%削減できる即効改善（実測検証済み）。

---

## 5. 圧縮（追加依頼①後半）

- zlib9で416B→276B（~66%）。小さいファイルでも一定の効果、大きくなるほど圧縮率は改善。
- 用途別の評価：
  - **ZMS/NVM節約**: RRAM 1.5MBに対しbytecode数KBでは実益は薄い（OpenBlinkのzms_storageは96KB）。
  - **BLE転送時間短縮**: OpenBlink「0.1秒Blink」の売りに寄与。圧縮転送→伸張は有効。
  - **RAM節約**: 伸張イメージをRAMへ置くと効果ゼロ。**「圧縮物→NVMのexec領域へストリーミング伸張→XIP」なら伸張時RAMは小窓のみ**で成立する。
- ライブラリ: sdk-nrf-bmにdecompress系なし。NCSには`nrf_compress`(LZMA、streaming API、MCUboot圧縮イメージ更新用、`subsys/nrf_compress`)があるがZephyr依存。BMではLZ4/heatshrink/miniz/LzmaDecをvendorするのが現実的（いずれも単一〜少数ファイル）。

---

## 6. mruby/cパッチによる圧縮bytecode直接実行（追加依頼②③）

命令フェッチは全て`*vm->inst++`の生ポインタ（`opcode.h:27-103` FETCH_*）。`vm->inst`はjmp/callinfo/catch handlerで直接演算・保存・復元される（`vm.c:160,176,215,255,339`）。`irep.pool`も生ポインタ（`vm.h:91` `mrbc_irep_pool_ptr`）。

| 方式 | 実装規模 | 効果 | 判定 |
|---|---|---|---|
| 全体一括伸張→RAM | 小（loader前処理のみ） | NVM節約のみ、RAM不変 | 目的に応じてあり |
| 圧縮物→NVMへ伸張→XIP | 小〜中（streaming伸張+flash書込） | NVM圧縮＋RAMほぼ0＋直接実行 | **最も素直** |
| irep単位遅延展開＋LRU | 中〜大 | 呼ばれないirep分だけRAM節約 | bytecode巨大化した場合のみ |
| ブロック圧縮＋索引＋小cache（ソフトzram） | 大 | inst/pool全アクセス仮想化、性能低下 | 非推奨 |
| 命令エンコード変更（Huffman等） | mruby側codegen改造も必要 | 学術先例あり（TinyVM系、`TR_0001`等） | 実用外 |

→ 「**圧縮してZMS/rawに保存→実行時にNVM exec領域へ伸張→XIP**」が現実解。bytecode数KBの現状でirep単位以下の圧縮実行は実装コスト対効果が悪い。なお「圧縮bytecodeをそのまま逐語実行」は全fetch経路の仮想化が必要で、mruby/c上流互換性も失うため推奨しない。

---

## 7. Zram相当をZephyrに（追加依頼④）

- **公式**: `CONFIG_DEMAND_PAGING`+backing storeは`CONFIG_MMU`必須（x86_64/AArch64/ARC等）。**Cortex-M33はMPUのみでMMUなし** → ページフォルト型の透明圧縮RAMはハード的に不可能。Zephyrにzram/zswap相当は存在しない。
- **コミュニティ/学術**: CRAMES（Linux VM前提）、MEMMU（MMU-less向け・学術実装）、MiniMem（Linux kernel module、PTE marker + kprobe）。いずれもM-class Zephyrには転用不可。
- コミュニティ調査で「MMUのないMCU上で透過的圧縮RAM」の実用実装は見つからなかった。**実質的な代替は6の「アクセス経路を絞った圧縮キャッシュ」であり、対象をmruby/cのbytecode/heapに限定しないと現実的でない**。
- 参考: mruby/c heap(`alloc.c`)のオブジェクトを透明圧縮するには全`mrbc_value`参照経路の書き換えが必要 → 非現実的。

---

## 8. 結論と推奨

1. **ZMS内データの直接実行は実現可能**（lookup_cache＋ATE 16B読み、~80行の薄いコード）。ユーザーの「アドレス取得手段がない」は公開APIとして正しいが、内部構造を使えば解決できる。「不連続」は誤りで、実際の制約は**GCによる移動**のみ。
2. GC対策として**bytecode専用のbm_zmsインスタンス**（更新はVM停止中のみ）か、**raw partition＋独自ヘッダ**を推奨。共有ZMSは実行中移動の危険がある。
3. minifyは`--remove-lv`を`mrubyc.cmake`に付与するだけで~11%（既に未適用を発見）。
4. 圧縮は「BLE転送・NVM削減」に有効。**「圧縮→NVM伸張→XIP」**が最も素直な直接実行の形。圧縮直接実行・圧縮メモリ実行は現サイズでは対費用効果が悪い。
5. zram相当はZephyr/Cortex-Mに実用実装なし（MMU不可）。透明圧縮RAMは本件では選択肢外。

## 9. 未検証・要確認事項

- RRAM読み出し性能：命令フェッチ毎のRRAMアクセスはRAM比で遅い可能性（`nrfx_rramc`のread path性能）→ 実機ベンチ推奨。
- `zms_lookup_cache_pos`/`struct zms_ate`の複製は`bm_zms_priv.h`依存 → vendorピン留めで管理するかupstream提案の検討。
- lookup_cache無効時のフォールバック（ATE走査実装量）と、GC直後のcache再構築タイミング（write完了イベント後に解決すること）。
- OpenBlink側に同様のXIP適用は可能（スタック8KB節約）だが、両者のzms構造体は別物（bm_zms_fs vs zms_fs）で実装は別途必要。

[調査索引へ戻る](../README.md)
