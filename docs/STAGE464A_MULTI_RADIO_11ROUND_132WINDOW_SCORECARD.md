<!-- doc-head: STAGE464A_MULTI_RADIO_11ROUND_132WINDOW_SCORECARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 464A: 11-Round (`132-Window`) Multi-Radio Statistical Scorecard (`XC .198`, `2XC .253`, `XM .20`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `Linux` (`2.6.32.68` sysctls & NAPI/qdisc tuning)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage464a_multi_radio_11round_132window_scorecard.json`](../artifacts/autoresearch/stage464a_multi_radio_11round_132window_scorecard.json)
- **Builder**: [`build_stage464a_multi_radio_11round_132window_scorecard.py`](../tools/benchmarks/build_stage464a_multi_radio_11round_132window_scorecard.py)
- **Verification**: [`test_stage464a.py`](../tests/test_stage464a.py)

## 1. Executive Summary (`132` Counterbalanced Windows / `66` Paired A-vs-B Comparisons)

Stage 464A aggregates all 11 live counterbalanced `A1 -> B1 -> A2 -> B2` autoresearch rounds across the three live bench architectures:
1. **Rocket Prism 5AC Gen2 (`198.18.0.64`, `XC.v8.7.25`, `QCA9558 + QCA9880` + Active AirPrism GPIO `13..16`)**:
   - Rounds 1..11: `Stage 151A`, `Stage 182A`, `Stage 200A`, `Stage 215A`, `Stage 269A`, `Stage 293A`, `Stage 335A`, `Stage 365A`, `Stage 389A`, `Stage 431A`, `Stage 461A` (`44` windows, `22` paired comparisons).
2. **Rocket 2AC Prism (`198.18.0.65`, `2XC.v8.7.11`, `QCA9558 + QCA9880` + 2.4 GHz AirPrism)**:
   - Rounds 1..11: `Stage 151A`, `Stage 182A`, `Stage 200A`, `Stage 215A`, `Stage 270A`, `Stage 294A`, `Stage 336A`, `Stage 366A`, `Stage 390A`, `Stage 432A`, `Stage 462A` (`44` windows, `22` paired comparisons).
3. **NanoStation M5 (`198.18.0.50` via `.253` Bridge, `XM.v6.1.12`, `AR7241` 32 MB RAM)**:
   - Rounds 1..11: `Stage 152A`, `Stage 183A`, `Stage 201A`, `Stage 216A`, `Stage 271A`, `Stage 295A`, `Stage 337A`, `Stage 367A`, `Stage 391A`, `Stage 433A`, `Stage 463A` (`44` windows, `22` paired comparisons).

## 2. Statistical Proof & Wilcoxon / Cohen's `d` Results

- **Total Live Windows**: `132` counterbalanced windows (`66` Baseline `A` windows vs `66` Candidate `B` windows).
- **Paired Sign-Test Win Rate**: `100%` (`66 / 66` paired drift-cancelled improvements).
- **Wilcoxon Signed-Rank Two-Sided Exact Bound**: $p < 5 \times 10^{-6}$ per radio (`22/22` pairs each) and $p < 10^{-11}$ fleet-wide (`66/66` pairs).
- **Zero Regressions / Zero OOM**: `0` watchdog rollbacks across all `132` windows; `MemFree >= 6,800 kB` preserved on 32 MB `XM` NanoStation M5.

## 3. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`, `ath9k.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-33`).
- **Pillar C**: `132` counterbalanced `A1->B1->A2->B2` windows with `45s` rollback watchdog.
- **Pillar D**: Paired Wilcoxon signed-rank, Cohen's $d$, and Pareto non-dominance proof.
- **Pillar E**: `memory-master` claim `MM-STAGE464A-132WINDOW-11ROUND-MULTIRADIO-SCORECARD`.
