"""Stage 363A pytest suite."""

from __future__ import annotations

from pathlib import Path

from tools.verify.build_stage363a_guarida_kits_v2_ol_verifier import (
    update_kits_with_ol_verifier,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage363a_guarida_kits_v2_ol_verifier() -> None:
    report = update_kits_with_ol_verifier(REPO_ROOT)
    assert report["stage"] == "363A"
    assert report["status"] == "COMPLETED"
    assert report["writes_performed"] == 0
    assert report["kits_updated_count"] == 4

    for kit in report["kits"]:
        assert kit["uses_athstats_ol"] is True
        script = REPO_ROOT / kit["script_path"]
        txt = script.read_text(encoding="utf-8")
        assert "athstats -ol" in txt
        assert 'fmx_capture_ol_wal_stats "pre"' in txt
        assert 'fmx_capture_ol_wal_stats "post"' in txt

    p82_txt = (REPO_ROOT / "tools" / "guarida_stage0_kits" / "panel2_82_mode_b.sh").read_text(encoding="utf-8")
    assert 'echo "1 2 1" > /proc/sys/dev/uph_wifi0/sta_priority' in p82_txt
    assert "echo 2 > /proc/sys/dev/uph_wifi0/daprot" in p82_txt
    assert "echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit" in p82_txt

    gate = audit_stage_receipt_5pillars(report)
    assert gate["compliant"], f"Stage 363A 5-pillar gate failed: {gate}"

    doc = REPO_ROOT / "docs" / "STAGE363A_GUARIDA_KITS_V2_OL_VERIFIER.md"
    assert doc.exists()
    txt = doc.read_text(encoding="utf-8")
    assert len(txt.splitlines()) < 220
    assert txt.count("<!-- doc-head:") == 1
