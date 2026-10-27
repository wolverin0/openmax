#!/bin/sh
# AP bridge maintenance only. Authentication remains in hostapd.
# No captured vendor IEs, fixed BSSID, beacon or regulatory override.
set -u
once=${1:-}
tick() {
 # Bound host memory on 64 MiB units; never increase a smaller existing cap.
 mem=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
 if [ "${mem:-0}" -gt 0 ] && [ "$mem" -le 70000 ]; then
  for aqm in /sys/kernel/debug/ieee80211/phy*/aqm; do
   [ -f "$aqm" ] || continue
   cap=$(awk '$2 == "fq_memory_limit" {print $3}' "$aqm")
   case "$cap" in ''|*[!0-9]*) continue ;; esac
   if [ "$cap" -gt 4194304 ]; then
    printf 'fq_memory_limit 4194304' > "$aqm" 2>/dev/null || true
   fi
  done
  for pid in $(pidof hostapd wpa_supplicant 2>/dev/null); do
   [ -w "/proc/$pid/oom_score_adj" ] || continue
   printf '%s' -900 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
  done
 fi
 for obj in $(ubus list 'hostapd.phy*-ap0' 2>/dev/null); do
  iface=${obj#hostapd.}
  case "$iface" in phy*-ap0) ;; *) continue ;; esac
  [ -d "/sys/class/net/$iface" ] || continue
  for dev in /sys/class/net/"$iface".sta*; do
   [ -e "$dev" ] || continue
   sta=${dev##*/}
   ip link set dev "$sta" up 2>/dev/null || continue
   ip link set dev "$sta" master br-lan 2>/dev/null || true
  done
 done
}
while :; do
 tick
 [ "$once" = '--once' ] && exit 0
 sleep 5
done
