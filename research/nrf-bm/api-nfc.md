# NFCの公開 API 索引

固定版 v2.0.1 の公開 header を単位に、関数・型・event・macro の名前を整理します。関数の呼び方・バッファ寿命・引数と戻り値はリンク先を契約とします。`include/` の全 header と、別 include directory の `bm_installs.h` が対象です。内部 helper の field callback も名前索引に含みます。

## `ch.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/ch.h:1-563`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_ch_ac_rec_auxiliary_data_ref_add`、`nfc_ndef_ch_ac_rec_auxiliary_data_ref_clear`、`nfc_ndef_ch_ac_rec_payload_encode`、`nfc_ndef_ch_cr_rec_payload_encode`、`nfc_ndef_ch_hc_rec_payload_encode`、`nfc_ndef_ch_rec_local_record_add`、`nfc_ndef_ch_rec_local_record_clear`、`nfc_ndef_ch_rec_payload_encode` |
| struct・enum・typedef・callback | `carrier`、`nfc_ndef_ch_ac_rec`、`nfc_ndef_ch_ac_rec_cps`、`nfc_ndef_ch_ac_rec_ref`、`nfc_ndef_ch_cr_rec`、`nfc_ndef_ch_hc_rec`、`nfc_ndef_ch_rec` |
| enum 値・event 定数 | `NFC_AC_CPS_ACTIVATING`、`NFC_AC_CPS_ACTIVE`、`NFC_AC_CPS_INACTIVE`、`NFC_AC_CPS_UNKNOWN` |
| 定義 macro | `NFC_NDEF_CH_AC_CPS_MASK`、`NFC_NDEF_CH_AC_RECORD_DESC`、`NFC_NDEF_CH_AC_RECORD_DESC_DEF`、`NFC_NDEF_CH_CR_RECORD_DESC_DEF`、`NFC_NDEF_CH_HC_RECORD_DESC`、`NFC_NDEF_CH_HC_RECORD_DESC_DEF`、`NFC_NDEF_CH_HI_RECORD_DESC_DEF`、`NFC_NDEF_CH_HM_RECORD_DESC_DEF`、`NFC_NDEF_CH_HR_RECORD_DESC_DEF`、`NFC_NDEF_CH_HS_RECORD_DESC_DEF`、`NFC_NDEF_CH_RECORD_DESC`、`NFC_NDEF_CH_RECORD_DESC_DEF`、`NFC_NDEF_CH_REC_TYPE_LENGTH`、`NFC_NDEF_CR_RECORD_DESC` |

## `ch_msg.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/ch_msg.h:1-169`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_ch_msg_hi_create`、`nfc_ndef_ch_msg_hm_create`、`nfc_ndef_ch_msg_hr_create`、`nfc_ndef_ch_msg_hs_create`、`nfc_ndef_ch_msg_le_oob_encode` |
| struct・enum・typedef・callback | `nfc_ndef_ch_msg_records` |
| enum 値・event 定数 | なし |
| 定義 macro | `NFC_NDEF_CH_MSG_MAJOR_VER`、`NFC_NDEF_CH_MSG_MINOR_VER` |

## `launchapp_msg.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/launchapp_msg.h:1-61`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_launchapp_msg_encode` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `launchapp_rec.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/launchapp_rec.h:1-79`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `NFC_ANDROID_REC_TYPE_LENGTH`、`NFC_NDEF_ANDROID_LAUNCHAPP_RECORD_DESC`、`NFC_NDEF_ANDROID_LAUNCHAPP_RECORD_DESC_DEF` |

## `le_oob_rec.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/le_oob_rec.h:1-176`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_le_oob_rec_payload_constructor` |
| struct・enum・typedef・callback | `nfc_ndef_le_oob_rec_le_role`、`nfc_ndef_le_oob_rec_payload_desc` |
| enum 値・event 定数 | `NFC_NDEF_LE_OOB_REC_LE_ROLE_CENTRAL_ONLY`、`NFC_NDEF_LE_OOB_REC_LE_ROLE_CENTRAL_PREFFERED`、`NFC_NDEF_LE_OOB_REC_LE_ROLE_OPTIONS_NUM`、`NFC_NDEF_LE_OOB_REC_LE_ROLE_PERIPH_ONLY`、`NFC_NDEF_LE_OOB_REC_LE_ROLE_PERIPH_PREFFERED` |
| 定義 macro | `NFC_NDEF_LE_OOB_RECORD_DESC`、`NFC_NDEF_LE_OOB_RECORD_DESC_DEF`、`NFC_NDEF_LE_OOB_REC_APPEARANCE`、`NFC_NDEF_LE_OOB_REC_FLAGS`、`NFC_NDEF_LE_OOB_REC_LE_ROLE`、`NFC_NDEF_LE_OOB_REC_TK_LEN` |

## `msg.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/msg.h:1-167`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_msg_clear`、`nfc_ndef_msg_encode`、`nfc_ndef_msg_record_add` |
| struct・enum・typedef・callback | `nfc_ndef_msg_desc` |
| enum 値・event 定数 | なし |
| 定義 macro | `NFC_NDEF_MSG`、`NFC_NDEF_MSG_DEF`、`NFC_NDEF_NESTED_NDEF_MSG_RECORD`、`NFC_NDEF_NESTED_NDEF_MSG_RECORD_DEF` |

## `payload_type_common.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/payload_type_common.h:1-85`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | なし |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `record.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/record.h:1-294`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_bin_payload_memcopy`、`nfc_ndef_record_encode` |
| struct・enum・typedef・callback | `nfc_ndef_bin_payload_desc`、`nfc_ndef_record_desc`、`nfc_ndef_record_location`、`nfc_ndef_record_tnf`、`payload_constructor_t` |
| enum 値・event 定数 | `NDEF_FIRST_RECORD`、`NDEF_LAST_RECORD`、`NDEF_LONE_RECORD`、`NDEF_MIDDLE_RECORD`、`TNF_ABSOLUTE_URI`、`TNF_EMPTY`、`TNF_EXTERNAL_TYPE`、`TNF_MEDIA_TYPE`、`TNF_RESERVED`、`TNF_UNCHANGED`、`TNF_UNKNOWN_TYPE`、`TNF_WELL_KNOWN` |
| 定義 macro | `NDEF_RECORD_ID_LEN_SIZE`、`NDEF_RECORD_IL_MASK`、`NDEF_RECORD_LOCATION_MASK`、`NDEF_RECORD_PAYLOAD_LEN_LONG_SIZE`、`NDEF_RECORD_PAYLOAD_LEN_SHORT_SIZE`、`NDEF_RECORD_SR_MASK`、`NDEF_RECORD_TNF_MASK`、`NFC_NDEF_BIN_PAYLOAD_DESC`、`NFC_NDEF_GENERIC_RECORD_DESC`、`NFC_NDEF_GENERIC_RECORD_DESC_DEF`、`NFC_NDEF_RECORD_BIN_DATA`、`NFC_NDEF_RECORD_BIN_DATA_DEF` |

## `text_rec.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/text_rec.h:1-140`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_text_rec_payload_encode` |
| struct・enum・typedef・callback | `nfc_ndef_text_rec_payload`、`nfc_ndef_text_rec_utf` |
| enum 値・event 定数 | `UTF_16`、`UTF_8` |
| 定義 macro | `NFC_NDEF_TEXT_RECORD_DESC`、`NFC_NDEF_TEXT_RECORD_DESC_DEF`、`NFC_NDEF_TEXT_REC_TYPE_LENGTH` |

## `uri_msg.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/uri_msg.h:1-62`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_uri_msg_encode` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | なし |

## `uri_rec.h`

`vendor/sdk-nrf-bm/include/bm/nfc/ndef/uri_rec.h:1-162`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_ndef_uri_rec_payload_encode` |
| struct・enum・typedef・callback | `nfc_ndef_uri_rec_id`、`nfc_ndef_uri_rec_payload` |
| enum 値・event 定数 | `NFC_URI_BTGOEP`、`NFC_URI_BTL2CAP`、`NFC_URI_BTSPP`、`NFC_URI_DAV`、`NFC_URI_FILE`、`NFC_URI_FTP`、`NFC_URI_FTPS`、`NFC_URI_FTP_ANONYMOUS`、`NFC_URI_FTP_FTP`、`NFC_URI_HTTP`、`NFC_URI_HTTPS`、`NFC_URI_HTTPS_WWW`、`NFC_URI_HTTP_WWW`、`NFC_URI_IMAP`、`NFC_URI_IRDAOBEX`、`NFC_URI_MAILTO`、`NFC_URI_NEWS`、`NFC_URI_NFS`、`NFC_URI_NONE`、`NFC_URI_POP`、`NFC_URI_RFU`、`NFC_URI_RTSP`、`NFC_URI_SFTP`、`NFC_URI_SIP`、`NFC_URI_SIPS`、`NFC_URI_SMB`、`NFC_URI_TCPOBEX`、`NFC_URI_TEL`、`NFC_URI_TELNET`、`NFC_URI_TFTP`、`NFC_URI_URN`、`NFC_URI_URN_EPC`、`NFC_URI_URN_EPC_ID`、`NFC_URI_URN_EPC_PAT`、`NFC_URI_URN_EPC_RAW`、`NFC_URI_URN_EPC_TAG`、`NFC_URI_URN_NFC` |
| 定義 macro | `NFC_NDEF_URI_RECORD_DESC`、`NFC_NDEF_URI_RECORD_DESC_DEF` |

## `ndef_file.h`

`vendor/sdk-nrf-bm/include/bm/nfc/t4t/ndef_file.h:1-65`

| 区分 | 公開名（引数・field・戻り値の契約は上記 header） |
|---|---|
| 関数・inline | `nfc_t4t_ndef_file_encode` |
| struct・enum・typedef・callback | なし |
| enum 値・event 定数 | なし |
| 定義 macro | `NFC_NDEF_FILE_NLEN_FIELD_SIZE`、`nfc_t4t_ndef_file_msg_get`、`nfc_t4t_ndef_file_msg_size_get` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
