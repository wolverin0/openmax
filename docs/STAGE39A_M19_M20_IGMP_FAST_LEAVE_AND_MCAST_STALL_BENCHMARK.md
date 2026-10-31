<!-- doc-head: STAGE39A_M19_M20_IGMP_FAST_LEAVE_AND_MCAST_STALL_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 39A — Live 3-CPE 5 GHz `M19` + `M20` (`IGMP` Fast-Leave on Dynamic WDS Ports + Stock `airOS 8` Multicast Airtime Limit & Shared `uph_wifi0` Buffer Audit) Physical Benchmark (`T-S39A-M19-M20-AIROS8-MCAST-STALL-AND-IGMP-FAST-LEAVE-BENCH`)

- **Date**: `2026-10-25`
- **Task ID**: `T-S39A-M19-M20-AIROS8-MCAST-STALL-AND-IGMP-FAST-LEAVE-BENCH`
- **Hardware Sector**: `LAP-120` AP (`198.18.0.43`, OpenWrt 24.10.4 `r28959`, `QCA988x` 5 GHz `20 MHz` `5180 MHz`) + `NanoStation 5AC Loco` (`198.18.0.47` / `198.18.0.67`, `WA`) + `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC` Stock airOS v8.7.11) + `LiteBeam M5` (`198.18.0.48` / `198.18.0.52`, `XW` Stock airOS v6.3.22)
- **Baseline Starting Point**: **`Stage 37A Champion v11`** (`M17b_MAC80211_FQ_LIMIT_TRIPLE_PLAY_QUANTUM_VO_AQL`: AP `fq_quantum=4542` `3×MTU`, CPE `fq_quantum=1514`, `fq_limit=2048/1024`, `AC_VO aql=300/600 us`, `multicast_to_unicast=1`, `airtime_weight=720:512:112`)
- **Safety Verification**: **`0` flash writes** (`flash_writes: 0`, RAM-only `/sys/devices/virtual/net/br-lan/brif/*/multicast_fast_leave`, `/sys/devices/virtual/net/br0/brif/*/multicast_fast_leave`, and `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit`; `0` production radio interactions)
- **Authoritative Receipt**: [`artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json`](../artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json)

---

## 1. Research Question & Physical Control Boundary

Starting strictly from **`Stage 37A Champion v11`**, **Stage 39A (`T-S39A-M19-M20-AIROS8-MCAST-STALL-AND-IGMP-FAST-LEAVE-BENCH`)** tests the physical effect of the Reactor-synthesized `M19` + `M20` multicast/bridge mechanisms under simultaneous **3-Tier Triple-Play Saturation** (`128 Kbps` VoIP in `tid6_ac0` `WMM AC_VO` + `5.0 Mbps` Dual `1080p60` IPTV in `tid4_ac1` `WMM AC_VI` + 3-CPE Bulk TCP in `tid0_ac2` `WMM AC_BE`):
1. **`M20` (`Bridge Port Multicast Fast-Leave & IGMP Discipline` on `LAP-120` `.20` + `Loco 5AC` `.250`)**:
   - On OpenWrt 24.10.4 (`Linux 6.6.110`), `/sys/devices/virtual/net/br-lan/brif/*/multicast_fast_leave` defaults to `0` on `eth0`, `phy0-ap0`, `phy0-ap0.sta1`, and `phy0-ap0.sta2`.
2. **`M19` (`Stock airOS 8 CPE Multicast Stall Prevention & Shared Procfs Buffer Discipline` on `Rocket Prism 5AC Gen2` `.198`)**:
   - On `Rocket Prism 5AC Gen2` (`airOS v8.7.11`), `/sys/module/ame_core/parameters/*` (`add_stall_bd_mcast_threshold`, `UL_data_weight`) belongs to the `LTU` (`AD9361`) architecture, whereas `Rocket Prism 5AC Gen2` (`QCA988x`) uses `ubnt_poll_host.ko` (`/proc/sys/dev/uph_wifi0/*`) and Linux bridge `/sys/devices/virtual/net/br0/brif/*/multicast_fast_leave`.

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Physical Benchmark Results (`S39A-R1` .. `S39A-R3`)

| Round ID | Mechanism ID | Control Arm A | Treatment Arm B | Arm A Goodput | Arm B Goodput | Goodput $\Delta$ | Arm A `p95` RTT | Arm B `p95` RTT | `p95` RTT $\Delta$ | Arm A `p50` RTT | Arm B `p50` RTT | Dual IPTV (`tid4_ac1`) Loss / Jitter | VoIP (`tid6_ac0`) Loss / Jitter | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S39A-R1`** | `M19_M20_IGMPV3_FAST_LEAVE_AND_AIROS8_MCAST_VOIP_BIAS` | `Champion v11` (`IGMPv2=2`, `fast_leave=0`, `r198 voip_bias=0`) | `IGMPv3=3` + CPE `multicast_snooping=1` + `r198 voip_bias=1` after `ff_mcast_airtime_limit=5` | `52.394 Mbps` | `50.005 Mbps` | `-4.560%` | `109.735 ms` | `123.703 ms` | `+12.729%` | `45.073 ms` | `45.380 ms` | `0.00%` loss / `1.211 -> 1.784 ms` | `0.00%` loss / `2.127 -> 2.210 ms` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S39A-R2`** | `M19b_M20b_AP_WDS_FAST_LEAVE_AND_SINGLE_QUERIER_DISCIPLINE` | `Champion v11` (`fast_leave=0`, per-phase `r5ac_champ` & CPE `snooping=0` write) | `IGMPv2=2` + AP WDS `fast_leave=1` + CPE `querier=0` (with per-phase `r5ac_champ` reset) | `37.583 Mbps` | `37.320 Mbps` | `-0.700%` | `79.203 ms` | `88.498 ms` | `+11.736%` | `33.353 ms` | `37.280 ms` | `0.28% -> 0.76%` loss / `1.760 -> 1.826 ms` | `0.00% -> 0.08%` loss / **`2.566 -> 1.841 ms` (`-28.25%`)** | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S39A-R3`** | `M19c_M20c_CLEAN_WDS_FAST_LEAVE_AND_UPH_MCAST_LIMIT` | `Champion v11` (`brif/*/multicast_fast_leave=0`, clean single-init `r5ac_champ`) | **`Stage 39A Champion v12`** (`AP WDS phy0-ap0* fast_leave=1 + DMS=1` + `Loco/Rocket brif fast_leave=1` + `ff_mcast_airtime_limit=5`) | `48.949 Mbps` | **`51.819 Mbps`** | **`+5.863%`** | `113.749 ms` | **`107.651 ms`** | **`-5.361%`** | `49.605 ms` | **`45.266 ms` (`-8.75%`)** | **`0.00%` loss** (`0/5,669` pkts, `4.945 Mbps`) / `1.451 ms` | **`0.00%` loss** (`0/1,199` pkts, `127.5 Kbps`) / `1.892 ms` | **`PROMOTE_NEW_CHAMPION` (`Champion v12`, Pareto `+7.740%`)** |

---

## 3. Three Hardware-Verified Discoveries in `S39A-R1` .. `S39A-R3`

1. **Discovery 1 (`S39A-R1` — Shared `sysctl_table->data` Buffer Clobber in `ubnt_poll_host.ko` + `IGMPv3` `tid7_ac0` Preemption)**:
   - On `Rocket Prism 5AC Gen2` (`airOS v8.7.11`), `/proc/sys/dev/uph_wifi0/voip_bias`, `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit`, `fixed_frame`, `atpc`, `cms_bias`, and `evm_meas_config` share the same 16-integer `sysctl_table->data` vector inside `ubnt_poll_host.ko`. Writing `echo 1 > /proc/sys/dev/uph_wifi0/voip_bias` *after* `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` overwrote `ff_mcast_airtime_limit` from `5` down to `1` (`"uph_wifi0/ff_mcast_airtime_limit": 1` in `S39A-R1` `B1`/`B2` readbacks).
   - Simultaneously, upgrading `multicast_igmp_version` from `2` to `3` and enabling `multicast_snooping=1` on the CPE bridges caused the Linux bridge to inject `72`-byte `CS6` (`Internetwork Control` $\rightarrow$ **`tid7_ac0` `WMM AC_VO`**) IGMPv3 general query frames during active traffic windows (`tid7_ac0: tx_packets_delta = 2` in `B1` and `1` in `B2`, compared to `0` in `A1`/`A2`), regressing goodput by `-4.560%` and `p95` RTT by `+12.729%`.
2. **Discovery 2 (`S39A-R2` — Mid-Round `br_multicast_toggle()` MDB Flush & `tc qdisc replace` Reset)**:
   - Keeping `IGMPv2=2` eliminated the `tid7_ac0` preemption (`tx_packets_delta = 0`) and reduced VoIP jitter by **`-28.254%`** (`2.566 -> 1.841 ms`), but writing to `/sys/devices/virtual/net/br-lan/bridge/multicast_snooping` on `Loco 5AC` and re-running `tc qdisc replace dev ath0 root fq_codel` on `Rocket Prism 5AC Gen2` before each 6-second window flushed bridge MDB/qdisc state and induced `drops_delta > 0` (`5, 1, 4, 2`) on `tid0_ac2`.
3. **Discovery 3 (`S39A-R3` — `M19c_M20c_CLEAN_WDS_FAST_LEAVE_AND_UPH_MCAST_LIMIT` $\rightarrow$ `Stage 39A Champion v12`)**:
   - Initializing `r5ac_champ` once before `A1` and enabling per-port `multicast_fast_leave = 1` + `multicast_to_unicast = 1` on `LAP-120` dynamic WDS ports (`phy0-ap0`, `phy0-ap0.sta1`, `phy0-ap0.sta2`), `Loco 5AC` (`eth0`), and `Rocket Prism 5AC Gen2` (`ath0`, `eth0` + `ff_mcast_airtime_limit = 5`) with Single-Querier IGMPv2 (`multicast_igmp_version = 2` on AP only):
     - Boosts 3-CPE aggregate goodput from **`48.949 Mbps` to `51.819 Mbps` (`+5.863%`)** (`B1 = 51.599 Mbps`, `B2 = 52.040 Mbps` vs `A1 = 48.706 Mbps`, `A2 = 49.191 Mbps`),
     - Cuts loaded 3-CPE `p95` RTT from **`113.749 ms` to `107.651 ms` (`-5.361%`)**,
     - Cuts loaded 3-CPE `p50` RTT from **`49.605 ms` to `45.266 ms` (`-8.747%`)**,
     - Delivers **`0.00%` Dual `1080p60` IPTV loss** (`0 / 5,669` datagrams lost across `B1` + `B2`, `4.945 Mbps` delivered, `1.451 ms` jitter in `tid4_ac1`) and **`0.00%` VoIP loss** (`0 / 1,199` datagrams lost across `B1` + `B2`, `127.5 Kbps` delivered, `1.892 ms` jitter in `tid6_ac0`) with **`0` drops** across all hardware TXQs (`tid0_ac2`, `tid4_ac1`, `tid6_ac0`, `tid7_ac0`).

---

## 4. Exact `Stage 39A Champion v12` RAM Profile (`STAGE39A_CHAMPION_V12_OVERLAY`)

- **OpenWrt `LAP-120` AP (`198.18.0.43`)**:
  ```sh
  echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_snooping
  echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_querier
  echo 2 > /sys/devices/virtual/net/br-lan/bridge/multicast_igmp_version
  for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
  for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast; do echo 1 > $p 2>/dev/null || true; done
  echo fq_quantum 4542 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_limit 2048 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
  nft delete table inet fmx_iptv_qos 2>/dev/null || true
  nft add table inet fmx_iptv_qos
  nft 'add chain inet fmx_iptv_qos mangle_out { type filter hook postrouting priority -150; policy accept; udp dport 5202 ip dscp set cs4 counter; udp dport 5203 ip dscp set ef counter; }'
  ```
- **OpenWrt `NanoStation 5AC Loco` CPE (`198.18.0.47` / `198.18.0.67`)**:
  ```sh
  for p in /sys/devices/virtual/net/br-lan/brif/*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
  echo fq_quantum 1514 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_limit 1024 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '2 900 1500' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
  ```
- **Stock airOS `Rocket Prism 5AC Gen2` CPE (`198.18.0.64`)**:
  ```sh
  for p in /sys/devices/virtual/net/br0/brif/*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
  echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit
  ```
