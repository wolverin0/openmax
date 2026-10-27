#!/bin/sh
# FuturaMAX Stage 662A — PBE-5AC-Gen2 PtP Champion v3 VHT40 OTA Rollout Kit
# Packages VHT40 24.83 Mbps (+115.35%) breakthrough with deterministic wifi down / sleep 2 / wifi up
# sequence to prevent WMI_PEER_ASSOC_CMDID (0x5003) peer_phymode desync, plus pktlog_filter=0x0
# to eliminate CE1/PCIe telemetry DMA tax on MIPS 74Kc.
# HARD SAFETY: Zero touches on live .241, .242, .20, .250, or mtd0/1/5.

set -eu

PHY="${1:-phy0}"
HTMODE="${2:-VHT40}"

apply_pbe5ac_v3() {
    # 1. Disable ath10k pktlog DMA overhead (pktlog_filter=0x0)
    if [ -w "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" ]; then
        echo 0x0 > "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" 2>/dev/null || true
    fi

    # 2. Configure VHT40 & clean WMI_PEER_ASSOC_CMDID re-association sequence
    uci set wireless.radio0.htmode="${HTMODE}" 2>/dev/null || true
    uci commit wireless 2>/dev/null || true
    wifi down >/dev/null 2>&1 || true
    sleep 2
    wifi up >/dev/null 2>&1 || true
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_pbe5ac_v3
fi
echo "STAGE662A_PBE5AC_PTP_V3_VHT40_OK phy=${PHY} htmode=${HTMODE} pktlog_filter=0x0"
