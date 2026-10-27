<!-- doc-head: Stage 515A SimPy + pymoo NSGA-II Evaluation of LTU DCXO GPS Discipline vs Free-Running TCXO on 4096-QAM (12X) -->
Models and optimizes `LTU`'s `bbp_rf_dcxo_sync_track` (`GPS`-disciplined `DCXO`) vs `BBEA_track_tcxo_routine` (free-running `TCXO`) discovered in Stage 486A (`ame_core.ko`), quantifying Carrier Frequency Offset (`CFO`) impact on `4096-QAM` (`12X`) constellation EVM.
<!-- /doc-head -->

# Stage 515A — `SimPy` + `pymoo` `NSGA-II` Evaluation of `LTU` `DCXO` GPS Discipline vs Free-Running `TCXO` on `4096-QAM` (`12X`)

- **Epistemic Status**: `CONFIRMED` (`Stage 486A` `ame_core.ko` `43` `dcxo` / `25` `tcxo` symbol RE + `SimPy`/`NSGA-II` Pareto simulation)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko` `bbp_rf_dcxo_*` & `BBEA_track_tcxo_routine`)
- **Script**: [`run_stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.py`](../tools/sim/run_stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.py)
- **JSON Receipt**: [`stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.json`](../artifacts/autoresearch/stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.json)

---

## 1. Stage 486A Symbol Discovery in `ame_core.ko` (`SHA-256: fe5d489e...`)

Stage 486A dissected all `9,699` defined symbols in `ame_core.ko` and discovered that `LTU` manages frequency synthesis accuracy through **two distinct oscillator tracking loops** (`43` `dcxo` hits and `25` `tcxo` hits):
1. **GPS-Disciplined Digitally Controlled Crystal Oscillator (`DCXO`)**:
   - `bbp_rf_dcxo_is_sync_by_gps`, `bbp_rf_dcxo_get_gps_state`, `bbp_rf_dcxo_sync_start`, `bbp_rf_dcxo_sync_track`, `bbp_rf_dcxo_sync_adjust`, `bbp_rf_dcxo_adj`, and `ame_core_NxN_dcxo_sync`.
2. **Free-Running Temperature Compensated Crystal Oscillator (`TCXO`) Fallback**:
   - `bbp_rf_dcxo_is_sync_by_tcxo`, `BBEA_track_tcxo_routine`, `ap_sched_track_tcxo_routine`, and `bbp_rf_tcxo_item_expired`.

Why does this matter for **`4096-QAM` (`12X`, `12` bits/symbol)**? Decoding a `64x64` (`4096`-point) I/Q grid requires an RMS Error Vector Magnitude (`EVM`) better than **`-38.0 dB` (`1.26%` error)**. Under free-running `TCXO` drift (`~160–420 Hz` residual CFO at `5.8 GHz`), inter-carrier phase rotation pushes effective EVM to `-35.8 dB`, locking the link out of `4096-QAM` (`0.0%` `12X` dwell).

---

## 2. `SimPy` + `NSGA-II` Pareto Results (`DCXO` GPS Discipline vs Free-Running `TCXO`)

| Oscillator Mode (`ame_core.ko`) | Tracking Period (`ms`) | `12X` Entry Floor (`dB`) | Pull Step (`ppb`) | Mean Goodput (`Mbps`) | `4096-QAM` (`12X`) Dwell | `p99` Latency (`ms`) | LDPC Retrans Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Free-Running `TCXO` (`bbp_rf_dcxo_is_sync_by_tcxo`)** | `25.0 ms` | `-37.0 dB` | `10.0 ppb` | `409.73 Mbps` | `0.0%` | `2.95 ms` | `0.0%` |
| **GPS-Disciplined `DCXO` Champion (`bbp_rf_dcxo_is_sync_by_gps`)** | **`35.2 ms`** | **`-39.29 dB`** | **`36.0 ppb`** | **`618.0 Mbps` (`+50.83%`)** | **`100.0%`** | **`2.15 ms`** | **`0.0%`** |
