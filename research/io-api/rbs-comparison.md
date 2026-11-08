# mruby_io_types と MPIG 本文の照合

参照は poporonnet/mruby_io_types の [sig/](https://github.com/poporonnet/mruby_io_types/tree/401ec111049bd9b3508893f29a3a1b35ca97a465/sig)、commit `401ec111049bd9b3508893f29a3a1b35ca97a465`（MIT）。型の補助資料として読み、MPIG 本文を上書きする仕様とはしません。RBS checker を導入・実行したわけではなく、固定ファイルの source 比較です。

## 六 class の型情報

| 型・class | 固定 RBS の記述 | 本文との関係・留保 |
|---|---|---|
| pin / id | Integer または String | RBOS の DeviceTree-label Symbol は含まれない。将来の RBOS 型定義では拡張部分を区別 |
| GPIO | `_Mode` interface に OR、六定数。initialize(pin, mode)、instance read/high?/low?/write/setmode、class setmode/read_at/high_at?/low_at?/write_at | bool と Integer を区別。write / setmode は void。void は利用者に戻り値を利用させない型で、runtime の nil を検証するものではない |
| ADC | initialize(pin, *untyped)、read_voltage: Float、read の alias、read_raw: Integer | Float 無効時の NotImplementedError、gain、reference、bit 幅は型に表れない |
| PWM | initialize(pin, frequency:/freq:/duty:)。frequency / duty は Integer または Float、period_us / pulse_width_us は Integer、setter は void | default 50%、0 で停止、過大 pulse 幅の制限、実効値は型から分からない |
| UART | 任意の nil 許容 id、baudrate:/baud:/data_bits:/stop_bits:/parity:/flow_control:/unit:/各 pin。read/gets: String、write: Integer、puts: nil、残量: Integer、can_read_line: bool、flush/clear: void、任意 send_break 時間 | NONE/EVEN/ODD/RTSCTS は Integer の parameter 型。定数の意味、待機、行長、送信完了は本文が必要 |
| I2C | 任意の nil 許容 id、frequency:/freq:/scl_pin:/sda_pin:。read: String、write/raw_write: Integer、出力は Integer / Array<Integer> / String の可変引数。low-level 群も宣言 | low-level 宣言があることは、全実装で対応必須という意味ではない。7-bit 範囲、ACK、repeated start、short read は本文で確認 |
| SPI | 任意の nil 許容 id、unit:/frequency:/mode:/first_bit:。mode は 0/1/2/3、first_bit は Integer。read/transfer: String、write: nil | opaque constant を十分に表せないという FIXME あり。受理できる整数すべてが有効な first_bit ではない |

## 差異と使用時の注意

- **SPI#setmode は RBS では `mode:` のみ**です。MPIG 本文は constructor に準じるため frequency / first_bit / unit も候補になります。RBS だけから受理可能 keyword を削減しません。
- MPIG の `new(id=nil, *params)` という表記を、RBS は `initialize` と keyword に具体化しています。native 登録で `new` を実装する方式と Ruby の initialize 経由は実装方法の差であり、引数・結果が同じかを別途確認します。
- pin の `_Mode`、parameter、first_bit の型は、実装が数値を共有する保証ではありません。定数の数値を cross-platform protocol に保存しません。
- RBS は exception・blocking・buffer lifetime・副作用・context・timeout・対応ハードウェアの一覧ではありません。`read -> String` だけから「常に要求長」「空なら nil」「timeout 時は空文字」を推測しないことが重要です。
- RBS の README には gem template の未完成文も残っています。runtime 実装や完成済み package として紹介せず、sig の比較資料として参照します。

出典は同 commit の `sig/adc.rbs`、`gpio.rbs`、`pwm.rbs`、`uart.rbs`、`i2c.rbs`、`spi.rbs` と共通型定義です。本文側の意味は [GPIO・ADC・PWM](gpio-adc-pwm.md) / [UART・I2C・SPI](serial-buses.md)を参照してください。RBOS 用の RBS や type checker は今回追加していません。

[調査の入口](overview.md) / [調査索引へ戻る](../README.md)
