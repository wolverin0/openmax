from __future__ import annotations

import json
import pytest

from tools.bench.run_stage24f_ltu_pure_symbol_window_bench import (
    DEFAULT_OUTPUT_PATH,
    FORBIDDEN_HOSTS,
    LTU_HOST,
    assert_commands_safe,
    assert_host_allowed,
    get_candidate_b_commands,
    get_champion_a_commands,
)


def test_stage24f_command_and_host_safety_guards() -> None:
    assert_host_allowed(LTU_HOST)
    for bad_host in FORBIDDEN_HOSTS:
        with pytest.raises(ValueError, match="forbidden"):
            assert_host_allowed(bad_host)

    a_cmds = get_champion_a_commands()
    b_cmds = get_candidate_b_commands()
    assert_commands_safe(a_cmds)
    assert_commands_safe(b_cmds)

    a_joined = "\n".join(a_cmds)
    assert "echo 14 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin" in a_joined
    assert "echo 60 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end" in a_joined
    assert "echo 70 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_end" in a_joined
    assert "echo 0 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE" in a_joined

    b_joined = "\n".join(b_cmds)
    assert "echo 12 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin" in b_joined
    assert "echo 62 > /sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end" in b_joined
    assert "echo 72 > /sys/module/ame_core/parameters/sched_mcs_limit_symbol_end" in b_joined
    assert "echo 0 > /sys/module/ame_core/parameters/DGAIN_DL_ENABLE" in b_joined
    assert "echo 0 > /sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ" in b_joined
    assert "echo 2 > /sys/class/ame/ame_ctrl_dev/pb_boost" in b_joined


def test_stage24f_artifact_integrity() -> None:
    assert DEFAULT_OUTPUT_PATH.exists(), f"Missing artifact: {DEFAULT_OUTPUT_PATH}"
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 24F"
    assert data["task_id"] == "T-S24F-LTU-PURE-SYMBOL-WINDOW-ISOLATION-BENCH"
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
        assert p["sysfs_state"]["board_ssid"] == "44549"
        assert p["sysfs_state"]["netmode"] == "1"
        assert p["sysfs_state"]["DGAIN_DL_ENABLE"] == "0"
        assert p["sysfs_state"]["SNR_BOOST_THD_ADJ"] == "0"
        if p["phase_id"].startswith("A"):
            assert p["sysfs_state"]["sched_mcs_limit_symbol_begin"] == "14"
            assert p["sysfs_state"]["sched_ap_mcs_limit_symbol_end"] == "60"
            assert p["sysfs_state"]["sched_mcs_limit_symbol_end"] == "70"
        else:
            assert p["sysfs_state"]["sched_mcs_limit_symbol_begin"] == "12"
            assert p["sysfs_state"]["sched_ap_mcs_limit_symbol_end"] == "62"
            assert p["sysfs_state"]["sched_mcs_limit_symbol_end"] == "72"

    decision = data["promotion_decision"]
    assert decision["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")
    assert decision["active_profile_left_in_ram"] in (
        "LTU-CANDIDATE-S24F-SYM-WINDOW",
        "LTU-CHAMPION-S17B-R3",
    )
