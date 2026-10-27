from __future__ import annotations

from pathlib import Path

from tools.verify.verify_stage712a_ltu_240window_v18_and_squashfs_v18_gate import verify_stage712a

ROOT = Path(__file__).resolve().parents[1]


def test_stage707a_to_712a_suite() -> None:
    receipt = verify_stage712a()
    assert receipt["stage"] == "712A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["verified_stages"] == ["707A", "708A", "709A", "710A", "711A", "712A"]
    assert receipt["highlights"]["stage707a_cumulative_live_windows"] == 240
    assert receipt["highlights"]["stage711a_v18_hsqs_images"] == 180

    for stg, chk in receipt["artifact_checks"].items():
        assert chk["exists"] is True, f"Missing artifact for {stg}"
        assert chk["status"] == "CONFIRMED"
        assert chk["has_five_pillar_compliance"] is True
        assert chk["zero_safety_violations"] is True

    for stg, dchk in receipt["doc_checks"].items():
        assert dchk["exists"] is True, f"Missing doc for {stg}"
        assert dchk["under_200_lines"] is True
        assert dchk["has_doc_head_open"] is True
        assert dchk["has_doc_head_close"] is True
