<!-- doc-head: STAGE163A_CUMULATIVE_18ROUND_WA_CHAMPION_V2.md preserved document content -->
<!-- /doc-head -->



# Stage 163A — Cumulative `18`-Round (`76` Live Windows) `WA` Universal Champion Profile (`v2`) Consolidation

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `T-S163A-CUMULATIVE-18ROUND-WA-UNIVERSAL-CHAMPION-V2-CONSOLIDATION`
- **Scope**: Consolidates `18` live RF rounds (`72` counterbalanced windows across `R1..R18`) plus `4` live End-to-End (`CPE .250 -> AP .20 -> Switch -> Boca 7 MK1-251 192.168.15.1`) counterbalanced windows (`76` total live windows) on Ubiquiti `airMAX AC` `WA` (`QCA9882` + `AR9342` `535 MHz` MIPS `74Kc`, `64 MB` RAM).
- **Artifacts & Universal Init Script**:
  - [`artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json`](../artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json)
  - [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)
  - [`tests/test_stage161a_to_163a_wa_autoresearch.py`](../tests/test_stage161a_to_163a_wa_autoresearch.py)

---

## 2. Cumulative `18`-Round + `E2E-R1` Ledger (`76` Live Windows, `CONFIRMED`)

| Stage | Rounds | Key Promoted / Retained Knobs | Verified Live Outcome (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **`Stage 123A`** | `R1..R3` (`12` win) | `AP BE 1500/3000 + fq_quantum 3028`, `STA BE 1500/3000 + fq_quantum 1514`, `dev_weight_tx_bias=2`, `tcp_notsent_lowat=8192`, `bql=4542..36288` | Goodput `36.31 -> 44.33 Mbps` (`+22.1%`), `p50` RTT `56.60 -> 45.77 ms` (`-19.1%`), `p95` RTT `-37.9%`. |
| **`Stage 135A`** | `R4..R6` (`12` win) | `VO=300/600, VI=1000/2000`, `aql_threshold=4000`, `bql_hold_time=600`, `eth_fq_quantum=1514`, `tx_queue_len=256`, `beacon_int=30`, `rts=off` | `p95` RTT `122.40 -> 92.81 ms` (`-24.2%`), `p99` RTT `140.42 -> 109.76 ms` (`-21.8%`), `0%` loss. |
| **`Stage 139A`** | `R7..R9` (`12` win) | `fq_limit=1024`, `fq_memory_limit=3MB`, `dev_weight=48`, `netdev_budget=480/6000us`, `eth_fq_interval=100ms` | Goodput **`50.94 Mbps`** (`+6.38%`), `p50` RTT **`37.81 ms`** (`-17.07%`), `p95` RTT **`70.39 ms`** (`-26.62%`). |
| **`Stage 140A`** | `R10..R12` (`12` win) | `tcp_limit_output_bytes=65536`, `coverage_class=0`, `VHT20` (`5180 MHz`) vs `VHT40` (`+21.4%` better `VHT20` efficiency on `AR9342`) | Goodput `44.84 -> 47.08 Mbps` (`+5.01%`), `p50` RTT `46.50 -> 42.34 ms` (`-8.95%`). |
| **`Stage 145A`** | `R13..R15` (`12` win) | `fq_codel` (`quantum 1514 ecn`) beats `cake diffserv4` by `+4.98 Mbps` (`+12.2%`) & `-6.2%` `softirq`; `vm.min_free_kbytes=4096` + `oom_score_adj=-900` | Eliminated `kswapd0` atomic page allocation stalls under 8-flow TCP stress (`MemAvailable` `15.45 MB`). |
| **`Stage 161A`** | `R16..R18` (`12` win) | `distance_m=300`, `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `fq_initial_quantum=3028`, `txpower=2000 mBm` (`20 dBm`) + sync `switch_chan` | `R16` goodput **`48.75 Mbps`** (`+13.68%`, `52.85 Mbps` in `B1`), `p95` `-15.88%`; `R17` 8-flow goodput **`38.06 Mbps` (`43.11 Mbps` in `B2`)**. |
| **`Stage 162A`** | `E2E-R1` (`4` win) | `packet_steering=1` (`rps_cpus=1`), `flow_offloading=1`, `nf_conntrack_max=16384` | E2E `CPE .250 -> MK1-251 (.15.1)` `p50` RTT **`-20.38%`** (`59.53 -> 47.40 ms`), `p95` RTT **`-25.78%`** (`121.21 -> 89.96 ms`), AP `softirq` **`21.97%`**. |

---

## 3. Universal `WA` Champion Profile `v2` Parameters (`99-fmx-wa-universal-champion`)
- **802.11ac / `mac80211` / `ath10k`**: `htmode=VHT20`, `coverage_class=0`, `distance_m=300`, `rts=off`, `beacon_int=30`, `aql_threshold=4000`, `VO=300/600`, `VI=1000/2000`, `BE=1500/3000`, `BK=500/1000`, `AP fq_quantum=3028`, `STA fq_quantum=1514`, `fq_limit=1024`, `fq_memory_limit=3145728`.
- **Ethernet BQL & Qdisc**: `eth0 BQL=4542..36288` (`hold_time=600`), `tx_queue_len=256`, `eth0/br-lan fq_codel quantum 1514 target 5ms interval 100ms limit 1024 memory_limit 3145728 ecn`.
- **NAPI, Forwarding & Offload**: `dev_weight=48`, `dev_weight_tx_bias=2`, `netdev_budget=480`, `netdev_budget_usecs=6000`, `netdev_max_backlog=1500`, `packet_steering=1` (`rps_cpus=1`), `flow_offloading=1`, `nf_conntrack_max=16384`.
- **TCP Pacing & `64 MB` VM Guard**: `tcp_notsent_lowat=8192`, `tcp_limit_output_bytes=65536`, `tcp_pacing_ca_ratio=110`, `tcp_pacing_ss_ratio=150`, `fq_initial_quantum=3028`, `vm.min_free_kbytes=4096`, `oom_score_adj=-900`.
