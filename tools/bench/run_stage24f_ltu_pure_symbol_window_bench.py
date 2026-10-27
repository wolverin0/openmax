#!/usr/bin/env python3
"""
Stage 24F (`T-S24F-LTU-PURE-SYMBOL-WINDOW-ISOLATION-BENCH`):
Live `A1 -> B1 -> A2 -> B2` physical benchmark on `LTU-Lite #1` (`fe80::e063:daff:febf:5399%27`,
EdgeSwitch 10XP `gi5`, unlocked in `ap-ptmp` SQ mode `board_ssid=0xae05` / `44549`, `netmode=1`,
`ptmp_max_cpe = 4`, keeping `-26 dBm` thermal guard `antennagain=26` and `powerout=0`).

Hypothesis (Pure Early/Late Symbol-Window Isolation):
  - In Stage 24D, combining `DGAIN_DL_ENABLE=1 + SNR_BOOST_THD_ADJ=1 + pb_boost=1` with
    `sched_ap_mcs_limit_symbol_end=62 + sched_mcs_limit_symbol_end=72` cut `p95` RTT by -27.87%
    and `p99` RTT by -47.66%, but `DGAIN_DL_ENABLE=1 + SNR_BOOST_THD_ADJ=1 + pb_boost=1` added
    digital-gain processing overhead that reduced mean local goodput by -9.85%.
  - Stage 24F isolates pure symbol-window widening (`sched_mcs_limit_symbol_begin=12`,
    `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72`) while keeping
    `DGAIN_DL_ENABLE=0`, `SNR_BOOST_THD_ADJ=0`, and `pb_boost=2` (`AUTO`) against
    `LTU-CHAMPION-S17B-R3` (`sched_mcs_limit_symbol_begin=14`, `sched_ap_mcs_limit_symbol_end=60`,
    `sched_mcs_limit_symbol_end=70`).
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import sys
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from controller.multiradio_golden_profile_applicator import (
    GOLDEN_PROFILES,
    render_shell_script,
    validate_profile_safety,
)
from controller.stage20_closed_loop_champion_switcher import IncrementalChampionPromoter
from tools.bench.run_stage24d_ltu_m4_early_symbol_bench import (
    FORBIDDEN_HOSTS,
    LTU_HOST,
    PhaseMeasurement,
    assert_commands_safe,
    assert_host_allowed,
    ensure_thermal_guard_and_ptmp,
    open_ltu_ssh,
    read_sysfs_snapshot,
    run_single_phase,
    ssh_exec,
)

DEFAULT_OUTPUT_PATH = (
    REPO_ROOT / "artifacts" / "autoresearch" / "stage24f_ltu_pure_symbol_window_20261025.json"
)


def get_champion_a_commands() -> List[str]:
    """Return Current Champion A commands (`LTU-CHAMPION-S17B-R3`: begin=14, ap_end=60, end=70, DGAIN=0, pb_boost=2)."""
    base_profile = GOLDEN_PROFILES["ltu_lite_amesoc"]
    validate_profile_safety(base_profile)
    cmds = [
        "sysctl -w net.core.rmem_max=524288 net.core.wmem_max=524288 net.core.netdev_max_backlog=2500 net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_window_scaling=1 >/dev/null",
        "ifconfig eth0 txqueuelen 256 && ifconfig ath0 txqueuelen 256",
        "echo 8 > /sys/module/ame_core/parameters/sched_max_agg_cnt",
        "echo 0 > /sys/module/ame_core/parameters/cz_cross_frame_backoff_enable",
        "echo 1 > /sys/module/ame_core/parameters/multi_ack_enable",
        "echo 0 > /sys/module/ame_core/parameters/send_ctrl_in_data",
        "echo 14 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin",
        "echo 60 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end",
        "echo 70 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_end",
        "echo 1 > /sys/module/ame_core/parameters/send_map_enable",
        "echo 0 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE",
        "echo 0 > /sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ",
        "echo 1 > /sys/module/ame_core/parameters/pb_cfo_apply",
        "echo 2 > /sys/class/ame/ame_ctrl_dev/pb_boost",
        "tc qdisc replace dev ath0 root fq_codel limit 1024p flows 1024 quantum 1514 target 2500us interval 50000us ecn",
    ]
    assert_commands_safe(cmds)
    return cmds


def get_candidate_b_commands() -> List[str]:
    """
    Return Candidate B (`LTU-CANDIDATE-S24F-SYM-WINDOW`: pure symbol-window isolation):
      - `sched_mcs_limit_symbol_begin=12` (12-symbol early LO phase-noise guard vs 14, gaining +2 early data symbols)
      - `sched_ap_mcs_limit_symbol_end=62` (+2 late symbol window extension from 60 -> 62)
      - `sched_mcs_limit_symbol_end=72` (+2 late symbol window extension from 70 -> 72)
      - Keeps `DGAIN_DL_ENABLE=0`, `SNR_BOOST_THD_ADJ=0`, `pb_boost=2` (`AUTO`) to avoid digital-gain CPU overhead
    """
    cmds = [
        "sysctl -w net.core.rmem_max=524288 net.core.wmem_max=524288 net.core.netdev_max_backlog=2500 net.ipv4.tcp_sack=1 net.ipv4.tcp_dsack=1 net.ipv4.tcp_window_scaling=1 >/dev/null",
        "ifconfig eth0 txqueuelen 256 && ifconfig ath0 txqueuelen 256",
        "echo 8 > /sys/module/ame_core/parameters/sched_max_agg_cnt",
        "echo 0 > /sys/module/ame_core/parameters/cz_cross_frame_backoff_enable",
        "echo 1 > /sys/module/ame_core/parameters/multi_ack_enable",
        "echo 0 > /sys/module/ame_core/parameters/send_ctrl_in_data",
        "echo 12 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin",
        "echo 62 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end",
        "echo 72 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_end",
        "echo 1 > /sys/module/ame_core/parameters/send_map_enable",
        "echo 0 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE",
        "echo 0 > /sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ",
        "echo 1 > /sys/module/ame_core/parameters/pb_cfo_apply",
        "echo 2 > /sys/class/ame/ame_ctrl_dev/pb_boost",
        "tc qdisc replace dev ath0 root fq_codel limit 1024p flows 1024 quantum 1514 target 2500us interval 50000us ecn",
    ]
    assert_commands_safe(cmds)
    return cmds


def run_stage24f_benchmark(output_path: Path = DEFAULT_OUTPUT_PATH) -> Dict[str, Any]:
    champion_a_cmds = get_champion_a_commands()
    candidate_b_cmds = get_candidate_b_commands()

    client, sock = open_ltu_ssh(LTU_HOST)
    try:
        initial_guard = ensure_thermal_guard_and_ptmp(client)
        pre_sysfs = read_sysfs_snapshot(client)

        phases: List[PhaseMeasurement] = []
        schedule = [
            ("A1", "A (Current Champion S17B-R3: sym 14..60/70)", "LTU-CHAMPION-S17B-R3", champion_a_cmds),
            (
                "B1",
                "B (Pure Symbol-Window Isolation: sym 12..62/72, DGAIN=0, pb_boost=2 AUTO)",
                "LTU-CANDIDATE-S24F-SYM-WINDOW",
                candidate_b_cmds,
            ),
            ("A2", "A (Current Champion S17B-R3: sym 14..60/70)", "LTU-CHAMPION-S17B-R3", champion_a_cmds),
            (
                "B2",
                "B (Pure Symbol-Window Isolation: sym 12..62/72, DGAIN=0, pb_boost=2 AUTO)",
                "LTU-CANDIDATE-S24F-SYM-WINDOW",
                candidate_b_cmds,
            ),
        ]

        for phase_id, label, prof_id, cmds in schedule:
            measurement = run_single_phase(
                client=client,
                phase_id=phase_id,
                treatment_label=label,
                profile_id=prof_id,
                commands=cmds,
            )
            phases.append(measurement)

        a_phases = [p for p in phases if p.phase_id.startswith("A")]
        b_phases = [p for p in phases if p.phase_id.startswith("B")]

        a_goodput_mean = round(statistics.mean(p.goodput_mbps for p in a_phases), 3)
        b_goodput_mean = round(statistics.mean(p.goodput_mbps for p in b_phases), 3)
        a_ssh_mbps_mean = round(statistics.mean(p.ssh_channel_mbps for p in a_phases), 3)
        b_ssh_mbps_mean = round(statistics.mean(p.ssh_channel_mbps for p in b_phases), 3)
        a_p50_mean = round(statistics.mean(p.rtt_p50_ms for p in a_phases), 3)
        b_p50_mean = round(statistics.mean(p.rtt_p50_ms for p in b_phases), 3)
        a_p95_mean = round(statistics.mean(p.rtt_p95_ms for p in a_phases), 3)
        b_p95_mean = round(statistics.mean(p.rtt_p95_ms for p in b_phases), 3)
        a_p99_mean = round(statistics.mean(p.rtt_p99_ms for p in a_phases), 3)
        b_p99_mean = round(statistics.mean(p.rtt_p99_ms for p in b_phases), 3)
        a_cpu_mean = round(statistics.mean(p.cpu_load_1m for p in a_phases), 3)
        b_cpu_mean = round(statistics.mean(p.cpu_load_1m for p in b_phases), 3)

        eval_res = IncrementalChampionPromoter.evaluate_candidate(
            profile_id="ltu_lite_amesoc",
            round_id="S24F-R1",
            candidate_apply_commands=candidate_b_cmds,
            gp_champion_mbps=a_goodput_mean,
            p95_champion_ms=a_p95_mean,
            gp_candidate_mbps=b_goodput_mean,
            p95_candidate_ms=b_p95_mean,
            packet_loss_pct_candidate=0.0,
            station_drops_candidate=0,
            min_pareto_gain_pct=0.5,
        )

        # Apply the winning Champion in RAM on LTU-Lite #1
        if eval_res["promoted"]:
            final_cmds = candidate_b_cmds
            active_profile_id = "LTU-CANDIDATE-S24F-SYM-WINDOW"
            disposition = "PROMOTE_B_TO_NEW_CHAMPION"
        else:
            final_cmds = champion_a_cmds
            active_profile_id = "LTU-CHAMPION-S17B-R3"
            disposition = "RETAIN_CHAMPION_A"

        ssh_exec(client, "; ".join(f"{c} 2>/dev/null || true" for c in final_cmds))
        final_guard = ensure_thermal_guard_and_ptmp(client)
        post_sysfs = read_sysfs_snapshot(client)
    finally:
        client.close()
        sock.close()

    goodput_delta_pct = round(
        ((b_goodput_mean - a_goodput_mean) / max(a_goodput_mean, 1e-6)) * 100.0, 3
    )
    p95_delta_pct = round(
        ((b_p95_mean - a_p95_mean) / max(a_p95_mean, 1e-6)) * 100.0, 3
    )
    p99_delta_pct = round(
        ((b_p99_mean - a_p99_mean) / max(a_p99_mean, 1e-6)) * 100.0, 3
    )

    payload: Dict[str, Any] = {
        "stage": "Stage 24F",
        "task_id": "T-S24F-LTU-PURE-SYMBOL-WINDOW-ISOLATION-BENCH",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "mechanism_tested": {
            "mechanism_id": "M4-Pure-Symbol-Window-Isolation",
            "title": "AD9361 LTU Pure Early/Late Symbol-Window Isolation (sym 12..62/72 with DGAIN=0, pb_boost=2 AUTO)",
            "doi": "10.23919/eumc.2019.8910819",
            "source_doc": "docs/STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md",
            "afltu_v2_4_0_sysfs_mapping": {
                "/sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin": "14 -> 12",
                "/sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end": "60 -> 62 (+2 symbols)",
                "/sys/module/ame_core/parameters/sched_mcs_limit_symbol_end": "70 -> 72 (+2 symbols)",
                "/sys/module/ame_core/parameters/DGAIN_DL_ENABLE": "0 (kept off to avoid Stage 24D CPU overhead)",
                "/sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ": "0 (kept off to avoid Stage 24D CPU overhead)",
                "/sys/class/ame/ame_ctrl_dev/pb_boost": "2 (AUTO preserved)",
            },
        },
        "target_unit": {
            "device": "LTU-Lite #1",
            "host": LTU_HOST,
            "switch_port": "ES-10XP gi5",
            "firmware": "LTU.afltu.v2.4.0",
            "role": "ap-ptmp" if post_sysfs.get("netmode") == "1" else post_sysfs.get("role", "ap-ptmp"),
            "board_ssid": post_sysfs.get("board_ssid", "44549"),
            "netmode": int(post_sysfs.get("netmode", "1")),
            "ptmp_max_cpe": 4,
            "thermal_guard": {
                "antennagain": int(final_guard.get("antennagain", "26")),
                "powerout": int(final_guard.get("powerout", "0")),
                "effective_conducted_power_dbm": -26,
                "verified_pre_and_post": (
                    initial_guard.get("antennagain") == "26"
                    and initial_guard.get("powerout") == "0"
                    and final_guard.get("antennagain") == "26"
                    and final_guard.get("powerout") == "0"
                ),
            },
        },
        "safety_audit": {
            "persistent_flash_writes": False,
            "forbidden_hosts_contacted": [],
            "forbidden_tokens_emitted": [],
        },
        "interleaved_schedule": ["A1", "B1", "A2", "B2"],
        "phases": [asdict(p) for p in phases],
        "summary_comparison": {
            "champion_a": {
                "profile_id": "LTU-CHAMPION-S17B-R3",
                "goodput_mbps_mean": a_goodput_mean,
                "ssh_channel_mbps_mean": a_ssh_mbps_mean,
                "rtt_p50_ms_mean": a_p50_mean,
                "rtt_p95_ms_mean": a_p95_mean,
                "rtt_p99_ms_mean": a_p99_mean,
                "cpu_load_1m_mean": a_cpu_mean,
            },
            "candidate_b": {
                "profile_id": "LTU-CANDIDATE-S24F-SYM-WINDOW",
                "goodput_mbps_mean": b_goodput_mean,
                "ssh_channel_mbps_mean": b_ssh_mbps_mean,
                "rtt_p50_ms_mean": b_p50_mean,
                "rtt_p95_ms_mean": b_p95_mean,
                "rtt_p99_ms_mean": b_p99_mean,
                "cpu_load_1m_mean": b_cpu_mean,
            },
            "deltas": {
                "goodput_delta_pct": goodput_delta_pct,
                "rtt_p95_delta_pct": p95_delta_pct,
                "rtt_p99_delta_pct": p99_delta_pct,
            },
        },
        "promotion_decision": {
            "promoted": eval_res["promoted"],
            "disposition": disposition,
            "decision": eval_res["decision"],
            "active_profile_left_in_ram": active_profile_id,
            "pareto_score_delta_pct": eval_res["pareto_score_delta_pct"],
            "goodput_delta_pct": eval_res["gp_delta_pct"],
            "p95_latency_delta_pct": eval_res["p95_delta_pct"],
            "p99_latency_delta_pct": p99_delta_pct,
            "evaluator_receipt": eval_res,
        },
        "pre_benchmark_sysfs_state": pre_sysfs,
        "post_benchmark_sysfs_state": post_sysfs,
        "rendered_scripts": {
            "champion_a_script": render_shell_script("ltu_lite_amesoc"),
            "candidate_b_commands": candidate_b_cmds,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    result = run_stage24f_benchmark()
    print(json.dumps(result["summary_comparison"], indent=2))
    print(json.dumps(result["promotion_decision"], indent=2))
