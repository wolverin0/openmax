from __future__ import annotations

import json
from pathlib import Path

from tools.qca988x.trace_utf_handlers import (
    VALID_CLASSIFICATIONS,
    build_ar9888_utf_command_traces,
    build_utf_handler_trace_summary,
    parse_cmd_rsp_parms_dict_text,
    parse_init_cmd_process_tlv2_registrations,
)
from tools.qca988x.utf_build_inventory import (
    build_ar9888_utf_build_inventory,
    build_combined_utf_handler_and_build_matrix,
    parse_makefile_target_subdirs,
    write_ar9888_utf_handler_and_build_matrix_json,
)


def test_parse_cmd_rsp_parms_dict_and_init_registrations() -> None:
    snippet = """
    CMD_REGREAD = 9,
    CMD_MEMREAD = 42,
    CMD_ADCCAPTURE = 59,
    CMD_GENWAVEFORM = 61,
    SYSCMD_PHYDBGDUMP = 10009,
    """
    parsed = parse_cmd_rsp_parms_dict_text(snippet)
    assert parsed["CMD_REGREAD"] == 9
    assert parsed["CMD_MEMREAD"] == 42
    assert parsed["CMD_ADCCAPTURE"] == 59
    assert parsed["CMD_GENWAVEFORM"] == 61
    assert parsed["SYSCMD_PHYDBGDUMP"] == 10009

    c_snippet = """
    void initCmdProcessTlv2()
    {
        registerREGREADHandler (regReadHandler);
        registerMEMREADHandler(memReadHandler);
        initLMQueryHandler();
    }
    """
    regs = parse_init_cmd_process_tlv2_registrations(c_snippet)
    assert len(regs) == 3
    assert regs[0]["registration_call"] == "registerREGREADHandler"
    assert regs[0]["handler_symbol"] == "regReadHandler"
    assert regs[1]["registration_call"] == "registerMEMREADHandler"
    assert regs[1]["handler_symbol"] == "memReadHandler"
    assert regs[2]["registration_call"] == "initLMQueryHandler"


def test_utf_command_traces_classifications_and_ids() -> None:
    traces = {t.command_name: t for t in build_ar9888_utf_command_traces()}
    assert len(traces) == 14
    for entry in traces.values():
        assert entry.classification in VALID_CLASSIFICATIONS

    # Verify ADCCAPTURE (59) and GENWAVEFORM (61) and SYSCMD_PHYDBGDUMP (10009) are SHARED_ONLY
    adc = traces["CMD_ADCCAPTURE"]
    assert adc.command_id == 59
    assert adc.response_command_id == 60
    assert adc.registered_in_ar9888_utf is False
    assert adc.classification == "SHARED_ONLY"

    gen = traces["CMD_GENWAVEFORM"]
    assert gen.command_id == 61
    assert gen.response_command_id == 62
    assert gen.registered_in_ar9888_utf is False
    assert gen.classification == "SHARED_ONLY"

    phydbg = traces["SYSCMD_PHYDBGDUMP"]
    assert phydbg.command_id == 10009
    assert phydbg.registered_in_ar9888_utf is False
    assert phydbg.classification == "SHARED_ONLY"

    # Verify REGREAD (9), REGWRITE (11), MEMWRITE (40), MEMREAD (42) are EXACT_AR9888
    assert traces["CMD_REGREAD"].command_id == 9
    assert traces["CMD_REGREAD"].classification == "EXACT_AR9888"
    assert traces["CMD_REGREAD"].non_destructive_read_only is True

    assert traces["CMD_REGWRITE"].command_id == 11
    assert traces["CMD_REGWRITE"].classification == "EXACT_AR9888"
    assert traces["CMD_REGWRITE"].non_destructive_read_only is False

    assert traces["CMD_MEMREAD"].command_id == 42
    assert traces["CMD_MEMREAD"].classification == "EXACT_AR9888"
    assert traces["CMD_MEMREAD"].non_destructive_read_only is True

    assert traces["CMD_MEMWRITE"].command_id == 40
    assert traces["CMD_MEMWRITE"].classification == "EXACT_AR9888"
    assert traces["CMD_MEMWRITE"].non_destructive_read_only is False

    # Verify TCMD_SET_REG_ID (5) is NOT_FOUND in tcmd_parse_cmd switch
    assert traces["TCMD_SET_REG_ID"].command_id == 5
    assert traces["TCMD_SET_REG_ID"].classification == "NOT_FOUND"
    assert traces["TCMD_SET_REG_ID"].registered_in_ar9888_utf is False


def test_utf_handler_trace_summary_non_destructive_list() -> None:
    summary = build_utf_handler_trace_summary()
    safe_cmds = set(summary["safe_non_destructive_ar9888_utf_commands"])
    assert {"CMD_REGREAD", "CMD_MEMREAD", "CMD_TXSTATUS", "CMD_RXSTATUS", "CMD_LMQUERY"} == safe_cmds
    assert "CMD_NOISEFLOORREAD" not in safe_cmds  # calls whalReset()


def test_parse_makefile_and_build_inventory(tmp_path: Path) -> None:
    mk_text = """
ifeq ($(TARGET),AR9888)
SUBDIRS += eeprom lib otpdump utf wlansetup utfsetup
endif
"""
    blocks = parse_makefile_target_subdirs(mk_text)
    assert blocks["AR9888"] == ["eeprom", "lib", "otpdump", "utf", "wlansetup", "utfsetup"]

    inv = build_ar9888_utf_build_inventory()
    assert inv["can_build_standalone_utf_from_public_tree_alone"] is False
    assert inv["present_in_public_tree_count"] == 3
    assert inv["missing_from_public_tree_count"] == 4
    assert inv["hard_build_blocker_ids"] == ["DEP-UTF-04", "DEP-UTF-05", "DEP-UTF-06"]

    out_path = tmp_path / "ar9888_utf_handler_and_build_matrix.json"
    matrix = write_ar9888_utf_handler_and_build_matrix_json(out_path)
    assert out_path.exists()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["live_devices_touched"] is False
    assert loaded["task_id"] == "T-PB-GEM2-02"
    assert loaded["workstream_e3_utf_handler_trace"]["total_commands_traced"] == 14
    assert matrix["workstream_e4_utf_build_inventory"]["target"] == "AR9888"
