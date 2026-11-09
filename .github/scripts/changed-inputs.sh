#!/usr/bin/env bash
set -euo pipefail

kind=${1:-}
case "$kind" in
  firmware|mruby-wasm) ;;
  *) echo 'Usage: changed-inputs.sh <firmware|mruby-wasm>' >&2; exit 2 ;;
esac

changed=true
base=${BASE_SHA:-}
head=${HEAD_SHA:-HEAD}
if [ "${PUSH_FORCED:-false}" != true ] &&
   [[ "$base" =~ ^[a-f0-9]{40}$ ]] && [[ ! "$base" =~ ^0+$ ]] &&
   git cat-file -e "$base^{commit}" 2>/dev/null &&
   git cat-file -e "$head^{commit}" 2>/dev/null &&
   git merge-base --is-ancestor "$base" "$head"; then
  files=$(mktemp)
  trap 'rm -f "$files"' EXIT
  git diff --name-only --no-renames -z "$base" "$head" > "$files"
  changed=false
  while IFS= read -r -d '' path; do
    case "$kind:$path" in
      *:.github/scripts/changed-inputs.sh|*:tests/check-changes/*|*:.gitmodules|\
      firmware:firmware/*|firmware:tools/bm-build/*|firmware:.github/actions/ncs-bm-setup/*|\
      firmware:.github/workflows/firmware.yml|firmware:.github/workflows/firmware-release.yml|firmware:vendor/sdk-nrf-bm|\
      mruby-wasm:src/*|mruby-wasm:include/*|mruby-wasm:tests/mruby/*|mruby-wasm:tools/mrubyc-wasm/*|\
      mruby-wasm:vendor/mruby|mruby-wasm:vendor/mrubyc|mruby-wasm:.github/workflows/mruby-wasm.yml)
        changed=true
        break
        ;;
    esac
  done < "$files"
fi

echo "Relevant $kind inputs changed: $changed"
echo "changed=$changed" >> "${GITHUB_OUTPUT:?}"
