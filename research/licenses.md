# ライセンスと配布条件

本書は実装・配布時の確認項目であり、法的助言ではありません。ファイル単位の SPDX、同梱バイナリ、west の推移依存も配布前に確認します。

| 対象 | 主なライセンス | 根拠 |
|---|---|---|
| RBOS | BSD-3-Clause | `LICENSE:1-28` |
| mruby/c | BSD-3-Clause | `vendor/mrubyc/LICENSE:1-28` |
| OpenBlink | BSD-3-Clause | [LICENSE](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/LICENSE#L1-L28) |
| sdk-nrf-bm | LicenseRef-Nordic-5-Clause | `vendor/sdk-nrf-bm/LICENSE:1-40` |
| MCUboot | Apache-2.0 | `vendor/sdk-mcuboot/LICENSE:1-30` |
| yomiyasu | MIT | `vendor/yomiyasu/LICENSE:1-21` |

## 実装・再配布への影響

- BSD のコードを取り込むときは著作権表示、条件、免責を保持します。バイナリ配布では文書等への表示が必要です。権利者名による推奨を示唆しません。根拠: `LICENSE:5-18`。
- Nordic 5-Clause は Nordic Semiconductor の IC でのみ利用でき、同ライセンスのバイナリに逆解析等の制限があります。RBOS 本体が BSD でも、この制限を消すことはできません。根拠: `vendor/sdk-nrf-bm/LICENSE:8-28`。
- Apache-2.0 の再配布条件、変更表示、該当する NOTICE を確認します。根拠: `vendor/sdk-mcuboot/LICENSE:89-121`。
- yomiyasu を再配布する場合も MIT の著作権表示と許諾文を保持します。根拠: `vendor/yomiyasu/LICENSE:5-21`。

OpenBlink の実装からコードを転用する場合は ViXion の表示を保持します。パターンだけを参考に新規実装したファイルへ、転用していないコードの著作権表示を機械的に追加しません。引用する設計根拠と、コピーするソースを区別します。

現在は submodule の固定と調査文書のみです。ファームウェア配布物、署名鍵の管理、SDK バイナリの同梱方法は未実装です。製品化前に依存一覧と同梱ライセンス一覧を成果物へ含めることを受け入れ条件にします。

[調査索引へ戻る](README.md)
