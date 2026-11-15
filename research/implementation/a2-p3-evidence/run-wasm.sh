#!/usr/bin/env bash
set -euo pipefail
root=$(git rev-parse --show-toplevel)
src="$root/research/implementation/a2-p3-evidence"
build="$root/tools/mrubyc-wasm/build"
sha=$(git -C "$root/vendor/mruby" rev-parse HEAD)
mrbc="$build/mruby-$sha/build/host/bin/mrbc"
out="$root/.git/a2-p3-replay"
mkdir -p "$out"
for fixture in system spin sleep block error empty; do
  "$mrbc" -B"c_${fixture}_code" -o "$out/c_${fixture}_code.c" "$src/c_${fixture}.rb"
done
for fixture in cases child raise victim; do
  "$mrbc" -B"sudo_${fixture}_code" -o "$out/sudo_${fixture}_code.c" "$src/sudo_${fixture}.rb"
done
emcc -O1 -Wall -Wextra -Wno-unused-parameter -finstrument-functions \
  -include "$src/c_system_config.h" -I"$src" -I"$out" -I"$build/mrubyc/src" \
  -DMAX_VM_COUNT=32 -sSINGLE_FILE=1 -sENVIRONMENT=node -sEXIT_RUNTIME=1 \
  -sASSERTIONS=1 -sSTACK_OVERFLOW_CHECK=1 -sSTACK_SIZE=1048576 \
  -Wl,--wrap=mrbc_vm_run "$src/c_system_probe.c" "$build"/mrubyc/src/*.c \
  -o "$out/c-system.js" > "$out/c-system-build.log" 2>&1
for mode in normal empty error sleep spin idle-only block; do
  timeout 15s node "$out/c-system.js" "$mode"
done
emcc -O1 -Wall -Wextra -Wno-unused-parameter -DSUDO_TIMER_STYLE \
  -include "$src/sudo_config.h" -I"$src" -I"$out" -I"$build/mrubyc/src" \
  -DMAX_VM_COUNT=32 -sSINGLE_FILE=1 -sENVIRONMENT=node -sEXIT_RUNTIME=1 \
  -sASSERTIONS=1 -sSTACK_OVERFLOW_CHECK=1 -sSTACK_SIZE=1048576 \
  "$src/sudo_probe.c" "$build"/mrubyc/src/*.c \
  -o "$out/sudo.js" > "$out/sudo-build.log" 2>&1
timeout 20s node "$out/sudo.js"
for fixture in priority trusted untrusted; do
  "$mrbc" -B"${fixture}_code" -o "$out/${fixture}_code.c" "$src/${fixture}.rb"
done
emcc -O1 -Wall -Wextra -Wno-unused-parameter \
  -I"$src" -I"$build/mrubyc/src" -DMAX_VM_COUNT=32 \
  -sSINGLE_FILE=1 -sENVIRONMENT=node -sEXIT_RUNTIME=1 \
  -sASSERTIONS=1 -sSTACK_OVERFLOW_CHECK=1 -sSTACK_SIZE=1048576 \
  "$src/task_registry_probe.c" "$build"/mrubyc/src/*.c \
  "$out/priority_code.c" "$out/trusted_code.c" "$out/untrusted_code.c" \
  -o "$out/task-wrapper.js" > "$out/task-wrapper-build.log" 2>&1
timeout 20s node "$out/task-wrapper.js"
