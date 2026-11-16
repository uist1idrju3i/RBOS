# A7：配線不要の ring 飽和と DFU 保持 fixture

[調査索引](../README.md) / [改訂計画](session-plan-revised.md) / [資源予約](resource-reservations.md)

## 目的と検証の範囲

Phase B の B-1/B-2 に渡す試験専用 image と log checker です。通常 image の API、GPIO allowlist、partition layout は変更しません。Kconfig は既定で無効です。実装・host 試験・BM compile/link と、実機の受け入れ結果は区別します。ここに実機の合格記録はありません。

基準 commit は `6801dbe4357986d597faebafc611a76056bff7a8`。固定 SDK は BM v2.0.1 / sdk-nrf v3.3.0、toolchain は bundle `911f4c5c26` です。対応する公式 container と比較条件は [評価記録](toolchain-container.md)を参照してください。

## B-1：三つに分ける理由

1. 自動生成：TIMER21 COMPARE0 → DPPIC20 → GPIOTE20 OUT → P1.11 の input buffer → GPIO PORT/SENSE → GPIOTE20 IRQ → `changed()` → 実 `rbos_event_post()`。
2. 製品 IN 経路：通常 image の物理 Button0..3 を押下・解放し、既存の `check-p2-log.py` で確認。
3. ring 満杯：fixture の C が非 coalesce の completion event を実 `rbos_event_post()` に事前投入。生成信号だけでは、同じ Button のイベントが集約され、16件の ring は満杯になりません。

1 は**製品の GPIOTE IN channel 経路ではありません**。同一 pin の OUT channel と IN channel の二重割当ては使いません。[nRF54L15 GPIOTE 仕様](https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/gpiote.html-concept_gpio_pin_config)と、固定 nrfx の `drivers/include/nrfx_gpiote.h` の output sensing 契約に基づき、出力の input buffer を接続し、IN channel を割り当てず PORT/SENSE を使います。

P1.11 は DK header に出ています。**外部回路・計測器の駆動を外し、board/SoC revision と pin の空きを確認してから**使ってください。物理 Button の pin は駆動しません。[DK GPIO 表](https://docs.nordicsemi.com/r/bundle/ug_nrf54l15_dk/page/ug/nrf54l15_dk/hw_desription/connector_if.html)、[Errata 100](https://docs.nordicsemi.com/r/bundle/errata_nrf54l15_rev2/page/err/nrf54l15/rev2/latest/anomaly_l15_100.html)、[Errata 33](https://docs.nordicsemi.com/r/bundle/errata_nrf54l15_rev1/page/err/nrf54l15/rev1/latest/anomaly_l15_33.html)を確認してください。

追加 DT overlay は既存の `button0` / `sw0` の pin だけを 45 から 43（P1.11）へ置換します。通常 DT や通常 allowlist に pin を追加しません。fixture の Ruby task は `Button.new(:sw0)` と `poll` を使い、通常の peripheral task とは排他です。

### 資源と実行

- TIMER21、GPIOTE20 は PERI domain。PPIB は消費しません。TIMER10/20 と DPPIC20 channel 0 の S115 予約は維持します。
- GPIOTE channel と DPPI 接続は nrfx allocator で確保します。固定 channel 番号は使いません。失敗は Button 作成失敗または `a7 error=...` になり、完了 log が欠ければ checker は不合格です。
- 1 ms 後に一回だけ OUT を toggle する timer を使い、foreground が COMPARE event と IRQ 到達を照合してから次を生成します。各 phase は5 edge。これは最大周波数・IRQ latency の測定ではありません。
- COMPARE の STOP short 後に nrfx の disable を呼び、driver の state も戻してから再開します。終了後は timer/DPPI を解放しますが、pin は最後の level の出力のままです。リセットまたは Button の close まで外部回路を接続しないでください。
- 配送だけを一時保留します。BM scheduler/service、BLE、supervisor、watchdog、IRQ は止めません。IRQ 不達・過剰、配送待ちには1秒の期限があります。
- `coalesce` は空の ring から5 edge、`drop` は filler 16件へ5 edge、`full` は Button 1件＋filler 15件へ残り4 edge。drop 後は16 filler の FIFO 内容も照合します。
- phase 行に生成数、実測 IRQ 数、受理数、前後の pending/overflow/coalesced、初期・最終 level を記録。delivery 行は実 `Button#poll` の Array 作成後の native hook から出し、level/count/pending を照合します。drop は配送なしを記録します。

`generated` は COMPARE event の実測、`irq` は GPIOTE20 ISR 入口の実測数です。別に `changed()` 到達数も数え、両方5回を要求します。hardware 内部で発生して消えた edge を Ruby の count から逆算しません。最終 GPIO read と callback level も照合します。診断行が欠ける・重複する・不正・順不同・値が違う場合は checker が失敗します。

## Build（通常と別 directory）

[BM build 手順](bm-build.md)で環境を load し、BM workspace で実行してください。以下の `RBOS` は checkout の絶対パスです。

```sh
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  "$RBOS/firmware" --sysbuild -d build-a7-saturation-debug -- \
  -DEXTRA_CONF_FILE="$RBOS/firmware/saturation.conf" \
  -DEXTRA_DTC_OVERLAY_FILE="$RBOS/firmware/boards/saturation.overlay"
```

適用 profile は debug / stress / release。stress は `-DEXTRA_CONF_FILE="$RBOS/firmware/stress.conf;$RBOS/firmware/saturation.conf"`、release は `-DFILE_SUFFIX=release` と [外部署名鍵の指定](bm-build.md)を追加します。OOM と WDT 故障 image には適用しません。saturation と retention は別 image にします。

初回の実機手順：

1. 通常 debug/stress image で B-1 の Button0..3 の物理押下試験を実施し、`check-p2-log.py` の証拠を保存。
2. pin の安全確認後に saturation image を導入。配線不要です。起動ごとに一回だけ自己検査後の Ruby task が自動実行します。
3. boot から `a7 done phases=3` までを一つの UART log として採取。複数 boot を連結しません。
4. `python3 tools/bm-build/check-a7-log.py saturation saturation.log` を実行。
5. 接続中 BLE/MCUmgr、watchdog、通常 service の継続を別に確認し、board/SoC revision、電源、commit、差分、最終 `.config`/DTS/map と実際に導入した image の SHA-256 を記録。

## B-2：storage0 sentinel の A/B 試験

現行 app は settings/ZMS/bonding を使いません。fixture は storage0（`0x8c00`、4 KiB）の先頭32 Bに magic/schema/試験 nonce/payload/CRC32 を置きます。peer_manager（`0x7c00`、4 KiB）は全体の CRC32 を読み取るだけです。**bonding や settings の保持試験とは呼びません。** CRC32 は偶発的な破損の検出用で、暗号学的な完全性の証明ではありません。

1. image A を `retention-seed.conf`、image B を `retention-verify.conf` で build。両方に同じ試験固有の非ゼロ `-DCONFIG_RBOS_RETENTION_NONCE=0x1234abcd` を指定します。例の値は実試験ごとに変えてください。
2. saturation の build 例から追加 DT overlay を外し、`.conf` だけを置換します。stress/release の追加指定は同様です。A/B は同じ鍵・partition layout とし、version/TWEAK と入口は [DFU 手順](dk-provisioning.md)に従います。同じ SemVer で upgrade=true が拒否される条件にも注意してください。
3. A を導入し、**物理 Button1 を押しながら app を起動**して seed を明示。Button0 は loader 入口なので使いません。A は Button1 がなければ失敗し、書きません。起動時の `p5 mode=seed ... verified=1 writes=1` を保存してから解放します。A を再起動するときも意図せず seed しないでください。
4. BM storage の SD backend に一回 write を依頼し、非同期完了と readback を確認します。format/erase/自動修復はしません。既存 storage0 の先頭32 Bは上書きするため、試験用 DK だけで実施してください。peer_manager は書込み先にしません。
5. `ERASE_NONE` の更新または既存の BLE MCUmgr 経路で B へ DFU。seed 完了 log のない試行を使い回しません。B は読み取り専用で sentinel を照合し、欠落・破損なら失敗します。B から write API は呼びません。
6. B の `p5 mode=verify ... verified=1 writes=0` を保存し、`python3 tools/bm-build/check-a7-log.py retention image-a.log image-b.log` を実行。
7. checker は各 image の peer 前後一致に加え、A/B 間の nonce/sentinel/peer CRC32 の一致を要求します。boot mode retention は loader で消費される別の値です。MCUboot trailer は boot 管理領域であり、sentinel として使いません。

write 完了待ちは C supervisor の poll 内で進めます。待っている間に IRQ/BLE/service/WDT を停止しません。10秒以内に完了しなければ失敗します。verify image の起動だけでは DFU 経路の正しさまでは判定できません。導入方法、入口、電源断の位置、署名と起動結果も別に記録してください。

## 自動検査と未確認

- `tests/check-changes/test_a7_log.py`：正常、空、欠落、重複、不正、counter/delivery/保持値の不一致、CLI の失敗。
- `test_a7_native.py`：実 fixture C と実 queue の host 模擬。3 phase の正常配送、空の待機、allocator/API 失敗、IRQ/配送 timeout、seed 明示、非同期 write 完了、read-only verify、欠落/破損/peer 変化を検査。GPIO/DPPI/SD の電気的動作は mock です。
- BM は9 fixture 構成と通常4 profile を compile/link。通常 profile は基準 commit の同構成と実行部分を比較します。実行用の署名鍵ではなく、一時鍵を使う build 検査です。
- 新 Ruby task は BM の固定 mrbc で compile。共有 Button binding の host/Wasm 試験とは別に、実機の task/IRQ 統合を Phase B で確認します。
- 実機の OUT→PORT/SENSE、電気特性、BLE 並走、DFU と電源断、CRC の前後保持は**未実施**。BM build 成功や checker の合成 log 成功で代用しません。

fixture は内部試験用の既定無効機能で、通常の Ruby API・board 契約・DFU 契約を変えません。semver skill に従い、この変更だけでは VERSION/CHANGELOG を更新しません。

## BM/toolchain の定期確認

`.github/workflows/vendor-release-watch.yml` は毎週月曜03:23 UTC（日本時間12:23）に実行されます。`tools/vendor-release-watch.py` は sdk-nrf-bm を含む正式 release tag を監視し、新しい BM の sdk-nrf revision・対応 bundle・image digest を BM の Issue 本文に記載します。固定 bundle tag の digest 変化や、新 BM に対応する bundle/digest と固定値の差分は、toolchain の Issue に通知します。**通知のみで、固定値は自動更新しません。** sdk-nrf 単独の新版一覧や全 toolchain tag の変化は対象外です。公開 metadata・重複抑止・対象外の詳細は [現在の監視範囲](vendor-watch-toolchain.md)、v3.4.x LTS への更新条件は [toolchain 方針](toolchain-container.md)を参照してください。
