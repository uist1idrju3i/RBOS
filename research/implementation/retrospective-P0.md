# P0 の振り返り

[段階計画](porting-plan.md)の P0「BM の再現可能な基盤」の最初の実装を振り返ります。作業日は 2026-11-09、基準 commit は `6c4740c8145c0c5f7f86fae6a04433b51336cd36` です。手順と結果の詳細は [build 再現手順](bm-build.md)にあります。

「実機結果」より前は、最初の実装時点の記録です。当時の未確認事項を残し、利用者報告を受けた現在の達成範囲と P0 の判定を末尾に追記しました。

## 達成と未達

| 項目 | 結果 | 証拠・残り |
|---|---|---|
| NCS/toolchain v3.3.0 + BM v2.0.1 の独立 workspace | 達成 | `west init` から作り直し、`check-workspace.sh` が全 SHA の一致を確認 |
| recovery sample の build | 達成 | S115 target で sysbuild の全 image が成功 |
| recovery sample の flash、BLE、console | 未達 | DK を接続していない |
| RBOS の CMake・Kconfig・sysbuild・overlay・署名の最小構成 | 達成 | `firmware/`。debug と release の build が成功 |
| release/debug と鍵の分離 | 達成 | release の鍵の検査が五つの拒否例で失敗し、試験用の外部鍵で成功 |
| module SHA・map・compiler 版の保存 | 初回は一部、現在は達成（追記） | 当時は収集 script のみ。現在は [CI artifact の保存](#ci-artifact-の保存)を確認済み |
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
| 別 host での成果物の一致 | porting-plan P0 の受け入れ条件、checklist P0 | 受け入れ条件に追加。commit `5664b86` の CI とローカルの debug build で、署名済み image と `production.hex` の hash が一致 |

あわせて、正式 release を GitHub Actions の Environment `release` の Secret で署名する方針と、利用者が鍵を替える手順を[署名鍵の手順](signing-keys.md)にまとめました。

## 実機結果（2026-11-09 JST、利用者報告）

macOS に接続した PCA10156 revision 1.0.0 の結果です。エージェントによる追試ではありません。入力 image の出所、hash、未 commit の版変更、実行した操作と log は [DK の準備](dk-provisioning.md)に記録しました。CI debug は commit `6d09bd5` の成果物、v0.1.1 と recovery sample は Devin のローカル build です。後二つの hash をリポジトリでの再現の証拠にはしません。

### 達成と未確認

| 項目 | 今回の結果 | 境界 |
|---|---|---|
| DK の表示と pin | `220-JP8930`、LED0 P2.09、BUTTON0 P1.13、TXD1 P1.04 が資料と一致 | 観察した範囲の照合。任意の無線設定の適法性の保証ではない |
| 初回準備 | SDK 標準相当の program `ERASE_ALL` → KMU provision → reset で app 起動 | `west flash --erase` 自体と、空の KMU での erase なしの初回準備は未確認 |
| LED・console・GPIO loader 入口 | LED0 点灯、`RBOS 0.1.0+0`、`nRF_BM_MCUmgr` の広告、RESET で app 復帰 | banner は `My Application`。VCOM は二段階の有効化が必要だった |
| 通常更新 | 全体 erase と鍵の再準備なしで v0.1.1 起動 | `ERASE_RANGES_TOUCHED_BY_FIRMWARE` を使用。保存データの維持は未確認 |
| BLE DFU（P0 外） | iOS app が upload の Success を表示 | 導入済みと同じ版。DFU した image が起動したかは区別できない |
| recovery sample | 起動 log と `nRF_BM_Entry` の広告を確認。RBOS の再書き込みで復帰。追記報告では nRF Connect Device Manager Android の Switch to Firmware Loader Mode（Boot Mode=1）も成功 | MCUboot の再起動後に `BLE MCUmgr sample started` と `Advertising as FL_12345` を確認。`Booting firmware loader` 行はこの build では出ない |

### P0 の受け入れ判定

P0 は閉じられると判断します。[段階計画](porting-plan.md#p0-bm-の再現可能な基盤)の受け入れ条件との対応は次のとおりです。

- clean workspace からの build と、同じ commit を CI / ローカルで build した debug 成果物の一致は、既存の commit `5664b86` の記録で確認しています（[build 再現手順](bm-build.md)）。今回のローカル v0.1.1 の hash でこの証拠を置き換えません。
- DK 上の LED / console / loader 入口は、今回の利用者報告でそろいました。recovery sample の flash、起動、BLE 広告も確認されました。
- 初回準備の破壊的な全体 erase と、通常更新を分けました。通常の script / CI に自動 erase は追加していません。

これは P0 の受け入れ条件の判定で、checklist 全項目や DFU の検証完了を意味しません。保存データの維持、erase なしの初回準備、DFU 後の新 image 起動は未確認のままです。Device Manager からの loader 遷移は、2026-11-09 JST の追記報告で Android による成功を確認しました。

### 残るリスクと P1 への提案

1. toolchain の版と west の workspace は別々に確認します。workspace の外で別の NCS が選ばれた失敗を、P1 の手順でも防ぎます。
2. USB に VCOM が現れることと、Board Configurator の VCOM0 / VCOM1 の有効化を分けて確認します。無出力だけで app の起動失敗とは判断しません。
3. P1 で boot banner の application 名を RBOS と分かる表示にする案を検討します。`CONFIG_BOOT_BANNER` 周辺の設定と app 名の指定方法を確認してから決める提案で、今回は code を変えていません。
4. 版と署名済み image を区別できる DFU 試験を P5 で行います。同じ版の upload 成功だけで、新 image の起動成功とは扱いません。保存データも既知の内容を書いて前後を比較します。
5. P1 の mruby/c 結合後も、この LED / console / loader 入口を再確認し、debug / release の map 増分と時間・stack/pool の実機計測へ進みます。開発用鍵での今回の成功を release 鍵の実機検証に流用しません。
6. iOS の nRF Connect Device Manager は、利用者の画面録画による報告で Send Reset Command の直後に crash しました。広告名 `FL_232659` の設定は済みましたが reset は起きていません。app のバージョンは未記録です。この環境では Android app を使い、広告名の設定だけを reset や loader 遷移の成功と扱いません。一般的な iOS の不具合や firmware の失敗とは断定しません。

## CI artifact の保存

2026-11-09 に [workflow](../../.github/workflows/firmware.yml) と [収集 script](../../tools/bm-build/collect-evidence.sh) を照合しました。debug / release の matrix が、module SHA、`zephyr.map`、`.config`、`build_info.yml`、compiler/tool のバージョン、`SHA256SUMS` を含む `firmware-evidence-<variant>-<sha>` を7日間保存します。`.pem` と `keyfile.json` は収集対象から除外し、upload 前にも混入を検査します。

[run 42620432714](https://github.com/uist1idrju3i/RBOS/actions/runs/42620432714) の debug / release artifact が存在し、期限が7日後であることを GitHub API でも確認しました。debug artifact は利用者が DK 書き込みに使ったものです。P0 と同内容の P6 の保存項目も完了に訂正しました。stack/pool 使用量や長時間試験ログの保存は別項目で、今回の確認に含めません。

[正式 release workflow](../../.github/workflows/firmware-release.yml) には90日間の artifact 保存設定があります。ただし、正式署名の実行や期限を超える長期保管の運用を確認したわけではありません。通常 CI の7日間の保存を、その完了の証拠にはしません。

[調査索引へ戻る](../README.md)
