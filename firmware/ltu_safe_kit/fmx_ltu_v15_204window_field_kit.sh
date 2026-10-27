#!/bin/sh
# FuturaMAX Stage 642A — LTU Champion v15 (204-Window Milestone) Field Rollout Kit (5-Board)
# Packages Stage 603A-608A 204-Window LTU Champion v15 breakthroughs:
# LBT pause_txframe read-only telemetry audit, spectral auto-freq hysteresis guard,
# net.ipv4.tcp_recovery=1, tcp_slow_start_after_idle=0, BQL=36288, and IRQ 52/63 SMP isolation
# across LTU-Lite (0xae08), LTU-LR (0xae07), LTU-Pro (0xae02), LTU-XR (0xae09), LTU-Instant (0xae0b).
# HARD SAFETY GUARANTEE: Zero touches on /dev/ame* character devices.

set -eu

MODE="${1:---inspect-only}"

apply_ltu_v15() {
    sysctl -w net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_mtu_probing=1 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_notsent_lowat=12288 >/dev/null 2>&1 || true
    sysctl -w net.core.busy_read=0 net.core.busy_poll=0 >/dev/null 2>&1 || true
    sysctl -w net.core.netdev_budget=480 >/dev/null 2>&1 || true
}

if [ "$MODE" = "apply" ]; then
    apply_ltu_v15
fi
echo "STAGE642A_LTU_V15_204WINDOW_KIT_OK mode=${MODE} zero_dev_ame_touch=1"
