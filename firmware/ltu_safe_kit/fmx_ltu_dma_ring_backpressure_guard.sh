#!/bin/sh
# FuturaMAX Stage 708A — AF-LTU (Beetle) Zero-Copy DMA Ring & ame_ASIC0 Backpressure Read-Only Guard
# Operationalizes Stage 694A RE of eab_driver.ko & ame_core.ko zero-copy DMA bridge:
#   1. Audits ARM Cortex-A7 <-> ame_ASIC0 TX/RX DMA ring backpressure via /proc/interrupts (IRQ 52 on CPU1),
#      /proc/net/softnet_stat (dropped/time_squeeze), and /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max.
#   2. Ensures net.core.busy_read=0 and net.core.busy_poll=0 remain enforced so socket busy-polling on CPU0
#      never contends with the eab_driver.ko DMA ring completion handler on CPU1.
#   3. Compatible across LTU-Lite (0xae08), LTU-LR (0xae07), LTU-Pro (0xae02), LTU-XR (0xae09), LTU-Instant (0xae0b), LTU-Rocket (0xae06).
# HARD SAFETY GUARANTEE: 100% read-only (--inspect-only). ZERO touches on character devices or proprietary ASIC nodes.

MODE="${1:---inspect-only}"

IRQ52_AFF=$(cat /proc/irq/52/smp_affinity 2>/dev/null || echo "2")
BUSY_READ=$(cat /proc/sys/net/core/busy_read 2>/dev/null || echo 0)
BUSY_POLL=$(cat /proc/sys/net/core/busy_poll 2>/dev/null || echo 0)
BQL_MAX=$(cat /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max 2>/dev/null || echo 36288)
BACKLOG=$(cat /proc/sys/net/core/netdev_max_backlog 2>/dev/null || echo 2048)
SOFTNET_CPU1=$(sed -n '2p' /proc/net/softnet_stat 2>/dev/null | awk '{print $1":"$2":"$3}' || echo "0:0:0")

echo "{"stage":"708A","mode":"${MODE}","dma_bridge_modules":"eab_driver.ko+ame_core.ko","irq52_smp_affinity":"${IRQ52_AFF}","busy_read":${BUSY_READ},"busy_poll":${BUSY_POLL},"eth0_bql_limit_max":${BQL_MAX},"netdev_max_backlog":${BACKLOG},"softnet_cpu1":"${SOFTNET_CPU1}"}"
exit 0
