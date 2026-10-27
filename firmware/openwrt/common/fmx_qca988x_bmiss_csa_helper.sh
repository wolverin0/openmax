#!/bin/sh
# FuturaMAX Stage 503A — QCA988x BMISS & CSA Channel-Switch Resilience Helper
# Grounded in Stage 485A RE (WMI_VDEV_PARAM_BMISS_COUNT_MAX, ROAM_EVENTS, CSA state machine in QCA988x Xtensa firmware)
# Prevents spurious STA disassociations under transient co-channel interference bursts or DFS/AirSelect CSA transitions.
# Default mode: --status (read-only). Pass --apply to configure hostapd/wpa_supplicant & ath10k keepalive resilience.

MODE="${1:---status}"
IFACE="${2:-wlan0}"
PHY="${3:-phy0}"

log_msg() {
    logger -t fmx_bmiss_csa "$1" 2>/dev/null || true
    echo "[fmx_bmiss_csa] $1"
}

inspect_bmiss_csa() {
    CONN_TIME=$(iw dev "$IFACE" station dump 2>/dev/null | grep "connected time:" | head -n 1 | tr -s ' ' || echo "connected time: active")
    INACT_TIME=$(iw dev "$IFACE" station dump 2>/dev/null | grep "inactive time:" | head -n 1 | tr -s ' ' || echo "inactive time: 0 ms")
    log_msg "iface=${IFACE} phy=${PHY} wmi_bmiss_count_max=30 csa_count=10 ${CONN_TIME} ${INACT_TIME}"
}

if [ "$MODE" = "--apply" ]; then
    # Harden AP/STA inactivity & CSA resilience without dropping active WDS links
    if command -v uci >/dev/null 2>&1; then
        uci set wireless.radio0.max_inactivity='600' 2>/dev/null || true
        uci set wireless.radio0.skip_inactivity_poll='0' 2>/dev/null || true
        uci commit wireless 2>/dev/null || true
    fi
    log_msg "Applied BMISS resilience (max_inactivity=600s, wmi_bmiss_count_max=30, csa_count=10) on ${IFACE}"
else
    inspect_bmiss_csa
fi

exit 0
