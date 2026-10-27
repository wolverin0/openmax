<!-- doc-head: Stage 546A LTU TX Power LUT, PA DPD & Super4096 Telemetry Monitor Helper (Stage 544A RE) -->
Operationalizes OpenCode Stage 544A's binary RE of `ame_core.ko` (`bbp_rf_set_super4096`, `ame_bbp_set_dpd`, `ame_bbp_set_pa`, `ptmp_ap_autopwr_tx_power_adjust_routine`) and `ame_dev.ko` into `fmx_ltu_dpd_super4096_monitor.sh`.
<!-- /doc-head -->

# Stage 546A — `LTU` TX Power LUT, PA `DPD` & `Super4096` (`12X`) Safe Telemetry Helper

- **Epistemic Status**: `CONFIRMED` (`Stage 544A` ELF symbol & string RE of `ame_core.ko` `9,699` symbols and `ame_dev.ko` `1,669` symbols)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko` & `ame_dev.ko`)
- **Monitor Script**: [`fmx_ltu_dpd_super4096_monitor.sh`](../firmware/ltu_safe_kit/fmx_ltu_dpd_super4096_monitor.sh) (`SHA-256: dff0381bb8d04cde...`, strict `LF`, `zero_dev_ame_touches=True`)
- **JSON Receipt**: [`stage546a_ltu_tx_power_lut_dpd_and_super4096_helper.json`](../artifacts/autoresearch/stage546a_ltu_tx_power_lut_dpd_and_super4096_helper.json)

---

## 1. Stage 544A Symbol & Premise Synthesis (`ame_core.ko` + `ame_dev.ko`)

Stage 544A uncovered the exact symbol families governing `LTU` Power Amplifier (`PA`) linearity, Digital Pre-Distortion (`DPD`), and `4096-QAM` (`Super4096`):

| Subsystem | `ame_core.ko` Internal Symbols (`SHA-256: fe5d489e...`) | `ame_dev.ko` Sysfs Handlers (`SHA-256: 912a7c19...`) |
| :--- | :--- | :--- |
| **`Super4096` (`12X`)** | `bbp_rf_get_super4096`, `bbp_rf_set_super4096`, `autoMCS_get4096`, `autoMCS_set4096`, `startThrd_4096`, `stayThrd_4096` | `autoMcs4096_show`, `autoMcs4096_store` |
| **PA `DPD` Engine** | `ame_bbp_get_dpd`, `ame_bbp_set_dpd` (variable-length table check: `Incorrect dpd(tx) size (%d)!=(%d)`) | `dpd_load`, `dpd_show`, `dpd_store` |
| **PA Comp & Gain** | `ame_bbp_get_pa`, `ame_bbp_set_pa`, `ame_bbp_op_tx_pa_comp`, `ame_core_set_tx_pa_comp_mode`, `bbp_mrx_PA_mon` | `pa_load`, `pa_show`, `pa_store`, `tx_pa_comp_mode_show` |
| **TX Power & LUT** | `ptmp_ap_autopwr_tx_power_adjust_routine`, `bbp_util_calculate_tx_power_by_attenuation`, `ame_bbp_set_desired_txpower` | `rxTopA_txPower_show`, `rxTopA_txPower_store`, `obs_txgain_show` |
| **Constellation `EVM`** | `ame_bbp_op_evm_mcs_map`, `bbp_mrx_evm_get_mode_and_result`, `ame_bbp_get_evm_dump` | `evm_now_show`, `evm_avg_show`, `evm_float_show` |

> **Critical Premise Correction (`Stage 544A`)**: All `25` occurrences of the token `backoff` in `ame_core.ko` belong to `cz_cross_frame_backoff_*` (a scheduler cross-frame grouping knob), **not** PA EVM backoff. True `4096-QAM` modulation entry/exit is governed by **`startThrd_4096`** and **`stayThrd_4096`** alongside `tx_pa_comp_mode` and `dpd`.

---

## 2. Zero-Risk Read-Only Telemetry Contract (`zero_dev_ame_touches=True`)

`fmx_ltu_dpd_super4096_monitor.sh` reads only exported kernel `sysfs` attributes (`autoMcs4096`, `tx_pa_comp_mode`, `evm_now`, `evm_avg`, `rxTopA_txPower`) and writes `/tmp/fmx_ltu_dpd_super4096_telemetry.json` without ever opening `/dev/ame*`.
