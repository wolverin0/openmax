from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage468a_spectral_nf_helper() -> None:
    receipt_path = REPO_ROOT / "artifacts" / "autoresearch" / "stage468a_xtensa_spectral_scan_and_nf_cal_helper.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "468A"
    assert data["status"] == "CONFIRMED"
    assert all(data["checks"].values())
    assert data["wmi_spectral_parameters"]["fft_bins"] == 64
    assert not any(data["safety_audit"].values())
