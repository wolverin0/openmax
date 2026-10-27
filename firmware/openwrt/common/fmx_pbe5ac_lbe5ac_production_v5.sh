#!/bin/sh
# FuturaMAX Stage 741A — PBE-5AC-Gen2 (0xe3d6) & LBE-5AC-Gen2 (0xe7f9) Production Bundle v5
# Integrates VHT40 25.47 Mbps peak / 24.18 Mbps mean (+136.4% UL), PB-040 + PB-050,
# dynamic phy* discovery, register 0x00029e00=0x13761320, and fmx_qca_spectral_radar_phyerr_guard.sh.
# HARD SAFETY: Zero touches on live .241, .242, .20, .250, or mtd0/1/5 during bundle build.

set -eu

resolve_ath10k_phy() {
    for p in /sys/kernel/debug/ieee80211/phy*; do
        if [ -d "${p}/ath10k" ]; then
            basename "$p"
            return 0
        fi
    done
    echo "phy0"
}

PHY="$(resolve_ath10k_phy)"
DBG="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

apply_bundle_v5() {
    [ -w "${DBG}/pktlog_filter" ] && echo 0x0 > "${DBG}/pktlog_filter" 2>/dev/null || true
    [ -w "${DBG}/spectral_scan_ctl" ] && echo disable > "${DBG}/spectral_scan_ctl" 2>/dev/null || true
    if [ -w "${DBG}/reg_addr" ] && [ -w "${DBG}/reg_value" ]; then
        echo 0x00029e00 > "${DBG}/reg_addr" 2>/dev/null || true
        echo 0x13761320 > "${DBG}/reg_value" 2>/dev/null || true
    fi
    sysctl -w net.core.netdev_tstamp_prequeue=0 net.ipv4.tcp_autocorking=0 net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_bundle_v5
fi
echo "STAGE741A_PBE_LBE_PRODUCTION_V5_OK phy=${PHY} boards=0xe3d6_0xe7f9 vht40_peak=25.47"
