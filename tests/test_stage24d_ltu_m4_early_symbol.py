from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.bench.run_stage24d_ltu_m4_early_symbol_bench import (
    DEFAULT_OUTPUT_PATH,
    FORBIDDEN_HOSTS,
    LTU_HOST,
    assert_commands_safe,
    assert_host_allowed,
    get_candidate_b_commands,
    get_champion_a_commands,
)


def test_stage24d_command_and_host_safety_guards() -> None:
    assert_host_allowed(LTU_HOST)
    for bad_host in FORBIDDEN_HOSTS:
        with pytest.raises(ValueError, match="forbidden"):
            assert_host_allowed(bad_host)

    a_cmds = get_champion_a_commands()
    b_cmds = get_candidate_b_commands()
    assert_commands_safe(a_cmds)
    assert_commands_safe(b_cmds)

    # Confirm Champion A includes S17B-R3 baseline parameters
    a_joined = "\n".join(a_cmds)
    assert "echo 14 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin" in a_joined
    assert "echo 1 > /sys/module/ame_core/parameters/send_map_enable" in a_joined
    assert "echo 0 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE" in a_joined
    assert "echo 60 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end" in a_joined

    # Confirm Candidate B layers M4 power_Balance_adjust=1 + dl_ul_Symbol_adjust=2 on top of Champion A
    b_joined = "\n".join(b_cmds)
    assert "echo 14 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin" in b_joined
    assert "echo 1 > /sys/module/ame_core/parameters/send_map_enable" in b_joined
    assert "echo 1 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE" in b_joined
    assert "echo 1 > /sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ" in b_joined
    assert "echo 1 > /sys/class/ame/ame_ctrl_dev/pb_boost" in b_joined
    assert "echo 62 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end" in b_joined
    assert "echo 72 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_end" in b_joined
    assert "power_Balance_adjust" in b_joined
    assert "dl_ul_Symbol_adjust" in b_joined


def test_stage24d_artifact_integrity() -> None:
    assert DEFAULT_OUTPUT_PATH.exists(), f"Missing artifact: {DEFAULT_OUTPUT_PATH}"
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 24D"
    assert data["task_id"] == "T-S24D-LTU-M4-EARLY-SYMBOL-AND-POWER-BALANCE-BENCH"
    assert data["mechanism_tested"]["mechanism_id"] == "M4"
    assert data["mechanism_tested"]["doi"] == "10.23919/eumc.2019.8910819"
    assert data["target_unit"]["host"] == LTU_HOST
    assert data["target_unit"]["role"] == "ap-ptmp"
    assert data["target_unit"]["thermal_guard"]["antennagain"] == 26
    assert data["target_unit"]["thermal_guard"]["powerout"] == 0
    assert data["target_unit"]["thermal_guard"]["verified_pre_and_post"] is True
    assert data["safety_audit"]["persistent_flash_writes"] is False

    assert data["interleaved_schedule"] == ["A1", "B1", "A2", "B2"]
    phases = data["phases"]
    assert len(phases) == 4
    assert [p["phase_id"] for p in phases] == ["A1", "B1", "A2", "B2"]

    for p in phases:
        assert p["thermal_guard_verified"] is True
        assert p["goodput_mbps"] > 0.0
        assert p["rtt_p95_ms"] > 0.0
        assert p["sysfs_state"]["sched_mcs_limit_symbol_begin"] == "14"
        assert p["sysfs_state"]["board_ssid"] == "44549"
        assert p["sysfs_state"]["netmode"] == "1"
        if p["phase_id"].startswith("A"):
            assert p["sysfs_state"]["DGAIN_DL_ENABLE"] == "0"
            assert p["sysfs_state"]["SNR_BOOST_THD_ADJ"] == "0"
            assert p["sysfs_state"]["sched_ap_mcs_limit_symbol_end"] == "60"
            assert p["sysfs_state"]["sched_mcs_limit_symbol_end"] == "70"
        else:
            assert p["sysfs_state"]["DGAIN_DL_ENABLE"] == "1"
            assert p["sysfs_state"]["SNR_BOOST_THD_ADJ"] == "1"
            assert p["sysfs_state"]["sched_ap_mcs_limit_symbol_end"] == "62"
            assert p["sysfs_state"]["sched_mcs_limit_symbol_end"] == "72"

    decision = data["promotion_decision"]
    assert decision["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")
    assert decision["active_profile_left_in_ram"] in ("LTU-CANDIDATE-S24D-M4", "LTU-CHAMPION-S17B-R3")
