#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 3 ]; then
  echo "Usage: $0 <workspace> <build_dir> <out_dir>" >&2
  exit 2
fi
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo=$(git -C "$script_dir" rev-parse --show-toplevel)
workspace=$(realpath -- "$1")
build=$(realpath -e -- "$2")
out=$(realpath -m -- "$3")
case "$out/" in
  "$repo/"*) echo 'Evidence directory must be outside the RBOS repository.' >&2; exit 2 ;;
esac
if [ -e "$out" ]; then
  echo 'Evidence directory must not already exist.' >&2
  exit 2
fi
case "$out/" in
  "$build/"*|"$workspace/"*) echo 'Evidence directory must be outside the build and workspace.' >&2; exit 2 ;;
esac
mkdir -p -- "$out"
python3 - "$build" "$out" <<'PY'
import pathlib
import shutil
import sys

build, out = map(pathlib.Path, sys.argv[1:])
for source in sorted(build.rglob('*')):
    if not source.is_file() or source.is_symlink():
        continue
    name = source.name
    # keyfile.json contains public keys, but is intentionally excluded too.
    if name.endswith('.pem') or name == 'keyfile.json':
        continue
    selected = (
        name in ('.config', 'zephyr.map', 'build_info.yml')
        or name.endswith(('.signed.bin', '.signed.hex'))
        or (name.endswith('.hex') and ('merged' in name or name in (
            'production.hex', 'combined_signed_update_images.hex')))
    )
    if selected:
        target = out / source.relative_to(build)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

with (out / 'cmake-commands.txt').open('w') as target:
    target.write('CMake regeneration commands recorded by Ninja; see build_info.yml for the west invocation.\n')
    for source in sorted(build.rglob('rules.ninja')):
        for line in source.read_text().splitlines():
            if 'command =' in line and '--regenerate-during-build' in line:
                target.write(f'{source.relative_to(build)}: {line.strip()}\n')
PY
(
  cd -- "$workspace"
  # Inactive internal projects are not cloned in the public BM workspace.
  west manifest --freeze --active-only > "$out/west-manifest.yml"
  west list -f '{name} {path} {sha}' > "$out/west-list.txt"
  git -C "$(west list manifest -f '{path}')" rev-parse HEAD > "$out/manifest-head.txt"
)
git -C "$repo" rev-parse HEAD > "$out/rbos-git.txt"
git -C "$repo" status --porcelain >> "$out/rbos-git.txt"
{
  for tool in arm-zephyr-eabi-gcc cmake ninja python3 west nrfutil; do
    printf '\n== %s ==\n' "$tool"
    "$tool" --version
  done
} > "$out/tool-versions.txt" 2>&1
(
  cd -- "$out"
  mapfile -d '' files < <(find . -type f -print0 | LC_ALL=C sort -z)
  sha256sum "${files[@]}" > SHA256SUMS
)
printf 'Evidence collected: %s\n' "$out"
