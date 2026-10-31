<!-- doc-head: STAGE407A_CUMULATIVE_49ROUND_200WINDOW_WA_CHAMPION_V8.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 407A — Cumulative `49`-Round (**`200`-Window**) Universal `WA` Champion `v8` Master Synthesis

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 407A` (verified by `Stage 408A` regression test suite `tests/test_stage403a_to_408a_wa_200window_champion.py`).
- **Cumulative Evidence Base**: **`49` counterbalanced `A1 -> B1 -> A2 -> B2` RF autoresearch rounds (`196` RF windows + `4` Stage 162A E2E windows = `200` live hardware windows; `212` including `E2E-R2..R4`)** on `OpenWrt 24.10.4` `WA` (`AR9342` + `QCA9882` `ath10k-ct`) + live production deployment on `Panel1-Guarida` (`198.18.0.7`).
- **Primary Artifact**: [`artifacts/autoresearch/stage407a_cumulative_49round_200window_wa_champion_v8.json`](<repo>/artifacts/autoresearch/stage407a_cumulative_49round_200window_wa_champion_v8.json)

## 2. Cumulative Campaign Progression (`R1..R49` = `200` Windows)

| Campaign Phase | Rounds (`Windows`) | Promoted Architectural Breakthroughs | Key Quantitative Gain (`CONFIRMED`) |
| :--- | :---: | :--- | :--- |
| **`Stages 83C..213A`** | `R1..R18` (`72` win) | `aql_txq_limit`, `htt_max_amsdu_ampdu`, `ani_enable=1`, `eth0` `fq_codel`, `bql`, `rps_cpus` | `77.31 Mbps` (`VHT40`), `-48.03%` `p99` RTT |
| **`Stages 212A..279A`** | `R19..R30` (`124` win) | `netdev_budget=600`, `tcp_notsent_lowat=8192`, `aql_threshold=4000`, `min_free_kbytes=4096` | `-56.10%` E2E `p50` RTT (`10.197 ms`) |
| **`Stages 311A..315A`** | `R31..R36` (`148` win) | `gro_normal_batch=16`, `fq_limit=512`, `tcp_early_retrans=4`, `multicast_to_unicast=1` | `74.26 Mbps` (`R33 B1`), `-54.61%` E2E `p95` |
| **`Stages 381A..385A`** | `R37..R42` (`172` win) | `htt_max_amsdu_ampdu='2 64'`, `rts off`, `tcp_autocorking=0`, `1 Hz` `fw_stats`, `1x1` rescue | `79.51 Mbps` (`R38 A1`), `-89.85%` E2E `p50` (`8.987 ms`) |
| **`Stages 403A..407A`** | **`R43..R49` (`200` win)** | **`PB040-CANARY/CCA` RAM SGMT patch (`912bcb63`), `nf_cal_period=120`, `pktlog_filter=0x0` (`+27.66%` GP, `-51.65%` jit), tight per-TID AQL (`BE=1500/2500`), `tcp_comp_sack=250us/16`, `multicast_querier=1` (`-32.73%` `p50`)** | **`-43.03%` `p95` RTT (`R49`)**, **`3.613 ms` E2E `B1` (`S405A`)**, **`19.07h` `0`-drop on `.84`** |

## 3. Canonical `200`-Window Universal `WA` Champion `v8` Knob Matrix
- **Xtensa Target Firmware & `ath10k` Debugfs**:
  - `PB040-CANARY-RODATA` (`0x0040bc30`) & `PB040-CCA-AGC-OVERRIDE` (`0x009b7584` / `0x00029e00`) verified in `/tmp` RAM (`fw_checksums = 912bcb63 / 278d2d76`).
  - `pktlog_filter = 0x0`, `nf_cal_period = 120`, `htt_max_amsdu_ampdu = '2 64'`, `ani_enable = 1`, `iw phy0 set rts off`.
- **`mac80211` Airtime & FQ-CoDel**:
  - `aql_threshold = 4000`, `aql_txq_limit`: `VO(0) = 300/600`, `VI(1) = 1000/2000`, `BE(2) = 1500/2500` (`1500/3000` PtMP AP), `BK(3) = 500/1000`.
  - `aqm`: `fq_limit = 512`, `fq_memory_limit = 3145728`, `AP fq_quantum = 3028`, `STA fq_quantum = 1514`.
- **Linux Bridge, GMAC0 (`eth0`) & TCP Stack**:
  - `br-lan`: `multicast_snooping = 1`, `multicast_querier = 1`, `multicast_to_unicast = 1` (via `FMX-DISC-36` safe sysfs path).
  - `sysctl`: `tcp_autocorking = 0`, `tcp_comp_sack_delay_ns = 250000`, `tcp_comp_sack_nr = 16`, `tcp_notsent_lowat = 8192`, `tcp_limit_output_bytes = 65536`, `tcp_early_retrans = 4`, `tcp_slow_start_after_idle = 0`, `gro_normal_batch = 16`, `vm.min_free_kbytes = 4096`.
