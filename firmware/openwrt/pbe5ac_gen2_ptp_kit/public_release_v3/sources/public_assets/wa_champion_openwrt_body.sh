# SPDX-License-Identifier: GPL-2.0-or-later
# Public adaptation: Linux/mac80211 queue controls only. No RF/UCI/airOS writes.
# Configured values are experimental; application is NOT inferred from exit 0.
[ -f /etc/openwrt_release ] || exit 0
[ -d /sys/kernel/debug/ieee80211 ] || exit 0
board=$(cat /tmp/sysinfo/board_name 2>/dev/null)
case "$board" in
 ubnt,powerbeam-5ac-gen2|ubnt,litebeam-ac-gen2|ubnt,lap-120|ubnt,nanostation-ac-loco) ;;
 *) exit 0 ;;
esac
# Opt in after wired setup; no stock-to-champion performance dominance is claimed.
grep -qx 'enabled=1' /etc/openmax/champion.conf 2>/dev/null || exit 0
case "${ACTION:-}" in ''|add|ifup|register) ;; *) exit 0 ;; esac
umask 077
state=/var/run/openmax-champion
mkdir -p "$state" || exit 0
[ ! -L "$state" ] && [ -d "$state" ] || exit 0
mkdir "$state/lock" 2>/dev/null || exit 0
trap 'rmdir "$state/lock" 2>/dev/null' EXIT
trap 'exit 0' HUP INT TERM
report=$state/status
[ ! -L "$report" ] || exit 0
printf 'profile=public-v3\napplication=unverified\n' > "$report"
write_value() {
 [ -e "$1" ] || { printf 'missing=%s\n' "$1" >> "$report"; return 1; }
 if ! printf '%s\n' "$2" > "$1" 2>/dev/null; then
  printf 'write_failed=%s\n' "$1" >> "$report"
  return 1
 fi
 # A successful syscall is not necessarily a matching getter (kernel clamps).
 printf 'requested=%s:%s\n' "$1" "$2" >> "$report"
 return 0
}
any_ap=0
any_sta=0
for phy_dir in /sys/kernel/debug/ieee80211/phy*; do
 [ -d "$phy_dir" ] || continue
 phy=${phy_dir##*/}
 ap=0
 sta=0
 for net in /sys/class/net/phy*-ap0 /sys/class/net/phy*-sta0; do
  [ -d "$net" ] || continue
  resolved=$(readlink -f "$net/phy80211" 2>/dev/null)
  [ "${resolved##*/}" = "$phy" ] || continue
  case "${net##*/}" in *-ap0) ap=1 ;; *-sta0) sta=1 ;; esac
 done
 if [ "$ap:$sta" = '1:0' ]; then
  quantum=$FMX_AP_FQ_QUANTUM
  be_low=$FMX_AP_AQL_BE_LOW
  be_high=$FMX_AP_AQL_BE_HIGH
  any_ap=1
 elif [ "$ap:$sta" = '0:1' ]; then
  quantum=$FMX_STA_FQ_QUANTUM
  be_low=$FMX_STA_AQL_BE_LOW
  be_high=$FMX_STA_AQL_BE_HIGH
  any_sta=1
 else
  printf 'role_unknown_or_mixed=%s\n' "$phy" >> "$report"
  continue
 fi
 write_value "$phy_dir/aqm" "fq_quantum $quantum" || true
 write_value "$phy_dir/aqm" "fq_limit $FMX_FQ_LIMIT" || true
 write_value "$phy_dir/aqm" "fq_memory_limit $FMX_FQ_MEM_LIMIT" || true
 write_value "$phy_dir/aql_threshold" "$FMX_AQL_THRESHOLD" || true
 write_value "$phy_dir/aql_txq_limit" "0 $FMX_AQL_VO_LOW $FMX_AQL_VO_HIGH" || true
 write_value "$phy_dir/aql_txq_limit" "1 $FMX_AQL_VI_LOW $FMX_AQL_VI_HIGH" || true
 write_value "$phy_dir/aql_txq_limit" "2 $be_low $be_high" || true
 write_value "$phy_dir/aql_txq_limit" "3 $FMX_AQL_BK_LOW $FMX_AQL_BK_HIGH" || true
done
[ "$any_ap:$any_sta" = '0:0' ] && exit 0
# Global host queues have no unique role on a simultaneous AP/STA device.
if [ "$any_ap:$any_sta" = '1:0' ]; then
 quantum=$FMX_AP_FQ_QUANTUM
elif [ "$any_ap:$any_sta" = '0:1' ]; then
 quantum=$FMX_STA_FQ_QUANTUM
else
 quantum=
 printf 'global_qdisc_role=mixed_skipped\n' >> "$report"
fi
write_value /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max "$FMX_BQL_MAX" || true
write_value /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min "$FMX_BQL_MIN" || true
write_value /sys/class/net/eth0/queues/tx-0/byte_queue_limits/hold_time "$FMX_BQL_HOLD" || true
for q in /sys/class/net/br-lan/tx_queue_len /sys/class/net/eth0/tx_queue_len /sys/class/net/phy*-*/tx_queue_len; do
 [ -e "$q" ] && write_value "$q" "$FMX_TX_QUEUE_LEN" || true
done
if [ -n "$quantum" ]; then
 for net in eth0 br-lan; do
  if ! tc qdisc replace dev "$net" root fq_codel quantum "$quantum" limit "$FMX_FQ_LIMIT" memory_limit "$FMX_FQ_MEM_LIMIT" 2>/dev/null; then
   printf 'qdisc_failed=%s\n' "$net" >> "$report"
  fi
 done
fi
for pid in $(pidof hostapd wpa_supplicant 2>/dev/null); do
 [ -w "/proc/$pid/oom_score_adj" ] && write_value "/proc/$pid/oom_score_adj" -900 || true
done
if ! sysctl -w \
 net.core.dev_weight_tx_bias="$FMX_DEV_WEIGHT_TX_BIAS" \
 net.core.netdev_budget="$FMX_NETDEV_BUDGET" \
 net.core.netdev_budget_usecs="$FMX_NETDEV_BUDGET_USECS" \
 net.core.dev_weight="$FMX_DEV_WEIGHT" \
 net.core.netdev_max_backlog="$FMX_NETDEV_MAX_BACKLOG" \
 net.ipv4.tcp_notsent_lowat="$FMX_TCP_NOTSENT_LOWAT" \
 net.ipv4.tcp_limit_output_bytes="$FMX_TCP_LIMIT_OUTPUT_BYTES" >/dev/null 2>&1; then
 printf 'sysctl_batch_failed=1\n' >> "$report"
fi
# Preserve raw observations instead of claiming the requested state took effect.
for phy_dir in /sys/kernel/debug/ieee80211/phy*; do
 [ -d "$phy_dir" ] || continue
 for getter in aqm aql_txq_limit aql_threshold; do
  printf 'getter=%s/%s\n' "$phy_dir" "$getter" >> "$report"
  cat "$phy_dir/$getter" >> "$report" 2>/dev/null || true
 done
done
for getter in net.core.dev_weight net.core.netdev_budget net.core.netdev_budget_usecs net.core.dev_weight_tx_bias net.core.netdev_max_backlog net.ipv4.tcp_notsent_lowat net.ipv4.tcp_limit_output_bytes; do
 sysctl "$getter" >> "$report" 2>/dev/null || true
done
for getter in limit_min limit_max hold_time; do
 printf 'getter=bql/%s\n' "$getter" >> "$report"
 cat "/sys/class/net/eth0/queues/tx-0/byte_queue_limits/$getter" >> "$report" 2>/dev/null || true
done
exit 0
