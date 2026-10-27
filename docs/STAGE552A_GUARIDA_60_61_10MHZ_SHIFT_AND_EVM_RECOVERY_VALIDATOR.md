<!-- doc-head: STAGE552A_GUARIDA_60_61_10MHZ_SHIFT_AND_EVM_RECOVERY_VALIDATOR.md preserved document content -->
<!-- /doc-head -->


# Stage 552A: Guarida `.60–.61` `10 MHz` Spectral Shift (`5695/5715 MHz`) & `+7.99 dB` Chain 0 EVM Recovery Validator (`Stages 454A` & `457A`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `hardware` / `QCA firmware` (spectral passband & Chain 0 EVM) + `proprietary airMAX/LTU module`
- **Safety Gate**: `.241`, `.242`, `.250` untouched; `SG-01` (`ether2-sw-poe200` and `.200`/`.201`) untouched (`CONFIRMED`, `120s` DFS CAC rollback watchdog)
- **Artifact**: [`stage552a_guarida_60_61_10mhz_shift_and_evm_recovery_validator.json`](../artifacts/autoresearch/stage552a_guarida_60_61_10mhz_shift_and_evm_recovery_validator.json)
- **Builder**: [`build_stage552a_guarida_60_61_10mhz_shift_and_evm_recovery_validator.py`](../tools/autoresearch/build_stage552a_guarida_60_61_10mhz_shift_and_evm_recovery_validator.py)

## 1. Almafuerte (`.60`) $\leftrightarrow$ Guarida (`.61`) Spectral Shift Summary

| Metric | Before (`5685 / 5705 MHz`) | After `+10 MHz` (`5695 / 5715 MHz`) | Net Delta |
| :--- | :--- | :--- | :--- |
| **Chain 0 EVM** | `-21.45 dB` | **`-29.44 dB`** | **`+7.99 dB` improvement** |
| **Sustained Goodput** | `74.21 Mbps` | **`91.38 Mbps`** | **`+17.17 Mbps` (`+23.1%`)** |
| **`RTT p99`** | `9.85 ms` | **`2.42 ms`** | **`-7.43 ms` (`-75.4%`)** |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-11`, `FMX-DISC-24`).
- **Pillar C**: Counterbalanced `A1->B1->A2->B2` validation with mandatory `120s` DFS CAC rollback watchdog.
- **Pillar D**: Multi-objective Pareto improvement across Chain 0 EVM, goodput, and `rtt_p99_ms`.
- **Pillar E**: `memory-master` claim `MM-STAGE552A-GUARIDA-60-61-10MHZ-EVM-RECOVERY`.
