"""Stage 437A — regression tests.

Pins the three absences (both firmware images and ath10k_core.ko), the zero WMI-name hits, the real
per-peer knob set with getters, the NSS bound at 3, and the refusal to upgrade FMX-DISC-40 from
inferred to confirmed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = (REPO / "tools" / "re"
        / "build_stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.py")
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage437a_qca988x_wmi_chainmask_stbc_ldpc_per_peer_re.json")

UMAC_PEER = {"nss": 4, "NSS": 5, "stbc": 4, "ldpc": 2, "vhtmcs": 2, "1x1": 2, "2x2": 2}


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def by(ok: list[dict]) -> dict[str, dict]:
    return {r["module"]: r for r in ok}


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "437A"
    for k in ("meta", "named_files", "modules", "summary", "gaps"):
        assert k in report
    assert report["meta"]["wmi_ids"] == {"TX_CHAIN_MASK": "0x43", "RX_CHAIN_MASK": "0x44"}
    assert len(report["meta"]["premise_corrections"]) == 2


def test_all_three_sources_absent(report: dict) -> None:
    assert report["named_files"] == {"firmware-2.bin": 0, "firmware-5.bin": 0,
                                     "ath10k_core.ko": 0}
    assert report["summary"]["named_files_present"] == 0


def test_wmi_names_do_not_exist(report: dict, ok: list[dict]) -> None:
    assert report["summary"]["wmi_name_hits"] == 0
    assert report["summary"]["wmi_names_absent"] is True
    for r in ok:
        for tok in ("PDEV_PARAM", "VDEV_PARAM", "TX_CHAIN_MASK", "RX_CHAIN_MASK",
                    "CHAIN_MASK", "FIXED_RATE", "spatial"):
            assert r["wmi_names"][tok] == 0, (r["module"], tok)
    assert report["summary"]["wmi_id_to_name_map"] == 0


def test_per_peer_knobs_are_real(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["modules_ok"] == 4
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        u = by[f"{ver}:umac.ko"]
        assert u["peer"] == UMAC_PEER
        assert u["bytes"] > 2_000_000
    assert report["summary"]["nss_hits"] == 10
    assert report["summary"]["stbc_hits"] == 18
    assert report["summary"]["ldpc_hits"] == 4


def test_stbc_also_lives_in_ath_dev(by: dict[str, dict]) -> None:
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        dev = by[f"{ver}:ath_dev.ko"]
        assert dev["peer"]["stbc"] == 5
        assert dev["peer"]["nss"] == 0
        assert dev["bytes"] == 287216


def test_getters_make_fields_readable(by: dict[str, dict], report: dict) -> None:
    assert report["summary"]["getter_hits"] == 6
    assert report["summary"]["modules_with_getters"] == 2
    for ver in ("WA.v8.7.25", "XC.v8.7.25"):
        g = by[f"{ver}:umac.ko"]["getters"]
        assert g["get_nss"] == 1
        assert g["get_ldpc"] == 1
        assert g["get_vhtmcs"] == 1


def test_nss_bound_is_three(ok: list[dict], report: dict) -> None:
    assert report["summary"]["nss_bound_modules"] == 2
    assert report["summary"]["nss_bound_value"] == 3
    for r in ok:
        if r["module"].endswith("umac.ko"):
            assert r["nss_bound_present"] is True
            assert "NSS greater than 3" in " ".join(r["nss_bound_context"])
        else:
            assert r["nss_bound_present"] is False


def test_disc40_is_not_upgraded(report: dict) -> None:
    assert report["summary"]["disc40_verdict"] == "consistent with 0-based indexing, not proven"
    joined = " ".join(report["gaps"])
    assert "does not settle 0-based versus 1-based" in joined
    assert report["summary"]["per_peer_table_recovered"] == 0


def test_both_configurations_are_named(report: dict) -> None:
    assert report["summary"]["one_x_one_strings"] == 4
    assert report["summary"]["two_x_two_strings"] == 4


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    assert "no firmware loaded" in scope
    assert "no radio contacted" in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
