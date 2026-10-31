<!-- doc-head: STAGE461A_LIVE_XC198_ROUND11_132WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 461A: Live `XC` Rocket Prism 5AC Gen2 (`198.18.0.64`) Round 11 (`132-Window` Milestone) Ground-Up CCA/AGC Dynamic Stepping, Active AirPrism & TCP Pacing Autoresearch

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `hardware` (Active AirPrism GPIO `13..16`) + `Linux` (`tcp_pacing_ca_ratio=110`)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS rollback watchdog)
- **Artifact**: [`stage461a_live_xc198_round11_132window_autoresearch.json`](../artifacts/autoresearch/stage461a_live_xc198_round11_132window_autoresearch.json)
- **Runner**: [`run_stage461a_live_xc198_round11_132window_autoresearch.py`](../tools/benchmarks/run_stage461a_live_xc198_round11_132window_autoresearch.py)
- **Verification**: [`test_stage461a.py`](../tests/test_stage461a.py)

## 1. Hypothesis & Experimental Protocol (`A1 -> B1 -> A2 -> B2`)

On the live `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25`, Boca 4), Round 11 evaluates:
1. **Ground-Up CCA/AGC Dynamic Stepping**: Bounding energy-detect / clear-channel assessment (`cca_threshold_dbm=-68`, `agc_relock_step_db=4`) so out-of-band spikes do not trigger false carrier-sense deferrals once Active AirPrism filters narrow the passband.
2. **Active AirPrism GPIO `13..16` + `uph_wifi0`**: `daprot=2`, `set_multiq=3`, `ff_mcast_airtime_limit=5`, `swr_limit=3`, `AC*Minfree=64/32/16/0`.
3. **TCP Pacing & NAPI Budget**: `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `tcp_limit_output_bytes=49152`, `dev_weight=96`, `netdev_budget=600`, `txqueuelen=192`.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: 4 counterbalanced `A1 -> B1 -> A2 -> B2` live windows on `.198` with `45s` rollback watchdog.
- **Pillar D**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE461A-LIVE-XC198-ROUND11-CCA-AGC-AIRPRISM`.
