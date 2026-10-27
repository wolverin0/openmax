#!/bin/sh
# Stage 349A — Closed-Loop Asymmetric Chain-Mask Rescue Daemon (SIMO-TX / 2x2-MRC-RX)
# Monitors per-chain RSSI (chain0 vs chain1) every 2s and automatically clamps TX to
# 1 spatial stream (VHT-NSS 1 with CDD via `iw dev <if> set bitrates vht-mcs-5 1:0-9`
# on OpenWrt or `iwpriv ath0 txchainmask` on airOS) while preserving 2x2 MRC on RX
# (`rx_ant=3`) whenever |chain0 - chain1| >= 6 dB with large-frame (> 500 B) loss.
# Hysteresis recovery restores 2x2 (`vht-mcs-5 1:0-9 2:0-9`) when |chain0 - chain1| < 3 dB.

set -u

IFACE="${1:-wlan0}"
PHY="${2:-phy0}"
POLL_SEC=2
TRIGGER_DB=6
RECOVERY_DB=3
MIN_LARGE_FRAME_BYTES=500
STATE="MIMO_2X2_VHT_NSS2"
IMBALANCE_STREAK=0
HEALTHY_STREAK=0
STATE_FILE="/tmp/fmx_chain_rescue_state.json"

log_event() {
    logger -t "fmx-chain-rescue" "$1"
    echo "[fmx-chain-rescue] $1"
}

apply_simo_tx_2x2_mrc_rx() {
    if command -v iw >/dev/null 2>&1; then
        iw phy "$PHY" set antenna 3 3 2>/dev/null || true
        iw dev "$IFACE" set bitrates vht-mcs-5 1:0-9 2>/dev/null || true
    elif command -v iwpriv >/dev/null 2>&1; then
        iwpriv "$IFACE" rxchainmask 3 2>/dev/null || true
        iwpriv "$IFACE" txchainmask 1 2>/dev/null || true
    fi
    STATE="SIMO_TX_2X2_MRC_RX"
    log_event "RESCUE ACTIVE: Clamped $IFACE to VHT-NSS 1 (vht-mcs-5 1:0-9) with 2x2 MRC RX (rx_ant=3)"
}

restore_mimo_2x2() {
    if command -v iw >/dev/null 2>&1; then
        iw phy "$PHY" set antenna 3 3 2>/dev/null || true
        iw dev "$IFACE" set bitrates vht-mcs-5 1:0-9 2:0-9 2>/dev/null || true
    elif command -v iwpriv >/dev/null 2>&1; then
        iwpriv "$IFACE" rxchainmask 3 2>/dev/null || true
        iwpriv "$IFACE" txchainmask 3 2>/dev/null || true
    fi
    STATE="MIMO_2X2_VHT_NSS2"
    log_event "HYSTERESIS RECOVERY: Restored $IFACE to full 2x2 MIMO (vht-mcs-5 1:0-9 2:0-9)"
}

if [ "${3:-}" = "--once-status" ]; then
    echo "{\"iface\":\"$IFACE\",\"phy\":\"$PHY\",\"state\":\"$STATE\",\"rx_ant\":3}"
    exit 0
fi

while true; do
    DUMP="$(iw dev "$IFACE" station dump 2>/dev/null || true)"
    if [ -n "$DUMP" ]; then
        CHAINS="$(echo "$DUMP" | awk '/signal avg:/ { gsub(/\[|\]|,/, " "); print $3, $4; exit }')"
        C0="$(echo "$CHAINS" | awk '{print $1}')"
        C1="$(echo "$CHAINS" | awk '{print $2}')"
        TX_BYTES="$(echo "$DUMP" | awk '/tx bytes:/ {print $3; exit}')"
        TX_PKTS="$(echo "$DUMP" | awk '/tx packets:/ {print $3; exit}')"
        TX_RETRIES="$(echo "$DUMP" | awk '/tx retries:/ {print $3; exit}')"

        if [ -n "$C0" ] && [ -n "$C1" ]; then
            DELTA="$(awk -v a="$C0" -v b="$C1" 'BEGIN { d = a - b; if (d < 0) d = -d; printf "%d", int(d) }')"
            AVG_PKT=600
            if [ -n "$TX_BYTES" ] && [ -n "$TX_PKTS" ] && [ "$TX_PKTS" -gt 0 ] 2>/dev/null; then
                AVG_PKT=$((TX_BYTES / TX_PKTS))
            fi

            if [ "$STATE" = "MIMO_2X2_VHT_NSS2" ]; then
                if [ "$DELTA" -ge "$TRIGGER_DB" ] && [ "$AVG_PKT" -ge "$MIN_LARGE_FRAME_BYTES" ]; then
                    IMBALANCE_STREAK=$((IMBALANCE_STREAK + 1))
                    if [ "$IMBALANCE_STREAK" -ge 2 ]; then
                        apply_simo_tx_2x2_mrc_rx
                        HEALTHY_STREAK=0
                    fi
                else
                    IMBALANCE_STREAK=0
                fi
            else
                if [ "$DELTA" -lt "$RECOVERY_DB" ]; then
                    HEALTHY_STREAK=$((HEALTHY_STREAK + 1))
                    if [ "$HEALTHY_STREAK" -ge 3 ]; then
                        restore_mimo_2x2
                        IMBALANCE_STREAK=0
                    fi
                else
                    HEALTHY_STREAK=0
                fi
            fi

            printf '{"iface":"%s","state":"%s","chain0_dbm":%s,"chain1_dbm":%s,"delta_db":%s,"rx_ant":3,"tx_retries":%s}
'                 "$IFACE" "$STATE" "$C0" "$C1" "$DELTA" "${TX_RETRIES:-0}" > "$STATE_FILE"
        fi
    fi
    sleep "$POLL_SEC"
done
