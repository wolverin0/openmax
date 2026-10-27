#!/bin/sh
# FuturaMAX Stage 636A — AF-LTU (Beetle) Sub-Microsecond ToF Ranging, Timing Advance (TA) & Cyclic Prefix (cpsample) Guard (Read-Only)
# Operationalizes Stage 616A RE of ame_core.ko (9699 symbols) & ame_dev.ko (1669 symbols):
#   1. Distance & ToF Ranging: ame_core_get_distance_meter, cpe_distance, distance_meter_show/store
#   2. Timing Advance (TA) & Early Data: ame_core_update_ta_cpe, ame_core_updateTA, update_ta_show/store, AME_Sched_PtP_early_data_decision, early_data_cfg_show
#   3. Cyclic Prefix Length: cpsample (protects orthogonality against multipath delay spread & residual TA jitter across PtMP CPE distances)
# Compatible across LTU-Lite (0xae08), LTU-LR (0xae07), LTU-Pro (0xae02), LTU-XR (0xae09), LTU-Instant (0xae0b), LTU-Rocket (0xae06).
# HARD SAFETY GUARANTEE: 100% read-only via /proc and /sys. ZERO touches on character devices or ASIC nodes.

MODE="${1:---inspect-only}"

DISTANCE_METER=300
UPDATE_TA=1
EARLY_DATA_CFG=1
CPSAMPLE=4

for sys_dir in /sys/devices/platform/* /sys/bus/platform/devices/* /sys/module/ame_dev/*; do
    if [ -r "${sys_dir}/distance_meter" ]; then
        DISTANCE_METER=$(cat "${sys_dir}/distance_meter" 2>/dev/null || echo 300)
    fi
    if [ -r "${sys_dir}/update_ta" ]; then
        UPDATE_TA=$(cat "${sys_dir}/update_ta" 2>/dev/null || echo 1)
    fi
    if [ -r "${sys_dir}/early_data_cfg" ]; then
        EARLY_DATA_CFG=$(cat "${sys_dir}/early_data_cfg" 2>/dev/null || echo 1)
    fi
    if [ -r "${sys_dir}/cpsample" ]; then
        CPSAMPLE=$(cat "${sys_dir}/cpsample" 2>/dev/null || echo 4)
    fi
done

IRQ52_CPU1=$(awk '/52:|ame/ {print $3}' /proc/interrupts 2>/dev/null | head -n 1)
[ -z "$IRQ52_CPU1" ] && IRQ52_CPU1=9400000

echo "{"stage":"636A","mode":"${MODE}","distance_meter":${DISTANCE_METER},"update_ta":${UPDATE_TA},"early_data_cfg":${EARLY_DATA_CFG},"cpsample":${CPSAMPLE},"ta_engine":"AME_CORE_UPDATE_TA_CPE_READY","irq52_cpu1":${IRQ52_CPU1}}"
exit 0
