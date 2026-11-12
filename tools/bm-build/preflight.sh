#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <workspace> <new-build-directory>" >&2
  exit 2
fi
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo=$(git -C "$script_dir" rev-parse --show-toplevel)
workspace=$(realpath -e -- "$1")
build=$(realpath -m -- "$2")
for tool in west arm-zephyr-eabi-gcc cmake ninja python3; do
  command -v "$tool" >/dev/null || { echo "Preflight missing tool: $tool" >&2; exit 2; }
done
case "$build/" in
  "$repo/"*|"$workspace/"*) echo 'Preflight build must be outside repo/workspace.' >&2; exit 2 ;;
esac
if [ -e "$build" ]; then
  echo 'Preflight requires a new build directory; existing files are not removed.' >&2
  exit 2
fi
"$script_dir/check-workspace.sh" "$workspace"
cd -- "$workspace"
west build -b bm_nrf54l15dk/nrf54l15/cpuapp/s115_softdevice/mcuboot \
  "$repo/firmware" --sysbuild -d "$build" -- -Dfirmware_RBOS_PREFLIGHT=ON
grep -q 'preflight_gpiote20' "$build/firmware/zephyr/zephyr.map"
echo 'BM preflight: PASS (SDK API, generated DT, resource/IRQ guards, compile/link only; not hardware acceptance)'
