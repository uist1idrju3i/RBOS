# 実装へ進むための段階計画

この文書は実装の段階案です。P0 は最小構成の build と利用者による実機確認の記録があります（[build 再現手順](bm-build.md)、[P0 の振り返り](retrospective-P0.md)）。P1 は mruby/c・BM HAL・BLE を実装し、debug/release build と Wasm の検査に加え、利用者が CI debug image の DK 自己検査・BLE 接続中の統計を採取しました。観測値の限界と未確認項目は [P1 の振り返り](retrospective-P1.md)に記録しています。P2〜P6 の段階完了は主張しません。各段階を独立した PR に分け、受け入れ条件を満たしてから次へ進みます。

## 段階の進め方

1. 着手時に、[チェックリスト](checklist.md)の該当項目を PR の本文へ転記する。
2. 作業中は、証拠（実行した commit、コマンド、成果物の hash、実機の記録）がそろった項目だけに印を付ける。
3. 段階の終わりに `retrospective-P<n>.md` を作り、達成と未達、リスクと blocker、次の段階への改善提案、checklist と本計画への追記候補を記録する。
4. 追記候補は利用者の判断を得てから反映する。

## P0: BM の再現可能な基盤

- NCS/toolchain v3.3.0 + BM v2.0.1 の独立 workspace を構築する。
- recovery sample を main target で build/flash し、BLE と console を確認する。
- RBOS の CMake、Kconfig、sysbuild、board overlay、署名設定の最小構成を作る。
- release/debug と秘密鍵の配置を分離し、全 module SHA、map、compiler 版を保存する。
- 新しい DK の初回準備（KMU への鍵の書き込み）を通常の書き込みと分けて手順にする。[DK の準備](dk-provisioning.md)参照。

**受け入れ条件**: clean workspace で再現でき、DK 上で LED/console/loader 入口を確認できること。同じ commit を CI とローカルで build し、debug の成果物の hash が一致すること。自動 erase を通常操作に含めないこと。

**状況（2026-11-09 初回記録）**: build の再現と鍵の分離は確認済み。当時は DK での確認と recovery sample の flash が未実施のため、P0 は未完了でした。その後の利用者報告を受けた現在の判定は [P0 の受け入れ判定](retrospective-P0.md#p0-の受け入れ判定)を参照してください。

根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:37-49`、`vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_entry/README.rst:1-60`、[構築調査](../nrf-bm/setup-and-build.md)。

## P1: mruby/c を OS の中核として動かす

**状況: P1 完了（承認済み closeout 条件）**。新既定 image `ef8514585aa2` の DK 自己検査10項目と完全接続400.140059秒の stress が PASS しました。公平性の a/b=1.014307、tick 920..1064 µs、catchups=0を確認し、既存の OOM、再接続・広告停止、Wasm Mutex fault と合わせて判定します。利用者の決定で P1 の残る4項目は観測値で完了とし、厳密な上限・進行保証は P6、予約表と SD RAM/queue の照合は P2 へ移管します。release 実機・ERASE_NONE は P5、保存データ保持は P5/P6 が担当します。[最終実機証拠](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)と[証拠付き checklist](checklist.md#p1-vm-と時間)を参照してください。

- vendor/mruby 4.0.0 の mrbc を build して固定し、RITE0400 の最小プログラムを作る。
- mruby/c を `firmware/` へ結合したら、debug と release の両方を build し、P0 の map と比べた増分を記録する。
- BM 用 HAL を新設し、pool、console write/flush、abort、idle を接続する。
- tick は bm_timer を第一候補とし、直接 GRTC を使う場合も予約 channel0 を避ける。
- IRQ mask はアプリ側の共有 queue の保護に限定し、SoftDevice priority 0/1 を止めない。
- idle は SDK の SoftDevice 対応待機経路を確認して実装する。WFE や SD wait API を未確認のまま決め打ちしない。
- bm_scheduler の foreground 処理と rrt0 の共存点を作る。rrt0 が常時 ready の場合も保守処理が進む設計にする。
- SDH の IRQ/SCHED/POLL を .config で確定し、BM queue の容量・drain 時間、LESC、shell、管理処理の実行機会を予算化する。[SDK 実行モデル](../nrf-bm/runtime-primitives.md)参照。

**受け入れ条件**: 二つ以上の task の同時実行、同 priority の巡回、priority 変更、sleep、mutex、suspend/resume、idle wakeupを試験すること。BLE 接続中の tick jitter と stack/pool 最大使用量を計測すること。

**承認済み closeout 条件: 達成**。Wasm Mutex fault と規約、DK の二つの常時 ready task 負荷中の BLE 完全接続 stats 窓5分、DK OOM/abort の証拠がそろいました。利用者の決定で stress 時間を30分から5分へ変更しました。旧偏り log と X/Y 比較も保存し、新既定の最終 log で公平性自己検査と400.140059秒の完全接続窓を確認しました。2倍超は現在 FAIL です。[最終判定と未確認範囲](retrospective-P1.md#新既定-image-の最終-dk-確認と-p1-完了判定)を参照してください。vendor scheduler は未変更です。 利用者は DK の Mutex fault 試験を行わず、Wasm 試験と採用規約で十分と承認しました。公平性の閾値は実測約1.01に狭めず、2倍を維持します。

根拠: `vendor/mrubyc/src/rrt0.c:146-181,339-425`、`vendor/mrubyc/hal/minimal.h:1-55`、`vendor/sdk-nrf-bm/include/bm/bm_timer.h:30-112`、[HAL](../mrubyc/hal-porting.md)、[割り込み](../nrf-bm/softdevice-and-interrupts.md)。

## P2: native class と値の規約

- 利用者の決定により P1 から移管: peripheral を使い始める前に peripheral/DPPI/IRQ の完全な予約表を照合し、SDH 配送 model・SD RAM usage・BM queue 容量を SDK 仕様・設定・map・実測で確認する。

- LED/Button/GPIO を最初の対象とし、board pin を C 側で管理する。
- ダイ温度の読み出しを native API として追加する。backend は nRF54L15 の TEMP ペリフェラルを使う。BM board の dtsi が `&temp` node を削除しているため DT 駆動は使えず、nrfx_temp か register 直接の経路にする。OpenBlink の [温度 HAL](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/drv/hal/die_temperature.c)は Zephyr の sensor API を使うため流用せず、BM bare-metal 向けに新規実装する。
- 温度 API の契約（class/method 名、返り値の型と単位、失敗時の例外、同期・非同期の扱い）は本段階の値の規約に合わせて決める。
- argc、type、範囲の検査を共有 C helper に集約し、所有権・エラー値/例外を共通規約にする。Wasm fake で正常・引数なし・nil・誤型・境界・driver failure を検査する。
- ISR から Ruby へ直接入らず、固定長 ring を介して foreground で通知する。overflow は newest を drop し、stats の overflow counter で観測する。Button edge は pin ごとに coalesce して count を残す。
- native API を追加するたびに P1 の map 分類と stack/pool 観測方法で増分を記録する。標本 peak と厳密な上限は区別する。
- ADC/PWM/I2C/UART は要件と pin/IRQ の一覧が揃ってから追加する。
- [SDK component 表](../nrf-bm/component-catalog.md)の backend 候補から必要なものを選ぶ。共有 binding に Nordic header を入れず、製品動作は Ruby へ置く。UART/shell の instance 重複、NFC TIMER24、GRTC の所有を確認する。

**受け入れ条件**: 正常、引数なし、nil、誤型、境界、driver failure、OOM をP6 で整える host test 基盤へ追加する。ハードウェア依存は mock と実機を分けて確認する。

根拠: `vendor/mrubyc/src/class.h:234-246`、`vendor/mrubyc/src/value.h:221-263,546-572`、[OpenBlink API](../openblink/api-binding-patterns.md)、[OpenBlink の温度 HAL](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/drv/hal/die_temperature.c)、[nrfx TEMP ドライバ](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/drivers/include/nrfx_temp.h)、[nRF54L15 の TEMP 定義](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/bsp/stable/mdk/nrf54l15_application_peripherals.h#L1039-L1040)、`vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/bm_nrf54l15dk_nrf54l051015_peripherals.dtsi:58`。

## P3: system-task と権限

- firmware 内の system bytecode と user bytecode を区別する。
- VM ID だけの永続認証ではなく、生成時に付与し破棄時に消す権限情報を設計する。
- 特権 method の全てで caller を検査し、class 名の秘匿に頼らない。
- Task.create、他 task の terminate/raise、ID 再利用、debug API の公開範囲を定義する。
- user VM の priority=/suspend/terminate/raise は自己だけに許し、system task と他 task への操作を拒否する。system task は user から変更不能にし、認可の拒否試験を加える。
- watchdog の kick は system task が担当する。fatal は debug では現在どおり halt、release では log flush 後に reboot する。watchdog・release 回復経路の実装と試験は P3 が担当し、P6 で長時間・障害試験を行う。

**受け入れ条件**: user VM が system LED、loader 遷移、storage 管理等の特権操作を実行できないこと。子 task 生成・破棄後にも権限が漏れないこと。native memory の完全 sandbox を達成したとは主張しないこと。

根拠: [OpenBlink の HMAC ToDo と VM ID 判定](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/api/api.c#L47-L67)、`vendor/mrubyc/src/rrt0.c:1040-1199`。

## P4: const bytecode の生成・結合

- vendor/mruby の mrbc で RITE0400 の C 配列を生成する。
- const 配列を app に link し、RRAM 配置と入力の寿命を保証する。
- IREP/補助表/String 等の RAM を実測し、alignment macro を固定する。
- storage backend、BLE bytecode 転送、動的 reload は初期に実装しない。

**受け入れ条件**: 正常・空プログラム・不正形式・OOM を試し、全体 RAM コピーなしで実行できること。String を変更しても const blob が変わらないこと。

根拠: [埋め込み設計](../dfu/embedded-bytecode.md)。

## P5: firmware DFU

- BLE DFU の転送速度のため、DLE と ATT MTU の値を決定して実機測定する。現行 app の data length は iPhone の251要求に27で応答するが、DFU loader の設定・交渉結果は別に確認する。

- bytecode 更新を含めて firmware 再build・single-bank DFU に一本化する。
- MCUboot + BLE MCUmgr firmware loader の single-bank を結合する。
- app/loader の RAM は別 image として map を測定し、128 KiB upload buffer と VM stack/heap を単純合算しない。
- 固有の ED25519 key、KMU provisioning、IRoT、installer 更新の製造・復旧手順を作る。
- release 鍵で準備した DK の release image 起動と ERASE_NONE 更新を検証する。広告の開始・停止・再開条件は P5 が所有し、DFU・電力・復旧の要件と合わせて実装する。P1 は現行 timeout の観測に限る。
- BLE のデバイス名にシリアル番号由来の識別子を含める。FICR の DEVICEID（64-bit）をもとに 4 桁の 16 進を生成し、`RBOS_XXXX` の形にする。OpenBlink の [blink_get_name](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/blink.c)を参考にし、BM bare-metal 向けに新規実装する。ハッシュの多項式・seed・表記と広告名の長さの上限は P5 で決める。
- MCUmgr の characteristic/command の認証と署名検証を別に設計する。flat settings の retention name と汎用 settings DB を区別する。[管理機能](../nrf-bm/mcumgr.md)参照。

**受け入れ条件**: signed app、誤署名、電源断、切断からの再 DFU、三つの入口、installer 更新を実機で試すこと。storage と peer data が意図せず消えないこと。dummy key の release を拒否すること。

根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/ug_dfu.rst:24-104`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:6-106`、[single-bank](../dfu/single-bank-dfu.md)、[OpenBlink の blink_get_name](https://github.com/OpenBlink/openblink-demo-nrf/blob/6d22b676d2cf4bc599a7709ecebaa1b890af9e3a/src/app/blink.c)、[nRF54L15 の FICR DEVICEID](https://github.com/zephyrproject-rtos/hal_nordic/blob/1acb428a205bad58f3dfd4e38f2d1663bb784ba1/nrfx/bsp/stable/mdk/nrf54l15_types.h#L9583)。

## P6: CI と長時間試験

- 利用者の決定により P1 から移管: 長時間負荷で pool/IREP 等の追加確保・瞬間 peak・C/ISR stack・queue/drain の厳密な上限と idle/deferred の一般的な進行保証を評価する。P1 は観測値で完了とし、標本値を保証値へ読み替えない。

- SDK build の CI は P0 の改善として `.github/workflows/firmware.yml` に置き、nRF Util の toolchain bundle を固定して使う。版固定した container へ移すかは、配布元・digest・利用条件を確かめてから判断する。
- mruby/c の emscripten HAL による Ruby compile・smoke CI は実装済みです。[共通手順](../../tools/mrubyc-wasm/README.md)と `.github/workflows/mruby-wasm.yml` を使用します。ASYNCIFY と timeout を用い、実機 IRQ/BLE の代替にはしません。native API の mock は今後の課題です。根拠: `vendor/mrubyc/hal/emscripten/hal.h:1-7,27-74`。
- host で mrbc format、native 引数、権限、queue overflow の試験を行う。
- map/size、stack/pool high-water、warnings、署名対象、license notice を成果物に残す。
- DK の HIL で BLE 長時間接続、timer jitter、watchdog、DFU の電源断 fault injection を行う。
- P5 の更新・storage の設計に対し、保存データの更新前後の保持を実機で検証し、release DK・ERASE_NONE 試験の証拠とともに保存する。

**受け入れ条件**: build/host test と実機試験の境界が分かる CI、再現可能な証拠、未検証事項が揃うこと。実装開始後に C の formatter、静的解析、unit-test framework を選定すること。

既存の文書・skill 検査は `AGENTS.md:58-69` にあります。将来の firmware CI と、今回の文書検査を混同しません。

## 初期構成の後

OpenBlink の BLE 転送・storage・reload と外部 system bytecode の HMAC は [将来計画](../openblink/future-support.md)として再評価します。

[調査索引へ戻る](../README.md)
