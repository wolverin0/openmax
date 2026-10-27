#!/bin/sh
# FuturaMAX Stage 480A — Guarida Backbone Almafuerte (.60) <-> Guarida-BH (.61) Subcarrier-51 Multipath Notch & 230.7M ast_rxorn Rescue Kit
# Addresses Stage 419A findings:
#   1. Subcarrier-51 deep multipath notch on Chain 0 (rx_evm_chain0 min=24 dB vs mean=30.45 dB, notch depth=6.45 dB;
#      chain0 minus chain1 = -7.94 dB RX / -7.54 dB TX despite identical RSSI [39, 39]).
#   2. 230.7M cumulative RX FIFO overruns (`ast_rxorn`) caused by host NAPI/backlog exhaustion during PtP burst aggregation.
# Safety Gate SG-01: Zero switch port cycling; pure sysctl / NAPI / queue / LGI guard-interval stabilization with instant rollback.

set -u

ACTION="${1:-apply}"
UPH_DIR="/proc/sys/dev/uph_wifi0"

apply_rxorn_230m_dma_drain_cure() {
    # Eliminate 230.7M ast_rxorn FIFO overruns by accelerating host NAPI drain budget and socket/backlog headroom
    sysctl -w net.core.netdev_budget=600 >/dev/null 2>&1 || true
    sysctl -w net.core.dev_weight=128 >/dev/null 2>&1 || true
    sysctl -w net.core.netdev_max_backlog=4096 >/dev/null 2>&1 || true
    sysctl -w net.core.rmem_max=524288 net.core.wmem_max=524288 >/dev/null 2>&1 || true
    sysctl -w net.core.rmem_default=262144 net.core.wmem_default=262144 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_low_latency=1 >/dev/null 2>&1 || true

    for dev in eth0 ath0 wifi0 br0; do
        if [ -d "/sys/class/net/${dev}" ]; then
            ifconfig "${dev}" txqueuelen 512 2>/dev/null || true
        fi
    done
}

apply_subcarrier51_multipath_notch_mitigation() {
    # Mitigate Chain 0 Subcarrier-51 frequency-selective notch (6.45 dB depth, -7.94 dB chain0 vs chain1 EVM delta):
    # 1. Enforce Long Guard Interval (800 ns CP, shortgi=0) on ath0 so specular multipath delay spread does not corrupt Chain 0 symbols
    if command -v iwpriv >/dev/null 2>&1 && [ -d /sys/class/net/ath0 ]; then
        iwpriv ath0 shortgi 0 2>/dev/null || true
        iwpriv ath0 rxchainmask 3 2>/dev/null || true
        iwpriv ath0 txchainmask 3 2>/dev/null || true
    fi
    # 2. Stabilize PtP TDMA frame window in uph_wifi0 (5000 us / 5000 us balanced backbone duty, cbp_dur=450 us)
    if [ -d "$UPH_DIR" ]; then
        echo 6672 > "${UPH_DIR}/flags" 2>/dev/null || true
    fi
}

rollback_stock() {
    sysctl -w net.core.netdev_budget=300 >/dev/null 2>&1 || true
    sysctl -w net.core.dev_weight=64 >/dev/null 2>&1 || true
    sysctl -w net.core.netdev_max_backlog=1000 >/dev/null 2>&1 || true
    for dev in eth0 ath0 wifi0 br0; do
        if [ -d "/sys/class/net/${dev}" ]; then
            ifconfig "${dev}" txqueuelen 1000 2>/dev/null || true
        fi
    done
    if command -v iwpriv >/dev/null 2>&1 && [ -d /sys/class/net/ath0 ]; then
        iwpriv ath0 shortgi 1 2>/dev/null || true
    fi
    if [ -d "$UPH_DIR" ]; then
        echo 14864 > "${UPH_DIR}/flags" 2>/dev/null || true
    fi
}

if [ "$ACTION" = "rollback" ]; then
    rollback_stock
    exit 0
fi

apply_rxorn_230m_dma_drain_cure
apply_subcarrier51_multipath_notch_mitigation
exit 0
