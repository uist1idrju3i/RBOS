# P2 の実機受け入れ

[調査索引](../README.md) / [checklist](checklist.md#p2-native-api-と資源) / [資源予約](resource-reservations.md)

## 実施前の条件

[開発・証拠検査](development-gates.md)の `implementation` / `host_wasm` / `bm_build` と、以下の `real_hardware` を別々に記録してください。log checker の診断 PASS だけでは実機の全項目を完了にしません。

GPIO/Button・温度・三電源 ADC の実装と host/Wasm/build の検査は、実機の受け入れと分けます。この手順の実行結果はまだありません。DK の flash/erase は所有者の明示的な承認を得てから行ってください。鍵の生成・KMU provisioning・erase・release の書込みは P2 の通常試験には含めません。

1. [BM build 手順](bm-build.md)で debug/stress image を用意し、commit、artifact 名、image header、SHA-256 を記録します。SDK の既定開発鍵を使う debug から始めます。
2. [DK 準備・通常の更新手順](dk-provisioning.md)に従います。既存の鍵や bootloader を消さないでください。P1 の `ERASE_RANGES_TOUCHED_BY_FIRMWARE` 成功例を ERASE_NONE の保証とは扱いません。
3. UARTE20 の VCOM を115200 baudで capture し、試験する boot 一回の log を保存します。機器の serial number・秘密鍵・完全な device ID を公開 log に含めません。
4. VDD の実測値、計測器と許容誤差、電源・負荷・室温を記録し、試験前に四つの許容区間を決めます。温度はダイ温度であり、室温との一致を精度基準にしません。DVDD/AVDD の内部 0.9 V の妥当性は仕様条件と突き合わせ、VDD の外部計測を内部電源の直接測定の代わりにしません。

## 既定 debug image

- P1 の自己検査が完了し、`PASS: P2 native setup` が出ることを確認します。診断 task は4 Button を所有するため、同じ pin を別の Ruby から再設定しないでください。
- LED0 が点灯し、`GPIO.read` / `write` の物理0/1が実測と一致することを確認します。LED は active-high、Button は押下時0です。
- Button0..3 を一つずつ、押下・解放それぞれ100 ms以上保持して操作します。`button index=0..3 level=0/1 count=…` の両レベルと正の count を確認します。チャタリングは複数 edge になり、debounce ではありません。
- 100巡回ごとの `temperature c=…` と三電源の `adc rail=… raw=… volts=…` を3組以上保存します。100巡回は厳密な1秒周期の保証ではありません。raw は signed 16-bit で、single-ended 12-bit の理想的な正方向の範囲は0–4095です。raw と volts は別々の測定なので、同じ一 sample として換算誤差を比較しません。
- 起動時の `scheduler_probe` を payload 0/16/64 Bの3行とも保存します。`accepted` は実際に受け付けた件数、`delivered` は再確保一件を含む値です。`exhausted=0` の場合は64件までの下限だけで、最大容量ではありません。
- BLE 有効化後の `resources` と SDK の SD RAM log、生成 DTS、`.config`、map を照合します。SD RAM と VM pool と app RAM を合算・二重計上しません。SDK の SDH defer 枯渇は warning で配送保証がなく、起動 probe だけで負荷中の SDH producer の安全性は確認できません。

## log の検査

`limits.json` は試験前に記録した `temperature_c` / `dvdd_v` / `avdd_v` / `vdd_v` の四つの `[下限, 上限]` の JSON object とします。便宜的な固定値を合格基準として配布しません。

```sh
python3 tools/bm-build/check-dk-log.py debug.log --profile selftest --json
python3 tools/bm-build/check-p2-log.py debug.log --limits limits.json --min-samples 3
```

後者は最後の boot だけを採用し、診断・probe の欠落、各 Button の押下/解放、反復回数、入力範囲、事前の許容区間を検査します。区間なしでは INCOMPLETE となり、終了値1です。この PASS は log にある値の検査であり、計測器との比較、IRQ latency、pool の瞬間 peak、SDH 枯渇からの回復を証明しません。

## IRQ・寿命・負荷

1. [GPIO/Button 契約](gpio-button-api.md)の Ruby 例を診断 task と置き換え、`45` / `"P1.13"` / `:sw0` の物理値の一致、二重 watch・GPIO write の busy、close 後の再設定を確認します。
2. `wait` / `each_event` の task を終了してから同じ Button を作り直し、旧 generation の edge が新しい subscription に届かないこと、他 task と BM maintenance が進むことを確認します。Wasm の強制終了・VM ID 再利用試験の代わりにはしません。
3. 正規の application IRQ producer だけを使う別の計測 fixture で、ring 満杯の newest drop、pin/generation ごとの coalesce、最新レベルと飽和 count、overflow/coalesced の増加を確認します。安全な GPIO 信号源・配線が必要です。スイッチを手で押すだけの試験を deterministic な ring 飽和の証拠とは扱いません。
4. [P1 の最終条件](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)と同じ方法で、stress image の完全 BLE 接続窓5分を保存します。Button 操作と反復 ADC/温度を続け、tick、catch-up、spinner 公平性、drain、stack/pool、BLE の接続/切断/再広告を比較します。

```sh
python3 tools/bm-build/check-dk-log.py stress.log --profile stress --require-connected 300 --json
python3 tools/bm-build/check-p2-log.py stress.log --limits limits.json --min-samples 3
```

P1 と同じ map 分類で静的増分を比較し、SDK heap・event header と VM pool・stack を分けて記録します。stack paint の未 paint margin、保守時だけの pool 観測、queue drain の観測最大を厳密な上限と呼びません。release 実機・電源断・DFU・保存データ・認可/信頼境界は、それぞれ P3/P5/P6 の範囲です。

[調査索引へ戻る](../README.md)
