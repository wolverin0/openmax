#!/usr/bin/env python3
"""Stage and execute Batch 9 (R165..R170): Orthogonal Single-Factor (1-Knob-at-a-Time) Causal Ablations at 6000m (covclass=13)."""

from __future__ import annotations

import py_compile
import subprocess
import sys
import time
from pathlib import Path

BENCH_DIR = Path(__file__).resolve().parent
ROOT = BENCH_DIR.parent.parent
ART_DIR = ROOT / "artifacts" / "autoresearch"

ABLATIONS = [
    {
        "r": 165,
        "slug": "isolated_aql_txq_limit_only",
        "factor": "aql_txq_limit",
        "desc": "Single-Factor Causal Ablation #1: ONLY aql_txq_limit/aql_threshold varied (AP BE=1850/3700, CPE BE=2400/4800, VO=500/1100); all other knobs held at Stock (fq_quantum=300, codel=20/100ms, af=3, fq_limit=8192, ftx=0, retry=4/4, ampdu=64, TSQ=Stock)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_aql_be1850_only",
        description="Isolated Single-Factor AP AQL Only (VO=500/1100, VI=500/1100, BE=1850/3700, thresh=7400; Stock fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        vo_low_us=500,
        vo_high_us=1100,
        vi_low_us=500,
        vi_high_us=1100,
        be_low_us=1850,
        be_high_us=3700,
        bk_low_us=500,
        bk_high_us=1100,
        aql_threshold_us=7400,
        dscp_micro_vo_steering=1,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_aql_be2400_only",
        description="Isolated Single-Factor CPE AQL Only (VO=500/1100, VI=700/1500, BE=2400/4800, thresh=9600; Stock fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        vo_low_us=500,
        vo_high_us=1100,
        vi_low_us=700,
        vi_high_us=1500,
        be_low_us=2400,
        be_high_us=4800,
        bk_low_us=500,
        bk_high_us=1100,
        aql_threshold_us=9600,
        dscp_micro_vo_steering=1,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
    },
    {
        "r": 166,
        "slug": "isolated_fq_quantum_1514_only",
        "factor": "fq_quantum",
        "desc": "Single-Factor Causal Ablation #2: ONLY fq_quantum=1514 varied; all other knobs held at Stock (AQL=5000/12000, codel=20/100ms, af=3, fq_limit=8192, ftx=0, retry=4/4, ampdu=64, TSQ=Stock)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_fq_quantum_1514_only",
        description="Isolated Single-Factor fq_quantum=1514 Only (Stock AQL=5000/12000, codel=20/100ms, RC=0, TSQ=Stock)",
        fq_quantum_bytes=1514,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_fq_quantum_1514_only",
        description="Isolated Single-Factor fq_quantum=1514 Only (Stock AQL=5000/12000, codel=20/100ms, RC=0, TSQ=Stock)",
        fq_quantum_bytes=1514,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
    },
    {
        "r": 167,
        "slug": "isolated_codel_target10_interval50_only",
        "factor": "codel_target_interval",
        "desc": "Single-Factor Causal Ablation #3: ONLY codel_target=10ms & codel_interval=50ms varied; all other knobs held at Stock (AQL=5000/12000, fq_quantum=300, af=3, fq_limit=8192, ftx=0, retry=4/4, ampdu=64, TSQ=Stock)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_codel_10_50ms_only",
        description="Isolated Single-Factor CoDel target=10ms/interval=50ms Only (Stock AQL=5000/12000, fq_quantum=300, RC=0, TSQ=Stock)",
        fq_target_us=10000,
        fq_interval_us=50000,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_codel_10_50ms_only",
        description="Isolated Single-Factor CoDel target=10ms/interval=50ms Only (Stock AQL=5000/12000, fq_quantum=300, RC=0, TSQ=Stock)",
        fq_target_us=10000,
        fq_interval_us=50000,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
    },
    {
        "r": 168,
        "slug": "isolated_airtime_flags_1_only",
        "factor": "airtime_flags",
        "desc": "Single-Factor Causal Ablation #4: ONLY airtime_flags=1 varied; all other knobs held at Stock (AQL=5000/12000, fq_quantum=300, codel=20/100ms, fq_limit=8192, ftx=0, retry=4/4, ampdu=64, TSQ=Stock)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_airtime_flags_1_only",
        description="Isolated Single-Factor airtime_flags=1 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_airtime_flags_1_only",
        description="Isolated Single-Factor airtime_flags=1 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        complexity_cost=1,
    )""",
        "arm_b_tuple": "1,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
    },
    {
        "r": 169,
        "slug": "isolated_htt_aggr_size_ampdu32_only",
        "factor": "htt_aggr_size",
        "desc": "Single-Factor Causal Ablation #5: ONLY htt_aggr_size (htt_max_amsdu_ampdu = 3 32) varied; all other knobs held at Stock (AQL=5000/12000, fq_quantum=300, codel=20/100ms, af=3, fq_limit=8192, retry=4/4, TSQ=Stock)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_htt_ampdu32_only",
        description="Isolated Single-Factor htt_max_amsdu_ampdu=3/32 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_htt_ampdu32_only",
        description="Isolated Single-Factor htt_max_amsdu_ampdu=3/32 Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0, TSQ=Stock)",
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            1,\n            4,\n            4,\n            4096,",
        "ampdu": 32,
    },
    {
        "r": 170,
        "slug": "isolated_tcp_tsq_512k_128k_only",
        "factor": "tcp_tsq",
        "desc": "Single-Factor Causal Ablation #6: ONLY TCP Small Queues (tcp_limit_output_bytes=512KB, tcp_notsent_lowat=128KB) varied; all other knobs held at Stock (AQL=5000/12000, fq_quantum=300, codel=20/100ms, af=3, fq_limit=8192, ftx=0, retry=4/4, ampdu=64)",
        "ap_state_block": """    ap_hmac_1550_q1514_codel8_end = R11CrossLayerKnobState(
        name="ap_isolated_tcp_tsq_512k_128k_only",
        description="Isolated Single-Factor TCP TSQ 512KB/128KB Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0)",
        tcp_limit_output_bytes=524288,
        tcp_notsent_lowat=131072,
        complexity_cost=1,
    )
    cpe_hmac_2100_q1514_codel8_end = R11CrossLayerKnobState(
        name="cpe_isolated_tcp_tsq_512k_128k_only",
        description="Isolated Single-Factor TCP TSQ 512KB/128KB Only (Stock AQL=5000/12000, fq_quantum=300, codel=20/100ms, RC=0)",
        tcp_limit_output_bytes=524288,
        tcp_notsent_lowat=131072,
        complexity_cost=1,
    )""",
        "arm_b_tuple": "3,\n            8192,\n            0,\n            4,\n            4,\n            4096,",
        "ampdu": 64,
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

    for ab in ABLATIONS:
        r = ab["r"]
        fname = f"run_live_autoresearch_r{r}_{ab['slug']}_bidir_8flow_voip_covclass13_6000m_abba16_dyadic_zero_loss_wds_n160_20261024.py"
        fpath = BENCH_DIR / fname
        src = r141_src
        assert OLD_STATE_BLOCK in src, "Expected OLD_STATE_BLOCK in R141 template"
        assert OLD_ARM_B_TUPLE in src, "Expected OLD_ARM_B_TUPLE in R141 template"
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
    for ab in ABLATIONS:
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
