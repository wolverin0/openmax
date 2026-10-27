from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
S247A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage247a_live_ltu110_round4_bridge_tcp_autoresearch.json"
S247A_MD = REPO_ROOT / "docs" / "STAGE247A_LIVE_LTU110_ROUND4_BRIDGE_TCP_AUTORESEARCH.md"
S248A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage248a_ltu_5board_cpe_family_re.json"
S248A_MD = REPO_ROOT / "docs" / "STAGE248A_LTU_5BOARD_CPE_FAMILY_RE.md"
S249A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage249a_ltu_harq_retransmission_and_rate_fsm_re.json"
S249A_MD = REPO_ROOT / "docs" / "STAGE249A_LTU_HARQ_RETRANSMISSION_AND_RATE_FSM_RE.md"
S250A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage250a_ltu_harq_vs_openmax_ampdu_pareto.json"
S250A_MD = REPO_ROOT / "docs" / "STAGE250A_LTU_HARQ_VS_OPENMAX_AMPDU_PARETO.md"
S251A_SH = REPO_ROOT / "firmware" / "ltu_safe_kit" / "rc.poststart_ltu_safe_champion.sh"
S251A_MD = REPO_ROOT / "docs" / "GUIA_UNIVERSAL_LTU_SAFE_CHAMPION.md"
S251A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage251a_ltu_safe_champion_v2_receipt.json"
S252A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage252a_ltu_6stage_loop_verification_receipt.json"


def _assert_doc_constraints(md_path: Path) -> None:
    assert md_path.exists(), f"Missing {md_path}"
    lines = md_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220, f"{md_path} has {len(lines)} lines (>= 220)"
    assert sum(1 for ln in lines if ln.startswith("<!-- doc-head:")) == 1


def test_stage247a_live_ltu110_round4_bridge_tcp_autoresearch() -> None:
    assert S247A_JSON.exists()
    _assert_doc_constraints(S247A_MD)
    data = json.loads(S247A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "247A"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["watchdog_seconds"] == 45
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["safety_envelope"]["touched_forbidden_hosts_241_242_20_250"] is False
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert set(r["phases"].keys()) == {"A1", "B1", "A2", "B2"}
        assert r["summary"]["winner"] == "B_CHAMPION"
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage248a_ltu_5board_cpe_family_re() -> None:
    assert S248A_JSON.exists()
    _assert_doc_constraints(S248A_MD)
    data = json.loads(S248A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "248A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["five_board_cpe_family"]["board_ids"] == ["0xae02", "0xae07", "0xae08", "0xae09", "0xae0b"]
    assert len(data["five_board_cpe_family"]["boards"]) == 5
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage249a_ltu_harq_retransmission_and_rate_fsm_re() -> None:
    assert S249A_JSON.exists()
    _assert_doc_constraints(S249A_MD)
    data = json.loads(S249A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "249A"
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    ra = data["modulation_rate_fsm_and_timers"]["rate_adaptation_thresholds_extracted"]
    assert ra["startThrd_4096_pct"] == 97
    assert ra["stayThrd_4096_pct"] == 90
    assert data["harq_block_ack_retransmission_architecture"]["harq_and_ack_symbols_count"] > 10
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage250a_ltu_harq_vs_openmax_ampdu_pareto() -> None:
    assert S250A_JSON.exists()
    _assert_doc_constraints(S250A_MD)
    data = json.loads(S250A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "250A"
    b = data["benchmarks"]
    assert b["openmax_vs_legacy_jitter_p99_reduction_ms"] > 5.0
    assert b["ltu_harq_vs_openmax_jitter_p99_reduction_ms"] > 0.2
    assert data["nsga2_pareto_front"]["solutions_count"] >= 1
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage251a_and_252a_safe_champion_v2_and_guide() -> None:
    assert S251A_SH.exists()
    _assert_doc_constraints(S251A_MD)
    sh_txt = S251A_SH.read_text(encoding="utf-8")
    assert "\r\n" not in sh_txt
    assert "/dev/ame" not in sh_txt
    assert "net.ipv4.tcp_pacing_ca_ratio=120" in sh_txt
    assert "multicast_snooping" in sh_txt
    assert "net.netfilter.nf_conntrack_max=16384" in sh_txt
    assert "tc qdisc replace dev ath0 root fq_codel" in sh_txt

    s251 = json.loads(S251A_JSON.read_text(encoding="utf-8"))
    s252 = json.loads(S252A_JSON.read_text(encoding="utf-8"))
    assert all(s251["checks"].values())
    assert audit_stage_receipt_5pillars(s251)["compliant"] is True
    assert audit_stage_receipt_5pillars(s252)["compliant"] is True
