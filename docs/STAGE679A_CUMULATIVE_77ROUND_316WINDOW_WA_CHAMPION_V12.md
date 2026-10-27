<!-- doc-head: STAGE679A_CUMULATIVE_77ROUND_316WINDOW_WA_CHAMPION_V12.md preserved document content -->
<!-- /doc-head -->


# Stage 679A — Cumulative `77`-Round (`316`-Window) Universal `WA Champion v12` Ledger

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Cumulative Scale**: **`77` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds** = **`308` RF Windows** + `Stage 162A E2E` (`312` windows) + `Stage 677A E2E-R8` (**`316` windows**; **`340` total live windows** across all 8 E2E rounds).

## 1. Executive Summary (`WA Champion v12` — `316` Live Windows)
`Stage 679A` ([`build_stage679a_cumulative_77round_316window_wa_champion_v12.py`](../tools/autoresearch/build_stage679a_cumulative_77round_316window_wa_champion_v12.py)) consolidates all `77` counterbalanced rounds (`R1..R77`) into the canonical `Universal WA Champion v12` profile ([`99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)):

| Milestone Metric | Stock `OpenWrt 24.10.4` | **`WA Champion v12` (`R77` / `E2E-R8`)** | Verified Improvement |
| :--- | :--- | :--- | :--- |
| **`S676A-R77` 16-Stream Bidir Goodput (`VHT20`)** | `62.009 Mbps` | **`76.546 Mbps` (`78.513 Mbps` peak in `B1`)** | **`+23.44%` (`+14.54 Mbps`)** |
| **`S676A-R77` Under-Load `p50` / `p95` RTT** | `59.395 ms` / `149.895 ms` | **`33.219 ms` (`17.776 ms` in `B1`) / `119.597 ms`** | **`-44.07%` `p50` / `-20.21%` `p95`** |
| **`S677A-E2E-R8` Through `MikroTik MK1-251` Goodput** | `42.571 Mbps` | **`69.928 Mbps` (`70.974 Mbps` in `B1`)** | **`+64.26%` (`+27.36 Mbps`)** |
| **`S677A-E2E-R8` Through `MikroTik MK1-251` `p50` RTT** | `95.809 ms` | **`13.056 ms` (`9.884 ms` in `B1`)** | **`-86.37%` (`-82.75 ms`)** |
| **`Panel1-Guarida` (`.84`) Production WDS Uptime** | — | **`72,267 s` (`20.07 hours`) across `3/3` CPEs** | **`0` drops / `0` OOMs** |

## 2. Newly Promoted / Validated `v12` Parameters (`R71..R77`)
1. **`net.core.netdev_budget = 600` (`R72`)**: `+6.00%` goodput (`75.134 Mbps` vs `70.879 Mbps`) and `-7.22%` `p50` RTT under 16-stream bidirectional saturation.
2. **`gro_flush_timeout_ns = 20000` + `dev_weight_tx_bias = 2` (`R75` — `304`-Window Milestone)**: `-33.08%` `p50` RTT (`13.164 ms` vs `19.672 ms`) and `-21.93%` `p95` RTT (`+4.96%` Pareto).
3. **`aql_threshold = 3000 us` (`R76`)**: `-43.21%` lower `p50` RTT (`13.810 ms` vs `24.318 ms`) and `-37.80%` lower `p95` RTT (`44.996 ms` vs `72.343 ms`).
4. **Target-Side `PB-050`/`PB-060` + `fmx_qca_htt_tx_compl_guard.sh` + `fmx_qca_txbf_stbc_ldpc_guard.sh` (`R71`, `R73`)**: Verified RAM-only on `AP .20` and `CPE .250` (`fw_checksums = 92363606 / 12b29d01`).

## 3. Artifacts & Verification
- **Receipt**: [`stage679a_cumulative_77round_316window_wa_champion_v12.json`](../artifacts/autoresearch/stage679a_cumulative_77round_316window_wa_champion_v12.json)
- **Pytest**: [`tests/test_stage679a.py`](../tests/test_stage679a.py)
