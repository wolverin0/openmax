from __future__ import annotations

from pathlib import Path

from tools.sim.run_stage76a_simpy_guarida_32cpe_3panel_simulator import (
    DEFAULT_OUTPUT_JSON,
    N_REPLICATIONS,
    WARMUP_MS,
    load_guarida_32cpe_topology,
    run_stage76a_simpy_guarida_simulation,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE76A_DOC = REPO_ROOT / "docs" / "STAGE76A_SIMPY_DISCRETE_EVENT_GUARIDA_32CPE_3PANEL_SIMULATION.md"


def test_stage76a_loads_exact_3panel_32cpe_guarida_topology() -> None:
    sectors = load_guarida_32cpe_topology()
    assert len(sectors["Panel1-Guarida"]) == 4
    assert len(sectors["Panel2-Guarida"]) == 22
    assert len(sectors["Panel3-Guarida"]) == 6
    assert sum(len(v) for v in sectors.values()) == 32
    assert sum(1 for c in sectors["Panel2-Guarida"] if c["is_airtime_hog"]) == 3


def test_stage76a_simpy_replications_and_5pillar_compliance() -> None:
    assert N_REPLICATIONS >= 10
    assert WARMUP_MS > 0.0

    payload = run_stage76a_simpy_guarida_simulation()
    assert DEFAULT_OUTPUT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"Missing pillars: {gate['missing_pillars']}"

    p2 = payload["sector_results"]["Panel2_Guarida_22CPE_Comparison"]
    a0 = p2["Arm_A0_Stock_airOS8_Unpatched_CoChannel"]
    b1 = p2["Arm_B1_Stage71B_5540MHz_Stage73B_UPH_BNG_CAKE"]
    b2 = p2["Arm_B2_Full_OpenWrt_Champion_v20_VendorIE"]

    assert a0["n_replications"] >= 10
    assert 0.0 <= a0["voip_drop_rate_pct"]["mean"] <= 100.0
    assert b1["p95_queue_delay_ms"]["mean"] < a0["p95_queue_delay_ms"]["mean"]
    assert b2["p95_queue_delay_ms"]["mean"] < b1["p95_queue_delay_ms"]["mean"]
    assert b1["voip_drop_rate_pct"]["mean"] == 0.0
    assert b2["voip_drop_rate_pct"]["mean"] == 0.0
    assert b1["hog_airtime_share_pct"]["mean"] < a0["hog_airtime_share_pct"]["mean"]
    assert b1["jain_fairness_index"]["mean"] > a0["jain_fairness_index"]["mean"]
    assert b2["sector_goodput_mbps"]["mean"] > b1["sector_goodput_mbps"]["mean"] > a0["sector_goodput_mbps"]["mean"]


def test_stage76a_doc_budget_and_header() -> None:
    assert STAGE76A_DOC.exists()
    lines = STAGE76A_DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"Expected < 220 lines, got {len(lines)}"
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
