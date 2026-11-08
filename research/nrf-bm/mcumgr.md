# MCUmgr と install metadata

firmware 更新方式・署名・loader 入口は [single-bank DFU](../dfu/single-bank-dfu.md)、MCUboot の mode は [MCUboot 調査](../dfu/mcuboot.md)を正とし、ここでは subsystem の構成と RBOS の境界を扱います。[公開 API](api-storage.md)、[Kconfig](kconfig-storage.md)も参照してください。

| component | 機能と API 境界 | 実行 context・S115・RBOS での使い方 |
|---|---|---|
| mgmt | group/handler 登録・管理 event。CMake が Zephyr 側 mgmt.c を取り込む | role 非依存。`NCS_BM_MCUMGR` は NET_BUF・ZCBOR 依存。管理要求の許可と特権チェックは binding の class 登録とは別 |
| smp | Zephyr 側 SMP protocol 処理と CBOR version/error 規約 | 受信 transport がどの context から処理を呼ぶかを確認。protocol 名だけで worker thread があると考えない |
| util | upstream の CBOR/network buffer utility を結合 | Ruby に内部 net_buf を渡さず、必要なら request 結果だけをコピー |
| transport | request/response net_buf、SMP transport、reassembly、UART serial 化 | `smp_rx_req` はこの BM 実装で request を直接処理。BLE callback が IRQ なら深い処理を IRQ へ持ち込む可能性があり SDH model を確認 |
| transport/bm_uart | nrfx UARTE 受信を fragment/FIFO へ蓄え、`smp_uart_process_rx_queue()` で処理 | 対象。UART IRQ 既定 3。受信 IRQ で Ruby を呼ばず foreground で queue を処理。console/shell との peripheral 競合を確認 |
| grp/img_mgmt | app/installer の upload、info、state 関連 API。BM 固有の image write 実装 | 対象、基本は独立 firmware loader。存在する state API 名から汎用 MCUboot A/B rollback を推論しない |
| grp/os_mgmt | 外部 Zephyr OS management の情報・reset 等 | 対象。必要な command のみに絞り、reset や bootloader 遷移の権限を設計 |
| grp/settings_mgmt | flat Bluetooth name settings の read/write と access hook | 対象。`BM_FLAT_SETTINGS_BLUETOOTH_NAME` 依存。任意の application settings DB を提供するものではない |
| bm_installs | image の位置・長さ・checksum、init/is_valid/read/get_image_data | 対象。system 用 metadata。`BM_INSTALL_*` は sysbuild が設定する DO NOT ALTER 項目。Ruby の通常利用者に直接 write を公開しない |

構成・外部 source の根拠: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/CMakeLists.txt:1-17`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/mgmt/CMakeLists.txt:1-10`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/CMakeLists.txt:1-9`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/util/CMakeLists.txt:1-13`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/CMakeLists.txt:1-24`。直接 request 処理は `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/src/smp.c:1-117`、UART FIFO は `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/src/smp_uart.c:1-104`。settings の依存・access hook は `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:1-67`。

bm_installs は `vendor/sdk-nrf-bm/subsys/bm_installs/include/bm_installs.h:1-88` と `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:1-43`。`bm_installs_write/invalidate` は header にあっても「Functions not for public use」です。API 索引上の宣言を製品向け API と誤解しません。metadata の write 有効化も sysbuild と installer の責務にします。

## メモリ予算

| 項目 | 宣言上の既定と注意 |
|---|---|
| SMP net_buf | COUNT=4、SIZE=384（reassembly 有効なら 2475）。payload だけで 1536 または 9900 bytes。net_buf の管理情報等は別 |
| UART fragment | RX_BUF_COUNT=8、SIZE=128。payload 1024 bytes と FIFO/descriptor/driver buffer は別 |
| image upload | nRF54L15 では BM_MCUMGR_GRP_IMG_BUFFER_SZ=131072。range と wear unit の倍数を確認 |
| settings group | name/value default 各 32。stack/heap を choice で選択。heap は malloc arena 条件あり |
| install metadata | entry 数とサイズは sysbuild 依存。checksum と padding を含む構造で、アプリが任意に縮めない |

出典: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig:1-41`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:1-61`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:1-188`、`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:1-67`、`vendor/sdk-nrf-bm/subsys/bm_installs/include/bm_installs.h:1-88`。

これらを通常 app の mruby/c heap と一律に足し合わせません。app と loader は別 image で、各 map・stack を別に測ります。Ruby を動かしながら image upload する前提ではありません。

## RBOS backend の候補

- `dfu_request(reason)`: 特権 caller を確認して安全に終了し、boot mode/retention を設定して loader へ再起動する。
- `image_info()`: 必要な版・署名状態等を読取専用で返す。raw flash map や install write は公開しない。
- `dfu_name_set(name)`: 製品識別が必要なら retention clipboard の容量・CRC・有効期限を検証する。

いずれも未実装です。MCUmgr service の default security が OPEN である点を [services](ble-services.md)に記録しました。署名検証と transport/command の認証を別に設計し、誤署名・途中切断・満杯・電源断・reset/設定書換えの権限を試験します。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
