<!-- doc-head: STAGE629A_LIVE_WA_PB050_V3_AND_SGI_GUARD_R64_66.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 629A — Live WA `PB-050 v3` (`5000 ms`), SGI/PAPRD Guard & Netdev Backlog Ceiling (`R64..R66` = `268` Windows)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware` (`firmware-2.bin` `SGMT` `Seg[2]` `.data` `@ 0x0040c140`), `ath10k`, `mac80211`, `Linux` (`net/core/dev.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes (`RAM-only` `/tmp/firmware-2-pb050v3.bin` and `/tmp/firmware-2-pb050.bin`).

---

## 1. Live `PB-050 v3` (`0x1388` = `5000 ms`) & SGI/PAPRD Helpers Verification

Both `AP .20` and `CPE .250` staged `/tmp/firmware-2-pb050v3.bin` (`0x0040c140 = 0x1388` `5000 ms`), `/tmp/fmx_qca988x_peer_sgi_retry_helper.sh`, and `/tmp/fmx_qca_paprd_olpc_tpc_helper.sh` in volatile RAM (`fw_checksums = 92363606 / 12b29d01`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Summary (`R64..R66` = `268` Cumulative Windows)

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S629A-R64`** | `PB-050 v3` (`5000 ms` + `nf_cal=180s`) vs `PB-050 v1` (`4000 ms` + `nf_cal=120s`) | `67.891 Mbps` / `17.965 ms` / `46.447 ms` | `68.159 Mbps` (`+0.39%`) / `20.025 ms` / `54.454 ms` | `-8.51%` | `RETAIN_ARM_A` |
| **`S629A-R65`** | `WMI_PEER_ASSOC` SGI/Retry Guard (`Stage 591A`) + PAPRD/TPC (`Stage 573A`) (`16` streams) | `72.751 Mbps` / `19.326 ms` / `45.447 ms` | `69.619 Mbps` / `25.770 ms` / `53.380 ms` | `-14.66%` | `RETAIN_ARM_A` (`74.249 Mbps` window peak!) |
| **`S629A-R66`** | `netdev_max_backlog=1000, optmem_max=20480` vs `2048 / 65536` | `68.627 Mbps` / `17.259 ms` / `42.731 ms` | `68.531 Mbps` / **`14.921 ms`** (`-13.55%`) / `43.624 ms` | **`+1.77%`** | **`PROMOTE_ARM_B`** (VoIP jitter `2.695 -> 2.207 ms`) |

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json`](../artifacts/autoresearch/stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json)
- Runner: [`run_stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.py`](../tools/autoresearch/run_stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.py)
- Test Suite: [`test_stage629a.py`](../tests/test_stage629a.py)
