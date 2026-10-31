<!-- doc-head: STAGE102D_MKT_VLAN107_CSA_UNDER_LOAD_PROOF.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 102D — Live Zero-Downtime `802.11h` Channel Switch Announcement (`CSA` `5180 MHz <-> 5200 MHz`) Under `VLAN 107` (`MK1-251`) + 3-CPE Saturation

## 1. Executive Summary & Attribution (`CONFIRMED`)
- **Task ID**: `T-S102D-LIVE-MKT-VLAN107-CSA-DFS-EVASION-UNDER-BTEST-LOAD`
- **Artifacts**:
  - Benchmark Runner: [`tools/benchmarks/run_stage102d_mkt_vlan107_csa_under_load.py`](../tools/benchmarks/run_stage102d_mkt_vlan107_csa_under_load.py)
  - Counterbalanced Receipt: [`artifacts/autoresearch/stage102d_mkt_vlan107_csa_under_load.json`](../artifacts/autoresearch/stage102d_mkt_vlan107_csa_under_load.json)
  - Verification Suite: [`tests/test_stage102d_mkt_vlan107_csa_under_load.py`](../tests/test_stage102d_mkt_vlan107_csa_under_load.py)
- **Subsystem Attribution**: `external controller` (`ubus call hostapd.phy0-ap0 switch_chan` `bcn_count=10, block_tx=false` + `/usr/sbin/fmx_wds_churn_healer.sh`) + `Linux` (`eth0.107` `802.1Q` `0:0..7:7` + `tx_queue_len=64` + `nftables` `fmx_s97a_vlan107_qos`) + `mac80211` (`ieee80211_channel_switch` / `ieee80211_sta_process_chanswitch` + `WMM AC_VO/AC_VI`) + `ath10k` (`ath10k_mac_update_channel_list` + `AQL` `1200/2400 us`) + `proprietary airMAX/LTU module` (`XC` `umac.ko` `ieee80211_doth_switch_channel` `doth=1` + `set_multiq=3`).
- **Safety Invariants Verified (`CONFIRMED`)**:
  - `0` flash writes (`RAM-only` runtime execution with `45s` Non-DFS rollback watchdog).
  - `198.18.0.45` / `198.18.0.46` (`PBE-5AC-Gen2` PtP pair) and `198.18.0.2` (`ether2-sw-poe200`) / `.200` / `.201` (`SG-01` Guarida backbone) strictly untouched.
  - `EdgeSwitch 10XP Boca 7` (`gi7`, `MK1-251` `198.18.0.66`) strictly isolated in `VLAN 107` (`mkt_boca7_lab`).

---

## 2. Physical Mechanism Analysis (`FMX-S102D-01..02`, `CONFIRMED`)

### `FMX-S102D-01` (`CONFIRMED` — `hostapd` `switch_chan` `block_tx=false, bcn_count=10` vs Blocking `block_tx=true, bcn_count=5` Under `VLAN 107` Load)
- In each `7s` saturation window of `A1 -> B1 -> A2 -> B2`, `LAP-120` (`.20`) executed **two live 802.11h Channel Switch Announcements (`CSA`)**:
  - **Hop 1 (`t = +1.8s`)**: `Channel 36 (5180 MHz, VHT20) -> Channel 40 (5200 MHz, VHT20)` (`mid_freq_5200_verified = True` in `iw dev phy0-ap0 info`).
  - **Hop 2 (`t = +4.0s`)**: `Channel 40 (5200 MHz, VHT20) -> Channel 36 (5180 MHz, VHT20)` (`end_freq_5180_verified = True` in `iw dev phy0-ap0 info`).
- **Arm A (Control — Blocking `block_tx=true, bcn_count=5` + Unclassified `VLAN 107`)**:
  - Setting `block_tx=true` freezes `mac80211` data queues during the 5-beacon countdown (`~512 ms` per hop), causing a burst of backlogged `AC_BE` Bulk TCP frames on channel resume that spikes `WA (.250) -> MK1-251 (198.18.0.66)` E2E `p95` RTT to **`33.394 ms`** (`p99 = 41.304 ms`, `jitter = 12.183 ms`) and depresses 3-CPE aggregate goodput to `40.957 Mbps`.
- **Arm B (Treatment — `Stage 102D` `PtMP Champion v23` Non-Blocking `block_tx=false, bcn_count=10` + `VLAN 107` `802.1Q` QoS)**:
  - Keeping `block_tx=false` with `bcn_count=10` (`~1.024s` beacon announcement window so every STA receives multiple CSA beacons even under heavy interference) + `eth0.107` `802.1Q` `0:0..7:7` + `tx_queue_len=64` + `fmx_s97a_vlan107_qos` (`DSCP EF -> WMM AC_VO`, `DSCP CS4 -> WMM AC_VI`) + `/usr/sbin/fmx_wds_churn_healer.sh` cuts `WA (.250) -> MK1-251 (198.18.0.66)` **`p95` RTT by `-72.23%` (`33.394 ms -> 9.273 ms`)**, **`p99` RTT by `-68.54%` (`41.304 ms -> 12.993 ms`)**, **E2E jitter by `-74.26%` (`12.183 ms -> 3.136 ms`)**, and **VoIP jitter by `-34.26%` (`3.015 ms -> 1.982 ms`)**, while **increasing 3-CPE aggregate goodput by `+8.85%` (`40.957 -> 44.580 Mbps`)** and retaining **`3/3` stations (`100%`)**!

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`S102D-R1`, `CONFIRMED`)

| Metric (`A1 -> B1 -> A2 -> B2` Mean Across Double CSA Hop) | Arm A (Blocking CSA + Unclassified VLAN 107) | Arm B (`Stage 102D` Champion v23 Non-Blocking CSA) | Delta (`Arm B vs Arm A`) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **3-CPE Station Retention (`5180 -> 5200 -> 5180 MHz`)** | `3/3` (`100%`) | **`3/3` (`100%`)** | `0` stations dropped | `CONFIRMED` |
| **3-CPE Aggregate Goodput (`Mbps`)** | `40.957 Mbps` | **`44.580 Mbps`** | **`+8.85%`** | `CONFIRMED` |
| **E2E `WA (.250) -> MK1-251` `p50` RTT (`ms`)** | `2.505 ms` | **`2.469 ms`** | **`-1.44%`** | `CONFIRMED` |
| **E2E `WA (.250) -> MK1-251` `p95` RTT (`ms`)** | `33.394 ms` | **`9.273 ms`** | **`-72.23%`** | `CONFIRMED` |
| **E2E `WA (.250) -> MK1-251` `p99` RTT (`ms`)** | `41.304 ms` | **`12.993 ms`** | **`-68.54%`** | `CONFIRMED` |
| **E2E `WA (.250) -> MK1-251` Jitter (`ms`)** | `12.183 ms` | **`3.136 ms`** | **`-74.26%`** | `CONFIRMED` |
| **E2E `WA (.250) -> MK1-251` Packet Loss (`%`)** | `0.00%` | **`0.00%`** | **`0.00%`** | `CONFIRMED` |
| **3-CPE Sector `p95` RTT (`ms`)** | `43.057 ms` | **`37.785 ms`** | **`-12.24%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF`) Jitter (`ms`)** | `3.015 ms` | **`1.982 ms`** | **`-34.26%`** | `CONFIRMED` |
| **Karpathy Multi-Objective Pareto Score Delta** | Baseline (`0.00%`) | **`+13.1313%`** (`PROMOTE_NEW_CHAMPION`) | **`+13.13%`** | `CONFIRMED` |

### Per-Window Breakdown (`A1 -> B1 -> A2 -> B2`)

| Phase | CSA Mode (`5180 -> 5200 -> 5180 MHz`) | 3-CPE Goodput (`Mbps`) | `WA -> MK1-251` `p50` / `p95` / `p99` (`ms`) | `WA -> MK1-251` Jitter (`ms`) / Loss | Sector `p95` RTT (`ms`) | VoIP Jitter (`ms`) | `5200 MHz` & `5180 MHz` Verified |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `bcn_count=5, block_tx=true` | `41.293` | `1.946` / `31.686` / `47.146 ms` | `12.555 ms` (`0.0%`) | `46.190 ms` | `3.634 ms` | `True` / `True` (`3/3`) |
| **`B1`** | **`bcn_count=10, block_tx=false`** | **`44.343`** | **`2.040` / `8.790` / `16.007 ms`** | **`3.426 ms` (`0.0%`)** | `48.029 ms` | **`1.400 ms`** | **`True` / `True` (`3/3`)** |
| **`A2`** | `bcn_count=5, block_tx=true` | `40.622` | `3.064` / `35.102` / `35.462 ms` | `11.810 ms` (`0.0%`) | `39.924 ms` | `2.396 ms` | `True` / `True` (`3/3`) |
| **`B2`** | **`bcn_count=10, block_tx=false`** | **`44.816`** | **`2.898` / `9.757` / `9.979 ms`** | **`2.845 ms` (`0.0%`)** | **`27.540 ms`** | **`2.564 ms`** | **`True` / `True` (`3/3`)** |
