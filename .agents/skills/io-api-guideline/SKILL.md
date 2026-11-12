---
name: io-api-guideline
description: GPIO・ADC・PWM・UART・I2C・SPIなどの周辺機器Ruby APIを追加・変更するときに使う。MPIG互換、pin、待機と資源の契約を先に決め、RBSとWasm fakeの検査をそろえる。
---

# Common I/O API に沿う周辺機器 API

この skill は Ruby API の契約を扱います。C の登録・引数検査・所有権の実装手順は [ruby-api-binding](../ruby-api-binding/SKILL.md)、製品 Ruby の書き方は [ruby-idiomatic](../ruby-idiomatic/SKILL.md)へ委ねます。現在は GPIO・内部三電源 ADC と pin resolver、独自の Temperature/Button を実装しています。外部 pin ADC・PWM・UART・I2C・SPI は未実装です。

周辺機器の実装を広げる前に [BM preflight](../../../research/implementation/development-gates.md) を実行します。公開 API を追加したら、RBS と [契約・試験在庫](../../../research/implementation/api-contracts.json)を更新し、PR 前に異常系・寿命・必須 PASS を検査してください。実装・host/Wasm・BM build・実機受け入れの状態を分けます。

正本は [MPIG 固定版](https://github.com/mruby/microcontroller-peripheral-interface-guide/tree/514497cfe184edda842f4410cd0eaee1acbdfb9c)。読み方・版は [調査の入口](../../../research/io-api/overview.md)、意味の詳細は [GPIO・ADC・PWM](../../../research/io-api/gpio-adc-pwm.md) / [UART・I2C・SPI](../../../research/io-api/serial-buses.md)を参照します。community の実装例を正本の代わりにしません。

## 契約を先に決める

1. **MPIG との照合**: class/method 名、位置・keyword 引数、alias、定数、default、単位、返り値、例外、待機を正本と照合します。GPIO の必須 mode 不在の ArgumentError と write_at の範囲外の RangeError、ADC の read/read_voltage と Float 無効時の NotImplementedError、PWM の duty % と 0 停止、UART の指定長待機と flush、I2C の 7-bit master / repeated start、SPI の 8-bit master / zero dummy / CS は GPIO、を落としません。UART の default は可能なら 9600 8N1・flow control なし、I2C は 100 kHz、SPI は 1 MHz / mode 0 / MSB_FIRST です。
2. **対応範囲と拡張**: 任意 low-level method、非対応の parameter・mode・pin を明示します。`scan` / `timeout:` / `ALT` / 自動 CS 等は MPIG の標準と表示せず、名前・引数・default・結果が標準と衝突しない RBOS 拡張として記録します。既存の標準 method の意味を黙って変えません。本文に未規定の戻り値や例外は設計判断と区別します。
3. **pin**: [承認済み方針](../../../research/architecture/decisions.md)に従い、Integer の `port*32+pin`（P1.13 = 45）、String の `"P1.13"`、DeviceTree-label Symbol の `:led0` / `:sw0` を受け付けます。同じ物理 pin に解決されることを検査し、存在しない名前・範囲外・非対応機能・予約 pin の結果を定義します。DT node label / alias / label property、active-low の扱いはその実装 PR で明示します。unit の id にまで同じ契約を自動適用しません。
4. **資源と失敗**: binding を書く前に physical instance と buffer の owner、busy、timeout/cancel、permission、最大長、queue 上限、部分転送、解放時点を定義します。nil・空 String・false・0・例外を混同せず、標準の失敗と拡張の失敗を分けます。認可は native/system task で確認し、Ruby の private に頼りません。具体的な error hierarchy は実装 PR で決めます。
5. **待機**: blocking API は呼出し Ruby task を待たせ、rrt0 の他 task に実行機会を譲ります。単一 C method の spin / blocking driver 呼出しだけで実装せず、開始・待機・完了の分解、または owner/system task の経路を設計します。tick が C stack を自動保存するとは仮定しません。IRQ は bounded event を渡し、Ruby 呼出し・allocation/refcount・raise・task 操作は foreground 側で行います。[rrt0 連携案](../../../research/io-api/rrt0-integration.md)を確認します。
6. **RBS**: API と同じ PR で `sig/` の signature と契約在庫を追加・更新します。[mruby_io_types との比較](../../../research/io-api/rbs-comparison.md)を参照し、型記述だけで例外・待機を表したと見なしません。外部 RBS の pin 型には Symbol がなく、SPI#setmode の記述も本文より狭いことに注意します。
7. **binding と backend**: 契約が決まったら [ruby-api-binding](../ruby-api-binding/SKILL.md)に従い、共有登録と実 nRF / Wasm fake backend を実装します。I2C の repeated start、SPI の CS 範囲、UART の確認後の競合も transaction として扱い、String/DMA buffer を完了前に解放しません。[nRF 対応](../../../research/io-api/nrf54l15-mapping.md)の serial box と console/shell の競合を確認します。

## Wasm fake で契約を検査する

fake は単に成功を返す stub にせず、受理した設定、転送 byte 列、完了順、短い転送、失敗・busy・timeout・権限拒否を制御できるようにします。`tests/mruby/` の assertion と、必要な fake 側の観測を使い、少なくとも次を実行します。

| 対象 | 検査する契約 |
|---|---|
| 入力と default | 各 pin 形式、id、省略・alias・定数・単位。通常・空・nil・型違い・範囲外と、定義した例外 |
| 出力 | String の長さと byte、整数 count / bool / nil、部分転送、backend error。SPI write の nil と UART/I2C write の count を混ぜない |
| transaction | I2C の repeated start、SPI dummy zero と GPIO CS の順序、UART write の戻りと flush の完了の違い |
| 待機と競合 | 完了待ちの間も別 Ruby task が進むこと、同一 instance の二重利用・queue 上限、timeout/cancel 後の遅延 event |
| 寿命と認可 | buffer の保持・解放、task 終了・VM ID 再利用、権限がない呼出しの拒否と副作用がないこと |

test は compile だけでなく契約在庫の suite に追加し、check.sh の runner で実行します。通常の API 異常系は fixture 内で例外・戻り値・副作用を assertion し、成功で終えます。非対応構文の診断用 fixture だけを expect_failure に分け、単なる runtime crash を MPIG 適合として扱いません。実装済みの fixture と、実機だけで確認する項目を在庫で区別します。

## 帰属と完了確認

MPIG 文書は **CC BY 4.0**。引用・翻案する文書には原資料・版・ライセンス・変更したことを示し、mruby forum committee / Kyushu Institute of Technology / Shimane IT Open-Innovation Center（Copyright 2023）の帰属を保持します。[ライセンス一覧](../../../research/licenses.md)を確認してください。community-library 紹介部分は MPIG ライセンスの対象外で、コード転用時は各 library の条件を確認します。

完了には、API 契約・拡張の表示・RBS・fake の検査が同じ PR でそろい、emsdk 環境の `tools/mrubyc-wasm/check.sh` が成功していることが必要です。日本語文書は yomiyasu、Skill 更新時は check-skills / unittest / symlink / diff --check も確認します。Wasm で確認できない電気特性・DMA・IRQ・実効周波数・latency・電力は、実機で未確認と報告します。
