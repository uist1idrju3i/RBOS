# DK の初回準備と通常の書き込み

nRF54L15-DK で RBOS を動かす前の初回準備と、通常の書き込みを分けて記録します。build の手順は [build 再現手順](bm-build.md)にあります。2026-11-09 JST に利用者から報告された macOS での実機結果を、末尾の記録表にまとめました。エージェントが実機を操作して再確認した記録ではありません。

## path の置き換えと build 環境

コマンドの `<...>` は手元の値に置き換えます。そのまま入力する文字列ではありません。

| 表記 | 置き換えるもの |
|---|---|
| `<workspace>` | `.west/`、`nrf-bm/`、`zephyr/` を含む BM v2.0.1 の workspace root |
| `<RBOS>` | RBOS の checkout root。BM workspace とは別の directory |
| `<build>` | sysbuild の出力 directory。RBOS と workspace の外に置く |
| `<SN>` | 手元で選ぶ DK の識別値。文書、Issue、ログの共有には記録しない |

v3.3.0 の toolchain 環境を読み込み、必ず BM workspace の中から build します。`west topdir` が意図した workspace を返すことを確認してください。

```sh
eval "$(nrfutil sdk-manager toolchain env --ncs-version v3.3.0 --as-script sh)"
cd "<workspace>"
west topdir
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  "<RBOS>/firmware" --sysbuild -d "<build>" -p always
```

workspace の外から `west build` したところ、別に導入された NCS v3.4.2 が使われ、`No board named 'bm_nrf54l15dk'` で失敗したと報告されました。toolchain の環境だけでなく、west が参照する workspace も確認します。

## 初回準備が要る理由

RBOS の build は `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU=y` です。MCUboot は KMU に書いた公開鍵で app を検証するので、KMU に鍵がない DK では起動しません（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:65-80`）。build は公開鍵を書くための `keyfile.json` を build directory に作ります。鍵の名前は `BL_PUBKEY` です（`vendor/sdk-nrf-bm/cmake/sysbuild/generate_default_keyfile.cmake:11-19`）。

KMU に一度鍵を書くと、別の鍵へ替えるには SoC 全体の erase が必要です（[KMU provisioning の文書](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/doc/nrf/app_dev/device_guides/kmu_guides/kmu_provisioning_overview.rst#L147-L157)）。debug は SDK の開発用鍵、release は利用者の鍵で署名します。そのため、debug 用に準備した DK で release の image を起動するには erase と再準備が要ります。debug 用と release 用で DK を分けると、この erase を避けられます。

## 初回準備の二つの方法

| 方法 | コマンド | 消えるもの | 状態 |
|---|---|---|---|
| SDK の標準 | `west flash -d <build> --erase` | SoC 全体 | 下の nrfutil による標準相当の操作で起動成功。`west flash` 自体は未使用 |
| erase なしの候補 | `nrfutil device x-provision-keys --key-file <build>/keyfile.json` の後に `west flash -d <build>` | なし（KMU が空の場合） | ソースから導いた候補。未試験 |

標準の方法では、runner が書き込みの後に `keyfile.json` を KMU へ書きます。この動作は `--erase` か `--recover` を付けたときだけです（workspace の `zephyr/scripts/west_commands/runners/nrf_common.py:404-409`）。

### CI artifact と nrfutil で行う標準相当の準備

**`ERASE_ALL` は SoC 全体を消去します。初回準備や鍵の交換時だけ、人が明示して実行してください。通常の更新には使いません。必要なデータは先に退避します。**

CI の debug artifact から取り出した `production.hex` と、ローカルの debug build が生成した `keyfile.json` を用意します。CI artifact に `keyfile.json` は含まれません。今回の file は SDK の MCUboot 開発用鍵 `root-ed25519.pem` の公開鍵で、CI debug image と同じ開発用鍵に対応します。秘密鍵ではありませんが、生成物はリポジトリへ追加しません。release image に開発用鍵の keyfile を流用しないでください。

両 file のある directory で、同じ DK を指定して実行する例です。

```sh
nrfutil device program --serial-number "<SN>" --firmware production.hex \
  --options chip_erase_mode=ERASE_ALL
nrfutil device x-provision-keys --serial-number "<SN>" --key-file keyfile.json
nrfutil device reset --serial-number "<SN>"
```

利用者は program、公開鍵の provision、reset の成功と app の起動を報告しました。これは `west flash --erase` の program（`ERASE_ALL`）→ `x-provision-keys` と同じ順序です（workspace の `zephyr/scripts/west_commands/runners/nrf_common.py:367-374,402-409`）。runner を経由した試験とは区別します。

### erase なしの初回準備（未確認）

erase なしの候補は、runner が内部で使う操作と同じ `x-provision-keys` を単独で実行します。`west ncs-provision upload` も同じ nRF Util の命令を組み立てます。そこには erase の指定がありません（[ncs_provision.py](https://github.com/nrfconnect/sdk-nrf/blob/ba167d9f3db4abbdc9b67887ca3ea66c64f2d956/scripts/west_commands/ncs_provision.py#L109-L123)）。鍵の PEM から直接書く場合の例は次のとおりです。debug の鍵は MCUboot module の `root-ed25519.pem` です。

```sh
west ncs-provision upload --keyname BL_PUBKEY -s nrf54l15 -k <signing-key.pem>
west flash -d <build>
```

この候補は KMU が空の DK でだけ使えます。出荷時の DK の KMU が空か、出荷時の demo firmware の残りが RBOS の保存領域に影響しないかは、実機で確かめる必要があります。

今回、全体 erase なしの program を行った時点では KMU は準備済みでした。空の KMU への初回 provision を試した証拠にはなりません。

## 通常の書き込み

MCUboot と鍵を変えない更新の基本コマンドは `west flash -d <build>` です。nRF54L の nrfutil runner は erase を既定にしません（`nrf_common.py:367-374`）。script、CI、手順書の通常経路には `--erase`、`--recover`、`nrfutil device erase` を入れません。

利用者が確認した通常更新は、nrfutil で変更範囲の erase を許す方法です。鍵を再 provision せず、v0.1.1 の `production.hex` を次の設定で書き、`Image version: v0.1.1` と `RBOS 0.1.1+0` を確認しました。

```sh
nrfutil device program --serial-number "<SN>" --firmware production.hex \
  --options chip_erase_mode=ERASE_RANGES_TOUCHED_BY_FIRMWARE
nrfutil device reset --serial-number "<SN>"
```

これは全体 erase をしない更新の確認です。`ERASE_NONE` での書き込みや、保存データの前後比較は未確認です。

`SB_CONFIG_BM_BOOT_BOOTCONF_LOCK_WRITES` は既定で無効で、RBOS も有効にしていません。有効にすると boot partition への書き込みに erase all が必要になります（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/memory_partitioning.rst:55-67`）。採用は P5 で判断します。

## macOS で console が出ない場合

利用者の環境では、最初は J-Link USB に BULK / MSD / HID だけが見え、`serialPorts:false` で serial port がありませんでした。次の二段階で出力を得ています。

1. `JLinkExe` を起動して `vcom enable` を実行し、USB を抜き差しする。これで port が現れましたが、この時点では出力がありませんでした。
2. nRF Connect for Desktop の Board Configurator で **VCOM0 と VCOM1** を有効にする。`/dev/cu.usbmodem*` の port を 115200 baud で開くと log が出ました。

USB の VCOM 有効化と Board Configurator の設定を分けて確認します。port 名の個体を識別する部分は共有しません。得られた v0.1.0 の log は次のとおりです。

```text
*** Booting MCUboot v2.3.0-dev-fce4dac2e629 ***
*** Using nRF Connect SDK Bare Metal v2.0.1-51484143c091 ***
I: Starting bootloader
I: Booting main application
I: Bootloader chainload address offset: 0xa000
I: Image version: v0.1.0
I: Jumping to the first image slot
*** Booting My Application v0.1.0-6d09bd5068f2 ***
*** Using nRF Connect SDK Bare Metal v2.0.1-51484143c091 ***
[00:00:00.000,160] <inf> nrf_sdh: SoftDevice forward address: 0x163800
[00:00:00.016,503] <inf> rbos: RBOS 0.1.0+0
```

期待する RBOS の log は `RBOS 0.1.0+0` です。`RBOS v0.1.0...` ではありません。起動 banner の application 名は現在 `My Application` です。

## macOS で P1 stress log を採る

capture は reset 前に開始します。ほかの serial monitor は閉じてください。`ls /dev/cu.usbmodem*` で候補を調べ、port を一つ明示して選びます。DK には二つの VCOM port があります。P0/P1 で console に使った方、または別の terminal から `nrfutil device reset --serial-number "<SN>"` を実行すると `*** Booting My Application ... ***` が出る方です。識別値や port 名を共有 log に書き足しません。

次の一行を RBOS checkout root で実行します。`<PORT>` を選んだ port の末尾に置き換えます。必要なのは macOS の zsh、stty、Perl、tee と Python 3.9 以上です。追加 package や GNU timeout は使いません。

```zsh
port='/dev/cu.usbmodem<PORT>'; duration=1860; log="dk-stress-$(date +%Y%m%d-%H%M%S).log"; (set -o pipefail; (stty 115200 raw -echo clocal <&3 && perl -e '$|=1; $SIG{ALRM}=sub { exit 0 }; alarm shift; while (1) { my $n=sysread(STDIN,my $buf,4096); die "VCOM read failed\n" unless defined $n; last unless $n; print $buf or die "VCOM write failed\n"; }' "$duration" <&3) 3<"$port" | tee "$log") && python3 tools/bm-build/check-dk-log.py "$log" --profile stress --min-duration 1800 --require-connected 1800
```

開いた fd 3 に stty を適用し、同じ fd を Perl が読みます。alarm で1860秒後に読み取りを終え、表示と保存の pipeline が成功した場合だけ checker を実行します。capture 開始後、別の terminal で reset し、phone から BLE 接続を保ってください。stats の先頭から末尾までと、接続境界をまたがない窓の合計の双方に1800秒を要求します。接続準備が長引いた場合は `duration` を延ばして採り直します。これは Linux の PTY で設定・保存・終了まで検査した手順で、macOS 固有の port と zsh での実行は未確認です。

### log の判定

checker は [check-dk-log.py](../../tools/bm-build/check-dk-log.py) です。raw log を再表示せず、版・SHA・統計・BLE event と問題の行番号を出します。`--json` なら機械処理用の出力です。終了値は PASS=0、FAIL=1、引数・入力 file のエラー=2 です。

```sh
python3 tools/bm-build/check-dk-log.py capture.log --profile selftest
python3 tools/bm-build/check-dk-log.py capture.log --profile oom --json
```

- selftest/stress は9個の PASS、fatal/assert 不在、stats を要求します。`catchups>0` は失敗です。stats 間隔は Kconfig 既定の10秒で、`--stats-interval` で変更できます。1.5倍を超える欠落を失敗とし、初回を除く ticks は実 timestamp 差×1000 に対して±1%で判定します。
- 最初の stats は窓の開始が不明なので jitter 比較と rate 計算から除きます。connect/disconnect に触れる窓も jitter 比較から外します。BLE event 間の接続時間と、完全接続窓の合計は別の値です。`--require-connected` は後者を使います。
- `pool` は保守時に標本化した累積 peak、main/isr は paint scan による使用量の推定、`drain_us` は区間最大の経過 µs です。drain のない旧 log も受け付け、未計測と表示します。idle/service の rate は累積 counter の差を timestamp 差で割った値で、IRQ 数や CPU 使用率ではありません。
- stress は両 spinner の開始と進捗を要求します。進捗行には timestamp がないため、直前の timestamp を代用し、間隔の2.1倍（既定21秒）を超えたら失敗とします。stats 一区間程度のずれがあり、最終 timestamp 後の経過時間は分かりません。厳密な出力間隔の証明ではなく、`--spinner-interval` で基準を変更できます。
- oom は `OOM: start` の後の `RBOS fatal: Ruby pool exhausted` を要求します。短時間で停止して stats がない場合は未計測とし、fatal 前の stats があれば pool 等を集計します。複数回の boot は一回の試験として合算しません。

## 2026-11-09 JST の実機結果（利用者報告）

対象は macOS に接続した PCA10156 revision 1.0.0、認証表示 `220-JP8930` の nRF54L15-DK です。[ハードウェア調査](../hardware/nrf54l15-dk.md)と照合しました。背面印字は LED0 P2.09、BUTTON0 P1.13、TXD1 P1.04 で、SDK の board-config と一致したとの報告です。これは観察した表示・pin の照合であり、任意の無線設定の認証適合を保証しません。

### 使用した image

CI debug は [run 42620432714](https://github.com/uist1idrju3i/RBOS/actions/runs/42620432714) の artifact `firmware-evidence-debug-6d09bd5068f26c65258d9ed3da3d66ac6c84670a` です。

| image | 出所・変更範囲 | SHA-256 |
|---|---|---|
| v0.1.0 `production.hex` | 上記 CI debug artifact、commit `6d09bd5068f26c65258d9ed3da3d66ac6c84670a` | `1b751a801678415286890f5f8789a1006d97e3a9ef0336f76a5620d0bf0e5415` |
| v0.1.1 `production.hex` | Devin のローカル build。基準は commit `6d09bd5`、`firmware/VERSION` の `PATCHLEVEL=1` だけが未 commit の変更。開発用鍵で署名 | `3c483c613789fabd134b3da1cd8a45603cdc5bbd633e4e9b050edaf344cda695` |
| v0.1.1 app signed bin | 同じローカル build の署名済み app | `1010195e29ef16cf7cc40ce67593a77ac9b90fab20f198c05ea251ae5cdf386e` |
| recovery sample `production.hex` | Devin のローカル build。RBOS の基準 commit `6d09bd5` に対応する BM workspace の `mcuboot_recovery_entry` | `df46da199650b74c34ca10ff80255835be212bc852c78c88e541582b9de59c36` |

ローカル build の hash は利用者が試した image の識別情報です。リポジトリにそろった入力からの再現を示す証拠としては扱いません。v0.1.1 は試験用の写しであり、この変更で VERSION を更新したり、release を公開したりしたものではありません。

### 記録表

| 項目 | 手順 | 期待 | 結果 |
|---|---|---|---|
| DK の revision・認証表示・pin | 本体と背面の印字を読む | 調査資料・board-config と一致 | PASS。上記 revision、認証表示、三つの pin を照合 |
| erase なしの初回準備 | 空の KMU に provision して program | MCUboot が app を起動 | 未確認。今回の全体 erase なしの program 時には KMU が準備済み |
| SDK 標準相当の初回準備 | `ERASE_ALL` で program → `x-provision-keys` → reset | MCUboot が app を起動 | PASS。各操作が成功。`west flash --erase` 自体は未使用 |
| LED | CI debug を書き込む | LED0（P2.09）が点灯 | PASS |
| console | VCOM の設定後、UARTE20（TX P1.04）を 115200 baud で開く | `RBOS 0.1.0+0` | PASS。上記 log |
| GPIO による loader 入口 | BUTTON0（P1.13）を押して RESET | firmware loader が BLE で広告 | PASS。`I: Booting firmware loader`、offset `0x153000`、`Advertising as nRF_BM_MCUmgr` を確認し、phone app でも検出。RESET で RBOS に戻る |
| 通常の書き込み | v0.1.1 を `ERASE_RANGES_TOUCHED_BY_FIRMWARE` で program | 鍵の再準備なしで新しい版が起動 | PASS。`Image version: v0.1.1` と `RBOS 0.1.1+0`。保存データの維持は未確認 |
| BLE DFU（P0 外） | nRF Connect iOS から `nRF_BM_MCUmgr` 経由で v0.1.1 app signed bin を upload | 転送完了と更新 image の起動 | 一部。app は Success を表示。ただし導入済みと同じ版なので、DFU した image の起動は識別できず未確認 |
| recovery sample の起動・広告 | 全体 erase なしで sample を書き込む | sample が起動して BLE で広告 | PASS。起動 log と `Advertising as nRF_BM_Entry` を確認 |
| recovery sample から loader へ切り替え | nRF Connect Device Manager Android で Switch to Firmware Loader Mode を ON（Boot Mode=1）にして Send Reset Command | firmware loader に入る | PASS。`nRF_BM_Entry` に接続し、Adv. Name を `FL_12345` に指定。reset 後に MCUboot、`BLE MCUmgr sample started`、`Advertising as FL_12345` を確認（下記追記） |
| RBOS への復帰 | v0.1.1 RBOS を再度書き込む | RBOS が起動 | PASS。`RBOS 0.1.1+0` に復帰 |

### recovery sample から loader への切り替え（2026-11-09 JST 追記）

利用者は nRF Connect Device Manager **Android** で `nRF_BM_Entry` に接続し、Switch to Firmware Loader Mode を ON（Boot Mode=1）、Adv. Name を `FL_12345` にして reset を送りました。報告された log の順序は次のとおりです。

```text
I: Bluetooth name set to: FL_12345
I: Peer disconnected
*** Booting MCUboot v2.3.0-dev-fce4dac2e629 ***
I: BLE MCUmgr sample started
I: Advertising as FL_12345
```

この recovery sample build の MCUboot は `I: Booting firmware loader` 行を出しません。MCUboot の再起動後に `BLE MCUmgr sample started` が出て、指定した名前で広告したことを loader への切り替え成功の証拠とします。`FL_12345` は指定した広告名で、DK の識別番号ではありません。

この操作には Android app を使ってください。利用者の環境では iOS の nRF Connect Device Manager が Send Reset Command の直後に crash しました。利用者の画面録画による報告では、広告名 `FL_232659` の設定までは済みましたが reset は起きていません。iOS app のバージョンは未記録で、ほかの環境やバージョンでも起きるとは判断しません。これは前記の nRF Connect iOS による DFU upload の結果とは別の操作です。

console の pin は `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/include/board-config.h:55-63` にあります。P0 の判定と P1 への提案は [振り返り](retrospective-P0.md)に記録します。

## P1 の通常更新の実機報告

利用者は [CI run 42714459863](https://github.com/uist1idrju3i/RBOS/actions/runs/42714459863) の main `ff4c23e` の debug artifact を SHA256SUMS 全件照合後に書き込みました。P0 と同じ `ERASE_RANGES_TOUCHED_BY_FIRMWARE` の program と reset が成功し、全体 erase・鍵の再 provision は行っていません。エージェントは実機を操作していません。

全自己検査 PASS、BLE 接続・切断と再広告、接続中の区間統計を確認しました。artifact 名・production.hex の SHA-256・原文 log・統計の意味は [P1 の振り返り](retrospective-P1.md)に保存しています。ERASE_NONE 更新、保存データの維持、release image の実機起動、二度目の接続、slow 広告180秒後の停止は未確認です。

[調査索引へ戻る](../README.md)
