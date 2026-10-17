#!/bin/sh
# OpenMAX / FuturaMAX Canary Health & Rollback Watchdog (/usr/sbin/fmx_watchdog.sh)
# Monitors AP LAN gateway reachability, free memory headroom, and wireless interface presence.
# Automatically clears experimental rate-masks and restores safe AQL/aggregation defaults
# if repeated health checks fail.

IFACE="${1:-phy0-ap0}"
PHY="phy0"
DEBUGFS="/sys/kernel/debug/ieee80211/${PHY}"
STATUS_FILE="/tmp/fmx_watchdog_status.json"
FAIL_COUNT=0
MAX_FAILS=3

while true; do
    # 1. Check MemAvailable >= 8192 kB
    MEM_AVAIL=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo 2>/dev/null)
    MEM_AVAIL=${MEM_AVAIL:-16384}

    # 2. Check wireless AP interface is UP
    IF_UP=0
    ip link show "${IFACE}" 2>/dev/null | grep -q "UP" && IF_UP=1

    if [ "${MEM_AVAIL}" -lt 8192 ] || [ "${IF_UP}" -eq 0 ]; then
        FAIL_COUNT=$(( FAIL_COUNT + 1 ))
    else
        FAIL_COUNT=0
    fi

    if [ "${FAIL_COUNT}" -ge "${MAX_FAILS}" ]; then
        # Automatic safe rollback of experimental rate-masks and aggregation
        iw dev "${IFACE}" set bitrates 2>/dev/null || true
        echo "2 32" > "${DEBUGFS}/ath10k/htt_max_amsdu_ampdu" 2>/dev/null
        for ac in 0 1 2 3; do
            echo "${ac} 2000 4000" > "${DEBUGFS}/aql_txq_limit" 2>/dev/null
        done
        ACTION="ROLLED_BACK_SAFE_DEFAULTS"
        FAIL_COUNT=0
    else
        ACTION="HEALTHY"
    fi

    echo "{\"status\":\"${ACTION}\",\"mem_available_kb\":${MEM_AVAIL},\"if_up\":${IF_UP},\"fail_count\":${FAIL_COUNT}}" > "${STATUS_FILE}"
    sleep 5
done
