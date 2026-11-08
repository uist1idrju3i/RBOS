# opcode と mruby 4.0.0 の対応

数値・operand は mruby/c の enum、mruby 側は ops.h の列挙順で照合しました。「handler あり」は全ての引数・edge case・構成での互換性保証ではありません。未実装 handler は Exception を設定します。EXT は既定では例外です。

| code / opcode | operand・意味 | mruby 4.0.0 | mruby/c dispatch | 根拠 |
|---|---|---|---|---|
| 0x00 `NOP` | Z: no operation | 同数値 `vendor/mruby/include/mruby/ops.h:15-15` | op_nop | `vendor/mrubyc/src/opcode.h:124-124` / `vendor/mrubyc/src/vm.c:3174-3174` |
| 0x01 `MOVE` | BB: R[a] = R[b] | 同数値 `vendor/mruby/include/mruby/ops.h:16-16` | op_move | `vendor/mrubyc/src/opcode.h:125-125` / `vendor/mrubyc/src/vm.c:3175-3175` |
| 0x02 `LOADL` | BB: R[a] = Pool[b] | 同数値 `vendor/mruby/include/mruby/ops.h:17-17` | op_loadl | `vendor/mrubyc/src/opcode.h:126-126` / `vendor/mrubyc/src/vm.c:3176-3176` |
| 0x03 `LOADI8` | BB: R[a] = mrb_int(b) | 同数値 `vendor/mruby/include/mruby/ops.h:18-18` | op_loadi8 | `vendor/mrubyc/src/opcode.h:127-127` / `vendor/mrubyc/src/vm.c:3177-3177` |
| 0x04 `LOADINEG` | BB: R[a] = mrb_int(-b) | 同数値 `vendor/mruby/include/mruby/ops.h:19-19` | op_loadineg | `vendor/mrubyc/src/opcode.h:128-128` / `vendor/mrubyc/src/vm.c:3178-3178` |
| 0x05 `LOADI__1` | B: R[a] = mrb_int(-1) | 同数値 `vendor/mruby/include/mruby/ops.h:20-20` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:129-129` / `vendor/mrubyc/src/vm.c:3179-3179` |
| 0x06 `LOADI_0` | B: R[a] = mrb_int(0) | 同数値 `vendor/mruby/include/mruby/ops.h:21-21` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:130-130` / `vendor/mrubyc/src/vm.c:3180-3180` |
| 0x07 `LOADI_1` | B: R[a] = mrb_int(1) | 同数値 `vendor/mruby/include/mruby/ops.h:22-22` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:131-131` / `vendor/mrubyc/src/vm.c:3181-3181` |
| 0x08 `LOADI_2` | B: R[a] = mrb_int(2) | 同数値 `vendor/mruby/include/mruby/ops.h:23-23` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:132-132` / `vendor/mrubyc/src/vm.c:3182-3182` |
| 0x09 `LOADI_3` | B: R[a] = mrb_int(3) | 同数値 `vendor/mruby/include/mruby/ops.h:24-24` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:133-133` / `vendor/mrubyc/src/vm.c:3183-3183` |
| 0x0A `LOADI_4` | B: R[a] = mrb_int(4) | 同数値 `vendor/mruby/include/mruby/ops.h:25-25` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:134-134` / `vendor/mrubyc/src/vm.c:3184-3184` |
| 0x0B `LOADI_5` | B: R[a] = mrb_int(5) | 同数値 `vendor/mruby/include/mruby/ops.h:26-26` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:135-135` / `vendor/mrubyc/src/vm.c:3185-3185` |
| 0x0C `LOADI_6` | B: R[a] = mrb_int(6) | 同数値 `vendor/mruby/include/mruby/ops.h:27-27` | op_loadi_n（共有） | `vendor/mrubyc/src/opcode.h:136-136` / `vendor/mrubyc/src/vm.c:3186-3186` |
| 0x0D `LOADI_7` | B: R[a] = mrb_int(7) | 同数値 `vendor/mruby/include/mruby/ops.h:28-28` | op_loadi_n | `vendor/mrubyc/src/opcode.h:137-137` / `vendor/mrubyc/src/vm.c:3187-3187` |
| 0x0E `LOADI16` | BS: R[a] = mrb_int(b) | 同数値 `vendor/mruby/include/mruby/ops.h:29-29` | op_loadi16 | `vendor/mrubyc/src/opcode.h:138-138` / `vendor/mrubyc/src/vm.c:3188-3188` |
| 0x0F `LOADI32` | BSS: R[a] = mrb_int((b<<16)+c) | 同数値 `vendor/mruby/include/mruby/ops.h:30-30` | op_loadi32 | `vendor/mrubyc/src/opcode.h:139-139` / `vendor/mrubyc/src/vm.c:3189-3189` |
| 0x10 `LOADSYM` | BB: R[a] = Syms[b] | 同数値 `vendor/mruby/include/mruby/ops.h:31-31` | op_loadsym | `vendor/mrubyc/src/opcode.h:140-140` / `vendor/mrubyc/src/vm.c:3190-3190` |
| 0x11 `LOADNIL` | B: R[a] = nil | 同数値 `vendor/mruby/include/mruby/ops.h:32-32` | op_loadnil | `vendor/mrubyc/src/opcode.h:141-141` / `vendor/mrubyc/src/vm.c:3191-3191` |
| 0x12 `LOADSELF` | B: R[a] = self | 同数値 `vendor/mruby/include/mruby/ops.h:33-33` | op_loadself | `vendor/mrubyc/src/opcode.h:142-142` / `vendor/mrubyc/src/vm.c:3192-3192` |
| 0x13 `LOADTRUE` | B: R[a] = true | 同数値 `vendor/mruby/include/mruby/ops.h:34-34` | op_loadtrue | `vendor/mrubyc/src/opcode.h:143-143` / `vendor/mrubyc/src/vm.c:3193-3193` |
| 0x14 `LOADFALSE` | B: R[a] = false | 同数値 `vendor/mruby/include/mruby/ops.h:35-35` | op_loadfalse | `vendor/mrubyc/src/opcode.h:144-144` / `vendor/mrubyc/src/vm.c:3194-3194` |
| 0x15 `GETGV` | BB: R[a] = getglobal(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:36-36` | op_getgv | `vendor/mrubyc/src/opcode.h:145-145` / `vendor/mrubyc/src/vm.c:3195-3195` |
| 0x16 `SETGV` | BB: setglobal(Syms[b], R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:37-37` | op_setgv | `vendor/mrubyc/src/opcode.h:146-146` / `vendor/mrubyc/src/vm.c:3196-3196` |
| 0x17 `GETSV` | BB: R[a] = Special[Syms[b]] | 同数値 `vendor/mruby/include/mruby/ops.h:38-38` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:147-147` / `vendor/mrubyc/src/vm.c:3197-3197` |
| 0x18 `SETSV` | BB: Special[Syms[b]] = R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:39-39` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:148-148` / `vendor/mrubyc/src/vm.c:3198-3198` |
| 0x19 `GETIV` | BB: R[a] = ivget(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:40-40` | op_getiv | `vendor/mrubyc/src/opcode.h:149-149` / `vendor/mrubyc/src/vm.c:3199-3199` |
| 0x1A `SETIV` | BB: ivset(Syms[b],R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:41-41` | op_setiv | `vendor/mrubyc/src/opcode.h:150-150` / `vendor/mrubyc/src/vm.c:3200-3200` |
| 0x1B `GETCV` | BB: R[a] = cvget(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:42-42` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:151-151` / `vendor/mrubyc/src/vm.c:3201-3201` |
| 0x1C `SETCV` | BB: cvset(Syms[b],R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:43-43` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:152-152` / `vendor/mrubyc/src/vm.c:3202-3202` |
| 0x1D `GETCONST` | BB: R[a] = constget(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:44-44` | op_getconst | `vendor/mrubyc/src/opcode.h:153-153` / `vendor/mrubyc/src/vm.c:3203-3203` |
| 0x1E `SETCONST` | BB: constset(Syms[b],R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:45-45` | op_setconst | `vendor/mrubyc/src/opcode.h:154-154` / `vendor/mrubyc/src/vm.c:3204-3204` |
| 0x1F `GETMCNST` | BB: R[a] = R[a]::Syms[b] | 同数値 `vendor/mruby/include/mruby/ops.h:46-46` | op_getmcnst | `vendor/mrubyc/src/opcode.h:155-155` / `vendor/mrubyc/src/vm.c:3205-3205` |
| 0x20 `SETMCNST` | BB: R[a+1]::Syms[b] = R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:47-47` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:156-156` / `vendor/mrubyc/src/vm.c:3206-3206` |
| 0x21 `GETUPVAR` | BBB: R[a] = uvget(b,c) | 同数値 `vendor/mruby/include/mruby/ops.h:48-48` | op_getupvar | `vendor/mrubyc/src/opcode.h:157-157` / `vendor/mrubyc/src/vm.c:3207-3207` |
| 0x22 `SETUPVAR` | BBB: uvset(b,c,R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:49-49` | op_setupvar | `vendor/mrubyc/src/opcode.h:158-158` / `vendor/mrubyc/src/vm.c:3208-3208` |
| 0x23 `GETIDX` | B: R[a] = R[a][R[a+1]] | 同数値 `vendor/mruby/include/mruby/ops.h:50-50` | op_getidx | `vendor/mrubyc/src/opcode.h:159-159` / `vendor/mrubyc/src/vm.c:3209-3209` |
| 0x24 `GETIDX0` | BB: R[a] = R[b][0]; a+1 for method call | 同数値 `vendor/mruby/include/mruby/ops.h:51-51` | op_getidx0 | `vendor/mrubyc/src/opcode.h:160-160` / `vendor/mrubyc/src/vm.c:3210-3210` |
| 0x25 `SETIDX` | B: R[a][R[a+1]] = R[a+2] | 同数値 `vendor/mruby/include/mruby/ops.h:52-52` | op_setidx | `vendor/mrubyc/src/opcode.h:161-161` / `vendor/mrubyc/src/vm.c:3211-3211` |
| 0x26 `JMP` | S: pc+=a | 同数値 `vendor/mruby/include/mruby/ops.h:53-53` | op_jmp | `vendor/mrubyc/src/opcode.h:162-162` / `vendor/mrubyc/src/vm.c:3212-3212` |
| 0x27 `JMPIF` | BS: if R[a] pc+=b | 同数値 `vendor/mruby/include/mruby/ops.h:54-54` | op_jmpif | `vendor/mrubyc/src/opcode.h:163-163` / `vendor/mrubyc/src/vm.c:3213-3213` |
| 0x28 `JMPNOT` | BS: if !R[a] pc+=b | 同数値 `vendor/mruby/include/mruby/ops.h:55-55` | op_jmpnot | `vendor/mrubyc/src/opcode.h:164-164` / `vendor/mrubyc/src/vm.c:3214-3214` |
| 0x29 `JMPNIL` | BS: if R[a]==nil pc+=b | 同数値 `vendor/mruby/include/mruby/ops.h:56-56` | op_jmpnil | `vendor/mrubyc/src/opcode.h:165-165` / `vendor/mrubyc/src/vm.c:3215-3215` |
| 0x2A `JMPUW` | S: unwind_and_jump_to(a) | 同数値 `vendor/mruby/include/mruby/ops.h:57-57` | op_jmpuw | `vendor/mrubyc/src/opcode.h:166-166` / `vendor/mrubyc/src/vm.c:3216-3216` |
| 0x2B `EXCEPT` | B: R[a] = exc | 同数値 `vendor/mruby/include/mruby/ops.h:58-58` | op_except | `vendor/mrubyc/src/opcode.h:167-167` / `vendor/mrubyc/src/vm.c:3217-3217` |
| 0x2C `RESCUE` | BB: R[b] = R[a].isa?(R[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:59-59` | op_rescue | `vendor/mrubyc/src/opcode.h:168-168` / `vendor/mrubyc/src/vm.c:3218-3218` |
| 0x2D `RAISEIF` | B: raise(R[a]) if R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:60-60` | op_raiseif | `vendor/mrubyc/src/opcode.h:169-169` / `vendor/mrubyc/src/vm.c:3219-3219` |
| 0x2E `MATCHERR` | B: raise NoMatchingPatternError unless R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:61-61` | op_matcherr | `vendor/mrubyc/src/opcode.h:170-170` / `vendor/mrubyc/src/vm.c:3220-3220` |
| 0x2F `SSEND` | BBB: R[a] = self.send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..) (c=n&#124;k<<4) | 同数値 `vendor/mruby/include/mruby/ops.h:62-62` | op_ssend | `vendor/mrubyc/src/opcode.h:171-171` / `vendor/mrubyc/src/vm.c:3221-3221` |
| 0x30 `SSEND0` | BB: R[a] = self.send(Syms[b]) (no args) | 同数値 `vendor/mruby/include/mruby/ops.h:63-63` | op_ssend0 | `vendor/mrubyc/src/opcode.h:172-172` / `vendor/mrubyc/src/vm.c:3222-3222` |
| 0x31 `SSENDB` | BBB: R[a] = self.send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..,&R[a+n+2k+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:64-64` | op_ssendb | `vendor/mrubyc/src/opcode.h:173-173` / `vendor/mrubyc/src/vm.c:3223-3223` |
| 0x32 `SEND` | BBB: R[a] = R[a].send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..) (c=n&#124;k<<4) | 同数値 `vendor/mruby/include/mruby/ops.h:65-65` | op_send | `vendor/mrubyc/src/opcode.h:174-174` / `vendor/mrubyc/src/vm.c:3224-3224` |
| 0x33 `SEND0` | BB: R[a] = R[a].send(Syms[b]) (no args) | 同数値 `vendor/mruby/include/mruby/ops.h:66-66` | op_send0 | `vendor/mrubyc/src/opcode.h:175-175` / `vendor/mrubyc/src/vm.c:3225-3225` |
| 0x34 `SENDB` | BBB: R[a] = R[a].send(Syms[b],R[a+1]..,R[a+n+1]:R[a+n+2]..,&R[a+n+2k+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:67-67` | op_sendb | `vendor/mrubyc/src/opcode.h:176-176` / `vendor/mrubyc/src/vm.c:3226-3226` |
| 0x35 `CALL` | Z: self.call(*, **, &) (But overlay the current call frame; tailcall) | 同数値 `vendor/mruby/include/mruby/ops.h:68-68` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:177-177` / `vendor/mrubyc/src/vm.c:3227-3227` |
| 0x36 `BLKCALL` | BB: R[a] = R[a].call(R[a+1],... ,R[a+b]); direct block call | 同数値 `vendor/mruby/include/mruby/ops.h:69-69` | op_blkcall | `vendor/mrubyc/src/opcode.h:178-178` / `vendor/mrubyc/src/vm.c:3228-3228` |
| 0x37 `SUPER` | BB: R[a] = super(R[a+1],... ,R[a+b+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:70-70` | op_super | `vendor/mrubyc/src/opcode.h:179-179` / `vendor/mrubyc/src/vm.c:3229-3229` |
| 0x38 `ARGARY` | BS: R[a] = argument array (16=m5:r1:m5:d1:lv4) | 同数値 `vendor/mruby/include/mruby/ops.h:71-71` | op_argary | `vendor/mrubyc/src/opcode.h:180-180` / `vendor/mrubyc/src/vm.c:3230-3230` |
| 0x39 `ENTER` | W: arg setup according to flags (24=n1:m5:o5:r1:m5:k5:d1:b1) | 同数値 `vendor/mruby/include/mruby/ops.h:72-72` | op_enter | `vendor/mrubyc/src/opcode.h:181-181` / `vendor/mrubyc/src/vm.c:3231-3231` |
| 0x3A `KEY_P` | BB: R[a] = kdict.key?(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:73-73` | op_key_p | `vendor/mrubyc/src/opcode.h:182-182` / `vendor/mrubyc/src/vm.c:3232-3232` |
| 0x3B `KEYEND` | Z: raise unless kdict.empty? | 同数値 `vendor/mruby/include/mruby/ops.h:74-74` | op_keyend | `vendor/mrubyc/src/opcode.h:183-183` / `vendor/mrubyc/src/vm.c:3233-3233` |
| 0x3C `KARG` | BB: R[a] = kdict[Syms[b]]; kdict.delete(Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:75-75` | op_karg | `vendor/mrubyc/src/opcode.h:184-184` / `vendor/mrubyc/src/vm.c:3234-3234` |
| 0x3D `RETURN` | B: return R[a] (normal) | 同数値 `vendor/mruby/include/mruby/ops.h:76-76` | op_return | `vendor/mrubyc/src/opcode.h:185-185` / `vendor/mrubyc/src/vm.c:3235-3235` |
| 0x3E `RETURN_BLK` | B: return R[a] (in-block return) | 同数値 `vendor/mruby/include/mruby/ops.h:77-77` | op_return_blk | `vendor/mrubyc/src/opcode.h:186-186` / `vendor/mrubyc/src/vm.c:3236-3236` |
| 0x3F `RETSELF` | Z: return self | 同数値 `vendor/mruby/include/mruby/ops.h:78-78` | op_retself | `vendor/mrubyc/src/opcode.h:187-187` / `vendor/mrubyc/src/vm.c:3237-3237` |
| 0x40 `RETNIL` | Z: return nil | 同数値 `vendor/mruby/include/mruby/ops.h:79-79` | op_retnil | `vendor/mrubyc/src/opcode.h:188-188` / `vendor/mrubyc/src/vm.c:3238-3238` |
| 0x41 `RETTRUE` | Z: return true | 同数値 `vendor/mruby/include/mruby/ops.h:80-80` | op_rettrue | `vendor/mrubyc/src/opcode.h:189-189` / `vendor/mrubyc/src/vm.c:3239-3239` |
| 0x42 `RETFALSE` | Z: return false | 同数値 `vendor/mruby/include/mruby/ops.h:81-81` | op_retfalse | `vendor/mrubyc/src/opcode.h:190-190` / `vendor/mrubyc/src/vm.c:3240-3240` |
| 0x43 `BREAK` | B: break R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:82-82` | op_break | `vendor/mrubyc/src/opcode.h:191-191` / `vendor/mrubyc/src/vm.c:3241-3241` |
| 0x44 `BLKPUSH` | BS: R[a] = block (16=m5:r1:m5:d1:lv4) | 同数値 `vendor/mruby/include/mruby/ops.h:83-83` | op_blkpush | `vendor/mrubyc/src/opcode.h:192-192` / `vendor/mrubyc/src/vm.c:3242-3242` |
| 0x45 `ADD` | B: R[a] = R[a]+R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:84-84` | op_add | `vendor/mrubyc/src/opcode.h:193-193` / `vendor/mrubyc/src/vm.c:3243-3243` |
| 0x46 `ADDI` | BB: R[a] = R[a]+mrb_int(b) | 同数値 `vendor/mruby/include/mruby/ops.h:85-85` | op_addi | `vendor/mrubyc/src/opcode.h:194-194` / `vendor/mrubyc/src/vm.c:3244-3244` |
| 0x47 `SUB` | B: R[a] = R[a]-R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:86-86` | op_sub | `vendor/mrubyc/src/opcode.h:195-195` / `vendor/mrubyc/src/vm.c:3245-3245` |
| 0x48 `SUBI` | BB: R[a] = R[a]-mrb_int(b) | 同数値 `vendor/mruby/include/mruby/ops.h:87-87` | op_subi | `vendor/mrubyc/src/opcode.h:196-196` / `vendor/mrubyc/src/vm.c:3246-3246` |
| 0x49 `ADDILV` | BBB: R[a] = R[a]+mrb_int(c); R[b],R[b+1] for method call | 同数値 `vendor/mruby/include/mruby/ops.h:88-88` | op_addilv | `vendor/mrubyc/src/opcode.h:197-197` / `vendor/mrubyc/src/vm.c:3247-3247` |
| 0x4A `SUBILV` | BBB: R[a] = R[a]-mrb_int(c); R[b],R[b+1] for method call | 同数値 `vendor/mruby/include/mruby/ops.h:89-89` | op_subilv | `vendor/mrubyc/src/opcode.h:198-198` / `vendor/mrubyc/src/vm.c:3248-3248` |
| 0x4B `MUL` | B: R[a] = R[a]*R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:90-90` | op_mul | `vendor/mrubyc/src/opcode.h:199-199` / `vendor/mrubyc/src/vm.c:3249-3249` |
| 0x4C `DIV` | B: R[a] = R[a]/R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:91-91` | op_div | `vendor/mrubyc/src/opcode.h:200-200` / `vendor/mrubyc/src/vm.c:3250-3250` |
| 0x4D `EQ` | B: R[a] = R[a]==R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:92-92` | op_eq | `vendor/mrubyc/src/opcode.h:201-201` / `vendor/mrubyc/src/vm.c:3251-3251` |
| 0x4E `LT` | B: R[a] = R[a]<R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:93-93` | op_lt | `vendor/mrubyc/src/opcode.h:202-202` / `vendor/mrubyc/src/vm.c:3252-3252` |
| 0x4F `LE` | B: R[a] = R[a]<=R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:94-94` | op_le | `vendor/mrubyc/src/opcode.h:203-203` / `vendor/mrubyc/src/vm.c:3253-3253` |
| 0x50 `GT` | B: R[a] = R[a]>R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:95-95` | op_gt | `vendor/mrubyc/src/opcode.h:204-204` / `vendor/mrubyc/src/vm.c:3254-3254` |
| 0x51 `GE` | B: R[a] = R[a]>=R[a+1] | 同数値 `vendor/mruby/include/mruby/ops.h:96-96` | op_ge | `vendor/mrubyc/src/opcode.h:205-205` / `vendor/mrubyc/src/vm.c:3255-3255` |
| 0x52 `ARRAY` | BB: R[a] = ary_new(R[a],R[a+1]..R[a+b]) | 同数値 `vendor/mruby/include/mruby/ops.h:97-97` | op_array | `vendor/mrubyc/src/opcode.h:206-206` / `vendor/mrubyc/src/vm.c:3256-3256` |
| 0x53 `ARRAY2` | BBB: R[a] = ary_new(R[b],R[b+1]..R[b+c]) | 同数値 `vendor/mruby/include/mruby/ops.h:98-98` | op_array2 | `vendor/mrubyc/src/opcode.h:207-207` / `vendor/mrubyc/src/vm.c:3257-3257` |
| 0x54 `ARYCAT` | B: ary_cat(R[a],R[a+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:99-99` | op_arycat | `vendor/mrubyc/src/opcode.h:208-208` / `vendor/mrubyc/src/vm.c:3258-3258` |
| 0x55 `ARYPUSH` | BB: ary_push(R[a],R[a+1]..R[a+b]) | 同数値 `vendor/mruby/include/mruby/ops.h:100-100` | op_arypush | `vendor/mrubyc/src/opcode.h:209-209` / `vendor/mrubyc/src/vm.c:3259-3259` |
| 0x56 `ARYSPLAT` | B: R[a] = ary_splat(R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:101-101` | op_arysplat | `vendor/mrubyc/src/opcode.h:210-210` / `vendor/mrubyc/src/vm.c:3260-3260` |
| 0x57 `AREF` | BBB: R[a] = R[b][c] | 同数値 `vendor/mruby/include/mruby/ops.h:102-102` | op_aref | `vendor/mrubyc/src/opcode.h:211-211` / `vendor/mrubyc/src/vm.c:3261-3261` |
| 0x58 `ASET` | BBB: R[b][c] = R[a] | 同数値 `vendor/mruby/include/mruby/ops.h:103-103` | op_aset | `vendor/mrubyc/src/opcode.h:212-212` / `vendor/mrubyc/src/vm.c:3262-3262` |
| 0x59 `APOST` | BBB: *R[a],R[a+1]..R[a+c] = R[a][b..] | 同数値 `vendor/mruby/include/mruby/ops.h:104-104` | op_apost | `vendor/mrubyc/src/opcode.h:213-213` / `vendor/mrubyc/src/vm.c:3263-3263` |
| 0x5A `INTERN` | B: R[a] = intern(R[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:105-105` | op_intern | `vendor/mrubyc/src/opcode.h:214-214` / `vendor/mrubyc/src/vm.c:3264-3264` |
| 0x5B `SYMBOL` | BB: R[a] = intern(Pool[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:106-106` | op_symbol | `vendor/mrubyc/src/opcode.h:215-215` / `vendor/mrubyc/src/vm.c:3265-3265` |
| 0x5C `STRING` | BB: R[a] = str_dup(Pool[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:107-107` | op_string | `vendor/mrubyc/src/opcode.h:216-216` / `vendor/mrubyc/src/vm.c:3266-3266` |
| 0x5D `STRCAT` | B: str_cat(R[a],R[a+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:108-108` | op_strcat | `vendor/mrubyc/src/opcode.h:217-217` / `vendor/mrubyc/src/vm.c:3267-3267` |
| 0x5E `HASH` | BB: R[a] = hash_new(R[a],R[a+1]..R[a+b*2-1]) | 同数値 `vendor/mruby/include/mruby/ops.h:109-109` | op_hash | `vendor/mrubyc/src/opcode.h:218-218` / `vendor/mrubyc/src/vm.c:3268-3268` |
| 0x5F `HASHADD` | BB: hash_push(R[a],R[a+1]..R[a+b*2]) | 同数値 `vendor/mruby/include/mruby/ops.h:110-110` | op_hashadd | `vendor/mrubyc/src/opcode.h:219-219` / `vendor/mrubyc/src/vm.c:3269-3269` |
| 0x60 `HASHCAT` | B: R[a] = hash_cat(R[a],R[a+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:111-111` | op_hashcat | `vendor/mrubyc/src/opcode.h:220-220` / `vendor/mrubyc/src/vm.c:3270-3270` |
| 0x61 `LAMBDA` | BB: R[a] = lambda(Irep[b],L_LAMBDA) | 同数値 `vendor/mruby/include/mruby/ops.h:112-112` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:221-221` / `vendor/mrubyc/src/vm.c:3271-3271` |
| 0x62 `BLOCK` | BB: R[a] = lambda(Irep[b],L_BLOCK) | 同数値 `vendor/mruby/include/mruby/ops.h:113-113` | op_block | `vendor/mrubyc/src/opcode.h:222-222` / `vendor/mrubyc/src/vm.c:3272-3272` |
| 0x63 `METHOD` | BB: R[a] = lambda(Irep[b],L_METHOD) | 同数値 `vendor/mruby/include/mruby/ops.h:114-114` | op_method | `vendor/mrubyc/src/opcode.h:223-223` / `vendor/mrubyc/src/vm.c:3273-3273` |
| 0x64 `RANGE_INC` | B: R[a] = range_new(R[a],R[a+1],FALSE) | 同数値 `vendor/mruby/include/mruby/ops.h:115-115` | op_range_inc | `vendor/mrubyc/src/opcode.h:224-224` / `vendor/mrubyc/src/vm.c:3274-3274` |
| 0x65 `RANGE_EXC` | B: R[a] = range_new(R[a],R[a+1],TRUE) | 同数値 `vendor/mruby/include/mruby/ops.h:116-116` | op_range_exc | `vendor/mrubyc/src/opcode.h:225-225` / `vendor/mrubyc/src/vm.c:3275-3275` |
| 0x66 `OCLASS` | B: R[a] = ::Object | 同数値 `vendor/mruby/include/mruby/ops.h:117-117` | op_oclass | `vendor/mrubyc/src/opcode.h:226-226` / `vendor/mrubyc/src/vm.c:3276-3276` |
| 0x67 `CLASS` | BB: R[a] = newclass(R[a],Syms[b],R[a+1]) | 同数値 `vendor/mruby/include/mruby/ops.h:118-118` | op_class | `vendor/mrubyc/src/opcode.h:227-227` / `vendor/mrubyc/src/vm.c:3277-3277` |
| 0x68 `MODULE` | BB: R[a] = newmodule(R[a],Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:119-119` | op_module | `vendor/mrubyc/src/opcode.h:228-228` / `vendor/mrubyc/src/vm.c:3278-3278` |
| 0x69 `EXEC` | BB: R[a] = blockexec(R[a],Irep[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:120-120` | op_exec | `vendor/mrubyc/src/opcode.h:229-229` / `vendor/mrubyc/src/vm.c:3279-3279` |
| 0x6A `DEF` | BB: R[a].newmethod(Syms[b],R[a+1]); R[a] = Syms[b] | 同数値 `vendor/mruby/include/mruby/ops.h:121-121` | op_def | `vendor/mrubyc/src/opcode.h:230-230` / `vendor/mrubyc/src/vm.c:3280-3280` |
| 0x6B `TDEF` | BBB: target_class.newmethod(Syms[b],Irep[c]); R[a] = Syms[b] | 同数値 `vendor/mruby/include/mruby/ops.h:122-122` | op_tdef | `vendor/mrubyc/src/opcode.h:231-231` / `vendor/mrubyc/src/vm.c:3281-3281` |
| 0x6C `SDEF` | BBB: R[a].singleton_class.newmethod(Syms[b],Irep[c]); R[a] = Syms[b] | 同数値 `vendor/mruby/include/mruby/ops.h:123-123` | op_sdef | `vendor/mrubyc/src/opcode.h:232-232` / `vendor/mrubyc/src/vm.c:3282-3282` |
| 0x6D `ALIAS` | BB: alias_method(target_class,Syms[a],Syms[b]) | 同数値 `vendor/mruby/include/mruby/ops.h:124-124` | op_alias | `vendor/mrubyc/src/opcode.h:233-233` / `vendor/mrubyc/src/vm.c:3283-3283` |
| 0x6E `UNDEF` | B: undef_method(target_class,Syms[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:125-125` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:234-234` / `vendor/mrubyc/src/vm.c:3284-3284` |
| 0x6F `SCLASS` | B: R[a] = R[a].singleton_class | 同数値 `vendor/mruby/include/mruby/ops.h:126-126` | op_sclass | `vendor/mrubyc/src/opcode.h:235-235` / `vendor/mrubyc/src/vm.c:3285-3285` |
| 0x70 `TCLASS` | B: R[a] = target_class | 同数値 `vendor/mruby/include/mruby/ops.h:127-127` | op_tclass | `vendor/mrubyc/src/opcode.h:236-236` / `vendor/mrubyc/src/vm.c:3286-3286` |
| 0x71 `DEBUG` | BBB: print a,b,c | 同数値 `vendor/mruby/include/mruby/ops.h:128-128` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:237-237` / `vendor/mrubyc/src/vm.c:3287-3287` |
| 0x72 `ERR` | B: raise(LocalJumpError, Pool[a]) | 同数値 `vendor/mruby/include/mruby/ops.h:129-129` | 未実装→Exception | `vendor/mrubyc/src/opcode.h:238-238` / `vendor/mrubyc/src/vm.c:3288-3288` |
| 0x73 `EXT1` | Z: make 1st operand (a) 16bit | 同数値 `vendor/mruby/include/mruby/ops.h:130-130` | MRBC_SUPPORT_OP_EXT 条件付き | `vendor/mrubyc/src/opcode.h:239-239` / `vendor/mrubyc/src/vm.c:3291-3291` |
| 0x74 `EXT2` | Z: make 2nd operand (b) 16bit | 同数値 `vendor/mruby/include/mruby/ops.h:131-131` | MRBC_SUPPORT_OP_EXT 条件付き | `vendor/mrubyc/src/opcode.h:240-240` / `vendor/mrubyc/src/vm.c:3292-3292` |
| 0x75 `EXT3` | Z: make 1st and 2nd operands 16bit | 同数値 `vendor/mruby/include/mruby/ops.h:132-132` | MRBC_SUPPORT_OP_EXT 条件付き | `vendor/mrubyc/src/opcode.h:241-241` / `vendor/mrubyc/src/vm.c:3293-3293` |
| 0x76 `STOP` | Z: stop VM | 同数値 `vendor/mruby/include/mruby/ops.h:133-133` | op_stop | `vendor/mrubyc/src/opcode.h:242-242` / `vendor/mrubyc/src/vm.c:3299-3299` |

mruby/c は 119 命令、mruby は 119 命令です。mruby のみ: 。

[Ruby-first の制約](ruby-first-capabilities.md) / [調査索引へ戻る](../README.md)
