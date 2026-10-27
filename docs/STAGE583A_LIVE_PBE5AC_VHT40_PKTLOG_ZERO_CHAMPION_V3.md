<!-- doc-head: STAGE583A_LIVE_PBE5AC_VHT40_PKTLOG_ZERO_CHAMPION_V3.md preserved document content -->
<!-- /doc-head -->



# Stage 583A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) `VHT40` + `pktlog_filter=0x0` + `tcp_notsent_lowat=131072` Counterbalanced `PtP Champion v3`

## 1. Objective & Cross-Pollinated Architecture (`CONFIRMED`, attribution: `QCA firmware` + `ath10k` + `mac80211` + `Linux`)
- Cross-pollinates the `WA` (`QCA9882`) baseband and kernel discoveries onto the live `PowerBeam 5AC Gen2` (`0xe3d6`, `.241` AP $\leftrightarrow$ `.242` Remote OTA STA) pair in `VHT40` (`40 MHz`, `Channel 40 / 5200 MHz`, `bw=1`):
  1. **Zero-Overhead `ath10k` Packet Log Ring (`pktlog_filter=0x0`)**: Eliminates PCIe Copy Engine (`CE`) DMA ring copies for packet-log events (`0x40 -> 0x0`).
  2. **Relaxed Baseband Noise-Floor Calibration (`nf_cal_period=120`) & CCA/AGC Override (`0x29e00=0x13761320`)**: Reduces periodic off-air NF calibration stalls from `30s` to `120s` and sets `BB_timing_controls_1` (`0x00029e00`) to `0x13761320`.
  3. **TCP Socket & Netdev Queue Bounding**: `net.ipv4.tcp_notsent_lowat=131072`, `net.ipv4.tcp_comp_sack_delay_ns=250000`, `net.ipv4.tcp_early_retrans=4`, `tx_queue_len=1000`, and differentiated per-AC AQL (`VO=500/1000`, `VI=1000/1500`, `BE=1500/2000`, `BK=1000/1500`).
  4. **Clean `WMI_PEER_ASSOC_CMDID` `VHT40` Association (`wifi down; sleep 2; wifi up`) + Asymmetric `VHT LGI` (`pream=3, sgi=0, bw=1`)**: `AP 2x2 VHT-MCS 2` (`81.0 Mbps`) + `STA 1x1 VHT-MCS 2` (`40.5 Mbps`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Live Results (`CONFIRMED`)

| Window / Arm | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate (Mbps) | Full-MTU `1472B` Loss (%) |
| :--- | :---: | :---: | :---: | :---: |
| **`A1` (`VHT40` Baseline)** | `10.62` | `5.61` | `16.23` | `12.0%` |
| **`B1` (`PtP Champion v3`)** | **`16.96`** | **`8.51`** | **`25.47`** | **`0.0%`** |
| **`A2` (`VHT40` Baseline)** | `14.62` | `7.76` | `22.38` | `0.0%` |
| **`B2` (`PtP Champion v3`)** | **`14.46`** | **`8.44`** | **`22.90`** | `12.0%` |
| **`Arm A` Mean (`VHT40` Baseline)** | `12.62` | `6.69` | `19.30` | `6.0%` |
| **`Arm B` Mean (`PtP Champion v3`)** | **`15.71` (`+24.5%`)** | **`8.47` (`+26.6%` vs Arm A / `+135.3%` vs airOS)** | **`24.18` (`+25.3%` vs Arm A / `+6.1%` vs airOS)** | `6.0%` (`0.0%` in `B1`) |

- Script: [`run_stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.py`](../tools/benchmarks/run_stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.py)
- Receipt: [`stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.json`](../artifacts/autoresearch/stage583a_live_pbe5ac_vht40_pktlog_zero_champion_v3.json)
- Test: [`test_stage583a.py`](../tests/test_stage583a.py)
