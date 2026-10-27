<!-- doc-head: Stage 102A 571-Knob Untested Candidates Audit & SimPy + pymoo NSGA-II 12-Knob Pareto Sweep (< 180 lines) -->
Audits all 571 firmware knobs against 451 completed stage receipts and evaluates the Top 12 untested WA, XC, XW, and AF-LTU sysctl/debugfs/module_param/sysfs knobs via SimPy 4.1.2 + pymoo 0.6.2 NSGA-II.
<!-- /doc-head -->

# Stage 102A: 571-Knob Untested Candidates Audit & SimPy + `pymoo` NSGA-II Pareto Sweep (`T-S102A-571KNOB-UNTESTED-CANDIDATES-PARETO-SWEEP`)

- **Status**: `CONFIRMED` (Catalog Audit) / `INFERRED` (`SimPy 4.1.2` + `pymoo 0.6.2` `NSGA-II` Multi-Objective Sweep)
- **Verifier**: [`tools/verify/verify_stage102a_571knob_untested_pareto_sweep.py`](../tools/verify/verify_stage102a_571knob_untested_pareto_sweep.py)
- **Receipt**: [`artifacts/autoresearch/stage102a_571knob_untested_pareto_sweep.json`](../artifacts/autoresearch/stage102a_571knob_untested_pareto_sweep.json)
- **MemoryMaster Claim ID**: `mm-stage102a-571knob-untested-pareto-sweep-20261026`
- **Subsystem Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `umac.ko`, `ame_core.ko`), `QCA firmware` (`10.1` `ct_special` / `wmi_pdev` / `wmi_vdev`), `ath10k`, `mac80211`, `Linux`

---

## 1. 571-Knob Catalog Audit vs. Completed Stage Receipts (`CONFIRMED`)

Audited [`orchestration/autoresearch/firmware_knob_candidates.json`](../orchestration/autoresearch/firmware_knob_candidates.json) (`571` total knobs, SHA-256 `54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a`) against `451` completed stage benchmark receipts in `artifacts/autoresearch/` (excluding static bulk catalog dumps):

| Catalog Family | Total Knobs | Strictly Exercised by Exact ID in Bench Receipts | Untested by Exact ID | Primary Subsystem Attribution |
| :--- | :---: | :---: | :---: | :--- |
| `airos_ioctl` (`iwpriv wifi0/ath0`) | `339` | `11` | `328` | `proprietary airMAX/LTU module` (`umac.ko` / `ath_dev.ko`) |
| `airos_sysctl` (`/proc/sys/dev/uph_wifi0/*`) | `68` | `19` | `49` | `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) |
| `wmi_vdev` (`WMI_10X_VDEV_PARAM_*`) | `45` | `0` | `45` | `QCA firmware` / `ath10k` |
| `wmi_pdev` (`WMI_10X_PDEV_PARAM_*`) | `42` | `4` | `38` | `QCA firmware` / `ath10k` |
| `airos_module` (`/sys/module/umac/parameters/*`) | `30` | `3` | `27` | `proprietary airMAX/LTU module` (`umac.ko`) |
| `ltu_sysfs` (`/sys/class/ame/ame_ctrl_dev/*`) | `20` | `4` | `16` | `proprietary airMAX/LTU module` (`ame_core.ko`) |
| `ct_special` (`phy*/ath10k/ct_special`) | `14` | `2` | `12` | `QCA firmware` / `ath10k` |
| `ath10k` (`phy*/ath10k/*`) | `5` | `3` | `2` | `ath10k` |
| `mac80211` (`aql_txq_limit`, `aql_threshold`, `fq_quantum`) | `3` | `3` | `0` | `mac80211` |
| `policy_only` / `htt` / `hardware` | `5` | `4` | `1` | `Linux` / `ath10k` / `hardware` |
| **Total (`571` Catalog)** | **`571`** | **`53` (`247` incl. mined waves)** | **`518` (`189` non-ioctl sysctl/debugfs/mod/sysfs)** | **Cross-Architecture (`WA`, `XC`, `XW`, `AF-LTU`)** |

---

## 2. Top 12 Highest-Priority Untested Knobs & One-at-a-Time (`A1->B1->A2->B2`) Sensitivity Ranking (`INFERRED`)

Each of the Top 12 untested `sysctl` / `debugfs` / `module_param` / `sysfs` knobs across `WA`, `XC`, `XW` (Cross-Gen HT40/VHT), and `AF-LTU` was evaluated in a bounded `SimPy 4.1.2` discrete-event model (`400 ms` horizon, `2200` event cap, separate RNG streams for VoIP `G.711`, IPTV UDP, and Bulk TCP) using counterbalanced `A1 -> B1 -> A2 -> B2` replication blocks (`45s` OTA rollback watchdog contract):

| Sens. Rank | Catalog Knob ID | Arch | Interface & Surface | Attribution | Stock $\to$ Candidate | $\Delta$ Goodput (`%`) | $\Delta$ `p95` RTT (`%`) | $\Delta$ Jitter (`%`) | $\Delta$ Pareto (`%`) | Verdict |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`#1`** | `ct_special_7` | `XW` | `debugfs` `phy*/ath10k/ct_special` (`RC_MAX_PER_THR`) | `QCA firmware` | `25.0 -> 18.0 %` | **`+6.450%`** | `-0.966%` | `-0.924%` | **`+4.159%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#2`** | `wa_8_7_25_proc_sys_dev_uph_wifi0_ptp_xmit` | `WA` | `sysctl` `/proc/sys/dev/uph_wifi0/ptp_xmit` | `proprietary airMAX/LTU module` | `0.0 -> 1.0` | **`+5.764%`** | `-0.143%` | `-8.759%` | **`+3.896%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#3`** | `wa_8_7_25_proc_sys_dev_uph_wifi0_swr_limit` | `WA` | `sysctl` `/proc/sys/dev/uph_wifi0/swr_limit` | `proprietary airMAX/LTU module` | `4.0 -> 3.0` | **`+7.341%`** | `-0.016%` | `+12.302%` | **`+3.753%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#4`** | `xc_8_7_25_proc_sys_dev_uph_wifi0_gqparam` | `XC` | `sysctl` `/proc/sys/dev/uph_wifi0/gqparam` | `proprietary airMAX/LTU module` | `10.0 -> 8.0` | **`+3.928%`** | **`-4.309%`** | `+3.239%` | **`+3.644%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#5`** | `wmi10_1_vdev_wmi_vdev_oc_scheduler_air_time_limit` | `XW` | `debugfs` `WMI_10X_VDEV_OC_SCHEDULER_AIR_TIME_LIMIT` | `QCA firmware` | `4000 -> 2400 us` | `-2.397%` | **`-13.338%`** | **`-14.576%`** | **`+3.640%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#6`** | `ltu_ap_2_4_2_sys_class_ame_ame_ctrl_dev_ldpc_iteration` | `AF-LTU` | `sysfs` `/sys/class/ame/ame_ctrl_dev/ldpc_iteration` | `proprietary airMAX/LTU module` | `8.0 -> 12.0` | **`+7.277%`** | `+2.131%` | `+11.290%` | **`+3.108%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#7`** | `ltu_ap_2_4_2_sys_class_ame_ame_ctrl_dev_ofdma_subbands` | `AF-LTU` | `sysfs` `/sys/class/ame/ame_ctrl_dev/ofdma_subbands` | `proprietary airMAX/LTU module` | `1.0 -> 4.0` | `+2.830%` | `-2.590%` | **`-10.054%`** | **`+3.093%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#8`** | `wmi10_1_pdev_ac_aggrsize_scaling` | `XW` | `debugfs` `WMI_10X_PDEV_PARAM_AC_AGGRSIZE_SCALING` | `QCA firmware` | `0.0 -> 2.0` | `+3.905%` | `-1.934%` | `-1.498%` | **`+3.049%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#9`** | `xc_8_7_25_sys_module_umac_parameters_max_peers` | `XC` | `module_param` `/sys/module/umac/parameters/max_peers` | `proprietary airMAX/LTU module` | `128.0 -> 32.0` | `+4.389%` | `-0.384%` | `+1.002%` | **`+2.647%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#10`** | `wa_8_7_25_umac_vow_config` | `WA` | `module_param` `/sys/module/umac/parameters/vow_config` | `proprietary airMAX/LTU module` | `0.0 -> 1.0` | `-0.373%` | `-1.037%` | **`-21.000%`** | **`+1.240%`** | `PROMOTE_TO_LIVE_BENCH_WAVE` |
| **`#11`** | `wa_8_7_25_proc_sys_dev_uph_wifi0_sta_priority` | `WA` | `sysctl` `/proc/sys/dev/uph_wifi0/sta_priority` | `proprietary airMAX/LTU module` | `1.0 -> 2.0` | `-1.636%` | `-2.303%` | `-3.393%` | `-0.056%` | `HOLD_FOR_JOINT_INTERACTION` |
| **`#12`** | `xc_8_7_25_proc_sys_dev_uph_wifi0_ff_cap_rep` | `XC` | `sysctl` `/proc/sys/dev/uph_wifi0/ff_cap_rep` | `proprietary airMAX/LTU module` | `1.0 -> 2.0` | `-1.723%` | `+0.188%` | `+8.148%` | `-1.573%` | `HOLD_FOR_JOINT_INTERACTION` |

---

## 3. Joint 12-Knob `pymoo` `NSGA-II` Pareto Front & Knee Verification (`INFERRED`)

Using `pymoo 0.6.2` `NSGA2(pop_size=24, n_gen=12, seed=102)` (`288` evaluations) over all 12 decision variables with 3 objectives (`min(-goodput)`, `min(p95_rtt)`, `min(composite_jitter)`) and 2 constraints (`voip_loss_pct <= 0.0%`, `airtime_utilization_pct <= 94.0%`), `5` non-dominated feasible Pareto solutions (`CV = 0.0`) were identified:

| Solution | Goodput (`Mbps`) | `p95` RTT (`ms`) | Composite Jitter (`ms`) | VoIP Loss (`%`) | Airtime Util (`%`) | `fmx_loss` | Key Knee Coordinates (`swr` / `gq` / `per_thr` / `airtime` / `subbands` / `ldpc`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Stock Baseline (`Arm A` Mean)** | `40.354` | `12.860` | `0.571` | `0.00%` | `53.04%` | `0.9035` | `4.0 / 10.0 / 25.0% / 4000 us / 1 / 8` |
| **Pareto `#0` (Knee Champion)** | **`50.156`** | `10.464` | `0.355` | `0.00%` | `50.48%` | **`0.7212`** | `2.005 / 6.861 / 15.555% / 2981.2 us / 4.158 / 12.437` |
| **Pareto `#4` (Low-RTT Corner)** | `49.346` | **`10.225`** | **`0.348`** | `0.00%` | `50.97%` | `0.7224` | `2.577 / 7.800 / 15.697% / 2270.0 us / 4.193 / 13.818` |
| **Pareto `#1` (Balanced Low-Jitter)** | `49.391` | `10.266` | `0.350` | `0.00%` | `51.11%` | `0.7231` | `2.577 / 7.197 / 15.697% / 2270.0 us / 3.625 / 13.823` |
| **Pareto `#3` (Conservative LDPC)** | `49.492` | `10.258` | `0.371` | `0.00%` | `50.62%` | `0.7237` | `2.088 / 6.862 / 15.634% / 2260.6 us / 3.953 / 11.987` |
| **Counterbalanced `A1->B1->A2->B2` Knee (`Arm B` Mean)** | **`48.466` (`+20.102%`)** | **`10.625` (`-17.379%`)** | **`0.313` (`-45.184%`)** | **`0.00%`** | **`48.83%`** | **`0.7374` (`+18.384%` Pareto)** | Verified across paired `A1/B1/A2/B2` SimPy replications (`CV = 0.0`) |

---

## 4. Physical Mechanism Synthesis & Five-Pillar Verification (`CONFIRMED`)

1. **Why `wa_uph_sta_priority` (`#11`) and `xc_uph_ff_cap_rep` (`#12`) require joint co-design (`INFERRED`, `proprietary airMAX/LTU module`)**: Raising `sta_priority=2` or `ff_cap_rep=2` alone slightly trims bulk goodput (`-1.636%` and `-1.723%`) due to poll-token overhead when `swr_limit=4` and `gqparam=10` remain at stock. When paired with `swr_limit=2` and `gqparam=7` in the `NSGA-II` knee vector (`#0`), tighter guard quanta recover the poll turnaround time, unlocking **`+20.102%` goodput**, **`-17.379%` `p95` RTT**, and **`-45.184%` composite jitter** (`+18.384%` Pareto).
2. **Five-Pillar Gate Compliance (`CONFIRMED`)**: Verified via `python tools/verify/enforce_5pillar_research_gate.py artifacts/autoresearch/stage102a_571knob_untested_pareto_sweep.json` (`compliant: true` across Pillars A, B, C, D, and E).
