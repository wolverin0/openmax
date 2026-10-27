<!-- doc-head: STAGE463A_LIVE_XM20_ROUND11_132WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->


# Stage 463A: Live `XM/WA` (`192.168.1.20` / `.20` via `.253` Bridge) Round 11 (`132-Window` Milestone) Cooperative Sensing & Airtime Deficit Autoresearch

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ath_dev.ko`, `ath_rate_atheros.ko`) + `mac80211` / `ath9k` + `Linux` (`vm.min_free_kbytes=1536`)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS rollback watchdog)
- **Artifact**: [`stage463a_live_xm20_round11_132window_autoresearch.json`](../artifacts/autoresearch/stage463a_live_xm20_round11_132window_autoresearch.json)
- **Runner**: [`run_stage463a_live_xm20_round11_132window_autoresearch.py`](../tools/benchmarks/run_stage463a_live_xm20_round11_132window_autoresearch.py)
- **Verification**: [`test_stage463a.py`](../tests/test_stage463a.py)

## 1. Milestone & Experimental Protocol (`A1 -> B1 -> A2 -> B2`)

Stage 463A completes the **`132-Window` Multi-Radio Milestone** (`11 rounds x 4 windows x 3 radio families = 132 counterbalanced live windows`) by evaluating on `192.168.1.20` (logical `.20` via `.253` bridge):
1. **Cooperative Spectral Sensing & ANI Step Control**: `cooperative_sensing_ani_mode=1` (`intmit=1`), `aggr_limit_bytes=16384`, and `asymmetric_lgi_rescue_enable=True`.
2. **AQL / BQL & Minstrel-HT Retry Bounds**: `aql_txq_limit=2000/4000 us`, `eth0_bql_limit_max=24576`, `minstrel_retry_chain=[4,4,2,2]`, `txqueuelen=48`, and `vm.min_free_kbytes=1536`.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ath_dev.ko`, `ath_rate_atheros.ko`, `mac80211.ko`, `ath9k.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-33`).
- **Pillar C**: 4 counterbalanced `A1 -> B1 -> A2 -> B2` live windows reaching `132` cumulative multi-radio windows with `45s` rollback watchdog.
- **Pillar D**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, and `jitter_ms`.
- **Pillar E**: `memory-master` claim `MM-STAGE463A-LIVE-XM20-ROUND11-132WINDOW`.
