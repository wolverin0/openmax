<!-- doc-head: STAGE507A_LIVE_WA_PB050_RC_PROBE_DAMPEN_AND_SLOT_R50_52.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 507A — Live WA `PB-050` `SGMT` `Seg[2]` Rate-Control Probe Dampening & Slot/Socket Bounding (`R50..R52` = `212` Windows)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware` (`firmware-2.bin` `SGMT` `Seg[2]` `.data` `@ 0x0040c140` + `Seg[1]` `.rodata` + `Seg[3]` `.text`), `ath10k`, `mac80211`, `Linux` (`net/ipv4/tcp_output.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes (`RAM-only` bind-mount `/tmp/firmware-2-pb050.bin` with `45s` rollback watchdog).

---

## 1. Live `PB-050` `SGMT` `Seg[2]` `.data` Firmware Patch Verification (`AP .20` & `CPE .250`)

Both `AP .20` (`LiteBeam 5AC Gen2`) and `CPE .250` (`PowerBeam 5AC Gen2`) booted `/tmp/firmware-2-pb050.bin` (`204,796 B`, `SHA-256 = a49160ff008390a34e43145bc56f6b8d047f8e02433aff20f965b6f2874ef52f`) via volatile RAM bind-mount and associated cleanly over 5 GHz 4-address WDS:

| Field | Verified Value (`AP .20` & `CPE .250`) |
| :--- | :--- |
| **`firmware-N.bin` CRC32** | `92363606` (Stock `firmware-2.bin`: `dd0cd60a`, `PB-040`: `bc55d20e`) |
| **`athwlan` payload CRC32** | `12b29d01` (Stock `firmware-2.bin`: `a6398d0b`, `PB-040`: `92ba3ae2`) |
| **`otp` payload CRC32** | `4c4fd0bc` (Unmodified) |
| **`PB-050` `Seg[2]` `.data` Patch** | `vaddr = 0x0040c140` (`file_off = 0x3b1d`, `.lit4` `0x00980754`): `0x07d0` (`2000 ms`) $\rightarrow$ `0x0fa0` (`4000 ms`) |
| **`PB-040` `Seg[3]` `.text` Patch** | `vaddr = 0x009b7584` (`file_off = 0x31b0c`): `0x00029e00` `BB_timing_controls_1` `0x13721320 -> 0x13761320` |

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Summary (`R50..R52`)

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S507A-R50`** | `PB-050` `Seg[2]` RC Probe `4000 ms` + `nf_cal_period=120s` vs `30s` baseline | `68.865 Mbps` / `23.437 ms` / `49.278 ms` | `64.620 Mbps` / `22.041 ms` (`-5.96%`) / `44.094 ms` (`-10.52%`) | `-5.45%` | `RETAIN_ARM_A` (`PB-050` lowers `p50`/`p95` RTT & VoIP jitter `2.291 -> 2.219 ms`) |
| **`S507A-R51`** | `pktlog=0x0` + `fw_stats` + `distance=1200 m / cov=3` vs `150 m / cov=0` (`16` streams) | `71.391 Mbps` / `14.706 ms` / `66.678 ms` | `73.972 Mbps` (`+3.62%`) / `22.386 ms` / `73.654 ms` | `-6.29%` | `RETAIN_ARM_A` (`1200 m / cov=3` lowers `p50` RTT under 16-stream burst) |
| **`S507A-R52`** | `tcp_notsent_lowat=131072` vs `16384` (`tcp_early_retrans=3`) | `62.034 Mbps` / `40.617 ms` / `128.314 ms` | **`68.818 Mbps`** (`+10.94%`) / **`22.462 ms`** (`-44.70%`) / **`67.017 ms`** (`-47.77%`) | **`+112.91%`** | **`PROMOTE_ARM_B`** |

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.json`](../artifacts/autoresearch/stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.json)
- Benchmark Runner: [`run_stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.py`](../tools/benchmarks/run_stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.py)
- Test Suite: [`test_stage507a.py`](../tests/test_stage507a.py)
