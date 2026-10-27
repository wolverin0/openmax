#!/usr/bin/env python3
"""Sequential executor for Batch 6 (R147..R152) on LAP-120 <-> Loco195."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"


def main() -> None:
    rounds = list(range(147, 153))
    for r in rounds:
        existing = sorted(ART_DIR.glob(f"lap120_loco195_r{r}_*.json"))
        if existing and existing[-1].stat().st_size > 1000:
            print(f"[SKIP] R{r} already completed -> {existing[-1].name}", flush=True)
            continue
        matches = sorted(BENCH_DIR.glob(f"run_live_autoresearch_r{r}_*.py"))
        if not matches:
            raise FileNotFoundError(f"Missing script for R{r}")
        script = matches[0]
        print(f"\n==========================================", flush=True)
        print(f"STARTING R{r}: {script.name} at {time.strftime('%H:%M:%S')}", flush=True)
        print(f"==========================================", flush=True)
        res = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False)
        if res.returncode != 0:
            print(f"[WARN] R{r} exited with code {res.returncode}; retrying once after 3s...", flush=True)
            time.sleep(3)
            res = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=True)
        json_matches = sorted(ART_DIR.glob(f"lap120_loco195_r{r}_*.json"))
        assert json_matches, f"Expected JSON receipt for R{r} in {ART_DIR}"
        print(f"[OK] COMPLETED R{r} -> {json_matches[-1].name}", flush=True)


if __name__ == "__main__":
    main()
