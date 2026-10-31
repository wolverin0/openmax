<!-- doc-head: STAGE757A_LIVE_WA_MK1_251_E2E_V13_MILESTONE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 757A — Live End-to-End `.250 <-> .20 <-> Boca 7 MikroTik MK1-251` `WA Champion v13` Stress (`S757A-E2E-R9` = `344` / `368` Windows)

- **Status**: `CONFIRMED`
- **Attribution**: `QCA firmware` + `ath10k` + `mac80211` + `Linux` + `hardware`
- **Protocol**: Counterbalanced `A1 -> B1 -> A2 -> B2` across `CPE 198.18.0.47 <-> 5 GHz 4-addr WDS <-> AP 198.18.0.43 <-> Switch <-> Boca 7 MikroTik MK1-251 198.18.0.48`
- **Safety Boundaries**: `198.18.0.45` & `198.18.0.46` untouched (`touched_241_or_242 = false`).

## 1. Executive Summary (`S757A-E2E-R9` — `344` / `368` Cumulative Live Windows)
In `Stage 757A` ([`run_stage757a_live_wa_mk1_251_e2e_v13_milestone.py`](../tools/bench/run_stage757a_live_wa_mk1_251_e2e_v13_milestone.py)), we executed the 9th full End-to-End (`E2E-R9`) counterbalanced `A1 -> B1 -> A2 -> B2` stress benchmark through `MikroTik MK1-251` (`198.18.0.48`), reaching **`344` cumulative windows (`368` across all 9 E2E rounds)**:

| Window | Arm | Goodput (`Mbps`) | `TCP DL` / `UL` (`Mbps`) | `RF` & `MK1-251` `p50` RTT (`ms`) | `p95` RTT (`ms`) | `VoIP` Jitter (`ms`) / Loss |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`A1`** | Stock `OpenWrt 24.10.4` | `58.143 Mbps` | `26.730` / `26.387` | `93.496 ms` | `162.450 ms` | `3.863 ms` / `0.0%` |
| **`B1`** | **`WA Champion v13`** | **`64.408 Mbps`** | `36.310` / `23.040` | **`19.358 ms`** | **`75.214 ms`** | **`1.472 ms` / `0.0%`** |
| **`A2`** | Stock `OpenWrt 24.10.4` | `53.198 Mbps` | `25.120` / `23.031` | `73.815 ms` | `117.112 ms` | `3.413 ms` / `0.0%` |
| **`B2`** | **`WA Champion v13`** | **`67.607 Mbps`** | `38.940` / `23.620` | **`12.267 ms`** | **`77.760 ms`** | **`1.710 ms` / `0.0%`** |
| **Mean** | **`WA Champion v13` vs Stock** | **`66.007` vs `55.671 Mbps` (`+18.57%`)** | — | **`15.812` vs `83.655 ms` (`-81.10%`)** | **`76.487` vs `139.781 ms` (`-45.28%`)** | **`1.591` vs `3.638 ms` (`-56.27%`)** |

## 2. Key End-to-End Findings
- **`+18.57%` End-to-End Goodput, `-81.10%` `p50` RTT & `-56.27%` `VoIP` Jitter**: Across `CPE .250 <-> AP .20 <-> Switch <-> Boca 7 MK1-251`, `WA Champion v13` delivered **`66.007 Mbps` (`B2 = 67.607 Mbps`)**, **`15.812 ms` `p50` RTT (`B2 = 12.267 ms`)**, and **`1.591 ms` `VoIP` jitter** vs `55.671 Mbps`, `83.655 ms`, and `3.638 ms` on Stock `OpenWrt 24.10.4` (`Pareto +268.96%`, `PROMOTE_ARM_B`).

## 3. Artifacts & Verification
- **Receipt**: [`stage757a_live_wa_mk1_251_e2e_v13_milestone.json`](../artifacts/autoresearch/stage757a_live_wa_mk1_251_e2e_v13_milestone.json)
- **Pytest**: [`tests/test_stage757a.py`](../tests/test_stage757a.py)
