#!/usr/bin/env python3
"""Stage 588A — Consolidated Verification & Pytest Gate (Stages 583A..588A)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
RECEIPT_PATH = ROOT / "artifacts" / "verification" / "stage588a_pbe5ac_ptp_champion_v3_gate_receipt.json"


def run_stage588a_gate() -> Dict[str, Any]:
    pytest_files = [
        "tests/test_stage583a.py",
        "tests/test_stage584a.py",
        "tests/test_stage585a.py",
        "tests/test_stage586a.py",
        "tests/test_stage587a.py",
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
        "stage": "Stage 588A",
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
    print("[Stage 588A] Gate Receipt:", json.dumps(payload, indent=2), flush=True)
    if not payload["all_gates_passed"]:
        raise SystemExit(1)
    return payload


if __name__ == "__main__":
    run_stage588a_gate()
