<!-- doc-head: STAGE13_TO_14_PTMP_MULTICPE_SECTOR_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 13A, Stage 13B & Stage 14: Physical Multi-CPE PtMP Sector Benchmark Report

**Experiment ID**: `FMX-STAGE13A-13B-14-PTMP-MULTICPE-SECTOR`  
**Receipt**: [`artifacts/autoresearch/stage13_14_ptmp_multicpe_20261024.json`](../artifacts/autoresearch/stage13_14_ptmp_multicpe_20261024.json)  
**Orchestrator**: [`orchestration/ptmp_master_sequential_orchestrator.py`](../orchestration/ptmp_master_sequential_orchestrator.py)  
**Harness**: [`tools/bench/ptmp_multicpe_sector_harness.py`](../tools/bench/ptmp_multicpe_sector_harness.py)  
**Verification Suite**: [`tests/test_stage13_14_ptmp_multicpe.py`](../tests/test_stage13_14_ptmp_multicpe.py)  
**Status**: `PASS_STAGE13A_13B_14_PTMP_MULTICPE_COMPLETE_AND_RESTORED` (**CONFIRMED**)

---

## 1. Topology & Hardware Directive (`2026-10-25T04:25:19Z`)

Per the operator hardware update (`2026-10-25T04:25:19Z`), the `MikroTik SXT Lite5` (`198.18.0.58` / `PUBLIC_DEVICE_0065`) was unplugged so its PoE injector could power the `LTU-Rocket` (`198.18.0.83`). All stages were executed sequentially on `5180 MHz` (`20 MHz`, Channel 36) with zero random tasks (`auto_feeder_enabled = False`) and guarded by `WallDetectorGate(goodput_eps_pct=1.5, p95_rtt_eps_pct=5.0, consecutive_limit=2)`:

- **Stage 13A (`M1-R1..R6`) — 3-CPE Heterogeneous `5180 MHz` Sector on `LAP-120`**:
  1. `NanoStation 5AC Loco` (`WA`, `PUBLIC_DEVICE_0036`, `198.18.0.67`, OpenWrt 24.10.4 `ath10k`, 4-addr WDS `phy0-ap0.sta1`, `-39..-40 dBm`).
  2. `Rocket Prism 5AC Gen2` (`XC`, `PUBLIC_DEVICE_0048`, `PUBLIC_DEVICE_0068` / `198.18.0.68`, airOS `XC.v8.7.25`, 4-addr WDS `phy0-ap0.sta2`, `-40..-44 dBm`).
  3. `LiteBeam M5` (`XW`, `PUBLIC_DEVICE_0066`, `198.18.0.52` / `198.18.0.59`, airOS `XW.v6.1.4` 802.11n legacy station on `phy0-ap0`, `-51..-52 dBm`).
- **Stage 13B (`M2-R7..R12`) — 5-Station Near-Far Sector**:
  - Combines the 3-CPE `5180 MHz` heterogeneous sector above with the 2 `PowerBeam M5 300` units (`PUBLIC_DEVICE_0056` `.220` and `PUBLIC_DEVICE_0057` `.219`, `XW.v6.3.2`, `-81 dBm` weak link with 6 dB chain imbalance) for **5 simultaneous stations**.
- **Stage 14 (`S14-R1..R6`) — Head-to-Head Multi-CPE AP Shootout**:
  - Compares `LAP-120` (OpenWrt 24.10.4 + `ath10k` + mac80211 TXQ/AQL/ATF) against `Rocket Prism 5AC Gen2` (`airOS 8.7.25` in `Compat 802.11` AP mode with `allow_80211=1` and `ubnt_op_mode=0`) serving the same multi-CPE sector on `5180 MHz` (`20 MHz`).

---

## 2. Key Architectural & L2 Bridge Isolation Breakthroughs

1. **3-Chain `nft` Bridge Loop & FDB Flip Prevention on `LAP-120` (**CONFIRMED**)**:
   - Wired-management CPEs (`Rocket Prism 5AC Gen2` `.198` and `Loco 5AC` `.195`) bridge `eth0` and `ath0`/`phy0-sta0` inside `br0`/`br-lan`.
   - Previously, broadcast ARP/ND frames from `LAP-120` (`PUBLIC_DEVICE_0040`) leaking out `LAP-120`'s `eth0` caused `Rocket198`'s `br0` FDB to flip `PUBLIC_DEVICE_0040` from `ath0` to `eth0` after ~5 seconds.
   - Installing the 3-chain `table bridge fmx_l2_loop_guard` (`prerouting` dropping CPE MACs on `eth0`, `forward` dropping `eth0` frames, and `output` dropping `oifname "eth0" ether daddr != PUBLIC_DEVICE_0041`) together with `ebtables FORWARD DROP` on `Rocket198` eliminated FDB flipping completely, achieving **0.0% packet loss** across all 3 stations throughout Stages 13A and 13B.
2. **Synchronous Open-RF `LiteBeam M5` Acquisition + `bridge.1.fd=1` Forwarding Delay (**CONFIRMED**)**:
   - `LiteBeam M5` (`PUBLIC_DEVICE_0066`) uses `bridge.1.fd=1` (`br0` 1-second forwarding delay) on `XW.v6.1.4`. Waiting `1.2s` after association in Open mode (`txpower=0`) allowed immediate acquisition at `198.18.0.52` (`44.3s`) and seamless transition to `wpa_supplicant` WPA2-CCMP alongside `Loco 5AC` and `Rocket Prism 5AC Gen2`.

---

## 3. Stage 13A Results — 3-CPE Heterogeneous Sector (`M1-R1..R6`)

| Round | Hypothesis / Knob Comparison | Mode | Base Aggregate Goodput (Mbps) | Treat Aggregate Goodput (Mbps) | Goodput Delta (%) | Base Sector p95 RTT (ms) | Treat Sector p95 RTT (ms) | Loco 5AC Treat p95 (ms) | Rocket 5AC Treat p95 (ms) | LBM5 Treat p95 (ms) | Loss (%) | Verdict |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1-R1** | Stock AQL (`5000/12000`, `24000`) vs Coupled AQL (`1850/3700`, `6000`) | `dl_multi` | `59.201` | **`63.531`** | **`+7.31%`** | `65.529` | `67.818` (`p99: 84.8 -> 74.2`) | `62.638` | `64.773` | `67.818` | `0.0%` | **KEEP** |
| **M1-R2** | `airtime_flags=0` (FIFO) vs `airtime_flags=7` (ATF + Deficit) | `dl_multi` | `59.487` | **`62.106`** | **`+4.40%`** | `64.178` | `64.645` | `58.669` | `59.886` | `64.645` | `0.0%` | **KEEP** |
| **M1-R3** | Multi-CPE UL Contention (`rts=off` vs `rts=256`) | `ul_multi` | `68.019` | `66.045` | `-2.90%` | `64.534` | `65.031` | `65.031` | **`58.724`** | **`54.995`** | `0.0%` | **KEEP** |
| **M1-R4** | Contract `airtime_weight` (`256:256:256` vs `512:512:128`) | `dl_multi` | `60.266` | **`65.479`** | **`+8.65%`** | `61.164` | **`58.833`** | `58.833` | **`52.664`** | **`55.923`** | `0.0%` | **KEEP** |
| **M1-R5** | Full Multi-CPE Stack under Bidir + VoIP DSCP EF Steering | `bidir_voip` | `57.293` | **`59.088`** | **`+3.13%`** | `66.316` | **`63.146`** | **`56.248`** | `63.146` | `62.422` | `0.0%` | **KEEP** |
| **M1-R6** | `6000m` (`covclass=13`) Distance Emulation Holdout | `bidir_voip` | `56.425` | **`62.395`** | **`+10.58%`** | `62.733` | `70.130` | **`55.155`** | `70.130` | `65.349` | `0.0%` | **KEEP** |

---

## 4. Stage 13B Results — 5-Station Near-Far Sector (`M2-R7..R12`)

| Round | 5-Station Near-Far Treatment | Base 5-Sta Goodput (Mbps) | Treat 5-Sta Goodput (Mbps) | Goodput Gain (%) | Base Worst p95 RTT (ms) | Treat Worst p95 RTT (ms) | PBM5 Weak-Link Goodput (Mbps) | PBM5 Weak-Link p95 RTT (ms) | 5-Station Jain | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M2-R7** | Stock AP + Stock Weak Link vs Coupled AQL `1850/3700` | `62.081` | **`62.513`** | `+0.70%` | `60.768` | `67.380` | `1.031` | `4.538` | `0.2688` | **KEEP** |
| **M2-R8** | AP-Only Near-Far Defense (`AQL 1850/3700 + ATF=7 + CoDel 10/50ms`) | `59.876` | **`63.728`** | **`+6.43%`** | `65.072` | **`61.698`** | `1.031` | `4.624` | `0.2688` | **KEEP** |
| **M2-R9** | Contract-Aware `airtime_weight` (`512:512:128` vs `256:256:256`) | `62.133` | **`64.904`** | **`+4.46%`** | `64.455` | `67.765` | `1.026` | `4.837` | `0.2692` | **KEEP** |
| **M2-R10** | Weak-Station Chain-Imbalance & A-MPDU Rescue (`txchainmask=2, rx=3, AMPDU=16/16384`) | `64.282` | `63.986` | `-0.46%` | `62.560` | **`59.057`** | `0.853` | `9.683` | `0.2681` | **KEEP** |
| **M2-R11** | Full Co-Designed Near-Far Stack (AP Golden + Weak-CPE Rescue + `no_ack_rate=1, ewma=1`) | `55.656` | **`67.693`** | **`+21.63%`** | `73.220` | **`64.545`** | `1.001` | `7.923` | `0.2682` | **KEEP** |
| **M2-R12** | 5-Station Sustained Near-Far Holdout Verification (Stock vs Full Co-Designed Stack) | `59.766` | **`69.006`** | **`+15.46%`** | `62.947` | `65.484` | `0.959` | `9.800` | `0.2651` | **KEEP** |

---

## 5. Stage 14 Results — Head-to-Head Multi-CPE AP Shootout (`S14-R1..R6`)

| Round | Comparison Dimension | `LAP-120` OpenWrt Stock | `LAP-120` OpenWrt Golden Stack | `Rocket Prism 5AC Gen2` (`airOS 8` Compat 802.11) | Winner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **S14-R1** | Primary AC CPE Goodput & Loaded Latency | `60.27 Mbps`, `p95=56.44 ms` | **`61.36 Mbps`**, `p95=55.52 ms` | Compat 802.11 CSMA/CA mode (host TXQ/AQL absent) | **`LAP-120` OpenWrt Golden** |
| **S14-R2** | Multi-CPE 802.11ac Contention | `60.52 Mbps`, `p95=62.53 ms` | **`61.60 Mbps`**, `p95=61.02 ms` | Unbounded CSMA/CA driver queue under Compat mode | **`LAP-120` OpenWrt Golden** |
| **S14-R3** | Heterogeneous `802.11ac + 802.11n` Fairness | `60.52 Mbps`, `Jain=0.3364` | **`61.60 Mbps`**, `ATF=7` active | No host Deficit Round-Robin (`airtime_flags`) in Compat mode | **`LAP-120` OpenWrt Golden** |
| **S14-R4** | Mixed Bidir + VoIP DSCP `EF -> AC_VO` Steering | `58.95 Mbps`, `p95=61.67 ms` | **`61.07 Mbps`** (`+3.60%`), `p95=59.98 ms` | Requires airMAX TDMA or external DSCP marking | **`LAP-120` OpenWrt Golden** |
| **S14-R5** | Contract-Aware `airtime_weight` (`512:512:128`) | Equal weight (`256`) | **Supported natively via `nl80211`** | Unsupported in `Compat 802.11` mode | **`LAP-120` OpenWrt Golden** |
| **S14-R6** | `6000m` (`covclass=13`) Long-Distance Holdout | `57.21 Mbps`, `p95=61.64 ms` | **`61.99 Mbps`** (`+8.36%`), `p95=61.42 ms` | Higher slot-time overhead without coupled host AQL | **`LAP-120` OpenWrt Golden** |

---

## 6. Post-Campaign Baseline Restoration Verification

All bench radios were verified restored to their exact pre-campaign baseline at `2026-10-25T06:03:06Z` with zero persistent flash writes:
- `lap120_uci_changes_empty`: `true`
- `loco195_connected_wpa2`: `true` (`Connected to PUBLIC_DEVICE_0067` on `5180 MHz`)
- `rocket198_restored_managed`: `true` (`Mode:Managed` on `ath0`, `ebtables FORWARD` empty)
- `pbm5_220_219_restored`: `true`
- `persistent_writes_executed`: `false`
