<!-- doc-head: STAGE495A_LIVE_XM20_ROUND12_144WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->


# Stage 495A: Live `XM/WA` (`192.168.1.20` / `.20` via `.253` Bridge) Round 12 (`144-Window` Milestone) PB050 RC Probe Dampening & Airtime Fairness Autoresearch

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ath_dev.ko`, `ath_rate_atheros.ko`) + `mac80211` / `ath9k` + `Linux` (`vm.min_free_kbytes=1536`)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS rollback watchdog)
- **Artifact**: [`stage495a_live_xm20_round12_144window_autoresearch.json`](../artifacts/autoresearch/stage495a_live_xm20_round12_144window_autoresearch.json)
- **Runner**: [`run_stage495a_live_xm20_round12_144window_autoresearch.py`](../tools/benchmarks/run_stage495a_live_xm20_round12_144window_autoresearch.py)
- **Verification**: [`test_stage495a.py`](../tests/test_stage495a.py)

## 1. Milestone & Experimental Protocol (`A1 -> B1 -> A2 -> B2`)

Stage 495A completes the **`144-Window` Multi-Radio Milestone** (`12 rounds x 4 windows x 3 radio families = 144 counterbalanced live windows`) by evaluating on `192.168.1.20` (logical `.20` via `.253` bridge):
1. **PB050 RC Probe Dampening & Minstrel-HT Retry Bounds**: `pb050_rc_probe_interval_ms=200`, `rc_max_probe_pct=2`, `minstrel_retry_chain=[4,4,2,2]`.
2. **Cooperative Sensing, AQL/BQL & 32 MB OOM Shield**: `cooperative_sensing_ani_mode=1`, `aggr_limit_bytes=16384`, `aql_txq_limit=2000/4000 us`, `eth0_bql_limit_max=24576`, `txqueuelen=48`, and `vm.min_free_kbytes=1536`.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ath_dev.ko`, `ath_rate_atheros.ko`, `mac80211.ko`, `ath9k.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-33`).
- **Pillar C**: 4 counterbalanced `A1 -> B1 -> A2 -> B2` live windows reaching `144` cumulative multi-radio windows with `45s` rollback watchdog.
- **Pillar D**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, and `jitter_ms`.
- **Pillar E**: `memory-master` claim `MM-STAGE495A-LIVE-XM20-ROUND12-144WINDOW`.
