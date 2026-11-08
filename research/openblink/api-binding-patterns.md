# OpenBlink の API と system-task 権限

## 共通の登録方法

`api_<name>_define()` が `mrbc_define_class(0, name, mrbc_class_object)` と `mrbc_define_method(0, cls, ruby_name, callback)` を呼びます。Ruby は登録名を呼び、C が値を検査して driver へ渡し、SET 系で結果を戻します。出典: [Blink の登録](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L68-L77)。以下の表のリンクは全て同じ固定版です。

## API 別の値の流れ

| Ruby API | C callback | 引数・戻り値・エラー |
|---|---|---|
| `ADC.update!` / `ADC.read` | `c_update_adc` / `c_get_adc` | update は bool。read は numeric として入力を検査し GET_INT_ARG、mV を 1000 で割って Float。型不正時は 0.0。[adc.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/adc.c#L33-L68) |
| `BLE.state` | `c_get_ble` | 状態を整数 Off/Advertising/Connected で返す。[ble.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/ble.c#L30-L62) |
| `Blink.req_reload?` | `c_get_reload` | VM ID ごとの heartbeat を更新し bool。[blink.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L164-L172) |
| `Blink.sample_string` | `c_sample_string` | String の data/size を読む例。成功値を明示的に返していない。[blink.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L87-L102) |
| `Blink.sample_array` / `sample_array2` | `c_sample_array` / `c_sample_array2` | 3 要素だけ読む例。直接 data を読む方法と GET_ARY_ARG + array_get。要素型の完全検査ではない。[blink.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L111-L138) |
| `Blink.sample_array3` | `c_sample_array3` | array_new、float_value、array_set で配列を作り SET_RETURN。[blink.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L147-L156) |
| `I2C.read` | `c_i2c_read` | device/address/size を読み `[driver_rc,data...]`。失敗データは 0。[i2c.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/i2c.c#L71-L114) |
| `I2C.write` | `c_i2c_write` | device/address/Array を読み driver の整数 status。[i2c.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/i2c.c#L125-L152) |
| `Input.pressed?` / `released?` | `c_get_sw_pressed` / `c_get_sw_released` | 必須 keyword part を Symbol として検査、bool。[input.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/input.c#L62-L117) |
| `Input.sw1_read` | `c_sw1_read` | expert 許可時のみ登録。実体は 1 を返す dummy。[input.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/input.c#L45-L52)、[実体](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/input.c#L120-L123) |
| `LED.set` | `c_set_led` | 必須 part、任意 state の keyword。bool。LED3 は system VM のみ。[led.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/led.c#L52-L95) |
| `PWM.set` | `c_set_pwm` | numeric 二つを整数 field で読み driver 呼出、bool。[pwm.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/pwm.c#L32-L54) |
| `Temperature.value` | `c_get_temp` | driver の値を Float。[temperature.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/temperature.c#L32-L48) |

`api_symbol_define` は led/sw 等の symbol を登録し、その ID を native API で比較する補助です。`api_api_get_bool` は TRUE/FALSE を C bool にし、それ以外をログと false で扱います。出典: [symbol.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/symbol.c)、[api.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L22-L37)。これらは Ruby class 自体の登録ではありません。

## system-task の実体と制限

`api_api_set_systemtask` は VM ID を保存しますが、HMAC 検証は **ToDo** です。`api_api_check_systemtask` は ID の一致を判定するだけです。出典: [api.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L47-L67)。

`LED.set` は callback 内で `api_api_check_systemtask(vm->vm_id)` を呼び LED3 を保護します。一方、class の生成そのものには caller ごとの非公開設定はありません。expert API の登録条件も system-task 判定とは別で、CONFIG_DEBUG の場合に許可する実装です。出典: [LED の権限確認](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/led.c#L88-L95)、[expert 判定](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L74-L81)。

## RBOS で採る設計案

1. 最初の system Ruby は署名済み firmware 内の組み込み bytecode とする。
2. system class も公開名だけで守らず、全ての特権 C callback が VM ごとの権限を検査する。
3. storage の利用者 `.mrb` には、slot 名や priority だけで system 権限を与えない。
4. 子 task、Task 操作、例外送信、VM ID 再利用、再ロード後の権限失効を定義する。
5. デバッグ限定 API と system-task 限定 API を別に管理し、本番で debug 設定を拒否する。

これらは RBOS の提案で、OpenBlink が実現済みという主張ではありません。ネイティブメモリ保護のある sandbox とも主張しません。C の誤実装や不正 bytecode まで防げるかは別の検証対象です。

型検査は参照例より厳密にします。numeric であれば integer field を安全に読めるとは限らず、短い argc で v[n] を読む、配列長を uint8_t へ縮めてから検査する、失敗を正常値 0 と混同するパターンを避けます。[C API](../mrubyc/c-api.md)の所有権・エラー規約と合わせて仕様化します。

[調査索引へ戻る](../README.md)
