from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage329a_to_334a_ltu_v5_end_to_end() -> None:
    receipt_paths = [
        REPO_ROOT / "artifacts" / "autoresearch" / "stage329a_live_ltu110_round7_conntrack_rps.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage330a_ltu_management_ipc_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage331a_ltu_dfs_radar_engine_re.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage332a_ltu_64cpe_ofdma_airtime_pareto.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage333a_ltu_7round_champion_v5_receipt.json",
        REPO_ROOT / "artifacts" / "autoresearch" / "stage334a_ltu_v5_verification_receipt.json",
    ]
    for p in receipt_paths:
        assert p.exists(), f"Missing receipt {p}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_paths = [
        REPO_ROOT / "docs" / "STAGE329A_LIVE_LTU110_ROUND7_CONNTRACK_RPS.md",
        REPO_ROOT / "docs" / "STAGE330A_LTU_MANAGEMENT_IPC_RE.md",
        REPO_ROOT / "docs" / "STAGE331A_LTU_DFS_RADAR_ENGINE_RE.md",
        REPO_ROOT / "docs" / "STAGE332A_LTU_64CPE_OFDMA_AIRTIME_PARETO.md",
        REPO_ROOT / "docs" / "STAGE333A_LTU_7ROUND_CHAMPION_V5.md",
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
    assert "net.netfilter.nf_conntrack_tcp_be_liberal=1" in sh_txt
    assert "net.core.netdev_budget_usecs=4000" in sh_txt
