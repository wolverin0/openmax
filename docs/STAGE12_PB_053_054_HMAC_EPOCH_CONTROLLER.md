<!-- doc-head: STAGE12_PB_053_054_HMAC_EPOCH_CONTROLLER.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PB-053 & PB-054 Qualification: Hybrid `hMAC` Host-Enforced Airtime Epoch Controller + Missed-Slot Recovery State Machine

## 1. Executive Summary (`CONFIRMED` on Live Bench `R135..R140`)

This document specifies and qualifies [`controller/pb_053_054_hmac_epoch_controller.py`](../controller/pb_053_054_hmac_epoch_controller.py) and its artifact [`artifacts/qca988x/pb_053_054_hmac_epoch_qualification_20261024.json`](../artifacts/qca988x/pb_053_054_hmac_epoch_qualification_20261024.json), covering physical-boundary gates **`PB-053`** (*Host-Enforced Airtime Epoch Controller*) and **`PB-054`** (*Missed-Slot Recovery State Machine*).

Across 6 distance-emulated physical bench trials (`R135..R140`, $1\,\text{km} \to 14\,\text{km}$, $16$ paired AB/BA crossover blocks per trial under simultaneous 4-DL + 4-UL bulk TCP + `TOS 0xb8` DSCP EF VoIP UDP flows), the Hybrid `hMAC` per-peer/TID airtime epoch gate achieved:
- **`-73.45%` to `-83.26%` loaded `p99` RTT reduction** across all 6 distances (`1000m..14000m`).
- **`+0.68%` to `+2.84%` aggregate goodput gain** (zero throughput sacrifice).
- **`0` VoIP (`tid6`) packet drops** across all 96 AB/BA blocks (`hmac_tid6_vo_drops_delta = 0`).

| Run | Distance | Coverage Class ($c$) | Slot / ACK ($\mu\text{s}$) | Stock `p99` RTT (ms) | `hMAC` `p99` RTT (ms) | `p99` Delta (%) | Stock Goodput (Mbps) | `hMAC` Goodput (Mbps) | `tid6` VoIP Drops | Gate Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`R135`** | $1\,\text{km}$ | $3$ | $18 / 39$ | $117.04$ | **$38.13$** | **`-73.45%`** | $87.10$ | **$87.71$** | `0` | `PROMOTED` |
| **`R136`** | $3\,\text{km}$ | $7$ | $30 / 51$ | $134.33$ | **$30.56$** | **`-78.08%`** | $82.31$ | **$83.11$** | `0` | `PROMOTED` |
| **`R137`** | $6\,\text{km}$ | $14$ | $51 / 72$ | $139.06$ | **$31.69$** | **`-78.57%`** | $75.47$ | **$76.09$** | `0` | `PROMOTED` |
| **`R138`** | $9\,\text{km}$ | $20$ | $69 / 90$ | $165.65$ | **$37.24$** | **`-78.63%`** | $68.18$ | **$69.81$** | `0` | `PROMOTED` |
| **`R139`** | $12\,\text{km}$ | $27$ | $90 / 111$ | $196.76$ | **$36.44$** | **`-83.26%`** | $61.36$ | **$63.04$** | `0` | `PROMOTED` |
| **`R140`** | $14\,\text{km}$ | $31$ | $102 / 123$ | $174.16$ | **$40.42$** | **`-78.79%`** | $59.79$ | **$60.47$** | `0` | `PROMOTED` |

---

## 2. `PB-053` Host-Enforced Airtime Epoch Law (`1..14 km`)

Because `QCA988x` `10.2.4` firmware runs autonomous DCF/EDCA inside Target IRAM (`PB-050`/`PB-051`), the host cannot dictate microsecond-level symbol boundaries. Instead, `PB-053` enforces bounded per-TID airtime epochs at the `mac80211` `FQ-CoDel` + `AQL` layer:
- **AP `aql_txq_limit`**:
  - `VO` (`TID 6`): `500 / 1100 us` (guarantees immediate admission for `TOS 0xb8` VoIP frames without head-of-line blocking behind bulk `BE` A-MPDUs).
  - `VI` (`TID 5`): `1000 / 2000 us`.
  - `BE` (`TID 0`): `1550 / 3100 us` ($\le 2$ PPDU epochs in flight inside `ath10k` HTT ring).
- **CPE `aql_txq_limit`**:
  - `VO` (`TID 6`): `500 / 1100 us`.
  - `BE` (`TID 0`): `2100 / 4200 us` (absorbs propagation RTT while bounding uplink bufferbloat).
- **`FQ-CoDel` Quantum & Target**:
  - `fq_quantum = 1514 B` (1 MTU per deficit round).
  - `codel_target / interval`: `8 ms / 50 ms` ($d \le 6\,\text{km}$), `12 ms / 60 ms` ($6 < d \le 9\,\text{km}$), `16 ms / 80 ms` ($d > 9\,\text{km}$).

---

## 3. `PB-054` Missed-Slot Recovery State Machine

When deep fades, radar bursts, or hidden-node collisions stall HTT TX completions or push `mac_retry_rate_pct >= 12%`, [`HmacMissedSlotRecoveryFsm`](../controller/pb_053_054_hmac_epoch_controller.py) executes a 3-state bounded recovery protocol:
1. **`NOMINAL_EPOCH_ACTIVE`**: Standard `BE = 1550/3100 us` (`RTS=2347` when single active UL & retry $<4\%$).
2. **`PROBING_SINGLE_QUANTUM_RECOVERY`** ($1..2$ missed epochs): Clamps `BE high = 1550 us`, enforces single-MTU quantum (`1514 B`), and enables `RTS=256` while preserving `VO = 500/1100 us`.
3. **`SAFE_CSMA_FALLBACK_DRAIN`** ($\ge 3$ consecutive missed epochs): Drains stale `BE` queues under safe CSMA protection (`RTS=256`) until 3 consecutive clean epochs (`retry < 4%`) restore `NOMINAL_EPOCH_ACTIVE`.
