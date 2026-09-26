#!/bin/bash
# FuturaMAX build hang diagnostic — run as root inside WSL: wsl -u root -- bash -c 'bash "/mnt/g/.../diag-hang.sh"'
echo "== loadavg =="; cat /proc/loadavg
echo "== io pressure =="; cat /proc/pressure/io 2>/dev/null; cat /proc/pressure/memory 2>/dev/null
echo "== mounts of interest =="; mount | grep -E " / |sdf|/mnt/g|9p|drvfs" | cut -c1-140
echo "== D/Z state tasks (via /proc, 3s cap each) =="
for p in /proc/[0-9]*; do
  pid=${p#/proc/}
  st=$(timeout 3 awk '{print $3}' "$p/stat" 2>/dev/null)
  if [ "$st" = "D" ] || [ "$st" = "Z" ]; then
    cmd=$(timeout 3 tr '\0' ' ' < "$p/cmdline" 2>/dev/null | cut -c1-100)
    wch=$(timeout 3 cat "$p/wchan" 2>/dev/null)
    echo "pid=$pid state=$st wchan=$wch cmd=$cmd"
    timeout 3 cat "$p/stack" 2>/dev/null | head -8 | sed 's/^/    /'
  fi
done
echo "== dmesg tail =="; dmesg 2>/dev/null | tail -25
echo "== build log tail =="; tail -3 /home/ggorbalan/futuramax/openwrt-24.10.4/logs/futuramax-build.log
