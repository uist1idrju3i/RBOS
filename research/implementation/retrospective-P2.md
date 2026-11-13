# P2 の調査判断・検証結果と振り返り

[調査索引](../README.md) / [実装計画](porting-plan.md) / [実機受け入れ](p2-acceptance.md)

## 対象と結論

native 共通基盤から GPIO/Button・温度・内部三電源 ADC までの調査と実装を記録します。コード実装・host/Wasm・BM build と、実機受け入れは別の状態です。P2 の実機受け入れは未完了で、このセッションでは flash/erase を行っていません。

| 変更 | 検証・判断の確認先 |
|---|---|
| 共通 helper と ring | [PR #35](https://github.com/uist1idrju3i/RBOS/pull/35)、[共通基盤](native-foundation.md) |
| 三電源を P2 へ追加 | [PR #36](https://github.com/uist1idrju3i/RBOS/pull/36)、[ADC 契約](adc-api.md) |
| S115 予約保護と起動診断 | [PR #37](https://github.com/uist1idrju3i/RBOS/pull/37)、[資源予約表](resource-reservations.md) |
| 温度と keyword 拒否 | [PR #38](https://github.com/uist1idrju3i/RBOS/pull/38)、[PR #39](https://github.com/uist1idrju3i/RBOS/pull/39)、[温度契約](temperature-api.md) |
| 協調待機の三電源 ADC | [PR #40](https://github.com/uist1idrju3i/RBOS/pull/40)、[ADC 契約](adc-api.md) |
| GPIO/Button と caller-task 配送 | [PR #41](https://github.com/uist1idrju3i/RBOS/pull/41)、[GPIO/Button 契約](gpio-button-api.md) |
| 振り返りの改善4項目 | [PR #42](https://github.com/uist1idrju3i/RBOS/pull/42)、[開発検査](development-gates.md) |

## 採用した判断と不採用の経路

| 調査・利用者の判断 | 採用した契約と根拠の所在 |
|---|---|
| 温度は S115 公式機能、公開形は A | `Temperature.read`。MPSL が TEMP を予約するため直接 register/nrfx_temp と独自 TEMP IRQ を使わない。約50 µsの同期取得は仕様値で、実測値ではない。[温度](temperature-api.md)、[設計判断](../architecture/decisions.md#ダイ温度の取得経路) |
| ADC の factory と busy は A | `ADC.internal(:dvdd)` / `ADC.internal(:avdd)` / `ADC.internal(:vdd)`。後発は RuntimeError、順番待ち queue は作らない。DVDD/AVDD は内部 0.9 V rail、VDD は主電源。換算・校正・符号と STOPPED/DMA の条件は [ADC 契約](adc-api.md) |
| GPIO の active-low は A | Integer/String/Symbol は同じ物理電気レベル。Symbol だけ反転しない。許可集合は DK の LED/Button 8 pin。[pin・mode・例外](gpio-button-api.md)、[MPIG と実装範囲](../io-api/overview.md) |
| Button の配送は A | `wait` / `each_event` を呼出し task で実行する。別 dispatcher task と native の Ruby Proc 保持は採用しない。ring は16件、mailbox は4 watch、generation と lease で古い event と寿命を扱う。[配送・回収](gpio-button-api.md) |
| console は A | UARTE20 のログを維持し、TX/必要時 CTS を保護。UARTE30 application/shell は初期化しない。RTT/BLE console は新設せず、pairing/bonding 非対応も維持。[資源予約](resource-reservations.md) |

## 実装で判明した制約

- BM は GPIO/GPIOTE/ADC の DT node を削除します。GPIO driver を復活させず、RBOS 専用の DT メタデータと nrfx を使います。固定 SDK に `nrf_gpio_pin_cnf_get` はなく、[GPIO adapter](../../src/platform/nrf/gpio.c)は port の PIN_CNF を使います。BM の直接 IRQ 接続も [preflight](../../tools/bm-build/preflight.c)で compile/link します。
- mruby/c の argc は位置引数だけです。keyword Hash を別に検査しないと `Temperature.read(unexpected: nil)` が backend に到達します。[共通基盤](native-foundation.md)と [温度回帰](../../tests/mruby/temperature.rb)に拒否条件を記録しました。
- 固定 VM の Float 無効 build は vendor header の `RObject.d` 参照で失敗しました。vendor は変更せず、binding の拒否 guard だけを host fixture で検査しました。Float 無効 VM 全体の実行成功とはしません。[制限と検査](temperature-api.md#検査と未確認項目)
- SAADC の abort 復帰だけでは DMA 停止を保証できません。校正中の取消しで SDK callback が来ない経路は IRQ wrapper の STOPPED 捕捉で扱い、停止確認前には buffer を再利用しません。[ADC の IRQ・取消し](adc-api.md#irqdma-と取消しの境界)
- task 終了試験で Wasm の idle hook が実 scheduler の service に届かない不具合を検出しました。回収経路を直し、実際の task 終了・削除・同じ VM ID の再利用と旧結果の拒否を [ADC](../../tests/mruby/adc_lifetime.rb)と [Button](../../tests/mruby/button_lifetime.rb)で検査します。fake の API 呼出しだけを寿命の証拠にしません。
- RAM の memory region 容量を使用量に数える集計誤りを修正しました。現在は output section の終端と RAM origin の差を取り、app build log と照合します。SHA-256/header/vector の照合は、製品鍵での署名検証や source/binary 再現性の保証ではありません。[成果物の検査](development-gates.md#3-成果物の再利用可能な検査)
- OOM の実成果物では、依存条件が偽の `CONFIG_RBOS_PERIPHERAL_EXERCISE` が `.config` に出力されませんでした。verifier は Bool の行省略も n と扱い、必須 y・数値・文字列の欠落は拒否します。合成 fixture もこの実際の形に直し、n の各表記・誤った有効化・必須値欠落を回帰試験に追加しました。

## P2 実装済み main の検証記録

対象は [main 039d4ea](https://github.com/uist1idrju3i/RBOS/commit/039d4eac810db8b82beb0103b47312c52f124dc6)、firmware 0.1.4、application image 0.1.4+0 です。PR #41 head と source tree が一致し、マージ後の全16 check が成功しました。[main firmware CI](https://github.com/uist1idrju3i/RBOS/actions/runs/43255357037)と [main Wasm CI](https://github.com/uist1idrju3i/RBOS/actions/runs/43255357335)が入力・成果物の確認先です。

host は当時69件、Wasm、RBS parser、skills と7件の unittest、research、wiki JSON、diff の検査が成功しました。各構成34ファイルの checksum、source revision、固定 module、鍵不在を照合しました。IRQ213/218/268 は map/vector 上で SAADC/GPIOTE20/GPIOTE30 に対応します。実際の IRQ 発火・優先度・latency の測定ではありません。

次表の増分は [ADC 実装済み main 1f815eb](https://github.com/uist1idrju3i/RBOS/commit/1f815eb981e85b28f4ba391d9775575a1abf57ac) 比で、PR #41 と main の値は一致しました。

| 構成 | FLASH | FLASH 増分 | 静的 RAM | RAM 増分 |
|---|---:|---:|---:|---:|
| debug | 140,036 B | +13,436 B | 85,536 B | +1,448 B |
| release | 120,280 B | +11,480 B | 85,288 B | +1,448 B |
| stress | 140,836 B | +13,436 B | 85,536 B | +1,448 B |
| oom | 136,412 B | +12,288 B | 85,536 B | +1,448 B |

| main application signed image | SHA-256 |
|---|---|
| debug | `6747543cb71ab7883830ae58b403486526ef70a147de072eb1b4328c688e94c7` |
| release | `553b12f5b0409da755136a81e287a6f2ffa4a3b9a1ea02acd284bb37146db6ff` |
| stress | `93c6972af47f1f6a30b7cb24b679bac08cdf008fd5afe2cff0daba043f225951` |
| oom | `58c8188d3d59fd8f616a7d0221abe08d33c5ede0f71e443bf911fdc29c584cd7` |

RAM は配置・alignment を含む静的な値で、Ruby pool の空きや stack/heap の瞬間 peak ではありません。CI release は一時鍵による build 検査で、DK 配布用 image ではありません。OOM profile は反復 peripheral 診断を無効にします。

## 振り返りと改善の適用

| 起きたこと | 実装した改善 |
|---|---|
| BM の DT 削除・IRQ 方式・存在しない SDK helper を広い build の途中で発見した | 固定 workspace と最小 SDK compile/link を通常四構成より前に行う preflight |
| keyword、task 終了、VM ID 再利用、部分解放の追加検査で漏れを発見した | 公開25 API の [契約・試験在庫](api-contracts.json)と、RBS/C/Ruby・alias・内部 helper の根拠の照合 |
| artifact 照合を繰り返し、RAM 集計も誤った | checksum・鍵・版・profile・IRQ・map・build log を共通 verifier と異常系回帰で検査 |
| 固定 sleep で結果の観測前に次へ進み、診断は ADC 開始数だけで終了し得た | condition＋deadline と ensure。三電源の二巡回が返った後の次 request まで観測し、必須 PASS・異常 log・timeout を検査 |

[PR #42 の検査](https://github.com/uist1idrju3i/RBOS/pull/42/checks)で実行結果を追跡します。実装時の host は88件、skill unittest は7件、Wasm の正常 suite と最小 BM preflight の compile/link は成功しました。四構成の機械可読結果は CI の `firmware-verification-<revision>` artifact を正本とし、上の過去の image hash を流用しません。[開発検査](development-gates.md)がコマンド・完了状態・保証しない範囲を定義します。

## 改善適用後の最終 CI と成果物

[PR #42 最終 head 3ab7129](https://github.com/uist1idrju3i/RBOS/commit/3ab71297341074149e5427f55ec59d6bee8271e1)の全16 check と、[main 8096c28](https://github.com/uist1idrju3i/RBOS/commit/8096c2864849390fdf5f2185ba4a7bda42642590)の全18 check が成功しました。PR の build 入力は GitHub の検査用 merge revision `995bae77a1d321ebadcb3656ee7eb5e41681c685` です。main の [firmware CI](https://github.com/uist1idrju3i/RBOS/actions/runs/43334033333)と [Wasm CI](https://github.com/uist1idrju3i/RBOS/actions/runs/43334033318)を参照してください。

main の四構成 evidence を取得し、共通 verifier を再実行しました。各構成35ファイルの checksum、source/module、0.1.4+0、profile、秘密鍵不在、IRQ/vector、map/build log は PASS です。再実行した集約 JSON は CI の集約結果と一致しました。以前の34ファイルからは build.log が追加されています。

さらに main 039d4ea の四構成 evidence を baseline として、各構成の map 差分を検査しました。FLASH/RAM と text/rodata/data/bss/noinit は全構成とも増減0 Bです。保存した [四構成の検証 JSON](p2-gate-results.json)には、この追加の `map_delta` と、各 image の SHA-256、debug 比の profile 差分を含みます。`map_delta` 以外の field は CI の集約結果と一致します。署名済み image の hash が異なっても、binary 再現性を判定したものではありません。

JSON の完了状態は `bm_build: PASS`、`real_hardware: NOT_RUN` です。`implementation` / `host_wasm` が NOT_EVALUATED なのは、成果物 verifier の担当外のためで、上記の実装・host/Wasm の失敗を表しません。実機の確認項目は引き続き未完了です。

## 調査結果の反映確認と残る受け入れ

このセッションの判断・SDK 制約・失敗原因・検証結果を、上記の契約、設計判断、予約表、開発検査、[checklist](checklist.md#p2-native-api-と資源)と照合しました。初回の Common I/O 調査・pin 対応・共通基盤・段階計画に残っていた「未実装」「候補」「mock は今後」の記述を、現在の実装と履歴に分けて更新しました。外部 pin ADC と他の未実装 I/O は未実装のまま明記します。

実機の電位、温度・三電源の精度、GPIOTE/SAADC IRQ・DMA/STOPPED、BLE/tick、SD RAM/queue の余裕、stack/pool の瞬間 peak は未確認です。事前の許容区間、測定器・電源条件、3組以上の反復測定、Button の実操作、5分 stress、close/終了/再作成と飽和試験を [実機受け入れ](p2-acceptance.md)に残します。log の PASS だけでも実機全体の完了にはしません。本番鍵の手動 release、暗号学的な署名検証、binary 再現性も今回の検証範囲外です。
