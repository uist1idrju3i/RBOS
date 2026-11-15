# ライセンスと配布条件

本書は実装・配布時の確認項目であり、法的助言ではありません。ファイル単位の SPDX、同梱バイナリ、west の推移依存も配布前に確認します。

| 対象 | 主なライセンス | 根拠 |
|---|---|---|
| RBOS | BSD-3-Clause | `LICENSE:1-28` |
| mruby（host compiler） | MIT | `vendor/mruby/LICENSE:1-19` |
| mruby/c | BSD-3-Clause | `vendor/mrubyc/LICENSE:1-28` |
| OpenBlink demo-nrf | BSD-3-Clause | [LICENSE](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/LICENSE#L1-L28) |
| OpenBlink MDBT / HMAC | BSD-3-Clause | [LICENSE](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/LICENSE#L1-L28) |
| sdk-nrf-bm | LicenseRef-Nordic-5-Clause | `vendor/sdk-nrf-bm/LICENSE:1-40` |
| MCUboot | Apache-2.0 | [LICENSE](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/LICENSE#L1-L30) |
| yomiyasu | MIT | `vendor/yomiyasu/LICENSE:1-21` |
| ruby-style-guide | CC BY 3.0 Unported | [README の License](https://github.com/rubocop/ruby-style-guide/blob/72ea4198d617e5c3db425cb3806b68b71dcc129f/README.adoc#L6518-L6520) |
| MPIG 文書 | CC BY 4.0 | [README の License](https://github.com/mruby/microcontroller-peripheral-interface-guide/blob/514497cfe184edda842f4410cd0eaee1acbdfb9c/README.md) |
| mruby_io_types | MIT | [LICENSE.txt](https://github.com/poporonnet/mruby_io_types/blob/401ec111049bd9b3508893f29a3a1b35ca97a465/LICENSE.txt) |
| rp2040-peripheral-demo | MIT | [LICENSE](https://github.com/picoruby/rp2040-peripheral-demo/blob/9641ddae51d04d5129c78a6df7e6df8b7da6d0b7/LICENSE) |
| PicoRuby | MIT | [LICENSE](https://github.com/picoruby/picoruby/blob/a8d170f2802ac0d88659a56e9390a94ac77b77e6/LICENSE) |
| mrubyc-esp32 | MIT | [LICENSE](https://github.com/gfd-dennou-club/mrubyc-esp32/blob/8a0971b04d9a4e104e1fe71375d5582491490a01/LICENSE) |
| pic32mx170_mrubyc | BSD-3-Clause | [LICENSE](https://github.com/YoshihiroOgura/pic32mx170_mrubyc/blob/d91b359d0a3daf84c6490bce817e8ae638b9dfa4/LICENSE) |
| mrubyc-nucleo-L476RG | BSD-3-Clause | [LICENSE](https://github.com/HirohitoHigashi/mrubyc-nucleo-L476RG/blob/bfc6c6cb0c818aff66eb60da834f030f31a1cfa2/LICENSE) |
| mruby-esp32 | MIT | [LICENSE](https://github.com/mruby-esp32/mruby-esp32/blob/6fac2a45cf72a75e8ebc9e3e70026a3c41405ce2/LICENSE) |

## style guide・I/O 調査の帰属

[Ruby style 調査](ruby-style/principles.md)は rubocop/ruby-style-guide contributors の文書を要約しています。元資料、固定 commit、CC BY 3.0 を示し、説明・対応表・実行例を RBOS 向けに作成しました。原文の推奨を Ruby の言語仕様へ格上げせず、原著者の推奨を受けた製品とも表示しません。

[I/O 調査](io-api/overview.md)は MPIG 文書を要約・翻案しています。元資料の著作権表示は **Copyright (C) 2023 mruby forum committee; Kyushu Institute of Technology; Shimane IT Open-Innovation Center**。CC BY 4.0 に従い、原資料のリンク・固定版・ライセンスと変更したことを示します。CC BY の資料を参照しても、RBOS 本体すべてを同じライセンスへ変更するものではありません。

MPIG の community-library 紹介部分は MPIG 文書ライセンスの対象外と明記されています。community code、submodule、外部 gem は各権利者の条件を個別に確認します。今回コードは転用していません。将来転用する場合、MIT/BSD の表示・免責を保持し、PicoRuby / demo の Hitoshi Hasumikin 等の既存表示を落としません。root LICENSE だけで全推移依存が同一ライセンスだと扱わないでください。

## 実装・再配布への影響

- BSD のコードを取り込むときは著作権表示、条件、免責を保持します。バイナリ配布では文書等への表示が必要です。権利者名による推奨を示唆しません。根拠: `LICENSE:5-18`。
- Nordic 5-Clause は Nordic Semiconductor の IC でのみ利用でき、同ライセンスのバイナリに逆解析等の制限があります。RBOS 本体が BSD でも、この制限を消すことはできません。根拠: `vendor/sdk-nrf-bm/LICENSE:8-28`。
- Apache-2.0 の再配布条件、変更表示、該当する NOTICE を確認します。根拠: [LICENSE](https://github.com/nrfconnect/sdk-mcuboot/blob/fce4dac2e6295cf98bd02a85f7c4254f6102106d/LICENSE#L89-L121)。
- mruby を配布する場合は MIT の著作権表示と許諾文を保持します。host compiler の追加であり、mruby runtime を RBOS firmware に link する計画ではありません。根拠: `vendor/mruby/LICENSE:1-19`。
- MCUboot は独立 submodule を削除しても west 依存として配布条件の確認が必要です。
- yomiyasu を再配布する場合も MIT の著作権表示と許諾文を保持します。根拠: `vendor/yomiyasu/LICENSE:5-21`。

OpenBlink の実装からコードを転用する場合は ViXion の表示を保持します。パターンだけを参考に新規実装したファイルへ、転用していないコードの著作権表示を機械的に追加しません。引用する設計根拠と、コピーするソースを区別します。

## firmware の配布 notice

app 更新 image と初期導入 image の両方に、`THIRD_PARTY_NOTICES` と `third-party/` を添付します。[collector](../tools/bm-build/collect-evidence.sh) は各 build 後に vendor・固定 workspace・実際の compiler の license 本文を読み直します。[部品定義](../tools/bm-build/third-party-components.json)を使う[生成器](../tools/bm-build/third-party-notices.py)が inventory と本文を生成し、通常の CI artifact と release evidence の両方に同梱します。vendor は変更しません。

`third-party/inventory.json` は部品ごとの license、元ファイルの相対 path・SHA256、project revision、適用 image、map の archive/member と map の SHA256 を記録します。非ゼロの output section を根拠に選び、discarded section、ゼロ長 section、`LOAD` だけの archive は除きます。LTO は選択された plugin 入力も記録するため、個別 object の最終的な残存とは区別します。新しい未分類 archive が現れた場合は収集を止めます。

配布区分は app 更新（app・loader）と初期導入（app・loader・MCUboot・installer・S115）です。installer も実行 code を含むため対象にします。S115 は ELF の link 対象ではなく HEX であり、元 HEX の SHA256 と data 領域を記録し、署名済み S115 と `production.hex` の payload を照合します。host mrbc・emsdk・toolchain binary は再配布しないため、この inventory の部品には含めません。compiler runtime の libgcc と picolibc は image に link されるので含めます。

MCUboot の NOTICE、S115 の agreement と ARM attribution、picolibc の COPYING 類、libgcc の GPL 本文と runtime exception を同梱します。Mbed TLS と Oberon の Mbed TLS 由来部分は Apache-2.0 を選びます。この選択は Oberon の Nordic 5-Clause 部分を変更しません。S115 の Nordic IC 製品・更新向けの表示例外に依存せず、ARM の BSD-3-Clause 表示も添付します。

[verifier](../tools/bm-build/verify-evidence.py) は map と inventory を再照合し、必須 license・NOTICE の欠落、本文の変更、適用 image の不一致を拒否します。これは技術的な収集・整合性検査です。header 由来の code、ファイル単位の例外、LTO 後の全 object を含めた最終的な license 適合は未確認であり、正式配布前の確認事項として残します。署名鍵の管理と実機更新の受入れも、notice の検査とは別です。

[調査索引へ戻る](README.md)
