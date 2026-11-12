# P2 の native 共通基盤

P2 の最初の共通基盤を記録した文書です。後続の [GPIO/Button](gpio-button-api.md)、[温度](temperature-api.md)、[ADC](adc-api.md)、[予約表](resource-reservations.md)に公開 API と backend を追加しました。実機の受け入れは未完了で、[checklist](checklist.md#p2-native-api-と資源)に未確認項目を残します。

## callback の規約

共有実装は `include/rbos/native.h` と `src/rbos/native.c` です。vendor の `mrubyc.h` を使い、Nordic/Zephyr の header は含めません。

| 操作 | 契約 |
|---|---|
| `rbos_require_argc` | 位置引数の最小・最大を含む個数を検査。範囲外は ArgumentError。引数へ触れる前に呼ぶ |
| `rbos_require_type` | 型の一致を検査。不一致は TypeError。暗黙変換はしない |
| `rbos_require_integer` | Integer 型を検査し、最小・最大を含む範囲外は RangeError。失敗時は出力先を変えない |
| `rbos_require_status` | invalid pin は RangeError、unsupported は NotImplementedError、それ以外の非 OK は RuntimeError。IO・未知の値は `Driver failure`、busy は `Device busy`、timeout は `Device timeout`、reserved は `Pin is reserved` |
| `rbos_return_borrowed` | incref 後に返却 slot の旧参照を decref。返却 slot と借用元が同じ場合も保持する |
| `rbos_return_owned` | 生成した一参照を返却 slot へ移す。移譲後に呼出し元が decref しない |

require helper が false を返したら callback を直ちに終了します。例外設定後に backend を呼ばず、返却 slot も上書きしません。型の helper には、argc 検査を通過した有効な値の pointer を渡します。範囲の上下限と出力先は binding 実装側の責任です。`rbos_return_owned` へ借用値を渡してはいけません。

native callback の `argc` は位置引数だけで、keyword は `v[argc+1]` の Hash にあります。新しい binding では、keyword を使う API は MRBC_KW_ARG 等で取り出してから MRBC_KW_END で残りを検査し、使わない API も MRBC_KW_END で未知 keyword を拒否します。[温度 API](temperature-api.md)は引数0の検査とこの検査を組み合わせ、拒否時の backend 副作用も Wasm で確認します。根拠: `vendor/mrubyc/src/value.h:405-456`。

これは内部 C 規約です。Ruby の error hierarchy や peripheral API の標準契約を決めたものではなく、各 API の追加時に MPIG と照合します。既存の `RBOSSystem.service` は権限検査を先に行い、その後の argc 検査だけを共有 helper に置き換えます。成功時の戻り値、無権限時の拒否、引数不正のメッセージは変えません。

## event ring

共有実装は `include/rbos/event_queue.h` と `src/rbos/event_queue.c`、firmware の保護は `firmware/src/runtime.c` です。

- 静的にゼロ初期化する16件の ring です。一回の push が一 event を表し、入力の count は使いません。callback、動的確保、Ruby 操作は行いません。
- completion は source が同じでも別々に FIFO へ入ります。満杯では新しい event を捨て、overflow を増やします。
- Button は同じ source（解決済みの物理 pin）と generation の未処理 event にまとめます。最初の FIFO 位置を維持し、count を加算して value を最新値へ置き換えます。これは全 edge の時刻・値の列を保存する仕組みではありません。
- 満杯でも既存 Button の coalesce は受け付けます。別 pin は新しい event なので満杯なら捨てます。pop 後の同じ pin は新しい event になります。
- count が UINT32_MAX ならその追加 edge を捨て、overflow を増やします。捨てた edge の値は反映しません。overflow と coalesced も UINT32_MAX で飽和し、0 へ巻き戻りません。
- push は最大16件を走査し、pop は一件をコピーします。実行時間の実測や IRQ latency の上限は未確認です。

core 自体は lock を持ちません。firmware の `rbos_event_post` / `rbos_event_take` と stats snapshot が `irq_lock` を使って直列化します。現在の BASEPRI では SoftDevice priority 0/1 は止まらないため、この経路の producer は NVIC priority 2以上のアプリ側 IRQ に限定します。SoftDevice IRQ から直接 post してはいけません。SDH 配送と callback context は peripheral 実装時にも照合が必要です。

consumer の取り出し口だけを追加し、未処理 event を保守処理で捨てるような仮 dispatcher は入れません。Button の producer、資源所有、Ruby callback の寿命・通知処理は未実装です。

## stats と検査

既存 stats の末尾に `event_pending`（snapshot 時点の件数）、`event_overflow`（起動後の破棄数）、`event_coalesced`（起動後の集約数）を追加します。後二つは累積・飽和 counter です。P1 の tick/drain の区間 reset は変えません。

`tools/bm-build/check-dk-log.py` は旧 log と新 log の両方を読みます。未記録の event 統計は未測定とし、0 と推定しません。overflow が一件以上あれば FAIL、pending が16超・counter が32-bit超・累積値が減少しても FAIL です。

再実行コマンド:

```sh
tools/mrubyc-wasm/check.sh
python3 -m unittest discover -s tests/check-changes
python3 .github/scripts/check-skills.py
python3 .github/scripts/check-research.py
git diff --check
```

Wasm は argc/type/range、nil・空 String/Array、境界値、IO/busy/timeout/未知 status、拒否時に backend が呼ばれないこと、失敗後の回復を試します。String/Array の借用、返却 slot と借用元の同一参照、生成値の移譲は Ruby の結果と500回の C 操作前後の pool 使用量で確認します。実機の認可・割り込み・stack/pool の瞬間 peak を確認したことにはしません。

host C は FIFO、ring の周回、満杯時の破棄、複数 pin と completion の分離、pop 後の再受付、count と統計の飽和を試します。実際の IRQ 競合・tick jitter は host C だけでは確認できません。

## 残る受け入れ条件

- peripheral/DPPI/IRQ の完全な予約表と SDH・SD RAM・BM queue の照合。
- GPIO/Button と温度 API の契約、実機 backend、foreground から Ruby への通知。
- 追加する各 API の map 増分と stack/pool 観測、DK の正常・失敗・timeout 試験。

この変更は公開 Ruby API を追加・変更しないため VERSION を増分しません。firmware の stats は診断出力で、旧形式の checker では新 log を読めないため、同じ revision の checker を使用してください。

[実装計画へ戻る](porting-plan.md)

[調査索引へ戻る](../README.md)
