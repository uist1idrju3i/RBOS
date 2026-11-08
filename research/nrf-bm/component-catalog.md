# sdk-nrf-bm コンポーネント調査の索引と範囲

## 基準と読み方

2026-11-08 に v2.0.1 / `51484143c09199e19bccc16fa3b437f7a502a72b` を調査しました。対象は drivers、lib、subsys の全 component、include の全 62 header、別 include directory の bm_installs、nRF54L15-DK の board、全 27 samples です。API 名、型、event と Kconfig 宣言は別索引へ分離しました。SDK build、最終 .config、link map、実機・タイミング試験は未実施です。

「S115 対象」は SDK の役割・依存から適用候補にできるという意味で、RBOS の実装済み API や動作保証ではありません。「対象外」も棚卸しに残します。Ruby backend 名は設計例であり、現在の backend 契約に関数を追加したものではありません。

| 主題 | 用途・制約・RBOS への接続 | 公開 API | Kconfig |
|---|---|---|---|
| drivers | [LPUARTE・clock・console・flash](drivers.md) | [I/O](api-core.md) | [I/O](kconfig-core.md) |
| lib（非 BLE） | [timer・scheduler・buttons・GPIOTE・banner・queue・sensorsim](runtime-primitives.md) | [共通](api-core.md) | [共通](kconfig-core.md) |
| Bluetooth lib | [advertising・接続・GATT・peer manager](ble-libraries.md) | [Bluetooth](api-ble.md) | [Bluetooth](kconfig-ble.md) |
| Bluetooth services | [全 server/client](ble-services.md) | [services](api-services.md) | [services](kconfig-services.md) |
| storage・fs | [RRAM・retention・ZMS・flash map](storage-and-fs.md) | [storage](api-storage.md) | [storage](kconfig-storage.md) |
| MCUmgr・bm_installs | [protocol・transport・group・image 情報](mcumgr.md) | [管理](api-storage.md) | [管理](kconfig-storage.md) |
| logging・shell | [出力と対話処理](logging-shell-console.md) | [共通](api-core.md) | [共通](kconfig-core.md) |
| NFC | [platform・T2T/T4T・NDEF](nfc.md) | [NFC](api-nfc.md) | [NFC](kconfig-nfc.md) |
| SoftDevice・handler | [予約資源・context](softdevice-and-interrupts.md) | [handler](api-softdevice.md) | [handler](kconfig-softdevice.md) |
| board・module・sysbuild | [nRF54L15-DK](board-integration.md) | board-config は同文書 | [宣言](kconfig-platform.md) |
| samples | [27 個の実演内容](samples.md) | 各 sample の main.c | [sample の宣言](kconfig-samples.md) |
| 版差 | [公式 latest との照合](version-comparison.md) | latest の API は固定版と区別 | 更新は今回行わない |

## 設定の依存と棚卸し方法

568 個の config/menuconfig 宣言を、同名 symbol の再定義も別行として記録しました。driver/lib/subsys の 353 宣言に加え、依存を上書きする modules、sysbuild、全 samples、対象 board、NCS_BM の宣言を含みます。applications と tests の個別 Kconfig、他 board は対象外です。

根の `NCS_BM` が drivers/lib/modules/samples/subsys を取り込みます。`vendor/sdk-nrf-bm/Kconfig.nrf_bm:1-21`。Bluetooth の親設定は `vendor/sdk-nrf-bm/lib/bluetooth/Kconfig:1-31` と `vendor/sdk-nrf-bm/subsys/bluetooth/Kconfig:1-11`、NFC は `vendor/sdk-nrf-bm/subsys/nfc/Kconfig:1-13`、MCUmgr は `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/Kconfig:1-47` です。個別表のファイル内 if だけでなく、この source 経路と外部 Zephyr/NCS の symbol も依存に含めて読みます。

- Kconfig 表は宣言値です。choice の既定と外側の条件、`select`/`imply`、DT 条件、別ファイルでの default によって最終値が変わります。記載のない default を「無条件 n」とはしません。
- logging の module ごとの `*_LOG_LEVEL` や backend の形式選択は、外部 template が生成します。全 template 展開後の symbol 集合・既定は未解決です。例: `vendor/sdk-nrf-bm/lib/bm_timer/Kconfig:1-29`。
- API 表は関数・型・callback・enum/event・macro の名前索引です。引数・field・所有権を転載せず header を参照します。内部 header は安定した Ruby API 契約にはしません。
- clock/console/flash、queue、MCUmgr の多くは外部 Zephyr の API 型を再利用します。固定版に独自の公開 header がないものは、用途文書に明記しました。
- component ごとの byte 数が不明なら未測定とします。静的配列や Kconfig の容量は積算材料であり、padding・allocator 管理領域・SoftDevice RAM・stack を含む総量ではありません。

## 共通の実行規約（RBOS 設計案）

IRQ から Ruby VM、Ruby allocator、例外処理へ直接入らず、native 側で最小限の event をコピーし foreground で処理します。native method は実機処理を要求してすぐ戻る形を優先し、完了前の buffer を GC や task 破棄で失わないよう所有権を管理します。同期完了 callback の再帰にも備えます。

BM scheduler は mruby/c の task scheduler ではありません。rrt0 の idle だけに BM の処理を置くと、常時 ready の Ruby task がある間はイベントが進まない構成になり得ます。処理機会と一回の処理量を設計し、queue 満杯時の backpressure と診断を用意します。[実行プリミティブ](runtime-primitives.md)と[割り込み](softdevice-and-interrupts.md)に根拠をまとめます。

製品利用者は Ruby を書き、SDK の C API は nRF backend 内で使う方針です。DeviceTree や board 設定は別途必要です。共有 binding に Nordic header を取り込む方針ではありません。

[調査索引へ戻る](../README.md)
