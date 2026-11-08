# 新しい OpenBlink 参照実装

## 対象と初期範囲

主参照は OpenBlink/openblink-demo-nrf の `6d22b676d2cf4bc599a7709ecebaa1b890af9e3a` です。NCS/toolchain v3.3.0 と nRF54L15-DK を対象にしますが、Zephyr 上のアプリであり BM ではありません。出典: [README](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/README.md#L124-L169)。RBOS の OpenBlink 対応は将来計画で、初期は BLE bytecode 転送・保存・reload を含めません。

CMake は mruby/c ソースと独自 Zephyr HAL を app に追加します。VM の stack 定数は50 KiB、pool は15 KiB、loop 内には二つの bytecode buffer があります。出典: [CMakeLists](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/CMakeLists.txt)、[VM](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L35-L179)。RBOS は RAM buffer 方式ではなく [const bytecode](../dfu/embedded-bytecode.md)を採ります。

## Ruby の polling を不要にする停止経路

1. BLE reload command `L` が `BLE_EVENT_RELOAD` を生成する。[受信処理](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/drv/ble_blink.c#L250-L264)。
2. comm が `app_mrubyc_vm_restart()` を呼ぶ。保存と reload は別 event。[dispatch](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/comm.c#L58-L83)。
3. restart は mutex、scheduler lock、irq_lock の下で TCB 配列の各 task を terminate/delete する。[restart](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L89-L117)。
4. VM loop は `mrbc_run` 復帰後に timer 停止と cleanup を行い、次の周回で再初期化する。[loop](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L129-L190)。

`Blink.req_reload?` は互換 API として残りますが、deprecated ログを出して **常に false** を返します。停止要求の polling ではなく、RBOS には不要です。出典: [Blink API](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/blink.c#L39-L58)。

これは Zephyr の別 thread から停止する仕組みです。BM へ lock 操作を直訳せず、native callback、mutex 所有、追加 task、TCB の寿命を再検証します。任意位置で安全に停止できる保証とは扱いません。

## 保存・API の差

新参照の blink_load/store は storage read/write を呼び、旧 MDBT 版の LZ4 経路を踏襲しません。[blink.c](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/blink.c#L55-L95)。既定配列も RAM buffer へ memcpy します。[load_bytecode](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L203-L237)。

新参照の API は LED/Input/BLE/Blink が中心で、LED3 の system VM ID 検査はありません。[登録](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/mrubyc_vm.c#L144-L154)、[LED3](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/api/led.c#L85-L93)。旧版の HMAC TODO が解決したとは解釈しません。[API と権限](api-binding-patterns.md)、[HMAC](hmac-authentication.md)、[将来計画](future-support.md)へ分けます。

[調査索引へ戻る](../README.md)
