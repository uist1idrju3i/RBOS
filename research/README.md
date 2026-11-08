# 実装前調査

[プロジェクトの README](../README.md)

## 目的と読み方

RBOS の実装に必要な仕様、参照実装、制約、試験項目をまとめます。実装はまだ始めていません。調査日と利用者による方式決定日は 2026-11-08 です。

- **確認済み（資料）**: 固定したソースまたは公式文書から読み取れた内容です。動作確認を意味しません。
- **設計案**: RBOS でこれから実装・評価する方針です。上流が保証する仕様とは区別します。
- **未確認**: 本リポジトリでは試していない内容、外部資料との照合が済んでいない内容です。
- `vendor/...:開始行-終了行` は、この調査で固定した submodule 内の出典です。OpenBlink は固定 SHA の公開リンクを使います。

この調査ではビルド、実機への書き込み、電源断、BLE 通信、電波認証の照合を実施していません。文書の検査結果を実機試験の代わりに扱わないでください。

## 資料の版

以下の SHA は調査時の `git submodule status` と `.gitmodules:1-16` に基づきます。依存を更新したら、版と引用行も更新します。

| 資料 | 固定した版・commit | 用途 |
|---|---|---|
| RBOS 調査開始点 | `e20433c5c9793f71e9d5548d5b093d395eee7d8a` | README・開発規約の基準 |
| mruby/c | `434bccd609f2a3e90d6bb95c458621898bc6a508` | VM・スケジューラ・C API |
| nRF Connect SDK Bare Metal | v2.0.1 / `51484143c09199e19bccc16fa3b437f7a502a72b` | 公式の開発・DFU 基盤 |
| mruby | 4.0.0 / `831da26b9021de0369d17b71b5667e2941a1a32d` | host mrbc、RITE0400 |
| MCUboot（west 経由） | `fce4dac2e6295cf98bd02a85f7c4254f6102106d` | NCS v3.3.0 の ncs-v3.3.0、ブート処理と署名 |
| yomiyasu | `29d67ccb05e370b5958d72920a9cd1aa829dee80` | 日本語推敲 |
| OpenBlink demo-nrf（主参照） | [`6d22b676d2cf4bc599a7709ecebaa1b890af9e3a`](https://github.com/OpenBlink/openblink-demo-nrf/tree/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a) | nRF54L15、native API、停止経路 |
| OpenBlink MDBT（補助） | [`d6efc07877ebac6bd55519b8458be4629bef80c3`](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/tree/d6efc07877ebac6bd55519b8458be4629bef80c3) | Ruby と C の接続例 |

公式サイトの [latest](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/index.html) は可変です。2026-11-08 の調査記録では v2.0.99、sdk-nrf-bm main `14b3836` 由来でした。[single-bank DFU の章](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/app_dev/dfu/single_bank_dfu.html)の方式は固定版 v2.0.1 と同じく single-bank です。再現の基準は latest ではなく上表の固定版とします。固定版の明記は `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:6-24` を参照してください。

## 決定事項

| 日付 | 決定 | 文書 |
|---|---|---|
| 2026-11-08 | mruby/c を OS の中核とし、rrt0 で Ruby タスクを多重化 | [タスク](mrubyc/task-scheduler.md) |
| 2026-11-08 | nRF54L15-DK と NCS Bare Metal を使用 | [ハードウェア](hardware/nrf54l15-dk.md) |
| 2026-11-08 | 公式 single-bank DFU、MCUboot + BLE MCUmgr firmware loader | [DFU](dfu/single-bank-dfu.md) |
| 2026-11-08 | `.mrb` は const 配列で firmware に結合し RRAM から実行。旧 storage 方針を置換 | [バイトコード](dfu/embedded-bytecode.md) |
| 2026-11-08 | ファームウェア A/B とバイトコード A/B は検討して不採用 | [判断の記録](architecture/decisions.md) |
| 2026-11-08 | central 不使用、S115 固定。OpenBlink 対応は将来 | [判断の記録](architecture/decisions.md) |

方式決定の根拠は利用者の指示です。調査更新日は 2026-11-08 JST です。権限の具体策は未決定です。emscripten HAL の Ruby 検査 CI は後続作業で実装しました。[検査手順](../tools/mrubyc-wasm/README.md)を参照してください。

## 文書一覧

| 分野 | 文書 |
|---|---|
| 全体設計 | [構成・起動・メモリ](architecture/overview.md)、[採否と未決事項](architecture/decisions.md) |
| ボード | [nRF54L15-DK](hardware/nrf54l15-dk.md) |
| mruby/c | [版とビルド](mrubyc/overview-and-build.md)、[タスク](mrubyc/task-scheduler.md)、[HAL 移植](mrubyc/hal-porting.md)、[C API](mrubyc/c-api.md)、[設定とメモリ](mrubyc/configuration-and-memory.md) |
| OpenBlink | [構成と再ロード](openblink/architecture.md)、[API と権限](openblink/api-binding-patterns.md)、[HMAC](openblink/hmac-authentication.md)、[将来対応と保存](openblink/future-support.md) |
| NCS Bare Metal | [開発環境](nrf-bm/setup-and-build.md)、[SoftDevice と割り込み](nrf-bm/softdevice-and-interrupts.md)、[ライブラリ](nrf-bm/libraries.md) |
| 更新と保存 | [single-bank DFU](dfu/single-bank-dfu.md)、[MCUboot](dfu/mcuboot.md)、[埋め込みバイトコード](dfu/embedded-bytecode.md) |
| 実装準備 | [段階的計画](implementation/porting-plan.md)、[着手前チェックリスト](implementation/checklist.md) |
| 配布条件 | [ライセンス](licenses.md) |

先に全体設計と判断の記録を読み、次に担当する分野へ進んでください。各文書末尾からこの索引へ戻れます。
