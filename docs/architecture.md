---
layout: page
title: 構成とタスクモデル
---
{% include nav.html %}

## 構成案

以下は実装を進めるための設計方針です。nRF 上での RBOS 動作を確認した完成構成ではありません。

```text
MCUboot
  ├─ slot0: RBOS application
  │    ├─ mruby/c VM + rrt0 scheduler
  │    ├─ Bare Metal HAL + shared Ruby bindings
  │    ├─ system Ruby tasks
  │    └─ user Ruby tasks
  ├─ slot1: BLE MCUmgr firmware loader
  └─ shared SoftDevice S115 / metadata / application storage
```

NCS Bare Metal の peripheral・timer・イベント処理を活用し、HAL と backend が Ruby API を実機につなぎます。Ruby task を別 RTOS の thread へ一対一で割り当てる構成ではありません。

## 起動と single-bank DFU

通常は MCUboot が slot0 の application を検証して起動し、更新時は独立した slot1 の firmware loader を使う設計です。slot1 は旧 application を保管する A/B bank ではありません。旧 image への自動 rollback を前提にしません。

更新方式は NCS Bare Metal の single-bank DFU に合わせます。署名鍵、復旧手順、切断・電源断時の動作を検証してから製品へ適用する必要があります。

## bytecode と RAM

mruby 4.0.0 の mrbc で Ruby を compile し、const 配列として firmware に link します。bytecode 本体を RAM へ全体コピーせず、RRAM から参照する方針です。独立した bytecode 保存・転送経路は初期構成に含めず、変更には firmware の再 build と DFU が必要です。

mruby/c の loader は元 bytecode への参照を保持しますが、IREP の管理情報、symbol、Ruby の実行時 String、task・register などは RAM を使います。RAM が不要になるわけではありません。最終的な linker 配置、alignment、メモリ使用量は実機で確認する課題です。

## タスクと権限

rrt0 は priority と同 priority 内の巡回を用いて VM を切り替えます。Ruby は sleep、pass、Mutex、join などを使って task を連携させます。tick と native callback の実行時間は応答性に影響するため、Wasm CI と実機 timing 試験の両方が必要です。

system task と user task の権限を分ける計画ですが、class を登録しただけではアクセス制御になりません。特権 method で caller の権限を検査し、task の生成・破棄に合わせて失効させる仕組みは今後の実装対象です。

## 根拠と詳細

- [構成・メモリ調査](https://github.com/uist1idrju3i/RBOS/blob/main/research/architecture/overview.md)
- [bytecode 埋め込み](https://github.com/uist1idrju3i/RBOS/blob/main/research/dfu/embedded-bytecode.md)
- [single-bank DFU](https://github.com/uist1idrju3i/RBOS/blob/main/research/dfu/single-bank-dfu.md)
- [mruby/c scheduler](https://github.com/uist1idrju3i/RBOS/blob/main/research/mrubyc/task-scheduler.md)
- [API と権限設計](https://github.com/uist1idrju3i/RBOS/blob/main/research/openblink/api-binding-patterns.md)
