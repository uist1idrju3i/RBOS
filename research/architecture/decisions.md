# 採否と未決事項

## 採用する方式

以下の利用者決定は 2026-11-08 時点のものです。実装の完了を意味しません。

| 決定 | 理由・境界 |
|---|---|
| mruby/c を OS の中核にする | rrt0 の VM タスクを使う。BM の関数イベントキューは別の役割 |
| nRF54L15-DK + NCS Bare Metal | 指定された開発対象と SDK |
| 公式 single-bank DFU | MCUboot、slot1 の firmware loader、BLE MCUmgr を使用 |
| `.mrb` は storage 領域に単一コピーで保存 | ファームウェア画像とは別管理。A/B にしない |

技術上の対応箇所: `vendor/mrubyc/src/rrt0.c:339-425`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_scheduler.rst:10-37`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:6-24`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:29-47`。

## 検討して不採用

| 案 | 不採用理由（2026-11-08） |
|---|---|
| MCUboot swap-offset / swap-move / scratch | NCS BM の公式 DFU は single-bank。既定 sysbuild は loader または single slot を選び、BM uploader は slot0 に直接書く。独自 A/B の検証範囲を増やさない |
| direct-XIP + revert | 2 つの実行位置・画像配置と復帰条件を設計する必要がある。共有 SoftDevice はアプリ A/B の外側。利用者は single-bank を選択 |
| アプリ領域を二等分した A/B | 更新用の同規模領域によりアプリ容量が減る。既存の非対称 slot0/slot1 は維持する |
| `.mrb` の A/B | 利用者が不要と判断。途中更新時の復旧は単一コピーの無効判定と既定プログラムで扱う |

根拠: `vendor/sdk-nrf-bm/sysbuild/image_configurations/BOOTLOADER_image_default.cmake:8-12`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/bm_img_mgmt.c:95-121`、`vendor/sdk-mcuboot/boot/zephyr/CMakeLists.txt:158-178`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:29-47`。汎用 MCUboot の各方式は `vendor/sdk-mcuboot/docs/design.md:1-100` から辿れます。[MCUboot 調査](../dfu/mcuboot.md)も参照してください。

「Nordic 非対応」は、この固定版 BM の公式 DFU 手順が A/B を提供しないという意味です。MCUboot 自体に swap 機能がない、改造しても絶対に動かないという意味ではありません。アプリ容量の減少は配置上の推論で、最終バイナリ容量は未確認です。

## 推奨案と未決事項

| 項目 | 現時点の提案 | 決定に必要な条件 |
|---|---|---|
| SoftDevice | S115 を主対象とする | central、多接続が必要なら S145。利用予定の BLE 機能を決める |
| `.mrb` 保存 API | 小さい blob なら bm_zms + SD backend | 最大サイズ、更新頻度、GC 用空き容量を決める。大きい blob は raw bm_storage と比較 |
| コンパイラ配布 | mruby 4.0.0 の mrbc を固定 | 配布対象 OS、入手経路、ハッシュ、コンテナ利用の可否 |
| console | 最初は UARTE console | RTT / BLE への出力、割り込み中の禁止、バッファ上限 |
| システムタスク認証 | 組み込みコードを信頼の起点にする | 書き換え可能コードへ権限を渡す場合の署名鍵・検証方法 |
| 権限単位 | C callback で VM ごとの権限を検査 | 子タスクへの継承、VM ID 再利用、再ロード時の失効 |
| `.mrb` の電源断 | 未完了データは起動しない | 既定プログラム、再送手段、メタデータ破損時の扱い |
| 保存容量 | 専用領域を拡張する可能性あり | 既定 storage0 は 4 KiB。peer manager と分離を保つ |

これらは利用者に既に決定された事項ではありません。根拠と比較は [保存設計](../dfu/bytecode-storage.md)、[API 権限](../openblink/api-binding-patterns.md)、[SoftDevice](../nrf-bm/softdevice-and-interrupts.md)に集約します。S115/S145 の役割は `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:24-34`、コンパイラ版は `vendor/mrubyc/mrblib/global.rb:11-13` に基づきます。

[調査索引へ戻る](../README.md)
