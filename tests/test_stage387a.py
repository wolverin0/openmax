"""Stage 387A — regression tests.

The stage is mostly a refutation, and the tests are built to keep it that way:

  * the dense slot array of 372A has grown to 432 entries, so 0x9064 and 0x9070 are slots 25 and
    28 — `id_hits_outside_dense_run` must stay 0;
  * the claimed jump-table address must stay outside every segment window;
  * the real positives (the `WMI_UBNT_*` namespace and the two handler symbols) are pinned so a
    later run cannot lose them.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "re" / "qca988x_wmi_0x9064_51entry_jump_table_re.py"
RECEIPT = (REPO / "artifacts" / "autoresearch"
           / "stage387a_qca988x_wmi_0x9064_jump_table_re.json")

SLOT_START = 0x239F70
SLOT_STRIDE = 8


@pytest.fixture(scope="module")
def report() -> dict:
    assert RECEIPT.exists(), f"missing: {RECEIPT}"
    return json.loads(RECEIPT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ok(report: dict) -> list[dict]:
    return [r for r in report["modules"] if r.get("status") == "ok"]


@pytest.fixture(scope="module")
def umac(ok: list[dict]) -> dict:
    return next(r for r in ok if r["module"].endswith("umac.ko"))


@pytest.fixture(scope="module")
def poll(ok: list[dict]) -> dict:
    return next(r for r in ok if r["module"].endswith("ubnt_poll_host.ko"))


def test_receipt_shape(report: dict) -> None:
    assert report["meta"]["stage"] == "387A"
    for k in ("meta", "container", "address_windows", "dense_slot_arrays", "modules",
              "summary", "gaps", "subcommands"):
        assert k in report
    assert report["meta"]["target_address"] == "0x009b2037"
    assert report["meta"]["target_jump"] == "0x009b5c02"


def test_target_outside_every_window(report: dict) -> None:
    s = report["summary"]
    assert s["target_in_any_window"] == 0
    assert s["jump_in_any_window"] == 0
    assert s["bytes_past_nearest_window"] == 7318
    wins = report["address_windows"]
    assert len(wins) == 4
    assert all(w["contains_target"] is False for w in wins)
    # the widest window is segment 3 read little-endian
    widest = max(wins, key=lambda w: int(w["hi"], 16))
    assert widest["hi"] == "0x009b03a1"
    assert widest["endian"] == "le"


def test_dense_slot_array(report: dict) -> None:
    arrays = report["dense_slot_arrays"]
    assert len(arrays) == 1
    a = arrays[0]
    assert a["start"] == "0x239f70"
    assert a["count"] == 432
    assert a["trailing"] == "00000102"
    assert report["summary"]["dense_slot_arrays"] == 1


def test_ids_are_inside_the_dense_run(report: dict, umac: dict) -> None:
    for ident, slot in (("0x9064", 25), ("0x9070", 28)):
        rec = umac["ids"][ident]
        assert rec["aligned"] == 1
        assert rec["outside_dense_run"] == 0
        c = rec["classified"][0]
        assert c["in_dense_slot_array"] is True
        assert c["slot_index"] == slot
        assert int(c["at"], 16) == SLOT_START + SLOT_STRIDE * slot
    assert report["summary"]["id_hits_outside_dense_run"] == 0
    assert report["summary"]["aligned_id_hits"] == 2


def test_blob_has_no_usable_id(report: dict) -> None:
    ids = report["blob_ids"]
    assert ids["0x9064"] == {"be": 0, "le": 0}
    assert ids["0x9070"] == {"be": 0, "le": 1}


def test_wmi_ubnt_namespace_is_real(umac: dict) -> None:
    assert umac["name_probes"]["WMI_UBNT"] == 6
    ctx = " ".join(umac["name_contexts"]["WMI_UBNT"])
    assert "WMI_UBNT_POLL_CMDID" in ctx
    assert "WMI_UBNT_STATS_EVENTID" in ctx
    assert "WMI_UBNT_PEER_ADD_EVENTID" in ctx


def test_single_tunnel_symbol_does_not_exist(umac: dict, report: dict) -> None:
    # WMI_UBNT_CMDID is not one of the enumerated names
    assert umac["name_probes"]["UBNT_CMDID"] == 0
    ctx = " ".join(umac["name_contexts"]["WMI_UBNT"])
    assert "WMI_UBNT_CMDID" not in ctx
    assert report["blob_name_probes"].get("WMI_UBNT", 0) == 0


def test_handlers_are_real_symbols_in_poll_host(poll: dict) -> None:
    assert poll["name_probes"]["set_txq_param"] == 1
    assert poll["name_probes"]["set_rate_override"] == 1
    txq = " ".join(poll["name_contexts"]["set_txq_param"])
    rate = " ".join(poll["name_contexts"]["set_rate_override"])
    assert "ubnt_poll_host_set_txq_param" in txq
    assert "ubnt_poll_host_set_rate_override" in rate
    # and they are not in umac.ko
    assert poll["module"] != "WA:umac.ko"


def test_no_jump_table_recovered(report: dict) -> None:
    s = report["summary"]
    assert s["jump_table_recovered"] == 0
    assert s["pointer_runs_51plus"] == 0
    for seg, runs in report["blob_pointer_runs"].items():
        assert len(runs) == 0, (seg, runs)


def test_subcommands_declared_but_not_bound(report: dict) -> None:
    subs = {s["id"]: s["name"] for s in report["subcommands"]}
    assert subs == {"0x17": "set_txq_param", "0x1e": "set_rate_override"}
    # declared by the stage, not proven by the receipt
    joined = " ".join(report["gaps"])
    assert "opcode" in joined


def test_radio_safety(report: dict) -> None:
    scope = report["meta"]["scope"]
    for phrase in ("no firmware loaded", "no module loaded", "no radio contacted"):
        assert phrase in scope


def test_tool_is_reproducible() -> None:
    before = RECEIPT.read_bytes()
    subprocess.run([sys.executable, str(TOOL)], check=True, cwd=str(REPO),
                   stdout=subprocess.DEVNULL)
    assert RECEIPT.read_bytes() == before
