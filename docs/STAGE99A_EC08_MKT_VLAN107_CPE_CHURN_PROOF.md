<!-- doc-head: STAGE99A_EC08_MKT_VLAN107_CPE_CHURN_PROOF.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 99A — Edge-Case 8 (`EC-08`): Live Mid-Stream CPE Churn & Re-Association Under `VLAN 107` (`MK1-251`) + 3-CPE Saturation

## 1. Executive Summary & Attribution (`CONFIRMED`)
- **Task ID**: `T-S99A-EC08-MKT-VLAN107-AND-3CPE-CHURN-RESILIENCE-PROOF`
- **Artifacts**:
  - Benchmark Runner: [`tools/benchmarks/run_stage99a_ec08_mkt_vlan107_cpe_churn_benchmark.py`](../tools/benchmarks/run_stage99a_ec08_mkt_vlan107_cpe_churn_benchmark.py)
  - Counterbalanced Receipt: [`artifacts/autoresearch/stage99a_ec08_mkt_vlan107_cpe_churn_benchmark.json`](../artifacts/autoresearch/stage99a_ec08_mkt_vlan107_cpe_churn_benchmark.json)
  - Verification Suite: [`tests/test_stage99a_ec08_mkt_vlan107_cpe_churn.py`](../tests/test_stage99a_ec08_mkt_vlan107_cpe_churn.py)
- **Subsystem Attribution**: `external controller` (`hostapd` `phy0-ap0.staX` WDS stale-interface cleanup + `TRIAL_IE` scan pulse) + `Linux` (`eth0.107` `802.1Q` `0:0..7:7` QoS mapping + `tx_queue_len=64` + `nftables` `fmx_s97a_vlan107_qos`) + `mac80211` (per-station `iTXQ` FQ-CoDel + `WMM AC_VO/AC_VI` isolation) + `ath10k` (`AQL` `1200/2400 us`) + `proprietary airMAX/LTU module` (`XC` `ath_dev.ko` `aggr_swretry=2` + `umac.ko` `set_multiq=3` + `rmmod ath_pktlog`).
- **Safety Invariants Verified (`CONFIRMED`)**:
  - `0` flash writes (`RAM-only` runtime execution with `45s` Non-DFS rollback watchdog).
  - `198.18.0.45` / `198.18.0.46` (`PBE-5AC-Gen2` PtP pair) and `198.18.0.2` (`ether2-sw-poe200`) / `.200` / `.201` (`SG-01` Guarida backbone) strictly untouched.
  - `EdgeSwitch 10XP Boca 7` (`gi7`, `MK1-251` `198.18.0.66`) strictly isolated in `VLAN 107` (`mkt_boca7_lab`).

---

## 2. `EC-08` Physical Mechanism Discovery (`FMX-S99A-01..02`, `CONFIRMED`)

### `FMX-S99A-01` (`CONFIRMED` — `hostapd` `4addr` WDS `AP/VLAN` `phy0-ap0.staX` Stale-Interface Lock on Unannounced `XC` Re-Association)
- **Observed Mechanism**: On an `OpenWrt` AP (`LAP-120 .20`) with `wds='1'` (`4addr: on`), `hostapd` dynamically creates a per-station `AP/VLAN` virtual interface (`phy0-ap0.sta1` for `WA .250`, `phy0-ap0.sta2` for `XC .198`). When a stock `airOS 8` `XC` station (`Rocket 5AC Prism Gen2` `.198`, `PUBLIC_DEVICE_0048`) executes a mid-stream `wpa_cli -i ath0 reassociate` under heavy load:
  1. In **Unoptimized Stock (Arm A)**: `phy0-ap0.sta2` remains bound to the old `4addr` key state while `wpa_supplicant` on `.198` flushes its BSS entry and enters `wpa_state=SCANNING` (`> 2500 ms` timeout), while unqueued retries (`aggr_swretry=8`) and `eth0.107` `tx_queue_len=1000` cause a transient latency spike (`p95 = 26.625 ms`, `p99 = 31.814 ms` in `A1`) on the **surviving** `Loco 5AC` (`WA .250`) $\rightarrow$ `MK1-251` (`198.18.0.66` `VLAN 107`) path.
  2. In **Stage 99A (Arm B)**: Releasing stale `phy0-ap0.sta2` state (`iw dev phy0-ap0.sta2 del`) + pulsing `TRIAL_IE` (`FMX-DISC-17`) + bounding `XC` software retries (`aggr_swretry=2, nonaggr_swretry=2`) cuts `XC` re-association recovery time by **`-53.48%` (`2500.0 ms -> 1163.0 ms`)** and restores `198.18.0.68` L3 forwarding at **`1.300 ms` RTT** (`0%` post-rejoin loss).

### `FMX-S99A-02` (`CONFIRMED` — Per-Station `mac80211` `iTXQ` + `VLAN 107` `802.1Q` Survivor Isolation)
- During the mid-window station churn (`t = +2.2s` into each `7s` saturation window), `Stage 99A` (`eth0.107` `802.1Q` `0:0..7:7` + `tx_queue_len=64` + `nftables` `fmx_s97a_vlan107_qos` `DSCP EF -> WMM AC_VO TID 6 / PCP 6` + `AP AQL 1200/2400 us`) isolates the surviving CPEs (`Loco 5AC WA .250` and `LiteBeam M5 XW .4`) and `MK1-251` (`198.18.0.66`) from the churning station's retry/re-key burst, cutting the surviving `WA (.250) -> MK1-251 (198.18.0.66)` **`p95` RTT spike by `-67.41%` (`19.567 ms -> 6.377 ms`)**, **`p99` RTT spike by `-66.28%` (`22.600 ms -> 7.620 ms`)**, and **E2E jitter by `-72.93%` (`5.836 ms -> 1.580 ms`)** with **`0.0%` E2E packet loss**.

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`S99A-R1`, `CONFIRMED`)

| Metric (`A1 -> B1 -> A2 -> B2` Mean Under Mid-Stream Churn) | Arm A (Unoptimized Churn Baseline) | Arm B (`Stage 99A` Churn-Isolated Stack) | Delta (`Arm B vs Arm A`) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Survivor `WA (.250) -> MK1-251` E2E `p50` RTT (`ms`)** | `2.341 ms` | **`2.167 ms`** | **`-7.43%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E `p95` RTT (`ms`)** | `19.567 ms` | **`6.377 ms`** | **`-67.41%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E `p99` RTT (`ms`)** | `22.600 ms` | **`7.620 ms`** | **`-66.28%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E Jitter (`ms`)** | `5.836 ms` | **`1.580 ms`** | **`-72.93%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E Packet Loss (`%`)** | `0.00%` | **`0.00%`** | **`0.00%`** | `CONFIRMED` |
| **`LAP-120 (.20) -> MK1-251` `VLAN 107` `p50` RTT (`ms`)** | `2.864 ms` | **`1.685 ms`** | **`-41.17%`** | `CONFIRMED` |
| **`LAP-120 (.20) -> MK1-251` `VLAN 107` `p99` RTT (`ms`)** | `61.806 ms` | **`40.054 ms`** | **`-35.19%`** | `CONFIRMED` |
| **Surviving Sector `p95` RTT (`WA + AP-MK1 + XW`) (`ms`)** | `37.545 ms` | **`32.500 ms`** | **`-13.44%`** | `CONFIRMED` |
| **Surviving Sector `p99` RTT (`WA + AP-MK1 + XW`) (`ms`)** | `49.502 ms` | **`37.258 ms`** | **`-24.73%`** | `CONFIRMED` |
| **Survivor `WA (.250)` Air-Only `p95` RTT (`ms`)** | `77.850 ms` | **`64.607 ms`** | **`-17.01%`** | `CONFIRMED` |
| **IPTV Dual-Stream (`AC_VI` `DSCP CS4`) Jitter (`ms`)** | `1.790 ms` | **`1.436 ms`** | **`-19.80%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF`) Packet Loss (`%`)** | `0.57%` | **`0.93%` (`< 1.0%` SLA)** | `0` `mac80211` `aqm` `TID 6` drops | `CONFIRMED` |
| **Churned `XC (.198)` Re-Association Recovery (`ms`)** | `2500.0 ms` (Scan stall) | **`1163.0 ms`** (`1.30 ms` post-rejoin RTT) | **`-53.48%`** | `CONFIRMED` |

### Per-Window Breakdown (`A1 -> B1 -> A2 -> B2`)

| Phase | Survivor `WA -> MK1-251` `p50` / `p95` / `p99` (`ms`) | Survivor `WA -> MK1-251` Jitter (`ms`) | `LAP-120 -> MK1-251` `p50` / `p99` (`ms`) | Survivor Sector `p95` / `p99` (`ms`) | IPTV Jitter (`ms`) | `:2000` `btest` Handshake `p50` (`ms`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `2.296` / `26.625` / `31.814 ms` | `8.298 ms` | `5.160` / `72.520 ms` | `45.045` / `56.145 ms` | `1.724 ms` | `4.262 ms` (`0x01000000`) |
| **`B1`** | **`2.191` / `7.607` / `8.746 ms`** | **`1.980 ms`** | **`1.494` / `39.816 ms`** | **`31.925` / `37.554 ms`** | **`1.688 ms`** | `4.219 ms` (`0x01000000`) |
| **`A2`** | `2.387` / `12.510` / `13.386 ms` | `3.373 ms` | `0.567` / `51.092 ms` | `30.044` / `42.859 ms` | `1.856 ms` | `4.198 ms` (`0x01000000`) |
| **`B2`** | **`2.144` / `5.147` / `6.494 ms`** | **`1.180 ms`** | **`1.875` / `40.291 ms`** | **`33.075` / `36.962 ms`** | **`1.183 ms`** | `4.205 ms` (`0x01000000`) |
