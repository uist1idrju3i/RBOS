# MPIG の UART・I2C・SPI

[固定版とライセンス](overview.md)に従う MPIG の要約・翻案です。String は転送 byte 列として扱い、CRuby の IO・filesystem・encoding の全機能を前提にしません。未列挙の例外、0 / 負の count、timeout / cancel は本文から一律には決まりません。

## UART

一次資料: [mruby_io_UART_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_UART_ja.md)。非同期 serial の class ですが、Ruby method がすべて nonblocking という意味ではありません。

`UART.new(id=nil, *params)` は物理 unit を指定します。可能な場合の default は **9600 baud / 8 data bits / 1 stop bit / parity NONE / flow control NONE**。すべての parameter の対応を義務づけてはいません。

| keyword | 型・意味 |
|---|---|
| `baudrate` / `baud` | Integer、baud rate |
| `data_bits` / `stop_bits` | Integer、data bit / stop bit |
| `parity` | NONE / EVEN / ODD |
| `flow_control` | NONE / RTSCTS |
| `unit` | 物理 unit の識別 |
| `txd_pin` / `rxd_pin` / `rts_pin` / `cts_pin` | 各信号の pin。board 固定なら省略できるかは実装を確認 |

| API | 返り値・待機・注意 |
|---|---|
| `#setmode(*params)` | constructor と同じ parameter。本文に戻り値指定なし |
| `#read(read_bytes)` | String。指定 byte 数が届くまで block。事前に bytes_available を確認すれば待機を避ける使い方が可能 |
| `#write(string)` | 送信した byte 数の Integer。FIFO / software buffer により物理送信完了前に戻る場合あり。空き容量次第で block し得る |
| `#gets` | LF までの byte 列を String で返す。1行未着なら block。改行なしで RX buffer が満ちる場合の進行を保証しない |
| `#puts(string)` | nil。末尾に改行がなければ追加。default は LF のみ |
| `#bytes_available` | 受信済みで読み込める byte 数の Integer |
| `#bytes_to_write` | 未出力の送信 buffer byte 数の Integer。buffer なしなら常に 0 |
| `#can_read_line` | 1行を読めるかの bool |
| `#flush` | buffer の実送信完了まで block。本文に戻り値指定なし |
| `#clear_rx_buffer` / `#clear_tx_buffer` | 対応 buffer を破棄。進行中 DMA の cancel や送信済みの取り消しまで意味するとは書かれていない |
| `#send_break(time)` | time は任意、Integer / Float の秒。機器によっては固定長（例: 12 bit）で変更不可 |

定数は NONE / EVEN / ODD / RTSCTS で、数値自体を portable な値として埋め込まないようにします。一般的なエラーの class、最大行長、buffer overflow、EOF、timeout は本文で統一されていません。複数 reader による「確認してから読む」の競合は [rrt0 連携](rrt0-integration.md)で扱います。

## I2C

一次資料: [mruby_io_I2C_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_I2C_ja.md)。**master・7-bit address** が対象で、10-bit address / slave は標準の対象外です。

`I2C.new(id=nil, *params)`。unit が一つ等の場合は id を省略可能。keyword は `frequency` / `freq`（Integer、default **100 kHz**）、`scl_pin` / `sda_pin`。全 parameter が対応するとは限りません。標準定数はありません。

| API | 返り値・transaction |
|---|---|
| `#read(i2c_adrs_7, read_bytes, *param)` | String。param があれば先に送信し、**repeated start** を挟んで読む。途中の NAK で要求長より短い String の可能性あり |
| `#write(i2c_adrs_7, *outputs)` | 実際に書けた byte 数の Integer。outputs は Integer / Array<Integer> / String を複数指定できる |
| `#send_start` / `#send_restart` / `#send_stop` | 任意実装の low-level。各 bus condition を出力。本文に返り値指定なし |
| `#raw_read(read_bytes, ack_nack=false)` | 任意実装。String。最後の byte で true は ACK、false は NACK を出す |
| `#raw_write(*outputs)` | 任意実装。write と同じ入力型、書けた byte 数の Integer |

low-level 群は必要な場合だけ実装してよいとされています。bus が戻るまでの最大時間、clock stretching、timeout、arbitration、NAK の例外化、short write の原因は一律に定義されていません。read-with-output を単なる STOP 付き write + read へ分解すると、MPIG の transaction を変えてしまいます。

## SPI

一次資料: [mruby_io_SPI_ja.md](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_SPI_ja.md)。**master・8-bit 単位**を規定。**CS / SS は GPIO を使い、SPI class では規定しません。**

`SPI.new(id=nil, *params)`。keyword は `unit`、`frequency`（Integer、default **1 MHz**）、`mode`（0〜3、default **0**）、`first_bit`（MSB_FIRST / LSB_FIRST、default **MSB_FIRST**）。定数の数値や pin 設定方法は platform に依存します。

| API | 返り値・転送 |
|---|---|
| `#setmode(*params)` | constructor に準じた設定変更。本文に戻り値指定なし |
| `#read(read_bytes)` | String。clock と同時に **0** を出力して指定 byte 数を読む |
| `#write(*outputs)` | nil。Integer / Array<Integer> / String を出力 |
| `#transfer(outputs, additional_read_bytes=0)` | String。指定出力と同時に受信し、追加読み込み分は続けて 0x00 を出力 |

transfer は write の複数可変長引数と同じ signature ではありません。block / CS 自動制御 / timeout は標準 method ではなく、[community の拡張](community-comparison.md)と区別します。同期 call の待機時間、DMA 制約、一般例外、実効周波数の丸めは本文では統一されません。nrfx が送る dummy byte の default をそのまま採用せず、MPIG の zero output と照合する必要があります。

UART は明示的な block 契約があります。I2C / SPI は「非同期完了 callback が標準」とも「待機時間が有限」とも規定していません。RBOS は呼出し task の同期 semantics と scheduler 全体の進行を両立させる必要があります。具体策は [rrt0 連携案](rrt0-integration.md)、型の差は [RBS 比較](rbs-comparison.md)を参照してください。

[調査索引へ戻る](../README.md)
