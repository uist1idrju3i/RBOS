# ダイ温度 API

[調査索引へ戻る](../README.md)

## 公開契約

2026-11-12 に利用者が S115 公式 API と class method 形式を承認しました。0.1.1 の互換追加で、MPIG の六 class には含まれない RBOS 拡張です。気温や外部センサを表す API ではありません。

keyword 引数の拒否漏れは宣言済みの契約に合わせる互換 bug fix として 0.1.2 で修正します。署名 image の目標は `0.1.2+0` です。tag 作成・公開や実機の更新経路は検証に含めません。

```ruby
celsius = Temperature.read
puts celsius
```

| 項目 | 契約 |
|---|---|
| method | `Temperature.read`。位置・keyword 引数なし |
| 結果 | ダイ温度の Float、単位は °C。S115 の signed 0.25°C 単位を4で除算。0と負温度も有効 |
| 引数エラー | 引数が一つでもあれば ArgumentError。backend を呼ばない |
| 取得失敗 | RuntimeError。backend 不在、SDK の失敗、S115 無効・取得に不適切な C context を含む。失敗時の一時値は返さない |
| busy / timeout | 共通 status は RuntimeError に変換するが、S115 の `sd_temp_get` が列挙する戻り値は NRF_SUCCESS のみ。独自の再試行・期限・cancel は実装しない |
| instance | `Temperature.new` は TypeError。pin、設定、close は持たない |
| 公開範囲 | 全 Ruby task から使える読み取り専用 API。権限管理・native memory sandbox の完成を意味しない |
| Float 無効 | binding は NotImplementedError を設定して backend を呼ばない。ただし固定 VM 全体の Float 無効 build は下記の理由で未対応 |

既定の mruby/c は `MRBC_USE_FLOAT=2`（double）です。Integer の raw 値は公開せず、nil・0・false を失敗値に使いません。精度、対応温度範囲、異常温度の判定を fake の入力範囲から推定しないでください。

mruby/c の native `argc` は位置引数の数だけです。keyword は別 slot の Hash なので、`MRBC_KW_END()` で未知 keyword も拒否し、取得前に ArgumentError とします。空の `**{}` は引数なしと同じです。位置引数だけの検査で keyword を許可したとは判断しません。

RBS は [`sig/temperature.rbs`](../../sig/temperature.rbs) に置き、同名の class method と Float、生成の常時例外を記述します。例外・待機・資源条件は RBS だけでは表せないため、この本文と併用します。構文は Ruby/RBS 導入環境で次のように検査でき、host test は signature の宣言内容と binding/実行経路を照合します。全 Ruby program の静的型検査ではありません。

```sh
ruby -rrbs -e 'RBS::Parser.parse_signature(File.read(ARGV[0]))' sig/temperature.rbs
```

## 取得経路と寿命

共有 `src/rbos/bindings.c` は Nordic/Zephyr header を含みません。`include/rbos/backend.h` の operation は context と `int32_t *` を借用し、RBOS_OK の場合だけ0.25°C単位の値を書き込みます。provider/context は静的寿命で、`rbos_define_classes()` は VM 初期化後・task 作成前に一度だけ呼びます。task 間に Ruby 値や借用 pointer を保持しません。

nRF は `src/platform/nrf/backend.c` で実装します。IPSR・PRIMASK・BASEPRI・FAULTMASK が0であることを確認し、IRQ/割り込み禁止中の SVC 呼出しを拒否します。`sd_softdevice_is_enabled` の成功と有効状態を確認してから `sd_temp_get` を呼び、一時出力を成功時だけ呼出し元へコピーします。SDK の有効状態 query は各測定の直前に行います。

TEMP の owner は S115/MPSL のままです。app は nrfx_temp/register、IRQ215、DPPI/GRTC、独自の FICR 補正や EasyDMA buffer を使いません。測定出力は C stack に置き、SVC 完了後に借用を終えます。SDK 内部の校正方式を header だけから断定せず、精度条件と実機値の検証は残します。[資源予約](resource-reservations.md)も参照してください。

## 同期処理の承認範囲

`sd_temp_get` は測定完了まで同期的に待ち、仕様上の所要時間は約50 µsです。これは厳密な上限ではありません。binding 自身の spin、IRQ mask、BM event 処理、Ruby 再入はありませんが、SVC 呼出し中に他 Ruby task を実行することはできません。外側の timeout でこの C 呼出しを中断できるとは主張しません。

通常の I/O skill の task-yield 設計に対し、この温度取得だけは利用者承認済みの同期経路とします。ADC/UART 等へこの例外を一般化せず、長時間・可変長の待機は開始・待機・完了に分解します。温度の実時間と tick/BLE への影響を実機で測り、不適切なら owner task/cached 値などの方式を改めて判断します。

## 検査と未確認項目

Wasm は同じ binding と fake backend で、正負・0・0.25°C刻み、型・値、全引数の拒否と副作用ゼロ、constructor の拒否、driver error/busy/timeout/未知 status、backend 不在・復帰、1000回の反復と参照寿命を検査します。fake の制御は Wasm 専用 NativeFixture に置き、firmware へ link しません。

host C は SDK の代役 header で、四つの不正 context・無効/失敗状態・出力不変・復帰・int32境界を検査します。Float 無効の binding も代役 VM header で検査します。固定 mruby/c の `boxing_no.h:87-91` は Float 無効時にも存在しない `RObject.d` を参照するため、VM 全体の Float 無効 Wasm build は失敗しました。vendor は変更しておらず、拒否 guard の host 検査を VM 全体の実行成功と読み替えません。

firmware の既定／stress profile は P1 coordinator の自己検査後に `temperature c=<Floatの°C>` を一回出します。既存の PASS/stats は維持し、OOM profile はこの coordinator を実行しません。診断一回の成功だけで精度・時間・負荷を合格とは判定しません。

DK では、別途温度計との比較条件、負荷・反復時の安定性、取得時間、BLE 接続中の tick、公平性、stack/pool を確認する必要があります。map の静的増分は別途記録しますが、pool の予約量が同じでも内部使用量が不変という意味ではありません。P2 の実機受け入れ、GPIO/Button dispatcher、三電源 ADC は未完了です。

出典: `vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/nrf_soc.h:582-591`、`vendor/sdk-nrf-bm/components/softdevice/nrf54l/s115/s115_API/include/nrf_sdm.h:329-335`、`vendor/mrubyc/src/vm_config.h:39-46`。
