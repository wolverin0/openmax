from __future__ import annotations

from pathlib import Path

from tools.research.run_stage75b_nsga2_pareto_and_statistical_synthesis import (
    DEFAULT_OUTPUT_JSON,
    build_stage75b_nsga2_pareto_and_statistical_synthesis,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE75B_DOC = REPO_ROOT / "docs" / "STAGE75B_GLOBAL_NSGA2_PARETO_AND_STATISTICAL_SYNTHESIS.md"


def test_stage75b_pareto_frontiers_hypervolume_and_5pillar_gate() -> None:
    payload = build_stage75b_nsga2_pareto_and_statistical_synthesis()
    assert DEFAULT_OUTPUT_JSON.exists()

    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"Missing pillars: {gate['missing_pillars']}"

    families = payload["families"]
    assert set(families.keys()) == {
        "family_1_openwrt_ptmp",
        "family_2_openwrt_ptp",
        "family_3_airos8_wa_xc_ptp",
        "family_4_af_ltu",
    }

    for fk, fdata in families.items():
        assert fdata["total_candidates_evaluated"] >= 2
        assert fdata["pareto_front_count"] >= 2
        assert fdata["hypervolume_3d_final"] >= fdata["hypervolume_3d_initial"]
        assert fdata["hypervolume_3d_gain"] > 0.0
        assert fdata["nsga2_surrogate_front_hv"] > 0.0

    fam1_stats = families["family_1_openwrt_ptmp"]["statistical_effect_sizes"]["promoted_champions_goodput_mbps"]
    assert fam1_stats["cohen_dz_signed"] > 1.0
    assert fam1_stats["hedges_gz_signed"] > 0.9
    assert fam1_stats["ci95_low"] > 0.0

    fam3_stats = families["family_3_airos8_wa_xc_ptp"]["statistical_effect_sizes"]["promoted_champions_p95_rtt_ms"]
    assert fam3_stats["cohen_dz_signed"] > 1.0
    assert fam3_stats["hedges_gz_signed"] > 0.9
    assert fam3_stats["ci95_high"] < 0.0


def test_stage75b_doc_budget_and_header() -> None:
    assert STAGE75B_DOC.exists()
    lines = STAGE75B_DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"Expected < 220 lines, got {len(lines)}"
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
