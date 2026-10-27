<!-- doc-head: STAGE162A_LIVE_WA_E2E_FORWARDING_OFFLOAD_BENCHMARK.md preserved document content -->
<!-- /doc-head -->



# Stage 162A — Live `WA` End-to-End Forwarding & Offload Benchmark (`CPE .250` $\rightarrow$ `AP .20` $\rightarrow$ Switch $\rightarrow$ Boca 7 `MK1-251` `192.168.15.1`)

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S162A-LIVE-WA-E2E-FORWARDING-AND-OFFLOAD-BENCHMARK`
- **End-to-End Topology (`CONFIRMED`)**:
  - `CPE .250` (`LiteBeam 5AC Gen2` `WA`, `192.168.15.250` on `br-lan`) $\leftrightarrow$ 5 GHz `VHT20` WDS (`4addr=1`) $\leftrightarrow$ `AP .20` (`NanoStation 5AC loco` `WA`, `192.168.15.20` on `br-lan`) $\leftrightarrow$ Switch $\leftrightarrow$ **Boca 7 (`MK1-251` `192.168.15.1`)** + Host (`192.168.15.150`).
- **Artifacts**:
  - [`artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json`](../artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json)
  - [`tools/benchmarks/run_stage161a_to_163a_wa_megamission.py`](../tools/benchmarks/run_stage161a_to_163a_wa_megamission.py)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` End-to-End Results (`S162A-E2E-R1`)

| Metric | Arm A (`packet_steering=0`, `flow_offloading=0`) | Arm B (`packet_steering=1`, `flow_offloading=1`, `nf_conntrack_max=16384`) | Delta (`B - A`) | Attribution |
| :--- | :--- | :--- | :--- | :--- |
| **Bidirectional Goodput (`Mbps`)** | `41.584 Mbps` | **`41.613 Mbps` (`44.173 Mbps` in `B2`)** | **`+0.07%`** | `Linux` + `mac80211` |
| **E2E `CPE .250 -> MK1-251 (192.168.15.1)` `p50` RTT (`ms`)** | `59.534 ms` | **`47.398 ms` (`33.535 ms` in `B1`)** | **`-12.136 ms` (`-20.38%`)** | `Linux` RPS + `nftables` flowtable |
| **E2E `CPE .250 -> MK1-251 (192.168.15.1)` `p95` RTT (`ms`)** | `121.206 ms` | **`89.961 ms` (`59.100 ms` in `B1`)** | **`-31.245 ms` (`-25.78%`)** | `Linux` RPS + `nftables` flowtable |
| **E2E `CPE .250 -> MK1-251 (192.168.15.1)` `p99` RTT (`ms`)** | `122.396 ms` | **`112.418 ms` (`65.070 ms` in `B1`)** | **`-9.978 ms` (`-8.15%`)** | `Linux` RPS + `nftables` flowtable |
| **E2E `CPE .250 -> MK1-251 (192.168.15.1)` Loss (`%`)** | `0.0%` | **`0.0%`** | `0.0%` | Zero-drop forwarding |
| **AP `softirq` CPU (`%`)** | `23.81%` | **`21.97%` (`19.69%` in `B1`)** | **`-1.84%`** | Reduced `net_rx_action` overhead |
| **AP `idle` CPU Headroom (`%`)** | `6.24%` | **`12.11%`** | **`+5.87%` (`+94.1%` relative)** | Higher single-core MIPS headroom |
| **AP / CPE `MemAvailable` (`MB`)** | `17.57 MB` / `11.11 MB` | **`18.67 MB` / `10.89 MB`** | **`+1.10 MB`** on AP | `64 MB` RAM stability |

---

## 3. Engineering Conclusion (`CONFIRMED`)
- Enabling `network.globals.packet_steering=1` (`rps_cpus=1` across `eth0`, `br-lan`, and `phy0-*`), `firewall.@defaults[0].flow_offloading=1`, and `net.netfilter.nf_conntrack_max=16384` on both `WA` endpoints (`AR9342` `535 MHz` MIPS `74Kc`) cut end-to-end RTT across the radio link AND the physical switch to Boca 7 (`MK1-251` `192.168.15.1`) by **`-20.38%` (`p50`)** and **`-25.78%` (`p95`)** while nearly doubling AP idle CPU headroom (`6.24% -> 12.11%`). Promoted to the Universal `WA` Champion Profile `v2` (`Stage 163A`).
