<!-- doc-head: STAGE385A_CUMULATIVE_42ROUND_172WINDOW_WA_CHAMPION_V7.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 385A — Cumulative `42`-Round (`172`-Window) `WA` Hardware Autoresearch Synthesis & Universal Champion `v7` Blueprint

## 1. Executive Summary (`CONFIRMED`)
- **Stage ID**: `Stage 385A` (verified by `Stage 386A` regression test suite `tests/test_stage381a_to_386a_wa_172window_champion.py`).
- **Cumulative Evidence Base**: **`42` counterbalanced `A1 -> B1 -> A2 -> B2` autoresearch rounds (`172` live `15s` hardware windows)** across `Stage 83C` through `Stage 385A` on `OpenWrt 24.10.4` `WA` (`AR9342` + `QCA9882` `ath10k-ct`) + `3` end-to-end `MK1-251` stress rounds + live production deployment on `Panel1-Guarida` (`198.18.0.7`).
- **Primary Artifact**: [`artifacts/autoresearch/stage385a_cumulative_42round_172window_wa_champion_v7.json`](<repo>/artifacts/autoresearch/stage385a_cumulative_42round_172window_wa_champion_v7.json)

## 2. Progression of `WA` Hardware Autoresearch Milestones (`R1..R42`, `172` Windows)

| Campaign Stage | Rounds (`Windows`) | Key Promoted Breakthroughs | Peak Goodput / Key Latency Breakthrough |
| :--- | :---: | :--- | :--- |
| **`Stages 83C..152A`** | `R1..R12` (`48` win) | `aql_txq_limit=3000/4000`, `htt_max_amsdu_ampdu='3 64'`, `ani_enable=1`, `tx_Weight=64`, `eth0` `fq_codel`, `bql=24576` | `66.15 Mbps` (`1x1`), `-48.03%` `p99` RTT |
| **`Stages 211A..213A`** | `R13..R18` (`72` win) | `nf_conntrack_tcp_be_liberal=1`, `rps_cpus=0`, `eth0 txqueuelen=256`, `sch_fq_codel target 3ms interval 40ms` | **`77.31 Mbps` (`2x2` `VHT40`)**, `12.69 ms` `p50` |
| **`Stages 241A..245A`** | `R19..R24` (`96` win) | `netdev_budget=600` (`3000 us`), `tcp_notsent_lowat=8192`, `p50=11.094 ms` (`-56.04%` vs stock) + `Panel1` `v4` | `72.42 Mbps` (`R23 B2`), `11.094 ms` `p50` |
| **`Stages 275A..279A`** | `R25..R30` (`124` win) | `aql_threshold=4000`, `vm.min_free_kbytes=4096`, `tcp_slow_start_after_idle=0` + `MK1-251` (`-56.10%` `p50`) + `Panel1` `v5` | `69.93 Mbps` (`R26 A2`), `10.197 ms` `p50` |
| **`Stages 311A..315A`** | `R31..R36` (`148` win) | `gro_normal_batch=16` (`-21.55%` `p95`), `fq_codel limit 512` (`-16.57%` `p95`), `tcp_early_retrans=4` + `MK1-251` (`-54.61%` `p95`) + `Panel1` `v6` | **`74.26 Mbps` (`R33 B1`)**, `10.506 ms` `p50` |
| **`Stages 381A..385A`** | **`R37..R42` (`172` win)** | `htt_max_amsdu_ampdu='2 64'` (`-27.00%` `p50`), `rts off` (`-23.43%` `p95`), `tcp_autocorking=0` (`-15.50%` jitter), `1 Hz` `fw_stats`, `1x1` rescue + **`MK1-251` `p50` `-89.85%` (`88.574 -> 8.987 ms`)** + `Panel1` `v7` | **`79.51 Mbps` (`R38 A1`)**, **`8.987 ms` E2E `MK1-251` `p50`** |

## 3. Canonical Universal `WA` (`AR9342` + `QCA9882`) Champion `v7` Profile
- **Wireless `mac80211` / `ath10k-ct`**:
  - `aql_threshold = 4000`, `aql_txq_limit`: `VO(0)=3000`, `VI(1)=3000`, `BE(2)=4000`, `BK(3)=4000`
  - `htt_max_amsdu_ampdu = '2 64'`, `ani_enable = 1`, `tx_Weight = 64,64,64,64`, `iw phy0 set rts off`, `frag off`
- **Wired GMAC0 (`eth0`) & Linux Qdisc**:
  - `bql/max_limit = 24576`, `txqueuelen = 256`, `rps_cpus = 0`, `xps_cpus = 0`
  - `tc qdisc replace dev eth0 root fq_codel limit 512 quantum 300 target 3ms interval 40ms ecn`
- **Kernel Networking & VM (`sysctl`)**:
  - `net.core.netdev_budget = 600`, `net.core.netdev_budget_usecs = 3000`, `net.core.gro_normal_batch = 16`, `net.core.dev_weight = 64`
  - `net.ipv4.tcp_notsent_lowat = 8192`, `net.ipv4.tcp_limit_output_bytes = 65536`, `net.ipv4.tcp_autocorking = 0`, `net.ipv4.tcp_early_retrans = 4`, `net.ipv4.tcp_slow_start_after_idle = 0`, `net.netfilter.nf_conntrack_tcp_be_liberal = 1`, `vm.min_free_kbytes = 4096`
- **Packaged Files**: [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion`](<repo>/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion), [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp`](<repo>/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp), [`tools/panel1/fmx_panel1_champion_persistence.sh`](<repo>/tools/panel1/fmx_panel1_champion_persistence.sh).
