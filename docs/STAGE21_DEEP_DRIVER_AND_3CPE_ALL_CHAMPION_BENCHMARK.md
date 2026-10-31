<!-- doc-head: STAGE21_DEEP_DRIVER_AND_3CPE_ALL_CHAMPION_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 21 — OpenWrt Deep Driver (`pktlog_filter`, `tcp_notsent_lowat`, `netdev_budget`) & 3-CPE Heterogeneous All-Champion Co-Design Benchmark

- **Task ID**: `T-S21-OPENWRT-DEEP-DRIVER-AND-3CPE-ALL-CHAMPION-BENCH`
- **Completed UTC**: `2026-10-25T15:05:44Z`
- **Status**: `PASS_STAGE21_DEEP_DRIVER_AND_3CPE_ALL_CHAMPION_COMPLETE`
- **Receipt**: [`artifacts/autoresearch/stage21_deep_driver_and_3cpe_all_champion_20261025.json`](../artifacts/autoresearch/stage21_deep_driver_and_3cpe_all_champion_20261025.json)
- **Runner**: [`tools/bench/run_stage21_deep_driver_and_3cpe_all_champion_bench.py`](../tools/bench/run_stage21_deep_driver_and_3cpe_all_champion_bench.py)

---

## 1. Incremental Champion-as-Baseline Methodology

Every round in Stage 21 starts strictly from the **Stage 19 Champion v2** profile (`A = Current Champion v2`, never reverting to Stock as baseline) and tests an incremental mutation (`B = Current Champion v2 + Untested Variable`) using `A1 -> B1 -> A2 -> B2` interleaving on the physical 5 GHz PtMP bench (`5825 MHz / 20 MHz`, `LAP-120` AP `198.18.0.81` + `NanoStation 5AC Loco` `198.18.0.67` + `Rocket Prism 5AC` `198.18.0.64` + `LiteBeam M5` `198.18.0.129`). All operations are 100% RAM-only (`persistent_flash_writes: false`).

---

## 2. Physical Benchmark Results (`A1 -> B1 -> A2 -> B2`)

| Round | Control Arm `A` (Current Champion) | Treatment Arm `B` (Champion + Candidate Mutation) | Arm `A` Goodput | Arm `B` Goodput | Goodput $\Delta$ | Arm `A` `p95` RTT | Arm `B` `p95` RTT | `p95` RTT $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S21-R1`** | Stage 19 Champion v2 (`pktlog_filter=0x40`, `ani_enable=1`, `quiet_period=0`) | Stage 19 Champion v2 + `pktlog_filter=0` + `ani_enable=1` + `quiet_period=0` | `75.32 Mbps` | `76.37 Mbps` | **`+1.39%`** | `15.61 ms` | `20.51 ms` | `+31.37%` | **`RETAIN_CURRENT_CHAMPION`** (`pktlog_filter=0x40`) |
| **`S21-R2`** | Stage 19 Champion v2 (`tcp_notsent_lowat=4294967295`, `netdev_budget=300`) | Stage 19 Champion v2 + `tcp_notsent_lowat=16384` + `netdev_budget=600` | `74.79 Mbps` | `74.53 Mbps` | `-0.35%` | `19.92 ms` | **`17.46 ms`** | **`-12.35%`** | **`KEEP_NEW_CHAMPION`** |
| **`S21-R3`** | 3-CPE Sector: `LAP-120` AP Multi-CPE Champion ONLY + Stock STAs (`256:256:256`) | **3-CPE All-Champion Co-Design**: `LAP-120` AP Champion + `Loco 5AC` STA Champion + `Rocket Prism 5AC` STA Champion + `LiteBeam M5` STA Champion (`512:512:128`) | `39.49 Mbps` | `39.12 Mbps` | `-0.94%` | `63.36 ms` | **`57.09 ms`** | **`-9.89%`** | **`KEEP_NEW_CHAMPION`** |

---

## 3. Key Findings & Promotion to `Champion v3`

1. **`S21-R1` (`pktlog_filter=0` vs `0x40`)**:
   - While disabling `pktlog_filter` increased raw goodput by `+1.39%` (`75.32 -> 76.37 Mbps`), `p95` RTT increased (`15.61 -> 20.51 ms`) because `ath10k` on `QCA988x` uses the `0x40` rate-control completion event path to update host-visible airtime/TX completion state promptly. Our fail-closed Pareto gate (`IncrementalChampionPromoter`) rejected `S21-R1` and retained `pktlog_filter=0x40`.
2. **`S21-R2` (`tcp_notsent_lowat=16384` + `netdev_budget=600`, `KEEP_NEW_CHAMPION`)**:
   - Adding socket-level unsent-byte backpressure (`sysctl -w net.ipv4.tcp_notsent_lowat=16384`) and doubling NAPI softirq drain budget (`sysctl -w net.core.netdev_budget=600`) on top of `tcp_limit_output_bytes=131072` cut `p95` loaded RTT by another **`-12.35%` (`19.92 -> 17.46 ms`)** at virtually identical goodput (`74.79 -> 74.53 Mbps`, `-0.35%`).
3. **`S21-R3` (`3-CPE All-Champion Co-Design`, `KEEP_NEW_CHAMPION`)**:
   - Applying the verified STA Champions simultaneously on all three heterogeneous CPEs (`NanoStation 5AC Loco` OpenWrt STA + `Rocket Prism 5AC` `XC` STA + `LiteBeam M5` `XW` 1x1 STA) plus contract `airtime_weight` `512:512:128` reduced 3-CPE sector `p95` RTT by **`-9.89%` (`63.36 -> 57.09 ms`, `0.0%` loss)** and cut `Loco 5AC` `p95` RTT under 3-CPE load to `41.57 ms` (`B2`).
4. **Final Live RAM State**:
   - All 4 radios on the 5 GHz PtMP bench (`LAP-120` AP, `NanoStation 5AC Loco` STA, `Rocket Prism 5AC` STA, and `LiteBeam M5` STA) were verified at completion with the promoted `Champion v3` (`S21-R2` + `S21-R3`) parameters active in RAM (`persistent_flash_writes: false`).
