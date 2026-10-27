from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage469a_wa_xc_xw_v10_bake() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage469a_universal_wa_xc_xw_v10_squashfs_bake.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "469A"
    assert data["status"] == "CONFIRMED"
    assert data["total_verified_hsqs_images"] >= 20
    assert data["all_images_have_hsqs_superblock"] is True
    assert data["integrated_v10_components"]["stage430a_pbe5ac_lbe5ac_ptp_champion_v2_verified"] is True
    assert data["integrated_v10_components"]["stage445a_receipt_verified"] is True
    assert data["integrated_v10_components"]["stage446a_tof_187m_detector_verified"] is True
    assert not any(data["safety_audit"].values())
