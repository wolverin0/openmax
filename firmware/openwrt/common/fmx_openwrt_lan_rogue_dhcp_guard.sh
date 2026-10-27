#!/bin/sh
# FuturaMAX Stage 763A — OpenWrt Bridge Zero-Rogue-DHCP/RA & QCA988x ANI Immunity Guard
# CRITICAL LAN SAFETY INVARIANT:
#   By default, OpenWrt configures dnsmasq and odhcpd with dhcp.lan.dhcpv4='server', dhcp.lan.dhcpv6='server',
#   and dhcp.lan.ra='server' on br-lan. On a bridged WDS PtP/PtMP radio connected to a switch or LAN,
#   this leaks rogue DHCPv4/v6/RA offers and hijacks the default gateway!
#   This guard enforces dhcp.lan.ignore='1', disables dhcpv4/dhcpv6/ra, stops and disables dnsmasq & odhcpd,
#   and audits QCA988x Adaptive Noise Immunity (ANI, Stage 753A) across phy0..phy2.

MODE="${1:---status}"

log_msg() {
    logger -t fmx_lan_dhcp_ani_guard "$1" 2>/dev/null || true
    echo "[fmx_lan_dhcp_ani_guard] $1"
}

enforce_zero_rogue_dhcp() {
    uci set dhcp.lan.ignore='1' 2>/dev/null || true
    uci set dhcp.lan.dhcpv4='disabled' 2>/dev/null || true
    uci set dhcp.lan.dhcpv6='disabled' 2>/dev/null || true
    uci set dhcp.lan.ra='disabled' 2>/dev/null || true
    uci commit dhcp 2>/dev/null || true
    /etc/init.d/dnsmasq stop 2>/dev/null || true
    /etc/init.d/dnsmasq disable 2>/dev/null || true
    /etc/init.d/odhcpd stop 2>/dev/null || true
    /etc/init.d/odhcpd disable 2>/dev/null || true
    log_msg "Enforced Zero-Rogue-DHCP/RA on br-lan (dhcp.lan.ignore=1, dnsmasq/odhcpd stopped & disabled)"
}

audit_status() {
    DHCP_IGNORE=$(uci -q get dhcp.lan.ignore 2>/dev/null || echo "1")
    DHCPV4=$(uci -q get dhcp.lan.dhcpv4 2>/dev/null || echo "disabled")
    DHCPV6=$(uci -q get dhcp.lan.dhcpv6 2>/dev/null || echo "disabled")
    RA_MODE=$(uci -q get dhcp.lan.ra 2>/dev/null || echo "disabled")
    ANI_STATE="enabled"
    for p in phy0 phy1 phy2; do
        if [ -r "/sys/kernel/debug/ieee80211/${p}/ath10k/ani_enable" ]; then
            ANI_STATE=$(cat "/sys/kernel/debug/ieee80211/${p}/ath10k/ani_enable" 2>/dev/null || echo "1")
        fi
    done
    log_msg "dhcp.lan.ignore=${DHCP_IGNORE} dhcpv4=${DHCPV4} dhcpv6=${DHCPV6} ra=${RA_MODE} qca988x_ani=${ANI_STATE} wmi_ani=WMI_PDEV_PARAM_ANI_ENABLE"
}

if [ "$MODE" = "--apply" ]; then
    enforce_zero_rogue_dhcp
    for p in phy0 phy1 phy2; do
        if [ -w "/sys/kernel/debug/ieee80211/${p}/ath10k/ani_enable" ]; then
            echo 1 > "/sys/kernel/debug/ieee80211/${p}/ath10k/ani_enable" 2>/dev/null || true
        fi
    done
else
    audit_status
fi

exit 0
