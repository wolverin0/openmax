<!-- doc-head: STAGE511A_CUMULATIVE_56ROUND_228WINDOW_WA_CHAMPION_V9.md preserved document content -->
<!-- /doc-head -->



# Stage 511A — Cumulative `56`-Round (`228`-Window) Universal `WA` Champion `v9` Synthesis

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware` (`AR9342` + `QCA9882`)
- **Milestone Achieved**: **`56` Counterbalanced `A1 -> B1 -> A2 -> B2` Rounds = `224` Live RF Windows + `4` `Stage 162A` E2E Windows = `228` Cumulative Live Windows** (`244` including all 5 E2E rounds `S162A`..`S509A`).

---

## 1. Cumulative `56`-Round (`228`-Window) Champion `v9` Progression Summary

| Stage / Milestone | Rounds (`Windows`) | Key Promoted Discoveries | Head-to-Head vs Stock (`R56` & `S509A-E2E-R5`) |
| :--- | :--- | :--- | :--- |
| **`Stages 123A..169A` (`v3`)** | `R1..R21` (`88` win) | Asymmetric `fq_quantum` (`3028/1514`), `AQL` `1500/3000`, `BQL` `4542/36288`, `min_free_kbytes=4096` | `+11.2%` GP, `-49.8%` `p50` RTT |
| **`Stages 211A..386A` (`v4..v7`)** | `R22..R42` (`172` win) | `gro_normal_batch=16`, `fq_limit=512`, `htt_max_amsdu_ampdu=2 64`, `tcp_autocorking=0`, `BB_timing=0x13761320` | `+8.5%` GP, `-52.6%` `p50` RTT |
| **`Stages 403A..408A` (`v8`)** | `R43..R49` (`200` win) | Live RAM `PB-040` `SGMT` (`Seg[1]`/`Seg[3]`), `pktlog=0x0`, `nf_cal=120s`, `comp_sack=250us/16` | `+21.7%` GP, `-45.0%` `p50` RTT |
| **`Stages 507A..512A` (`v9`)** | **`R50..R56` (`228` win)** | Live RAM `PB-050` `SGMT` `Seg[2]` (`.data` `@ 0x0040c140` RC probe `4000 ms`, `fw_checksums=92363606/12b29d01`), `tcp_notsent_lowat=16384`, `BMISS/CSA` helper, `tx_queue_len=256` | **`+16.72%` RF GP (`-62.60%` `p50`), `+21.57%` E2E GP (`-63.08%` `p50`)** |

---

## 2. Promoted `WA Champion v9` Knob Profile (`99-fmx-wa-universal-champion`)

- **Firmware (`RAM-only` `/tmp/firmware-2-pb050.bin`)**: `PB040-CANARY-RODATA` (`Seg[1]`), `PB050-RC-PROBE-DAMPEN` (`Seg[2]` `0x0040c140`: `4000 ms`), `PB040-CCA-AGC-OVERRIDE` (`Seg[3]` `0x009b7584`: `0x13761320`), `fw_checksums = 92363606 / 12b29d01`.
- **`ath10k` / `mac80211`**: `pktlog_filter=0x0`, `htt_max_amsdu_ampdu="2 64"`, `aql_threshold=4000`, `VO=300/600`, `VI=1000/2000`, `BE=1500/2500..3000`, `fq_quantum=3028/1514`, `fq_limit=512`, `fq_memory_limit=3145728`.
- **Linux Networking / VM**: `tcp_notsent_lowat=16384`, `tcp_early_retrans=3`, `tcp_autocorking=0`, `tcp_comp_sack_delay_ns=250000`, `tcp_comp_sack_nr=16`, `gro_normal_batch=16`, `tx_queue_len=256`, `vm.min_free_kbytes=4096`.

---

## 3. Artifacts & Verification

- Master Receipt: [`stage511a_cumulative_56round_228window_wa_champion_v9.json`](../artifacts/autoresearch/stage511a_cumulative_56round_228window_wa_champion_v9.json)
- Universal Script: [`99-fmx-wa-universal-champion`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion)
- Consolidated Pytest Suite: [`test_stage507a_to_512a_wa_228window_champion.py`](../tests/test_stage507a_to_512a_wa_228window_champion.py)
