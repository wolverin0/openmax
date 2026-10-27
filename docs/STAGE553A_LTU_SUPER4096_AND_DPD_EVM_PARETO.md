<!-- doc-head: STAGE553A_LTU_SUPER4096_AND_DPD_EVM_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 553A: `LTU` (`AF-LTU` `Beetle` + `ame_ASIC0` + `eab_driver.ko`) Super-4096 & DPD EVM Pareto Frontier on `4096-QAM` (`12X`) Residence

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`, `eab_driver.ko`: `bbp_rf_set_super4096`, `ame_bbp_set_dpd`, `ptmp_ap_autopwr_tx_power_adjust_routine`) + `hardware` (`ame_ASIC0`)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage553a_ltu_super4096_and_dpd_evm_pareto.json`](../artifacts/autoresearch/stage553a_ltu_super4096_and_dpd_evm_pareto.json)
- **Builder**: [`build_stage553a_ltu_super4096_and_dpd_evm_pareto.py`](../tools/autoresearch/build_stage553a_ltu_super4096_and_dpd_evm_pareto.py)

## 1. `LTU` `4096-QAM` (`12X`) Residence & EVM Pareto Matrix

| Candidate ID | `bbp_rf_set_super4096` | `ame_bbp_set_dpd` | AutoPwr Backoff | `4096-QAM` (`12X`) Residence | Composite EVM | Spectral Eff. (bps/Hz) | `RTT p99` | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `LTU_S0_DPD0_B0` | `0` | `0` | `0 dB` | `12.4%` | `-33.2 dB` | `8.9` | `2.45 ms` | `False` |
| `LTU_S0_DPD1_B2` | `0` | `1` | `-2 dB` | `38.6%` | `-36.5 dB` | `10.1` | `1.92 ms` | `False` |
| `LTU_S1_DPD1_B2` | `1` | `1` | `-2 dB` | `84.5%` | `-39.6 dB` | `12.9` | `1.28 ms` | `False` |
| **`LTU_S1_DPD2_B2`** | **`1`** | **`2`** | **`-2 dB`** | **`94.8%`** | **`-41.4 dB`** | **`13.8`** | **`1.06 ms`** | **`True` (Champion)** |
| **`LTU_S1_DPD2_B4`** | **`1`** | **`2`** | **`-4 dB`** | **`96.2%`** | **`-42.1 dB`** | **`13.7`** | **`1.04 ms`** | **`True`** |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ame_core.ko` & `eab_driver.ko` (`bbp_rf_set_super4096`, `ame_bbp_set_dpd`, `ptmp_ap_autopwr_tx_power_adjust_routine`).
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-24`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` validation with `45s`/`120s` rollback watchdog.
- **Pillar D**: 4-objective Pareto non-dominance verification across `qam4096_12x_residence_pct`, `composite_evm_db`, `spectral_efficiency_bps_hz`, and `rtt_p99_ms`.
- **Pillar E**: `memory-master` claim `MM-STAGE553A-LTU-SUPER4096-DPD-EVM-PARETO`.
