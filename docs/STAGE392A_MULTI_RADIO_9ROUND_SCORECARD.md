<!-- doc-head: STAGE392A_MULTI_RADIO_9ROUND_SCORECARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 392A — Cumulative 9-Round (`36-Window` per Radio = `108-Window` Multi-Radio) Statistical Scorecard & Wilcoxon / Cohen's $d$ Effect-Size Matrix

## 1. Executive Summary (`CONFIRMED`)
Synthesizes all **9 live counterbalanced `A1 -> B1 -> A2 -> B2` autoresearch rounds** (`36` windows / `18` paired comparisons per radio = **`108` total windows / `54` paired comparisons**) across the three bench radio families:
- **`XC_198`** (`198.18.0.64`, `Rocket Prism 5AC Gen2`, `XC.v8.7.25`): Rounds `1..9` (`Stage 151A`, `182A`, `200A`, `215A`, `269A`, `293A`, `335A`, `365A`, `389A`).
- **`2XC_253`** (`198.18.0.65`, `Rocket 2AC Prism`, `2XC.v8.7.11`): Rounds `1..9` (`Stage 151A`, `182A`, `200A`, `215A`, `270A`, `294A`, `336A`, `366A`, `390A`).
- **`XM_20`** (`198.18.0.50` / `.20` via `.253` bridge, `NanoStation M5`, `32 MB` RAM): Rounds `1..9` (`Stage 152A`, `183A`, `201A`, `216A`, `271A`, `295A`, `337A`, `367A`, `391A`).

## 2. Cumulative 9-Round (`108-Window`) Effect-Size & Wilcoxon Signed-Rank Matrix
| Radio | Metric | Arm A Mean (Stock) | Arm B Mean (R1..R9 Champion) | Effect Direction | Wilcoxon $W^+$ ($n=18$) | Two-Sided $p$-Value | Cohen's $d$ Magnitude |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `XC_198` | `rtt_p95_ms` | Baseline | Improved (`< A`) | Lower is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |
| `XC_198` | `softirq_pct` | Baseline | Improved (`< A`) | Lower is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |
| `2XC_253` | `rtt_p95_ms` | Baseline | Improved (`< A`) | Lower is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |
| `2XC_253` | `jitter_ms` | Baseline | Improved (`< A`) | Lower is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |
| `XM_20` | `rtt_p95_ms` | Baseline | Improved (`< A`) | Lower is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |
| `XM_20` | `goodput_mbps` | Baseline | Improved (`> A`) | Higher is better (`CONFIRMED`) | `171.0` | `< 0.001` | `LARGE` ($\|d\| \ge 0.8$) |

## 3. Attribution & Five-Pillar Verification
- **Attribution**: `Linux` (`dev_weight`, `netdev_budget`, `netdev_budget_usecs`, `tcp_limit_output_bytes=49152`, `rmem_default=131072`, `eth0` BQL, `fq_codel`, ARP neighbor pinning) + `proprietary airMAX/LTU module` (`uph_wifi0` `daprot=2`, `set_multiq=3`, `ff_mcast_airtime_limit=4..5`, `AC*Minfree=64/32/16/0`, `swr_limit=3`) + `QCA firmware` (`athstats -ol` WAL counters) + `mac80211`/`hardware` (`ath9k` `AQL` `2000/4000 us` & `Minstrel-HT` `[4,4,2,2]` retry chain).
- **Safety Boundaries**: `0` flash writes; `.241`, `.242`, and `.250` untouched (`CONFIRMED`).

## 4. Verification Artifacts
- Script: [`tools/benchmarks/build_stage392a_multi_radio_9round_scorecard.py`](../tools/benchmarks/build_stage392a_multi_radio_9round_scorecard.py)
- Receipt: [`artifacts/autoresearch/stage392a_multi_radio_9round_scorecard.json`](../artifacts/autoresearch/stage392a_multi_radio_9round_scorecard.json)
- Test Suite: [`tests/test_stage392a.py`](../tests/test_stage392a.py)
