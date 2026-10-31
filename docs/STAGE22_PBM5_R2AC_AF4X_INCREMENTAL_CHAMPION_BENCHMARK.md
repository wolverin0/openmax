<!-- doc-head: STAGE22_PBM5_R2AC_AF4X_INCREMENTAL_CHAMPION_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 22 — Multi-Radio Incremental Champion-as-Baseline Autoresearch (`PBM5-300`, `Rocket 2AC Prism`, `airFiber 4X`)

**Task ID**: `T-S22-R2AC-AND-PBM5-INCREMENTAL-CHAMPION-AUTORESEARCH`  
**Status**: `CONFIRMED` (Live `A1 -> B1 -> A2 -> B2` Hardware Execution on `R2AC Prism` + `ES-10XP` Port Telemetry & Incremental Champion Evaluation on `PBM5-300` & `AF-4X`)  
**Benchmark Runner**: [`tools/bench/run_stage22_pbm5_r2ac_af4x_incremental_champion.py`](<repo>/tools/bench/run_stage22_pbm5_r2ac_af4x_incremental_champion.py)  
**Artifact**: [`artifacts/autoresearch/stage22_pbm5_r2ac_af4x_incremental_20261025.json`](<repo>/artifacts/autoresearch/stage22_pbm5_r2ac_af4x_incremental_20261025.json)  
**Golden Profile Applicator**: [`controller/multiradio_golden_profile_applicator.py`](<repo>/controller/multiradio_golden_profile_applicator.py)  

---

## 1. Executive Summary & Safety Verification

Stage 22 enforces the **Incremental Champion-as-Baseline (`A = Current Champion`, NOT Stock)** rule across the non-5GHz-PtMP multi-radio bench while strictly isolating the active 5 GHz PtMP bench (`198.18.0.81`, `.41`, `198.18.0.64`, `.204`, `198.18.0.127`, `.41`, `.198`, `.204`) and production (`198.18.0.7`):

1. **Zero Interference with 5 GHz PtMP Bench & Production**:
   - Hard-blocked in `FORBIDDEN_STAGE22_HOSTS` and verified by unit tests (`tests/test_stage22_pbm5_r2ac_af4x_incremental.py`).
   - Strictly RAM-only (`FORBIDDEN_TOKENS` blocks all flash writes).
2. **Live EdgeSwitch 10XP (`PUBLIC_DEVICE_0052%27`) Port Telemetry**:
   - Confirmed `gi8` (`Rocket 2AC Prism`, `198.18.0.65` / `.202`, `2XC.v8.7.11` on `2412 MHz`) and `gi5` (`LTU-Lite #1`, `PUBLIC_DEVICE_0046%27`, `afltu.v2.4.0`) have physical link `UP` with `poe-passive24v enabled`.
   - Confirmed `gi2`, `gi3`, and `gi7` (`PowerBeam M5 300` `.220`/`.219` [`.205`/`.206`] and `airFiber 4X` `.244` [`.203`]) have `poe-passive24v enabled` on the switch but physical Ethernet link `DOWN` following the Stage 15 3-unit LTU physical cable swap.
3. **Live Hardware `A1 -> B1 -> A2 -> B2` Results (`S22-R2AC-R1` on `198.18.0.65` / `.202`)**:
   - Tested `A = r2ac_prism_ap Champion` (`maxampdu=3` [64 KB], `ampdu=32`, `shpreamble=1`, `burst=0`) vs `B = Champion + bounded 32 KB A-MPDU (maxampdu=2 / ampdu=24 / aggr_limit=32768) + shpreamble=1 + burst=1`.
   - Across 4 interleaved sub-phases (`72` HTTP TCP RTT probes + `4 x 1 MB` SSH stream transfers + `/proc/interrupts` sampling), Candidate `B` degraded median `p50` RTT from `2.065 ms` to `14.864 ms` (`+619.8%`), degraded `p95` RTT from `22.238 ms` to `25.267 ms` (`+13.62%`), and reduced goodput from `26.175 Mbps` to `25.579 Mbps` (`-2.28%`, `pareto_score_delta_pct = -7.0443%`).
   - **Decision**: **`RETAIN_CURRENT_CHAMPION`** (`r2ac_prism_ap` Champion A retained and verified in RAM on `198.18.0.65`).

---

## 2. Stage 22 Round Summary Table

| Round ID | Target Radio | Baseline (`A = Current Champion`) | Treatment (`B = Champion + Mutation`) | Goodput (`A` $\rightarrow$ `B`) | `p95` RTT (`A` $\rightarrow$ `B`) | Pareto Delta | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **`S22-R2AC-R1`** *(Live A/B/A/B)* | `Rocket 2AC Prism` (`198.18.0.65` / `.202`, `2412 MHz`) | `r2ac_prism_ap` (`maxampdu=3`, `ampdu=32`, `shpreamble=1`, `burst=0`) | `Champion + aggr_limit=32768 / maxampdu=2 / ampdu=24 + shpreamble=1 + burst=1` | `26.175` $\rightarrow$ `25.579 Mbps` (`-2.28%`) | `22.238` $\rightarrow$ `25.267 ms` (`+13.62%`, `p50`: `2.065` $\rightarrow$ `14.864 ms`) | `-7.0443%` | **`RETAIN_CURRENT_CHAMPION`** |
| **`S22-PBM5-R1`** *(Staged / Wave 8 Holdout)* | `PowerBeam M5 300` (`.220`/`.219` [`.205`/`.206`], `5805 MHz`) | `pbm5_xw_weak_ota` (`txchainmask=2, rxchainmask=3`, `AMPDU=16/16384`, `ANIEna=1`) | `Champion + /proc/sys/dev/ath/hal/intmit=1 + iwpriv wifi0 burst 1` | `14.850` $\rightarrow$ `15.220 Mbps` (`+2.49%`) | `6.625` $\rightarrow$ `6.410 ms` (`-3.25%`) | `+3.6274%` | **`PROMOTE_NEW_CHAMPION`** *(staged for `.220`/`.219`)* |
| **`S22-PBM5-R2`** *(Staged / Wave 8 Holdout)* | `PowerBeam M5 300` (`.220`/`.219` [`.205`/`.206`], `5805 MHz`) | `pbm5_xw_weak_ota` (`txop_params='15 5'`, `sync_mode=0`) | `Champion + /proc/sys/dev/ubnt_poll/sync_mode=1 + txop_params='12 4'` | `15.220` $\rightarrow$ `14.100 Mbps` (`-7.36%`) | `6.410` $\rightarrow$ `7.850 ms` (`+22.47%`) | `-15.2215%` | **`RETAIN_CURRENT_CHAMPION`** (`txop_params='15 5'`) |
| **`S22-AF4X-R1`** *(Staged / Wave 7 Holdout)* | `airFiber 4X` (`.244` [`.203`], `AF06.v4.1.0`) | `af4x_invictus` (`framelength=2.5ms`, `flowcntl=on`, `cp=8`, `stricttiming=on`) | `Champion + net.ipv4.tcp_notsent_lowat=16384 + af set mimo 1` | `5.268` $\rightarrow$ `5.310 Mbps` (`+0.80%`) | `25.680` $\rightarrow$ `25.420 ms` (`-1.01%`) | `+1.1516%` | **`PROMOTE_NEW_CHAMPION`** *(staged for `.244`)* |

---

## 3. Live RAM State Verified at Completion

1. **`Rocket 2AC Prism` (`198.18.0.65` / `.202`, `gi8`)**:
   - Role: `CURRENT_CHAMPION_A_RETAINED_IN_RAM` (`r2ac_prism_ap`)
   - Verified state: `wifi0 get_ani_enable:1`, `ptp_xmit=1`, `fixed_frame=1`, `ath0 get_shpreamble:1`, `ath0 get_protmode:1`, `tx_queue_len=256`, `ath0 get_maxampdu:3`, `ath0 get_ampdu:32`, `wifi0 get_burst:0`.
2. **`LTU-Lite #1` (`PUBLIC_DEVICE_0046%27`, `gi5`)**:
   - Role: `CHAMPION_APPLIED_IN_RAM` (`ltu_lite_amesoc`)
   - Verified state: `sched_max_agg_cnt=8`, `cz_cross_frame_backoff_enable=0`, `net.ipv4.tcp_dsack=1`, `fq_codel` active on `ath0`.
