# BM と Nordic toolchain の更新監視

[調査索引](../README.md) / [toolchain 方針と比較](toolchain-container.md)

## 目的と範囲

`tools/vendor-release-watch.py` の週次通知を拡張します。正式 release tag と gitlink の比較に加え、新しい BM の `west.yml`、対応する sdk-nrf と toolchain、固定 bundle tag の digest 変化を確認します。通知だけを行い、gitlink・workflow・bundle・image の固定値は変更しません。

対象は Linux x86_64 の公式 toolchain です。nrfutil の実行、Nordic アカウント、Docker login は不要です。GitHub Issue を変更する場合だけ、従来どおり対象 repository の `GITHUB_TOKEN` を使います。

## 公開 metadata の調査

2026-11-16 に以下の応答を確認しました。

| 情報 | 公開 URL と形式 |
|---|---|
| sdk-manager の toolchain index | [index-linux-x86_64.json](https://files.nordicsemi.com/artifactory/NCS/external/bundles/v3/index-linux-x86_64.json)。配列の `json_api_version=2`、`key` が SDK tag または bundle id、`metadata.version` が bundle id |
| BM manifest | [v2.0.1/west.yml](https://raw.githubusercontent.com/nrfconnect/sdk-nrf-bm/v2.0.1/west.yml)。`manifest.projects` の `nrf` / `repo-path: sdk-nrf` に `revision: v3.3.0` |
| GHCR anonymous token | [pull token endpoint](https://ghcr.io/token?service=ghcr.io&scope=repository:nrfconnect/sdk-nrf-toolchain:pull)。匿名の pull scope を要求し、token は出力・保存しない |
| image tags | [tags/list](https://ghcr.io/v2/nrfconnect/sdk-nrf-toolchain/tags/list)。取得には上記 Bearer token を使う |
| digest | [bundle manifest](https://ghcr.io/v2/nrfconnect/sdk-nrf-toolchain/manifests/911f4c5c26)。`Docker-Content-Digest` と取得本文の SHA-256 を照合 |

index の URL は sdk-manager の toolchain index 設定と通信 log から特定し、認証情報なしの HTTPS GET で確認しました。実装は個人環境の設定を参照せず、上記の公開 index を取得します。

公式 image には SDK tag（例 `v3.3.0`）と10桁の bundle id tag（例 `911f4c5c26`）があります。初期の SDK には `2.4.1` のような例外もあるため、SDK tag の文字列から image tag を推測しません。index で bundle id に解決して、その id の manifest を取得します。`latest`、preview、RC を更新候補にはしません。

確認した対応は以下です。

- sdk-nrf `v3.3.0` と `v3.3.5` → bundle `911f4c5c26`。
- sdk-nrf `v3.4.2` → bundle `197d1ad490`。
- image の `911f4c5c26` と `v3.3.0` → `sha256:f24d8932ff081ebcd8da9c248f4449bdabe461c0620a7a4ac9e95eb577ba2276`。

tag 一覧はページ分割されます。watcher は一覧全体を走査せず、index の bundle id を直接指定します。manifest は OCI index、Docker manifest list、OCI/Docker 単一 manifest を Accept し、返された最上位 manifest の digest を比較します。platform 子 manifest や展開後の rootfs の比較ではありません。

## 検査と通知

1. 固定 digest は `.github/workflows/firmware*.yml` の公式 image 参照から、固定 bundle は `.github/actions/ncs-bm-setup/action.yml` の SDK path 検査から取得します。空・複数の不一致は失敗です。
2. 固定 bundle id の index entry と同名の GHCR tag を毎回確認。digest が repository の固定値と違えば通知候補にします。
3. 固定 BM より新しい正式 tag ごとに raw GitHub の `west.yml` を取得。sdk-nrf 正式 revision を抽出し、index → bundle → image digest と解決して BM の Issue 本文へ記載します。
4. sdk-nrf が `v3.4.x` なら、[既存方針](toolchain-container.md)に従って BM と toolchain を一緒に LTS へ更新できることを明記します。採用前の互換性・build・ライセンス・実機検査は省略しません。
5. 新 BM の bundle または digest が固定値と違う場合も、toolchain の差分 Issue の対象にします。同じ bundle/digest なら新 BM 通知だけです。

toolchain 通知は固定タイトルの Issue 一つを作成・更新します。body 内の fingerprint は固定値と検出差分の JSON から作ります。同一状態の open Issue は書き直しません。closed Issue の同一 fingerprint は見送りを維持し、異なる fingerprint なら再度開きます。marker を認識できない closed Issue は従来の正式 release 通知と同様に維持します。

正式 release の Issue は従来の tag/version による重複抑止を維持します。新 BM の対応関係が変わっても、同じ BM 版で閉じた release Issue を勝手に開きません。toolchain 差分は別の通知として扱います。

## 実行と失敗時

```sh
python3 tools/vendor-release-watch.py --json vendor-releases.json
```

上のコマンドは Issue を変更しません。週次 workflow だけが `--update-issues` を付け、月曜03:23 UTC に実行します。従来の workflow・権限で足りるため変更しません。

HTTP error、timeout、不正 JSON、対応なし・重複した index entry、不正 manifest/digest は `FAIL`、終了値1です。通信失敗を「新版なし」に置き換えません。west.yml は現行の block 形式と正式な `vX.Y.Z` revision を対象とする限定 parser です。YAML anchor、inline mapping、commit SHA への形式変更は失敗させ、手動で評価します。

offline unittest は fetch を mock し、正常・候補なし・固定 tag drift、新 BM の別 bundle/LTS、digest 本文検証、通信/metadata 失敗、Issue の作成・重複・再通知を検査します。実通信の `--json` 実行も行いますが、実 Issue の作成・再開は行いません。

## 対象外と版管理

- sdk-nrf 単独の新版一覧、BM の prerelease、固定 bundle 以外の全 image tag の変化は監視しません。
- index の bundle 対応は公開 metadata として信頼します。image 内 compiler と bundle 内容の一致、再 build、実機互換性を証明する検査ではありません。
- image digest の変化は改ざんの断定でも更新許可でもありません。原因を調べ、人が採否を判断します。
- firmware の public API と実行部分を変えない内部通知の拡張なので、semver skill に従い VERSION/CHANGELOG は更新しません。
