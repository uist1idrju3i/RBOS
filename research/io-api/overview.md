# Common I/O API 調査の範囲と版

MPIG（mruby, mruby/c Common I/O API Guidelines）は MCU を越えた Ruby program と sensor library の再利用を目指す共通 interface です。RBOS の Ruby-first 方針では、利用者が native driver の C 呼出しを書くのではなく、この共通語彙を Ruby から使えることを目指します。この文書は初回の比較調査です。後続の P2 で [GPIO/Button](../implementation/gpio-button-api.md)、[内部三電源 ADC](../implementation/adc-api.md)、[温度](../implementation/temperature-api.md)の binding と backend を実装しました。外部 pin ADC・PWM・UART・I2C・SPI は未実装で、実機の受け入れも未完了です。

## 読み分け

| 分類 | 本調査の扱い |
|---|---|
| MPIG 本文 | 共通の名前・引数・動作の基準。対応しない platform parameter や任意 low-level API もある |
| RBS | community の型記述。本文との照合資料であり、runtime 実装や全意味の保証ではない |
| community implementation | 採用例・差異・制約。`scan` / `timeout:` / `ALT` 等を MPIG 標準へ混ぜない |
| sdk-nrf-bm / nrfx / DTS | nRF backend の候補と予約資源。Ruby class が既にあることを意味しない |
| RBOS の決定 | GPIO の三形式 resolver・error 契約と実/fake backend は実装済み。具体的な現在の範囲は上記の P2 契約を参照 |
| 提案・未確認 | rrt0 待機の分解、cancel、bus 所有、実機 timing・電気的適合。確定事項から分離 |

## 固定した参照先

| 資料 | commit・公開参照 |
|---|---|
| MPIG | [`514497cfe184edda842f4410cd0eaee1acbdfb9c`](https://github.com/mruby/microcontroller-peripheral-interface-guide/tree/514497cfe184edda842f4410cd0eaee1acbdfb9c) |
| mruby_io_types | [`401ec111049bd9b3508893f29a3a1b35ca97a465`](https://github.com/poporonnet/mruby_io_types/tree/401ec111049bd9b3508893f29a3a1b35ca97a465) |
| rp2040-peripheral-demo | [`9641ddae51d04d5129c78a6df7e6df8b7da6d0b7`](https://github.com/picoruby/rp2040-peripheral-demo/tree/9641ddae51d04d5129c78a6df7e6df8b7da6d0b7) |
| PicoRuby | [`a8d170f2802ac0d88659a56e9390a94ac77b77e6`](https://github.com/picoruby/picoruby/tree/a8d170f2802ac0d88659a56e9390a94ac77b77e6) |
| mrubyc-esp32 | [`8a0971b04d9a4e104e1fe71375d5582491490a01`](https://github.com/gfd-dennou-club/mrubyc-esp32/tree/8a0971b04d9a4e104e1fe71375d5582491490a01) |
| pic32mx170_mrubyc | [`d91b359d0a3daf84c6490bce817e8ae638b9dfa4`](https://github.com/YoshihiroOgura/pic32mx170_mrubyc/tree/d91b359d0a3daf84c6490bce817e8ae638b9dfa4) |
| mrubyc-nucleo-L476RG | [`bfc6c6cb0c818aff66eb60da834f030f31a1cfa2`](https://github.com/HirohitoHigashi/mrubyc-nucleo-L476RG/tree/bfc6c6cb0c818aff66eb60da834f030f31a1cfa2) |
| mruby-esp32 | [`6fac2a45cf72a75e8ebc9e3e70026a3c41405ce2`](https://github.com/mruby-esp32/mruby-esp32/tree/6fac2a45cf72a75e8ebc9e3e70026a3c41405ce2) |

mruby/c・mruby・sdk-nrf-bm は [研究索引の固定版](../README.md)を使用します。community code は source 比較で、各 board の build・動作・完全な適合試験はしていません。別版の PicoRuby を demo の submodule へ混ぜて解釈しないことも重要です。

## 主題別の入口

- [GPIO・ADC・PWM](gpio-adc-pwm.md): mode、単位、返り値、例外、platform 差。
- [UART・I2C・SPI](serial-buses.md): defaults、binary String、blocking、任意 low-level API。
- [RBS との照合](rbs-comparison.md): 型で表せることと表せないこと、本文との差。
- [community 比較](community-comparison.md): pin、エラー、C binding、拡張、scheduler への影響。
- [nRF54L15-DK 対応](nrf54l15-mapping.md): serial box の排他、SDK/nrfx の経路、pin resolver。
- [rrt0 連携案](rrt0-integration.md): 待機中の他 task の進行、ownership、検証の条件。

本調査の MPIG 部分は mruby forum committee / Kyushu Institute of Technology / Shimane IT Open-Innovation Center（Copyright 2023）の文書を要約・翻案したもので、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) に従い元資料・版・変更を表示しています。community library はこのライセンスの対象外です。[個別ライセンス](../licenses.md)を確認してからコードを転用します。

[調査索引へ戻る](../README.md)
