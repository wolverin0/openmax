#!/bin/bash
# FuturaMAX FMX-0011 — stop any running build, install the gcc-12 shim, relaunch detached.
# Run from Windows:  wsl -- bash "/mnt/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/tools/openwrt-build/relaunch.sh"
set -u
P="/mnt/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/tools/openwrt-build"
BR="$HOME/futuramax/openwrt-24.10.4"
LABEL="${1:-attempt}"

pkill -f "build.sh" 2>/dev/null
pkill -x make 2>/dev/null
for i in 1 2 3 4 5 6 7 8 9 10; do
  if [ "$(pgrep -c -x make)" -eq 0 ] && [ "$(pgrep -c -f build.sh)" -eq 0 ]; then break; fi
  sleep 1
done
echo "running make procs: $(pgrep -c -x make)"

sed -i 's/\r//' "$P/hostcc-shim.sh" "$P/build.sh"
bash "$P/hostcc-shim.sh" || { echo "SHIM FAILED"; exit 2; }

cd "$BR" || exit 97
cp "$P/build.sh" ./build.sh && chmod +x build.sh
rm -rf build_dir/host/cmake-3.30.5
mkdir -p logs
[ -f logs/futuramax-build.log ] && mv -f logs/futuramax-build.log "logs/futuramax-build.${LABEL}.log"

nohup setsid ./build.sh > logs/futuramax-build.log 2>&1 < /dev/null &
sleep 10
echo "=== log head ==="; head -3 logs/futuramax-build.log
echo "=== staging compiler links ==="; ls -l staging_dir/host/bin/gcc staging_dir/host/bin/g++ 2>&1
echo "=== procs ==="; pgrep -fa "build.sh|make -j" | grep -v pgrep | head -3
