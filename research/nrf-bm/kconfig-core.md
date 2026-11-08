# I/O・イベント・診断のKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `drivers/bm_lpuarte/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_SW_LPUARTE` | 未宣言 | BM_GPIOTE; BM_TIMER; NRFX_UARTE | bool "Low Power UARTE using REQ/RDY lines" | `vendor/sdk-nrf-bm/drivers/bm_lpuarte/Kconfig:7-15` |
| `BM_SW_LPUARTE_HFXO` | y | SOFTDEVICE; if BM_SW_LPUARTE | bool "Turn on HFXO for RX and TX" | `vendor/sdk-nrf-bm/drivers/bm_lpuarte/Kconfig:18-31` |

## `drivers/console/Kconfig.bm_uarte`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_UARTE_CONSOLE` | 未宣言 | CONSOLE; NRFX_UARTE | select CONSOLE_HAS_DRIVER; bool "UARTE console" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:7-12` |
| `DEPRECATED_UART_NRFX_UARTE_LEGACY_SHIM` | n | if BM_UARTE_CONSOLE | bool | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:15-18` |
| `BM_UARTE_CONSOLE_UARTE_IRQ_PRIO` | 5 | if BM_UARTE_CONSOLE | range 5 7 if SOFTDEVICE; range 2 7; int "IRQ priority" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:19-29` |
| `BM_UARTE_CONSOLE_UARTE_USE_HWFC` | 未宣言 | if BM_UARTE_CONSOLE | bool "Use hardware flow control" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:30-32` |
| `BM_UARTE_CONSOLE_UARTE_PARITY_INCLUDED` | 未宣言 | if BM_UARTE_CONSOLE | bool "Use parity" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:33-35` |
| `BM_UARTE_CONSOLE_ADD_CR_BEFORE_LF` | y | if BM_UARTE_CONSOLE | bool "Add carriage return before linefeed" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:36-42` |
| `BM_UARTE_CONSOLE_LF_TERMINATION` | 未宣言 | if BM_UARTE_CONSOLE | bool "LF termination" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:51-52` |
| `BM_UARTE_CONSOLE_CR_LF_TERMINATION` | 未宣言 | if BM_UARTE_CONSOLE | bool "CR+LF termination" | `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:53-54` |

- choice（prompt "Termination mode"; default BM_UARTE_CONSOLE_CR_LF_TERMINATION）: `vendor/sdk-nrf-bm/drivers/console/Kconfig.bm_uarte:43-55`

## `drivers/flash/Kconfig.nrf_rram`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SOC_FLASH_NRF_RRAM_BM` | y if SOFTDEVICE | DT_HAS_NORDIC_RRAM_CONTROLLER_ENABLED; FLASH | select NRFX_RRAMC if !BUILD_WITH_TFM; select FLASH_HAS_DRIVER_ENABLED; select FLASH_HAS_PAGE_LAYOUT; select FLASH_HAS_NO_EXPLICIT_ERASE; select FLASH_NRF_FORCE_ALT; select MPU_ALLOW_FLASH_WRITE if ARM_MPU; bool "Nordic Semiconductor nRF SoftDevice-based RRAM flash driver" | `vendor/sdk-nrf-bm/drivers/flash/Kconfig.nrf_rram:7-20` |
| `NRF_RRAM_REGION_ADDRESS_RESOLUTION` | 0x1000 | if SOC_FLASH_NRF_RRAM_BM | hex | `vendor/sdk-nrf-bm/drivers/flash/Kconfig.nrf_rram:23-29` |
| `NRF_RRAM_REGION_SIZE_UNIT` | 0x1000 | if SOC_FLASH_NRF_RRAM_BM | hex | `vendor/sdk-nrf-bm/drivers/flash/Kconfig.nrf_rram:30-35` |

## `lib/bm_buttons/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_BUTTONS` | 未宣言 | BM_TIMER; BM_GPIOTE | bool "Buttons library" | `vendor/sdk-nrf-bm/lib/bm_buttons/Kconfig:7-13` |
| `BM_BUTTONS_NUM_PINS` | 24 if SOC_SERIES_NRF54L | if BM_BUTTONS | range 1 24 if SOC_SERIES_NRF54L; int "Number of available pins for buttons" | `vendor/sdk-nrf-bm/lib/bm_buttons/Kconfig:16-24` |

## `lib/bm_gpiote/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_GPIOTE` | 未宣言 | NRFX_GPIOTE | bool "GPIOTE library" | `vendor/sdk-nrf-bm/lib/bm_gpiote/Kconfig:7-12` |
| `BM_GPIOTE_IRQ_PRIO` | 5 if SOFTDEVICE; 3 | if BM_GPIOTE | range 2 7; int "GPIOTE IRQ priority" | `vendor/sdk-nrf-bm/lib/bm_gpiote/Kconfig:15-23` |

## `lib/bm_scheduler/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_SCHEDULER` | 未宣言 | KERNEL_MEM_POOL | bool "Event scheduler" | `vendor/sdk-nrf-bm/lib/bm_scheduler/Kconfig:6-12` |
| `BM_SCHEDULER_BUF_SIZE` | 512 | if BM_SCHEDULER | int "Event buffer size" | `vendor/sdk-nrf-bm/lib/bm_scheduler/Kconfig:15-26` |

## `lib/bm_timer/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_TIMER` | 未宣言 | SOFTDEVICE &#124;&#124; CLOCK_CONTROL | bool "Timer library" | `vendor/sdk-nrf-bm/lib/bm_timer/Kconfig:6-12` |
| `BM_TIMER_IRQ_PRIO` | 5 if SOFTDEVICE; 3 | if BM_TIMER | range 2 7; int "Timer IRQ priority" | `vendor/sdk-nrf-bm/lib/bm_timer/Kconfig:15-28` |

## `lib/boot_banner/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `NCS_BARE_METAL_BOOT_BANNER` | y | !NCS_BOOT_BANNER | select PRINTK; select EARLY_CONSOLE; bool "NCS Bare Metal boot banner" | `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:7-16` |
| `NCS_BARE_METAL_APPLICATION_BOOT_BANNER_STRING` | "My Application" if "$(APP_VERSION_EXTENDED_STRING)" != "" | if NCS_BARE_METAL_BOOT_BANNER | string "Boot banner string" if "$(APP_VERSION_EXTENDED_STRING)" != "" | `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:19-24` |
| `NCS_BARE_METAL_BOOT_BANNER_STRING` | "nRF Connect SDK Bare Metal" | if NCS_BARE_METAL_BOOT_BANNER | string | `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:25-28` |
| `NCS_BARE_METAL_ZEPHYR_BOOT_BANNER` | 未宣言 | if NCS_BARE_METAL_BOOT_BANNER | bool "Include Zephyr OS banner" | `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:29-31` |
| `NCS_BARE_METAL_ZEPHYR_BOOT_BANNER_STRING` | "Zephyr OS [no multithreading]" | NCS_BARE_METAL_ZEPHYR_BOOT_BANNER; if NCS_BARE_METAL_BOOT_BANNER | string | `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:32-36` |

## `lib/sensorsim/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SENSORSIM` | 未宣言 | 直接指定なし | bool "Sensor simulator" | `vendor/sdk-nrf-bm/lib/sensorsim/Kconfig:7-8` |

## `lib/zephyr_queue/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `ZEPHYR_QUEUE` | 未宣言 | 直接指定なし | bool "Zephyr queue implementation" | `vendor/sdk-nrf-bm/lib/zephyr_queue/Kconfig:7-10` |

## `subsys/logging/backends/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `LOG_BACKEND_UART` | n if LOG_BACKEND_BM_UARTE | UART_CONSOLE |  | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig:12-15` |

## `subsys/logging/backends/Kconfig.bm_uarte`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `LOG_BACKEND_BM_UARTE` | 未宣言 | NRFX_UARTE | select LOG_BACKEND_SUPPORTS_FORMAT_TIMESTAMP; bool "Bare Metal UARTE backend" | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:7-13` |
| `LOG_BACKEND_UART` | n | if LOG_BACKEND_BM_UARTE |  | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:17-20` |
| `DEPRECATED_UART_NRFX_UARTE_LEGACY_SHIM` | n | if LOG_BACKEND_BM_UARTE | bool | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:21-24` |
| `LOG_BACKEND_BM_UARTE_BUFFER_SIZE` | 200 | if LOG_BACKEND_BM_UARTE | int "Maximum number of bytes to buffer in RAM before flushing" | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:25-35` |
| `LOG_BACKEND_BM_UARTE_IRQ_PRIO` | 5 | if LOG_BACKEND_BM_UARTE | range 2 7; int "IRQ priority" | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:36-43` |
| `LOG_BACKEND_BM_UARTE_USE_HWFC` | 未宣言 | if LOG_BACKEND_BM_UARTE | bool "Use hardware flow control" | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:44-46` |
| `LOG_BACKEND_BM_UARTE_PARITY_INCLUDED` | 未宣言 | if LOG_BACKEND_BM_UARTE | bool "Use parity" | `vendor/sdk-nrf-bm/subsys/logging/backends/Kconfig.bm_uarte:47-53` |

## `subsys/shell/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SHELL_LOG_BACKEND` | n | 直接指定なし |  | `vendor/sdk-nrf-bm/subsys/shell/Kconfig:10-14` |

## `subsys/shell/backends/Kconfig.bm_uarte`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `SHELL_BACKEND_BM_UARTE` | 未宣言 | 直接指定なし | select RING_BUFFER; select EXPERIMENTAL; bool "UARTE shell backend [Experimental]" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:7-13` |
| `SHELL_BACKEND_BM_UARTE_RX_RBUF_SIZE` | 128 | if SHELL_BACKEND_BM_UARTE | int "Receive ring buffer size in bytes" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:16-22` |
| `SHELL_BACKEND_BM_UARTE_RX_DBUF_SIZE` | 128 | if SHELL_BACKEND_BM_UARTE | int "Receive double buffer size in bytes" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:23-28` |
| `SHELL_BACKEND_BM_UARTE_TX_BUF_SIZE` | 128 | if SHELL_BACKEND_BM_UARTE | int "Transmit buffer size in bytes" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:29-34` |
| `SHELL_BACKEND_BM_UARTE_IRQ_PRIO` | 5 | if SHELL_BACKEND_BM_UARTE | range 3 7; int "IRQ priority" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:35-39` |
| `SHELL_BACKEND_BM_UARTE_USE_HWFC` | 未宣言 | if SHELL_BACKEND_BM_UARTE | bool "Use hardware flow control" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:40-42` |
| `SHELL_BACKEND_BM_UARTE_PARITY_INCLUDED` | 未宣言 | if SHELL_BACKEND_BM_UARTE | bool "Use parity" | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:43-46` |
| `SHELL_BACKEND_SERIAL` | n | if SHELL_BACKEND_BM_UARTE |  | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:47-50` |
| `SHELL_MINIMAL` | y | if SHELL_BACKEND_BM_UARTE |  | `vendor/sdk-nrf-bm/subsys/shell/backends/Kconfig.bm_uarte:51-53` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
