from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage541a_wa_xc_xw_v12_bake() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage541a_universal_wa_xc_xw_v12_squashfs_bake.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "541A"
    assert data["status"] == "CONFIRMED"
    assert data["total_verified_hsqs_images"] == 180
    assert data["all_images_have_hsqs_superblock"] is True
    assert data["integrated_v12_components"]["stage487a_vht80_cap_and_vht40_unlock_verified"] is True
    assert data["integrated_v12_components"]["stage403a_pktlog0_and_pb040_ram_canary_verified"] is True
    assert not any(data["safety_audit"].values())
