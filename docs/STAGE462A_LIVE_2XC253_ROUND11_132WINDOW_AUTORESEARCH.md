<!-- doc-head: STAGE462A_LIVE_2XC253_ROUND11_132WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 462A: Live `2XC` Rocket 2AC Prism (`198.18.0.65`) Round 11 (`132-Window` Milestone) 2.4 GHz Co-Channel Immunity & WMM Airtime Deficit Fairness Autoresearch

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `hardware` (2.4 GHz AirPrism) + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS rollback watchdog)
- **Artifact**: [`stage462a_live_2xc253_round11_132window_autoresearch.json`](../artifacts/autoresearch/stage462a_live_2xc253_round11_132window_autoresearch.json)
- **Runner**: [`run_stage462a_live_2xc253_round11_132window_autoresearch.py`](../tools/benchmarks/run_stage462a_live_2xc253_round11_132window_autoresearch.py)
- **Verification**: [`test_stage462a.py`](../tests/test_stage462a.py)

## 1. Hypothesis & Experimental Protocol (`A1 -> B1 -> A2 -> B2`)

On the live `Rocket 2AC Prism` (`198.18.0.65`, `2XC.v8.7.11`, Boca 6), Round 11 evaluates:
1. **2.4 GHz Co-Channel Immunity**: `daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`, and `dynamic_rts_cts_bytes=512` to bound collision blast radius in 2.4 GHz.
2. **WMM Airtime Deficit Fairness**: Per-AC descriptor reservation (`AC*Minfree=64/32/16/0`, `set_multiq=3`, `wmm_airtime_quantum_us=[1500, 2500, 3000, 1000]`) preventing bulk `AC_BE`/`AC_BK` frames from starving `AC_VO`/`AC_VI`.
3. **NAPI & TSQ Pacing**: `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: 4 counterbalanced `A1 -> B1 -> A2 -> B2` live windows on `.253` with `45s` rollback watchdog.
- **Pillar D**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE462A-LIVE-2XC253-ROUND11-COCHANNEL-WMM`.
