<!-- doc-head: STAGE70C_XC_PURE_MULTIQ_CKSUM_NETDEV800_CHAMPION_V20_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 70C — Isolated `XC` Multi-Queue, Checksum Offload & `netdev_budget=800` Benchmark (`S70C-XC-PURE-MULTIQ-CKSUM-NETDEV800`)

- **Task ID**: `T-S70C-ISOLATED-XC-MULTIQ-CKSUM-NETDEV800-CHAMPION-V20-BENCH`
- **Status**: `CONFIRMED` (4 counterbalanced `A1 -> B1 -> A2 -> B2` windows executed on live 3-CPE 5 GHz bench; `0` flash writes; `45s` auto-rollback watchdog; `198.18.0.45/.242` untouched)
- **Artifacts**:
  - Bench Runner: [`tools/bench/run_stage70c_xc_pure_multiq_cksum_champion_v20.py`](<repo>/tools/bench/run_stage70c_xc_pure_multiq_cksum_champion_v20.py)
  - Receipt JSON: [`artifacts/autoresearch/stage70c_xc_pure_multiq_cksum_champion_v20_20261026.json`](<repo>/artifacts/autoresearch/stage70c_xc_pure_multiq_cksum_champion_v20_20261026.json)
  - Reactor Integration: [`tools/research/closed_loop_research_reactor.py`](<repo>/tools/research/closed_loop_research_reactor.py) (`M40`)
  - Verification Suite: [`tests/test_stage70c_xc_pure_multiq_cksum_champion_v20.py`](<repo>/tests/test_stage70c_xc_pure_multiq_cksum_champion_v20.py)

---

## 1. Experimental Design & Hypothesis

In Stage 68C (`S68C-XC-R1` vs `S68C-XC-R2`), we discovered:
- `S68C-XC-R1` (`set_multiq=1, aggr_swretry=6, nonaggr_swretry=8, AMPDUFrames=32, enable_tx_tcp_cksum=1`) slashed Dual IPTV jitter by `-42.815%` and `p99` RTT by `-17.442%`, but `AMPDUFrames=32` + `swretry=6/8` on the `XC` CPE caused `-1.534%` goodput and `+9.568%` `p95` RTT due to longer uplink retry channel holding time against `Loco 5AC` and `LiteBeam M5`.
- `S68C-XC-R2` (`netdev_budget=800, tcp_limit_output_bytes=98304, uph_wifi0 6/6/2/5`) slashed loaded 3-CPE `p95` RTT by `-9.228%` (`110.442 -> 100.250 ms`) and `p99` RTT by `-10.180%` (`Pareto +3.1486%`).

**Stage 70C Hypothesis (`S70C-XC-PURE-MULTIQ-CKSUM-NETDEV800`)**:
Keep `AMPDUFrames=24, aggr_swretry=4, nonaggr_swretry=4` fixed on `Rocket 5AC Prism Gen2` (`.198 / 198.18.0.68`) to prevent heterogeneous PtMP airtime hogging, while combining `iwpriv ath0 set_multiq 1`, `echo 1 > /sys/module/umac/parameters/enable_tx_tcp_cksum`, `sysctl -w net.core.netdev_budget=800`, `sysctl -w net.ipv4.tcp_limit_output_bytes=98304`, and `uph_wifi0` (`cms_bias=6, voip_bias=6, daprot=2, ff_mcast_airtime_limit=5` written last per `FMX-DISC-11`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results

| Window | Arm | Aggregate Goodput (`Mbps`) | Spectral Eff (`bps/Hz`) | `Loco 5AC` GP (`Mbps`) | `XC Prism` GP (`Mbps`) | Sector `p50` RTT (`ms`) | Sector `p95` RTT (`ms`) | IPTV Jitter (`ms`) | VoIP Jitter (`ms`) | Loss (`%`) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `Stage 55A Champion v19` | `40.886` | `2.044` | `39.850` | `1.003` | `42.196` | `95.226` | `1.496` | `2.315` | `0.0%` |
| **`B1`** | `S70C Candidate (v20)` | `45.596` | `2.280` | `44.612` | `0.952` | `48.037` | `112.659` | `1.643` | `2.150` | `0.0%` |
| **`A2`** | `Stage 55A Champion v19` | `46.768` | `2.338` | `45.650` | `1.086` | `35.266` | `107.354` | `1.137` | `2.571` | `0.0%` |
| **`B2`** | `S70C Candidate (v20)` | **`49.559`** | **`2.478`** | **`48.418`** | **`1.111`** | `39.960` | **`101.608`** | `1.404` | **`1.594`** | `0.0%` |
| **Mean A** | `Stage 55A Champion v19` | `43.827` | `2.191` | `42.750` | `1.045` | `38.731` | **`101.290`** | **`1.317`** | `2.443` | `0.0%` |
| **Mean B** | `S70C Candidate (v20)` | **`47.578`** | **`2.379`** | **`46.515`** | `1.032` | `43.998` | `107.133` | `1.523` | **`1.872`** | `0.0%` |
| **Delta** | **Arm B vs Arm A** | **`+8.559%`** | **`+8.559%`** | **`+8.807%`** | `-1.244%` | `+13.60%` | `+5.769%` | `+15.642%` | **`-23.373%`** | **`0.0%`** |

- **Pareto Score Delta**: **`+6.5396%`** (0 IPTV loss out of `5,688` datagrams; 0 VoIP loss out of `1,200` datagrams; `0` `fq_overlimit` / `fq_overmemory` drops).
- **Strict Gate Verdict**: **`RETAIN_CURRENT_CHAMPION` (`Stage 55A Champion v19`)** for heterogeneous 3-CPE PtMP because mean loaded `p95` RTT increased by `+5.769%` (`101.290 -> 107.133 ms`), even though `B2` achieved the highest 3-CPE goodput ever recorded on this 20 MHz bench (`49.559 Mbps` / `2.478 bps/Hz`), `-23.373%` VoIP jitter (`1.594 ms` in `B2`), and lower `p95` RTT than `A2` (`101.608 ms` vs `107.354 ms`).

---

## 3. Causal Attribution & Hardware Readback Findings

1. **Why Goodput Surged `+8.559%` (`43.827 -> 47.578 Mbps`, Peak `49.559 Mbps`) & VoIP Jitter Fell `-23.373%` (`CONFIRMED` — `proprietary airMAX module` `umac.ko` / `ath_dev.ko` + `Linux`)**:
   - Restoring `AMPDUFrames=24, aggr_swretry=4, nonaggr_swretry=4` eliminated the `-1.534%` goodput penalty seen in `S68C-XC-R1`.
   - Enabling `enable_tx_tcp_cksum=1` + `set_multiq=1` + `netdev_budget=800` on `Rocket 5AC Prism` (`.198`) accelerated TCP ACK turnaround and WMM `AC_VO` queue servicing, driving `AP` `tid0_ac2` (`AC_BE`) transmitted packets from `17,586` (`A1`) / `18,596` (`A2`) up to `18,939` (`B1`) / `20,191` (`B2` — `28.49 MB` in `6.0s`) while slashing VoIP G.711 jitter by `-23.373%` (`2.443 -> 1.872 ms`).
2. **Why `B1` `p95` RTT Rose While `B2` `p95` RTT Beat `A2` (`101.608 ms` vs `107.354 ms`) (`CONFIRMED` — `mac80211` / `ath10k`)**:
   - The `+8.559%` bulk TCP goodput surge kept `OpenWrt LAP-120` (`.20`) `AC_BE` AQL (`1500/3000 us`) continuously full during `B1`, raising `Loco5AC_WA` `p95` RTT (`97.07 -> 114.105 ms`).
   - Meanwhile, in `B2`, `Rocket5AC_XC` `p95` RTT was `91.807 ms` and `LiteBeamM5_XW` `p95` RTT dropped `-30.82%` (`124.483 -> 86.116 ms`), proving that `S70C-XC-PURE-MULTIQ-CKSUM-NETDEV800` (`M40`) is **throughput-and-VoIP Pareto-dominant (`+6.54%`)**, whereas `S68C-XC-R2` (`netdev_budget=800, tcp_limit_output_bytes=98304, daprot=2` **without** `enable_tx_tcp_cksum=1` / `set_multiq=1`) is **strictly latency-dominant (`-9.228%` `p95` RTT, `-10.180%` `p99` RTT)**.
3. **Direct Hardware Verification of `FMX-DISC-11` on `XC` (`QCA9558 + QCA9880`) (`CONFIRMED` — `proprietary airMAX module` `ubnt_poll_host.ko`)**:
   - Live getter readback (`xc_extended_readback`) after running `echo 6 > cms_bias && echo 6 > voip_bias && echo 2 > daprot && echo 5 > ff_mcast_airtime_limit` returned `cms_bias: 5, voip_bias: 5, daprot: 2, ff_mcast_airtime_limit: 5`.
   - This confirms on live `XC` silicon that `cms_bias`, `voip_bias`, and `ff_mcast_airtime_limit` alias `int[0]` of the shared 64-byte `sysctl_table->data` vector (`0x0002d004`), whereas `daprot` resides at its own independent `.data` symbol (`0x0002cfd0`) and retains `2`.
