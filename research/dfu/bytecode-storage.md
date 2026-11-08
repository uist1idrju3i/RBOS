# `.mrb` の単一コピー保存

## 採用方針と容量

ユーザー決定により `.mrb` は storage 内の **単一の論理プログラム** とし、実行用の A/B slot は作りません。firmware DFU と format・転送・有効判定を分けます。[決定表](../architecture/decisions.md)参照。

既定 DTS の storage は 8 KiB ですが、そのうち peer manager が 4 KiB、storage0 は **4 KiB** です。従って `.mrb` に 8 KiB 全部を使えるわけではありません。出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:44-59`。

最大 bytecode 長は未決定です。必要な Ruby プログラムを mruby 4.0.0 の mrbc で compile し、metadata、alignment、GC に必要な容量を足して決めます。OpenBlink の 16000-byte 上限をそのまま採用しません。現状の 4 KiB で不足するなら slot0/storage の境界変更を設計し、loader/MCUboot/installer を含む全 image の map を再検査します。

## backend 比較と推奨

| 項目 | bm_zms | raw bm_storage |
|---|---|---|
| 管理単位 | key-value、mount、GC | address と erase/write |
| 必要容量 | 最低 2 sectors、ATE と GC の余白 | 固定 header + payload + alignment |
| 更新 | 同一 key の新しい record を追加 | 旧 record を消して一つを上書き |
| 履歴 | 内部に旧 record が残る場合がある | 外部に rollback コピーを持たない |
| RBOS の負担 | mount/async 完了/容量管理 | commit marker、破損判定、電源断処理も自前 |

根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:6-30,80-92`、`vendor/sdk-nrf-bm/include/bm/fs/bm_zms.h:152-205,247-262`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:15-32,63-133`。

**推奨案** は bm_zms の一つの key に header + `.mrb` を保存する方式です。アプリとして A/B 選択や履歴 fallback は実装しません。ただし内部 GC が旧 record を保持する点は単一物理コピーとは異なります。「単一コピー」を物理的にも旧データを残さない意味にする場合は raw bm_storage を選ぶ必要があるため、採用確定前に意味を確認します。

SoftDevice 有効構成の storage は SD backend を使います。RRAM backend は SoftDevice 無効を要求します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:143-155`。BM_ZMS の採用には現行 storage0 の sector size/count と最大連続 record 長を試算する必要があり、まだ成立を確認していません。

## record と検証の案

次の項目は提案 format であり、現時点の RBOS 実装ではありません。

| field | 用途 |
|---|---|
| magic / format version | 保存形式の識別 |
| bytecode version | RITE0400 を要求 |
| payload length | partition と転送 buffer の上限検査 |
| digest | CRC32 または hash による破損検出 |
| trust class | system 権限には使わず、未信頼 user として扱う |
| valid/commit state | 書き込み途中の実行を防ぐ |

RITE0400 の根拠: `vendor/mrubyc/src/load.c:30-34,77-86`。CRC/hash の一致は権限認証ではありません。system Ruby を外部更新するなら、別途署名検証と信頼鍵・許可対象を設計します。

## 書き込み・起動の手順案

1. 転送開始時に全長を検査し、既存 VM を安全な区切りで停止する。二重更新を拒否する。
2. chunk の offset、重複、欠落、上限、timeout を検査する。
3. storage を更新し、非同期 write 完了まで buffer を保持する。raw 方式では invalid 化→erase→payload/header→commit を検討する。
4. read-back と digest を検査する。エラーなら無効のままにする。
5. 次回起動/再ロードで長さと RITE を検査し、`mrbc_create_task` の失敗を処理する。
6. 不在・空・破損・互換性不一致なら firmware 内の既定プログラムを使い、診断理由を残す。

storage の async 契約は `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:99-133`。loader の format 検査だけで悪意ある任意 bytecode の安全が証明されるわけではありません。

bytecode を直接 NVM から実行するか RAM にコピーするかは未決定です。少なくとも VM/IREP が参照している間に元データを更新・解放しない必要があります。loader は bytecode 内を参照して IREP を作ります。出典: `vendor/mrubyc/src/load.c:111-166`。初期案は検証済みの RAM buffer を VM 終了まで保持する方式とし、heap と別枠の RAM 予算へ計上します。

## 電源断と転送経路

single-copy のため、更新途中の電源断で利用者プログラムを失うことを許容し、内蔵既定プログラム + 再転送を復旧経路にします。bm_zms の内部 record が残る場合も、アプリの A/B rollback 保証として仕様化しません。

転送候補は BLE 独自 service、MCUmgr 独自 group、開発用 UART です。SDK の image group を `.mrb` 保存へ転用しません。OpenBlink の length/CRC/chunk は参考ですが、暗号化接続、更新権限、再送規約、host tool は RBOS 用に定義します。参考: [OpenBlink の転送処理](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/drv/ble_blink.c#L145-L211)。

## 未実施の試験

正常・空・上限ぴったり・上限超過、誤 RITE、digest 不一致、途中 reset、各 write の電源断、busy、GC、通信切断、再ロード時の buffer 寿命を確認します。旧 user program の自動復旧ではなく、**無効データを実行しないことと既定プログラムへ戻れること**を合格条件にします。

[調査索引へ戻る](../README.md)
