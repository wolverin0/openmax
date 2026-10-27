#!/bin/sh
# Stage818A defaults to inspection. Guarded DHCP apply never changes modulation.
set -eu
MODE="${1:---inspect-only}"
CHAIN=FMX818_DHCP

chain_matches() {
  rules=$(ebtables -t filter -L "$CHAIN" --Lx) || return 1
  actual=$(printf '%s\n' "$rules" | awk -v chain="$CHAIN" '
    $4 == "-A" && $5 == chain {
      for(i=6;i<=NF;i++) { if($i=="--ip-proto")$i="--ip-protocol"; if($i=="--ip6-proto")$i="--ip6-protocol"; printf "%s%s",$i,(i<NF?" ":"\n") }
    }')
  expected=$(printf '%s\n' '-p IPv4 --ip-protocol udp --ip-sport 67 --ip-dport 68 -j DROP' '-p IPv6 --ip6-protocol udp --ip6-sport 547 --ip6-dport 546 -j DROP')
  [ "$actual" = "$expected" ]
}

jump_matches() {
  parent="$1"
  listing=$(ebtables -t filter -L "$parent" --Lx) || return 1
  first=$(printf '%s\n' "$listing" | awk -v parent="$parent" '
    $4 == "-A" && $5 == parent { for(i=6;i<=NF;i++)printf "%s%s",$i,(i<NF?" ":"\n"); exit }')
  [ "$first" = "--logical-out br1 -j $CHAIN" ] || return 1
  actual=$(printf '%s\n' "$listing" | awk -v parent="$parent" -v chain="$CHAIN" '
    $4 == "-A" && $5 == parent {
      found=0; for(i=6;i<NF;i++)if($i=="-j" && $(i+1)==chain)found=1
      if(found)for(i=6;i<=NF;i++)printf "%s%s",$i,(i<NF?" ":"\n")
    }')
  [ "$actual" = "--logical-out br1 -j $CHAIN" ]
}

rollback_new_chain() {
  [ "$created" -eq 1 ] || return 0
  failed=0
  # Only exact jumps to our newly created chain and that chain may be removed.
  ebtables -t filter -D FORWARD --logical-out br1 -j "$CHAIN" >/dev/null 2>&1 || true
  ebtables -t filter -D OUTPUT --logical-out br1 -j "$CHAIN" >/dev/null 2>&1 || true
  ebtables -t filter -F "$CHAIN" >/dev/null 2>&1 || failed=1
  ebtables -t filter -X "$CHAIN" >/dev/null 2>&1 || failed=1
  if [ "$failed" -ne 0 ]; then
    printf '%s\n' 'ROLLBACK_INCOMPLETE: operator inspection required' >&2
    return 1
  fi
}

cleanup() {
  result=$?
  trap - 0 HUP INT TERM
  if [ "$success" -eq 0 ]; then
    rollback_new_chain || result=70
  fi
  rmdir "$lock" || result=70
  exit "$result"
}

apply_zero_dhcp() {
  [ "$#" -eq 1 ] && [ "$1" = '--confirm-br1-192.168.1.20' ] || {
    printf '%s\n' 'BLOCKED: explicit --confirm-br1-192.168.1.20 required' >&2; return 64;
  }
  for tool in id ip ebtables awk mkdir rmdir; do
    command -v "$tool" >/dev/null 2>&1 || { printf 'BLOCKED: missing %s\n' "$tool" >&2; return 69; }
  done
  [ "$(id -u)" = 0 ] || { printf '%s\n' 'BLOCKED: uid0 required' >&2; return 77; }
  version=$(ebtables --version) || return 69
  case "$version" in
    'ebtables v2.'*|'ebtables v1.'*'(legacy)'*|'ebtables v1.'*'(nf_tables)'*) ;;
    *) printf '%s\n' 'BLOCKED: unknown ebtables backend' >&2; return 69 ;;
  esac
  addresses=$(ip -4 -o addr show dev br1) || return 69
  printf '%s\n' "$addresses" | awk '$2=="br1" && $3=="inet" {split($4,a,"/");if(a[1]=="192.168.1.20")n++} END{exit(n==1?0:1)}' || {
    printf '%s\n' 'BLOCKED: br1 fallback address must be exactly 192.168.1.20' >&2; return 78;
  }
  lock="${TMPDIR:-/tmp}/fmx-stage818a-zero-dhcp.lock"
  mkdir "$lock" || { printf '%s\n' 'BLOCKED: concurrent DHCP shield operation' >&2; return 75; }
  created=0 success=0
  trap cleanup 0
  trap 'exit 1' HUP INT TERM
  if ebtables -t filter -L "$CHAIN" --Lx >/dev/null 2>&1; then
    # Never flush an existing chain; accept repeats only after exact readback.
    chain_matches && jump_matches OUTPUT && jump_matches FORWARD || {
      printf '%s\n' 'BLOCKED: existing owned chain/jumps differ; preserving firewall' >&2; return 78;
    }
  else
    ebtables -t filter -N "$CHAIN" || return 1
    created=1
    ebtables -t filter -A "$CHAIN" -p IPv4 --ip-protocol udp --ip-sport 67 --ip-dport 68 -j DROP || return 1
    ebtables -t filter -A "$CHAIN" -p IPv6 --ip6-protocol udp --ip6-sport 547 --ip6-dport 546 -j DROP || return 1
    ebtables -t filter -I OUTPUT 1 --logical-out br1 -j "$CHAIN" || return 1
    ebtables -t filter -I FORWARD 1 --logical-out br1 -j "$CHAIN" || return 1
    chain_matches && jump_matches OUTPUT && jump_matches FORWARD || return 1
  fi
  success=1
  printf '%s\n' 'br1 DHCP server-offer filter installed; lease_capture_verified=false persistence=UNKNOWN'
}

case "$MODE" in
  --inspect-only)
    printf '%s\n' 'Stage818A LTU 4096QAM/12X LDPC Super4096: runtime=UNKNOWN'
    printf '%s\n' 'br1 192.168.1.20 zero_rogue_dhcp_verified=false guarded_apply_available=true'
    ;;
  --inspect-local)
    # Read only explicitly named sysfs attributes, never a character device.
    for attr in autoMcs4096 tx_pa_comp_mode evm_now evm_avg; do
      found=0
      for base in /sys/module/ame_core/parameters /sys/module/ame_dev/parameters; do
        if [ -f "$base/$attr" ]; then
          printf '%s=' "$attr"
          head -n 1 "$base/$attr"
          found=1
          break
        fi
      done
      [ "$found" -eq 1 ] || printf '%s=UNKNOWN\n' "$attr"
    done
    ;;
  --plan-zero-dhcp)
    # Printed proposal only. Deployment requires independent bench acceptance.
    printf '%s\n' '# PLAN ONLY: confirm br1 has fallback 192.168.1.20; do not execute unreviewed.'
    printf '%s\n' '# Guarded apply uses dedicated FMX818_DHCP chain and first-rule br1 jumps.'
    printf '%s\n' '# FMX818_DHCP: IPv4 UDP 67->68 DROP; IPv6 UDP 547->546 DROP.'
    printf '%s\n' '# Runtime lease, respawn and persistence verification: UNKNOWN'
    ;;
  --apply-zero-dhcp)
    shift
    apply_zero_dhcp "$@"
    ;;
  *)
    printf '%s\n' 'BLOCKED: no validated modulation unlock or DHCP apply path in offline kit' >&2
    exit 64
    ;;
esac
