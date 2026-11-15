#!/usr/bin/env bash
set -euo pipefail
if [[ $# != 3 ]]; then
  echo 'Usage: run-host.sh OPENBLINK_CHECKOUT MBEDTLS_CHECKOUT LIBMBEDCRYPTO_A' >&2
  exit 2
fi
root=$(git rev-parse --show-toplevel)
src="$root/research/implementation/a2-p3-evidence"
out="$root/.git/a2-p3-host-replay"
mkdir -p "$out"
cc -O2 -fstack-usage -I"$src/logging_shim" -I"$1/src/lib" \
  -I"$2/include" -I"$2/library" "$src/hmac_host.c" \
  "$1/src/lib/hmac-sha256.c" "$3" -lpthread -o "$out/hmac-host"
"$out/hmac-host"
