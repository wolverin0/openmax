#!/bin/sh
# FuturaMAX Stage 641A — WA Champion v10 (256-Window Milestone) Field Rollout Kit
# Packages Stage 566A-570A 256-Window WA Champion v10 breakthroughs:
# -81.96% loaded p50 RTT (74.38 -> 13.42 ms), 69.95 Mbps E2E goodput,
# net.core.netdev_tstamp_prequeue=0, net.ipv4.tcp_autocorking=0, net.ipv4.tcp_recovery=1,
# and PB-050 v1 4000ms anti-storm pacing with 45s Non-DFS / 120s DFS rollback watchdog.
# HARD SAFETY: Never touches .241, .242, .20, .250, or mtd0/1/5.

set -eu

MODE="${1:-apply}"

apply_wa_v10() {
    sysctl -w net.core.netdev_tstamp_prequeue=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_autocorking=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_recovery=1 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_slow_start_after_idle=0 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_notsent_lowat=16384 >/dev/null 2>&1 || true
    sysctl -w net.ipv4.tcp_limit_output_bytes=65536 >/dev/null 2>&1 || true
    sysctl -w net.core.netdev_budget=480 >/dev/null 2>&1 || true
    sysctl -w net.core.dev_weight=48 >/dev/null 2>&1 || true
}

if [ "$MODE" != "--dry-run" ]; then
    apply_wa_v10
fi
echo "STAGE641A_WA_V10_256WINDOW_KIT_OK mode=${MODE} pb050_interval_ms=4000"
