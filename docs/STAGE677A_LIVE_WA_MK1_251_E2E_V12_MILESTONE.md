<!-- doc-head: STAGE677A_LIVE_WA_MK1_251_E2E_V12_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 677A — Live End-to-End `.250 <-> .20 <-> Boca 7 MikroTik MK1-251` `WA Champion v12` Stress (`S677A-E2E-R8` = `316` Windows)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` across the full wired+wireless path (`CPE 198.18.0.47 <-> 5 GHz 4-addr WDS <-> AP 198.18.0.43 <-> Switch <-> Boca 7 MikroTik MK1-251 198.18.0.48`)
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`).

## 1. Executive Summary (`S677A-E2E-R8` — `316` Cumulative Live Windows)
In `Stage 677A` ([`run_stage677a_live_wa_mk1_251_e2e_v12_milestone.py`](../tools/bench/run_stage677a_live_wa_mk1_251_e2e_v12_milestone.py)), we executed the 8th full End-to-End (`E2E-R8`) counterbalanced `A1 -> B1 -> A2 -> B2` stress benchmark through `MikroTik MK1-251` (`198.18.0.48`), bringing cumulative live `WA` windows to **`316` (`340` across all 8 E2E rounds)**:

| Window | Arm | Goodput (`Mbps`) | `TCP DL` / `UL` (`Mbps`) | `RF` & `MK1-251` `p50` RTT (`ms`) | `p95` RTT (`ms`) | `VoIP` Jitter (`ms`) / Loss |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`A1`** | Stock `OpenWrt 24.10.4` | `55.279 Mbps` | `25.811` / `24.453` | `78.867 ms` | `194.728 ms` | `3.918 ms` / `0.0%` |
| **`B1`** | **`WA Champion v12`** | **`70.974 Mbps`** | `35.146` / `30.768` | **`9.884 ms`** | **`51.248 ms`** | **`2.905 ms` / `0.0%`** |
| **`A2`** | Stock `OpenWrt 24.10.4` | `29.863 Mbps` | `15.421` / `9.452` | `112.752 ms` | `179.658 ms` | `3.226 ms` / `0.0%` |
| **`B2`** | **`WA Champion v12`** | **`68.881 Mbps`** | `37.218` / `26.621` | **`16.227 ms`** | **`69.328 ms`** | **`3.153 ms` / `0.0%`** |
| **Mean** | **`WA Champion v12` vs Stock** | **`69.928` vs `42.571 Mbps` (`+64.26%`)** | — | **`13.056` vs `95.809 ms` (`-86.37%`)** | **`60.288` vs `187.193 ms` (`-67.79%`)** | **`3.029` vs `3.572 ms`** |

## 2. Key End-to-End Findings
- **`+64.26%` End-to-End Goodput & `-86.37%` `p50` RTT Reduction**: Across `CPE .250 <-> AP .20 <-> Switch <-> Boca 7 MK1-251`, `WA Champion v12` delivered **`69.928 Mbps` mean (`70.974 Mbps` in `B1`)** and **`13.056 ms` `p50` RTT (`9.884 ms` in `B1`)** vs `42.571 Mbps` and `95.809 ms` on Stock `OpenWrt 24.10.4` (`Pareto +459.45%`, `PROMOTE_ARM_B`).

## 3. Artifacts & Verification
- **Receipt**: [`stage677a_live_wa_mk1_251_e2e_v12_milestone.json`](../artifacts/autoresearch/stage677a_live_wa_mk1_251_e2e_v12_milestone.json)
- **Pytest**: [`tests/test_stage677a.py`](../tests/test_stage677a.py)
