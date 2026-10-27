#!/bin/sh
# SOURCE_STAGE984_WATCHDOG_V1: bounded startup link guard; native RAM rollback only.
# No firmware restore, reboot, DHCP, network reload or protected-partition writes.
set -eu
set -f
MODE=--dry-run QDISC_MODE=auto UCI_MODE=disabled
IDENTITY= STATE= WATCH= PEER= CHANNEL= EXPECTED_SHA=
SEEN_MODE=0
die() { printf 'FAILED_PRECONDITION %s\n' "$1" >&2; exit 65; }
while [ "$#" -gt 0 ]; do
 case "$1" in
  --dry-run|--inspect-only|--apply|--verify|--rollback)
   [ "$SEEN_MODE" -eq 0 ] || die 'duplicate mode'; MODE=$1; SEEN_MODE=1; shift ;;
  --identity) [ "$#" -ge 2 ] || die 'identity required'; IDENTITY=$2; shift 2 ;;
  --state-dir) [ "$#" -ge 2 ] || die 'native snapshot required'; STATE=$2; shift 2 ;;
  --watch-state-dir) [ "$#" -ge 2 ] || die 'watch snapshot required'; WATCH=$2; shift 2 ;;
  --peer) [ "$#" -ge 2 ] || die 'peer required'; PEER=$2; shift 2 ;;
  --channel-class) [ "$#" -ge 2 ] || die 'explicit channel class required'; CHANNEL=$2; shift 2 ;;
  --transaction-sha256) [ "$#" -ge 2 ] || die 'transaction hash required'; EXPECTED_SHA=$2; shift 2 ;;
  --qdisc-mode) [ "$#" -ge 2 ] || die 'qdisc mode required'; QDISC_MODE=$2; shift 2 ;;
  --uci-mode) [ "$#" -ge 2 ] || die 'UCI mode required'; UCI_MODE=$2; shift 2 ;;
  *) die 'unsupported argument' ;;
 esac
done
case "$QDISC_MODE" in auto|tc|sysfs-default) ;; *) die 'invalid qdisc mode' ;; esac
case "$UCI_MODE" in disabled|ram) ;; *) die 'invalid UCI mode' ;; esac
case "$MODE" in --dry-run|--inspect-only)
 printf 'PLANNED watchdog=SOURCE_STAGE984_WATCHDOG_V1 qdisc_mode=%s non_dfs_s=45 dfs_s=120 physical_acceptance=UNKNOWN\n' "$QDISC_MODE"
 exit 0 ;;
esac
case "$CHANNEL" in non-dfs) BUDGET=45 ;; dfs) BUDGET=120 ;; *) die 'explicit non-dfs or dfs class required' ;; esac
for tool in id stat cat awk sha256sum mkdir rmdir mv sh ping sleep; do
 command -v "$tool" >/dev/null 2>&1 || die "missing tool: $tool"
done
[ "$(id -u)" = 0 ] || die 'uid0 required'
printf '%s\n' "$PEER" | awk 'length<1 || length>253 || $0!~/^[a-zA-Z0-9][a-zA-Z0-9_.:-]*$/{exit 1}' || die 'peer syntax'
printf '%s\n' "$EXPECTED_SHA" | awk 'length!=64 || $0!~/^[0-9a-f]+$/{exit 1}' || die 'source hash syntax'
for path in "$IDENTITY" "$STATE" "$WATCH"; do
 case "$path" in /*) ;; *) die 'absolute identity and snapshot paths required' ;; esac
 [ ! -L "$path" ] || die 'indirect identity or state path'
done
[ "$STATE" != "$WATCH" ] || die 'separate watchdog snapshot required'
[ -f "$IDENTITY" ] && [ -d "$STATE" ] || die 'native identity and existing snapshot required'
case "$0" in */*) ENGINE=${0%/*}/fmx_pbe_lbe_runtime_transaction.sh ;; *) die 'explicit script location required' ;; esac
hash_file() { result=$(sha256sum "$1") || return 1; printf '%s\n' "${result%% *}"; }
IDENTITY_SHA=$(hash_file "$IDENTITY") || die 'identity hash getter'
trusted_sources() {
 [ -f "$ENGINE" ] && [ ! -L "$ENGINE" ] || return 1
 metadata=$(stat -c '%u:%a:%h' "$ENGINE") || return 1
 [ "$metadata" = 0:755:1 ] || return 1
 actual=$(hash_file "$ENGINE") || return 1
 [ "$actual" = "$EXPECTED_SHA" ] || return 1
 [ -f "$IDENTITY" ] && [ ! -L "$IDENTITY" ] || return 1
 metadata=$(stat -c '%u:%a:%h' "$IDENTITY") || return 1
 [ "$metadata" = 0:600:1 ] || return 1
 actual=$(hash_file "$IDENTITY") || return 1
 [ "$actual" = "$IDENTITY_SHA" ]
}
native_call() {
 trusted_sources || return 1
 sh "$ENGINE" "$1" --identity "$IDENTITY" --state-dir "$STATE" --qdisc-mode "$QDISC_MODE" --uci-mode "$UCI_MODE" || return 1
 trusted_sources
}
native_verified() {
 output=$(native_call --verify) || return 1
 printf '%s\n' "$output" | awk '$1=="APPLIED_VERIFIED"{n++} END{exit !(NR==1 && n==1)}'
}
clock_ms() {
 uptime=$(cat /proc/uptime) || return 1
 printf '%s\n' "$uptime" | awk 'NF!=2 || $1!~/^[0-9]+([.][0-9]+)?$/ || $2!~/^[0-9]+([.][0-9]+)?$/ || $1>2147483647{bad=1}
 END{if(bad || NR!=1)exit 1;printf "%.0f\n",$1*1000}'
}
FILES='identity_sha transaction_sha native_state peer channel budget qdisc_mode uci_mode phase start_ms'
secure_watch() {
 [ -d "$WATCH" ] && [ ! -L "$WATCH" ] || return 1
 metadata=$(stat -c '%u:%a' "$WATCH") || return 1
 [ "$metadata" = 0:700 ] || return 1
 for field in $FILES; do
  [ -f "$WATCH/$field" ] && [ ! -L "$WATCH/$field" ] || return 1
  metadata=$(stat -c '%u:%a:%h' "$WATCH/$field") || return 1
  [ "$metadata" = 0:600:1 ] || return 1
 done
 [ ! -e "$WATCH/phase.tmp" ] && [ ! -L "$WATCH/phase.tmp" ]
}
match_field() { got=$(cat "$WATCH/$1") && [ "$got" = "$2" ]; }
phase() { [ -d "$WATCH" ] && [ ! -L "$WATCH" ] || return 1; (umask 077; set -C; printf '%s\n' "$1" > "$WATCH/phase.tmp") && mv "$WATCH/phase.tmp" "$WATCH/phase"; }
create_field() { (umask 077; set -C; printf '%s\n' "$2" > "$WATCH/$1"); }
trusted_sources || die 'untrusted transaction source or identity'
if [ -d "$WATCH" ]; then
 secure_watch || die 'untrusted watchdog snapshot'
 match_field identity_sha "$IDENTITY_SHA" && match_field transaction_sha "$EXPECTED_SHA" &&
 match_field native_state "$STATE" && match_field peer "$PEER" && match_field channel "$CHANNEL" &&
 match_field budget "$BUDGET" && match_field qdisc_mode "$QDISC_MODE" && match_field uci_mode "$UCI_MODE" || die 'watchdog snapshot binding mismatch'
 [ "$MODE" != --apply ] || die 'existing watchdog cannot restart its deadline'
else
 [ "$MODE" = --apply ] || die 'watchdog snapshot missing'
fi
LOCK=$WATCH.lock
[ ! -L "$LOCK" ] || die 'indirect lock'
umask 077
mkdir "$LOCK" || die 'watchdog locked'
ARMED=0 ARMING_VERIFY=0 RESTORING=0 SIGNAL_PENDING=0 FAIL_REASON=UNEXPECTED_EXIT
restore_verified() {
 reason=$1; target_phase=$2; RESTORING=1
 if output=$(native_call --rollback) &&
    printf '%s\n' "$output" | awk '$1=="FAILED_ROLLED_BACK" && $2=="readback=verified"{n++} END{exit !(NR==1 && NF==2 && n==1)}'; then
  ARMED=0 RESTORING=0
  if phase "$target_phase"; then :; else printf 'WATCHDOG_STATE_RECORD_FAILED restored_readback=verified\n' >&2; fi
  printf '%s reason=%s readback=verified physical_acceptance=UNKNOWN\n' "$target_phase" "$reason"
  return 0
 fi
 ARMED=0 RESTORING=0
 if phase ROLLBACK_FAILED; then :; else printf 'WATCHDOG_STATE_RECORD_FAILED recovery_required=true\n' >&2; fi
 printf 'ROLLBACK_FAILED reason=%s recovery_required=true\n' "$reason" >&2
 return 1
}
finish() {
 code=$?; trap - 0; trap '' HUP INT TERM
 if [ "$ARMED" -eq 1 ]; then
  if restore_verified "$FAIL_REASON" FAILED_ROLLED_BACK; then [ "$code" -ne 0 ] || code=1
  else code=70; fi
 fi
 rmdir "$LOCK" || code=70
 exit "$code"
}
trap finish 0
on_signal() {
 if [ "$ARMING_VERIFY" -eq 1 ] || [ "$RESTORING" -eq 1 ]; then SIGNAL_PENDING=1
 else FAIL_REASON=SIGNAL; exit 130; fi
}
trap on_signal HUP INT TERM
case "$MODE" in
 --verify)
  saved_phase=$(cat "$WATCH/phase") || die 'watchdog phase unavailable'
  case "$saved_phase" in WATCHDOG_HEALTHY_VERIFIED|ARMED)
   native_verified || die 'native configuration readback failed'
   ping -c 1 -i 1 -W 1 "$PEER" >/dev/null 2>&1 || { printf 'VERIFY_FAILED peer_readback=unavailable\n' >&2; exit 1; }
   printf 'WATCHDOG_HEALTHY_VERIFIED readback=verified physical_acceptance=UNKNOWN\n'; exit 0 ;;
   *) die 'restored_state_requires_separate_baseline_audit' ;;
  esac ;;
 --rollback)
  ARMED=1
  restore_verified MANUAL MANUAL_ROLLED_BACK || exit 70
  exit 0 ;;
esac
# Lock and traps precede readback. Responsibility begins before any WATCH IO.
# Defer signals during the readback boundary until its trust result is known.
ARMING_VERIFY=1
native_verified || { ARMING_VERIFY=0; die 'active exact-identity native snapshot could not be verified'; }
ARMED=1
ARMING_VERIFY=0
[ "$SIGNAL_PENDING" -eq 0 ] || { FAIL_REASON=SIGNAL; exit 130; }
FAIL_REASON=WATCHDOG_STATE_IO_ERROR
mkdir "$WATCH" || die 'cannot create watchdog snapshot'
create_field identity_sha "$IDENTITY_SHA"
create_field transaction_sha "$EXPECTED_SHA"
create_field native_state "$STATE"
create_field peer "$PEER"
create_field channel "$CHANNEL"
create_field budget "$BUDGET"
create_field qdisc_mode "$QDISC_MODE"
create_field uci_mode "$UCI_MODE"
phase ARMED
FAIL_REASON=MONOTONIC_CLOCK_ERROR
start=$(clock_ms) || exit 1
create_field start_ms "$start"
deadline=$((start + BUDGET * 1000))
last=$start probes=0
while [ "$probes" -le "$BUDGET" ]; do
 FAIL_REASON=MONOTONIC_CLOCK_ERROR
 now=$(clock_ms) || exit 1
 if [ "$now" -lt "$last" ] || { [ "$probes" -gt 0 ] && [ "$now" -le "$last" ]; }; then
  FAIL_REASON=MONOTONIC_CLOCK_REGRESSION_OR_STALL; exit 1
 fi
 if [ "$now" -ge "$deadline" ]; then
  restore_verified DEADLINE_EXPIRED TIMEOUT_ROLLED_BACK || exit 70
  exit 2
 fi
 last=$now
 probes=$((probes + 1))
 rc=0
 ping -c 1 -i 1 -W 1 "$PEER" >/dev/null 2>&1 || rc=$?
 FAIL_REASON=MONOTONIC_CLOCK_ERROR
 after_probe=$(clock_ms) || exit 1
 [ "$after_probe" -ge "$now" ] || { FAIL_REASON=MONOTONIC_CLOCK_REGRESSION_OR_STALL; exit 1; }
 if [ "$after_probe" -ge "$deadline" ]; then
  restore_verified DEADLINE_EXPIRED TIMEOUT_ROLLED_BACK || exit 70
  exit 2
 fi
 if [ "$rc" -eq 0 ]; then
  FAIL_REASON=NATIVE_VERIFY_ERROR
  native_verified || exit 1
  FAIL_REASON=MONOTONIC_CLOCK_ERROR
  after_verify=$(clock_ms) || exit 1
  [ "$after_verify" -ge "$after_probe" ] || { FAIL_REASON=MONOTONIC_CLOCK_REGRESSION_OR_STALL; exit 1; }
  if [ "$after_verify" -ge "$deadline" ]; then
   restore_verified DEADLINE_EXPIRED TIMEOUT_ROLLED_BACK || exit 70
   exit 2
  fi
  phase WATCHDOG_HEALTHY_VERIFIED
  ARMED=0
  printf 'WATCHDOG_HEALTHY_VERIFIED budget_s=%s probes=%s readback=verified physical_acceptance=UNKNOWN\n' "$BUDGET" "$probes"
  exit 0
 fi
 if [ "$rc" -ne 1 ]; then FAIL_REASON=PING_PROBE_ERROR; exit 1; fi
 last=$after_probe
 remaining=$(((deadline - after_probe) / 1000))
 delay=5
 [ "$remaining" -ge 5 ] || delay=$remaining
 [ "$delay" -gt 0 ] || delay=1
 FAIL_REASON=SLEEP_ERROR
 sleep "$delay" || exit 1
done
FAIL_REASON=EVENT_BUDGET_EXCEEDED
exit 1
