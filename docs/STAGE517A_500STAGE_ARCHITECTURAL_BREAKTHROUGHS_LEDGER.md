<!-- doc-head: Stage 517A Quantitative Ledger of All Ground-Up Architectural Breakthroughs Through Stage 517A -->
Curates the definitive 500+ Stage quantitative ledger of FuturaMAX's 5 First-Principles Pillars and cross-fleet live hardware validation (`820` counterbalanced live bench windows across `WA`, `XC`, `2XC`, `XW/XM`, `LTU`, and `AF-4X`).
<!-- /doc-head -->

# Stage 517A — 500-Stage Quantitative Ledger of Ground-Up Architectural Breakthroughs

- **Epistemic Status**: `CONFIRMED` (`845` JSON receipts, `630` technical docs, `820` cumulative live counterbalanced hardware windows)
- **Attribution**: `QCA firmware` · `proprietary airMAX/LTU module` · `Linux` · `mac80211` · `ath10k` · `hardware` · `external controller`
- **Generator**: [`build_stage517a_500stage_architectural_breakthroughs_ledger.py`](../tools/verify/build_stage517a_500stage_architectural_breakthroughs_ledger.py)
- **JSON Receipt**: [`stage517a_500stage_architectural_breakthroughs_ledger.json`](../artifacts/autoresearch/stage517a_500stage_architectural_breakthroughs_ledger.json)

---

## 1. Master Quantitative Breakthroughs Table (`FMX-BRK-01` .. `FMX-BRK-06`)

| ID | Pillar / Domain | Core First-Principles Mechanism | Verified Quantitative Proof |
| :---: | :--- | :--- | :--- |
| **`FMX-BRK-01`** | **Pillar 1 (`Xtensa` RAM & `CCA` Stepping)** | Unsigned `SGMT` `BMI_LZ_DATA` RAM patcher + `1 Hz` `cca_thresh62` (`-82..-70 dBm`) + `5/10 MHz` PLL + `120 s` DFS CAC | **`+71.2%` TX starvation cut**, `+3/+6 dB` noise floor in `10/5 MHz`, `0` Flash writes |
| **`FMX-BRK-02`** | **Pillar 2 (`16-Pilot EVM`, `1.87 m` ToF & `VHT40`)** | `rx_ppdu_end_qca988x` (`84 B`) `80 MHz` (`12.5 ns`) ToF + Fraunhofer (`< 6.2 m`) switch + STA `VHT80` cap unlock | **`1.873 m` ToF precision**; `.241<->.242` **`VHT40` `24.83 Mbps` (`0%` loss)**; VoIP loss **`13% -> 0%` (`-82.9%` `p50`)** |
| **`FMX-BRK-03`** | **Pillar 3 (`WMI 0x9044` `50 µs` Retry & `32` Hooks)** | `WMI_PEER_RATE_RETRY_SCHED_CMDID` (`0x9044`) hardware Try `#2` (`2x2 SGI -> 1x2 CDD LGI` in `50 µs`) + `0x9064/0x9065` | **`160x` faster turnaround (`50 µs` vs `8 ms`)**, **`+163.53%` fade goodput**, **`-87.0%` `p99` RTT** |
| **`FMX-BRK-04`** | **Pillar 4 (`LTU` `SQ`, `AD9361` & `DCXO` `12X`)** | Native `Short-Queue (0 < ptmp_max_cpe <= 16)`, `AD9361` Split-Freq (`TX != RX`), and `bbp_rf_dcxo_is_sync_by_gps` | **`144` live LTU `.110` windows (`0` `/dev/ame*` crashes)**; **`+50.83%` goodput (`615.39 Mbps`)** & `100%` `12X` dwell |
| **`FMX-BRK-05`** | **Pillar 5 (`< 48 KB` C Worker & `Guarida v4`)** | `controller/fmx_micro_worker.c` + `64`-subcarrier EVM notch radiography + `Panel2` `cbp_dur=900 µs` + `Panel3` MCS 2 cure | **`+46.36 Mbps` (`+42.5%`) Guarida `.82+.83` goodput**, **`-70.14 ms` `p99`**, **`+82.61%` `32`-CPE goodput**, `0.0%` false alerts |
| **`FMX-BRK-06`** | **Cross-Fleet Live Hardware Validation** | Counterbalanced `A1 -> B1 -> A2 -> B2` harness across `WA`, `XC`, `2XC`, `XW/XM`, `LTU`, and `AF-4X` | **`820` live hardware windows**; `AF-4X` `.244` **`-22.8%` `p95` RTT**; `PBM5` `.144` **`+5 dB` RSSI / `-68%` `p95` RTT** |

---

## 2. Live Bench Hardware Window Census (`820` Counterbalanced Windows)

- **`WA` (`LAP-120 .20 <-> Loco5AC .250` & `PBE-5AC-Gen2 .241 <-> .242`)**: `196` windows (`0` unrecoverable states)
- **`LTU-Lite` (`.110`)**: `12` rounds = `144` windows (`0` `/dev/ame*` touches)
- **`XC` (`Rocket 5AC Prism .198`) & `2XC` (`Rocket 2AC Prism .253`) & `XM/XW` (`.20/.144`)**: `144` windows each (`432` total)
- **`airFiber AF-4X` (`Invictus v2 .244`)**: `12` rounds = `48` windows
