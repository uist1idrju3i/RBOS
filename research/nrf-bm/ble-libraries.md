# Bluetooth 共通ライブラリと peer manager

全公開関数・型・event は [API 索引](api-ble.md)、既定・依存・range は [Kconfig](kconfig-ble.md)へ分けています。共通 context は [SoftDevice 配送モデル](softdevice-and-interrupts.md)に従います。observer が IRQ か foreground かを、ライブラリ名だけで決めません。

## component ごとの適用

| component | 目的・主要な入口 | S115 と callback の扱い | RAM・RBOS backend 設計例 |
|---|---|---|---|
| ble_adv | init/start/stop、data_update、peer/allow-list reply、広告 mode event | peripheral 対象。extended advertising は S115 の対象外。observer に加え利用者の start 呼出からも状態が変わるので一つの owner に集約 | instance 内の広告 data と設定、SoftDevice の広告資源。`ble_advertise/start/stop`。name/UUID は Ruby から設定し board C に製品動作を書かない |
| ble_conn_params | ATT MTU・data length・PHY の get/set、conn override、更新 event | 対象。ただし coded PHY は S115 対象外。自動 GAP/MTU/data-length/PHY 更新は個別に無効化できる | 接続数と MTU/data length が SD RAM に影響。`ble_connection_config/status`。要求値と交渉結果を分ける |
| ble_conn_state | connection handle と index、role/security/flags、接続集合の列挙 | peripheral 分を使用。central 列挙 API も存在するが S115 で central 動作は使わない。切断後 handle の再利用に備える | 接続状態・user flag の固定表。`ble_connections/security_state`。Ruby object に SD の一時 event pointer を残さない |
| ble_db_discovery | init/service_register/start と発見 event | `SOFTDEVICE_CENTRAL` 依存なので S115 対象外。必要性を理由に S145 へ変更する計画ではない | default MAX_SRV=6 により discovery struct が増える。初期 Ruby backend に discovery を追加しない |
| ble_gq（BLE_GATT_QUEUE） | connection register、item_add、GATT request の queue と error callback | Kconfig は SOFTDEVICE 依存で、central 専用と一括扱いしない。利用 request が S115 の API 範囲にあるか個別確認。主な利用者の client/discovery は対象外 | default 1 connection、8 requests/connection、variable data heap 256 bytes。queue node と管理 overhead は別。`ble_gatt_submit` は必要になった場合のみ |
| ble_qwr | init、connection assign、attribute register、value_get、prepare/execute write event | GATT server の queued write として対象。user memory・長い value を caller が保持し、validate/execute の途中に VM 再入しない | MAX_ATTR default 0。登録表・buffer を製品に合わせて確保。`ble_gatt_long_write` 候補。認証を満たす前の値を適用しない |
| ble_racp | encode/decode、opcode/operator/response の codec | role 非依存。CGMS 等の Record Access Control Point 用。入力長・operand 検証を binding にも設ける | 利用者の packet buffer。通信 stack を別に起動するものではない。`ble_record_control_encode/decode`、必要時のみ公開 |
| ble_radio_notification | init に active/inactive handler を渡す | 対象。SWI02、priority default 5・range 5〜7。SoftDevice event observer とは異なる IRQ 経路。短い native 処理に限定 | handler と小さな状態。Ruby callback の精密 timing source とせず、`radio_activity` 計測を native で集約して通知 |
| ble_scan | start/stop、filter/params、scan report event | CENTRAL 依存、S115 対象外。scan の header と設定は索引に残す | scan buffer default 32 bytes、name/short name 各 32、filters 数で増加。初期 Ruby backend なし |
| peer_manager | init/register、security、peer load/store/delete、allow-list/privacy、PM event | 対象。SDH・timer・BM_ZMS 依存。bonding の永続書込みは非同期。切断と保存完了は別 event | FLASH_BUFFERS default 4、registrants 3、sector 1024 bytes。接続数・PSA key slot/heap も予算化。`ble_pair/bonds/delete_bond` は特権チェック付き |

各行の設定根拠は `vendor/sdk-nrf-bm/lib/bluetooth/ble_adv/Kconfig:1-136`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_params/Kconfig:1-167`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_conn_state/Kconfig:1-27`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_db_discovery/Kconfig:1-33`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_gq/Kconfig:1-39`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_qwr/Kconfig:1-23`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_racp/Kconfig:1-16`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_radio_notification/Kconfig:1-40`、`vendor/sdk-nrf-bm/lib/bluetooth/ble_scan/Kconfig:1-124`、`vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:1-124` です。API の寿命・event は上記索引の各 header に記載があります。coded PHY の制限は `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bluetooth/ble_conn_params.rst:1-150`。

## 共通 header（component と別の補助 API）

| header | 役割と使用方針 |
|---|---|
| ble_adv_data.h | advertising の encode/parse/search/name/UUID 検索。借用する packet/field の lifetime を native で管理 |
| ble_common.h | security mode、CCCD の notification/indication 判定。暗号化・認証を設定する際の共通規約 |
| ble_date_time.h | date/time encode/decode。時刻を計測・同期する clock ではない |
| ble_gatt_db.h | discovery の service/characteristic/descriptor の型。S115 向けに discovery API を有効化する根拠にはしない |

出典は `vendor/sdk-nrf-bm/include/bm/bluetooth/ble_adv_data.h:1-317`、`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_common.h:1-139`、`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_date_time.h:1-72`、`vendor/sdk-nrf-bm/include/bm/bluetooth/ble_gatt_db.h:1-81`。

## peer manager を使い切るための分担

公開面は `peer_manager.h`、`peer_manager_types.h`、`peer_manager_handler.h` と `nrf_ble_lesc.h` です。helper handler は security failure に対する切断、flash cleanup、log を提供します。LESC は ECDH と RNG、ECC P-256、PSA key slot または heap の設定が必要で、`nrf_ble_lesc_request_handler()` を main loop から実行する必要があります。debug private key export は製品で有効にしません。根拠: `vendor/sdk-nrf-bm/include/bm/bluetooth/peer_manager/nrf_ble_lesc.h:1-129` と `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/Kconfig:1-124`。

| 内部機構 | 役割・Ruby へ直接公開しない理由 |
|---|---|
| security_dispatcher / security_manager | SD の security event と pairing 要求の状態遷移。公開 pm_* 経由にして二重状態管理を避ける |
| id_manager / peer_id / conn_state | identity、peer ID、connection handle の対応。task ID を認証の代わりにしない |
| peer_database / peer_data_storage / pm_buffer | データ分類、BM_ZMS の永続化、非同期保持 buffer。Ruby の寿命管理と保存完了は backend が仲介 |
| gatt_cache_manager / gatts_cache_manager | remote/local DB と service changed の管理。GATT client 用機能は S115 初期範囲外 |
| auth_status_tracker | pairing の繰返し失敗に対する tracking/backoff。許可する peer 管理方針とは区別 |
| peer_manager_internal / nrf_strerror | 内部連携と error 表示。アプリ ABI として固定しない |

構成と責務の説明は `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bluetooth/peer_manager.rst:1-476`。内部 header の実在は `vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/include/modules/security_manager.h:1-164`、`vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/include/modules/peer_data_storage.h:1-219`、`vendor/sdk-nrf-bm/lib/bluetooth/peer_manager/include/modules/auth_status_tracker.h:1-58` を含む同 directory で確認しています。

## RAM と試験の境界

service instance、GATT table、SD の MTU buffer、queue、bonding buffer と crypto の作業域は別の費用です。上表の数値は Kconfig の宣言値で、最終 RAM/RRAM 合計は未測定です。通知の `NRF_ERROR_RESOURCES` 等を成功扱いせず、完了通知と backpressure を Ruby 側の event に写す設計とします。

S115 の制約、observer priority と NVIC priority の違い、RAM 問合せは [SoftDevice](softdevice-and-interrupts.md)、GATT services は [services](ble-services.md)、bond の保存先は [storage](storage-and-fs.md)へ進みます。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
