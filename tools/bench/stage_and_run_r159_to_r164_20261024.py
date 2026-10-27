#!/usr/bin/env python3
"""Stage Batch 8 (R159..R164) Golden-Ratio Coupled AP BE(d) & CPE BE(d) Lockstep Law across 1km..14km."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"

SPECS_B8 = [
    {"r": 159, "cov": 2, "dist": 1000, "dist_km": "1.0", "slot_us": 15, "ack_us": 36, "codel_ms": 8, "interval_ms": 40, "ampdu": 32, "rc": 24, "ap_be": 1650, "cpe_be": 2150},
    {"r": 160, "cov": 6, "dist": 3000, "dist_km": "3.0", "slot_us": 27, "ack_us": 48, "codel_ms": 8, "interval_ms": 40, "ampdu": 32, "rc": 24, "ap_be": 1750, "cpe_be": 2250},
    {"r": 161, "cov": 13, "dist": 6000, "dist_km": "6.0", "slot_us": 48, "ack_us": 69, "codel_ms": 10, "interval_ms": 50, "ampdu": 32, "rc": 24, "ap_be": 1850, "cpe_be": 2400},
    {"r": 162, "cov": 20, "dist": 9000, "dist_km": "9.0", "slot_us": 69, "ack_us": 90, "codel_ms": 12, "interval_ms": 60, "ampdu": 16, "rc": 22, "ap_be": 1950, "cpe_be": 2500},
    {"r": 163, "cov": 26, "dist": 12000, "dist_km": "12.0", "slot_us": 87, "ack_us": 108, "codel_ms": 14, "interval_ms": 70, "ampdu": 16, "rc": 20, "ap_be": 2050, "cpe_be": 2650},
    {"r": 164, "cov": 31, "dist": 14000, "dist_km": "14.0", "slot_us": 102, "ack_us": 123, "codel_ms": 16, "interval_ms": 80, "ampdu": 16, "rc": 20, "ap_be": 2150, "cpe_be": 2750},
]


def stage_all() -> None:
    r141_path = next(BENCH_DIR.glob("run_live_autoresearch_r141_*.py"))
    r141_src = r141_path.read_text(encoding="utf-8")

    for sp in SPECS_B8:
        r = sp["r"]
        ap_be = sp["ap_be"]
        ap_high = ap_be * 2
        ap_thresh = ap_be * 4
        cpe_be = sp["cpe_be"]
        cpe_high = cpe_be * 2
        cpe_thresh = cpe_be * 4
        fname = (
            f"run_live_autoresearch_r{r}_golden_lockstep_ap_be{ap_be}_cpe_be{cpe_be}_hmac_epoch_ampdu{sp['ampdu']}_"
            f"bidir_8flow_voip_covclass{sp['cov']}_{sp['dist']}m_be{ap_be}_{cpe_be}_q1514_"
            f"codel{sp['codel_ms']}_rc{sp['rc']}_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py"
        )
        fpath = BENCH_DIR / fname
        src = r141_src
        src = src.replace("141", str(r))
        src = src.replace("covclass2", f"covclass{sp['cov']}")
        src = src.replace("COVCLASS2", f"COVCLASS{sp['cov']}")
        src = src.replace("coverage 2", f"coverage {sp['cov']}")
        src = src.replace("coverage_class=2", f"coverage_class={sp['cov']}")
        src = src.replace('"coverage_class": 2', f'"coverage_class": {sp["cov"]}')
        src = src.replace("1000m", f"{sp['dist']}m")
        src = src.replace("1000M", f"{sp['dist']}M")
        src = src.replace("1000 m", f"{sp['dist']} m")
        src = src.replace("1.0 km", f"{sp['dist_km']} km")
        src = src.replace("1.0km", f"{sp['dist_km']}km")
        src = src.replace('"distance_m": 1000', f'"distance_m": {sp["dist"]}')
        src = src.replace("slot_time_us=15", f"slot_time_us={sp['slot_us']}")
        src = src.replace("slot=15us", f"slot={sp['slot_us']}us")
        src = src.replace('"slot_time_us": 15', f'"slot_time_us": {sp["slot_us"]}')
        src = src.replace("ack_timeout_us=36", f"ack_timeout_us={sp['ack_us']}")
        src = src.replace("ACK=36us", f"ACK={sp['ack_us']}us")
        src = src.replace('"ack_timeout_us": 36', f'"ack_timeout_us": {sp["ack_us"]}')
        src = src.replace("codel8", f"codel{sp['codel_ms']}")
        src = src.replace("CODEL8", f"CODEL{sp['codel_ms']}")
        src = src.replace("8/40ms", f"{sp['codel_ms']}/{sp['interval_ms']}ms")
        src = src.replace("fq_target_us=8000", f"fq_target_us={sp['codel_ms'] * 1000}")
        src = src.replace("fq_interval_us=40000", f"fq_interval_us={sp['interval_ms'] * 1000}")
        src = src.replace("rc_per_thresh=24", f"rc_per_thresh={sp['rc']}")
        src = src.replace("rc24", f"rc{sp['rc']}")
        src = src.replace("RC24", f"RC{sp['rc']}")
        src = src.replace("RC=24%", f"RC={sp['rc']}%")
        src = src.replace('echo "3 32" >', f'echo "3 {sp["ampdu"]}" >')
        src = src.replace("be_low_us=1550", f"be_low_us={ap_be}")
        src = src.replace("be_high_us=3100", f"be_high_us={ap_high}")
        src = src.replace("aql_threshold_us=6200", f"aql_threshold_us={ap_thresh}")
        src = src.replace("be_low_us=2100", f"be_low_us={cpe_be}")
        src = src.replace("be_high_us=4200", f"be_high_us={cpe_high}")
        src = src.replace("aql_threshold_us=8400", f"aql_threshold_us={cpe_thresh}")
        src = src.replace("be1550_2100", f"be{ap_be}_{cpe_be}")
        src = src.replace("BE1550-2100", f"BE{ap_be}-{cpe_be}")
        src = src.replace("BE=1550/3100", f"BE={ap_be}/{ap_high}")
        src = src.replace("BE=2100/4200", f"BE={cpe_be}/{cpe_high}")
        fpath.write_text(src, encoding="utf-8")
        py_compile.compile(str(fpath), doraise=True)
        print(f"STAGED R{r}: {fname}", flush=True)


def run_all() -> None:
    stage_all()
    for sp in SPECS_B8:
        r = sp["r"]
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
