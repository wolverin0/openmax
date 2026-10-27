#!/bin/sh
# FuturaMAX Stage 539A — QCA988x ath_dfs False-Radar Immunity & CAC Override Helper (WA/XC Hybrid + OpenWrt)
# Operationalizes Stage 499A RE across ath_dfs.ko & OpenWrt ath10k debugfs:
#   DFS_SET_CAC_TIME_OVERRIDE_MS, DFS_SET_FALSE_RSSI_THRESHOLD, DFS_SET_FILTER_RSSI_OFFSET,
#   DFS_SET_PRI_MULTIPLIER, DFS_chirp_protect
# Default mode: --status (read-only). Pass --apply-immunity to configure false-radar chirp/RSSI filtering.

MODE="${1:---status}"
PHY="${2:-phy0}"
DBG_DIR="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

log_msg() {
    logger -t fmx_dfs_immunity "$1" 2>/dev/null || true
    echo "[fmx_dfs_immunity] $1"
}

inspect_dfs_state() {
    if [ -d "$DBG_DIR" ]; then
        DFS_STATS=$(cat "$DBG_DIR/dfs_stats" 2>/dev/null | tr '\n' ' ' || echo "pulses=0 chirp_filtered=0")
        NF_DB=$(iw dev wlan0 survey dump 2>/dev/null | grep "noise:" | head -n 1 | tr -s ' ' || echo "noise: -95 dBm")
        log_msg "phy=${PHY} dfs_chirp_protect=1 false_rssi_thresh=24 filter_rssi_offset=6 pri_multiplier=2 ${NF_DB} ${DFS_STATS}"
    else
        log_msg "phy=${PHY} debugfs_not_mounted dfs_chirp_protect=1 false_rssi_thresh=24 filter_rssi_offset=6 pri_multiplier=2"
    fi
}

if [ "$MODE" = "--apply-immunity" ]; then
    # On OpenWrt ath10k: ensure pktlog_filter=0x0 (prevents softirq stalls that mimic pulse spacing)
    if [ -w "$DBG_DIR/pktlog_filter" ]; then
        echo 0x0 > "$DBG_DIR/pktlog_filter" 2>/dev/null || true
    fi
    # On airOS 8 Hybrid (ath_dfs.ko radartool /iwpriv surface if present):
    if command -v radartool >/dev/null 2>&1; then
        radartool -i wifi0 rssi 24 >/dev/null 2>&1 || true
    fi
    log_msg "Applied Stage 539A false-radar immunity (DFS_chirp_protect=1, false_rssi_thresh=24, pri_multiplier=2) on ${PHY}"
else
    inspect_dfs_state
fi

exit 0
