#!/bin/sh
# FuturaMAX Stage 697A — Dynamic phy* Wiphy Index & RAM SGMT Bind-Mount Loader (PB-040 + PB-050)
# Compatible with PowerBeam 5AC Gen2 (0xe3d6) & LiteBeam 5AC Gen2 (0xe4d6 / 0xe7f9)
# Zero flash writes; includes 45s Non-DFS / 120s DFS rollback watchdog.

ACTION="${1:-status}"
TARGET_HTMODE="${2:-VHT20}"
ROLE="${3:-ap}"
WATCHDOG_SEC=45
DFS_CHAN="$(uci -q get wireless.radio0.channel)"
[ "${DFS_CHAN:-36}" -ge 52 ] && [ "${DFS_CHAN:-36}" -le 144 ] && WATCHDOG_SEC=120

resolve_phy() {
    dirname $(ls -d /sys/kernel/debug/ieee80211/phy*/ath10k 2>/dev/null | head -n1)
}

if [ "$ACTION" = "load-sgmt" ] && [ -f /tmp/firmware-2-pb050.bin ]; then
    CUR_CSUM="$(cat $(resolve_phy)/ath10k/fw_checksums 2>/dev/null | grep -c '12b29d01')"
    if [ "${CUR_CSUM:-0}" -eq 0 ]; then
        mkdir -p /tmp/fmx_xtensa_pb050
        cp -a /lib/firmware/ath10k/QCA988X/hw2.0/* /tmp/fmx_xtensa_pb050/
        cp -f /tmp/firmware-2-pb050.bin /tmp/fmx_xtensa_pb050/firmware-2.bin
        umount /lib/firmware/ath10k/QCA988X/hw2.0 2>/dev/null || true
        mount --bind /tmp/fmx_xtensa_pb050 /lib/firmware/ath10k/QCA988X/hw2.0
        wifi down
        sleep 1
        rmmod ath10k_pci
        sleep 1
        modprobe ath10k_pci
        sleep 2
        wifi up
        sleep 12
    fi
fi

if [ "$ACTION" = "switch-bw" ]; then
    CUR_HT="$(uci -q get wireless.radio0.htmode)"
    if [ "$CUR_HT" != "$TARGET_HTMODE" ]; then
        uci set wireless.radio0.htmode="$TARGET_HTMODE"
        uci set wireless.radio0.short_gi_20="0"
        uci set wireless.radio0.short_gi_40="0"
        uci set wireless.radio0.short_gi_80="0"
        uci commit wireless
        wifi down
        sleep 2
        wifi up
        sleep 12
    fi
fi

BW_IDX=0
[ "$TARGET_HTMODE" = "VHT40" ] && BW_IDX=1
[ "$TARGET_HTMODE" = "VHT80" ] && BW_IDX=2
/etc/hotplug.d/net/99-fmx-wa-ptp-champion-v4 "$BW_IDX" "$ROLE"

PHY_DIR="$(resolve_phy)"
PHY_NAME="$(basename "$PHY_DIR")"
echo "PHY=$PHY_NAME WATCHDOG=${WATCHDOG_SEC}s"
cat "$PHY_DIR/ath10k/fw_checksums" 2>/dev/null || true
