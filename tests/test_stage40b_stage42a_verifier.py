"""Saved JSON and literal-text fixtures only; no device runner imports or execution."""
from __future__ import annotations

import copy
import ast
import json
from pathlib import Path

import pytest

from controller import stage42a_netdev_txq_and_airos6_verifier as subject


ROOT = Path(__file__).resolve().parents[1]
STAGE42 = ROOT / "artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json"
STAGE40 = ROOT / "artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json"
INTERFACES = ("br-lan", "phy0-ap0", "phy0-ap0.sta17")


@pytest.fixture
def documents():
    # Parse data only, never recipes, controllers, rc.poststart or firmware bytes.
    return json.loads(STAGE42.read_text(encoding="utf-8")), json.loads(STAGE40.read_text(encoding="utf-8"))


def txq_text(values=None):
    values = {name: 1000 for name in INTERFACES} if values is None else values
    return "\n\n".join(f"==> /sys/class/net/{name}/tx_queue_len <==\n{value}"
                          for name, value in values.items()) + "\n"


def test_canonical_digest_ignores_key_order_but_not_types_or_values():
    assert subject.canonical_digest({"a": 1, "b": [2, 3]}) == subject.canonical_digest({"b": [2, 3], "a": 1})
    assert subject.canonical_digest({"allowed": False}) != subject.canonical_digest({"allowed": 0})
    assert subject.canonical_digest({"a": [2, 3]}) != subject.canonical_digest({"a": [3, 2]})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_digest_does_not_silently_serialize_nonfinite_metadata(value):
    with pytest.raises(ValueError): subject.canonical_digest({"value": value})


def test_tx_queue_len_header_parser_keeps_exact_dynamic_interface_names():
    result = subject.parse_tx_queue_len_readback(txq_text(), expected_interfaces=INTERFACES)
    assert result == {name: 1000 for name in INTERFACES}
    varied = {"br-lan": 256, "phy0-ap0": 128, "phy0-ap0.sta17": 2**32 - 1}
    assert subject.parse_tx_queue_len_readback(txq_text(varied), expected_interfaces=INTERFACES) == varied


@pytest.mark.parametrize("attack", ["duplicate", "missing", "extra", "truncated", "overflow", "negative", "bool",
    "nan", "wrong_path", "wrong_header", "extra_value", "nul"])
def test_tx_queue_len_malformed_or_partial_readback_never_becomes_a_write_intent(attack):
    raw = txq_text()
    if attack == "duplicate": raw += txq_text({"br-lan": 128})
    elif attack == "missing": raw = txq_text({name: 1000 for name in INTERFACES[:-1]})
    elif attack == "extra": raw += txq_text({"eth99": 128})
    elif attack == "truncated": raw = raw.rstrip("\n")
    elif attack == "overflow": raw = raw.replace("\n1000", f"\n{2**32}", 1)
    elif attack == "negative": raw = raw.replace("\n1000", "\n-1", 1)
    elif attack == "bool": raw = raw.replace("\n1000", "\nTrue", 1)
    elif attack == "nan": raw = raw.replace("\n1000", "\nNaN", 1)
    elif attack == "wrong_path": raw = raw.replace("/sys/class/net/br-lan/", "/tmp/br-lan/")
    elif attack == "wrong_header": raw = raw.replace("==>", "=>", 1)
    elif attack == "extra_value": raw += "1000\n"
    else: raw += "\x00\n"
    with pytest.raises(ValueError): subject.parse_tx_queue_len_readback(raw, expected_interfaces=INTERFACES)


def test_airos6_unpolled_state_requires_all_three_explicit_coordinates():
    baseline = dict(txop_params="0 0", no_ack_rate="0 -1", no_auto_prio=0)
    assert subject.assess_airos6_state(baseline)["unpolled_compatible"] is True
    treatment = dict(txop_params="15 5", no_ack_rate="1 -1", no_auto_prio=1)
    assert subject.assess_airos6_state(treatment)["unpolled_compatible"] is False
    assert subject.assess_airos6_state({})["unpolled_compatible"] is None
    assert subject.assess_airos6_state(dict(txop_params="", no_ack_rate="", no_auto_prio=""))["unpolled_compatible"] is None
    for field, value in [("txop_params", "15 5"), ("no_ack_rate", "1 -1"), ("no_auto_prio", 1)]:
        altered = dict(baseline); altered[field] = value
        assert subject.assess_airos6_state(altered)["unpolled_compatible"] is False


@pytest.mark.parametrize("probe", [None, False, True])
def test_absent_configuration_or_probe_path_does_not_mean_snooping_disabled(probe):
    result = subject.bridge_snooping_evidence(config_text=None, probe_exists=probe)
    assert result["config_state"] == "UNKNOWN"
    assert subject.bridge_snooping_evidence(config_text="", probe_exists=probe)["config_state"] == "UNKNOWN"


@pytest.mark.parametrize("text,expected", [("CONFIG_BRIDGE_IGMP_SNOOPING=y\n", "ENABLED"),
    ("# CONFIG_BRIDGE_IGMP_SNOOPING is not set\n", "DISABLED"), ("CONFIG_BRIDGE=y\n", "UNKNOWN")])
def test_only_explicit_kernel_config_stanza_establishes_snooping_configuration(text, expected):
    result = subject.bridge_snooping_evidence(config_text=text, probe_exists=False)
    assert result["config_state"] == expected and result["sysfs_state"] == "ABSENT"
    assert result["native_build_authenticated"] is False
    assert result["version_or_empty_getter_proves_config"] is False


@pytest.mark.parametrize("text", ["CONFIG_BRIDGE_IGMP_SNOOPING=m\n",
    "CONFIG_BRIDGE_IGMP_SNOOPING=y\n# CONFIG_BRIDGE_IGMP_SNOOPING is not set\n",
    "CONFIG_BRIDGE_IGMP_SNOOPING=y\nCONFIG_BRIDGE_IGMP_SNOOPING=y\n"])
def test_ambiguous_or_unsupported_kernel_configuration_cannot_be_certified(text):
    with pytest.raises(ValueError): subject.bridge_snooping_evidence(config_text=text)


def test_one_byte_splice_layout_preserves_original_mapping_and_two_exact_offsets():
    result = subject.patch_splice_layout(2000000)
    assert result["same_size"] is True and result["preserved_mapping"] is True
    assert result["patch_offsets"] == [1756200, 1756264]
    assert subject.assess_byte_emission(None, expected=5)["state"] == "UNKNOWN"
    assert subject.assess_byte_emission(bytes([5]), expected=5)["state"] == "MATCH"
    assert subject.assess_byte_emission(b"\\x05", expected=5)["state"] == "MISMATCH"
    assert subject.assess_byte_emission(b"", expected=5)["state"] == "MISMATCH"


def test_four_literal_characters_change_splice_size_and_mapping_not_just_content():
    result = subject.patch_splice_layout(2000000, payload_lengths=(4, 4))
    assert result["same_size"] is False and result["preserved_mapping"] is False
    equal_total = subject.patch_splice_layout(2000000, payload_lengths=(0, 2))
    assert equal_total["same_size"] is True and equal_total["preserved_mapping"] is False
    wrong_skip = subject.patch_splice_layout(2000000, middle_skip=1756202)
    assert wrong_skip["preserved_mapping"] is False


@pytest.mark.parametrize("kwargs", [dict(source_size=True), dict(source_size=-1), dict(source_size=1756200),
    dict(source_size=2000000, prefix_bytes=True), dict(source_size=2000000, middle_count=-1),
    dict(source_size=2000000, payload_lengths=(True, 1))])
def test_splice_arithmetic_rejects_undefined_negative_or_boolean_coordinates(kwargs):
    with pytest.raises(ValueError): subject.patch_splice_layout(**kwargs)


@pytest.mark.parametrize("expected", [True, -1, 256])
def test_expected_byte_must_be_exact_u8_not_a_boolean(expected):
    with pytest.raises(ValueError): subject.assess_byte_emission(b"x", expected=expected)


def test_poststart_literal_extraction_is_ast_only_and_does_not_execute_module_code():
    source = "raise RuntimeError('must never execute')\nLTU1_RC_POSTSTART = '#!/bin/sh\\necho -ne \\\"\\\\x05\\\"\\n'\nLTU2_RC_POSTSTART = '#!/bin/sh\\nprintf x\\n'\n"
    literals = subject.extract_poststart_literals(source)
    assert literals["LTU1_RC_POSTSTART"].startswith("#!/bin/sh\n")
    assert "echo -ne" in literals["LTU1_RC_POSTSTART"] and "printf" in literals["LTU2_RC_POSTSTART"]


@pytest.mark.parametrize("source", ["LTU1_RC_POSTSTART = str('x')\nLTU2_RC_POSTSTART='y'\n",
    "LTU1_RC_POSTSTART='x'\n", "LTU1_RC_POSTSTART='x'\nLTU1_RC_POSTSTART='y'\nLTU2_RC_POSTSTART='z'\n"])
def test_computed_missing_or_duplicate_poststart_assignments_are_not_saved_literal_proof(source):
    with pytest.raises(ValueError): subject.extract_poststart_literals(source)


def test_poststart_size_and_line_counts_never_certify_deployed_bytes_or_binary_patch():
    script = "#!/bin/sh\necho -ne '\\x05'\nprintf '%s' x\n"
    result = subject.audit_poststart_script(script, recorded_bytes=len(script.encode()), recorded_lines=3)
    assert result["current_bytes"] == len(script.encode()) and result["current_lines"] == 3
    assert result["size_matches"] is True and result["line_count_matches"] is True
    assert result["exact_deployed_script_verified"] is False and result["patch_binary_verified"] is False
    assert result["uses_echo_ne"] is True and result["uses_printf"] is True
    drift = subject.audit_poststart_script(script, recorded_bytes=1, recorded_lines=100)
    assert drift["size_matches"] is False and drift["line_count_matches"] is False


def test_source_contract_rejects_round_and_poststart_drift(documents):
    stage42, stage40 = documents
    subject.source_contract(stage42, stage40)
    for source in ("stage42", "stage40", "poststart"):
        first, second = copy.deepcopy(stage42), copy.deepcopy(stage40)
        if source == "stage42": first["rounds"][0]["goodput_delta_pct"] = -8.352
        elif source == "stage40": second["rounds"]["S40A-R2"]["deltas"]["goodput_delta_pct"] = 999
        else: second["ltu_persistent_poststart_receipt"]["ltu1_boca5"]["frequency_mhz"] = 2400
        with pytest.raises(ValueError): subject.source_contract(first, second)


def test_stage42_saved_semantics_refute_titles_without_inventing_physical_reexecution(documents):
    result = subject.audit_stage42a(documents[0])
    assert result["windows"] == 16 and set(result["rounds"]) == {f"S42A-R{i}" for i in range(1, 5)}
    rounds = result["rounds"]
    assert rounds["S42A-R1"]["metrics"]["goodput_delta_pct"] == -8.346
    assert rounds["S42A-R2"]["metrics"]["goodput_delta_pct"] == -1.403
    assert rounds["S42A-R1"]["queue_intent_observed"] is False
    assert rounds["S42A-R2"]["queue_intent_observed"] is False
    assert rounds["S42A-R2"]["three_peer_window_complete"] is False
    assert rounds["S42A-R3"]["queue_intent_observed"] is True
    assert rounds["S42A-R3"]["metrics"]["p95_rtt_delta_pct"] == 2.378
    assert rounds["S42A-R3"]["metrics"]["voip_mean_loss_pct"] == {"A": 2.1685, "B": 2.1666}
    assert rounds["S42A-R4"]["metrics"]["goodput_delta_pct"] == -3.003
    assert rounds["S42A-R4"]["metrics"]["p95_rtt_delta_pct"] == 29.472
    assert result["historical_champion_retained"] is True
    assert result["global_optimum_proven"] is False and result["physical_acceptance"] is False
    assert result["source_authentication"] == "NOT_CHECKED_BY_THIS_FUNCTION"
    assert "NETDEV_INTENT_NOT_OBSERVED" in rounds["S42A-R1"]["issues"]
    assert "THREE_PEER_WINDOW_INCOMPLETE" in rounds["S42A-R2"]["issues"]


def test_stage40_distinguishes_loaded_ping_composite_latency_and_radio_route(documents):
    result = subject.audit_stage40a(documents[1])
    assert result["windows"] == 8 and set(result["rounds"]) == {"S40A-R1", "S40A-R2"}
    assert result["source_authentication"] == "NOT_CHECKED_BY_THIS_FUNCTION"
    first, second = result["rounds"]["S40A-R1"], result["rounds"]["S40A-R2"]
    assert first["route_qualification"] == "UNQUALIFIED_24GHZ_PATH"
    assert second["route_qualification"] == "LTU_5500MHZ"
    for name, saved_id in [(first, "S40A-R1"), (second, "S40A-R2")]:
        saved = documents[1]["rounds"][saved_id]
        a, b, m = saved["arm_a_summary"], saved["arm_b_summary"], name["metrics"]
        assert m["loaded_ping_p95_delta_pct"] == pytest.approx(
            (b["loaded_ping_p95_ms"] / a["loaded_ping_p95_ms"] - 1) * 100, abs=0.01)
        assert m["composite_p95_delta_pct"] == pytest.approx(saved["deltas"]["p95_rtt_delta_pct"], abs=0.01)
        assert m["qoe_goodput_delta_pct"] == pytest.approx(saved["deltas"]["goodput_delta_pct"], abs=0.01)
        assert m["bulk_tcp_delta_pct"] == pytest.approx(saved["deltas"]["bulk_tcp_delta_pct"], abs=0.01)
    assert second["metrics"]["loaded_ping_p95_delta_pct"] < 0 < second["metrics"]["composite_p95_delta_pct"]


def test_pinned_source_contract_binds_all_six_rounds_and_poststart_receipt(documents):
    contract = subject.source_contract(*documents)
    assert contract["source_authenticated"] is True and contract["windows"] == 24
    assert set(contract["round_bindings"]) == {f"S42A-R{i}" for i in range(1, 5)} | {"S40A-R1", "S40A-R2"}
    assert contract["poststart_receipt_sha256"] == subject.canonical_digest(
        documents[1]["ltu_persistent_poststart_receipt"])


@pytest.mark.parametrize("attack", ["missing_round", "duplicate_round", "missing_40_round", "missing_receipt"])
def test_source_authentication_cannot_ignore_missing_or_duplicate_members(documents, attack):
    first, second = copy.deepcopy(documents)
    if attack == "missing_round": first["rounds"] = [row for row in first["rounds"] if row["round_id"] != "S42A-R4"]
    elif attack == "duplicate_round": first["rounds"].append(copy.deepcopy(first["rounds"][0]))
    elif attack == "missing_40_round": del second["rounds"]["S40A-R2"]
    else: del second["ltu_persistent_poststart_receipt"]
    with pytest.raises(ValueError): subject.source_contract(first, second)


@pytest.mark.parametrize("attack", ["phase_container", "boolean_goodput", "nonfinite_p95"])
def test_semantic_audit_rejects_malformed_measured_windows_instead_of_success_defaults(documents, attack):
    first = copy.deepcopy(documents[0])
    row = first["rounds"][0]
    if attack == "phase_container": row["phases"]["B1"] = None
    elif attack == "boolean_goodput": row["phases"]["B1"]["aggregate_goodput_mbps"] = True
    else: row["phases"]["B1"]["sector_p95_rtt_ms"] = float("nan")
    with pytest.raises(ValueError): subject.audit_stage42a(first)


def test_saved_source_wrapper_parses_current_poststart_text_without_certifying_deployment():
    result = subject.audit_saved_sources(root=ROOT)
    assert result["source_contract"]["source_authenticated"] is True
    assert result["stage42a"]["windows"] == 16 and result["stage40a"]["windows"] == 8
    first, second = result["poststart"]["ltu1"], result["poststart"]["ltu2"]
    assert (first["current_bytes"], first["current_lines"]) == (5609, 101)
    assert first["size_matches"] is False and first["line_count_matches"] is False
    assert (second["current_bytes"], second["current_lines"]) == (4249, 78)
    assert second["size_matches"] is True and second["line_count_matches"] is True
    assert all(row["exact_deployed_script_verified"] is False and row["patch_binary_verified"] is False
               and row["native_emission"]["state"] == "UNKNOWN" for row in (first, second))
    assert result["device_access_executed"] is False and result["script_or_patch_executed"] is False
    assert result["runtime_dispatch_allowed"] is False and result["physical_acceptance"] is False


@pytest.mark.parametrize("text", ['{"rounds": [], "rounds": []}', '{"x": NaN}', '{"x": Infinity}', '[]'])
def test_local_json_reader_rejects_duplicate_keys_nonfinite_numbers_and_wrong_root(tmp_path, text):
    path = tmp_path / "fixture.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError): subject.read_json(path)


def test_extra_round_is_explicitly_unassessed_without_replacing_requested_four(documents):
    first, second = copy.deepcopy(documents)
    original_extra = subject.audit_stage42a(first)["unassessed_round_ids"]
    first["rounds"].append({"round_id": "S42A-R99"})
    assert subject.source_contract(first, second)["windows"] == 24
    assert subject.audit_stage42a(first)["unassessed_round_ids"] == sorted([*original_extra, "S42A-R99"])


def test_summary_and_composite_metric_drift_are_reported_by_unpinned_audits(documents):
    first, second = copy.deepcopy(documents)
    first["rounds"][0]["goodput_delta_pct"] = -8.352
    assert "SAVED_SUMMARY_MISMATCH" in subject.audit_stage42a(first)["rounds"]["S42A-R1"]["issues"]
    second["rounds"]["S40A-R2"]["phases"]["B1"]["p95_rtt_ms"] = 1.0
    row = subject.audit_stage40a(second)["rounds"]["S40A-R2"]
    assert "DERIVED_PHASE_METRIC_MISMATCH" in row["issues"] and "SAVED_SUMMARY_MISMATCH" in row["issues"]
    assert row["loaded_ping_samples_authenticated"] is False


def test_zero_loss_percentage_does_not_override_receiver_loss_count(documents):
    second = copy.deepcopy(documents[1])
    second["rounds"]["S40A-R1"]["phases"]["B1"]["iptv_lost_packets"] = 1
    row = subject.audit_stage40a(second)["rounds"]["S40A-R1"]
    assert "UDP_PERCENTAGE_MISMATCH" in row["issues"]
    assert row["phases"]["B1"]["receiver_observations"]["iptv"]["lost"] == 1


def test_all_saved_composite_formulas_recompute_but_raw_ping_authentication_stays_unknown(documents):
    result = subject.audit_stage40a(documents[1])
    for row in result["rounds"].values():
        assert "LOADED_PING_RAW_SAMPLES_NOT_SAVED" in row["issues"]
        assert row["composite_p95_is_raw_percentile"] is False and row["loaded_ping_samples_authenticated"] is False
        for phase in row["phases"].values():
            assert phase["formula_recomputation"]["matches_saved"] is True


def test_equal_full_uph_views_do_not_allow_uncaptured_tail_changes(documents):
    second = copy.deepcopy(documents[1])
    snapshot = second["rounds"]["S40A-R1"]["phases"]["B1"]["snapshot"]
    for name in ["FF_MCAST", "CMS_BIAS", "VOIP_BIAS", "FIXED_FRAME"]:
        values = snapshot[name].split(); values[1] = "9"; snapshot[name] = " ".join(values)
    row = subject.audit_stage40a(second)["rounds"]["S40A-R1"]
    assert row["phases"]["B1"]["alias_views_equal"] is True
    assert "UPH_NONFIRST_COMPONENT_DRIFT" in row["issues"]
    assert row["native_alias_addresses_proven"] is False


def test_dd_redirection_and_literal_escape_tokens_are_checked_without_execution():
    text = (ROOT / "tools/bench/deploy_stage40a_ltu_poststart.py").read_text(encoding="utf-8")
    script = subject.extract_poststart_literals(text)["LTU1_RC_POSTSTART"]
    result = subject.audit_poststart_script(script, recorded_bytes=5164, recorded_lines=94)
    assert result["layout_arithmetic_only"] is True and result["literal_emission_tokens_match_intent"] is True
    altered = script.replace("count=63 >> /tmp/air_fpga", "count=63 > /tmp/air_fpga")
    assert subject.audit_poststart_script(altered, recorded_bytes=5164, recorded_lines=94)["layout_arithmetic_only"] is False


def test_product_imports_remain_stdlib_only_under_the_explicit_offline_contract():
    tree = ast.parse(Path(subject.__file__).read_text(encoding="utf-8"))
    allowed = {"__future__", "ast", "ctypes", "hashlib", "json", "math", "os", "pathlib", "re", "stat"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import): assert all(alias.name in allowed for alias in node.names)
        elif isinstance(node, ast.ImportFrom): assert node.module in allowed


@pytest.mark.parametrize("path", [r"\\server\share\fixture.json", "//server/share/fixture.json",
    "/\\server/share/fixture.json", "https://example.test/data.json", "ssh://radio/data.json"])
def test_network_or_uri_inputs_fail_before_metadata_or_content_read(monkeypatch, path):
    def forbidden(*args, **kwargs):
        pytest.fail("network metadata/content must not be accessed")
    monkeypatch.setattr(Path, "lstat", forbidden)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError): subject.read_json(path)
    with pytest.raises(ValueError): subject.audit_saved_sources(root=path)


def test_reparse_or_symlink_inputs_fail_before_content_read(monkeypatch, tmp_path):
    path = tmp_path / "fixture.json"
    path.write_text("{}", encoding="utf-8")
    original_lstat = Path.lstat
    def observed(item):
        if item == path:
            return type("Info", (), {"st_mode": 0o100644, "st_file_attributes": 0x400})()
        return original_lstat(item)
    def forbidden(*args, **kwargs): pytest.fail("reparse target must not be read")
    monkeypatch.setattr(Path, "lstat", observed)
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError): subject.read_json(path)


@pytest.mark.parametrize("attack", ["ap_float", "ap_bool_threshold", "cpe_none", "cpe_bad_limits", "cpe_bad_threshold"])
def test_all_present_role_aql_readbacks_are_typed_and_validated(documents, attack):
    first = copy.deepcopy(documents[0])
    getter = first["rounds"][0]["phases"]["A1"]["getter_readback"]
    if attack == "ap_float": getter["ap_aql_txq_limit"]["VO"]["low_us"] = 300.0
    elif attack == "ap_bool_threshold": getter["ap_aql_threshold"] = True
    elif attack == "cpe_none": getter["loco_aql_txq_limit"] = None
    elif attack == "cpe_bad_limits": getter["loco_aql_txq_limit"] = {"VO": {"low_us": 1, "high_us": 2}}
    else: getter["loco_aql_threshold"] = 5000
    row = subject.audit_stage42a(first)["rounds"]["S42A-R1"]
    assert "AVAILABLE_V13_READBACK_MISMATCH" in row["issues"]
    assert row["phases"]["A1"]["available_v13"]["available_fields_match"] is False


def test_reordered_byte_emitters_do_not_pass_the_intended_splice_sequence():
    text = (ROOT / "tools/bench/deploy_stage40a_ltu_poststart.py").read_text(encoding="utf-8")
    script = subject.extract_poststart_literals(text)["LTU1_RC_POSTSTART"]
    lines = script.splitlines()
    emitters = [line for line in lines if line.strip().startswith("echo -ne ")]
    reordered = "\n".join([line for line in lines if line not in emitters] + emitters) + "\n"
    result = subject.audit_poststart_script(reordered, recorded_bytes=5164, recorded_lines=94)
    assert result["literal_emission_tokens_match_intent"] is True
    assert result["emitter_sequence_matches_intent"] is False and result["layout_arithmetic_only"] is False
