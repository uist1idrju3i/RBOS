#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <workspace>" >&2
  exit 2
fi
script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
expected=${RBOS_BM_MODULES:-$script_dir/modules.txt}
expected=$(realpath -- "$expected")
cd -- "$1"
actual=$(west list -f '{name} {path} {sha}' | awk '$1 != "manifest" {print $1, $2, $3}')
manifest_path=$(west list manifest -f '{path}')
manifest_sha=$(git -C "$manifest_path" rev-parse HEAD)
actual=$(printf '%s\nnrf-bm %s %s\n' "$actual" "$manifest_path" "$manifest_sha")
failed=0
diff -u <(LC_ALL=C sort "$expected") <(printf '%s\n' "$actual" | LC_ALL=C sort) || failed=1
while read -r name path sha; do
  head=$(git -C "$path" rev-parse HEAD)
  if [ "$head" != "$sha" ]; then
    diff -u <(printf '%s %s %s\n' "$name" "$path" "$sha") \
      <(printf '%s %s %s\n' "$name" "$path" "$head") || failed=1
  fi
  status=$(git -C "$path" status --porcelain)
  if [ -n "$status" ]; then
    printf 'Dirty project: %s (%s)\n%s\n' "$name" "$path" "$status" >&2
    failed=1
  fi
done <<< "$actual"
if [ "$failed" -ne 0 ]; then
  echo 'Workspace check: FAIL' >&2
  exit 1
fi
echo 'Workspace check: PASS (project paths, SHAs, and clean working trees)'
