# storage と filesystem の使い分け

初期 bytecode は [firmware 埋め込み](../dfu/embedded-bytecode.md)です。以下はアプリデータ・bond・loader 連携のための SDK 機能であり、bytecode 保存方式の再変更ではありません。[API](api-storage.md) と [全 Kconfig](kconfig-storage.md)を併読してください。

| component | 役割・公開境界 | S115・context・所有権 | 費用と Ruby backend 設計例 |
|---|---|---|---|
| bm_storage | instance と partition を backend に結び init/uninit/read/write/erase/busy/info、write/erase result event を提供 | 対象。受付と完了を区別。`evt.is_async`・result・src/len/ctx を確認し入力 buffer を完了まで保持。全 backend の callback context が同じとは仮定しない | instance + backend 固有状態。`storage_read/write/erase/status`、原則管理 API。Ruby へ物理アドレスを無制限に渡さない |
| bm_storage/sd | SD の flash API と SoC 完了 event で非同期 queue を進める | S115 の基本候補。SOFTDEVICE・NRF_SDH・RING_BUFFER が必要。retry を尽くす失敗も伝播 | queue default 4、max retries 8、max write 32 bytes。operation descriptor・current op・erase block 設定分の buffer を別計上 |
| bm_storage/rram | RRAMC へ直接アクセスする同期 backend | `!SOFTDEVICE` 依存。S115 を有効にする RBOS では対象外。callback 内で次の要求を呼ぶと再帰する可能性 | hardware access の小さな状態。通常 app の backend に選ばない |
| bm_storage/native_sim | 試験用の simulated NVM | BOARD_NATIVE_SIM と ZTEST 依存。S115 実機用ではない | テスト用容量設定あり。Wasm fake と同一 driver ではなく、別の検証層 |
| bm_zms | key-value、mount/read/history/write/delete/clear/free-space と完了 event | S115 は SD backend 上で候補。read は同期、変更と mount の完了は event。read/free-space の全走査を tick で行わない | 最低 2 sectors、GC 用空き sector と ATE/CRC。lookup cache は任意、128 entries × 8 = 1024 bytes。op queue default 16。`settings_get/set/delete` の候補 |
| bm_rmem | retained SRAM の TLV clipboard、CRC32、init/read/write/clear | 対象。DT chosen の clipboard 領域が必要。再起動を跨ぐ app/loader の引継ぎであり不揮発保存ではない。CRC は改ざん認証ではない | TLV header 4 bytes、CRC TLV 10 bytes、payload、context。`boot_handoff_write/read` は特権内部機能 |
| ble_rmem | loader の advertising name を retention から読む。flat settings handler と連携 | 対象。`BM_FLAT_SETTINGS_BLUETOOTH_NAME` は `!SETTINGS`、BM_RMEM_CLIPBOARD を select。汎用 settings filesystem と同義ではない | name 最大 16 bytes の定義。`dfu_advertising_name` の候補。通常の BLE name 永続化とは別 |
| flash_map | Zephyr flash_area に app/installer の 2 entry を提供 | 対象だが loader 用の custom map。app の任意の領域公開用ではない | slot0/slot1 の定数 table。`image_target_info` の内部機構。slot1 を application の A/B bank と扱わない |

契約の根拠は `vendor/sdk-nrf-bm/include/bm/storage/bm_storage.h:1-359`、`vendor/sdk-nrf-bm/subsys/storage/bm_storage/Kconfig:1-52`、`vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/Kconfig:1-47` と `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/bm_storage_sd.c:1-569`。ZMS の cache/queue は `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:1-62`、API・64 KiB の write 上限（partition 容量ではない）と len=0 の削除は `vendor/sdk-nrf-bm/include/bm/fs/bm_zms.h:1-315`、sector/GC と ID-ATE は `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:1-366`。

retention の layout は `vendor/sdk-nrf-bm/subsys/storage/bm_rmem/src/bm_rmem.c:1-222`、公開関数・借用 pointer は `vendor/sdk-nrf-bm/include/bm/storage/bm_rmem.h:1-111`、name は `vendor/sdk-nrf-bm/include/bm/storage/ble_rmem.h:1-33` と `vendor/sdk-nrf-bm/subsys/storage/ble_rmem/Kconfig:1-23`。flash map は `vendor/sdk-nrf-bm/subsys/storage/flash_map/flash_map_mcumgr.c:1-27` と `vendor/sdk-nrf-bm/subsys/storage/flash_map/Kconfig:1-22`。

## 同期・非同期と再入

同期 backend では callback 内で次の write を要求すると呼出が積み重なる場合があります。BM_SCHEDULER があれば同期 event を foreground へ defer する SDK の仕組みがあります。SD backend は queue で処理しますが、Ruby VM の再入を許す根拠にはしません。完了 event を backend の request ID と結び、task の破棄後に借用 buffer を解放していないか確認します。根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:1-169`。

raw flash driver、bm_storage、ZMS を同じ領域へ独立に同時書込みする構成は避けます。instance ごとの排他と、peer manager が使う partition を含む領域所有権を決めます。新規保存には電源断、CRC 不一致、GC、queue 満杯、busy、寿命・wear を試験します。

## 予算と初期範囲

nRF54L15-DK の MCUboot/S115 構成では peer manager と storage0 はそれぞれ既定 4 KiB です。cache の RAM と実データ容量、空き sector、書換え回数は別々に見積もります。[board 統合](board-integration.md)に partition の根拠があります。peer manager の採用時には初期 BLE でも storage 依存が生じるため、「bytecode storage が将来」だから全 storage が不要とはしません。

ZMS の data CRC、history、GC、cache は必要性に応じて選び、free-space の全走査を毎回の Ruby read に追加しません。追加 RAM/RRAM 合計は未測定です。将来の OpenBlink 転送と単一保存の比較は [将来計画](../openblink/future-support.md)に残します。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
