# 採否と未決事項

## 採用する方式

以下の利用者決定は 2026-11-08 時点のものです。実装の完了を意味しません。

| 決定 | 理由・境界 |
|---|---|
| mruby/c を OS の中核にする | rrt0 の VM タスクを使う。BM の関数イベントキューは別の役割 |
| nRF54L15-DK + NCS Bare Metal | 指定された開発対象と SDK |
| 公式 single-bank DFU | MCUboot、slot1 の firmware loader、BLE MCUmgr を使用 |
| `.mrb` は const 配列として firmware に結合 | RRAM から参照。全体を RAM 展開しない。更新は firmware DFU |
| S115 固定 | central を使用しない |
| OpenBlink 対応は将来 | BLE bytecode 転送・保存・reload は初期範囲外 |
| host compiler は vendor/mruby 4.0.0 | RITE0400 を生成。実行系は引き続き mruby/c |
| I/O の pin は Integer・String・DeviceTree-label Symbol を受理 | Nordic の物理番号と board の意味を Ruby から表せるようにする。GPIO/Button で実装し、他 class への展開は未完了 |

技術上の対応箇所: `vendor/mrubyc/src/rrt0.c:339-425`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_scheduler.rst:10-37`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:6-24`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:29-47`。

## I/O の pin 識別子

利用者が承認した方針は、Integer の `port*32+pin`（P1.13 は 45）、String の `"P1.13"`、DeviceTree-label Symbol の `:led0` / `:sw0` を受け付けることです。Integer は Nordic の物理 pin、String は可読な物理名、Symbol は board 上の意味を表します。同じ数値を全 MCU へ共通化する方針ではありません。

これは MPIG の Integer / platform 固有表現を土台とする RBOS の決定です。Symbol が MPIG の必須型であるという意味ではありません。GPIO は利用者の A 選択により、全表記を物理電気レベルで統一し、Symbol だけを active-low で反転しません。BM で削除される GPIO DT node の代わりに、RBOS の pin メタデータの node label と明示した sw alias を使います。label property は使いません。既定の公開範囲、未知の名前・非対応 pin・競合の例外と検査時点は [GPIO/Button 契約](../implementation/gpio-button-api.md)を参照してください。unit の識別子へ同じ三形式を自動適用する決定はしていません。

Button も利用者の A 選択により、`wait` が `[物理値, edge数]` を返し、`each_event` が呼出し task の block へ配送します。native は Ruby Proc を保持せず、IRQ では固定 event を置くだけです。console は A の UARTE20 維持で確定し、既存の pairing/bonding 非対応は維持します。

## ダイ温度の取得経路

2026-11-12 の利用者承認により、温度 backend は S115 公式の `sd_temp_get` を利用します。MPSL が TEMP を予約するため、nrfx_temp/register の直接操作と app 独自の IRQ 接続は採用しません。公開形は A の `Temperature.read`（引数なし、Float °C、取得失敗は RuntimeError）を選択しました。0.25°C単位の値を約50 µsの同期 API で得る仕様で、呼出し中は他 Ruby task が進みません。これは温度の承認済み例外で、実機評価は未完了です。[公開契約](../implementation/temperature-api.md)と [資源予約・出典](../implementation/resource-reservations.md)を参照してください。

## 三電源 ADC の選択と同時要求

利用者は `ADC.internal(:dvdd)` / `:avdd` / `:vdd` の factory と、測定中の後発呼出しを RuntimeError（busy）で拒否する方式を選択しました。順番待ち queue は作りません。`read_voltage` と `read` は Float の V、`read_raw` は signed Integer です。他 Ruby task と BM maintenance は待機中も進めます。停止要求の発行だけで DMA buffer を再利用せず、停止確認まで native lease を維持します。[入力・換算・取消しと検査](../implementation/adc-api.md)を正本とし、外部 pin ADC と実機の精度確認は含めません。

## SemVer と公開権限

利用者が承認した版管理の方針です。根拠となる規格、SDK の制約、parser 実行、ruleset の取得結果は [版管理調査](../release/versioning.md)に分けています。

| 項目 | 承認済み判断 |
|---|---|
| public API | Ruby class/method の引数・返り値・例外・待機、対応する Ruby の範囲と mrbc/mruby/c の版、board 設定規約（Symbol pin label 等）を宣言する。C backend 契約は内部。DFU/MCUmgr は実装時点で追加する |
| 増分 | SemVer 2.0.0 を採用。0.x の非互換変更は 0.MINOR、互換追加・修正は 0.x.PATCH。1.0.0 以降は SemVer の MAJOR/MINOR/PATCH 規則 |
| 正本 | application を追加する PR で VERSION を作り、CHANGELOG.md と対応させる。EXTRAVERSION が pre-release、署名 image は X.Y.Z+TWEAK。同じ X.Y.Z 内では TWEAK を単調増加し、数値4項目を 0–255 に制限する |
| 変更記録 | 日本語の Keep a Changelog 1.1.0。利用者に影響する変更は同じ PR の Unreleased を更新する。非推奨を明記し、少なくとも1回の MINOR release の猶予を経て削除する |
| 公開 | tag 作成・release 公開は管理者のみ。agent は行わない。v* tag の管理者 bypass 設定も管理者が行う。承認は設定変更の完了を意味しない |
| 最初の版 | 今は採番せず、最初の build 可能な firmware で 0.1.0。過去の release を作らない |

TWEAK の一意化は rollback 対策ではありません。BM MCUmgr の upgrade=true は build を比較しないため、同じ X.Y.Z の rc と正式版の更新経路を別途検証します。HW counter を含む保証は未確認です。

## 検討して不採用

| 案 | 不採用理由（2026-11-08） |
|---|---|
| MCUboot swap-offset / swap-move / scratch | NCS BM の公式 DFU は single-bank。既定 sysbuild は loader または single slot を選び、BM uploader は slot0 に直接書く。独自 A/B の検証範囲を増やさない |
| direct-XIP + revert | 2 つの実行位置・画像配置と復帰条件を設計する必要がある。共有 SoftDevice はアプリ A/B の外側。利用者は single-bank を選択 |
| アプリ領域を二等分した A/B | 更新用の同規模領域によりアプリ容量が減る。既存の非対称 slot0/slot1 は維持する |
| `.mrb` の A/B / 初期 storage 保存 | 最新指示で firmware 埋め込みへ変更。独立 bytecode 更新は行わない |
| S145 | central を使わないため不採用 |
| Ruby からの reload polling | 不要。初期は動的 reload 自体が範囲外 |

根拠: `vendor/sdk-nrf-bm/sysbuild/image_configurations/BOOTLOADER_image_default.cmake:8-12`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/bm_img_mgmt.c:95-121`、[boot/zephyr/CMakeLists.txt](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/zephyr/CMakeLists.txt#L159-L178)、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:29-47`。汎用 MCUboot の各方式は [docs/design.md](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/docs/design.md#L212-L455) から辿れます。[MCUboot 調査](../dfu/mcuboot.md)も参照してください。

「Nordic 非対応」は、この固定版 BM の公式 DFU 手順が A/B を提供しないという意味です。MCUboot 自体に swap 機能がない、改造しても絶対に動かないという意味ではありません。アプリ容量の減少は配置上の推論で、最終バイナリ容量は未確認です。

## 未決事項

| 項目 | 現時点の提案と残る確認 |
|---|---|
| compiler 配布 | vendor/mruby 4.0.0 を build。配布 OS、再現用 toolchain、生成物 hash を決める |
| console の将来拡張 | 現行は承認済みの UARTE20。RTT/BLE への変更や別の buffer 設計は今回採用していない |
| system-task 認証 | 初期は署名済み firmware 内コードを信頼。将来の外部コードには HMAC 等を設計 |
| 権限単位 | callback で VM 権限を検査。子 task、VM ID 再利用、破棄時の失効を決める |
| RAM と alignment | const blob とは別に IREP/文字列等を見積もり、配置と access 条件を検証 |

[埋め込み設計](../dfu/embedded-bytecode.md)、[HMAC](../openblink/hmac-authentication.md)、[将来の storage 検討](../openblink/future-support.md)を参照してください。storage backend は初期 RBOS の未決事項ではありません。emscripten HAL の Ruby 検査 CI は実装済みです。[検査手順](../../tools/mrubyc-wasm/README.md)を参照してください。

[調査索引へ戻る](../README.md)
