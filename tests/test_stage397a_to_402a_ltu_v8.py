from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage397a_to_402a_ltu_v8_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage397a_live_ltu110_round10_120window_milestone.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage398a_ltu_ble_gatt_provisioning_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage399a_ltu_dualbank_nand_ameimg_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage400a_ltu_gps_reuse1_tdd_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage401a_ltu_10round_120window_champion_v8_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage402a_ltu_v8_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE397A_LIVE_LTU110_ROUND10_120WINDOW_MILESTONE.md",
        REPO_ROOT / "docs" / "STAGE398A_LTU_BLE_GATT_PROVISIONING_RE.md",
        REPO_ROOT / "docs" / "STAGE399A_LTU_DUALBANK_NAND_AMEIMG_RE.md",
        REPO_ROOT / "docs" / "STAGE400A_LTU_GPS_REUSE1_TDD_PARETO.md",
        REPO_ROOT / "docs" / "STAGE401A_LTU_10ROUND_120WINDOW_CHAMPION_V8.md",
    ]
    for dp in doc_paths:
        assert dp.exists(), f"Missing doc {dp}"
        lines = dp.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 220, f"{dp} exceeds 220 lines"
        assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1

    champ_sh = REPO_ROOT / "firmware" / "ltu_safe_kit" / "rc.poststart_ltu_safe_champion.sh"
    sh_txt = champ_sh.read_text(encoding="utf-8")
    assert "\r\n" not in sh_txt
    assert "/dev/ame" not in sh_txt
    assert "vm.dirty_ratio=10" in sh_txt
    assert "vm.dirty_background_ratio=5" in sh_txt
    assert "vm.vfs_cache_pressure=50" in sh_txt
