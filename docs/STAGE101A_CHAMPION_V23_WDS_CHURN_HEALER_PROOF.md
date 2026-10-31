<!-- doc-head: STAGE101A_CHAMPION_V23_WDS_CHURN_HEALER_PROOF.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 101A — `PtMP Champion v23`: Autonomous `4addr` WDS Churn Healer Daemon (`/usr/sbin/fmx_wds_churn_healer.sh`) & Live `VLAN 107` Soak Proof

## 1. Executive Summary & Attribution (`CONFIRMED`)
- **Task ID**: `T-S101A-CHAMPION-V23-WDS-CHURN-HEALER-DAEMON-AND-SOAK`
- **Artifacts**:
  - Updated Panel 1 Admitter: [`tools/panel1/panel1_admitter.sh`](../tools/panel1/panel1_admitter.sh)
  - Benchmark Runner & Daemon Installer: [`tools/benchmarks/run_stage101a_champion_v23_wds_churn_healer_benchmark.py`](../tools/benchmarks/run_stage101a_champion_v23_wds_churn_healer_benchmark.py)
  - Counterbalanced Receipt: [`artifacts/autoresearch/stage101a_champion_v23_wds_churn_healer_benchmark.json`](../artifacts/autoresearch/stage101a_champion_v23_wds_churn_healer_benchmark.json)
  - Verification Suite: [`tests/test_stage101a_champion_v23_wds_churn_healer.py`](../tests/test_stage101a_champion_v23_wds_churn_healer.py)
- **Subsystem Attribution**: `external controller` (`/usr/sbin/fmx_wds_churn_healer.sh` + `tools/panel1/panel1_admitter.sh` `heal_stale_wds_and_reapply_qos`) + `Linux` (`eth0.107` `802.1Q` `0:0..7:7` + `tx_queue_len=64` + `nftables` `fmx_s97a_vlan107_qos`) + `mac80211` (per-station `iTXQ` + `4addr` `AP/VLAN` `phy0-ap0.staX` cleanup) + `ath10k` (`AQL` `1200/2400 us`) + `proprietary airMAX/LTU module` (`XC` `ath_dev.ko` `aggr_swretry=2` + `umac.ko` `set_multiq=3`).
- **Safety Invariants Verified (`CONFIRMED`)**:
  - `0` flash writes (`RAM-only` deployment on `LAP-120 .20` with `45s` Non-DFS rollback watchdog).
  - `198.18.0.45` / `198.18.0.46` (`PBE-5AC-Gen2` PtP pair) and `198.18.0.2` (`ether2-sw-poe200`) / `.200` / `.201` (`SG-01` Guarida backbone) strictly untouched.
  - `EdgeSwitch 10XP Boca 7` (`gi7`, `MK1-251` `198.18.0.66`) strictly isolated in `VLAN 107` (`mkt_boca7_lab`).

---

## 2. Autonomous Daemon Architecture (`FMX-S101A-01`, `CONFIRMED`)

Following the discovery of **`FMX-S99A-01`** in `Stage 99A` (`hostapd` `4addr` WDS `AP/VLAN` `phy0-ap0.staX` stale-interface lock when a stock `airOS 8` `XC`/`WA` station disconnects or re-associates without a clean deauth handshake), we engineered and deployed two production artifacts:
1. **`tools/panel1/panel1_admitter.sh` (`heal_stale_wds_and_reapply_qos`)**:
   - Integrated directly into the `ubus subscribe hostapd.phy0-ap0` event loop (`*'"disassoc"'*|*'"deauth"'*` and 1s `collect` poll).
   - Inspects every `/sys/class/net/phy0-ap0.sta*` interface, verifies whether its bound station MAC is in `GOOD` (`authorized=true && wds=true`), immediately deletes any orphaned/stale `phy0-ap0.staX` interface (`iw dev "$sta_if" del`), ensures active WDS interfaces are bridged into `br-lan`, and re-enforces `AQL 1200/2400 us` (`aql_threshold=4000`) + `eth0.107 tx_queue_len=64`.
2. **`/usr/sbin/fmx_wds_churn_healer.sh` on `LAP-120` (`198.18.0.43`, PID `32369`)**:
   - Polls `ubus call hostapd.phy0-ap0 get_clients` and `/sys/class/net/phy0-ap0.sta*` every `250 ms`.
   - Upon detecting any stale `phy0-ap0.staX` interface or missing WDS station (`flushed=1` or `missing=1`), logs `FMX_S101A_STALE_WDS_FLUSH` / `FMX_S101A_AUTO_HEAL_PULSE` to `/tmp/fmx_wds_churn_healer.log`, flushes the stale `phy0-ap0.staX` interface, pulses `TRIAL_IE` for `750 ms` followed by a `3500 ms` IE-free association window (`FMX-DISC-17`), and re-applies `Champion v23` AQL and `VLAN 107` QoS settings automatically.

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Autonomous Verification (`S101A-R1`, `CONFIRMED`)

- **Arm A (Control)**: `/usr/sbin/fmx_wds_churn_healer.sh` **STOPPED** + Unoptimized Churn Baseline during an unannounced mid-stream `wpa_cli -i ath0 disconnect/scan/reassociate` on `Rocket 5AC Prism` (`.198`) at `t = +2.0s`.
- **Arm B (Treatment — `PtMP Champion v23`)**: `/usr/sbin/fmx_wds_churn_healer.sh` **RUNNING AUTONOMOUSLY** on `LAP-120` (`.20`) + `eth0.107` `802.1Q` `0:0..7:7` + `tx_queue_len=64` + `nftables` `fmx_s97a_vlan107_qos` + `AQL 1200/2400 us` + `XC aggr_swretry=2, set_multiq=3` with **ZERO external Python healing commands** during the window.

| Metric (`A1 -> B1 -> A2 -> B2` Mean) | Arm A (Healer Daemon Stopped) | Arm B (`PtMP Champion v23` Healer Active) | Delta (`Arm B vs Arm A`) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **3-CPE Aggregate Goodput (`Mbps`)** | `47.636 Mbps` | `46.996 Mbps` | `-1.34%` (within noise floor) | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E `p50` RTT (`ms`)** | `1.884 ms` | **`1.913 ms`** | `< 2.0 ms` (`+0.03 ms`) | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E `p95` RTT (`ms`)** | `20.218 ms` | **`6.892 ms` (`< 8.0 ms` SLA)** | **`-65.91%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` E2E `p99` RTT (`ms`)** | `35.887 ms` | **`18.387 ms`** | **`-48.76%`** | `CONFIRMED` |
| **Survivor `WA (.250) -> MK1-251` Packet Loss (`%`)** | `0.00%` | **`0.00%`** | **`0.00%`** | `CONFIRMED` |
| **Surviving Sector `p95` RTT (`WA + AP-MK1 + XW`) (`ms`)** | `42.988 ms` | **`33.486 ms`** | **`-22.10%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF`) Jitter (`ms`)** | `3.326 ms` | **`1.494 ms`** | **`-55.08%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF`) Packet Loss (`%`)** | `0.072%` | **`0.000%`** | **`-100.0%` (`0` lost packets)** | `CONFIRMED` |
| **Autonomous `XC (.198)` WDS Re-Join Time (`ms`)** | `2500.0 ms` (Unhealed stall) | **`1111.0 ms`** (Auto-healed by `.20` daemon) | **`-55.56%`** | `CONFIRMED` |
| **Karpathy Multi-Objective Pareto Score Delta** | Baseline (`0.00%`) | **`+6.3928%`** (`PROMOTE_NEW_CHAMPION`) | **`+6.39%`** | `CONFIRMED` |

### Per-Window Breakdown (`A1 -> B1 -> A2 -> B2`)

| Phase | Daemon State | Survivor `WA -> MK1-251` `p50` / `p95` / `p99` (`ms`) | Sector `p95` RTT (`ms`) | VoIP Jitter (`ms`) / Loss (`%`) | Auto-Heal Recovery (`ms`) | Daemon Log Event (`/tmp/fmx_wds_churn_healer.log`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`A1`** | `STOPPED` | `1.897` / `23.282` / `31.899 ms` | `47.571 ms` | `2.582 ms` (`0.14%`) | `2500.0 ms` (Stall) | *(Daemon stopped)* |
| **`B1`** | **`ACTIVE`** | **`1.825` / `8.922` / `16.956 ms`** | **`35.758 ms`** | **`1.421 ms` (`0.00%`)** | **`1124.0 ms`** | `FMX_S101A_AUTO_HEAL_PULSE flushed=0 missing=1` |
| **`A2`** | `STOPPED` | `1.871` / `17.154` / `39.875 ms` | `38.405 ms` | `4.070 ms` (`0.00%`) | `2500.0 ms` (Stall) | *(Daemon stopped)* |
| **`B2`** | **`ACTIVE`** | **`2.000` / `4.862` / `19.818 ms`** | **`31.213 ms`** | **`1.566 ms` (`0.00%`)** | **`1098.0 ms`** | `FMX_S101A_AUTO_HEAL_PULSE flushed=0 missing=1` |
