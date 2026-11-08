# nRF54L15-DK の backend と pin の対応

MPIG class と native 機構の対応候補です。**Ruby の実装・実機試験・最終 pinmux の確認は未実施**です。SDK 固定版は [研究索引](../README.md)、board 全体は [既存の board 調査](../nrf-bm/board-integration.md)を参照してください。

## SDK から利用する経路

| MPIG | backend の候補（関数名は設計例） | native 側で確認すること |
|---|---|---|
| GPIO | gpio_open/config/read/write → nrf_gpio。event 拡張が必要なら bm_gpiote / nrfx_gpiote | port/pin の存在、pull/drive/analog 切替、S115 の資源、割込み event の bounded queue |
| ADC | adc_open/read_raw/read_voltage → nrfx_saadc | analog input と物理 pin の対応、gain/reference/校正、conversion 完了、V 換算、buffer 寿命 |
| PWM | pwm_open/set_frequency/set_duty/set_pulse_width → nrfx_pwm | PWM20/21/22 の割当て、channel の周期共有、0 停止・pulse 上限、DMA sequence 寿命 |
| UART | uart_open/read/write/flush → nrfx_uarte、必要時 bm_lpuarte | console/shell との instance・pin 共有。通常 UART と LPUARTE の REQ/RDY 追加信号を混ぜない |
| I2C | i2c_open/transaction → nrfx_twim | repeated-start TX-RX、NAK / short read、DMA、clock stretch、bus 復旧、serial box の排他 |
| SPI | spi_open/transfer → nrfx_spim、CS は GPIO | zero dummy byte、mode/first_bit/周波数、TX/RX length、CS を含む transaction の排他 |

上表の backend 関数はまだありません。現在は [shared registration](../../src/rbos/bindings.c)と [backend 型](../../include/rbos/backend.h)の最小入口のみです。NRFX_PWM / SAADC / SPIM / TWIM / UARTE は `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:169-170,207-209,229-230,258-259,272-273` に宣言されています。Kconfig があることは全 pin・全 mode の適合保証ではありません。

BM の独自 driver が六 class 分そろっているわけではありません。[driver 調査](../nrf-bm/drivers.md)と `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/bm_nrfx.rst:1-25` は、nrfx を直接使用する場合の IRQ 接続を説明します。S115 が許す IRQ priority・予約資源は [割込み調査](../nrf-bm/softdevice-and-interrupts.md)に従い、ISR から Ruby を呼びません。

## console・shell と serial box

`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:55-99` は既定で console を **UARTE20**、application と shell を **UARTE30** にします。UART の二重 init だけでなく、同じ box を別 protocol で使う競合にも注意が必要です。既定 macro は利用者が上書きでき、最終構成は未確認です。

NCS v3.3.0 の manifest に対応する参照 checkout は nRF `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956`、Zephyr `fd9204a02d52630660ce8d729945a4dd743feabf`、hal_nordic `1acb428a205bad58f3dfd4e38f2d1663bb784ba1` です。BM 側の入口は `vendor/sdk-nrf-bm/west.yml:15-31`。以下は [固定 DTS](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/dts/vendor/nordic/nrf54l_05_10_15.dtsi) の register / IRQ の照合です。

| DTS の node 群 | reg offset / IRQ が一致する範囲 | 設計への影響 |
|---|---|---|
| i2c20 / spi20 / uart20 | 0xc6000 / 198（309〜348行） | console の UARTE20 を使いながら同じ box の TWIM20 / SPIM20 を独立利用する案は不可 |
| i2c21 / spi21 / uart21 | 0xc7000 / 199（350〜389行） | protocol が違っても同じ資源として割当てる |
| i2c22 / spi22 / uart22 | 0xc8000 / 200（391〜430行） | 同上 |
| i2c30 / spi30 / uart30 | 0x104000 / 260（616〜655行） | application/shell の UARTE30 と TWIM30 / SPIM30 は別資源扱いにできない |

この一致を根拠に排他資源として設計します。runtime での安全な protocol 切替・pin routing・最大周波数の全条件は検証していません。DT node の存在だけで nrfx instance が使用中・未使用と判定することもできません。

BM は `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l051015_peripherals.dtsi:14-70` で GPIO / ADC / PWM / I2C / SPI / UART 等の node を削除します。Zephyr の普通の DT driver 初期化がそのまま動く、と説明してはいけません。board-config と nrfx に加え、Ruby 用にどの DT 情報を残し・生成するかが実装課題です。

## pin の承認済み方針と未実装部分

[設計判断](../architecture/decisions.md)で、Integer の `port*32+pin`（P1.13 は 45）、String `"P1.13"`、DeviceTree-label Symbol `:led0` / `:sw0` を受け付ける方針を採用しました。同一の物理 pin に解決できるようにするための方針で、全 board が同じ Integer 番号を持つという主張ではありません。

- Integer は Nordic の物理識別、String は可読な port 名、Symbol は board の意味を表す役割です。portable application は board label を利用する設計にできます。
- DT の node label、alias、`label` property を同一視しません。`:led0` の lookup 元・生成物・存在しない名前のエラーは未実装です。GPIO label の active-low 情報を「raw 電位」と「論理 LED 点灯」のどちらへ適用するかも契約が必要です。
- 存在しない port、範囲外 pin、SAADC 非対応 pin、予約 pin、競合資源を検査します。具体的な exception class と発生時点はまだ決まっていません。
- unit の id と pin の三形式は別の契約です。`:uart30` 等の unit Symbol まで承認済みと拡張解釈しません。

PicoRuby の nrf52 port を nRF54L15 の完成 backend として再利用できるとは確認していません。[community の差異](community-comparison.md)と [rrt0 待機案](rrt0-integration.md)を踏まえ、実機で DMA・IRQ・latency・RAM・競合を試験する必要があります。

[調査索引へ戻る](../README.md)
