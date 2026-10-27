<!-- doc-head: STAGE315A_CUMULATIVE_36ROUND_148WINDOW_WA_CHAMPION_V6.md preserved document content -->
<!-- /doc-head -->


# Stage 315A — Cumulative `36`-Round (**`148`-Window**) Universal `WA` Champion Profile `v6` (`99-fmx-wa-universal-champion`)

- **Claim Label**: `CONFIRMED`
- **Attribution**: `Linux` + `mac80211` + `ath10k` + `hardware` (`AR9342` + `QCA9882`)
- **Milestone**: **`36` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds (`144` RF Windows) + `4` `Stage 162A` E2E Windows = `148` Cumulative Live Windows** (plus `4` `Stage 313A` `MK1-251` E2E Windows = **`152` Total Bench Windows**) + `18.23h` Live `Panel1-Guarida` (`.84`) Production Verification
- **JSON Receipt**: [`artifacts/autoresearch/stage315a_cumulative_36round_148window_wa_champion_v6.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage315a_cumulative_36round_148window_wa_champion_v6.json)
- **Firmware Profiles Updated**:
  - [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)
  - [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wmm-dscp-qos`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wmm-dscp-qos)
  - [`firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-pbe5ac-ptp)
  - [`tools/panel1/fmx_panel1_champion_persistence.sh`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/panel1/fmx_panel1_champion_persistence.sh)

---

## 1. Consolidated `36`-Round (`148`-Window) Universal `WA` Champion `v6` Knob Table

| Subsystem | Knob / Parameter | Stock OpenWrt Default | Universal `WA` Champion `v6` | Proven Impact (`R1..R36`) |
| :--- | :--- | :---: | :---: | :--- |
| **Linux VM (`64 MB` RAM)** | `vm.min_free_kbytes` | `8192` | **`4096`** (`FMX-DISC-34`) | `+235%..+616%` `MemAvailable` (`9.023 MB` on `.84`) |
| **mac80211 AQL (`VHT20`)** | `aql_txq_limit` (`VO`/`VI`/`BE`/`BK`) | `5000/12000` | **`300/600`, `1000/2000`, `1500/3000`, `500/1000`** | `-29.4%` to `-49.3%` `p95` RTT (`R31`, `R36`) |
| **mac80211 AQL (`VHT40`/`VHT80`)** | `FMX_VHT40_AQL_BE` / `FMX_VHT80_AQL_BE` | `5000/12000` | **`4000/4000` (`VHT40`) / `2000/4000`, `thr=3000` (`VHT80`)** | `-30.10%` `p50` (`VHT40`), `-23.13%` `p95` (`VHT80`) |
| **mac80211 FQ-CoDel** | `AP` / `STA` `fq_quantum`, `fq_limit`, `fq_memory_limit` | `300`, `1024`, `4 MB` | **`3028` (`2xMTU` AP) / `1514` (`1xMTU` STA), `512`, `3 MB`** | `-20.91%` Pure UL `p50` RTT (`R32`), `-16.5%` `p95` (`R23`) |
| **WMM DSCP & `nftables` QoS** | `99-fmx-wmm-dscp-qos` (`inet fmx_wmm_qos`) | Unclassified (`TID 0`) | **Auto `EF->TID 6`, `CS6->TID 6`, `AF41->TID 5`, `CS1->TID 1`** | `+23.99%` Pareto (`R30`), `-49.30%` `p95` RTT (`R36`) |
| **NAPI & GRO Amortization** | `gro_normal_batch` / `gro_flush_timeout` / `budget` | `8` / `0` / `300` | **`16` / `20000 ns` / `480` (`dev_weight=48, tx_bias=2`)** | Cuts `AR9342` `NET_RX` softirq & `-8.28%` `p50` (`R27`) |
| **TCP Pacing, Loss & Idle** | `ca_ratio` / `ss_ratio` / `early_retrans` / `slow_start_after_idle` | `120` / `200` / `3` / `1` | **`110` / `150` / `4` / `0` (`mtu_probing=1, thin_linear=1`)** | `-31.30%` bursty `p50` RTT (`R33`), `+35.55%` Pareto (`R17`) |
| **Bridge & Forwarding** | `flow_offloading` / `packet_steering` / `multicast_snooping` | `0` / `0` / `0` | **`1` / `1` (`rps_cpus=1`) / `1` (`multicast_to_unicast=1`)** | `-59.69%` RF `p50` & `4.341 ms` `MK1-251` E2E `p50` (`Stage 313A`) |
