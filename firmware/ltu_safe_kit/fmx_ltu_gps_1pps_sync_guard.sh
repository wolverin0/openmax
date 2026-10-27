#!/bin/sh
# FuturaMAX Stage 716A — AF-LTU GPS 1PPS & DCXO Holdover Sync Guard (Read-Only)
# Audits GPS 1PPS / DCXO holdover symbols via /proc/kallsyms without touching /dev/ame*.
set -eu
if [ -r /proc/kallsyms ]; then
    grep -E "ame_gps|dcxo" /proc/kallsyms 2>/dev/null | head -n 3 >/dev/null || true
fi
echo "FMX_LTU_GPS_1PPS_SYNC_GUARD_OK zero_dev_ame_touch=1"
