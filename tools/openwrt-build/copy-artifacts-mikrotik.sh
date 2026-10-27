#!/bin/bash
# Copy the ath79/mikrotik build (SXT Lite5) into the repo and restore the generic .config. Runs INSIDE WSL.
set -u
BR="$HOME/futuramax/openwrt-24.10.4"
D="/mnt/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/firmware/openwrt/futuramax-r28959-mikrotik-sxt"
B="$BR/bin/targets/ath79/mikrotik"
mkdir -p "$D"
cp "$B"/*sxt* "$B"/sha256sums "$B"/*.manifest "$B"/*.buildinfo "$D"/
cp "$BR/.config" "$D/dot.config"
cp "$BR/futuramax-mikrotik.diffconfig" "$D/"
cp "$BR/logs/futuramax-build.log" "$D/build.log"
echo "copied $(ls "$D" | wc -l) files"
# restore the generic config so the next generic build is reproducible
cp "$BR/.config.generic-2026-10-05" "$BR/.config" && (cd "$BR" && make defconfig >/dev/null 2>&1) && grep -c "^CONFIG_TARGET_ath79_generic=y" "$BR/.config"
