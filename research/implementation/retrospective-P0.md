# P0 の振り返り

[段階計画](porting-plan.md)の P0「BM の再現可能な基盤」の最初の実装を振り返ります。作業日は 2026-11-09、基準 commit は `6c4740c8145c0c5f7f86fae6a04433b51336cd36` です。手順と結果の詳細は [build 再現手順](bm-build.md)にあります。

## 達成と未達

| 項目 | 結果 | 証拠・残り |
|---|---|---|
| NCS/toolchain v3.3.0 + BM v2.0.1 の独立 workspace | 達成 | `west init` から作り直し、`check-workspace.sh` が全 SHA の一致を確認 |
| recovery sample の build | 達成 | S115 target で sysbuild の全 image が成功 |
| recovery sample の flash、BLE、console | 未達 | DK を接続していない |
| RBOS の CMake・Kconfig・sysbuild・overlay・署名の最小構成 | 達成 | `firmware/`。debug と release の build が成功 |
| release/debug と鍵の分離 | 達成 | release の鍵の検査が五つの拒否例で失敗し、試験用の外部鍵で成功 |
| module SHA・map・compiler 版の保存 | 一部 | 収集 script はある。CI の artifact としては未保存 |
| clean workspace での再現 | 一部 | 同じ host の二回の build が一致。別 host、`--path-cache` なしの取得は未確認 |
| DK 上の LED・console・loader 入口 | 未達 | 実機がない |
| 自動 erase を通常操作に含めない | 達成 | script・設定に erase はない。runner の既定は `ERASE_NONE` |

P0 の受け入れ条件は実機確認を含むため、P0 は未完了です。[チェックリスト](checklist.md)には証拠のある項目だけに印を付けました。

## 判明したリスクと blocker

- **実機がない**: LED、console、loader 入口、recovery sample の flash を確認できません。P0 を閉じる blocker です。
- **初回の書き込みは erase を伴う**: KMU を使う設定では、公開鍵を KMU に書くまで MCUboot が起動しません。runner は `--erase` か `--recover` の時だけ鍵を書きます。通常の手順から erase を外すと、新しい DK では起動しません。初回の準備を別手順として扱う必要があります。
- **retention 入口が既定で有効**: board の Kconfig.sysbuild が `ENTRANCE_BOOT_MODE` を既定 y にします。RBOS の app はまだ入口要求を書きませんが、P3 の権限設計では loader 遷移を特権操作として扱う必要があります。
- **Kconfig の文字列引数**: `-DSB_CONFIG_..._KEY_FILE` は値を二重引用符で囲まないと Kconfig の警告で build が止まりました。
- **`west manifest --freeze` の失敗**: 取得しない `sdk-nrf-bm-internal` があるため、`--active-only` が必要でした。
- **allowlist と実体の差**: BM の allowlist にある dragoon は group 無効のため取得されず、lz4 と tinycrypt は NCS v3.3.0 の Zephyr manifest に定義がありません。`nrf/west.yml:44-46,181-187`、`zephyr/west.yml:320-325,377-385`（workspace 内の path）で確認しました。現在の build には影響しません。
- **鍵名の判定**: release の検査は `root-*.pem` という名前の鍵を一律に拒否します。利用者が同じ名前を付けた正当な鍵も拒否されます（追記: 公開鍵の比較に変えて解消）。
- **SoftDevice の既定設定**: app は BLE を使いませんが、`CONFIG_SOFTDEVICE=y` で peripheral link 1 本の設定が入ります。central の設定は入っていません。
- **license header**: 既存の `src/rbos/` にも SPDX header がなく、`firmware/` も合わせて付けていません。方針は未決です。

## P1 への改善提案

1. P1 の着手前に DK で P0 の未確認項目を確かめ、結果をこの文書へ追記します。初回準備（erase と KMU）と通常の書き込みを別の手順として実行し、保存データが残るかも見ます。
2. firmware の build を CI に入れます。container の選定（P6）を待たず、`nrfutil sdk-manager` の toolchain と `check-workspace.sh`・`collect-evidence.sh` を使い、成果物を artifact に残す案を比較します。
3. mrbc と mruby/c を `firmware/` へ結合する時は、P0 と同じく debug/release の両方を build し、map の差を記録します。
4. 段階ごとに「計画 → checklist の項目を PR に転記 → 証拠付きで印 → 振り返り」の順にします。振り返りは `retrospective-P<n>.md` とし、本文書と同じ四つの見出しを使います。
5. `prj.conf` と `prj_release.conf` は内容がほぼ重複しています。P1 で設定が増える前に、共通部分と差分の分け方を決めます。

## checklist と porting-plan への追記候補

- checklist P0: 「新しい DK の初回準備（erase、KMU provisioning）を手順化し、通常の書き込みと分ける」
- checklist P0: 「`west ncs-provision` で erase なしに KMU を書けるか調べる」
- checklist P3: 「retention 入口（boot mode）の要求を書く API を特権操作に限る」
- checklist P5: 「release の鍵の検査を、名前ではなく公開鍵の比較で既定鍵と区別する」
- checklist P6: 「firmware build の成果物と SHA256SUMS を CI artifact に残す」
- porting-plan P0: 受け入れ条件に「別 host での成果物の一致」を含めるかを決める
- porting-plan 全体: 各段階の終わりに振り返り文書を作ることを明記する

## 改善提案と追記候補の反映（2026-11-09 追記）

利用者の判断で、上の改善提案と追記候補をすべて採用しました。実機での確認が要る項目は、DK の確認を待っています。

| 提案・候補 | 反映先 | 状態 |
|---|---|---|
| DK で P0 の未確認項目を確かめる | [DK の準備](dk-provisioning.md)の記録表 | 実機確認待ち |
| firmware build を CI に入れる | `.github/workflows/firmware.yml`、`.github/actions/ncs-bm-setup/` | 実装。debug と使い捨て鍵の release を build し、証拠を artifact に残す |
| mruby/c の結合後に debug/release の map を比べる | checklist P1、porting-plan P1 | 追記 |
| 段階の運用を定める | porting-plan の「段階の進め方」 | 追記 |
| `prj.conf` の重複をなくす | `firmware/common.conf` | 実装。変更前と `.config` が一致 |
| 初回準備と通常の書き込みを分ける | [DK の準備](dk-provisioning.md)、checklist P0 | 手順を作成。実機は未確認 |
| erase なしで KMU に鍵を書く方法を調べる | [DK の準備](dk-provisioning.md) | `x-provision-keys` の単独実行を候補として記録。実機は未確認 |
| retention 入口の要求を特権操作に限る | checklist P3 | 追記 |
| 既定鍵を公開鍵の比較で拒否する | `firmware/sysbuild.cmake` | 実装。改名した既定鍵を拒否し、`root-*.pem` という名前の新しい鍵を受け入れることを build で確認 |
| 成果物と SHA256SUMS を CI artifact に残す | `.github/workflows/firmware.yml` | 実装 |
| 別 host での成果物の一致 | porting-plan P0 の受け入れ条件、checklist P0 | 受け入れ条件に追加。CI とローカルの比較で確かめる |

あわせて、正式 release を GitHub Actions の Environment `release` の Secret で署名する方針と、利用者が鍵を替える手順を[署名鍵の手順](signing-keys.md)にまとめました。

[調査索引へ戻る](../README.md)
