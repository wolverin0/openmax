#!/usr/bin/env python3
"""Stage and execute Batch 10 (R171..R176): Pure 1-Coordinate Single-Knob Ablations (aql_txq_limit dscp=0, VO-only, Stepwise AQL+Quantum, Stepwise AQL+Quantum+CoDel, ct_special_7 only, rts_threshold=256 only) at 6000m (covclass=13)."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"

RUNS = [
    {
        "r": 171,
        "slug": "pure_aql_txq_limit_dscp0_only",
        "factor": "pure_aql_txq_limit_dscp0",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_pure_aql_txq_limit_be1850_dscp0_only",
        description="Pure 1-Coordinate aql_txq_limit Only (BE=1850/3700; Stock aql_threshold=24000, dscp=0, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        be_low_us=1850,
        be_high_us=3700,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_pure_aql_txq_limit_be2400_dscp0_only",
        description="Pure 1-Coordinate aql_txq_limit Only (BE=2400/4800; Stock aql_threshold=24000, dscp=0, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        be_low_us=2400,
        be_high_us=4800,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "off",
    },
    {
        "r": 172,
        "slug": "pure_dscp_vo_steering_stock_aql_only",
        "factor": "pure_dscp_vo_steering",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_pure_dscp_vo_steering_stock_aql_only",
        description="Pure DSCP AC_VO Steering Only with Stock AQL=5000/12000 (dscp=1; Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        dscp_micro_vo_steering=1,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_pure_dscp_vo_steering_stock_aql_only",
        description="Pure DSCP AC_VO Steering Only with Stock AQL=5000/12000 (dscp=1; Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        dscp_micro_vo_steering=1,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "off",
    },
    {
        "r": 173,
        "slug": "stepwise_aql_plus_fq_quantum1514_dscp0",
        "factor": "stepwise_aql_plus_fq_quantum",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_stepwise_aql_be1850_plus_q1514_dscp0",
        description="Stepwise Forward #2: Pure aql_txq_limit (BE=1850/3700) + fq_quantum=1514 with dscp=0 (Stock codel=20/100ms, RC=0, TSQ=Stock)",
        be_low_us=1850,
        be_high_us=3700,
        fq_quantum_bytes=1514,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_stepwise_aql_be2400_plus_q1514_dscp0",
        description="Stepwise Forward #2: Pure aql_txq_limit (BE=2400/4800) + fq_quantum=1514 with dscp=0 (Stock codel=20/100ms, RC=0, TSQ=Stock)",
        be_low_us=2400,
        be_high_us=4800,
        fq_quantum_bytes=1514,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "off",
    },
    {
        "r": 174,
        "slug": "stepwise_aql_plus_q1514_plus_codel10_dscp0",
        "factor": "stepwise_aql_plus_q1514_plus_codel10",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_stepwise_aql_be1850_q1514_codel10_dscp0",
        description="Stepwise Forward #3: Pure aql_txq_limit (BE=1850/3700) + fq_quantum=1514 + codel=10/50ms with dscp=0 (Stock RC=0, TSQ=Stock)",
        be_low_us=1850,
        be_high_us=3700,
        fq_quantum_bytes=1514,
        fq_target_us=10000,
        fq_interval_us=50000,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_stepwise_aql_be2400_q1514_codel10_dscp0",
        description="Stepwise Forward #3: Pure aql_txq_limit (BE=2400/4800) + fq_quantum=1514 + codel=10/50ms with dscp=0 (Stock RC=0, TSQ=Stock)",
        be_low_us=2400,
        be_high_us=4800,
        fq_quantum_bytes=1514,
        fq_target_us=10000,
        fq_interval_us=50000,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "off",
    },
    {
        "r": 175,
        "slug": "pure_ct_special_7_rc_per_thresh24_only",
        "factor": "pure_ct_special_7",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_pure_ct_special_7_rc24_only",
        description="Pure 1-Coordinate ct_special_7 (rc_per_thresh=24) Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, dscp=0, TSQ=Stock)",
        rc_per_thresh=24,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_pure_ct_special_7_rc24_only",
        description="Pure 1-Coordinate ct_special_7 (rc_per_thresh=24) Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, dscp=0, TSQ=Stock)",
        rc_per_thresh=24,
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "off",
    },
    {
        "r": 176,
        "slug": "pure_rts_threshold_256_only",
        "factor": "pure_rts_threshold_256",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_pure_rts_threshold_256_only",
        description="Pure 1-Coordinate rts_threshold=256 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, dscp=0, RC=0, TSQ=Stock)",
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_pure_rts_threshold_256_only",
        description="Pure 1-Coordinate rts_threshold=256 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, dscp=0, RC=0, TSQ=Stock)",
        dscp_micro_vo_steering=0,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            1,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
        "rts_b": "256",
    },
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

    for ab in RUNS:
        r = ab["r"]
        fname = f"run_live_autoresearch_r{r}_{ab['slug']}_bidir_8flow_voip_covclass13_6000m_abba16_dyadic_zero_loss_wds_n160_20261024.py"
        fpath = BENCH_DIR / fname
        src = r141_src
        src = src.replace(OLD_STATE_BLOCK, ab["ap_state_block"])
        src = src.replace(OLD_ARM_B_TUPLE, "            " + ab["arm_b_tuple"])
        src = src.replace("141", str(r))
        src = src.replace("covclass2", "covclass13")
        src = src.replace("COVCLASS2", "COVCLASS13")
        src = src.replace("coverage 2", "coverage 13")
        src = src.replace("coverage_class=2", "coverage_class=13")
        src = src.replace('"coverage_class": 2', '"coverage_class": 13')
        src = src.replace("1000m", "6000m")
        src = src.replace("1000M", "6000M")
        src = src.replace("1000 m", "6000 m")
        src = src.replace("1.0 km", "6.0 km")
        src = src.replace("1.0km", "6.0km")
        src = src.replace('"distance_m": 1000', '"distance_m": 6000')
        src = src.replace("slot_time_us=15", "slot_time_us=48")
        src = src.replace("slot=15us", "slot=48us")
        src = src.replace('"slot_time_us": 15', '"slot_time_us": 48')
        src = src.replace("ack_timeout_us=36", "ack_timeout_us=69")
        src = src.replace("ACK=36us", "ACK=69us")
        src = src.replace('"ack_timeout_us": 36', '"ack_timeout_us": 69')
        src = src.replace('echo "3 32" >', f'echo "3 {ab["ampdu"]}" >')
        if ab["rts_b"] != "off":
            src = src.replace(
                'echo "3 64" > /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu 2>/dev/null || true\nfi',
                f'echo "3 64" > /sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu 2>/dev/null || true\nfi\nif [ "{{force_tx_status}}" = "1" ]; then iw phy phy0 set rts {ab["rts_b"]} 2>/dev/null || true; else iw phy phy0 set rts off 2>/dev/null || true; fi',
            )
        src = src.replace(
            "hmac_be1550_2100_q1514_codel8_rc24_af1_fql2048_ftx1_retry64",
            ab["slug"],
        )
        src = src.replace(
            "hmac_per_peer_tid_bidir_8flow_voip_covclass13_6000m_be1550_2100_q1514_codel8_rc24_af1_retry64",
            f"{ab['slug']}_bidir_8flow_voip_covclass13_6000m",
        )
        fpath.write_text(src, encoding="utf-8")
        py_compile.compile(str(fpath), doraise=True)
        print(f"STAGED R{r} ({ab['factor']}): {fname}", flush=True)


def run_all() -> None:
    stage_all()
    for ab in RUNS:
        r = ab["r"]
        existing = sorted(ART_DIR.glob(f"lap120_loco195_r{r}_*.json"))
        if existing and existing[-1].stat().st_size > 1000:
            print(f"[SKIP] R{r} already completed -> {existing[-1].name}", flush=True)
            continue
        script = sorted(BENCH_DIR.glob(f"run_live_autoresearch_r{r}_*.py"))[0]
        print(f"\n==========================================", flush=True)
        print(f"STARTING R{r} ({ab['factor']}): {script.name} at {time.strftime('%H:%M:%S')}", flush=True)
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
