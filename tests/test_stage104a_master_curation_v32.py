#!/usr/bin/env python3
"""Unit tests for Stage 104A Master Curation v32.0 (`T-S104A-MASTER-CURATION-V32-S103-WAVE-SYNC`)."""

from __future__ import annotations

import json

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_stage104a_master_curation_v32 import (
    OUTPUT_JSON_PATH,
    TARGET_DOCS,
    run_stage104a_verification,
)


def test_stage104a_master_curation_v32_execution_and_receipt() -> None:
    receipt = run_stage104a_verification()
    assert OUTPUT_JSON_PATH.exists()
    assert receipt["stage"] == "104A"
    assert receipt["curation_version"] == "v32.0"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["all_docs_passed"] is True

    disc35 = receipt["synchronized_receipts"]["fmx_disc_35_ubntbox_and_w4d"]
    assert disc35["discovery_id"] == "FMX-DISC-35"
    assert disc35["ubntbox_gpio_flock_set_va"] == "0x40c2a0"
    assert "0x9fec" in disc35["ubntbox_rsa_ends_gate_offset"]
    assert disc35["w4d_images_audited"] == 2

    s103a = receipt["synchronized_receipts"]["stage103a_wa_xc_untested_knobs"]
    assert s103a["kernel_boundary_laws_count"] == 3
    assert "FMX-S103A-KB-01" in s103a["kernel_boundary_law_ids"]
    assert s103a["wa250_p95_rtt_delta_pct"] == -46.93
    assert s103a["decision"] == "PROMOTE_NEW_CHAMPION"

    s103d = receipt["synchronized_receipts"]["stage103d_mkt_bidirectional_rfc2544_soak"]
    assert s103d["frame_sizes_bytes"] == [64, 512, 1400]
    assert s103d["goodput_delta_pct"] == 6.159
    assert s103d["voip_jitter_delta_pct"] == -57.944
    assert s103d["pareto_delta_pct"] == 6.3373

    s103e = receipt["synchronized_receipts"]["stage103e_pbe5ac_to_mkt_e2e_bench"]
    assert s103e["frequency_mhz"] == 5200
    assert s103e["voip_jitter_delta_pct"] == -46.46
    assert s103e["arm_b_e2e_mk1_loss_pct"] == 0.0
    assert s103e["decision"] == "PROMOTE_NEW_CHAMPION"

    s103f = receipt["synchronized_receipts"]["stage103f_ltu_dual_and_2xc_bench"]
    assert s103f["ltu_scheduler_giveup_max"] == 0
    assert s103f["ltu_symbol_giveup_max"] == 0
    assert s103f["r2ac_wifi1_irq_delta_total"] == 0
    assert s103f["r2ac_p95_rtt_arm_b_median_ms"] == 6.357


def test_stage104a_docs_line_budgets_and_5pillar_gate() -> None:
    loaded = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"

    for doc_path in TARGET_DOCS:
        assert doc_path.exists(), f"Missing {doc_path.name}"
        lines = doc_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 215, f"{doc_path.name} has {len(lines)} lines (>= 215)"
        doc_heads = [ln for ln in lines if "<!-- doc-head" in ln]
        assert len(doc_heads) == 1, f"{doc_path.name} must have exactly 1 doc-head"
