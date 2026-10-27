"""Offline Stage44B tests; CLI checks use disposable local source fixtures."""
import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from controller import stage48b_ltu_ota_triple_play_and_loop_flee_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "artifacts/autoresearch/stage48b_ltu_ota_triple_play_and_standalone_poe_20261025.json"
REPORT = "docs/STAGE48B_LTU_OTA_TRIPLE_PLAY_AND_STANDALONE_POE_BENCHMARK.md"
SOURCE_PIN = "3e75a0c9d2d20127a29d6a8fd5bfa4cdbf513c88a65ddc59014caddc7d617f02"
REPORT_PIN = "259e96b1c930570bcb6be8eb4a0e5cc0a5b71dd32ab2dfb73db307319ccbb6eb"
STOCK = "S48B-R0-STOCK-QUEUE"
CHAMPION = "S48B-R1-CHAMPION-V1"
TRIAL_PINS = (
    "9561375819a87e9f635bf6e53bbab97b650e8d25212c1dbcfc401c6bde93d411",
    "9b1774fb3873ce4e84dee8733f1b1c7ba04ce8000c689b392adc8e9c806468fb",
    "49de972a3e426c715f539a191e266622aad22dc28c0171b728c71d821cf26a35",
    "112387c6d7b0c5250bbac5bf69c8caa07e35c706a50695265b98ccec37b82a24",
    "6fb031ab406fb1a1aeffafaf0027d4ca81820d1ffa237da8a527fe1deb7c5cfe",
    "2f090ae6931ef2dbffa091caa88156b868e84bfd7e587269395db53b0688e96b",
)


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture(scope="module")
def saved_sources():
    return (
        json.loads((ROOT / SOURCE).read_text(encoding="utf-8-sig")),
        (ROOT / REPORT).read_bytes().decode("utf-8"),
    )


@pytest.fixture
def document(saved_sources):
    return deepcopy(saved_sources[0])


@pytest.fixture
def source_root(tmp_path):
    for relative in (SOURCE, REPORT):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / relative).read_bytes())
    return tmp_path


def test_whole_saved_json_report_and_six_trials_have_independent_exact_bindings(saved_sources):
    document, report = saved_sources
    assert _digest(document) == SOURCE_PIN
    assert hashlib.sha256(report.encode()).hexdigest() == REPORT_PIN
    assert tuple(_digest(trial) for trial in document["trials"]) == TRIAL_PINS
    assert isinstance(verifier.source_contract(document, report), dict)


@pytest.mark.parametrize("index", range(6))
def test_every_trial_is_content_pinned(document, saved_sources, index):
    document["trials"][index]["bulk_tcp_mbps"] += 1
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1])


@pytest.mark.parametrize("key", ("timestamp_utc", "standalone_poe_keeper_persistence",
                                   "ota_link_verification_post_bench", "summary_by_profile", "extra_field"))
def test_json_envelope_is_pinned_outside_trials(document, saved_sources, key):
    document[key] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1])


@pytest.mark.parametrize("change", ("append", "newlines", "claim"))
def test_report_binding_preserves_original_bytes(saved_sources, change):
    document, report = saved_sources
    changed = {
        "append": report + "\n",
        "newlines": report.replace("\r\n", "\n") if "\r\n" in report else report.replace("\n", "\r\n"),
        "claim": report.replace("-92.5", "-82.5"),
    }[change]
    assert changed != report
    with pytest.raises(ValueError):
        verifier.source_contract(document, changed)


MEAN_FIELDS = {
    "bulk_tcp_mbps": "mean_bulk_tcp_mbps", "iptv_udp_mbps": "mean_iptv_udp_mbps",
    "iptv_jitter_ms": "mean_iptv_jitter_ms", "iptv_loss_pct": "mean_iptv_loss_pct",
    "voip_jitter_ms": "mean_voip_jitter_ms", "voip_loss_pct": "mean_voip_loss_pct",
    "loaded_ping_p50_ms": "mean_loaded_ping_p50_ms", "loaded_ping_p95_ms": "mean_loaded_ping_p95_ms",
    "loaded_ping_p99_ms": "mean_loaded_ping_p99_ms",
}


def test_all_six_trials_and_reported_means_are_preserved_and_recomputed(saved_sources):
    document, report = saved_sources
    original = _digest(document)
    result = verifier.audit_stage48b(document, report)
    assert _digest(document) == original
    assert len(result["trials"]) == 6
    assert result["design"]["listed_order"] == [
        {"profile_id": profile, "rep": rep} for rep in (1, 2, 3) for profile in (STOCK, CHAMPION)]
    for profile in (STOCK, CHAMPION):
        selected = [trial for trial in document["trials"] if trial["profile_id"] == profile]
        for field, summary_field in MEAN_FIELDS.items():
            expected = round(sum(trial[field] for trial in selected) / 3, 3)
            comparison = result["profiles"][profile]["summary_comparisons"][summary_field]
            assert comparison["recomputed"] == expected
            assert comparison["reported"] == document["summary_by_profile"][profile][summary_field]
            assert comparison["consistent"] is True
    assert result["audit_status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert result["native_acceptance"] is False
    assert result["physical_status"] == "UNKNOWN"


def test_latency_reduction_is_reported_with_throughput_and_iptv_loss_tradeoffs(saved_sources):
    result = verifier.audit_stage48b(*saved_sources)
    changes = result["changes_pct"]
    assert changes["mean_loaded_ping_p50_ms"] < -90
    assert changes["mean_loaded_ping_p95_ms"] < -80
    assert changes["mean_bulk_tcp_mbps"] < 0
    assert changes["mean_iptv_udp_mbps"] < 0
    assert changes["mean_voip_jitter_ms"] > 0
    means = result["profiles"][CHAMPION]["means"]
    assert means["mean_bulk_tcp_mbps"] == 15.892
    assert means["mean_iptv_udp_mbps"] == 8.867
    assert means["mean_iptv_loss_pct"] == 3.254
    loss = next(item for item in result["findings"] if item["code"] == "IPTV_LOSS_TRADEOFF_NOT_SHOWN_IN_MAIN_REPORT_TABLE")
    assert loss["candidate_rep1_pct"] == 9.456
    assert loss["candidate_mean_pct"] == 3.254


def test_n5_latency_summaries_are_mean_trial_quantiles_and_not_pooled_tail_evidence(saved_sources):
    result = verifier.audit_stage48b(*saved_sources)
    assert all(trial["ping_samples"] == 5 for trial in result["trials"])
    assert all(trial["values"]["loaded_ping_p95_ms"] == trial["values"]["loaded_ping_p99_ms"] for trial in result["trials"])
    for profile in result["profiles"].values():
        assert profile["latency_statistic"] == "MEAN_OF_THREE_PER_TRIAL_QUANTILES_NOT_POOLED_QUANTILE"
    design = result["design"]
    assert design["five_samples_per_trial"] is True
    assert design["p95_p99_alias_under_reported_n5_rank_recipe"] is True
    assert design["timestamps_raw_ping_and_receiver_counts"] == "MISSING"
    assert design["source_declared_counterbalancing_is_abba"] is False
    assert design["randomization_proven"] is False
    assert design["isolated_treatment_effect_proven"] is False
    assert design["cross_profile_state_restoration_proven"] is False


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown_profile", "bad_rep"))
def test_trial_inventory_requires_six_unique_known_profile_rep_pairs(document, saved_sources, change):
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
        verifier.audit_stage48b(document, saved_sources[1])


@pytest.mark.parametrize("field", tuple(MEAN_FIELDS) + ("voip_udp_mbps", "bulk_tcp_retransmits", "loaded_ping_samples"))
def test_trial_measurements_never_coerce_booleans_to_numbers(document, saved_sources, field):
    document["trials"][0][field] = True
    with pytest.raises(ValueError):
        verifier.audit_stage48b(document, saved_sources[1])


@pytest.mark.parametrize("field,bad", (
    ("bulk_tcp_retransmits", 0.5), ("bulk_tcp_retransmits", 2**53),
    ("loaded_ping_samples", 0), ("loaded_ping_p50_ms", 1000),
    ("iptv_loss_pct", 101), ("voip_jitter_ms", float("nan")), ("iptv_udp_mbps", -1),
))
def test_trial_metrics_require_finite_counts_order_and_loss_ranges(document, saved_sources, field, bad):
    document["trials"][0][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage48b(document, saved_sources[1])


def test_changed_summary_is_a_finding_instead_of_replacing_trial_measurements(document, saved_sources):
    document["summary_by_profile"][CHAMPION]["mean_bulk_tcp_mbps"] = 99
    result = verifier.audit_stage48b(document, saved_sources[1])
    comparison = result["profiles"][CHAMPION]["summary_comparisons"]["mean_bulk_tcp_mbps"]
    assert comparison == {"reported": 99.0, "recomputed": 15.892, "consistent": False}
    assert any(item["code"] == "SUMMARY_MEAN_DISAGREES" for item in result["findings"])
    assert result["native_acceptance"] is False


@pytest.mark.parametrize("value,dscp,ecn", ((0x80, 32, 0), (0x81, 32, 1), (0x83, 32, 3),
                                           (0xB8, 46, 0), (0xBB, 46, 3), (0xFF, 63, 3)))
def test_tos_byte_separates_dscp_from_ecn_without_asserting_private_firmware_abi(value, dscp, ecn):
    decoded = verifier.decode_tos_byte(value)
    assert decoded["dscp"] == dscp
    assert decoded["ecn"] == ecn
    assert decoded["ecn_agnostic_mask"] == 0xFC
    assert decoded["private_firmware_selector_abi_qualified"] is False


@pytest.mark.parametrize("bad", (True, -1, 256, 128.0, "0x80", None))
def test_tos_input_is_an_unsigned_byte_without_coercion(bad):
    with pytest.raises(ValueError):
        verifier.decode_tos_byte(bad)


@pytest.fixture
def gains():
    return {"initial_rssi": [-116, -107], "final_rssi": [-83, -80], "peak_rssi": [-80, -78],
            "initial_rxgain": [51, 50], "final_rxgain": [75, 74], "claimed_gain_db": 36}


def test_reported_gain_math_is_per_chain_and_does_not_prove_causality(gains):
    result = verifier.gain_claim_arithmetic(**gains)
    assert result["report_only_final_rssi_delta_db"] == [33, 27]
    assert result["report_only_peak_rssi_delta_db"] == [36, 29]
    assert result["report_only_rxgain_delta_db"] == [24, 24]
    assert result["claim_applies_to_all_final_chains"] is False
    assert result["native_gain_causality_proven"] is False
    assert result["synchronized_before_after_capture"] == "MISSING"


@pytest.mark.parametrize("field,bad", (
    ("initial_rssi", [-116]), ("final_rssi", [-83, -80, -79]), ("peak_rssi", "-80,-78"),
    ("initial_rxgain", [True, 50]), ("final_rxgain", [75, float("inf")]),
    ("claimed_gain_db", True), ("claimed_gain_db", float("nan")),
))
def test_gain_math_requires_two_finite_numeric_chains(gains, field, bad):
    gains[field] = bad
    with pytest.raises(ValueError):
        verifier.gain_claim_arithmetic(**gains)


def test_gain_subtraction_cannot_overflow_to_nonfinite_delta(gains):
    gains["initial_rssi"] = [-1e308, -107]
    gains["final_rssi"] = [1e308, -80]
    with pytest.raises(ValueError):
        verifier.gain_claim_arithmetic(**gains)


@pytest.fixture
def progress(document):
    return document["standalone_poe_keeper_persistence"]["ltu1_boca5"]["cfgmtd_out"]


def test_progress_backspaces_render_two_successful_partition_receipts_but_not_cold_boot(progress):
    result = verifier.audit_progress_receipt(progress, 0)
    assert "\b" in result["raw_progress"]
    assert "\b" not in result["rendered_progress"]
    assert "Storing Active[1] ... [%100]" in result["rendered_progress"]
    assert "Active->Backup[2] ... [%100]" in result["rendered_progress"]
    assert result["dual_partition_progress_complete"] is True
    assert result["command_success_receipt"] is True
    assert result["persisted_content_readback_proven"] is False
    assert result["unattended_cold_boot_proven"] is False


def test_nonzero_command_exit_does_not_become_success_from_progress_text(progress):
    result = verifier.audit_progress_receipt(progress, 1)
    assert result["dual_partition_progress_complete"] is True
    assert result["command_success_receipt"] is False


@pytest.mark.parametrize("change", ("missing", "reversed", "duplicate", "error"))
def test_incomplete_ambiguous_or_error_progress_is_not_a_success_receipt(progress, change):
    if change == "missing":
        text = "Storing Active[1] ... [%100]"
    elif change == "reversed":
        text = "Active->Backup[2] ... [%100]\nStoring Active[1] ... [%100]"
    elif change == "duplicate":
        text = progress + "\nStoring Active[1] ... [%100]"
    else:
        text = progress + "\nERROR: write incomplete"
    assert verifier.audit_progress_receipt(text, 0)["command_success_receipt"] is False


@pytest.mark.parametrize("bad", (True, -1, 256, "0", 0.0))
def test_progress_exit_code_is_strict_bounded_integer(progress, bad):
    with pytest.raises(ValueError):
        verifier.audit_progress_receipt(progress, bad)


@pytest.mark.parametrize("bad", ("", "a\0b", "a" * 8193, None))
def test_progress_text_is_bounded_and_control_safe(bad):
    with pytest.raises(ValueError):
        verifier.audit_progress_receipt(bad, 0)


def test_qdisc_excerpt_preserves_present_leaf_without_inventing_missing_tree(document):
    stock = verifier.audit_qdisc_excerpt(document["trials"][0]["ath0_qdisc"], profile_id=STOCK)
    target = verifier.audit_qdisc_excerpt(document["trials"][1]["ath0_qdisc"], profile_id=CHAMPION)
    assert stock["root_kind"] == "fq_codel"
    assert target["root_kind"] == "htb"
    assert target["leaf_excerpts"] == [{"kind": "fq_codel", "handle": "10:", "parent": "1:10"}]
    for result in (stock, target):
        assert result["profile_root_matches"] is True
        for key in ("complete_class_filter_tree_proven", "module_identity_proven", "private_dscp_readback_proven",
                    "eab_ring_occupancy_proven", "zero_host_backlog_proves_empty_firmware_queue"):
            assert result[key] is False


def test_wrong_qdisc_root_is_a_finding_and_duplicate_roots_are_ambiguous(document):
    text = document["trials"][0]["ath0_qdisc"]
    assert verifier.audit_qdisc_excerpt(text, profile_id=CHAMPION)["profile_root_matches"] is False
    with pytest.raises(ValueError):
        verifier.audit_qdisc_excerpt(text + "\n" + text, profile_id=STOCK)


def test_persistence_gain_loop_and_classifier_evidence_remain_qualified(saved_sources):
    result = verifier.audit_stage48b(*saved_sources)
    for receipt in result["persistence"]["receipts"].values():
        assert receipt["command_success_receipt"] is True
        assert receipt["unattended_cold_boot_proven"] is False
    assert result["persistence"]["cold_boot_proven"] is False
    assert result["persistence"]["direct_unreachable_proves_no_wired_bypass"] is False
    assert result["persistence"]["persisted_config_and_deployed_script_hashes"] == "MISSING"
    assert result["loop_flee"]["switch_bridge_vlan_readbacks"] == "MISSING"
    assert result["loop_flee"]["permanent_elimination_proven"] is False
    assert result["link_snapshot"]["standalone_ota_route_isolation_proven"] is False
    assert result["htb_dscp"]["u32_filters_and_full_class_tree"] == "MISSING"
    assert result["htb_dscp"]["private_firmware_selector_abi"] == "UNKNOWN"
    assert result["htb_dscp"]["native_eab_occupancy_proven"] is False


@pytest.fixture
def audit(source_root):
    return verifier.audit_saved_sources(source_root)


def test_atomic_export_roundtrips_and_allows_managed_audit_refresh(audit, tmp_path):
    output = tmp_path / "audit.json"
    assert verifier.write_audit(audit, output) == output
    assert json.loads(output.read_text(encoding="utf-8")) == audit
    updated = deepcopy(audit)
    updated["test_refresh_marker"] = "second managed export"
    verifier.write_audit(updated, output)
    assert json.loads(output.read_text(encoding="utf-8"))["test_refresh_marker"] == "second managed export"
    assert not list(tmp_path.glob(".stage44b-*.tmp"))


@pytest.mark.parametrize("existing", ({"other": "data"}, {"task_id": "OTHER", "audit_version": 1},
                                      {"task_id": verifier.TASK_ID, "audit_version": True}))
def test_export_refuses_unowned_existing_json_and_preserves_content(audit, tmp_path, existing):
    output = tmp_path / "existing.json"
    output.write_text(json.dumps(existing), encoding="utf-8")
    before = output.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_audit(audit, output)
    assert output.read_bytes() == before


def test_export_refuses_protected_source_even_when_path_is_json(audit, source_root):
    source = source_root / SOURCE
    before = source.read_bytes()
    with pytest.raises(ValueError, match="SOURCE_OVERWRITE_REJECTED"):
        verifier.write_audit(audit, source, protected_paths=(source, source_root / REPORT))
    assert source.read_bytes() == before


@pytest.mark.parametrize("filename", ("audit.txt", "audit.py", "NUL.json", "CON.json", "COM1.json", "bad name.json"))
def test_export_requires_literal_nondevice_json_filename(audit, tmp_path, filename):
    output = tmp_path / filename
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError):
        verifier.write_audit(audit, output)
    # Windows exposes DOS devices through exists() even without a directory entry.
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("path", ("//example.invalid/share/audit.json", "https://example.invalid/audit.json",
                                  "file:///tmp/audit.json", "C:audit.json", "\\\\?\\C:\\audit.json", "bad\0.json"))
def test_export_rejects_network_uri_device_or_nul_paths_before_access(audit, path):
    with pytest.raises(ValueError):
        verifier.write_audit(audit, path)


def test_symlink_output_is_rejected_without_modifying_target(audit, tmp_path):
    target = tmp_path / "target.json"
    target.write_text(json.dumps(audit), encoding="utf-8")
    link = tmp_path / "link.json"
    try:
        os.symlink(target, link)
    except OSError as error:
        pytest.skip(f"Local symlink creation unavailable: {error}")
    before = target.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_audit(audit, link)
    assert target.read_bytes() == before


def test_failed_serialization_leaves_existing_managed_output_unchanged(audit, tmp_path):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()
    broken = deepcopy(audit)
    broken["invalid_number"] = float("nan")
    with pytest.raises(ValueError):
        verifier.write_audit(broken, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage44b-*.tmp"))


def test_failed_atomic_replace_preserves_output_and_cleans_temporary_file(audit, tmp_path, monkeypatch):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()

    def fail_replace(_source, _target):
        raise OSError("Synthetic local replace failure")

    monkeypatch.setattr(verifier.os, "replace", fail_replace)
    with pytest.raises(OSError, match="Synthetic local replace failure"):
        verifier.write_audit(audit, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage44b-*.tmp"))


CLI = ROOT / "tools/verify_stage48b_ltu_ota_triple_play.py"


def _run_cli(source_root, *arguments):
    return subprocess.run([sys.executable, str(CLI), "--root", str(source_root), *map(str, arguments)],
                          cwd=ROOT, capture_output=True, text=True, timeout=20, check=False)


@pytest.mark.parametrize("strict,expected_exit", ((False, 0), (True, 1)))
def test_cli_exports_qualified_audit_in_default_and_strict_modes(source_root, strict, expected_exit):
    output = source_root / "cli-audit.json"
    arguments = ["--output", output]
    if strict:
        arguments.append("--strict")
    completed = _run_cli(source_root, *arguments)
    assert completed.returncode == expected_exit, completed.stderr + completed.stdout
    status = json.loads(completed.stdout)
    assert status["status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert status["trials"] == 6
    assert status["native_acceptance"] is False
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["task_id"] == verifier.TASK_ID
    assert exported["stage48b"]["native_acceptance"] is False


def test_cli_source_overwrite_error_preserves_source(source_root):
    source = source_root / SOURCE
    before = source.read_bytes()
    completed = _run_cli(source_root, "--output", source)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert source.read_bytes() == before


def test_cli_drifted_source_exits_two_without_export(source_root):
    source = source_root / SOURCE
    document = json.loads(source.read_text(encoding="utf-8"))
    document["stage"] = "ALTERED"
    source.write_text(json.dumps(document), encoding="utf-8")
    output = source_root / "cli-audit.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["native_dispatch_allowed"] is False
    assert not output.exists()


@pytest.mark.parametrize("relative", ("docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"))
def test_live_index_docs_stay_compact_with_a_single_opening_doc_head(relative):
    lines = (ROOT / relative).read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) < 250
    assert lines[0].startswith("<!-- doc-head:")
    assert sum("<!-- doc-head:" in line for line in lines) == 1
    assert sum("<!-- /doc-head -->" in line for line in lines) == 1


def test_module_and_cli_ast_do_not_import_or_dispatch_native_or_bench_runners():
    allowed = {"__future__", "argparse", "hashlib", "json", "math", "os", "pathlib", "re", "sys", "tempfile",
               "controller.stage42a_netdev_txq_and_airos6_verifier",
               "controller.stage48b_ltu_ota_triple_play_and_loop_flee_verifier"}
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
                assert name not in {"system", "popen", "Popen", "run", "check_call", "check_output",
                                    "spawn", "socket", "connect", "urlopen", "CDLL", "WinDLL", "dlopen"}

