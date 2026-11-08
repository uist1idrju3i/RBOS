# compile-time macro の全条件索引

src の #if/#elif/#ifdef/#ifndef に現れる symbol を列挙しました。include guard は除外しています。内部判定・compiler predefined symbol も含み、全てが利用者向け override ではありません。既定と予算の説明は [設定とメモリ](configuration-and-memory.md)を参照してください。

| symbol | 宣言・定義（条件付き default を含む） | 条件を使う箇所 |
|---|---|---|
| `MAX_REGS_SIZE` | #define MAX_REGS_SIZE 110 `vendor/mrubyc/src/vm_config.h:25-25` | `vendor/mrubyc/src/vm_config.h:24-24` |
| `MAX_SYMBOLS_COUNT` | #define MAX_SYMBOLS_COUNT 255 `vendor/mrubyc/src/vm_config.h:30-30` | `vendor/mrubyc/src/symbol.c:36-36`、`vendor/mrubyc/src/vm_config.h:29-29` |
| `MAX_VM_COUNT` | #define MAX_VM_COUNT 5 `vendor/mrubyc/src/vm_config.h:20-20` | `vendor/mrubyc/src/vm_config.h:19-19` |
| `MRBC_ABORT_BY_EXCEPTION` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/vm.c:365-365` |
| `MRBC_ALLOC_16BIT` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:129-129` |
| `MRBC_ALLOC_24BIT` | #define MRBC_ALLOC_24BIT `vendor/mrubyc/src/vm_config.h:36-36` | `vendor/mrubyc/src/alloc.c:160-160` |
| `MRBC_ALLOC_FLI_BIT_WIDTH` | # define MRBC_ALLOC_FLI_BIT_WIDTH 9	// ~~~~~~~~~~~ `vendor/mrubyc/src/alloc.c:81-81` | `vendor/mrubyc/src/alloc.c:80-80` |
| `MRBC_ALLOC_IGNORE_LSBS` | # define MRBC_ALLOC_IGNORE_LSBS	  4	//                ~~~~ `vendor/mrubyc/src/alloc.c:87-87` | `vendor/mrubyc/src/alloc.c:86-86` |
| `MRBC_ALLOC_LIBC` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:54-54`、`vendor/mrubyc/src/alloc.h:23-23`、`vendor/mrubyc/src/alloc.h:62-62`、`vendor/mrubyc/src/alloc.h:103-103`、`vendor/mrubyc/src/c_object.c:455-455`、`vendor/mrubyc/src/c_object.c:853-853` |
| `MRBC_ALLOC_SLI_BIT_WIDTH` | # define MRBC_ALLOC_SLI_BIT_WIDTH 3	//            ~~~ `vendor/mrubyc/src/alloc.c:84-84` | `vendor/mrubyc/src/alloc.c:83-83` |
| `MRBC_ALLOC_VMID` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:134-134`、`vendor/mrubyc/src/alloc.c:141-141`、`vendor/mrubyc/src/alloc.c:164-164`、`vendor/mrubyc/src/alloc.c:173-173`、`vendor/mrubyc/src/alloc.c:203-203`、`vendor/mrubyc/src/alloc.c:890-890`、`vendor/mrubyc/src/alloc.c:1111-1111`、`vendor/mrubyc/src/alloc.h:77-77`、`vendor/mrubyc/src/alloc.h:107-107`、`vendor/mrubyc/src/c_array.c:119-119`、`vendor/mrubyc/src/c_hash.h:92-92`、`vendor/mrubyc/src/c_proc.c:78-78`、`vendor/mrubyc/src/c_range.c:72-72`、`vendor/mrubyc/src/c_string.c:126-126`、`vendor/mrubyc/src/class.c:370-370`、`vendor/mrubyc/src/global.c:171-171`、`vendor/mrubyc/src/keyvalue.c:177-177`、`vendor/mrubyc/src/value.c:155-155`、`vendor/mrubyc/src/vm.c:386-386` |
| `MRBC_BIG_ENDIAN` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/boxing_nan.h:75-75`、`vendor/mrubyc/src/value.h:610-610`、`vendor/mrubyc/src/value.h:642-642`、`vendor/mrubyc/src/value.h:685-685`、`vendor/mrubyc/src/value.h:727-727`、`vendor/mrubyc/src/value.h:749-749`、`vendor/mrubyc/src/vm_config.h:107-107` |
| `MRBC_BUILTIN_SYMBOL_MAX` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/symbol.c:43-43` |
| `MRBC_CONVERT_CRLF` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/console.c:129-129`、`vendor/mrubyc/src/console.c:174-174` |
| `MRBC_DEBUG` | #define MRBC_DEBUG `vendor/mrubyc/src/vm_config.h:122-122` | `vendor/mrubyc/src/alloc.c:58-58`、`vendor/mrubyc/src/alloc.c:497-497`、`vendor/mrubyc/src/alloc.c:614-614`、`vendor/mrubyc/src/alloc.c:665-665`、`vendor/mrubyc/src/alloc.c:711-711`、`vendor/mrubyc/src/alloc.c:1044-1044`、`vendor/mrubyc/src/c_array.h:109-109`、`vendor/mrubyc/src/c_array.h:114-114`、`vendor/mrubyc/src/c_object.c:381-381`、`vendor/mrubyc/src/c_object.c:606-606`、`vendor/mrubyc/src/c_object.c:849-849`、`vendor/mrubyc/src/class.c:135-135`、`vendor/mrubyc/src/class.c:139-139`、`vendor/mrubyc/src/class.c:186-186`、`vendor/mrubyc/src/class.c:190-190`、`vendor/mrubyc/src/class.h:92-92`、`vendor/mrubyc/src/class.h:128-128`、`vendor/mrubyc/src/class.h:158-158`、`vendor/mrubyc/src/global.c:44-44`、`vendor/mrubyc/src/global.c:183-183`、`vendor/mrubyc/src/keyvalue.c:141-141`、`vendor/mrubyc/src/keyvalue.c:253-253`、`vendor/mrubyc/src/keyvalue.c:310-310`、`vendor/mrubyc/src/keyvalue.h:40-40`、`vendor/mrubyc/src/load.c:136-136`、`vendor/mrubyc/src/load.c:142-142`、`vendor/mrubyc/src/load.c:199-199`、`vendor/mrubyc/src/rrt0.c:210-210`、`vendor/mrubyc/src/rrt0.c:1514-1514`、`vendor/mrubyc/src/rrt0.h:77-77`、`vendor/mrubyc/src/symbol.c:440-440`、`vendor/mrubyc/src/value.h:135-135`、`vendor/mrubyc/src/vm.c:211-211`、`vendor/mrubyc/src/vm.c:289-289`、`vendor/mrubyc/src/vm.h:44-44`、`vendor/mrubyc/src/vm.h:49-49`、`vendor/mrubyc/src/vm.h:56-56`、`vendor/mrubyc/src/vm.h:122-122`、`vendor/mrubyc/src/vm.h:151-151` |
| `MRBC_DEBUG_REGS` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/vm.c:381-381` |
| `MRBC_EXCEPTION_CALL_NEST_LEVEL` | #define MRBC_EXCEPTION_CALL_NEST_LEVEL 8 `vendor/mrubyc/src/error.h:33-33` | `vendor/mrubyc/src/error.h:32-32` |
| `MRBC_INSTANCE_DESTRUCTOR` | # define MRBC_INSTANCE_DESTRUCTOR 1 `vendor/mrubyc/src/class.h:37-37` | `vendor/mrubyc/src/class.c:329-329`、`vendor/mrubyc/src/class.h:36-36`、`vendor/mrubyc/src/class.h:111-111`、`vendor/mrubyc/src/class.h:283-283` |
| `MRBC_INT16` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/boxing_nan.h:15-15`、`vendor/mrubyc/src/value.h:40-40` |
| `MRBC_INT64` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/boxing_nan.h:15-15`、`vendor/mrubyc/src/load.c:170-170`、`vendor/mrubyc/src/load.c:246-246`、`vendor/mrubyc/src/load.c:364-364`、`vendor/mrubyc/src/load.c:424-424`、`vendor/mrubyc/src/value.h:43-43`、`vendor/mrubyc/src/value.h:663-663` |
| `MRBC_KV_SIZE_INCREMENT` | #define MRBC_KV_SIZE_INCREMENT 5 `vendor/mrubyc/src/keyvalue.c:65-65` | `vendor/mrubyc/src/keyvalue.c:64-64` |
| `MRBC_KV_SIZE_INIT` | #define MRBC_KV_SIZE_INIT 2 `vendor/mrubyc/src/keyvalue.c:62-62` | `vendor/mrubyc/src/keyvalue.c:61-61` |
| `MRBC_LITTLE_ENDIAN` | # define MRBC_LITTLE_ENDIAN `vendor/mrubyc/src/vm_config.h:108-108` | `vendor/mrubyc/src/boxing_nan.h:39-39`、`vendor/mrubyc/src/value.h:605-605`、`vendor/mrubyc/src/value.h:637-637`、`vendor/mrubyc/src/value.h:672-672`、`vendor/mrubyc/src/value.h:723-723`、`vendor/mrubyc/src/value.h:738-738`、`vendor/mrubyc/src/vm_config.h:107-107` |
| `MRBC_MIN_MEMORY_BLOCK_SIZE` | #define MRBC_MIN_MEMORY_BLOCK_SIZE sizeof(FREE_BLOCK) `vendor/mrubyc/src/alloc.c:98-98` | `vendor/mrubyc/src/alloc.c:97-97` |
| `MRBC_NAN_BOXING` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/value.h:160-160` |
| `MRBC_NOT_RECOMMEND_TO_USE` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/value.h:255-255` |
| `MRBC_NO_STDIO` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/c_object.c:257-257`、`vendor/mrubyc/src/c_object.c:286-286`、`vendor/mrubyc/src/c_object.c:300-300`、`vendor/mrubyc/src/c_object.c:787-787`、`vendor/mrubyc/src/c_object.c:825-825`、`vendor/mrubyc/src/c_object.c:842-842` |
| `MRBC_NO_TIMER` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/rrt0.c:371-371` |
| `MRBC_OUT_OF_MEMORY` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:571-571` |
| `MRBC_REQUIRE_32BIT_ALIGNMENT` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/value.h:605-605`、`vendor/mrubyc/src/value.h:610-610`、`vendor/mrubyc/src/value.h:614-614`、`vendor/mrubyc/src/value.h:637-637`、`vendor/mrubyc/src/value.h:642-642`、`vendor/mrubyc/src/value.h:646-646` |
| `MRBC_REQUIRE_64BIT_ALIGNMENT` | #define MRBC_REQUIRE_64BIT_ALIGNMENT `vendor/mrubyc/src/vm_config.h:115-115` | `vendor/mrubyc/src/value.h:672-672`、`vendor/mrubyc/src/value.h:685-685`、`vendor/mrubyc/src/value.h:689-689`、`vendor/mrubyc/src/value.h:723-723`、`vendor/mrubyc/src/value.h:727-727`、`vendor/mrubyc/src/value.h:738-738`、`vendor/mrubyc/src/value.h:749-749` |
| `MRBC_SCHEDULER_EXIT` | #define MRBC_SCHEDULER_EXIT 0 `vendor/mrubyc/src/rrt0.c:29-29` | `vendor/mrubyc/src/rrt0.c:28-28`、`vendor/mrubyc/src/rrt0.c:355-355` |
| `MRBC_STRING_SIZE_T` | #define MRBC_STRING_SIZE_T uint16_t `vendor/mrubyc/src/c_string.h:35-35` | `vendor/mrubyc/src/c_string.h:34-34` |
| `MRBC_SUPPORT_OP_EXT` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/opcode.h:29-29`、`vendor/mrubyc/src/vm.c:416-416`、`vendor/mrubyc/src/vm.c:3109-3109`、`vendor/mrubyc/src/vm.c:3162-3162`、`vendor/mrubyc/src/vm.c:3290-3290`、`vendor/mrubyc/src/vm.c:3304-3304` |
| `MRBC_SYMBOL_SEARCH_BTREE` | #define MRBC_SYMBOL_SEARCH_BTREE `vendor/mrubyc/src/symbol.c:33-33` | `vendor/mrubyc/src/symbol.c:32-32`、`vendor/mrubyc/src/symbol.c:52-52`、`vendor/mrubyc/src/symbol.c:143-143`、`vendor/mrubyc/src/symbol.c:177-177` |
| `MRBC_SYMBOL_SEARCH_LINEAR` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/symbol.c:32-32`、`vendor/mrubyc/src/symbol.c:134-134` |
| `MRBC_TASK_NAME_LEN` | #define MRBC_TASK_NAME_LEN 15 `vendor/mrubyc/src/rrt0.h:63-63` | `vendor/mrubyc/src/rrt0.h:62-62` |
| `MRBC_TIMESLICE_TICK_COUNT` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/rrt0.c:34-34`、`vendor/mrubyc/src/rrt0.c:34-34` |
| `MRBC_USE_ALLOC_PROF` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:244-244`、`vendor/mrubyc/src/alloc.c:380-380`、`vendor/mrubyc/src/alloc.c:1010-1010` |
| `MRBC_USE_FLOAT` | #define MRBC_USE_FLOAT 2 `vendor/mrubyc/src/vm_config.h:45-45` | `vendor/mrubyc/src/boxing_no.h:23-23`、`vendor/mrubyc/src/c_math.c:33-33`、`vendor/mrubyc/src/c_numeric.c:21-21`、`vendor/mrubyc/src/c_numeric.c:31-31`、`vendor/mrubyc/src/c_numeric.c:93-93`、`vendor/mrubyc/src/c_numeric.c:282-282`、`vendor/mrubyc/src/c_numeric.c:427-427`、`vendor/mrubyc/src/c_numeric.c:441-441`、`vendor/mrubyc/src/c_object.c:712-712`、`vendor/mrubyc/src/c_object.c:742-742`、`vendor/mrubyc/src/c_object.c:889-889`、`vendor/mrubyc/src/c_object.c:939-939`、`vendor/mrubyc/src/c_string.c:897-897`、`vendor/mrubyc/src/c_string.c:903-903`、`vendor/mrubyc/src/c_string.c:2542-2542`、`vendor/mrubyc/src/console.c:23-23`、`vendor/mrubyc/src/console.c:78-78`、`vendor/mrubyc/src/console.c:528-528`、`vendor/mrubyc/src/console.c:926-926`、`vendor/mrubyc/src/load.c:418-418`、`vendor/mrubyc/src/rrt0.c:878-878`、`vendor/mrubyc/src/value.c:70-70`、`vendor/mrubyc/src/value.c:76-76`、`vendor/mrubyc/src/value.c:117-117`、`vendor/mrubyc/src/value.c:148-148`、`vendor/mrubyc/src/value.h:51-51`、`vendor/mrubyc/src/vm.c:2019-2019`、`vendor/mrubyc/src/vm.c:2061-2061`、`vendor/mrubyc/src/vm.c:2090-2090`、`vendor/mrubyc/src/vm.c:2132-2132`、`vendor/mrubyc/src/vm.c:2159-2159`、`vendor/mrubyc/src/vm.c:2187-2187`、`vendor/mrubyc/src/vm.c:2217-2217`、`vendor/mrubyc/src/vm.c:2274-2274`、`vendor/mrubyc/src/vm_config.h:44-44` |
| `MRBC_USE_MATH` | #define MRBC_USE_MATH 0 `vendor/mrubyc/src/vm_config.h:50-50` | `vendor/mrubyc/src/c_math.c:33-33`、`vendor/mrubyc/src/c_numeric.c:93-93`、`vendor/mrubyc/src/c_numeric.c:462-462`、`vendor/mrubyc/src/c_numeric.c:527-527`、`vendor/mrubyc/src/class.c:637-637`、`vendor/mrubyc/src/vm_config.h:49-49` |
| `MRBC_USE_STRING` | #define MRBC_USE_STRING 1 `vendor/mrubyc/src/vm_config.h:55-55` | `vendor/mrubyc/src/c_array.c:1296-1296`、`vendor/mrubyc/src/c_array.c:1400-1400`、`vendor/mrubyc/src/c_hash.c:670-670`、`vendor/mrubyc/src/c_hash.c:742-742`、`vendor/mrubyc/src/c_numeric.c:294-294`、`vendor/mrubyc/src/c_numeric.c:430-430`、`vendor/mrubyc/src/c_numeric.c:501-501`、`vendor/mrubyc/src/c_numeric.c:534-534`、`vendor/mrubyc/src/c_object.c:649-649`、`vendor/mrubyc/src/c_object.c:840-840`、`vendor/mrubyc/src/c_object.c:900-900`、`vendor/mrubyc/src/c_object.c:943-943`、`vendor/mrubyc/src/c_object.c:952-952`、`vendor/mrubyc/src/c_object.c:973-973`、`vendor/mrubyc/src/c_object.c:982-982`、`vendor/mrubyc/src/c_object.c:1003-1003`、`vendor/mrubyc/src/c_range.c:166-166`、`vendor/mrubyc/src/c_range.c:201-201`、`vendor/mrubyc/src/c_string.c:37-37`、`vendor/mrubyc/src/console.c:412-412`、`vendor/mrubyc/src/console.c:569-569`、`vendor/mrubyc/src/load.c:405-405`、`vendor/mrubyc/src/symbol.c:384-384`、`vendor/mrubyc/src/symbol.c:429-429`、`vendor/mrubyc/src/value.c:44-44`、`vendor/mrubyc/src/value.c:133-133`、`vendor/mrubyc/src/value.c:167-167`、`vendor/mrubyc/src/vm.c:2669-2669`、`vendor/mrubyc/src/vm_config.h:54-54` |
| `MRBC_USE_STRING_UTF8` | #define MRBC_USE_STRING_UTF8 0 `vendor/mrubyc/src/vm_config.h:65-65` | `vendor/mrubyc/src/c_numeric.c:299-299`、`vendor/mrubyc/src/c_numeric.c:336-336`、`vendor/mrubyc/src/c_string.c:327-327`、`vendor/mrubyc/src/c_string.c:373-373`、`vendor/mrubyc/src/c_string.c:858-858`、`vendor/mrubyc/src/c_string.c:931-931`、`vendor/mrubyc/src/c_string.c:1033-1033`、`vendor/mrubyc/src/c_string.c:1045-1045`、`vendor/mrubyc/src/c_string.c:1081-1081`、`vendor/mrubyc/src/c_string.c:1161-1161`、`vendor/mrubyc/src/c_string.c:1328-1328`、`vendor/mrubyc/src/c_string.c:1347-1347`、`vendor/mrubyc/src/c_string.c:1375-1375`、`vendor/mrubyc/src/c_string.c:1428-1428`、`vendor/mrubyc/src/c_string.c:1461-1461`、`vendor/mrubyc/src/c_string.c:1490-1490`、`vendor/mrubyc/src/c_string.c:1595-1595`、`vendor/mrubyc/src/c_string.c:1741-1741`、`vendor/mrubyc/src/c_string.c:1997-1997`、`vendor/mrubyc/src/c_string.c:2161-2161`、`vendor/mrubyc/src/c_string.c:2174-2174`、`vendor/mrubyc/src/c_string.c:2308-2308`、`vendor/mrubyc/src/c_string.c:2546-2546`、`vendor/mrubyc/src/console.c:418-418`、`vendor/mrubyc/src/vm_config.h:64-64` |
| `MRBC_USE_UNICODE_CASE` | #define MRBC_USE_UNICODE_CASE 0 `vendor/mrubyc/src/vm_config.h:76-76` | `vendor/mrubyc/src/c_string.c:327-327`、`vendor/mrubyc/src/c_string.c:489-489`、`vendor/mrubyc/src/vm_config.h:75-75` |
| `NDEBUG` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/vm_config.h:121-121` |
| `OFFSET_BUILTIN_SYMBOL` | #define OFFSET_BUILTIN_SYMBOL 256 `vendor/mrubyc/src/symbol.c:42-42` | `vendor/mrubyc/src/symbol.c:43-43` |
| `UCHAR_MAX` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/symbol.c:36-36` |
| `UINTPTR_MAX` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.c:463-463`、`vendor/mrubyc/src/value.h:501-501` |
| `__EMSCRIPTEN__` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/rrt0.c:141-141`、`vendor/mrubyc/src/rrt0.c:440-440` |
| `__cplusplus` | src 内に定義なし。build/HAL/toolchain または未定義 | `vendor/mrubyc/src/alloc.h:30-30`、`vendor/mrubyc/src/alloc.h:157-157`、`vendor/mrubyc/src/c_array.h:30-30`、`vendor/mrubyc/src/c_array.h:120-120`、`vendor/mrubyc/src/c_hash.h:29-29`、`vendor/mrubyc/src/c_hash.h:151-151`、`vendor/mrubyc/src/c_math.h:18-18`、`vendor/mrubyc/src/c_math.h:27-27`、`vendor/mrubyc/src/c_numeric.h:22-22`、`vendor/mrubyc/src/c_numeric.h:28-28`、`vendor/mrubyc/src/c_object.h:24-24`、`vendor/mrubyc/src/c_object.h:42-42`、`vendor/mrubyc/src/c_proc.h:27-27`、`vendor/mrubyc/src/c_proc.h:70-70`、`vendor/mrubyc/src/c_range.h:28-28`、`vendor/mrubyc/src/c_range.h:104-104`、`vendor/mrubyc/src/c_string.h:30-30`、`vendor/mrubyc/src/c_string.h:139-139`、`vendor/mrubyc/src/class.h:30-30`、`vendor/mrubyc/src/class.h:347-347`、`vendor/mrubyc/src/console.h:30-30`、`vendor/mrubyc/src/console.h:181-181`、`vendor/mrubyc/src/error.h:27-27`、`vendor/mrubyc/src/error.h:77-77`、`vendor/mrubyc/src/global.h:24-24`、`vendor/mrubyc/src/global.h:49-49`、`vendor/mrubyc/src/keyvalue.h:28-28`、`vendor/mrubyc/src/keyvalue.h:165-165`、`vendor/mrubyc/src/load.h:28-28`、`vendor/mrubyc/src/load.h:49-49`、`vendor/mrubyc/src/mrblib.c:2-2`、`vendor/mrubyc/src/opcode.h:22-22`、`vendor/mrubyc/src/opcode.h:246-246`、`vendor/mrubyc/src/rrt0.h:29-29`、`vendor/mrubyc/src/rrt0.h:153-153`、`vendor/mrubyc/src/symbol.h:24-24`、`vendor/mrubyc/src/symbol.h:91-91`、`vendor/mrubyc/src/value.h:28-28`、`vendor/mrubyc/src/value.h:797-797`、`vendor/mrubyc/src/vm.h:33-33`、`vendor/mrubyc/src/vm.h:248-248` |

## 作用と default の読み方

上表は宣言上の default です。#ifdef/defined の switch は -DNAME=0 でも定義済みになります。#if NAME の数値 switch と区別し、最終 compiler command と HAL include の順を保存します。

| symbol / family | 作用・相互制約 |
|---|---|
| MAX_VM_COUNT / MAX_REGS_SIZE / MAX_SYMBOLS_COUNT | 同時 VM ID bitmap、task の既定 register 数、dynamic symbol table。builtin symbol の集合は別の生成 table |
| MRBC_ALLOC_16BIT / 24BIT | block size 管理形式。24BIT が固定 config で有効。16BIT を単に追加して双方を有効にしない |
| ALLOC_FLI_BIT_WIDTH / SLI_BIT_WIDTH / IGNORE_LSBS / MIN_MEMORY_BLOCK_SIZE | free-list 分類と pool header の規模、最小 block と丸め。TLSF の表と sizeof(FREE_BLOCK) に影響 |
| MRBC_ALLOC_LIBC | 内蔵 pool の代わりに malloc/calloc/realloc/free。statistics、VMID、usable_size と profiling の利用可否を再確認 |
| MRBC_ALLOC_VMID | allocation に VM ID を記録し、global の ID clear と VM 終了時の bulk free を有効化 |
| MRBC_USE_ALLOC_PROF | allocation 使用量の high/low 記録。statistics と別の条件 |
| MRBC_NAN_BOXING | 通常 boxing の代わりに NaN boxing。boxing_nan.h は INT16/INT64 に compile error。ABI 全体を揃える |
| MRBC_INT16 / INT64 | mrbc_int_t と loader の literal 対応。既定は int32。任意精度にする flag ではない |
| MRBC_USE_FLOAT / MATH | float precision と数値演算、Math/libm。Math 定数と関数の登録も条件に依存 |
| MRBC_USE_STRING / STRING_UTF8 / UNICODE_CASE | String C 実装、文字単位の対象操作、BMP case map。Unicode case は UTF8 を必要とする |
| MRBC_STRING_SIZE_T | String length の保持型、既定 uint16_t。protocol の長さ検証は別に必要 |
| MRBC_KV_SIZE_INIT / INCREMENT | ivar/global/constant 用 key-value 配列の初期 capacity と増分 |
| MRBC_REQUIRE_32BIT_ALIGNMENT / 64BIT_ALIGNMENT | bytecode の未整列 multi-byte 値の読み方。64BIT が既定で有効 |
| MRBC_BIG_ENDIAN / LITTLE_ENDIAN | byte 列変換・boxing layout。nRF の endianness と一致させる |
| MRBC_NO_TIMER | hardware tick による slice と実行回数での模擬 slice を切替 |
| MRBC_SCHEDULER_EXIT | ready/waiting/suspended が空になれば run を返す。HAL が既定を上書きする場合あり |
| MRBC_TIMESLICE_TICK_COUNT | 正の整数でなければ compile error。時間単位の MRBC_TICK_UNIT は HAL 側で定義 |
| MRBC_TASK_NAME_LEN | TCB 内の name 領域。sizeof(TCB) と RAM に影響 |
| MRBC_SUPPORT_OP_EXT | EXT1/2/3 operand 拡張。未定義時は専用例外 |
| MRBC_EXCEPTION_CALL_NEST_LEVEL | exception に保存する call trace の深さと object サイズ |
| MRBC_INSTANCE_DESTRUCTOR | native instance destructor の field/呼出しを有効化。resource 解放の契約に影響 |
| MRBC_ABORT_BY_EXCEPTION | vm_end の既定 print/decref を hook に変更。hook 自身の停止/cleanup 方針が必要 |
| MRBC_OUT_OF_MEMORY | allocation 失敗 hook。未指定時の既定は print/abort。recoverable Ruby OOM を保証しない |
| MRBC_CONVERT_CRLF | console の LF 出力変換。binary payload の出力経路と区別 |
| MRBC_NO_STDIO | Object の標準出力 method 等を除く。console C API 全体を無効にする保証ではない |
| NDEBUG / MRBC_DEBUG / MRBC_DEBUG_REGS | assert/debug marker・診断 method、終了時 register 使用量表示。release と debug の sizeof を混同しない |
| MRBC_NOT_RECOMMEND_TO_USE | 古い互換 value setter macro を露出。新規 binding の推奨 API ではない |
| MRBC_BUILTIN_SYMBOL_MAX / OFFSET_BUILTIN_SYMBOL | generated builtin symbol の最大値と dynamic 領域の offset。表との境界検査 |
| UCHAR_MAX / UINTPTR_MAX | limits/stdint 由来の platform 判定。symbol index の幅、pointer/alignment の処理 |
| __EMSCRIPTEN__ / __cplusplus | Wasm export/単一 task 実行 API の分岐、C linkage。製品 feature switch ではない |

表中の MRBC_ 接頭辞を省略した family は上の全 symbol 表と同名です。上表の条件を使う行と [memory layout](memory-and-sizing.md)が実装の根拠です。生成 table/Unicode header は compile 前に作る依存です。Makefile の -D、HAL と mrblib の生成条件は [build と samples](tests-and-samples.md)、runtime に提供される method は各 method 索引の構成条件列で確認します。

[調査索引へ戻る](../README.md)
