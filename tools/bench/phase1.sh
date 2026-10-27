#!/bin/bash
# Phase 1 chain (1.3-1.6) — detached runner; log: research/raw/bench/<date>/phase1.log
cd "/g/_OneDrive/OneDrive/Desktop/Py Apps/futuraMAX" || exit 1
echo "PHASE1 START $(date -Is)"
python tools/bench/bench.py sweep-txpower 11 --secs 4      # sets operating point (sweep ends on first level)
echo "== 1.3 matrix =="; python tools/bench/bench.py matrix --secs 10
echo "== 1.4 aql-ab =="; python tools/bench/bench.py aql-ab --rounds 2 --secs 12
echo "== 1.5 spectral =="; python tools/bench/bench.py spectral --load down --secs 15
echo "== 1.6 ctdebug =="; python tools/bench/bench.py ctdebug
echo "PHASE1 DONE $(date -Is)"
