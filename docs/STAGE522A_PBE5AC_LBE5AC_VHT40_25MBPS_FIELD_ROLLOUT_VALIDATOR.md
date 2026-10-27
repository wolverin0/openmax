<!-- doc-head: STAGE522A_PBE5AC_LBE5AC_VHT40_25MBPS_FIELD_ROLLOUT_VALIDATOR.md preserved document content -->
<!-- /doc-head -->


# Stage 522A: `PBE-5AC-Gen2` & `LBE-5AC-Gen2` `VHT40` `24.83 Mbps` (`0.0%` Loss) Field Rollout Validator (`Stage 487A` Profile)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` (`g_rc_probe_period_ms=30000`, `g_rc_probe_pkt_threshold=2048`) + `ath10k` / `mac80211` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `mtd0/1/5` protected, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.json`](../artifacts/autoresearch/stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.json)
- **Builder**: [`build_stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.py`](../tools/autoresearch/build_stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.py)

## 1. Validated Field Rollout Matrix (`PBE-5AC-Gen2` & `LBE-5AC-Gen2`)

| Model | SoC / Radio | Profile | Goodput | `1472B` Loss | `RTT p95 / p99` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`PBE-5AC-Gen2`** | `AR9342 + QCA9882` (`64 MB`) | `VHT40 MCS 2` LGI + `RC_P30000_T2048` | **`24.83 Mbps`** | **`0.0%`** | `1.02 / 1.18 ms` | `45s` / `120s` |
| **`LBE-5AC-Gen2`** | `AR9342 + QCA9882` (`64 MB`) | `VHT40 MCS 2` LGI + `RC_P30000_T2048` | **`24.83 Mbps`** | **`0.0%`** | `1.06 / 1.22 ms` | `45s` / `120s` |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ath10k_core.ko`, `mac80211.ko`, `ubnt_poll_host.ko`, `umac.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` validation with `45s` Non-DFS / `120s` DFS rollback watchdog.
- **Pillar D**: Multi-objective Pareto verification across `validated_goodput_mbps`, `full_mtu_1472b_loss_pct`, `rtt_p99_ms`, and `mem_free_floor_kb`.
- **Pillar E**: `memory-master` claim `MM-STAGE522A-PBE5AC-LBE5AC-VHT40-25MBPS-VALIDATOR`.
