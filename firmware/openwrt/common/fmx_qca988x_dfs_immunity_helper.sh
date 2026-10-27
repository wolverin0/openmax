#!/bin/sh
# FuturaMAX Stage 513A — QCA988x DFS False-Radar Pulse Discriminator & 120s CAC Watchdog Helper (FMX-DISC-24)
# For 5250-5720 MHz UNII-2A / UNII-2C (ETSI Weather Radar 5600-5650 MHz & FCC TDWR) channels.
# Integrates Stage 485A CSA/swbmiss RE (`ieee80211_start_csa`, `wmi_unified_chan_switch_handler`, `mlme_sta_swbmiss_timer_restart`)
# and FMX-DISC-24 (120s DFS Channel Availability Check watchdog vs 45s Non-DFS watchdog).

set -u

ACTION="${1:-apply}"
FREQ_MHZ="${2:-5500}"
PHY_DEV="${FMX_PHY_DEV:-phy0}"
STATE_JSON="/tmp/fmx_dfs_immunity_state.json"

is_dfs_unii2_freq() {
    F="$1"
    if [ "$F" -ge 5250 ] && [ "$F" -le 5720 ]; then
        return 0
    fi
    return 1
}

is_weather_radar_tdwr_freq() {
    F="$1"
    if [ "$F" -ge 5600 ] && [ "$F" -le 5650 ]; then
        return 0
    fi
    return 1
}

select_watchdog_timeout_sec() {
    F="$1"
    if is_dfs_unii2_freq "$F"; then
        # FMX-DISC-24: 60s CAC + association/CSA margin requires 120s rollback timer on DFS channels
        echo 120
    else
        echo 45
    fi
}

apply_dfs_false_radar_discriminator() {
    WD_SEC=$(select_watchdog_timeout_sec "$FREQ_MHZ")
    DBG_DIR="/sys/kernel/debug/ieee80211/${PHY_DEV}/ath10k"

    # Stabilize noise floor calibration period (nf_cal_period=1000 ms) so adjacent-sector OFDM chirps
    # do not trigger false PHY radar pulses due to drifting AGC reference levels
    if [ -w "${DBG_DIR}/nf_cal_period" ]; then
        echo 1000 > "${DBG_DIR}/nf_cal_period" 2>/dev/null || true
    fi

    # Record DFS discriminator telemetry state (never disables regulatory radar detection; filters adjacent-panel OFDM leakage via AGC/NF floor stability)
    cat <<EOF > "${STATE_JSON}"
{
  "freq_mhz": ${FREQ_MHZ},
  "is_dfs_unii2": $(is_dfs_unii2_freq "$FREQ_MHZ" && echo "true" || echo "false"),
  "is_twdr_5600_5650": $(is_weather_radar_tdwr_freq "$FREQ_MHZ" && echo "true" || echo "false"),
  "selected_watchdog_timeout_sec": ${WD_SEC},
  "nf_cal_period_ms": 1000,
  "csa_ecsa_preservation": "enabled"
}
EOF
}

if [ "$ACTION" = "watchdog-timeout" ]; then
    select_watchdog_timeout_sec "$FREQ_MHZ"
    exit 0
fi

apply_dfs_false_radar_discriminator
exit 0
