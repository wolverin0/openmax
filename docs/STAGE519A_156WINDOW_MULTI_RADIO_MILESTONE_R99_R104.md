<!-- doc-head: STAGE519A_156WINDOW_MULTI_RADIO_MILESTONE_R99_R104.md preserved document content -->
<!-- /doc-head -->


# Stage 519A: `156-Window` Multi-Radio Milestone (`R99–R104`) Autoresearch (`VHT40` Asymmetric MCS 2 LGI + `pktlog_filter=0x0` + `nf_cal_period=120`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` / `ath10k` + `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `ath_dev.ko`) + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage519a_156window_multi_radio_milestone_r99_r104.json`](../artifacts/autoresearch/stage519a_156window_multi_radio_milestone_r99_r104.json)
- **Runner**: [`run_stage519a_156window_multi_radio_milestone_r99_r104.py`](../tools/autoresearch/run_stage519a_156window_multi_radio_milestone_r99_r104.py)

## 1. Milestone & Experimental Protocol (`R99–R104`, `12` New Windows $\rightarrow$ `156` Cumulative Multi-Radio Windows)

Stage 519A executes 12 new counterbalanced `A1 -> B1 -> A2 -> B2` windows (`W145_R99_A1` .. `W156_R104_B2`) across the live bench fleet (`XC .198`, `2XC .253`, and `XM/WA .20` via `.253` bridge), reaching **`156` cumulative multi-radio counterbalanced windows** (`39` rounds):
1. **`VHT40` Asymmetric MCS 2 `LGI` (`800 ns`)**: Eliminates cyclic-prefix ISI under near-field multipath while preserving clean `1472 B` full-MTU framing (`0.0%` loss).
2. **`pktlog_filter=0x0`**: Disables host-to-target diagnostic ring DMA copies, reducing `softirq_pct` by `5.9` to `7.7` percentage points.
3. **`nf_cal_period=120`**: Stabilizes periodic noise-floor calibration so burst interference does not skew AGC/CCA thresholds.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `ath10k_core.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: `12` new counterbalanced `A1->B1->A2->B2` windows (`156` cumulative) with `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `full_mtu_1472b_loss_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE519A-156WINDOW-MULTI-RADIO-MILESTONE-R99-R104`.
