# NFCのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `subsys/nfc/lib/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_NFC_PLATFORM` | y if NFC_T2T_NRFXLIB &#124;&#124; NFC_T4T_NRFXLIB | NCS_BM | select NRFX_NFCT; bool "Common NFC configuration for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/lib/Kconfig:6-13` |
| `BM_NFCT_IRQ_PRIORITY` | 5 if SOFTDEVICE; 3 | if BM_NFC_PLATFORM | range 2 7; int "NFCT interrupt priority for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/lib/Kconfig:16-24` |

## `subsys/nfc/ndef/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_NFC_NDEF` | 未宣言 | 直接指定なし | bool "NDEF libraries for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:7-11` |
| `BM_NFC_NDEF_PAYLOAD_TYPE_COMMON` | 未宣言 | 直接指定なし | bool "Standard NDEF Record Type definitions for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:12-16` |
| `BM_NFC_NDEF_MSG` | 未宣言 | if BM_NFC_NDEF | bool "NDEF Message generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:19-21` |
| `BM_NFC_NDEF_RECORD` | 未宣言 | if BM_NFC_NDEF | bool "NDEF Record generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:22-24` |
| `BM_NFC_NDEF_LE_OOB_REC` | 未宣言 | SOFTDEVICE; if BM_NFC_NDEF | select BM_NFC_NDEF_PAYLOAD_TYPE_COMMON; bool "NDEF LE OOB record generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:25-29` |
| `BM_NFC_NDEF_TEXT_RECORD` | 未宣言 | if BM_NFC_NDEF | bool "Encoding data for a text record for NFC Tag for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:30-32` |
| `BM_NFC_NDEF_URI_MSG` | 未宣言 | if BM_NFC_NDEF | bool "NDEF URI messages generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:33-35` |
| `BM_NFC_NDEF_URI_REC` | 未宣言 | if BM_NFC_NDEF | bool "NDEF URI record generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:36-38` |
| `BM_NFC_NDEF_CH_MSG` | 未宣言 | if BM_NFC_NDEF | select BM_NFC_NDEF_CH_REC; bool "NDEF pairing Connection Handover message generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:39-44` |
| `BM_NFC_NDEF_CH_REC` | 未宣言 | if BM_NFC_NDEF | bool "NDEF Connection Handover records generator library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:45-49` |
| `BM_NFC_NDEF_LAUNCHAPP_MSG` | 未宣言 | if BM_NFC_NDEF | select BM_NFC_NDEF_LAUNCHAPP_REC; bool "NDEF Launch App message library for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:50-55` |
| `BM_NFC_NDEF_LAUNCHAPP_REC` | 未宣言 | if BM_NFC_NDEF | bool "NDEF Launch App records for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:56-60` |
| `BM_NFC_NDEF_CH_MAJOR_VERSION` | 1 | if BM_NFC_NDEF_CH_MSG | int "Connection Handover major version" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:65-70` |
| `BM_NFC_NDEF_CH_MINOR_VERSION` | 5 | if BM_NFC_NDEF_CH_MSG | int "Connection Handover minor version" | `vendor/sdk-nrf-bm/subsys/nfc/ndef/Kconfig:71-76` |

## `subsys/nfc/t4t/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_NFC_T4T_NDEF_FILE` | y if NFC_T4T_NRFXLIB && BM_NFC_NDEF_MSG | 直接指定なし | bool "NFC Type 4 Tag NDEF File for Bare Metal" | `vendor/sdk-nrf-bm/subsys/nfc/t4t/Kconfig:7-11` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
