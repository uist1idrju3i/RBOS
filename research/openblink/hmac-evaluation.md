# HMAC wrapper の実測と BM backend の評価

[調査索引へ戻る](../README.md)

2026-11-15 の host/固定 source 調査です。[初期調査](hmac-authentication.md)の後に実施しました。現在の採用方針と未実装の認証候補は [A2 脅威モデル](../implementation/a2-p3-authentication.md)へ分離しています。

## 参照実装・ライセンス

対象は [OpenBlink MDBT 版 d6efc078](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3)。`src/lib/hmac-sha256.c/.h:1-4` は BSD-3-Clause、Copyright 2025 ViXion Inc.。RBOS の [LICENSE](../../LICENSE)も BSD-3-Clause です。取り込む場合は著作権・条件・免責を保持します。今回 wrapper 自体は vendor/製品/research にコピーしていません。

| 観点 | 結果 | 固定 OpenBlink source |
|---|---|---|
| 実体 | PSA wrapper。鍵は32-byte value＋PSA handle | [header:20-71](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.h#L20-L71) |
| 長い鍵 | 32 bytes 超を拒否。64 bytes 超の鍵を hash する一般 HMAC の仕様を扱えない | [C:93-124](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L93-L124) |
| 短い message | 32 bytes 未満を拒否。HMAC 自体の制約ではない | 同 `:99-102,186-189` |
| input/error | import/export 戻り値未検査。verify は宣言 key/MAC 長ではなく配列容量を使う | [C:41-65,180-239](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L180-L239) |
| 後始末 | wrapper に key destroy、失敗時 abort、raw key zeroize がない。再 import で旧 handle を失う | 同 C 全体 |
| export/log | volatile key を EXPORT 許可で作り raw key を export。raw key の LOG_DBG コードもあるが module は現在 WRN | [C:19,41-81](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L41-L81) |
| 実使用 | 起動時 dummy data の debug sign/verify。system task の HMAC 検証は TODO | [main:33-41,83-119](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/main.c#L83-L119)、[api:47-67](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L47-L67) |

この実装から bytecode HMAC、provisioning、replay 防止が完成しているとは判断できません。そのまま移植することは勧めません。

## host の RFC 4231 試験

[harness と raw 結果](../implementation/a2-p3-evidence/README.md)を保存しました。元 wrapper は無変更、Zephyr logging のみ no-op。host Mbed TLS は `5bb86aeae32420e4f537e5cc390f7219a1bcf500`。PSA 直接経路と wrapper 経路を分けています。

| RFC 4231 case | PSA の既知値照合 | 元 wrapper sign | 元 wrapper verify | 鍵長 / data 長 |
|---|---|---|---|---|
| 1 | PASS | REJECT | REJECT | 20 / 8 |
| 2 | PASS | REJECT | REJECT | 4 / 28 |
| 3 | PASS | REJECT | ACCEPT | 20 / 50 |
| 4 | PASS | REJECT | ACCEPT | 25 / 50 |
| 5 | PASS：16-byte prefix | REJECT | REJECT | 20 / 20 |
| 6 | PASS | REJECT | REJECT | 131 / 54 |
| 7 | PASS | REJECT | REJECT | 131 / 152 |

RFC 出典は [RFC 4231 §4.2–4.8](https://www.rfc-editor.org/rfc/rfc4231.html)。case 5 は truncation の既知 prefix を比較し、PSA の full MAC も verify しています。wrapper の REJECT は非成功または既知値を得られなかった分類であり、全 case が同じ error code という意味ではありません。

追加で32-byte 鍵・32 bytes 超の data の roundtrip と改変 MAC 拒否は PASS、**MAC の宣言長を0にしても配列内の full MAC が正しければ verify 成功**を再現しました。暗号 primitive の誤りを示すのではなく、wrapper の入力制限と属性・長さ検査に関する結果です。空 message の PSA KAT、全 PSA error、全 key lifecycle の試験を完了した意味ではありません。

`cc -O2 -fstack-usage` では wrapper の frame は genkey 64 / sign 496 / verify 496 bytes でした。[stack 記録](../implementation/a2-p3-evidence/hmac-stack.tsv)は x86・logging 無効の測定で、呼出先を含む最大 stack や nRF 実測値ではありません。

software PSA の比較は [Mbed TLS psa_crypto_mac.c:423-450](https://github.com/nrfconnect/sdk-mbedtls/blob/5bb86aeae32420e4f537e5cc390f7219a1bcf500/library/psa_crypto_mac.c#L423-L450)の `mbedtls_ct_memcmp` で、同 file が一時 MAC を消去します。CRACEN も [cracen_psa_mac.c:137-162](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/subsys/nrf_security/src/drivers/cracen/cracenpsa/src/cracen_psa_mac.c#L137-L162)に長さ検査・定数時間比較があります。wrapper 自体の鍵消去とは別であり、元 OpenBlink firmware の backend binary の選択までは検証していません。

## 固定 NCS / BM の backend

以下は NCS `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956` の source/document 調査です。PSA は API、CRACEN/Oberon は backend、KMU は鍵の保管・利用方法であり、別々の認証 protocol ではありません。

| 対象 | 判定・制約 | 根拠：固定 NCS 内 |
|---|---|---|
| PSA Crypto | RBOS は NRF_SECURITY/PSA を有効化 | `firmware/common.conf:15-17` |
| CRACEN HMAC | source 上対応。実機動作は未確認 | [psa_driver.Kconfig:1677-1700](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/subsys/nrf_security/src/drivers/cracen/psa_driver.Kconfig#L1677-L1700) |
| Oberon HMAC | software driver に対応。Oberon core 有効と driver 有効は別 | [Kconfig:1199-1220](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/subsys/nrf_security/src/drivers/nrf_oberon/Kconfig#L1199-L1220) |
| KMU HMAC | 文書保証は SHA-256・128-bit key・Raw scheme。Protected は AES に限定 | [KMU model:210-219](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/doc/nrf/app_dev/device_guides/kmu_guides/kmu_psa_crypto_api_prog_model.rst#L210-L219)、[driver:1077-1082](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/subsys/nrf_security/src/drivers/cracen/cracenpsa/src/cracen_psa_kmu.c#L1077-L1082) |
| CPU RAM | HMAC key を key buffer にロード。KMU 採用だけで CPU RAM に出ないとはいえない | [driver:1336-1338](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/subsys/nrf_security/src/drivers/cracen/cracenpsa/src/cracen_psa_kmu.c#L1336-L1338) |

調査時の既存 debug `.config` は PSA_CORE_OBERON/PSA_CRYPTO_DRIVER_CRACEN 有効、OBERON driver 無効、CRACEN_LIB_KMU 有効でした。一方 PSA_WANT_ALG_HMAC / ALG_SHA_256 / KEY_TYPE_HMAC は未有効でした。これは再生成した build の証拠ではなく既存 artifact の観察です。抽出値は [config 観察記録](../implementation/a2-p3-evidence/crypto-config.txt)、現在の source の [sample 設定](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/samples/crypto/hmac/prj.conf#L16-L24)に必要3項目があります。

MCUboot artifact は KMU の公開鍵1組・base slot 242。SDK 文書の予約は boot 公開鍵242–243、IKG seed183–185、protected RAM 無効化248–249です（[予約表](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/doc/nrf/app_dev/device_guides/kmu_guides/kmu_cracen_overview.rst#L167-L209)）。追加鍵は予約と衝突させません。**実機 slot の占有、鍵 provisioning、256-bit HMAC key の BM 受け入れは未確認**です。

**今回、BM HMAC build・CRACEN/KMU の動作・BLE 認証・nRF 上の stack は未検証です。** host の software PSA 成功でそれらを代用しません。
