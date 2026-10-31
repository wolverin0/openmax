<!-- doc-head: STAGE68A_PBE5AC_HYBRID_OTA_READINESS_AND_V5_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 68A: PowerBeam 5AC Gen2 (`0xe3d6`) Hybrid OTA OpenWrt STA Readiness, `mtd` Flags Audit & Ground-Up `Champion v5` Autoresearch

- **Stage / Ticket**: `Stage 68A` (`T-S68A-PBE5AC-HYBRID-OTA-OPENWRT-STA-242-AND-AIROS8-V5-BENCH`)
- **Date**: `2026-10-26`
- **Target Hardware**:
  - `198.18.0.45` (`198.18.0.8`, `PUBLIC_DEVICE_0038`, `PBE-5AC-Gen2` `0xe3d6`, `WA.v8.7.11` AP)
  - `198.18.0.46` (`198.18.0.74`, `PUBLIC_DEVICE_0037`, `PBE-5AC-Gen2` `0xe3d6`, `WA.v8.7.11` Remote OTA STA)
- **Artifacts & Tools**:
  - [`tools/bench/run_stage68a_pbe5ac_hybrid_and_v5_autoresearch.py`](../tools/bench/run_stage68a_pbe5ac_hybrid_and_v5_autoresearch.py)
  - [`artifacts/autoresearch/stage68a_pbe5ac_hybrid_and_v5_autoresearch_20261026.json`](../artifacts/autoresearch/stage68a_pbe5ac_hybrid_and_v5_autoresearch_20261026.json)
  - [`tests/test_stage68a_pbe5ac_hybrid_and_v5.py`](../tests/test_stage68a_pbe5ac_hybrid_and_v5.py)

---

## 1. Pre-Flight & Hybrid `airOS 8` AP $\leftrightarrow$ `OpenWrt` STA Readiness + `mtd` Audit (`CONFIRMED`)

1. **Hybrid Admission Readiness on `198.18.0.45` (`AP`, `CONFIRMED`)**:
   - Verified with a `45s` auto-rollback guard on `198.18.0.45` that applying `allow_80211=1` + `iwpriv ath0 wds 1` keeps `198.18.0.46` (`STA`) `100%` associated (`0%` packet loss on `198.18.0.46` [`1.423..8.175 ms`] and `198.18.0.74` [`1.540..4.069 ms`], `-67 dBm` AP RX / `-65 dBm` STA RX, `noisefloor = -89 dBm`).
2. **Remote STA (`198.18.0.46`) `/proc/mtd`, `sysfs` Flags & `tmpfs` Audit (`CONFIRMED`)**:
   - `/proc/mtd` & `/sys/class/mtd/mtd*/flags` on `.242`:
     - `mtd0` (`u-boot`, `262,144` B), `mtd1` (`u-boot-env`, `65,536` B), `mtd2` (`kernel`, `1,048,576` B), `mtd3` (`rootfs`, `15,073,280` B), `mtd4` (`cfg`, `262,144` B), `mtd5` (`EEPROM`, `65,536` B) all report `flags=0xc00` (`MTD_CAP_NORFLASH = MTD_WRITEABLE 0x400 | MTD_BIT_WRITEABLE 0x800`), while `ubnthal.ko` gates physical SPI NOR writes on `mtd2`/`mtd3` via `/dev/gpio` (`c 127, 0`, `ioctl(11, 0x14bede4d)` per `FMX-DISC-17`).
   - `/var` (`/tmp`) `tmpfs` on `.242` has **`14,428 KiB` (`14.77 MB`) free** (`17%` used out of `17,408 KiB`), which comfortably fits the `6,947,480`-byte (`6.78 MiB`) SquashFS-repacked `factory-sta-242.bin` or `sysupgrade-sta-242.bin`.

---

## 2. Counterbalanced 12-Window Over-The-Air Autoresearch Sweep (`S68A-R1..R3`)

All rounds were evaluated against `S68A-R0` (`Stage 62A-R2` Champion v4 baseline) across `198.18.0.8 -> 198.18.0.74` (`30` loaded RTT samples/arm) using `compute_fmx_objective` from `orchestration/autoresearch/fmx_autoresearch_harness.py`:

| Round | Candidate Treatment | Arm A Goodput (Mbps) | Arm B Goodput (Mbps) | Goodput $\Delta$ | Bulk TCP $\Delta$ | Arm A `p50`/`p95` (ms) | Arm B `p50`/`p95` (ms) | `p95` RTT $\Delta$ | Karpathy `fmx_loss` (`A -> B`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S68A-R1`** | Per-AC WMM `AC_VI` (`cwmin=2, cwmax=4, aifs=2, txop=3008`) + `AC_VO` (`1/3/2/1504`) + `shortgi=1` + `ldpc=1` + `chainmask=3` | `9.713` | `13.774` | **`+41.81%`** | **`+57.67%`** | `6.989` / `33.549` | `3.023` / `11.950` | **`-64.38%`** | `1.4385 -> 0.4191` | **`KEEP`** (`CONFIRMED`) |
| **`S68A-R2`** | **`set_CabqMaxdur=20` + `SyncFlex=0` + `dev_weight=64` + `netdev_max_backlog=2000` + `tcp_limit_output_bytes=131072` + `tcp_pacing=120/200`** | `19.877` | **`22.723`** (`B1=25.235`) | **`+14.32%`** | **`+24.87%`** | `2.497` / `7.232` | **`2.093` / `6.164`** | **`-14.77%`** | **`0.2306 -> 0.1966`** | **`KEEP` (`Stage 68A Champion v5`)** |
| **`S68A-R3`** | Combined `S68A-R1` + `S68A-R2` | `20.035` | `19.549` | `-2.43%` | `-6.52%` | `2.139` / `5.903` | `2.455` / `7.325` | `+24.09%` | `0.2108 -> 0.2784` | **`DISCARD`** (`CONFIRMED`) |

- **Why `S68A-R2` Won (`Stage 68A Champion v5`) and `S68A-R3` Was `DISCARD` (`CONFIRMED`)**:
  - `S68A-R2` achieved the lowest absolute `fmx_loss` (`0.196621`, `fmx_score = 0.803379`), boosting Aggregate Goodput **`+14.32%` (`19.877 -> 22.723 Mbps`, `B1=25.235 Mbps`)** and Bulk TCP **`+24.87%` (`11.104 -> 13.866 Mbps`)** while simultaneously cutting loaded `p50` RTT **`-16.18%` (`2.497 -> 2.093 ms`)**, `p95` RTT **`-14.77%` (`7.232 -> 6.164 ms`)**, and VoIP loss **`-77.78%` (`0.117% -> 0.026%`)** (`Jain = 0.9967`).
  - In `S68A-R3`, stacking `S68A-R1`'s narrower `AC_VI` contention window (`cwmin=2, cwmax=4, aifs=2, txop=3008` us) with `S68A-R2`'s larger TCP small-queue budget (`131,072` B) allowed `0x80` Video TCP bursts (`7.769 Mbps`) to preempt `AC_BE` Bulk TCP (`-6.52%`) and raise `p95` RTT (`+24.09%`).
  - **Persistence Receipt**: `S68A-R2` (`Stage 68A Champion v5`) persisted to `/etc/persistent/rc.poststart` + `cfgmtd -w -p /etc/` on both `.241` (`CFGMTD_RC=0`) and `.242` (`CFGMTD_RC=0`).
