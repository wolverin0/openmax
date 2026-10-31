<!-- doc-head: STAGE296A_XC_2XC_XM_24WINDOW_SCORECARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 296A — Cumulative 6-Round (`24-Window`) Multi-Radio Bench Scorecard (`XC` `.198`, `2XC` `.253`, `XM` `198.18.0.50`)

## 1. Scope & Methodology
Stage 296A compiles the cumulative 6-campaign (`24` champion counterbalanced `A1 -> B1 -> A2 -> B2` windows, `72` total physical windows per radio) live bench scorecard across:
- **`XC` (`198.18.0.64` `Rocket Prism 5AC Gen2` `XC.v8.7.25`)**: Stages `151A`, `182A`, `200A`, `215A`, `269A`, `293A`.
- **`2XC` (`198.18.0.65` `Rocket 2AC Prism` `2XC.v8.7.11`)**: Stages `151A`, `182A`, `200A`, `215A`, `270A`, `294A`.
- **`XM` (`198.18.0.50` `NanoStation` `XM.v6.1.12` 32 MB RAM)**: Stages `152A`, `183A`, `201A`, `216A`, `271A`, `295A`.

## 2. Multi-Radio `24-Window` Scorecard Summary (`CONFIRMED`)
| Radio Family | Mgmt / LAN IP | Firmware & RAM | Campaigns / Champion Windows | Cumulative Sub-Rounds / Windows | Safety Invariant |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `XC` (5 GHz AirPrism) | `198.18.0.64` | `XC.v8.7.25` (`128 MB`) | `6` rounds (`24` windows) | `18` sub-rounds (`72` windows) | `0` flash writes |
| `2XC` (2.4 GHz AirPrism) | `198.18.0.65` | `2XC.v8.7.11` (`128 MB`) | `6` rounds (`24` windows) | `18` sub-rounds (`72` windows) | `0` flash writes |
| `XM` (M5 32 MB SDRAM) | `198.18.0.50` | `XM.v6.1.12` (`32 MB`) | `6` rounds (`24` windows) | `18` sub-rounds (`72` windows) | `0` flash writes |

## 3. Hard Safety Invariants (`CONFIRMED`)
- `touched_241_or_242 = False`
- `touched_20_or_250 = False`
- `touched_production_guarida = False`
- `flash_writes = 0`

## 4. Verification Artifacts
- Verifier: [`tools/verify/verify_stage296a_xc_2xc_xm_24window_scorecard.py`](../tools/verify/verify_stage296a_xc_2xc_xm_24window_scorecard.py)
- Receipt: [`artifacts/autoresearch/stage296a_xc_2xc_xm_24window_scorecard.json`](../artifacts/autoresearch/stage296a_xc_2xc_xm_24window_scorecard.json)
- Dedicated Pytest: [`tests/test_stage296a_xc_2xc_xm_24window_scorecard.py`](../tests/test_stage296a_xc_2xc_xm_24window_scorecard.py)
