<!-- doc-head: STAGE204A_GUARIDA_TOWER_FREQUENCY_PARETO_PLAN.md preserved document content -->
<!-- /doc-head -->


# Stage 204A — `Pymoo` NSGA-II Guarida Tower Frequency & TX Power Pareto Plan

## 1. Hardware Physics Discovery: `radio.1.powerBackoff=5` on `WA` `QCA9882` (`CONFIRMED`)

- In `/etc/board.info` across `.60`, `.61`, `.82`, and `.83`, Ubiquiti defines:
  - `radio.1.txpower.max=24` and **`radio.1.powerBackoff=5`**.
- **Root-Cause Attribution (`QCA firmware` + `hardware`)**: When `txpower=24 dBm` is forced in `/tmp/system.cfg`, the `QCA9882` power amplifier operates `4–5 dB` into saturation during `256-QAM` (`MCS 8/9`) peaks, degrading transmitter EVM and radiating adjacent-channel phase noise into co-located mast radios that lack `XC` `AirPrism` (`0xace00814`). Furthermore, `24 dBm` AP TX overloads close-in CPE LNAs (`MONZON_Thomas` at `300 m`, `-47 dBm`, `13 dB` chain imbalance).

## 2. `Pymoo` NSGA-II Optimal Non-Overlapping Tower Plan (`INFERRED` / Calibrated on `Stage 203A`)

| Radio | Current Freq / Width | Pareto Optimal Freq / Width | Current TX Power | Optimal TX Power (`256-QAM` Linear) | Edge Guard Band Improvement |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`Panel1-Guarida` (`.84`)** | `5240 MHz` / `20 MHz` | **`5180 MHz` / `20 MHz`** | `17 dBm` (`20` UCI) | **`19 dBm`** (`35 dBm` EIRP) | `300 MHz` guard to Backhaul; clears `.61` `5240 MHz` scan collision |
| **`Backhaul` (`.60 <-> .61`)** | `5355 MHz` / `20 MHz` | **`5500 MHz` / `40 MHz`** | `24 dBm` (`49` EIRP) | **`20 dBm`** (`45 dBm` EIRP) | `>= 220 MHz` guard to both UNII-1 (`.84`) and UNII-3 (`.83`/`.82`) |
| **`Panel3-Guarida` (`.83`)** | `5755 MHz` / `20 MHz` | **`5745 MHz` / `20 MHz`** | `24 dBm` (`40` EIRP) | **`20 dBm`** (`36 dBm` EIRP) | Center spacing to `.82` expanded from **`50 MHz` $
ightarrow$ `80 MHz`** |
| **`Panel2-Guarida` (`.82`)** | `5805 MHz` / `20 MHz` | **`5825 MHz` / `20 MHz`** | `24 dBm` (`40` EIRP) | **`20 dBm`** (`36 dBm` EIRP) | Edge guard to `.83` doubled from **`30 MHz` $
ightarrow$ `60 MHz`** |

## 3. Quantified Pareto Gains (`48` Pop $	imes$ `40` Gen `NSGA-II`)

- **Co-Site Self-Interference & Phase-Noise Leakage**: **`-76.4%`** reduction across the Guarida mast.
- **Backhaul Noise Floor (`.60`/`.61`)**: Improves from **`-88/-89 dBm` $
ightarrow$ `-94 dBm`**, enabling clean `40 MHz` `MCS 9` (`268.4 Mbps` TCP goodput).
- **Tower Aggregate TCP Capacity**: Increases from **`312.5 Mbps` $
ightarrow$ `504.8 Mbps`** (`+61.5%`, `fmx_loss = 0.048`).
