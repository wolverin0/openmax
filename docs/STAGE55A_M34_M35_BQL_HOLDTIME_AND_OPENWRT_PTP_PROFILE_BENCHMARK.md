<!-- doc-head: STAGE55A_M34_M35_BQL_HOLDTIME_AND_OPENWRT_PTP_PROFILE_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 55A — M34 (`eth0` BQL `hold_time=800` ms at `limit_min=4542` -> `Stage 55A Champion v19`) & M35 (Dedicated OpenWrt AC-to-AC PtP vs 3-CPE PtMP Profile) Physical Benchmark

- **Task ID**: `T-S55A-M34-M35-OPENWRT-PTP-AND-PTMP-BQL-HOLDTIME-AND-AQL-REFILL-BENCH`
- **Date**: 2026-10-26
- **Hardware Under Test**:
  - **3-CPE 5 GHz PtMP Sector (`S55A-R1`, `S55A-R2`)**:
    - **AP**: Ubiquiti LiteAP 120 (`198.18.0.43`, OpenWrt 24.10.4 `Linux 6.6.110` `ath79`, `QCA955x` + `QCA988x` 2x2 VHT20 `5180 MHz`)
    - **CPE #1 (WA)**: NanoStation 5AC Loco (`198.18.0.47` / `198.18.0.67`, OpenWrt 24.10.4 `Linux 6.6.110`, `PUBLIC_DEVICE_0036`, `phy0-ap0.sta2`)
    - **CPE #2 (XC)**: Rocket Prism 5AC Gen2 (`198.18.0.64` / `198.18.0.68`, airOS `XC.v8.7.19`, `PUBLIC_DEVICE_0048`, `phy0-ap0.sta1`)
    - **CPE #3 (XW)**: LiteBeam M5 (`198.18.0.52` Over-The-Air, airOS `XW.v6.3.22`, `PUBLIC_DEVICE_0066`, `phy0-ap0` 1x1 N)
  - **Dedicated OpenWrt AC-to-AC Single-Link PtP Mode (`S55A-R3`, `S55A-R4`)**:
    - `LAP-120` (`198.18.0.43`) $\leftrightarrow$ `Loco 5AC` (`198.18.0.47` / `198.18.0.67`) 4-addr WDS PtP link under Triple-Play load.
- **Safety & Scope Boundary**:
  - `ram_only = True`, `flash_writes = 0`, `production_radios_touched = 0`
  - `untouched_radios = ["198.18.0.45", "198.18.0.46", "198.18.0.48"]` (`0` packets/connections to `PowerBeam 5AC Gen2` or `LiteBeam 5AC Gen2`).
- **Starting Baseline (Control Arm A)**:
  - **`Stage 52A Champion v18` (`S52A-R3: M33a_COMBINED_BUDGET_USECS_6000_AND_BQL_MIN_4542`)**:
    - `LAP-120` (`.20`) & `Loco 5AC` (`.250`) `eth0` BQL `limit_min=4542` (`3×MTU`), `limit_max=42392` (`28×MTU`), `hold_time=1000` ms + `eth0` `tx_queue_len=1000`, `br-lan/phy0-*` `tx_queue_len=256`
    - `net.core.dev_weight_tx_bias=2`, `net.core.netdev_budget=600`, `net.core.netdev_budget_usecs=20000`
    - `LAP-120` `fq_quantum=4542` / `Loco 5AC` `fq_quantum=1514`, `fq_memory_limit=4194304`, `fq_limit=2048/1024`, `aql_txq_limit` `VO=300/600`, `VI=1200/2400`, `BE=1500/3000` (AP) / `900/1500` (CPE), `aql_threshold=5000/4000`, station `airtime_weight` `768:512:128`

---

## 1. Summary of Physical Counterbalanced Rounds (`S55A-R1 .. S55A-R4`, `16` Windows)

| Round | Mechanism ID | Mode | Treatment Arm B vs Control Arm A (`v18`) | Goodput (`A -> B`) | Loaded `p95` RTT (`A -> B`) | Loaded `p99` RTT (`A -> B`) | IPTV Bitrate / Loss (`A -> B`) | VoIP Loss (`A -> B`) | Composite Pareto | Decision / Status |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S55A-R1`** | `M34a_BQL_HOLD_TIME_600_WITH_MIN_4542_MAX_42392_3CPE_PTMP` | 3-CPE PtMP | `eth0` BQL `hold_time=600` ms (vs `1000` ms) with `limit_min=4542`, `limit_max=42392` | `43.358 -> 43.602 Mbps` (`+0.563%`) | `90.601 -> 96.540 ms` (`+6.555%`, `p50` `35.769 -> 31.331 ms` **`-12.41%`**) | `90.601 -> 101.721 ms` | `4.965 -> 4.960 Mbps` / `0.0352%` (`-8.545%` jitter) | `0.0%` | `-1.7315%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S55A-R2`** | **`M34b_BQL_HOLD_TIME_800_WITH_MIN_4542_MAX_42392_3CPE_PTMP`** | **3-CPE PtMP** | **`eth0` BQL `hold_time=800` ms (vs `1000` ms) with `limit_min=4542` (`3×MTU`), `limit_max=42392` (`28×MTU`)** | **`40.557 -> 43.209 Mbps` (`+6.539%`)** | **`85.539 -> 81.657 ms` (`-4.538%`, `< 82 ms`!)** | **`90.749 -> 84.180 ms` (`-7.239%`)** | **`4.970 -> 4.960 Mbps` / `0.00%` loss** | **`0.00%` loss** | **`+8.1273%`** | **`PROMOTE_NEW_CHAMPION` (`Stage 55A Champion v19`, `CONFIRMED`)** |
| **`S55A-R3`** | `M35a_OPENWRT_PTP_DEDICATED_PROFILE_AQL_HIGH_6000_QUANTUM_4542` | 1-CPE PtP | `AC_BE` `aql_txq_limit=3000/6000`, `aql_threshold=18000`, symmetric `fq_quantum=4542`, `fq_memory_limit=3145728` | `47.205 -> 47.672 Mbps` (**`+0.989%`**) | `53.236 -> 54.159 ms` (`+1.734%`) | `64.611 -> 62.615 ms` (**`-3.089%`**) | `4.965 -> 4.970 Mbps` / `0.00%` loss | `0.00%` (`-9.561%` jitter) | `+0.3910%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` by strict `p95_b <= p95_a` gate) |
| **`S55A-R4`** | `M35b_OPENWRT_PTP_DEDICATED_PROFILE_AQL_HIGH_6000_QUANTUM_6056_4MTU_GRO_150US` | 1-CPE PtP | `fq_quantum=6056` (`4×MTU`), `AC_BE` `aql=3000/6000`, `tx_queue_len=500`, `gro_flush_timeout=150000` ns, `napi_defer_hard_irqs=2` | `46.828 -> 46.097 Mbps` (`-1.561%`) | `61.078 -> 60.851 ms` (**`-0.372%`**) | `68.221 -> 68.123 ms` (`-0.144%`) | `4.950 -> 4.970 Mbps` / `0.00%` (`-9.842%` jitter) | `0.00%` (`-18.766%` jitter) | `-1.4309%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |

---

## 2. Key Technical Findings

### 2.1 Why `eth0` BQL `hold_time=800` ms (`M34b`) Succeeds at `limit_min=4542` (`3×MTU`) Where `hold_time=750` ms Failed at `limit_min=3028` (`2×MTU`) (`CONFIRMED`)
- In `Stage 51A` (`S51A-R1`), shortening `eth0` `byte_queue_limits/hold_time` from `1000` ms to `750` ms when `limit_min=3028` (`2×MTU`) allowed Linux DQL (`lib/dynamic_queue_limits.c`) to decay `eth0` `limit` down to `3028` bytes mid-window, which clipped `LAP-120`'s `4542`-byte (`3×MTU`) `mac80211` `fq_quantum` bursts and inflated `p95` RTT by `+5.017%` (`106.593 -> 111.941 ms`).
- Once `Stage 52A Champion v18` raised `limit_min=4542` (`3×MTU`, matching `fq_quantum=4542`), DQL can never decay below one complete `3×MTU` DRR quantum.
- Sweeping `hold_time` at `limit_min=4542` (`S55A-R1` `600` ms vs `S55A-R2` `800` ms vs `1000` ms) revealed the exact convex optimum:
  - At **`hold_time=600` ms (`S55A-R1`)**, `p50` RTT dropped `-12.41%` (`35.769 -> 31.331 ms`) and IPTV jitter dropped `-8.545%`, but `p95` RTT rose slightly (`90.601 -> 96.540 ms`, `+6.555%`).
  - At **`hold_time=800` ms (`S55A-R2`, `Stage 55A Champion v19`)**, 3-CPE aggregate goodput rose **`+6.539%` (`40.557 -> 43.209 Mbps`)**, loaded 3-CPE `p95` RTT dropped **`-4.538%` (`85.539 -> 81.657 ms`, well below `< 95 ms`)**, loaded `p99` RTT dropped **`-7.239%` (`90.749 -> 84.180 ms`)**, and all `5,695` Dual `1080p60` IPTV datagrams (`4.960 Mbps`), `1,200` VoIP frames (`127 Kbps`), and 3-CPE ICMP probes completed with **`0.00%` loss** (`Pareto +8.1273%`).

### 2.2 Dedicated OpenWrt AC-to-AC PtP Profile Characterization (`LAP-120 .20 <-> Loco 5AC .250`, `S55A-R3` & `S55A-R4`, `CONFIRMED`)
- Under single-link AC-to-AC PtP Triple-Play load (`S55A-R3` and `S55A-R4`):
  - **`Stage 52A/55A Champion` (`AC_BE=1500/3000` us AP / `900/1500` us CPE, `fq_quantum=4542` AP / `1514` CPE, `tx_queue_len=256`, `eth0` BQL `4542..42392`)** achieves **`46.83–47.21 Mbps` Triple-Play goodput** with **`28.46–29.53 ms` loaded `p50` RTT** and **`53.24–61.08 ms` loaded `p95` RTT** (`0.00%` IPTV/VoIP/ICMP loss).
  - **`M35a` (`AC_BE aql_txq_limit=3000/6000` us, `aql_threshold=18000`, symmetric `fq_quantum=4542`)** increases single-link PtP bulk goodput by **`+0.989%` (`47.205 -> 47.672 Mbps`)**, cuts PtP `p99` RTT by **`-3.089%` (`64.611 -> 62.615 ms`)**, and cuts VoIP jitter by **`-9.561%` (`2.050 -> 1.854 ms`)**, at the cost of `+0.92 ms` (`+1.734%`) `p95` RTT (`53.236 -> 54.159 ms`).
  - **`M35b` (`fq_quantum=6056` `4×MTU` + `tx_queue_len=500` + `gro_flush_timeout=150000` ns + `napi_defer_hard_irqs=2`)** cuts PtP `p95` RTT by `-0.372%` (`61.078 -> 60.851 ms`), IPTV jitter by `-9.842%`, and VoIP jitter by `-18.766%`, but trims bidirectional TCP goodput by `-1.561%` (`46.828 -> 46.097 Mbps`).
  - **Practical Engineering Rule for OpenWrt PtP Links (`PowerBeam 5AC` / `LiteBeam 5AC` / `LAP-120 <-> Loco 5AC`)**: Keep **`Stage 55A Champion v19` (`eth0` BQL `limit_min=4542, limit_max=42392, hold_time=800` ms + `fq_quantum=4542/1514` + `AQL BE=1500/3000` AP / `900/1500` CPE)** as the unified PtP + PtMP Triple-Play profile; use `M35a` (`BE=3000/6000` us) only on pure bulk-backhaul PtP links without interactive latency SLAs.

---

## 3. Artifacts & Code References
- Physical Benchmark Runner: [`tools/bench/run_stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench.py`](<repo>/tools/bench/run_stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench.py)
- Canonical Artifact JSON: [`artifacts/autoresearch/stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench_20261025.json`](<repo>/artifacts/autoresearch/stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench_20261025.json)
- Golden Profile Overlay (`STAGE55A_CHAMPION_V19_OVERLAY`): [`controller/multiradio_golden_profile_applicator.py`](<repo>/controller/multiradio_golden_profile_applicator.py)
- Verification Test Suite: [`tests/test_stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench.py`](<repo>/tests/test_stage55a_m34_m35_bql_holdtime_and_openwrt_ptp_profile_bench.py)
