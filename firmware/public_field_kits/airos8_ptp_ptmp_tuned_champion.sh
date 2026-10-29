#!/bin/sh
# =============================================================================
# openMAX — Stock airOS 8 (WA / XC) Tuned PtP & PtMP Champion Kit
# Compatible with: PowerBeam 5AC Gen2, LiteBeam 5AC Gen2, NanoBeam 5AC,
#                  NanoStation 5AC / Loco, LiteAP AC (LAP-120 / LAP-GPS),
#                  Rocket 5AC Lite / Prism Gen2 (airOS v8.5.12 – v8.7.25)
#
# What this tunes on Stock airOS 8 (without flashing OpenWrt):
#   1. Bounded NIC/Bridge TX queues (tx_queue_len=192 vs stock 1000) to stop
#      Ethernet-to-radio bufferbloat.
#   2. Linux NAPI softirq budget (netdev_budget=600, dev_weight=64, backlog=600)
#      for MIPS 74Kc (AR9342 535 MHz / QCA9558 720 MHz).
#   3. TCP buffer & SACK/DSACK/ECN tuning (rmem_max/wmem_max=4 MB).
#   4. A-MPDU frame bounding (ampduFrames=24, ampduLimit=50000) on wifi0/ath0
#      to prevent head-of-line blocking of VoIP/ICMP behind giant aggregates.
#   5. WMM hardware EDCA prioritization for Video (AC_VI) and Voice (AC_VO).
#   6. Datapath CPU fast-path: disables unconsumed per-PPDU packet logging
#      (rmmod ath_pktlog) and VoW extended stats (vow_extstats=0).
#
# Usage:
#   sh airos8_ptp_ptmp_tuned_champion.sh --dry-run
#   sh airos8_ptp_ptmp_tuned_champion.sh --apply-ram
#   sh airos8_ptp_ptmp_tuned_champion.sh --persist
#   sh airos8_ptp_ptmp_tuned_champion.sh --verify
#   sh airos8_ptp_ptmp_tuned_champion.sh --rollback
# =============================================================================
set -u

MODE="${1:---dry-run}"
POSTSTART="/etc/persistent/rc.poststart"
BACKUP_DIR="/tmp/openmax_airos8_backup"

print_plan() {
    cat <<'EOF'
=== openMAX Stock airOS 8 Tuned Champion Plan ===
  - Interfaces (eth0, ath0, br0): tx_queue_len = 192 (stock: 1000)
  - Kernel NAPI & Backlog: netdev_budget=600, dev_weight=64, netdev_max_backlog=600
  - TCP Stack: rmem_max=4194304, wmem_max=4194304, tcp_sack=1, tcp_dsack=1, tcp_ecn=1
  - Aggregation (VAP/Radio): ampdu=24, amsdu=2, shortgi=1
  - WMM EDCA: AC_VI (aifs=1, cwmin=2, cwmax=3), AC_VO (aifs=1, cwmin=1, cwmax=2)
  - CPU Fast-Path: vow_extstats=0, rmmod ath_pktlog (if loaded)
EOF
}

save_backup() {
    mkdir -p "$BACKUP_DIR"
    if [ ! -f "$BACKUP_DIR/saved" ]; then
        cat /sys/class/net/eth0/tx_queue_len > "$BACKUP_DIR/eth0_txq" 2>/dev/null || true
        sysctl -n net.core.netdev_budget > "$BACKUP_DIR/netdev_budget" 2>/dev/null || true
        sysctl -n net.core.dev_weight > "$BACKUP_DIR/dev_weight" 2>/dev/null || true
        sysctl -n net.core.netdev_max_backlog > "$BACKUP_DIR/netdev_max_backlog" 2>/dev/null || true
        echo 1 > "$BACKUP_DIR/saved"
    fi
}

apply_runtime() {
    save_backup
    for dev in eth0 ath0 br0; do
        [ -w "/sys/class/net/$dev/tx_queue_len" ] && echo 192 > "/sys/class/net/$dev/tx_queue_len" 2>/dev/null || true
    done

    for kv in \
        net.core.netdev_budget=600 \
        net.core.dev_weight=64 \
        net.core.netdev_max_backlog=600 \
        net.core.rmem_max=4194304 \
        net.core.wmem_max=4194304 \
        net.ipv4.tcp_sack=1 \
        net.ipv4.tcp_dsack=1 \
        net.ipv4.tcp_ecn=1
    do
        sysctl -w "$kv" >/dev/null 2>&1 || true
    done

    # Radio / VAP aggregation & WMM EDCA tuning
    iwpriv wifi0 ampduFrames 24 2>/dev/null || true
    iwpriv wifi0 ampduLimit 50000 2>/dev/null || true
    iwpriv ath0 ampdu 24 2>/dev/null || true
    iwpriv ath0 amsdu 2 2>/dev/null || true
    iwpriv ath0 shortgi 1 2>/dev/null || true
    iwpriv ath0 aifs 2 1 2 2>/dev/null || true
    iwpriv ath0 cwmin 2 1 2 2>/dev/null || true
    iwpriv ath0 cwmax 2 1 3 2>/dev/null || true
    iwpriv ath0 aifs 3 1 1 2>/dev/null || true
    iwpriv ath0 cwmin 3 1 1 2>/dev/null || true
    iwpriv ath0 cwmax 3 1 2 2>/dev/null || true

    # Kernel .ko CPU fast-path (prune unconsumed telemetry tax)
    iwpriv wifi0 vow_extstats 0 2>/dev/null || true
    lsmod 2>/dev/null | grep -q '^ath_pktlog' && rmmod ath_pktlog 2>/dev/null || true

    echo "[openMAX airOS 8] Applied runtime Tuned Champion in RAM."
}

verify_runtime() {
    echo "=== openMAX airOS 8 Live Read-Back ==="
    echo "eth0 tx_queue_len: $(cat /sys/class/net/eth0/tx_queue_len 2>/dev/null || echo unknown)"
    echo "ath0 tx_queue_len: $(cat /sys/class/net/ath0/tx_queue_len 2>/dev/null || echo unknown)"
    echo "netdev_budget:     $(sysctl -n net.core.netdev_budget 2>/dev/null || echo unknown)"
    echo "dev_weight:        $(sysctl -n net.core.dev_weight 2>/dev/null || echo unknown)"
    echo "max_backlog:       $(sysctl -n net.core.netdev_max_backlog 2>/dev/null || echo unknown)"
    echo "rmem_max:          $(sysctl -n net.core.rmem_max 2>/dev/null || echo unknown)"
    echo "ath_pktlog loaded: $(lsmod 2>/dev/null | grep -c '^ath_pktlog' || echo 0)"
}

persist_flash() {
    apply_runtime
    mkdir -p /etc/persistent
    cp "$0" /etc/persistent/openmax_airos8_champion.sh 2>/dev/null || true
    chmod 0755 /etc/persistent/openmax_airos8_champion.sh 2>/dev/null || true
    if [ ! -f "$POSTSTART" ] || ! grep -q "openmax_airos8_champion.sh" "$POSTSTART" 2>/dev/null; then
        [ -f "$POSTSTART" ] || echo "#!/bin/sh" > "$POSTSTART"
        echo "/bin/sh /etc/persistent/openmax_airos8_champion.sh --apply-ram >/dev/null 2>&1 &" >> "$POSTSTART"
        chmod 0755 "$POSTSTART"
    fi
    cfgmtd -w -p /etc/ >/dev/null 2>&1
    echo "[openMAX airOS 8] Persisted to $POSTSTART via cfgmtd -w -p /etc/."
}

rollback_stock() {
    for dev in eth0 ath0 br0; do
        [ -w "/sys/class/net/$dev/tx_queue_len" ] && echo 1000 > "/sys/class/net/$dev/tx_queue_len" 2>/dev/null || true
    done
    sysctl -w net.core.netdev_budget=300 net.core.dev_weight=64 net.core.netdev_max_backlog=300 >/dev/null 2>&1 || true
    iwpriv wifi0 ampduFrames 32 2>/dev/null || true
    iwpriv ath0 ampdu 32 2>/dev/null || true
    iwpriv ath0 amsdu 3 2>/dev/null || true
    if [ -f "$POSTSTART" ]; then
        sed -i '/openmax_airos8_champion.sh/d' "$POSTSTART" 2>/dev/null || true
    fi
    rm -f /etc/persistent/openmax_airos8_champion.sh
    echo "[openMAX airOS 8] Restored stock queue/aggregation defaults."
}

case "$MODE" in
    --dry-run)
        print_plan
        ;;
    --apply-ram)
        apply_runtime
        verify_runtime
        ;;
    --persist)
        persist_flash
        verify_runtime
        ;;
    --verify)
        verify_runtime
        ;;
    --rollback)
        rollback_stock
        verify_runtime
        ;;
    *)
        echo "Usage: $0 [--dry-run | --apply-ram | --persist | --verify | --rollback]" >&2
        exit 1
        ;;
esac
exit 0
