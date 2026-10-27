"""Tests for Stage 483A: Public Tester Ground-Up Showcase Bundle v5 with All 5 First-Principles Pillars Integrated."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SH_PATH = REPO_ROOT / "firmware" / "openwrt" / "common" / "fmx_public_tester_ground_up_showcase_v5.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage483a_public_tester_ground_up_showcase_v5.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE483A_PUBLIC_TESTER_GROUND_UP_SHOWCASE_V5.md"


def test_stage483a_showcase_v5_script_lf_and_5pillars():
    assert BUNDLE_SH_PATH.exists()
    raw = BUNDLE_SH_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    for p in range(1, 6):
        assert f"[Pillar {p}]" in text
    assert "rollback" in text


def test_stage483a_receipt_verifies_all_5_pillars():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "483A"
    assert data["showcase_bundle_v5"]["version"] == "5.0.0"
    manifest = data["five_first_principles_pillars_manifest"]
    assert len(manifest) == 5
    for item in manifest:
        assert len(item["script_sha256"]) == 64
        assert len(item["companion_sha256"]) == 64
    assert "five_pillar_compliance" in data


def test_stage483a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
