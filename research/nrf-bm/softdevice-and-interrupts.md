# SoftDevice と割り込み

## S115 と S145

SDK v2.0.1 に含まれる SoftDevice は 10.0.1 です。S115 は peripheral 専用、S145 は central と peripheral に対応し同時接続数も多くできます。RBOS は BLE MCUmgr と peripheral の初期構成として S115 を推奨します。central または多接続が要件になれば S145 を評価します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:24-34`。

| nRF54L15 向け版 | NVM 本体 | RAM 本体 | IRQ stack の追加注意 | load address |
|---|---:|---:|---:|---:|
| S115 10.0.1 | `0x19400`（101 KiB） | `0x1080` | `0x700` | `0x163800` |
| S145 10.0.1 | `0x22400`（137 KiB） | `0x1480` | `0x700` | `0x15a800` |

出典: `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/doc/s115_10.0.1_release-notes.rst:19-40`、`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s145/doc/s145_10.0.1_release-notes.rst:19-40`。本体のサイズは MCUboot header/TLV を含む partition サイズとは異なります。また構成に応じた追加 RAM と board の予約を別に確認します。[メモリ予算](../architecture/overview.md)参照。

## 予約資源と priority

BM の割り込み番号は NVIC priority 0〜7 に直接対応し、SoftDevice 使用時は 0 と 1 を予約、アプリは 2〜7 を使います。Zephyr の zero-latency 構成の priority offset と混同しません。`BM_IRQ_DIRECT_CONNECT` と `BM_IRQ_SET_PRIORITY` は有効範囲を build-time assert します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:20-39`。

system timer は GRTC channel0 と GRTC_2_IRQn を使用し、bm_timer と logging timestamp の両方に関係します。GRTC と SYSCOUNTER は SoftDevice の前提でもあります。出典: 同 `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:8-18`。mruby/c の tick 用に同じ channel を無断で再設定しません。

SoftDevice が所有する peripheral の ISR は handler が転送します。これらは zero-latency IRQ とされ、`irq_lock` で mask できません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nrf_sdh.rst:23-28`。全割り込みを一律に止める HAL は設計しません。

資源の完全な予約表について、SDK 文書は SoftDevice Controller と MPSL の Integration Notes を参照させています。BM の短い一覧だけから「それ以外は全て自由」と結論しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:13-18`。個別の peripheral、DPPI、timer、IRQ 利用前に対象版の外部仕様と SD ヘッダを照合する作業は未完了です。

## observer とイベント処理

nrf_sdh は SoftDevice の enable/disable、IRQ 転送、BLE/SoC event、fault を扱います。observer は state、Bluetooth、SoC、stack の四種で、同種内の順序を HIGHEST/HIGH/USER/USER_LOW/LOWEST で指定します。この優先度を NVIC の数値や Ruby task priority と混同しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nrf_sdh.rst:10-55`。

設計案では ISR/observer 内で Ruby を直接呼びません。必要な情報を所有期限の明確な queue へコピーし、foreground で VM に渡します。BLE event のポインタを長期保持しない、queue overflow と接続切断を処理する、C callback の再入を防ぐことを試験項目にします。

## RBOS の割り込み資源一覧

実装前に、次の列を持つ一覧表をビルド構成ごとに作ります。現時点で空き資源を確定したものではありません。

| 列 | 記録する内容 |
|---|---|
| 所有者 | SoftDevice / BM system / RBOS driver |
| peripheral・channel | GRTC、GPIOTE、UARTE、DPPI 等の instance |
| IRQ・NVIC priority | 予約と衝突しない設定 |
| callback context | ISR / observer / foreground |
| 共有データ | 排他範囲、コピーの有無、寿命 |
| 最悪実行時間 | 実測値、BLE と tick への影響 |

[HAL 移植](../mrubyc/hal-porting.md)と合わせて P1 の受け入れ条件にします。実機の jitter・接続維持・低消費電力は未確認です。

[調査索引へ戻る](../README.md)
