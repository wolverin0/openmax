from __future__ import annotations

from pathlib import Path

from tools.verify.verify_stage766a_ltu_264window_v20_and_squashfs_v20_gate import verify_stage766a

ROOT = Path(__file__).resolve().parents[1]


def test_stage761a_to_766a_suite() -> None:
    receipt = verify_stage766a()
    assert receipt["stage"] == "766A"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["verified_stages"] == ["761A", "762A", "763A", "764A", "765A", "766A"]
    assert receipt["highlights"]["stage761a_cumulative_live_windows"] == 264
    assert receipt["highlights"]["stage765a_v20_hsqs_images"] == 180
    assert receipt["highlights"]["zero_rogue_dhcp_guarantee"] is True

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
