# 実装前調査

[プロジェクトの README](../README.md)

## 目的と読み方

RBOS の実装に必要な仕様、参照実装、制約、試験項目をまとめます。P0 の記録に続き、P1 の mruby/c 結合・BM HAL・BLE の実装と debug/release build、Wasm の自己検査まで進めました。利用者による P1 CI debug image の DK 自己検査・BLE 接続中の区間統計も記録しています。release の実機起動や高負荷時の資源上限は未確認です。調査日と利用者による方式決定日は 2026-11-08 です。

- **確認済み（資料）**: 固定したソースまたは公式文書から読み取れた内容です。動作確認を意味しません。
- **設計案**: RBOS でこれから実装・評価する方針です。上流が保証する仕様とは区別します。
- **未確認**: 本リポジトリでは試していない内容、外部資料との照合が済んでいない内容です。
- `vendor/...:開始行-終了行` は、この調査で固定した submodule 内の出典です。OpenBlink は固定 SHA の公開リンクを使います。

SDK の build は [BM の再現手順と P1 map 比較](implementation/bm-build.md)に記録しました。P0 の実機操作は[利用者報告](implementation/dk-provisioning.md)と区別し、P1 の未確認項目は [P1 の振り返り](implementation/retrospective-P1.md)にまとめています。host の Wasm build と短い Ruby の実行結果は [mruby/c 能力確認](mrubyc/capability-probes.md)へ分離しました。文書の検査結果を実機試験の代わりに扱わないでください。

## Ruby らしさと共通 I/O API

実装済みの RBOS 拡張: [ダイ温度 API の契約・検査・未確認条件](implementation/temperature-api.md)。MPIG 六 class の実装完了や P2 全体の完了を意味しません。

三電源 ADC: [内部入力・協調待機・busy・DMA 寿命と検査の境界](implementation/adc-api.md)。外部 pin ADC と DK での検証は未完了です。

後続の `ruby-idiomatic` / `io-api-guideline` skill に先立つ調査です。skill 本体・RuboCop・六 class の実装は今回追加していません。

- Ruby: [原則と一次資料](ruby-style/principles.md)、[guide と VM の対応](ruby-style/idiom-compatibility.md)、[組込み idiom](ruby-style/embedded-idioms.md)、[外部の主張の照合](ruby-style/attachment-review.md)。
- 実行の証拠: [版・結果・hash](ruby-style/capability-probes.md)、[成功入力](ruby-style/probe-inputs.md)、[非対応入力](ruby-style/negative-probe-inputs.md)。
- I/O: [固定版と読み方](io-api/overview.md)、[GPIO・ADC・PWM](io-api/gpio-adc-pwm.md)、[UART・I2C・SPI](io-api/serial-buses.md)、[RBS](io-api/rbs-comparison.md)。
- 移植: [community 比較](io-api/community-comparison.md)、[nRF54L15 対応](io-api/nrf54l15-mapping.md)、[rrt0 待機案](io-api/rrt0-integration.md)。pin の承認済み方針は [設計判断](architecture/decisions.md)、出典の条件は [ライセンス](licenses.md)。

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

P2 の [資源予約と配送 context](implementation/resource-reservations.md)には、S115 の DPPI/PPIB 保護、GRTC/IRQ 検査、SD RAM と BM scheduler の診断・未確認項目をまとめています。

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
| mruby/c の Ruby 能力 | [Ruby-first の能力と制約](mrubyc/ruby-first-capabilities.md)、[Object 等](mrubyc/methods-objects.md)、[container](mrubyc/methods-collections.md)、[数値・文字列](mrubyc/methods-numeric-text.md)、[Task 等](mrubyc/methods-tasks.md)、[opcode](mrubyc/opcode-compatibility.md)、[Wasm 能力確認](mrubyc/capability-probes.md) |
| mruby/c の native 契約 | [値と class API](mrubyc/c-api-values.md)、[container API](mrubyc/c-api-collections.md)、[runtime API](mrubyc/c-api-runtime.md)、[所有権と binding](mrubyc/c-api-ownership.md)、[macro](mrubyc/compile-macros.md)、[メモリ予算](mrubyc/memory-and-sizing.md)、[task lifecycle](mrubyc/scheduler-lifecycle.md) |
| mruby/c の上流資料 | [test/sample/HAL/build](mrubyc/tests-and-samples.md)、[公式 Wiki との照合](mrubyc/official-document-comparison.md) |
| OpenBlink | [構成と再ロード](openblink/architecture.md)、[API と権限](openblink/api-binding-patterns.md)、[HMAC](openblink/hmac-authentication.md)、[将来対応と保存](openblink/future-support.md) |
| NCS Bare Metal | [開発環境](nrf-bm/setup-and-build.md)、[全 component・API・Kconfig 索引](nrf-bm/component-catalog.md)、[SoftDevice と割り込み](nrf-bm/softdevice-and-interrupts.md)、[ライブラリ案内](nrf-bm/libraries.md)、[samples](nrf-bm/samples.md)、[公式 latest 比較](nrf-bm/version-comparison.md) |
| 更新と保存 | [single-bank DFU](dfu/single-bank-dfu.md)、[MCUboot](dfu/mcuboot.md)、[埋め込みバイトコード](dfu/embedded-bytecode.md) |
| 実装準備 | [段階的計画](implementation/porting-plan.md)、[着手前チェックリスト](implementation/checklist.md)、[BM build 再現手順・P1 map](implementation/bm-build.md)、[DK の準備](implementation/dk-provisioning.md)、[署名鍵の手順](implementation/signing-keys.md)、[P0 の振り返り](implementation/retrospective-P0.md)、[P1 の振り返り](implementation/retrospective-P1.md) |
| 配布条件 | [ライセンス](licenses.md) |
| 版と公開 | [SemVer・VERSION・image の制約と承認判断](release/versioning.md) |

先に全体設計と判断の記録を読み、次に担当する分野へ進んでください。各文書末尾からこの索引へ戻れます。
