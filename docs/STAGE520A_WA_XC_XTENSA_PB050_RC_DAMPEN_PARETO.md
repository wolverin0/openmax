<!-- doc-head: STAGE520A_WA_XC_XTENSA_PB050_RC_DAMPEN_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 520A: `WA`/`XC` Xtensa `PB050` Rate-Control Probe Dampening Pareto Frontier (`g_rc_probe_period_ms` $\times$ `g_rc_probe_pkt_threshold`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` (`Xtensa` rate-control `g_rc_probe_period_ms`, `g_rc_probe_pkt_threshold`) + `ath10k` + `proprietary airMAX/LTU module`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.json`](../artifacts/autoresearch/stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.json)
- **Builder**: [`build_stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.py`](../tools/autoresearch/build_stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.py)

## 1. Full $3 \times 3$ Factorial Matrix (`1472 B` Full-MTU Loss under Near-Field Multipath)

| Candidate ID | `g_rc_probe_period_ms` | `g_rc_probe_pkt_threshold` | `1472B` Loss (%) | `RTT p99` (ms) | Goodput (Mbps) | Pareto Optimal |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RC_P5000_T32` | `5000` | `32` | `4.85%` | `8.40` | `18.20` | `False` |
| `RC_P5000_T512` | `5000` | `512` | `2.60%` | `5.10` | `21.40` | `False` |
| `RC_P5000_T2048` | `5000` | `2048` | `1.45%` | `3.60` | `22.90` | `False` |
| `RC_P30000_T32` | `30000` | `32` | `1.10%` | `2.95` | `23.50` | `False` |
| `RC_P30000_T512` | `30000` | `512` | `0.15%` | `1.48` | `24.65` | `False` |
| **`RC_P30000_T2048`** | **`30000`** | **`2048`** | **`0.00%`** | **`1.18`** | **`24.83`** | **`True` (Champion)** |
| `RC_P60000_T32` | `60000` | `32` | `0.45%` | `2.10` | `24.10` | `False` |
| **`RC_P60000_T512`** | **`60000`** | **`512`** | **`0.00%`** | **`1.15`** | **`24.81`** | **`True`** |
| **`RC_P60000_T2048`** | **`60000`** | **`2048`** | **`0.00%`** | **`1.12`** | **`24.79`** | **`True`** |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of Xtensa rate-control globals (`g_rc_probe_period_ms`, `g_rc_probe_pkt_threshold`) in `QCA988x` firmware + `ubnt_poll_host.ko`.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` validation with `45s` rollback watchdog.
- **Pillar D**: Exact 4-objective Pareto non-dominance verification across the $3 \times 3$ grid (`3` non-dominated Pareto frontier points).
- **Pillar E**: `memory-master` claim `MM-STAGE520A-WA-XC-XTENSA-PB050-RC-DAMPEN-PARETO`.
