from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage575a_wa_xc_xw_v14_bake() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage575a_universal_wa_xc_xw_v14_squashfs_bake.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "575A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["total_verified_hsqs_images"] == 180
    assert data["all_images_have_hsqs_superblock"] is True
    assert not any(data["safety_audit"].values())
