---
layout: page
title: RBOS — Ruby Bytecode OS
---
{% include nav.html %}

## Ruby を主役にする組み込み OS

RBOS（Ruby Bytecode OS）は、mruby/c の VM と rrt0 scheduler を OS の中核に置くプロジェクトです。Nordic の nRF Connect SDK Bare Metal 上で、複数の Ruby task を動かす構成を研究しています。

目標は、製品開発者が主に Ruby を書き、通常は C を編集せずに利用できることです。DeviceTree などの board 設定は必要です。周辺機器への接続や Ruby API は RBOS 側で整備する方針です。

## 現在の状況

研究・実装準備の段階です。技術調査、Wasm 上の mruby/c smoke CI、共有 Ruby API の登録入口と backend の土台があります。nRF 用の RBOS firmware、実際の device API、system-task の権限モデルはまだ実装されていません。

CI は task・Mutex・例外処理などを確認しますが、実機の動作、BLE、DFU、消費電力を保証するものではありません。製品への導入手順が完成している段階ではありません。

## 対象ハードウェア

対象は **Nordic Semiconductor nRF54L15-DK** です。central は使わず、SoftDevice は **S115** を選びます。想定する board target は次のとおりです。

```text
bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot
```

初期構成では Ruby bytecode を build 時に firmware へ結合し、firmware の single-bank DFU で更新する方針です。OpenBlink 対応は将来計画です。

## 詳しく知る

- [構成とタスクモデル]({{ '/architecture.html' | relative_url }})
- [ロードマップ]({{ '/roadmap.html' | relative_url }})
- [開発・参加]({{ '/development.html' | relative_url }})
- [GitHub リポジトリ](https://github.com/uist1idrju3i/RBOS)
- [README](https://github.com/uist1idrju3i/RBOS/blob/main/README.md)
- [調査索引・判断記録](https://github.com/uist1idrju3i/RBOS/blob/main/research/README.md)
