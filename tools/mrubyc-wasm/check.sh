#!/usr/bin/env bash
set -euo pipefail

mode=${1:-}
if [[ $# -gt 1 || ( -n "$mode" && "$mode" != --pool-min ) ]]; then
  echo 'Usage: check.sh [--pool-min]' >&2
  exit 2
fi
started=$SECONDS
root=$(cd "$(dirname "$0")/../.." && pwd)
build="$root/tools/mrubyc-wasm/build"
for tool in git ruby make cc emcc node python3 timeout; do
  command -v "$tool" >/dev/null || { echo "Missing tool: $tool" >&2; exit 2; }
done
mkdir -p "$build"
cc -std=c11 -Wall -Wextra -Werror -I"$root/include" \
  "$root/src/rbos/event_queue.c" "$root/tools/mrubyc-wasm/test_event_queue.c" \
  -o "$build/test-event-queue"
timeout 10s "$build/test-event-queue"
sha=$(git -C "$root/vendor/mruby" rev-parse HEAD)
host="$build/mruby-$sha"
if [[ ! -d "$host" ]]; then
  cp -R "$root/vendor/mruby" "$host"
fi
(cd "$host" && MRUBY_CONFIG=build_config/mrbc.rb ruby minirake)
mrbc="$host/build/host/bin/mrbc"
"$mrbc" -Brbos_adc_bytecode -o "$build/adc_bytecode.c" "$root/src/rbos/adc.rb"
"$mrbc" -Brbos_button_bytecode -o "$build/button_bytecode.c" "$root/src/rbos/button.rb"
"$mrbc" -Brbos_adc_lifetime_worker -o "$build/adc_lifetime_worker.c" "$root/tests/mruby/adc_lifetime_worker.rb"
"$mrbc" -Brbos_button_lifetime_worker -o "$build/button_lifetime_worker.c" "$root/tests/mruby/button_lifetime_worker.rb"
"$mrbc" -Brbos_peripherals_fixture -o "$build/peripherals_fixture.c" "$root/firmware/ruby/peripherals.rb"

mkdir -p "$build/mrubyc"
for dir in src support mrblib hal; do
  cp -R "$root/vendor/mrubyc/$dir" "$build/mrubyc/"
done
make -C "$build/mrubyc/mrblib" MRBC="$mrbc" all
make -C "$build/mrubyc/src" autogen
mapfile -t sources < <(find "$build/mrubyc/src" -maxdepth 1 -name '*.c' | sort)
mapfile -t bindings < <(find "$root/src/rbos" -type f -name '*.c' | sort)
build_runner() {
  local pool=$1 output=$2
  emcc -O1 -Wall -Wextra -Wno-unused-parameter \
  -include "$root/tools/mrubyc-wasm/runner_config.h" \
  -I"$root/include" \
  -I"$root/tools/mrubyc-wasm" \
  -I"$build/mrubyc/src" -I"$build/mrubyc/hal/emscripten" \
  -DRBOS_WASM_POOL_SIZE="$pool" -DMAX_VM_COUNT=32 -sASYNCIFY -sNODERAWFS=1 -sENVIRONMENT=node \
  -sEXIT_RUNTIME=1 -sALLOW_MEMORY_GROWTH=1 \
  -sASSERTIONS=1 -sSTACK_OVERFLOW_CHECK=1 -sCHECK_NULL_WRITES=1 \
  -sSTACK_SIZE=1048576 -sASYNCIFY_STACK_SIZE=65536 \
  "$root/tools/mrubyc-wasm/main.c" "${sources[@]}" \
  "$build/adc_bytecode.c" \
  "$build/button_bytecode.c" \
  "$build/adc_lifetime_worker.c" \
  "$build/button_lifetime_worker.c" \
  "$build/peripherals_fixture.c" \
  "${bindings[@]}" "$root/tools/mrubyc-wasm/backend.c" \
  "$root/tools/mrubyc-wasm/native_fixture.c" \
  "$build/mrubyc/hal/emscripten/hal.c" -o "$output"
}
build_runner 1048576 "$build/runner.js"

for source in "$root"/tests/mruby/*.rb; do
  "$mrbc" -o "$build/$(basename "${source%.rb}").mrb" "$source"
done
for source in "$root"/firmware/ruby/selftest/*.rb; do
  "$mrbc" -o "$build/p1-$(basename "${source%.rb}").mrb" "$source"
done
"$mrbc" -o "$build/p1-system.mrb" "$root/firmware/ruby/system.rb"

if [[ "$mode" == --pool-min ]]; then
  mkdir -p "$build/pool-min"
  pool_trial() {
    local kib=$1 runner="$build/runner.js" status=0 log="$build/pool-min/run-$1.log"
    if [[ "$kib" != 1024 ]]; then
      runner="$build/pool-min/runner.js"
      if ! build_runner "$((kib * 1024))" "$runner" > "$build/pool-min/build-$kib.log" 2>&1; then
        cat "$build/pool-min/build-$kib.log"
        exit 1
      fi
    fi
    timeout 30s node "$runner" "$build/p1-coordinator.mrb" \
      "$build/p1-worker_a.mrb" "$build/p1-worker_b.mrb" > "$log" 2>&1 || status=$?
    if [[ "$status" == 0 ]] && grep -Fxq 'PASS: P1 selftest' "$log" && ! grep -Fq 'FAIL:' "$log"; then
      echo "POOL: $kib KiB PASS"
      return 0
    fi
    if [[ "$status" != 0 && "$status" != 124 && "$status" != 137 ]] &&
       grep -Fxq 'Fatal error: Out of memory.' "$log" && ! grep -Fq 'FAIL:' "$log"; then
      echo "POOL: $kib KiB OOM (exit $status)"
      return 1
    fi
    cat "$log"
    echo "Unexpected pool trial failure: $kib KiB / exit $status" >&2
    exit 1
  }
  pool_trial 1024 || { echo 'P1 baseline failed' >&2; exit 1; }
  low=0 high=1024
  while (( high - low > 1 )); do
    mid=$(((low + high) / 2))
    if pool_trial "$mid"; then high=$mid; else low=$mid; fi
  done
  echo "PASS: P1 selftest minimum pool=$high KiB ($((high * 1024)) bytes), lower neighbor=$low KiB"
  echo "POOL: total elapsed=$((SECONDS - started)) s (includes build and system.rb compile; system task not run)"
  exit 0
fi

timeout 30s node "$build/runner.js" "$build/scheduler.mrb" \
  "$build/worker_a.mrb" "$build/worker_b.mrb" "$build/empty.mrb"
echo 'PASS: multiple tasks and empty Ruby program'

timeout 30s node "$build/runner.js" "$build/p1-coordinator.mrb" \
  "$build/p1-worker_a.mrb" "$build/p1-worker_b.mrb" | tee "$build/p1-selftest.log"
grep -Fxq 'PASS: P1 selftest' "$build/p1-selftest.log"
echo 'PASS: compiled system task and ran P1 selftests'

for profile in stress fault; do
  for source in "$root"/firmware/ruby/"$profile"/*.rb; do
    "$mrbc" -o "$build/p1-$profile-$(basename "${source%.rb}").mrb" "$source"
  done
done
echo 'PASS: compiled stress spinners and OOM fault task (compile only)'

mutex_case() {
  local expected=$1 log="$build/mutex-$1.log"
  shift
  timeout 30s node "$build/runner.js" "$@" | tee "$log"
  if grep -Fq 'FAIL:' "$log" || ! grep -Fxq "PASS: $expected" "$log"; then
    echo "Missing mutex PASS or unexpected FAIL: $expected" >&2
    exit 1
  fi
}
mutex_case 'mutex owner termination' "$build/mutex_terminated.mrb" \
  "$build/mutex_fault_owner.mrb" "$build/mutex_fault_waiter.mrb"
mutex_case 'mutex ensure release' "$build/mutex_ensure.mrb" \
  "$build/mutex_fault_owner.mrb" "$build/mutex_fault_waiter.mrb"
mutex_case 'mutex priority inversion' "$build/mutex_inversion.mrb" \
  "$build/mutex_fault_owner.mrb" "$build/mutex_fault_middle.mrb" "$build/mutex_fault_waiter.mrb"

for fixture in native_helpers temperature idiom_collections idiom_objects idiom_values idiom_resources; do
  timeout 30s node "$build/runner.js" "$build/$fixture.mrb"
done
adc_case() {
  local expected=$1 log="$build/adc-check.log"
  shift
  timeout 30s node "$build/runner.js" "$@" | tee "$log"
  if grep -Fq 'Exception(' "$log" || ! grep -Fxq "PASS: $expected" "$log"; then
    echo "Missing ADC PASS or unexpected exception: $expected" >&2
    exit 1
  fi
}
adc_case 'ADC input voltage errors cancellation and ownership' "$build/adc.mrb"
adc_case 'ADC cooperative waiting and concurrent busy' "$build/adc_concurrent.mrb" "$build/adc_worker.mrb"
adc_case 'ADC termination VM-ID reuse and foreground recovery' "$build/adc_lifetime.mrb"
adc_case 'GPIO pin modes physical levels errors and ownership' "$build/gpio.mrb"
adc_case 'Button coalescing overflow generation and cleanup' "$build/button.mrb"
adc_case 'Button cooperative wait termination and VM-ID reuse' "$build/button_lifetime.mrb"
adc_case 'P2 diagnostic task repeated samples and cleanup' "$build/peripherals.mrb"

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
expect_failure 1 'P1 selftest: same-priority fairness' "$build/p1-coordinator.mrb" \
  "$build/fairness_unfair_worker.mrb" "$build/p1-worker_b.mrb"
expect_failure 1 'expected smoke failure' "$build/expected_failure.mrb" "$build/empty.mrb"
expect_failure 1 'Mutex unlock error. not owner or not locked.' \
  "$build/mutex_non_owner.mrb" "$build/mutex_fault_owner.mrb"
if grep -Fq 'FAIL:' "$build/expected-failure.log" ||
   ! grep -Fxq 'PASS: non-owner unlock ready' "$build/expected-failure.log"; then
  echo 'Missing non-owner assertion setup PASS or unexpected FAIL' >&2
  exit 1
fi
echo 'PASS: mutex non-owner unlock assertion'
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
