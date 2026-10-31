<!-- doc-head: STAGE493A_LIVE_XC198_ROUND12_144WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 493A: Live `XC` Rocket Prism 5AC Gen2 (`198.18.0.64`) Round 12 (`144-Window` Milestone) Ground-Up PB050 RC Probe Dampening Profile, Active AirPrism & BQL/AQL Pacing Autoresearch

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `hardware` (Active AirPrism GPIO `13..16`) + `Linux` (BQL/AQL & TCP pacing)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS rollback watchdog)
- **Artifact**: [`stage493a_live_xc198_round12_144window_autoresearch.json`](../artifacts/autoresearch/stage493a_live_xc198_round12_144window_autoresearch.json)
- **Runner**: [`run_stage493a_live_xc198_round12_144window_autoresearch.py`](../tools/benchmarks/run_stage493a_live_xc198_round12_144window_autoresearch.py)
- **Verification**: [`test_stage493a.py`](../tests/test_stage493a.py)

## 1. Hypothesis & Experimental Protocol (`A1 -> B1 -> A2 -> B2`)

On the live `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25`, Boca 4), Round 12 evaluates:
1. **Ground-Up PB050 RC Probe Dampening Profile**: Dampening upward rate-control probing (`pb050_rc_probe_interval_ms=200`, `rc_max_probe_pct=2`, `swr_limit=3`) to eliminate `p99` tail-latency spikes caused by speculative high-MCS probe failures.
2. **Active AirPrism GPIO `13..16` + `uph_wifi0`**: `daprot=2`, `set_multiq=3`, `ff_mcast_airtime_limit=5`, `AC*Minfree=64/32/16/0`.
3. **BQL/AQL & TCP Pacing**: `bql_limit_max=32768`, `aql_txq_limit_us=3000`, `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `tcp_limit_output_bytes=49152`, `dev_weight=96`, `netdev_budget=600`, `txqueuelen=192`.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: 4 counterbalanced `A1 -> B1 -> A2 -> B2` live windows on `.198` with `45s` rollback watchdog.
- **Pillar D**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE493A-LIVE-XC198-ROUND12-PB050-RC-DAMPENER`.
