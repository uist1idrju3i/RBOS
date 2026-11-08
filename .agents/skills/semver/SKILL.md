---
name: semver
description: RBOSのpublic API、依存、版、CHANGELOG、公開準備を変更するときに使う。SemVerとMCUboot image versionを区別し、互換性と公開権限を確認する。
---

# RBOS の版管理

[承認済み判断](../../../research/architecture/decisions.md)と [版管理調査](../../../research/release/versioning.md)に従います。規格は [SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)。今は採番せず、application を追加する PR で VERSION を作り、最初の build 可能な firmware に 0.1.0 を付けます。

## 変更の分類

1. 変更前の契約と変更後の契約を並べ、影響する public API 項目を PR に記載します。Ruby class/method の名前・引数・default・返り値・例外・待機、対応する Ruby の範囲と mrbc/mruby/c の版、board 設定規約が対象です。C backend は内部契約。DFU/MCUmgr は実装した時点で public API に追加します。
2. 実装の差分ではなく、宣言した契約への影響で次の表から増分を選びます。複数の変更があれば最大の増分を採用し、MINOR 更新時は PATCH、MAJOR 更新時は MINOR/PATCH を 0 に戻します。
3. 非推奨は API 文書と CHANGELOG の Deprecated に、代替と移行方法を明記します。削除は少なくとも1回の MINOR release の猶予を経てから行い、その版を PR で確認します。0.x でも猶予を省きません。削除の増分は非互換変更として判定します。
4. mruby/c・mrbc・sdk-nrf-bm 等の更新は [vendor-update](../vendor-update/SKILL.md)で上流の変更履歴を調べ、宣言した Ruby/board/更新契約への影響を検査します。依存先の MAJOR/MINOR をそのまま RBOS に転記しません。Wasm 成功を nRF 実機の互換性の証拠にしません。

| 変更 | 0.y.z（RBOS 独自規則） | 1.0.0 以降 |
|---|---|---|
| 非互換変更・削除 | 0.MINOR | MAJOR |
| 互換追加 | PATCH | MINOR |
| 互換 bug fix | PATCH | PATCH |
| 互換の非推奨化 | PATCH、削除までの MINOR の猶予は別に確認 | MINOR |
| 内部・文書のみで契約への影響なし | その変更だけを理由に増分しない | 同左 |

0.y.z を安定 API と見なさない SemVer の規則と、上の RBOS の増分規則を区別します。権限や待機時間などの変更も契約に影響し得るため、名前や引数が同じという理由だけで互換と判定しません。

## VERSION と署名 image の対応

VERSION は application root、利用者向けの変更記録は [CHANGELOG.md](../../../CHANGELOG.md)に置きます。以下は形式の例で、現在の firmware の版ではありません。

| 正本の値・生成物 | 例と確認内容 |
|---|---|
| VERSION_MAJOR / VERSION_MINOR / PATCHLEVEL | 1 / 2 / 3 → X.Y.Z |
| EXTRAVERSION | rc.1 → 人向け SemVer は 1.2.3-rc.1。正式版は空 |
| VERSION_TWEAK | 4。同じ X.Y.Z の配布 image ごとに単調増加。rc→正式版でも再利用しない |
| APP_VERSION_STRING | 1.2.3-rc.1 |
| APP_VERSION_EXTENDED_STRING | 1.2.3-rc.1+4 |
| APP_VERSION_TWEAK_STRING | 1.2.3+4。CONFIG_MCUBOOT_IMGTOOL_SIGN_VERSION から署名へ渡す |
| app_version.h の数値 macro | APP_VERSION_MAJOR / APP_VERSION_MINOR / APP_PATCHLEVEL / APP_TWEAK。APP_VERSION_TWEAK と混同しない |

数値4項目が整数の 0–255 に収まることを検査します。MCUboot header の revision/build の容量が大きくても、この入口の制限を緩めません。TWEAK を wrap・再利用せず、255 に達したら次の版と更新経路を決め直します。

通常版は X.Y.Z、先頭ゼロなし。pre-release は空でない dot 区切りの ASCII 英数字・hyphen、数値識別子に先頭ゼロなしで検査し、さらに EXTRAVERSION の lowercase a-z・数字・dot・hyphen 制限も満たします。build metadata は優先順位を変えません。imgtool は pre-release や任意の文字列 metadata を受け付けないため、SemVer 全文を --version へ渡しません。

TWEAK の増加は一意化であり、SemVer の順序や rollback 防止ではありません。BM MCUmgr の upgrade=true は build を比較せず、同じ X.Y.Z の rc→正式版を拒否します。配布前にこの更新経路を検証し、security counter の設定・初期化・更新も別に確認します。未検証を保証済みと記録しません。

## CHANGELOG と公開準備

1. 利用者に影響する変更は同じ PR の Unreleased に日本語で記録します。[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)に従い、必要な Added / Changed / Deprecated / Removed / Fixed / Security に分類します。内部 commit の列挙や存在しない release 履歴を作りません。
2. 公開準備では VERSION、SemVer 表示、CHANGELOG の版を照合し、release 日と版間の比較リンクを付け、先頭に次の Unreleased を残します。通常 tag 名は vX.Y.Z、pre-release は vX.Y.Z-rc.N 等。SemVer 本体に v は含めません。
3. 対応表に SemVer 全文、git commit、board/設定、署名 image の X.Y.Z+TWEAK、security counter（未使用・未検証も明記）、artifact の SHA-256 を記録します。最終 .config、生成 header、実際の signing command、署名 artifact の header を照合します。
4. 変更を覆う repo の検査、必要な firmware build・署名・更新試験を行い、結果と未確認の条件を報告します。未実施なら公開可能と判断しません。Ruby の検査は [ruby-idiomatic](../ruby-idiomatic/SKILL.md)、API の契約は [io-api-guideline](../io-api-guideline/SKILL.md)も使います。
5. 管理者が tag ruleset の v* 作成権限・bypass 方針を確認します。調査時点では全 tag 作成が制限されています。agent は ruleset を変更せず、tag 作成・GitHub Release 公開も行いません。
6. 管理者が対象 commit に tag を作成し、CHANGELOG に対応する説明、成果物、hash を公開します。公開済みの版・tag・成果物を書き換えず、修正は新しい版にします。

完了条件は、影響する契約と増分の根拠、必要な CHANGELOG、版の対応、検査結果と未確認の条件が PR に揃い、agent が tag/release を作成していないことです。
