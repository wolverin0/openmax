<!-- doc-head: STAGE123A_LIVE_WA_QCA9882_DEEP_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 123A — Live WA-Family (`QCA9882` + `AR9342`) Deep Counterbalanced Autoresearch Sweep (`.20` $\leftrightarrow$ `.250`)

- **Task ID**: `T-S123A-LIVE-WA-QCA9882-DEEP-AUTORESEARCH-SWEEP-ON-BENCH-20-250`
- **Status**: `CONFIRMED`
- **Attribution**: `Linux + mac80211 + ath10k + hardware`
- **Artifact**: [`artifacts/autoresearch/stage123a_live_wa_qca9882_deep_autoresearch.json`](../artifacts/autoresearch/stage123a_live_wa_qca9882_deep_autoresearch.json)
- **Runner**: [`tools/benchmarks/run_stage123a_live_wa_qca9882_deep_autoresearch.py`](../tools/benchmarks/run_stage123a_live_wa_qca9882_deep_autoresearch.py)
- **Test Suite**: [`tests/test_stage123a_live_wa_qca9882_deep_autoresearch.py`](../tests/test_stage123a_live_wa_qca9882_deep_autoresearch.py)

---

## 1. Bench Topology & Strict Safety Boundaries (`CONFIRMED`)

- **AP Node**: `198.18.0.43` / `198.18.0.81` (`Ubiquiti LiteAP AC LAP-120`, `OpenWrt 24.10.4 r28959-29397011cc`, `Linux 6.6.110`, `AR9342` MIPS `74Kc` + `QCA9882` `ath10k_pci`).
- **CPE Node**: `198.18.0.47` / `198.18.0.67` (`Ubiquiti NanoStation 5AC Loco`, `OpenWrt 24.10.4 r28959-29397011cc`, `Linux 6.6.110`, `AR9342` MIPS `74Kc` + `QCA9882` `ath10k_pci`, MAC `PUBLIC_DEVICE_0049`).
- **RF Channel**: `5180 MHz` (`VHT20`, Non-DFS, `45s` rollback watchdog).
- **Safety Boundaries**: `0` flash writes (100% volatile `/sys/kernel/debug/ieee80211/phy0/*`, `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/*`, and `sysctl`), `0` packets sent to `198.18.0.45`/`.242` or Guarida production (`198.18.0.2`/`.200`/`.201`/`.84`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`12` Live Triple-Play Windows)

Each window ran bidirectional bulk TCP (`iperf3 --bidir -P 2`), IPTV UDP (`2 x 2.5 Mbps`, `1316B`, `DSCP CS4 0x80`), VoIP UDP (`128 kbps`, `160B`, `DSCP EF 0xb8`), continuous BusyBox ICMP RTT probes (`p50`/`p95`/`p99`), and `/proc/stat` CPU/softirq delta profiling.

| Round ID | Arm A vs Arm B Knob Matrix | Arm A Goodput (`Mbps`) | Arm B Goodput (`Mbps`) | Arm A RTT `p50` / `p95` / `p99` (`ms`) | Arm B RTT `p50` / `p95` / `p99` (`ms`) | Arm A / Arm B VoIP Jitter (`ms`) | Arm A / Arm B AP `softirq` (`%`) | Pareto $\Delta$ (`%`) | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S123A-R1`** | **Arm A**: `AQL BE=2000/4000`, `thr=5000`, `fq_quantum=4542`, `BQL=3028/65536/1000`, `tx_bias=1`, `budget=300`, `tcp_limit=131072`<br>**Arm B**: `99-fmx-wa-universal-champion` (`AQL BE=1500/3000`, `thr=5000`, `fq_quantum=1514`, `BQL=4542/42392/800`, `tx_bias=2`, `budget=600`, `tcp_limit=98304`) | `55.727` | **`55.931`** (`+0.37%`) | `27.464` / `59.574` / `59.880` | `30.026` / **`59.243`** / **`59.243`** | `2.541` / **`1.869`** (`-26.4%`) | `32.55%` / **`30.40%`** (`-2.15%`) | **`+5.71%`** | **`PROMOTE_ARM_B`** |
| **`S123A-R2`** | **Arm A**: Symmetric `fq_quantum=1514` (`1xMTU`) on AP & CPE (`AQL BE=1500/3000`, `thr=5000`, `BQL=4542/42392/800`)<br>**Arm B**: Asymmetric **AP `fq_quantum=3028` (`2xMTU`) / CPE `fq_quantum=1514` (`1xMTU`)** (`AQL BE=1500/3000`, `thr=5000`, `BQL=4542/42392/800`) | `57.675` | **`57.907`** (`+0.40%`) | `34.199` / `85.303` / `85.303` | **`24.300`** (`-28.95%`) / **`71.422`** (`-16.27%`) / **`71.422`** (`-16.27%`) | `1.997` / **`1.804`** (`-9.66%`) | `29.28%` / **`27.17%`** (`-2.11%`) | **`+13.35%`** | **`PROMOTE_ARM_B`** |
| **`S123A-R3`** | **Arm A**: `AQL BE=1500/3000`, `thr=5000`, `tcp_limit=98304` (AP `fq=3028` / CPE `fq=1514`)<br>**Arm B**: Tight `AQL BE=1200/2400`, `thr=4000`, `tcp_limit=65536` (AP `fq=3028` / CPE `fq=1514`) | **`55.002`** | `54.068` (`-1.70%`) | `25.095` / **`65.046`** / **`65.046`** | **`20.808`** (`-17.08%`) / `73.389` (`+12.83%`) / `73.389` | `1.628` / **`1.570`** (`-3.56%`) | **`28.18%`** / `34.68%` (`+6.50%`) | `-8.29%` | **`RETAIN_ARM_A`** |

---

## 3. Physical & Kernel Mechanisms (`CONFIRMED`)

1. **`FMX-S123A-01` (`99-fmx-wa-universal-champion` vs Relaxed AQL/FQ/BQL)**:
   - Tightening `aql_txq_limit BE` from `2000/4000 us` to `1500/3000 us` alongside `eth0` BQL `4542/42392/800`, `dev_weight_tx_bias=2`, `netdev_budget=600`, and `tcp_limit_output_bytes=98304` (`S123A-R1` Arm B) improves goodput (`55.931` vs `55.727 Mbps`), cuts VoIP jitter by **`-26.45%`** (`1.869` vs `2.541 ms`), lowers `p99` RTT (`59.243` vs `59.880 ms`), and reduces AP `NET_RX`/`NET_TX` `softirq` CPU load by **`-2.15%`** (`30.40%` vs `32.55%`, Pareto **`+5.71%`**).
2. **`FMX-S123A-02` (Asymmetric AP `fq_quantum=3028` / CPE `fq_quantum=1514` Discovery on `AR9342` + `QCA9882`)**:
   - In `S123A-R2`, setting `fq_quantum=3028` (`2xMTU`) on the `LAP-120` AP while keeping `fq_quantum=1514` (`1xMTU`) on the `NanoStation 5AC Loco` CPE amortizes per-dequeue `fq_tin_dequeue` spinlock overhead on the CPU-bound AP (`AR9342` at `~96%` busy) while preserving `1xMTU` uplink fairness on the CPE (`~76%` busy).
   - Result: Under-load `p50` RTT drops **`-28.95%`** (`34.199 -> 24.300 ms`), `p95`/`p99` RTT drops **`-16.27%`** (`85.303 -> 71.422 ms`), VoIP jitter drops **`-9.66%`** (`1.997 -> 1.804 ms`), AP `softirq` drops **`-2.11%`** (`29.28% -> 27.17%`), AP idle headroom increases (`3.70% -> 4.25%`), and goodput reaches **`57.907 Mbps`** (`59.537 Mbps` peak in `B2`, Pareto **`+13.35%`**).
3. **`FMX-S123A-03` (Sub-`1500 us` AQL Boundary on Single-Core MIPS `AR9342`)**:
   - In `S123A-R3`, tightening `AQL BE` further to `1200/2400 us` (`aql_threshold=4000`, `tcp_limit=65536`) achieves the lowest median under-load RTT (**`p50=20.808 ms`**, `-17.08%`, `18.299 ms` in `B2`), but increases `ath10k_htt_txrx_compl_task` wakeup frequency on `AR9342` (`softirq` `28.18% -> 34.68%`, `+6.50%`), trimming goodput by `-1.70%` (`55.002 -> 54.068 Mbps`) and raising `p95` tail latency (`65.046 -> 73.389 ms`). Thus `AQL BE=1500/3000` (`thr=5000`, AP `fq_quantum=3028`, CPE `fq_quantum=1514`) is retained as the Pareto-optimal `WA` profile (`0.7108` / `0.6934`).
