#!/usr/bin/env python3
"""Pytest suite for Stage 153A: Cross-Fleet WA + XC + 2XC + XW + XM Champion Synthesis & Master Curation v37.0."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars  # noqa: E402
from tools.verify.verify_stage153a_cross_fleet_champion_v37 import (  # noqa: E402
    OUT_JSON,
    verify_stage153a_cross_fleet_champion_v37,
)


def test_stage153a_receipt_exists_and_5pillar_compliant() -> None:
    verify_stage153a_cross_fleet_champion_v37()
    assert OUT_JSON.is_file(), f"Missing {OUT_JSON}"
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-153A"
    assert data["curation_version"] == "v37.0"
    assert data["status"] == "CONFIRMED"
    assert data["five_pillar_compliant"] is True
    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"] is True
    assert audit["missing_pillars"] == []


def test_stage153a_all_five_families_consolidated() -> None:
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert data["families_consolidated"] == ["WA", "XC", "2XC", "XW", "XM"]
    champions = data["cross_fleet_champions"]
    for fam in ("WA", "XC", "2XC", "XW", "XM"):
        assert fam in champions
        assert champions[fam]["family_id"] == fam
        assert len(champions[fam]["winning_knobs"]) >= 5


def test_stage153a_upstream_receipts_and_safety_boundaries() -> None:
    data = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    up = data["upstream_stage_receipts"]
    assert up["stage151a"]["rounds_count"] == 3
    assert up["stage151a"]["five_pillar_compliant"] is True
    assert up["stage152a"]["rounds_count"] == 3
    assert up["stage152a"]["five_pillar_compliant"] is True

    sb = data["safety_boundaries"]
    assert sb["touched_241_or_242"] is False
    assert sb["touched_production_guarida"] is False
    assert sb["flash_writes"] == 0
    assert sb["guarida_3_panels_32_cpes_preserved"]["total_guarida_cpes"] == 32
    assert data["repo_deterministic_gates"]["compliant"] is True
