# Community implementation の比較

版・repository・ライセンスの入口は [固定参照一覧](overview.md)です。ここでの「あり」は source 上の比較であり、実機の完全な MPIG 適合宣言ではありません。以下の拡張を MPIG の標準 method として扱いません。

## 実装の分担と差異

| 実装 | 確認した経路・API | pin・例外・待機と留保 |
|---|---|---|
| mrubyc-nucleo-L476RG | [Core/mrubyc](https://github.com/HirohitoHigashi/mrubyc-nucleo-L476RG/tree/bfc6c6cb0c818aff66eb60da834f030f31a1cfa2/Core/mrubyc) の stm32f4_gpio/adc/pwm/uart/i2c/spi.c。mrbc_define_class/method で登録。ADC は read_voltage/read/read_raw、PWM は四 setter、UART は MPIG 群、SPI は read/write/transfer | GPIO は pin handle を instance data に保持し、new の引数数・mode を確認。ArgumentError / RangeError。I2C は固定 hi2c1、read/write 登録で、low-level 群・unit constructor の互換を確認できない。HAL の同期呼出し・timeout はそのまま rrt0 の yield ではない |
| mrubyc-esp32 | [main/](https://github.com/gfd-dennou-club/mrubyc-esp32/tree/8a0971b04d9a4e104e1fe71375d5582491490a01/main) の mrbc_esp32_gpio/adc/uart/i2c/spi.c と ledc.c。mrbc_define_class/method、instance data と ESP-IDF を接続。GPIO の他に Pin、I2C に readfrom / scan、LEDC で PWM と四 setter を登録 | README は mruby/c 4.0 と guideline への準拠を目標にする。目標と完全適合は別。UART は Integer unit、read に nonblock:。六 class が登録されることと全 semantics の一致を区別 |
| PicoRuby | [mrbgems/](https://github.com/picoruby/picoruby/tree/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems) の picoruby-{gpio,adc,pwm,uart,i2c,spi}。Ruby layer / src/mrubyc / src/mruby / ports の分離 | VM 差と board 差を分ける設計が参考になる。GPIO ALT、I2C timeout:/scan、SPI CS と block select/deselect は拡張。独自 runtime の補助機能を RBOS にあると見なさない |
| rp2040-peripheral-demo | [CMakeLists.txt](https://github.com/picoruby/rp2040-peripheral-demo/blob/9641ddae51d04d5129c78a6df7e6df8b7da6d0b7/CMakeLists.txt) と [mruby_config.rb](https://github.com/picoruby/rp2040-peripheral-demo/blob/9641ddae51d04d5129c78a6df7e6df8b7da6d0b7/mruby_config.rb)。PicoRuby ports と peripherals gembox を組合せ、LED / ADC / UART / RTC の利用例 | 独立した六 class の新実装ではない。lib/picoruby の gitlink は `5863a4908a6aad21c4b1f5a2edd6e9c457ab8a19`。上段の別版 PicoRuby の仕様を、この demo の動作として転記しない |
| pic32mx170_mrubyc | [gpio.c](https://github.com/YoshihiroOgura/pic32mx170_mrubyc/blob/d91b359d0a3daf84c6490bce817e8ae638b9dfa4/gpio.c) 等の C binding。mrbc_define_class/method と PIN_HANDLE、直接 register 操作 | GPIO は Integer の board connector 対応と String（例 B3）を受理。Nordic の Integer 番号とは意味が異なる。HIGH_Z が失敗する経路あり。C method の存在だけで全 mode 対応と判断しない |
| mruby-esp32 | [esp32_build_config.rb](https://github.com/mruby-esp32/mruby-esp32/blob/6fac2a45cf72a75e8ebc9e3e70026a3c41405ce2/components/mruby_component/esp32_build_config.rb) が外部 gpio/adc/ledc/spi gems 等を選択。[gpio.rb](https://github.com/mruby-esp32/mruby-esp32/blob/6fac2a45cf72a75e8ebc9e3e70026a3c41405ce2/main/examples/gpio.rb) は ESP32::GPIO.pinMode/digitalWrite | 例は top-level GPIO.new とは異なる。LEDC を MPIG PWM と同一視しない。外部 gem の checkout・commit はこの調査では解決しておらず、全 C binding / 六 class / blocking 適合性は未確認 |

## 移植に効く具体例

### PicoRuby: Ruby wrapper と低層の分離

- [gpio.rb](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-gpio/mrblib/gpio.rb) は mode の組合せを検証し、独自 Error の負コードを IOError に変換します。error code と Ruby exception の境界を明示する例です。固定 mruby/c にも IOError は定義されています（`vendor/mrubyc/src/error.c:319-331`）が、IO class や PicoRuby の Error code 群まで存在するわけではありません。RBOS 側の mapping は未設計です。
- [mrubyc/gpio.c](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-gpio/src/mrubyc/gpio.c) の pin_num は Integer / String / Symbol を分岐します。しかし **Symbol 受理と board 名の解決成功は別**です。[nrf52 port](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-gpio/ports/nrf52/gpio.c) は String 変換が -1、open drain / function 設定が no-op です。nRF52 の source があっても、nRF54L15 対応や三形式の pin 解決が実装済みとは言えません。
- [i2c.rb](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-i2c/mrblib/i2c.rb) は keyword-only unit と timeout、scan を持ちます。scan は実際の bus transaction を行う診断機能で、全 device に無害な定数時間操作ではありません。[RP2040 port](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-i2c/ports/rp2040/i2c.c) は SDK の timeout 付き同期 read/write を呼びます。timeout があるだけで scheduler が進む保証にはなりません。
- [spi.rb](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/mrbgems/picoruby-spi/mrblib/spi.rb) の select / deselect block は ensure を使って CS を復旧する例です。MPIG 本体は CS を規定しないため、採用時は別の拡張契約にします。さらに default frequency は **100 kHz** で、MPIG の **1 MHz** と異なります。

### ESP32 / Nucleo: blocking と error の差

[mrbc_esp32_uart.c](https://github.com/gfd-dennou-club/mrubyc-esp32/blob/8a0971b04d9a4e104e1fe71375d5582491490a01/main/mrbc_esp32_uart.c) の read は既定 100 ms、nonblock: 1 で timeout 0。負 count / malloc 失敗 / driver error は nil、0 count は空 String、到着数が足りなければ短い String を返す経路です。これは「指定数まで待つ」MPIG read と違います。別の1 byte 読み込み loop は 20 ms の timeout を使い、全 method に同じ待機仕様があるわけではありません。ESP-IDF task の block を rrt0 の Ruby task 待機へそのまま移せません。

Nucleo の [stm32f4_i2c.c](https://github.com/HirohitoHigashi/mrubyc-nucleo-L476RG/blob/bfc6c6cb0c818aff66eb60da834f030f31a1cfa2/Core/mrubyc/stm32f4_i2c.c) は引数エラーを ArgumentError、HAL 失敗を mrbc_raisef で変換します。STM32 HAL の固定 timeout は全 VM を止めないための仕組みではありません。binding パターンを参考にしても、argc / 型 / OOM / owner / lifetime の検査を RBOS 側で再設計します。

## RBOS で維持する境界

共通 Ruby 登録は [既存の ruby-api-binding skill](../../.agents/skills/ruby-api-binding/SKILL.md)に従い、実 nRF backend と Wasm fake backend を分けます。上記の source・設計パターンを調査しただけで、コードを転載してはいません。Ruby の private を権限境界とせず、native/system task で資源・権限を検査します。community の platform 固有 extension は portable な application の前提から外します。

完全な各 board の互換行列、全異常系、外部 gem の推移依存、実測 timing は未確認です。[個別ライセンス](../licenses.md) / [rrt0 の設計案](rrt0-integration.md) / [調査索引へ戻る](../README.md)
