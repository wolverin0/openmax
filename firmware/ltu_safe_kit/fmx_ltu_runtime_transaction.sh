#!/bin/sh
# Native transient queue transaction; no firmware, DHCP, services or radio reload.
set -eu
set -f
FAMILY=ltu
MODE=--dry-run QDISC_MODE=auto UCI_MODE=disabled IDENTITY= STATE=
SEEN_MODE=0
die() { printf 'FAILED_PRECONDITION %s\n' "$1" >&2; exit 65; }
while [ "$#" -gt 0 ]; do
 case "$1" in
  --dry-run|--inspect-only|--apply|--verify|--rollback)
   [ "$SEEN_MODE" -eq 0 ] || die 'duplicate mode'; MODE=$1; SEEN_MODE=1; shift ;;
  --qdisc-mode) [ "$#" -ge 2 ] || die 'qdisc mode required'; QDISC_MODE=$2; shift 2 ;;
  --uci-mode) [ "$#" -ge 2 ] || die 'uci mode required'; UCI_MODE=$2; shift 2 ;;
  --identity) [ "$#" -ge 2 ] || die 'identity required'; IDENTITY=$2; shift 2 ;;
  --state-dir) [ "$#" -ge 2 ] || die 'state directory required'; STATE=$2; shift 2 ;;
  *) die 'unsupported argument' ;;
 esac
done
case "$QDISC_MODE" in auto|tc|sysfs-default) ;; *) die 'invalid qdisc mode' ;; esac
case "$UCI_MODE" in disabled|ram) ;; *) die 'invalid uci mode' ;; esac
case "$MODE" in --dry-run|--inspect-only)
 printf 'PLANNED family=%s qdisc_mode=%s uci_mode=%s hardware_acceptance=UNKNOWN\n' "$FAMILY" "$QDISC_MODE" "$UCI_MODE"; exit 0 ;;
esac
for tool in id ubus jsonfilter uname ethtool readlink cat tee sysctl awk sha256sum mkdir rmdir mv stat; do
 command -v "$tool" >/dev/null 2>&1 || die "missing tool: $tool"
done
[ "$(id -u)" = 0 ] || die 'uid0 required'
[ -f "$IDENTITY" ] && [ ! -L "$IDENTITY" ] || die 'regular identity contract required'
awk -F= 'BEGIN{split("board revision kernel driver firmware radio phy egress radio_ifindex egress_ifindex fingerprint",a," ");for(i in a)allowed[a[i]]=1}
 NF!=2 || !($1 in allowed) || $2=="" || seen[$1]++ {bad=1}
 END{if(NR!=11)bad=1;exit bad}' "$IDENTITY" || die 'identity schema'
value() { awk -F= -v key="$1" '$1==key{print $2}' "$IDENTITY"; }
BOARD=$(value board); REVISION=$(value revision); KERNEL=$(value kernel)
DRIVER=$(value driver); FIRMWARE=$(value firmware); RADIO=$(value radio)
PHY=$(value phy); EGRESS=$(value egress); RADIO_INDEX=$(value radio_ifindex)
EGRESS_INDEX=$(value egress_ifindex); FINGERPRINT=$(value fingerprint)
case "$FAMILY:$BOARD" in
 pbe-lbe:ubnt,powerbeam-5ac-gen2|pbe-lbe:ubnt,litebeam-ac-gen2) [ "$DRIVER" = ath10k_pci ] || die 'driver family' ;;
 ltu:ubnt,ltu-lite|ltu:ubnt,ltu-pro|ltu:ubnt,ltu-lr|ltu:ubnt,ltu-rocket|ltu:ubnt,af-ltu)
  [ "$DRIVER" = eab_driver ] && [ "$PHY" = none ] || die 'LTU native driver/PHY contract' ;;
 *) die 'unsupported board family' ;;
esac
printf '%s\n' "$RADIO" "$EGRESS" | awk 'length>15 || $0!~/^[a-zA-Z0-9_][a-zA-Z0-9_.:-]*$/ || $0==".."{bad=1} END{exit bad}' || die 'interface name'
printf '%s\n' "$RADIO_INDEX" "$EGRESS_INDEX" | awk '$0!~/^[0-9]+$/ || $0<1{bad=1} END{exit bad}' || die 'interface indices'
printf '%s\n' "$FINGERPRINT" | awk 'length!=64 || $0!~/^[0-9a-f]+$/{exit 1}' || die 'fingerprint format'
actual=$(printf '%s\n' "$BOARD" "$REVISION" "$KERNEL" "$DRIVER" "$FIRMWARE" "$RADIO" "$PHY" "$EGRESS" "$RADIO_INDEX" "$EGRESS_INDEX" | sha256sum)
[ "${actual%% *}" = "$FINGERPRINT" ] || die 'identity fingerprint'
board_json=$(ubus call system board) || die 'native board getter unavailable'
got=$(jsonfilter -s "$board_json" -e '@.board_name') || die 'board field'
[ "$got" = "$BOARD" ] || die 'board mismatch'
got=$(jsonfilter -s "$board_json" -e '@.board_revision') || die 'revision field'
[ "$got" = "$REVISION" ] || die 'revision mismatch or unavailable'
got=$(uname -r) || die 'kernel getter'; [ "$got" = "$KERNEL" ] || die 'kernel mismatch'
driver_info=$(ethtool -i "$RADIO") || die 'driver getter'
got=$(printf '%s\n' "$driver_info" | awk '/^driver: /{sub(/^driver: /,"");print}')
[ "$got" = "$DRIVER" ] || die 'driver mismatch'
got=$(printf '%s\n' "$driver_info" | awk '/^firmware-version: /{sub(/^firmware-version: /,"");print}')
[ "$got" = "$FIRMWARE" ] || die 'firmware mismatch'
got=$(readlink -f "/sys/class/net/$RADIO/device/driver") || die 'driver mapping getter'
[ "${got##*/}" = "$DRIVER" ] || die 'driver mapping mismatch'
if [ "$FAMILY" = pbe-lbe ]; then
 printf '%s\n' "$PHY" | awk '$0!~/^phy[0-9]+$/{exit 1}' || die 'explicit PHY required'
 got=$(readlink -f "/sys/class/net/$RADIO/phy80211") || die 'PHY mapping getter'
 [ "${got##*/}" = "$PHY" ] || die 'PHY mapping mismatch'
fi
got=$(cat "/sys/class/net/$RADIO/ifindex") || die 'radio index getter'; [ "$got" = "$RADIO_INDEX" ] || die 'radio index mismatch'
got=$(cat "/sys/class/net/$EGRESS/ifindex") || die 'egress index getter'; [ "$got" = "$EGRESS_INDEX" ] || die 'egress index mismatch'
case "$STATE" in /*) ;; *) die 'absolute state directory required' ;; esac
[ ! -L "$STATE" ] && [ ! -L "$STATE.lock" ] || die 'state symlink'
FILES='fingerprint family qdisc_backend uci_mode tx_queue_len backlog qdisc desired_qdisc ready phase'
[ "$UCI_MODE" != ram ] || FILES="$FILES uci_value uci_changes"
secure_state() {
 metadata=$(stat -c '%u:%a' "$STATE") || return 1
 [ "$metadata" = 0:700 ] || return 1
 for name in $FILES; do
  [ -f "$STATE/$name" ] && [ ! -L "$STATE/$name" ] || return 1
  metadata=$(stat -c '%u:%a:%h' "$STATE/$name") || return 1
  [ "$metadata" = 0:600:1 ] || return 1
 done
 [ ! -e "$STATE/phase.tmp" ] && [ ! -L "$STATE/phase.tmp" ]
}
default_fq_codel() { got=$(cat /proc/sys/net/core/default_qdisc) && [ "$got" = fq_codel ]; }
BACKEND=
if [ -d "$STATE" ]; then
 secure_state || die 'untrusted snapshot metadata or temporary path'
 got=$(cat "$STATE/fingerprint") || die 'snapshot identity getter'; [ "$got" = "$FINGERPRINT" ] || die 'snapshot identity mismatch'
 got=$(cat "$STATE/family") || die 'snapshot family getter'; [ "$got" = "$FAMILY" ] || die 'snapshot family mismatch'
 got=$(cat "$STATE/uci_mode") || die 'snapshot UCI mode getter'; [ "$got" = "$UCI_MODE" ] || die 'snapshot UCI mode mismatch'
 got=$(cat "$STATE/ready") || die 'snapshot ready getter'; [ "$got" = READY ] || die 'incomplete snapshot'
 BACKEND=$(cat "$STATE/qdisc_backend") || die 'snapshot backend getter'
 case "$BACKEND:$QDISC_MODE" in tc:auto|tc:tc|kernel_default_fq_codel:auto|kernel_default_fq_codel:sysfs-default) ;; *) die 'snapshot backend mismatch' ;; esac
else
 case "$QDISC_MODE" in auto) if command -v tc >/dev/null 2>&1; then BACKEND=tc; else BACKEND=kernel_default_fq_codel; fi ;;
  tc) BACKEND=tc ;; sysfs-default) BACKEND=kernel_default_fq_codel ;;
 esac
fi
case "$BACKEND" in tc) command -v tc >/dev/null 2>&1 || die 'tc backend unavailable' ;;
 kernel_default_fq_codel) default_fq_codel || die 'kernel default is not fq_codel' ;;
 *) die 'invalid backend' ;;
esac
if [ "$UCI_MODE" = ram ]; then command -v uci >/dev/null 2>&1 || die 'UCI RAM backend unavailable'; fi
uint() { printf '%s\n' "$1" | awk '$0!~/^[0-9]+$/{exit 1}{print $0+0}'; }
read_uint() { number=$(cat "$1") && uint "$number"; }
TXQLEN="/sys/class/net/$EGRESS/tx_queue_len"
KEY=net.core.netdev_max_backlog
read_qdisc() {
 if [ "$BACKEND" = kernel_default_fq_codel ]; then default_fq_codel || return 1; printf 'kernel_default_fq_codel\n'; return 0; fi
 output=$(tc -d qdisc show dev "$EGRESS") || return 1
 printf '%s\n' "$output" | awk '
 function bad(){error=1;exit 1}
 function integer(v){if(v!~/^[0-9]+$/)bad();return v+0}
 function timer(v,u){if(v!~/^[0-9]+([.][0-9]+)?(us|ms|s)$/)bad();u=v;sub(/^[0-9.]+/,"",u);return sprintf("%.0fus",v*(u=="s"?1000000:u=="ms"?1000:1))}
 function memory(v,u){if(v!~/^[0-9]+([.][0-9]+)?(b|Kb|Mb|Gb)$/)bad();u=v;sub(/^[0-9.]+/,"",u);return sprintf("%.0f",v*(u=="Gb"?1073741824:u=="Mb"?1048576:u=="Kb"?1024:1))}
 {if(NR!=1 || $1!="qdisc" || $2!="fq_codel" || $3!~/^[0-9a-f]+:$/ || $3=="0:" || $4!="root")bad();handle=$3
 for(i=5;i<=NF;i++){k=$i;if(k=="refcnt"){integer($(++i));continue}if(seen[k]++)bad()
 if(k=="ecn" || k=="noecn"){if(ecn!="")bad();ecn=k;continue}v=$(++i)
 if(k=="limit"){sub(/p$/,"",v);limit=integer(v)}else if(k=="flows")flows=integer(v)
 else if(k=="quantum")quantum=integer(v);else if(k=="target")target=timer(v)
 else if(k=="interval")interval=timer(v);else if(k=="memory_limit")mem=memory(v)
 else if(k=="drop_batch")drop=integer(v);else bad()}}
 END{if(error || NR!=1 || !seen["limit"] || !seen["flows"] || !seen["quantum"] || !seen["target"] || !seen["interval"] || ecn=="")exit 1
 printf "%s limit %s flows %s quantum %s target %s interval %s",handle,limit,flows,quantum,target,interval
 if(seen["memory_limit"])printf " memory_limit %s",mem;if(seen["drop_batch"])printf " drop_batch %s",drop;print " " ecn}'
}
set_attr() { printf '%s\n' "$2" | tee "$1" >/dev/null; }
set_qdisc() {
 if [ "$BACKEND" = kernel_default_fq_codel ]; then [ "$1" = kernel_default_fq_codel ] && default_fq_codel; return $?; fi
 set -- $1; handle=$1; shift
 tc qdisc replace dev "$EGRESS" root handle "$handle" fq_codel "$@"
}
phase() { (umask 077; set -C; printf '%s\n' "$1" > "$STATE/phase.tmp") && mv "$STATE/phase.tmp" "$STATE/phase"; }
verify_uci() {
 [ "$UCI_MODE" = ram ] || return 0
 got=$(uci -q get network.lan.mtu) || return 1
 [ "$got" = 1500 ] || return 1
 got=$(uci changes network) || return 1
 prior=$(cat "$STATE/uci_value") || return 1
 if [ "$prior" = 1500 ]; then [ -z "$got" ]; else [ "$got" = "network.lan.mtu='1500'" ]; fi
}
verify_applied() {
 got=$(read_uint "$TXQLEN") || return 1; [ "$got" = 1000 ] || return 1
 got=$(sysctl -n "$KEY") || return 1; [ "$got" = 1000 ] || return 1
 got=$(read_qdisc) || return 1; expected=$(cat "$STATE/desired_qdisc") || return 1
 [ "$got" = "$expected" ] || return 1
 verify_uci
}
verify_restored() {
 got=$(read_uint "$TXQLEN") || return 1; expected=$(cat "$STATE/tx_queue_len") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(sysctl -n "$KEY") || return 1; expected=$(cat "$STATE/backlog") || return 1
 [ "$got" = "$expected" ] || return 1
 got=$(read_qdisc) || return 1; expected=$(cat "$STATE/qdisc") || return 1
 [ "$got" = "$expected" ] || return 1
 if [ "$UCI_MODE" = ram ]; then
  got=$(uci -q get network.lan.mtu) || return 1; expected=$(cat "$STATE/uci_value") || return 1
  [ "$got" = "$expected" ] || return 1
  got=$(uci changes network) || return 1; [ -z "$got" ] || return 1
 fi
}
restore() {
 broken=0
 old=$(cat "$STATE/tx_queue_len") && set_attr "$TXQLEN" "$old" || broken=1
 old=$(cat "$STATE/backlog") && sysctl -w "$KEY=$old" >/dev/null || broken=1
 old=$(cat "$STATE/qdisc") && set_qdisc "$old" || broken=1
 if [ "$UCI_MODE" = ram ]; then uci revert network.lan.mtu || broken=1; fi
 verify_restored || broken=1
 [ "$broken" -eq 0 ]
}
report() {
 if [ "$BACKEND" = kernel_default_fq_codel ]; then scope='qdisc_readback=default_policy_only active_qdisc=UNKNOWN custom_qdisc_parameters=NOT_APPLIED'
 else scope='qdisc_readback=tc'; fi
 printf 'APPLIED_VERIFIED qdisc_backend=%s %s uci_runtime_activation=NOT_REQUESTED hardware_acceptance=UNKNOWN\n' "$BACKEND" "$scope"
}
LOCK="$STATE.lock"
umask 077
mkdir "$LOCK" || die 'transaction locked'
DIRTY=0 SUCCESS=0
finish() {
 code=$?; trap - 0 HUP INT TERM
 if [ "$DIRTY" -eq 1 ]; then
  if restore && phase FAILED_ROLLED_BACK; then printf 'FAILED_ROLLED_BACK readback=verified\n'; code=1
  else printf 'ROLLBACK_FAILED recovery_required=true\n' >&2; code=70; fi
 elif [ "$SUCCESS" -eq 0 ]; then printf 'FAILED_PRECONDITION no_device_writes=true\n' >&2
 fi
 rmdir "$LOCK" || code=70
 exit "$code"
}
trap finish 0
trap 'exit 130' HUP INT TERM
if [ -d "$STATE" ]; then
 if [ "$MODE" = --rollback ]; then
  DIRTY=1; restore || exit 1; phase FAILED_ROLLED_BACK || exit 1
  DIRTY=0 SUCCESS=1; printf 'FAILED_ROLLED_BACK readback=verified\n'; exit 0
 fi
 got=$(cat "$STATE/phase") || die 'snapshot phase getter'
 [ "$got" = APPLIED_VERIFIED ] || die 'recover existing transaction before applying'
 verify_applied || die 'configuration drift; use rollback'
 SUCCESS=1; report; exit 0
fi
[ "$MODE" = --apply ] || die 'snapshot missing'
mkdir "$STATE" || die 'cannot create snapshot'
printf '%s\n' "$FINGERPRINT" > "$STATE/fingerprint"
printf '%s\n' "$FAMILY" > "$STATE/family"
printf '%s\n' "$BACKEND" > "$STATE/qdisc_backend"
printf '%s\n' "$UCI_MODE" > "$STATE/uci_mode"
read_uint "$TXQLEN" > "$STATE/tx_queue_len"
old=$(sysctl -n "$KEY") || die 'backlog getter'; uint "$old" > "$STATE/backlog"
read_qdisc > "$STATE/qdisc"
if [ "$BACKEND" = tc ]; then
 awk '{for(i=1;i<=NF;i++){if($i=="quantum")$(i+1)=1514;else if($i=="target")$(i+1)="5000us";else if($i=="interval")$(i+1)="100000us"}print}' "$STATE/qdisc" > "$STATE/desired_qdisc"
else printf 'kernel_default_fq_codel\n' > "$STATE/desired_qdisc"; fi
if [ "$UCI_MODE" = ram ]; then
 old=$(uci -q get network.lan.mtu) || die 'explicit UCI key unavailable'; uint "$old" > "$STATE/uci_value"
 pending=$(uci changes network) || die 'UCI pending changes getter'
 [ -z "$pending" ] || die 'pre-existing UCI changes'
 printf '\n' > "$STATE/uci_changes"
fi
printf 'READY\n' > "$STATE/ready"
phase SNAPSHOTTED
DIRTY=1
set_attr "$TXQLEN" 1000
sysctl -w "$KEY=1000" >/dev/null
set_qdisc "$(cat "$STATE/desired_qdisc")"
if [ "$UCI_MODE" = ram ]; then
 old=$(cat "$STATE/uci_value") || exit 1
 if [ "$old" != 1500 ]; then uci set network.lan.mtu=1500; fi
fi
verify_applied
phase APPLIED_VERIFIED
DIRTY=0 SUCCESS=1
report
