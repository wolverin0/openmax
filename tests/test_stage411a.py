from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage411a_edge_micro_worker_c_classifier() -> None:
    receipt_path = REPO_ROOT / "artifacts/autoresearch/stage411a_edge_micro_worker_c_classifier.json"
    doc_path = REPO_ROOT / "docs/STAGE411A_EDGE_MICRO_WORKER_C_CLASSIFIER.md"
    c_path = REPO_ROOT / "controller/fmx_micro_worker.c"
    assert receipt_path.exists()
    assert doc_path.exists()
    assert c_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "411A"
    assert data["status"] == "CONFIRMED"
    assert data["footprint_and_latency_budget"]["stripped_mips_arm_elf_budget_kb"] <= 48
    assert data["footprint_and_latency_budget"]["floating_point_instructions"] == 0

    vecs = {v["name"]: v["predicted_class"] for v in data["canonical_test_vectors"]}
    assert vecs["Vector_0_Healthy_Link"] == "HEALTHY_RF"
    assert vecs["Vector_A_Tower_Interference"] == "CLASS_A_TOWER_INTERFERENCE"
    assert vecs["Vector_B_Neighbor_WiFi_Interference"] == "CLASS_B_NEIGHBOR_INTERFERENCE"
    assert vecs["Vector_C_Chain_Imbalance_Foliage"] == "CLASS_C_CHAIN_IMBALANCE_NLOS"
    assert vecs["Vector_D_LAN_PoE_Cable_Fault"] == "CLASS_D_LAN_POE_CABLE_DEGRADE"
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
