<!-- doc-head: STAGE633A_CUMULATIVE_70ROUND_284WINDOW_WA_CHAMPION_V11.md preserved document content -->
<!-- /doc-head -->



# Stage 633A — Cumulative `70`-Round (`284`-Window) `WA Champion v11` Golden Synthesis & Promotion Ledger

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware` (`AR9342` + `QCA9882`)
- **Milestone Achieved**: **`70` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds = `280` Live RF Windows + `4` `Stage 162A` E2E Windows = `284` Cumulative Live Windows** (`308` including all 7 E2E rounds `S162A`..`S631A`).

---

## 1. Cumulative `70`-Round (`284`-Window) Champion `v11` Progression Summary

| Stage / Milestone | Rounds (`Windows`) | Key Promoted Discoveries | Head-to-Head vs Stock (`R70` & `S631A-E2E-R7`) |
| :--- | :--- | :--- | :--- |
| **`Stages 123A..169A` (`v3`)** | `R1..R21` (`88` win) | Asymmetric `fq_quantum` (`3028/1514`), `AQL` `1500/3000`, `BQL` `4542/36288`, `min_free_kbytes=4096` | `+11.2%` GP, `-49.8%` `p50` RTT |
| **`Stages 211A..386A` (`v4..v7`)** | `R22..R42` (`172` win) | `gro_normal_batch=16`, `fq_limit=512`, `htt_max_amsdu_ampdu=2 64`, `tcp_autocorking=0`, `BB_timing=0x13761320` | `+8.5%` GP, `-52.6%` `p50` RTT |
| **`Stages 403A..408A` (`v8`)** | `R43..R49` (`200` win) | Live RAM `PB-040` `SGMT` (`Seg[1]`/`Seg[3]`), `pktlog=0x0`, `nf_cal=120s`, `comp_sack=250us/16` | `+21.7%` GP, `-45.0%` `p50` RTT |
| **`Stages 507A..570A` (`v9..v10`)** | `R50..R63` (`256` win) | Live RAM `PB-050 v1/v2` `SGMT` `Seg[2]` (`.data` `@ 0x0040c140`, `fw_checksums=92363606/12b29d01`), `tcp_notsent_lowat=16384`, `netdev_tstamp_prequeue=0` | `+14.05%` RF GP, `-81.96%` `p50` RTT |
| **`Stages 629A..634A` (`v11`)** | **`R64..R70` (`284` win)** | `PB-050 v3` (`5000 ms`), `SGI/Retry` + `PAPRD/TPC` helpers, `netdev_max_backlog=2048`, `optmem_max=65536`, `tcp_fin_timeout=15` | **`+21.50%` RF GP (`70.72 Mbps`, `-75.99%` `p50`), `+19.54%` E2E GP (`70.10 Mbps`, `-65.23%` `p50`)** |

---

## 2. Artifacts & Verification

- Master Receipt: [`stage633a_cumulative_70round_284window_wa_champion_v11.json`](../artifacts/autoresearch/stage633a_cumulative_70round_284window_wa_champion_v11.json)
- Universal Script: [`99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)
- Test Suite: [`test_stage633a.py`](../tests/test_stage633a.py)
