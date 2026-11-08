# native API と権限

## 主参照の値の流れ

OpenBlink demo-nrf は class/method 登録、keyword 取得、SET 系戻り値の参考です。以下は全て同じ固定版です。

| Ruby API | C callback と挙動 | 出典 |
|---|---|---|
| LED.set | c_set_led。part/state keyword と bool。LED3 に system 認可なし | [led.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/led.c#L39-L93) |
| Input.pressed? / released? | c_get_sw_pressed/released。part Symbol を検査して bool | [input.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/input.c#L42-L112) |
| BLE.state | c_get_ble。接続状態を整数で返す | [ble.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/ble.c#L30-L51) |
| Blink.lock / unlock | c_lock_blink / c_unlock_blink。restart mutex の操作、bool | [blink.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/blink.c#L60-L92) |

互換用 `Blink.req_reload?` は deprecated で false 固定です。[登録と実体](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/blink.c#L39-L58)。RBOS に用意する計画はありません。

`api_api_get_bool` は TRUE/FALSE を C bool にし、その他はログと false にします。[api.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/api.c#L20-L34)。RBOS では型エラーと正常 false を区別する規約を設計します。

## 旧参照の用途と権限

MDBT 版の ADC/PWM/I2C/Temperature は補助資料です。[旧 API 一覧](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api)。新参照が同じ class を全て提供するとは扱いません。

旧版は VM ID 一致で LED3 を許可し、system task 登録時の HMAC 検証は TODO です。[旧 api.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L47-L67)、[旧 led.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/led.c#L88-L95)。新参照の LED3 にはこの判定がなく、権限モデルの完成例ではありません。

## RBOS の設計案

- 初期は署名済み firmware に含まれる system bytecode を信頼の起点にする。
- 特権 C callback 全てで caller VM の権限を検査し、class 名の秘匿に頼らない。
- 子 task、他 task の terminate/raise、VM ID 再利用、破棄時の失効を定義する。
- 外部 system bytecode の認証は [HMAC 調査](hmac-authentication.md)を基に将来設計する。
- argc/type/range、所有権、OOM、driver failure を [C API 規約](../mrubyc/c-api.md)に揃える。

全て未実装です。native memory の完全な sandbox を保証しません。

[調査索引へ戻る](../README.md)
