from __future__ import annotations

import json
from pathlib import Path

from firmware.xtensa_sgmt_surgical_patcher import SgmtContainer
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts/autoresearch/stage474a_pb050_xtensa_rc_probe_dampener_sgmt_patch.json"
DOC = ROOT / "docs/STAGE474A_PB050_XTENSA_RC_PROBE_DAMPENER_SGMT_PATCH.md"


def test_stage474a_pb050_sgmt_patch_artifact_and_binaries() -> None:
    assert ARTIFACT.exists(), f"Missing {ARTIFACT}"
    assert DOC.exists(), f"Missing {DOC}"
    doc_lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(doc_lines) < 220, f"Doc exceeds 220 lines ({len(doc_lines)})"

    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert data["stage"] == "474A"
    assert data["status"] == "CONFIRMED"
    assert data["live_devices_touched"] is False
    assert data["profile_id"] == "PB050-RC-PROBE-DAMPEN"
    assert data["patched_image_count"] == 7

    for img in data["patched_images"]:
        sgmt_path = ROOT / img["output_sgmt_path"]
        assert sgmt_path.exists(), f"Missing patched SGMT binary {sgmt_path}"
        parsed = SgmtContainer.from_bytes(sgmt_path.read_bytes())
        assert parsed.entry_point == 0x00983C00
        assert img["signature_bytes"] == 0
        assert img["verified_values"]["g_rc_probe_period_ms"] == 15000
        assert img["verified_values"]["g_rc_probe_pkt_threshold"] == 512
        assert img["verified_values"]["wmi_peer_assoc_overwrite_neutralized"] is True
        if img["target_id"] != "OpenWrt_10.1.467-ct_IE3":
            assert img["verified_values"]["g_default_xretry_per_penalty"] == 12
            assert img["verified_values"]["g_rc_rate_max_per_thr"] == 72

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"
