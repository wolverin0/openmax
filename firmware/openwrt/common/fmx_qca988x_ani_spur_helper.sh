#!/bin/sh
# FuturaMAX Stage 545A — QCA988x Adaptive Noise Immunity (ANI), Firstep & Spur Immunity Controller
# Operationalizes WMI_PDEV_PARAM_ANI_ENABLE (0x900d), WMI_PDEV_PARAM_ANI_OFDM_LEVEL (0x900e),
# WMI_PDEV_PARAM_ANI_CCK_LEVEL (0x900f), OpenWrt debugfs `ani_enable`, and airOS 8 UMAC proc knobs
# (`ani_ofdm_level`, `ani_cck_level`, `ani_poll_len`, `ani_listen_len`, `dyntxchain` from Stage 543A RE).

set -u

REGIME="${1:-auto}"
PHY_DEV="${FMX_PHY_DEV:-phy0}"
STATE_FILE="/tmp/fmx_qca988x_ani_spur_state.json"

# WMI PDEV Parameter IDs (QCA988x 10.1 / 10.2.4 target ABI)
WMI_PDEV_PARAM_ANI_ENABLE="0x900d"
WMI_PDEV_PARAM_ANI_OFDM_LEVEL="0x900e"
WMI_PDEV_PARAM_ANI_CCK_LEVEL="0x900f"

select_ani_profile() {
    MODE="$1"
    case "$MODE" in
        nearfield_cavity)
            # Near-field (< 6.2m dish cavity): keep ANI enabled (1) with moderate OFDM immunity (level 2)
            echo "1 2 2 100 100"
            ;;
        dense_tower_spur)
            # Co-located multi-sector tower with strong out-of-band/adjacent spurs: high OFDM immunity (level 4)
            echo "1 4 3 100 100"
            ;;
        long_range_weak_signal)
            # Long-range weak-signal link (<-74 dBm): enable weak-signal detection (OFDM level 0) so firstep stays sensitive
            echo "1 0 0 250 100"
            ;;
        *)
            # Balanced adaptive default
            echo "1 1 1 100 100"
            ;;
    esac
}

apply_ani_profile() {
    set -- $(select_ani_profile "$REGIME")
    ANI_EN="$1"
    OFDM_LVL="$2"
    CCK_LVL="$3"
    POLL_LEN="$4"
    LISTEN_LEN="$5"

    # OpenWrt ath10k debugfs path
    for d in /sys/kernel/debug/ieee80211/${PHY_DEV}/ath10k /sys/kernel/debug/ath10k/${PHY_DEV}; do
        if [ -d "$d" ] && [ -w "${d}/ani_enable" ]; then
            echo "$ANI_EN" > "${d}/ani_enable" 2>/dev/null || true
        fi
    done

    # airOS 8 WA/XC UMAC proc/iwpriv path (Stage 543A verified knobs)
    if command -v iwpriv >/dev/null 2>&1 && [ -d /sys/class/net/wifi0 ]; then
        iwpriv wifi0 ani_enable "$ANI_EN" 2>/dev/null || true
        iwpriv wifi0 ani_ofdm_level "$OFDM_LVL" 2>/dev/null || true
        iwpriv wifi0 ani_cck_level "$CCK_LVL" 2>/dev/null || true
        iwpriv wifi0 ani_poll_len "$POLL_LEN" 2>/dev/null || true
        iwpriv wifi0 ani_listen_len "$LISTEN_LEN" 2>/dev/null || true
    fi

    cat <<EOF > "${STATE_FILE}"
{
  "regime": "${REGIME}",
  "wmi_pdev_ani_enable_0x900d": ${ANI_EN},
  "wmi_pdev_ani_ofdm_level_0x900e": ${OFDM_LVL},
  "wmi_pdev_ani_cck_level_0x900f": ${CCK_LVL},
  "ani_poll_len_ms": ${POLL_LEN},
  "ani_listen_len_ms": ${LISTEN_LEN}
}
EOF
}

apply_ani_profile
exit 0
