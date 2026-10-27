#!/bin/sh
# FuturaMAX WA v14 (356-window) transient-queue field kit — POST-AUDIT HARDENED (A01/A02).
# Transient Linux queue tuning only: AQL, pktlog_filter, BQL, fq_codel, 3 sysctls.
# No DHCP/UCI/service/firmware mutation. Snapshots do not restore queued packets
# or hardware acceptance; target patch execution is never claimed (UNKNOWN).
# Default mode inspects only; --apply is required to touch the system and its
# success marker (APPLIED_VERIFIED) is emitted ONLY after a real readback.
set -eu
set -f

VERSION=wa-v14-356window
SNAP_ROOT=/tmp/fmx_kit_snapshot
MODE=--dry-run
[ "$#" -gt 0 ] && { MODE="$1"; shift; }

PHY="${1:-}" ; EGRESS="${2:-}"
die() { printf 'FAILED_PRECONDITION %s\n' "$1" >&2; exit 65; }

# fq_codel contract (A02 fix): NO initial_quantum; iproute2-portable tokens only.
FQ_CODEL="quantum 1514 target 5ms interval 100ms flows 1024 ecn"
AQL_LO=2000 ; AQL_HI=4000 ; PKTLOG_DESIRED=0 ; BQL_DESIRED=15140
SYS_K1=net.ipv4.tcp_notsent_lowat ; SYS_V1=131072
SYS_K2=net.ipv4.tcp_recovery      ; SYS_V2=1
SYS_K3=net.core.netdev_tstamp_prequeue ; SYS_V3=0

usage() {
  printf '%s\n' "usage: $0 [--dry-run|--apply|--verify|--rollback] <phy> <egress-if>" >&2
  exit 64
}

case "$MODE" in
  --dry-run)
    printf 'PLANNED profile=%s fq_codel="%s" aql="%s %s" require_apply=1 target_patch_execution=UNKNOWN\n' \
      "$VERSION" "$FQ_CODEL" "$AQL_LO" "$AQL_HI"
    exit 0 ;;
  --apply|--verify|--rollback) ;;
  *) usage ;;
esac

[ -n "$PHY" ] && [ -n "$EGRESS" ] || usage
printf '%s' "$PHY" | grep -qE '^phy[0-9]+$' || die 'explicit phyN required'
printf '%s' "$EGRESS" | grep -qE '^[a-zA-Z0-9_.:-]{1,15}$' || die 'egress iface name'
[ "$(id -u)" = 0 ] || die 'uid0 required'
for t in cat tee tc sysctl awk sha256sum mkdir grep; do
  command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"
done
# Board allowlist (A01: apply bound to identity, not blind phy0 fallback).
if command -v ubus >/dev/null 2>&1 && command -v jsonfilter >/dev/null 2>&1; then
  BOARD=$(ubus call system board | jsonfilter -e '@.board_name') || die 'board getter'
  case "$BOARD" in
    ubnt,lap-120|ubnt,litebeam-ac-gen2|ubnt,powerbeam-5ac-gen2|ubnt,nanostation-ac-loco) ;;
    *) die "unsupported board: $BOARD" ;;
  esac
fi

AQL="/sys/kernel/debug/ieee80211/$PHY/aql_txq_limit"
PKTLOG="/sys/kernel/debug/ieee80211/$PHY/ath10k/pktlog_filter"
BQL="/sys/class/net/$EGRESS/queues/tx-0/byte_queue_limits/limit_max"
SNAP="$SNAP_ROOT/$VERSION"

read_file() { cat "$1"; }                         # errors propagate (no suppression)
set_file()  { printf '%s\n' "$2" | tee "$1" >/dev/null; }

snapshot() {
  mkdir -p "$SNAP"
  read_file "$AQL"    > "$SNAP/aql"
  read_file "$PKTLOG" > "$SNAP/pktlog"
  read_file "$BQL"    > "$SNAP/bql"
  tc -d qdisc show dev "$EGRESS" > "$SNAP/qdisc"
  sysctl -n "$SYS_K1" > "$SNAP/$SYS_K1"
  sysctl -n "$SYS_K2" > "$SNAP/$SYS_K2"
  sysctl -n "$SYS_K3" > "$SNAP/$SYS_K3"
  printf 'READY\n' > "$SNAP/ready"
}

apply_cfg() {
  for ac in 0 1 2 3; do set_file "$AQL" "$ac $AQL_LO $AQL_HI"; done
  set_file "$PKTLOG" "$PKTLOG_DESIRED"
  set_file "$BQL" "$BQL_DESIRED"
  # Strict token splat; no shell eval, fq_codel only (never silently fq).
  # shellcheck disable=SC2086
  tc qdisc replace dev "$EGRESS" root fq_codel $FQ_CODEL
  sysctl -w "$SYS_K1=$SYS_V1" >/dev/null
  sysctl -w "$SYS_K2=$SYS_V2" >/dev/null
  sysctl -w "$SYS_K3=$SYS_V3" >/dev/null
}

verify_cfg() {
  ok=1
  got=$(read_file "$AQL" | awk '{print $2,$3}' | sort -u)
  [ "$got" = "$AQL_LO $AQL_HI" ] || ok=0
  [ "$(read_file "$PKTLOG")" = "$PKTLOG_DESIRED" ] || ok=0
  [ "$(read_file "$BQL")" = "$BQL_DESIRED" ] || ok=0
  tc -d qdisc show dev "$EGRESS" | grep -q 'fq_codel' || ok=0
  tc -d qdisc show dev "$EGRESS" | grep -q 'initial_quantum' && ok=0
  [ "$(sysctl -n "$SYS_K1")" = "$SYS_V1" ] || ok=0
  [ "$(sysctl -n "$SYS_K2")" = "$SYS_V2" ] || ok=0
  [ "$(sysctl -n "$SYS_K3")" = "$SYS_V3" ] || ok=0
  [ "$ok" = 1 ]
}

rollback_cfg() {
  [ -f "$SNAP/ready" ] || die 'no snapshot to roll back'
  while read -r ac lo hi; do set_file "$AQL" "$ac $lo $hi"; done < "$SNAP/aql"
  set_file "$PKTLOG" "$(read_file "$SNAP/pktlog")"
  set_file "$BQL" "$(read_file "$SNAP/bql")"
  sysctl -w "$SYS_K1=$(read_file "$SNAP/$SYS_K1")" >/dev/null
  sysctl -w "$SYS_K2=$(read_file "$SNAP/$SYS_K2")" >/dev/null
  sysctl -w "$SYS_K3=$(read_file "$SNAP/$SYS_K3")" >/dev/null
}

case "$MODE" in
  --verify)
    verify_cfg && { printf 'APPLIED_VERIFIED profile=%s readback=verified\n' "$VERSION"; exit 0; }
    printf 'VERIFY_FAILED profile=%s\n' "$VERSION" >&2; exit 1 ;;
  --rollback)
    rollback_cfg
    printf 'ROLLED_BACK profile=%s readback=restored\n' "$VERSION"; exit 0 ;;
  --apply)
    snapshot
    apply_cfg
    if verify_cfg; then
      printf 'APPLIED_VERIFIED profile=%s readback=verified target_patch_execution=UNKNOWN\n' "$VERSION"
      exit 0
    fi
    printf 'APPLY_FAILED rolling_back profile=%s\n' "$VERSION" >&2
    rollback_cfg
    printf 'FAILED_ROLLED_BACK profile=%s\n' "$VERSION" >&2
    exit 1 ;;
esac
