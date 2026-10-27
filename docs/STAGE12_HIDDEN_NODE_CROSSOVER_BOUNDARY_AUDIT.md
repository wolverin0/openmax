<!-- doc-head: STAGE12_HIDDEN_NODE_CROSSOVER_BOUNDARY_AUDIT.md preserved document content -->
<!-- /doc-head -->


# Stage 12 Audit: Exact Hidden-Node & Distance Crossover Boundary Between Mode A (OpenWrt Tuned CSMA/CA) and Mode B (Stock airOS 8 TDMA Polling) Across $N=2..32$ CPEs and $d=1..14\text{ km}$

## 1. Executive Summary & Epistemic Ledger

This document audits the exact physical, MAC-timing, and queueing crossover boundary between:
- **Mode A (`OpenWrt Tuned CSMA/CA`)**: OpenWrt `mac80211` + `ath10k-ct` (`10.1.467-ct-com-full-014-96d543`) configured with:
  1. **`RTS/CTS = 256B`** (`iw phy0 set rts 256` — AP broadcasts sector-wide `CTS` frames that set the Network Allocation Vector (NAV) on all hidden CPEs, eliminating payload-length collisions),
  2. **Cooperative Asymmetric Per-AC AQL + ATF** (`AP BE = 1500/3000 µs`, `CPE BE = 2100/4200 µs`, `VO/VI = 600/1200 µs`, `airtime_flags=3`, `fq_quantum=256B`, `codel=10ms/50ms`, `TCP TSQ=128KB`), and
  3. **`WMM AC_VO DiffServ Deficit Bypass`** (`DSCP EF` classifying interactive/control packets into `AC_VO`, routing them through `Deficit: VO (+256 µs)` to bypass negative `Deficit: BE (-67,099 µs)` during rate fallback or hidden-node retries).
- **Mode B (`Stock airOS 8 TDMA Polling`)**: Ubiquiti `WA.v8.7.x` `ubnt_poll_host.ko` + `umac.ko` + `athwlan_AR9888v2_ptmp_ap_bin` / `ptmp_sta_bin` (`addradio` mode `1` autonomous TX suppression, centralized AP poll scheduling, `INFOTXQ`, `NO-TX-DETECT`, and `30s` missing-poll panic timer).

### Epistemic Classification (`AGENTS.md` Sections 2 & 6)

| Claim / Parameter | Status | Source Evidence |
| :--- | :--- | :--- |
| `ATF (airtime_flags=3) + AQL (1500/3000 µs)` cuts loaded `p50` RTT by `4.06x` (`51.35 -> 12.65 ms`) and TCP retransmits by `10x` (`158 -> 16`) at 3 dBm edge SNR | **CONFIRMED ON BENCH** | [`docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md`](STAGE7_MULTIVENDOR_PTMP_REPORT.md) (§7.2) |
| `RTS/CTS = 256B` under 3-station hidden-node UL contention boosts sector UL goodput by `+18.5%` (`150.40 -> 178.17 Mbps`) and weak NLOS CPE goodput by `3.07x` (`1.97 -> 6.03 Mbps`) | **CONFIRMED ON BENCH** | [`docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md`](STAGE7_MULTIVENDOR_PTMP_REPORT.md) (§7.3) |
| `WMM AC_VO DiffServ Deficit Bypass` (`Deficit: VO +256 µs` vs `Deficit: BE -67,099 µs`) cuts weak-station `p50` RTT by `21.0x` (`143.00 -> 6.80 ms`) and strong-station `p95` RTT by `3.84x` (`31.30 -> 8.15 ms`) | **CONFIRMED ON BENCH** | [`docs/STAGE7_MULTIVENDOR_PTMP_REPORT.md`](STAGE7_MULTIVENDOR_PTMP_REPORT.md) (§7.4) |
| Cooperative Asymmetric AP/CPE AQL (`AP=1500 µs`, `CPE=2100 µs`) across 11 declared timing distances (`100 m .. 15,000 m`, `class 0..33`) boosts bidirectional UL goodput by `+41%..+59%` (`16.19 -> 24.41 Mbps` at `1.5 km`; `10.76 -> 17.08 Mbps` at `13.5 km`) while cutting `p95` RTT from `45–53 ms` to `14.25–21.73 ms` | **CONFIRMED ON BENCH** | [`docs/COOPERATIVE_CPE_FEASIBILITY.md`](COOPERATIVE_CPE_FEASIBILITY.md), [`docs/STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md`](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md) |
| Stock `airOS 8` TDMA disables autonomous CPE TX (`addradio` mode `1`) and uses AP poll frames (`ubnt_poll_host.ko` + `athwlan_AR9888v2_ptmp_ap_bin`), `INFOTXQ`, `NO-TX-DETECT`, and a `30s` missing-poll watchdog (`.text+0x7c08`) | **CONFIRMED BY STATIC RE** | [`knowledge/RADIO_FIRMWARE_ANALYSIS.md`](../knowledge/RADIO_FIRMWARE_ANALYSIS.md), [`docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md`](STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md) |
| Coupled Bianchi + hidden-node `RTS` vulnerability window $T_{\text{vuln}}(d)$ + coverage-class slot inflation $\sigma(d)$ vs. TDMA polling turnaround overhead across $N=4..32$ CPEs and outdoor physical propagation $d=1..14\text{ km}$ | **INFERRED / MODELED** | [`analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py`](../analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py), [`artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json`](../artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json) |
| Real outdoor multi-kilometer multipath/ducting over $N > 4$ physical CPEs | **UNKNOWN (UNMEASURED)** | Requires physical sector field trial |

---

## 2. Fundamental Physical Asymmetry: Slot-Multiplied Propagation Delay (Mode A) vs. Once-Per-Poll Propagation Delay (Mode B)

### 2.1 Distance-to-Timing Law ($d \in [1..14]\text{ km}$)

At distance $d$ (in km), the one-way air propagation delay is $\tau(d) = \frac{1000\,d}{c_0} \approx 3.3356\text{ }\mu\text{s/km} \times d_{\text{km}}$, and the round-trip propagation delay is $2\tau(d) \approx 6.6713\text{ }\mu\text{s/km} \times d_{\text{km}}$.

In OpenWrt `mac80211` / `ath10k`, setting `iw phy phy0 set distance <d_m>` programs coverage class $c(d) \approx \lfloor d_{\text{m}} / 450 \rfloor$, which stretches **every CSMA/CA backoff slot** and **every ACK/CTS timeout**:
$$\sigma(d) = 9 + 3\,c(d)\text{ }\mu\text{s}, \qquad \text{ACK\_TO}(d) = \text{CTS\_TO}(d) = 18 + 6\,c(d)\text{ }\mu\text{s}$$

### 2.2 Why Mode A (`CSMA/CA + RTS/CTS 256B`) Degrades Super-Linearly with $(N \times d)$

Even though `RTS/CTS = 256B` eliminates collisions on the `1450–1550 µs` A-MPDU data payload (because the AP's broadcast `CTS` sets the NAV on all CPEs across the sector), Mode A faces **two compounding physical penalties** as $N$ and $d$ increase:

1. **Hidden-Node `RTS` Vulnerability Window ($T_{\text{vuln}}(d)$)**:
   Mutually hidden CPEs (fraction $\alpha_{\text{HN}} \in [0, 1]$ of station pairs) cannot hear each other's `20 µs` `RTS` preamble. They remain blind until the first bit of the AP's `CTS` arrives back at their antenna:
   $$T_{\text{vuln}}(d) = T_{\text{RTS}} (20\text{ }\mu\text{s}) + \text{SIFS} (16\text{ }\mu\text{s}) + 2\tau(d) = 36 + 6.6713\,d_{\text{km}}\text{ }\mu\text{s}$$
   From $d = 1\text{ km}$ to $d = 14\text{ km}$, $T_{\text{vuln}}(d)$ grows from **`42.7 µs` to `129.4 µs`**. Any hidden contender whose backoff counter reaches zero within $T_{\text{vuln}}(d)$ transmits a colliding `RTS`.

2. **Slot-Multiplied Propagation Tax ($\sigma(d) \times \bar{W}(N_{\text{eff}}, p_c)$) & `CTS_Timeout(d)`**:
   In CSMA/CA, every single backoff slot must be at least $\sigma_0 + 2\tau_{\max}(d) = 9 + 3c(d)\text{ }\mu\text{s}$ so all stations can sense whether the previous slot became busy before decrementing their backoff counter by 1.
   - Consequently, **CSMA/CA pays the round-trip propagation delay $2\tau(d)$ on every single backoff slot** ($\text{AIFSN}_{\text{BE}} + \bar{W}_0 = 10.5$ times per frame even with zero collisions, and $25\text{--}60+$ times per frame under binary exponential backoff!).
   - Furthermore, every colliding `RTS` wastes:
     $$T_{\text{coll},A}(d) = T_{\text{RTS}} (20\text{ }\mu\text{s}) + \text{CTS\_TO}(d) + \text{AIFS}_{\text{BE}}(d)$$
     At $d = 14\text{ km}$ ($c = 31$, $\sigma = 102\text{ }\mu\text{s}$, $\text{CTS\_TO} = 204\text{ }\mu\text{s}$, $\text{AIFS}_{\text{BE}} = 322\text{ }\mu\text{s}$), a single hidden-node `RTS` collision plus `CW1` backoff ($15.5$ slots) wastes **$546\text{ }\mu\text{s} + 1581\text{ }\mu\text{s} = 2,127\text{ }\mu\text{s}$ (`2.13 ms`) of dead air**!

### 2.3 Why Mode B (`ubnt_poll_host.ko` TDMA) Scales Linearly with $(N, d)$ But Pays a Fixed Framing & Latency Tax at Low $N$

In Mode B (`ubnt_poll_host.ko` + `athwlan_AR9888v2_ptmp_ap_bin`):
- **Zero Hidden-Node Collisions & Zero Backoff Slots**: Autonomous CPE transmission is disabled (`addradio` mode `1`). A CPE transmits immediately (`SIFS = 16 µs`) after receiving its dedicated Poll frame from the AP.
- **Once-Per-Poll Propagation Delay**: Instead of paying $2\tau(d)$ on every backoff slot, Mode B pays $2\tau(d)$ **only once per polled station**:
  $$T_{\text{poll\_active}}(d) = T_{\text{poll\_hdr}} (36\text{ }\mu\text{s}) + \text{SIFS} (16\text{ }\mu\text{s}) + T_{\text{guard}} (24\text{ }\mu\text{s}) + 2\tau(d) = 76 + 6.6713\,d_{\text{km}}\text{ }\mu\text{s}$$
  $$T_{\text{poll\_idle}}(d) = T_{\text{poll\_hdr}} (36\text{ }\mu\text{s}) + T_{\text{no\_tx\_detect}} (32\text{ }\mu\text{s}) + 2\tau(d) = 68 + 6.6713\,d_{\text{km}}\text{ }\mu\text{s}$$
- **Why Mode B Loses at Small $N < N^*(d)$**:
  1. Fixed TDMA superframe turnaround + Contention-Based Period (`polling_ff_cbp_slots`) overhead (`~400 µs` per cycle) plus empty-poll (`NO-TX-DETECT`) waste on semi-active stations costs `8–11%` throughput at small $N$.
  2. Stock `airOS 8` lacks Cooperative Asymmetric AQL (`AP=1500 µs`, `CPE=2100 µs`), resulting in lower bidirectional UL share (`~16.0–18.5%` vs `23.8%` in Mode A, `CONFIRMED ON BENCH` in Stage 12 `R76–R79`).
  3. Stock `airOS 8` lacks `fq_codel` (`256B / 10ms`) and `WMM AC_VO Deficit Bypass`, suffering `34–55 ms` loaded `p95` RTT (`INFOTXQ` soak + TDMA token-rotation wait across $N$ stations) compared to Mode A's `6.8–18.4 ms` `AC_VO` RTT.

---

## 3. Exact Crossover Boundary Table Across $N=2..32$ CPEs and $d=1..14\text{ km}$

The solver ([`analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py`](../analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py)) evaluates four distinct crossover contours $N^*(d)$ (the minimum number of CPEs $N \in [2..32]$ at which **Mode B overtakes Mode A**):
1. **$N^*_{\text{Tot}}(d)$ (`Total Goodput Crossover`)**: $G_{\text{tot},B}(N, d) > G_{\text{tot},A}(N, d)$
2. **$N^*_{\text{UL}}(d)$ (`Hidden-Node Uplink Goodput Crossover`)**: $G_{\text{UL},B}(N, d) > G_{\text{UL},A}(N, d)$
3. **$N^*_{\text{FMX}}(d)$ (`Composite FuturaMAX QoE Crossover`)**: $S_{\text{FMX},B}(N, d) > S_{\text{FMX},A}(N, d)$ (`45%` Total GP + `25%` UL GP + `20%` Interactive `p95` RTT + `10%` Jain Fairness)
4. **$N^*_{\text{p95}}(d)$ (`Interactive WMM AC_VO p95 Latency Crossover`)**: $\text{RTT}_{p95,B}(N, d) < \text{RTT}_{p95,A}^{\text{VO}}(N, d)$

### 3.1 Master 19-Point Distance Crossover Table ($d = 1.0 .. 14.0\text{ km}$)

| Distance $d$ (km) | Cov. Class $c(d)$ | Slot $\sigma(d)$ ($\mu\text{s}$) | ACK/CTS Timeout ($\mu\text{s}$) | Hidden RTS $T_{\text{vuln}}(d)$ ($\mu\text{s}$) | **Regime 3: Saturated Full HN** ($\alpha_{\text{HN}}=1.0, \rho_{\text{UL}}=1.0$) `$N^*_{\text{UL}}$ / $N^*_{\text{Tot}}$ / $N^*_{\text{FMX}}$ / $N^*_{\text{p95}}$` | **Regime 2: Typical `90°–120°` WISP Sector** ($\alpha_{\text{HN}}=0.50, \rho_{\text{UL}}=0.35$) `$N^*_{\text{UL}}$ / $N^*_{\text{Tot}}$ / $N^*_{\text{FMX}}$ / $N^*_{\text{p95}}$` | **Regime 1: Low-HN / Narrow Sector** ($\alpha_{\text{HN}}=0.15, \rho_{\text{UL}}=0.25$) `$N^*_{\text{UL}}$ / $N^*_{\text{Tot}}$ / $N^*_{\text{FMX}}$ / $N^*_{\text{p95}}$` |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1.0 km** | `2` | `15 µs` | `30 µs` | `42.7 µs` | **`4 / 2 / 5 / 11`** | **`11 / 6 / 18 / >32`** | **`22 / 11 / >32 / >32`** |
| **1.5 km** *(R76)* | `3` | `18 µs` | `36 µs` | `46.0 µs` | **`3 / 2 / 5 / 11`** | **`10 / 5 / 17 / >32`** | **`20 / 10 / 32 / >32`** |
| **2.0 km** | `4` | `21 µs` | `42 µs` | `49.3 µs` | **`3 / 2 / 4 / 10`** | **`9 / 5 / 16 / >32`** | **`18 / 9 / 30 / >32`** |
| **3.0 km** *(R61)* | `6` | `27 µs` | `54 µs` | `56.0 µs` | **`3 / 2 / 4 / 9`** | **`8 / 4 / 14 / >32`** | **`16 / 7 / 26 / >32`** |
| **4.0 km** | `8` | `33 µs` | `66 µs` | `62.7 µs` | **`3 / 2 / 4 / 9`** | **`8 / 4 / 12 / 30`** | **`14 / 7 / 23 / >32`** |
| **4.5 km** *(R70)* | `10` | `39 µs` | `78 µs` | `66.0 µs` | **`3 / 2 / 4 / 8`** | **`7 / 4 / 11 / 28`** | **`13 / 6 / 21 / >32`** |
| **5.0 km** | `11` | `42 µs` | `84 µs` | `69.4 µs` | **`3 / 2 / 4 / 8`** | **`7 / 3 / 11 / 27`** | **`12 / 6 / 20 / >32`** |
| **6.0 km** *(R62)* | `13` | `48 µs` | `96 µs` | `76.0 µs` | **`3 / 2 / 4 / 8`** | **`7 / 3 / 10 / 25`** | **`11 / 5 / 19 / >32`** |
| **7.0 km** | `15` | `54 µs` | `108 µs` | `82.7 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 10 / 24`** | **`11 / 5 / 18 / >32`** |
| **7.5 km** *(R77)* | `16` | `57 µs` | `114 µs` | `86.0 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 9 / 23`** | **`10 / 5 / 17 / >32`** |
| **8.0 km** | `17` | `60 µs` | `120 µs` | `89.4 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 9 / 23`** | **`10 / 4 / 16 / >32`** |
| **9.0 km** *(R69)* | `20` | `69 µs` | `138 µs` | `96.1 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 9 / 21`** | **`10 / 4 / 15 / >32`** |
| **10.0 km** | `22` | `75 µs` | `150 µs` | `102.7 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 8 / 21`** | **`9 / 4 / 15 / >32`** |
| **10.5 km** *(R78)* | `23` | `78 µs` | `156 µs` | `106.1 µs` | **`3 / 2 / 3 / 7`** | **`6 / 3 / 8 / 20`** | **`9 / 4 / 14 / 32`** |
| **11.0 km** | `24` | `81 µs` | `162 µs` | `109.4 µs` | **`3 / 2 / 3 / 7`** | **`5 / 2 / 8 / 20`** | **`9 / 4 / 14 / 32`** |
| **12.0 km** *(R73)* | `27` | `90 µs` | `180 µs` | `116.1 µs` | **`2 / 2 / 3 / 6`** | **`5 / 2 / 8 / 19`** | **`8 / 3 / 13 / 30`** |
| **13.0 km** | `28` | `93 µs` | `186 µs` | `122.8 µs` | **`2 / 2 / 3 / 6`** | **`5 / 2 / 8 / 19`** | **`8 / 3 / 13 / 29`** |
| **13.5 km** *(R79)* | `30` | `99 µs` | `198 µs` | `126.1 µs` | **`2 / 2 / 3 / 6`** | **`5 / 2 / 8 / 18`** | **`8 / 3 / 13 / 29`** |
| **14.0 km** | `31` | `102 µs` | `204 µs` | `129.4 µs` | **`2 / 2 / 3 / 6`** | **`5 / 2 / 7 / 18`** | **`8 / 3 / 13 / 28`** |

---

## 4. Phase-Space Deep Dive & Quantitative Comparison Matrices

### 4.1 Regime 2 (`Typical 90°–120° WISP Sector`, $\alpha_{\text{HN}}=0.50, \rho_{\text{UL}}=0.35$)

In a representative residential/SME WISP sector where `50%` of CPE pairs are mutually hidden by terrain, roofs, or trees and Cooperative CPE Asymmetric AQL (`2100/4200 µs`) + `TCP TSQ (128 KB)` paces uplink bursts to `35%` simultaneous contention ($\rho_{\text{UL}} = 0.35$):

| $(N, d)$ Coordinate | Mode A `RTS` $p_{\text{coll}}$ | Mode A Total / UL GP (Mbps) | Mode B Total / UL GP (Mbps) | Mode A `AC_VO` `p95` RTT (ms) | Mode B `p95` RTT (ms) | Mode A / Mode B FMX Score | Operational Winner & Regime Diagnosis |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$N=2, d=1.5\text{ km}$** | `4.1%` | **`105.0 / 24.1`** | `99.4 / 18.4` | **`14.5 ms`** | `39.7 ms` | **`91.3` vs `77.9`** | **Mode A (`+5.6 Mbps` Tot, `+5.7 Mbps` UL, `2.7x` lower `p95`)** |
| **$N=4, d=1.5\text{ km}$** | `11.1%` | **`100.3 / 21.8`** | `100.2 / 18.5` | **`16.5 ms`** | `41.5 ms` | **`86.8` vs `77.7`** | **Mode A (`+3.3 Mbps` UL, `2.5x` lower `p95`)** |
| **$N=8, d=1.5\text{ km}$** | `21.6%` | `92.3 / 18.0` | **`100.6 / 18.6`** | **`23.8 ms`** | `45.3 ms` | **`77.7` vs `76.5`** | **Transition Band (Mode B `+0.6 Mbps` UL; Mode A `1.9x` lower `p95`)** |
| **$N=16, d=1.5\text{ km}$** | `35.1%` | `81.1 / 12.6` | **`100.5 / 18.6`** | **`49.6 ms`** | `52.9 ms` | **`62.0` vs `73.7`** | **Mode B (`+19.4 Mbps` Tot, `+6.0 Mbps` UL)** |
| **$N=32, d=1.5\text{ km}$** | `49.9%` | `69.9 / 7.2` | **`100.3 / 18.6`** | `140.4 ms` | **`68.0 ms`** | `49.2` vs **`72.3`** | **Mode B (`2.6x` UL GP, `2.1x` lower `p95`)** |
| **$N=2, d=6.0\text{ km}$** | `2.6%` | **`91.4 / 20.9`** | `90.2 / 16.7` | **`15.4 ms`** | `40.9 ms` | **`91.0` vs `79.6`** | **Mode A (`+4.2 Mbps` UL, `2.7x` lower `p95`)** |
| **$N=6, d=6.0\text{ km}$** | `11.0%` | `83.5 / 16.9` | **`91.3 / 16.9`** | **`21.7 ms`** | `44.9 ms` | **`80.6` vs `78.9`** | **Exact UL Crossover (`16.9 Mbps`); Mode A wins `AC_VO` `p95` by `2.1x`** |
| **$N=10, d=6.0\text{ km}$** | `17.5%` | `77.6 / 14.0` | **`91.3 / 16.9`** | **`32.2 ms`** | `48.8 ms` | `71.0` vs **`77.4`** | **Mode B overtakes Composite FMX QoE (`N*_FMX = 10`)** |
| **$N=24, d=6.0\text{ km}$** | `32.5%` | `65.7 / 8.0` | **`90.8 / 16.8`** | **`94.7 ms`** | **`62.7 ms`** | `52.6` vs **`74.6`** | **Mode B dominates both throughput (`2.1x` UL) and `p95` RTT** |
| **$N=2, d=14.0\text{ km}$** | `2.1%` | `69.8 / 15.8` | **`70.3 / 13.0`** | **`16.9 ms`** | `43.2 ms` | **`89.7` vs `80.8`** | **Mode A wins UL (`+2.8 Mbps`) and `AC_VO` `p95` (`16.9 vs 43.2 ms`)** |
| **$N=5, d=14.0\text{ km}$** | `7.9%` | `62.9 / 12.2` | **`71.5 / 13.2`** | **`23.8 ms`** | `46.5 ms` | **`78.3` vs `80.2`** | **Mode B overtakes UL (`N*_UL = 5`); approaches FMX crossover (`N*_FMX = 7`)** |
| **$N=16, d=14.0\text{ km}$** | `22.7%` | `50.2 / 5.7` | **`70.7 / 13.1`** | `72.4 ms` | **`58.6 ms`** | `53.2` vs **`76.5`** | **Mode B dominates all metrics (`2.3x` UL, `+20.5 Mbps` Tot, lower `p95`)** |

---

### 4.2 Regime 3 (`Worst-Case Saturated Full Hidden-Node Uplink`, $\alpha_{\text{HN}}=1.0, \rho_{\text{UL}}=1.0$)

When **100% of CPEs are mutually hidden** and **all $N$ stations are simultaneously backlogged with continuous uplink traffic** (e.g., synchronized speedtests, CCTV continuous uplink flood, or unpaced UDP uplink saturation):

- **At $d = 1.0..1.5\text{ km}$**:
  - Mode A (`RTS/CTS = 256B` + `Asymmetric AQL` + `AC_VO Bypass`) holds its own for **$N = 2..3$ CPEs** (`CONFIRMED ON BENCH` in Stage 7.3 where $N=3$ hidden-node UL jumped `+18.5%` with `RTS/CTS = 256B`).
  - At **$N = 4$ ($1.0\text{ km}$) / $N = 3$ ($1.5\text{ km}$)**, hidden-node `RTS` collision probability reaches $p_c = 25\text{--}33\%$, causing Mode B (`ubnt_poll_host.ko` TDMA) to overtake Mode A on Uplink Goodput ($N^*_{\text{UL}} = 3..4$).
  - At **$N^*_{\text{FMX}} = 5$ ($1.0..1.5\text{ km}$) / $N^*_{\text{FMX}} = 4$ ($2.0..6.0\text{ km}$)**, Mode B overtakes Mode A on Composite FMX QoE.
  - At **$N^*_{\text{p95}} = 6..11$**, RF medium saturation in Mode A pushes even `WMM AC_VO` `p95` RTT above Mode B's TDMA polling latency.
- **At $d = 7.0..14.0\text{ km}$**:
  - Because coverage-class slot time $\sigma(d) = 54..102\text{ }\mu\text{s}$ and `CTS_Timeout(d) = 108..204 µs` make every single backoff slot and `RTS` collision cost $6\times\text{--}11\times$ more airtime than at short range, **Mode B (`ubnt_poll_host.ko` TDMA) beats Mode A for any saturated hidden-node sector with $N \ge 3$ CPEs**!

---

## 5. Three-Zone Phase-Space Partition & Operational Architecture Rules

Across the $(N \in [2..32], d \in [1..14]\text{ km})$ plane, the comparison between Mode A and Mode B partitions into **three distinct operational zones**:

1. **Zone I — Pure Mode A Dominance ($N < N^*_{\text{UL}}(d)$)**:
   - *Typical WISP Sector (`Regime 2`)*: **$N = 2..10$ CPEs at $d \le 1.5\text{ km}$**, **$N = 2..7$ CPEs at $d = 3..6\text{ km}$**, **$N = 2..5$ CPEs at $d = 7.5..10.5\text{ km}$**, and **$N = 2..4$ CPEs at $d = 11..14\text{ km}$**.
   - *Narrow / Co-Visible LOS Sector (`Regime 1`)*: **$N = 2..21$ CPEs at $d = 1\text{ km}$**, **$N = 2..15$ CPEs at $d = 3\text{ km}$**, **$N = 2..10$ CPEs at $d = 6\text{ km}$**, and **$N = 2..7$ CPEs at $d = 12..14\text{ km}$**.
   - **Behavior**: Mode A (`OpenWrt + RTS/CTS 256B + Asymmetric AQL + WMM AC_VO Deficit Bypass`) achieves **both higher uplink goodput (`+15% to +35%`) AND `2.0x to 2.8x` lower interactive `p95` RTT (`14–22 ms` vs `38–46 ms`)** than Stock `airOS 8` TDMA polling, because CSMA/CA collision rates are low ($p_c < 12\%$) and zero airtime is wasted on TDMA framing or empty polls.

2. **Zone II — The Throughput-vs-Latency Tradeoff Band ($N^*_{\text{UL}}(d) \le N < N^*_{\text{FMX}}(d)$)**:
   - *Typical WISP Sector (`Regime 2`)*: **$N = 11..17$ at $d = 1..1.5\text{ km}$**, **$N = 8..13$ at $d = 3..4.5\text{ km}$**, **$N = 6..9$ at $d = 6..9\text{ km}$**, and **$N = 5..7$ at $d = 10.5..14\text{ km}$**.
   - **Behavior**: Mode B (`ubnt_poll_host.ko` TDMA) delivers **higher raw aggregate and uplink throughput** because deterministic polling eliminates growing `RTS` collisions and coverage-class backoff slots, **but Mode A still delivers lower interactive (`AC_VO` / VoIP / gaming) `p95` latency** (`22–38 ms` vs `45–55 ms`) thanks to `WMM AC_VO Deficit Bypass` (`Deficit: VO +256 µs`) and `AQL + fq_codel`.

3. **Zone III — Pure Mode B (`TDMA Polling`) Dominance ($N \ge N^*_{\text{FMX}}(d)$)**:
   - *Typical WISP Sector (`Regime 2`)*: **$N \ge 18$ at $d = 1\text{ km}$**, **$N \ge 14$ at $d = 3\text{ km}$**, **$N \ge 10$ at $d = 6\text{ km}$**, **$N \ge 9$ at $d = 7.5..9\text{ km}$**, and **$N \ge 7..8$ at $d = 10..14\text{ km}$**.
   - *Saturated Full Hidden-Node Uplink (`Regime 3`)*: **$N \ge 5$ at $d = 1..1.5\text{ km}$**, **$N \ge 4$ at $d = 2..6\text{ km}$**, and **$N \ge 3$ at $d = 7..14\text{ km}$**.
   - **Behavior**: Mode B (`ubnt_poll_host.ko` TDMA) decisively beats Mode A on **all metrics** (Total Goodput, Uplink Goodput, Jain Fairness, and Composite QoE), and for $N \ge N^*_{\text{p95}}(d)$ even beats Mode A's `AC_VO` `p95` RTT because Mode A's RF medium is choked by `RTS` collisions and `CTS_Timeout(d)` stalls.
   - **Architectural Implication for FuturaMAX**: To outperform Mode B in **Zone III** (`high-N, high-d hidden-node sectors`), OpenWrt cannot rely solely on passive `CSMA/CA + RTS/CTS 256B + AQL`. It requires **either**:
     - Keeping `airOS` TDMA (`ubnt_poll_host.ko`) at the radio link layer while applying **Stage 1 external/cooperative CAKE + DiffServ + TCP pacing** (`Hybrid Architecture` per `AGENTS.md` §2), **or**
     - Adding a **cooperative host-level Uplink Token / Poll Pacer** over the OpenWrt CPE fleet that bounds simultaneous uplink contenders to $N_{\text{eff}} \le 2$ inside each `5–8 ms` window.

---

## 6. Reproducibility & Verification Receipts

- **Solver Script**: [`analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py`](../analysis/simulation/fmx_mode_a_vs_mode_b_crossover_audit.py)
- **Full $(N=2..32) \times (d=1..14\text{ km})$ Dataset (`1,767` evaluated phase-space points)**: [`artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json`](../artifacts/autoresearch/mode_a_vs_mode_b_crossover_20261024.json)
- **Automated Test Suite (`4/4 PASS`)**: [`tests/test_fmx_mode_a_vs_mode_b_crossover_audit.py`](../tests/test_fmx_mode_a_vs_mode_b_crossover_audit.py)
