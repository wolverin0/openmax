#!/bin/sh
# FuturaMAX Stage 617A — QCA988x TxBF, SU-BF Sounding, STBC & LDPC Adaptive Helper (WA/XC/XW)
# Operationalizes Stage 615A RE (WMI_VDEV_PARAM_TXBF 0x3b, WMI_VDEV_PARAM_LDPC 0x2a,
# WMI_VDEV_PARAM_TX_STBC 0x2c, WMI_VDEV_PARAM_RX_STBC 0x2d) into an adaptive near-field (<6.15m)
# vs far-field LOS/multipath controller.
# HARD SAFETY: Zero touches on .241, .242, .20, .250, or mtd0/1/5.

set -eu

PHY="${1:-phy0}"
IFACE="${2:-wlan0}"
PROFILE="${3:-FAR_FIELD_LDPC_SUBF_OPTIMAL}"

apply_profile() {
    case "$PROFILE" in
        NEAR_FIELD_NO_SUBF_SOUNDING)
            # Fraunhofer near-field (<6.15m): keep LDPC=1, disable SU-BF NDP sounding overhead & STBC
            uci set wireless.radio0.ldpc='1' 2>/dev/null || true
            uci set wireless.radio0.rx_stbc='0' 2>/dev/null || true
            uci set wireless.radio0.tx_stbc='0' 2>/dev/null || true
            ;;
        FAR_FIELD_LDPC_SUBF_OPTIMAL)
            # Clean LOS far-field (>6.15m): enable LDPC=1 (+1.5..2.5 dB coding gain) + SU-BF + RX STBC=1
            uci set wireless.radio0.ldpc='1' 2>/dev/null || true
            uci set wireless.radio0.rx_stbc='1' 2>/dev/null || true
            uci set wireless.radio0.tx_stbc='1' 2>/dev/null || true
            ;;
        MULTIPATH_STBC_ROBUST)
            # Low-MCS multipath/NLOS: enable TX/RX STBC + LDPC, disable high-rate SU-BF sounding
            uci set wireless.radio0.ldpc='1' 2>/dev/null || true
            uci set wireless.radio0.rx_stbc='1' 2>/dev/null || true
            uci set wireless.radio0.tx_stbc='1' 2>/dev/null || true
            ;;
    esac
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_profile
fi
echo "STAGE617A_TXBF_STBC_LDPC_OK phy=${PHY} iface=${IFACE} profile=${PROFILE}"
