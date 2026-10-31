<!-- doc-head: STAGE508A_LIVE_WA_CCA_AGC_AND_ANI_IMMUNITY_R53_56.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 508A — Live WA CCA/AGC Daemon, BMISS/CSA Helper & `228`-Window Milestone (`R53..R56`)

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux` (`net/core/dev.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes.

---

## 1. Executive Summary (`R53..R56` = `228` Cumulative Live Windows!)

`Stage 508A` completes rounds `R53..R56`, reaching **`56` counterbalanced rounds = `224` RF windows + `4` `Stage 162A` E2E windows = `228` cumulative live windows** (`244` including all 5 E2E rounds):

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S508A-R53`** | `ani_enable=0` static vs `ani_enable=1` + `fmx_xtensa_cca_agc_daemon.sh` (`-82 dBm` step) | `61.047 Mbps` / `14.952 ms` / `45.303 ms` | `59.999 Mbps` / `16.233 ms` / `49.115 ms` (VoIP jitter `3.061 -> 2.873 ms`) | `-3.64%` | `RETAIN_ARM_A` |
| **`S508A-R54`** | `fmx_qca988x_bmiss_csa_helper.sh` (`Stage 503A`) + `dtim_period=2, beacon_int=100` | `61.248 Mbps` / `13.722 ms` / `53.716 ms` | **`66.445 Mbps`** (`+8.49%`) / **`12.915 ms`** (`-5.88%`) / `57.792 ms` | **`+10.24%`** | **`PROMOTE_ARM_B`** |
| **`S508A-R55`** | `tx_queue_len=1000` vs `tx_queue_len=256` on `br-lan`, `eth0`, `phy0-*` | `66.594 Mbps` / `11.237 ms` / `50.392 ms` | **`69.350 Mbps`** (`+4.14%`) / `14.923 ms` / **`45.770 ms`** (`-9.17%`) | **`+7.19%`** | **`PROMOTE_ARM_B`** |
| **`S508A-R56`** | **Stock `OpenWrt 24.10.4` vs `56`-Round (`228`-Window) `WA Champion v9`** | `56.540 Mbps` / `61.097 ms` / `196.901 ms` | **`65.992 Mbps`** (**`+16.72%`**) / **`22.850 ms`** (**`-62.60%`**) / **`91.302 ms`** (**`-53.63%`**) | **`+2161.02%`** | **`PROMOTE_ARM_B`** |

---

## 2. Key Findings (`S508A-R56` Head-to-Head)

1. **Goodput Gain**: `+16.72%` (`56.540 -> 65.992 Mbps`) under simultaneous bidirectional TCP + IPTV (`5 Mbps` `AF41`) + VoIP (`G.711` `EF`) + Gaming UDP.
2. **Latency Collapse**: Under-load `p50` RTT drops `-62.60%` (`61.097 -> 22.850 ms`) and `p95` RTT drops `-53.63%` (`196.901 -> 91.302 ms`).
3. **VoIP Jitter Reduction**: VoIP jitter drops `-47.32%` (`3.669 -> 1.933 ms`, `0%` packet loss).

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.json`](../artifacts/autoresearch/stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.json)
- Runner: [`run_stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.py`](../tools/benchmarks/run_stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.py)
- Test Suite: [`test_stage508a.py`](../tests/test_stage508a.py)
