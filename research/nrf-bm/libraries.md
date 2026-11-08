# Bare Metal ライブラリの案内

SDK 全体の棚卸しは [component 索引](component-catalog.md)へ統合しました。公開 API と Kconfig の宣言は主題別の一覧を参照してください。

| 主題 | 読む文書 |
|---|---|
| timer・BM scheduler・buttons・GPIOTE・queue・banner・sensorsim | [実行プリミティブ](runtime-primitives.md) |
| LPUARTE・clock・console・flash | [drivers](drivers.md) |
| advertising・接続・GATT・pairing | [BLE ライブラリ](ble-libraries.md)、[services](ble-services.md) |
| storage backend・ZMS・retention・flash map | [保存機能](storage-and-fs.md) |
| logging・shell | [診断経路](logging-shell-console.md) |
| MCUmgr と install metadata | [管理機能](mcumgr.md)、[single-bank DFU](../dfu/single-bank-dfu.md) |
| NFC | [NFC 統合](nfc.md) |
| サンプルと版差 | [全 samples](samples.md)、[公式 latest 比較](version-comparison.md) |

初期 bytecode は firmware に結合します。storage の調査は、アプリデータ・peer manager と将来の OpenBlink 対応のためです。[将来の保存方式比較](../openblink/future-support.md)と区別してください。

[調査索引へ戻る](../README.md)
