# 署名鍵の作成と交換

RBOS の firmware を自分の Ruby とともに配布する利用者と、RBOS の正式 release を作る管理者のための手順です。build の詳細は [build 再現手順](bm-build.md)、DK への鍵の書き込みは [DK の準備](dk-provisioning.md)にあります。手順は SDK の文書とソースから組み立てたもので、実機ではまだ試していません。

## 鍵を替える理由

debug の build は MCUboot に同梱された `root-ed25519.pem` で署名します。この鍵の秘密部分は公開されているため、誰でも同じ署名を作れます。自分の Ruby を組み込んで配布する場合は、自分だけが持つ鍵で release を build します。RBOS の release 用の鍵を、利用者の製品に流用しません。

MCUboot は KMU に書かれた公開鍵で image を検証します。KMU の鍵を替えるには SoC 全体の erase が必要です。配布した機器の鍵は、実質的に替えられないものとして扱います。

## 利用者の手順

1. リポジトリの外で ED25519 の鍵を作ります。MCUboot 同梱の imgtool を使います。

   ```sh
   mkdir -p ~/rbos-keys && chmod 700 ~/rbos-keys
   python3 <workspace>/bootloader/mcuboot/scripts/imgtool.py \
     keygen -k ~/rbos-keys/product-release.pem -t ed25519
   chmod 600 ~/rbos-keys/product-release.pem
   ```

   OpenSSL 3 でも作れます（`openssl genpkey -algorithm ed25519 -out product-release.pem`）。macOS では Homebrew の `openssl@3` を使います。`ssh-keygen` は OpenSSH 形式の鍵を書き出し、imgtool はこの形式を読めないため使いません。どちらの方法でも、ファイルは `-----BEGIN PRIVATE KEY-----` で始まります。

2. 鍵の写しをオフラインの媒体に保管します。鍵を失うと、配布済みの機器へ新しい firmware を入れるには erase が必要になります。

3. release を build します。`<key-dir>` は手順 1 の directory の絶対 path です。値は二重引用符を含めて渡します。

   ```sh
   west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
     <RBOS>/firmware --sysbuild -d <build-release> -p always -- \
     -DFILE_SUFFIX=release \
     '-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE="<key-dir>/product-release.pem"'
   ```

   `firmware/sysbuild.cmake` は、鍵の指定がない場合、リポジトリ内の鍵、相対 path、MCUboot の既定鍵と公開鍵が同じ鍵を拒否します。

4. 署名を確かめます。

   ```sh
   python3 <workspace>/bootloader/mcuboot/scripts/imgtool.py \
     verify -k ~/rbos-keys/product-release.pem \
     <build-release>/firmware/zephyr/zephyr.signed.bin
   ```

5. 機器の KMU に新しい公開鍵を書きます。debug 用に準備した DK を使う場合は、[DK の準備](dk-provisioning.md)の SDK 標準の方法（`west flash --erase`）で全体を消してから書きます。

## 正式 release の鍵（GitHub Actions）

管理者が検証済みの `main` コミットに署名なしの正式版タグ `vX.Y.Z` を作成して push すると、`.github/workflows/firmware-release.yml` が起動します。管理者は対象の版とコミットを確認し、`production` の署名ジョブを承認します。鍵は runner の一時ディレクトリに権限 600 で書き、ジョブの終わりに消します。成果物に PEM と `keyfile.json` を入れません。GitHub Release の公開は管理者が行います。

管理者が一度だけ行う設定は次のとおりです。

1. GitHub の Settings の Environments で `production` を作成するか、既存の設定を確認します。Required reviewers に承認者を指定し、管理者バイパスを無効にします。Deployment branches and tags では Tag の `v*` だけを許可します。
2. 鍵を上の利用者の手順 1 と同じ方法で作り、オフラインに保管します。
3. `production` の Environment secrets に `RBOS_RELEASE_SIGNING_KEY` を追加し、PEM の全文（`BEGIN` と `END` の行を含む）を登録します。`gh secret set RBOS_RELEASE_SIGNING_KEY --env production < rbos-release.pem` でも登録できます。承認前のジョブに鍵を渡さないため、Repository secrets には登録しません。
4. `production` の保護設定と Secret の登録を確認してからタグを push します。ワークフローは保護設定を構築前と承認後に検査します。
5. 登録後、手元の鍵の写しをオフラインの保管先以外から消します。

pull request の CI（`.github/workflows/firmware.yml`）は、job ごとに作る使い捨ての鍵で release の build を確かめます。この鍵の image は配布しません。

## 鍵が漏れた場合

漏れた鍵で署名した image は、その公開鍵を KMU に持つ全機器で起動します。新しい鍵を作り、配布済みの機器を erase して再準備します。MCUboot の鍵の失効（`CONFIG_BOOT_KEYS_REVOCATION`）は、最初の build から有効にしないと後から使えません（`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:82-101`）。採用するかは P5 で判断します。

[調査索引へ戻る](../README.md)
