#!/usr/bin/env python3
"""Stage and execute Batch 12 (R183..R188): Pure 1-Coordinate aql_txq_limit ONLY (dscp=0, all other knobs Stock) Distance Sweep across 1km..14km."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"

SPECS_B12 = [
    {"r": 183, "cov": 2, "dist": 1000, "dist_km": "1.0", "slot_us": 15, "ack_us": 36, "ap_be": 1650, "cpe_be": 2150},
    {"r": 184, "cov": 6, "dist": 3000, "dist_km": "3.0", "slot_us": 27, "ack_us": 48, "ap_be": 1750, "cpe_be": 2250},
    {"r": 185, "cov": 13, "dist": 6000, "dist_km": "6.0", "slot_us": 48, "ack_us": 69, "ap_be": 1850, "cpe_be": 2400},
    {"r": 186, "cov": 20, "dist": 9000, "dist_km": "9.0", "slot_us": 69, "ack_us": 90, "ap_be": 1950, "cpe_be": 2500},
    {"r": 187, "cov": 26, "dist": 12000, "dist_km": "12.0", "slot_us": 87, "ack_us": 108, "ap_be": 2050, "cpe_be": 2650},
    {"r": 188, "cov": 31, "dist": 14000, "dist_km": "14.0", "slot_us": 102, "ack_us": 123, "ap_be": 2150, "cpe_be": 2750},
]

OLD_STATE_BLOCK = """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_hmac_be1550_q1514_codel8_rc24_tsq512k_end",
        description="AP Coarse hMAC Per-Peer/TID Gate (VO=500/1100 TOS 0xb8 EF slice, VI=500/1100, BE=1550/3100, thresh=6200, fq_quantum=1514, flows=1024, codel=8/40ms, RC=24%, TSQ=512/128KB, DSCP=1)",
        vo_low_us=500,
        vo_high_us=1100,
        vi_low_us=500,
        vi_high_us=1100,
        be_low_us=1550,
        be_high_us=3100,
        bk_low_us=500,
        bk_high_us=1100,
        aql_threshold_us=6200,
        fq_quantum_bytes=1514,
        fq_target_us=8000,
        fq_interval_us=40000,
        rc_per_thresh=24,
        dscp_micro_vo_steering=1,
        tcp_limit_output_bytes=524288,
        tcp_notsent_lowat=131072,
        complexity_cost=2,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_hmac_be2100_q1514_codel8_rc24_tsq512k_end",
        description="CPE Coarse hMAC Per-Peer/TID Gate (VO=500/1100 TOS 0xb8 EF slice, VI=700/1500, BE=2100/4200, thresh=8400, fq_quantum=1514, flows=1024, codel=8/40ms, RC=24%, TSQ=512/128KB, DSCP=1)",
        vo_low_us=500,
        vo_high_us=1100,
        vi_low_us=700,
        vi_high_us=1500,
        be_low_us=2100,
        be_high_us=4200,
        bk_low_us=500,
        bk_high_us=1100,
        aql_threshold_us=8400,
        fq_quantum_bytes=1514,
        fq_target_us=8000,
        fq_interval_us=40000,
        rc_per_thresh=24,
        dscp_micro_vo_steering=1,
        tcp_limit_output_bytes=524288,
        tcp_notsent_lowat=131072,
        complexity_cost=2,
    )"""

OLD_ARM_B_TUPLE = """            1,
            2048,
            1,
            6,
            4,
            1024,"""


def stage_all() -> None:
    r141_path = next(BENCH_DIR.glob("run_live_autoresearch_r141_*.py"))
    r141_src = r141_path.read_text(encoding="utf-8")

    for sp in SPECS_B12:
        r = sp["r"]
        ap_be = sp["ap_be"]
        ap_high = ap_be * 2
        cpe_be = sp["cpe_be"]
        cpe_high = cpe_be * 2
        slug = f"pure_aql_txq_limit_only_dscp0_be{ap_be}_{cpe_be}"
        fname = (
            f"run_live_autoresearch_r{r}_{slug}_bidir_8flow_"
            f"covclass{sp['cov']}_{sp['dist']}m_abba16_dyadic_zero_loss_wds_n160_20261024.py"
        )
        fpath = BENCH_DIR / fname
        new_state_block = f"""    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_pure_aql_txq_limit_be{ap_be}_dscp0_only",
        description="Pure 1-Coordinate aql_txq_limit Only at {sp['dist']}m (BE={ap_be}/{ap_high}; Stock aql_threshold=24000, dscp=0, fq_quantum=300, codel=20/100ms, af=3, fq_limit=8192, retry=4/4, RC=0, TSQ=Stock)",
        be_low_us={ap_be},
        be_high_us={ap_high},
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_pure_aql_txq_limit_be{cpe_be}_dscp0_only",
        description="Pure 1-Coordinate aql_txq_limit Only at {sp['dist']}m (BE={cpe_be}/{cpe_high}; Stock aql_threshold=24000, dscp=0, fq_quantum=300, codel=20/100ms, af=3, fq_limit=8192, retry=4/4, RC=0, TSQ=Stock)",
        be_low_us={cpe_be},
        be_high_us={cpe_high},
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )"""
        src = r141_src
        src = src.replace(OLD_STATE_BLOCK, new_state_block)
        src = src.replace(OLD_ARM_B_TUPLE, "            3,\n            8192,\n            0,\n            4,\n            4,\n            4096,")
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
        src = src.replace('echo "3 32" >', 'echo "3 64" >')
        src = src.replace("hmac_be1550_2100_q1514_codel8_rc24_af1_fql2048_ftx1_retry64", slug)
        fpath.write_text(src, encoding="utf-8")
        py_compile.compile(str(fpath), doraise=True)
        print(f"STAGED R{r}: {fname}", flush=True)


def run_all() -> None:
    stage_all()
    for sp in SPECS_B12:
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
