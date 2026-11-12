# MPIG の GPIO・ADC・PWM

以下は [固定 MPIG と調査の区別](overview.md)に従う要約・翻案です。表の未規定部分を一般的な Ruby IO の挙動で補いません。pin は標準では Integer、platform 固有の String 等も許されます。RBOS が承認した Symbol は [追加の pin 方針](../architecture/decisions.md)です。

## GPIO

一次資料: [mruby_io_GPIO_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_GPIO_ja.md)。通常は一つの物理 pin を扱い、platform が必要とする場合は複数 bit をまとめられます。

| API・定数 | 引数・返り値・意味 |
|---|---|
| `GPIO.new(pin, params)` | object を生成し mode を設定。params は定数の bitwise OR。IN / OUT / HIGH_Z の指示は必須で、なければ ArgumentError |
| `IN` / `OUT` / `HIGH_Z` | 入力 / 出力 / high impedance。具体的な数値を application に埋め込まない |
| `PULL_UP` / `PULL_DOWN` / `OPEN_DRAIN` | pull-up / pull-down / open drain。ハードウェア対応と組合せの可否は platform を確認 |
| `GPIO.setmode(pin, params)` | 指定 pin の mode 変更、nil |
| `GPIO.read_at(pin)` / `#read` | 通常 0 / 1、複数 bit 実装では任意 Integer。出力 pin でも可能なら設定値ではなく実際の電位を読む |
| `GPIO.high_at?(pin)` / `#high?` | 読み値 == 1 の bool |
| `GPIO.low_at?(pin)` / `#low?` | 読み値 == 0 の bool |
| `GPIO.write_at(pin, integer_data)` | 通常 0 / 1 を出力。本文は範囲外の RangeError を明記。戻り値の規定なし |
| `#write(integer_data)` | 通常 0 / 1、複数 bit 実装では任意 Integer。本文は戻り値・例外を別途列挙していない |
| `#setmode(params)` | nil。IN / OUT / HIGH_Z の再指定時、既存の pull 等は無効化される。pull だけの指定と区別 |

mode の省略 default はありません。`read` は bool ではなく数値なので `if gpio.read` を high 判定に使えません。Ruby で 0 は真です。MPIG は割込み callback、edge event、debounce、ALT、pull 抵抗値、drive strength、実行時間上限を規定していません。blocking / IRQ safe / 再入可とも断言していません。

RBOS は nrf_gpio による物理値・mode 操作を実装しました。Button は MPIG 外の拡張として GPIOTE、固定 ring と foreground 配送を使います。[pin・mode・例外・所有・RBS と検査の境界](../implementation/gpio-button-api.md)を参照してください。Wasm/build の成功は実機の電気特性・IRQ の受け入れを意味しません。

## ADC

一次資料: [mruby_io_ADC_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_ADC_ja.md)。標準の追加定数・sampling rate default はありません。

| API | 引数・返り値・意味 |
|---|---|
| `ADC.new(pin, *params)` | object を生成。analog/digital 切替が必要な MCU では analog mode に変更。追加 params は sampling 速度等の platform 機能用 |
| `#read_voltage` | Float、単位 V。Float が利用できない VM では NotImplementedError |
| `#read` | read_voltage の alias。同じ単位・型を維持 |
| `#read_raw` | 電圧変換前の Integer。bit 数・signedness・gain・reference 等は別途 platform を確認 |

変換開始から完了までの待機、校正、DMA、buffer 長、失敗時の追加例外、電圧精度は本文では一律に定義されません。RBOS では SAADC を backend 候補にし、gain/reference と V 換算を確認します。整数 ADC 値だけを返す実装へ `read` を黙って変更してはいけません。固定 VM の Float と、backend が対応する機能は別の確認項目です。

## PWM

一次資料: [mruby_io_PWM_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_PWM_ja.md)。標準定数はなく、ここでの method は getter ではなく設定操作です。

| API | 引数・default・意味 |
|---|---|
| `PWM.new(pin, *params)` | keyword `frequency`（alias `freq`）、`duty`。frequency 指定で duty 50% の出力を開始。別 duty で始めるなら同時指定。unit 等の拡張を許容 |
| `#frequency(freq)` | Integer / Float、Hz。開始または変更。0 は停止。duty を保持。最大・最小・分解能は platform 依存 |
| `#period_us(micro_sec)` | Integer、周期 μs。0 は停止、duty を保持 |
| `#duty(percent)` | Integer / Float、0〜100%。0〜1 の比率へ読み替えない |
| `#pulse_width_us(micro_sec)` | Integer、ON 時間 μs。周期を超える値は可能な最大 ON 値へ制限し、エラーにしない |

frequency 未指定時の周波数・出力状態、各 setter の返り値、一般的な引数エラー、切替完了までの待機は本文に明示されません。停止時は low が望ましいとされますが、即時停止か現在周期の終了後かは platform 依存です。数値の丸め、実効周波数、channel ごとの周期共有は backend で説明する必要があります。

RBOS は nrfx PWM を候補とし、sequence buffer の寿命と channel / instance の割当てを設計します。上記を実機で満たすことは未確認です。[RBS](rbs-comparison.md)の void は本文にない setter の戻り値を新たに保証する根拠にはしません。

[UART・bus](serial-buses.md) / [nRF 対応](nrf54l15-mapping.md) / [調査索引へ戻る](../README.md)
