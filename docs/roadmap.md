---
layout: page
title: ロードマップ
---
{% include nav.html %}

## 段階的な実装

期限を約束する release 計画ではありません。各段階で試験と制約を確認し、受け入れ条件を満たしてから次へ進む方針です。

| 段階 | 目標 | 主な確認点 |
|---|---|---|
| P0: build 基盤 | NCS Bare Metal の workspace と RBOS build 構成 | clean build、console、loader 入口、署名設定 |
| P1: OS の中核 | mruby/c HAL と BM イベント処理の接続 | 複数 task、idle、tick、SoftDevice と IRQ の共存 |
| P2: Ruby API | native class と共通の値・エラー規約 | 引数、所有権、backend の失敗、実機 peripheral |
| P3: 権限 | system task と user task の境界 | caller 検査、子 task、VM ID 再利用、破棄時の失効 |
| P4: bytecode 結合 | const bytecode を firmware に埋め込む | RRAM 配置、alignment、RAM 予算、失敗時の安全状態 |
| P5: firmware 更新 | single-bank DFU の結合 | 署名、再 DFU、切断・電源断、製造と復旧の手順 |
| P6: 品質 | CI、長時間試験、公開に必要な情報 | 実機試験との役割分担、ログ、license notice |

## すでにあるものと、これからのもの

mruby-wasm CI と共有 Ruby API の登録入口はあります。Wasm 上で task・Mutex・例外などを検査できますが、P0〜P5 の実機実装が完成したことを意味しません。nRF firmware の build CI、実機の長時間試験、DFU の fault injection は今後の課題です。

初期構成の後に、OpenBlink の BLE bytecode 転送、storage、動的 reload、外部 system bytecode の認証を検討します。現在の firmware 埋め込み方式と混同しません。

## 参加するときの資料

- [段階計画と受け入れ条件](https://github.com/uist1idrju3i/RBOS/blob/main/research/implementation/porting-plan.md)
- [実装前チェックリスト](https://github.com/uist1idrju3i/RBOS/blob/main/research/implementation/checklist.md)
- [採用・不採用の判断](https://github.com/uist1idrju3i/RBOS/blob/main/research/architecture/decisions.md)
- [将来の OpenBlink 対応](https://github.com/uist1idrju3i/RBOS/blob/main/research/openblink/future-support.md)
- [開発・参加]({{ '/development.html' | relative_url }})
