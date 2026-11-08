# NFC platform・tag・NDEF

[公開 API/型/macro](api-nfc.md)、[Kconfig](kconfig-nfc.md)が名前と宣言の全体索引です。S115 と組み合わせる候補ですが、NFCT/TIMER の予約と IRQ を別に管理します。ここで実機動作を確認したものではありません。

## platform と tag

| component | 機能・境界 | context・RAM・RBOS backend 設計例 |
|---|---|---|
| subsys/nfc/lib | NFCT と clock の連携、platform_setup、NFCID1、event_handler。実際の tag protocol library は外部 nrfxlib | field と HFCLK の準備を待って NFCT を有効化。NFCT と選択 TIMER の IRQ を接続、SD 時 default priority 5。platform buffer は T2T 用と T4T 用×2 の最大値。`nfc_start/stop` の低層候補 |
| Type 2 Tag | read-only NDEF、992 bytes の tag data。外部 `NFC_T2T_NRFXLIB` の API を利用 | NFCT/TIMER を専有。`nfc_payload_set` に渡す buffer を tag 動作中に解放・変更しない契約を確認 |
| Type 4 Tag | read-only/read-write NDEF、最大 64 KB の tag data。外部 `NFC_T4T_NRFXLIB` | 最大値は実 RAM 確保済み容量ではない。書込み event と buffer 返却を管理。`nfc_read/write_event` を foreground へ渡す候補 |
| subsys/nfc/t4t | NDEF file の length field を付ける `nfc_t4t_ndef_file_encode` | caller の buffer に encode。tag stack 本体と区別。`nfc_ndef_file_encode` の候補 |

根拠: `vendor/sdk-nrf-bm/subsys/nfc/lib/nfc_bm_platform.c:1-218`、`vendor/sdk-nrf-bm/subsys/nfc/lib/Kconfig:1-32`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nfc/integration_notes.rst:1-89`、`vendor/sdk-nrf-bm/include/bm/nfc/t4t/ndef_file.h:1-65`。T2T/T4T の application API は BM の include/ 内に全てがあるわけではなく外部 nrfxlib 側の契約を合わせて確認します。

nRF54L の nrfx NFCT は TIMER24 を既定で使い、NFCT とその TIMER は当該 library が唯一の利用者である必要があります。二種類の tag を同じ peripheral で同時に動かす計画にはしません。TIMER の変更は nrfx_config.h の明示設定が必要です。GRTC system timer と別の TIMER 資源である点にも注意します。根拠: 上記 integration_notes。

## NDEF component

| module/header | 役割・主 API | Ruby 側の用途候補 |
|---|---|---|
| msg.h | message descriptor、record_add/clear/encode | `nfc_message_encode(records)` |
| record.h | record descriptor、binary payload constructor、record_encode | 共通の `nfc_record_encode` |
| payload_type_common.h | standard record type の定数・共通宣言 | 独立 class でなく encoder の型選択 |
| text_rec.h | UTF encoding/language code と text payload | `nfc_text_record` |
| uri_rec.h / uri_msg.h | URI prefix と payload/message encoder | `nfc_uri_record/message` |
| launchapp_rec.h / launchapp_msg.h | Android/汎用 app link の record descriptor と message encode | `nfc_launchapp_message` |
| le_oob_rec.h | BLE LE OOB pairing payload constructor | 特権の `nfc_pairing_payload` |
| ch.h / ch_msg.h | carrier/alternative carrier、collision resolution、handover select/request/mediation/initiate | `nfc_handover_message`、pairing 設計と一緒に追加 |

関数・struct・enum と descriptor macro の根拠は [API 索引](api-nfc.md)の全 12 header、選択依存は `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:1-77` です。payload/record の記述子が借用する String/array は encode 完了まで保持し、tag stack が継続参照する場合は停止・更新完了まで native buffer を所有します。

## 導入時の境界と予算

純粋な NDEF encoder と hardware tag backend を分ければ、Ruby の正常・空・不正長・不正 UTF/record・容量不足を Wasm で検査できます。NFCT event、SD clock 要求、TIMER IRQ、実際の phone との互換は実機試験です。

library の作業域に加え payload、message/record descriptor と pointer array が必要です。platform buffer の外部 macro 値、外部 prebuilt library の RRAM と stack の最終量は未測定です。BLE OOB は [peer manager](ble-libraries.md)の LESC と組み合わせ、NFC field を検出したことを system-task の認証そのものにしません。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
