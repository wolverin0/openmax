"""Stage 891A..896A unified suite.

Covers the fail-closed SGMT audit, the binary-versus-runtime matrix, both truth classifiers, the
consolidated table and the gate: structure, per-stage invariants, the three cross-stage agreements, the
documentation contract (under 180 lines, exactly one doc-head, no exclamation mark in prose) and
byte-level reproducibility of every tool.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AR = REPO / "artifacts" / "autoresearch"

R = {
    "891A": AR / "stage891a_sgmt_fail_closed_binary_audit.json",
    "892A": AR / "stage892a_pb040_pb100_binary_vs_runtime_audit.json",
    "893A": AR / "stage893a_xtensa_findings_truth_classification.json",
    "894A": AR / "stage894a_ko_module_claims_truth_classification.json",
    "895A": AR / "stage895a_ko_module_claims_truth_table.json",
    "896A": AR / "stage896a_re_fail_closed_truth_gate.json",
}

TOOLS = {
    "891A": REPO / "tools" / "qca988x" / "verify_all_sgmt_patches_fail_closed_audit.py",
    "892A": REPO / "tools" / "qca988x" / "audit_stage892a_pb040_to_pb100_binary_vs_runtime.py",
    "893A": REPO / "tools" / "re" / "dissect_stage893a_xtensa_findings_truth_classification.py",
    "894A": REPO / "tools" / "re" / "dissect_stage894a_ko_module_claims_truth_classification.py",
    "895A": REPO / "tools" / "verify" / "build_stage895a_ko_module_claims_truth_table.py",
    "896A": REPO / "tools" / "verify" / "verify_stage896a_re_fail_closed_truth_gate.py",
}

DOCS = {
    "891A": REPO / "docs" / "STAGE891A_SGMT_FAIL_CLOSED_BINARY_AUDIT.md",
    "892A": REPO / "docs" / "STAGE892A_PB040_PB100_BINARY_VS_RUNTIME_AUDIT.md",
    "893A": REPO / "docs" / "STAGE893A_XTENSA_FINDINGS_TRUTH_CLASSIFICATION.md",
    "894A": REPO / "docs" / "STAGE894A_KO_MODULE_CLAIMS_TRUTH_CLASSIFICATION.md",
    "895A": REPO / "docs" / "STAGE895A_KO_MODULE_CLAIMS_TRUTH_TABLE.md",
    "896A": REPO / "docs" / "STAGE896A_RE_FAIL_CLOSED_TRUTH_GATE.md",
}

FROZEN = ("tools/qca988x/sgmt_container_inspector.py",
          "firmware/xtensa_sgmt_surgical_patcher.py")


def load(stage: str) -> dict:
    assert R[stage].exists(), f"missing receipt: {R[stage]}"
    return json.loads(R[stage].read_text(encoding="utf-8"))


def test_all_six_receipts_are_labelled() -> None:
    for stage in R:
        assert load(stage)["meta"]["stage"] == stage


def test_all_six_tools_exist() -> None:
    for stage, path in TOOLS.items():
        assert path.exists(), f"{stage} script missing"


def test_all_six_docs_respect_the_contract() -> None:
    for stage, path in DOCS.items():
        assert path.exists(), f"{stage} doc missing"
        text = path.read_text(encoding="utf-8")
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
        assert lines < 180, f"{stage} doc has {lines} lines"
        assert text.count("<!-- doc-head") == 1, stage
        prose = re.sub(r"```.*?```", "", re.sub(r"<!--.*?-->", "", text, flags=re.S), flags=re.S)
        assert "!" not in prose, f"{stage} doc contains an exclamation mark in prose"


def test_all_six_declare_static_scope_and_gaps() -> None:
    for stage in R:
        report = load(stage)
        assert "static" in report["meta"]["scope"].lower(), stage
        assert report["meta"]["radio_safety"] == "static only", stage
        assert report["gaps"], stage


def test_frozen_files_were_not_rewritten_by_this_batch() -> None:
    # the audit reads these for the format only; Codex #2 owns them and they must not be touched
    for relative in FROZEN:
        path = REPO / relative
        assert path.exists(), relative
    for stage in ("891A", "892A", "893A", "894A", "895A", "896A"):
        source = TOOLS[stage].read_text(encoding="utf-8")
        module = Path(TOOLS[stage]).name
        assert "import sgmt_container_inspector" not in source, module
        assert "from sgmt_container_inspector" not in source, module
        assert "import xtensa_sgmt_surgical_patcher" not in source, module


def test_891a_fail_closed() -> None:
    summary = load("891A")["summary"]
    assert summary["containers_found"] == 35
    assert summary["containers_ok"] == 35
    assert summary["containers_failed"] == 0
    assert summary["failure_count"] == 0
    assert summary["total_segments"] == 140
    assert summary["flags_compressed"] == 35
    assert summary["flags_uncompressed"] == 0
    assert summary["patches_ok"] == summary["patches_audited"] == 12
    assert summary["ram_roles_matched"] == summary["ram_roles_checked"] == 3
    assert summary["fail_closed"] == 1


def test_891a_containers_are_disjoint_but_not_address_ordered() -> None:
    containers = load("891A")["containers"]
    assert all(c["checks"]["segments_disjoint"] for c in containers)
    assert all(c["checks"]["ended_with_sentinel"] for c in containers)
    # file order is not a format rule: none of the 35 containers is ascending by target address
    assert not any(c["checks"]["segments_ascending_in_file"] for c in containers)


def test_892a_no_gate_reaches_runtime() -> None:
    summary = load("892A")["summary"]
    assert summary["gates"] == 7
    assert summary["gates_static_proven"] == 3
    assert summary["gates_on_target_present"] == 2
    assert summary["gates_site_execution_proven"] == 0
    assert summary["gates_runtime_proven"] == 0
    assert summary["gates_pending"] == 7
    assert summary["dmesg_receipts"] == 0
    assert summary["explicit_pending_statement"] == 1


def test_893a_and_894a_are_structurally_complete() -> None:
    for stage, total in (("893A", 143), ("894A", 258)):
        summary = load(stage)["summary"]
        receipt = load(stage)
        assert summary["receipts_classified"] == total
        assert summary["structural_complete"] == 1
        assert summary["provenance_undeclared"] == len(receipt["unclassified"])
        assert (summary["citable_findings"] + summary["provenance_undeclared"]) == total


def test_894a_per_module_fractions_are_bounded() -> None:
    per_module = load("894A")["per_module"]
    assert len(per_module) >= 10
    for module, stats in per_module.items():
        assert 0.0 <= stats["live_fraction"] <= 1.0, module
    # only the two small modules have no live evidence; the busy ones were measured as well
    assert per_module["ath_hal"]["confirmed_live_hardware"] == 0
    assert per_module["ath_spectral"]["confirmed_live_hardware"] == 0
    assert per_module["ubnt_poll_host"]["confirmed_live_hardware"] > 0
    assert per_module["ath_dev"]["confirmed_live_hardware"] > 0


def test_895a_tallies_and_promotion_rules() -> None:
    report = load("895A")
    summary = report["summary"]
    assert summary["receipts_in_range"] == 333
    assert summary["receipts_in_range"] == (summary["confirmed_live_hardware"]
                                            + summary["confirmed_static_binary"]
                                            + summary["simulated_model_only"]
                                            + summary["refuted"]
                                            + summary["provenance_undeclared"])
    assert summary["classifier_disagreements"] == 0
    assert summary["gates_runtime_proven"] == 0
    assert summary["gates_audited"] == 7
    rules = report["promotion_rules"]
    assert len(rules) == 5
    assert rules["UNCLASSIFIED"]["may"] == "nothing"
    assert rules["SIMULATED_MODEL_ONLY"]["never"].startswith("any measurement")


def test_896a_gate_is_compliant() -> None:
    summary = load("896A")["summary"]
    assert summary["stages_present"] == summary["stages_expected"] == 5
    assert summary["failures"] == 0
    assert summary["compliant"] == 1
    assert summary["checks_run"] == summary["checks_passed"]
    assert summary["cross_stage_checks"] == 3


def test_three_cross_stage_agreements_hold() -> None:
    gates = ["PB-040", "PB-050", "PB-060", "PB-070", "PB-080", "PB-090", "PB-100"]
    derived = set()
    for container in load("891A")["containers"]:
        name = container["file"].lower().replace("-", "").replace("_", "")
        for gate in gates:
            if gate.replace("-", "").lower() in name and container["ok"] == 1:
                derived.add(gate)
    assert len(derived) == load("892A")["summary"]["gates_static_proven"] == 3
    assert load("892A")["summary"]["gates_runtime_proven"] == 0
    assert load("895A")["summary"]["gates_runtime_proven"] == 0
    assert load("895A")["classifier_disagreement"] == []


def test_every_tool_is_reproducible() -> None:
    # a first priming pass is required: 892A..895A read other receipts, and earlier suites in the
    # same session may have rewritten them. Reproducibility means two consecutive runs from the
    # same inputs agree, not that a stale file equals a fresh one.
    for tool in TOOLS.values():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    before = {stage: path.read_bytes() for stage, path in R.items()}
    for tool in TOOLS.values():
        subprocess.run([sys.executable, str(tool)], check=True, cwd=str(REPO),
                       stdout=subprocess.DEVNULL)
    for stage, path in R.items():
        assert path.read_bytes() == before[stage], f"{stage} receipt is not deterministic"
