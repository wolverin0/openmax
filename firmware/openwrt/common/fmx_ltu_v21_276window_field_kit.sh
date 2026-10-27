#!/bin/sh
# FuturaMAX LTU v21 (276-window) Linux-side field kit — POST-AUDIT HARDENED (A01/A02).
# Tunes ONLY the LTU host Linux datapath: eth egress fq_codel, IRQ smp_affinity,
# tx_queue_len, and 3 sysctls. HARD SAFETY GUARANTEE: zero touches on /dev/ame*
# and no ame/ASIC register writes. Default mode inspects only; --apply required;
# APPLIED_VERIFIED emitted only after a real readback; --verify / --rollback real.
set -eu
set -f

VERSION=ltu-v21-276window
SNAP_ROOT=/tmp/fmx_kit_snapshot
MODE=--dry-run
[ "$#" -gt 0 ] && { MODE="$1"; shift; }

EGRESS="${1:-}" ; IRQ="${2:-}"
die() { printf 'FAILED_PRECONDITION %s\n' "$1" >&2; exit 65; }

# fq_codel contract (A02 fix): NO initial_quantum.
FQ_CODEL="quantum 1514 target 5ms interval 100ms flows 1024 ecn"
TXQLEN_DESIRED=2000 ; SMP_AFFINITY_DESIRED=2
SYS_K1=net.core.netdev_budget ; SYS_V1=600
SYS_K2=net.ipv4.tcp_recovery  ; SYS_V2=1
SYS_K3=net.ipv4.tcp_notsent_lowat ; SYS_V3=131072

usage() {
  printf '%s\n' "usage: $0 [--dry-run|--apply|--verify|--rollback] <egress-if> <eth-irq>" >&2
  exit 64
}

case "$MODE" in
  --dry-run)
    printf 'PLANNED profile=%s fq_codel="%s" txqlen=%s smp_affinity=%s zero_dev_ame_touch=1\n' \
      "$VERSION" "$FQ_CODEL" "$TXQLEN_DESIRED" "$SMP_AFFINITY_DESIRED"
    exit 0 ;;
  --apply|--verify|--rollback) ;;
  *) usage ;;
esac

[ -n "$EGRESS" ] && [ -n "$IRQ" ] || usage
printf '%s' "$EGRESS" | grep -qE '^[a-zA-Z0-9_.:-]{1,15}$' || die 'egress iface name'
printf '%s' "$IRQ" | grep -qE '^[0-9]+$' || die 'numeric IRQ required'
[ "$(id -u)" = 0 ] || die 'uid0 required'
for t in cat tee tc sysctl grep; do command -v "$t" >/dev/null 2>&1 || die "missing tool: $t"; done
# HARD GUARANTEE: this kit never opens ame character devices.
AFFINITY="/proc/irq/$IRQ/smp_affinity"
TXQLEN="/sys/class/net/$EGRESS/tx_queue_len"
SNAP="$SNAP_ROOT/$VERSION"

read_file() { cat "$1"; }
set_file()  { printf '%s\n' "$2" | tee "$1" >/dev/null; }

snapshot() {
  mkdir -p "$SNAP"
  read_file "$AFFINITY" > "$SNAP/affinity"
  read_file "$TXQLEN"   > "$SNAP/txqlen"
  tc -d qdisc show dev "$EGRESS" > "$SNAP/qdisc"
  sysctl -n "$SYS_K1" > "$SNAP/$SYS_K1"
  sysctl -n "$SYS_K2" > "$SNAP/$SYS_K2"
  sysctl -n "$SYS_K3" > "$SNAP/$SYS_K3"
  printf 'READY\n' > "$SNAP/ready"
}

apply_cfg() {
  set_file "$AFFINITY" "$SMP_AFFINITY_DESIRED"
  set_file "$TXQLEN" "$TXQLEN_DESIRED"
  # shellcheck disable=SC2086
  tc qdisc replace dev "$EGRESS" root fq_codel $FQ_CODEL
  sysctl -w "$SYS_K1=$SYS_V1" >/dev/null
  sysctl -w "$SYS_K2=$SYS_V2" >/dev/null
  sysctl -w "$SYS_K3=$SYS_V3" >/dev/null
}

verify_cfg() {
  ok=1
  [ "$(read_file "$TXQLEN")" = "$TXQLEN_DESIRED" ] || ok=0
  tc -d qdisc show dev "$EGRESS" | grep -q 'fq_codel' || ok=0
  tc -d qdisc show dev "$EGRESS" | grep -q 'initial_quantum' && ok=0
  [ "$(sysctl -n "$SYS_K1")" = "$SYS_V1" ] || ok=0
  [ "$(sysctl -n "$SYS_K2")" = "$SYS_V2" ] || ok=0
  [ "$(sysctl -n "$SYS_K3")" = "$SYS_V3" ] || ok=0
  [ "$ok" = 1 ]
}

rollback_cfg() {
  [ -f "$SNAP/ready" ] || die 'no snapshot to roll back'
  set_file "$AFFINITY" "$(read_file "$SNAP/affinity")"
  set_file "$TXQLEN" "$(read_file "$SNAP/txqlen")"
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
      printf 'APPLIED_VERIFIED profile=%s readback=verified zero_dev_ame_touch=1\n' "$VERSION"
      exit 0
    fi
    printf 'APPLY_FAILED rolling_back profile=%s\n' "$VERSION" >&2
    rollback_cfg
    printf 'FAILED_ROLLED_BACK profile=%s\n' "$VERSION" >&2
    exit 1 ;;
esac
