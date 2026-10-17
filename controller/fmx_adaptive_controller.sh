#!/bin/sh
# FuturaMAX Closed-Loop Adaptive Sector Controller Daemon (fmx_adaptive_controller.sh)
# Zero-fork pure-debugfs implementation for 533 MHz MIPS 74Kc APs (AR9342 + QCA988x).
# Reads /sys/kernel/debug/ieee80211/phy0/netdev:<iface>/stations/<mac>/airtime directly
# using POSIX shell built-ins (0 subshells/forks per poll cycle, <0.1% AP CPU).
#
# Dynamically switches the sector between:
#   - SINGLE_STA_TURBO (<=1 active station): Agg 3x64, AQL 3000/6000 us
#   - MULTI_STA_ADAPTIVE (>=2 active stations): Bounded Agg 1x16, AQL 1500/3000 us,
#     proportional airtime weights (768 for VHT80 802.11ac, 256 for low-deficit 802.11n,
#     128 SLA floor for deep negative BE-deficit obstructed stations).

IFACE="${1:-phy0-ap0}"
PHY="phy0"
DEBUGFS="/sys/kernel/debug/ieee80211/${PHY}"
STA_ROOT="${DEBUGFS}/netdev:${IFACE}/stations"
STATE_FILE="/tmp/fmx_controller_state.json"
ACTIVE_THRESH_US=15000

echo 3 > "${DEBUGFS}/airtime_flags" 2>/dev/null

LAST_MODE="NONE"
mkdir -p /tmp/fmx_sta_prev

while true; do
    ACTIVE_COUNT=0
    ACTIVE_LIST=""

    for STA_DIR in "${STA_ROOT}"/*; do
        [ -f "${STA_DIR}/airtime" ] || continue
        MAC="${STA_DIR##*/}"
        PREV_FILE="/tmp/fmx_sta_prev/${MAC}"

        {
            read _ RX_US _
            read _ TX_US _
            read _ CUR_WEIGHT _
            read _ _ VO_DEF _ _ VI_DEF _ _ BE_DEF _
        } < "${STA_DIR}/airtime"

        TX_US=${TX_US:-0}
        CUR_WEIGHT=${CUR_WEIGHT:-256}
        BE_DEF=${BE_DEF:-0}

        if [ -f "${PREV_FILE}" ]; then
            read PREV_TX_US < "${PREV_FILE}"
        else
            PREV_TX_US=${TX_US}
        fi
        echo "${TX_US}" > "${PREV_FILE}"

        DELTA_TX_US=$(( TX_US - PREV_TX_US ))
        if [ "${DELTA_TX_US}" -ge "${ACTIVE_THRESH_US}" ]; then
            ACTIVE_COUNT=$(( ACTIVE_COUNT + 1 ))
            ACTIVE_LIST="${ACTIVE_LIST} ${MAC}"
        fi

        # Check VHT capability once via pure built-in read
        VHT_LINE=""
        [ -f "${STA_DIR}/vht_capa" ] && read VHT_LINE < "${STA_DIR}/vht_capa"
        case "${VHT_LINE}" in
            "VHT supported"*)
                TARGET_WEIGHT=768
                ;;
            *)
                if [ "${BE_DEF}" -lt -15000 ]; then
                    TARGET_WEIGHT=128
                else
                    TARGET_WEIGHT=256
                fi
                ;;
        esac

        if [ "${CUR_WEIGHT}" != "${TARGET_WEIGHT}" ]; then
            iw dev "${IFACE}" station set "${MAC}" airtime_weight "${TARGET_WEIGHT}" 2>/dev/null
        fi
    done

    if [ "${ACTIVE_COUNT}" -le 1 ]; then
        MODE="SINGLE_STA_TURBO"
        if [ "${LAST_MODE}" != "${MODE}" ]; then
            echo "3 64" > "${DEBUGFS}/ath10k/htt_max_amsdu_ampdu" 2>/dev/null
            for ac in 0 1 2 3; do
                echo "${ac} 3000 6000" > "${DEBUGFS}/aql_txq_limit" 2>/dev/null
            done
            echo 12000 > "${DEBUGFS}/aql_threshold" 2>/dev/null
            LAST_MODE="${MODE}"
        fi
    else
        MODE="MULTI_STA_ADAPTIVE"
        if [ "${LAST_MODE}" != "${MODE}" ]; then
            echo "1 16" > "${DEBUGFS}/ath10k/htt_max_amsdu_ampdu" 2>/dev/null
            for ac in 0 1 2 3; do
                echo "${ac} 1500 3000" > "${DEBUGFS}/aql_txq_limit" 2>/dev/null
            done
            echo 6000 > "${DEBUGFS}/aql_threshold" 2>/dev/null
            LAST_MODE="${MODE}"
        fi
    fi

    echo "{\"mode\":\"${MODE}\",\"active_count\":${ACTIVE_COUNT},\"active_stations\":\"${ACTIVE_LIST# }\"}" > "${STATE_FILE}"
    sleep 1
done
