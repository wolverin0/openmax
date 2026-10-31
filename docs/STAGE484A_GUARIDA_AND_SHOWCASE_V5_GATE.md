<!-- doc-head: Stage 484A Consolidated Verification & 5-Pillar Gate Check for Guarida Coexistence v3 & Public Showcase v5 (Stages 479A..484A) -->
Consolidates the verification receipts, SHA-256 digests, `< 220` line-count checks, strict `LF` shell checks, and `enforce_5pillar_research_gate.py --check-repo` compliance across `Stages 479A` through `484A`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 484A — Consolidated Guarida Coexistence v3 & Public Showcase v5 Gate (`Stages 479A..484A`)

- **Epistemic Status**: `CONFIRMED` (`100%` pass across all 6 stage receipts, docs `< 220` lines, strict `LF` scripts, and `enforce_5pillar_research_gate.py --check-repo`)
- **Attribution**: `external controller` · `proprietary airMAX/LTU module` · `QCA firmware` · `hardware`
- **Verifier**: [`verify_stage484a_guarida_and_showcase_v5_gate.py`](../tools/verify/verify_stage484a_guarida_and_showcase_v5_gate.py)
- **JSON Receipt**: [`stage484a_guarida_and_showcase_v5_gate_receipt.json`](../artifacts/autoresearch/stage484a_guarida_and_showcase_v5_gate_receipt.json)

---

## 1. Consolidated Stage Summary (`Stages 479A..484A`)

| Stage | Deliverable & Scope | Key Quantitative Result | Doc Lines | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **`479A`** | `rc.poststart_panel2_panel3_coexistence_v3.sh` (`Guarida` `.82`/`.83`) | `cbp_dur=900 µs`, `flags=6672` (`0` deferred lockouts), **`+46.36 Mbps` (`+42.5%`)**, **`-70.14 ms` `p99`** | `33` | `PASS` |
| **`480A`** | `rc.poststart_backbone_60_61_notch_rescue.sh` (`.60 <-> .61` Backbone) | Cures Subcarrier-51 `6.45 dB` Chain 0 notch (`shortgi=0`) + `230.7M` `ast_rxorn` (`netdev_budget=600`) | `32` | `PASS` |
| **`481A`** | Fraunhofer Near-Field (`< 6.15 m` for `400 mm` dish) vs Far-Field Switch | Reconciles `Stages 105A` & `425A–429A` (`VHT20` `MCS 3/2 NSS=1 LGI` `19.62 Mbps`, `0.0%` `1472B` loss) | `33` | `PASS` |
| **`482A`** | `32`-CPE Cooperative Edge Micro-Worker `SimPy` + `NSGA-II` Pareto | **`+82.61%` `32`-CPE goodput**, **`-81.05%` `p99` RTT**, `0.9457` Jain, **`0.0%` false-positive alerts** | `28` | `PASS` |
| **`483A`** | `fmx_public_tester_ground_up_showcase_v5.sh` (`All 5 Pillars`) | Hardware-auto-detecting v5 showcase across `WA`, `XC`, `XW`, `LTU`, and `Invictus v2` | `28` | `PASS` |
| **`484A`** | Consolidated Verification & 5-Pillar Gate (`enforce_5pillar_research_gate.py`) | `compliant: True` (`0` failures across entire repo) | `< 60` | `PASS` |

---

## 2. Hard Safety & Topology Verification

- **Protected Bench Radios Untouched**: `198.18.0.45`, `198.18.0.46`, `198.18.0.43`, and `198.18.0.47` were **not** contacted (`0` packets sent).
- **Guarida Backbone (`SG-01`) & LTU `.110`**: `0` production writes performed; `/dev/ame*` on `.110` untouched.
