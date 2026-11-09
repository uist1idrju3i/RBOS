# P1 runtime

対象と build 手順は [BM build 手順](../research/implementation/bm-build.md)を参照してください。flash / erase は build に含めません。

## build 時の生成

`cmake/mrubyc.cmake` は `vendor/mruby` を app の build directory の `mruby-host/` にコピーし、host の Ruby と C compiler で mrbc 4.0.0 を作ります。compiler binary は配布しません。既存の host compiler を使う場合は、west build の `--` の後で `-DRBOS_MRBC=/absolute/path/to/mrbc` を指定します。版が異なる compiler は拒否します。

mruby/c の `src/`、`support/`、`mrblib/` も build directory にコピーします。vendor にある `mrblib.c` は使わず、コピー上で `make -C mrblib MRBC=... all` を毎回 configure 時に実行します。vendor にない `_autogen*.h` は、コピー上の `make -C src autogen` で生成します。vendor のファイルは変更しません。元の VM source と mrblib の変更は CMake の再構成対象です。

Ruby の順序は system、coordinator、worker_a、worker_b で固定します。各 `.rb` は build 時に `mrbc -B` で `const uint8_t` 配列へ変換し、生成した `embedded.c` の表から task を作ります。`.rb` の変更は対応する配列の再生成対象です。bytecode は RRAM の rodata に置き、RAM へコピーしません。

生成した task 配列と mrblib は `tools/bm-build/check-bytecode.py` で検査します。先頭の `RITE0400` と、big-endian の宣言サイズが実サイズと一致することを確認し、不一致なら build を止めます。正常・空・不正 magic・不正 version・不正 size の検査は `tests/check-changes/test_bytecode.py` に置き、CI の変更判定 job でも実行します。

VM 数と pool は `CONFIG_RBOS_MAX_VM_COUNT`（既定 8）と `CONFIG_RBOS_VM_POOL_SIZE`（既定 65536 bytes）で設定します。VM の他の設定は上流の既定値です。release は `CONFIG_RBOS_VM_NDEBUG` により、mruby/c source だけに `NDEBUG` を追加します。

## 実行

BM の repeated timer は 31 ticks（992 µs）周期です。絶対 uptime から経過した整数 ms を求め、経過分だけ `mrbc_tick()` を呼びます。IRQ lock は BASEPRI により SoftDevice の priority 0/1 を残します。BLE のイベントは BM scheduler を通して main context で処理します。

firmware 専用の `RBOSSystem.service` は、起動時に保持した system task の VM だけが呼べます。引数は受け取りません。system task は rrt0 の最高 priority 0 で動きます。service と HAL idle は共通の maintenance を呼び、BM scheduler、最大 4 回の log processing、pool の使用量集計を実行します。service の既定周期は 10 ms、統計 log は 10000 ms です。pool の最大値は maintenance 時点の観測値で、呼び出し間の一時的な最大割当ては含みません。

tick の最小・最大間隔、catch-up 回数、`mrbc_tick()` 回数は、前回の統計から今回までの区間値です。出力用の snapshot と reset を一つの `irq_lock()` 内で実行し、出力中の tick は次の区間へ数えます。pool 最大値、stack 使用量、idle / service 回数は起動後の累積値です。

ISR stack は `CONFIG_INIT_STACKS` で paint します。main stack は no-thread path では自動 paint されないため、main の最初に現在の PSP より 256 bytes 下まで paint します。統計の main stack 使用量は、この未 paint の余裕も使用済みとして数える保守的な値です。

`ruby/selftest/` の三つの task は firmware 専用 API を使いません。Wasm runner へ coordinator、worker_a、worker_b の順で渡せます。busy worker は timeslice の検査用で、通常の待機方法としては使いません。system task は常駐するため、Wasm の終了検査には渡しません。

build と Wasm の成功だけでは、実機の tick 精度、stack の余裕、BLE 接続や切断後の再広告を確認できません。これらは実機での確認が必要です。
