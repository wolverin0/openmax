#!/bin/sh
# =============================================================================
# openMAX — OpenWrt 24.10.4 (Linux 6.6.x) PtP & PtMP Champion Kit (Wave 338)
# Compatible with: Ubiquiti airMAX AC WA / XC boards running OpenWrt 24.10.x
#   - PowerBeam 5AC Gen2 (ubnt,powerbeam-5ac-gen2)
#   - LiteBeam 5AC Gen2  (ubnt,litebeam-ac-gen2)
#   - NanoStation 5AC Loco (ubnt,nanostation-ac-loco)
#   - LiteAP 120 / GPS   (ubnt,lap-120)
#   - Rocket 5AC Lite / Prism Gen2
#
# Includes the Wave 338 per-key sysctl loop fix (0 differs on live read-back)
# so missing kernel keys (e.g. netdev_budget_usecs on non-tickless kernels)
# never abort subsequent CoTSQ (tcp_limit_output_bytes=65536) writes.
#
# Usage:
#   sh openwrt24_ptp_ptmp_champion.sh --dry-run [--role ptp|ptmp-ap|ptmp-cpe]
#   sh openwrt24_ptp_ptmp_champion.sh --apply-ram [--role ptp|ptmp-ap|ptmp-cpe]
#   sh openwrt24_ptp_ptmp_champion.sh --persist [--role ptp|ptmp-ap|ptmp-cpe]
#   sh openwrt24_ptp_ptmp_champion.sh --verify
#   sh openwrt24_ptp_ptmp_champion.sh --rollback
# =============================================================================
set -u

MODE="--dry-run"
ROLE="ptmp-cpe"
PHY="phy0"

while [ "$#" -gt 0 ]; do
    case "$1" in
        --dry-run|--apply-ram|--persist|--verify|--rollback)
            MODE="$1"; shift ;;
        --role)
            ROLE="${2:-ptmp-cpe}"; shift 2 ;;
        --phy)
            PHY="${2:-phy0}"; shift 2 ;;
        *)
            echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

case "$ROLE" in
    ptp)
        FQ_QUANTUM=1514
        FQ_LIMIT=1024
        FQ_MEM=4194304
        BQL_MIN=4542
        BQL_MAX=8192
        BQL_HOLD=800
        ;;
    ptmp-ap)
        FQ_QUANTUM=4542
        FQ_LIMIT=2048
        FQ_MEM=4194304
        BQL_MIN=4542
        BQL_MAX=36288
        BQL_HOLD=600
        ;;
    ptmp-cpe|*)
        FQ_QUANTUM=1514
        FQ_LIMIT=1024
        FQ_MEM=4194304
        BQL_MIN=4542
        BQL_MAX=42392
        BQL_HOLD=800
        ;;
esac

SYSCTL_KEYS="vm.min_free_kbytes=4096 net.core.gro_normal_batch=16 net.core.dev_weight_tx_bias=2 net.core.netdev_budget=600 net.core.dev_weight=48 net.core.netdev_max_backlog=2048 net.ipv4.tcp_notsent_lowat=8192 net.ipv4.tcp_limit_output_bytes=65536 net.ipv4.tcp_pacing_ca_ratio=110 net.ipv4.tcp_pacing_ss_ratio=150"

print_plan() {
    cat <<EOF
=== openMAX OpenWrt 24.10.4 Champion Plan (role=${ROLE}, phy=${PHY}) ===
  1. OOM Protection (64 MB RAM): wpa_supplicant/hostapd oom_score_adj = -900, vm.min_free_kbytes = 4096
  2. mac80211 FQ-CoDel: fq_memory_limit=${FQ_MEM} (4 MiB vs 16 MiB default), fq_quantum=${FQ_QUANTUM}, fq_limit=${FQ_LIMIT}
  3. Airtime Queue Limits (AQL): VO=300/600, VI=1000/2000, BE=1500/3000, BK=500/1000 us; aql_threshold=5000
  4. ath10k Datapath: htt_max_amsdu_ampdu="2 64", pktlog_filter=0x0, nf_cal_period=120, ani_enable=1
  5. Ethernet BQL (eth0): limit_min=${BQL_MIN}, limit_max=${BQL_MAX}, hold_time=${BQL_HOLD} ms
  6. Per-key sysctl (Wave 338 safe loop): ${SYSCTL_KEYS}
EOF
}

apply_runtime() {
    # 1. Protect wireless control-plane daemons from 64 MB OOM killer
    for p in $(pidof wpa_supplicant hostapd 2>/dev/null); do
        [ -w "/proc/$p/oom_score_adj" ] && echo -900 > "/proc/$p/oom_score_adj" 2>/dev/null || true
    done

    # 2. mac80211 FQ-CoDel (cap at 4 MiB on 64 MB radios)
    DBG="/sys/kernel/debug/ieee80211/${PHY}"
    if [ -w "$DBG/aqm" ]; then
        echo "fq_memory_limit ${FQ_MEM}" > "$DBG/aqm" 2>/dev/null || true
        echo "fq_quantum ${FQ_QUANTUM}" > "$DBG/aqm" 2>/dev/null || true
        echo "fq_limit ${FQ_LIMIT}" > "$DBG/aqm" 2>/dev/null || true
    fi
    [ -w "$DBG/aqm/fq_memory_limit" ] && echo "$FQ_MEM" > "$DBG/aqm/fq_memory_limit" 2>/dev/null || true
    [ -w "$DBG/aqm/fq_quantum" ] && echo "$FQ_QUANTUM" > "$DBG/aqm/fq_quantum" 2>/dev/null || true
    [ -w "$DBG/aqm/fq_limit" ] && echo "$FQ_LIMIT" > "$DBG/aqm/fq_limit" 2>/dev/null || true

    # 3. Per-AC AQL airtime limits & threshold
    if [ -w "$DBG/aql_txq_limit" ]; then
        echo "0 300 600" > "$DBG/aql_txq_limit" 2>/dev/null || true
        echo "1 1000 2000" > "$DBG/aql_txq_limit" 2>/dev/null || true
        echo "2 1500 3000" > "$DBG/aql_txq_limit" 2>/dev/null || true
        echo "3 500 1000" > "$DBG/aql_txq_limit" 2>/dev/null || true
    fi
    [ -w "$DBG/aql_threshold" ] && echo 5000 > "$DBG/aql_threshold" 2>/dev/null || true

    # 4. ath10k QCA988x driver parameters
    [ -w "$DBG/ath10k/htt_max_amsdu_ampdu" ] && echo "2 64" > "$DBG/ath10k/htt_max_amsdu_ampdu" 2>/dev/null || true
    [ -w "$DBG/ath10k/nf_cal_period" ] && echo 120 > "$DBG/ath10k/nf_cal_period" 2>/dev/null || true
    [ -w "$DBG/ath10k/pktlog_filter" ] && echo 0x0 > "$DBG/ath10k/htt_pktlog_filter" 2>/dev/null || true
    [ -w "$DBG/ath10k/pktlog_filter" ] && echo 0x0 > "$DBG/ath10k/pktlog_filter" 2>/dev/null || true
    [ -w "$DBG/ath10k/ani_enable" ] && echo 1 > "$DBG/ath10k/ani_enable" 2>/dev/null || true

    # 5. Ethernet Byte Queue Limits (BQL)
    BQL_DIR="/sys/class/net/eth0/queues/tx-0/byte_queue_limits"
    if [ -d "$BQL_DIR" ]; then
        echo "$BQL_MAX" > "$BQL_DIR/limit_max" 2>/dev/null || true
        echo "$BQL_MIN" > "$BQL_DIR/limit_min" 2>/dev/null || true
        echo "$BQL_HOLD" > "$BQL_DIR/hold_time" 2>/dev/null || true
    fi

    [ -w /sys/class/net/eth0/tx_queue_len ] && echo 1000 > /sys/class/net/eth0/tx_queue_len 2>/dev/null || true
    for q in /sys/class/net/br-*/tx_queue_len /sys/class/net/phy0-*/tx_queue_len; do
        [ -w "$q" ] && echo 256 > "$q" 2>/dev/null || true
    done

    # 6. Per-key sysctl loop (Wave 338 fix: isolated per-key execution)
    for kv in $SYSCTL_KEYS; do
        sysctl -w "$kv" >/dev/null 2>&1 || true
    done

    echo "[openMAX OpenWrt 24.10] Applied Champion profile (role=${ROLE}, phy=${PHY})."
}

verify_runtime() {
    DBG="/sys/kernel/debug/ieee80211/${PHY}"
    BQL_DIR="/sys/class/net/eth0/queues/tx-0/byte_queue_limits"
    echo "=== openMAX OpenWrt 24.10 Live Read-Back (${PHY}) ==="
    [ -r "$DBG/aqm" ] && grep -E 'fq_memory_limit|fq_quantum|fq_limit|fq_overmemory' "$DBG/aqm" 2>/dev/null || true
    [ -r "$DBG/aql_threshold" ] && echo "aql_threshold: $(cat "$DBG/aql_threshold")"
    [ -r "$DBG/aql_txq_limit" ] && cat "$DBG/aql_txq_limit"
    [ -d "$BQL_DIR" ] && echo "eth0 BQL min/max/hold: $(cat "$BQL_DIR/limit_min" 2>/dev/null)/$(cat "$BQL_DIR/limit_max" 2>/dev/null)/$(cat "$BQL_DIR/hold_time" 2>/dev/null)"
    for k in vm.min_free_kbytes net.core.netdev_budget net.core.netdev_max_backlog net.ipv4.tcp_limit_output_bytes net.ipv4.tcp_notsent_lowat; do
        echo "$k = $(sysctl -n "$k" 2>/dev/null || echo unknown)"
    done
}

persist_flash() {
    apply_runtime
    cp "$0" /usr/sbin/openmax_openwrt_champion.sh
    chmod 0755 /usr/sbin/openmax_openwrt_champion.sh
    mkdir -p /etc/hotplug.d/net
    cat > /etc/hotplug.d/net/99-openmax-champion <<EOF
#!/bin/sh
/usr/sbin/openmax_openwrt_champion.sh --apply-ram --role ${ROLE} --phy ${PHY} >/dev/null 2>&1
EOF
    chmod 0755 /etc/hotplug.d/net/99-openmax-champion
    if [ -f /etc/rc.local ] && ! grep -q "openmax_openwrt_champion.sh" /etc/rc.local 2>/dev/null; then
        sed -i "/^exit 0/i /usr/sbin/openmax_openwrt_champion.sh --apply-ram --role ${ROLE} --phy ${PHY} >/dev/null 2>&1" /etc/rc.local 2>/dev/null || true
    fi
    echo "[openMAX OpenWrt 24.10] Persisted to /usr/sbin/openmax_openwrt_champion.sh and /etc/hotplug.d/net/99-openmax-champion."
}

rollback_defaults() {
    DBG="/sys/kernel/debug/ieee80211/${PHY}"
    if [ -w "$DBG/aqm" ]; then
        echo "fq_memory_limit 4194304" > "$DBG/aqm" 2>/dev/null || true
        echo "fq_quantum 300" > "$DBG/aqm" 2>/dev/null || true
        echo "fq_limit 8192" > "$DBG/aqm" 2>/dev/null || true
    fi
    if [ -w "$DBG/aql_txq_limit" ]; then
        for ac in 0 1 2 3; do
            echo "$ac 5000 12000" > "$DBG/aql_txq_limit" 2>/dev/null || true
        done
    fi
    [ -w "$DBG/aql_threshold" ] && echo 24000 > "$DBG/aql_threshold" 2>/dev/null || true
    sysctl -w net.ipv4.tcp_limit_output_bytes=1048576 >/dev/null 2>&1 || true
    rm -f /etc/hotplug.d/net/99-openmax-champion /usr/sbin/openmax_openwrt_champion.sh
    [ -f /etc/rc.local ] && sed -i '/openmax_openwrt_champion.sh/d' /etc/rc.local 2>/dev/null || true
    echo "[openMAX OpenWrt 24.10] Rolled back to OpenWrt defaults (kept 4 MiB fq_memory_limit safety cap)."
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
        rollback_defaults
        verify_runtime
        ;;
esac
exit 0
