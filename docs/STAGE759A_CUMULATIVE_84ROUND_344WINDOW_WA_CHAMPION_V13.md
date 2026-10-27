<!-- doc-head: STAGE759A_CUMULATIVE_84ROUND_344WINDOW_WA_CHAMPION_V13.md preserved document content -->
<!-- /doc-head -->


# Stage 759A — Cumulative `84`-Round (`344`-Window) Universal `WA Champion v13` Ledger

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Cumulative Scale**: **`84` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds** = **`336` RF Windows** + `Stage 162A E2E` (`340` windows) + `Stage 757A E2E-R9` (**`344` windows**; **`368` total live windows** across all 9 E2E rounds).

## 1. Executive Summary (`WA Champion v13` — `344` / `368` Live Windows)
`Stage 759A` ([`build_stage759a_cumulative_84round_344window_wa_champion_v13.py`](../tools/autoresearch/build_stage759a_cumulative_84round_344window_wa_champion_v13.py)) consolidates all `84` counterbalanced rounds (`R1..R84`) into the canonical `Universal WA Champion v13` profile ([`99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)):

| Milestone Metric | Stock `OpenWrt 24.10.4` | **`WA Champion v13` (`R84` / `E2E-R9`)** | Verified Improvement |
| :--- | :--- | :--- | :--- |
| **`S756A-R84` 16-Stream Bidir Goodput (`VHT20`)** | `55.117 Mbps` | **`64.052 Mbps` (`64.682 Mbps` in `B1`)** | **`+16.21%` (`+8.94 Mbps`)** |
| **`S756A-R84` Under-Load `p50` / `p95` RTT** | `84.835 ms` / `145.767 ms` | **`28.741 ms` (`27.571 ms` in `B2`) / `87.589 ms`** | **`-66.12%` `p50` / `-39.91%` `p95`** |
| **`S757A-E2E-R9` Through `MikroTik MK1-251` Goodput** | `55.671 Mbps` | **`66.007 Mbps` (`67.607 Mbps` in `B2`)** | **`+18.57%` (`+10.34 Mbps`)** |
| **`S757A-E2E-R9` Through `MikroTik MK1-251` `p50` RTT** | `83.655 ms` | **`15.812 ms` (`12.267 ms` in `B2`)** | **`-81.10%` (`-67.84 ms`)** |
| **`Panel1-Guarida` (`.84`) Production WDS Uptime** | — | **`73,224 s` (`20.34 hours`) across `3/3` CPEs** | **`0` drops / `0` OOMs** |

## 2. Newly Promoted / Validated `v13` Parameters (`R78..R84`)
1. **`fmx_qca_spectral_radar_phyerr_guard.sh` + `nf_cal_period = 120` (`R78`)**: `-14.33%` `p50` RTT (`16.398 ms` vs `19.141 ms`) and `-24.91%` `p95` RTT (`+8.45%` Pareto).
2. **`tcp_notsent_lowat = 8192` + `netdev_budget_usecs = 8000` (`R80`)**: `+8.84%` goodput (`67.156 Mbps` vs `61.699 Mbps`) and `1.785 ms` `VoIP` jitter (`+15.72%` Pareto).
3. **Asymmetric `AP/STA FQ Quantum` (`4542 B` / `3028 B` in `R81`)**: `-40.61%` `p50` RTT (`17.392 ms` vs `29.285 ms`) and `+1.12%` goodput (`+16.33%` Pareto).
4. **Tighter `eth0 BQL` (`bql_max = 24192 B`, `bql_hold = 400 ms` in `R82`)**: `-36.81%` `p95` RTT (`43.874 ms` vs `69.427 ms`) and `-9.47%` `p50` RTT (`+21.48%` Pareto).

## 3. Artifacts & Verification
- **Receipt**: [`stage759a_cumulative_84round_344window_wa_champion_v13.json`](../artifacts/autoresearch/stage759a_cumulative_84round_344window_wa_champion_v13.json)
- **Pytest**: [`tests/test_stage759a.py`](../tests/test_stage759a.py)
