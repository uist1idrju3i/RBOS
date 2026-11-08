# SemVer と firmware image の版管理

本書は SemVer 2.0.0、固定 SDK の実装、parser の実行結果、利用者が承認した RBOS 方針を区別して記録します。firmware build・署名・実機 DFU・HW counter の運用を検証した文書ではありません。

## SemVer 2.0.0 の規則

出典は [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)。public API は 0.y.z の段階からコードまたは文書で宣言し、正確・包括的に定義します。0.y.z は初期開発で API は安定と見なされず、何でも変更できます。0.x の増分の決め方は RBOS の追加規則です。

1.0.0 で public API を確立し、それ以降は互換 bug fix が PATCH、互換追加・非推奨化が MINOR、非互換変更が MAJOR。MINOR を上げたら PATCH、MAJOR を上げたら MINOR/PATCH を 0 に戻します。公開済みの版の内容を書き換えず、変更は新しい版で配布します。

| 要素 | 構文と順序 |
|---|---|
| 通常版 | X.Y.Z。非負整数、先頭ゼロなし。各要素を数値比較 |
| pre-release | `-rc.1` 等。dot 区切りの空でない ASCII 英数字・hyphen。数値識別子は先頭ゼロ不可。同じ通常版より低位 |
| pre-release 同士 | 左から比較。数値同士は数値順、非数値は ASCII 順、数値は非数値より低位。同じ prefix なら識別子が多い方が高位 |
| build metadata | `+build.7` 等。空でない同じ文字集合の識別子。数値の先頭ゼロ可。優先順位に影響しない |

`v1.2.3` は git tag の名前にできても、SemVer 本体は `1.2.3` です。SemVer は firmware の署名、rollback 防止、脆弱性対策の代わりにはなりません。

## 固定 SDK と application VERSION

`vendor/sdk-nrf-bm/west.yml:15-26` は NCS v3.3.0 と MCUboot の import を指定します。[NCS manifest](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/west.yml#L66-L68)と [MCUboot entry](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/west.yml#L128-L131)を照合した checkout の版は以下です。

| component | 固定 SHA |
|---|---|
| sdk-nrf | `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956` |
| sdk-zephyr | `fd9204a02d52630660ce8d729945a4dd743feabf` |
| sdk-mcuboot | `fce4dac2e6295cf98bd02a85f7c4254f6102106d` |

Zephyr は application root の VERSION を読みます。以下は形式の説明で、現在の RBOS にこの application を追加したわけではありません。

```text
VERSION_MAJOR = 1
VERSION_MINOR = 2
PATCHLEVEL = 3
VERSION_TWEAK = 4
EXTRAVERSION = rc.1
```

数値4項目はそれぞれ 0–255。EXTRAVERSION は lowercase a-z、数字、dot、hyphen で、SemVer 全体の構文検証器ではありません。例では APP_VERSION_STRING が `1.2.3-rc.1`、APP_VERSION_EXTENDED_STRING が `1.2.3-rc.1+4`、APP_VERSION_TWEAK_STRING が `1.2.3+4` になります。出典は [VERSION parser と文字列生成](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/cmake/modules/version.cmake#L38-L104)。

[生成処理](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/CMakeLists.txt#L738-L759)の出力は `include/generated/zephyr/app_version.h`。macro は APPVERSION、APP_VERSION_NUMBER、APP_VERSION_MAJOR、APP_VERSION_MINOR、APP_PATCHLEVEL、APP_TWEAK、上記3種類の String、APP_BUILD_VERSION です。**固定 template は APP_TWEAK** を定義します。[template](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/version.h.in#L12-L22)と [文書の APP_VERSION_TWEAK 表記](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/doc/build/version/index.rst#L168-L174)には差があります。

## 署名する image の版

BM は `vendor/sdk-nrf-bm/sysbuild/image_configurations/MAIN_image_default.cmake:8-25` で BOOTLOADER_MCUBOOT と updater / single-app mode を設定します。Zephyr の [signing dispatch](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/CMakeLists.txt#L2182-L2200)は sysbuild 指定、target property、既定 MCUboot script の順に選択します。

CONFIG_MCUBOOT_IMGTOOL_SIGN_VERSION の default は VERSION があれば APP_VERSION_TWEAK_STRING、なければ `0.0.0+0`。[Kconfig](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/modules/Kconfig.mcuboot#L110-L117)と [Zephyr signer](https://github.com/nrfconnect/sdk-zephyr/blob/fd9204a02d52630660ce8d729945a4dd743feabf/cmake/mcuboot.cmake#L103-L106)で `imgtool sign --version` へ渡されます。NCS の [firmware-loader signer](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/cmake/sysbuild/image_signing_firmware_loader.cmake#L69-L79)と BM installer（`vendor/sdk-nrf-bm/cmake/sysbuild/image_signing_installer.cmake:65`）も同じ設定を使います。実際に選ばれる script と値は、将来の RBOS build の出力で確認する必要があります。

MCUboot の [image_version](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/bootutil/include/bootutil/image.h#L150-L155)は major u8、minor u8、revision u16、build u32 です。ただし VERSION を入口とする RBOS の数値4項目は各 0–255 に制限します。pre-release 文字列を格納する field はありません。SoftDevice の署名は別の CONFIG_SOFTDEVICE_VERSION です（`vendor/sdk-nrf-bm/cmake/image_signing_softdevice.cmake:49`）。

### Parser の実行記録

2026-11-08 UTC、Python 3.12.16 で上記 MCUboot SHA の [scripts/imgtool/version.py](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/scripts/imgtool/version.py#L19-L49)だけを実行しました。入力・出力は次のとおり。SDK workspace で再実行するコマンドです。

```sh
python3 --version
MCUBOOT_SOURCE="$(west list mcuboot -f '{abspath}')" python3 - <<'PY'
import os
import runpy
import subprocess
from pathlib import Path

root = Path(os.environ["MCUBOOT_SOURCE"])
print(subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                              text=True).strip())
decode = runpy.run_path(str(root / "scripts/imgtool/version.py"))["decode_version"]
for value in ("1.2.3+7", "1.2.3-rc.1", "1.2.3+sha.abc"):
    try:
        print(value, "->", decode(value))
    except ValueError as error:
        print(value, "-> ValueError:", error)
PY
```

```text
Python 3.12.16
fce4dac2e6295cf98bd02a85f7c4254f6102106d
1.2.3+7 -> SemiSemVersion(major=1, minor=2, revision=3, build=7)
1.2.3-rc.1 -> ValueError: Invalid version number, should be maj.min.rev+build with later parts optional
1.2.3+sha.abc -> ValueError: Invalid version number, should be maj.min.rev+build with later parts optional
```

これは parser の受理形式の試験です。header への pack、署名、実機への書込みの試験ではありません。

## Single-bank と downgrade の境界

BM の mode 選択は `vendor/sdk-nrf-bm/sysbuild/image_configurations/BOOTLOADER_image_default.cmake:8-12`。MCUboot の [CMake dispatch](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/zephyr/CMakeLists.txt#L159-L180)は、その設定により single_loader.c または firmware_loader_bm.c を選びます。通常の swap loader を前提にした説明を流用しません。

| 経路 | 確認した挙動と限界 |
|---|---|
| BM loader | [validate_image / boot_go](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/zephyr/firmware_loader_bm.c#L60-L80)から署名・hash を検査して起動先を選択。関数全体に SW version の新旧比較はない |
| MCUboot 設定 | [Kconfig](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/zephyr/Kconfig#L1144-L1185)に SW/HW downgrade prevention、security counter、build 比較の選択あり。存在だけで BM での有効性を保証しない |
| HW validation | [共通 image_validate.c](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/boot/bootutil/src/image_validate.c#L590-L649)に、HW macro 有効時の保存 counter との比較あり。同値を許す。BM の counter 初期化・更新・複数 image の割当てと最終設定は未検証 |
| BM MCUmgr upload | request の upgrade は既定 false（`vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/img_mgmt.c:225-244`）。true のときだけ同じか古い版を拒否。比較は major/minor/revision のみで build を無視（同 directory の `zephyr_img_mgmt.c:35-55,141-159`） |
| BM image list | header の ih_ver を読む `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/img_mgmt.c:93-115` と、version を返す `vendor/sdk-nrf-bm/subsys/mgmt/mcumgr/grp/img_mgmt/src/img_mgmt_state.c:62-95,167-192` がある。pre-release の全文は復元できない |

したがって TWEAK を増やすだけでは、同じ X.Y.Z の rc→正式版を upgrade=true で通せません。request の指定に依存する比較を強制 rollback protection と見なさず、署名・認可・security counter を分けて検証します。[single-bank DFU](../dfu/single-bank-dfu.md)の運用検証は別途必要です。

## RBOS の版と承認済み判断

mruby/c は RUBY_VERSION=`4.0`、MRUBY_VERSION=`4.0.0`、MRUBYC_VERSION=`4.0.0` を Ruby に定義します（`vendor/mrubyc/mrblib/global.rb:11-14`）。これは依存の版で、RBOS の版ではありません。現在の `src/rbos/bindings.c:3-6` は空。mrbc_define_module と mrbc_set_class_const（`vendor/mrubyc/src/class.h:236-237`、`vendor/mrubyc/src/global.c:75-82`）を使う RBOS::VERSION は追加可能と判断しますが、実装・実行試験は未実施です。

以下は利用者の承認済み方針です。仕様の根拠と詳細は [判断の記録](../architecture/decisions.md)にも残します。

| 決定 | RBOS の方針 |
|---|---|
| public API | Ruby class/method の契約、対応する Ruby/mrbc/mruby/c、board 設定規約。C backend は内部。DFU/MCUmgr は実装した時点で追加 |
| 0.x | 非互換変更は 0.MINOR、互換追加・修正は 0.x.PATCH。SemVer 本体とは別の RBOS 規則 |
| 正本と image | application 追加時に VERSION を置き、CHANGELOG と対応させる。pre-release は EXTRAVERSION、image は X.Y.Z+TWEAK。同じ X.Y.Z 内で TWEAK を単調増加し、4項目の 0–255 を検査 |
| CHANGELOG | Keep a Changelog 1.1.0、日本語。利用者に影響する変更は同じ PR の Unreleased に記録 |
| 公開権限 | tag 作成・release 公開は管理者のみ。agent は行わない。v* tag の管理者 bypass 設定は管理者の作業 |
| 最初の版 | 今は採番しない。最初の build 可能な firmware ができた時点で 0.1.0。現時点で release 履歴を作らない |

非推奨は文書と CHANGELOG に明記し、少なくとも1回の MINOR release による猶予を経てから削除する手順です。TWEAK は wrap・再利用せず、上限到達時は次の版と更新経路を決め直します。bytecode は [build 時埋込み](../dfu/embedded-bytecode.md)で、独立配布 ABI を保証する決定ではありません。

## Tag ruleset と公開手順の前提

2026-11-08 UTC に `gh api repos/uist1idrju3i/RBOS/rulesets` と `gh api repos/uist1idrju3i/RBOS/rulesets/26779547` を読み取りました。[release ruleset](https://github.com/uist1idrju3i/RBOS/rules/26779547)は可変の運用状態で、固定 source の事実とは区別します。

```json
{"name":"release","target":"tag","enforcement":"active",
 "conditions":{"ref_name":{"exclude":[],"include":["~ALL"]}},
 "rules":[{"type":"deletion"},{"type":"non_fast_forward"},
          {"type":"update"},{"type":"creation"}],
 "current_user_can_bypass":"never"}
```

取得時点では全 tag の作成・更新・削除が制限され、現在の実行主体は bypass できません。管理者に v* の作成を許可する承認方針と、設定が変更済みであることは別です。agent は ruleset を変更せず、tag/release を作成しません。初回公開前に管理者が設定を確認します。

[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)は人向けに重要な変更を整理する慣習です。最新版を先頭にし、日付・版・比較へのリンク、Unreleased、Added/Changed/Deprecated/Removed/Fixed/Security を使います。commit log の転記ではありません。将来の GitHub Releases は CHANGELOG に対応する説明、artifact、hash を管理者が公開する候補で、今回公開したものではありません。

[調査索引へ戻る](../README.md)
