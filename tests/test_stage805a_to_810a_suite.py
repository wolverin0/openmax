"""Stage 805A..810A unified suite.

Covers all six stages with structural checks, the per-stage negatives, the cross-stage agreement the
verifier relies on, and reproducibility of every tool including the verifier itself.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
AR = REPO / "artifacts" / "autoresearch"

R = {
    "805A": AR / "stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.json",
    "806A": AR / "stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json",
    "807A": AR / "stage807a_ltu_split_freq_and_ofdma_subchannel_re.json",
    "808A": AR / "stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.json",
    "809A": AR / "stage809a_pb040_to_pb070_quad_patch_pareto.json",
    "810A": AR / "stage810a_xtensa_pb070_and_ltu_split_freq_suite.json",
}

TOOLS = {
    "805A": REPO / "tools" / "re"
            / "dissect_stage805a_xtensa_wal_rc_ratefind_and_txbf_sounding_re.py",
    "806A": REPO / "tools" / "firmware"
            / "build_stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.py",
    "807A": REPO / "tools" / "re"
            / "dissect_stage807a_ltu_split_freq_and_ofdma_subchannel_re.py",
    "808A": REPO / "tools" / "re"
            / "dissect_stage808a_xc_qca9558_pcie_dma_and_airview_coexistence_re.py",
    "809A": REPO / "tools" / "sim" / "run_stage809a_pb040_to_pb070_quad_patch_pareto.py",
    "810A": REPO / "tools" / "verify"
            / "verify_stage810a_xtensa_pb070_and_ltu_split_freq_suite.py",
}

DOCS = {
    "805A": REPO / "docs" / "STAGE805A_XTENSA_WAL_RC_RATEFIND_AND_TXBF_SOUNDING_RE.md",
    "806A": REPO / "docs" / "STAGE806A_PB070_XTENSA_RC_PROBE_PER_SGMT_PATCH.md",
    "807A": REPO / "docs" / "STAGE807A_LTU_SPLIT_FREQ_AND_OFDMA_SUBCHANNEL_RE.md",
    "808A": REPO / "docs" / "STAGE808A_XC_QCA9558_PCIE_DMA_AND_AIRVIEW_COEXISTENCE_RE.md",
    "809A": REPO / "docs" / "STAGE809A_PB040_TO_PB070_QUAD_PATCH_PARETO.md",
    "810A": REPO / "docs" / "STAGE810A_XTENSA_PB070_AND_LTU_SPLIT_FREQ_SUITE.md",
}


def load(name: str) -> dict:
    assert R[name].exists(), f"missing receipt: {R[name]}"
    return json.loads(R[name].read_text(encoding="utf-8"))


# ------------------------------------------------------------------ structure
def test_all_six_receipts_labelled() -> None:
    for stage in R:
        assert load(stage)["meta"]["stage"] == stage


def test_all_six_tools_exist() -> None:
    for stage, p in TOOLS.items():
        assert p.exists(), f"{stage} script missing"


def test_all_six_docs_under_180_lines_with_one_doc_head() -> None:
    for stage, p in DOCS.items():
        assert p.exists(), f"{stage} doc missing"
        text = p.read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        assert lines < 180, f"{stage} doc has {lines} lines"
        assert text.count("<!-- doc-head") == 1, stage


def test_all_six_declare_static_and_gaps() -> None:
    for stage in R:
        r = load(stage)
        assert "static" in r["meta"]["scope"].lower(), stage
        assert r["meta"]["radio_safety"] == "static only", stage
        assert r["gaps"], stage


# ------------------------------------------------------------------ 805A / 806A
def test_805a_firmware_nameless_and_walk_hostside() -> None:
    s = load("805A")["summary"]
    assert s["firmware_names_absent"] == 1
    assert s["ratefind_is_host_side"] == 1
    assert s["ratefind_walk_complete"] == 1
    assert s["sounding_absent"] == 1


def test_806a_plan_without_patch() -> None:
    s = load("806A")["summary"]
    assert s["segments"] == 2
    assert s["total_ascii_runs"] == 111
    assert s["segments_with_anchor"] == 2
    assert s["segments_viable"] == 0
    assert s["patch_emitted"] == 0


def test_cross_stage_segment_count_agrees() -> None:
    assert load("805A")["summary"]["segments"] == load("806A")["summary"]["segments"]


# ------------------------------------------------------------------ 807A / 808A
def test_807a_ulmap_not_subchannel() -> None:
    s = load("807A")["summary"]
    assert s["subchannel_vocabulary_absent"] == 1
    assert s["ulmap_is_named_subsystem"] == 1
    assert s["split_freq_pair_present"] == 1


def test_808a_airview_is_userspace() -> None:
    s = load("808A")["summary"]
    assert s["kernel_airview_hits"] == 0
    assert s["airview_is_userspace"] == 1
    assert s["airview_bytes"] == 8647
    assert s["daemons_readable"] == 4


# ------------------------------------------------------------------ 809A / 810A
def test_809a_projection_and_blocked() -> None:
    s = load("809A")["summary"]
    assert s["measurement_or_projection"] == "projection"
    assert s["execution_authorised"] == 0
    assert s["all_roles_blocked"] == 1
    assert s["pareto_front_size"] + s["dominated_count"] == s["roles_parsed"]


def test_810a_compliant() -> None:
    s = load("810A")["summary"]
    assert s["stages_present"] == s["stages_expected"] == 5
    assert s["failures"] == 0
    assert s["compliant"] == 1
    assert s["checks_run"] == s["checks_passed"]


# ------------------------------------------------------------------ reproducibility
def test_every_tool_is_reproducible() -> None:
    before = {s: p.read_bytes() for s, p in R.items()}
    for stage, tool in TOOLS.items():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    for stage, p in R.items():
        assert p.read_bytes() == before[stage], f"{stage} receipt is not deterministic"
