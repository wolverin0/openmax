#!/bin/bash
# Copy a finished OpenWrt build's outputs into the repo (runs INSIDE WSL).
# Usage: bash copy-artifacts.sh <dest-dir-name>   e.g. futuramax-r28959-spectral
set -u
NAME="${1:?dest dir name}"
BR="$HOME/futuramax/openwrt-24.10.4"
REPO="/mnt/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX"
D="$REPO/firmware/openwrt/$NAME"
B="$BR/bin/targets/ath79/generic"
mkdir -p "$D"
cp "$B"/*.bin "$B"/sha256sums "$B"/*.manifest "$B"/profiles.json "$B"/*.buildinfo "$D"/
cp "$BR/.config" "$D/dot.config"
cp "$BR/futuramax.diffconfig" "$D/futuramax.diffconfig"
cp "$BR/logs/futuramax-build.log" "$D/build.log"
echo "copied $(ls "$D" | wc -l) files to $D"
echo "== CT firmware identity =="
sha256sum "$BR/build_dir/target-mips_24kc_musl/root-ath79/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin"
ls "$BR"/dl | grep -i "ath10k\|ct-firm" | head
for t in "$BR"/dl/ath10k-ct-firmware*; do
  [ -f "$t" ] || continue
  echo "tarball: $(basename "$t")"
  tar tzf "$t" 2>/dev/null | grep "community-22.bin.lede.022" | head -3
  tar xzOf "$t" --wildcards "*firmware-2-ct-full-community-22.bin.lede.022" 2>/dev/null | sha256sum | sed 's/^/  sha256 of lede.022 inside tarball: /'
done
echo "== sizes =="
ls -l "$D"/*.bin | awk '{print $5, $9}' | sed 's#.*/##'
