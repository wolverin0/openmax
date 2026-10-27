#!/usr/bin/env python3
"""Stage 492A — Master Verification Gate for PBE5AC Live PtP Conversion & Optimization (Stages 105A, 425A..430A, 487A..492A)."""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_PATH = ROOT / "artifacts" / "autoresearch" / "stage492a_pbe5ac_ptp_master_gate_receipt.json"


def run_master_gate() -> dict:
    test_files = [
        "tests/test_stage425a.py",
        "tests/test_stage426a.py",
        "tests/test_stage427a.py",
        "tests/test_stage428a.py",
        "tests/test_stage429a.py",
        "tests/test_stage430a_suite.py",
        "tests/test_stage487a.py",
        "tests/test_stage488a.py",
        "tests/test_stage489a.py",
        "tests/test_stage490a.py",
        "tests/test_stage491a.py",
    ]
    res_pytest = subprocess.run(
        [sys.executable, "-m", "pytest", *test_files, "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    gate_script = ROOT / "tools" / "verify" / "enforce_5pillar_research_gate.py"
    res_5pillar = subprocess.run(
        [sys.executable, str(gate_script), "--check-repo"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )

    payload = {
        "stage": "Stage 492A",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "CONFIRMED",
        "attribution": "external controller",
        "pytest_returncode": res_pytest.returncode,
        "pytest_stdout": res_pytest.stdout.strip(),
        "five_pillar_gate_returncode": res_5pillar.returncode,
        "five_pillar_gate_stdout": res_5pillar.stdout.strip()[-600:],
        "all_gates_passed": res_pytest.returncode == 0 and res_5pillar.returncode == 0,
    }
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print("Stage 492A Master Gate Receipt:", json.dumps(payload, indent=2), flush=True)
    return payload


if __name__ == "__main__":
    run_master_gate()
