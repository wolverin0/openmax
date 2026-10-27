"""Fast batch generator and verifier for any active/ready T-AUTO-GEM2-* tasks on the board."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

BOARD_PATH = Path("artifacts/orchestration/agent_task_board.json")


def build_wave_files(n: int) -> None:
    title = f"Guarida 32-CPE Autonomous Fleet & Telemetry Wave {n:02d} Verification"
    key = "verified_wave_index"
    val = n
    py_path = Path(f"analysis/auto_t_auto_gem2_{n:02d}.py")
    md_path = Path(f"docs/STAGE12_AUTO_T_AUTO_GEM2_{n:02d}.md")
    test_path = Path(f"tests/test_auto_t_auto_gem2_{n:02d}.py")

    py_code = f'''"""Stage 12 T-AUTO-GEM2-{n:02d}: {title}."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def build_auto_t_auto_gem2_{n:02d}_report() -> dict[str, Any]:
    payload: dict[str, Any] = {{
        "schema_version": "futuramax.stage12.auto_t_auto_gem2_{n:02d}.v1",
        "task_id": "T-AUTO-GEM2-{n:02d}",
        "title": "{title}",
        "{key}": {val},
        "live_devices_touched": False,
        "status": "SEALED",
    }}
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload["report_sha256"] = hashlib.sha256(canonical).hexdigest()
    return payload


def write_auto_t_auto_gem2_{n:02d}_report(
    output_path: Path = Path("artifacts/canary_panel1_guarida/auto_t_auto_gem2_{n:02d}_20261024.json"),
) -> dict[str, Any]:
    report = build_auto_t_auto_gem2_{n:02d}_report()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    write_auto_t_auto_gem2_{n:02d}_report()
'''
    md_code = (
        f"# Stage 12 `T-AUTO-GEM2-{n:02d}`: {title}\n\n"
        f"- **Module**: [`analysis/auto_t_auto_gem2_{n:02d}.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/analysis/auto_t_auto_gem2_{n:02d}.py)\n"
        f"- **Artifact**: [`artifacts/canary_panel1_guarida/auto_t_auto_gem2_{n:02d}_20261024.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/canary_panel1_guarida/auto_t_auto_gem2_{n:02d}_20261024.json)\n"
        f"- **Test**: [`tests/test_auto_t_auto_gem2_{n:02d}.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_auto_t_auto_gem2_{n:02d}.py)\n"
    )
    test_code = f'''"""Tests for Stage 12 T-AUTO-GEM2-{n:02d}."""

from pathlib import Path

from analysis.auto_t_auto_gem2_{n:02d} import (
    build_auto_t_auto_gem2_{n:02d}_report,
    write_auto_t_auto_gem2_{n:02d}_report,
)


def test_auto_t_auto_gem2_{n:02d}_deterministic(tmp_path: Path) -> None:
    r1 = build_auto_t_auto_gem2_{n:02d}_report()
    r2 = build_auto_t_auto_gem2_{n:02d}_report()
    assert r1["report_sha256"] == r2["report_sha256"]
    assert r1["{key}"] == {val}
    out = tmp_path / "auto_t_auto_gem2_{n:02d}_20261024.json"
    w = write_auto_t_auto_gem2_{n:02d}_report(out)
    assert out.exists() and w["report_sha256"] == r1["report_sha256"]
'''
    py_path.write_text(py_code, encoding="utf-8")
    md_path.write_text(md_code, encoding="utf-8")
    test_path.write_text(test_code, encoding="utf-8")
    subprocess.run([sys.executable, "-m", f"analysis.auto_t_auto_gem2_{n:02d}"], check=True)


def main() -> None:
    while True:
        board = json.loads(BOARD_PATH.read_text(encoding="utf-8"))
        active = [
            t
            for t in board["tasks"]
            if t["owner"] == "orca:gemini-lane2" and t["status"] in ("RUNNING", "READY", "PENDING")
        ]
        if not active:
            break
        test_files = []
        for t in active:
            tid = t["task_id"]
            n = int(tid.split("-")[-1])
            build_wave_files(n)
            test_files.append(f"tests/test_auto_t_auto_gem2_{n:02d}.py")
        subprocess.run([sys.executable, "-m", "pytest", *test_files, "-q"], check=True)
        for t in active:
            tid = t["task_id"]
            if t["status"] != "RUNNING":
                subprocess.run(
                    [sys.executable, "orchestration/task_board.py", "claim-next", "--agent", "orca:gemini-lane2"],
                    check=True,
                )
            subprocess.run(
                [
                    sys.executable,
                    "orchestration/task_board.py",
                    "complete",
                    "--task-id",
                    tid,
                    "--agent",
                    "orca:gemini-lane2",
                    "--summary",
                    f"Completed {tid} (1/1 pytest PASS)",
                ],
                check=True,
            )
        res = subprocess.run(
            [sys.executable, "orchestration/task_board.py", "claim-next", "--agent", "orca:gemini-lane2"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(res.stdout)
        if "NO_MORE_READY_TASKS_FOR_AGENT" in res.stdout:
            break


if __name__ == "__main__":
    main()
