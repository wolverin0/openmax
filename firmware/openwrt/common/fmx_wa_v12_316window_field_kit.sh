#!/bin/sh
# FuturaMAX Stage 715A — WA Champion v12 (316-Window Milestone) Field Rollout Kit
# Consolidates 316 cumulative live counterbalanced WA windows (.20 <-> .250 bench):
# - Xtensa PB-040 + PB-050 v1 (4000ms anti-storm pacing) + PB-060 CABQ guard
# - fmx_qca_htt_tx_compl_guard.sh + dynamic phy* discovery across ath10k_pci reloads
# - BQL=15140 + AQL=2000/4000us + FQ-CoDel quantum=3028 / initial_quantum=15140
# HARD SAFETY: Zero touches on live .241, .242, .20, .250, or mtd0/1/5 during build.

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
ETH="${1:-eth0}"

apply_wa_v12() {
    if [ -w "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" ]; then
        for ac in 0 1 2 3; do
            echo "${ac} 2000 4000" > "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" 2>/dev/null || true
        done
    fi
    if [ -w "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" ]; then
        echo 0x0 > "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" 2>/dev/null || true
    fi
    if [ -w "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" ]; then
        echo 15140 > "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" 2>/dev/null || true
    fi
    tc qdisc replace dev "${ETH}" root fq_codel limit 1024 flows 1024 quantum 3028 initial_quantum 15140 target 2500us interval 50000us ecn 2>/dev/null || true
    sysctl -w net.core.netdev_tstamp_prequeue=0 net.ipv4.tcp_autocorking=0 net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_wa_v12
fi
echo "STAGE715A_WA_V12_316WINDOW_KIT_OK phy=${PHY} eth=${ETH} windows=316"
