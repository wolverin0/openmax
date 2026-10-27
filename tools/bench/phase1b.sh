#!/bin/bash
# Phase 1b: re-run the TCP matrix (loaded RTT) after the runner fix; waits for phase1 to finish first.
cd "/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX" || exit 1
L="research/raw/bench/$(date +%Y-%m-%d)/phase1.log"
until grep -q "PHASE1 DONE" "$L" 2>/dev/null; do sleep 15; done
echo "PHASE1B START $(date -Is)"
python tools/bench/bench.py matrix --modes VHT80 VHT40 VHT20 --secs 10 --no-udp
echo "PHASE1B DONE $(date -Is)"
