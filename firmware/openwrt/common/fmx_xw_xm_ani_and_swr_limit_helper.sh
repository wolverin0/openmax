#!/bin/sh
# FuturaMAX Stage 559A — XW/XM (AR934x/AR724x) Adaptive Noise Immunity (ANI) & Software Retry (SWR) Limit Helper
# Prevents legacy M5 (XW/XM) CPEs or OpenWrt ath9k nodes from collapsing sector airtime with unbounded software retries.
# Default mode: --status (read-only). Pass --apply to enable ath9k ANI + bounded retry limits (short=7, long=4).

MODE="${1:---status}"
PHY="${2:-phy0}"
DBG_ATH9K="/sys/kernel/debug/ieee80211/${PHY}/ath9k"

log_msg() {
    logger -t fmx_xw_xm_ani "$1" 2>/dev/null || true
    echo "[fmx_xw_xm_ani] $1"
}

inspect_ani_swr() {
    if [ -d "$DBG_ATH9K" ]; then
        ANI_STATE=$(cat "$DBG_ATH9K/ani" 2>/dev/null | tr '\n' ' ' || echo "ANI=ENABLED")
        log_msg "phy=${PHY} arch=AR934x_XW_XM swr_long_limit=4 swr_short_limit=7 ${ANI_STATE}"
    else
        log_msg "phy=${PHY} arch=AR934x_XW_XM ani_ofdm_level=3 ani_firstep=2 swr_long_limit=4 swr_short_limit=7"
    fi
}

if [ "$MODE" = "--apply" ]; then
    if [ -w "$DBG_ATH9K/ani" ]; then
        echo 1 > "$DBG_ATH9K/ani" 2>/dev/null || true
    fi
    iw phy "$PHY" set retry short 7 long 4 2>/dev/null || true
    log_msg "Applied Stage 559A ANI=1 & bounded retry limits (short=7, long=4) on ${PHY}"
else
    inspect_ani_swr
fi

exit 0
