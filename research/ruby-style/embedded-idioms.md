# 組込みと rrt0 に合わせた Ruby の書き方

ここは mruby/c の制約から導いた RBOS 向け設計指針です。Ruby community 全体の規範や、未実装の I/O の動作保証とはしません。既存の [scheduler lifecycle](../mrubyc/scheduler-lifecycle.md)、[ownership](../mrubyc/c-api-ownership.md)、[memory sizing](../mrubyc/memory-and-sizing.md)に詳細を委ねます。

## 進行と所有者をコードに表す

- 待ち時間には `sleep` / `sleep_ms`、並行する役割には `Task` を使います。成功例は今回の `sleep-mutex` と既存 runner の scheduler test です。busy-wait は他の foreground 処理と電力に不利で、tick による切替だけへ頼りません。
- `Mutex` は Ruby task 間の共有状態を守るものです。IRQ と共有する lock にはしません。lock 範囲・取得順・例外時の unlock を明示します。probe は lock/unlock の正常系だけで、競合・所有 task 終了・cancel の安全性は未検証です。
- 一つの bus に複数 task が要求する場合は、短い Mutex 範囲か、単一 owner task に transaction を渡す設計を検討します。後者は RBOS の提案で、queue API はまだありません。
- request の順序、buffer の上限、待機 task の数、timeout 後の遅延 callback の扱いを先に決めます。`private` や「普段はこの順に呼ぶ」という慣習を認可・競合防止の代わりにしません。

MPIG の同期的な `read` は呼出し task が待つ契約です。**native method の中で C の blocking read を呼ぶだけでは、rrt0 全体を止め得ます。** C の stack を Ruby の sleep と同様に自動保存できるとは限りません。[I/O と scheduler の設計案](../io-api/rrt0-integration.md)に待機の分解と未検証事項を記載します。

## collection の表現と割当てを分けて考える

`map` は変換結果、`select` は必要な要素、`any?` は存在確認を表します。これらの [実行入力](probe-inputs.md)は小さな Array での意味を確認したもので、割当て量や速度を測定したものではありません。hot loop では以下を確認します。

| 確認 | 判断 |
|---|---|
| 毎回の Array / Hash / String 生成が必要か | 初期化時の設定と繰返し処理を分離。再利用する buffer には容量上限と所有者を定義 |
| 変換結果を捨てていないか | `map` ではなく `each` や bounded while を検討 |
| 中間 collection が増えていないか | chain の読みやすさと一時割当てを比較。明示 accumulator は `sum-alternative` で確認 |
| object が互いを保持し続けないか | parent-child / callback-owner / queue-request の cycle を避け、完了・cancel・終了時に参照を外す |
| device 入力が無制限でないか | 長さ・件数・timeout・最大再試行を契約化。OOM が例外で必ず回復可能とは仮定しない |

mruby/c は refcount であり tracing GC ではありません。cycle の回収や、再利用すれば必ず速いという主張はしません。native へ値を保持する場合は [C API の ownership](../mrubyc/c-api-ownership.md)を守ります。String の immutable 化に `freeze` を使う案は現構成では不可です。

## 値と例外の境界

- int32 を前提に byte count、時間、周波数の積を見積もります。今回 `int32` は Wasm で wrap し、`int64-literal` は load 失敗でした。compiler の定数畳込みで大きい literal になる場合と実行時演算を区別します。nRF の overflow・浮動小数点精度は別途確認が必要です。
- String は既定で byte 単位です。`bytes` は UTF-8 の「あ」の length が 3 であることを確認しました。UART/SPI の payload と表示文字列を同じ文字数 API で処理しません。
- `||=` は nil だけでなく false も置換します。sensor の false、通信の空データ、読み込み失敗の nil を混ぜません。`truth-memo` が意味の確認です。
- 通常の業務失敗を捕捉する範囲は `StandardError` 系に限定します。未実装 opcode が根の `Exception` を投げることを理由に、全 loop を `rescue Exception` で囲んで正常動作に見せかけません。`standard-rescue` は bare rescue では捕まらない経路を明示的に確認する診断用入力です。
- cleanup に ensure を使えることは `ensure` で確認済みですが、task の強制終了・reset・OOM の全状況で実行される保証までは試験していません。

ISR は bounded event を native queue へ渡すだけとし、Ruby 呼出し、allocation/refcount、raise、task 操作を直接実行しません。[IRQ 境界](../mrubyc/hal-porting.md)と [S115 の割込み制約](../nrf-bm/softdevice-and-interrupts.md)に従います。nRF での latency、stack、RAM、電力は未測定です。

[原則](principles.md) / [対応表](idiom-compatibility.md) / [調査索引へ戻る](../README.md)
