<!-- doc-head: STAGE658A_GUARIDA_32CPE_PB060_VOIP_IPTV_BULK_SIM.md preserved document content -->
<!-- /doc-head -->



# Stage 658A — SimPy Simulation of Guarida (`3` Panels / `32` CPEs) under `PB-040` + `PB-050` + `PB-060`

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-658A`
- **Simulator**: `SimPy` PriorityResource Discrete-Event Engine (`seed=6580..6600`).
- **Topology (`3` Panels / `32` CPEs)**:
  - **`Panel1-Guarida` (`.84`)**: `4` CPEs (`3` active + `1` pending)
  - **`Panel2-Guarida` (`.82`)**: `22` CPEs
  - **`Panel3-Guarida` (`.83`)**: `6` CPEs
- **Key Result**: Under Peak-Hour Triple-Play (`VoIP EF` + `1316B IPTV CS4` + `Bulk TCP BE`), the triple Xtensa patch stack (`PB-040 + PB-050 + PB-060` with `1504 us` CABQ/TXOP cap) eliminates IPTV `1316B` packet drops (`0.0%` loss across all 3 panels) and delivers **`299.8 Mbps`** aggregate tower goodput.

## 2. Triple-Stack (`PB-040` + `PB-050` + `PB-060`) Performance by Panel
| Panel | CPEs | Mode | Aggregate Goodput (`Mbps`) | IPTV `1316B` Loss (`%`) |
| :--- | :--- | :--- | :--- | :--- |
| `Panel1-Guarida` (`.84`) | `4` | `TRIPLE_PB040_PB050_PB060` | **`106.60 Mbps`** | **`0.0%`** |
| `Panel2-Guarida` (`.82`) | `22` | `TRIPLE_PB040_PB050_PB060` | **`92.40 Mbps`** | **`0.0%`** |
| `Panel3-Guarida` (`.83`) | `6` | `TRIPLE_PB040_PB050_PB060` | **`100.80 Mbps`** | **`0.0%`** |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.py`](../tools/sim/run_stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.py)
- **Receipt**: [`artifacts/autoresearch/stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.json`](../artifacts/autoresearch/stage658a_guarida_32cpe_pb060_voip_iptv_bulk_sim.json)
- **Pytest**: [`tests/test_stage658a.py`](../tests/test_stage658a.py)
