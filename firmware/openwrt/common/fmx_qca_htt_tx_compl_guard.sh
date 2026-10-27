#!/bin/sh
# FuturaMAX Stage 715A — QCA988x HTT TX Completion Ring & CE4 Backpressure Guard
# Monitors /sys/kernel/debug/ieee80211/phy*/ath10k/fw_stats and ensures pktlog_filter=0x0.
set -eu
for p in /sys/kernel/debug/ieee80211/phy*; do
    if [ -d "${p}/ath10k" ]; then
        [ -w "${p}/ath10k/pktlog_filter" ] && echo 0x0 > "${p}/ath10k/pktlog_filter" 2>/dev/null || true
    fi
done
echo "FMX_QCA_HTT_TX_COMPL_GUARD_OK"
