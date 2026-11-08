#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../.." && pwd)
build="$root/tools/mrubyc-wasm/build"
for tool in git ruby make cc emcc node python3 timeout; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 2; }
done
mkdir -p "$build"
sha=$(git -C "$root/vendor/mruby" rev-parse HEAD)
host="$build/mruby-$sha"
if [[ ! -d "$host" ]]; then
  cp -R "$root/vendor/mruby" "$host"
fi
(cd "$host" && MRUBY_CONFIG=build_config/mrbc.rb ruby minirake)
mrbc="$host/build/host/bin/mrbc"

mkdir -p "$build/mrubyc"
for dir in src support mrblib hal; do
  cp -R "$root/vendor/mrubyc/$dir" "$build/mrubyc/"
done
make -C "$build/mrubyc/mrblib" MRBC="$mrbc" all
make -C "$build/mrubyc/src" autogen
mapfile -t sources < <(find "$build/mrubyc/src" -maxdepth 1 -name '*.c' | sort)
mapfile -t bindings < <(find "$root/src/rbos" -type f -name '*.c' | sort)
emcc -O1 -Wall -Wextra -Wno-unused-parameter \
  -include "$root/tools/mrubyc-wasm/runner_config.h" \
  -I"$root/include" \
  -I"$build/mrubyc/src" -I"$build/mrubyc/hal/emscripten" \
  -DMAX_VM_COUNT=32 -sASYNCIFY -sNODERAWFS=1 -sENVIRONMENT=node \
  -sEXIT_RUNTIME=1 -sALLOW_MEMORY_GROWTH=1 \
  -sASSERTIONS=1 -sSTACK_OVERFLOW_CHECK=1 -sCHECK_NULL_WRITES=1 \
  -sSTACK_SIZE=1048576 -sASYNCIFY_STACK_SIZE=65536 \
  "$root/tools/mrubyc-wasm/main.c" "${sources[@]}" \
  "${bindings[@]}" "$root/tools/mrubyc-wasm/backend.c" \
  "$build/mrubyc/hal/emscripten/hal.c" -o "$build/runner.js"

for source in "$root"/tests/mruby/*.rb; do
  "$mrbc" -o "$build/$(basename "${source%.rb}").mrb" "$source"
done
timeout 30s node "$build/runner.js" "$build/scheduler.mrb" \
  "$build/worker_a.mrb" "$build/worker_b.mrb" "$build/empty.mrb"
echo 'PASS: multiple tasks and empty Ruby program'

for fixture in idiom_collections idiom_objects idiom_values idiom_resources; do
  timeout 30s node "$build/runner.js" "$build/$fixture.mrb"
done

expect_failure() {
  local expected=$1 marker=$2 status=0
  shift 2
  timeout 30s node "$build/runner.js" "$@" > "$build/expected-failure.log" 2>&1 || status=$?
  if [[ "$status" != "$expected" ]] || ! grep -Fq "$marker" "$build/expected-failure.log"; then
    cat "$build/expected-failure.log"
    echo "Unexpected failure result: $status (expected $expected / $marker)" >&2
    exit 1
  fi
  cat "$build/expected-failure.log"
  echo "PASS: expected failure detected (exit $status / $marker)"
}
expect_failure 1 'expected smoke failure' "$build/expected_failure.mrb" "$build/empty.mrb"
expect_failure 1 'Unimplemented opcode (0x61) found (Exception)' "$build/idiom_avoid_lambda.mrb"
expect_failure 1 'no block given (yield)' "$build/idiom_avoid_symbol_proc.mrb"
expect_failure 2 'Unsupported int64 (set MRBC_INT64 in vm_config)' "$build/idiom_avoid_int64.mrb"
expect_failure 2 'Usage:'
expect_failure 2 'Cannot open bytecode:' "$build/missing.mrb"
expect_failure 2 'Invalid bytecode size:' "$root/tests/mruby/empty.rb"
python3 - "$build/empty.mrb" "$build/wrong-version.mrb" <<'PY'
from pathlib import Path
import sys
data = bytearray(Path(sys.argv[1]).read_bytes())
data[4:8] = b'0000'
Path(sys.argv[2]).write_bytes(data)
data[:4] = b'NOPE'
Path(sys.argv[2]).with_name('wrong-magic.mrb').write_bytes(data)
data[:8] = b'RITE0400'
data[8:12] = (len(data) + 1).to_bytes(4, 'big')
Path(sys.argv[2]).with_name('wrong-size.mrb').write_bytes(data)
PY
expect_failure 2 'Failed to load bytecode:' "$build/wrong-version.mrb"
expect_failure 2 'Invalid bytecode header:' "$build/wrong-magic.mrb"
expect_failure 2 'Invalid declared bytecode size:' "$build/wrong-size.mrb"

count=0
if [[ -d "$root/src" ]]; then
  while IFS= read -r -d '' source; do
    "$mrbc" -o "$build/src-$count.mrb" "$source"
    count=$((count + 1))
  done < <(find "$root/src" -type f -name '*.rb' -print0)
fi
echo "PASS: compiled $count src Ruby files (zero is allowed)"
