<!-- doc-head: Stage 449A airFiber AF-4X / AF-5X Invictus 2 TDD & Cyclic Prefix (CP) Safe Optimization Kit -->
Reconciles Stage 388A's static binary RE (`ame_core.ko`, `ame_dev.ko`, `UBNT-AirFIBER-MIB.txt`) with the live `AF-4X` (`198.18.0.83`) Wave 2 `Invictus v2` FPGA autoresearch receipt to package the safe `fmx_af4x_af5x_invictus2_tdd_cp_kit.sh` optimization kit.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 449A — `airFiber` `AF-4X` / `AF-5X` `Invictus 2` TDD & Cyclic Prefix (`CP`) Safe Optimization Kit

- **Epistemic Status**: `CONFIRMED` (`Stage 388A` static RE + `12` live counterbalanced `A1->B1->A2->B2` rounds on `AF-4X` `198.18.0.83`)
- **Attribution**: `proprietary airMAX/LTU module` (`Invictus v2` FPGA `af` CLI on `AF-4X`/`AF-5X` vs `ame_core.ko`/`ame_dev.ko` on `AF-5XHD`/`LTU`)
- **Kit Script**: [`fmx_af4x_af5x_invictus2_tdd_cp_kit.sh`](../firmware/openwrt/common/fmx_af4x_af5x_invictus2_tdd_cp_kit.sh) (`SHA-256: cad31862d9f308b7...`, strict `LF`)
- **JSON Receipt**: [`stage449a_af4x_af5x_invictus2_tdd_tuning_kit.json`](../artifacts/autoresearch/stage449a_af4x_af5x_invictus2_tdd_tuning_kit.json)

---

## 1. Stage 388A Architectural Reconciliation (`Invictus v2` vs `LTU Beetle`)

Stage 388A proved why searching `LTU` kernel modules or SNMP MIBs for `AF-4X` `af set` strings yields a clean separation between Ubiquiti's two custom TDD families:
1. **`AF-4X` / `AF-5X` (`TI DaVinci AM1808` `ARM926EJ-S` + `Invictus v2` FPGA `IRQ 140`, `AF06.v4.1.0`)**:
   - `UBNT-AirFIBER-MIB.txt` (`157` `OBJECT-TYPE` definitions, `SHA-256: bcd9c47d...`) exposes read-only telemetry OIDs (`0` writable TDD/CP objects).
   - Runtime TDD frame length (`framelength`), cyclic prefix (`cp`, `cpsel`, `shortcp`), and timing (`stricttiming`, `flowcntl`, `dpcntl`, `ber`) are controlled via the userspace **`af` CLI** communicating with `radiod` and `Invictus v2`.
2. **`AF-5XHD` / `LTU` (`Beetle` SoC + `ame_asic0` / `AD9361` SDR)**:
   - Controlled via `ame_core.ko` (`SHA-256: fe5d489e...`) and `ame_dev.ko` (`SHA-256: 912a7c19...`) kernel attributes: `duty_cycle`, `cpsample`, `frame_len`, `frame_period`, `dl_symbols`, `ul_symbols`, `gap0`, and `sync_mode`.

---

## 2. Live-Verified `AF-4X` / `AF-5X` `Invictus 2` Champion Parameters (`.244`)

| Knob / Command | Stock (`AF06.v4.1.0`) | Champion Setting | Measured Impact on `AF-4X` (`198.18.0.83`) |
| :--- | :---: | :---: | :--- |
| **`af set framelength`** | `2.0ms` (`500 Hz` IRQ) | **`2.5ms` (`400 Hz` IRQ)** | Reduces `IRQ 140` overhead on `124 BogoMIPS` CPU (`-16.1%` `p95` RTT, `+15.3%` stream) |
| **`af set stricttiming`** | `off` | **`on`** | Enforces deterministic TDD guard turnaround |
| **`af set cpsel` + `af set cp`** | `enabled` (`cp=24`) | **`disabled` + `cp 8` + `shortcp on`** | Strips excessive cyclic-prefix overhead on clean/moderate LOS links |
| **`af set flowcntl` + `dpcntl`** | `off` / `on` | **`flowcntl on` + `dpcntl off`** | **`+13.6%` throughput**, cumulative **`-22.8%` `p95` tail latency (`33.25 -> 25.68 ms`)** |
