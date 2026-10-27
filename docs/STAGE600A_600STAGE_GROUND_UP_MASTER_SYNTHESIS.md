<!-- doc-head: STAGE600A_600STAGE_GROUND_UP_MASTER_SYNTHESIS.md preserved document content -->
<!-- /doc-head -->



# Stage 600A — `600-Stage` Ground-Up Master Synthesis (`5` First-Principles Pillars & `8` Radio Families)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-600A` (**`600-Stage` Ground-Up Milestone**)
- **Radio Families Covered (`8`)**: `WA`, `XC`, `2WA`, `2XC`, `XW`, `XM`, `TI`, `AF-LTU`.
- **Total Counterbalanced Windows (`600`)**: `228` `WA` windows + `192` `Multi-Radio` windows (`Stage 597A`) + `180` `AF-LTU` windows.

## 2. Synthesis Across the 5 First-Principles Pillars
| Pillar | Core Breakthroughs Verified (`Stages 1..600A`) | Status |
| :--- | :--- | :--- |
| **I. Silicon & RF Physics** | Active AirPrism GPIO `13..16`, QCA `PAPRD=1` + `CLPC 1.5 dB` (`-34.9 dB` EVM), `AF-LTU` `super4096` + `DPD` (`78.4%` `12X`) | `CONFIRMED` |
| **II. Binary RE & Xtensa RAM** | Disjoint `PB-040` (`.text 0x009b7584`) + `PB-050` (`.data` RC dampening) `SGMT` patch; `571` knobs; `FMX-DISC-11` `daprot` vector | `CONFIRMED` |
| **III. Queueing & TCP Pacing** | `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `tcp_notsent_lowat=131072`, AQL `2000`, `CS4` `0.0%` IPTV loss | `CONFIRMED` |
| **IV. RF Observability & Guarida** | Guarida `.60-.61` `10 MHz` shift (`+7.99 dB` Chain 0 EVM, `+17.17 Mbps`); `Panel1-Guarida` (`.84`) `19.36h` `0`-disconnect soak | `CONFIRMED` |
| **V. Autoresearch Governance** | `600` counterbalanced `A1->B1->A2->B2` windows across `WA`/`Multi-Radio`/`LTU` with `45s`/`120s` watchdogs and `0` flash bricks | `CONFIRMED` |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage600a_600stage_ground_up_master_synthesis.py`](../tools/autoresearch/build_stage600a_600stage_ground_up_master_synthesis.py)
- **Receipt**: [`artifacts/autoresearch/stage600a_600stage_ground_up_master_synthesis.json`](../artifacts/autoresearch/stage600a_600stage_ground_up_master_synthesis.json)
