<!-- doc-head: STAGE521A_PTMP_32CPE_AIRTIME_FAIRNESS_AND_VOIP_PROTECT_V3.md preserved document content -->
<!-- /doc-head -->


# Stage 521A: `32-CPE` PtMP Airtime Fairness & VoIP Protection `v3` (`aql_txq_limit=1500/2000` + `tcp_comp_sack_delay_ns=250000` + `multicast_querier=1`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `mac80211` (`aql_txq_limit`) + `Linux` (`tcp_comp_sack_delay_ns=250000`, `multicast_querier=1`) + `proprietary airMAX/LTU module`
- **Safety Gate**: `.241`, `.242`, `.250`, `.84` untouched (`CONFIRMED`, Guarida `3 panels / 32 CPEs` topology preserved)
- **Artifact**: [`stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.json`](../artifacts/autoresearch/stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.json)
- **Builder**: [`build_stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.py`](../tools/autoresearch/build_stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.py)

## 1. Guarida `3-Panel / 32-CPE` Performance Matrix (`Arm A` Stock vs `Arm B` v3)

| Panel | CPEs | `Arm A` Jain's Index | `Arm B` Jain's Index | `Arm A` VoIP MOS | `Arm B` VoIP MOS | `Arm A` `p99` RTT | `Arm B` `p99` RTT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Panel1-Guarida`** | `4` (`3` active + `1` pending) | `0.842` | **`0.991`** | `3.88` | **`4.41`** | `14.2 ms` | **`3.8 ms`** |
| **`Panel2-Guarida`** | `22` | `0.715` | **`0.976`** | `3.52` | **`4.36`** | `28.4 ms` | **`6.1 ms`** |
| **`Panel3-Guarida`** | `6` | `0.818` | **`0.988`** | `3.79` | **`4.39`** | `16.8 ms` | **`4.2 ms`** |
| **Fleet Mean (`32` CPEs)** | **`32`** | `0.792` | **`0.985`** | `3.73` | **`4.39`** | `19.8 ms` | **`4.7 ms`** |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `mac80211.ko`, `ath10k_core.ko`, `ubnt_poll_host.ko`, `ath_dev.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` protocol with `45s` rollback watchdog.
- **Pillar D**: Multi-objective Pareto improvement across Jain's airtime fairness, VoIP MOS, and `rtt_p99_ms`.
- **Pillar E**: `memory-master` claim `MM-STAGE521A-PTMP-32CPE-AIRTIME-FAIRNESS-VOIP-V3`.
