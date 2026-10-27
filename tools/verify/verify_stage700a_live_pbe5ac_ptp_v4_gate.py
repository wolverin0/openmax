#!/usr/bin/env python3
"""Stage 700A — Live PowerBeam 5AC Gen2 PtP Champion v4 700-Stage Consolidated Gate.

Verifies the live receipts Stages 695A..699A (CONFIRMED + required invariants),
runs their pytest suite and the repo-wide 5-pillar gate, and writes a single
consolidated receipt. 100% offline: reads existing receipts, touches no radio.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts" / "autoresearch"
RECEIPT_PATH = ART / "stage700a_live_pbe5ac_ptp_v4_gate_receipt.json"

# (receipt filename, required top-level assertions as (dotted_key, expected_value))
REQUIRED_RECEIPTS: List[Dict[str, Any]] = [
    {
        "file": "stage695a_live_pbe5ac_vht40_pb040_pb050_champion_v4.json",
        "checks": [("status", "CONFIRMED"), ("vht40_clean_associated", True),
                   ("ap_241_pb040_pb050_active", True)],
    },
    {
        "file": "stage696a_live_pbe5ac_mk1_251_e2e_vht40_pb050_triple_play.json",
        "checks": [("status", "CONFIRMED"), ("ap_wds_vlan_active", True),
                   ("sta_4addr_wds_active", True)],
    },
    {
        "file": "stage697a_pbe5ac_dynamic_phy_and_sgmt_loader_v4.json",
        "checks": [("status", "CONFIRMED"), ("deployed_on_241_and_242", True),
                   ("watchdog_non_dfs_s", 45), ("watchdog_dfs_s", 120)],
    },
    {
        "file": "stage698a_pbe5ac_lbe5ac_tester_release_package_v4.json",
        "checks": [("status", "CONFIRMED")],
    },
    {
        "file": "stage699a_pbe5ac_ptp_complete_evolution_ledger_v4.json",
        "checks": [("status", "CONFIRMED"), ("total_ptp_stages_completed", 25)],
    },
]

PYTEST_FILES = [
    "tests/test_stage695a.py",
    "tests/test_stage696a.py",
    "tests/test_stage697a.py",
    "tests/test_stage698a.py",
    "tests/test_stage699a.py",
]


def _get(d: Dict[str, Any], dotted: str) -> Any:
    cur: Any = d
    for part in dotted.split("."):
        cur = cur[part]
    return cur


def verify_receipts() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    all_ok = True
    for spec in REQUIRED_RECEIPTS:
        p = ART / spec["file"]
        entry: Dict[str, Any] = {"file": spec["file"], "exists": p.exists(), "failures": []}
        if not p.exists():
            entry["ok"] = False
            all_ok = False
            results.append(entry)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        for key, expected in spec["checks"]:
            try:
                actual = _get(d, key)
            except (KeyError, TypeError):
                actual = "<missing>"
            if actual != expected:
                entry["failures"].append({"key": key, "expected": expected, "actual": actual})
        entry["ok"] = not entry["failures"]
        all_ok = all_ok and entry["ok"]
        results.append(entry)
    return {"all_receipts_ok": all_ok, "receipts": results}


def run_stage700a_gate() -> Dict[str, Any]:
    receipt_audit = verify_receipts()

    res_pytest = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST_FILES, "-q"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    res_5pillar = subprocess.run(
        [sys.executable, "tools/verify/enforce_5pillar_research_gate.py", "--check-repo"],
        cwd=str(ROOT), capture_output=True, text=True,
    )

    all_gates = (
        receipt_audit["all_receipts_ok"]
        and res_pytest.returncode == 0
        and res_5pillar.returncode == 0
    )
    payload = {
        "stage": "Stage 700A",
        "milestone": "700-Stage Milestone & Live PtP Champion v4 Consolidated Gate (Stages 695A..700A)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if all_gates else "FAILED",
        "attribution": "external controller",
        "live_devices_touched": False,
        "receipt_audit": receipt_audit,
        "pytest_returncode": res_pytest.returncode,
        "pytest_stdout_tail": res_pytest.stdout.strip().splitlines()[-1:] or [""],
        "five_pillar_gate_returncode": res_5pillar.returncode,
        "all_gates_passed": all_gates,
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("[Stage 700A] Gate:", json.dumps(
        {k: payload[k] for k in ("status", "all_gates_passed", "pytest_returncode",
                                 "five_pillar_gate_returncode")}, indent=2), flush=True)
    if not all_gates:
        print("[Stage 700A] receipt_audit:", json.dumps(receipt_audit, indent=2), flush=True)
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    run_stage700a_gate()
