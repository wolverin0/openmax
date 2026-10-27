from __future__ import annotations

from pathlib import Path

from tools.verify.verify_stage734a_ltu_252window_v19_and_squashfs_v19_gate import verify_stage734a

ROOT = Path(__file__).resolve().parents[1]


def test_stage729a_to_734a_suite() -> None:
    receipt = verify_stage734a()
    assert receipt["stage"] == "734A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["verified_stages"] == ["729A", "730A", "731A", "732A", "733A", "734A"]
    assert receipt["highlights"]["stage729a_cumulative_live_windows"] == 252
    assert receipt["highlights"]["stage733a_v19_hsqs_images"] == 180

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
