# 固定版 v2.0.1 と公式 latest の照合

## 照合方法と範囲

2026-11-08 に公式 [Introduction](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/index.html)を既存 Chrome の CDP に Playwright で接続して読みました。表示は **2.0.99**、footer は **Last updated on Nov 06, 2026**。その目次の同サイト HTML リンク 136 ページを取得し、driver/library/service/sample/DFU の導入記述・設定名と固定版の source/header/Kconfig を照合しました。通信エラーは 0 件です。

これは全 API の仕様等価性・全行差分・最新 binary の検証ではありません。latest は可変であり、再現基準は `vendor/sdk-nrf-bm` の v2.0.1 / `51484143c09199e19bccc16fa3b437f7a502a72b` です。以前の調査で記録した main `14b3836` と、今回表示されたサイトの source commit が一致するかは再確認できていません。

## latest で掲載され、固定版にはないもの

| 公式 latest の章 | 読み取れた機能 | 固定版と RBOS の扱い |
|---|---|---|
| [SPI transaction manager](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/bm_spi_mngr.html) | nrfx SPIM の非同期 FIFO、transaction 内の複数 transfer、任意完了 callback、装置ごとの設定。BM_SPI_MNGR は NRFX_SPIM に依存し RING_BUFFER を select | `lib/bm_spi_mngr`、対応 public header/Kconfig は固定版に存在しない。Ruby SPI backend の将来候補で、今回追加・vendor 更新しない |
| [Memfault](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/memfault.html) | thread なし環境の lock、main/ISR/fault の分離、metrics/coredump/chunk export の統合 | 固定版に専用の導入章・BM Memfault component はない。外部 NCS が持つ Memfault と区別し、現行 RBOS の利用可能機能とは説明しない |
| [MDS](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/bluetooth/services/ble_mds.html) | Memfault Diagnostic Service、upload URI/authorization、diagnostic chunk 通知 | 固定版の service/header/Kconfig に BLE_MDS はない。cloud authorization を扱うので、将来検討でも認証情報の公開範囲を設計 |
| [MDS sample](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/samples/bluetooth/ble_mds/README.html) | BLE gateway への診断 export | 固定版 samples に存在しない |
| [SPI sample](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/samples/peripherals/spi/README.html) | nrfx SPIM/SPIS | 固定版 samples に存在しない。nrfx 自体が利用不能という意味ではない |
| [SPI manager sample](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/samples/peripherals/spi_mngr/README.html) | 外部 flash の read/program/sector erase | 固定版 samples と manager に存在しない |
| [Radio test](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/samples/peripherals/radio_test/README.html) | radio の定常 RX/TX carrier、modulated TX 等の測定 | 固定版 samples に存在しない。通常 BLE stack と併用できると仮定しない |

存在判定は driver/lib/subsys/include/samples の全ファイル棚卸しと [API](api-core.md)・[設定](kconfig-platform.md)の source に基づきます。latest の API 名を固定版の実装として Ruby binding に使わないことが重要です。

## 共通内容と食い違い

| 主題 | 公式 latest と固定版の対照 | RBOS の判断 |
|---|---|---|
| IRQ/予約 | [allocation](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/drivers/allocation_interrupts.html) と固定版で GRTC channel0/GRTC_2、SD priority0/1、BM macro の説明は一致 | 予約外を全て自由とせず SDC/MPSL の仕様も照合 |
| SDH default | [nrf_sdh](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/nrf_sdh.html) は IRQ を default と説明。固定版 Kconfig の choice は SCHED を default とし、SCHED 自体は BM_SCHEDULER 依存 | BM_SCHEDULER が使えなければ別の choice へ解決され得る。単純に「常に IRQ/SCHED」とせず .config を保存して確認 |
| storage | [bm_storage](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/bm_storage.html) の SD 非同期/直接 RRAM 同期、同期 event の defer、[ZMS](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/bm_zms.html) の空き sector/GC は固定版と整合 | buffer の所有と完了処理を nRF backend の契約にする |
| NFC | [integration](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/libraries/nfc/integration_notes.html) は TIMER24、NFCT/TIMER の専有、SD clock と IRQ を説明。固定版にも同内容あり | 独自 timer/clock 操作と競合させない |
| DFU | [single-bank](https://nrfconnectdocs.nordicsemi.com/ncs-bm/latest/nrf-bm/app_dev/dfu/single_bank_dfu.html) は app の直接上書き、installer による SD/loader 更新後の再 app 更新を説明。固定版も同方式 | A/B へ変更しない。bytecode は firmware に結合 |
| board | latest の sample 対応表には nRF54LC10 DK があるが、固定版の boards/nordic は L15/LM20/LV10/LS05 の 4 directory | 固定版の全 SoC 対応を latest の表で補わない。対象 L15-DK は変更なし |

固定版の根拠: `vendor/sdk-nrf-bm/doc/nrf-bm/drivers/allocation_interrupts.rst:1-42`、`vendor/sdk-nrf-bm/subsys/softdevice_handler/Kconfig:1-263`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nrf_sdh.rst:1-220`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_storage.rst:1-169`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/bm_zms.rst:1-366`、`vendor/sdk-nrf-bm/doc/nrf-bm/libraries/nfc/integration_notes.rst:1-89`、`vendor/sdk-nrf-bm/doc/nrf-bm/app_dev/dfu/single_bank_dfu.rst:1-42`。board の latest 側は上記 MDS sample 対応表、固定側は各 board.yml（例 `vendor/sdk-nrf-bm/boards/nordic/bm_nrf54l15dk/board.yml:1-111`）。

## source 側にあり導入目次では見つからないもの

今回の公式目次には ble_conn_state、ble_racp、boot_banner、zephyr_queue、bm_rmem/ble_rmem、bm_installs、個別 logging/shell backend の専用導入章がありませんでした。固定版には source・Kconfig・public header（または外部 API への接続）があり、この調査で項目を補っています。API reference や他章からも一切参照されないと主張するものではありません。

逆に clock_control は directory があっても独自 C 実装でなく library amend、MCUmgr protocol/mgmt/os/util は外部 Zephyr の source を取り込みます。directory 数だけで BM 独自実装の数を数えません。[drivers](drivers.md)、[MCUmgr](mcumgr.md)に根拠を記載しています。

移行判断では「名称が同じ」だけでなく API/struct、default と select、IRQ model、map/stack、署名・loader・metadata の互換を再評価します。今回 vendor、依存版、製品の機能範囲は変更していません。

[コンポーネント索引](component-catalog.md) / [調査索引へ戻る](../README.md)
