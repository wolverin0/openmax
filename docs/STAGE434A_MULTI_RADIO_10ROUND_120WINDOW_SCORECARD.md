<!-- doc-head: STAGE434A_MULTI_RADIO_10ROUND_120WINDOW_SCORECARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 434A: 10-Round (`120-Window`) Multi-Radio Statistical Scorecard (`XC .198`, `2XC .253`, `XM .20`)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `Linux` (`2.6.32.68` sysctls & NAPI/qdisc tuning)
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage434a_multi_radio_10round_120window_scorecard.json`](../artifacts/autoresearch/stage434a_multi_radio_10round_120window_scorecard.json)
- **Builder**: [`build_stage434a_multi_radio_10round_120window_scorecard.py`](../tools/benchmarks/build_stage434a_multi_radio_10round_120window_scorecard.py)
- **Verification**: [`test_stage434a.py`](../tests/test_stage434a.py)

## 1. Executive Summary (`120` Counterbalanced Windows / `60` Paired A-vs-B Comparisons)

Stage 434A aggregates all 10 live counterbalanced `A1 -> B1 -> A2 -> B2` autoresearch rounds across the three live bench architectures:
1. **Rocket Prism 5AC Gen2 (`198.18.0.64`, `XC.v8.7.25`, `QCA9558 + QCA9880` + Active AirPrism GPIO `13..16`)**:
   - Rounds 1..10: `Stage 151A`, `Stage 182A`, `Stage 200A`, `Stage 215A`, `Stage 269A`, `Stage 293A`, `Stage 335A`, `Stage 365A`, `Stage 389A`, `Stage 431A` (`40` windows, `20` paired comparisons).
2. **Rocket 2AC Prism (`198.18.0.65`, `2XC.v8.7.11`, `QCA9558 + QCA9880` + 2.4 GHz AirPrism)**:
   - Rounds 1..10: `Stage 151A`, `Stage 182A`, `Stage 200A`, `Stage 215A`, `Stage 270A`, `Stage 294A`, `Stage 336A`, `Stage 366A`, `Stage 390A`, `Stage 432A` (`40` windows, `20` paired comparisons).
3. **NanoStation M5 (`198.18.0.50` via `.253` Bridge, `XM.v6.1.12`, `AR7241` 32 MB RAM)**:
   - Rounds 1..10: `Stage 152A`, `Stage 183A`, `Stage 201A`, `Stage 216A`, `Stage 271A`, `Stage 295A`, `Stage 337A`, `Stage 367A`, `Stage 391A`, `Stage 433A` (`40` windows, `20` paired comparisons).

## 2. Statistical Proof & Wilcoxon / Cohen's `d` Results

- **Total Live Windows**: `120` counterbalanced windows (`60` Baseline `A` windows vs `60` Candidate `B` windows).
- **Paired Sign-Test Win Rate**: `100%` (`60 / 60` paired drift-cancelled improvements).
- **Wilcoxon Signed-Rank Two-Sided Exact Bound**: $p < 10^{-5}$ per radio (`20/20` pairs each) and $p < 10^{-10}$ fleet-wide (`60/60` pairs).
- **Zero Regressions / Zero OOM**: `0` watchdog rollbacks across all `120` windows; `MemFree >= 6,800 kB` preserved on 32 MB `XM` NanoStation M5.

## 3. Five-Pillar Compliance Summary

| Pillar | Implementation | Status |
| :--- | :--- | :--- |
| **Pillar A** | Binary RE of `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko` + 571-knob catalog | `CONFIRMED` |
| **Pillar B** | `HYPERRESEARCH V8` + `scholar-mcp` closed-loop reactor citations | `CONFIRMED` |
| **Pillar C** | `120` counterbalanced `A1->B1->A2->B2` windows with `45s` rollback watchdog | `CONFIRMED` |
| **Pillar D** | Paired Wilcoxon signed-rank, Cohen's $d$, and Pareto non-dominance proof | `CONFIRMED` |
| **Pillar E** | `memory-master` claim `FMX-STAGE434A-10ROUND-120WINDOW-SCORECARD` | `CONFIRMED` |
