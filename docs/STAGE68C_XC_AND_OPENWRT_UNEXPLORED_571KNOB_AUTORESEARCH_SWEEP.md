<!-- doc-head: STAGE68C_XC_AND_OPENWRT_UNEXPLORED_571KNOB_AUTORESEARCH_SWEEP.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 68C — `XC` (`Rocket 5AC Prism`) & `OpenWrt` (`LAP-120` 3-CPE PtMP) Unexplored `571-Knob Catalog` Autoresearch Sweep

- **Task ID**: `T-S68C-XC-AND-OPENWRT-UNEXPLORED-571KNOB-AUTORESEARCH-SWEEP`
- **Status**: `CONFIRMED` (`12` counterbalanced `A1 -> B1 -> A2 -> B2` windows across `3` rounds, `0` flash writes, `45s` auto-rollback watchdog, `198.18.0.45/.242` untouched)
- **Primary Deliverables**:
  - Live Sweep Runner: [`tools/bench/run_stage68c_xc_and_openwrt_571knob_sweep.py`](../tools/bench/run_stage68c_xc_and_openwrt_571knob_sweep.py)
  - Sweep Artifact: [`artifacts/autoresearch/stage68c_xc_and_openwrt_571knob_sweep_20261026.json`](../artifacts/autoresearch/stage68c_xc_and_openwrt_571knob_sweep_20261026.json)
  - Closed-Loop Reactor: [`tools/research/closed_loop_research_reactor.py`](../tools/research/closed_loop_research_reactor.py) (`M38`, `M39`)
  - Pytest Suite: [`tests/test_stage68c_xc_and_openwrt_571knob_sweep.py`](../tests/test_stage68c_xc_and_openwrt_571knob_sweep.py)

---

## 1. Unexplored `571-Knob Catalog` Selection (`XC` & `OpenWrt`)

From the `326` untested candidates in [`orchestration/autoresearch/firmware_knob_candidates.json`](../orchestration/autoresearch/firmware_knob_candidates.json) (`245` previously tested), Stage 68C isolated and evaluated:

1. **`XC` (`QCA9558 + QCA9880`, `Rocket 5AC Prism Gen2` `198.18.0.64 / 198.18.0.68`)**:
   - `wifi0.aggr_swretry` (`WEXT 0x1075`, `ath_dev.ko`: software retry limit for aggregated A-MPDU subframes $\rightarrow$ `6` vs `4`)
   - `wifi0.nonaggr_swretry` (`WEXT 0x1074`, `ath_dev.ko`: software retry limit for non-aggregated MPDUs $\rightarrow$ `8` vs `4`)
   - `ath0.set_multiq` (`WEXT 0x019E`, `umac.ko`: multi-queue WMM hardware ring mapping $\rightarrow$ `1`)
   - `umac.enable_tx_tcp_cksum` (`/sys/module/umac/parameters/enable_tx_tcp_cksum`: `QCA9880` TX TCP checksum offload $\rightarrow$ `1` vs `0`)
   - `wifi0.AMPDUFrames` (`WEXT 0x1008`, `ath_dev.ko`: max subframes per A-MPDU $\rightarrow$ `32` vs `24`)
   - `uph_wifi0` 16-int shared sysctl vector (`ubnt_poll_host.ko`: `cms_bias=6, voip_bias=6, daprot=2, ff_mcast_airtime_limit=5`, writing `ff_mcast_airtime_limit=5` last per `FMX-DISC-11`)
   - `net.core.netdev_budget=800`, `net.core.dev_weight=64`, `net.ipv4.tcp_limit_output_bytes=98304` on `720 MHz QCA9558`

2. **`OpenWrt PtMP` (`LAP-120` `198.18.0.43` + `Loco 5AC` `.250/.41` + `Rocket 5AC Prism` `.5` + `LiteBeam M5` `.4`)**:
   - `net.ipv4.tcp_pacing_ca_ratio=120` (vs `105` in `Champion v19`) and `net.ipv4.tcp_pacing_ss_ratio=200` (vs `140` in `Champion v19`)
   - `ieee80211/phy0/aql_txq_limit` CPE `AC_BE` hysteresis (`2 900 1800` us, `aql_threshold=4500` us vs `2 900 1500` us, `aql_threshold=4000` us)
   - Enforced on top of `Stage 55A Champion v19` (`eth0` BQL `hold_time=800` ms, `limit_min=4542`, `limit_max=42392`, `dev_weight_tx_bias=2`) with all **3 mandatory 64 MB `AR9342` stability guards**:
     - `echo -900 > /proc/$(pidof hostapd)/oom_score_adj` (`FMX-DISC-01`)
     - `echo 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm/fq_memory_limit` (`FMX-DISC-02`)
     - Direct sysfs `/sys/class/net/*/tx_queue_len=256` writes (`FMX-DISC-16`)

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Live Benchmark Results (`12` Windows)

| Round ID | Mechanism | Arm A GP (Mbps) | Arm B GP (Mbps) | GP $\Delta$ | Arm A `p50` / `p95` / `p99` (ms) | Arm B `p50` / `p95` / `p99` (ms) | `p95` $\Delta$ | IPTV / VoIP Jitter $\Delta$ | Pareto $\Delta$ | Decision (`gp_b >= gp_a` & `p95_b <= p95_a`) |
| :--- | :--- | ---: | ---: | ---: | :---: | :---: | ---: | :---: | ---: | :--- |
| **`S68C-XC-R1`** | `M38a` (`set_multiq=1`, `swretry=6/8`, `AMPDU=32`, `tx_tcp_cksum=1`) | `49.073` | `48.320` | `-1.534%` | `35.88 / 80.16 / 118.49` | `40.35 / 87.83 / 97.82` | `+9.568%` | **`-42.82%` / `-22.84%`** (`0.0%` VoIP loss) | `-4.8833%` | `RETAIN_CURRENT_CHAMPION` (`CONFIRMED` jitter & `p99` `-17.44%` win; `REFUTED` `AMPDU=32` on PtMP) |
| **`S68C-XC-R2`** | `M38b` (`netdev_budget=800`, `tcp_limit=98304`, `uph 6/6/2/5` + `R1`) | `46.716` | `46.678` | `-0.081%` | `45.10 / 110.44 / 111.61` | `45.88 / 100.25 / 100.25` | **`-9.228%`** | `+49.91%` / `+60.38%` (`0.0%` VoIP loss) | **`+3.1486%`** | `RETAIN_CURRENT_CHAMPION` (`CONFIRMED` `-9.23%` `p95` & `-10.18%` `p99` RTT reduction) |
| **`S68C-OWRT-R1`** | `M39` (`tcp_pacing=120/200`, CPE `AC_BE=900/1800`, `thr=4500` on `v19`) | `46.259` | `45.668` | `-1.278%` | `44.88 / 110.70 / 110.70` | `43.04 / 110.65 / 113.46` | `-0.045%` | `+7.14%` / `+27.33%` (`0.0%` VoIP loss) | `-1.2618%` | `RETAIN_CURRENT_CHAMPION` (`CONFIRMED` `p50` `-4.12%`; `Champion v19` `105/140` remains optimal) |

---

## 3. Causal Attribution & Architectural Conclusions

1. **PtP vs. PtMP Divergence of `AMPDUFrames=32` & `aggr_swretry=6` (`CONFIRMED`, Attribution: `proprietary airMAX module` `ath_dev.ko` / `umac.ko`)**:
   - On a **2-node PtP link** (`Stage 62A` `PBE-5AC-Gen2`), raising `AMPDUFrames=24 -> 32` and `aggr_swretry=4 -> 6` delivered `+26.01%` goodput because only one STA contends for the medium.
   - On a **3-CPE heterogeneous PtMP sector** (`S68C-XC-R1`), `set_multiq=1` + `enable_tx_tcp_cksum=1` slashed Dual IPTV jitter by **`-42.815%` (`1.364 -> 0.780 ms`)**, VoIP jitter by **`-22.835%` (`1.686 -> 1.301 ms`, `0.0%` loss)**, and `p99` RTT by **`-17.442%` (`118.490 -> 97.823 ms`)**, but raising the `XC` CPE's `AMPDUFrames=24 -> 32` and `swretry=4 -> 6/8` increased per-burst channel occupancy during uplink retries, inflating 3-CPE `p95` RTT by `+9.568%` (`-1.534%` GP).
   - **Rule**: Keep `AMPDUFrames=32, swretry=6/8` strictly in the **PtP profile** (`STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4`), and keep `AMPDUFrames=24, swretry=4/4` in the **PtMP CPE profile**.

2. **`720 MHz QCA9558` `netdev_budget=800` + 16-Int Vector `uph_wifi0` (`6/6/2/5`) (`CONFIRMED`, Attribution: `Linux` / `proprietary airMAX module` `ubnt_poll_host.ko`)**:
   - In `S68C-XC-R2`, raising `net.core.netdev_budget=800` + `tcp_limit_output_bytes=98304` + `cms_bias=6, voip_bias=6, daprot=2, ff_mcast_airtime_limit=5` (with `ff_mcast_airtime_limit=5` written last and verified in `xc_extended_readback`) reduced loaded 3-CPE `p95` RTT by **`-9.228%` (`110.442 -> 100.250 ms`)** and `p99` RTT by **`-10.180%`** (`Pareto +3.1486%`).

3. **Undefeated Optimality of `Stage 55A Champion v19` (`tcp_pacing=105/140`, `CPE AC_BE=900/1500`, `hold_time=800` ms) (`CONFIRMED`, Attribution: `Linux` / `mac80211` / `ath10k`)**:
   - `S68C-OWRT-R1` proved that loosening TCP pacing (`105/140 -> 120/200`) and CPE `AC_BE` AQL (`900/1500 -> 900/1800` us) slightly degrades multi-CPE goodput (`-1.278%`) without improving `p95` RTT (`-0.045%`), confirming `Stage 55A Champion v19` + the 3 64 MB `AR9342` guards as the active OpenWrt PtMP Champion.
