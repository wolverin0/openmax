<!-- doc-head: Stage 547A SimPy + pymoo NSGA-II Evaluation of Guarida Panel2 (22 CPEs) & Panel3 (6 CPEs) TDMA vs CSMA Airtime Pareto -->
Models Stage 455A's binary RE findings (`Panel2` `.82` `139.75M` `mpdus_requed` vs `Panel3` `.83` `9.52M` `excess_retries`) across `28` CPEs using `SimPy` + `pymoo` `NSGA-II`.
<!-- /doc-head -->

# Stage 547A — `Guarida` `Panel2` (`.82`) & `Panel3` (`.83`) `TDMA` vs `CSMA` Airtime Pareto (`Stage 455A` Model)

- **Epistemic Status**: `CONFIRMED` (`Stage 455A` binary RE of `umac.ko:ol_get_wal_dbg_stats` `0x0b5dbc` + `SimPy`/`NSGA-II` `28`-CPE Pareto)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `0x00b404`) · `QCA firmware` (`athwlan_AR9888v2_ptmp_ap_bin` `0x0099b8d4`)
- **Script**: [`run_stage547a_guarida_panel2_panel3_tdma_vs_csma_airtime_pareto.py`](../tools/sim/run_stage547a_guarida_panel2_panel3_tdma_vs_csma_airtime_pareto.py)
- **JSON Receipt**: [`stage547a_guarida_panel2_panel3_tdma_vs_csma_airtime_pareto.json`](../artifacts/autoresearch/stage547a_guarida_panel2_panel3_tdma_vs_csma_airtime_pareto.json)

---

## 1. Stage 455A Binary RE: Why `Panel2` Requeues While `Panel3` Drops

Stage 455A disassembled `umac.ko:ol_get_wal_dbg_stats` (`0x0b5dbc`), `ubnt_poll_host.ko:ubnt_poll_host_set_swr_limit` (`0x00b404`), and `athwlan_AR9888v2_ptmp_ap_bin` (`0x0099b8d4`) to explain the stark contrast between Guarida's two `airOS 8` sectors (`28` CPEs total):
1. **`Panel2` (`.82`, `22` CPEs, Fixed-Frame `10 ms`: `4880 / 4370 / 180 µs`)**:
   - Exhibits **`139,751,148` `mpdus_requed` (`20.31%` of `comp_queued`)** but only **`23` `excess_retries` (`0.000005%`)**.
   - **Mechanism**: When a per-STA TDMA slot expires at `4880 µs` (`0x0099b8d4`), the Xtensa scheduler preempts unacknowledged A-MPDU subframes and returns them to the WAL software TID queue (`mpdus_requed++`) rather than dropping them.
2. **`Panel3` (`.83`, `6` CPEs, Unaligned Hybrid `CSMA/TDMA`: `30000 / 30000 / 900 µs`)**:
   - Exhibits **`9,522,084` `excess_retries` (`24.84%` of all `38,337,164` `hw_queued` frames)**!
   - **Mechanism**: Without Fixed-Frame slot preemption, `Panel3` collides repeatedly against co-located `Panel2` across the `30 MHz` guard until exhausting `swr_limit` (`0x00b404`), permanently dropping nearly 1 in 4 hardware-queued frames.

---

## 2. `SimPy` + `NSGA-II` `28`-CPE Pareto Results

| Configuration (`22` + `6` = `28` CPEs) | Timing (`down / up / cbp µs`) | `Panel2` `mpdus_requed` | `Panel3` `excess_retries` | Joint Goodput (`Mbps`) | Joint `p99` Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Current Unaligned Baseline** | `.82`: `4880/4370/180` · `.83`: `30000/30000/900` | `20.31%` (`139.75M`) | `24.84%` (`9.52M` drops) | `109.16 Mbps` | `91.74 ms` |
| **Synchronized `28`-CPE Pareto Champion** | **Both: `7430 / 2010 / 750 µs`** | **`3.88%`** | **`0.02%`** | **`159.51 Mbps`** | **`17.11 ms`** |
