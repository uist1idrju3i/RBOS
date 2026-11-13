# mruby/c の Wasm 検査

host の mrbc と emscripten HAL を使い、Ruby の compile と smoke test を実行します。
firmware の build や Nordic の IRQ・BLE・タイミング試験を代替するものではありません。

P2 の正常 suite と必須 PASS は [API 契約・試験在庫](../../research/implementation/api-contracts.json)で管理し、`check.sh` から `check-contracts.py --run` で実行します。exit 0 だけでなく、worker の完了も含む全 PASS と runtime failure の不在を検査します。[開発・証拠検査](../../research/implementation/development-gates.md)も参照してください。

`temperature.rb` は共有 `Temperature.read` を fake backend で実行し、正負・0.25°C刻み、位置・keyword 引数と constructor の拒否、driver failure/busy/timeout、backend 不在からの復帰、反復読出しと参照寿命を検査します。[温度の契約と Float 無効 build の制限](../../research/implementation/temperature-api.md)も参照してください。SDK の実時間・校正精度は検査しません。

`adc.rb` と複数 task の fixture は、三電源の共有 binding、busy、協調待機、取消し、task 終了と VM ID の再利用を実行します。[ADC の契約と検査の境界](../../research/implementation/adc-api.md)を参照してください。runner の `hal.h` は vendor HAL を取り込み、idle に foreground service を追加する薄い adapter です。

## ローカル実行

Ruby、C compiler、Make、Python 3、Git、Node.js、GNU timeout が必要です。
emsdk は公式 repository の tag `6.0.12` に固定します。任意の作業領域で次を実行し、環境を読み込んでください。

```sh
git clone --depth 1 --branch 6.0.12 https://github.com/emscripten-core/emsdk.git emsdk
./emsdk/emsdk install 6.0.12
./emsdk/emsdk activate 6.0.12
source ./emsdk/emsdk_env.sh
```

RBOS のルートで実行します。

```sh
git submodule update --init --depth 1 vendor/mruby vendor/mrubyc
tools/mrubyc-wasm/check.sh
```

vendor の写しを `build/` に作り、mruby の `build_config/mrbc.rb` と rake で mrbc だけを build します。
mruby/c の組み込み Ruby と生成 header も写しで再生成し、vendor のファイルは変更しません。
host build のキャッシュは mruby の submodule SHA ごとに分けます。固定値の更新時は emsdk の release と実行結果を確認し、build 方法を変えた場合は workflow の cache key も更新します。

## 検査範囲

- host C の event queue 検査で FIFO・wrap・newest drop・Button の coalesce・counter 飽和を確かめます。Wasm の `native_helpers.rb` は、試験専用 `NativeFixture` から共有 helper を呼び、引数・fake backend の失敗・参照寿命を検査します。`NativeFixture` は firmware へ結合しない試験用 API です。
- `tests/mruby/` では複数 task、sleep_ms、priority、pass、Mutex、join/value、rescue、空プログラムを実行します。
- 未捕捉例外の fixture は exit 1 と例外メッセージを照合します。引数なし・存在しない file・空 file・不一致 RITE version・magic・宣言サイズは exit 2 と診断を照合します。timeout は失敗です。
- `src/**/*.rb` はすべて個別に compile します。共有 library `src/rbos/adc.rb` は bytecode として firmware / Wasm に結合し、登録時に一度だけ定義を読み込みます。それ以外の製品 Ruby は無限 loop や native API を含み得るため、自動実行しません。

runner は `.mrb` ごとに task を作り、Node.js の NODERAWFS で読みます。ASYNCIFY を有効にし、emscripten HAL の MRBC_NO_TIMER と MRBC_SCHEDULER_EXIT に従います。検査用 heap は 1 MiB、MAX_VM_COUNT は 32、実行 timeout は 30 秒です。BM のメモリ設定ではありません。

例外時に VM は `mrbc_run()` へ 2 を返し（`vendor/mrubyc/src/vm.c:3307-3335`）、scheduler はその終了状態を保持します（`vendor/mrubyc/src/rrt0.c:391-400`）。通常の task は終了時に例外を解放するため（`vendor/mrubyc/src/vm.c:362-371`）、runner は公開 hook `MRBC_ABORT_BY_EXCEPTION` で解放前に記録・表示し、同じ参照を解放します。permanence task も scheduler の戻り値で失敗とします。flag_permanence を runner から変更せず、Task.value の通常の戻り値を保ちます（`vendor/mrubyc/src/vm.c:1734-1745`）。

bytecode の buffer は VM 終了まで保持します。runner は信頼するローカル compiler の生成物を対象とし、不正な任意 binary を安全に処理する validator や sandbox ではありません。実行後の資源はプロセス終了時に回収します。

## RBOS の Ruby API を追加する

runner は task 作成前に `rbos_define_classes(rbos_wasm_backend())` を呼びます。共有 binding は `src/rbos/`、backend 契約は `include/rbos/backend.h`、Wasm fake は `tools/mrubyc-wasm/backend.c` に置き、温度・三電源 ADC・GPIO・Button を実装しています。NativeFixture の task 生成・破棄等は検査専用で、firmware へは結合しません。

`gpio.rb` は同じ物理 pin の三表記、mode と予約・所有、backend failure を検査します。`button.rb` / `button_lifetime.rb` は物理値、coalesce/overflow、stale generation、caller-task の wait/each_event、close retry、orphan 回収と VM ID 再利用を検査します。`peripherals.rb` は実際の firmware Ruby 診断 task を別 VM で実行し、反復 ADC と task 終了時の4 Button 回収を確かめます。GPIOTE の IRQ latency や実配線は fake で検査できません。
class/method の登録、引数・所有権・権限の検査、fake と Ruby test の追加手順は [ruby-api-binding skill](../../.agents/skills/ruby-api-binding/SKILL.md)にまとめています。同じ C binding を将来の nRF build と共有し、製品開発者が Ruby を主に書ける構成を目指します。

## temporary の browser bridge との比較

比較対象は temporary の commit `c5e206ffe939f02c287ed420dd1febc2eca9a6ad` です。

| 比較対象 | RBOS CI での採否 |
|---|---|
| [main.c:7-83](https://github.com/uist1idrju3i/temporary/blob/c5e206ffe939f02c287ed420dd1febc2eca9a6ad/src/main.c#L7-L83) | RITE magic と長さの検査を維持し、header の宣言サイズと実ファイル長の一致も検査。128 KiB pool は採らず、32 VM の試験予算として 1 MiB を維持。プロセス終了で回収するため browser 用 reset/KEEPALIVE は不要 |
| [Makefile:20-53](https://github.com/uist1idrju3i/temporary/blob/c5e206ffe939f02c287ed420dd1febc2eca9a6ad/Makefile#L20-L53) | ASSERTIONS、STACK_OVERFLOW_CHECK、CHECK_NULL_WRITES と 1 MiB stack・64 KiB Asyncify stack を採用。診断重視で O1 を維持し O3/LTO は見送る。Math の強制有効化、VM 数 5 への縮小は採用しない |
| 同 Makefile の web/export 設定 | Node の CLI なので browser 用 MODULARIZE/ES6 export/--no-entry は使わない。NODERAWFS と EXIT_RUNTIME=1 を維持し、FILESYSTEM=0/ENVIRONMENT=web は採用しない |
| [mruby_build_config.rb:1-46](https://github.com/uist1idrju3i/temporary/blob/c5e206ffe939f02c287ed420dd1febc2eca9a6ad/mruby_build_config.rb#L1-L46) | mrbc 専用・disable_libmruby の方針は同じ。CI は host mrbc を cache するため compiler の Wasm 化と browser export 設定は採用しない |

ブラウザー playground と `/docs` の GitHub Pages ファイルは後続作業です。この runner は Node 用で、今回その browser build は行いません。

emsdk の上流: [emscripten-core/emsdk](https://github.com/emscripten-core/emsdk/tree/6.0.12)（MIT）。新規の検査用依存であり、旧版からの更新ではありません。ASYNCIFY と Node filesystem を採用し、ブラウザー配信・BM HAL の emulation は対象外です。

[リポジトリ README へ戻る](../../README.md)
