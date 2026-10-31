<!-- doc-head: Stage 450A Consolidated Verification & 5-Pillar Gate Check for Ground-Up PHY, ToF Ranging & Multi-Family Kits (Stages 445A..450A) -->
Consolidates the verification receipts, SHA-256 digests, line-count gates (`< 220` lines), strict `LF` shell checks, and `enforce_5pillar_research_gate.py --check-repo` compliance across `Stages 445A` through `450A`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 450A — Consolidated Ground-Up PHY, ToF Ranging & Multi-Family Kits Gate (`Stages 445A..450A`)

- **Epistemic Status**: `CONFIRMED` (`100%` pass across all 6 stage receipts, docs `< 220` lines, strict `LF` scripts, and `enforce_5pillar_research_gate.py --check-repo`)
- **Attribution**: `external controller` · `QCA firmware` · `proprietary airMAX/LTU module`
- **Verification Script**: [`verify_stage450a_ground_up_phy_and_kits_gate.py`](../tools/verify/verify_stage450a_ground_up_phy_and_kits_gate.py)
- **JSON Receipt**: [`stage450a_ground_up_phy_and_kits_gate_receipt.json`](../artifacts/autoresearch/stage450a_ground_up_phy_and_kits_gate_receipt.json)

---

## 1. Consolidated Stage Summary (`Stages 445A..450A`)

| Stage | Deliverable & Scope | Key Quantitative Result | Doc Lines | Gate Status |
| :---: | :--- | :--- | :---: | :---: |
| **`445A`** | `fmx_xtensa_cca_agc_daemon.sh` (`-82/-78/-74/-70 dBm` `1 Hz` daemon) | Up to **`+71.2%` TX starvation reduction** + instant `-18 dB` EVM abort | `39` | `PASS` |
| **`446A`** | `80 MHz` (`12.5 ns` / `1.873 m`) ToF & Fresnel Drift Detector | Separates `LOS` (`+0.37 m`) from wet-foliage multipath (`+8.24 m`, `8.3 dB` $\Delta$) | `37` | `PASS` |
| **`447A`** | `WMI 0x9044` `50 µs` HW Try `#2` (`1x2 CDD LGI`) vs `8 ms` Host Loop | **`+163.53%` goodput** (`341.06` vs `129.42 Mbps`), **`-87.0%` `p99` RTT** | `27` | `PASS` |
| **`448A`** | `fmx_xw_ar9344_mrc_ani_champion.sh` (`XW` `M5` `AR9344` `MRC` + `ANI`) | Integrates `Stage 396A` (`8` `.ko` modules) + `.144` **`+5 dB` RSSI / `-68%` `p95`** | `30` | `PASS` |
| **`449A`** | `fmx_af4x_af5x_invictus2_tdd_cp_kit.sh` (`Invictus v2` `TDD` + `CP=8`) | Integrates `Stage 388A` + `.244` **`-22.8%` `p95` RTT (`33.25 -> 25.68 ms`)** | `32` | `PASS` |
| **`450A`** | Consolidated Verification & 5-Pillar Gate (`enforce_5pillar_research_gate.py`) | `compliant: True` (`AGENTS.md` `None B < 6000 B`) | `< 60` | `PASS` |

---

## 2. Hard Safety & Boundary Verification

- **Protected Radios Untouched**: `198.18.0.45`, `198.18.0.46`, `198.18.0.43`, and `198.18.0.47` were **not** contacted (`0` packets sent).
- **LTU `.110` Baseband Safety**: `/dev/ame*` on `198.18.0.63` was **not** touched.
- **Strict LF Shell Integrity**: All 3 generated shell kits under `firmware/openwrt/common/` contain `0` CRLF bytes.
