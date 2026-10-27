#!/usr/bin/env python3
"""Stage 700A — 700-Stage Milestone & PtP Champion v4 Master Verification Gate (Stages 695A..700A)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
RECEIPT_PATH = ROOT / "artifacts" / "verification" / "stage700a_pbe5ac_ptp_champion_v4_700stage_gate_receipt.json"


def run_stage700a_gate() -> Dict[str, Any]:
    pytest_files = [
        "tests/test_stage425a_to_430a_suite.py",
        "tests/test_stage487a_to_492a_suite.py",
        "tests/test_stage583a_to_588a_pbe5ac_v3_suite.py",
        "tests/test_stage695a.py",
        "tests/test_stage696a.py",
        "tests/test_stage697a.py",
        "tests/test_stage698a.py",
        "tests/test_stage699a.py",
    ]
    res_pytest = subprocess.run(
        [sys.executable, "-m", "pytest", *pytest_files, "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    res_5pillar = subprocess.run(
        [sys.executable, "tools/verify/enforce_5pillar_research_gate.py", "--check-repo"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    payload = {
        "stage": "Stage 700A",
        "milestone": "700-Stage Milestone & PtP Champion v4 Master Gate",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIRMED" if (res_pytest.returncode == 0 and res_5pillar.returncode == 0) else "FAILED",
        "attribution": "external controller",
        "pytest_returncode": res_pytest.returncode,
        "pytest_stdout": res_pytest.stdout.strip(),
        "five_pillar_gate_returncode": res_5pillar.returncode,
        "five_pillar_gate_stdout": res_5pillar.stdout.strip(),
        "all_gates_passed": (res_pytest.returncode == 0 and res_5pillar.returncode == 0),
    }
    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("[Stage 700A] Gate Receipt:", json.dumps(payload, indent=2), flush=True)
    if not payload["all_gates_passed"]:
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    run_stage700a_gate()
