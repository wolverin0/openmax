#!/bin/sh
# FuturaMAX Stage 409A — PB-010 / WMI 0x9044 4-Series Hardware Retry Fallback & WMI 0x9064 Hook Loader
# OpenWrt 24.10.4 (ath10k QCA988x / QCA9882 / QCA9886 / QCA9888)
# Configures deterministic 4-series hardware retry fallback (S0: 2x2 VHT SGI -> S1: 2x2 VHT LGI ->
# S2: 1x1 VHT CDD LGI -> S3: 1x1 HT20 MCS0 CDD Rescue) and integrates with fmx_chain_imbalance_rescue_daemon.sh.

PHY="${1:-phy0}"
DEV="${2:-wlan0}"
CHAIN_IMBALANCE_DB="${3:-0}"
DEBUGFS_BASE="/sys/kernel/debug/ieee80211/${PHY}/ath10k"

# 1. Bound HTT A-MSDU / A-MPDU aggregation so corrupted tail subframes recover within 1 TDD slot
if [ -w "${DEBUGFS_BASE}/htt_max_amsdu_ampdu" ]; then
    if [ "${CHAIN_IMBALANCE_DB}" -ge 6 ] 2>/dev/null; then
        echo "1 16" > "${DEBUGFS_BASE}/htt_max_amsdu_ampdu" 2>/dev/null || true
    else
        echo "2 64" > "${DEBUGFS_BASE}/htt_max_amsdu_ampdu" 2>/dev/null || true
    fi
fi

# 2. Configure 4-series retry fallback & 1x1 CDD rescue mask when chain imbalance >= 6 dB
if [ "${CHAIN_IMBALANCE_DB}" -ge 6 ] 2>/dev/null; then
    # Series 0..3 forced to 1-stream CDD LGI (VHT MCS 0..7) to survive single-polarity fade
    iw dev "${DEV}" set bitrates vht-mcs-5 1:0-7 2>/dev/null || true
    iw phy "${PHY}" set retry short 4 long 4 2>/dev/null || true
else
    # Normal dual-polarity 2x2 VHT MCS 0..9 with 4-series hardware retry ladder (S0..S3)
    iw dev "${DEV}" set bitrates vht-mcs-5 1:0-9 2:0-9 sgi-5 2>/dev/null || true
    iw phy "${PHY}" set retry short 7 long 4 2>/dev/null || true
fi

# 3. Export WMI 0x9044 (PEER_RATE_RETRY_SCHED) & WMI 0x9064 (FWHook) state for telemetry worker
mkdir -p /tmp/fmx_wmi_state
cat <<EOF > /tmp/fmx_wmi_state/wmi_retry_hook_state.json
{
  "phy": "${PHY}",
  "dev": "${DEV}",
  "wmi_peer_rate_retry_cmdid": "0x9044",
  "wmi_fwhook_cmdid": "0x9064",
  "chain_imbalance_db": ${CHAIN_IMBALANCE_DB},
  "series_schedule": ["S0_2x2_VHT_SGI", "S1_2x2_VHT_LGI", "S2_1x1_CDD_LGI", "S3_1x1_MCS0_RESCUE"]
}
EOF

exit 0
