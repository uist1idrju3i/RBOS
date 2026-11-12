# P2 の開発・証拠検査

[調査索引](../README.md) / [checklist](checklist.md#p2-native-api-と資源) / [実機受け入れ](p2-acceptance.md)

P2 の振り返りを受け、SDK の事前照合、API 契約と試験在庫、成果物検査、時間依存試験の完了条件を CI に組み込みました。Ruby API・board の契約と firmware の版は変更しません。

## 1. SDK と BM の事前照合

新しい周辺機器の実装を広げる前に、[BM build 環境](bm-build.md)で次を実行します。出力先には、repo と SDK workspace の外にある、まだ存在しない directory を指定します。既存 directory は削除しません。

```sh
tools/bm-build/preflight.sh "<workspace>" "<new-build-directory>"
```

- `check-workspace.sh` で [固定 module](../../tools/bm-build/modules.txt) の path・SHA・clean な作業状態を照合します。
- 通常 firmware と同じ Kconfig・board overlay を使い、生成 DT の Zephyr GPIO/GPIOTE node の削除、RBOS pin metadata、LED/Button alias と極性を検査します。
- S115、DPPI/PPIB/GRTC、GPIOTE20/30、SAADC、UARTE20、IRQ 番号・優先度、shell/NFC 無効を compile-time assertion で照合します。
- `preflight.c` が固定 SDK の GPIO/GPIOTE/SAADC と S115 温度 API を compile/link します。GPIO の設定保存は port decode と `PIN_CNF` を使い、存在しない helper を仮定しません。

これは VM を含まない検査用 application です。生成 image を DK に書き込んではいけません。probe は実 peripheral を動かす試験ではなく、通常 backend の build と実機検査を置き換えません。SDK API や予約を追加する場合は、この probe も同じ変更で更新します。

firmware CI は一つの preflight job の成功後に debug/release/stress/oom を build します。手動の release workflow も同じ事前検査を使います。

## 2. API 契約と試験在庫

正本は [api-contracts.json](api-contracts.json) です。class の共通契約を `defaults`、method ごとの引数・戻り値・実行 suite を `contracts` に置きます。結合後の各契約には次を必須とします。

| 項目 | 記録する内容 |
|---|---|
| arguments / returns / keywords | 省略、nil、誤型、範囲、単位、例外、未知 keyword と backend の副作用 |
| effects / waiting / busy | 物理電位、同期・協調待機、queue と後発要求の扱い |
| cancellation / cleanup / reuse | 取消し、停止確認、部分解放の再試行、task 終了と旧 event/result の抑止 |
| abnormal / lifetime | 実在する試験と assertion の目印 |
| hardware | host/Wasm では確認できない実機限定の項目 |

```sh
python3 tools/mrubyc-wasm/check-contracts.py
python3 -m unittest discover -s tests/check-changes
tools/mrubyc-wasm/check.sh
```

在庫 checker は RBS の method/alias と契約を双方向に照合し、共有 C/Ruby にだけ追加された class/method も拒否します。内部 lease class・内部 method は理由と名前を明示します。これは認可機構ではありません。新しい API は RBS・契約・異常系と寿命の試験を PR 前に揃えます。

必須の回帰には `Temperature.read(unexpected: nil)` の backend 前の拒否、ADC の STOPPED/DMA buffer、Button の部分解放 retry と stale generation、task 終了・VM ID 再利用を含みます。Float 無効は binding の host 検査だけであり、固定 vendor の Float 無効 VM は動作確認済みではありません。

関連する API 判断は、引数・戻り値・待機・所有を一緒に整理します。ただし未決の判断は一つずつ、選択肢と推奨理由を添えて確認し、実装で勝手に決めません。

## 3. 成果物の再利用可能な検査

build の終了値を保持する `pipefail` 環境で全 build log を保存し、次のように証拠へ含めます。収集は clean な source から行います。

```sh
tools/bm-build/collect-evidence.sh "<workspace>" "<build-directory>" "<new-evidence-directory>" "<build.log>"
python3 tools/bm-build/verify-evidence.py "<evidence-directory>" --profile debug --revision "$REVISION"
```

`REVISION` は期待する source の完全な40桁 SHA です。image 版は checkout の `firmware/VERSION` と照合し、別の版なら `--version X.Y.Z+TWEAK` を明示します。検査結果は JSON と終了値で返します。

検査対象は source SHA と dirty 状態、固定 SDK/module の path と SHA、checksum の完全性、MCUboot header の magic・長さ・版・flags、profile 別の `.config`、秘密鍵の file/content 不在、symlink と危険な checksum path、map と build log の使用量、IRQ vector です。IRQ 213/218/268 は map の `saadc_irq` / `button_irq20` / `button_irq30` の Thumb address と照合します。

RAM は Memory Configuration の容量ではなく、RAM origin から最後の output section の終端までで計算します。FLASH は `_flash_used`、分類は text/rodata/data/bss/noinit です。build log は sysbuild の `firmware` block だけを選び、loader/installer の表と取り違えません。

四構成をまとめて確認する場合は、各 directory を `firmware-evidence-<profile>-<revision>` の名前で一つの親 directory に置きます。四構成の欠落を拒否し、debug との差分も返します。

```sh
python3 tools/bm-build/verify-evidence.py "<four-profile-directory>" --revision "$REVISION" --baseline "<baseline-parent>"
```

`--baseline` は checksum を検査した過去の同名 profile との map 差分を返します。`--expected-sizes` には `{"debug":{"flash":140036,"ram":85536}}` のような比較用 JSON を指定できます。この数値は形式例で、現在値や許容量の指定ではありません。四構成の検査では四構成分を用意します。差分だけで自動的に安全と判定せず、stack/pool と実機条件を別に評価します。

従来の三引数の収集も残しますが、build log のない証拠は新 verifier の完全検査には使えません。署名の暗号学的検証、source と binary の再現性、書込み・更新成功を証明する機能ではありません。release の本番鍵を使う手動 workflow は、PR の一時試験鍵による release build と区別します。

## 4. 時間と完了条件

ADC の取消し・idle 回収、Button の setup・再利用・通知、peripheral 診断の反復は、状態の変化か deadline を待ちます。例外・期限切れでも `ensure` で fixture task を削除し、foreground 回収を進めます。診断 fixture は Button#poll の結果を試験内で観測し、edge 消費前に次の level を注入しません。製品 API は変更しません。

短い scheduler yield、負荷用 sleep、fairness や Mutex の不進行を観測する時間窓は完了待ちではないため維持します。suite 全体にも30秒の期限を設けます。正常 suite は exit 0 だけでは合格にせず、在庫にある全 PASS 行を要求します。意図的な失敗 fixture は別経路で終了値と診断を照合します。

| JSON の状態欄 | 合格として言えること | それだけでは言えないこと |
|---|---|---|
| implementation | 契約・RBS・共有 binding・必要な試験在庫が対応する | runtime/実機の成功 |
| host_wasm | host 試験と、必須 PASS を含む Wasm 実行が成功する | nRF の IRQ/DMA・電気特性 |
| bm_build | preflight・四構成の build・成果物検査が成功する | DK の受け入れ |
| real_hardware | 実機手順の全項目に証拠がある | build 成功による代用 |

checker は担当外の段階を `NOT_RUN` / `NOT_EVALUATED` とします。`check-p2-log.py` の診断が PASS でも、精度・stress・pool/stack・SDH 回復等を別途確認するため `real_hardware` は `INCOMPLETE` のままです。全体の受け入れは [P2 実機手順](p2-acceptance.md)で判断します。
