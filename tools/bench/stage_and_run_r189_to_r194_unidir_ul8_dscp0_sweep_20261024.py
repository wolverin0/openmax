#!/usr/bin/env python3
"""Stage and execute Batch 13 (R189..R194): Unfiltered AC_BE (dscp=0) Heavy 8-Flow Uplink Hammering (unidir_ul_8flow -P 8 -R, rts=off) Distance Sweep across 1km..14km."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"

MAP_B13 = [
    {"src_r": 134, "new_r": 189, "dist": 1000},
    {"src_r": 129, "new_r": 190, "dist": 3000},
    {"src_r": 130, "new_r": 191, "dist": 6000},
    {"src_r": 131, "new_r": 192, "dist": 9000},
    {"src_r": 132, "new_r": 193, "dist": 12000},
    {"src_r": 133, "new_r": 194, "dist": 14000},
]


def stage_all() -> None:
    for item in MAP_B13:
        src_r = item["src_r"]
        new_r = item["new_r"]
        src_path = sorted(BENCH_DIR.glob(f"run_live_autoresearch_r{src_r}_*.py"))[0]
        src_text = src_path.read_text(encoding="utf-8")

        new_name = src_path.name.replace(f"_r{src_r}_", f"_r{new_r}_dscp0_")
        new_path = BENCH_DIR / new_name

        txt = src_text
        txt = txt.replace(f"Round {src_r}", f"Round {new_r}")
        txt = txt.replace(f"LIVE-{src_r}-", f"LIVE-{new_r}-DSCP0-")
        txt = txt.replace(f"TSV_R{src_r}_PATH", f"TSV_R{new_r}_PATH")
        txt = txt.replace(f"JSON_R{src_r}_PATH", f"JSON_R{new_r}_PATH")
        txt = txt.replace(f"lap120_loco195_r{src_r}_", f"lap120_loco195_r{new_r}_dscp0_")
        txt = txt.replace(f"r{src_r}_iter0_", f"r{new_r}_iter0_")
        txt = txt.replace(f"r{src_r}_iter1_", f"r{new_r}_iter1_dscp0_")
        txt = txt.replace(f"[R{src_r} Block", f"[R{new_r} Block")
        txt = txt.replace(f"SAVED_R{src_r}_RECEIPT", f"SAVED_R{new_r}_RECEIPT")
        txt = txt.replace("dscp_micro_vo_steering=1", "dscp_micro_vo_steering=0")
        txt = txt.replace("DSCP=1", "DSCP=0")

        new_path.write_text(txt, encoding="utf-8")
        py_compile.compile(str(new_path), doraise=True)
        print(f"STAGED R{new_r} ({item['dist']}m): {new_name}", flush=True)


def run_all() -> None:
    stage_all()
    for item in MAP_B13:
        r = item["new_r"]
        existing = sorted(ART_DIR.glob(f"lap120_loco195_r{r}_*.json"))
        if existing and existing[-1].stat().st_size > 1000:
            print(f"[SKIP] R{r} already completed -> {existing[-1].name}", flush=True)
            continue
        script = sorted(BENCH_DIR.glob(f"run_live_autoresearch_r{r}_*.py"))[0]
        print(f"\n==========================================", flush=True)
        print(f"STARTING R{r}: {script.name} at {time.strftime('%H:%M:%S')}", flush=True)
        print(f"==========================================", flush=True)
        res = subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=False)
        if res.returncode != 0:
            time.sleep(3)
            subprocess.run([sys.executable, str(script)], cwd=str(ROOT), check=True)
        json_matches = sorted(ART_DIR.glob(f"lap120_loco195_r{r}_*.json"))
        assert json_matches, f"Expected JSON receipt for R{r}"
        print(f"[OK] COMPLETED R{r} -> {json_matches[-1].name}", flush=True)


if __name__ == "__main__":
    run_all()
