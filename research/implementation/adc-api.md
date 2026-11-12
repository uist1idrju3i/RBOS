# 三電源 ADC の契約

## 公開 API

内部電源の選択は RBOS 拡張で、利用者承認済みの factory を使います。

```ruby
vdd = ADC.internal(:vdd)
avdd = ADC.internal(:avdd)
dvdd = ADC.internal(:dvdd)
vdd.read_voltage
vdd.read
vdd.read_raw
```

DVDD と AVDD は内部 0.9 V rail、VDD は主電源です。物理 pin・DeviceTree label とは別の名前空間です。外部 pin 用の `ADC.new(pin, *params)` は予約のみで、現時点では `NotImplementedError`、pin 引数の欠落は `ArgumentError` になります。内部用 object の生成は SAADC を占有せず、未使用 object に `close` は不要です。

| API / 入力 | 契約 |
|---|---|
| `ADC.internal(source)` | 小文字の `:dvdd`、`:avdd`、`:vdd` のみ。未知 Symbol は ArgumentError、他の型は TypeError |
| `read_raw` | 引数なし。signed 16-bit sample を Integer で返す。nRF の測定設定は single-ended 12-bit、理想的な正方向の範囲は 0–4095。負値と範囲端も切り詰めない |
| `read_voltage` / alias `read` | 引数なし。Float の V。負の raw も符号を保つ |
| 位置引数の過不足・未知 keyword | backend 到達前に ArgumentError。空の `**{}` は keyword なしと同じ |
| Float 無効 | 電圧読出しを取得前に NotImplementedError。raw 読出しには Float を要求しない |
| busy | 同一・別 object、同一・別 rail とも、先行 request が残っていれば RuntimeError（`Device busy`）。待ち queue と自動再試行はない |
| 取得失敗 | driver・校正開始・換算 metadata の不正は RuntimeError。未知 backend status も成功値として扱わない |
| timeout | 100 ms の watchdog。foreground が次に動いたときに判定する。100 ms 以内の復帰や測定精度の保証ではない |

RBS は [ADC](../../sig/adc.rbs)、共有 binding は [adc_binding.c](../../src/rbos/adc_binding.c)、待機 wrapper は [adc.rb](../../src/rbos/adc.rb)です。Ruby の `read` 系は VM の引数検査、native helper は位置引数と keyword の双方を検査します。

## 協調待機と request の所有権

開始・未完了の確認・foreground service・取消しを分離しています。Ruby wrapper は未完了時に `sleep_ms(1)` し、C stack を保持した task suspend や `mrbc_run` の再帰呼出しはしません。実機の service は BM maintenance と idle から、Wasm は runner の idle adapter から呼びます。task の停止中も native service は期限と driver の状態を処理します。

結果を受け取る権利は native が生成した opaque request object の同一性で照合します。request は VM に属さない領域へ割り当て、処理中は native が一つの参照を保持します。backend は Ruby object・VM・TCB pointer を保持せず、単調増加する token と native buffer だけを使います。token は wrap せず、上限到達時は以後の開始を拒否します。

VM ID や TCB の再利用で他 task へ結果を push / resume することはありません。完了は request を持つ caller の poll で取得します。内部 helper の request を意図的に他 task へ渡した場合は、その同じ object を持つ task が取得・取消しできます。複製した別 object、整数や無関係な object では現在の request を操作できません。private や推測可能な token 値を認可の境界には使いません。内部 helper は公開 RBS の対象外で、安定した利用者 API ではありません。

全 user task に同じ三電源の読出しを許します。system-task 専用の権限を追加したものでも、P3 の認証・管理 API を完成させたものでもありません。

通常の例外では Ruby の `ensure` が取消しを要求します。強制終了で `ensure` が走らない場合、未取得の結果も含めて期限で回収します。すでに driver が停止済みなら即時に回収でき、未完了なら非同期 STOP を要求します。STOP の確認が来るまでは SAADC と buffer を保持して後続開始を拒否します。停止確認が永久に欠落した場合は隔離を継続し、timeout を理由に buffer を再利用しません。

## nRF54L15 backend と換算

[nRF adapter](../../src/platform/nrf/adc.c)は一つの SAADC、channel 0、NVIC IRQ 213 / priority 7 を専有します。BM の優先度 offset を引いた Zephyr priority で接続し、nrfx の設定と揃えます。S115 の予約と console UARTE に重ならない資源です。外部 pin ADC を追加するときも、この同じ owner を通す必要があります。

固定 nrfx の public input 型は `nrfx_analog_input_t` です。`NRFX_ANALOG_INTERNAL_DVDD` / `AVDD` / `VDD` を渡し、SDK の `nrfx_saadc_ain_get` が `NRF_SAADC_INPUT_*` へ変換します。HAL の encoded selector を nrfx の引数へ直接渡しません。BM は `&adc` を削除するため、DT ADC driver は使わず BM の `CONFIG_NRFX_SAADC` を有効にします。

設定は内部基準 0.9 V、gain 1/4、single-ended 12-bit、oversampling 無効です。nrfx default の取得時間を使い、測定ごとに非同期 offset calibration を実行します。SDK が FICR trim を扱い、RBOS 独自の補正式は追加しません。DMA は 4-byte aligned な static RAM の signed 16-bit 一要素 buffer を使います。

backend は `raw`、`full_scale_uv = 3600000`、`bits = 12` を成功時だけ返します。共有 binding の換算は `raw × full_scale_uv / (2**bits × 1_000_000)` V です。基準電圧と gain の補正を表すもので、VDD に他 SoC の VDDH/5 等の分圧倍率を加えません。三 selector の換算設定は同じで、DVDD/AVDD の測定対象が内部 rail である点は区別します。

## IRQ・DMA と取消しの境界

callback は固定長の event bit と signed sample のみを記録し、allocation・参照計数・Ruby・例外・task 操作をしません。同時 request は一つ、校正完了から測定開始へ進めるのは foreground のみなので、一般の Button event ring と独立した専用 mailbox に保持できます。phase に反する完了や sample の二重格納を失敗にし、sample buffer と要素数も検査します。mailbox の読取りと phase 切替えは IRQ lock で保護します。

`nrfx_saadc_abort()` の復帰は DMA 停止を意味しません。固定 SDK は校正完了前の STOP で callback を呼ばないため、IRQ wrapper が nrfx の event clear より先に STOPPED を捕捉します。DONE / 校正完了で SDK が peripheral を無効にした場合、または STOPPED を確認した場合にだけ解放します。再初期化時には SDK が古い peripheral event を clear します。IRQ 内に次 request を開始する処理はありません。

## 検査と未確認条件

host では [request lifecycle](../../tools/mrubyc-wasm/test_adc.c)、[nRF adapter fixture](../../tests/check-changes/test_adc_nrf.py)、[Float 無効 guard](../../tests/check-changes/test_adc_binding.py)を実行します。selector、開始・校正・測定の失敗、signed 境界、不正 metadata、busy、clock wrap、timeout、停止待ち、旧 token、VM-independent な出力寿命を検査します。

Wasm は [API](../../tests/mruby/adc.rb)、[協調待機](../../tests/mruby/adc_concurrent.rb)、[worker](../../tests/mruby/adc_worker.rb)、[task 終了と VM ID 再利用](../../tests/mruby/adc_lifetime.rb)を runner で実行します。VM ID 再利用 fixture は、[専用 worker](../../tests/mruby/adc_lifetime_worker.rb)を native fixture から実際に生成・終了・削除し、同じ ID の新 task が旧結果を取得しないことを確かめます。これは本体の task 管理 API を拡張するものではありません。

DK では、VDD と電源の実測値、DVDD/AVDD の妥当性、selector 切替え、反復測定、校正効果、IRQ / STOPPED、DMA RAM、BLE 接続中の tick・latency・stack/pool・資源競合を確認します。許容誤差は試験前に電源条件・測定器・仕様から定めます。これらは未確認で、host・Wasm・CI を実機の電気特性や実時間の証拠とは扱いません。P2 全体の完了でもありません。

通常・stress の起動自己検査後には、三 rail の `adc rail=... raw=... volts=...` または `error=...` を診断として出します。raw と volts はそれぞれ独立した測定で、同じ sample の二表現ではありません。値を出しただけでは ADC の精度試験や P2 受け入れ PASS にはしません。OOM profile は ADC 診断を実行しません。

## 根拠と帰属

- [固定 nrfx の入力型](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/helpers/nrfx_analog_common.h)、[API](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/drivers/include/nrfx_saadc.h)、[driver](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/drivers/src/nrfx_saadc.c)。
- [公式 SAADC 仕様](https://docs.nordicsemi.com/bundle/ps_nrf54L15/page/saadc.html)、[待機規約](../io-api/rrt0-integration.md)、[S115 資源予約](resource-reservations.md)。
- MPIG の `read_voltage` / `read` / `read_raw` は [固定版](https://github.com/mruby/microcontroller-peripheral-interface-guide/tree/514497cfe184edda842f4410cd0eaee1acbdfb9c)を参照・翻案しています。CC BY 4.0、mruby forum committee / Kyushu Institute of Technology / Shimane IT Open-Innovation Center、Copyright 2023。内部入力・busy・期限・request の所有権は RBOS の追加契約です。

[調査資料の入口へ戻る](../README.md)
