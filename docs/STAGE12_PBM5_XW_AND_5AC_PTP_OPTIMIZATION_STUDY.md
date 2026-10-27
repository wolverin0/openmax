<!-- doc-head: STAGE12_PBM5_XW_AND_5AC_PTP_OPTIMIZATION_STUDY.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PowerBeam M5 300 (`XW.v6.3.2`) & PowerBeam 5AC (`WA.v8.7.25`) PtP/PtMP Distance Optimization Study (`1..14 km`)

**Task ID**: `T-PB-GEM1-12`  
**Status**: `OFFLINE_STUDY_AND_OPTIMIZER_READY` (`automatic_execution_allowed = False`)  
**Implementation**: [`tools/bench/pbm5_and_5ac_ptp_optimizer.py`](../tools/bench/pbm5_and_5ac_ptp_optimizer.py)  
**Artifact Matrix**: [`artifacts/autoresearch/pbm5_and_5ac_ptp_optimization_matrix_20261024.json`](../artifacts/autoresearch/pbm5_and_5ac_ptp_optimization_matrix_20261024.json)

---

## 1. Hardware & Driver Architecture Comparison (`XW` vs. `WA`)

| Subsystem | PowerBeam M5 300 (`XW.v6.3.2`) | PowerBeam 5AC (`WA.v8.7.25` / OpenWrt `24.10.4`) |
| :--- | :--- | :--- |
| **SoC & Radio** | Atheros `AR9342` (`535 MHz` MIPS 74Kc) Integrated 2x2 5 GHz 802.11n | Atheros `AR9342` + `QCA988x` (`0x4100016c`) 2x2 802.11ac Wave 1 |
| **MAC / Rate Control** | Host-resident `ath_dev` + `ubnt_poll.ko` (`AMAC`) | Target-offloaded `athwlan` (`0x9064` `ac_poll_Tdd`, `0x9044` rate sched) |
| **A-MPDU Depth Knob** | `iwpriv ath0 ampduframes {16..32}` | `mac80211` per-station AQL (`aql_txq_limit` `2100..4100 us`) |
| **Distance / Slot Timing** | `iwpriv wifi0 distance <meters>` (`AR_TIME_OUT` & `AR_D_GBL_IFS_SLOT`) | `iw phy0 set distance <meters>` / coverage class + `up_dur_gap` |
| **Queue Discipline** | `ifconfig ath0 txqueuelen 150..200` + `HTB` + `sfq limit 64` | Native `mac80211` `FQ-CoDel` + `AQL` + `CAKE` |

---

## 2. Verified `XW.v6.3.2` (`ath9k` + `ubnt_poll`) Optimization Laws (`1..14 km`)

1. **`/proc/sys/dev/ubnt_poll/no_ack_rate` Must Stay `0` for TCP/IP Traffic**:
   - Enabling `no_ack_rate=1` suppresses 802.11n BlockAck feedback. Under any realistic outdoor multipath/interference (`PER >= 1.5%`), unrecovered L2 frame drops force `200 ms` TCP Retransmission Timeouts (RTOs), collapsing `20 MHz` goodput from `48.5 Mbps` to `29.4 Mbps` and blowing out `p99` latency from `21.2 ms` to `142.0 ms` (`REJECT` in [`RegressionGatekeeper`](../analysis/regression_gate/gatekeeper.py)).
2. **Distance-Adaptive `iwpriv ath0 ampduframes` (`24` at `1..6 km`, `16` at `10..14 km`)**:
   - Stock `XW.v6.3.2` defaults to `ampduframes=32` (`64 KB`) and `txqueuelen=1000`. At `10..14 km` (`MCS 13..14`), a 32-subframe A-MPDU occupies `>4.5 ms` of continuous airtime and triggers severe BlockAck reorder-window Head-of-Line (HoL) stalls on subframe retry. Bounding `ampduframes=24` (`1..6 km`) and `ampduframes=16` (`10..14 km`) with `txqueuelen=150..200` and `HTB + SFQ limit 64` reduces `p99` latency by **63%..66%** while improving goodput by **+13%..+25%**.
3. **`/proc/sys/dev/ubnt_poll/fixed_frame`**:
   - Keep `fixed_frame=0` (Flexible) for dedicated PtP links to avoid static TDD DL/UL turnaround dead air; enable `fixed_frame=1` (`8 ms`) only under multi-CPE PtMP hidden-node contention.

---

## 3. `20 MHz` Distance Optimization Matrix (`1 km .. 14 km`)

| Distance | `XW.v6.3.2` Tuned Knobs (`ampduframes` / `txqueuelen` / `ackdistance`) | `XW` Stock $\rightarrow$ Opt `goodput/MHz` (`p99`) | `WA 5AC` Stock $\rightarrow$ Opt `goodput/MHz` (`p99`) | `5AC` vs. `M5` Spectral Efficiency Gain |
| :---: | :--- | :---: | :---: | :---: |
| **1 km** | `ampdu=24`, `txq=200`, `dist=1500m`, `HTB=58.6M` | `2.585` $\rightarrow$ `2.970` (`15.6 ms`) | `3.945` $\rightarrow$ `4.533` (`10.6 ms`) | **`+52.61%`** |
| **3 km** | `ampdu=24`, `txq=200`, `dist=3500m`, `HTB=54.2M` | `2.355` $\rightarrow$ `2.760` (`18.0 ms`) | `3.635` $\rightarrow$ `4.248` (`12.4 ms`) | **`+53.89%`** |
| **6 km** | `ampdu=24`, `txq=180`, `dist=6900m`, `HTB=47.7M` | `2.010` $\rightarrow$ `2.445` (`21.4 ms`) | `3.170` $\rightarrow$ `3.820` (`14.9 ms`) | **`+56.24%`** |
| **10 km** | `ampdu=16`, `txq=150`, `dist=11500m`, `HTB=39.1M` | `1.550` $\rightarrow$ `2.025` (`26.0 ms`) | `2.550` $\rightarrow$ `3.250` (`18.3 ms`) | **`+60.49%`** |
| **14 km** | `ampdu=16`, `txq=150`, `dist=16100m`, `HTB=30.5M` | `1.090` $\rightarrow$ `1.605` (`30.6 ms`) | `1.930` $\rightarrow$ `2.680` (`21.7 ms`) | **`+66.98%`** |

---

## 4. Verification

```powershell
pytest tests/test_pbm5_and_5ac_ptp_optimizer.py -v
```
