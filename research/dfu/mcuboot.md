# MCUboot の機能と BM での境界

## 汎用 MCUboot の mode

| mode | 仕組み | RBOS の採否 |
|---|---|---|
| swap-scratch | 二つの slot と scratch を使って交換 | 不採用 |
| swap-move | primary の追加 sector を使って交換 | 不採用 |
| swap-offset | secondary の先頭追加 sector を使って交換 | 不採用 |
| overwrite-only | secondary から primary を上書き | BM の direct upload と同一視しない |
| direct-XIP | 対応 address へ link した二つの image を直接起動 | 不採用 |
| RAM-load | image を SRAM へ展開 | 不採用 |
| firmware loader / single application | main app と recovery 用 loader、または app 一つ | **公式 BM 経路を採用** |

汎用 mode の根拠: `vendor/sdk-mcuboot/docs/design.md:28-60,129-215`。採否は RBOS の判断です。汎用 MCUboot が swap を持つ事実と、NCS BM がその mode を製品向けに統合済みかどうかは別です。

## trailer と test/confirm/revert

汎用 swap は trailer の magic、image_ok、copy_done、swap status 等を用いて更新の進行と状態を記録します。test 起動後に confirm しない場合の revert はその mode の機能です。出典: `vendor/sdk-mcuboot/docs/design.md:427-560`。single-bank の直接上書きに、旧 image へ戻すための保管領域があるという意味ではありません。

公開 API は次の通りです。

```c
int boot_set_pending(int permanent);
int boot_set_pending_multi(int image_index, int permanent);
int boot_set_confirmed(void);
int boot_set_confirmed_multi(int image_index);
```

出典: `vendor/sdk-mcuboot/boot/bootutil/include/bootutil/bootutil_public.h:180-229`。multi API が推奨されていますが、RBOS の通常 single-bank update にこの test/revert 手順を導入する計画はありません。

## stock BM の選択経路

1. BM sysbuild は loader があれば `BOOT_FIRMWARE_LOADER`、なければ `SINGLE_APPLICATION_SLOT` を設定します。出典: `vendor/sdk-nrf-bm/sysbuild/image_configurations/BOOTLOADER_image_default.cmake:8-12`。
2. MCUboot の CMake はその選択で `single_loader.c` を使い、BM firmware loader では `firmware_loader_bm.c` を追加します。出典: `vendor/sdk-mcuboot/boot/zephyr/CMakeLists.txt:158-178`。
3. BM image management の upload は `s0_storage` と `S0_SIZE` に対して処理されます。S1 の address 定義だけから secondary upload と解釈できません。出典: `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/bm_img_mgmt.c:24-43,95-121,160-195`。

`firmware_loader_bm.c` は metadata に基づく SoftDevice/loader の検証、loader 起動判断と installer の処理を持つ BM 固有の接続点です。出典: `vendor/sdk-mcuboot/boot/zephyr/firmware_loader_bm.c:1-120`。汎用 swap を選ぶだけでこの経路と同等になるとは確認していません。

## A/B を採らない理由

- ユーザーが single-bank と `.mrb` 単一コピーを指定した。
- BM 公式 DFU の説明と build/upload 経路が single-bank 前提である。
- 二つの大きい app slot に分けると現行 slot0 の利用可能量が減る。具体的な分割サイズは未設計。
- SoftDevice と metadata は app slot の外であり、app A/B だけでは全体の互換性・復旧を保証できない。

partition の根拠は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:14-47`。Nordic が BM の汎用 A/B をサポートする根拠は今回の固定版資料では得られていません。「MCUboot 自体に A/B がない」とは記録しません。

## imgtool の位置付け

汎用 imgtool の `sign` は `--version`、`--header-size`、`--slot-size`、`--pad`、`--confirm` 等で image と trailer を構成します。出典: `vendor/sdk-mcuboot/docs/imgtool.md:1-120`。RBOS はまず sysbuild が生成する署名済み成果物を使い、手動で他 mode の padding/confirm を加えません。実際の鍵方式、header/TLV、partition 最大長を build output と照合する作業は P5 に残します。

[調査索引へ戻る](../README.md)
