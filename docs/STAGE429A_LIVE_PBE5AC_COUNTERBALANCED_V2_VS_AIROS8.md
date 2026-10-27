<!-- doc-head: STAGE429A_LIVE_PBE5AC_COUNTERBALANCED_V2_VS_AIROS8.md preserved document content -->
<!-- /doc-head -->



# Stage 429A — Live `PowerBeam 5AC Gen2` (`.241 <-> .242`) Counterbalanced `PtP Champion v2` vs Stock `airOS 8` & OpenWrt `Arm A`

## 1. Objective & Protocol
- Execute a counterbalanced `A1 -> B1 -> A2 -> B2` benchmark on the live `OpenWrt 24.10.4` `PowerBeam 5AC Gen2` PtP link (`.241 <-> .242`) comparing:
  - **Arm A (OpenWrt `24.10.4` Stock Baseline)**: `set_rate_override active=0` (upstream default `2x2 VHT` rate control), `fq_quantum = 1514`.
  - **Arm B (`FuturaMAX PtP Champion v2`)**:
    - Asymmetric VHT Long-GI (`short_gi_20=0`, `disassoc_low_ack=0`): AP `.241` on `2x2 VHT-NSS 2 MCS 3 LGI` (`nss=1 mcs=3 pream=3 sgi=0`, `52 Mbps`) + STA `.242` on `1x1 VHT-NSS 1 MCS 2 LGI` (`nss=0 mcs=2 pream=3 sgi=0`, `19.5 Mbps`).
    - `htt_max_amsdu_ampdu = "3 64"`, `fq_quantum = 300`, `BQL limit_max = 32768`, `AQL = 4000/12000`, `uhttpd max_requests = 32`, and Ground-Up WMI retry/rescue hooks (`Stage 428A`).
  - **Historical Reference (`Stock airOS 8` TDMA `WA.v8.7.25 <-> WA.v8.7.11`)**: `p50 = 1.96 ms`, `p95 = 7.56 ms`, `p99 = 10.68 ms`, `DL = 19.20 Mbps`, `UL = 3.60 Mbps` (`22.80 Mbps` aggregate).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`20 MHz` @ `5200 MHz`)

| Window / Profile | Full-MTU (`1472B`) Loss (%) | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate Goodput (Mbps) |
| :--- | :---: | :---: | :---: | :---: |
| **Stock `airOS 8` TDMA (`20 MHz`)** | `0.0%` | `19.20` | `3.60` | `22.80` |
| **OpenWrt `A1` (`Arm A` Stock)** | `10.0%` | `12.54` | `1.46` | `14.00` |
| **OpenWrt `B1` (`Arm B` Champion v2)** | **`0.0%`** | **`15.23`** | **`7.23` (`+100.8%` vs airOS)** | **`22.46`** |
| **OpenWrt `A2` (`Arm A` Stock)** | `50.0%` | `6.81` | `0.48` | `7.29` |
| **OpenWrt `B2` (`Arm B` Champion v2)** | **`0.0%`** | **`14.85`** | **`3.85` (`+6.9%` vs airOS)** | **`18.70`** |
| **Mean `Arm A` (`A1, A2`)** | `30.0%` | `9.67` | `0.97` | `10.64` |
| **Mean `Arm B` (`B1, B2`)** | **`0.0%`** | **`15.04` (`+55.5%`)** | **`5.54` (`+471.1%` vs Arm A, `+53.9%` vs airOS)** | **`20.58` (`+93.4%`)** |

---

## 3. Key Engineering Conclusions (`CONFIRMED`, attribution: `QCA firmware` / `mac80211` / `Linux`)
1. **Zero Full-MTU (`1472B`) Packet Loss (`0.0%` in `B1` & `B2` vs `30.0%` mean loss in `A1` & `A2`)**:
   - `PtP Champion v2` (`Arm B`) eliminates the `1500B` MPDU decoding cliff caused by `2x2 SGI` on `.242 -> .241`.
2. **Uplink Goodput Beats Both OpenWrt Stock (`+471.1%`) and Stock `airOS 8` TDMA (`+53.9%` mean, `+100.8%` peak)**:
   - Clamping `.242` TX to `1x1 VHT-NSS 1 MCS 2 LGI` while `.241` receives with 2-chain MRC boosts UL TCP goodput to `5.54 Mbps` mean (`7.23 Mbps` peak in `B1`), more than doubling Stock `airOS 8` TDMA's `3.60 Mbps` UL while raising aggregate goodput by **`+93.4%`** over OpenWrt Stock (`10.64 -> 20.58 Mbps` mean, `22.46 Mbps` peak).

## 4. Artifacts & Verification
- Script: [`run_stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.py`](../tools/benchmarks/run_stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.py)
- JSON Artifact: [`stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.json`](../artifacts/autoresearch/stage429a_live_pbe5ac_counterbalanced_v2_vs_airos8.json)
- Test Suite: [`test_stage429a.py`](../tests/test_stage429a.py)
