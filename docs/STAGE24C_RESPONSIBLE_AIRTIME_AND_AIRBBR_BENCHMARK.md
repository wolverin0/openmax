<!-- doc-head: STAGE24C_RESPONSIBLE_AIRTIME_AND_AIRBBR_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 24C — Physical Responsible-Airtime Overhead Accounting & AirBBR Pacing Benchmark

- **Task ID**: `T-S24C-PHYSICAL-RESPONSIBLE-AIRTIME-AND-AIRBBR-BENCH`
- **Completed UTC**: `2026-10-25T15:38:38Z`
- **Status**: `PASS_STAGE24C_RESPONSIBLE_AIRTIME_AND_AIRBBR_COMPLETE`
- **Receipt**: [`artifacts/autoresearch/stage24c_responsible_airtime_and_airbbr_20261025.json`](../artifacts/autoresearch/stage24c_responsible_airtime_and_airbbr_20261025.json)
- **Runner**: [`tools/bench/run_stage24c_responsible_airtime_and_airbbr_bench.py`](../tools/bench/run_stage24c_responsible_airtime_and_airbbr_bench.py)

---

## 1. Incremental Champion-as-Baseline Methodology

Every round in Stage 24C starts strictly from our verified **Stage 21 Champion v3** profile (`A = Current Champion v3`, never reverting to Stock as baseline) and evaluates two literature-sourced mechanisms from Stage 24B using `A1 -> B1 -> A2 -> B2` interleaving on the physical 4-radio 5 GHz PtMP bench (`5180 MHz / 20 MHz`, `LAP-120` AP `198.18.0.81` + `NanoStation 5AC Loco` `198.18.0.67` + `Rocket Prism 5AC Gen2` `198.18.0.64` + `LiteBeam M5` `198.18.0.52`). All operations are 100% RAM-only (`persistent_flash_writes: false`):

1. **Mechanism 1 — `Responsible Airtime` Overhead Accounting (Yu & Park, *Sensors* 2018, `doi:10.3390/s18113658`)**:
   - Standard `mac80211` airtime fairness (`airtime_flags=7`) accounts for data PPDU TX/RX airtime but under-counts per-PPDU MAC/IFS/RTS-CTS and TCP ACK turnaround overhead on slower `1x1` (`LiteBeam M5`) or multi-retry stations.
   - Treatment (`B`): Per-AC `aql_txq_limit` differentiation (`AC_VO 0: 750/1500 us`, `AC_VI 1: 1200/2400 us`, `AC_BE 2: 1500/3000 us`, `AC_BK 3: 1500/3000 us`, `aql_threshold=5000`) plus overhead-corrected `airtime_weight` `640:512:96` (`Loco 5AC : Rocket Prism 5AC : LiteBeam M5`).
2. **Mechanism 2 — `AirBBR` MAC-Aware Pacing & Small-Queue FQ Pacing (Zhou et al. 2026, `doi:10.2139/ssrn.7434484`)**:
   - Tightening Linux TCP pacing ratios (`sysctl -w net.ipv4.tcp_pacing_ca_ratio=110 net.ipv4.tcp_pacing_ss_ratio=150` vs kernel defaults `120 / 200`) and bounding `fq_codel` memory (`memory_limit 4mb`) on top of Stage 21 Champion v3 (`tcp_limit_output_bytes=131072`, `tcp_notsent_lowat=16384`, `netdev_budget=600`).

---

## 2. Physical Benchmark Results (`A1 -> B1 -> A2 -> B2`)

| Round | Control Arm `A` (Stage 21 Champion v3) | Treatment Arm `B` (Champion v3 + Stage 24C Candidate) | Arm `A` Goodput | Arm `B` Goodput | Goodput $\Delta$ | Arm `A` `p95` RTT | Arm `B` `p95` RTT | `p95` RTT $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S24C-R1`** (1-CPE `LAP-120 <-> Loco 5AC`) | Stage 21 Champion v3 (`tcp_pacing_ca_ratio=120`, `tcp_pacing_ss_ratio=200`, `aql=900/1500`) | Stage 21 Champion v3 + **AirBBR Pacing** (`tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `fq_codel memory_limit 4mb`) | `77.09 Mbps` | `75.12 Mbps` | `-2.56%` | `19.74 ms` | **`19.11 ms`** | **`-3.17%`** | **`KEEP_NEW_CHAMPION`** |
| **`S24C-R2`** (3-CPE Heterogeneous Sector) | Stage 21 3-CPE All-Champion v3 (`airtime_weight 512:512:128`, `aql_txq_limit 1850/3700`, `aql_threshold 6000`) | Stage 21 3-CPE All-Champion v3 + **Responsible-Airtime Overhead-Corrected Weights** (`640:512:96`, per-AC `aql_txq_limit` `750..1500/1500..3000`, `aql_threshold 5000`) + **AirBBR Pacing** | `45.73 Mbps` | **`50.84 Mbps`** | **`+11.19%`** | `95.09 ms` | **`73.50 ms`** | **`-22.70%`** | **`KEEP_NEW_CHAMPION`** |

---

## 3. Key Findings & Promotion to `Champion v4`

1. **`S24C-R1` (`1-CPE AirBBR Pacing + fq_codel memory_limit 4mb` — `KEEP_NEW_CHAMPION`)**:
   - Lowering `tcp_pacing_ca_ratio` (`120 -> 110`) and `tcp_pacing_ss_ratio` (`200 -> 150`) alongside `fq_codel memory_limit 4mb` on top of Stage 21 Champion v3 reduced 1-CPE bidirectional `p95` RTT by **`-3.17%` (`19.739 -> 19.114 ms`)** with **`0.0%` packet loss** in both treatment phases (`B1` and `B2`, compared to `1.82%` loss in `A2`), while maintaining `75.115 Mbps` (`-2.56%`).
2. **`S24C-R2` (`3-CPE Responsible-Airtime Overhead Accounting + AirBBR Co-Design` — `KEEP_NEW_CHAMPION`)**:
   - On the 3-CPE heterogeneous sector (`Loco 5AC` `2x2 VHT20` + `Rocket Prism 5AC` `2x2 VHT20` + `LiteBeam M5` `1x1 HT20`), combining Responsible-Airtime overhead-corrected weights (`640:512:96`), per-AC `aql_txq_limit` (`0: 750/1500`, `1: 1200/2400`, `2: 1500/3000`, `3: 1500/3000`, `aql_threshold=5000`), and AirBBR pacing simultaneously improved aggregate 3-CPE goodput by **`+11.19%` (`45.728 -> 50.843 Mbps`, `2.542 Mbps/MHz`)** AND reduced worst-case sector `p95` RTT by **`-22.70%` (`95.088 -> 73.502 ms`)**.
   - Mean packet loss across the 3-CPE sector dropped from `5.42%` (`A1: 0.0%`, `A2: 10.83%`) to `2.23%` (`B1: 1.28%`, `B2: 3.17%`), with `0.0%` loss on both `Rocket Prism 5AC` and `LiteBeam M5` across both `B1` and `B2`.
3. **Final Live RAM State (`Champion v4`)**:
   - All 4 radios on the 5 GHz bench (`LAP-120` AP, `NanoStation 5AC Loco` STA, `Rocket Prism 5AC Gen2` STA, and `LiteBeam M5` STA) were verified at completion with the promoted **Stage 24C Champion v4** parameters active in RAM (`persistent_flash_writes: false`).
