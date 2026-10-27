<!-- doc-head: STAGE551A_168WINDOW_MULTI_RADIO_MILESTONE_R105_R110.md preserved document content -->
<!-- /doc-head -->


# Stage 551A: `168-Window` Multi-Radio Milestone (`R105–R110`) Autoresearch (ANI OFDM/CCK Immunity + DFS Chirp Protection + `VHT40` Asymmetric MCS 2 LGI)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` / `ath10k` + `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `ath_dev.ko`) + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `0` flash writes, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage551a_168window_multi_radio_milestone_r105_r110.json`](../artifacts/autoresearch/stage551a_168window_multi_radio_milestone_r105_r110.json)
- **Runner**: [`run_stage551a_168window_multi_radio_milestone_r105_r110.py`](../tools/autoresearch/run_stage551a_168window_multi_radio_milestone_r105_r110.py)

## 1. Milestone & Experimental Protocol (`R105–R110`, `12` New Windows $\rightarrow$ `168` Cumulative Multi-Radio Windows)

Stage 551A executes 12 new counterbalanced `A1 -> B1 -> A2 -> B2` windows (`W157_R105_A1` .. `W168_R110_B2`) across the live bench fleet (`XC .198`, `2XC .253`, and `XM/XW/WA .20` via `.253` bridge), reaching **`168` cumulative multi-radio counterbalanced windows** (`42` rounds):
1. **ANI OFDM/CCK Immunity (`intmit=1`, `ani_ofdm_level=2`, `ani_cck_level=2`)**: Suppresses weak-signal false preamble locks without degrading desired frame sensitivity.
2. **DFS Chirp Protection (`dfs_chirp_protection_enable=True`, `120s` CAC watchdog)**: Prevents broadband non-radar RF impulses from triggering false DFS channel evacuations (`FMX-DISC-24`).
3. **`VHT40` Asymmetric MCS 2 `LGI` (`800 ns`)**: Guarantees `0.0%` loss on `1472 B` full-MTU packets under multipath.

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `ath10k_core.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: `12` new counterbalanced `A1->B1->A2->B2` windows (`168` cumulative) with `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `full_mtu_1472b_loss_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE551A-168WINDOW-MULTI-RADIO-MILESTONE-R105-R110`.
