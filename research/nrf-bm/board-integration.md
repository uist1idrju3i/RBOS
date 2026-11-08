# nRF54L15-DK の board 統合

対象は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot`。同 board directory に nRF54L10/L05 emulation、S145、MCUboot なしの variants もありますが、RBOS の採用 target を増やすものではありません。出典: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/board.yml:1-111`。

## 構成ファイルの役割

| ファイル群 | 役割と制約 |
|---|---|
| board.yml、Kconfig.bm_nrf54l15dk、各 YAML/defconfig | target/variant、SoC、runner、標準設定。MCUboot の ROM_START_OFFSET default 0x800 を持つ |
| nrf54l15_cpuapp_common.dtsi | NCS の peripheral nodes を整理し、app SRAM、KMU push area、boot mode の GPREGRET1 を定義 |
| nrf54l051015_peripherals.dtsi | GPIO/GPIOTE、UART、SPI、I2C、PWM、NFCT 等の多数の標準 node を削除。Zephyr device API が全てそのまま使える前提にしない |
| nrf54l051015_oscillator.dtsi | HFXO/LFXO 有効、内部 load capacitance 15/17 pF。GRTC channels 7〜11 は SoftDevice 子所有 |
| S115 + MCUboot DTS | MCUboot/app/loader/SD/metadata/storage と retained clipboard を区画 |
| include/board-config.h | button/LED/UARTE の nrfx 用既定。多くが ifndef で上書き可能。DT だけで全 pin 設定を変更できるとは断定しない |
| CMakeLists.txt、board.cmake、Kconfig | board include path、runner・Zephyr/BM 統合。外部 SoC/Zephyr 定義と併用 |

根拠は `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.defconfig:1-12`、`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_common.dtsi:1-63`、`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l051015_peripherals.dtsi:1-76`、`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l051015_oscillator.dtsi:1-55`、`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:1-126`。

## pin・peripheral の既定

| 用途 | 既定 |
|---|---|
| button 0〜3 | P1.13、P1.09、P1.08、P0.04 |
| LED 0〜3 | P2.09、P1.10、P2.07、P1.14、active high |
| console/log | UARTE20、TX=P1.04、CTS=P1.07 |
| application UART | UARTE30、TX/RX/RTS/CTS=P0.00/01/02/03 |
| shell UART | application と同じ UARTE30 と pin |

出典: 上記 board-config.h。pin の物理接続・solder bridge・同時使用は [ハードウェア調査](../hardware/nrf54l15-dk.md)と実機で照合します。LPUARTE の REQ/RDY と NFC/TIMER も割当表へ追加します。

## メモリと保持領域

MCUboot/S115 の DTS は peer manager 4 KiB、storage0 4 KiB、app slot 1316 KiB、loader slot 64 KiB を宣言します。clipboard は `0x2003fb00` に 0x100 bytes、app_ram は 237 KiB です。SD RAM、本体 header/TLV、metadata、stack、heap は別の境界であるため、ここで示した slot サイズを Ruby が使える容量としません。全配置は [構成とメモリ](../architecture/overview.md)を参照してください。

根拠: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.dts:1-106`。retention は SRAM で、電源断を跨ぐ保存ではありません。

## Ruby-first への接続

LED/Button/GPIO の pin 所有は nRF backend が引き受け、Ruby 製品コードには論理名・設定・event を渡す方針です。利用者に SDK の C を修正させず board 設定から必要な情報を backend へ渡す仕組みは、RBOS がこれから整備する部分です。現状の SDK sample の board-config を「DeviceTree のみで製品対応済み」と説明しません。

S115 の SVC を呼ぶ IRQ は 2〜7 の範囲というだけでなく、利用 API の呼出可能 priority を確認します。GRTC channel 0 と 7〜11、NFCT の TIMER24、GPIOTE、console/app UART の重複を一覧で管理します。[割り込み調査](softdevice-and-interrupts.md)と [NFC](nfc.md)参照。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
