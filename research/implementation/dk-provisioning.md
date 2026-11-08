# DK の初回準備と通常の書き込み

nRF54L15-DK で RBOS を動かす前の初回準備と、通常の書き込みを分けて記録します。build の手順は [build 再現手順](bm-build.md)にあります。この文書の手順は SDK の文書とソースから組み立てたもので、実機ではまだ試していません。結果は末尾の記録表に書き込みます。

## 初回準備が要る理由

RBOS の build は `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU=y` です。MCUboot は KMU に書いた公開鍵で app を検証するので、KMU に鍵がない DK では起動しません（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:65-80`）。build は公開鍵を書くための `keyfile.json` を build directory に作ります。鍵の名前は `BL_PUBKEY` です（`vendor/sdk-nrf-bm/cmake/sysbuild/generate_default_keyfile.cmake:11-19`）。

KMU に一度鍵を書くと、別の鍵へ替えるには SoC 全体の erase が必要です（[KMU provisioning の文書](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/doc/nrf/app_dev/device_guides/kmu_guides/kmu_provisioning_overview.rst#L147-L157)）。debug は SDK の開発用鍵、release は利用者の鍵で署名します。そのため、debug 用に準備した DK で release の image を起動するには erase と再準備が要ります。debug 用と release 用で DK を分けると、この erase を避けられます。

## 初回準備の二つの方法

| 方法 | コマンド | 消えるもの | 状態 |
|---|---|---|---|
| SDK の標準 | `west flash -d <build> --erase` | SoC 全体 | SDK 文書の手順。未試験 |
| erase なしの候補 | `nrfutil device x-provision-keys --key-file <build>/keyfile.json` の後に `west flash -d <build>` | なし（KMU が空の場合） | ソースから導いた候補。未試験 |

標準の方法では、runner が書き込みの後に `keyfile.json` を KMU へ書きます。この動作は `--erase` か `--recover` を付けたときだけです（workspace の `zephyr/scripts/west_commands/runners/nrf_common.py:404-409`）。

erase なしの候補は、runner が内部で使う操作と同じ `x-provision-keys` を単独で実行します。`west ncs-provision upload` も同じ nRF Util の命令を組み立てます。そこには erase の指定がありません（[ncs_provision.py](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/scripts/west_commands/ncs_provision.py#L109-L123)）。鍵の PEM から直接書く場合の例は次のとおりです。debug の鍵は MCUboot module の `root-ed25519.pem` です。

```sh
west ncs-provision upload --keyname BL_PUBKEY -s nrf54l15 -k <signing-key.pem>
west flash -d <build>
```

この候補は KMU が空の DK でだけ使えます。出荷時の DK の KMU が空か、出荷時の demo firmware の残りが RBOS の保存領域に影響しないかは、実機で確かめる必要があります。

## 通常の書き込み

MCUboot と鍵を変えない更新は `west flash -d <build>` だけを使います。nRF54L の nrfutil runner は erase を既定にしません（`nrf_common.py:367-374`）。script、CI、手順書の通常経路には `--erase`、`--recover`、`nrfutil device erase` を入れません。

`SB_CONFIG_BM_BOOT_BOOTCONF_LOCK_WRITES` は既定で無効で、RBOS も有効にしていません。有効にすると boot partition への書き込みに erase all が必要になります（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:55-67`）。採用は P5 で判断します。

## 実機確認の記録表

実機で確かめたら、日付、DK の revision、RBOS の commit、結果を書きます。

| 項目 | 手順 | 期待 | 結果 |
|---|---|---|---|
| DK の revision と認証表示 | 本体の印字を読む | 調査資料と一致 | 未確認 |
| erase なしの初回準備 | 上の候補の二行を実行 | MCUboot が app を起動 | 未確認 |
| SDK 標準の初回準備 | `west flash --erase` | MCUboot が app を起動 | 未確認 |
| LED | debug を書き込む | LED0（P2.09）が点灯 | 未確認 |
| console | UARTE20（TX P1.04）を board の既定の baud rate で開く | `RBOS v0.1.0...` の log | 未確認 |
| GPIO による loader 入口 | Button 0（P1.13）を押して reset | firmware loader が BLE で広告 | 未確認 |
| 通常の書き込み | 版を変えて `west flash` | 鍵の再準備なしで新しい版が起動 | 未確認 |
| recovery sample | sample を書き込み BLE で接続 | sample の説明どおり | 未確認 |

console の pin は `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:55-63` にあります。baud rate は書き込み前に SDK の log backend の設定で確かめます。

[調査索引へ戻る](../README.md)
