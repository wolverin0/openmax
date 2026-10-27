#!/bin/sh
# Legacy actuator retired: no direct firmware/configuration/device commands remain.
# Original source bytes are retained privately; this release does not activate them.
set -eu
set -f
MODE=--dry-run
QDISC_MODE=auto
SEEN_MODE=0
while [ "$#" -gt 0 ]; do
 case "$1" in
  --dry-run|--inspect-only|--apply|--verify|--rollback)
   [ "$SEEN_MODE" -eq 0 ] || exit 64; MODE=$1; SEEN_MODE=1; shift ;;
  --qdisc-mode) [ "$#" -ge 2 ] || exit 64; QDISC_MODE=$2; shift 2 ;;
  --identity|--state-dir|--uci-mode) [ "$#" -ge 2 ] || exit 64; shift 2 ;;
  *) printf 'FAILED_PRECONDITION retired legacy argument\n' >&2; exit 65 ;;
 esac
done
case "$QDISC_MODE" in auto|tc|sysfs-default) ;; *) exit 64 ;; esac
case "$MODE" in
 --dry-run|--inspect-only)
  printf 'PLANNED_RETIRED native_replacement=EXPLICIT_SEPARATE_TRANSACTION runtime=UNKNOWN\n'; exit 0 ;;
 *) printf 'FAILED_PRECONDITION legacy actuator retired; select reviewed native transaction explicitly\n' >&2; exit 65 ;;
esac
