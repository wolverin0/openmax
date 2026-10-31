<!-- doc-head: STAGE491A_PBE5AC_PTP_COMPLETE_DOSSIER_AND_SCORECARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 491A — Complete `PowerBeam 5AC Gen2` (`.241 <-> .242`) Live PtP Dossier & Master Scorecard

## 1. Consolidated 11-Stage Live Hardware Progression (`CONFIRMED`)
Synthesizes all 11 live hardware stages executed on the `PowerBeam 5AC Gen2` (`WA` `AR9342` + `QCA9882`, `0xe3d6`) PtP bench pair (`198.18.0.45` AP $\leftrightarrow$ `198.18.0.46` Remote OTA STA on `MK1-251` `Boca 7`):
- `Stage 105A`: Golden `mtd0/1/4/5` backups, Stock `airOS 8` baseline (`22.80 Mbps`, `p95=7.56 ms`), 100% remote OTA dual-bank (`mtd2`+`mtd3`) conversion to `OpenWrt 24.10.4`, and initial `A1 -> B1 -> A2 -> B2` (`14.62 Mbps` mean, `0.0%` `1472B` loss).
- `Stage 425A`: Asymmetric High-MCS DL & `htt_max_amsdu_ampdu="3 64"` sweep (`14.43 Mbps` DL + `5.19 Mbps` UL = `19.62 Mbps`).
- `Stage 426A`: Near-field `txpower` (`4..23 dBm`) & aggregation sweep (`txp23_amsdu3_64` winner).
- `Stage 427A`: `VHT20` / `VHT40` / `VHT80` bandwidth autoresearch with 26s rollback guard.
- `Stage 428A`: Live deployment of `fmx_chain_imbalance_rescue_daemon.sh` (`Stage 349A`) & `fmx_wmi_retry_and_hook_loader.sh` (`Stage 409A`).
- `Stage 429A`: Counterbalanced `A1 -> B1 -> A2 -> B2` `PtP Champion v2` (**`20.58 Mbps` mean, `22.46 Mbps` peak in `B1`, `5.54 Mbps` mean UL / `7.23 Mbps` peak UL, `0.0%` `1472B` loss**).
- `Stage 430A`: Universal `WA` `PtP Champion v2` kit (`PBE-5AC-Gen2`, `LBE-5AC-Gen2`, `NBE-5AC-Gen2`, `NS-5AC`).
- `Stage 487A`: `.242` STA `VHT80` capability unlock & `VHT40` (`bw=1`) live sweep.
- `Stage 488A`: Simultaneous Triple-Play (`VoIP 64B` + `IPTV 1316B` + `Bulk TCP`) QoE verification.
- `Stage 489A`: End-to-end L2/L3 `4addr` WDS bridge & multicast snooping verification (`Host PC -> .241 -> .242`).
- `Stage 490A`: Zero-flash-touch Xtensa `SGMT` RAM bind-mount canary reload on `.241`.

---

## 2. Master Scorecard (`20 MHz` & `40 MHz` @ `5200 MHz`)

| Stack / Arm | Width | 64B RTT `p50` / `p95` (ms) | Full-MTU `1472B` Loss (%) | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate (Mbps) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stock `airOS 8` TDMA (`WA.v8.7.25/11`)** | `20 MHz` | `1.96` / `7.56` (`p99=10.68`) | `0.0%` | `19.20` | `3.60` | `22.80` |
| **OpenWrt `24.10.4` Stock (`Arm A` Mean)** | `20 MHz` | `1.659` / `2.470` | `30.0%` | `9.67` | `0.97` | `10.64` |
| **OpenWrt `FuturaMAX PtP Champion v2` (`Arm B` Mean)** | `20 MHz` | **`1.589` (`-18.9%`)** / **`2.676` (`-64.6%`)** | **`0.0%`** | **`15.04` (`+55.5%`)** | **`5.54` (`+53.9%` vs airOS)** | **`20.58` (`+93.4%`)** |
| **OpenWrt `FuturaMAX PtP Champion v2` (`B1` Peak)** | `20 MHz` | `1.621` / `3.201` | **`0.0%`** | **`15.23`** | **`7.23` (`+100.8%` vs airOS)** | **`22.46`** |
| **OpenWrt `Stage 487A VHT40 Champion` (`bw=1`)** | `40 MHz` | `1.701` / `17.882` | **`0.0%`** | **`16.74`** | **`8.09` (`+124.7%` vs airOS)** | **`24.83` (`+8.9%` vs airOS)** |

- **Additional Stage 488A–490A Proofs (`CONFIRMED`)**:
  - **Stage 488A Triple-Play QoE**: Concurrent Bulk TCP **`1.90 -> 6.05 Mbps` (`+218.4%`)**, IPTV `1316B` loss **`40.0% -> 0.0%`**, VoIP `64B` loss **`13.0% -> 6.0%`**.
  - **Stage 489A Bidirectional E2E WDS Bridge**: `4,194,304 B` (`4 MB`) single-stream HTTP transfer from Host PC $\rightarrow$ `.241` (`Boca 3`) $\rightarrow$ OTA `4addr` WDS $\rightarrow$ `.242` (`MK1-251` `Boca 7`) at **`6.77 Mbps`** with `multicast_snooping=1` and `multicast_to_unicast=1`.
  - **Stage 490A Xtensa `SGMT` RAM Bind-Mount Canary**: Zero-flash-touch `/tmp/fmx_xtensa_canary` bind-mount over `/lib/firmware/ath10k/QCA988X/hw2.0` (`board.bin` + `firmware-2.bin`), clean `wifi down && wifi up` reload, and **`0.0%` `1472B` loss (`10/10` packets)**; also discovered and fixed the `OpenWrt 24.10.4` in-place `wifi reload` `VHT40 -> VHT20` Xtensa peer-phymode desync by enforcing `wifi down; sleep 2; wifi up`.

## 3. Artifacts & Verification
- Script: [`build_stage491a_pbe5ac_ptp_complete_dossier_and_scorecard.py`](../tools/benchmarks/build_stage491a_pbe5ac_ptp_complete_dossier_and_scorecard.py)
- JSON Artifact: [`stage491a_pbe5ac_ptp_complete_dossier_and_scorecard.json`](../artifacts/autoresearch/stage491a_pbe5ac_ptp_complete_dossier_and_scorecard.json)
- Test Suite: [`test_stage491a.py`](../tests/test_stage491a.py)
