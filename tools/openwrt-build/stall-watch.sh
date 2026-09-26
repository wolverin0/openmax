#!/bin/bash
# Emits one line when the build log has not changed for >10 min (kernel hang detector), plus
# a terminal line when the build finishes. Run under a Monitor; each stdout line is an event.
L="$HOME/futuramax/openwrt-24.10.4/logs/futuramax-build.log"
while true; do
  sleep 120
  if grep -q "ATTACHED-RUNNER done" "$L" 2>/dev/null; then
    echo "DONE: $(grep -E 'BUILD_EXIT|ATTACHED-RUNNER done' "$L" | tail -2 | tr '\n' ' ')"
    exit 0
  fi
  now=$(date +%s)
  m=$(stat -c %Y "$L" 2>/dev/null || echo 0)
  age=$((now - m))
  if [ "$age" -gt 600 ]; then
    echo "STALL: log unchanged for ${age}s; last: $(tail -1 "$L")"
  fi
done
