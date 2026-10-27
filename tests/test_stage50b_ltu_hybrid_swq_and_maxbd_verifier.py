"""Stage46B saved-evidence tests; bench source is data, never imported or run."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

import pytest

from controller import stage50b_ltu_hybrid_swq_and_maxbd_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "artifacts/autoresearch/stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench_20261025.json"
REPORT = "docs/STAGE50B_LTU_HYBRID_SWQ_AND_MCS_CEILING_OTA_BENCHMARK.md"
RUNNER = "tools/bench/run_stage50b_ltu_hybrid_swq_and_mcs_ceiling_ota_bench.py"
SOURCE_PIN = "bd8a356d2d7cf78ab02e1c3808dd75aad67c079306f8c4f9694f84f70ae03fca"
REPORT_PIN = "092161b50d2b50f1511bc34d41f58d3448d1474c924640480262ff609ee2e3cd"
RUNNER_PIN = "cd97f7afabae6f2ca53e2b327e878374c26fc3838ce3f97fecca9d661bbef7cf"
PROFILES = ("S50B-R0-STAGE49B-BASELINE", "S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X",
            "S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2")
TRIAL_PINS = (
    "457d1cf7791cb4be4cfbd5bb0a362c6017bce5ea13cc20cea5c8e0bed47bb3d0",
    "29d850bae8186c59b48fcd9820be215e1f5f781d2e6f0574cd62aa1bcdd32e64",
    "26982f79a96e42c00ecc0713434d9329c62e926a80da13de3f05b4589ef9d66c",
    "8fae3223f5e48d0b01ed6cac07db42227873826e78914e6a05e203165bb929aa",
    "61f482f7e501b3e6305580fa396533ebdcfa8e98d5986c0136edfc0cd0d39651",
    "de8652001fc14c10971bf87f546e1afafbd97ba251d325285fee54944cc6749d",
    "95a29760b66623359c6859cbd48934a7853aa89e1265cbfa11d5cbe5e3096d7b",
    "144524d23f60549405be5012357cc2e98ced1c046f4bd6765fc400908dbfd3d6",
    "3fbc1c62879f0ede8021baa82e6a346840fda0681365ddd79d90243dd177159a",
)


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture(scope="module")
def saved_sources():
    return (json.loads((ROOT / SOURCE).read_text(encoding="utf-8-sig")), (ROOT / REPORT).read_bytes().decode("utf-8"))


@pytest.fixture
def document(saved_sources):
    return deepcopy(saved_sources[0])


@pytest.fixture
def source_root(tmp_path):
    for relative in (SOURCE, REPORT):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    return tmp_path


def test_saved_json_report_trials_and_static_runner_have_independent_exact_bindings(saved_sources):
    document, report = saved_sources
    assert _digest(document) == SOURCE_PIN
    assert hashlib.sha256(report.encode()).hexdigest() == REPORT_PIN
    assert tuple(_digest(trial) for trial in document["trials"]) == TRIAL_PINS
    assert hashlib.sha256((ROOT / RUNNER).read_bytes()).hexdigest() == RUNNER_PIN
    assert isinstance(verifier.source_contract(document, report), dict)


@pytest.mark.parametrize("index", range(9))
def test_each_of_nine_trials_is_pinned(document, saved_sources, index):
    document["trials"][index]["bulk_tcp_mbps"] += 1
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1])


@pytest.mark.parametrize("key", ("remote_cpe_stage_meta", "winning_profile", "flash_persistence_receipt",
                                   "ota_link_verification_post_bench", "summary_by_profile", "extra_field"))
def test_whole_envelope_is_bound_outside_trials(document, saved_sources, key):
    document[key] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1])


@pytest.mark.parametrize("change", ("append", "newlines", "claim"))
def test_report_binding_preserves_original_raw_bytes(saved_sources, change):
    document, report = saved_sources
    changed = {"append": report + "\n",
               "newlines": report.replace("\r\n", "\n") if "\r\n" in report else report.replace("\n", "\r\n"),
               "claim": report.replace("19%", "29%")}[change]
    assert changed != report
    with pytest.raises(ValueError):
        verifier.source_contract(document, changed)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown_profile", "bad_rep"))
def test_trial_inventory_requires_nine_unique_known_profile_rep_pairs(document, change):
    if change == "missing":
        document["trials"].pop()
    elif change == "extra":
        document["trials"].append(deepcopy(document["trials"][0]))
    elif change == "duplicate":
        document["trials"][-1] = deepcopy(document["trials"][0])
    elif change == "unknown_profile":
        document["trials"][0]["profile_id"] = "UNKNOWN"
    else:
        document["trials"][0]["rep"] = True
    with pytest.raises(ValueError):
        verifier.audit_stage50b(document)


MEAN_FIELDS = ("bulk_tcp_mbps", "iptv_udp_mbps", "iptv_jitter_ms", "iptv_loss_pct", "voip_jitter_ms",
               "voip_loss_pct", "loaded_ping_p50_ms", "loaded_ping_p95_ms", "loaded_ping_p99_ms")


def test_all_nine_trials_and_all_thirty_nine_summary_fields_are_preserved(document):
    before = _digest(document)
    result = verifier.audit_stage50b(document)
    assert _digest(document) == before
    assert len(result["trials"]) == 9
    assert sum(len(summary) for summary in document["summary_by_profile"].values()) == 39
    for profile in PROFILES:
        selected = [trial for trial in document["trials"] if trial["profile_id"] == profile]
        assert len(selected) == document["summary_by_profile"][profile]["n_trials"] == 3
        expected = {"mean_" + key: round(statistics.mean(trial[key] for trial in selected), 3) for key in MEAN_FIELDS}
        expected["mean_aggregate_dl_mbps"] = round(statistics.mean(trial["bulk_tcp_mbps"] + trial["iptv_udp_mbps"] for trial in selected), 3)
        for short in ("p50", "p95"):
            expected["median_loaded_ping_" + short + "_ms"] = statistics.median(trial["loaded_ping_" + short + "_ms"] for trial in selected)
        assert result["profiles"][profile]["means"] == expected
        assert all(result["profiles"][profile]["summary_checks"].values())
        assert all(document["summary_by_profile"][profile][key] == value for key, value in expected.items())
    assert result["native_acceptance"] is False
    assert result["physical_status"] == "UNKNOWN"


def test_measured_maxbd_values_are_saved_reads_and_not_a_hardware_cap(document):
    result = verifier.audit_stage50b(document)
    assert [trial["maxbd"]["value"] for trial in result["trials"]] == [9, 6, 7, 5, 6, 5, 5, 10, 5]
    assert result["profiles"][PROFILES[0]]["maxbd"] == {"values": [9, 5, 10], "min": 5, "max": 10}
    assert result["profiles"][PROFILES[1]]["maxbd"]["max"] == 6
    assert result["profiles"][PROFILES[2]]["maxbd"]["max"] == 7
    for trial in result["trials"]:
        assert trial["maxbd"]["in_reported_5_to_10_range"] is True
        assert trial["maxbd"]["native_eab_high_water_semantics_authenticated"] is False
        assert trial["maxbd"]["reset_epoch_and_success_proven"] is False
        assert trial["maxbd"]["hard_cap_or_instantaneous_occupancy_proven"] is False


def test_subset_selection_excludes_a_lower_scoring_baseline_and_retains_tradeoffs(document):
    result = verifier.audit_stage50b(document)
    selection = result["selection"]
    assert selection["eligible_profiles"] == list(PROFILES[1:])
    assert selection["scores_all_profiles"] == {PROFILES[0]: 13.620, PROFILES[1]: 19.494, PROFILES[2]: 22.699}
    assert selection["recomputed_winner"] == selection["reported_winner"] == PROFILES[1]
    assert selection["scores_all_profiles"][PROFILES[0]] < selection["scores_all_profiles"][PROFILES[1]]
    assert selection["global_optimum_or_pareto_improvement_proven"] is False
    changes = result["changes_vs_baseline_pct"][PROFILES[1]]
    assert changes["mean_loaded_ping_p95_ms"] < 0
    assert changes["mean_bulk_tcp_mbps"] < 0
    assert changes["mean_aggregate_dl_mbps"] < 0
    assert changes["mean_iptv_loss_pct"] > 0
    assert changes["mean_voip_jitter_ms"] > 0


def test_reported_bler_range_conflicts_with_saved_correct_total_headers(document):
    result = verifier.audit_stage50b(document)
    assert result["profiles"][PROFILES[2]]["reported_fragment_percent_values"] == [40, 46, 52]
    finding = next(item for item in result["findings"] if item["code"] == "R2_REPORT_BLER_19_TO_21_NOT_IN_SAVED_FRAGMENT_PERCENT_FIELDS")
    assert finding["saved_displayed_percent"] == [40, 46, 52]
    for trial in result["trials"]:
        raw = trial["fragment_snapshot"]
        assert raw["display_matches_floor_correct_ratio"] is True
        assert raw["bps_matches_correct_times_fragment_bits"] is True
        assert raw["display_is_authenticated_bler_or_packet_loss"] is False
        assert raw["counter_reset_interval_and_rf_cause_proven"] is False


@pytest.mark.parametrize("field", MEAN_FIELDS + ("voip_udp_mbps", "bulk_tcp_retransmits", "loaded_ping_samples"))
def test_numeric_trial_fields_reject_boolean_coercion(document, field):
    document["trials"][0][field] = True
    with pytest.raises(ValueError):
        verifier.audit_stage50b(document)


@pytest.mark.parametrize("field,bad", (("iptv_loss_pct", 101), ("voip_udp_mbps", float("inf")),
                                      ("loaded_ping_p95_ms", float("nan")), ("bulk_tcp_retransmits", 0.5),
                                      ("loaded_ping_samples", 0), ("loaded_ping_p50_ms", 1000)))
def test_trial_numbers_remain_finite_ordered_and_bounded(document, field, bad):
    document["trials"][0][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage50b(document)


@pytest.mark.parametrize("field", ("ota_verified", "cpe_watchdog_disarmed_after_verify"))
def test_apply_readback_flags_require_booleans(document, field):
    document["trials"][0]["apply_meta"][field] = 1
    with pytest.raises(ValueError):
        verifier.audit_stage50b(document)


def test_apply_marker_and_ota_boolean_must_agree(document):
    document["trials"][0]["apply_meta"]["ota_verified"] = False
    with pytest.raises(ValueError):
        verifier.audit_stage50b(document)


def test_summary_mismatch_and_out_of_reported_maxbd_range_remain_findings(document):
    document["summary_by_profile"][PROFILES[1]]["mean_bulk_tcp_mbps"] = 99
    document["trials"][0]["maxBD_peak_hex"] = "0x31"
    result = verifier.audit_stage50b(document)
    assert result["profiles"][PROFILES[1]]["means"]["mean_bulk_tcp_mbps"] == 9.775
    assert result["trials"][0]["maxbd"]["value"] == 49
    assert any(item["code"] == "PROFILE_SUMMARY_DISAGREES" for item in result["findings"])
    assert any(item["code"] == "MAXBD_OUTSIDE_REPORTED_RANGE" for item in result["findings"])
    assert result["native_acceptance"] is False


@pytest.mark.parametrize("level,label", ((7, "QPSKl"), (11, "16Ql"), (15, "64Ql"),
                                         (19, "256Ql"), (23, "1024Ql"), (31, "4096l")))
@pytest.mark.parametrize("opcode", (0, 2))
def test_stage50_discrete_cpe_ceiling_contract_is_supplied_and_conflicts_prior_claim(level, label, opcode):
    result = verifier.verify_cpe_mcs_contract(cpe_id=0, mcs_level=level, opcode=opcode)
    assert result["reported_label"] == label
    assert result["supplied_stage50b_contract_consistent"] is True
    assert result["conflicts_with_stage49b_sentinel32_claim"] is True
    assert result["native_abi_authenticated"] is False


@pytest.mark.parametrize("opcode", (0, 2))
def test_stage50_contract_rejects_sentinel32_without_resolving_native_abi(opcode):
    with pytest.raises(ValueError, match="32_REJECTED"):
        verifier.verify_cpe_mcs_contract(cpe_id=0, mcs_level=32, opcode=opcode)


@pytest.mark.parametrize("field,bad", (("cpe_id", 1), ("cpe_id", False), ("mcs_level", True),
                                      ("mcs_level", 8), ("mcs_level", "19"), ("opcode", 1), ("opcode", True)))
def test_discrete_rate_contract_fails_closed_for_unknown_or_coerced_fields(field, bad):
    arguments = {"cpe_id": 0, "mcs_level": 19, "opcode": 0}
    arguments[field] = bad
    with pytest.raises(ValueError):
        verifier.verify_cpe_mcs_contract(**arguments)


@pytest.mark.parametrize("raw,value", (("0x0", 0), ("0xa", 10), ("0x31", 49), ("0xffffffff", 2**32 - 1)))
def test_maxbd_parser_preserves_bounded_hex_without_assuming_semantics(raw, value):
    result = verifier.audit_maxbd(raw)
    assert result["value"] == value and result["raw"] == raw
    assert result["hard_cap_or_instantaneous_occupancy_proven"] is False


@pytest.mark.parametrize("raw", (None, True, 10, "", "10", "0x", "-0x1", " 0xa", "0xa\n",
                                 "0x100000000", "0xa;echo unsafe"))
def test_maxbd_parser_rejects_nonliteral_or_out_of_bounds_hex(raw):
    with pytest.raises(ValueError):
        verifier.audit_maxbd(raw)


@pytest.fixture
def bler_text(document):
    return document["trials"][0]["bler_snapshot"]


def test_fragment_parser_retains_hex_counts_and_reports_arithmetic_without_native_bler(bler_text):
    result = verifier.audit_bler_snapshot(bler_text)
    assert result["raw"] == bler_text
    assert result["correct"] == int("00000B32", 16)
    assert result["total"] == int("00001DC5", 16)
    assert result["correct_over_total_pct"] == pytest.approx(100 * int("B32", 16) / int("1DC5", 16))
    assert result["reported_bps"] == int("B32", 16) * 80 * 8
    assert result["displayed_percent"] == 37
    assert result["display_is_authenticated_bler_or_packet_loss"] is False


@pytest.mark.parametrize("change", ("empty", "duplicate", "missing_header", "header_over_100", "zero_total",
                                   "correct_over_total", "count_over_exact_range", "nonfinite_bps", "bad_fragment_size"))
def test_fragment_parser_rejects_malformed_or_unbounded_snapshots(bler_text, change):
    changed = {
        "empty": "", "duplicate": bler_text + "\n" + bler_text,
        "missing_header": bler_text.replace("Correct   Total", "Unknown   Total"),
        "header_over_100": bler_text.replace("037", "101"),
        "zero_total": bler_text.replace("00001DC5", "00000000"),
        "correct_over_total": bler_text.replace("00000B32", "FFFFFFFF"),
        "count_over_exact_range": bler_text.replace("00000B32", "20000000000000"),
        "nonfinite_bps": bler_text.replace("1.834240e+06", "1e999"),
        "bad_fragment_size": bler_text.replace("size 80 bytes", "size 65537 bytes"),
    }[change]
    with pytest.raises(ValueError):
        verifier.audit_bler_snapshot(changed)


def test_fragment_label_arithmetic_disagreement_is_a_retained_finding(document):
    document["trials"][0]["bler_snapshot"] = document["trials"][0]["bler_snapshot"].replace("1.834240e+06", "1.0")
    result = verifier.audit_stage50b(document)
    assert result["trials"][0]["fragment_snapshot"]["reported_bps"] == 1
    assert any(item["code"] == "FRAGMENT_LABEL_ARITHMETIC_DISAGREES" for item in result["findings"])
    assert result["native_acceptance"] is False


def test_dual_partition_progress_receipts_do_not_prove_deployed_content_or_cold_boot(document):
    result = verifier.audit_stage50b(document)
    persistence = result["persistence"]
    assert persistence["winning_mcs_ceiling"] == 19
    assert persistence["cpe_live_ceiling_staged"] == 23
    assert persistence["cpe_persisted_ceiling_reported"] == 19
    for receipt in persistence["receipts"].values():
        assert receipt["command_success_receipt"] is True
        assert receipt["dual_partition_progress_complete"] is True
        assert receipt["unattended_cold_boot_proven"] is False
    assert persistence["persisted_content_and_deployed_script_hashes"] == "MISSING"
    assert persistence["new_poststart_executed_by_runner"] is False
    assert persistence["live_and_postboot_profiles_equivalent_proven"] is False
    assert persistence["cold_boot_proven"] is False


def test_failed_flash_command_is_not_rescued_by_drawn_100_percent_progress(document):
    document["flash_persistence_receipt"]["ltu2_ota_cfgmtd_rc"] = 1
    result = verifier.audit_stage50b(document)
    assert result["persistence"]["receipts"]["LTU2"]["command_success_receipt"] is False
    assert any(item["code"] == "CFGMTD_SUCCESS_RECEIPT_INCOMPLETE" for item in result["findings"])


@pytest.fixture
def audit(source_root):
    return verifier.audit_saved_sources(source_root)


def test_root_audit_binds_static_reference_and_keeps_all_acceptance_boundaries(audit):
    assert audit["audit_status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert audit["source_contract"]["native_acquisition_authenticated"] is False
    assert audit["static_recipe_context_sha256"][RUNNER] == RUNNER_PIN
    assert audit["stage50b"]["design"]["aggregate_dl_excludes_voip"] is True
    assert audit["stage50b"]["design"]["randomization_proven"] is False
    assert audit["stage50b"]["design"]["raw_receiver_json_counts_and_ping_samples"] == "MISSING"
    assert audit["stage50b"]["recipe_qualifications"]["dmesg_ELF_relocation_module_hashes_and_complete_native_getters"] == "MISSING"
    assert audit["boundary"] == {"offline_only": True, "ssh": False, "hardware_access": False,
                                  "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}


def test_atomic_export_roundtrip_and_managed_refresh(audit, tmp_path):
    output = tmp_path / "audit.json"
    assert verifier.write_audit(audit, output) == output
    assert json.loads(output.read_text(encoding="utf-8")) == audit
    updated = deepcopy(audit)
    updated["test_refresh"] = True
    verifier.write_audit(updated, output)
    assert json.loads(output.read_text(encoding="utf-8"))["test_refresh"] is True
    assert not list(tmp_path.glob(".stage46b-*.tmp"))


def test_export_refuses_source_overwrite(audit, source_root):
    output = source_root / SOURCE
    before = output.read_bytes()
    with pytest.raises(ValueError, match="SOURCE_OVERWRITE_REJECTED"):
        verifier.write_audit(audit, output, protected_paths=(output, source_root / REPORT))
    assert output.read_bytes() == before


@pytest.mark.parametrize("content", ({"other": "data"}, {"task_id": verifier.TASK_ID, "audit_version": True}))
def test_export_refuses_unowned_existing_json(audit, tmp_path, content):
    output = tmp_path / "existing.json"
    output.write_text(json.dumps(content), encoding="utf-8")
    before = output.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_audit(audit, output)
    assert output.read_bytes() == before


@pytest.mark.parametrize("name", ("audit.txt", "bad name.json", "NUL.json", "CON.json", "COM1.json"))
def test_export_requires_literal_nondevice_json_name_without_creating_entries(audit, tmp_path, name):
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError):
        verifier.write_audit(audit, tmp_path / name)
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("path", ("//example.invalid/share/audit.json", "https://example.invalid/audit.json",
                                  "file:///tmp/audit.json", "C:audit.json", "\\\\?\\C:\\audit.json", "bad\0.json"))
def test_export_rejects_network_uri_device_and_nul_paths_without_access(audit, path):
    with pytest.raises(ValueError):
        verifier.write_audit(audit, path)


def test_optional_real_symlink_output_is_rejected_without_modifying_target(audit, tmp_path):
    target = tmp_path / "target.json"
    target.write_text(json.dumps(audit), encoding="utf-8")
    link = tmp_path / "link.json"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"Local symlink creation unavailable: {error}")
    before = target.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_audit(audit, link)
    assert target.read_bytes() == before


def test_nonfinite_export_preserves_existing_managed_file(audit, tmp_path):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()
    broken = deepcopy(audit)
    broken["not_finite"] = float("nan")
    with pytest.raises(ValueError, match="FINITE_JSON_AUDIT_REQUIRED"):
        verifier.write_audit(broken, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage46b-*.tmp"))


def test_failed_replace_preserves_previous_output_and_cleans_temporary(audit, tmp_path, monkeypatch):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()

    def fail_replace(_source, _target):
        raise OSError("Synthetic local replace failure")

    monkeypatch.setattr(verifier.os, "replace", fail_replace)
    with pytest.raises(OSError, match="Synthetic local replace failure"):
        verifier.write_audit(audit, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage46b-*.tmp"))


CLI = ROOT / "tools/verify_stage50b_ltu_hybrid_swq_and_maxbd.py"


def _run_cli(source_root, *arguments):
    return subprocess.run([sys.executable, str(CLI), "--root", str(source_root), *map(str, arguments)],
                          cwd=ROOT, capture_output=True, text=True, timeout=20, check=False)


@pytest.mark.parametrize("strict,expected_exit", ((False, 0), (True, 1)))
def test_cli_default_and_strict_modes_export_qualified_audit(source_root, strict, expected_exit):
    output = source_root / "cli-audit.json"
    arguments = ["--output", output]
    if strict:
        arguments.append("--strict")
    completed = _run_cli(source_root, *arguments)
    assert completed.returncode == expected_exit, completed.stdout + completed.stderr
    status = json.loads(completed.stdout)
    assert status["status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert status["trials"] == 9
    assert status["native_acceptance"] is False
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["task_id"] == verifier.TASK_ID
    assert exported["stage50b"]["native_acceptance"] is False


def test_cli_refuses_input_overwrite_without_touching_source(source_root):
    source = source_root / SOURCE
    before = source.read_bytes()
    completed = _run_cli(source_root, "--output", source)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert source.read_bytes() == before


def test_cli_drifted_source_returns_error_without_export(source_root):
    source = source_root / SOURCE
    document = json.loads(source.read_text(encoding="utf-8-sig"))
    document["stage"] = "ALTERED"
    source.write_text(json.dumps(document), encoding="utf-8")
    output = source_root / "cli-audit.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["native_dispatch_allowed"] is False
    assert not output.exists()


@pytest.mark.parametrize("relative", ("docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"))
def test_current_docs_stay_compact_with_a_single_first_line_doc_head(relative):
    lines = (ROOT / relative).read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) < 250
    assert lines[0].startswith("<!-- doc-head:")
    assert sum("<!-- doc-head:" in line for line in lines) == 1
    assert sum("<!-- /doc-head -->" in line for line in lines) == 1


def test_module_and_cli_ast_have_no_native_or_bench_runner_imports_or_dispatch():
    allowed = {"__future__", "argparse", "hashlib", "json", "math", "os", "pathlib", "re", "statistics", "sys", "tempfile",
               "controller.stage42a_netdev_txq_and_airos6_verifier",
               "controller.stage48b_ltu_ota_triple_play_and_loop_flee_verifier",
               "controller.stage50b_ltu_hybrid_swq_and_maxbd_verifier"}
    for path in (Path(verifier.__file__), CLI):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name in allowed for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module in allowed
            elif isinstance(node, ast.Call):
                function = node.func
                name = function.id if isinstance(function, ast.Name) else getattr(function, "attr", "")
                if isinstance(function, ast.Name):
                    assert name not in {"__import__", "eval", "exec", "compile"}
                assert name not in {"system", "popen", "Popen", "run", "check_call", "check_output", "spawn",
                                    "socket", "connect", "urlopen", "CDLL", "WinDLL", "dlopen"}


