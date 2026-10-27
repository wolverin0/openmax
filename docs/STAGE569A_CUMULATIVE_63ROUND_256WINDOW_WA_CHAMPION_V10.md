<!-- doc-head: STAGE569A_CUMULATIVE_63ROUND_256WINDOW_WA_CHAMPION_V10.md preserved document content -->
<!-- /doc-head -->



# Stage 569A — Cumulative `63`-Round (`256`-Window) `WA Champion v10` Golden Synthesis & Promotion Ledger

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware` (`AR9342` + `QCA9882`)
- **Milestone Achieved**: **`63` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds = `252` Live RF Windows + `4` `Stage 162A` E2E Windows = `256` Cumulative Live Windows** (`276` including all 6 E2E rounds `S162A`..`S567A`).

---

## 1. Cumulative `63`-Round (`256`-Window) Champion `v10` Progression Summary

| Stage / Milestone | Rounds (`Windows`) | Key Promoted Discoveries | Head-to-Head vs Stock (`R63` & `S567A-E2E-R6`) |
| :--- | :--- | :--- | :--- |
| **`Stages 123A..169A` (`v3`)** | `R1..R21` (`88` win) | Asymmetric `fq_quantum` (`3028/1514`), `AQL` `1500/3000`, `BQL` `4542/36288`, `min_free_kbytes=4096` | `+11.2%` GP, `-49.8%` `p50` RTT |
| **`Stages 211A..386A` (`v4..v7`)** | `R22..R42` (`172` win) | `gro_normal_batch=16`, `fq_limit=512`, `htt_max_amsdu_ampdu=2 64`, `tcp_autocorking=0`, `BB_timing=0x13761320` | `+8.5%` GP, `-52.6%` `p50` RTT |
| **`Stages 403A..408A` (`v8`)** | `R43..R49` (`200` win) | Live RAM `PB-040` `SGMT` (`Seg[1]`/`Seg[3]`), `pktlog=0x0`, `nf_cal=120s`, `comp_sack=250us/16` | `+21.7%` GP, `-45.0%` `p50` RTT |
| **`Stages 507A..512A` (`v9`)** | `R50..R56` (`228` win) | Live RAM `PB-050` `SGMT` `Seg[2]` (`.data` `@ 0x0040c140` RC probe `4000 ms`, `fw_checksums=92363606/12b29d01`), `tcp_notsent_lowat=16384` | `+16.72%` RF GP, `-62.60%` `p50` RTT |
| **`Stages 565A..570A` (`v10`)** | **`R57..R63` (`256` win)** | `PB-050 v1/v2` (`4000 ms` vs `3000 ms`), `netdev_tstamp_prequeue=0`, `tcp_recovery=1` (RACK-TLP), `fmx_qca988x_dfs_chirp_immunity.sh` | **`+14.05%` RF GP (`-81.96%` `p50`), `+12.63%` E2E GP (`-69.22%` `p50`)** |

---

## 2. Artifacts & Verification

- Master Receipt: [`stage569a_cumulative_63round_256window_wa_champion_v10.json`](../artifacts/autoresearch/stage569a_cumulative_63round_256window_wa_champion_v10.json)
- Universal Script: [`99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)
- Test Suite: [`test_stage569a.py`](../tests/test_stage569a.py)
