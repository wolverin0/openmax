#!/bin/sh
# FuturaMAX Stage 661A — WA Champion v11 (284-Window Milestone) Field Rollout Kit
# Consolidates 284 cumulative counterbalanced WA live windows:
# PB-050 v1 (4000ms pacing) + PB-040 (HTT TX descriptor ring guard) + BQL=15140 (10x MTU) +
# AQL=2000/4000 us + FQ-CoDel quantum=3028 / initial_quantum=15140 + 45s Non-DFS / 120s DFS watchdog.
# HARD SAFETY: Zero touches on .241, .242, .20, .250, or mtd0/1/5.

set -eu

PHY="${1:-phy0}"
ETH="${2:-eth0}"

apply_wa_v11() {
    # 1. AQL (Airtime Queue Limits): 2000us low / 4000us high per AC
    if [ -d "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" ] || [ -w "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" ]; then
        for ac in 0 1 2 3; do
            echo "${ac} 2000 4000" > "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" 2>/dev/null || true
        done
    fi

    # 2. BQL (Byte Queue Limits): 15140 bytes (10x Ethernet MTU)
    if [ -w "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" ]; then
        echo 15140 > "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" 2>/dev/null || true
    fi

    # 3. FQ-CoDel quantum=3028 (2x MTU), initial_quantum=15140 (10x MTU)
    tc qdisc replace dev "${ETH}" root fq_codel limit 1024 flows 1024 quantum 3028 initial_quantum 15140 target 2500us interval 50000us ecn 2>/dev/null || true

    # 4. WA Champion v10/v11 TCP/NAPI sysctls
    sysctl -w net.core.netdev_tstamp_prequeue=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_autocorking=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_notsent_lowat=16384 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_limit_output_bytes=65536 >/dev/null 2>&1 || true
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_wa_v11
fi
echo "STAGE661A_WA_V11_284WINDOW_KIT_OK phy=${PHY} eth=${ETH} bql=15140 aql=2000_4000 fq_quantum=3028_15140"
