<!-- doc-head: STAGE12_PB_050_051_SCHEDULER_TIMING_AND_SLOT_GATE_SPEC.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PB-050 & PB-051 Scheduler Timing & Slot Gate Specification

**Workstream**: Phase 0 Physical-Boundary Program (`PB-050` & `PB-051`)  
**Status**: `OFFLINE_HARNESS_READY` (`automatic_execution_allowed = False`)  
**Implementation**: [`controller/pb_050_051_scheduler_timing_harness.py`](../controller/pb_050_051_scheduler_timing_harness.py)  
**Artifact Fixture**: [`artifacts/qca988x/pb_050_051_timing_jitter_fixture.json`](../artifacts/qca988x/pb_050_051_timing_jitter_fixture.json)

---

## 1. Scientific Objective & Physical Boundary

Standard Linux host queue-gating (`mac80211` TXQ + `hrtimer` + WMI/HTT descriptor enqueue across PCIe/AHB) traverses multiple asynchronous queueing layers before the QCA988x PCU transmits on air. Our static reverse-engineering of `WA.v8.7.25` and `XC.v8.7.25` (`ubnt_poll.ko`) revealed why Ubiquiti's airMAX AC TDD engine (`ac_poll_Tdd`) executes its slot timer and guard-interval state machine directly inside the QCA988x Xtensa target via `WMI_UBNT_POLL_CMDID` (`0x9064`), configuring microsecond guard parameters (`up_dur_gap = 260..325 us`, `down_dur_gap = 210..275 us`).

Gates **PB-050** and **PB-051** establish the quantitative timing truth and promotion criteria for host vs. target slot scheduling:

1. **PB-050 (Host Queue-Gating vs. Target TSF Timer Jitter Benchmark)**:
   - Measures the cumulative distribution function (CDF: `p50`, `p95`, `p99`, `max`) of TX burst-start jitter ($\mu\text{s}$) using external SDR RF envelope energy detection (`SdrBurstObservation`).
   - Computes the minimum safe guard interval floor at link distance $d_{\text{km}}$:
     $$\text{GuardFloor}_{\mu\text{s}} = 2 \cdot J_{p99} + \frac{2 \cdot d_{\text{km}}}{c} + \text{SIFS/Turnaround}_{\mu\text{s}}$$
2. **PB-051 (Target-Resident Sub-ms / 2ms Slot Scheduler Feasibility Gate)**:
   - Evaluates whether a target-resident TSF/PCU slot gate on a `PB-040`-qualified target image satisfies all three mandatory physical-boundary gates under 2-CPE hidden-node contention:
     - `jitter_p99_us <= 250.0 us`
     - `out_of_slot_violation_rate_pct < 0.5%`
     - Paired 6-block A/B/A/B evaluation via [`RegressionGatekeeper`](../analysis/regression_gate/gatekeeper.py) reaches `PROMOTE` on `goodput_per_mhz` (`channel_width_mhz=20`) and `p99_lat_ms`.

---

## 2. Benchmark Fixture Comparison (`6.0 km` PtMP Link)

| Metric | Host Queue-Gating (`15 ms` slots) | Target TSF Timer (`2 ms` slots) | Physical Interpretation |
| :--- | :---: | :---: | :--- |
| `jitter_p50_us` | `417.6 us` | `18.87 us` | `22.1x` tighter median release timing |
| `jitter_p95_us` | `1242.0 us` | `52.7 us` | Eliminates PCIe/HTT ring wake-up tail |
| `jitter_p99_us` | `1660.0 us` | `80.0 us` | `20.75x` reduction in p99 slot-boundary jitter |
| `minimum_safe_guard_interval_us` | `3392.03 us` | `232.03 us` | Matches airOS `up_dur_gap = 260 us` (`HT20`) |
| `sub_ms_slots_physically_credible` | `False` | `True` | Host gating is restricted to coarse `>=15 ms` windows |
| `out_of_slot_violation_rate_pct` | `0.0%` (at `3.8 ms` guard) | `0.0%` (at `260 us` guard) | Zero out-of-slot CSMA leakage |

---

## 3. Verification

Run the offline test suite:

```powershell
pytest tests/test_pb_050_051_scheduler_timing_harness.py -v
```
