# Ver 1 と将来の BLE 転送：脅威モデルと認証候補

[調査索引へ戻る](../README.md)

## 現在の判断

利用者は Ver 1 を「C と事前 compile 済み bytecode を同じ firmware に埋め込む組込み製品」とし、重要な処理を C に移し、mruby/c の実行環境を一つに保つ方針を選びました。[設計と試作結果](a2-p3-design.md)に従い、Ver 1 の目的は**悪意ある任意 Ruby の実行を許した上での強固な sandbox ではなく、不具合の封じ込め**です。転送の認証と HMAC は将来候補であり未実装です。

| 境界 | Ver 1 | 将来の BLE bytecode 転送 |
|---|---|---|
| 信頼するもの | 製品の build・配布主体、C と埋め込み Ruby。C binding の型・範囲・所有権検査 | それらに加え、送信を承認する管理者・鍵 provisioning・端末側 verifier |
| 想定する問題 | Ruby の無限 loop、例外、誤 pin、二重要求、queue/pool 枯渇、user 間干渉、C/driver の故障 | 未認証送信、改ざん、途中切断、replay、旧版投入、別 device 用 payload、保存中の電断、検証後変更 |
| 守るもの | system pin、SD/IRQ/DMA 予約、boot と更新領域、native 管理の進行、回復経路、storage 整合性 | 左記と実行 code の発行元・内容・適用先・鮮度、鍵、承認範囲 |
| 最小策 | system Ruby を置かない、native policy、bounded 要求と資源上限、WDT と診断 | 認証 envelope、再送/commit 状態、replay/rollback policy、検証後不変の blob、loader/VM lifetime 管理 |
| 目的に含めない保証 | native memory の完全 sandbox、任意の C 脆弱性への耐性、侵襲的な物理攻撃への全面対策 | HMAC だけで RAM 分離・CPU 特権分離・実行 code の無害性が得られるという保証 |

firmware image の署名は初期 bytecode も覆いますが、暗号化ではありません。外部転送を追加した場合、そのデータが既存 image 署名で自動的に保護されるわけではありません。OpenBlink の転送 CRC16 も認証ではありません（[固定 source](https://github.com/OpenBlink/openblink-demo-mdbt50q-db-40/blob/d6efc07877ebac6bd55519b8458be4629bef80c3/src/drv/ble_blink.c#L172-L206)）。MCUmgr の reset 等の認証も image 署名と分けます（[MCUmgr 調査](../nrf-bm/mcumgr.md)）。

## sudo 型を採用しない理由

認証を fixture token で代用した [Wasm 試作](a2-p3-evidence/sudo_probe.c)で、次を確認しました。[実行ログ](a2-p3-evidence/sudo.log)は成功だけでなく、不成立を再現した行を残しています。HMAC と統合した試験ではありません。

| 項目 | 結果・意味 | 固定 source の根拠 |
|---|---|---|
| TCB ごとの depth、nested、task switch、子 task、外へ出した非捕捉 Proc | 別 TCB へ権限が漏れない fixture を実装可能 | `vendor/mrubyc/src/rrt0.h:76-96` |
| 例外・break・非局所 return・外部 Task#raise | 試作の Ruby ensure は cleanup を実行 | `vendor/mrubyc/src/vm.c:1716-1770`、`vendor/mrubyc/src/rrt0.c:1179-1204` |
| user が共有 method を定義し昇格 caller から呼ぶ | **昇格したまま実行された** | `vendor/mrubyc/src/vm.c:2975-3048`、`vendor/mrubyc/src/class.c:415-463` |
| Ruby cleanup method の再定義 | **ensure 内の leave を置換し、降格を回避した** | 同 method 定義・探索経路 |
| 昇格中の Task#terminate | **Ruby ensure は呼ばれない**。試作は HAL 観測で native 失効 | `vendor/mrubyc/src/rrt0.c:653-663` |
| C callback の Proc.call 前後で enter/leave | **Ruby block が走る前に C の後処理が走った** | `vendor/mrubyc/src/c_proc.c:112-130` |

したがって `sudo(token) { 任意の Ruby }` と Ruby ensure だけを管理境界にしません。HMAC が正しくても、同じ共有 class 空間にある未信頼 method を特権 caller が実行する問題は残ります。HMAC は「data を承認した」ことの検証であり、その後の method 群の安全性を保証しません。

symbol は共通表に登録され `Symbol.all_symbols` で列挙できます（`vendor/mrubyc/src/load.c:209-225`、`vendor/mrubyc/src/symbol.c:369-380`）。一方、任意の他 VM の String literal/IREP pool を Ruby から読む一般 API は確認できませんでした。「同 image なら他 VM の全 literal を Ruby から直接読める」とは断定しません。配布 image に秘密鍵を literal として置かず、共有 global/constant に置いた token も秘密とは扱いません。

## 将来候補：何に MAC を付けるか

先行の Task wrapper 調査では、後登録 method が builtin より優先され、元 callback の保存・委譲ができることを [Wasm で確認](a2-p3-evidence/task-wrapper.log)しました（`vendor/mrubyc/src/class.c:274-295,415-463`）。ただし get/list の handle は TCB pointer のみで、registry の generation だけでは stale handle を防げません（`vendor/mrubyc/src/rrt0.c:919-969`）。HAL による DORMANT 観測は試作できても専用 lifecycle hook ではなく、直接 VM close や解放の管理が別に必要です（同 `:391-398,653-663`、`vendor/mrubyc/src/vm.c:398-412`）。共有 method 再定義の問題も残るため、これだけで旧 A2 の権限分離を保証できるとは判断しませんでした。C/user-only 構成では system role 用 wrapper 自体を不要にします。

両方式とも未実装です。Ruby のキーワード引数、namespace、返却型も提案であり、製品 API 契約ではありません。

| 方式 | 主な用途 | MAC が覆うもの | 残る設計 |
|---|---|---|---|
| (a) bytecode 全体の認証 | BLE で送った program／短命コマンドを load する許可 | domain・protocol version、device ID、boot nonce または単調 counter、期限、manifest、bytecode 全体または length と暗号学的 digest | manifest は形式・ABI・版・要求資源・許可操作を含める。永続 install と一回実行の鮮度 policy を分ける |
| (b) 操作ごとの challenge-response | reboot 等、既存の native 操作一回の承認 | domain、device、boot nonce、request ID/nonce、操作 ID、**全引数**、期限、必要なら task identity/generation | 保留要求数・期限・使用済み化を native に保持。任意 block の包括昇格にはしない |

候補 (b) の形：

```ruby
challenge = RBOS::Authorization.challenge(:reboot)
# An external administrator returns the challenge with an HMAC
RBOS::System.reboot(authorization: response)
```

native verifier は canonical な形式と長さを検査し、MAC・対象・引数・鮮度を照合し、使用済み化してから限定操作を実行します。検証後に Ruby callback を特権で実行しません。device が user に無制限の任意 message 署名機能を渡すと認証を迂回できるため、そのような鍵 API は公開しません。

### 用途の違いと組合せ

bytecode 自体に HMAC を付けたいという案は、**「受信した code を実行してよいか」には直接対応します**。ただし認証済み code でも資源を枯渇させたり共有 method を変更できるため、自動的に system role へ昇格させません。Ver 1 から続く C policy の下で user code として動かすのが基本候補です。

長寿命の受信 program は (a) で install を認証し、reboot・設定全消去等だけ (b) でその都度承認する組合せが考えられます。逆に「一回の短いコマンド bytecode」へ操作・引数・一回限りの request を manifest として束縛できるなら、(a) に操作承認も含められます。二重 HMAC を無条件に要求するのではなく、承認対象を決めます。

boot nonce は同じ boot 内の重複を単独では防ぎません。request の消費記録が必要です。期限は信頼できる時間基盤と組にし、時刻がなければ起動内の monotonic time と nonce を使う等の契約を定めます。永続 bytecode は boot nonce が変わると再承認が必要になるため、長期 install には永続 counter・版・rollback 状態との組合せを検討します。counter の電断・消耗・更新順序も未設計です。

MAC は chunk ごとの検査だけで終えず、完成した payload 全体と manifest を commit 前に検証します。検証後の mutable String の書換え、ZMS の GC/削除、参照中 blob の交換を禁止またはコピーで分離します。認証と bytecode の構造検査は別です。

HMAC は共有秘密を知る全主体が生成できます。管理端末が多数ある場合の鍵配布・失効・端末紛失、device ごとの鍵、cross-device replay、署名方式との比較を別途決めます。KMU は鍵保管の一部であり、この protocol や Ruby の分離を完成させません。[暗号評価](../openblink/hmac-evaluation.md)を参照してください。

**実機・BM HMAC build・KMU provisioning/slot 読出し・CRACEN・BLE 認証の動作は未確認です。**
