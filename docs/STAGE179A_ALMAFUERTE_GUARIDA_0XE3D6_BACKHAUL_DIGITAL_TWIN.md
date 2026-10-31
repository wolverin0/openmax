<!-- doc-head: STAGE179A_ALMAFUERTE_GUARIDA_0XE3D6_BACKHAUL_DIGITAL_TWIN.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 179A — `Almafuerte (.60) <-> Guarida (.61)` (`3.75 km` `PBE-5AC-Gen2` `0xe3d6`) Digital Twin & `SimPy`/`Pymoo` Model

## 1. Live Read-Only Telemetry Baseline (`CONFIRMED`, `0` Writes)

| Parameter | `198.18.0.3` (`Ap.Guarida`, Almafuerte) | `198.18.0.4` (`St.Guarida`, Guarida) | Attribution / Notes |
| :--- | :--- | :--- | :--- |
| **Model / `board.sysid`** | `PowerBeam 5AC Gen2` (`0xe3d6`) | `PowerBeam 5AC Gen2` (`0xe3d6`) | `AR9342` `64 MB` + `QCA9882` (`ubnthal.ko`) |
| **MAC / Role** | `PUBLIC_DEVICE_0072` (`ap-ptp`) | `PUBLIC_DEVICE_0073` (`sta-ptp`) | Stock `WA.v8.7.25` (`uph.ko` `FF` mode) |
| **Link Distance** | `3,750 m` (`ack=49`) | `3,750 m` (`ack=49`) | `12.50 us` 1-way / `25.00 us` 2-way air propagation |
| **Signal / Noise / CINR** | `-53 dBm` / `-88 dBm` / `30 dB` | `-54 dBm` / `-89 dBm` / `30 dB` | Chains: `[39, 39]` dB (`0 dB` delta) |
| **PHY Rate (`VHT20`)** | `173.3 Mbps` (`MCS 8` `2x2`) | `173.3 Mbps` (`MCS 8` `2x2`) | Maximum `20 MHz` `256-QAM` `5/6` rate |
| **airMAX Capacity (`cb/dl/ul`)** | `103.6 / 94.9 / 112.3 Mbps` | `113.1 / 112.3 / 113.9 Mbps` | Carries all `32` Guarida CPEs (`Panel1..3`) |

## 2. Long-Distance (`3.75 km`) Slot & ACK Timing Calibration (`CONFIRMED`)

- **Physical Propagation**: At $d = 3,750\text{ m}$, 1-way air propagation is $\tau_{1w} = 12.50\text{ }\mu\text{s}$ and 2-way round-trip air propagation is $\tau_{2w} = 25.00\text{ }\mu\text{s}$.
- **Optimal `mac80211` / `ath10k` Distance Knob**:
  - Setting `iw phy phy0 set distance 4050` ($3,750\text{ m} + 300\text{ m}$ margin) programs `coverage_class = 5` (`slottime = 22 us` effective, `ack_timeout = 54 us`), preventing premature ACK timeouts and hidden-slot collisions across the `3.75 km` link.

## 3. `SimPy` + `Pymoo` NSGA-II Pareto Regimes (`32` Downstream Guarida CPEs)

| Regime | Width | PHY (Mbps) | TCP Goodput (Mbps) | Unloaded `p50` (ms) | Loaded `32-CPE` `p50 / p95 / p99` (ms) | VoIP MOS | `fmx_loss` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`R0` Stock `WA.v8.7.25`** (`CONFIRMED`) | `20 MHz` | `173.3` | `108.4` (`94.9 DL`) | `1.85` | `14.20 / 28.60 / 44.10` | `4.08` | `0.312` |
| **`R1` Mode B (`rc.poststart`)** (`INFERRED`) | `20 MHz` | `173.3` | `118.6` (`106.2 DL`) | `1.62` | `8.90 / 16.40 / 24.80` | `4.29` | `0.194` |
| **`R2` OpenWrt `24.10.4` Champion `v2`** (`INFERRED`) | `20 MHz` | `173.3` | `134.8` (`124.5 DL`) | `1.18` | `4.15 / 7.80 / 11.40` | `4.41` | `0.108` |
| **`R3` OpenWrt `24.10.4` Champion `v2`** (`INFERRED`) | `40 MHz` | `400.0` | `268.4` (`246.0 DL`) | `0.94` | `2.65 / 5.10 / 7.90` | `4.46` | `0.062` |

## 4. Two-Step Remote OTA Conversion & Rollback Architecture (`SG-01..05`)

1. **Zero-Flash Immediate Gain (`R1`)**: Apply `rc.poststart` (`vm.min_free_kbytes=4096`, `netdev_max_backlog=2048`) on `.60` and `.61` during maintenance window if staying on Stock `airOS 8`.
2. **Two-Step Remote OTA Conversion (`R2`/`R3`)**:
   - **Step 1 (Hybrid WDS)**: Enable `allow_80211=1` + `op_mode=0` on `Almafuerte (.60)`, flash remote `Guarida (.61)` OTA with SquashFS-repacked `openwrt-24.10.4-ath79-generic-ubnt_powerbeam-5ac-gen2-squashfs-factory.bin` (`99-fmx-pbe5ac-ptp-sta` + `fmx_ptp_rollback_watchdog.sh` `45s` Non-DFS / `120s` DFS).
   - **Step 2 (Full OpenWrt PtP)**: Once `.61` associates to `.60` and passes ping/iperf3, flash local `Almafuerte (.60)` with `99-fmx-pbe5ac-ptp-ap` (`fq_quantum=3028`, `aql_threshold=4000`, `distance=4050`).
