# P0 の build 再現手順

[段階計画](porting-plan.md)の P0 で作った firmware の最小構成を、別の環境で同じ版から build するための手順です。2026-11-09 に RBOS commit `6c4740c8145c0c5f7f86fae6a04433b51336cd36` と本 PR の変更を Linux x86_64 で build しました。実機への書き込みと起動は試していません。

## 構成

firmware は RBOS の `firmware/` に置きます。`src/rbos/` の共有 binding は Nordic の header を含まないため、BM の Zephyr application とは分けました。

| ファイル | 役割 |
|---|---|
| `firmware/CMakeLists.txt` | sysbuild 以外、他 board target、firmware loader 以外の MCUboot mode を拒否 |
| `firmware/Kconfig` | log level の設定 |
| `firmware/Kconfig.sysbuild` | release を示す `SB_CONFIG_RBOS_RELEASE` |
| `firmware/sysbuild.cmake` | release の署名鍵の検査 |
| `firmware/common.conf` | debug / release 共通の app 設定 |
| `firmware/prj.conf` / `prj_release.conf` | debug / release の最適化設定だけを指定。共通設定は CMake で追加 |
| `firmware/sysbuild.conf` / `sysbuild_release.conf` | BLE MCUmgr loader、GPIO 入口、release の印。retention 入口は board の既定で有効（`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/Kconfig.sysbuild:73-74`） |
| `firmware/boards/bm_nrf54l15dk_nrf54l15_cpuapp_s115_softdevice_mcuboot.overlay` | board overlay の置き場。現在は model 名だけを変更 |
| `firmware/VERSION` | 0.1.0、TWEAK 0。署名 image は `0.1.0+0` |
| `firmware/src/main.c` | 版を UARTE の log へ出し、LED0 を点灯して log を flush し続ける |
| `tools/bm-build/` | module SHA の照合と成果物の収集 |

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

`<workspace>` で実行します。build directory は RBOS の外に置きます。

```sh
# debug: SDK 既定の開発用 ED25519 鍵で署名する
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-debug> -p always

# release: リポジトリ外の鍵を絶対 path で渡す。Kconfig の文字列は二重引用符が必要
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  <RBOS>/firmware --sysbuild -d <build-release> -p always -- \
  -DFILE_SUFFIX=release \
  '-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE="<key-dir>/rbos-release.pem"'
```

比較用に、SDK の `nrf-bm/samples/boot/mcuboot_recovery_entry` も同じ board で build しました。

| build | 結果 | app の FLASH / RAM |
|---|---|---|
| recovery sample | 成功 | 19188 B / 13024 B（installer の表示。app は log 参照） |
| RBOS debug | 成功 | 31760 B / 5448 B |
| RBOS release（試験用の鍵） | 成功 | 27024 B / 5440 B |

MCUboot は FLASH 22272 B / 31 KB、firmware loader は FLASH 43124 B / 64 KB、RAM 150900 B を使い、debug と release で同じでした。`imgtool verify` は debug と release の app の署名を各鍵で検証し、`Image version: 0.1.0+0` を表示しました。

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

`firmware.yml` は debug / release の matrix を並列に動かします。一方が失敗しても他方は止めません。release 側だけで試験用 ED25519 鍵を作り、成功・失敗にかかわらず削除します。成果物名は `firmware-evidence-<variant>-<sha>` です。`.config` を含む証拠を zip に保存し、保存前に PEM と `keyfile.json` がないことを検査します。

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

最後の同名 job は `if: always()` で結果をまとめます。変更判定が成功し、必要な build / test が成功した場合、または入力変更なしで省略した場合だけ成功します。判定や build / test の失敗・取消は成功にしません。matrix の check 名は `build (debug)` / `build (release)` で、必須にするのは集約した `firmware` だけです。workflow 全体を paths で省略すると必須 check が pending のまま残るため、この形にしています。

マージ後に管理者が Settings → Rules → Rulesets → main → Require status checks で、source が GitHub Actions の `agent-docs`、`mruby-wasm`、`firmware` を追加します。Require branches to be up to date は off のままにします。必要なら Require code scanning results も追加し、CodeQL の threshold を High 以上に設定してください。今回の変更では ruleset を操作しません。

## 実機で確認する項目（未検証）

- 通常の書き込み後に MCUboot から app が起動し、UARTE20（VCOM）に `RBOS 0.1.0+0` が出る。
- LED0（P2.09、active high）が点灯する。
- BTN_0（P1.13）を押して reset すると BLE MCUmgr loader に入る。入口は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/entering_dfu.rst:13-19` の GPIO 方式。
- 通常の書き込みの前後で、書き込む範囲の外のデータが残る。

[調査索引へ戻る](../README.md)
