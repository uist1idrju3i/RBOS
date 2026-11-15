# A5: Nordic toolchain container の比較

[調査索引](../README.md) / [BM build の再現手順](bm-build.md)

## 目的と結論

2026-11-15 に、bundle 導入方式と Nordic 公式 image を比較しました。対象の RBOS は base commit `c250ccfd05b778a2401dc6db5685d27e73b88178` です。firmware・vendor・module SHA は変更していません。

**CI は公式 image の digest 固定へ移行します。** debug / release / stress / oom の全構成で、app と loader の HEX が一致しました。ELF 全体は一致しませんが、debug 情報を除いた ELF は byte 単位で一致します。追加で比較した MCUboot と installer も、後述の debug symbol を除けば一致します。両方式の `verify-evidence` は全8件 PASS です。

これは同じ Linux x86_64 host 上の bundle / container 比較です。GitHub Actions 上の job container、cache の復元・保存、実機の起動・更新は未確認です。build/link の結果を実機受け入れとは扱いません。

## 固定した入力と版

- BM v2.0.1 / `51484143c09199e19bccc16fa3b437f7a502a72b`。
- sdk-nrf v3.3.0 / `ba167d9f3db4abbdc9b67887ca3ea66c64f2d956`。
- bundle `911f4c5c26`。workspace の全 project path・SHA・clean tree は、両方式とも `tools/bm-build/check-workspace.sh` で PASS。
- image: `ghcr.io/nrfconnect/sdk-nrf-toolchain@sha256:f24d8932ff081ebcd8da9c248f4449bdabe461c0620a7a4ac9e95eb577ba2276`。pull の返した digest と一致しました。
- board: `bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot`。
- 同じ source・workspace・build の絶対 path を bind mount で共有し、方式ごとに `-p always` で build しました。release だけは同じ一時 Ed25519 鍵を両方式で使いました。製品の署名鍵は使っていません。

| tool | bundle 方式 | container 方式 |
|---|---|---|
| ARM GCC / Zephyr SDK | 12.2.0 / 0.17.0 | 同左 |
| CMake | 4.2.1 | 同左 |
| Ninja | 1.13.2 | 同左 |
| Python | 3.12.4 | 同左 |
| west | 1.5.0 | 同左 |
| bundle 内 nrfutil | 8.1.1 | 同左 |
| GNU Make | 4.3 | 同左 |
| Ruby | 3.0.2 | 3.2.3 |
| host cc | GCC 11.4.0 | GCC 13.3.0 |
| host OS | Ubuntu 22.04 | Ubuntu 24.04 |

bundle 方式の導入用 nrfutil は 9.0.0、sdk-manager は 1.17.0 でした。移行前の CI は導入用 nrfutil 1.4.2 を使いますが、選択する bundle ID は同じです。ARM compiler と `libgcc.a` は、両方式で次の SHA-256 に一致しました。

```text
arm-zephyr-eabi-gcc 42e96e38c3d24e74ec0f5752b0a644362c84f2dd473461158f6ab3816f7fa4f7
libgcc.a            686d1c254f77d0fe9dcb20bbcf4f85f5bca6de5ac119aa75a44bbce2cd96321e
```

公式 image には Ruby と make がなかったため、実行中の container に `build-essential ruby python3` を apt で導入しました。自前の image は作成・公開・mirror していません。CI でも同じ host build 依存を導入し、cache 圧縮用に `zstd` を追加します。apt package の版までは digest 固定の対象ではありません。

## LTS と BM release の対応方針

最新 LTS 系は v3.4.x、今回検討した版は v3.4.2 です。[Nordic の v3.4.2 release notes の原文](https://github.com/nrfconnect/sdk-nrf/blob/v3.4.2/doc/nrf/releases_and_maturity/releases/release-notes-3.4.2.rst)は、v3.4.0 から5年間の LTS と明記しています。[必要 tool の文書](https://github.com/nrfconnect/sdk-nrf/blob/v3.4.2/doc/nrf/installation/recommended_versions.rst)は、SDK に対応する bundle 内の版を検証対象とし、他の版は未検証としています。

ただし、toolchain は固定した BM release の sdk-nrf に合わせます。BM v2.0.1 の [公開 west.yml](https://github.com/nrfconnect/sdk-nrf-bm/blob/v2.0.1/west.yml) と `vendor/sdk-nrf-bm/west.yml:14-17` は v3.3.0 を指定しています。今回は **BM v2.0.1 / sdk-nrf v3.3.0 / bundle `911f4c5c26` を維持**します。

`nrfutil --json sdk-manager toolchain search v3.3` の公開 registry 応答では、v3.3.0〜v3.3.5 が同じ `911f4c5c26` に対応しました。v3.3.5 を選んでも toolchain は変わらず、BM の sdk-nrf 自体を v3.3.5 へ差し替える理由にはしません。`search v3.4.2` は別 bundle `197d1ad490` を返します。v3.4.2 の導入・build は今回試していません。

`vendor-release-watch` が BM の新しい正式 release tag を通知したら、その `west.yml` が v3.4.x を対象にするかを確認します。対応する正式 BM release が出てから、BM と toolchain を一緒に LTS 系へ更新し、再比較します。toolchain だけを先行して更新しません。

## 実行したコマンド

以下では実際の絶対 path を `RBOS`、`WORKSPACE`、`LOGS`、`ARTIFACTS`、`KEY` に置き換えています。`LOGS` は gitignore 対象、`ARTIFACTS` と鍵は repository 外です。両方式を順番に実行し、同じ build directory の次の build 前に比較用ファイルをコピーしました。比較用の snapshot は evidence の外へ保存します。収集済みの evidence に追加すると checksum 検査が拒否するためです。

```bash
IMAGE=ghcr.io/nrfconnect/sdk-nrf-toolchain@sha256:f24d8932ff081ebcd8da9c248f4449bdabe461c0620a7a4ac9e95eb577ba2276
docker pull "$IMAGE"
docker image inspect "$IMAGE"
# Run from a clean Bash, before the bundle changes PATH and NRFUTIL_HOME.
nrfutil --json sdk-manager toolchain search v3.3
nrfutil --json sdk-manager toolchain search v3.4.2
eval "$(nrfutil sdk-manager toolchain env --toolchain-bundle-id 911f4c5c26 --as-script sh)"
umask 077
python3 "$WORKSPACE/bootloader/mcuboot/scripts/imgtool.py" keygen -t ed25519 -k "$KEY"
```

container は repository・workspace・出力先を同じ絶対 path に mount して起動しました。image の `BASH_ENV=/opt/non-interactive-setup.sh` が `/opt/toolchain-env.sh` を読みます。確認・依存導入のコマンドは次のとおりです。

```bash
docker run -d --name rbos-a5-container \
  -v "$RBOS:$RBOS" -v "$WORKSPACE:$WORKSPACE" -v "$ARTIFACTS:$ARTIFACTS" \
  "$IMAGE" 'exec tail -f /dev/null'
docker exec rbos-a5-container bash -c 'test -z "${ACCEPT_JLINK_LICENSE+x}"; test ! -x /usr/bin/JLinkExe'
docker exec rbos-a5-container bash -c 'apt-get update && apt-get install --no-install-recommends -y build-essential ruby python3'
docker exec rbos-a5-container bash -c 'arm-zephyr-eabi-gcc --version; cmake --version; ninja --version; python3 --version; west --version; nrfutil --version; ruby --version; cc --version; make --version'
```

`ACCEPT_JLINK_LICENSE` は設定せず、J-Link の license を承諾していません。比較時の build は、bind mount の所有者と同じ uid/gid で `docker exec --user` を使いました。書込み可能な HOME を渡し、nrfutil の log directory の所有者だけを合わせました。image 本体の compiler・library は変更していません。

両方式で、次の処理を `mode=bundle` と `mode=container` として実行しました。container 側も Bash です。

```bash
export CMAKE_BUILD_PARALLEL_LEVEL=4
cd "$WORKSPACE"
"$RBOS/tools/bm-build/check-workspace.sh" "$WORKSPACE"
for profile in debug release stress oom; do
  args=()
  if [ "$profile" = release ]; then
    args+=(-- -DFILE_SUFFIX=release "-DSB_CONFIG_BM_BOOTLOADER_MCUBOOT_SIGNATURE_KEY_FILE=\"$KEY\"")
  elif [ "$profile" != debug ]; then
    args+=(-- "-DEXTRA_CONF_FILE=$RBOS/firmware/$profile.conf")
  fi
  build="$LOGS/build-$profile"
  out="$ARTIFACTS/$mode-$profile"
  west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
    "$RBOS/firmware" --sysbuild -d "$build" -p always "${args[@]}" \
    > "$LOGS/$mode-build-$profile.log" 2>&1
  "$RBOS/tools/bm-build/collect-evidence.sh" "$WORKSPACE" "$build" "$out" \
    "$LOGS/$mode-build-$profile.log"
  python3 "$RBOS/tools/bm-build/verify-evidence.py" "$out" \
    --profile "$profile" --revision "$(git -C "$RBOS" rev-parse HEAD)"
  for image in firmware firmware_loader mcuboot installer; do
    comparison="$ARTIFACTS/comparison/$mode-$profile/$image/zephyr"
    mkdir -p "$comparison"
    cp "$build/$image/zephyr/zephyr."{elf,hex} "$comparison/"
  done
done
```

各 ELF / HEX の `sha256sum` を採取しました。ELF は同じ SDK の `arm-zephyr-eabi-objcopy --strip-debug input.elf output.elf` を両方式に適用し、出力を `cmp` で照合しました。差分は ELF32 section header と section data を読み取って分類し、`readelf --debug-dump=rawline`、`readelf -SW`、`readelf --wide --symbols` でも確認しました。

## 判定基準と結果

採用条件は、全構成の build と verifier が成功し、HEX が一致することです。ELF 全体が異なる場合は、実行部分の差がないことと、差分の理由を確認します。説明できない差や失敗があれば移行しません。

| profile | bundle build / verifier | container build / verifier | app FLASH / RAM（byte、両方式共通） |
|---|---|---|---|
| debug | PASS / PASS | PASS / PASS | 149428 / 96180 |
| release | PASS / PASS | PASS / PASS | 127852 / 95996 |
| stress | PASS / PASS | PASS / PASS | 150228 / 96180 |
| oom | PASS / PASS | PASS / PASS | 145804 / 96180 |

**全32組: HEX 16組は完全一致、ELF 16組は `--strip-debug` 後に完全一致。** このうち依頼対象の app / loader は、HEX 8組・ELF 8組です。全ファイルの両 SHA-256、strip 後の SHA-256、異なる section、verifier の結果は[機械可読の比較結果](toolchain-container-results.json)に保存しました。

app・loader・installer の差分は `.debug_info` / `.debug_line` です。DWARF の include directory に、bundle の導入先と container の `/opt/ncs/toolchains/911f4c5c26` の違いがありました。デバッグ時に source path の対応付けは必要ですが、HEX と strip 後の ELF に差はありません。Ruby と host cc の版の違いによる実行部分の差も、この入力では出ていません。

MCUboot は両方式とも `CONFIG_LTO=y` です。`.debug_info` / `.debug_line` に加え、`.symtab` / `.strtab` も異なりました。最初の比較器は debug section の差だけを許可したため、この追加対象4組を FAIL にしました。`readelf` で、異なる weak hidden symbol が非 ALLOC の `.debug_info` を参照していることを確認しました。debug section を参照する symbol を除き、名前・値・size・属性・参照 section を順序によらず比べると全 symbol が一致します。strip 後のファイル全体も一致するため、実行部分の差ではありません。最終判定は32組 PASS です。

実行中には、bundle 環境を二重に読み込んだ際の sdk-manager 探索失敗と、補助 script 終了時の構文 error がありました。4 build・4 verifier の成功と全 snapshot を個別に照合し、選択済み compiler の path・版・hash も確認しました。container では非 root uid の nrfutil log 書込み権限で最初の collector が止まったため、log の所有者を直して収集から再開しました。成功済みの build は再実行していません。

## CI への反映と残す範囲

- `firmware.yml` の preflight と四構成 build、`firmware-release.yml` の build に、同じ digest の job container を指定します。
- 共通 action は Bash で image の環境を読み込み、toolchain path と J-Link 未導入を検査します。workspace の init / update と全 module の SHA・clean tree 検査は残します。
- sdk-manager の毎回導入と bundle cache は外します。workspace / compiler cache は image digest の先頭を含む新しい namespace に分け、旧 host の cache を復元しません。main だけで保存する条件、release の compiler cache 無効化、鍵の検査と削除は維持します。
- **提案: bundle 方式は比較用の手順として残し、常設の二重 CI や自動 fallback は追加しません。** [既存のローカル手順](bm-build.md#workspace-を作る)とこの記録から再比較できます。今回の比較は移行前の CI artifact との直接比較ではなく、同じ bundle を使うローカル build との比較です。CI の実行時間改善はまだ測定していません。
- semver skill の「内部・文書のみで契約への影響なし」に該当します。public Ruby API、board 契約、SDK の版、firmware の実行部分を変えないため、VERSION・CHANGELOG は更新しません。

この評価は実機動作や、全 object の最終的な license 適合を保証しません。一時署名鍵は比較終了後に削除しました。新しい commit での app hash と、別の一時鍵での release hash は、この記録の値から変わります。
