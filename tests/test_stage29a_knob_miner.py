"""Offline Stage29A contracts; disposable fixtures and retained local bytes only."""
from __future__ import annotations

import ast
import copy
import json
import struct
from collections import Counter

import pytest

from tools.research import pb010_012_firmware_wmi_and_ame_knob_miner as miner


@pytest.fixture(scope="module")
def report():
    return miner.load_json(miner.read_local(miner.ROOT/miner.OUTPUT))


@pytest.mark.parametrize(("expression", "expected"), [
    ("0x9000UL", 0x9000), ("WMI_CMD_GRP(G)", 0x3001),
    ("WMI_EVT_GRP(G)", 0x3001), ("BIT(7)", 128),
    ("(A | 2) + 1", 19), ("(A << 2) - 1", 63),
    ("~0", -1), ("+7", 7), ("16 >> 2", 4),
    ("15 & 6", 6), ("15 ^ 6", 9), ("3 * 5", 15),
])
def test_restricted_enum_arithmetic(expression, expected):
    assert miner.integer_expression(expression, {"G": 3, "A": 16}) == expected


@pytest.mark.parametrize("expression", [
    "__import__('os').getcwd()", "open('no-write')", "A.real", "A[0]",
    "2 ** 32", "1 / 2", "BIT(32)", "1 << -1", "1 << 32",
    "unknown(1)", "MISSING + 1", "0x100000000", "True",
    "WMI_CMD_GRP(1, 2)", "BIT(value=3)", "1" * 1025,
])
def test_enum_expressions_cannot_execute_or_guess(expression):
    with pytest.raises((ValueError, SyntaxError)):
        miner.integer_expression(expression, {"A": 16})


def test_enum_aliases_lines_and_unresolved_propagation():
    source = """// offsets must survive comments
enum wmi_cmd_group { GROUP = 3 };
enum wmi_cmd_id {
 FIRST_CMDID = WMI_CMD_GRP(GROUP),
 SECOND_CMDID,
 ALIAS_CMDID = SECOND_CMDID,
 UNKNOWN_CMDID = bad(1, 2),
 AFTER_UNKNOWN_CMDID,
 RESET_CMDID = 0x1234,
 NEXT_CMDID
};
"""
    rows = miner.enum_catalog(source, "fixture.h")
    assert [r["value"] for r in rows] == [0x3001, 0x3002, 0x3002, None, None, 0x1234, 0x1235]
    assert rows[2]["alias_of"] == "SECOND_CMDID"
    assert rows[0]["line"] == 4
    assert all(r["direction"] == "H2T" and not r["runtime_support_verified"] for r in rows)
    assert all(r["symbol"] in source.splitlines()[r["line"]-1] for r in rows)


def test_sentinels_do_not_hide_real_start_or_max_controls(report):
    rows = {r["symbol"]: r for r in report["protocol_declarations"]}
    for abi in ("10X", "10_2", "10_4"):
        for edge in ("START", "END"):
            for kind in ("CMDID", "EVENTID"):
                assert rows[f"WMI_{abi}_{edge}_{kind}"]["sentinel"]
        assert not rows[f"WMI_{abi}_MU_CAL_START_CMDID"]["sentinel"]
    for prefix in ("WMI", "WMI_10X", "WMI_10_4"):
        assert not rows[f"{prefix}_VDEV_PARAM_BMISS_COUNT_MAX"]["sentinel"]
    assert rows["HTT_DBG_NUM_STATS"]["sentinel"]
    assert rows["HTT_DBG_NUM_STATS"]["value"] == 17
    assert rows["HTT_H2T_NUM_MSGS"]["sentinel"]
    assert not rows["HTT_H2T_MSG_TYPE_AGGR_CFG"]["sentinel"]


def test_protocol_census_has_namespaces_parameters_events_and_host_mappings(report):
    summary = report["protocol_summary"]
    assert len(report["protocol_declarations"]) == 1269
    assert summary["by_kind"] == {
        "command": 529, "event": 193, "parameter": 409, "bitmask": 6, "message": 132,
    }
    assert summary["unresolved"] == 34
    assert not summary["counts_are_executable_opcodes"]
    rows = {r["symbol"]: r for r in report["protocol_declarations"]}
    assert rows["WMI_INIT_CMDID"]["value"] == 1
    assert rows["WMI_10X_START_SCAN_CMDID"]["value"] == 0x9000
    assert rows["WMI_10_2_START_SCAN_CMDID"]["value"] == 0x9000
    assert rows["WMI_10_4_START_SCAN_CMDID"]["value"] == 0x9000
    assert rows["WMI_INIT_CMDID"]["host_maps"] == ["wmi_cmd_map.init_cmdid"]
    assert rows["HTT_H2T_MSG_TYPE_AGGR_CFG"]["value"] == 5
    for row in report["protocol_declarations"]:
        if row["namespace"].startswith("htt") and "_t2h_" in row["namespace"]:
            assert row["direction"] == "T2H"
        assert not row["runtime_support_verified"]
        assert row["exact_build_testedness"] == "UNKNOWN"


def api5(records):
    out = b"QCA-ATH10K\0" + b"\0"
    for ident, payload in records:
        out += struct.pack("<II", ident, len(payload)) + payload
        out += b"\0" * ((-len(payload)) % 4)
    return out


def test_api5_container_metadata_never_qualifies_image_abi():
    value = miner.api5_metadata(api5([(1, b"version"), (3, b"fixture-image")]))
    assert [r["id"] for r in value["records"]] == [1, 3]
    assert value["records"][1]["sha256"] == miner.sha256(b"fixture-image")
    assert not value["loader_abi_qualified"] and not value["execution_verified"]


@pytest.mark.parametrize("blob", [
    b"SGMT" + b"\0"*24,
    b"QCA-ATH10K\0",
    api5([(1, b"no image")]),
    api5([(3, b"first"), (3, b"duplicate")]),
    api5([(3, b"main")]) + b"\0",
    api5([(3, b"main")]) + struct.pack("<II", 4, 100) + b"x",
    api5([(3, b"x")])[:-1],
    api5([(3, b"main")] + [(100+i, b"") for i in range(256)]),
])
def test_api5_rejects_wrong_format_truncation_duplicates_and_budget(blob):
    with pytest.raises(ValueError):
        miner.api5_metadata(blob)


def test_firmware_gaps_and_vendor_literals_remain_separate(report):
    firmware = report["firmware"]
    assert firmware["requested_firmware5_status"] == "ABSENT_IN_BOUNDED_TREE"
    assert firmware["inventory"]["firmware5_matches"] == []
    assert not firmware["inventory"]["universal_absence_claim"]
    assert len(firmware["vendor_sgmt_images"]) == 3
    assert [r["segments"] for r in firmware["vendor_sgmt_images"]] == [4, 4, 4]
    assert [r["decoded_bytes"] for r in firmware["vendor_sgmt_images"]] == [309464, 289752, 266072]
    assert firmware["aligned_u32_literal_crossrefs"]
    for flag in ("literal_hits_prove_dispatch", "vendor_sgmt_is_api5",
                 "all_proprietary_opcodes_mined", "exact_firmware_runtime_abi_verified"):
        assert firmware[flag] is False
    assert report["coverage"]["firmware5_mining_complete"] is False
    assert report["coverage"]["ame_cpe_parameter_names"].startswith("UNKNOWN")


def test_all_retained_knob_populations_are_qualified_in_inventory(report):
    rows = report["knob_declarations"]
    assert len(rows) == 145
    assert Counter(r["population"] for r in rows) == {
        "airos_sysctl": 68, "ltu_sysfs": 20, "ame_core_module_parameter": 57,
    }
    assert len({r["id"] for r in rows}) == len(rows)
    for row in rows:
        assert row["physical_safe_range"] is None
        assert not row["permissions_verified"] and not row["writable_reversible_verified"]
        assert row["testedness"]["untested_everywhere_claim"] is False
        miner.testedness(row["surface"], None, [])


@pytest.mark.parametrize(("value", "expected"), [
    ("42", 42), ("-1", -1), ("0xff", 255), ("1 2 3", [1, 2, 3]),
])
def test_literal_source_recipes_extract_numeric_values_without_execution(value, expected):
    path = "/sys/module/ame_core/parameters/do_lotto"
    refs = miner.setting_references(f"echo '{value}' > {path} 2>/dev/null||true",
                                   "fixture.json", "/script", "RECIPE_INTENTION_NOT_EXECUTION")
    assert len(refs) == 1
    assert refs[0]["value"] == expected and refs[0]["surface"] == path
    assert refs[0]["error_suppression_present"] and not refs[0]["runtime_effect_verified"]


def test_declared_recipe_numeric_readback_and_value_overlap_are_not_conflated():
    path = "/sys/module/ame_core/parameters/do_lotto"
    raw = {
        miner.LEDGER: json.dumps({"profiles": [{"apply_commands": [f"echo 1 > {path}"]}]}).encode(),
        "artifacts/autoresearch/stage_fixture.json": json.dumps({
            "automatic_execution_allowed": False,
            "script": f"echo 2 > {path}",
            "final_ram_state": {path: "3"},
        }).encode(),
        "artifacts/autoresearch/stage_plan.json": json.dumps({
            "mode": "OFFLINE_STATIC", "final_ram_state": {"do_lotto": 4},
        }).encode(),
    }
    knobs = [{"name": "do_lotto", "surface": path, "population": "ame_core_module_parameter"}]
    refs = miner.tested_references(raw, knobs)
    assert {r["category"] for r in refs} == {
        "CHAMPION_DECLARED_SETTING", "RECIPE_INTENTION_NOT_EXECUTION",
        "NUMERIC_RECEIPT_MENTION", "OFFLINE_PLAN_ONLY",
    }
    result = miner.testedness(path, 3, refs)
    assert result["matching_value_references"] == 1
    assert result["status"] == "REPORTED_CONTROL_OVERLAP_EXACT_BUILD_UNRESOLVED"
    assert miner.testedness(path, 99, refs)["matching_value_references"] == 0
    assert not result["independent_execution_or_causal_acceptance"]
    recipe_only = miner.testedness(path, 2, [r for r in refs if r["category"].startswith("RECIPE")])
    assert recipe_only["status"] == "PROPOSED_OR_MENTIONED_NOT_EXECUTION"
    assert miner.testedness(path, None, [])["status"] == "NO_MATCH_IN_FROZEN_CORPUS"


@pytest.mark.parametrize("bad", [True, 1.0, "1", [True], [1]*17, {"value": 1}])
def test_testedness_rejects_boolean_aliases_and_untyped_mutation_values(bad):
    with pytest.raises(ValueError):
        miner.testedness("/sys/module/ame_core/parameters/do_lotto", bad, [])


def test_ranked_candidates_preserve_uncertainty_vault_provenance_and_one_coordinate(report):
    candidates = report["candidates"]
    assert {c["id"] for c in candidates} == {f"M{i}" for i in range(9, 16)}
    assert [c["rank"] for c in candidates] == list(range(1, 8))
    assert [(c["ranking_score"], -int(c["id"][1:])) for c in candidates] == sorted(
        [(c["ranking_score"], -int(c["id"][1:])) for c in candidates], reverse=True)
    by_id = {c["id"]: c for c in candidates}
    assert by_id["M9"]["payload_field"] == "cwmin"
    assert "A-MPDU" in by_id["M10"]["mutation"] and "3->2" in by_id["M10"]["mutation"]
    assert by_id["M12"]["selector"] == "cz_cross_frame_max_timeout"
    assert "backoff-enabled" in by_id["M12"]["mutation"]
    assert "scratch" in by_id["M14"]["hypothesis"]
    for candidate in candidates:
        assert candidate["hardware_testable_conditionally"] is True
        assert candidate["ready_for_hardware_dispatch"] is False
        assert candidate["expected_gain_pct"] is None and candidate["proposed_numeric_value"] is None
        assert candidate["execution_commands"] == [] and len(candidate["gates"]) == 4
        assert candidate["experiment"]["result"] == "NOT_RUN"
        assert candidate["experiment"]["decision"] == "INCONCLUSIVE"
        assert candidate["protocol_refs"] or candidate["control_refs"]
        assert candidate["vault_refs"]
        for ref in candidate["vault_refs"]:
            assert ref["match_kind"] == "LEXICAL_TOPIC_OVERLAP_ONLY"
            assert not ref["paper_claim_verified"] and not ref["hardware_transfer_proven"]


@pytest.mark.parametrize("path", [
    "//server/share/input", "\\\\server\\share\\input",
    "https://example.invalid/input", "\\\\.\\PhysicalDrive0",
])
def test_remote_or_device_input_paths_rejected_before_read(path):
    with pytest.raises(ValueError):
        miner.local_path(path)


def test_bounded_local_read(tmp_path):
    fixture = tmp_path/"fixture.json"
    fixture.write_bytes(b'{"fixture":true}')
    assert miner.read_local(fixture) == b'{"fixture":true}'
    with pytest.raises(ValueError):
        miner.read_local(fixture, limit=3)


@pytest.mark.parametrize("raw", [b'{"a":1,"a":2}', b'{"x":NaN}', b'{"x":Infinity}'])
def test_json_duplicates_and_nonfinite_constants_rejected(raw):
    with pytest.raises(ValueError):
        miner.load_json(raw)


def test_source_manifest_hashes_match_current_local_bytes(report):
    raw = miner.read_manifest(report["source_manifest"])
    assert set(miner.FIXED) <= set(raw)
    assert all(miner.sha256(raw[path]) == digest for path, digest in miner.PINS.items())


def test_champion_cutoff_is_independently_pinned_not_a_claim_about_live_state(report):
    cutoff = report["source_cutoff"]
    assert cutoff["ledger_original_path"] == "artifacts/autoresearch/champion_state_ledger.json"
    assert cutoff["ledger_snapshot_path"] == miner.LEDGER
    assert cutoff["ledger_snapshot_path"] != cutoff["ledger_original_path"]
    assert cutoff["ledger_sha256"] == miner.PINS[miner.LEDGER]
    assert cutoff["ledger_sha256"] in cutoff["ledger_snapshot_path"]
    assert miner.LIVE_LEDGER not in {row["path"] for row in report["source_manifest"]}


@pytest.mark.parametrize("mutation", ["digest", "bytes", "duplicate", "role", "traversal"])
def test_manifest_rejects_changed_forged_and_repeated_evidence(report, mutation):
    manifest = copy.deepcopy(report["source_manifest"])
    if mutation == "digest":
        manifest[0]["sha256"] = "0"*64
    elif mutation == "bytes":
        manifest[0]["bytes"] += 1
    elif mutation == "duplicate":
        manifest.append(copy.deepcopy(manifest[0]))
    elif mutation == "role":
        manifest[0]["role"] = "untrusted"
    else:
        manifest[0]["path"] = "../outside.json"
    with pytest.raises(ValueError):
        miner.read_manifest(manifest)


def test_frozen_population_cannot_silently_omit_a_saved_stage(report, monkeypatch):
    manifest = report["source_manifest"]
    omitted = [r for r in manifest if r["role"] == "stage_receipt_or_plan"][-1]
    monkeypatch.setattr(miner, "collect_manifest", lambda: (manifest, {}, {}))
    with pytest.raises(ValueError, match="population changed"):
        miner.build_report([r for r in manifest if r != omitted])


def test_saved_report_reconstructs_from_authenticated_frozen_inputs(report):
    assert miner.validate_report(report)


@pytest.mark.parametrize("mutation", ["dispatch", "rank", "range", "coverage", "claim", "extra"])
def test_report_metadata_cannot_override_recomputed_evidence(report, monkeypatch, mutation):
    changed = copy.deepcopy(report)
    if mutation == "dispatch":
        changed["candidates"][0]["ready_for_hardware_dispatch"] = True
    elif mutation == "rank":
        changed["candidates"][0]["ranking_score"] += 1
    elif mutation == "range":
        changed["knob_declarations"][0]["physical_safe_range"] = [0, 100]
    elif mutation == "coverage":
        changed["coverage"]["firmware5_mining_complete"] = True
    elif mutation == "claim":
        changed["candidates"][0]["vault_refs"][0]["paper_claim_verified"] = True
    else:
        changed["unverified_override"] = True
    # Exercise the semantic comparison against one already reconstructed fixture.
    monkeypatch.setattr(miner, "build_report", lambda manifest: report)
    with pytest.raises(ValueError, match="differs from recomputed"):
        miner.validate_report(changed)


def test_miner_has_no_process_network_or_device_executor():
    source = (miner.ROOT/"tools/research/pb010_012_firmware_wmi_and_ame_knob_miner.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)}
    assert not imports & {"subprocess", "socket", "requests", "paramiko", "urllib"}
    calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
    assert not calls & {"eval", "exec", "compile"}


def test_source_conflicts_and_physical_nonacceptance_survive(report):
    assert {r["topic"] for r in report["source_conflicts"]} == {
        "M3/M5 identity", "Target subtype routing", "M4 aliases",
    }
    assert not report["automatic_execution_allowed"] and not report["physical_acceptance"]
    assert report["new_physical_observations"] == 0 and not report["firmware_payload_exported"]
    assert report["decision"].endswith("DO_NOT_DISPATCH")
