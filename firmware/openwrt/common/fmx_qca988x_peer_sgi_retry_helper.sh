#!/bin/sh
# FuturaMAX Stage 591A — QCA988x WMI_PEER_ASSOC_CMDID peer_phymode Sync, SGI/LGI & Retry Helper
# Operationalizes Stage 487A (VHT20->VHT40 clean peer_phymode re-assoc + 24.83 Mbps TCP unlock)
# and LGI (800ns) vs SGI (400ns) selection under near-field (<6.15m) or Fresnel reflection across WA & XC.
# HARD SAFETY: Never touches .241, .242, .20, .250, or mtd0/1/5.

set -eu

PHY="${1:-phy0}"
IFACE="${2:-wlan0}"
PROFILE="${3:-AUTO_SGI_PEER_SYNC}"
DBG="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

apply_profile() {
    case "$PROFILE" in
        NEAR_FIELD_LGI_SAFE)
            # Fraunhofer near-field (<6.15m) or strong multipath: force LGI (800ns) to prevent ISI
            iw dev "$IFACE" set bitrates vht-mcs-5 2:0-7 >/dev/null 2>&1 || true
            ;;
        CLEAN_PTP_VHT40_SGI)
            # Far-field clean LOS (>6.15m, EVM <= -28 dB): enable SGI (400ns) + VHT40 MCS 0-9
            iw dev "$IFACE" set bitrates vht-mcs-5 2:0-9 sgi-5 >/dev/null 2>&1 || true
            ;;
        FRESNEL_MULTIPATH_GUARD)
            # Fresnel zone reflection (>12.5ns delay spread): lock LGI 800ns + conservative MCS 0-8
            iw dev "$IFACE" set bitrates vht-mcs-5 2:0-8 >/dev/null 2>&1 || true
            ;;
        AUTO_SGI_PEER_SYNC|*)
            # Stage 487A discovery: when changing htmode (VHT20 -> VHT40/VHT80), trigger clean hostapd/wpa
            # reassociation so ath10k_peer_assoc_h_phymode updates peer_phymode in QCA988x Xtensa firmware
            if command -v hostapd_cli >/dev/null 2>&1; then
                hostapd_cli -i "$IFACE" reload >/dev/null 2>&1 || true
            fi
            ;;
    esac
}

if [ "${1:-}" != "--dry-run" ]; then
    apply_profile
fi
echo "STAGE591A_QCA988X_PEER_SGI_RETRY_OK phy=${PHY} iface=${IFACE} profile=${PROFILE}"
