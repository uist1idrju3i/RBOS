# P1/P2 runtime

対象と build 手順は [BM build 手順](../research/implementation/bm-build.md)を参照してください。flash / erase は build に含めません。

P2 の `Temperature.read` は共有 binding と `src/platform/nrf/backend.c` で実装し、S115 の `sd_temp_get` を利用します。既定／stress profile の coordinator は P1 自己検査の後に `temperature c=<Floatの°C>` を一回出します。P1 の PASS/stats 形式は変えません。OOM profile では coordinator を実行しません。[API 契約・同期処理・未確認条件](../research/implementation/temperature-api.md)を参照してください。

P2 は GPIO と Button の [共有 API・DT pin メタデータ・GPIOTE 配送](../research/implementation/gpio-button-api.md)も実装します。既定の `RBOS_PERIPHERAL_EXERCISE` は自己検査の終了後に LED0 を GPIO API へ引き渡し、4 Button の物理値と count、温度と三電源の反復値を出します。この診断 task が Button を所有するため、製品 Ruby では task を置き換えるかこの設定を無効にしてください。console は UARTE20、pairing/bonding は非対応のままです。

## build 時の生成

`cmake/mrubyc.cmake` は `vendor/mruby` を app の build directory の `mruby-host/` にコピーし、host の Ruby と C compiler で mrbc 4.0.0 を作ります。compiler binary は配布しません。既存の host compiler を使う場合は、west build の `--` の後で `-DRBOS_MRBC=/absolute/path/to/mrbc` を指定します。版が異なる compiler は拒否します。

mruby/c の `src/`、`support/`、`mrblib/` も build directory にコピーします。vendor にある `mrblib.c` は使わず、コピー上で `make -C mrblib MRBC=... all` を毎回 configure 時に実行します。vendor にない `_autogen*.h` は、コピー上の `make -C src autogen` で生成します。vendor のファイルは変更しません。元の VM source と mrblib の変更は CMake の再構成対象です。

既定 profile の Ruby の順序は system、coordinator、worker_a、worker_b、診断有効時の peripherals です。各 `.rb` は build 時に `mrbc -B` で `const uint8_t` 配列へ変換し、生成した `embedded.c` の表から task を作ります。`.rb` の変更は対応する配列の再生成対象です。bytecode は RRAM の rodata に置き、RAM へコピーしません。

生成した task 配列と mrblib は `tools/bm-build/check-bytecode.py` で検査します。先頭の `RITE0400` と、big-endian の宣言サイズが実サイズと一致することを確認し、不一致なら build を止めます。正常・空・不正 magic・不正 version・不正 size の検査は `tests/check-changes/test_bytecode.py` に置き、CI の変更判定 job でも実行します。

VM 数と pool は `CONFIG_RBOS_MAX_VM_COUNT`（既定 8）と `CONFIG_RBOS_VM_POOL_SIZE`（既定 65536 bytes）で設定します。VM の他の設定は上流の既定値です。release は `CONFIG_RBOS_VM_NDEBUG` により、mruby/c source だけに `NDEBUG` を追加します。

## 資源予約

S115 の DPPI/PPIB 予約を nrfx allocator へ渡す header を application Kconfig の先行 default で選択し、Zephyr/nrfx library にも include path を渡します。`src/resources.c` は最終選択の header と IRQ/GRTC の前提を検査し、BLE 初期化成功後に SD RAM・BM heap byte 数・event header サイズを記録します。予約と callback context、診断値の読み方、未確認の実機項目は [P2 の資源予約](../research/implementation/resource-reservations.md)を参照してください。

## 実行

BM の repeated timer は 31 ticks（992 µs）周期です。絶対 uptime から経過した整数 ms を求め、経過分だけ `mrbc_tick()` を呼びます。IRQ lock は BASEPRI により SoftDevice の priority 0/1 を残します。BLE のイベントは BM scheduler を通して main context で処理します。

firmware 専用の `RBOSSystem.service` は、起動時に保持した system task の VM だけが呼べます。引数は受け取りません。system task は rrt0 の最高 priority 0 で動きます。service と HAL idle は共通の maintenance を呼び、BM scheduler、最大 4 回の log processing、pool の使用量集計を実行します。service の既定周期は 10 ms、統計 log は 10000 ms です。pool の最大値は maintenance 時点の観測値で、呼び出し間の一時的な最大割当ては含みません。

tick の最小・最大間隔、catch-up 回数、`mrbc_tick()` 回数は、前回の統計から今回までの区間値です。出力用の snapshot と reset を一つの `irq_lock()` 内で実行し、出力中の tick は次の区間へ数えます。pool 最大値と idle / service 回数は起動後の累積値です。stack は出力時点の paint scan による high-water の推定値で、厳密な最大深さではありません。

統計の末尾の `drain_us` は、区間内の `bm_scheduler_process()` 一回あたりの最大経過時間（µs）です。main context の保守経路で cycle counter を呼出し前後に読み、表示後に最大値を reset します。割り込みによる中断時間も含む観測値で、queue 処理時間の保証上限ではありません。ほかの統計 field の順序は変えません。

ISR stack は `CONFIG_INIT_STACKS` で paint します。main stack は no-thread path では自動 paint されないため、main の最初に現在の PSP より 256 bytes 下まで paint します。統計の main stack 使用量は、この未 paint の余裕も使用済みとして数える保守的な値です。

`ruby/selftest/` の三つの task は firmware 専用 API を使いません。Wasm runner へ coordinator、worker_a、worker_b の順で渡せます。busy worker は timeslice の検査用で、通常の待機方法としては使いません。system task は常駐するため、Wasm の終了検査には渡しません。

build と Wasm の成功だけでは、実機の tick 精度、stack の余裕、BLE 接続や切断後の再広告を確認できません。これらは実機での確認が必要です。

## DK 試験用 profile

Kconfig choice `RBOS_TEST_PROFILE` の既定は SELFTEST です。STRESS/OOM は debug build の west build の `--` の後に、それぞれ `-DEXTRA_CONF_FILE=<RBOS>/firmware/stress.conf` / `-DEXTRA_CONF_FILE=<RBOS>/firmware/oom.conf` を渡して選びます。system task は全 profile の先頭です。CI は debug/release に加えて stress/oom を build し、同じ `firmware-evidence-<variant>-<sha>` 形式で証拠を保存します。

STRESS は自己検査三 task に spinner 二 task を追加します。spinner は priority 128 で、coordinator の最終 PASS 後の `$p1_done` を sleep_ms で待ち、開始行を出して常時 ready の loop に入ります。各 spinner は VM tick で10000 msごとに `stress a=<count>` / `stress b=<count>` を出し、count は int32 の範囲に収めるため100万で巡回します。loop 内に sleep はありません。診断有効時は既定8 VMに対して計7 taskです。利用者承認済みの完全接続窓5分を採用しますが、この P2 構成での実機確認は未完了です。

OOM は system と fault task の二つだけです。`OOM: start` の後、配列に1024 byteの文字列を保持し続けます。`vendor/mrubyc/src/alloc.c:570-578` の枯渇分岐は HAL の MRBC_OUT_OF_MEMORY を呼び、`src/hal/hal.h` では `mrbc_hal_abort("Ruby pool exhausted\n")` に展開します。想定する最終行は `RBOS fatal: Ruby pool exhausted` で、LOG_PANIC 後に halt し、自動 reboot はしません。NoMemoryError の rescue loop ではありません。DK での fatal log はまだ未確認です。Wasm はこれらの新 task を compile するだけで、無限 loop や firmware の abort は実行しません。
