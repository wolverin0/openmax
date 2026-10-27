"""Stage 823A..824A unified suite.

Covers both stages with four structural tests plus the stage-specific negatives, and re-runs both
tools to prove determinism. The negatives are the point:

  823A  airMagic is a product name (0 kernel hits) and the bps/Hz expression does not exist
  824A  the classifier is in ame_dfs.ko not ame_core.ko, and LNA saturation is not named
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AR = REPO / "artifacts" / "autoresearch"

R823 = AR / "stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.json"
R824 = AR / "stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.json"

TOOLS = {
    "823A": REPO / "tools" / "re"
            / "dissect_stage823a_airos_ubnt_poll_airmagic_spectral_channel_scoring_re.py",
    "824A": REPO / "tools" / "re"
            / "dissect_stage824a_ltu_ame_core_dfs_radar_pulse_classifier_re.py",
}
DOCS = {
    "823A": REPO / "docs" / "STAGE823A_AIROS_UBNT_POLL_AIRMAGIC_SPECTRAL_CHANNEL_SCORING_RE.md",
    "824A": REPO / "docs" / "STAGE824A_LTU_AME_CORE_DFS_RADAR_PULSE_CLASSIFIER_RE.md",
}


def load(path: Path) -> dict:
    assert path.exists(), f"missing receipt: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def r823() -> dict:
    return load(R823)


@pytest.fixture(scope="module")
def r824() -> dict:
    return load(R824)


# ------------------------------------------------------------------ structure
def test_both_receipts_exist_and_are_labelled() -> None:
    for stage, path in (("823A", R823), ("824A", R824)):
        assert load(path)["meta"]["stage"] == stage


def test_both_tools_exist() -> None:
    for stage, path in TOOLS.items():
        assert path.exists(), f"{stage} script missing"


def test_both_docs_under_180_lines_with_one_doc_head() -> None:
    for stage, path in DOCS.items():
        assert path.exists(), f"{stage} doc missing"
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        assert lines < 180, f"{stage} doc has {lines} lines"
        assert text.count("<!-- doc-head") == 1, stage


def test_every_receipt_declares_static_scope_and_gaps() -> None:
    for path in (R823, R824):
        r = load(path)
        assert "static" in r["meta"]["scope"].lower()
        assert r["meta"]["radio_safety"] == "static only"
        assert r["gaps"], f"{path.name} has no declared gaps"


# ------------------------------------------------------------------ 823A
def test_823a_airmagic_is_not_a_kernel_symbol(r823: dict) -> None:
    s = r823["summary"]
    assert s["efficiency_token_hits"] == 0
    assert s["kernel_magic_hits"] == 3
    for m in r823["modules"]:
        if m.get("status") != "ok":
            continue
        if not m["module"].endswith("ubntspecd"):
            assert m["tokens"]["airmagic"] == 0


def test_823a_daemon_and_three_tiers(r823: dict) -> None:
    s = r823["summary"]
    assert s["daemon_bytes"] == 47192
    assert s["daemon_is_real_binary"] == 1
    assert s["scoring_tiers"] == ["BPS", "SCORE", "RATING"]
    assert s["scoring_tier_count"] == 3
    assert s["per_bandwidth_selection"] >= 1


def test_823a_formula_not_claimed(r823: dict) -> None:
    s = r823["summary"]
    assert s["formula_interface_recovered"] == 1
    assert s["formula_coefficients_recovered"] == 0
    assert s["bps_per_hz_expression_recovered"] == 0
    assert set(s["capacity_guards"]) == {"AMG_MAX_CHANS", "AMG_NUM_CONTROL"}


# ------------------------------------------------------------------ 824A
def test_824a_classifier_is_in_ame_dfs(r824: dict) -> None:
    s = r824["summary"]
    assert s["ame_dfs_present"] is True
    assert s["pulse_tokens_in_ame_dfs"] == 82
    assert s["pulse_tokens_in_ame_core"] == 22
    assert s["classifier_in_dfs_module"] == 1


def test_824a_classifier_symbols(r824: dict) -> None:
    s = r824["summary"]
    assert set(s["classifier_symbols"]) == {"DFSdetect", "DFSChanActivity",
                                           "DFS_heavy_env_det"}
    assert s["heavy_env_detector"] == 1
    assert s["filter_is_selectable"] == 1
    assert s["pulse_percent_max_reported"] == 1


def test_824a_lna_saturation_absent(r824: dict) -> None:
    s = r824["summary"]
    assert s["lna_token_hits"] == 0
    assert s["lna_saturation_named"] == 0
    assert s["lna_saturation_immunity_recovered"] == 0
    assert s["pw_pri_table_recovered"] == 0


# ------------------------------------------------------------------ reproducibility
def test_both_tools_are_reproducible() -> None:
    receipts = {s: p.read_bytes() for s, p in (("823A", R823), ("824A", R824))}
    for stage, tool in TOOLS.items():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    for stage, path in (("823A", R823), ("824A", R824)):
        assert path.read_bytes() == receipts[stage], f"{stage} receipt is not deterministic"
