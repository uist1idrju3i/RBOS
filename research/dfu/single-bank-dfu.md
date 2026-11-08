# 採用する single-bank DFU

## 更新するものを分ける

2026-11-08 の決定は、firmware を公式 NCS BM の single-bank DFU、Ruby bytecode を const 配列で firmware に結合するものです。bytecode 更新も firmware 再build と DFU が必要です。A/B rollback は採用しません。[判断記録](../architecture/decisions.md)を参照してください。

公式方式は MCUboot、slot0 の main application、slot1 の firmware loader、共有 SoftDevice と metadata を使います。slot1 は旧版アプリの待避場所ではありません。application update は既存アプリを直接上書きし、reset 後に検証、不正なら loader で再更新を待ちます。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:6-24`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:14-47`。

## 起動と入口

| 状態・入口 | 動作と設定 |
|---|---|
| 有効な slot0、DFU 要求なし | MCUboot から application |
| slot0 が無効 | firmware loader に移行 |
| GPIO | `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_GPIO`。既定で button0、定義は board-config.h |
| reset pin | `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_PIN_RESET`。recovery sample を参照 |
| retention | `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_BOOT_MODE`。`bootmode_set(BOOT_MODE_TYPE_BOOTLOADER)` 後に reset |

出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/entering_dfu.rst:6-35`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/ug_dfu.rst:24-44`。retention の retained area は **GPREGRET1** です。loader 遷移 API をユーザー Ruby に無条件公開する案ではありません。

BLE MCUmgr loader は `SB_CONFIG_BM_FIRMWARE_LOADER_BT_MCUMGR` を使います。SDK の BLE loader が画像管理を担い、RBOS は特権 callback から boot mode を設定する構成案です。出典: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:142-177`、`vendor/sdk-nrf-bm/applications/firmware_loader/ble_mcumgr/prj.conf:1-40`。スマートフォン/CLI との接続・pairing・再送は本リポジトリでは試していません。

## partition と更新対象

S115 MCUboot target の既定は boot 31 KiB、storage 8 KiB（peer manager 4 KiB と storage0 4 KiB）、slot0 1316 KiB、slot1 64 KiB です。SoftDevice と metadata はその後に分離配置されます。完全な address 表は [構成概要](../architecture/overview.md)を参照してください。根拠: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:39-82`。

application update と installer update を区別します。installer は slot0 に一時的に配置されて動き、SoftDevice/loader を更新する方式です。通常 application と同じように使い続ける image ではありません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:26-42`。installer 更新時の電源断復旧と各版の互換性は実機試験が必要です。

## 成果物の選択

| `<build_dir>/` 以下 | 用途 |
|---|---|
| `firmware_loader/zephyr/zephyr.signed.hex` | 初期書き込みの loader |
| `mcuboot/zephyr/zephyr_signed_softdevice_flash_metadata.hex` | MCUboot + SoftDevice + metadata |
| `<app_name>/zephyr/zephyr.signed.hex` | 初期書き込みの app |
| `production.hex` | 上記を含む製造用 |
| `installer_softdevice_firmware_loader.bin` | SoftDevice/loader の DFU |
| `<app_name>/zephyr/zephyr.signed.bin` | application の DFU |

出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/ug_dfu.rst:51-70`。`.mrb` をここへ直接渡すものではありません。初期は Ruby プログラムも firmware に含め、独立した転送経路を作りません。

## 鍵と製品化

SDK の既定は dummy ED25519 key であり、試験・製品では project ごとに固有の鍵を作り、安全に保持する必要があります。推奨は pure ED25519、nRF54L の CRACEN/KMU 支援を利用できます。`SB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE` で署名用 PEM を指定します。秘密鍵はリポジトリへ置きません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:6-47`。

KMU 利用時は公開鍵の provisioning が必要で、未実施なら boot しません。既定の自動 keyfile と `west flash --erase/--recover` は開発用初期化手順に関係します。製造時の鍵生成、公開鍵書き込み、失効 slot、debug 保護は別途手順化します。失効機能は experimental で、初期 bootloader で有効化が必要です。出典: 同 `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:49-106`。

BOOTCONF lock による MCUboot の IRoT 化は boot partition を書き込み保護します。解除には erase all/recover が必要になるため、開発中に安易に有効化せず、復旧可能性を確認した上で製造設定に分離します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:49-75`。

## 受け入れ試験案

- 正しい鍵・版・target の signed app を BLE で更新し、起動を確認する。
- 不正署名、誤 target、途中切断、電源断、容量超過を拒否し、loader から再更新する。
- 三つの入口と無効 slot0 からの recovery を確認する。
- installer 更新と通常 app の再投入、鍵 provisioning 失敗時の復旧を試す。
- `.mrb` と peer-manager 保存領域が通常 firmware DFU で壊れないことを確認する。

いずれも未実施です。single-bank なので更新前 app への自動 rollback を受け入れ条件にしません。

[調査索引へ戻る](../README.md)
