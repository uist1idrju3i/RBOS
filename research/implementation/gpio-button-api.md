# GPIO と Button の契約

[調査索引](../README.md) / [資源予約表](resource-reservations.md) / [P2 checklist](checklist.md#p2-native-api-と資源)

## pin と物理値

`GPIO.new(pin, mode)`、class の `setmode` / `read_at` / `high_at?` / `low_at?` / `write_at`、instance の `setmode` / `read` / `high?` / `low?` / `write` を共有 C binding と nRF/Wasm backend で実装します。[RBS](../../sig/gpio.rbs)も同じ入口を記述します。

pin は `port*32+pin` の Integer、厳密な `P<port>.<pin>` の String、DeviceTree の node label と明示した `sw0..sw3` alias の Symbol です。`45`、`"P1.13"`、`:button0`、`:sw0` は同じ物理 pin を指します。String は大文字 P、空白なし、pin 部は0–31で2桁まで、全体は13 byteまでとし、埋め込み NUL を拒否します。未知の Symbol と不正文法は ArgumentError、nil/誤型は TypeError、負数・不在 pin は RangeError です。

利用者承認により、GPIO の全表記を物理電気レベルで統一しました。`read` は Integer の0/1、`high?` / `low?` は bool、`write(1)` は物理 high です。Symbol だけを active-low で反転しません。DK Button は押下時0です。

BM board は元の GPIO/GPIOTE DT node を削除します。Zephyr GPIO driver は復活させず、[overlay](../../firmware/boards/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.overlay)の `rbos,gpio-bank` を pin メタデータとして使います。文字列の `label` property ではなく node label を列挙します。既定の公開対象は LED0..3（73/42/71/46）と Button0..3（45/41/40/4）の8 pinだけです。その他の存在する pin は RuntimeError（reserved）とし、Integer/String もこの制約を通します。UARTE20 の TX と HWFC 有効時の CTS は、メタデータに追加されても保護します。

追加 pin は board 管理者が回路・所有者・console/clock/debug/reset/NFC 等の競合を確認して DT の許可集合へ追加します。一般 header pin を無条件に開放しません。この許可集合は P3 の task 別認可や native memory sandbox ではありません。

## mode と共有状態

`IN` / `OUT` / `HIGH_Z` の一つと `PULL_UP` / `PULL_DOWN` / `OPEN_DRAIN` を組み合わせます。生成には方向が必要です。方向だけの再設定は修飾を外し、pull だけの `setmode` は設定済みの方向・drive を引き継ぎます。上下 pull の同時指定、複数方向、HIGH_Z の修飾、入力の OPEN_DRAIN、未知 bit は ArgumentError です。OUT の設定時は0から開始し、HIGH_Z は input を切り離します。出力以外への write は RuntimeError、0/1以外は RangeError、誤型は TypeError です。setter の戻り値は nil です。

mode は Ruby object 固有でなく物理 pin ごとの共有状態です。GPIO object を破棄しても出力は自動解除しません。未設定 pin の操作は RuntimeError、backend 非対応は NotImplementedError、driver failure / busy は RuntimeError です。Button の所有中は GPIO の read を許し、再設定・write・二重 watch を busy で拒否します。close 後は mode を改めて設定してください。

## Button の待機と寿命

Button は MPIG 外の RBOS 拡張です。[RBS](../../sig/button.rbs)に以下の契約を定めます。

- `Button.new(pin)`: DK の Button0..3だけを pull-up 入力として watch する。LED は NotImplementedError。
- `poll`: 非待機で `[physical_level, edge_count]` または nil を返す。
- `wait`: 呼出し task で poll と `sleep_ms(1)` を繰り返し、最初の値を返す。他 task と maintenance は進む。
- `each_event { |level, count| ... }`: 呼出し task の block に配送する。block なしは ArgumentError。native は Proc を保持しない。
- `pressed?`: 現在の物理値0を押下として返す。close 後は RuntimeError。
- `close`: 同期 unwatch して nil を返す。成功後の再 close は nil、poll/wait は RuntimeError。失敗時は所有を残し、再試行できる。
- `Button.stats`: `[ring_pending, ring_overflow, ring_coalesced, delivery_overflow]`。値は非負 Integer、INT_MAX で表示を飽和する。

最大4 watchです。通常の Ruby Button object は caller VM が所有し、native が保持するのは VM ID の付かない subscription object だけです。Ruby の値・Proc・task pointer を native state に保存しません。最後の Ruby 参照が消えた subscription は foreground で unwatch し、成功を確認するまで pin と native lease を保持します。task 強制終了・VM ID 再利用でも同じ回収経路を使います。generation は増加だけとし、UINT32_MAX 到達後は再利用せず busy にします。

## IRQ と bounded 配送

P1 Button0..2 は GPIOTE20、P0 Button3 は GPIOTE30 を使い、watch ごとに IN channel を nrfx allocator から確保します。各 instance の IRQ0（218/268、NVIC priority7）を BM の直接割込みで接続します。PORT/SENSE の低精度 event と DPPI は使いません。unwatch は IRQ を serialize して trigger を止め、pin/handler と channel を解除します。

callback は pin・物理値・generation を16件の固定 ring へ置くだけで、Ruby・割当て・参照カウント・task を操作しません。同一 pin **かつ generation** の未配送 event は最新レベルへまとめ、観測した callback 数を count に加算します。リングの満杯時は新着を drop して overflow を数えます。foreground は1回に最大16件を取り出し、4 watch の固定 mailbox へ配送します。count が INT_MAX を超える追加 batch は drop し、delivery_overflow を数えます。古い generation は破棄します。

debounce、個々の edge の時刻・順番、電気的な全 edge の捕捉は保証しません。GPIOTE が IRQ 前にまとめた edge は count から復元できません。API の error/返り値検査は hardware access より先に行います。

## 検査と実機の境界

Wasm fixture は pin 互換、active-low の物理値、mode、driver failure、busy、coalesce、newest drop、each_event、close 失敗と orphan 再試行、task 終了と VM ID 再利用を検査します。host は parser/mode/ring と nRF GPIO adapter を検査し、固定 SDK に対する firmware build は実際の nrfx/IRQ/DT の結合を検査します。

既定の `CONFIG_RBOS_PERIPHERAL_EXERCISE` は自己検査後に [Ruby 診断 task](../../firmware/ruby/peripherals.rb)を起動し、LED0を点灯、4 Button を所有して `button index=… level=… count=…` を出します。100巡回ごとに温度と三電源を反復測定します。raw と voltage は別の変換で、同じ一 sample の対ではありません。OOM profile では無効です。製品 Ruby に組み込むときはこの診断 task を置き換えます。

実機の電位、IRQ timing/競合、BLE/tick、stack/pool、ADC/温度の精度は未確認です。build/fake 成功を P2 の実機受け入れ完了とは扱いません。

## 出典

GPIO の API と mode の要約は [Microcontroller Peripheral Interface Guide の固定 GPIO 版](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/mruby_io_GPIO_ja.md)（Copyright 2023 mruby forum committee / Kyushu Institute of Technology / Shimane IT Open-Innovation Center、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)）をもとに、RBOS の pin/例外/所有/待機を追加したものです。実装例コードの転載ではありません。[元の調査](../io-api/gpio-adc-pwm.md#gpio)と [予約表](resource-reservations.md)を参照してください。
