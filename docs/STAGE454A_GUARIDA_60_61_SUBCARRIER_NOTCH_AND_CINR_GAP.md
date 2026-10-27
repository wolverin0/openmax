<!-- doc-head: STAGE454A_GUARIDA_60_61_SUBCARRIER_NOTCH_AND_CINR_GAP.md preserved document content -->
<!-- /doc-head -->



# Stage 454A — 5-Snapshot Temporal Read-Only Audit of `Almafuerte (.60) <-> Guarida-BH (.61)` `64`-Element `rx.evm` / `tx.evm` Arrays & `256-QAM` (`MCS 8`) Downshift

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`hardware` + `proprietary airMAX/LTU module` + `QCA firmware`, `0` writes performed).
- **Binary Dissection (`ubnt_poll_host.ko`)**:
  - `ubnt_poll_host_on_rx_evm_meas` (`.text + 0x00a3c4`, `292` B) jumps to `0x006b60`, which maintains a `64`-byte circular history per chain at `sta + 0x0b7` (`Chain 0`), `sta + 0x0f7` (`Chain 1`), `sta + 0x137` (`Chain 2`), and `sta + 0x177` (`Chain 3`) for RX (`$a3=0`) and `+0x103` (`259` B) stride for TX (`$a3=1`), indexed by sequence byte `sta + 0x0b5` and configured via `ubnt_poll_host_set_evm_meas_config` (`0x00b46c`).
- **5-Snapshot Temporal Finding (`22.32 s` window across `.60` and `.61`)**:
  1. **Stationary Polarization-Selective Multipath Asymmetry**:
     - On `Guarida-BH (.61)` RX, `chainrssi` is `[39, 41] -> [38, 39] -> [39, 40] -> [37, 39] -> [38, 40]` (`\le 2\text{ dB}` difference), yet **Chain 1 EVM is flat at `40.48 dB` (`min = 39 dB`, `0/64` samples `< 27 dB`)** while **Chain 0 EVM is locked at `31.19 dB` (`-9.29 dB` gap, `min = 22 dB`, `7.0/64` samples `< 27 dB`)**.
     - On `Almafuerte (.60)` RX, `chainrssi` is `[40, 38]` (Chain 0 RSSI is `+2 dB` *stronger* than Chain 1!), yet **Chain 0 EVM is `29.85 dB` (`-8.34 dB` worse than Chain 1's flat `38.19 dB`, `min = 25 dB`, `9.0/64` samples `< 27 dB`)**!
  2. **Direct `256-QAM` (`MCS 8`) Rate-Control Downshift**:
     - Because `2x2` MIMO `MCS 8` (`256-QAM 3/4`) requires `>= 27..28 dB` CINR/EVM on *both* spatial streams, Chain 0's recurrent `22..25 dB` dips force **`32.26%` of all `Almafuerte (.60) -> Guarida-BH (.61)` DL frames (`29,598,236` of `91,733,048` frames)** down to `MCS 7` (`64-QAM 5/6`, `144.4 Mbps`), visibly oscillating the live link rate between `144.4 Mbps`, `156.0 Mbps`, and `173.3 Mbps` across the 5 snapshots.

---

## 2. 5-Snapshot Temporal Comparison (`.60` vs `.61`)

| Radio & Direction | `chainrssi` (`Ch0 / Ch1`) | `Chain 0` Mean EVM | `Chain 0` Min EVM | `Chain 1` Mean EVM | `Chain 1` Min EVM | `Ch0 - Ch1` EVM Gap | Samples `< 27 dB` (`Ch0` vs `Ch1`) | `MCS 7` (`64-QAM`) Downshift Share |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: | :---: | ---: |
| **`.60` RX (UL from `.61`)** | `40 / 38 dB` | `29.85 dB` | `25 dB` | **`38.19 dB`** | `37 dB` | **`-8.34 dB`** | `9.0 / 64` vs `0 / 64` | `6.11%` (`4.40M / 72.02M`) |
| **`.61` RX (DL from `.60`)** | `38 / 40 dB` | `31.19 dB` | **`22 dB`** | **`40.48 dB`** | `39 dB` | **`-9.29 dB`** | `7.0 / 64` vs `0 / 64` | **`32.26%` (`29.60M / 91.73M`)** |

---

## 3. Verification & Reproducibility
- **Script**: [`audit_stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/observability/audit_stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.py)
- **Artifacts**:
  - [`stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json)
  - [`stage454a_guarida_60_61_5snapshot_cache.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage454a_guarida_60_61_5snapshot_cache.json)
- **Test Suite**: [`test_stage454a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage454a.py)
