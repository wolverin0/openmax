from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S301A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage301a_ltu_thermal_tcxo_iq_cal_re.json"
S301A_MD = REPO_ROOT / "docs" / "STAGE301A_LTU_THERMAL_TCXO_IQ_CAL_RE.md"


def test_stage301a_ltu_thermal_tcxo_iq_cal_re() -> None:
    assert S301A_JSON.exists()
    assert S301A_MD.exists()
    data = json.loads(S301A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "301A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    loops = data["calibration_and_compensation_loops"]
    assert loops["thermal_pa_gain_and_tssi_loop"]["symbols_count"] > 10
    assert loops["tcxo_vctcxo_afc_frequency_drift_loop"]["symbols_count"] > 10
    assert loops["tx_rx_iq_imbalance_and_dc_offset_loop"]["symbols_count"] > 10
    lines = S301A_MD.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True
