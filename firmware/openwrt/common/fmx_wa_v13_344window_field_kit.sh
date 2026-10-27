#!/bin/sh
# WA v13 transient queues only. No DHCP/UCI/services/firmware mutation.
# Configuration snapshots do not restore queued packets or hardware acceptance.
set -eu
set -f
MODE=--inspect-only
IDENTITY= STATE=
if [ "$#" -gt 0 ]; then MODE="$1"; shift; fi
case "$MODE" in
 --inspect-only|--dry-run)
  [ "$#" -eq 0 ] || exit 64
  printf '%s\n' 'PLANNED profile=wa-v13-transient runtime=UNKNOWN target_patch_execution=UNKNOWN'; exit 0 ;;
 --apply|--rollback) ;;
 *) printf '%s\n' 'FAILED_PRECONDITION unsupported mode' >&2; exit 64 ;;
esac
while [ "$#" -gt 0 ]; do
 case "$1" in
  --identity) [ "$#" -ge 2 ] || exit 64; IDENTITY="$2"; shift 2 ;;
  --state-dir) [ "$#" -ge 2 ] || exit 64; STATE="$2"; shift 2 ;;
  *) printf '%s\n' 'FAILED_PRECONDITION unsupported argument' >&2; exit 64 ;;
 esac
done
fail() { printf 'FAILED_PRECONDITION %s\n' "$1" >&2; exit 65; }
[ -n "$IDENTITY" ] && [ -n "$STATE" ] || fail 'identity and state-dir required'
for tool in id ubus jsonfilter uname ethtool readlink cat tee tc sysctl awk sha256sum mkdir rmdir mv; do
 command -v "$tool" >/dev/null 2>&1 || fail "missing tool: $tool"
done
[ "$(id -u)" = 0 ] || fail 'uid0 required'
[ -f "$IDENTITY" ] && [ ! -L "$IDENTITY" ] || fail 'regular identity contract required'
awk -F= 'BEGIN{split("board revision kernel driver firmware radio phy egress radio_ifindex egress_ifindex fingerprint",a," ");for(i in a)allowed[a[i]]=1}
 NF!=2 || !($1 in allowed) || $2=="" || seen[$1]++ {bad=1}
 END{if(NR!=11)bad=1;exit bad}' "$IDENTITY" || fail 'identity schema'
value() { awk -F= -v key="$1" '$1==key{print $2}' "$IDENTITY"; }
BOARD=$(value board); REVISION=$(value revision); KERNEL=$(value kernel)
DRIVER=$(value driver); FIRMWARE=$(value firmware); RADIO=$(value radio)
PHY=$(value phy); EGRESS=$(value egress); RADIO_INDEX=$(value radio_ifindex)
EGRESS_INDEX=$(value egress_ifindex); FINGERPRINT=$(value fingerprint)
case "$BOARD" in ubnt,lap-120|ubnt,litebeam-ac-gen2|ubnt,powerbeam-5ac-gen2|ubnt,nanostation-ac-loco) ;; *) fail 'unsupported board' ;; esac
[ "$DRIVER" = ath10k_pci ] || fail 'unsupported driver'
printf '%s\n' "$RADIO" "$EGRESS" | awk 'length>15 || $0!~/^[a-zA-Z0-9_][a-zA-Z0-9_.:-]*$/ || $0==".."{bad=1} END{exit bad}' || fail 'interface name'
printf '%s\n' "$PHY" | awk '$0!~/^phy[0-9]+$/{exit 1}' || fail 'explicit PHY required'
printf '%s\n' "$RADIO_INDEX" "$EGRESS_INDEX" | awk '$0!~/^[0-9]+$/ || $0<1{bad=1} END{exit bad}' || fail 'interface indices'
printf '%s\n' "$FINGERPRINT" | awk 'length!=64 || $0!~/^[0-9a-f]+$/{exit 1}' || fail 'fingerprint format'
actual=$(printf '%s\n' "$BOARD" "$REVISION" "$KERNEL" "$DRIVER" "$FIRMWARE" "$RADIO" "$PHY" "$EGRESS" "$RADIO_INDEX" "$EGRESS_INDEX" | sha256sum)
[ "${actual%% *}" = "$FINGERPRINT" ] || fail 'contract fingerprint'
board_json=$(ubus call system board) || fail 'board getter'
got_board=$(jsonfilter -s "$board_json" -e '@.board_name') || fail 'board field'
got_revision=$(jsonfilter -s "$board_json" -e '@.board_revision') || fail 'revision field'
[ "$got_board" = "$BOARD" ] && [ "$got_revision" = "$REVISION" ] || fail 'board/revision mismatch or unavailable'
got_kernel=$(uname -r) || fail 'kernel getter'
[ "$got_kernel" = "$KERNEL" ] || fail 'kernel mismatch'
driver_info=$(ethtool -i "$RADIO") || fail 'driver/firmware getter'
got_driver=$(printf '%s\n' "$driver_info" | awk '/^driver: /{sub(/^driver: /,"");print}')
got_fw=$(printf '%s\n' "$driver_info" | awk '/^firmware-version: /{sub(/^firmware-version: /,"");print}')
[ "$got_driver" = "$DRIVER" ] && [ "$got_fw" = "$FIRMWARE" ] || fail 'driver/firmware mismatch'
phy_path=$(readlink -f "/sys/class/net/$RADIO/phy80211") || fail 'radio PHY getter'
[ "${phy_path##*/}" = "$PHY" ] || fail 'radio/PHY mismatch'
driver_path=$(readlink -f "/sys/class/net/$RADIO/device/driver") || fail 'driver mapping getter'
[ "${driver_path##*/}" = "$DRIVER" ] || fail 'driver mapping mismatch'
got_radio_index=$(cat "/sys/class/net/$RADIO/ifindex") || fail 'radio index getter'
[ "$got_radio_index" = "$RADIO_INDEX" ] || fail 'radio index mismatch'
got_egress_index=$(cat "/sys/class/net/$EGRESS/ifindex") || fail 'egress index getter'
[ "$got_egress_index" = "$EGRESS_INDEX" ] || fail 'egress index mismatch'
case "$STATE" in /*) ;; *) fail 'absolute state directory required' ;; esac
[ ! -L "$STATE" ] && [ ! -L "$STATE.lock" ] || fail 'state symlink'
LOCK="$STATE.lock"
mkdir "$LOCK" || fail 'transaction locked'
umask 077
DIRTY=0 SUCCESS=0
AQL="/sys/kernel/debug/ieee80211/$PHY/aql_txq_limit"
PKTLOG="/sys/kernel/debug/ieee80211/$PHY/ath10k/pktlog_filter"
BQL="/sys/class/net/$EGRESS/queues/tx-0/byte_queue_limits/limit_max"
KEYS='net.core.netdev_tstamp_prequeue net.ipv4.tcp_autocorking net.ipv4.tcp_recovery'
uint() { case "$1" in ''|*[!0-9a-fA-Fx]*) return 1 ;; esac; printf '%u\n' "$1"; }
read_uint() { number=$(cat "$1") || return 1; uint "$number"; }
read_aql() {
 aql=$(cat "$AQL") || return 1
 printf '%s\n' "$aql" | awk '$1~/^[0-3]$/ {if(NF!=3 || $2!~/^[0-9]+$/ || $3!~/^[0-9]+$/ || $2>$3 || seen[$1]++)bad=1;lo[$1]=$2;hi[$1]=$3;n++}
 END{if(bad || n!=4)exit 1;for(i=0;i<4;i++)print i,lo[i],hi[i]}'
}
read_qdisc() {
 output=$(tc -d qdisc show dev "$EGRESS") || return 1
 printf '%s\n' "$output" | awk '
 function bad(){error=1;exit 1}
 function integer(v){if(v!~/^[0-9]+$/)bad();return v+0}
 function timer(v,u){if(v!~/^[0-9]+([.][0-9]+)?(us|ms|s)$/)bad();u=v;sub(/^[0-9.]+/,"",u);return sprintf("%.0fus",v*(u=="s"?1000000:u=="ms"?1000:1))}
 function memory(v,u){if(v!~/^[0-9]+([.][0-9]+)?(b|Kb|Mb|Gb)$/)bad();u=v;sub(/^[0-9.]+/,"",u);return sprintf("%.0f",v*(u=="Gb"?1073741824:u=="Mb"?1048576:u=="Kb"?1024:1))}
 {if(NR!=1 || $1!="qdisc" || $2!="fq_codel" || $3!~/^[0-9a-f]+:$/ || $3=="0:" || $4!="root")bad();handle=$3
 for(i=5;i<=NF;i++){
 k=$i;if(k=="refcnt"){integer($(++i));continue}
 if(seen[k]++)bad()
 if(k=="ecn" || k=="noecn"){if(ecn!="")bad();ecn=k;continue}
 v=$(++i)
 if(k=="limit"){sub(/p$/,"",v);limit=integer(v)}
 else if(k=="flows")flows=integer(v)
 else if(k=="quantum")quantum=integer(v)
 else if(k=="target")target=timer(v)
 else if(k=="interval")interval=timer(v)
 else if(k=="memory_limit")mem=memory(v)
 else if(k=="drop_batch")drop=integer(v)
 else bad()
 }}
 END{if(error || NR!=1 || !seen["limit"] || !seen["flows"] || !seen["quantum"] || !seen["target"] || !seen["interval"] || ecn=="")exit 1
 printf "%s limit %s flows %s quantum %s target %s interval %s",handle,limit,flows,quantum,target,interval
 if(seen["memory_limit"])printf " memory_limit %s",mem
 if(seen["drop_batch"])printf " drop_batch %s",drop
 print " " ecn}'
}
set_attr() { printf '%s\n' "$2" | tee "$1" >/dev/null; }
set_aql_file() { while read -r ac low high; do set_attr "$AQL" "$ac $low $high" || return 1; done < "$1"; }
set_qdisc() {
 # Strict parser tokens only; no shell evaluation, no change to sch_fq.
 set -- $1
 handle=$1; shift
 tc qdisc replace dev "$EGRESS" root handle "$handle" fq_codel "$@"
}
phase() { printf '%s\n' "$1" > "$STATE/phase.tmp" && mv "$STATE/phase.tmp" "$STATE/phase"; }
verify_snapshot() {
 got=$(read_aql) || return 1; expected=$(cat "$STATE/aql") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(read_uint "$PKTLOG") || return 1; expected=$(cat "$STATE/pktlog") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(read_uint "$BQL") || return 1; expected=$(cat "$STATE/bql") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(read_qdisc) || return 1; expected=$(cat "$STATE/qdisc") || return 1
 [ "$got" = "$expected" ] || return 1
 for key in $KEYS; do
  got=$(sysctl -n "$key") || return 1; expected=$(cat "$STATE/$key") || return 1
  [ "$got" = "$expected" ] || return 1
 done
}
restore_snapshot() {
 broken=0
 set_aql_file "$STATE/aql" || broken=1
 prior=$(cat "$STATE/pktlog_raw") && set_attr "$PKTLOG" "$prior" || broken=1
 prior=$(cat "$STATE/bql") && set_attr "$BQL" "$prior" || broken=1
 prior=$(cat "$STATE/qdisc") && set_qdisc "$prior" || broken=1
 for key in $KEYS; do
  previous=$(cat "$STATE/$key") || { broken=1; continue; }
  sysctl -w "$key=$previous" >/dev/null || broken=1
 done
 verify_snapshot || broken=1
 [ "$broken" -eq 0 ]
}
finish() {
 code=$?
 trap - 0 HUP INT TERM
 if [ "$DIRTY" -eq 1 ]; then
  if restore_snapshot && phase FAILED_ROLLED_BACK; then printf '%s\n' 'FAILED_ROLLED_BACK configuration_readback=verified'; code=1
  else printf '%s\n' 'ROLLBACK_FAILED recovery_required=true' >&2; code=70; fi
 elif [ "$SUCCESS" -eq 0 ]; then printf '%s\n' 'FAILED_PRECONDITION no_device_writes=true' >&2
 fi
 rmdir "$LOCK" || code=70
 exit "$code"
}
trap finish 0
trap 'exit 130' HUP INT TERM
verify_applied() {
 got=$(read_aql) || return 1
 [ "$got" = "$(printf '0 2000 4000\n1 2000 4000\n2 2000 4000\n3 2000 4000')" ] || return 1
 got=$(read_uint "$PKTLOG") || return 1; [ "$got" = 0 ] || return 1
 got=$(read_uint "$BQL") || return 1; [ "$got" = 15140 ] || return 1
 got=$(read_qdisc) || return 1; expected=$(cat "$STATE/desired_qdisc") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(sysctl -n net.core.netdev_tstamp_prequeue) || return 1; [ "$got" = 0 ] || return 1
 got=$(sysctl -n net.ipv4.tcp_autocorking) || return 1; [ "$got" = 0 ] || return 1
 got=$(sysctl -n net.ipv4.tcp_recovery) || return 1; [ "$got" = 1 ] || return 1
}
if [ -d "$STATE" ]; then
 [ "$(cat "$STATE/fingerprint")" = "$FINGERPRINT" ] || fail 'snapshot identity mismatch'
 [ "$(cat "$STATE/ready")" = READY ] || fail 'incomplete snapshot'
 if [ "$MODE" = --rollback ]; then
  DIRTY=1; restore_snapshot || exit 1; phase FAILED_ROLLED_BACK || exit 1
  DIRTY=0 SUCCESS=1; printf '%s\n' 'FAILED_ROLLED_BACK configuration_readback=verified'; exit 0
 fi
 [ "$(cat "$STATE/phase")" = APPLIED_VERIFIED ] || fail 'recover existing transaction before applying'
 verify_applied || fail 'applied configuration drift; use rollback'
 SUCCESS=1; printf '%s\n' 'APPLIED_VERIFIED idempotent=true target_patch_execution=UNKNOWN'; exit 0
fi
[ "$MODE" = --apply ] || fail 'snapshot missing'
mkdir "$STATE" || fail 'cannot create snapshot'
printf '%s\n' "$FINGERPRINT" > "$STATE/fingerprint"
read_aql > "$STATE/aql"
pktlog_raw=$(cat "$PKTLOG")
uint "$pktlog_raw" > "$STATE/pktlog"
printf '%s\n' "$pktlog_raw" > "$STATE/pktlog_raw"
read_uint "$BQL" > "$STATE/bql"
read_qdisc > "$STATE/qdisc"
for key in $KEYS; do previous=$(sysctl -n "$key") || fail 'sysctl snapshot getter'; uint "$previous" > "$STATE/$key" || fail 'sysctl snapshot value'; done
awk '{for(i=1;i<=NF;i++){if($i=="limit" || $i=="flows")$(i+1)=1024;else if($i=="quantum")$(i+1)=3028;else if($i=="target")$(i+1)="2500us";else if($i=="interval")$(i+1)="50000us"} print}' "$STATE/qdisc" > "$STATE/desired_qdisc"
printf '%s\n' READY > "$STATE/ready"
phase SNAPSHOTTED
DIRTY=1
for ac in 0 1 2 3; do set_attr "$AQL" "$ac 2000 4000"; done
set_attr "$PKTLOG" 0
set_attr "$BQL" 15140
set_qdisc "$(cat "$STATE/desired_qdisc")"
sysctl -w net.core.netdev_tstamp_prequeue=0 >/dev/null
sysctl -w net.ipv4.tcp_autocorking=0 >/dev/null
sysctl -w net.ipv4.tcp_recovery=1 >/dev/null
verify_applied
phase APPLIED_VERIFIED
DIRTY=0 SUCCESS=1
printf '%s\n' 'APPLIED_VERIFIED configuration_readback=verified target_patch_execution=UNKNOWN'
