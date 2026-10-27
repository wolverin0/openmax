"""
Tests for Stage 32A (`T-S32A-LIVE-MINED-KNOBS-M10-M11-M14-PHYSICAL-BENCH`):
  - Physical bench receipt (`artifacts/autoresearch/stage32a_mined_knobs_bench_20261025.json`)
  - Verification of `S32A-R1` (`M10`: `htt_max_amsdu_ampdu` `'2 64'` vs `'3 64'` on 3-CPE 5 GHz sector)
  - Verification of `S32A-R2` (`M11`: `AME do_lotto` `1` vs `0` on `LTU-Lite #1` unlocked `ap-ptmp` SQ mode)
  - Verification of `S32A-R3` (`M14`: `UPH swr_limit` `'1 6'` vs `'0 0'` on `Rocket 2AC Prism` under live 2.4 GHz load)
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage32a_mined_knobs_bench_20261025.json"


def test_stage32a_receipt_exists_and_has_three_rounds():
    assert RECEIPT_PATH.exists(), f"Missing Stage 32A receipt: {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE32A"
    assert data["task_id"] == "T-S32A-LIVE-MINED-KNOBS-M10-M11-M14-PHYSICAL-BENCH"
    assert data["status"] == "COMPLETED_ON_PHYSICAL_BENCH"
    assert data["safety_audit"]["persistent_flash_writes"] is False
    assert set(data["rounds"].keys()) == {"S32A-R1", "S32A-R2", "S32A-R3"}


def test_s32a_r1_m10_htt_amsdu_ampdu_qualification_and_abba():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    r1 = data["rounds"]["S32A-R1"]
    assert r1["mechanism_id"] == "M10"
    assert set(r1["phases"].keys()) == {"A1", "B1", "A2", "B2"}
    assert r1["phases"]["A1"]["getter_readback"]["ap_htt_max_amsdu_ampdu"].startswith("3")
    assert r1["phases"]["B1"]["getter_readback"]["ap_htt_max_amsdu_ampdu"].startswith("2")
    assert r1["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")
    assert r1["research_reactor_triggered"] is True


def test_s32a_r2_m11_ltu_do_lotto_qualification_and_abba():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    r2 = data["rounds"]["S32A-R2"]
    assert r2["mechanism_id"] == "M11"
    assert set(r2["phases"].keys()) == {"A1", "B1", "A2", "B2"}
    assert r2["phases"]["A1"]["do_lotto_readback"] == "0"
    assert r2["phases"]["B1"]["do_lotto_readback"] == "1"
    assert r2["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")
    assert r2["research_reactor_triggered"] is True


def test_s32a_r3_m14_uph_swr_limit_binary_and_dmesg_qualification():
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    r3 = data["rounds"]["S32A-R3"]
    assert r3["mechanism_id"] == "M14"
    assert "0x0b404" in r3["binary_qualification"]["handler_offset"]
    assert set(r3["phases"].keys()) == {"A1", "B1", "A2", "B2"}
    assert "SWR Limit" in r3["phases"]["B1"]["dmesg_swr_limit_getter"]
    assert r3["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")
    assert r3["research_reactor_triggered"] is True
