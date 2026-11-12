# BM firmware の build 再現手順

[段階計画](porting-plan.md)に沿って実装した firmware を、別の環境で同じ固定版から build するための手順です。P0 の初回は2026-11-09 に RBOS commit `6c4740c8145c0c5f7f86fae6a04433b51336cd36` と当時の PR の変更を Linux x86_64 で build しました。この build 作業では実機を試していません。別途、利用者から報告された 2026-11-09 JST の [DK の実機結果](dk-provisioning.md)を記録しました。

現在は P1 の mruby/c、BM HAL、BLE、組込み Ruby task まで実装済みです。debug/release build と Wasm runner で検査し、利用者が `ff4c23e` の CI debug image で DK 自己検査・BLE 接続中の統計を採取しました。[P1 の振り返り](retrospective-P1.md)に artifact の識別情報、観測値の限界と未確認項目をまとめています。以下の P0 の結果・hash は履歴として残します。

## 構成

firmware は RBOS の `firmware/` に置きます。`src/rbos/` の共有 binding は Nordic の header を含まないため、BM の Zephyr application とは分けました。

| ファイル | 役割 |
|---|---|
| `firmware/CMakeLists.txt` | sysbuild 以外、他 board target、firmware loader 以外の MCUboot mode を拒否 |
| `firmware/Kconfig` | log level、VM 数、pool、保守・統計周期、VM debug の設定 |
| `firmware/Kconfig.sysbuild` | release を示す `SB_CONFIG_RBOS_RELEASE` |
| `firmware/sysbuild.cmake` | release の署名鍵の検査 |
| `firmware/common.conf` | debug / release 共通の app 設定 |
| `firmware/prj.conf` / `prj_release.conf` | 最適化設定と release の VM 専用 NDEBUG。共通設定は CMake で追加 |
| `firmware/sysbuild.conf` / `sysbuild_release.conf` | BLE MCUmgr loader、GPIO 入口、release の印。retention 入口は board の既定で有効（`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:73-74`） |
| `firmware/boards/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.overlay` | board overlay の置き場。現在は model 名だけを変更 |
| `firmware/VERSION` | 0.1.0、TWEAK 0。署名 image は `0.1.0+0` |
| `firmware/cmake/mrubyc.cmake` | host mrbc、VM のコピーと生成物、const task 配列・固定順 table を結合 |
| `firmware/src/main.c` | 版の log、LED0、stack paint、BLE、VM/pool/binding/task の初期化後に mrbc_run |
| `firmware/src/hal/hal.h` / `hal.c` | BM timer、IRQ、console、idle、abort と区間 tick 統計 |
| `firmware/src/runtime.h` / `runtime.c` | 保守処理、RBOSSystem.service の caller 検査、stack/pool 統計 |
| `firmware/src/ble.c` | 接続可能な RBOS 広告と接続・切断 log |
| `firmware/src/embedded.h` | build directory に生成する task table の宣言 |
| `firmware/ruby/system.rb` / `selftest/*.rb` | 常設 system task と三つの移植可能な自己検査 task |
| `src/rbos/` / `include/rbos/` | Nordic/Zephyr header を含まない共有 binding と backend 契約 |
| `tools/bm-build/` | module SHA の照合と成果物の収集 |
| `tools/bm-build/check-bytecode.py` / `tests/check-changes/test_bytecode.py` | 生成 C 配列の header/size 検査と正常・拒否例 |

対象 board は `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot` だけです。S145 と central は使いません。

## 版の固定

| 対象 | 版 | 確認方法 |
|---|---|---|
| nRF Connect SDK Bare Metal | v2.0.1 / `51484143c09199e19bccc16fa3b437f7a502a72b` | `vendor/sdk-nrf-bm` の submodule と同じ commit |
| NCS（sdk-nrf） | v3.3.0 / `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956` | `vendor/sdk-nrf-bm/west.yml:14-17` の import |
| toolchain bundle | `911f4c5c26`（NCS v3.3.0 用） | `nrfutil sdk-manager` 1.17.0 で導入 |
| compiler | `arm-zephyr-eabi-gcc (Zephyr SDK 0.17.0) 12.2.0` | toolchain bundle に同梱 |
| host tool | west 1.5.0、CMake 4.2.1、Ninja 1.13.2、Python 3.12.4、nrfutil 8.1.1 | toolchain の環境で各 `--version` |

全 module の名前・path・SHA は [modules.txt](../../tools/bm-build/modules.txt) に固定しました。workspace がこの表と一致し、各 project に未 commit の変更がないことを `tools/bm-build/check-workspace.sh` で検査します。BM の manifest は sdk-nrf を tag で参照し、sdk-nrf は各 module を SHA または tag で参照します。tag の付け替えに備え、build の記録には `west manifest --freeze --active-only` の出力も残します。`--active-only` を付けないと、取得しない group の `sdk-nrf-bm-internal` が原因で freeze が失敗します。

`vendor/sdk-nrf-bm/west.yml:18-34` の allowlist に並ぶ dragoon、lz4、tinycrypt は、この workspace の `west list` に現れません。理由は[振り返り](retrospective-P0.md)に記録します。

## host mrbc と bytecode

**決定: host binary は再配布しません。** `firmware/cmake/mrubyc.cmake` が configure 時に、固定 submodule `vendor/mruby`（4.0.0、SHA は[調査索引](../README.md#資料の版)）を build directory の `mruby-host/` にコピーし、そこで次を実行します。vendor 内では build しません。

```sh
MRUBY_CONFIG=build_config/mrbc.rb ruby minirake
```

host には Ruby、C compiler（cc/gcc/clang）、ar、make、Python 3 が必要です。firmware CI は `build-essential ruby python3` を導入し、ruby/cc/make の版も出力します。CMake は host の CC/LD/AR を明示し、SDK の cross compiler 用 CFLAGS/CXXFLAGS/LDFLAGS を引き継がない構成です。Ruby、make、Python や既定 build 用の host compiler がなければ configure が失敗します。

既存の実行可能な compiler は app の CMake 引数 `-DRBOS_MRBC=<mrbc>` で指定できます。`mrbc --version` が `mruby 4.0.0` を報告する必要があり、版が合わなければ構成を止めます。override 時も mrblib/header の生成に Ruby と make を使うため、host の依存をすべて省けるわけではありません。

同じコピーの mrbc で `puts "hello"` を `mrbc -Bsample -o x.c foo.rb` として二回変換し、`cmp` が exit 0 になりました。両生成物の SHA-256 は `d41e941dce496d4fbd8fe712cdb3888565a95950cc8a20f2818f6b180ceda1d1` です。これは同一 host・入力での C 配列の一致であり、異なる host の compiler binary や firmware 全体の一致を保証する検査ではありません。

mruby/c の `src`・`support`・`mrblib` も build directory にコピーします。コピー上で mrblib と vendor にない `_autogen*.h` を生成するので、vendor の生成物を変更しません。system → coordinator → worker_a → worker_b の順に const 配列と task table を生成し、Ruby source の変更で再生成する依存を置きました。

各 task の `mrbc -B` custom command の直後と、configure 時の mrblib 生成後に `tools/bm-build/check-bytecode.py` を実行します。検査条件は、C 配列の先頭8 byte が `RITE0400` で、byte 8..11 の big-endian 宣言長が配列の実 byte 数と同じであることです。一致しなければ build は失敗します。正常、空・欠落・不正な C 配列、誤 magic/version/size の拒否例は `tests/check-changes/test_bytecode.py` にあります。CI でも `python3 -m unittest discover -s tests/check-changes` により実行する対象です。VM loader まで含む正常・空プログラム・誤形式の検査は `tools/mrubyc-wasm/check.sh` に分けています。

## workspace を作る

RBOS の checkout は west workspace にしません。別の directory に BM の workspace を作ります。toolchain の環境は `nrfutil sdk-manager toolchain env --ncs-version v3.3.0 --as-script sh` の出力を読み込んで作ります。

```sh
nrfutil sdk-manager install --ncs-version v3.3.0   # toolchain の導入。今回は導入済みで未実行
eval "$(nrfutil sdk-manager toolchain env --ncs-version v3.3.0 --as-script sh)"
west init -m https://github.com/nrfconnect/sdk-nrf-bm --mr v2.0.1 <workspace>
cd <workspace>
west update --narrow -o=--depth=1
west zephyr-export
<RBOS>/tools/bm-build/check-workspace.sh <workspace>
```

今回は既存の NCS v3.3.0 の取得物を `west update --path-cache` に渡して取得時間を短縮しました。取得後の SHA は `check-workspace.sh` で modules.txt と一致することを確かめています。`--path-cache` なしの取得はこの環境では試していません。

## build

実装を広げる前に [BM preflight](development-gates.md#1-sdk-と-bm-の事前照合) を実行します。四構成の build log と成果物は [共通 verifier](development-gates.md#3-成果物の再利用可能な検査) で照合し、build 成功を実機受け入れとして報告しません。

`<workspace>` で実行します。`<workspace>` は BM workspace root、`<RBOS>` は別に置いた RBOS checkout、`<build-debug>` / `<build-release>` はリポジトリと workspace の外の出力先に置き換えます。v3.3.0 の toolchain 環境を読み込んだ後、`cd "<workspace>"` と `west topdir` で参照先を確かめてください。別の NCS workspace が選ばれると `No board named 'bm_nrf54l15dk'` で失敗します（[環境の確認](dk-provisioning.md#path-の置き換えと-build-環境)）。

```sh
# debug: SDK 既定の開発用 ED25519 鍵で署名する
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-debug> -p always

# release: リポジトリ外の鍵を絶対 path で渡す。Kconfig の文字列は二重引用符が必要
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-release> -p always -- \
  -DFILE_SUFFIX=release \
  '-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE="<key-dir>/rbos-release.pem"'

# stress/oom: Add an overlay to debug; no release key is used.
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-stress> -p always -- \
  -DEXTRA_CONF_FILE=<RBOS>/firmware/stress.conf
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-oom> -p always -- \
  -DEXTRA_CONF_FILE=<RBOS>/firmware/oom.conf
```

### Spinner 公平性と quantum の既定

`CONFIG_RBOS_TIMESLICE_TICK_COUNT` は1..255 tick（既定1）、既存の `CONFIG_RBOS_SERVICE_INTERVAL_MS` は service 後の sleep 値（既定10 ms）です。`RBOSSystem.service` が後者を返し、system.rb が `sleep_ms` に渡します。利用者は DK の X/Y 比較後、周期の組合せに依存しない案 X を debug/release/stress 共通の既定に採用しました。

| overlay | profile | quantum | service sleep | 理想化した起床周期 |
|---|---|---|---|---|
| `stress.conf`（現在） | stress | 1 tick | 10 ms | 11 tick |
| 旧 X | stress | 1 tick | 10 ms | 11 tick |
| 旧 Y | stress | 10 tick | 9 ms | 10 tick |

HAL の tick は1 msです。mruby/c は `wakeup_tick < tick` で起こすため、旧 Y は sleep を9にしました（`vendor/mrubyc/src/rrt0.c:163-183,509-524`）。service の処理時間や IRQ の遅れは表の起床周期に含めていません。[実機比較と採用理由](retrospective-P1.md#xy-比較と1-tick-の採用)を参照してください。

比較専用の X/Y overlay と CI matrix は削除しました。特に旧 Y の sleep だけを新既定と組み合わせると、比較実験とは別の設定になるためです。通常の `stress.conf` を使い、各 app の `firmware/zephyr/.config` で quantum=1、service=10、STRESS=y を確認してください。自己検査は同 priority worker の1秒間の modulo 差分が互いに2倍以内かを判定します。BM は実 timer preemption、Wasm は別の擬似 tick 経路で実行します。

`python3 tools/bm-build/simulate-spinner.py` は tick 減算・起床・末尾への再挿入・dispatch 時の slice リセットを模した host モデルです。先に走る spinner を入れ替え、旧既定（legacy）・新既定（default）・旧 Y の a/b 比を表示します。service の実行時間をゼロとし、tick 境界ですぐ preempt できる仮定です。VM・Wasm・実機の測定ではなく、実際の dispatch 位相や処理時間は再現しません。

### 比較用 image の作り方

1. RBOS 側で対象の値を Kconfig から設定可能にします。vendor は変更せず、比較前の既定値と仮説を記録します。
2. stress profile をベースに一時 overlay と CI matrix の X/Y を用意します。既定に依存せず、比較する Kconfig 値を明示します。各 `.config` と artifact の image/hash を照合します。
3. 各 image を DK で約7分（420秒）実行し、`python3 tools/bm-build/check-dk-log.py <capture.log> --profile stress` で判定します。capture 長と完全接続 stats 窓300秒は別条件です。自己検査・公平性・jitter・drain・資源値も比較します。
4. log・checker 出力・hash と観測の限界を残して結果を判定し、利用者が採用案を決めます。
5. 採用値を通常の既定へ反映し、採用しなかった overlay と比較専用 CI matrix を削除します。採用側も既定と重複する一時 overlay は削除し、モデル・試験・証拠は維持します。

新既定の実測 a/b は約1.01ですが、利用者の決定により自己検査の公平性閾値は2倍以内を維持します。

### P0 の build 記録（履歴）

比較用に、SDK の `nrf-bm/samples/boot/mcuboot_recovery_entry` も同じ board で build しました。

| build | 結果 | app の FLASH / RAM |
|---|---|---|
| recovery sample | 成功 | 19188 B / 13024 B（installer の表示。app は log 参照） |
| RBOS debug | 成功 | 31760 B / 5448 B |
| RBOS release（試験用の鍵） | 成功 | 27024 B / 5440 B |

MCUboot は FLASH 22272 B / 31 KB、firmware loader は FLASH 43124 B / 64 KB、RAM 150900 B を使い、debug と release で同じでした。`imgtool verify` は debug と release の app の署名を各鍵で検証し、`Image version: 0.1.0+0` を表示しました。

## P1 の build 結果と map 比較

比較対象は app の `firmware/zephyr/zephyr.map` と `zephyr.elf`、その app link の FLASH/RAM 表示です。sysbuild の最後に出る installer の値とは区別します。P0 基準は `da063c210a4a37469093098e14e4fb78cd068c05`、P1 は `bb6e99b` に commit した変更を含む作業木（親 `92341ee2f340`）です。P1 の生成 `app_version.h` の APP_BUILD_VERSION は親を示すため、commit 後の clean build と hash は一致しません。

| app | FLASH (B) | RAM (B) | 結果 |
|---|---:|---:|---|
| P0 debug | 31,760 | 5,448 | 成功 |
| P0 release | 27,024 | 5,440 | 成功 |
| P1 debug | 114,204 | 83,600 | 成功、compiler warning/error 0 |
| P1 release | 98,468 | 83,360 | 成功、compiler warning/error 0 |

P1 も上の `west build --sysbuild -p always` を debug と外部試験鍵の release に適用しました。容量は app 領域 FLASH 1,316 KiB / RAM 237 KiB に対する値で、SoftDevice binary、MCUboot、loader は加算していません。

### 集計方法

部品別表は初期 P1 と P0 の比較であり、後述の closeout build の再集計ではありません。

Python で GNU ld map の `Linker script and memory map` 以降の入力 section（object/archive member 付き）を解析しました。`arm-zephyr-eabi-objdump -h` の ALLOC な出力 section 内だけを対象とし、discarded section と非 ALLOC の debug 情報を除外します。merge/relax 前の長さが出力 section を越える場合は出力の境界で切ります。LOAD と VMA/LMA で RAM 初期値を照合し、RAM と FLASH の両方に計上しました。`arm-zephyr-eabi-nm -S` で `vm_pool` と `z_main_stack` の領域を先に分離しています。

残る各 byte は map の出現順で最初の部品に一度だけ割り当てます。文字列の merge による重複範囲も二重計上しません。各 memory region の origin から link summary の使用末尾までを対象にし、未帰属 byte、配置 gap、padding と下表にない依存を「その他」に含めました。これは配置上の帰属であり、個々の機能を無効にした差分実験ではありません。共有文字列の帰属は link 順に依存します。

再集計時の入力は P0/P1 各 variant の app map/ELF と build log です。SDK toolchain 環境で `arm-zephyr-eabi-objdump -h <app.elf>`、`arm-zephyr-eabi-nm -S <app.elf>`、`arm-zephyr-eabi-size <app.elf>` を実行します。size の text/data/bss は領域外の KMU 等も含むので、単純合算を app RAM として使いません。

### BLE 手順応答修正の追加 build

親 `74cd704` の作業木に `firmware/src/ble.c` と `common.conf` の応答修正を加え、debug/stress を上の手順で pristine build しました。app の値を修正前の closeout build と比較します。両方 warning/error 0、MCUboot と loader は不変でした。以下の部品別表は旧 P1 の比較を維持し、この追加分の再帰属はしていません。実機での応答・切断の改善は未確認です。

| app | 修正前 FLASH / RAM (B) | 修正後 FLASH / RAM (B) | 増分 FLASH / RAM (B) |
|---|---:|---:|---:|
| debug | 114288 / 83600 | 117152 / 83624 | +2864 / +24 |
| stress | 115088 / 83600 | 117952 / 83624 | +2864 / +24 |

### 部品別増分（P1 − P0、byte）

| 部品（帰属する入力） | debug FLASH | debug RAM | release FLASH | release RAM |
|---|---:|---:|---:|---:|
| mruby/c VM（app 内のコピーした src、mrblib を除く） | +55,827 | +2,747 | +47,606 | +2,515 |
| 組込み bytecode + mrblib（rbos_task_*.c、embedded.c、mrblib.c） | +6,643 | 0 | +6,638 | 0 |
| RBOS HAL/runtime/BLE + main（pool を除く） | +2,239 | +448 | +1,910 | +448 |
| SoftDevice handler / BLE libs（softdevice_handler/、bluetooth/） | +5,099 | +12 | +3,855 | +12 |
| nrf_security / PSA（nrf_security、mbedtls、oberon、psa、crypto/） | +5,215 | +1,691 | +4,386 | +1,691 |
| logging（logging/、log_*.c、printk.c） | −22 | 0 | −18 | 0 |
| bm_scheduler / bm_timer（同名 library） | +458 | +540 | +402 | +540 |
| VM pool（vm_pool） | 0 | +65,536 | 0 | +65,536 |
| main stack（z_main_stack、1,024 → 8,192） | 0 | +7,168 | 0 | +7,168 |
| その他（共有 binding、kernel/libc/libgcc、配置差など） | +6,985 | +10 | +6,665 | +10 |
| **合計** | **+82,444** | **+78,152** | **+71,444** | **+77,920** |

各列の和は上の app summary の差と一致します。logging の減少を単体の最適化効果とは解釈しません。bytecode 行には task の名前・table も含みます。const blob の RAM コピーはありませんが、IREP や String など実行時の追加確保は pool 内に別途必要です。ISR stack は両方 2,048 B のままで「その他」に含み、増分はありません。

P1 debug app の `zephyr.signed.bin` は SHA-256 `16713af249a4f0ab4e98100a6d633e962d319db75ffb00f6b44f2c7c4f7f7f10` でした。これは CI artifact の hash ではなく、上記 commit 前作業木の識別情報です。起動 banner の commit 表記が変わるため、文書変更だけの commit でも firmware の hash は変わり得ます。release は鍵でも変わります。

### P1 closeout の四 variant

`37c995e` に commit した変更を含む作業木で、workspace 検査後に同じ target の四 variant を pristine build しました。全て compiler warning/error 0 です。commit 前の build なので banner は親 `6cad3f5` を示し、commit 後の artifact と hash は異なり得ます。

| app | FLASH (B) | RAM (B) | Ruby task |
|---|---:|---:|---|
| debug / SELFTEST | 114,288 | 83,600 | system＋coordinator＋二 worker |
| release / SELFTEST | 98,548 | 83,360 | 同上、VM source の NDEBUG 有効 |
| stress | 115,088 | 83,600 | SELFTEST＋二つの常時 ready spinner |
| oom | 112,380 | 83,600 | system＋保持割当て fault task |

`firmware/Kconfig` の choice は SELFTEST が既定で、`firmware/cmake/mrubyc.cmake` は常に system.rb を先頭にします。stress は自己検査完了後に priority 128 の spinner 二つを起動し、10000 VM ticks ごとに進捗を表示します。`VM.tick` は `mrbc_tick` の呼出数です（`vendor/mrubyc/src/rrt0.c:145-147,1457-1467`）。oom は `OOM: start` 後に文字列を保持し、pool 枯渇で HAL abort に入ります。いずれも DK の長時間・fault 実行は未確認です。

現在の stats 形式は次です。原文の旧 P1 実機 log に drain 値を補ってはいけません。

```text
stats tick_us=<min>..<max> catchups=<count> ticks=<count> pool=<used_max>/<total> main=<bytes> isr=<bytes> idle=<count> service=<count> drain_us=<max>
```

`firmware/src/runtime.c:41-44,62-65` は bm_scheduler_process の前後の cycle 差を µs に換算し、区間最大を出力後に reset します。割り込みによる中断も含む経過時間で、queue drain の時間上限を設ける変更ではありません。実行・判定は [capture と checker](dk-provisioning.md#macos-で-p1-stress-log-を採る)、残る実機条件は [P1 closeout](retrospective-P1.md#p1-closeout-の追加実装と判定)を参照してください。

## 鍵の分離

| 構成 | 鍵 | 用途 |
|---|---|---|
| debug | MCUboot 同梱の `root-ed25519.pem`（SDK の既定） | 開発専用。公開鍵が既知のため配布しない |
| release | リポジトリ外の利用者の PEM を build 時に指定 | 配布用。鍵の生成・保管・交換は[署名鍵の手順](signing-keys.md)、KMU への書き込みは [DK の準備](dk-provisioning.md) |

`firmware/sysbuild.cmake` は release で次の場合に構成を止めます。

- 鍵を指定しない（SDK 既定の鍵になる）、または既定の鍵を明示する
- 鍵が RBOS のリポジトリ内にある（symlink は解決して判定）
- 空文字列、相対 path、存在しない file、directory

sysbuild の Python と MCUboot 同梱の imgtool で公開鍵を取り出し、同梱の全 `root-*.pem` と比較します。既定の鍵は改名しても拒否し、新しい鍵は名前が `root-*.pem` でも使えます。imgtool の実行に失敗した場合も構成を止めます。`.gitignore` は `*.pem` と `keys/` を除外します。鍵の内容や保管場所を文書・PR・成果物に書きません。

## 書き込みと erase の区別

通常の書き込みは `west flash -d <build>` です。NCS v3.3.0 の nrfutil runner は nRF54L で erase を既定にせず、`ERASE_NONE` を使います（workspace の `zephyr/scripts/west_commands/runners/nrf_common.py:367-374`）。KMU への公開鍵の書き込みは `--erase` か `--recover` を付けたときだけ行われます（同 `:404-409`）。

これは runner の静的な説明で、ERASE_NONE の更新成功は未確認です。P0 と P1 の利用者による通常更新の成功例は `nrfutil device program` の `ERASE_RANGES_TOUCHED_BY_FIRMWARE` でした。実機で成功した方法は [DK の通常の書き込み](dk-provisioning.md#通常の書き込み)、P1 の image と log は [P1 の振り返り](retrospective-P1.md)を参照してください。全体 erase・鍵の再 provision は行っていませんが、保存データの維持は未試験です。

| 操作 | コマンド | 保存データ | RBOS での扱い |
|---|---|---|---|
| 通常の書き込み | `west flash -d <build>` | 書き込む範囲の外は残る想定（未確認） | 開発中の通常操作 |
| 初回の準備 | `west flash -d <build> --erase` | 全消去。KMU に公開鍵を書く | 新しい DK・鍵を変えたときだけ。人が明示して実行 |
| 復旧 | `west flash -d <build> --recover` | 全消去と保護の解除 | 起動不能や BOOTCONF lock の解除時だけ |

RBOS の build 設定は `SB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_USING_KMU=y` です。KMU に鍵がない DK では MCUboot が起動しません（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:62-80`）。そのため初回だけは erase を伴う準備が必要です。準備の手順を通常の手順書・script・CI に入れません。erase なしで KMU だけを書く `west ncs-provision` の利用は未確認で、P5 で調べます。

## 保存する成果物

`tools/bm-build/collect-evidence.sh <workspace> <build> <out>` で、RBOS の外の `<out>` に次を集めます。private key は集めません。

| 成果物 | 目的 |
|---|---|
| 各 image の `.config`、sysbuild の `zephyr/.config` | 設定の照合 |
| 各 image の `zephyr.map` | RAM/FLASH の配置と容量 |
| 署名済み app/loader/SoftDevice、`production.hex` 等の結合 hex | 書き込み・DFU の対象 |
| `SHA256SUMS` | 成果物の同一性 |
| `west manifest --freeze`、`west list` | 全 module SHA |
| RBOS の commit と `git status` | 入力の source |
| compiler、CMake、Ninja、Python、west、nrfutil の版 | host 環境 |

同じ workspace で debug を別の build directory へ二回 build し、次の成果物が byte 単位で一致しました。別の host での一致は確かめていません。

| 成果物 | SHA-256 |
|---|---|
| `firmware/zephyr/zephyr.signed.bin` | `e2618ebf1f7efa1c53c18d69b6cdb06fb811e1277396a4d2ec9a70d14599a0a9` |
| `mcuboot/zephyr/zephyr.bin` | `bf54260b29339c31a844fd64903376d56c495d116056ef4fd2a70f38edc47639` |
| `firmware_loader/zephyr/zephyr.signed.bin` | `3573c4c65e2abf8f853daa055adb35968702199735a7e2f6624d294a6c9c663a` |
| `softdevice.signed.bin` | `a485dbbfff88d2bc21b3e928737a98ac7f1b66daf2fcc728a2879eb2167bc002` |
| `production.hex` | `e79e14fb56a5a8d5790e78b837d3f26011ed1882b122bfa4d433861705207f56` |

別 host との比較として、PR #21 の merge commit `5664b86348922044807152ec6488fd06267c32c5` を GitHub Actions（[CI の実行](https://github.com/uist1idrju3i/RBOS/actions/runs/42528666949)）とこの手順の Linux host で debug build しました。次の成果物の SHA-256 が一致しました。`.config` と map は build directory の path を含むため一致しません。

| 成果物 | SHA-256 |
|---|---|
| `firmware/zephyr/zephyr.signed.bin` | `9c9177bd6e331efef8044e5509fbe415640adeff9ddbe57cd9a289f1d8d6aa0c` |
| `firmware_loader/zephyr/zephyr.signed.bin` | `3573c4c65e2abf8f853daa055adb35968702199735a7e2f6624d294a6c9c663a` |
| `softdevice.signed.bin` | `a485dbbfff88d2bc21b3e928737a98ac7f1b66daf2fcc728a2879eb2167bc002` |
| `production.hex` | `1be74718234016e1a5169723ad1b8b56286f0d10e0d5b1364fc22faed3318557` |
| `combined_signed_update_images.hex` | `064a73d639b94b08bcabcc4d5e8a0122092a6fb8fba09f9c1f24d5bc9adab3d8` |
| `installer_merged.hex` | `051b92a15f2d1f5c69071fc54bc022fa0735a2159b83f71f42bedc895e21daca` |

hash は SDK の開発用鍵で署名した debug のものです。release の hash は鍵ごとに変わるため記録しません。起動 banner に RBOS の `git describe`（例: `v0.1.0-6c4740c8145c`）が入るため、app と `production.hex` の hash は RBOS の commit ごとに変わります。上の表は commit 前の作業木（基準 `6c4740c`）の値です。push 後の commit を新しい clone から build した場合も、build は成功し、hash は表と異なりました。

## CI

`firmware.yml` は debug / release / stress / oom の matrix を並列に動かします。一つが失敗しても他は止めません。stress/oom は debug に overlay を追加します。release 側だけで試験用 ED25519 鍵を作り、成功・失敗にかかわらず削除します。成果物名は `firmware-evidence-<variant>-<sha>` です。`production.hex`、`.config`、map、SHA256SUMS を含む証拠を保存し、保存前に PEM と `keyfile.json` がないことを検査します。workspace 保存は従来どおり debug だけです。

toolchain は bundle ID、workspace は BM v2.0.1 と `modules.txt` の hash で cache を分けます。workspace cache の保存は main の debug job だけです。復元時は init を省きますが、west update と全 module の SHA・clean tree 検査は毎回行います。log に restore / init / update / check の秒数を残します。GitHub 上の warm cache と fresh 取得の比較は未実施です。復元が遅ければ workspace cache を外します。

compiler cache は variant、bundle ID、module hash、run ID・attempt ごとに保存し、同じ prefix の main cache を PR でも復元します。保存は main への push だけです。容量は variant ごとに 512 MB に制限し、統計を build 前にリセットして終了後に表示します。`CCACHE_BASEDIR` は RBOS と BM workspace の共通親、cache 自体は runner の一時領域に置きます。鍵や build directory は cache に含めません。

`firmware-release.yml` は最初に Secret の有無を確かめます。Environment、ref 制限、署名鍵の検査と削除、成果物の保存は維持します。compiler cache は `CCACHE_DISABLE=1` で無効にし、workspace cache も使いません。固定 toolchain の cache だけは従来どおり使います。flash / erase は行いません。main の firmware CI は ref ごとに直列化し、実行中の build を取り消しません。

### Actions 更新の確認

2026-11-09 に各 action の latest release と tag の commit を GitHub API で確認しました。checkout は v7.0.1 のままです。PR 安全性の検査、branch の空白処理、git config 値の escape 修正を確認し、`persist-credentials: false` を維持しました。

- [cache v4.2.4 → v6.1.0 の全変更](https://github.com/actions/cache/compare/v4.2.4...v6.1.0): v4.3.0、v5.0.0〜v5.0.5、v5.1.0、v6.0.0、v6.1.0 の release を確認しました。Node 24、ESM、依存の脆弱性・非推奨 API 修正、429 と read-only cache の扱いを採用します。runner の最低版は 2.327.1 です。保存条件を明示するため workspace と compiler cache は restore / save に分けます。非推奨の `save-always`、別 OS 間の archive、cache miss 時の失敗は不要なので使いません。
- [upload-artifact v4.6.2 → v7.0.2 の全変更](https://github.com/actions/upload-artifact/compare/v4.6.2...v7.0.2): v5.0.0、v6.0.0、v7.0.0〜v7.0.2 を確認しました。Node 24、ESM、依存修正を採用します。最低 runner 版は同じです。v7 の単一 file の直接 upload は証拠 directory に合わず、名前も file 名に変わるため使いません。`archive: true` と `include-hidden-files: true` を明示します。artifact の不変性に合わせ matrix の名前を分け、上書きはしません。v7.0.2 の download 時の 429 / Retry-After 修正も含まれますが、この workflow は download しません。

両 action の MIT license は旧版・新版で同じです。圧縮率と保存期間は変更しません。Dependabot は workflows に加え `.github/actions/ncs-bm-setup` も週次で検査します。CI だけの変更なので CHANGELOG は更新しません。

### 必須 check と変更判定

必須 check 名は `agent-docs`、`mruby-wasm`、`firmware` です。PR と main への push で必ず check を作るため、workflow-level の paths は使いません。agent-docs は常に全検査を行います。他の二つは最初の changes job で全履歴を取得し、PR の base SHA または push の before SHA から、検査する commit までを `git diff --name-only` で比較します。

`.github/scripts/changed-inputs.sh` が入力の directory と submodule pointer を判定します。変更判定 script とそのテストを変えた場合は両方の検査を実行します。before が空・全ゼロ、commit が取得できない、force push、履歴が連続しない場合も入力変更ありとして扱います。関係のない変更なら重い build / test だけを省きます。

最後の同名 job は `if: always()` で結果をまとめます。変更判定が成功し、必要な build / test が成功した場合、または入力変更なしで省略した場合だけ成功します。判定や build / test の失敗・取消は成功にしません。matrix の check 名は `build (debug)` / `build (release)` / `build (stress)` / `build (oom)` で、必須にするのは集約した `firmware` だけです。workflow 全体を paths で省略すると必須 check が pending のまま残るため、この形にしています。

マージ後に管理者が Settings → Rules → Rulesets → main → Require status checks で、source が GitHub Actions の `agent-docs`、`mruby-wasm`、`firmware` を追加します。Require branches to be up to date は off のままにします。必要なら Require code scanning results も追加し、CodeQL の threshold を High 以上に設定してください。今回の変更では ruleset を操作しません。

## 実機で確認した範囲と残り

2026-11-09 JST に利用者が、CI debug の MCUboot → app 起動、LED0 点灯、VCOM の `RBOS 0.1.0+0`、BUTTON0 + RESET による BLE MCUmgr loader 入口を確認しました。banner は `My Application` で、RBOS の log に `v` は付きません。macOS の VCOM 有効化と詳細な log は [DK の準備](dk-provisioning.md)を参照してください。

全体 erase なし・鍵の再準備なしの v0.1.1 への通常更新も起動しました。ただし、書き込む範囲の外の保存データを前後で比較した結果はありません。空の KMU での erase なしの初回準備と、BLE DFU 後に新しい image が起動することも未確認です。

[調査索引へ戻る](../README.md)
