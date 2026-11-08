# イベント・時間・GPIO の共通ライブラリ

[API](api-core.md) と [全 Kconfig](kconfig-core.md)を契約の索引とします。S115 で全 component が候補ですが、実機での並行動作は未確認です。

| component | 目的・API/型・event | context・再入制約 | メモリと Ruby backend 候補 |
|---|---|---|---|
| bm_timer | init/start/stop、single-shot/repeated、`struct bm_timer`、timeout handler | k_timer timeout から利用者 handler を直接呼ぶ。IRQ priority default 5（SD なし 3）、1 μs resolution でも最小 timeout は約 152 μs。handler から VM 実行や待機をしない | timer object に k_timer と callback。利用者 instance 数で増える。`timer_start/stop`、tick 供給。ただし Ruby `sleep` は rrt0 に任せ、timer ごとに VM を作らない |
| bm_scheduler | defer が event と data を専用 heap へコピー、process が main で callback を実行 | defer の失敗は -ENOMEM 等。process は queue が空になるまで drain。producer が連続生成すると一回の処理時間に上限がない。copy は浅いので data 内 pointer の寿命は別管理 | heap default 512 bytes に event header と allocator overhead が加わる。`platform_poll/event_enqueue` の内部機構で、Ruby task scheduler の置換ではない |
| bm_buttons | init/enable/disable/deinit/is_pressed、config array、press/release event と debounce | GPIOTE → timer で状態を観測し handler 呼出。config array・callback を保持。global state があるので binding が自由に多重 init しない | pin 数 default 24、timer と状態表。`button_subscribe/state/unsubscribe` の候補。event を foreground へ移して Ruby block を呼ぶ |
| bm_gpiote | GPIO port に合う `nrfx_gpiote_t *` を取得 | SYS_INIT が nrfx instance と IRQ を初期化。default priority 5。利用者は channel・pin の所有権を共有管理 | instance 配列は GPIOTE_COUNT に依存。`gpio_config/read/write/watch` の土台。単純 LED 出力に必ず event channel を消費するわけではない |
| boot_banner | 起動時にアプリ名・BM 版・任意 Zephyr 版を printk | SYS_INIT の出力。独立した公開 BM header/API はない | 文字列・printk の RRAM、正確な増分は map 待ち。`diagnostics_version` に使う版情報とは分け、通常は Ruby class 不要 |
| sensorsim | `sensorsim_init/measure`、config と state で三角波状の測定値を生成 | caller が状態を所有し、同じ state の同時更新は直列化。実 sensor driver ではない | state/config の sizeof 分。Wasm fake の `sensor_read` や実機デモの入力候補。製品の測定値として扱わない |
| zephyr_queue | 上流互換の k_queue_* を thread なし環境で提供 | IRQ lock で list を保護。blocking wait に頼らず foreground で取り出す。外部 Zephyr header の API で、独自公開 BM header はない | queue node と alloc 方式に依存。`event_queue` の内部候補。Ruby object を queue に直接入れず native payload を所有 |

根拠: timer は `vendor/sdk-nrf-bm/include/bm/bm_timer.h:1-120`、`vendor/sdk-nrf-bm/lib/bm_timer/bm_timer.c:1-91`、`vendor/sdk-nrf-bm/lib/bm_timer/Kconfig:1-29`。scheduler は `vendor/sdk-nrf-bm/include/bm/bm_scheduler.h:1-83` と `vendor/sdk-nrf-bm/lib/bm_scheduler/bm_scheduler.c:1-83`。buttons は `vendor/sdk-nrf-bm/include/bm/bm_buttons.h:1-160` と `vendor/sdk-nrf-bm/lib/bm_buttons/bm_buttons.c:1-387`、GPIOTE は `vendor/sdk-nrf-bm/lib/bm_gpiote/gpiote.c:1-81`。banner は `vendor/sdk-nrf-bm/lib/boot_banner/banner.c:1-53` と `vendor/sdk-nrf-bm/lib/boot_banner/Kconfig:1-37`、sensorsim は `vendor/sdk-nrf-bm/include/bm/sensorsim.h:1-98`、queue は `vendor/sdk-nrf-bm/lib/zephyr_queue/src/queue.c:1-301` と `vendor/sdk-nrf-bm/lib/zephyr_queue/Kconfig:1-10`。

## Ruby が常時 ready のときも進行させる

SoftDevice event の配送を BM scheduler にするなら、VM の idle 以外にも `bm_scheduler_process()` を実行する機会が必要です。SDK API は時間 budget を受け取らないため、「一回呼べば一定時間内に戻る」とは保証できません。

RBOS の設計案は、native callback を短くし、event producer を制限し、BM と Ruby 双方の backlog・drop・最大待ち時間を測ることです。scheduler の追加 heap は Ruby heap と別に予算化します。IRQ からの defer も zero-latency IRQ に無条件で安全とはしません。Zephyr heap・list に入れるのは application IRQ/foreground に限定する方針です。

## stack と動的メモリ

timer の利用者 context と callback、button config、GPIO handler、queue 内 pointer は処理完了まで有効である必要があります。Ruby String の backing pointer を借用したまま非同期要求を返す実装は避け、backend がコピーまたは参照を保持します。この所有権管理は SDK が Ruby GC のために行うものではありません。

sizeof と Kconfig から分かる静的容量以外の stack、heap fragmentation、実際の RRAM 増分は未測定です。tick 中の worst-case latency と timer stop 後の通知も HIL の試験項目にします。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
