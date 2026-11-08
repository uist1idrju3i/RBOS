# RBOS の構成、起動、メモリ

## 構成案

RBOS は mruby/c の VM と rrt0 スケジューラを OS の中核に置きます。NCS Bare Metal のイベント処理を併用し、別の RTOS のタスクへ Ruby タスクを一対一で対応させる構成にはしません。rrt0 が VM を実行する根拠は `vendor/mrubyc/src/rrt0.c:339-425`、BM のイベント実行モデルは `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_scheduler.rst:10-37` です。

```text
MCUboot
  +-- slot0: RBOS application
  |     +-- mruby/c VM + rrt0 scheduler
  |     +-- Bare Metal HAL + native classes
  |     +-- trusted system Ruby tasks
  |     +-- user Ruby tasks
  +-- slot1: BLE MCUmgr firmware loader
  +-- shared SoftDevice
  +-- metadata
  +-- storage: bytecode and application data
```

ブートローダ、slot0、slot1、共有 SoftDevice、metadata、storage の役割は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:14-47` に基づきます。Ruby タスクと権限境界は RBOS の設計案です。

## 起動と更新

1. MCUboot が画像を検証し、通常は slot0 の RBOS を起動します。
2. GPIO、リセット要因、retention の要求、または不正なアプリ画像に応じて slot1 の loader に入ります。
3. RBOS は保存領域の準備、mruby/c のヒープ初期化、ネイティブ API 登録、システムタスク、利用者タスクの順に初期化する設計とします。
4. ファームウェア更新では Ruby を実行し続けず、再起動して loader に移ります。

1・2 の根拠は `vendor/sdk-mcuboot/boot/zephyr/firmware_loader_bm.c:232-293`、4 の方式は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/entering_dfu.rst:6-10` です。3 の順序は未実装で、保存データの検証失敗時は組み込み既定プログラムだけを起動する案です。

## S115 + MCUboot の RRAM 配置

主対象は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` です。以下は SDK の DK 定義を読み取った値であり、RBOS の最終配置ではありません。

| 領域 | 開始 | サイズ | 終端（含まない） |
|---|---:|---:|---:|
| boot | `0x000000` | 31 KiB | `0x007c00` |
| storage | `0x007c00` | 8 KiB | `0x009c00` |
| 未使用（整列） | `0x009c00` | 1 KiB | `0x00a000` |
| slot0 | `0x00a000` | 1316 KiB | `0x153000` |
| slot1 / loader | `0x153000` | 64 KiB | `0x163000` |
| SoftDevice 画像領域 | `0x163000` | 103 KiB + `0x200` | `0x17ce00` |
| metadata | `0x17ce00` | `0x200` | `0x17d000` |

出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:39-82`。終端は開始とサイズから計算しました。slot1 は第二アプリバンクではありません。

storage の内訳は peer manager 4 KiB と storage0 4 KiB です。8 KiB 全部を `.mrb` に割り当ててはいけません。バイトコード用領域を拡大する場合は独自 board/overlay で slot0 との境界も管理します。出典: 同 DTS の `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:44-59`。[保存設計](../dfu/bytecode-storage.md)で上限を検討します。

## SRAM と RAM 予算

同 DTS の `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:94-104` では SRAM の親領域が `0x20000080` 起点です。SoftDevice 用 subregion は相対 `0x0`、サイズ `0x4380`、app_ram は相対 `0x4380`、237 KiB です。したがって app_ram の物理開始は計算上 `0x20004400`、終端は `0x2003f800` です。retained clipboard は `0x2003fb00`、`0x100` バイトで、app_ram とは別です（同 DTS `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:13-20`）。

S115 自体の最小 RAM 仕様 `0x1080` と、board 定義の予約 `0x4380` を混同しません。前者は SoftDevice のリリースノート、後者はこの board の構成値です。出典: `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/doc/s115_10.0.1_release-notes.rst:19-30`。

| 項目 | 調査値・設計上の扱い |
|---|---|
| アプリ全体の上限 | DK 定義は 237 KiB。静的領域、ヒープ、スタック、バッファを全て含める |
| mruby/c ヒープ | RBOS では未決。OpenBlink の 48 KiB を参考値として比較するだけ |
| VM・C スタック | OpenBlink の専用スレッドは 96 KiB。BM にそのまま移植しない |
| MCUmgr 画像バッファ | `CONFIG_BM_MCUMGR_GRP_IMG_BUFFER_SZ` は nRF54L15 で既定 128 KiB。通常アプリにも組み込む場合は競合を評価 |
| `.mrb` 読み込み | blob 本体、検証用領域、転送領域、VM ロード後の追加確保を別々に見積もる |

出典: [OpenBlink の定数](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/mrubyc_vm.c#L39-L47)、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:174-183`。

**容量上の衝突**: 48 + 96 + 128 = 272 KiB で、237 KiB を超えます。ただしこれは参照実装の値を同居させた仮計算で、実ビルドの不足を確認した結果ではありません。loader と通常アプリは別画像で動くため、両方の RAM を無条件で加算するのも誤りです。

設計案は、画像 DFU を専用 loader に閉じ込め、通常アプリでは `.mrb` 転送だけを用意することです。必要なら画像バッファを縮め、スタックの最大使用量を測定します。最終的には通常アプリ・loader・MCUboot の各 map と実測値を別々に保存します。

[調査索引へ戻る](../README.md)
