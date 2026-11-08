# storage・filesystem・MCUmgrのKconfig 宣言一覧

固定版の宣言を列挙します。`CONFIG_` prefix は省略。default の順序・条件を保持し、複数定義は統合しません。未宣言は「常に n」ではなく、別定義・choice・select・外部 module の影響を受けます。

依存欄は当該ファイルの直接 depends と if です。親ファイルの source 条件、menu の depends、choice の既定、外部 Zephyr/NCS の定義を展開した最終値ではありません。[設定と範囲](component-catalog.md)も参照してください。board の `.config` は未生成です。

## `subsys/bm_installs/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_INSTALL_IMAGES` | -1 | 直接指定なし | int "Install images (DO NOT ALTER)" | `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:9-14` |
| `BM_INSTALL_ENTRY_SIZE` | -1 | 直接指定なし | int "Entry size (DO NOT ALTER)" | `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:15-20` |
| `BM_INSTALL_ENTRIES` | -1 | 直接指定なし | int "Entries (DO NOT ALTER)" | `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:21-26` |
| `BM_METADATA_WRITE` | 未宣言 | 直接指定なし | select FLASH; select FLASH_MAP; bool "Metadata write functions (DO NOT ALTER)" | `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:27-37` |
| `BM_REQUIREMENTS` | y if BM_INSTALL_IMAGES != -1 | 直接指定なし | select CRC; bool | `vendor/sdk-nrf-bm/subsys/bm_installs/Kconfig:38-42` |

## `subsys/fs/bm_zms/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_ZMS` | 未宣言 | 直接指定なし | select CRC; select RING_BUFFER; select BM_STORAGE; bool "Bare Metal Zephyr Memory Storage" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:7-14` |
| `BM_ZMS_LOOKUP_CACHE` | 未宣言 | if BM_ZMS | bool "BM_ZMS lookup cache" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:17-23` |
| `BM_ZMS_LOOKUP_CACHE_SIZE` | 128 | BM_ZMS_LOOKUP_CACHE; if BM_ZMS | range 1 65536; int "BM_ZMS lookup cache size" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:24-32` |
| `BM_ZMS_DATA_CRC` | 未宣言 | if BM_ZMS | bool "BM_ZMS data CRC" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:33-35` |
| `BM_ZMS_CUSTOMIZE_BLOCK_SIZE` | 未宣言 | if BM_ZMS | bool "Customize the size of the buffer used internally for reads and writes" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:36-44` |
| `BM_ZMS_CUSTOM_BLOCK_SIZE` | 32 | BM_ZMS_CUSTOMIZE_BLOCK_SIZE; if BM_ZMS | int "BM_ZMS internal buffer size" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:45-51` |
| `BM_ZMS_OP_QUEUE_SIZE` | 16 | if BM_ZMS | int "BM_ZMS operations queue size" | `vendor/sdk-nrf-bm/subsys/fs/bm_zms/Kconfig:52-61` |

## `subsys/mgmt/mcumgr/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `NCS_BM_MCUMGR` | 未宣言 | NET_BUF; ZCBOR | bool "NCS BM MCUmgr Support" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/Kconfig:5-11` |
| `MCUMGR_SMP_LEGACY_RC_BEHAVIOUR` | 未宣言 | MCUMGR_SMP_SUPPORT_ORIGINAL_PROTOCOL; if NCS_BM_MCUMGR | bool "Legacy rc (result code) response behaviour" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/Kconfig:22-34` |

## `subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_GRP_IMG` | 未宣言 | FLASH; IMG_MANAGER; !MCUBOOT_BOOTLOADER_MODE_SINGLE_APP | select MPU_ALLOW_FLASH_WRITE if ARM_MPU; select MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_2; select MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_3 if ZCBOR_CANONICAL; imply IMG_ERASE_PROGRESSIVELY; bool "MCUmgr handlers for image management" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:15-26` |
| `MCUMGR_GRP_IMG_UPDATABLE_IMAGE_NUMBER` | UPDATEABLE_IMAGE_NUMBER | if MCUMGR_GRP_IMG | range 1 3; int "Number of supported images" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:29-40` |
| `MCUMGR_GRP_IMG_VERBOSE_ERR` | 未宣言 | if MCUMGR_GRP_IMG | select MCUMGR_SMP_VERBOSE_ERR_RESPONSE; bool "Verbose error responses when uploading application image" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:41-47` |
| `MCUMGR_GRP_IMG_ALLOW_CONFIRM_NON_ACTIVE_IMAGE_SECONDARY` | y | if MCUMGR_GRP_IMG | bool "Allow to confirm secondary slot of non-active image" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:48-57` |
| `MCUMGR_GRP_IMG_ALLOW_CONFIRM_NON_ACTIVE_IMAGE_ANY` | 未宣言 | if MCUMGR_GRP_IMG | select MCUMGR_GRP_IMG_ALLOW_CONFIRM_NON_ACTIVE_IMAGE_SECONDARY; bool "Allow to confirm slots of non-active image" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:58-67` |
| `MCUMGR_GRP_IMG_ALLOW_ERASE_PENDING` | y | if MCUMGR_GRP_IMG; if !MCUBOOT_BOOTLOADER_MODE_DIRECT_XIP | bool "Allow to erase pending slot" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:70-77` |
| `MCUMGR_GRP_IMG_VERSION_CMP_USE_BUILD_NUMBER` | 未宣言 | if MCUMGR_GRP_IMG | bool "Use build number while comparing image version" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:80-86` |
| `MCUMGR_GRP_IMG_UPLOAD_CHECK_HOOK` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_IMG | bool "Upload check hook" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:87-94` |
| `MCUMGR_GRP_IMG_STATUS_HOOKS` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_IMG | bool "Status hooks" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:95-102` |
| `MCUMGR_GRP_IMG_TOO_LARGE_DISABLED` | 未宣言 | if MCUMGR_GRP_IMG | bool "Disabled" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:116-120` |
| `MCUMGR_GRP_IMG_TOO_LARGE_SYSBUILD` | 未宣言 | ROM_END_OFFSET > 0 &#124;&#124; MCUBOOT_UPDATE_FOOTER_SIZE > 0; if MCUMGR_GRP_IMG | bool "Via Sysbuild from MCUboot configuration" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:121-126` |
| `MCUMGR_GRP_IMG_TOO_LARGE_BOOTLOADER_INFO` | 未宣言 | RETENTION_BOOTLOADER_INFO_OUTPUT_FUNCTION; if MCUMGR_GRP_IMG | bool "Via retention bootloader info" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:127-132` |
| `MCUMGR_GRP_IMG_IMAGE_SLOT_STATE_HOOK` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_IMG | bool "Image slot state hook" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:135-141` |
| `MCUMGR_GRP_IMG_IMAGE_SLOT_STATE_STATES` | 15 | if MCUMGR_GRP_IMG | int | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:142-150` |
| `MCUMGR_GRP_IMG_SLOT_INFO` | y if MCUMGR_GRP_IMG_UPDATABLE_IMAGE_NUMBER > 1 | if MCUMGR_GRP_IMG | bool "Slot info" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:151-157` |
| `MCUMGR_GRP_IMG_SLOT_INFO_HOOKS` | 未宣言 | MCUMGR_GRP_IMG_SLOT_INFO && MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_IMG | bool "Slot info hooks" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:158-164` |
| `BM_MCUMGR_GRP_IMG_NVM_WRITE_BLOCKS_MAX` | 512 | if MCUMGR_GRP_IMG | range 1 2048; int "Max NVM blocks per write operation" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:165-173` |
| `BM_MCUMGR_GRP_IMG_BUFFER_SZ` | 131072 if SOC_NRF54LM20A &#124;&#124; SOC_NRF54L15 &#124;&#124; SOC_NRF54L10 &#124;&#124; SOC_NRF54LV10A; 57344 | if MCUMGR_GRP_IMG | range MCUMGR_TRANSPORT_NETBUF_SIZE 131072; int "Image buffer size" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:174-187` |

- choice（prompt "Image size check overhead"; default MCUMGR_GRP_IMG_TOO_LARGE_DISABLED）: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/Kconfig:103-133`

## `subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_GRP_OS` | 未宣言 | 直接指定なし | imply REBOOT; bool "MCUmgr handlers for OS management" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:15-20` |
| `MCUMGR_GRP_OS_RESET_HOOK` | 未宣言 | REBOOT; MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_OS; if REBOOT | bool "Reset hook" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:25-37` |
| `MCUMGR_GRP_OS_RESET_BOOT_MODE` | 未宣言 | RETENTION_BOOT_MODE; if MCUMGR_GRP_OS; if REBOOT | bool "Boot mode" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:38-45` |
| `MCUMGR_GRP_OS_ECHO` | y | if MCUMGR_GRP_OS | select MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_2; bool "Support for echo command" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:48-52` |
| `MCUMGR_GRP_OS_MCUMGR_PARAMS` | 未宣言 | if MCUMGR_GRP_OS | bool "MCUMGR Parameters retrieval command" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:53-55` |
| `MCUMGR_GRP_OS_INFO` | 未宣言 | if MCUMGR_GRP_OS | bool "Support for info command" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:56-61` |
| `MCUMGR_GRP_OS_INFO_MAX_RESPONSE_SIZE` | 256 | if MCUMGR_GRP_OS; if MCUMGR_GRP_OS_INFO | range 32 512; int "Maximum response size for info command" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:64-72` |
| `MCUMGR_GRP_OS_INFO_CUSTOM_HOOKS` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_OS; if MCUMGR_GRP_OS_INFO | bool "Custom info hooks" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:73-79` |
| `MCUMGR_GRP_OS_INFO_BUILD_DATE_TIME` | 未宣言 | if MCUMGR_GRP_OS; if MCUMGR_GRP_OS_INFO | bool "Show build date and time" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:80-88` |
| `MCUMGR_GRP_OS_BOOTLOADER_INFO` | 未宣言 | if MCUMGR_GRP_OS | bool "Bootloader information" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:91-96` |
| `MCUMGR_GRP_OS_BOOTLOADER_INFO_HOOK` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_OS | bool "Bootloader info hooks" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/os_mgmt/Kconfig:97-107` |

## `subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_GRP_SETTINGS` | 未宣言 | BM_FLAT_SETTINGS_BLUETOOTH_NAME | select MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_2; select MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_2 if ZCBOR_CANONICAL; select MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_1; bool "MCUmgr handlers for settings management" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:4-12` |
| `MCUMGR_GRP_SETTINGS_BUFFER_TYPE_STACK` | 未宣言 | if MCUMGR_GRP_SETTINGS | bool "Stack (fixed size)" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:22-31` |
| `MCUMGR_GRP_SETTINGS_BUFFER_TYPE_HEAP` | 未宣言 | COMMON_LIBC_MALLOC_ARENA_SIZE > 0; if MCUMGR_GRP_SETTINGS | bool "Heap (dynamic size)" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:32-39` |
| `MCUMGR_GRP_SETTINGS_NAME_LEN` | 32 | if MCUMGR_GRP_SETTINGS | int "Maximum setting name length" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:42-49` |
| `MCUMGR_GRP_SETTINGS_VALUE_LEN` | 32 | if MCUMGR_GRP_SETTINGS | int "Maximum setting value length" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:50-58` |
| `MCUMGR_GRP_SETTINGS_ACCESS_HOOK` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS; if MCUMGR_GRP_SETTINGS | bool "Settings access hook" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:59-66` |

- choice（prompt "Buffer type"; default MCUMGR_GRP_SETTINGS_BUFFER_TYPE_STACK）: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/settings_mgmt/Kconfig:15-40`

## `subsys/mgmt/mcumgr/mgmt/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_MGMT_NOTIFICATION_HOOKS` | 未宣言 | 直接指定なし | bool "MCUmgr notification hook support" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/mgmt/Kconfig:12-28` |
| `MCUMGR_MGMT_HANDLER_USER_DATA` | 未宣言 | 直接指定なし | bool "MCUmgr mgmt handler user data support" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/mgmt/Kconfig:29-34` |
| `MCUMGR_MGMT_CUSTOM_PAYLOAD` | 未宣言 | 直接指定なし | bool "MCUmgr custom payload" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/mgmt/Kconfig:35-40` |

## `subsys/mgmt/mcumgr/smp/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_SMP_CBOR_MAX_MAIN_MAP_ENTRIES` | 15 | 直接指定なし | int "Number of predicted maximum entries to main response map" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:14-28` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVELS` | 7 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_7; 6 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_6; 5 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_5; 4 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_4; 3 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_3; 2 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_2; 1 if MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_1; 0 | 直接指定なし | select one of the MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_?.; int | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:29-46` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_1` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:47-49` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_2` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:50-52` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_3` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:53-55` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_4` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:56-58` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_5` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:59-61` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_6` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:62-64` |
| `MCUMGR_SMP_CBOR_MIN_DECODING_LEVEL_7` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:65-67` |
| `MCUMGR_SMP_CBOR_MAX_DECODING_LEVELS` | MCUMGR_SMP_CBOR_MIN_DECODING_LEVELS | 直接指定なし | range MCUMGR_SMP_CBOR_MIN_DECODING_LEVELS 15; int "Number of map/list encapsulations allowed for SMP decoding" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:68-84` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVELS` | 7 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_7; 6 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_6; 5 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_5; 4 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_4; 3 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_3; 2 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_2; 1 if MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_1 &#124;&#124; ZCBOR_CANONICAL; 0 | 直接指定なし | select one of the MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_?.; int | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:85-102` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_1` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:103-105` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_2` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:106-108` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_3` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:109-111` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_4` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:112-114` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_5` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:115-117` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_6` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:118-120` |
| `MCUMGR_SMP_CBOR_MIN_ENCODING_LEVEL_7` | 未宣言 | 直接指定なし | bool | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:121-123` |
| `MCUMGR_SMP_CBOR_MAX_ENCODING_LEVELS` | MCUMGR_SMP_CBOR_MIN_ENCODING_LEVELS | 直接指定なし | range MCUMGR_SMP_CBOR_MIN_ENCODING_LEVELS 15; int "Number of map/list encapsulations allowed for SMP encoding" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:124-134` |
| `MCUMGR_SMP_COMMAND_STATUS_HOOKS` | 未宣言 | MCUMGR_MGMT_NOTIFICATION_HOOKS | bool "SMP command status hooks" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:135-141` |
| `MCUMGR_SMP_SUPPORT_ORIGINAL_PROTOCOL` | y | 直接指定なし | bool "Support original protocol" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:142-151` |
| `MCUMGR_SMP_VERBOSE_ERR_RESPONSE` | 未宣言 | MCUMGR_SMP_SUPPORT_ORIGINAL_PROTOCOL | bool "Support verbose error response" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/smp/Kconfig:152-161` |

## `subsys/mgmt/mcumgr/transport/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_TRANSPORT_REASSEMBLY` | 未宣言 | 直接指定なし | bool "Reassembly support" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig:14-18` |
| `MCUMGR_TRANSPORT_NETBUF_COUNT` | 4 | 直接指定なし | int "Number of MCUmgr buffers" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig:19-25` |
| `MCUMGR_TRANSPORT_NETBUF_SIZE` | 2475 if MCUMGR_TRANSPORT_REASSEMBLY; 384 | 直接指定なし | int "Size of each MCUmgr buffer" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig:26-41` |

## `subsys/mgmt/mcumgr/transport/Kconfig.bm_uart`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `MCUMGR_TRANSPORT_BM_UART` | 未宣言 | BASE64; CRC | bool "Bare Metal UART MCUmgr SMP transport" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:11-17` |
| `MCUMGR_TRANSPORT_BM_UART_UARTE_HWFC` | 未宣言 | if MCUMGR_TRANSPORT_BM_UART | bool "UARTE HWFC" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:20-24` |
| `MCUMGR_TRANSPORT_BM_UART_UARTE_PARITY` | 未宣言 | if MCUMGR_TRANSPORT_BM_UART | bool "UARTE parity" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:25-29` |
| `MCUMGR_TRANSPORT_BM_UART_UARTE_IRQ_PRIO` | 3 | if MCUMGR_TRANSPORT_BM_UART | range 2 7; int "UARTE IRQ priority" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:30-37` |
| `MCUMGR_TRANSPORT_BM_UART_RX_BUF_SIZE` | 128 | if MCUMGR_TRANSPORT_BM_UART | int "Size of receive buffer for mcumgr fragments received over UART, in bytes" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:38-46` |
| `UART_MCUMGR_RX_BUF_SIZE` | MCUMGR_TRANSPORT_BM_UART_RX_BUF_SIZE | if MCUMGR_TRANSPORT_BM_UART | int | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:47-50` |
| `MCUMGR_TRANSPORT_BM_UART_RX_BUF_COUNT` | 8 | if MCUMGR_TRANSPORT_BM_UART | int "Number of receive buffers for mcumgr fragments received over UART" | `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/transport/Kconfig.bm_uart:51-60` |

## `subsys/storage/ble_rmem/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_FLAT_SETTINGS_BLUETOOTH_NAME` | 未宣言 | !SETTINGS | select BM_RMEM_CLIPBOARD; bool "Bluetooth name settings clipboard" | `vendor/sdk-nrf-bm/subsys/storage/ble_rmem/Kconfig:7-16` |

## `subsys/storage/bm_rmem/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_RMEM_CLIPBOARD` | 未宣言 | $(dt_chosen_enabled,$(DT_CHOSEN_NCSBM_CLIPBOARD_PARTITION)) | bool "Inter application RAM Clipboard" | `vendor/sdk-nrf-bm/subsys/storage/bm_rmem/Kconfig:10-17` |

## `subsys/storage/bm_storage/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_STORAGE` | 未宣言 | 直接指定なし | bool "Bare Metal storage" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/Kconfig:7-11` |
| `BM_STORAGE_BACKEND_RRAM` | 未宣言 | !SOFTDEVICE; if BM_STORAGE | bool "RRAMC" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/Kconfig:16-21` |
| `BM_STORAGE_BACKEND_SD` | y | SOFTDEVICE; NRF_SDH; RING_BUFFER; if BM_STORAGE | bool "SoftDevice" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/Kconfig:22-30` |
| `BM_STORAGE_BACKEND_NATIVE_SIM` | 未宣言 | BOARD_NATIVE_SIM; ZTEST; if BM_STORAGE | bool "Simulated (native)" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/Kconfig:31-37` |

## `subsys/storage/bm_storage/native_sim/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_STORAGE_BACKEND_NATIVE_SIM_ASYNC` | 未宣言 | 直接指定なし | bool "Asynchronous execution of storage operations" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/native_sim/Kconfig:9-11` |

## `subsys/storage/bm_storage/sd/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `BM_STORAGE_BACKEND_SD_QUEUE_SIZE` | 4 | 直接指定なし | int "Queue size" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/Kconfig:9-14` |
| `BM_STORAGE_BACKEND_SD_MAX_RETRIES` | 8 | 直接指定なし | range 0 255; int "Maximum number of retries when SoftDevice is busy" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/Kconfig:15-22` |
| `BM_STORAGE_BACKEND_SD_MAX_WRITE_SIZE` | 32 | 直接指定なし | int "Maximum number of bytes to pass to sd_flash_write() at once" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/Kconfig:23-38` |
| `BM_STORAGE_BACKEND_SD_ERASE_BLOCKS` | 未宣言 | 直接指定なし | bool "Erase in blocks" | `vendor/sdk-nrf-bm/subsys/storage/bm_storage/sd/Kconfig:39-46` |

## `subsys/storage/flash_map/Kconfig`

| symbol | 宣言 default | 直接 depends / ファイル内 if | select・imply / range / 型 | 出典 |
|---|---|---|---|---|
| `FLASH_MAP_CUSTOM_NCS_BM_MCUMGR` | 未宣言 | NCS_BM_MCUMGR; if FLASH_MAP_CUSTOM | bool "Bare metal MCUmgr flash map" | `vendor/sdk-nrf-bm/subsys/storage/flash_map/Kconfig:11-19` |

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
