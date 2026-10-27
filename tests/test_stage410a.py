from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage410a_sub20mhz_nlos_profile() -> None:
    receipt_path = REPO_ROOT / "artifacts/autoresearch/stage410a_sub20mhz_nlos_profile.json"
    doc_path = REPO_ROOT / "docs/STAGE410A_SUB20MHZ_NLOS_PROFILE.md"
    sh_path = REPO_ROOT / "firmware/openwrt/common/fmx_sub20mhz_nlos_profile.sh"
    assert receipt_path.exists()
    assert doc_path.exists()
    assert sh_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "410A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["sub20mhz_numerology"]["5mhz_quarter_rate"]["psd_snr_gain_db"] == 6.02
    assert data["sub20mhz_numerology"]["10mhz_half_rate"]["psd_snr_gain_db"] == 3.01
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
