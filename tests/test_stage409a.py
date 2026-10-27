from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage409a_wmi_retry_and_hook_loader() -> None:
    receipt_path = REPO_ROOT / "artifacts/autoresearch/stage409a_wmi_retry_and_hook_loader.json"
    doc_path = REPO_ROOT / "docs/STAGE409A_WMI_RETRY_AND_HOOK_LOADER.md"
    sh_path = REPO_ROOT / "firmware/openwrt/common/fmx_wmi_retry_and_hook_loader.sh"
    assert receipt_path.exists()
    assert doc_path.exists()
    assert sh_path.exists()

    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "409A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert len(data["wmi_commands_governed"]["four_series_retry_schedule"]) == 4
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
