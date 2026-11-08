# mruby/c の Wasm 検査

host の mrbc と emscripten HAL を使い、Ruby の compile と smoke test を実行します。
firmware の build や Nordic の IRQ・BLE・タイミング試験を代替するものではありません。

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

- `tests/mruby/` では複数 task、sleep_ms、priority、pass、Mutex、join/value、rescue、空プログラムを実行します。
- 未捕捉例外の fixture は exit 1 と例外メッセージを照合します。引数なし・存在しない file・空 file・不一致 RITE version は exit 2 と診断を照合します。timeout は失敗です。
- 将来の `src/**/*.rb` はすべて個別に compile します。まだ存在しなければ 0 件として成功します。これらは無限 loop や native API を含み得るため、自動実行しません。

runner は `.mrb` ごとに task を作り、Node.js の NODERAWFS で読みます。ASYNCIFY を有効にし、emscripten HAL の MRBC_NO_TIMER と MRBC_SCHEDULER_EXIT に従います。検査用 heap は 1 MiB、MAX_VM_COUNT は 32、実行 timeout は 30 秒です。BM のメモリ設定ではありません。

例外時に VM は `mrbc_run()` へ 2 を返し（`vendor/mrubyc/src/vm.c:3307-3335`）、scheduler はその終了状態を保持します（`vendor/mrubyc/src/rrt0.c:391-400`）。通常の task は終了時に例外を解放するため（`vendor/mrubyc/src/vm.c:362-371`）、runner は公開 hook `MRBC_ABORT_BY_EXCEPTION` で解放前に記録・表示し、同じ参照を解放します。permanence task も scheduler の戻り値で失敗とします。flag_permanence を runner から変更せず、Task.value の通常の戻り値を保ちます（`vendor/mrubyc/src/vm.c:1734-1745`）。

bytecode の buffer は VM 終了まで保持します。runner は信頼するローカル compiler の生成物を対象とし、不正な任意 binary を安全に処理する validator や sandbox ではありません。実行後の資源はプロセス終了時に回収します。

emsdk の上流: [emscripten-core/emsdk](https://github.com/emscripten-core/emsdk/tree/6.0.12)（MIT）。新規の検査用依存であり、旧版からの更新ではありません。ASYNCIFY と Node filesystem を採用し、ブラウザー配信・BM HAL の emulation は対象外です。

[リポジトリ README へ戻る](../../README.md)
