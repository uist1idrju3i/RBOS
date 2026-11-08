# board・外部 module・sysbuildのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `Kconfig.nrf_bm`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `NCS_BM` | y | 直接指定なし | bool "NCS Bare Metal" | `vendor/sdk-nrf-bm/Kconfig.nrf_bm:7-10` |

## `boards/nordic/bm_nrf54l15dk/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BOARD_BM_NRF54L15DK` | 未宣言 | 直接指定なし | select BOARD_LATE_INIT_HOOK | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig:7-8` |

## `boards/nordic/bm_nrf54l15dk/Kconfig.bm_nrf54l15dk`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BOARD_BM_NRF54L15DK` | 未宣言 | 直接指定なし | select SOC_NRF54L05_CPUAPP if BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S115_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S145_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S145_SOFTDEVICE_MCUBOOT; select SOC_NRF54L10_CPUAPP if BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S115_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S145_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S145_SOFTDEVICE_MCUBOOT; select SOC_NRF54L15_CPUAPP if BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S115_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;   BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S145_SOFTDEVICE &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S145_SOFTDEVICE_MCUBOOT | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.bm_nrf54l15dk:7-19` |

## `boards/nordic/bm_nrf54l15dk/Kconfig.defconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `ROM_START_OFFSET` | 0x800 if BOOTLOADER_MCUBOOT | 直接指定なし |  | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.defconfig:7-9` |

- choice（default NRF_GRTC_TIMER_SOURCE_LFLPRC if !$(dt_nodelabel_enabled,lfxo)）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.defconfig:10-12`

## `boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `PARTITION_MANAGER` | n | 直接指定なし |  | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:7-9` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU` | y | if BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S145_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S145_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S145_SOFTDEVICE_MCUBOOT |  | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:62-64` |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_BOOT_MODE` | y | if BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S115_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L05_CPUAPP_S145_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L10_CPUAPP_S145_SOFTDEVICE_MCUBOOT &#124;&#124;  BOARD_BM_NRF54L15DK_NRF54L15_CPUAPP_S145_SOFTDEVICE_MCUBOOT |  | `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:73-75` |

- choice（default SOFTDEVICE_S115）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:17-19`

- choice（default SOFTDEVICE_S145）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:35-37`

- choice（default BM_BOOTLOADER_MCUBOOT）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:54-56`

- choice（default BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:58-60`

- choice（default BM_BOOT_IMG_HASH_ALG_PURE）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:65-67`

- choice（default BM_FIRMWARE_LOADER_BT_MCUMGR）: `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:69-71`

## `modules/hal_nordic/nrfx/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `HAS_NRFX` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:8-10` |
| `NRFX_ADC` | 未宣言 | SOC_SERIES_NRF51X | bool "ADC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:14-17` |
| `NRFX_CLOCK` | 未宣言 | 直接指定なし | bool "CLOCK driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:18-20` |
| `NRFX_CLOCK_LFXO_TWO_STAGE_ENABLED` | 未宣言 | if NRFX_CLOCK | bool "Two stage start sequence of the low frequency clock" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:23-25` |
| `NRFX_CLOCK_LF_CAL_ENABLED` | 未宣言 | if NRFX_CLOCK | bool "LFRC Calibration enabled" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:26-28` |
| `NRFX_CLOCK_LF_SRC_RC` | 未宣言 | if NRFX_CLOCK | bool "RC Oscillator" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:29-31` |
| `NRFX_CLOCK_LF_SRC_XTAL` | 未宣言 | if NRFX_CLOCK | bool "Crystal Oscillator" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:32-34` |
| `NRFX_CLOCK_LF_SRC_SYNTH` | 未宣言 | !SOC_SERIES_NRF91X; if NRFX_CLOCK | bool "Synthesized from HFCLK" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:35-38` |
| `NRFX_CLOCK_LF_SRC_LOW_SWING` | 未宣言 | SOC_SERIES_NRF52X; if NRFX_CLOCK | bool "External low swing" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:39-42` |
| `NRFX_CLOCK_LF_SRC_FULL_SWING` | 未宣言 | SOC_SERIES_NRF52X; if NRFX_CLOCK | bool "External full swing" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:43-46` |
| `NRFX_COMP` | 未宣言 | 直接指定なし | bool "COMP driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:49-51` |
| `NRFX_CRACEN` | 未宣言 | SOC_COMPATIBLE_NRF54LX | bool "CRACEN drivers" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:52-55` |
| `NRFX_EGU` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:56-58` |
| `NRFX_EGU0` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:59-62` |
| `NRFX_EGU1` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU1 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:63-66` |
| `NRFX_EGU2` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU2 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:67-70` |
| `NRFX_EGU3` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU3 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:71-74` |
| `NRFX_EGU4` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU4 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:75-78` |
| `NRFX_EGU5` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU5 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:79-82` |
| `NRFX_EGU10` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU10 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:83-86` |
| `NRFX_EGU20` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU20 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:87-90` |
| `NRFX_EGU020` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU020 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:91-94` |
| `NRFX_EGU130` | 未宣言 | 直接指定なし | select NRFX_EGU; bool "EGU130 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:95-98` |
| `NRFX_GPIOTE` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:99-101` |
| `NRFX_GPIOTE0` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "GPIOTE0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:102-105` |
| `NRFX_GPIOTE1` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "GPIOTE1 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:106-109` |
| `NRFX_GPIOTE20` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "NRFX_GPIOTE20 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:110-113` |
| `NRFX_GPIOTE30` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "NRFX_GPIOTE30 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:114-117` |
| `NRFX_GPIOTE130` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "NRFX_GPIOTE130 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:118-121` |
| `NRFX_GPIOTE131` | 未宣言 | 直接指定なし | select NRFX_GPIOTE; bool "NRFX_GPIOTE131 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:122-125` |
| `NRFX_GPIOTE_NUM_OF_EVT_HANDLERS` | 未宣言 | NRFX_GPIOTE | range 1 15; int "Number of event handlers" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:126-133` |
| `NRFX_GPPI` | 未宣言 | 直接指定なし | bool "Generic PPI layer" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:134-139` |
| `NRFX_GRTC` | 未宣言 | 直接指定なし | bool "GRTC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:140-142` |
| `NRFX_I2S` | 未宣言 | 直接指定なし | bool "I2S driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:143-145` |
| `NRFX_IPC` | 未宣言 | 直接指定なし | bool "IPC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:146-148` |
| `NRFX_LPCOMP` | 未宣言 | !SOC_NRF52810 && !SOC_NRF52811 && !SOC_NRF52820 | bool "LPCOMP driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:149-152` |
| `NRFX_MRAMC` | 未宣言 | 直接指定なし | bool "MRAMC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:153-155` |
| `NRFX_NFCT` | 未宣言 | 直接指定なし | select NRFX_TIMER; bool "NFCT driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:156-159` |
| `NRFX_NVMC` | 未宣言 | 直接指定なし | bool "NVMC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:160-162` |
| `NRFX_PDM` | 未宣言 | 直接指定なし | bool "PDM driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:163-165` |
| `NRFX_POWER` | 未宣言 | 直接指定なし | bool "POWER driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:166-168` |
| `NRFX_PWM` | 未宣言 | 直接指定なし | bool "PWM driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:169-171` |
| `NRFX_QDEC` | 未宣言 | 直接指定なし | bool "QDEC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:172-174` |
| `NRFX_QSPI` | 未宣言 | 直接指定なし | bool "QSPI driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:175-177` |
| `NRFX_RNG` | 未宣言 | 直接指定なし | bool "RNG driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:178-180` |
| `NRFX_RRAMC` | 未宣言 | 直接指定なし | bool "RRAMC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:181-183` |
| `NRFX_RTC` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:184-186` |
| `NRFX_RTC0` | 未宣言 | 直接指定なし | select NRFX_RTC; bool "RTC0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:187-190` |
| `NRFX_RTC1` | 未宣言 | 直接指定なし | select NRFX_RTC; bool "RTC1 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:191-194` |
| `NRFX_RTC2` | 未宣言 | 直接指定なし | select NRFX_RTC; bool "RTC2 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:195-198` |
| `NRFX_RTC130` | 未宣言 | 直接指定なし | select NRFX_RTC; bool "RTC130 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:199-202` |
| `NRFX_RTC131` | 未宣言 | 直接指定なし | select NRFX_RTC; bool "RTC131 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:203-206` |
| `NRFX_SAADC` | 未宣言 | !SOC_SERIES_NRF51X | bool "SAADC driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:207-210` |
| `NRFX_SPI` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:211-213` |
| `NRFX_SPI0` | 未宣言 | 直接指定なし | select NRFX_SPI; bool "SPI0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:214-217` |
| `NRFX_SPI1` | 未宣言 | 直接指定なし | select NRFX_SPI; bool "SPI1 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:218-221` |
| `NRFX_SPI2` | 未宣言 | 直接指定なし | select NRFX_SPI; bool "SPI2 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:222-225` |
| `NRFX_SPIS` | 未宣言 | 直接指定なし | bool "SPIS driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:226-228` |
| `NRFX_SPIM` | 未宣言 | 直接指定なし | bool "SPIM driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:229-231` |
| `NRFX_SYSTICK` | 未宣言 | CPU_CORTEX_M_HAS_SYSTICK | bool "SYSTICK driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:232-235` |
| `NRFX_TBM` | 未宣言 | 直接指定なし | bool "TBM driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:236-238` |
| `NRFX_TEMP` | 未宣言 | 直接指定なし | bool "TEMP driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:239-241` |
| `NRFX_TIMER` | 未宣言 | 直接指定なし | bool "TIMER driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:242-244` |
| `NRFX_TWI` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:245-247` |
| `NRFX_TWI0` | 未宣言 | SOC_SERIES_NRF51X &#124;&#124; SOC_SERIES_NRF52X | select NRFX_TWI; bool "TWI0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:248-252` |
| `NRFX_TWI1` | 未宣言 | SOC_SERIES_NRF51X &#124;&#124; SOC_SERIES_NRF52X | select NRFX_TWI; bool "TWI1 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:253-257` |
| `NRFX_TWIM` | 未宣言 | 直接指定なし | bool "NRFX driver for TWIM peripheral" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:258-260` |
| `NRFX_TWIS` | 未宣言 | 直接指定なし | bool "NRFX driver for TWIS peripheral" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:261-263` |
| `NRFX_UART` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:264-266` |
| `NRFX_UART0` | 未宣言 | SOC_SERIES_NRF51X &#124;&#124; SOC_SERIES_NRF52X | select NRFX_UART; bool "UART0 driver instance" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:267-271` |
| `NRFX_UARTE` | 未宣言 | 直接指定なし | bool "UARTE driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:272-274` |
| `NRFX_UARTE_CONFIG_SKIP_GPIO_CONFIG` | 未宣言 | NRFX_UARTE | bool "UARTE GPIO configuration support" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:275-278` |
| `NRFX_UARTE_CONFIG_SKIP_PSEL_CONFIG` | 未宣言 | NRFX_UARTE | bool "UARTE PSEL configuration support" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:279-282` |
| `NRFX_UARTE_CONFIG_TX_LINK` | 未宣言 | NRFX_UARTE | bool "UARTE TX transfer linking support" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:283-286` |
| `NRFX_UARTE_CONFIG_RX_CACHE_ENABLED` | 未宣言 | NRFX_UARTE | bool "UARTE RX caching support" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:287-294` |
| `NRFX_USBREG` | 未宣言 | 直接指定なし | bool "USBREG driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:295-297` |
| `NRFX_WDT` | 未宣言 | 直接指定なし | bool "WDT driver" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:298-300` |
| `NRFX_PRS` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:303-305` |
| `NRFX_PRS_BOX_0` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 0" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:306-309` |
| `NRFX_PRS_BOX_1` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 1" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:310-313` |
| `NRFX_PRS_BOX_2` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 2" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:314-317` |
| `NRFX_PRS_BOX_3` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 3" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:318-321` |
| `NRFX_PRS_BOX_4` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 4" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:322-325` |
| `NRFX_PRS_BOX_5` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 5" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:326-329` |
| `NRFX_PRS_BOX_6` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 6" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:330-333` |
| `NRFX_PRS_BOX_7` | 未宣言 | 直接指定なし | select NRFX_PRS; bool "PRS box 7" | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:334-337` |
| `NRFX_RESERVED_RESOURCES_HEADER` | "nrfx_reserved_resources_ncs.h" | 直接指定なし | string | `vendor/sdk-nrf-bm/modules/hal_nordic/nrfx/Kconfig:340-343` |

## `modules/mcuboot/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SOFTDEVICE_FILE` | 未宣言 | if MCUBOOT | string "SoftDevice file (DO NOT ALTER)" | `vendor/sdk-nrf-bm/modules/mcuboot/Kconfig:11-13` |
| `SOFTDEVICE_PAD_HEADER` | 未宣言 | if MCUBOOT | bool "Pad SoftDevice header (DO NOT ALTER)" | `vendor/sdk-nrf-bm/modules/mcuboot/Kconfig:14-16` |
| `SOFTDEVICE_VERSION` | "0.0.0+0" | if MCUBOOT | string "SoftDevice signing version (DO NOT ALTER)" | `vendor/sdk-nrf-bm/modules/mcuboot/Kconfig:17-20` |
| `SOFTDEVICE_START_OFFSET` | 0x800 if SOC_SERIES_NRF54L; 0x200 | if MCUBOOT | hex | `vendor/sdk-nrf-bm/modules/mcuboot/Kconfig:21-25` |

## `sysbuild/Kconfig.bm`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_BOOTLOADER_NONE` | 未宣言 | 直接指定なし | bool "None" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:10-14` |
| `BM_BOOTLOADER_MCUBOOT` | 未宣言 | 直接指定なし | bool "MCUboot" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:15-19` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_NONE` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "No signature; use only hash check" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:31-33` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_RSA` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "RSA signatures" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:34-36` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ECDSA_P256` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "Elliptic curve digital signatures with curve P-256" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:37-39` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "Edwards curve digital signatures using ed25519" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:40-42` |
| `BM_CRACEN_MICROCODE_LOAD_ONCE` | y | BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519; !SOC_NRF54LM20A && !SOC_NRF54LM20B && !SOC_NRF54LV10A && !SOC_NRF54LS05B; if BM_BOOTLOADER_MCUBOOT | bool "Load CRACEN microcode once only" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:45-52` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE` | "$(ZEPHYR_MCUBOOT_MODULE_DIR)/root-ec-p256.pem" if BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ECDSA_P256; "$(ZEPHYR_MCUBOOT_MODULE_DIR)/root-ed25519.pem" if BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519; "$(ZEPHYR_MCUBOOT_MODULE_DIR)/root-rsa-2048.pem" if BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_RSA; "" | if BM_BOOTLOADER_MCUBOOT | string "Signing PEM key file" if !BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_NONE | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:53-61` |
| `BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU` | 未宣言 | SOC_SERIES_NRF54L && BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519; if BM_BOOTLOADER_MCUBOOT | bool "Use KMU stored keys for signature verification" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:62-67` |
| `BM_BOOTLOADER_MCUBOOT_GENERATE_DEFAULT_KMU_KEYFILE` | y | BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU; if BM_BOOTLOADER_MCUBOOT | bool "Generate default keyfile for provisioning during build" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:68-74` |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_GPIO` | y | if BM_BOOTLOADER_MCUBOOT | bool "GPIO" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:78-81` |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_PIN_RESET` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "Check for device reset by pin" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:82-84` |
| `BM_BOOTLOADER_MCUBOOT_FIRMWARE_LOADER_ENTRANCE_BOOT_MODE` | 未宣言 | if BM_BOOTLOADER_MCUBOOT | bool "Check boot mode via retention subsystem" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:85-87` |
| `BM_APP_CAN_SETUP_FIRMWARE_LOADER_NAME` | 未宣言 | !BM_FIRMWARE_LOADER_NONE; if BM_BOOTLOADER_MCUBOOT | select EXPERIMENTAL; bool "Remote setup firmware loader BLE Advertising Name [EXPERIMENTAL]" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:90-98` |
| `BM_BOOT_IMG_HASH_ALG_SHA256` | 未宣言 | !BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU; if BM_BOOTLOADER_MCUBOOT | bool "SHA256" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:104-107` |
| `BM_BOOT_IMG_HASH_ALG_SHA512` | 未宣言 | SOC_SERIES_NRF54L; !BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU; if BM_BOOTLOADER_MCUBOOT | bool "SHA512" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:108-112` |
| `BM_BOOT_IMG_HASH_ALG_PURE` | 未宣言 | BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519 && SOC_SERIES_NRF54L; if BM_BOOTLOADER_MCUBOOT | bool "Pure (hash of data directly without hash)" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:113-116` |
| `BM_BOOT_BOOTCONF_LOCK_WRITES` | 未宣言 | SOC_NRF54L15_CPUAPP &#124;&#124; SOC_NRF54L10_CPUAPP &#124;&#124; SOC_NRF54L05_CPUAPP &#124;&#124; SOC_NRF54LV10A_CPUAPP; if BM_BOOTLOADER_MCUBOOT | bool "Protect bootloader's NVM from writes" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:119-124` |
| `BM_BOOTLOADER_IMAGE_NAME` | "mcuboot" if BM_BOOTLOADER_MCUBOOT | if !BM_BOOTLOADER_NONE | string | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:131-136` |
| `BM_BOOTLOADER_IMAGE_PATH` | "${ZEPHYR_MCUBOOT_MODULE_DIR}/boot/zephyr" if BM_BOOTLOADER_MCUBOOT | if !BM_BOOTLOADER_NONE | string | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:137-142` |
| `BM_FIRMWARE_LOADER_NONE` | 未宣言 | if !BM_BOOTLOADER_NONE | bool "None" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:146-150` |
| `BM_FIRMWARE_LOADER_BT_MCUMGR` | 未宣言 | if !BM_BOOTLOADER_NONE | bool "Bluetooth MCUmgr" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:151-155` |
| `BM_FIRMWARE_LOADER_UART_MCUMGR` | 未宣言 | if !BM_BOOTLOADER_NONE | bool "UART MCUmgr" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:156-160` |
| `BM_FIRMWARE_LOADER_IMAGE_NAME` | "firmware_loader" | if !BM_BOOTLOADER_NONE; if !BM_FIRMWARE_LOADER_NONE | string | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:165-170` |
| `BM_FIRMWARE_LOADER_IMAGE_PATH` | "$(ZEPHYR_NRF_BM_MODULE_DIR)/applications/firmware_loader/ble_mcumgr" if BM_FIRMWARE_LOADER_BT_MCUMGR; "$(ZEPHYR_NRF_BM_MODULE_DIR)/applications/firmware_loader/uart_mcumgr" if BM_FIRMWARE_LOADER_UART_MCUMGR | if !BM_BOOTLOADER_NONE; if !BM_FIRMWARE_LOADER_NONE | string | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:171-177` |
| `SOFTDEVICE_NONE` | 未宣言 | 直接指定なし | bool "None" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:185-187` |
| `SOFTDEVICE_S115` | 未宣言 | SOC_SERIES_NRF54L | bool "S115" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:188-191` |
| `SOFTDEVICE_S145` | 未宣言 | SOC_SERIES_NRF54L | bool "S145" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:192-195` |
| `SOFTDEVICE_FILE` | "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s115/s115_nrf54l05_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54L05; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s115/s115_nrf54l10_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54L10; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s115/s115_nrf54l15_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54L15; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s145/s145_nrf54l05_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54L05; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s145/s145_nrf54l10_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54L10; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54l/s145/s145_nrf54l15_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54L15; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54lv/s115/s115_nrf54lv10_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54LV10A; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54lv/s145/s145_nrf54lv10_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54LV10A; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54lm/s115/s115_nrf54lm20_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54LM20A; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54lm/s145/s145_nrf54lm20_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54LM20A; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54ls/s115/s115_nrf54ls05_10.0.1_softdevice.hex" if SOFTDEVICE_S115 && SOC_NRF54LS05B; "$(ZEPHYR_NRF_BM_MODULE_DIR)/components/softdevice/nrf54ls/s145/s145_nrf54ls05_10.0.1_softdevice.hex" if SOFTDEVICE_S145 && SOC_NRF54LS05B | 直接指定なし | string | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:198-214` |
| `METADATA_SIZE` | 0x200 if SOC_SERIES_NRF54L | 直接指定なし | hex | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:215-220` |
| `METADATA_ENTRY_SIZE` | 32 | 直接指定なし | int | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:221-226` |
| `INSTALLER_HEX_OUTPUT` | 未宣言 | 直接指定なし | bool "Installer hex output [DEBUG]" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:227-230` |

- choice（prompt "Bootloader selection"）: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:7-20`

- choice（prompt "Signature type"; default BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519 if SOC_SERIES_NRF54L; default BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_RSA）: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:26-43`

- choice（prompt "Hashing algorithm"; default BM_BOOT_IMG_HASH_ALG_PURE if BM_BOOTLOADER_MCUBOOT_SIGNATURE_TYPE_ED25519 && SOC_SERIES_NRF54L; default BM_BOOT_IMG_HASH_ALG_SHA256）: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:99-117`

- choice（prompt "Firmware loader selection"）: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:143-161`

- choice（prompt "SoftDevice selection"）: `vendor/sdk-nrf-bm/sysbuild/Kconfig.bm:182-196`

## `sysbuild/Kconfig.sysbuild`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `NCS_BM` | y | 直接指定なし | bool "NCS Bare Metal" | `vendor/sdk-nrf-bm/sysbuild/Kconfig.sysbuild:1-4` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
