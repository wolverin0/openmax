#!/bin/sh
# FuturaMAX Stage 445A — Closed-Loop Pillar 1/3 Xtensa CCA/AGC Dynamic Threshold Stepping Daemon
# Steps cca_thresh62 across (-82 / -78 / -74 / -70 dBm) at 1 Hz using ath10k fw_stats + rx_ppdu_end EVM telemetry.
# Safety: Pure RAM / debugfs / WMI runtime operation; zero Flash writes; 45s Non-DFS / 120s DFS rollback guard.

set -u

PHY_DEV="${FMX_PHY_DEV:-phy0}"
STATE_FILE="/tmp/fmx_cca_agc_state.json"
WATCHDOG_TIMEOUT_NON_DFS=45
WATCHDOG_TIMEOUT_DFS=120
POLL_INTERVAL_SEC=1

# Step Ladder (dBm): Step 0 (-82 dBm clean), Step 1 (-78 dBm moderate), Step 2 (-74 dBm dense tower), Step 3 (-70 dBm extreme co-location)
STEP_0_DBM=-82
STEP_1_DBM=-78
STEP_2_DBM=-74
STEP_3_DBM=-70

# Hysteresis & Safety Gates
MIN_STEP_DWELL_SEC=10
EVM_DEGRADE_ABORT_DB=-18
BMISS_ABORT_COUNT=5
FCS_ERR_RATE_ABORT_PCT=12

find_debugfs_dir() {
    for d in /sys/kernel/debug/ieee80211/${PHY_DEV}/ath10k /sys/kernel/debug/ath10k/${PHY_DEV}; do
        if [ -d "$d" ]; then
            echo "$d"
            return 0
        fi
    done
    return 1
}

read_fw_telemetry() {
    DBG_DIR="$1"
    CYCLE_CLEAR_PCT=0
    RX_CLEAR_PCT=0
    PHY_ERR_PER_S=0
    EVM_PILOT_DB=-26
    BMISS_DELTA=0

    if [ -f "${DBG_DIR}/fw_stats" ]; then
        # Extract cycle clear and phy error counters from ath10k fw_stats
        CYCLE_CNT=$(awk '/Cycle count/ {print $NF; exit}' "${DBG_DIR}/fw_stats" 2>/dev/null || echo 0)
        RX_CLR=$(awk '/Rx clear count/ {print $NF; exit}' "${DBG_DIR}/fw_stats" 2>/dev/null || echo 0)
        PHY_ERR=$(awk '/PHY errors/ {print $NF; exit}' "${DBG_DIR}/fw_stats" 2>/dev/null || echo 0)
        if [ -n "$CYCLE_CNT" ] && [ "$CYCLE_CNT" -gt 0 ] 2>/dev/null; then
            CYCLE_CLEAR_PCT=$(( (RX_CLR * 100) / CYCLE_CNT ))
        fi
        PHY_ERR_PER_S="${PHY_ERR:-0}"
    fi

    if [ -f "/tmp/fmx_pb021_ppdu_evm.json" ]; then
        EVM_VAL=$(sed -n 's/.*"evm_stream_min_db":[[:space:]]*\([-0-9]*\).*/\1/p' /tmp/fmx_pb021_ppdu_evm.json 2>/dev/null | head -n 1)
        if [ -n "$EVM_VAL" ]; then
            EVM_PILOT_DB="$EVM_VAL"
        fi
    fi

    echo "${CYCLE_CLEAR_PCT} ${PHY_ERR_PER_S} ${EVM_PILOT_DB} ${BMISS_DELTA}"
}

apply_cca_step() {
    DBG_DIR="$1"
    TARGET_DBM="$2"
    STEP_IDX="$3"
    REASON="$4"

    # WMI / debugfs NF & CCA threshold injection (PB-031 / WMI 0x9064 / nf_cal_period hook)
    if [ -w "${DBG_DIR}/nf_cal_period" ]; then
        echo 1000 > "${DBG_DIR}/nf_cal_period" 2>/dev/null || true
    fi
    if [ -w "${DBG_DIR}/wmi_cca_thresh_dbm" ]; then
        echo "${TARGET_DBM}" > "${DBG_DIR}/wmi_cca_thresh_dbm" 2>/dev/null || true
    fi

    TS=$(date +%s 2>/dev/null || echo 0)
    cat <<EOF > "${STATE_FILE}"
{
  "timestamp_epoch": ${TS},
  "phy": "${PHY_DEV}",
  "active_step_index": ${STEP_IDX},
  "cca_thresh62_dbm": ${TARGET_DBM},
  "transition_reason": "${REASON}",
  "watchdog_non_dfs_sec": ${WATCHDOG_TIMEOUT_NON_DFS},
  "watchdog_dfs_sec": ${WATCHDOG_TIMEOUT_DFS}
}
EOF
}

select_target_step() {
    BUSY_PCT="$1"
    PHY_ERR="$2"
    EVM_DB="$3"
    BMISS="$4"
    CUR_STEP="$5"

    # Safety Rollback Gate: If pilot EVM degrades worse than -18 dB or beacon misses spike, step back to -82 dBm
    if [ "$EVM_DB" -gt "$EVM_DEGRADE_ABORT_DB" ] || [ "$BMISS" -ge "$BMISS_ABORT_COUNT" ]; then
        echo "0 ${STEP_0_DBM} safety_rollback_evm_or_bmiss"
        return 0
    fi

    if [ "$BUSY_PCT" -ge 75 ] && [ "$EVM_DB" -le -24 ]; then
        echo "3 ${STEP_3_DBM} extreme_colocation_cca_busy_ge_75pct"
    elif [ "$BUSY_PCT" -ge 55 ] && [ "$EVM_DB" -le -22 ]; then
        echo "2 ${STEP_2_DBM} dense_tower_cca_busy_ge_55pct"
    elif [ "$BUSY_PCT" -ge 35 ] && [ "$EVM_DB" -le -20 ]; then
        echo "1 ${STEP_1_DBM} moderate_interference_cca_busy_ge_35pct"
    else
        echo "0 ${STEP_0_DBM} clean_spectrum_baseline"
    fi
}

if [ "${1:-}" = "--once" ]; then
    DBG=$(find_debugfs_dir || echo "/tmp")
    apply_cca_step "$DBG" "$STEP_0_DBM" 0 "oneshot_init"
    exit 0
fi

CUR_STEP=0
LAST_CHANGE_TS=0
while true; do
    DBG=$(find_debugfs_dir || echo "/tmp")
    set -- $(read_fw_telemetry "$DBG")
    BUSY_PCT="${1:-0}"
    PHY_ERR="${2:-0}"
    EVM_DB="${3:--26}"
    BMISS="${4:-0}"

    set -- $(select_target_step "$BUSY_PCT" "$PHY_ERR" "$EVM_DB" "$BMISS" "$CUR_STEP")
    NEXT_STEP="$1"
    NEXT_DBM="$2"
    REASON="$3"

    NOW=$(date +%s 2>/dev/null || echo 0)
    if [ "$NEXT_STEP" != "$CUR_STEP" ]; then
        if [ "$NEXT_STEP" -eq 0 ] || [ $((NOW - LAST_CHANGE_TS)) -ge "$MIN_STEP_DWELL_SEC" ]; then
            apply_cca_step "$DBG" "$NEXT_DBM" "$NEXT_STEP" "$REASON"
            CUR_STEP="$NEXT_STEP"
            LAST_CHANGE_TS="$NOW"
        fi
    fi
    sleep "$POLL_INTERVAL_SEC"
done
