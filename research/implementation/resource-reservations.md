# P2 の資源予約と配送 context

[調査索引](../README.md) / [チェックリスト](checklist.md#p2-native-api-と資源)

## 対象と確認の限界

調査基準は RBOS `57dcd09`、BM v2.0.1、S115 10.0.1、NCS v3.3.0 です。以下は固定版の仕様と source を照合した予約表であり、実機での競合・時間上限の確認ではありません。GPIO/Button、温度、三電源 ADC の driver は未実装です。採用する channel、DMA buffer、pin の owner は各 backend の追加時に確定します。

S115 の予約は `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/nrf_sd_def.h:54-77` に従います。S115 10.0.1 が NCS v3.3.0 の Controller/MPSL を内包する根拠は `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/doc/s115_10.0.1_release-notes.rst:49-51` です。予約全体は [MPSL Integration Notes（3.3.0）](https://docs.nordicsemi.com/bundle/ncs-3.3.0/page/nrfxlib/mpsl/doc/mpsl.html)と [Controller Integration Notes（3.3.0）](https://docs.nordicsemi.com/bundle/ncs-3.3.0/page/nrfxlib/softdevice_controller/doc/softdevice_controller.html)の nRF54L の一覧を合わせて照合しました。

## peripheral と IRQ

| 資源 | 所有者・予約 | RBOS の制約 |
|---|---|---|
| NVIC priority 0/1 | S115 | application IRQ は2–7。IRQ 番号と priority は別の値 |
| RADIO、TIMER10、GRTC_3 | S115 の zero-latency 転送 | IRQ handler と priority を変更しない。`irq_lock()` で止まると仮定しない |
| TIMER20、ECB00 | MPSL | application の直接操作は禁止。TIMER10/20 は `SD_TIMER1X/2X_INSTANCES_USED=1` |
| AAR00/CCM00、RRAMC | Controller | 暗号処理・NVM を独自に動かさず、SD API/BM storage の経路を使う |
| CLOCK、TEMP | MPSL | raw register・nrfx の直接操作をしない。TEMP の IRQ 番号215は利用許可を意味しない |
| GRTC CC7–11、GRTC_3 IRQ229 | S115、mask `0xF80` | nrfx の許可 channel と交差させない |
| GRTC CC0、GRTC_2 IRQ228、SYSCOUNTER | BM system timer | tick と logging timestamp の基盤。RBOS tick は BM timer を使い、CC0 を追加確保しない |
| SWI00–02 | S115、mask `0x7` | SD event は SWI01 IRQ29、NVIC priority6。独自 handler に置き換えない |
| UARTE20 / SERIAL20 IRQ198 | BM console/logging、既定 NVIC priority5 | TX=P1.04、任意 CTS=P1.07。SPIM/TWIM 等の同じ SERIAL20 instance と共有しない |
| UARTE30 / SERIAL30 IRQ260 | BOARD_APP と BOARD_SHELL の両方の既定 | TX/RX=P0.00/P0.01、任意 RTS/CTS=P0.02/P0.03。現 app の shell は無効。将来 application UART と shell を同時に有効化しない |
| TIMER24 IRQ206 | NFC の nrfx_nfct が使う候補 | NFC を採用した構成では予約し、汎用 timer と重ねない。現 app で NFC は初期化していない |
| GPIOTE20/30、GPIO P0/P1/P2 | 将来の Button/GPIO backend | nrfx の Kconfig y は初期化済みの意味ではない。channel・port event・IRQ・pin の owner を backend ごとに決める |
| SAADC IRQ213、EasyDMA buffer | 将来の電源 ADC backend | S115 の上記予約には含まれない。DVDD/AVDD/VDD と将来の外部 pin ADC を一つの owner で排他する |
| LED0=P2.09 | 現 app 起動表示 | GPIO API が未実装でも、既に app が出力として設定している |

IRQ 接続の根拠は `vendor/sdk-nrf-bm/subsys/softdevice_handler/irq_connect.c:47-74`、SD event は `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/nrf_soc.h:81-85`、BM の予約は `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:9-18,26-38` です。pin は `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:36-107` に従います。NFC timer は `vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nfc/integration_notes.rst:33-57` が根拠です。board-config の override は各 backend 追加時にも再照合します。

**温度の計画不整合**: 既存計画の TEMP 直接操作は MPSL 予約と衝突します。S115 の `sd_temp_get` は0.25°C単位、約50 µsの同期 API です。採用は利用者の判断待ちで、今回の変更では温度の driver・契約・計画を置換しません。根拠: `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/nrf_soc.h:582-591`。

## DPPI と PPI bridge

| instance | S115 mask | 予約 channel |
|---|---|---|
| DPPIC00 | `0x0000000A` | 1、3 |
| DPPIC10 | `0x00000FFF` | 0–11 |
| DPPIC20 | `0x00000001` | 0 |
| PPIB00 / PPIB10 | 各 `0x0000000F` | 各0–3 |
| PPIB11 / PPIB21 | 各 `0x00000001` | 各0 |

上の mask は S115 header を正本とし、C に数値を重複定義しません。nrfx の bridge allocator は00–10と11–21を対で扱うため、両端の予約 mask の OR を渡します。表にない資源を無条件に空きと扱わず、hardware の channel 数、group、bridge 経路と driver の既存利用を採用時に確認します。

従来選ばれていた NCS の `nrfx_reserved_resources_ncs.h` は、`CONFIG_BT_LL_SOFTDEVICE` と `CONFIG_MPSL` が有効な場合に予約を追加します。standalone `CONFIG_SOFTDEVICE_S115` だけではこの経路に入りません。RBOS は `firmware/include/rbos_reserved_resources.h` で S115 の mask を nrfx の予約へ渡し、既存 NCS header を取り込む構成にしました。既存の GRTC/DT 等の制約は残します。これは allocator の保護であり、raw register 操作へのアクセス制御ではありません。

`NRFX_RESERVED_RESOURCES_HEADER` は SDK の非公開 Kconfig symbol なので、`.conf` に代入せず application Kconfig の先行 default で選択します。CMake の include path は app だけでなく Zephyr/nrfx library にも渡します。`resources.c` は最終設定で選ばれた header を使い、DPPI/PPIB の予約漏れ、GRTC の交差、SCHED 以外、HAL の NVIC 前提違反と512 B未満の BM heap を build 時に拒否します。512 Bは既存構成の下限であり、実負荷に十分な容量と証明した値ではありません。

## callback の context と寿命

| 経路 | context・保持するもの | 禁止事項・失敗時 |
|---|---|---|
| S115 zero-latency IRQ | SoftDevice の handler へ転送 | Ruby、RBOS ring、allocation、refcount、task 操作をしない |
| SD event IRQ → BM defer | application IRQ、payloadなしの poll 通知 | `bm_scheduler_defer()` の `-ENOMEM` を容量不足として扱う。SDK は warning を出すが、配送保証にはならない |
| BM process → SDH BLE/SoC observer | foreground、SDH の一時 event buffer | observer 内でも Ruby へ再入しない。非同期に渡す field は所有する buffer へコピーする |
| 将来の Button/SAADC IRQ → RBOS ring | NVIC2–7。値だけを固定長16件の ring へコピー | IRQ で Ruby を呼ばない。overflow/drop/coalesce と完了 event の回復規約は driver 側でも扱う |
| system service / HAL idle | Ruby の C callback / foreground、BM process を実行 | payload 処理で VM を再入せず、native completion は後続 dispatcher で処理する |

BM scheduler は `sizeof(struct bm_scheduler_event) + len` を固定 heap から `K_NO_WAIT` で確保し、payload をコピーします。handler 実行が終わるまでその allocation は解放されません。512 Bを512件、あるいは `512 / header` 件の保証として扱いません。allocator の metadata・alignment・実行中の一件・他の defer producer を含めた容量試験は未完了です。`bm_scheduler_process()` は空になるまで drain するため、厳密な時間上限は P6 に残します。出典: `vendor/sdk-nrf-bm/lib/bm_scheduler/bm_scheduler.c:22-80`。

## SD RAM と build の証拠

BLE 有効化後に `nrf_sdh_ble_sd_ram_usage_get()` の値を記録します。SDK の `CONFIG_NRF_SDH_BLE_LOG_SD_RAM_USAGE=y` も有効にし、SD RAM の始点・終点・使用 byte と、app RAM 開始位置を下げられる場合の案内を出します。起動診断は次の field です。

```text
resources sched_bytes=<heap設定byte> sched_header=<event headerのsizeof> service_ms=<周期> sd_ram=<BLE有効化後のbyte>
```

SD RAM の最小値 `0x1080` は現在の BLE 設定での実使用量ではありません。SDK は `sd_ble_enable()` に最終 app RAM 開始位置を渡して必要量を得ます。失敗時は既存の BLE 初期化失敗として停止し、診断は成功後だけ出します。予約 SRAM の境界を静的 map の app 使用 RAM や mruby/c pool と混同しません。出典: `vendor/sdk-nrf-bm/subsys/softdevice_handler/nrf_sdh_ble.c:247-286`。

`collect-evidence.sh` は従来の `.config` / map に生成 `zephyr.dts` と全 image 別の `resource-configurations.json` を加えます。JSON は関連する有効設定の抜粋であり、未掲載の symbol が無効という判定には使いません。全設定は `.config` を参照します。PEM と `keyfile.json` を除外する規約は維持します。

host の `test_resources.py` は SDK の代役 header を使う compile 検査です。正常、予約 mask の追随、五つの allocator の予約漏れ、dispatch/heap/IRQ 設定の破壊、GRTC 衝突を検査します。実際の SDK header との結合は firmware の四構成 build で確認し、どちらも DK での IRQ・SD RAM・queue 容量試験の代わりにはしません。

[調査索引へ戻る](../README.md)
