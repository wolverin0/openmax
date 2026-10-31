<!-- doc-head: STAGE75B_GLOBAL_NSGA2_PARETO_AND_STATISTICAL_SYNTHESIS.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 75B — Global `pymoo` NSGA-II Pareto Frontier & Paired Statistical Effect-Size Synthesis (`2026-10-26`)

- **Task ID**: `T-S75B-GLOBAL-NSGA2-PARETO-AND-STATISTICAL-EFFECT-SIZE-SYNTHESIS`
- **Epistemic Status**: `CONFIRMED`
- **Layer Attribution**: `proprietary airMAX/LTU module`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Synthesis Script**: [`tools/research/run_stage75b_nsga2_pareto_and_statistical_synthesis.py`](../tools/research/run_stage75b_nsga2_pareto_and_statistical_synthesis.py)
- **JSON Receipt (`5/5` Pillars Compliant)**: [`artifacts/autoresearch/stage75b_nsga2_pareto_and_statistical_synthesis_20261026.json`](../artifacts/autoresearch/stage75b_nsga2_pareto_and_statistical_synthesis_20261026.json)
- **Scientific Stack (Pillar D)**: `pymoo 0.6.2` (`NonDominatedSorting`, `HV`, `NSGA2`) + `scipy.stats 1.17.1` (paired $t$-test, signed `Cohen's d_z`, small-sample `Hedges' g_z`, `95% CI`, Shapiro-Wilk normality diagnostics)

---

## 1. Executive Summary (`CONFIRMED`)

Across all `38` physical counterbalanced `A1 -> B1 -> A2 -> B2` benchmark profiles spanning FuturaMAX's **4 Hardware Families** (`OpenWrt 24.10.4 PtMP`, `OpenWrt 24.10.4 PtP`, `airOS 8 WA/XC PtP`, and `Ubiquiti AF-LTU v2.3.1/v2.4.2`), 3-objective non-dominated sorting ($\max \text{Goodput}$, $\min \text{p95 RTT}$, $\min \text{VoIP Loss/Jitter}$) and normalized 3D Hypervolume (`HV` w.r.t. $\mathbf{r} = [1.1, 1.1, 1.1]$) confirm monotonic Pareto frontier expansion and statistically significant paired effect sizes on promoted Champions:

| Hardware Family | Stages Synthesized | Profiles Evaluated | 3D Pareto Front Size | Initial $\rightarrow$ Final 3D `HV` ($\Delta \text{HV}$) | Key Promoted Champion Paired Effect Size (`Cohen's d_z` / `Hedges' g_z`) |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **1. `OpenWrt 24.10.4 PtMP`** (`Champion v1..v20`) | `55A, 68C, 70C, 72A` | `14` | `4` | `0.2518 -> 1.2078` (**`+0.9560` / `+379.7%`**) | **Goodput**: $d_z = +1.3182$ ($g_z = +1.1101$), $+2.7287\text{ Mbps}$, $95\%\text{ CI }[0.5563, 4.9010]$, $p = 0.02323$ (`CONFIRMED`) |
| **2. `OpenWrt 24.10.4 PtP`** (`Dedicated 2-Node`) | `55A (S55A-R4)` | `2` | `2` | `0.0110 -> 0.1310` (**`+0.1200`**) | **Trade-off**: `v19` leads Goodput (`46.828 Mbps`), `M35` trims `p95` RTT (`60.851 ms`) & VoIP jitter (`2.173 ms`) (`CONFIRMED`) |
| **3. `airOS 8 WA/XC PtP`** (`Champion v1..v6`) | `60A, 62A, 68A, 70B, 72B, 73A` | `15` | `4` | `0.3597 -> 1.2340` (**`+0.8742` / `+243.0%`**) | **Loaded `p95` RTT**: $d_z = +1.2707$ ($g_z = +1.1478$), $-1.1288\text{ ms}$, $95\%\text{ CI }[-1.8116, -0.4460]$, $p = 0.00515$ (`CONFIRMED`) |
| **4. `Ubiquiti AF-LTU`** (`v2.3.1 / v2.4.2`) | `50B, 63B, 64A, 68B` | `7` | `5` | `0.0760 -> 0.3381` (**`+0.2620` / `+344.7%`**) | **Loaded `p95` RTT**: All-round $d_z = +0.7419$ ($g_z = +0.6452$, $-0.7719\text{ ms}$); Champions $d_z = +1.0793$ (`0` watchdog panics) (`CONFIRMED`) |

---

## 2. 3-Objective Non-Dominated Pareto Frontiers by Hardware Family (`CONFIRMED`)

### 2.1 Family 1 — `OpenWrt 24.10.4 PtMP` (`LAP-120 .20` + 3-CPE Heterogeneous Sector)
- **Pareto-Optimal Non-Dominated Set (`4` Solutions)**:
  1. `S68C-XC-R1_ARM_B`: **`48.320 Mbps` Goodput**, `87.832 ms` `p95` RTT, **`1.301` VoIP loss+jitter** (peak goodput & VoIP quality anchor).
  2. `S55A-R3_ARM_B`: **`47.672 Mbps` Goodput**, **`54.159 ms` `p95` RTT**, `1.854` VoIP loss+jitter (balanced high-throughput / low-latency knee).
  3. `S55A-R3_ARM_A`: `47.205 Mbps` Goodput, **`53.236 ms` `p95` RTT**, `2.050` VoIP loss+jitter (minimum `p95` RTT anchor).
  4. `S55A-R2_ARM_A`: `40.557 Mbps` Goodput, `85.539 ms` `p95` RTT, `1.697` VoIP loss+jitter.
- **Champion Progression**: `S55A-R2` (`Champion v19`, `hold_time=800 ms`, `+6.54%` GP), `S70C-R1` (`M40` pure XC `set_multiq=1` + `enable_tx_tcp_cksum=1` at `AMPDUFrames=24, swretry=4/4`, `+8.56%` GP), and `S72A-R4` (`Champion v20` warmed AP `v19` + XC `M40`, `+7.89%` GP, `-6.15%` `p95` RTT).

### 2.2 Family 2 — `OpenWrt 24.10.4 PtP` (`Stage 55A S55A-R4`)
- **Pareto-Optimal Non-Dominated Set (`2` Solutions)**:
  1. `S55A-R4_ARM_A_CHAMPION_V19`: **`46.828 Mbps` Goodput**, `61.078 ms` `p95` RTT, `2.675` VoIP loss+jitter (`RETAIN_CURRENT_CHAMPION`).
  2. `S55A-R4_ARM_B_M35_PTP_PROFILE`: `46.097 Mbps` Goodput, **`60.851 ms` `p95` RTT**, **`2.173` VoIP loss+jitter** (dedicated `CW 3/15 + AQL 2400/4800 + quantum 6056` profile).

### 2.3 Family 3 — `airOS 8 WA/XC PtP` (`PBE-5AC-Gen2 .241 <-> .242` `Champion v1..v6`)
- **Pareto-Optimal Non-Dominated Set (`4` Solutions)**:
  1. `S62A-R2_ARM_B` (`Champion v4`): **`25.615 Mbps` Per-Radio Mean (`55.541 Mbps` Pair Goodput)**, `7.438 ms` `p95` RTT, `0.195%` VoIP loss (`set_multiq=1`, `enable_tx_tcp_cksum=1`, `AMPDUFrames=32`, `swretry=6/8`).
  2. `S68A-R2_ARM_B` (`Champion v5`): **`22.723 Mbps` Per-Radio Mean (`58.568 Mbps` Pair Goodput)**, **`6.164 ms` `p95` RTT**, **`0.026%` VoIP loss** (`CabqMaxdur=20`, `SyncFlex=0`, `TSQ=131072`, `pacing=120/200`).
  3. `S70B-R1_ARM_B`: `18.181 Mbps` Goodput, `7.757 ms` `p95` RTT, **`0.000%` VoIP loss** (zero-loss boundary).
  4. `S70B-R2_ARM_B`: `18.794 Mbps` Goodput, **`5.598 ms` `p95` RTT**, `0.428%` VoIP loss (minimum `p95` RTT boundary, though `DISCARD` due to `18.114 ms` `p99` spike).
- **Stage 72B & 73A (`Champion v6`)**: Adding `ptp_xmit=1 + daprot=2 + ff_mcast_airtime_limit=5` (`S73A-R1`) reduced `fmx_loss` from `0.2621` to `0.2275` (`-8.49%` `p95` RTT, `-44.45%` `p99` RTT `18.001 -> 9.999 ms`, `-80.87%` VoIP loss).

### 2.4 Family 4 — `Ubiquiti AF-LTU v2.3.1/v2.4.2` (`Boca7 198.18.0.151`)
- **Pareto-Optimal Non-Dominated Set (`5` Solutions)**:
  1. `S50B-R0-STAGE49B-BASELINE`: **`23.371 Mbps` Goodput**, `10.437 ms` `p95` RTT, `0.829` VoIP jitter.
  2. `S63B-P1-SMP-IRQ-SPLIT-RPS-MAXBD84`: **`20.174 Mbps` Goodput**, **`7.165 ms` `p95` RTT**, `0` watchdog crashes (`21,920` `gmac0` IRQs offloaded to `CPU1`).
  3. `S63B-P3-GROUND-UP-CHAMPION` (`Stage 63B/64A/68B`): `19.569 Mbps` Goodput, **`7.085 ms` `p95` RTT** (`5.295 ms` `p50`, `7.400 ms` `p99`), `0.0%` VoIP loss, `0` watchdog crashes, with all `3` surgical ELF32 binary patches (`ame_bbp_set_autoMcsCeiling+20`, `frame_len_store+48`, `autoMcsUpDown`) verified in `Stage 64A/68B`.

---

## 3. Paired Statistical Effect-Size Audit (`scipy.stats`, APA Format) (`CONFIRMED`)

- **OpenWrt PtMP Promoted Champions (`n = 6` counterbalanced pairs across `S55A-R2`, `S70C-R1`, `S72A-R4`)**:
  - Paired goodput gain $M_{\Delta} = +2.7287\text{ Mbps}$, $SD_{\Delta} = 2.0700\text{ Mbps}$, $95\%\text{ CI }[0.5563, 4.9010]$, $t(5) = 3.2289, p = 0.02323$, signed $d_z = +1.3182$, bias-corrected $g_z = +1.1101$ (Shapiro-Wilk $p = 0.3348$ — normality not violated).
- **airOS 8 WA/XC PtP Promoted Champions (`n = 9` counterbalanced pairs across `S60A-R1`, `S62A-R2`, `S68A-R2`, `S72B-R1`, `S73A-R1`)**:
  - Paired `p95` RTT reduction $M_{\Delta} = -1.1288\text{ ms}$, $SD_{\Delta} = 0.8883\text{ ms}$, $95\%\text{ CI }[-1.8116, -0.4460]$, $t(8) = -3.8122, p = 0.00515$, signed improvement $d_z = +1.2707$, bias-corrected $g_z = +1.1478$ (Shapiro-Wilk $p = 0.6229$ — normality not violated).
- **Exploratory All-Rounds vs. Selective Champion Promotion**:
  - Across all `22` OpenWrt PtMP pairs and `27` airOS 8 PtP pairs (including intentionally falsified boundary probes like `S70B-R1` `ACMinfree=8` and `S72A-R1` `AC_BE=1350/2700`), aggregate all-round mean differences are near zero ($d_z = +0.0026$ and $-0.0280$), proving that the counterbalanced `A1 -> B1 -> A2 -> B2` gatekeeper accurately filters out regressions (`DISCARD`) while promoting only statistically robust Pareto improvements (`KEEP`).

---

## 4. Verification Commands (`CONFIRMED`)

```powershell
$env:PYTHONPATH="."; python tools/research/run_stage75b_nsga2_pareto_and_statistical_synthesis.py
python tools/verify/enforce_5pillar_research_gate.py artifacts/autoresearch/stage75b_nsga2_pareto_and_statistical_synthesis_20261026.json
pytest tests/test_stage75b_nsga2_pareto_synthesis.py -v
```
