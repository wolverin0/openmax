#!/bin/bash
# FuturaMAX FMX-0011 — run the OpenWrt build in the FOREGROUND of a long-lived wsl.exe client.
# Why: on Windows 10, WSL2 terminates the distro when the last wsl.exe client disconnects,
# killing nohup/setsid'd builds. Launch this from PowerShell so the client persists:
#   Start-Process wsl.exe -ArgumentList '-- bash -c "bash /mnt/g/_OneDrive/OneDrive/Desktop/Py\ Apps/futuraMAX/tools/openwrt-build/run-attached.sh <label>"' -WindowStyle Hidden
set -u
P="/mnt/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX/tools/openwrt-build"
BR="$HOME/futuramax/openwrt-24.10.4"
LABEL="${1:-attempt}"

pkill -f "build.sh" 2>/dev/null; pkill -x make 2>/dev/null
for i in 1 2 3 4 5 6 7 8 9 10; do
  [ "$(pgrep -c -x make)" -eq 0 ] && break; sleep 1
done

sed -i 's/\r//' "$P/hostcc-shim.sh" "$P/build.sh"
bash "$P/hostcc-shim.sh" > /dev/null || exit 2
cd "$BR" || exit 97
cp "$P/build.sh" ./build.sh && chmod +x build.sh
mkdir -p logs
[ -f logs/futuramax-build.log ] && mv -f logs/futuramax-build.log "logs/futuramax-build.${LABEL}.log"
echo "ATTACHED-RUNNER pid=$$ $(date -Is)" > logs/futuramax-build.log
./build.sh >> logs/futuramax-build.log 2>&1
rc=$?
echo "ATTACHED-RUNNER done rc=${rc} $(date -Is)" >> logs/futuramax-build.log
exit $rc
