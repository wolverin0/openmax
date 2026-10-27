#!/bin/sh
# Manually run on an already booted tester-owned device. No writes or network.
LC_ALL=C
export LC_ALL
clean() { printf '%s' "$1" | tr -cd 'A-Za-z0-9_,.-' | cut -c1-96; }
board=UNKNOWN
if [ -f /tmp/sysinfo/board_name ]; then
 value=$(head -n1 /tmp/sysinfo/board_name)
 case "$value" in ubnt,*) board=$(clean "$value") ;; esac
fi
sysid=UNKNOWN
if [ -f /etc/board.info ]; then
 value=$(sed -n 's/^board.sysid=//p' /etc/board.info | head -n1)
 case "$value" in 0x[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]) sysid=$value ;; esac
fi
memory=$(awk '/^MemTotal:/{print $2; exit}' /proc/meminfo 2>/dev/null)
case "$memory" in ''|*[!0-9]*) memory=null ;; esac
kernel=$(clean "$(uname -r)")
arch=$(clean "$(uname -m)")
printf '{"schema_version":1,"scope":"READ_ONLY_IDENTITY_METADATA","identity_authenticated":false,'
printf '"board":"%s","sysid":"%s","kernel":"%s","architecture":"%s","mem_total_kib":%s,' "$board" "$sysid" "$kernel" "$arch" "$memory"
printf '"wireless_drivers":['
separator=
for path in /sys/class/ieee80211/phy*/device/driver; do
 [ -L "$path" ] || continue
 target=$(readlink "$path" 2>/dev/null)
 driver=${target##*/}
 case "$driver" in ath9k|ath10k_pci|ath10k_ahb) ;; *) driver=UNKNOWN ;; esac
 printf '%s"%s"' "$separator" "$driver"
 separator=,
done
printf '],"interfaces":['
separator=
count=0
for path in /sys/class/net/*; do
 [ -e "$path" ] || continue
 name=${path##*/}
 case "$name" in lo|eth[0-9]*|br-lan|wlan[0-9]*|ath[0-9]*|phy*-ap[0-9]*|phy*-sta[0-9]*) ;; *) continue ;; esac
 name=$(clean "$name")
 wireless=false
 [ ! -d "$path/wireless" ] || wireless=true
 printf '%s{"name":"%s","wireless_metadata_present":%s}' "$separator" "$name" "$wireless"
 separator=,
 count=$((count + 1))
 [ "$count" -lt 32 ] || break
done
printf '],"hardware_acceptance":false,"firmware_install_approved":false}\n'
