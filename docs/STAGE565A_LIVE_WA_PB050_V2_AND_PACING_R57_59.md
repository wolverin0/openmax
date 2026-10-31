<!-- doc-head: STAGE565A_LIVE_WA_PB050_V2_AND_PACING_R57_59.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 565A — Live WA `PB-050 v2` `SGMT` `Seg[2]` Rate-Control Probe & Per-AC AQL/Pacing Tuning (`R57..R59` = `240` Windows)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware` (`firmware-2.bin` `SGMT` `Seg[2]` `.data` `@ 0x0040c140`), `ath10k`, `mac80211`, `Linux` (`net/ipv4/tcp_output.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes (`RAM-only` `/tmp/firmware-2-pb050v2.bin` and `/tmp/firmware-2-pb050.bin`).

---

## 1. Live `PB-050 v2` (`0x0bb8` = `3000 ms`) vs `PB-050 v1` (`0x0fa0` = `4000 ms`) Verification

Both `AP .20` and `CPE .250` staged `/tmp/firmware-2-pb050v2.bin` (`SHA-256 = 424eda4e988fcaaf470651f23bbaf5ddeea1244ddd99fb254a3442ff0912d683`) alongside `/tmp/firmware-2-pb050.bin` (`SHA-256 = a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`, `fw_checksums = 92363606 / 12b29d01`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Summary (`R57..R59` = `240` Cumulative Windows)

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S565A-R57`** | `PB-050 v2` (`3000 ms` + `nf_cal=60s`) vs `PB-050 v1` (`4000 ms` + `nf_cal=120s` + `pktlog=0x0`) | `64.949 Mbps` / `26.099 ms` / `66.424 ms` | `62.056 Mbps` / **`16.933 ms`** (`-35.12%`) / **`47.165 ms`** (`-28.99%`) | **`+5.04%`** | **`PROMOTE_ARM_B`** (AP `softirq` drops `32.41% -> 26.95%`, VoIP jitter `2.031 -> 1.927 ms`) |
| **`S565A-R58`** | `tcp_pacing_ca_ratio=120 / ss=200` vs `110 / 150` (`16` streams) | `61.411 Mbps` / `19.302 ms` / `64.857 ms` | `64.212 Mbps` (`+4.56%`) / `27.658 ms` / `96.952 ms` | `-22.57%` | `RETAIN_ARM_A` (`120/200` prevents `p50`/`p95` inflation under 16-stream burst) |
| **`S565A-R59`** | Uniform AQL `1500/2000` vs Differentiated Per-AC AQL (`VO=500/1000, VI=1000/1500, BE=1500/2000, BK=1000/1500`) | `64.514 Mbps` / `23.044 ms` / `44.525 ms` | `63.034 Mbps` / **`19.455 ms`** (`-15.57%`) / `57.291 ms` | `-6.14%` | `RETAIN_ARM_A` (Arm B lowers `p50` RTT `-15.57%`) |

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage565a_live_wa_pb050_v2_and_pacing_r57_59.json`](../artifacts/autoresearch/stage565a_live_wa_pb050_v2_and_pacing_r57_59.json)
- Runner: [`run_stage565a_live_wa_pb050_v2_and_pacing_r57_59.py`](../tools/autoresearch/run_stage565a_live_wa_pb050_v2_and_pacing_r57_59.py)
- Test Suite: [`test_stage565a.py`](../tests/test_stage565a.py)
