#!/bin/bash
# FuturaMAX FMX-0011 exit checks — run INSIDE WSL after a successful build.
# PASS criteria: images for every selected profile; kernel CONFIG_RELAY=y; ath10k-ct built with
# CONFIG_ATH10K_SPECTRAL=y and spectral symbols present in ath10k_core.ko; CT firmware = lede.022;
# mac80211 debugfs on. Prints PASS/FAIL per check and a final verdict.
cd ~/futuramax/openwrt-24.10.4 || exit 97
B=bin/targets/ath79/generic
T=build_dir/target-mips_24kc_musl
L=$(ls -d "$T"/linux-ath79_generic 2>/dev/null | head -1)
fail=0
ok()   { echo "PASS  $1"; }
bad()  { echo "FAIL  $1"; fail=1; }

echo "== 1. images =="
for p in ubnt_lap-120 ubnt_litebeam-ac-gen2 ubnt_nanostation-ac ubnt_nanostation-ac-loco; do
  for k in factory sysupgrade; do
    f=$(ls "$B"/openwrt-*ath79-generic-"${p}"-squashfs-"${k}".bin 2>/dev/null | head -1)
    if [ -n "$f" ] && [ -s "$f" ]; then ok "$(stat -c '%s' "$f") B  $(basename "$f")"; else bad "missing $f"; fi
  done
done

echo "== 2. kernel config =="
K=$(ls -d "$L"/linux-6.6.* 2>/dev/null | head -1)
echo "kernel tree: $K"
if grep -q '^CONFIG_RELAY=y' "$K/.config" 2>/dev/null; then ok "CONFIG_RELAY=y"; else bad "CONFIG_RELAY not set"; fi
if grep -q '^CONFIG_DEBUG_FS=y' "$K/.config" 2>/dev/null; then ok "CONFIG_DEBUG_FS=y"; else bad "CONFIG_DEBUG_FS not set"; fi
echo "kernel version: $(grep -m1 -o 'Linux/mips 6\.6\.[0-9]*' "$K/.config" || grep -m1 'Kernel Configuration' "$K/.config")"

echo "== 3. ath10k-ct spectral =="
C=$(ls -d "$L"/ath10k-ct-* 2>/dev/null | head -1)
echo "ath10k-ct tree: $C"
if grep -q 'CONFIG_ATH10K_SPECTRAL=y' package/kernel/ath10k-ct/Makefile && grep -q "^CONFIG_PACKAGE_ATH_SPECTRAL=y" .config; then ok "PACKAGE_ATH_SPECTRAL=y -> ath10k-ct Makefile passes CONFIG_ATH10K_SPECTRAL=y"; else bad "PACKAGE_ATH_SPECTRAL not wired into ath10k-ct"; fi
M=$(find "$L" -name ath10k_core.ko 2>/dev/null | head -1)
echo "module: $M"
n=$(strings "$M" 2>/dev/null | grep -ci 'spectral')
if [ "${n:-0}" -ge 3 ]; then ok "ath10k_core.ko has $n spectral strings"; strings "$M" | grep -i spectral | head -6 | sed 's/^/      /'; else bad "ath10k_core.ko has only ${n:-0} spectral strings"; fi
if readelf -sW "$M" 2>/dev/null | grep -q " ath10k_spectral_process_fft$" && readelf -sW "$M" | grep -q " UND relay_open$"; then ok "readelf: ath10k_spectral_process_fft defined, relay_open imported (spectral.c compiled in)"; else bad "spectral.c symbols absent from ath10k_core.ko"; fi

echo "== 4. CT firmware version shipped =="
FW=$(find "$T"/root-ath79/lib/firmware/ath10k/QCA988X/hw2.0 -maxdepth 1 -name 'firmware-2*' 2>/dev/null | head -3)
echo "$FW"
FWB="$T/root-ath79/lib/firmware/ath10k/QCA988X/hw2.0/firmware-2.bin"
if [ -s "$FWB" ] && strings "$FWB" | grep -q '10.1-ct-8x-__fW-022-ecad3248'; then ok "firmware-2.bin embeds 10.1-ct-8x-__fW-022-ecad3248 (FW022, same string the device reports)"; else bad "firmware-2.bin missing or not FW022 (10.1-ct-8x-__fW-022-ecad3248)"; fi
sha256sum "$FWB" 2>/dev/null | cut -c1-64 | sed 's/^/      sha256: /'
grep -o 'firmware-2-ct-full-community-22.bin.lede.022' package/firmware/ath10k-ct-firmware/Makefile | head -1 | sed 's/^/      Makefile pin: /'

echo "== 5. mac80211 debugfs =="
MM=$(find "$L" -name mac80211.ko 2>/dev/null | head -1)
d=$(strings "$MM" 2>/dev/null | grep -c 'debugfs')
if [ "${d:-0}" -ge 5 ]; then ok "mac80211.ko debugfs strings: $d"; else bad "mac80211.ko debugfs strings: ${d:-0}"; fi

echo "== 6. manifest / profiles =="
ls "$B"/*.manifest 2>/dev/null | sed 's/^/      /'
grep -h -E '^(kmod-ath10k-ct|ath10k-firmware-qca988x-ct|iperf3|tcpdump-mini|iw-full|ethtool|kmod-relay|kernel) ' "$B"/*.manifest 2>/dev/null | sed 's/^/      /'; cat "$B"/version.buildinfo 2>/dev/null | sed 's/^/      revision: /'

echo
if [ "$fail" -eq 0 ]; then echo "VERDICT: PASS"; else echo "VERDICT: FAIL"; fi
exit "$fail"
