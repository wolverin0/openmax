<!-- doc-head: STAGE12_DYNAMIC_ATPC_AND_MCS_CEILING_CONTROLLER.md preserved document content -->
<!-- /doc-head -->


# Stage 12 — Closed-Loop Per-CPE Dynamic ATPC (TX-Power) & MCS Ceiling Controller (`1 km .. 14 km`)

- **Task ID**: `T-ORCA-GEM1-03` (`orca:gemini-lane1`)
- **Controller Module**: [`controller/dynamic_atpc_mcs_controller.py`](../controller/dynamic_atpc_mcs_controller.py)
- **Verification Test Suite (`5/5 PASS`)**: [`tests/test_dynamic_atpc_mcs_controller.py`](../tests/test_dynamic_atpc_mcs_controller.py)
- **Safety Gate**: `automatic_execution_allowed = False` (100% offline/advisory; requires operator & Canary gate approval before live execution).

---

## 1. Executive Summary & Epistemic Ledger

In mixed-distance outdoor PtMP sectors (`0.5 km .. 14.0 km`), leaving CPE transmit power at static maximum (`22..24 dBm`) and leaving `802.11ac` VHT rate control free to probe `MCS 8/9` (`256-QAM`) across all stations creates two severe, mutually compounding sector pathologies:

1. **Close-In CPE AP LNA Saturation (`AP RX RSSI > -48 dBm`)**:
   - Close CPEs (`0.5 .. 1.8 km`) transmitting at `24 dBm` conducted power through `16..23 dBi` directional dishes arrive at the AP sector antenna at **`-38 to -45 dBm`**, exceeding the QCA988x LNA/mixer 3rd-order intermodulation threshold (`-48 dBm`).
   - During a close CPE's uplink A-MPDU burst, the AP receiver's Automatic Gain Control (AGC) steps in `6..15 dB` of front-end attenuation, deafening the AP to concurrent or immediately following `RTS` frames and poll responses from distant CPEs (`-65 to -74 dBm`).
2. **Distant / Fading CPE Upper-MCS Flapping (`1 km .. 14 km`, `covclass = 2 .. 31`)**:
   - Standard `ath10k` / `airOS` rate control periodically probes 1–2 MCS tiers above a station's sustainable CINR and chain-imbalance ceiling (e.g., probing `MCS 8/9` `256-QAM` when usable CINR is `< 26.5 dB`, when conducted PA power `>= 23 dBm` degrades PA EVM, or when H/V chain imbalance reaches `8..10 dB` as on `GALEANO`).
   - Because coverage-class slot time $\sigma(d) = 9 + 3c(d)\text{ }\mu\text{s}$ and `ACK/CTS_Timeout` $= 18 + 6c(d)\text{ }\mu\text{s}$ scale linearly with distance (`18/36 µs` at `1 km` vs `102/204 µs` at `14 km`), a single failed high-MCS A-MPDU probe at `9..14 km` wastes **`1.2 to 2.1 ms` of sector airtime** and plunges OpenWrt `mac80211` into a negative `Deficit: BE` spiral (`-67,099 µs`).

### Epistemic Classification (`AGENTS.md` Sections 2 & 6)

| Claim / Mechanism | Status | Evidence Anchor |
| :--- | :--- | :--- |
| `ubnt_poll_host.ko` implements `/proc/sys/dev/uph_<radio>/atpc` (`<en> <target_rssi> <min_pwr> <max_pwr>`) and `ptmp_netconf` offsets `+87` (`atpc_target_rssi`), `+100` (`atpc_max_power`), `+101` (`atpc_min_power`) | **CONFIRMED BY STATIC RE** | [`docs/STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md`](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md) (§3.2, §4.1) |
| `_retr_supression_levels` (`0xea4` in `ubnt_poll_host.ko`, indexed by `cms_bias = 0..9`) and `/proc/sys/dev/uph_<radio>/ro` control Mode B retry suppression and rate overrides | **CONFIRMED BY STATIC RE** | [`docs/STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md`](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md) (§3.2, §4.2) |
| Coverage-class timing inflation across `1 km .. 14 km` (`covclass = 2 .. 31`, `slot_time = 15 .. 102 µs`, `ACK_TO = 30 .. 204 µs`) amplifies the airtime cost of every retry and backoff slot | **CONFIRMED ON BENCH** | [`docs/STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md`](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md), [`docs/STAGE12_HIDDEN_NODE_CROSSOVER_BOUNDARY_AUDIT.md`](STAGE12_HIDDEN_NODE_CROSSOVER_BOUNDARY_AUDIT.md) |
| High H/V chain imbalance (`GALEANO` `10 dB` on Guarida `Panel3`) and weak edge links (`FRANCO_Debora` `-70 dBm`, `SEVERO` `-74 dBm` on `Panel2`) cause harmonic sector airtime collapse when probing upper MCS | **CONFIRMED ON PRODUCTION TELEMETRY** | [`docs/STAGE12_GUARIDA_32CPE_TELEMETRY_AND_MODE_B_OPTIMIZER.md`](STAGE12_GUARIDA_32CPE_TELEMETRY_AND_MODE_B_OPTIMIZER.md) |
| Closed-loop joint ATPC (`<= -48 dBm` ceiling, `-52 dBm` target) + distance/imbalance/PA-EVM MCS ceiling law across `1 km .. 14 km` | **INFERRED / MODELED** | [`controller/dynamic_atpc_mcs_controller.py`](../controller/dynamic_atpc_mcs_controller.py), [`tests/test_dynamic_atpc_mcs_controller.py`](../tests/test_dynamic_atpc_mcs_controller.py) |

---

## 2. Closed-Loop Control Laws

### 2.1 Law 1 — Hard `-48 dBm` LNA Protection & `-52 dBm` ATPC Target Regulation

For each CPE $i$ with current conducted TX power $P_{\text{TX},i} \in [P_{\min}, P_{\max}]$ (`4..24 dBm`), regulatory EIRP cap $P_{\text{EIRP\_cap},i} = \lfloor \text{EIRP}_{\max} - G_{\text{CPE},i} \rfloor$, and measured AP RX RSSI $R_{\text{AP},i}$:

1. **Immediate LNA Saturation Cut ($R_{\text{AP},i} > -48.0\text{ dBm}$)**:
   Whenever a close CPE exceeds the `-48.0 dBm` AP LNA saturation ceiling, the controller bypasses slow step-down limits and immediately cuts CPE TX power in a single step to bring predicted AP RX RSSI to the `-52.0 dBm` target:
   $$P_{\text{TX},i}^{\text{next}} = \max\!\left(P_{\min},\; P_{\text{TX},i} - \left\lceil R_{\text{AP},i} - (-52.0) \right\rceil\right)$$
2. **Damped Deadband Regulation ($R_{\text{AP},i} \le -48.0\text{ dBm}$)**:
   Within the target deadband $[-53.5, -50.5]\text{ dBm}$ (`-52.0 ± 1.5 dB`), TX power is held constant to prevent power hunting. Below `-53.5 dBm`, TX power steps up by at most `+3 dB` per cycle toward $\min(P_{\max}, P_{\text{EIRP\_cap},i})$.
3. **PA Linearity Backoff Cap**:
   If predicted UL CINR is $\ge 30\text{ dB}$ and AP RX RSSI remains $\ge -55\text{ dBm}$, conducted CPE TX power is capped at `18 dBm` (`20 dBm` for `CINR >= 25 dB`) so QCA988x PA EVM distortion never limits `256-QAM` (`MCS 8/9`) decoding.

### 2.2 Law 2 — Distance-, Chain-Imbalance-, and PA-EVM-Guarded MCS Ceiling (`1 km .. 14 km`)

The controller computes usable uplink and downlink CINR by subtracting three physical penalty terms from raw $\text{CINR}_i$:
$$\text{CINR}_{\text{usable},i}(d) = \text{CINR}_i - \Delta_{\text{dist}}(d) - \Delta_{\text{imb}}(\Delta_{\text{chain},i}) - \Delta_{\text{flap}}(\text{PER}_i, f_{\text{flap},i})$$

where:
- **Distance Timing & Multipath Guard**: $\Delta_{\text{dist}}(d) = \min(4.0,\; 0.28\,(d_{\text{km}} - 1.5))\text{ dB}$ for $d > 1.5\text{ km}$ (`0.0 dB` at `1.0..1.5 km`, rising to `+3.50 dB` at `14.0 km`), accounting for coverage-class slot inflation ($\sigma(d) = 18..102\text{ }\mu\text{s}$) and outdoor delay spread.
- **Chain-Imbalance Penalty**: $\Delta_{\text{imb}} = 0.65 \max(0,\; \Delta_{\text{chain},i} - 2.0)\text{ dB}$. Furthermore, if $\Delta_{\text{chain},i} \ge 8.5\text{ dB}$ (e.g., `GALEANO` `10 dB` mismatch), `256-QAM` (`MCS 8/9`) is hard-locked out (`MCS <= 6`); if $\Delta_{\text{chain},i} \ge 11.5\text{ dB}$ and $\text{CINR}_i < 18\text{ dB}$, spatial streams drop to `NSS = 1` (`1x1` SISO survival mode).
- **PER & Flap Hysteresis Guard**: $\Delta_{\text{flap}} = \min(4.0, 0.32\max(0, \text{PER}_i - 5\%)) + \min(4.0, 0.25\max(0, f_{\text{flap},i} - 2))\text{ dB}$.
- **PA EVM Ceiling**: When a distant CPE must transmit at `>= 23 dBm` conducted power to close the link budget, QCA988x PA nonlinearity caps sustainable modulation at `MCS 7` (`64-QAM 5/6`, `130 Mbps`).

---

## 3. Master 10-Point Distance Sweep Table (`1.0 km .. 14.0 km`)

Generated by [`evaluate_distance_sweep_1km_to_14km()`](../controller/dynamic_atpc_mcs_controller.py):

| Distance $d$ | Cov. Class $c(d)$ | Slot / ACK_TO ($\mu\text{s}$) | AP RX Before $\rightarrow$ After (dBm) | CPE TX Power Before $\rightarrow$ After (dBm) | LNA Saturation Status | UL MCS Before $\rightarrow$ Ceiling | Post-Ceiling UL PER (%) | Sector Airtime Saved (%) |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| **1.0 km** | `3` | `18 / 36 µs` | `-41.0 -> -52.0 dBm` | **`24 -> 13 dBm` (`-11 dB`)** | **`LNA_SATURATION_PREVENTED`** | `MCS 9 -> MCS 9` (`173.3 Mbps`) | `1.80%` | `0.00%` *(7.0 dB LNA overload removed)* |
| **1.5 km** | `4` | `21 / 42 µs` | `-45.0 -> -52.0 dBm` | **`24 -> 17 dBm` (`-7 dB`)** | **`LNA_SATURATION_PREVENTED`** | `MCS 9 -> MCS 9` (`173.3 Mbps`) | `1.80%` | `0.00%` *(3.0 dB LNA overload removed)* |
| **3.0 km** | `7` | `30 / 60 µs` | `-50.6 -> -50.6 dBm` | `24 -> 24 dBm` | `OPTIMAL_ATPC_WINDOW` | **`MCS 9 -> MCS 7`** (`130.0 Mbps`) | `1.69%` | **`+7.27%`** |
| **4.5 km** | `10` | `39 / 78 µs` | `-52.9 -> -52.9 dBm` | `24 -> 24 dBm` | `OPTIMAL_ATPC_WINDOW` | **`MCS 9 -> MCS 7`** (`130.0 Mbps`) | `2.05%` | **`+9.85%`** |
| **6.0 km** | `14` | `51 / 102 µs` | `-54.6 -> -54.6 dBm` | `24 -> 24 dBm` | `OPTIMAL_ATPC_WINDOW` | **`MCS 9 -> MCS 7`** (`130.0 Mbps`) | `2.41%` | **`+13.21%`** |
| **7.5 km** | `17` | `60 / 120 µs` | `-55.9 -> -53.9 dBm` | `22 -> 24 dBm` (`+2 dB`) | `OPTIMAL_ATPC_WINDOW` | **`MCS 9 -> MCS 7`** (`130.0 Mbps`) | `2.77%` | **`+16.58%`** |
| **9.0 km** | `20` | `69 / 138 µs` | `-57.0 -> -55.0 dBm` | `22 -> 24 dBm` (`+2 dB`) | `LINK_BUDGET_LIMITED` | **`MCS 9 -> MCS 7`** (`130.0 Mbps`) | `3.12%` | **`+20.34%`** |
| **10.5 km** | `24` | `81 / 162 µs` | `-57.9 -> -55.9 dBm` | `22 -> 24 dBm` (`+2 dB`) | `LINK_BUDGET_LIMITED` | **`MCS 8 -> MCS 7`** (`130.0 Mbps`) | `3.48%` | **`+25.05%`** |
| **12.0 km** | `27` | `90 / 180 µs` | `-58.7 -> -56.7 dBm` | `22 -> 24 dBm` (`+2 dB`) | `LINK_BUDGET_LIMITED` | **`MCS 8 -> MCS 6`** (`117.0 Mbps`) | `3.50%` | **`+30.60%`** |
| **14.0 km** | `31` | `102 / 204 µs` | `-59.6 -> -57.6 dBm` | `22 -> 24 dBm` (`+2 dB`) | `LINK_BUDGET_LIMITED` | **`MCS 8 -> MCS 5`** (`104.0 Mbps`) | `3.50%` | **`+38.87%`** |

---

## 4. OpenWrt (Mode A) & Stock `airOS 8` (Mode B) Command Synthesis

1. **Mode A (`OpenWrt + ath10k-ct`)**:
   - Applies VHT MCS ceiling via `iw dev phy0-ap0 set bitrates vht-mcs-5 <NSS>:0-<MCS_CEIL>` and coordinates CPE TX power (`iw dev wlan0 set txpower fixed <dBm_mBm>`) so close stations never exceed `-48 dBm` at the AP receiver.
2. **Mode B (`Stock airOS 8` `ubnt_poll_host.ko`)**:
   - Programs hardware ATPC directly via `/proc/sys/dev/uph_wifi0/atpc`:
     ```sh
     echo "1 -52 4 24" > /proc/sys/dev/uph_wifi0/atpc
     echo "5" > /proc/sys/dev/uph_wifi0/cms_bias
     ```
     which sets `atpc_target_rssi = -52 dBm` (`<= -48 dBm` ceiling), `atpc_min_power = 4 dBm`, `atpc_max_power = 24 dBm`, and enables level-5 retry suppression (`_retr_supression_levels[5]`: `dl_per_thresh_nr = 70%`, `ul_per_thresh_nr = 70%`, `txop_qual_thresh_nr_nb = 70%`).

---

## 5. Verification Receipt

- `pytest tests/test_dynamic_atpc_mcs_controller.py`: **`5/5 PASSED` (`100%`)**
