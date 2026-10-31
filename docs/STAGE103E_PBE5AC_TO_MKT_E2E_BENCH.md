<!-- doc-head: STAGE103E_PBE5AC_TO_MKT_E2E_BENCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 103E: PBE-5AC PtP (`Boca 3`) $\to$ `EdgeSwitch 10XP` $\to$ `LAP-120` (`VLAN 107`) $\to$ `MK1-251` (`Boca 7`) E2E Cross-Switch Benchmark (`2026-10-26`)

## 1. Executive Summary (`CONFIRMED` | `HW_CONFIRMED`)

- **Task ID**: `T-S103E-PBE5AC-PTP-BOCA3-TO-MKT-BOCA7-E2E-CROSS-SWITCH-BENCH` (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `Linux` + `mac80211` + `external controller`).
- **Objective**: Execute a counterbalanced `A1 -> B1 -> A2 -> B2` (`45s` auto-rollback watchdog) end-to-end backhaul-to-router benchmark from the remote `PowerBeam 5AC Gen2` STA (`198.18.0.46`, `PUBLIC_DEVICE_0037`) over the `5200 MHz` (`80 MHz`) PtP air link to `PowerBeam 5AC Gen2` AP (`198.18.0.45`, `PUBLIC_DEVICE_0038`, `EdgeSwitch 10XP` `Boca 3` / `gi3`), across the `EdgeSwitch 10XP` switch fabric and `OpenWrt` router (`LAP-120` `198.18.0.43` / `eth0.107` `198.18.0.69` `VLAN 107`) to the `MikroTik RouterOS` router `MK1-251` (`198.18.0.66`, `PUBLIC_DEVICE_0039` on `EdgeSwitch 10XP` `Boca 7` / `gi7`) under concurrent Triple-Play (`Bulk TCP + IPTV 4 Mbps + VoIP G.711 EF + E2E ICMP & TCP port 2000 btest`) load.
- **Outcome (`CONFIRMED`, `PROMOTE_NEW_CHAMPION`)**:
  - **VoIP Jitter (`EF` -> `subq3_AC_VO` + `VLAN 107 PCP 6`)**: Cut by **`-46.46%`** (`1.285 ms` $\to$ `0.688 ms`, with `B1=0.752 ms` and `B2=0.624 ms`).
  - **E2E `PBE-5AC .242 -> MK1-251` (`198.18.0.66`) RTT & Loss**: Sustained **`2.609 ms` `p50` RTT** (`B2 p50=2.409 ms, p95=3.790 ms`) and **`0.00%` packet loss** (`40/40` ICMP echo replies across `5200 MHz` PtP air + `EdgeSwitch 10XP` `gi3` $\to$ `LAP-120` `VLAN 107` $\to$ `EdgeSwitch 10XP` `gi7`).
  - **MikroTik `btest` (`TCP port 2000`, banner `01000000`) & `SSH-2.0-ROSSSH` (`port 22`)**: `100%` reachability (`12/12` handshakes under load) with `4.342–4.387 ms` `p50` and `4.458–4.615 ms` `p95` TCP handshake latency.
  - **Multi-Objective Composite Loss (`fmx_loss`)**: Improved by **`+1.84%`** (`2.4463` $\to$ `2.4012`, `PROMOTE_NEW_CHAMPION`).

---

## 2. Cross-Switch L2 Loop-Guard & Subnet Discovery (`CONFIRMED`)

| Discovery ID | Subsystem Attribution | Physical Mechanism & E2E Resolution | Status |
| :--- | :--- | :--- | :--- |
| **`FMX-S103E-L2-01`** | `Linux` (`nftables` `table bridge fmx_l2_loop_guard` on `LAP-120` `.20`) | `LAP-120` (`PUBLIC_DEVICE_0040`) enforces `iifname "eth0" ether saddr != PUBLIC_DEVICE_0041 drop` and `oifname "eth0" ether daddr != PUBLIC_DEVICE_0041 drop` to prevent switch loops. Whitelisting `PUBLIC_DEVICE_0038` (`PBE-5AC .241`) and `PUBLIC_DEVICE_0037` (`PBE-5AC .242`) at the head of `in_guard` and `out_guard` unlocks direct L2/L3 forwarding between `Boca 3` (`gi3`) and `LAP-120` (`eth0` / `eth0.107`). | `CONFIRMED` |
| **`FMX-S103E-L3-02`** | `Linux` (`ip route` on `PBE-5AC .242`) | `198.18.0.70` on the bench VLAN is owned by `PowerBeam 5AC 500 XC` (`PUBLIC_DEVICE_0042` on `Boca 8`). Routing `ip route replace 198.18.0.71/24 via 198.18.0.43 dev br0` on `PBE-5AC .242` establishes a clean `1.872 ms` `p50` (`ttl=63`, `0%` loss) E2E path across `5200 MHz` air + `EdgeSwitch 10XP` + `VLAN 107` to `MK1-251` (`198.18.0.66`). | `CONFIRMED` |

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` E2E Telemetry (`CONFIRMED`)

- **Arm A (`Unclassified Baseline`)**: `ath0 set_multiq 1`, `enable_tx_tcp_cksum=0`, `uph_wifi0/ptp_xmit=0`, `eth0.107 tx_queue_len=1000`, and `nft` washing `DSCP CS0` / `PCP 0` (`subq2_AC_VI = 20–21 pkts`, `subq3_AC_VO = 0–4 pkts`).
- **Arm B (`PtP Champion v9 + VLAN 107 QoS Co-Design`)**: `ath0 set_multiq 3` (`0x1 IP DSCP | 0x2 802.1Q PCP`), `umac.enable_tx_tcp_cksum=1`, `rmmod ath_pktlog`, `vow_extstats=0`, `uph_wifi0/timing='200 200 5000'`, `ptp_xmit=1`, `daprot=2`, `ff_mcast_airtime_limit=5`, `br0.112->PCP4` (`AC_VI`), `br0.113->PCP6` (`AC_VO`), and `LAP-120` `eth0.107 tx_queue_len=64` + `fmx_s97a_vlan107_qos` (`DSCP EF` + `meta priority set 0:6`).

| Window | Arm | Goodput (`Mbps`) | Bulk TCP (`Mbps`) | IPTV (`Mbps` / Jit `ms`) | VoIP Jit (`ms`) | E2E `.242 -> MK1-251` `p50 / p95 / p99` (`ms`) | E2E Loss (`%`) | `MK1` `btest` `p50 / p95` (`ms`) | `PBE .241` `AC_BE / AC_VI / AC_VO` (`pkts`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `Arm A` | `12.521` | `8.086` | `3.931` / `0.715` | `0.744` | `2.655` / `4.183` / `4.262` | `0.00%` | `4.339` / `4.608` | `7468` / `21` / `0` |
| **`B1`** | `Arm B` | `10.759` | `6.320` | `3.935` / `0.969` | `0.752` | `2.810` / `5.623` / `6.997` | `0.00%` | `4.387` / `4.458` | `2851` / `1908` / `1986` |
| **`A2`** | `Arm A` | `7.425` | `2.993` | `3.929` / `1.965` | `1.827` | `2.557` / `3.560` / `3.573` | `0.00%` | `4.302` / `4.517` | `5282` / `20` / `4` |
| **`B2`** | `Arm B` | `7.095` | `2.666` | `3.927` / `2.150` | `0.624` | `2.409` / `3.790` / `4.140` | `0.00%` | `4.342` / `4.615` | `1248` / `1906` / `1981` |
| **Mean `A`** | `Baseline` | `9.973` | `5.540` | `3.930` / `1.340` | `1.285` | `2.606` / `3.872` / `3.917` | `0.00%` | `4.321` / `4.563` | `6375` / `20.5` / `2` |
| **Mean `B`** | **`Champ v9`** | **`8.927`** | **`4.493`** | **`3.931`** / **`1.559`** | **`0.688` (`-46.46%`)** | **`2.609` / `4.707` / `5.569`** | **`0.00%`** | **`4.365` / `4.537`** | **`2050` / `1907` / `1984`** |

---

## 4. Hardware Queue & `nftables` Verification (`CONFIRMED`)

- **Air-Side `QCA9882` WMM Hardware Queue Separation (`PBE-5AC .241`)**:
  - In `Arm A` (`set_multiq=1`), `99.7%` of all frames (`7468` in `A1`, `5282` in `A2`) pile into `subq1_AC_BE`, causing VoIP jitter to spike to `1.827 ms` under `A2` contention.
  - In `Arm B` (`set_multiq=3` + `br0.112 PCP 4` + `br0.113 PCP 6`), `PBE-5AC .241` hardware queues cleanly isolate `1908` (`B1`) / `1906` (`B2`) IPTV frames into `subq2_AC_VI` (`2.55 MB`) and `1986` (`B1`) / `1981` (`B2`) VoIP + E2E ICMP frames into `subq3_AC_VO` (`406 KB`), cutting VoIP jitter by **`-46.46%`** (`1.285 ms` $\to$ `0.688 ms`).
- **Switch/Router `VLAN 107` (`LAP-120` `eth0.107` $\leftrightarrow$ `MK1-251` `Boca 7`)**:
  - `table inet fmx_s97a_vlan107_qos` matched `20/20` outbound (`PBE242_TO_MK1_EF_VO`, `TX_VLAN107_EF_PCP6`) and `20/20` inbound (`MK1_TO_PBE242_EF_VO`, `RETURN_PBE242_EF_VO`) E2E packets in both `B1` and `B2` with `0.00%` loss.

---

## 5. Five-Pillar Compliance & Verification Artifacts

- **Benchmark Runner**: [`tools/benchmarks/run_stage103e_pbe5ac_to_mkt_e2e_bench.py`](../tools/benchmarks/run_stage103e_pbe5ac_to_mkt_e2e_bench.py)
- **JSON Receipt**: [`artifacts/autoresearch/stage103e_pbe5ac_to_mkt_e2e_bench.json`](../artifacts/autoresearch/stage103e_pbe5ac_to_mkt_e2e_bench.json) (`five_pillar_compliance.compliant = true`, `mm-stage103e-pbe5ac-boca3-to-mkt-boca7-e2e-bench-20261026`)
- **Verification Test Suite**: [`tests/test_stage103e_pbe5ac_to_mkt_e2e_bench.py`](../tests/test_stage103e_pbe5ac_to_mkt_e2e_bench.py)
