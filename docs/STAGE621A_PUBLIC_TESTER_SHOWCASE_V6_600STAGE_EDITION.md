<!-- doc-head: STAGE621A_PUBLIC_TESTER_SHOWCASE_V6_600STAGE_EDITION.md preserved document content -->
<!-- /doc-head -->


# Stage 621A — Public Tester Showcase `v6` (`600`-Stage Milestone Edition)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **Milestone Release**: Packages the `600`-Stage Ground-Up breakthroughs into Public Tester Showcase `v6` (`wolverin0/openmax`), spanning **`180` SquashFS `v13` images** (`WA` `12`, `XC` `12`, `XW` `6`), the **5-Board `LTU` Champion `v13` kit**, and **`612` live counterbalanced windows**.

## 2. Multi-Family Showcase `v6` Matrix
| Hardware Family | Boards / Images | New `v6` Ground-Up Modules (`Stages 591A..620A`) | Flagship Verified Result |
| :--- | :---: | :--- | :--- |
| **`WA` (`QCA988x`)** | `12` (`72` imgs) | `fmx_qca988x_peer_sgi_retry_helper.sh` + `txbf_stbc_ldpc` + `7935B` A-MSDU | `+115.35%` `VHT40` (`24.83 Mbps`), `+25.26%` `7935B` A-MSDU |
| **`XC` (`QCA9558`)** | `12` (`72` imgs) | `fmx_qca988x_ani_spur_helper.sh` + `39us` `slot_guard_us` alerter | `+37.65%` Guarida `Panel2`/`3` goodput, `4.33%` guard tax |
| **`XW` (`AR9344`)** | `6` (`36` imgs) | `fmx_xw_xm_ani_swr_helper.sh` + `STBC`/`LDPC` adaptive helper | Zero VSWR PA trip + `2x1` Alamouti NLOS stability |
| **`AF-LTU` (`Beetle`)** | `5` boards (`v13`) | `fmx_ltu_lbt_auto_freq_helper.sh` + `fmx_ltu_tof_timing_advance_helper.sh` | `180` live windows (`0.191 ms` RTT, `0` `/dev/ame*` touches) |

## 3. Safety & Rollback Guarantees
- Mandatory `45 s` Non-DFS / `120 s` DFS (`FMX-DISC-24`) rollback watchdogs and `mtd0`/`mtd1`/`mtd5` SHA-256 backup gate before any flash.
