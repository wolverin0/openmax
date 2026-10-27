from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage287a_to_292a_ltu_v3_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage287a_live_ltu110_round5_autoresearch.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage288a_ltu_auto_duty_cycle_scheduler_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage289a_ltu_mimo_xpic_txbf_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage290a_ltu_dynamic_duty_cycle_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage291a_ltu_5round_champion_v3_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage292a_ltu_v3_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE287A_LIVE_LTU110_ROUND5_AUTORESEARCH.md",
        REPO_ROOT / "docs" / "STAGE288A_LTU_AUTO_DUTY_CYCLE_SCHEDULER_RE.md",
        REPO_ROOT / "docs" / "STAGE289A_LTU_MIMO_XPIC_TXBF_RE.md",
        REPO_ROOT / "docs" / "STAGE290A_LTU_DYNAMIC_DUTY_CYCLE_PARETO.md",
        REPO_ROOT / "docs" / "STAGE291A_LTU_5ROUND_CHAMPION_V3.md",
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
    assert "net.core.rmem_default=262144" in sh_txt
    assert "net.core.rps_sock_flow_entries=4096" in sh_txt
