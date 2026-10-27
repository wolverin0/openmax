"""Stage 809A — regression tests.

Pins the projection label, the three roles, the degenerate front, and the two independent gates that
authorise nothing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "sim"
        / "run_stage809a_pb040_to_pb070_quad_patch_pareto.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage809a_pb040_to_pb070_quad_patch_pareto.json")


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "809A"
    for k in ("meta", "inputs", "roles", "pareto_front", "dominated", "gates", "summary"):
        assert k in report
    assert "PROJECTION" in report["meta"]["label"]


def test_three_roles_not_four(report: dict) -> None:
    s = report["summary"]
    assert s["roles_parsed"] == 3
    assert len(report["roles"]) == 3


def test_front_is_degenerate_but_complete(report: dict) -> None:
    s = report["summary"]
    assert s["pareto_front_size"] == 1
    assert s["dominated_count"] == 2
    assert s["pareto_front_size"] + s["dominated_count"] == s["roles_parsed"]
    assert report["pareto_front"][0]["role"] == "athwlan_AR9888v2_ptmp_sta_bin"
    assert report["pareto_front"][0]["cost"] == 4


def test_costs(report: dict) -> None:
    s = report["summary"]
    assert s["total_cost_bytes"] == 12
    assert s["front_cost_bytes"] == 4
    assert s["cost_fraction_on_front"] == 0.3333
    for r in report["roles"]:
        assert r["cost"] == 4


def test_nothing_authorised(report: dict) -> None:
    s = report["summary"]
    assert s["all_roles_blocked"] == 1
    assert s["execution_authorised"] == 0
    g = report["gates"]
    assert g["spi_flash_write_allowed"] is False
    assert g["pb070_ready"] is False
    assert g["operator_gate_required"] is True


def test_labelled_as_projection(report: dict) -> None:
    s = report["summary"]
    assert s["measurement_or_projection"] == "projection"
    assert "PROJECTION" in report["meta"]["label"]
    joined = " ".join(report["gaps"])
    assert "not a measurement" in joined


def test_inputs_are_sha_pinned(report: dict) -> None:
    for key in ("pb040", "pb060_070"):
        assert len(report["inputs"][key]["sha256"]) == 64


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "static" in scope
    assert "no firmware" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
