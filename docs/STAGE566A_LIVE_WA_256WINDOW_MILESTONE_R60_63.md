<!-- doc-head: STAGE566A_LIVE_WA_256WINDOW_MILESTONE_R60_63.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 566A — Live WA `256`-Window Milestone (`R60..R63`): Prequeue/Autocork, DFS Chirp Immunity, RACK-TLP & `WA Champion v10`

- **Claim Classification**: `CONFIRMED`
- **Subsystem Attribution**: `QCA firmware` (`firmware-2.bin`), `ath10k`, `mac80211`, `Linux` (`net/core/dev.c`, `net/ipv4/tcp_recovery.c`), `hardware` (`AR9342` + `QCA9882`)
- **Safety Boundaries**: `198.18.0.45` and `198.18.0.46` untouched (`touched_241_or_242 = false`); `0` flash writes.

---

## 1. Executive Summary (`R60..R63` = `256` Cumulative Live Windows!)

`Stage 566A` completes rounds `R60..R63`, reaching **`63` counterbalanced rounds = `252` RF windows + `4` `Stage 162A` E2E windows = `256` cumulative live windows** (`276` including all 6 E2E rounds):

| Round | Hypothesis / Arm Comparison | Arm A Goodput / `p50` / `p95` | Arm B Goodput / `p50` / `p95` | Pareto $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`S566A-R60`** | `netdev_tstamp_prequeue=1, tcp_autocorking=1` vs `0 / 0` | `65.078 Mbps` / `23.960 ms` / `65.734 ms` | **`67.340 Mbps`** (`+3.48%`) / `27.071 ms` / **`58.834 ms`** (`-10.50%`) | **`+10.48%`** | **`PROMOTE_ARM_B`** (VoIP jitter `2.260 -> 2.052 ms`) |
| **`S566A-R61`** | `fmx_qca988x_dfs_chirp_immunity.sh` + `nf_cal=120s` + `0x00029e00` audit | `68.707 Mbps` / `15.840 ms` / `56.431 ms` | `65.023 Mbps` / `24.093 ms` / `53.913 ms` (`-4.46%`, VoIP jitter `2.663 -> 2.218 ms`) | `-4.05%` | `RETAIN_ARM_A` |
| **`S566A-R62`** | `tcp_recovery=0, tcp_thin_linear_timeouts=0` vs `1 / 1` (RACK-TLP) | `53.466 Mbps` / `16.174 ms` / `63.148 ms` | **`59.197 Mbps`** (`+10.72%`) / `17.974 ms` / **`53.011 ms`** (`-16.05%`) | **`+26.86%`** | **`PROMOTE_ARM_B`** (VoIP jitter `2.487 -> 1.596 ms`) |
| **`S566A-R63`** | **Stock `OpenWrt 24.10.4` vs `63`-Round (`256`-Window) `WA Champion v10`** | `50.204 Mbps` / `74.384 ms` / `177.632 ms` | **`57.259 Mbps`** (**`+14.05%`**) / **`13.422 ms`** (**`-81.96%`**) / **`66.567 ms`** (**`-62.53%`**) | **`+7461.18%`** | **`PROMOTE_ARM_B`** |

---

## 2. Key Findings (`S566A-R63` `256`-Window Head-to-Head)

1. **Goodput Gain**: `+14.05%` (`50.204 -> 57.259 Mbps`) under simultaneous bidirectional TCP + IPTV (`5 Mbps` `AF41`) + VoIP (`G.711` `EF`) + Gaming UDP.
2. **Latency Collapse**: Under-load `p50` RTT drops **`-81.96%`** (`74.384 -> 13.422 ms`) and `p95` RTT drops **`-62.53%`** (`177.632 -> 66.567 ms`).
3. **IPTV Jitter**: Drops from `2.159 ms` (Stock) to `1.207 ms` (`WA Champion v10`, `0%` packet loss).

---

## 3. Artifacts & Verification

- JSON Receipt: [`stage566a_live_wa_256window_milestone_r60_63.json`](../artifacts/autoresearch/stage566a_live_wa_256window_milestone_r60_63.json)
- Runner: [`run_stage566a_live_wa_256window_milestone_r60_63.py`](../tools/autoresearch/run_stage566a_live_wa_256window_milestone_r60_63.py)
- Test Suite: [`test_stage566a.py`](../tests/test_stage566a.py)
