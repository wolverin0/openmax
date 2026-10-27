<!-- doc-head: STAGE554A_WA_XC_PB040_PB050_COMBINED_RAM_PATCH_VALIDATOR.md preserved document content -->
<!-- /doc-head -->


# Stage 554A: `WA`/`XC` Combined `PB-040` (`.text 0x009b7584` CCA/AGC Override) + `PB-050` (`.data` RC Probe Dampening) `SGMT` RAM Image Safety Validator

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` (`SGMT` `.text` `0x009b7584` & `.data` `0x009e4120`) + `ath10k` / `proprietary airMAX/LTU module`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `mtd0/1/5` untouched, `0` flash writes, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage554a_wa_xc_pb040_pb050_combined_ram_patch_validator.json`](../artifacts/autoresearch/stage554a_wa_xc_pb040_pb050_combined_ram_patch_validator.json)
- **Builder**: [`build_stage554a_wa_xc_pb040_pb050_combined_ram_patch_validator.py`](../tools/autoresearch/build_stage554a_wa_xc_pb040_pb050_combined_ram_patch_validator.py)

## 1. Disjoint `SGMT` RAM Segment Verification (`WA` `QCA9882` & `XC` `QCA9880`)

| Patch ID | Segment | Target VAddr | Size | Function | Disjoint Check |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`PB-040`** | `.text` | `0x009b7584` | `16 B` | CCA/AGC dynamic stepping override (`-68 dBm` / `4 dB`) | `PASS` (`183,196 B` gap) |
| **`PB-050`** | `.data` | `0x009e4120` | `8 B` | Rate-control upward probe dampening (`30000 ms` / `2048 pkts`) | `PASS` (`183,196 B` gap) |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `QCA988x` `SGMT` firmware image (`.text` `0x009b7584`, `.data` `0x009e4120`) + `ubnt_poll_host.ko`.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` validation with `45s` rollback watchdog and ephemeral RAM-only target load.
- **Pillar D**: Multi-objective Pareto improvement across `full_mtu_1472b_loss_pct`, `rtt_p99_ms`, `goodput_mbps`, and `cca_false_deferral_rate`.
- **Pillar E**: `memory-master` claim `MM-STAGE554A-WA-XC-PB040-PB050-COMBINED-RAM-VALIDATOR`.
