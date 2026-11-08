# 将来の OpenBlink 対応

初期 RBOS は const bytecode を firmware に結合し、更新は firmware DFU のみとします。BLE bytecode 転送・保存・VM reload は初期の受け入れ条件から外します。[埋め込み方式](../dfu/embedded-bytecode.md)参照。

## 再検討する項目

| 項目 | 将来の検討内容 |
|---|---|
| 転送 | BLE service/独自 MCUmgr group、offset、長さ、再送、権限、host tool |
| 保存 | bm_zms 単一 key と raw bm_storage を比較。A/B は作らない |
| 停止 | demo-nrf の native restart を参考に BM の安全な停止点を設計 |
| 信頼 | user/system を区別し、system bytecode の認証を要求 |
| 障害 | 電源断、破損、空領域、OOM、途中切断時に安全状態へ復旧 |

現行 DTS の peer manager と storage0 は各4 KiB です。bytecode 保存容量は別途計測します。出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:44-59`。

bm_zms は最低2 sectors と GC 用空き領域が必要で、内部に旧 record が残る場合があります。raw は header/digest/commit の設計が必要です。SoftDevice 有効時は SD backend を候補とし、RRAM backend は無効構成用です。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:6-30,168-174,211-219`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:99-155`。

## 保存方式の比較と record 案

旧 storage 設計から移した将来案です。bm_zms は key-value、mount、GC を提供する一方、最低2 sectors、ATE と GC 用容量を見積もる必要があります。raw bm_storage は address/erase/write を直接扱い、header、commit marker、破損判定、電源断処理を自前で作ります。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:6-30,80-92`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:15-32,63-133`。

将来の第一候補は bm_zms の単一 key ですが、内部旧 record は単一物理コピーとは異なります。最大 `.mrb` を実際に compile し、metadata、alignment、GC の容量を加えて成立を確認してから採否を決めます。現在の partition で成立するとは確認していません。

record は magic/format version、RITE0400、payload length、CRC/hash、trust class、valid/commit state を持つ案です。CRC/hash は破損検出であり system 認証ではありません。trust class の自己申告で権限を与えません。RITE の根拠: `vendor/mrubyc/src/load.c:30-34,77-86`。

1. 全長を検査し、VM を安全な区切りで停止して二重更新を拒否する。
2. chunk の offset、重複、欠落、上限、timeout を検査する。
3. async write 完了まで buffer を保持する。raw は invalid 化→erase→payload/header→commit を検討する。
4. read-back/digest を検査し、失敗なら無効のままにする。
5. 起動時に長さ/RITE と task 作成失敗を扱う。不在・空・破損・互換性不一致なら内蔵 default と診断を用意する。

async 契約: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:99-133`。単一論理プログラムの更新中断では旧 user program を失い得るため、内蔵 default + 再転送で復旧する設計です。bm_zms の内部履歴を A/B rollback 保証とはしません。正常・空・上限・超過・誤 RITE・digest 不一致・busy・GC・切断・各 write の電源断・参照寿命は未試験です。

初期の partition 拡張提案ではありません。採用時には [停止経路](architecture.md)と [HMAC](hmac-authentication.md)も再評価します。

[調査索引へ戻る](../README.md)
