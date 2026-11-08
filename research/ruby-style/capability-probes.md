# Ruby idiom の Wasm 実行記録

調査日: 2026-11-08。RBOS の基準 commit は `bd634b2eb06c58494209a06437a197c35af6bbac`。vendor・runner・永続 tests は変更せず、研究用の一時入力を既存 runner で個別に実行しました。後続 skill の回帰 fixture は別 PR の対象です。

## 再現条件

- compiler: mruby 4.0.0、`831da26b9021de0369d17b71b5667e2941a1a32d` の mrbc。
- VM: mruby/c `434bccd609f2a3e90d6bb95c458621898bc6a508`。
- emcc: 6.0.12、Node: v24.21.0。build flags / copied HAL の範囲は [check.sh](../../tools/mrubyc-wasm/check.sh)と [runner 説明](../../tools/mrubyc-wasm/README.md)。vendor の source 自体は編集しません。
- runner.js SHA-256: `0d7b54e3e62732d52ffc09333cd1604d57a20a142f4ed671b2100d9089a0f564`。
- runner.wasm SHA-256: `61f7879ee7983ad456e527d5808d43843f080dd6a775d5dfe37a3b3e5a130fbb`。

[成功側の全入力](probe-inputs.md)と [非対応側の全入力](negative-probe-inputs.md)を UTF-8 / LF、末尾 newline 付きで保存します。既存 check.sh で runner を構築し、同じ compiler で `mrbc -o ID.mrb ID.rb`、`timeout 5s node tools/mrubyc-wasm/build/runner.js ID.mrb` を実行しました。全入力の compile exit は 0、timeout exit 124 はありませんでした。表の exit は runner process の終了値です。空出力の成功例は `raise unless` 等の assertion を通過したことを意味します。

## 結果と生成物

input / bytecode はそれぞれ SHA-256。非対応例は失敗を期待して記録したもので、runner の check.sh 自体の失敗ではありません。エラー出力の改行は表中で ` / ` に置き換え、研究用ファイル名は directory を除いた名前に正規化しました。

| ID | exit・出力 | input SHA-256 | bytecode SHA-256 |
|---|---|---|---|
| `names` | 0: 出力なし | `d1667d69028c2b93aba2d67e265de20af0512426545465e83a9b87f5e30ecd05` | `39b4e1b61b4393b80401ae487eed3907afc070533c22f9210aede9d2775986a5` |
| `guard-case` | 0: 出力なし | `17a444ee8cd6d8d5077a7d8fefb34de8a4edd0088ff6a43baf248071c95178be` | `3b7fc4a2010bb4cc1513331b2b2d41aecb7dac9fa6cec14058dde0b96af45a63` |
| `truth-memo` | 0: 出力なし | `f032dae1528ec5f536ee018a033717ae1cc7f869ef50b12dc77dadd81b5d0c72` | `bfddb36300f01d87e8b9e9b45b5b66899cd00f30df9d5fba44ae52d55f0b6a4e` |
| `safe-nav` | 0: 出力なし | `232f9d5e90c0a3b54511415c02e1269ea855d13fdb54c1f03b14f4ed56e78c49` | `cb6cde7c02491e6ea89866b37c51555d6817548794caf81d42090be33df2dc41` |
| `collections` | 0: 出力なし | `28ef240c25c7a85e1153f7e460a0b060cd38d743feb599dbb93464f3f3c8d19c` | `f5e0cc5d556c6deec267fe69245869f29f3f7e298c5d10cb523882f1af0e9f46` |
| `bounded-loop` | 0: 出力なし | `4fe195cae721f5c23e40e4eb880f645195c4304da3bef49be87293833424a59c` | `8291dae4f5f928879d7ef7999f34fbc021e2208d8dffc944ac09a934177457cc` |
| `hash` | 0: 出力なし | `82ebf81e6678a1b963d72d2a6a900eba1c139a44c84592eed76932cb211213e5` | `8aeafe85337b0793db56aba15504123e211ab1c736d8b3a5b50feb43224d63df` |
| `keyword` | 0: 出力なし | `daf2c5077ac32bd17e43f855663157f98b322e116fb77d7f53d0b196fbb2901a` | `de4ecdf64f8255e455645d286295640f6bdc8b03e0b861098ac8f5e023e09fc1` |
| `block-proc` | 0: 出力なし | `120f54d6d46492259e288ca2425aa56b1cdc29ce20f5110af0e76ae878a393ee` | `d2a8c2abeee0a4d95371ad71a169c24217aa356e0b26139b846c45cbebed98bd` |
| `mixin` | 0: 出力なし | `b967e104524e17f92665b81c43a3ba5a5d518ce60d4d138e364f2a6910c9d8dc` | `cbbff4841223c4ba8d3e0b35a4659138941baada71bdf404aa6272954eb9d9f8` |
| `ensure` | 0: 出力なし | `17a944b282b4fc30a769e73db7f35c188de58181c3432025c2820371b64fcd7e` | `f30d33ba37f6b0e53c9aecb9bc246f1910955fcaca24da0a090b1116d4546767` |
| `standard-rescue` | 0: root caught explicitly | `87c4ee90dc34650b50c6b7f0d9c3bb85d36589556009a6b21fa693c2ed7fd2d2` | `20466623a2ddee34bf4af59cf2c1eeb74fa05d86d3585eb10724206c3daaec12` |
| `pattern-array` | 0: 出力なし | `34f79756863d2871b8bdfaf13f0480c04d3c74e733629009389bfab6884c2520` | `73bd65c0585f9352326b2e6bd98e5cb6af650871f4f0c5fd6cda86e7a5c937e7` |
| `pattern-hash` | 0: 出力なし | `f287dd14e9acb52832236e13274043f9e7f927585011fe1409256c56b0bad9a3` | `5cdccac68efda14848f1b4e75c4ed912e33103a9a9053de5ab581518be92d25f` |
| `pattern-miss` | 0: 出力なし | `698e57416322321c7e4a9991029afd239e347b06fb1e1778a2f5c0ee956ccfc1` | `c447a68d4f6c942ae96ad84d3af4189246d18f26eacd0a63a4d241babc1cd375` |
| `count` | 0: 出力なし | `6ce5afd038c2c7a6aa95f4a70f3867e9e930d2fb9199d60ca29dd73669fb6fdc` | `8c52b9282d52ac66a2a31ec16b931dc852e70979e4b6b6635d4eacfeead22a22` |
| `privacy` | 0: 出力なし | `ff5f2e31fc342d386b1cc0751afcae0554ec97ab799b475368c4f5223bc11fa0` | `768289cd063368663a0a2b5468162243ae1e2536dc61e642daa19c4348ac9c1c` |
| `sleep-mutex` | 0: 出力なし | `e9fda452ca5968332b473226ba0b628b0c2c7334d39e6cdba78d3c73d0f74997` | `8354643d01ae97ded92d3704509d066d20f119cc991acda3badb93f4c21619d6` |
| `freeze` | 1: Exception(vm_id=1): undefined local variable or method 'freeze' for Array (NoMethodError) / Uncaught task exception (scheduler status 2) | `3614ba03962cb4a0424a240b36b1a25a03c68cb0a0336ffc5483ccefdedd7c4b` | `30d2283112605c1f070918bbe3658ce259ad1fd4fb09cb4e20dbfbb8d93564e4` |
| `symbol-proc` | 1: Exception(vm_id=1): no block given (yield) (Exception) / 	in `map' / 	in `each' / 	in `map' / Uncaught task exception (scheduler status 2) | `38b2b98d5abc05351c5058aafe08969a64fb6edd3c9791d04258144db01ca1cc` | `519aa13cac3022042aede4bcaa77a064f0c2afc09a98ae04130fe3bba80696fb` |
| `reduce` | 1: Exception(vm_id=1): undefined local variable or method 'reduce' for Array (NoMethodError) / Uncaught task exception (scheduler status 2) | `51ccd4e7dfb12c90694570f631964b70cd8efec72aa23e7369ae58eeb988ff5e` | `7ea09ed3f37d06bcd6c065305d5b814174e4028df5e025e8ea0c046e20910b32` |
| `inject` | 1: Exception(vm_id=1): undefined local variable or method 'inject' for Array (NoMethodError) / Uncaught task exception (scheduler status 2) | `18bde4928637f64c45077bfd0edb1b94fd4f4091efffc1b917aa4767e6c87db4` | `727afe21a7d7d557ae90b4d7d7fb30ed602930d1cd7ad563f64a999c98cda25e` |
| `enumerator` | 1: Exception(vm_id=1): uninitialized constant Enumerator (NameError) / Uncaught task exception (scheduler status 2) | `bd433277fd226a220f6b55e9fb337f4436bba8c9fe31cfafb9b79cf2d68b08d0` | `ccd507004d3c84d63bfe590f0bdf3b0bde0643647ed68e6f10a09d1fd990451c` |
| `each-no-block` | 1: Exception(vm_id=1): no block given (yield) (Exception) / 	in `each' / Uncaught task exception (scheduler status 2) | `a7edf19d8e3bc53e9573520e84ec819a8fd360f0f01042911590fa045c367f46` | `e7b8e620b3f4529433eec4368a077dafb7b38708c023a927de82dd591297bc59` |
| `lambda` | 1: Exception(vm_id=1): Unimplemented opcode (0x61) found (Exception) / Uncaught task exception (scheduler status 2) | `02b5cd57420e162f9e3d1b9c2a209eb9d74737ed12478582c33e6db52bb9c5f9` | `07268a7e303bbacae6912d428242ad209b4e088bbc099cc7b7e7164a45a37471` |
| `fiber` | 1: Exception(vm_id=1): uninitialized constant Fiber (NameError) / Uncaught task exception (scheduler status 2) | `63d30f71003c03d7e1439718a1b5132b137725df6c2a3697b8ce629b69d8c238` | `b9ef1e2b6a24c61e52b1d4b7195796c2bf9282f6f1798f451b3c9a4cea5f68e7` |
| `regexp` | 1: Exception(vm_id=1): uninitialized constant ::Regexp (NameError) / Uncaught task exception (scheduler status 2) | `f0c4ff382492107de9431695926c25bc377897ea9fc5d11ca16de4b370a209a7` | `2028adcfac4a5ec0421fe24392fcd77f612362f4dc0bc8926d68f70a5e1558c4` |
| `time` | 1: Exception(vm_id=1): uninitialized constant Time (NameError) / Uncaught task exception (scheduler status 2) | `c3616b500524fd5b6b59907b65ce6408debaa321d479a4431498d3823f77bec6` | `936a04a89665428e986a0f68aa32cb21bf87c6a703652a02196310e092f8498f` |
| `io` | 1: Exception(vm_id=1): uninitialized constant IO (NameError) / Uncaught task exception (scheduler status 2) | `b2406b0f024b691be03a7a39a36a5897729e7565e8a0dfeb7e81dc5584983f86` | `848f24e162a31541074fa4e1b287e1502d38499cbebfcde2800d848099d02ef2` |
| `classvar` | 1: Exception(vm_id=1): Unimplemented opcode (0x1c) found (Exception) / 	in `Reading' / Uncaught task exception (scheduler status 2) | `99cc467672d55920b0500a669926c0fde342d4d2aa5a6effa5064f53e22018bb` | `512f1de1f927b115bb8dbc334fd360e0949c4408d04fa39b94b7d9e6244aeb29` |
| `undef` | 1: Exception(vm_id=1): Unimplemented opcode (0x6e) found (Exception) / 	in `Reading' / Uncaught task exception (scheduler status 2) | `273f126d13674824d2d03c1120767b638689f1c4606eee9467cd15a3c5e75385` | `4e75037099e13c96b20d641ee1a4b7635ea1125b0b4072ab1a3c582ff4335b64` |
| `outer-const` | 1: Exception(vm_id=1): Unimplemented opcode (0x20) found (Exception) / Uncaught task exception (scheduler status 2) | `db92541ffcf9f3031284ea7317207eebf633fb9ddb93b9956ae4db4261d87b00` | `f731bd430f9f136ba3d5663762c21f536204b06be9beac4e6b305cb931ac232f` |
| `int64-literal` | 2: Exception(vm_id=1): Unsupported int64 (set MRBC_INT64 in vm_config) (NotImplementedError) / Failed to load bytecode: int64-literal.mrb | `9eea545e124c0e2b2e590870636e17d25b77bb4db148c5b16c7ef3a5c45342ca` | `4bbe41942664c7fd11ba3189d53f27b8daa03417821c93df67c5c61111da889b` |
| `int32` | 0: -2147483648 | `ddd6685eca2cd4c98e8dac4d9a770c57e958540a596c8a8b2f90a802dca0758e` | `da748ed4458e47975539d8f63facdf767a5a4d1d099ba2844328226f45dd906e` |
| `strings` | 0: 出力なし | `7fa20b1d4885b4298df3bc6556186f96025577083790dca567bc1653b2a5c64f` | `f0a252ac0d1b968c985c7402faf448636aa939a94d614a56f06a35e1858ef872` |
| `sum-alternative` | 0: 出力なし | `847e08bd3d915c2b2c36176ea875e5fde844aba2a6318708944fca19463299b9` | `256d10226198cd5ca44ef3eb96084836ba9393941c8bf647c0590a3f31852866` |
| `bytes` | 0: 出力なし | `0fb02c83d447cf0c143ffe866850b3ff61e355f14bffd070c6356a10e0381317` | `c15985cee0c8aae313a7f901aa3a24a6143163685fb0dff4184f6756bc6fda11` |

## 解釈の境界

- pattern の成功は単純な array/hash と不一致例外の例に限定します。全 pattern syntax、escaping closure、全 keyword forwarding は未検証です。
- privacy の成功は、private method を外から呼べたという **CRuby との差異**です。認可の成功を意味しません。
- int32 は `x=2147483647; puts x+1` が今回の Wasm で -2147483648 を出した結果です。比較用に `-2147483648` literal を入力へ追加した初回試行は、compiler の int64 表現で load 拒否になりました。これを実行時 overflow の証拠にせず、上記の出力のみの入力へ分離しました。int64-literal は独立した load 失敗です。nRF toolchain の保証ではありません。
- standard-rescue は根 Exception を直接 raise して bare rescue の範囲を調べた入力です。未実装 opcode が同じ根 Exception を出すことは別行の失敗と [opcode 調査](../mrubyc/opcode-compatibility.md)で確認します。
- sleep-mutex は単一 task の正常系です。既存 check.sh の scheduler test は複数 task を含み、今回も成功しました。新 I/O の待機・IRQ・性能を検証したわけではありません。
- 既存の [能力 probe](../mrubyc/capability-probes.md)の入力・結果は上書きしていません。今回の新しい主張は本表と対応表の限定範囲へとどめます。

[対応表](idiom-compatibility.md) / [調査索引へ戻る](../README.md)
