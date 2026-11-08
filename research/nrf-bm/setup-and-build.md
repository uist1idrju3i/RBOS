# NCS Bare Metal の環境とビルド

## バージョンを固定する

調査対象は BM v2.0.1、基盤となる NCS と toolchain は **v3.3.0** です。OpenBlink の v2.9.0 を使い回しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:6-9,37-49`、`vendor/sdk-nrf-bm/west.yml:1-20`。

公式の導入手順は nRF Connect for Desktop、J-Link、VS Code と nRF Connect 拡張を案内します。Quick Start で DK の初期設定を行い、BM v2.0.1 と対応 toolchain を選びます。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/install_nrf_bm.rst:10-109`。本リポジトリでは環境構築・ボードへの書き込みを試していません。

## submodule と west workspace の区別

RBOS の vendor は調査資料と依存バージョンを固定するための submodule です。これだけでは NCS の全依存、toolchain、west workspace が揃うとは限りません。公式 manifest は NCS の import を含みます。出典: `.gitmodules:1-16`、`vendor/sdk-nrf-bm/west.yml:1-42`。

以下は独立した SDK workspace を作る **計画例** です。既存の RBOS checkout を west init の対象にせず、対応 toolchain の shell 内で実施します。manifest の固定は release notes の v2.0.1 と west.yml に基づきます。

```sh
west init -m https://github.com/nrfconnect/sdk-nrf-bm --mr v2.0.1 ncs-bm-workspace
cd ncs-bm-workspace
west update
west zephyr-export
```

Python 依存は取得した SDK と toolchain の公式手順に従います。SDK の submodule を手作業で新しいバージョンへ変更しないでください。workspace の module SHA を `west manifest --freeze` 等で記録する方針です。公式の checkout 後の `west config manifest.path nrf-bm` と `west update` の説明は `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:37-49` を参照してください。

## 最初に動かすサンプル

次は SDK workspace のルートでの **検証予定コマンド** です。RBOS 自体のビルドコマンドではありません。主 target と single-bank の選択は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/ug_dfu.rst:80-104`、サンプルは `vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_entry/README.rst:1-60` に基づきます。

```sh
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  nrf-bm/samples/boot/mcuboot_recovery_entry --sysbuild -d build-recovery
west flash -d build-recovery
```

初回の鍵 provisioning、IRoT 設定、ボード復旧で erase/recover が必要な場合は保存データが失われます。通常の手順へ無条件に `--erase` を加えません。[DFU と鍵](../dfu/single-bank-dfu.md)を先に確認してください。

## sysbuild の設定面

以下は `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:7-230` の主な選択肢です。app の `prj.conf` に書く `CONFIG_*` と、`sysbuild.conf` の `SB_CONFIG_*` を区別します。

| `SB_CONFIG_` の後に続く名前 | 既定・意味 |
|---|---|
| `BM_BOOTLOADER_NONE` / `BM_BOOTLOADER_MCUBOOT` | bootloader 選択。target の設定も反映される |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_{NONE,RSA,ECDSA_P256,ED25519}` | nRF54L は ED25519 が既定。NONE は署名なし |
| `BM_CRACEN_MICROCODE_LOAD_ONCE` | 対応 ED25519 構成で既定 y |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE` | 署名用 PEM。既定の開発鍵は本番禁止 |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU` | KMU 鍵を利用。provisioning が必要 |
| `BM_BOOTLOADER_MCUBOOT_GENERATE_DEFAULT_KMU_KEYFILE` | KMU 用 keyfile 生成は既定 y |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_GPIO` | 入口 GPIO は既定 y |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_PIN_RESET` | reset pin 入口 |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_BOOT_MODE` | retention 入口 |
| `BM_APP_CAN_SETUP_FIRMWARE_LOADER_NAME` | loader の BLE 名を設定する実験的機能 |
| `BM_BOOT_IMG_HASH_ALG_{SHA256,SHA512,PURE}` | nRF54L ED25519 は PURE が既定。KMU 等の依存あり |
| `BM_BOOT_BOOTCONF_LOCK_WRITES` | IRoT 保護。既定有効とは扱わない |
| `BM_FIRMWARE_LOADER_{NONE,BT_MCUMGR,UART_MCUMGR}` | loader 選択。RBOS は BT_MCUMGR |
| `BM_BOOTLOADER_IMAGE_NAME/PATH` | MCUboot の image 名と source path |
| `BM_FIRMWARE_LOADER_IMAGE_NAME/PATH` | loader の image 名と source path |
| `SOFTDEVICE_{NONE,S115,S145}` / `SOFTDEVICE_FILE` | SoC と選択に対応した SoftDevice hex |
| `METADATA_SIZE` / `METADATA_ENTRY_SIZE` | nRF54L は `0x200` / 32 |
| `INSTALLER_HEX_OUTPUT` | debug 用 installer hex 出力 |

loader の有無による `BOOT_FIRMWARE_LOADER` / `SINGLE_APPLICATION_SLOT` の自動選択は `vendor/sdk-nrf-bm/sysbuild/image_configurations/BOOTLOADER_image_default.cmake:8-12` です。独自設定で汎用 swap mode を有効にする計画はありません。

## サンプルの選び方

| 分類 | 調べるサンプルと目的 |
|---|---|
| boot | `mcuboot_recovery_entry`（MCUmgr 経由の loader 遷移）、`mcuboot_recovery_retention`（bootmode 要求） |
| peripherals | `leds`、`buttons`、`pwm`、`timer`、`uarte`、`lpuarte`、`ppi` |
| Bluetooth | `hello_softdevice`、`ble_nus`、`ble_nus_central`、`ble_lbs`、`ble_hrs`、`ble_hrs_central` |
| その他の BLE | `ble_bms`、`ble_cgms`、`ble_hids_keyboard`、`ble_hids_mouse`、`ble_pwr_profiling`、`ble_radio_notification`、`peripheral_nfc_pairing` |
| NFC / subsys | `record_text_t2t/t4t`、storage 等。RBOS の初期実装では必須にしない |

分類の根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/install_nrf_bm.rst:137-153`。表の名前は `vendor/sdk-nrf-bm/samples/` のディレクトリ名です。各 sample の README と `sample.yaml` を使い、target、Kconfig、必要な外部配線を確認します。BLE MCUmgr loader 本体の選択と path は `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:142-177` にあります。

## リリースと成熟度

v2.0.0 は S115/S145 の役割分離と central 系の対応拡充等を含み、v2.0.1 は SoftDevice 10.0.1 の修正と MCUboot target の版情報ログ修正を含みます。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.0.rst:10-42`、`vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:6-9,69-81`。

成熟度の「Supported」は資料上の対応範囲であり、RBOS の結合試験済みという意味ではありません。Experimental は製品利用に推奨されず、API や検証が不完全な場合があります。機能・SoC ごとの表を個別に確認します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/bm_software_maturity.rst:14-29`。

[調査索引へ戻る](../README.md)
