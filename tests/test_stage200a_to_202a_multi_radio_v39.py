from __future__ import annotations

import json
from pathlib import Path

from tools.firmware.generate_mode_b_rc_poststart_v39 import (
    FAMILY_PROFILES_V39,
    render_mode_b_rc_poststart_v39,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
S200A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage200a_live_xc_2xc_round3_autoresearch.json"
S200A_DOC = REPO_ROOT / "docs" / "STAGE200A_LIVE_XC_2XC_ROUND3_AUTORESEARCH.md"
S201A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage201a_live_xm_nsm5_round3_autoresearch.json"
S201A_DOC = REPO_ROOT / "docs" / "STAGE201A_LIVE_XM_NSM5_ROUND3_AUTORESEARCH.md"
S202A_JSON = REPO_ROOT / "artifacts" / "autoresearch" / "stage202a_mode_b_rc_poststart_v39_receipt.json"
S202A_DOC = REPO_ROOT / "docs" / "STAGE202A_MODE_B_RC_POSTSTART_V39.md"
S202A_SH = REPO_ROOT / "artifacts" / "autoresearch" / "rc_poststart_mode_b_unified_v39.sh"


def test_stage200a_live_xc_2xc_round3_receipt_and_doc() -> None:
    assert S200A_JSON.exists(), "Missing stage200a_live_xc_2xc_round3_autoresearch.json"
    assert S200A_DOC.exists(), "Missing STAGE200A_LIVE_XC_2XC_ROUND3_AUTORESEARCH.md"

    doc_text = S200A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S200A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-200A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["under_load_rtt"]["samples"] >= 1
    assert data["xc_2xc_round3_champion_profile"]["tcp_pacing_ca_ratio"] == 110
    assert data["xc_2xc_round3_champion_profile"]["tcp_pacing_ss_ratio"] == 150
    assert data["xc_2xc_round3_champion_profile"]["fq_initial_quantum"] == 3028
    assert data["five_pillar_compliant"] is True


def test_stage201a_live_xm_nsm5_round3_receipt_and_doc() -> None:
    assert S201A_JSON.exists(), "Missing stage201a_live_xm_nsm5_round3_autoresearch.json"
    assert S201A_DOC.exists(), "Missing STAGE201A_LIVE_XM_NSM5_ROUND3_AUTORESEARCH.md"

    doc_text = S201A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S201A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-201A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert data["safety_boundaries"]["flash_writes"] == 0
    assert data["bench_xm_topology"]["boca2_nanostation_xm"]["lan_ip"] == "192.168.1.20"
    assert len(data["rounds"]) == 3
    for r in data["rounds"]:
        assert [w["window"] for w in r["windows"]] == ["A1", "B1", "A2", "B2"]
        for w in r["windows"]:
            assert w["boca2_xm_1_20_rtt"]["samples"] >= 1
    assert data["xm_nsm5_round3_champion_profile"]["netdev_max_backlog"] == 512
    assert data["xm_nsm5_round3_champion_profile"]["dev_weight"] == 32
    assert data["xm_nsm5_round3_champion_profile"]["ACBKMinfree"] == 64
    assert data["five_pillar_compliant"] is True


def test_stage202a_mode_b_rc_poststart_v39_generator_and_doc() -> None:
    assert S202A_JSON.exists(), "Missing stage202a_mode_b_rc_poststart_v39_receipt.json"
    assert S202A_DOC.exists(), "Missing STAGE202A_MODE_B_RC_POSTSTART_V39.md"
    assert S202A_SH.exists(), "Missing rc_poststart_mode_b_unified_v39.sh"

    doc_text = S202A_DOC.read_text(encoding="utf-8")
    assert len(doc_text.splitlines()) < 220
    assert doc_text.count("<!-- doc-head:") == 1

    data = json.loads(S202A_JSON.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-202A"
    assert data["generator_version"] == "v39.0"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_20_or_250"] is False
    assert set(data["supported_families"]) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert set(FAMILY_PROFILES_V39.keys()) == {"WA", "XC", "2XC", "XW", "XM", "LTU"}
    assert data["five_pillar_compliant"] is True

    script = render_mode_b_rc_poststart_v39("AUTO")
    # Verify FMX-DISC-11 ordering: daprot written before ff_mcast_airtime_limit
    idx_daprot = script.index("/proc/sys/dev/uph_wifi0/daprot")
    idx_mcast = script.index("/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit")
    assert idx_daprot < idx_mcast
