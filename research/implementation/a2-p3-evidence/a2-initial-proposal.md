# A2: P3 権限・watchdog・reboot の設計案（未承認）

[調査索引へ戻る](../../README.md)

これは C/user-only を選ぶ前の未承認案の原文です。[現在の設計](../a2-p3-design.md)を優先してください。特に #10 の「他 task の飢餓も reset で回復」は system heartbeat 単独では保証できず、後続調査で訂正しました。Task callback の再実装以外に、元 callback を保存して委譲できることも判明しています。以下は当時の本文を保持します。

調査の基点: main `3a88395`。この文書は提案であり、repository には push していません。

## 前提（既決の方針として維持するもの）

- user VM の `priority=` / `suspend` / `terminate` / `raise` は自分自身にだけ許可します。system task は user から変更できないようにします（`porting-plan.md:76`）。
- 特権 callback では、呼び出しの入口で必ず caller を検査します。class 名を隠すことには頼りません（`:74`）。
- watchdog の kick は system task が担当します。fatal のとき、debug では halt、release では log を flush してから reboot します（`:77`）。
- native memory を完全に sandbox 化したとは主張しません（`:79`）。

## 現状（調査で確認した事実）

- system task は「task table の先頭」で、`runtime.c:14` に pointer を1つ保持しているだけです。caller を検査しているのは `RBOSSystem.service` だけです。
- 固定版 mruby/c の Task API（`rrt0.c:1333-1360`）には認可がありません。`Task.get` や `Task.list` で他の task を取得し、`suspend` や `terminate` を実行できます。
- VM ID は再利用されます。また、終了（DORMANT）、run/rewind による再実行、delete は、それぞれ別の経路です。
- WDT、reboot、reset reason は未接続です。BM board の DT からは `wdt30` と `wdt31` が削除されています。ただし nrfx_wdt、`sys_reboot`、HWINFO は固定版の中にあります。MCUboot にも WDT を feed する経路があります。

## 推奨案

| # | 論点 | 推奨 | 理由・欠点 |
|---|---|---|---|
| 1 | system の信頼元 | 署名済み image 内の task table に、`role` を明示します（先頭であることに依存しない） | 署名で信頼の起点を一本化できます。外部 bytecode の認証は、将来 OpenBlink 転送を扱うときの課題とします |
| 2 | 権限の表現 | native registry に、TCB pointer、generation、capability bitset を持たせます | VM ID だけでは、再利用されたときに権限が漏れます。generation で、古い参照を無効にできます |
| 3 | 子 task | `Task.create` で作った task は、常に user 権限にします | 継承や委譲の経路を作らないことで、権限の漏れを構造的に防ぎます。system が補助 task を必要とする場合は、別の課題とします |
| 4 | 失効と再実行 | DORMANT になった時点で失効させます。run/rewind で再開した task は、user として新しく登録します。system task が終了した場合は fatal とします | 失効の時点が1つに決まります。system task を作り直す経路はなくします |
| 5 | system が操作できる範囲 | system は、すべての user task を監督できます | 現在の構成は system task が1つだけなので、これで足ります。supervisor capability を分離するのは、必要になってからにします |
| 6 | Task API の範囲 | user に対しては、変更系の操作（`priority=`、`suspend`、`resume`、`terminate`、`raise`、`run`、`rewind`、`name=`）をすべて自分自身に限ります。`get`、`list`、`status` などの参照系は公開のままにします | 列挙を禁止しても、変更系を止めなければ意味がありません。参照系を残せば、既存の Ruby が使い続けられます |
| 7 | 認可を置く場所 | 共通の caller-check helper を作ります。RBOS 側で Task の method を再定義して、上書きします | vendor の `rrt0.c` の callback は static で、vendor は編集しません。そのため、公開されている C API（`mrbc_change_priority` など）を使って再実装します。欠点は、上流の Task の挙動との差分を保守する必要があることです。この差分は、Wasm の互換性試験で検出します |
| 8 | user に許す peripheral | 固定の allowlist にします。GPIO（DT で許可された pin）、ADC、Button、Temperature は user にも許します。system LED、loader への遷移、storage は system だけに許します | 現在の API の範囲で、すぐに定義できます。VM ごとの lease は、資源が競合するようになってから導入します |
| 9 | WDT backend | RBOS の backend 契約で包み、nRF 側は nrfx_wdt を直接使い、host 側は fake にします | BM では DT の node が削除されているためです。instance（WDT31 を想定）と security 設定は、A3 の build で確認します |
| 10 | kick の条件 | `RBOSSystem.service` が、system task が進行しているときにだけ native helper から feed します | system task が止まった場合も、他の task に飢餓が起きた場合も、reset で回復できます。user から feed することはできません |
| 11 | timeout | profile によらず共通の値にします。sleep 中も計時し、debug halt 中は止めます。値は system loop の周期を A3 で測ってから決めます | 推測で値を固定しないためです |
| 12 | release で fatal が起きたとき | 期限付きで flush してから `sys_reboot` します。WDT は最後の回復手段として残します。loader への退避は将来の課題です | 既決の方針を、最小の構成で実現します |
| 13 | reset reason | 最初は起動時の log に出力するだけにし、Ruby には公開しません。MCUboot が値を clear する条件も記録します | API を公開すると契約が増えます。実機で値を確かめてから公開します |
| 14 | debug API | release の build では登録しません | 権限の検査に頼らず、release ではその経路を物理的になくします |
| 15 | 拒否時の契約 | 既存に合わせて `RuntimeError` とします。拒否したときに backend を呼ばないこと、task の状態が変わらないことを試験します | 既存の service の挙動と一致し、skill の要件も満たします |
| 16 | 実装の分割 | A3 を3つの PR に分けます。PR1: registry、Task 認可、拒否試験（Wasm）。PR2: 特権 API の入口検査と peripheral allowlist。PR3: WDT、reboot、reset reason（BM と fake） | Task の認可と回復の backend は互いに依存しないため、別々に review できます |

## 未確認として残すもの

- WDT と reboot が実機で動くこと、reset reason の実際の値、bootloader をまたいだときの挙動は、Phase B（B-3）で確認します。
