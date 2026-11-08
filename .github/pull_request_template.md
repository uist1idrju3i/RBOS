## 変更内容

<!-- Describe the user-facing change in Japanese. -->

## Public API と版の増分

- 影響する public API 項目（Ruby class/method、Ruby/mrbc/mruby/c 対応、board 設定、実装済みの DFU/MCUmgr。影響なしの場合はその理由）:
- 変更前と変更後の契約、互換性の判断:
- 版の増分（なし / PATCH / MINOR / MAJOR）と理由。0.x は非互換が MINOR、互換追加・修正が PATCH:
- 非推奨・削除の場合の移行方法と、少なくとも1回の MINOR release の猶予:

[semver skill](https://github.com/uist1idrju3i/RBOS/blob/main/.agents/skills/semver/SKILL.md)の規則を確認してください。

## 検査と未確認の条件

- 実行したコマンドと結果:
- 未確認の実機動作・更新経路など:

## 確認事項

- [ ] 利用者に影響する変更を CHANGELOG.md の Unreleased に記録した（対象外なら理由を本文に記載）
- [ ] VERSION を変更する場合、数値4項目の 0–255 と image version・TWEAK の対応を確認した
- [ ] agent は tag 作成・release 公開を行っていない
