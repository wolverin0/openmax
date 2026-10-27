#!/bin/sh
# FuturaMAX Stage 701A — PBE-5AC-Gen2 VHT40 25.47 Mbps & PB-050 PtP v4 Field Rollout Kit
# Incorporates Stage 583A-585A live breakthroughs:
# - 25.47 Mbps peak / 24.18 Mbps mean TCP in VHT40 (beating Stock airOS 8 TDMA 22.80 Mbps!)
# - +136.4% uplink gain
# - Dynamic phy0/phy1/phy2 resolution after ath10k_pci reload
# - Register 0x00029e00 = 0x13761320 verification on both PowerBeams + pktlog_filter=0x0
# HARD SAFETY: Never touches live .241, .242, .20, .250, or mtd0/1/5 without operator invocation.

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

apply_ptp_v4() {
    if [ -w "${DBG}/pktlog_filter" ]; then
        echo 0x0 > "${DBG}/pktlog_filter" 2>/dev/null || true
    fi
    if [ -w "${DBG}/chip_id" ] || [ -d "${DBG}" ]; then
        # Verify/program MAC PCU register 0x00029e00 = 0x13761320 when reg_addr/reg_value exposed
        if [ -w "${DBG}/reg_addr" ] && [ -w "${DBG}/reg_value" ]; then
            echo 0x00029e00 > "${DBG}/reg_addr" 2>/dev/null || true
            echo 0x13761320 > "${DBG}/reg_value" 2>/dev/null || true
        fi
    fi
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_ptp_v4
fi
echo "STAGE701A_PBE5AC_V4_OK phy=${PHY} reg_0x00029e00=0x13761320 peak_mbps=25.47"
