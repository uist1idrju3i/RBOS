# 実装へ進むための段階計画

この文書は実装の段階案です。P0 は `firmware/` の最小構成と SDK build まで進めました（[build 再現手順](bm-build.md)、[振り返り](retrospective-P0.md)）。P0 の実機確認と P1〜P6 の実装はまだ行っていません。各段階を独立した PR に分け、受け入れ条件を満たしてから次へ進みます。

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

**状況（2026-11-09）**: build の再現と鍵の分離は確認済み。DK での確認と recovery sample の flash は未実施のため、P0 は未完了です。

根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/release_notes/release_notes_2.0.1.rst:37-49`、`vendor/sdk-nrf-bm/samples/boot/mcuboot_recovery_entry/README.rst:1-60`、[構築調査](../nrf-bm/setup-and-build.md)。

## P1: mruby/c を OS の中核として動かす

- vendor/mruby 4.0.0 の mrbc を build して固定し、RITE0400 の最小プログラムを作る。
- mruby/c を `firmware/` へ結合したら、debug と release の両方を build し、P0 の map と比べた増分を記録する。
- BM 用 HAL を新設し、pool、console write/flush、abort、idle を接続する。
- tick は bm_timer を第一候補とし、直接 GRTC を使う場合も予約 channel0 を避ける。
- IRQ mask はアプリ側の共有 queue の保護に限定し、SoftDevice priority 0/1 を止めない。
- idle は SDK の SoftDevice 対応待機経路を確認して実装する。WFE や SD wait API を未確認のまま決め打ちしない。
- bm_scheduler の foreground 処理と rrt0 の共存点を作る。rrt0 が常時 ready の場合も保守処理が進む設計にする。
- SDH の IRQ/SCHED/POLL を .config で確定し、BM queue の容量・drain 時間、LESC、shell、管理処理の実行機会を予算化する。[SDK 実行モデル](../nrf-bm/runtime-primitives.md)参照。

**受け入れ条件**: 二つ以上の task の同時実行、同 priority の巡回、priority 変更、sleep、mutex、suspend/resume、idle wakeupを試験すること。BLE 接続中の tick jitter と stack/pool 最大使用量を計測すること。

根拠: `vendor/mrubyc/src/rrt0.c:146-181,339-425`、`vendor/mrubyc/hal/minimal.h:1-55`、`vendor/sdk-nrf-bm/include/bm/bm_timer.h:30-112`、[HAL](../mrubyc/hal-porting.md)、[割り込み](../nrf-bm/softdevice-and-interrupts.md)。

## P2: native class と値の規約

- LED/Button/GPIO を最初の対象とし、board pin を C 側で管理する。
- argc、type、範囲、所有権、エラー値/例外を共通規約にする。
- ISR から Ruby へ直接入らず、queue を介して foreground で通知する。
- ADC/PWM/I2C/UART は要件と pin/IRQ の一覧が揃ってから追加する。
- [SDK component 表](../nrf-bm/component-catalog.md)の backend 候補から必要なものを選ぶ。共有 binding に Nordic header を入れず、製品動作は Ruby へ置く。UART/shell の instance 重複、NFC TIMER24、GRTC の所有を確認する。

**受け入れ条件**: 正常、引数なし、nil、誤型、境界、driver failure、OOM をP6 で整える host test 基盤へ追加する。ハードウェア依存は mock と実機を分けて確認する。

根拠: `vendor/mrubyc/src/class.h:234-246`、`vendor/mrubyc/src/value.h:221-263,546-572`、[OpenBlink API](../openblink/api-binding-patterns.md)。

## P3: system-task と権限

- firmware 内の system bytecode と user bytecode を区別する。
- VM ID だけの永続認証ではなく、生成時に付与し破棄時に消す権限情報を設計する。
- 特権 method の全てで caller を検査し、class 名の秘匿に頼らない。
- Task.create、他 task の terminate/raise、ID 再利用、debug API の公開範囲を定義する。

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

- bytecode 更新を含めて firmware 再build・single-bank DFU に一本化する。
- MCUboot + BLE MCUmgr firmware loader の single-bank を結合する。
- app/loader の RAM は別 image として map を測定し、128 KiB upload buffer と VM stack/heap を単純合算しない。
- 固有の ED25519 key、KMU provisioning、IRoT、installer 更新の製造・復旧手順を作る。
- MCUmgr の characteristic/command の認証と署名検証を別に設計する。flat settings の retention name と汎用 settings DB を区別する。[管理機能](../nrf-bm/mcumgr.md)参照。

**受け入れ条件**: signed app、誤署名、電源断、切断からの再 DFU、三つの入口、installer 更新を実機で試すこと。storage と peer data が意図せず消えないこと。dummy key の release を拒否すること。

根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/ug_dfu.rst:24-104`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/bootloader_keys.rst:6-106`、[single-bank](../dfu/single-bank-dfu.md)。

## P6: CI と長時間試験

- SDK build の CI は P0 の改善として `.github/workflows/firmware.yml` に置き、nRF Util の toolchain bundle を固定して使う。版固定した container へ移すかは、配布元・digest・利用条件を確かめてから判断する。
- mruby/c の emscripten HAL による Ruby compile・smoke CI は実装済みです。[共通手順](../../tools/mrubyc-wasm/README.md)と `.github/workflows/mruby-wasm.yml` を使用します。ASYNCIFY と timeout を用い、実機 IRQ/BLE の代替にはしません。native API の mock は今後の課題です。根拠: `vendor/mrubyc/hal/emscripten/hal.h:1-7,27-74`。
- host で mrbc format、native 引数、権限、queue overflow の試験を行う。
- map/size、stack/pool high-water、warnings、署名対象、license notice を成果物に残す。
- DK の HIL で BLE 長時間接続、timer jitter、watchdog、DFU の電源断 fault injection を行う。

**受け入れ条件**: build/host test と実機試験の境界が分かる CI、再現可能な証拠、未検証事項が揃うこと。実装開始後に C の formatter、静的解析、unit-test framework を選定すること。

既存の文書・skill 検査は `AGENTS.md:58-69` にあります。将来の firmware CI と、今回の文書検査を混同しません。

## 初期構成の後

OpenBlink の BLE 転送・storage・reload と外部 system bytecode の HMAC は [将来計画](../openblink/future-support.md)として再評価します。

[調査索引へ戻る](../README.md)
