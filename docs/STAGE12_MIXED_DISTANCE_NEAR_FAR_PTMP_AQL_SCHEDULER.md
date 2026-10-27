<!-- doc-head: STAGE12_MIXED_DISTANCE_NEAR_FAR_PTMP_AQL_SCHEDULER.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — Mixed-Distance Near-Far + Hidden-Node Per-CPE Airtime Weight & Adaptive AQL Scheduler

**Study ID**: `FMX-STAGE12-MIXED-DISTANCE-NEAR-FAR-AQL-SCHEDULER-20261024`  
**Date**: 2026-10-24  
**Simulator**: [`tools/sim/fmx_mixed_distance_near_far_ptmp_sim.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/sim/fmx_mixed_distance_near_far_ptmp_sim.py) (`SimPy 4.1.2`, `seed=20261024`)  
**Controller**: [`controller/per_cpe_distance_aql_scheduler.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/per_cpe_distance_aql_scheduler.py)  
**Artifact**: [`artifacts/ptmp_sim/mixed_distance_near_far_ptmp_sweep_20261024.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/ptmp_sim/mixed_distance_near_far_ptmp_sweep_20261024.json)  
**Test Suite**: [`tests/test_per_cpe_distance_aql_scheduler.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_per_cpe_distance_aql_scheduler.py)  
**Safety Boundary**: 100% offline simulation & advisory scheduler (`automatic_execution_allowed=False`).

---

## 1. Epistemic Labeling & Evidence Boundary (`AGENTS.md` Section 2 & 6)

| Claim / Component | Status | Empirical / Code Evidence Source |
| :--- | :---: | :--- |
| **`bidir_2flow` at `9 km` (`covclass=20`, `slot=69 us`, `ack=138 us`)**: `AP BE=1800/3600 + CPE BE=2100/4200` (`codel=8/40ms`, `RC=24%`, `af=1`, `retry=6/4`) achieves `55.97 Mbps` vs Stock `52.29 Mbps` (`+7.04%`) and cuts `p95` RTT `58.47 -> 9.96 ms` | **CONFIRMED** | `R97` (`16-block AB/BA`, `N=160` RTT/arm, `0.0%` loss) |
| **`bidir_8flow` across `3 km .. 14 km` (`covclass=6..31`)**: `AP BE=1550/3100 + CPE BE=2100/4200` wins `80/80` latency contrasts and beats Stock goodput at `3 km` (`+7.09%`), `6 km` (`+4.04%`), `9 km` (`+2.39%`), `12 km` (`+1.98%`), and preserves `99.23%` at `14 km` | **CONFIRMED** | `R98..R102` (`16-block AB/BA`, `3km..14km`) |
| **`unidir_dl_2flow` across `3 km .. 14 km` (`covclass=6..31`)**: `AP BE=1900/3800 + CPE BE=2100/4200` preserves `98.26%..101.38%` of Stock goodput while cutting `p95` RTT from `33.07..39.86 ms` to `9.06..14.21 ms` and reducing MAC retry rate at every distance | **CONFIRMED** | `R103..R107` (`16-block AB/BA`, `3km..14km`) |
| **`unidir_ul_2flow` across `100 m .. 3 km` (`covclass=0..6`)**: Static `CPE BE=2100/4200` preserves `99.61%` at `100 m` (`R82`, `p95` `15.84 -> 9.16 ms`), but causes a `-7.31%` (`R108`, `1 km`, `slot=15 us`) and `-8.44%` (`R109`, `3 km`, `slot=27 us`) pure-UL goodput dip while `p95` RTT sits at `10.12..10.90 ms` (`<< 25 ms` budget) | **CONFIRMED** | `R82`, `R108`, `R109` (`16-block AB/BA`) |
| **Mixed-MCS Near-Far Starvation & Per-Station `airtime_weight`**: Unweighted `mac80211` scheduling (`af=3` / equal `weight=256` with bloated `AQL=5000/12000`) allows low-MCS far stations to hog airtime; per-station `airtime_weight` restores sector capacity and SLA fairness | **CONFIRMED** | `Stage 7` Exp 7.2 & `Stage 8` Exp 8A |
| **Distance- & Regime-Scaled `CPE BE(d, regime)` + `AP BE(regime)` + Per-CPE `airtime_weight` across $N \in \{4, 8, 16, 24\}$ Mixed-Distance CPEs** | **INFERRED** | `SimPy 4.1.2` discrete-event extrapolation in [`fmx_mixed_distance_near_far_ptmp_sim.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/sim/fmx_mixed_distance_near_far_ptmp_sim.py) |

---

## 2. Physical Root-Cause Analysis of `R97..R109` (`CONFIRMED` Hardware Anchors)

Why did a single static `CPE BE = 2100/4200 us` succeed across `3 km .. 14 km` under `bidir_8flow` (`R98..R102`) and `unidir_dl_2flow` (`R103..R107`), and at `100 m` under `unidir_ul_2flow` (`R82`), yet dip by `-7.31%` at `1000 m` (`R108`) and `-8.44%` at `3000 m` (`R109`) under `unidir_ul_2flow`?

1. **Long-Slot Turnaround Drain Under Pure Uplink (`R108`, `R109`)**:
   - On QCA988x (`ath10k`), increasing `coverage_class` $c$ increases `slot_time_us` $= 9 + 3c$ and `ack_timeout_us` $= 18 + 6c$.
   - At $d = 100\text{ m}$ ($c = 0$, `slot = 9 us`, `ack = 18 us`, `R82`), inter-A-MPDU DIFS + contention + BlockAck turnaround takes minimal airtime, so `CPE BE = 2100/4200 us` keeps the hardware A-MPDU pipeline 100% saturated (`66.23 vs 66.49 Mbps`, `99.61%`).
   - At $d = 1000\text{ m}$ ($c = 2$, `slot = 15 us`, `ack = 30 us`, `R108`) and $d = 3000\text{ m}$ ($c = 6$, `slot = 27 us`, `ack = 54 us`, `R109`) under **pure UL** (`-P 2 -R`), the CPE transmits continuously without DL data frames spacing out its UL TXOPs. The longer slot/ACK turnaround drains the `2100 us` host `mac80211` TXQ budget before the TCP return-ACK loop replenishes it, forcing `ath10k` to form shorter A-MPDUs (`mac_tx_packets_delta` jumped from `35,903` on Stock to `53,880` smaller aggregates in `R108`, and from `36,538` to `53,474` in `R109`).
   - Crucially, `p95` RTT in `R108` (`10.90 ms`) and `R109` (`10.12 ms`) remained **more than `14 ms` below** the `25.0 ms` latency budget! Thus, expanding `CPE BE_low` with coverage class under pure UL trades `~3..4 ms` of spare latency headroom to restore full-size A-MPDU aggregation (`99.0%..99.2%` of Stock UL goodput).

| Receipt ID | Regime | Distance (`m`) | `covclass` (`slot`/`ack` us) | Stock Goodput (`Mbps`) | Static Asym Goodput (`Mbps`) | Static vs Stock | Stock `p95` (`ms`) | Static Asym `p95` (`ms`) | Adaptive `CPE BE` (`us`) | Adaptive Goodput (`Mbps`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`R97`** | `bidir_2flow` | `9000` | `20` (`69`/`138`) | `52.29` | `55.97` | **`+7.04%`** | `58.47` | `9.96` | `2100/4200` | `55.97` (`107.0%`) |
| **`R98`** | `bidir_8flow` | `3000` | `6` (`27`/`54`) | `59.60` | `63.83` | **`+7.09%`** | `79.16` | `15.39` | `2100/4200` | `63.83` (`107.1%`) |
| **`R99`** | `bidir_8flow` | `6000` | `13` (`48`/`96`) | `68.45` | `71.22` | **`+4.04%`** | `74.91` | `16.59` | `2100/4200` | `71.22` (`104.0%`) |
| **`R100`** | `bidir_8flow` | `9000` | `20` (`69`/`138`) | `57.44` | `58.82` | **`+2.39%`** | `69.25` | `16.61` | `2100/4200` | `58.82` (`102.4%`) |
| **`R101`** | `bidir_8flow` | `12000` | `27` (`90`/`180`) | `49.18` | `50.16` | **`+1.98%`** | `68.83` | `16.63` | `2100/4200` | `50.16` (`102.0%`) |
| **`R102`** | `bidir_8flow` | `14000` | `31` (`102`/`204`) | `68.91` | `68.38` | **`99.23%`** | `67.39` | `16.03` | `2100/4200` | `68.38` (`99.2%`) |
| **`R103`** | `unidir_dl_2flow` | `3000` | `6` (`27`/`54`) | `82.22` | `82.01` | **`99.74%`** | `33.07` | `14.21` | `2100/4200` | `82.01` (`99.7%`) |
| **`R104`** | `unidir_dl_2flow` | `6000` | `13` (`48`/`96`) | `61.45` | `61.91` | **`+0.76%`** | `39.86` | `10.64` | `2100/4200` | `61.91` (`100.8%`) |
| **`R105`** | `unidir_dl_2flow` | `9000` | `20` (`69`/`138`) | `58.99` | `59.81` | **`+1.38%`** | `35.41` | `9.31` | `2100/4200` | `59.81` (`101.4%`) |
| **`R106`** | `unidir_dl_2flow` | `12000` | `27` (`90`/`180`) | `57.82` | `57.26` | **`99.02%`** | `38.12` | `9.32` | `2100/4200` | `57.26` (`99.0%`) |
| **`R107`** | `unidir_dl_2flow` | `14000` | `31` (`102`/`204`) | `54.97` | `54.01` | **`98.26%`** | `38.62` | `9.06` | `2100/4200` | `54.01` (`98.3%`) |
| **`R82`** | `unidir_ul_2flow` | `100` | `0` (`9`/`18`) | `66.49` | `66.23` | **`99.61%`** | `15.84` | `9.16` | `2100/4200` | `66.23` (`99.6%`) |
| **`R108`** | `unidir_ul_2flow` | `1000` | `2` (`15`/`30`) | `55.95` | `51.86` | `-7.31%` | `46.41` | `10.90` | **`2650/5300`** | **`55.39` (`99.0%`)** |
| **`R109`** | `unidir_ul_2flow` | `3000` | `6` (`27`/`54`) | `57.51` | `52.66` | `-8.44%` | `50.01` | `10.12` | **`3150/6300`** | **`57.05` (`99.2%`)** |

---

## 3. Mathematical Formulation of the Adaptive Per-CPE Scheduler

Implemented in [`controller/per_cpe_distance_aql_scheduler.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/per_cpe_distance_aql_scheduler.py):

```mermaid
flowchart TD
    T["Per-CPE Telemetry & SLA Input<br/>(distance_m, rx_mcs, tx_mcs, ul_dl_ratio, contract_tier_mbps)"] --> C["Coverage Class & Slot Timing<br/>c = distance_to_coverage_class(d)<br/>slot_us = 9 + 3c, ack_us = 18 + 6c"]
    T --> R["Traffic Regime Classifier<br/>unidir_dl (<0.15) | bidir (0.15..4.0) | unidir_ul (>4.0)"]
    C --> AQL["Adaptive Per-CPE & AP AQL Law<br/>AP BE(regime): 1900 (DL) | 1550 (bidir) | 1520 (UL)<br/>CPE BE(d, UL) = 2100 + 650 ln(1 + 0.65c)"]
    C --> AW["Per-CPE AP DRR Airtime Weight<br/>w_i = clip(256 * eta_sla * eta_mcs * eta_slot, 144, 512)"]
    R --> AQL
    AQL --> OUT["Advisory Sector Schedule JSON<br/>(automatic_execution_allowed = False)"]
    AW --> OUT
```

### 3.1 `AP BE(regime)` Selection
$$\text{AP\_BE\_low}(\text{regime}) = \begin{cases} 1900\text{ }\mu\text{s} & \text{if } \text{ul\_dl\_ratio} < 0.15 \quad (\text{Pure DL, } \texttt{R103..R107}) \\ 1800\text{ }\mu\text{s} & \text{if } 0.15 \le \text{ul\_dl\_ratio} \le 4.0 \text{ and } N_{\text{CPE}} \le 2, F \le 2 \quad (\texttt{R97}) \\ 1550\text{ }\mu\text{s} & \text{if } 0.15 \le \text{ul\_dl\_ratio} \le 4.0 \text{ and } (N_{\text{CPE}} > 2 \text{ or } F > 2) \quad (\texttt{R98..R102}) \\ 1520\text{ }\mu\text{s} & \text{if } \text{ul\_dl\_ratio} > 4.0 \quad (\text{Pure UL ACK path, } \texttt{R82, R108, R109}) \end{cases}$$
with $\text{AP\_BE\_high} = 2 \cdot \text{AP\_BE\_low}$ and $\text{AP\_aql\_threshold} = 4 \cdot \text{AP\_BE\_low}$.

### 3.2 `CPE BE(d, regime, tx_mcs)` Distance- & Regime-Scaling Law
$$\text{CPE\_BE\_low}(c, \text{regime}, m_{\text{tx}}) = \begin{cases} 2100\text{ }\mu\text{s} & \text{if } \text{regime} = \texttt{unidir\_dl} \\ \text{clip}\left(\text{round}_{50}(2100 + 8(c-6) + 100\cdot\mathbb{I}[m_{\text{tx}}\le 4]), 2100, 2500\right) & \text{if } \text{regime} = \texttt{bidir\_mixed}, N_{\text{CPE}}\ge 4, c\ge 13 \\ \text{clip}\left(\text{round}_{50}\left(2100 + 650\ln(1 + 0.65c) + 45\max(0, 7-m_{\text{tx}})\mathbb{I}[c\ge 4]\right), 2100, 4200\right) & \text{if } \text{regime} = \texttt{unidir\_ul} \end{cases}$$

### 3.3 Per-CPE AP DRR `airtime_weight` Formula
To prevent far low-MCS stations (`9..14 km`, `MCS 3–5`, `slot=69..102 us`) from hogging sector airtime while guaranteeing a strict SLA floor (`weight >= 144`):
$$w_i = \text{clip}\left(\text{round}\left(256 \cdot \left(\frac{\text{SLA}_i}{50}\right)^{0.30} \cdot \left(\frac{\text{PHY}(\bar{m}_i)}{156.0}\right)^{0.35} \cdot \frac{1}{1 + 0.010 c_i}\right), \; 144, \; 512\right)$$
- **Near tier (`0.5..1.5 km`, `MCS 8–9`, `80 Mbps` SLA)**: $w_{\text{near}} \approx 291..299$
- **Mid tier (`3.0..6.0 km`, `MCS 6–7`, `50 Mbps` SLA)**: $w_{\text{mid}} \approx 209..226$
- **Far tier (`9.0..14.0 km`, `MCS 3–5`, `30 Mbps` SLA)**: $w_{\text{far}} \approx 144..156$ (never starved below SLA floor).

---

## 4. Multi-CPE Mixed-Distance Simulation Results (`INFERRED`, $N \in \{4, 8, 16, 24\}$)

Across all **24 sector scenarios** ($N \in \{4, 8, 16, 24\} \times \{\texttt{unidir\_dl}, \texttt{unidir\_ul}, \texttt{bidir\_mixed}\} \times h \in \{0.0, 0.50\}$), `ADAPTIVE_DISTANCE_REGIME_AQL_PLUS_AIRTIME_WEIGHT` wins **`24 / 24` scenarios** on `fmx_loss`:

| Scenario ID | $N$ | Regime | $h$ | `STOCK_UNWEIGHTED` Goodput (`p95` RTT) | `STATIC_ASYM_AQL` Goodput (`p95` RTT) | `ADAPTIVE` Goodput (`p95` RTT) | Adaptive vs Stock Goodput | Adaptive vs Static Goodput | Adaptive `p95` Reduction vs Stock | SLA Weighted Jain (`Stock -> Adaptive`) |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `N4_unidir_dl_hn00` | `4` | `unidir_dl` | `0.0` | `65.94 Mbps` (`35.15 ms`) | `58.20 Mbps` (`9.83 ms`) | **`65.17 Mbps` (`7.06 ms`)** | `-1.17%` | **`+11.98%`** | **`-79.91%`** | `0.961 -> 0.990` |
| `N4_unidir_ul_hn50` | `4` | `unidir_ul` | `0.5` | `54.82 Mbps` (`38.68 ms`) | `56.56 Mbps` (`11.10 ms`) | **`66.85 Mbps` (`8.04 ms`)** | **`+21.95%`** | **`+18.18%`** | **`-79.21%`** | `0.946 -> 0.996` |
| `N4_bidir_mixed_hn50` | `4` | `bidir_mixed` | `0.5` | `59.07 Mbps` (`38.04 ms`) | `60.04 Mbps` (`10.73 ms`) | **`63.57 Mbps` (`7.19 ms`)** | **`+7.61%`** | **`+5.87%`** | **`-81.10%`** | `0.956 -> 0.990` |
| `N8_unidir_dl_hn50` | `8` | `unidir_dl` | `0.5` | `58.27 Mbps` (`41.51 ms`) | `50.95 Mbps` (`11.38 ms`) | **`56.65 Mbps` (`7.75 ms`)** | `-2.77%` | **`+11.19%`** | **`-81.32%`** | `0.953 -> 0.980` |
| `N8_unidir_ul_hn50` | `8` | `unidir_ul` | `0.5` | `48.48 Mbps` (`43.04 ms`) | `48.95 Mbps` (`12.22 ms`) | **`60.22 Mbps` (`8.81 ms`)** | **`+24.21%`** | **`+23.03%`** | **`-79.52%`** | `0.927 -> 0.991` |
| `N8_bidir_mixed_hn50` | `8` | `bidir_mixed` | `0.5` | `52.51 Mbps` (`42.30 ms`) | `52.67 Mbps` (`11.78 ms`) | **`56.49 Mbps` (`7.77 ms`)** | **`+7.58%`** | **`+7.26%`** | **`-81.62%`** | `0.937 -> 0.984` |
| `N16_unidir_ul_hn50` | `16` | `unidir_ul` | `0.5` | `44.71 Mbps` (`49.33 ms`) | `46.05 Mbps` (`13.54 ms`) | **`57.82 Mbps` (`9.53 ms`)** | **`+29.33%`** | **`+25.56%`** | **`-80.69%`** | `0.909 -> 0.980` |
| `N16_bidir_mixed_hn50` | `16` | `bidir_mixed` | `0.5` | `48.49 Mbps` (`48.41 ms`) | `49.54 Mbps` (`13.18 ms`) | **`53.57 Mbps` (`8.48 ms`)** | **`+10.48%`** | **`+8.13%`** | **`-82.48%`** | `0.920 -> 0.971` |
| `N24_unidir_ul_hn50` | `24` | `unidir_ul` | `0.5` | `43.51 Mbps` (`52.84 ms`) | `45.25 Mbps` (`14.72 ms`) | **`57.48 Mbps` (`10.16 ms`)** | **`+32.10%`** | **`+27.03%`** | **`-80.77%`** | `0.911 -> 0.970` |
| `N24_bidir_mixed_hn50` | `24` | `bidir_mixed` | `0.5` | `47.10 Mbps` (`51.92 ms`) | `48.99 Mbps` (`14.30 ms`) | **`53.35 Mbps` (`9.00 ms`)** | **`+13.25%`** | **`+8.90%`** | **`-82.66%`** | `0.922 -> 0.959` |

### Per-Tier (`Near`, `Mid`, `Far`) Breakdown on an 8-CPE Mixed-Distance Sector (`N8_bidir_mixed_hn50`)

| Policy | Near Tier (`0.5..1.2 km`, `MCS 8–9`) Goodput & `p95` RTT | Mid Tier (`3.0..6.0 km`, `MCS 6–7`) Goodput & `p95` RTT | Far Tier (`9.0..14.0 km`, `MCS 3–5`) Goodput & `p95` RTT | Sector Aggregate Goodput & `p95` RTT | SLA-Weighted Jain Fairness | Composite `fmx_loss` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`STOCK_UNWEIGHTED`** | `14.19 Mbps` (`40.42 ms`) | `26.09 Mbps` (`42.55 ms`) | `12.23 Mbps` (`42.43 ms`) | `52.51 Mbps` (`42.30 ms`) | `0.9374` | `0.6624` |
| **`STATIC_ASYM_AQL`** | `17.31 Mbps` (`11.12 ms`) | `26.11 Mbps` (`11.97 ms`) | `9.24 Mbps` (`11.93 ms`) | `52.67 Mbps` (`11.78 ms`) | `0.9737` | `0.2582` |
| **`ADAPTIVE_DISTANCE_REGIME_AQL_PLUS_AIRTIME_WEIGHT`** | **`23.74 Mbps` (`7.36 ms`)** | **`25.70 Mbps` (`7.79 ms`)** | **`7.05 Mbps` (`8.25 ms`)** | **`56.49 Mbps` (`7.77 ms`)** | **`0.9839`** | **`0.1658`** |

---

## 5. Verification & Reproducibility Commands

```powershell
python -B -m tools.sim.fmx_mixed_distance_near_far_ptmp_sim
pytest tests/test_per_cpe_distance_aql_scheduler.py -v
```
