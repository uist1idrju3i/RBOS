# SoftDevice と割り込み

## S115 に固定

SDK v2.0.1 に含まれる SoftDevice は 10.0.1 です。S115 は peripheral 専用、S145 は central と peripheral に対応し同時接続数も多くできます。RBOS は central を使用しないため S115 に固定します。S145 は不採用で、以下の値は不採用候補との資料比較に限ります。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:24-34`。

| nRF54L15 向け版 | NVM 本体 | RAM 本体 | IRQ stack の追加注意 | load address |
|---|---:|---:|---:|---:|
| S115 10.0.1 | `0x19400`（101 KiB） | `0x1080` | `0x700` | `0x163800` |
| S145 10.0.1 | `0x22400`（137 KiB） | `0x1480` | `0x700` | `0x15a800` |

出典: `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/doc/s115_10.0.1_release-notes.rst:19-40`、`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s145/doc/s145_10.0.1_release-notes.rst:19-40`。本体のサイズは MCUboot header/TLV を含む partition サイズとは異なります。また構成に応じた追加 RAM と board の予約を別に確認します。[メモリ予算](../architecture/overview.md)参照。

## 予約資源と priority

BM の割り込み優先度は NVIC priority 0〜7 に直接対応し、SoftDevice 使用時は 0 と 1 を予約、アプリは 2〜7 を使います。IRQ 番号や Zephyr の zero-latency 構成の priority offset と混同しません。`BM_IRQ_DIRECT_CONNECT` と `BM_IRQ_SET_PRIORITY` は有効範囲を build-time assert します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:20-39`。

system timer は GRTC channel0 と GRTC_2_IRQn を使用し、bm_timer と logging timestamp の両方に関係します。GRTC と SYSCOUNTER は SoftDevice の前提でもあります。出典: 同 `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:8-18`。mruby/c の tick 用に同じ channel を無断で再設定しません。

SoftDevice が所有する peripheral の ISR は handler が転送します。RADIO/TIMER10/GRTC_3 は zero-latency IRQ で、`irq_lock` で mask できません。AAR/CCM、CLOCK、ECB、SWI00 の転送は zero-latency ではありません。出典: `vendor/sdk-nrf-bm/subsys/softdevice_handler/irq_connect.c:47-74`。全割り込みを一律に止める HAL は設計しません。

資源の完全な予約表について、SDK 文書は SoftDevice Controller と MPSL の Integration Notes を参照させています。BM の短い一覧だけから「それ以外は全て自由」と結論しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:13-18`。P2 で固定版の予約を[資源予約表](../implementation/resource-reservations.md)にまとめました。各 backend の具体的な owner と実機競合の確認は未完了です。

## observer とイベント処理

nrf_sdh は SoftDevice の enable/disable、IRQ 転送、BLE/SoC event、fault を扱います。observer は state、Bluetooth、SoC、stack の四種で、同種内の順序を HIGHEST/HIGH/USER/USER_LOW/LOWEST で指定します。この優先度を NVIC の数値や Ruby task priority と混同しません。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nrf_sdh.rst:10-55`。

設計案では ISR/observer 内で Ruby を直接呼びません。必要な情報を所有期限の明確な queue へコピーし、foreground で VM に渡します。BLE event のポインタを長期保持しない、queue overflow と接続切断を処理する、C callback の再入を防ぐことを試験項目にします。

## 配送 model と callback の context

| NRF_SDH_DISPATCH_MODEL_* | 呼出の流れ | RBOS への制約 |
|---|---|---|
| IRQ | SD_EVT_IRQHandler → nrf_sdh_evts_poll → BLE/SoC observer | application event IRQ。SoftDevice 所有の zero-latency ISR とも別の context。Ruby へ直接入らない |
| SCHED | SD event IRQ → bm_scheduler_defer → main の bm_scheduler_process → poll | BM queue の容量不足で defer が失敗し得る。常時 ready の VM がいても process を進める |
| POLL | application が nrf_sdh_evts_poll を呼ぶ | 呼出側が実行頻度と context を決める。必要な IRQ notification の実装も確認 |

Kconfig choice は SCHED を default としますが、SCHED は BM_SCHEDULER に依存します。依存が満たされない場合も含め最終 choice は .config で確認し、文書の「IRQ default」だけから決めません。根拠: `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:16-46`、実際の dispatch は `vendor/sdk-nrf-bm/subsys/softdevice_handler/nrf_sdh.c:351-405`。[公式との照合](version-comparison.md)参照。

BLE poll は static event buffer を再利用して observer を順に呼びます。event の pointer を非同期 Ruby task へ借用せず必要な field をコピーします。callback が poll を再入させる構成も避けます。根拠: `vendor/sdk-nrf-bm/subsys/softdevice_handler/nrf_sdh_ble.c:370-399`。

## handler の API とメモリ設定

enable/disable request、observer ready、suspend/resume/is_suspended、poll、BLE enable、connection handle/index、SD RAM usage、info と event string が公開されています。state/stack/BLE/SoC の observer 定義 macro・型は [API 索引](api-softdevice.md)、全設定は [Kconfig](kconfig-softdevice.md)にあります。suspend は event interrupt の制御であり、SoftDevice 全停止の代わりではありません。根拠: `vendor/sdk-nrf-bm/subsys/softdevice_handler/nrf_sdh.c:304-349`。

S115 は SOFTDEVICE_PERIPHERAL と DATA_LENGTH_UPDATE を選択しますが CENTRAL/EXTENDED_ADVERTISING は選択しません。根拠: `vendor/sdk-nrf-bm/subsys/softdevice/Kconfig:33-46`。link count の S115 range は 0〜2、peripheral/total の default は各 1、ATT MTU default 23、attribute table default 1408 bytes、connection tag default 99 です。MTU と属性数の増加は SD の dynamic RAM を増やすため、NRF_SDH_BLE_LOG_SD_RAM_USAGE を使って確認します。根拠: `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:165-232`。

NRF_SDH_STR_TABLES は default y で、無効化すれば event 文字列の RRAM を減らす候補になります。clock source/accuracy、HFCLK latency と校正周期、PSA RNG seed も backend 初期化の設定対象です。root SOFTDEVICE と clock 条件は [platform 設定](kconfig-platform.md)と合わせて読みます。測定済みの RAM/RRAM 削減量はありません。

上記の文字列・clock・seed 設定は `vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:48-158,238-251` が根拠です。RBOS backend の設計候補は platform_init/poll、ble_enable/disable、ble_ram_usage で、製品利用者に raw SD enable/clock/IRQ 制御を無条件で公開しません。

## RBOS の割り込み資源一覧（統合時に作るもの）

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
