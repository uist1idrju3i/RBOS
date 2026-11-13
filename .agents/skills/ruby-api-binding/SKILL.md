---
name: ruby-api-binding
description: RBOSのRuby class・methodを共有C bindingとbackendで追加し、Wasmで引数・所有権・権限を検査するときに使う。
---

# RBOS の Ruby API 追加

RBOS では mruby/c が scheduler です。製品開発者が Ruby を中心に実装し、通常は C を編集せずに使えることを目指します。DeviceTree などの board 設定は必要です。C binding と backend の整備は RBOS 側の開発作業です。

## 配置と登録

| 対象 | 場所・契約 |
|---|---|
| 共有 binding | `src/rbos/`。Ruby の class/method は nRF と Wasm で同じ C を使う |
| 登録入口 | `include/rbos/bindings.h` の `rbos_define_classes(backend)`。`src/rbos/bindings.c` から各登録関数を呼ぶ |
| backend 契約 | `include/rbos/backend.h`。context と GPIO/Button・温度・ADC・event の operation |
| Wasm fake | `tools/mrubyc-wasm/backend.c`。hardware operation の追加時に fake も実装する |
| nRF 実装 | `src/platform/nrf/`。実機用 backend を link し、共有 binding から Nordic の header を直接 include しない |

GPIO/Button・Temperature・内部三電源 ADC を登録済みです。runner と nRF は `mrbc_init()` の後、task 作成前に一度だけ登録関数を呼びます。

[開発・証拠検査](../../../research/implementation/development-gates.md)に従い、公開 API は RBS・契約在庫・異常系と寿命の試験を同じ PR に揃えます。`check-contracts.py` は共有 C/Ruby だけに増えた公開面や、必須 PASS の欠落も拒否します。内部 helper の名前・理由も明示し、内部という表示を認可として扱いません。

## 追加手順

GPIO・ADC・PWM・UART・I2C・SPI 等の周辺機器では、先に [io-api-guideline](../io-api-guideline/SKILL.md)で MPIG・RBS・待機・資源の契約を決めてから、以下の C binding 手順へ進みます。

1. Ruby 側の class/method 名、引数・戻り値・例外、公開範囲を決めます。引数の省略、nil、型違い、範囲外、backend failure の契約も定義します。
2. `src/rbos/` に callback と登録処理を置きます。`mrbc_define_class(NULL, "Example", NULL)` で class を作り、`mrbc_define_method(NULL, cls, "method", callback)` で登録します。callback は `void callback(mrbc_vm *vm, mrbc_value v[], int argc)` です。`rbos_define_classes()` から登録してください。これは命名例で、Example を実装済み API として扱いません。
3. argc を調べてから `v[1]` 以降を参照し、型と範囲を検査します。借用値を返すときの incref、生成値の移譲、container・String の所有権を確認します。例外を設定したら後続の処理を止めます。[C API 規約](../../../research/mrubyc/c-api.md)の ownership・keyword 引数も確認してください。
4. hardware access が必要になった時点で backend に必要な operation を定義します。context の寿命、戻り値、失敗・busy の表現を揃え、Wasm fake と nRF backend を実装します。fake の状態で成功・失敗を再現し、共有 callback に環境分岐を散らしません。
5. system-task 専用操作は callback の入口で caller VM の権限を検査します。class の登録だけでは保護されません。子 task・VM ID 再利用・破棄時の失効も考慮します。[権限設計](../../../research/openblink/api-binding-patterns.md)と [HMAC 調査](../../../research/openblink/hmac-authentication.md)を参照してください。認証・権限モデルは未実装です。
6. `tests/mruby/` に Ruby script を追加します。正常・空・不正入力、fake の失敗、非特権 VM を検査します。`check.sh` は直下の全 `.rb` を compile しますが、**実行する script は明示的に列挙**しています。新しい正常系は runner の実行引数へ追加するか、別の timeout 付き実行を追加してください。失敗 fixture は `expect_failure` で終了値と診断を照合します。
7. emsdk 環境で `tools/mrubyc-wasm/check.sh` を実行します。`src/rbos/` 以下の `.c` は自動で Wasm に link されます。新規ファイルを nRF build に含める作業は firmware build 導入時に必要です。Wasm だけで実機の IRQ・BLE・timing を検証済みとはしません。

## 完了確認

- Ruby で呼び出す API は共有 binding に一度だけ実装し、vendor を編集していない。
- 正常系・空入力・エラー系の Ruby test が compile だけでなく実行される。
- backend の失敗と権限拒否が正常値と区別できる。
- `python3 .github/scripts/check-skills.py`、`python3 -m unittest discover -s tests/check-skills`、`git diff --check` を実行した。
- 日本語文書を yomiyasu で確認し、実機で未確認の項目を報告する。

[Wasm 検査手順へ戻る](../../../tools/mrubyc-wasm/README.md)
