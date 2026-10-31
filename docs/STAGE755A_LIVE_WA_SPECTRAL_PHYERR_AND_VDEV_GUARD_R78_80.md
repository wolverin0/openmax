<!-- doc-head: STAGE755A_LIVE_WA_SPECTRAL_PHYERR_AND_VDEV_GUARD_R78_80.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 755A — Live `WA` Spectral/Radar `PHYERR` Suppression & `WMI_VDEV_START` Guard (`R78..R80` = `328` Cumulative Windows)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` (`12` new live windows; `320` RF windows / `328` cumulative `WA` windows)
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes (`fw_checksums`: `92363606` / `12b29d01`).

## 1. Executive Summary (`R78..R80`)
In `Stage 755A` ([`run_stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.py`](../tools/bench/run_stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.py)), we staged `/tmp/fmx_qca_spectral_radar_phyerr_guard.sh` and `/tmp/fmx_qca_wmi_vdev_start_guard.sh` on both `AP .20` and `CPE .250`, then executed rounds `R78..R80`:

| Round | Hypothesis Tested | Arm A Goodput / `p50` RTT | Arm B Goodput / `p50` RTT | Delta (`GP` / `p50` / `Pareto`) | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S755A-R78`** | Spectral/Radar `PHYERR` Guard (`fmx_qca_spectral_radar_phyerr_guard.sh` + `nf_cal_period=120s` vs `60s`) | `59.620 Mbps` / `19.141 ms` | **`60.016 Mbps`** / **`16.398 ms`** (`p95=51.385 ms`) | `+0.66%` GP / **`-14.33%` `p50`** / **`+8.45%` Pareto** | **`PROMOTE_ARM_B`** |
| **`S755A-R79`** | `WMI_VDEV_START` Guard & `tcp_early_retrans` (`3` vs `4`) under 16-Stream Saturation | **`70.346 Mbps`** / `22.725 ms` | `54.950 Mbps` / `25.349 ms` | `-21.89%` GP / `+11.55%` `p50` / `-19.92%` Pareto | `RETAIN_ARM_A` (`early_retrans=3`) |
| **`S755A-R80`** | `tcp_notsent_lowat` (`16384/6000us` vs `8192/8000us`) | `61.699 Mbps` / `17.698 ms` | **`67.156 Mbps`** / `23.886 ms` (`VoIP jit=1.785 ms`) | **`+8.84%` GP** / `+34.96%` `p50` / **`+15.72%` Pareto** | **`PROMOTE_ARM_B`** (`8192` / `8000 us`) |

## 2. Key Physical-Layer & Kernel Findings
1. **Spectral/Radar `PHYERR` Suppression (`S755A-R78`)**: Disabling background spectral scan interrupts (`spectral_scan_ctl=disable`, `pktlog_filter=0x0`, `nf_cal_period=120`) reduced under-load `p50` RTT by **`-14.33%` (`16.398 ms` vs `19.141 ms`)** and `p95` RTT by **`-24.91%` (`51.385 ms` vs `68.430 ms`)** (`+8.45%` Pareto).
2. **Delayed `TLP` (`tcp_early_retrans=3` in `S755A-R79`)**: Under 16-stream bidirectional saturation, `tcp_early_retrans=4` caused spurious tail-loss probes over half-duplex 802.11ac aggregation (`54.950 Mbps`), whereas `tcp_early_retrans=3` preserved **`70.346 Mbps` (`A1 = 71.350 Mbps`)**.
3. **Tightened `tcp_notsent_lowat=8192` + `netdev_budget_usecs=8000` (`S755A-R80`)**: Increased mean goodput by **`+8.84%` (`67.156 Mbps` vs `61.699 Mbps`)** and lowered `VoIP` jitter from `2.772 ms` to **`1.785 ms`** (`+15.72%` Pareto).

## 3. Artifacts & Verification
- **Receipt**: [`stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.json`](../artifacts/autoresearch/stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.json)
- **Pytest**: [`tests/test_stage755a.py`](../tests/test_stage755a.py)
