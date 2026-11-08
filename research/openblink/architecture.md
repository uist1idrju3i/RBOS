# OpenBlink の構成と再ロード

## 参照範囲

参照版は OpenBlink `d6efc07877ebac6bd55519b8458be4629bef80c3` です。対象は nRF52840 の Raytac MDBT50Q-DB-40、NCS/toolchain は v2.9.0 です。RBOS の nRF54L15 + BM と同じ環境ではありません。出典: [README](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/README.md#L32-L41)。

mrubyc は gitlink `2cbbbf757bbc9366fd319dd76753dc2c8b8386b9` として記録されています。参照 checkout の submodule 本体は未取得で、内部のバージョンは未確認です。埋め込み Ruby データには RITE0300 があるため、RBOS の mruby/c 4.0.0 と互換と仮定しません。出典: [mrubyc gitlink](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3/mrubyc)、[slot2.rb](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/rb/slot2.rb)。

## ファイルの役割

| 場所 | 主な役割 |
|---|---|
| `src/main.c`、`src/app/init.c` | アプリ全体の開始と初期化 |
| `src/app/mrubyc_vm.c` | pool、task、timer、再ロード |
| `src/app/blink.c`、`storage.c` | slot と LZ4、NVS 保存 |
| `src/app/comm.c` | 通信・アプリ処理の接続 |
| `src/app/watchdog.c` | heartbeat と watchdog |
| `src/api/` | Ruby class と native callback |
| `src/drv/` | BLE、GPIO、ADC、PWM、温度等のハードウェア処理 |
| `src/lib/mrubyc/hal.*` | Zephyr 用 HAL、console を BLE へ出力 |
| `src/rb/slot1.rb`、`slot2.rb` | 既定の system/user プログラム |
| `doc/mruby_api.md` | Ruby API の利用説明 |
| `doc/bluetooth_specification.md` | Blink の command、chunk、CRC、応答 |

根拠: [src の一覧](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3/src)、[ビルド対象](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/CMakeLists.txt#L7-L54)、[文書](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3/doc)。

CMake は mruby/c の各 C ソースを app に直接追加し、独自 HAL の include を先に指定します。コンパイル設定は `MRBC_SCHEDULER_EXIT=1`、`MRBC_USE_FLOAT=1`、`MAX_VM_COUNT=5` です。出典: [CMakeLists](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/CMakeLists.txt#L32-L54)、[prj.conf](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/prj.conf#L10-L16)。

## VM lifecycle

VM は Zephyr thread で動き、48 KiB の pool と 96 KiB の thread stack を使います。ループ内で次の順に処理します。

1. `mrbc_init`、symbol と `api_*_define`。
2. reload flag を消し、storage または内蔵配列から二つの bytecode を読む。
3. `mrbc_create_task` で二つの task を作り、slot1 の VM ID を system-task として登録する。
4. priority 1 と 2 を設定し、1 ms の k_timer で `mrbc_tick` を呼び `mrbc_run`。
5. scheduler が戻ったら timer を止め、watchdog flag と VM を cleanup して繰り返す。

出典: [mrubyc_vm.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/mrubyc_vm.c#L39-L194)。同ファイルは create の NULL 検査前に task を参照する箇所があり、そのまま安全な初期化手順として転用しません。

reload は `Blink.req_reload?` を Ruby が定期的に呼び、true なら return する協調方式です。任意の native callback や無限ループを即時中断して再ロードできる保証ではありません。出典: [slot1.rb](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/rb/slot1.rb)、[reload flag](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/mrubyc_vm.c#L98-L109)。

## 保存と転送

OpenBlink の二つの slot は Ruby プログラム用で、MCUboot のファームウェア A/B ではありません。NVS 領域は `0xe0000..0xf8000`、settings は `0xf8000..0x100000` です。出典: [partition 定義](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/pm_static_raytac_mdbt50q_db_40_nrf52840.yml#L1-L30)。

bytecode 上限は 16000 bytes、LZ4 で圧縮保存・展開します。出典: [blink.h](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/blink.h#L18-L21)、[blink.c](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/blink.c#L66-L100)。これは RBOS の既定 storage0 4 KiB に収まるという意味ではありません。

BLE は offset 付き chunk を受け、length 上限と CRC16（polynomial `0xd175`、init `0xffff`）を検査し、成功時に `BLE_EVENT_BLINK` を dispatch します。CRC は署名認証ではありません。出典: [受信処理](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/drv/ble_blink.c#L145-L211)、[protocol](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/doc/bluetooth_specification.md#L120-L142)。

watchdog は `Blink.req_reload?` 呼出で VM ごとの feed flag を立て、周期検査で flag と thread heartbeat が揃ったときに feed します。出典: [Blink API](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/blink.c#L164-L204)、[watchdog](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/app/watchdog.c#L99-L130)。呼ばない VM の異常を必ず検出する仕組みとは扱いません。

## RBOS への採否

採用候補は class 登録、値変換、再ロード前後の資源解放、chunk の境界検査です。不採用は Zephyr thread/HAL の丸ごと移植、既存 RITE0300 の流用、二つの bytecode slot の踏襲です。RBOS では `.mrb` を単一コピーとし、[権限](api-binding-patterns.md)と[保存失敗時の復旧](../dfu/bytecode-storage.md)を別途設計します。

[調査索引へ戻る](../README.md)
