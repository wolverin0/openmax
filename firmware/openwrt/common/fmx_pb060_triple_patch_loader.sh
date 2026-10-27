#!/bin/sh
# Offline Stage817A loader: inspection/checksums only; no activation acceptance.
set -eu
MODE="${1:---inspect-only}"
case "$MODE" in
  --inspect-only)
    printf '%s\n' 'Stage817A PB040+PB050+PB060 kit; runtime=UNKNOWN activation=BLOCKED'
    ;;
  --verify)
    [ "$#" -eq 2 ] || { printf '%s\n' 'usage: --verify LOCAL_PACKAGE_DIR' >&2; exit 64; }
    [ -d "$2" ] || exit 66
    (cd "$2" && sha256sum -c SHA256SUMS)
    ;;
  *)
    printf '%s\n' 'BLOCKED: offline kit has no authorized or validated activation path' >&2
    exit 64
    ;;
esac
