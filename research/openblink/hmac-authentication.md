# HMAC-SHA256 と system-task 認証

## 参照実装

対象は MDBT 版 d6efc07877ebac6bd55519b8458be4629bef80c3 の [hmac-sha256.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L1-L239) です。header は BSD-3-Clause / ViXion。**自前 SHA-256 ではなく PSA Crypto の wrapper** で、Zephyr logging、PSA、fn_t に依存します。

| API | 実装 |
|---|---|
| hmac_sha256_genkey(key) | 256-bit volatile HMAC key を生成し raw key を export |
| hmac_sha256_sign(key, hmac, data, size) | key import → mac_sign_setup → update → finish |
| hmac_sha256_verify(key, hmac, data, size) | key import → mac_verify_setup → update → verify_finish |
| key / MAC | key は32-byte value、PSA id、len。MAC は32-byte value、len |

出典: [header](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.h#L20-L71)、[実装](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L27-L239)。

## 実際の利用と未完成部分

main は起動時に debug_lib_hmac を呼び、鍵生成と dummy data の生成/照合を行います。[呼出箇所](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/main.c#L33-L41)、[実体](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/main.c#L83-L119)。system task 登録の HMAC は TODO で、VM ID を保存するだけです。[api.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L47-L67)。wrapper の存在だけで認証済みとはいえません。

参照コードは32 bytes未満の data を拒否し、import 結果を確認せず、verify は key/MAC の配列容量を使います。失敗時の operation abort と key destroy も必要です。[sign/verify](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/lib/hmac-sha256.c#L93-L239)。これは HMAC 一般の最低 message 長ではありません。raw key のログ出力・export 方針も本番用に再設計し、そのまま移植しません。

## RBOS の案と NCS BM

将来は bytecode 全体と長さ、形式、役割、バージョンを認証対象にし、成功後だけ system 権限を付与します。共有秘密を持つ側は MAC を生成できるため、第三者配布用署名との違い、provisioning、rollback 防止、鍵寿命・失効を定義します。初期 bytecode は firmware の ED25519 署名で保護し、HMAC を無条件に重ねる決定ではありません。

PSA は API、Oberon/CRACEN は backend の選択肢であり別の認証 protocol ではありません。BM の BLE loader も security 設定を持ちます。出典: `vendor/sdk-nrf-bm/applications/firmware_loader/ble_mcumgr/prj.conf:41-50`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:12-17,49-65`。

NCS の [HMAC sample 設定](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/samples/crypto/hmac/prj.conf#L16-L24) は PSA_WANT_ALG_HMAC、PSA_WANT_ALG_SHA_256、PSA_WANT_KEY_TYPE_HMAC を有効化します。これは Zephyr sample で、BM への組込みを実証した結果ではありません。

PSA wrapper の呼出パターンを参考に、これらの Kconfig と backend 対応を対象 BM で確認します。ED25519 の hardware 対応を HMAC の対応の証明には使いません。KAT、空・短い message、改ざん、誤鍵、切り詰め MAC、PSA error、鍵解放の試験は未実施です。

[調査索引へ戻る](../README.md)
