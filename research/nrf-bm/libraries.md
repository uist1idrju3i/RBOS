# Bare Metal のライブラリ

## timer と scheduler

| API・機能 | 契約と RBOS での使い方 |
|---|---|
| `bm_timer_init(timer, mode, handler)` | single-shot / repeated を選ぶ |
| `bm_timer_start(timer, timeout_ticks, context)` | 単位は ticks。MS/US_TO_TICKS macro で変換 |
| `bm_timer_stop(timer)` | timer 停止 |
| `bm_scheduler_defer(...)` | ISR 等から処理を foreground へ遅延 |
| `bm_scheduler_process()` | main loop で定期実行が必要 |

timer の出典: `vendor/sdk-nrf-bm/include/bm/bm_timer.h:30-45,66-112`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/timer.rst:10-46`。resolution は 1 μs ですが、最小 timeout は `(5*1000000)/32768` μs、整数では 152 μs です。start は最小 ticks より小さい値を拒否します。

scheduler の出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_scheduler.rst:10-37`。これは関数イベントの queue で、mruby/c rrt0 の VM task scheduler の代わりではありません。`CONFIG_BM_SCHEDULER_BUF_SIZE` の容量と overflow の契約を決め、常時実行中の VM がいても process が進むよう設計します。

## bm_storage（将来の保存機能向け）

初期 bytecode は firmware 埋め込みです。以下の保存 API は将来の OpenBlink 対応の参考で、初期 bytecode backend の選定ではありません。

`bm_storage_init` で instance と領域を結び、read/write/erase を呼びます。完了 event、busy、program/wear/erase の単位を確認します。非同期 backend では受付成功と保存完了を区別し、完了まで入力バッファを維持します。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:15-32,63-121`。

| backend | 制約 |
|---|---|
| RRAM | SoftDevice 無効が必要 |
| SD | SoftDevice、NRF_SDH、ring buffer が必要 |

出典: 同 `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:143-159`。RBOS は S115 有効なので **SD backend を基本候補** とします。RRAM backend を SoftDevice と同時に使えると仮定しません。

同期 callback から次の保存処理を呼ぶと再帰が続く可能性があります。BM scheduler があれば同期 event を foreground へ遅延できます。出典: 同 `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:123-133`。完了 event 内で Ruby を再入させず、native の状態を更新して次の実行区切りで通知する設計にします。

## bm_zms

bm_zms は bm_storage 上で使う key-value storage です。少なくとも 2 sector が必要で、data と ID-ATE を書き、GC で有効な値を移します。ID-ATE は 32-bit key、位置、サイズ、CRC32 を持ちます。出典: `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:6-30,83-92`。

主 API は `bm_zms_mount`、`bm_zms_write`、`bm_zms_read`、`bm_zms_read_hist`、`bm_zms_get_data_length`、`bm_zms_calc_free_space` です。write の完了は event で通知され、len=0 は削除と同義、write の API 上限は 64 KiB です。これは現在の partition に 64 KiB 保存できるという意味ではありません。出典: `vendor/sdk-nrf-bm/include/bm/fs/bm_zms.h:152-205,227-305`。[将来の保存比較](../openblink/future-support.md)に採否をまとめます。

## ボタン、GPIOTE、周辺 I/O

| 機能 | 参照と設計上の確認点 |
|---|---|
| buttons | `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/buttons.rst:1-60`。有効レベル、debounce、callback context |
| bm_gpiote | `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_gpiote.rst:1-60`。複数利用者で instance/channel を管理 |
| nrfx | `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/bm_nrfx.rst:1-25`。BM の IRQ macro と予約資源に従う |
| LPUARTE | `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/lpuarte.rst:1-63`。REQ/RDY 配線とボタン・LED の共有を確認 |
| console | `vendor/sdk-nrf-bm/drivers/console/console_bm_uarte.c:1-80`。UARTE の出力経路を HAL に接続する候補 |
| logging | `vendor/sdk-nrf-bm/subsys/logging/CMakeLists.txt:1-7`。選択される backend と timestamp、出力容量を確定する |

表は参照箇所であり、全ドライバを実装する約束ではありません。初期 native class は LED/Button/GPIO までとし、ADC/PWM/I2C/UART は利用要件とピン競合を確認して順に追加する案です。

## MCUmgr

SDK は image、OS、settings の group を含み、transport には BLE MCUmgr service と BM UART があります。出典: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/Kconfig:5-9`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bluetooth/services/ble_mcumgr.rst:1-46`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:1-61`。

画像更新の BM 実装は slot0 を書き換える single-bank 用です。buffer の既定 128 KiB と非同期 write の進行を把握し、Ruby の転送 API と混同しません。出典: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/bm_img_mgmt.c:95-121,160-195`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:174-183`。

RBOS では firmware loader に画像管理を任せ、通常アプリには loader 遷移を用意し、`.mrb` 転送は将来範囲とします。認証・pairing、許可する group、設定書換え・reset の権限を決めてから公開します。

[調査索引へ戻る](../README.md)
