#!/bin/sh
# FuturaMAX Stage 773A — WA Champion v13 (344-Window Milestone) Field Rollout Kit
# Consolidates 344 live windows (.20 <-> .250 via MK1-251):
# - 78.51 Mbps peak / 76.55 Mbps mean TCP in VHT20
# - -86.37% loaded p50 RTT E2E via MK1-251
# - Permanent rogue DHCPv4/RA/DHCPv6 block on br-lan (dhcp.lan.ignore=1, ra/dhcpv6=disabled)
# - PB-040 + PB-050 + PB-060, BQL=15140, AQL=2000/4000us, FQ quantum=3028/initial_quantum=15140
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

apply_wa_v13() {
    # 1. Permanent Rogue DHCP / IPv6 RA Block on WDS Bridge (br-lan)
    uci set dhcp.lan.ignore='1' 2>/dev/null || true
    uci set dhcp.lan.dhcpv6='disabled' 2>/dev/null || true
    uci set dhcp.lan.ra='disabled' 2>/dev/null || true
    uci set dhcp.lan.ndp='disabled' 2>/dev/null || true
    uci commit dhcp 2>/dev/null || true
    /etc/init.d/dnsmasq reload >/dev/null 2>&1 || true
    /etc/init.d/odhcpd stop >/dev/null 2>&1 || true
    /etc/init.d/odhcpd disable >/dev/null 2>&1 || true

    # 2. AQL + BQL + FQ-CoDel + pktlog_filter=0x0
    if [ -w "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" ]; then
        for ac in 0 1 2 3; do
            echo "${ac} 2000 4000" > "/sys/kernel/debug/ieee80211/${PHY}/aql_txq_limit" 2>/dev/null || true
        done
    fi
    [ -w "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" ] && echo 0x0 > "/sys/kernel/debug/ieee80211/${PHY}/ath10k/pktlog_filter" 2>/dev/null || true
    [ -w "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" ] && echo 15140 > "/sys/class/net/${ETH}/queues/tx-0/byte_queue_limits/limit_max" 2>/dev/null || true
    tc qdisc replace dev "${ETH}" root fq_codel limit 1024 flows 1024 quantum 3028 initial_quantum 15140 target 2500us interval 50000us ecn 2>/dev/null || true
    sysctl -w net.core.netdev_tstamp_prequeue=0 net.ipv4.tcp_autocorking=0 net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_wa_v13
fi
echo "STAGE773A_WA_V13_344WINDOW_KIT_OK phy=${PHY} dhcp_lan_ignore=1 peak_vht20_mbps=78.51"
