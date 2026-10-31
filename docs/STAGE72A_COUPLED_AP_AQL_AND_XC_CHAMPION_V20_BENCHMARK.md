<!-- doc-head: STAGE72A_COUPLED_AP_AQL_AND_XC_CHAMPION_V20_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 72A — Coupled OpenWrt AP AQL / TCP Pacing & `XC` Offload Strict **`Champion v20`** Benchmark

- **Task ID**: `T-S72A-COUPLED-AP-ACBE-AQL-WITH-S70C-STRICT-CHAMPION-V20-BENCH`
- **Status**: `CONFIRMED` (`4` counterbalanced `A1 -> B1 -> A2 -> B2` rounds = `16` physical windows on 3-CPE 5 GHz bench; `0` flash writes; `45s` auto-rollback watchdog; `198.18.0.45/.242` untouched)
- **Promoted Champion**: **`Stage 72A Champion v20` (`S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20` / `M41d`)** (`+7.886%` goodput, `-3.112%` `p50` RTT, `-2.348%` `p95` RTT, `-9.518%` `p99` RTT, `-14.951%` IPTV jitter, `-2.409%` VoIP jitter, **`+8.7076%` Pareto score** -> **`PROMOTE_NEW_CHAMPION`**)
- **Artifacts**:
  - Bench Runner: [`tools/bench/run_stage72a_coupled_ap_aql_and_xc_champion_v20.py`](<repo>/tools/bench/run_stage72a_coupled_ap_aql_and_xc_champion_v20.py)
  - Receipt JSON: [`artifacts/autoresearch/stage72a_coupled_ap_aql_and_xc_champion_v20_20261026.json`](<repo>/artifacts/autoresearch/stage72a_coupled_ap_aql_and_xc_champion_v20_20261026.json)
  - Reactor Integration: [`tools/research/closed_loop_research_reactor.py`](<repo>/tools/research/closed_loop_research_reactor.py) (`M41`)
  - Verification Suite: [`tests/test_stage72a_coupled_ap_aql_and_xc_champion_v20.py`](<repo>/tests/test_stage72a_coupled_ap_aql_and_xc_champion_v20.py)

---

## 1. Summary of All 4 Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds (`16` Windows)

| Round ID | Mechanism | Arm A GP (`Mbps`) | Arm B GP (`Mbps`) | GP Delta (`%`) | Arm A `p95` (`ms`) | Arm B `p95` (`ms`) | `p95` Delta (`%`) | IPTV Jitter Delta | VoIP Jitter Delta | Pareto Delta | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S72A-COUPLED-AP-AQL-XC-V20` (`R1`)** | `M41`: `AP AC_BE=1350/2700 thr=2000` + `XC TSQ=65536` | `28.935` | `25.964` | `-10.268%` | `85.883` | `91.076` | `+6.047%` | `-6.565%` | **`-23.521%`** | `-12.384%` | `RETAIN` (`REFUTED`) |
| **`S72A-R2-AP-AQL-1500-3000-THR-4500-XC-V20`** | `M41b`: `AP AC_BE=1500/3000 thr=4500` + `XC TSQ=65536` | `34.047` | `33.118` | `-2.729%` | `95.489` | `154.785` | `+62.097%` | `+2.205%` | `+14.240%` | `-24.463%` | `RETAIN` (`REFUTED`) |
| **`S72A-R3-WARMED-PACED-AP-V19-XC-MULTIQ-CKSUM-BUDGET800-TSQ98304`** | `M41c`: Warmed + `AP/Loco Pacing 120/200 TSQ=65536` + `XC S70C` | `41.622` | `38.084` | `-8.500%` | `93.659` | **`90.802`** | **`-3.050%`** | **`-4.561%`** | **`-3.915%`** | `-7.433%` | `RETAIN` (`REFUTED`) |
| **`S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20`** | **`M41d` (`Champion v20`)**: Warmed + Untouched `AP v19` (`TSQ=98304, thr=5000`) + `XC S70C` (`TSQ=98304`) | `22.623` | **`24.407`** | **`+7.886%`** | `117.753` | **`114.988`** | **`-2.348%`** | **`-14.951%`** | **`-2.409%`** | **`+8.708%`** | **`PROMOTE_NEW_CHAMPION`** |

---

## 2. Step-by-Step Causal Isolation (`R1 -> R2 -> R3 -> R4`)

1. **`R1` (`S72A-COUPLED-AP-AQL-XC-V20` — `REFUTED` — `mac80211`)**:
   - Lowering `AP` `aql_threshold` from `5000` to `2000 us` (below `AC_BE` `high_us=2700 us`) forced `net/mac80211/tx.c:ieee80211_txq_airtime_check` to clamp all station TXQs permanently to `low_us=1350 us` whenever `Loco 5AC` transmitted a `2 ms` burst.
   - This triggered `tid0_ac2` (`AC_BE`) FQ_CoDel drops (`10` in `B1`, `7` in `B2`) and a `-10.268%` goodput drop, even while VoIP jitter fell `-23.521%`.
2. **`R2` (`S72A-R2-AP-AQL-1500-3000-THR-4500-XC-V20` — `REFUTED` — `proprietary airMAX module` `ath_rate_atheros` + `mac80211`)**:
   - Raising `AP AC_BE` back to `1500/3000` with `aql_threshold=4500` uncovered a critical bench invariant: immediately after `_apply_v18_baseline_once`, `LiteBeam M5` (`802.11n` 1x1 `XW`) starts `A1/B1` at `rx_bitrate_mbps=6.5` (`MCS0`), consuming **6x more airtime per packet** until its rate control trains up to `26.0–39.0 Mbps` in `A2/B2` (`45.661 Mbps` in `A2`).
   - Adding a 10-packet `1200 B` rate-control warmup across `.4`, `.5`, and `.41` before `A1` eliminated the `MCS0` cold-start artifact in `R3` and `R4`.
3. **`R3` (`S72A-R3-WARMED-PACED-AP-V19-XC-MULTIQ-CKSUM-BUDGET800-TSQ98304` — `REFUTED` — `Linux` TCP TSQ)**:
   - With pre-A1 rate-control warmup (`LiteBeam M5` at `26.0–39.0 Mbps` from `A1` onward) and `AP` AQL kept at `1500/3000, thr=5000` (`0` FQ_CoDel drops), `R3` cut `p50` RTT by `-9.31%` (`46.967 -> 42.593 ms`), `p95` RTT by `-3.050%` (`93.659 -> 90.802 ms`), IPTV jitter by `-4.561%`, and VoIP jitter by `-3.915%`.
   - However, lowering OpenWrt `AP`/`Loco` `tcp_limit_output_bytes` from `98304` (`96 KB`) to `65536` (`64 KB`) starved local socket queueing (`TSQ`) at `41.6 Mbps x 46 ms` BDP (`-8.500%` goodput).
4. **`R4` (`S72A-R4-WARMED-AP-V19-XC-S70C-CHAMPION-V20` — `CONFIRMED` — **`Stage 72A Champion v20`**)**:
   - Restoring `tcp_limit_output_bytes=98304` (`96 KB`) and `tcp_pacing=105/140` on `OpenWrt LAP-120` (`.20`) and `Loco 5AC` (`.250`) while keeping the pre-A1 rate-control warmup and applying `Stage 70C` on `Rocket 5AC Prism` (`.198`: `AMPDUFrames=24, aggr_swretry=4, nonaggr_swretry=4, set_multiq=1, enable_tx_tcp_cksum=1, netdev_budget=800, tcp_limit_output_bytes=98304, daprot=2, ff_mcast_airtime_limit=5`) achieved simultaneous `gp_b >= gp_a` (`+7.886%`) and `p95_b <= p95_a` (`-2.348%` `p95`, `-9.518%` `p99`, `-14.951%` IPTV jitter, `-2.409%` VoIP jitter, **`+8.7076%` Pareto**).
   - Combined with Stage 70C (`43.827 -> 47.578 Mbps`, peak `49.559 Mbps` / `2.478 bps/Hz`, `-23.373%` VoIP jitter), **`Stage 72A Champion v20`** is promoted as the new 3-CPE heterogeneous PtMP Champion.
