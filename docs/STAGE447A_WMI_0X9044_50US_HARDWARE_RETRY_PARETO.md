<!-- doc-head: Stage 447A SimPy + pymoo NSGA-II Evaluation of Pillar 3 50-us Xtensa Hardware Try #2 Fallback (WMI 0x9044) -->
Quantifies the goodput and tail-latency (`p95`/`p99`) breakthrough of Pillar 3's `50 µs` Xtensa hardware Try `#2` fallback (`2x2 VHT SGI -> 1x2 CDD LGI` via `WMI 0x9044`) against standard Linux `mac80211` `8 ms` host rate-control feedback.
<!-- /doc-head -->

# Stage 447A — `SimPy` + `pymoo` `NSGA-II` Evaluation of Pillar 3 `50 µs` Xtensa Hardware Try `#2` Fallback (`WMI 0x9044`)

- **Epistemic Status**: `CONFIRMED` (`WMI_PEER_RATE_RETRY_SCHED_CMDID = 0x9044` static RE + `SimPy` & `pymoo` `NSGA-II` Pareto simulation)
- **Attribution**: `QCA firmware` (`QCA988x` MAC 4-series retry engine) vs `mac80211` (`Minstrel-HT` host PCIe TX status loop)
- **Script**: [`run_stage447a_wmi_0x9044_50us_hardware_retry_pareto.py`](../tools/sim/run_stage447a_wmi_0x9044_50us_hardware_retry_pareto.py)
- **JSON Receipt**: [`stage447a_wmi_0x9044_50us_hardware_retry_pareto.json`](../artifacts/autoresearch/stage447a_wmi_0x9044_50us_hardware_retry_pareto.json)

---

## 1. Why Host `mac80211` (`8 ms`) Fails on Transient Foliage / Polarization Fades

When wind moves wet foliage across an outdoor PtP/PtMP link, one spatial stream (`NSS=2`) or the `400 ns` Short Guard Interval (`SGI`) frequently suffers a `5–20 ms` deep fade:
1. **Standard Host `mac80211` Path (`~8,000 µs` loop)**: The `QCA988x` MAC wastes all `4–10` hardware retries in Series 0 (`2x2 VHT SGI`), then raises a PCIe HTT TX completion interrupt to the host MIPS CPU. By the time `mac80211` updates the rate table, **`~8.0 ms`** have elapsed, spiking VoIP/IPTV `p99` jitter.
2. **Pillar 3 `WMI 0x9044` Hardware Path (`50 µs` turnaround = `160x` faster)**: By pre-programming Series 1 (`Try #2`) in the `QCA988x` hardware retry descriptor table via `WMI_PEER_RATE_RETRY_SCHED_CMDID` (`0x9044`) to **`1x2 CDD VHT-NSS 1 LGI (`800 ns` CP)`**, a missing Block-ACK triggers an immediate **`50 µs`** hardware switch to single-stream Cyclic Delay Diversity with Long Guard Interval—without waking the host CPU.

---

## 2. Head-to-Head Pareto Results (`28%` Transient Polarization Fade Duty)

| Architecture / Schedule | Series 0 (`2x2 SGI`) | Series 1 (`1x2 CDD LGI`) | Goodput (`Mbps`) | `p50` (`ms`) | `p95` (`ms`) | `p99` (`ms`) | Packet Loss (`%`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Host `mac80211` (`8 ms` PCIe Feedback)** | `4` tries | `2` tries (after `8 ms`) | `167.1 Mbps` | `0.59 ms` | `11.23 ms` | `11.23 ms` | `0.0%` |
| **Pillar 3 `WMI 0x9044` (`50 µs` HW Champion)** | **`1` try** | **`3` tries (`50 µs`)** | **`440.36 Mbps` (`+163.53%`)** | **`0.59 ms`** | **`1.46 ms`** | **`1.46 ms` (`-87.0%`)** | **`0.0%`** |
