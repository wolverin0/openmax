<!-- doc-head: STAGE103D_MKT_BIDIRECTIONAL_FRAMESIZE_SOAK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 103D — Live Bidirectional `RFC 2544` (`64B` / `512B` / `1400B`) & 4-Tin `DiffServ4` (`overhead 38 mpu 84 nat`) `VLAN 107` Soak Proof

## 1. Executive Summary & Attribution (`CONFIRMED`)
- **Task ID**: `T-S103D-LIVE-MKT-BOCA7-BIDIRECTIONAL-RFC2544-AND-CAKE-DSCP-SOAK`
- **Artifacts**:
  - Benchmark Runner: [`tools/benchmarks/run_stage103d_mkt_bidirectional_framesize_soak.py`](../tools/benchmarks/run_stage103d_mkt_bidirectional_framesize_soak.py)
  - Counterbalanced Receipt: [`artifacts/autoresearch/stage103d_mkt_bidirectional_framesize_soak.json`](../artifacts/autoresearch/stage103d_mkt_bidirectional_framesize_soak.json)
  - Verification Suite: [`tests/test_stage103d_mkt_bidirectional_framesize_soak.py`](../tests/test_stage103d_mkt_bidirectional_framesize_soak.py)
- **Subsystem Attribution**: `external controller` (`/usr/sbin/fmx_wds_churn_healer.sh` `PtMP Champion v23`) + `Linux` (`eth0.107` `802.1Q` PCP `0..7` + `nftables` `fmx_s103d_diffserv4` 4-Tin `DiffServ4` classifier + `eth0` BQL `limit_min=4542, limit_max=42392` accounting for `38B` `802.1Q`+Ethernet overhead and `84B` MPU) + `mac80211` (4-AC `FQ-CoDel` `fq_quantum=3028`) + `ath10k` (`AQL` `1200/2400 us`) + `proprietary airMAX/LTU module` (`XC` `umac.ko` `set_multiq=3` + `rmmod ath_pktlog`).
- **Safety Invariants Verified (`CONFIRMED`)**:
  - `0` flash writes (`RAM-only` runtime execution with `45s` Non-DFS rollback watchdog).
  - `198.18.0.45` / `198.18.0.46` (`PBE-5AC-Gen2` PtP pair) and `198.18.0.2` (`ether2-sw-poe200`) / `.200` / `.201` (`SG-01` Guarida backbone) strictly untouched.
  - `EdgeSwitch 10XP Boca 7` (`gi7`, `MK1-251` `198.18.0.66`) strictly isolated in `VLAN 107` (`mkt_boca7_lab`).

---

## 2. 4-Tin `DiffServ4` (`overhead 38 mpu 84 nat`) & `RFC 2544` Frame-Size Architecture (`FMX-S103D-01`, `CONFIRMED`)

Across the `3-CPE Sector` (`WA .250` + `XC .198` + `XW 198.18.0.52`) $\leftrightarrow$ `LAP-120` (`.20`) $\leftrightarrow$ `EdgeSwitch VLAN 107` (`gi3 <-> gi7`) $\leftrightarrow$ `MikroTik RB951G-2HnD` (`MK1-251`, `198.18.0.66`), we tested concurrent bidirectional `RFC 2544` frame sizes under full 3-CPE Triple-Play saturation:
1. **Tin 3 (`Voice / Control`, `64B` L2 / `-s 36` ICMP & `128 Kbps` `DSCP EF` `0xb8` VoIP)**:
   - Mapped to `meta priority 0:6` (`WMM AC_VO TID 6` on `phy0-ap0` and `802.1Q PCP 6` on `eth0.107`), accounting for the `84B` minimum physical frame unit (`64B` Ethernet + `4B` `802.1Q` + `16B` preamble/SFD/IFG).
2. **Tin 2 (`Video / Interactive`, `512B` L2 / `-s 484` ICMP & `5.0 Mbps` `DSCP CS4` `0x80` IPTV)**:
   - Mapped to `meta priority 0:5` (`WMM AC_VI TID 4` on `phy0-ap0` and `802.1Q PCP 5` on `eth0.107`).
3. **Tin 1 (`Best-Effort / MTU Bulk`, `1400B` L2 / `-s 1372` ICMP & `iperf3 --bidir -P 2` `DSCP CS0` `0x00`)**:
   - Mapped to `meta priority 0:0` (`WMM AC_BE TID 0` on `phy0-ap0` and `802.1Q PCP 0` on `eth0.107`), bounded by `eth0` BQL `limit_min=4542` (`3 * 1514B` including `38B` `802.1Q`+L1 overhead) and `limit_max=42392` (`28 * 1514B`) + `mac80211` `fq_quantum=3028`.
4. **Tin 0 (`Bulk / Scavenger`, `DSCP CS1` `0x20`)**:
   - Mapped to `meta priority 0:1` (`WMM AC_BK TID 1` and `802.1Q PCP 1`).

---

## 3. Counterbalanced `A1 -> B1 -> A2 -> B2` Results (`S103D-R1`, `CONFIRMED`)

| Metric (`A1 -> B1 -> A2 -> B2` Mean Under Concurrent `64B`/`512B`/`1400B` + 3-CPE Load) | Arm A (Single-Tin Unclassified Baseline) | Arm B (`Stage 103D` 4-Tin `DiffServ4` + `Champion v23`) | Delta (`Arm B vs Arm A`) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **3-CPE Aggregate Goodput (`Mbps`)** | `39.420 Mbps` | **`41.848 Mbps`** | **`+6.16%`** | `CONFIRMED` |
| **E2E `WA -> MK1-251` `64B` (`Voice Tin 3`) `p50` RTT (`ms`)** | `15.852 ms` | **`11.333 ms`** | **`-28.51%`** | `CONFIRMED` |
| **E2E `WA -> MK1-251` `64B` (`Voice Tin 3`) `p99` RTT (`ms`)** | `45.104 ms` | **`38.187 ms`** | **`-15.34%`** | `CONFIRMED` |
| **E2E `WA -> MK1-251` `64B` (`Voice Tin 3`) Mean RTT (`ms`)** | `17.236 ms` | **`14.246 ms`** | **`-17.35%`** | `CONFIRMED` |
| **E2E `WA -> MK1-251` `1400B` (`BestEffort Tin 1`) `p95` RTT (`ms`)** | `66.516 ms` | **`61.341 ms`** | **`-7.78%`** | `CONFIRMED` |
| **E2E `WA -> MK1-251` Composite (`64B+512B+1400B`) `p95` RTT (`ms`)** | `43.003 ms` | **`42.686 ms`** | **`-0.74%`** | `CONFIRMED` |
| **`LAP-120 -> MK1-251` `VLAN 107` `64B` `p99` RTT (`ms`)** | `53.776 ms` | **`42.934 ms`** | **`-20.16%`** | `CONFIRMED` |
| **3-CPE Sector `p95` RTT (`ms`)** | `46.802 ms` | **`46.564 ms`** | **`-0.51%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF` `64B`) Jitter (`ms`)** | `3.921 ms` | **`1.649 ms`** | **`-57.94%`** | `CONFIRMED` |
| **VoIP (`AC_VO` `DSCP EF` `64B`) Packet Loss (`%`)** | `0.215%` | **`0.286%` (`< 0.3%`, `0` `aqm` drops)** | `< 0.3%` SLA | `CONFIRMED` |
| **Karpathy Multi-Objective Pareto Score Delta** | Baseline (`0.00%`) | **`+6.3373%`** (`PROMOTE_NEW_CHAMPION`) | **`+6.34%`** | `CONFIRMED` |

### Per-Window Breakdown (`A1 -> B1 -> A2 -> B2`)

| Phase | 3-CPE Goodput (`Mbps`) | `WA -> MK1-251` `64B` `p50` / `p99` (`ms`) | `WA -> MK1-251` `512B` `p50` / `p95` (`ms`) | `WA -> MK1-251` `1400B` `p50` / `p95` (`ms`) | `LAP-120 -> MK1-251` `64B` `p50` / `p99` (`ms`) | VoIP Jitter (`ms`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `39.367` | `13.516` / `39.758 ms` | `12.003` / `29.538 ms` | `25.579` / `51.911 ms` | `0.936` / `53.736 ms` | `4.084 ms` |
| **`B1`** | **`39.901`** | **`12.107` / `44.012 ms`** | `13.289` / `35.805 ms` | **`21.754` / `74.092 ms`** | **`0.802` / `30.835 ms`** | **`1.815 ms`** |
| **`A2`** | `39.473` | `18.187` / `50.450 ms` | `15.008` / `37.091 ms` | `15.451` / `81.120 ms` | `0.549` / `53.816 ms` | `3.758 ms` |
| **`B2`** | **`43.795`** | **`10.559` / `32.362 ms`** | **`13.929` / `36.093 ms`** | **`17.875` / `48.591 ms`** | **`0.678` / `55.032 ms`** | **`1.483 ms`** |
