"""Stage45B offline saved-evidence and disposable local CLI regressions."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from controller import stage51a_v17_and_stage49b_ltu_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
SOURCE_51A = "artifacts/autoresearch/stage51a_m30_m31_bql_sweetspot_and_aql_bench_20261025.json"
SOURCE_49B = "artifacts/autoresearch/stage49b_ltu_pb_boost_and_frame_len_ota_bench_20261025.json"
REPORT_51A = "docs/STAGE51A_M30_M31_BQL_SWEETSPOT_AND_AQL_BENCHMARK.md"
REPORT_49B = "docs/STAGE49B_LTU_PB_BOOST_AND_FRAME_LEN_OTA_BENCHMARK.md"
SOURCE_51_PIN = "d829e73995ab55dfe71d41aab6a00a873c0aff83f05df29c7507cb1542869386"
SOURCE_49_PIN = "7346f3fb6a26ea5906465a874b8a462df5a3d68d39fc9070cd73461f69fb79a5"
REPORT_51_PIN = "85988021fc99c8b2c3bfbc41fcb905332c303d08a20f0554621df11dc69ac2e8"
REPORT_49_PIN = "c6c9f7e19f0749839586c6034ea3923fa4cd7d23ed88c9a0410a2aa4eec11126"
ROUND_PINS = (
    "6c7b4f237fae0c031a47816e42c0f0b6dbc08e12c8fbf49d465cea9e6e658ee1",
    "bf6ce44b1342c8023eba14658171a78b41b373f2a0cfbae336efdc31003100fd",
    "fc7265ab10aeb6fdbbd2e9ee07056e6ed5260d18b98c5a5b023bb2966126f79f",
    "0761e91a45f79290813f6fc844af02c87e7e94bca830130d740f4510c95c4727",
    "58d0518b8140637dacaff8e7986c777e911308e6450ce6207ef7dda0d2636065",
    "879a617a25144a2641b77a892f3d927c6430725ad65078a71841ecc2f0dd1007",
)
TRIAL_PINS = (
    "ab51dd67becc2a326b5c716e91d348a4ea4a166a0fa0692ab48adf1f29a24f10",
    "ff4eef49020bc0ae7e4a5256bf64ed102584de08f1c58a98667020b7332e14e6",
    "3db85b6d85963cbf2b7935f39158e6629415eea3504076ee6d8a4af640d0e05e",
    "5a897e5f55f9e717a6ae93ea85b0f95225fddc6a386e9a0d2a8c5944b8c91584",
    "7645f0907c5d030aef53799ba005b43615a4932c23f0305d1b0dc3f4ee409150",
    "a8bad8d0ae44f3cfb6bed3ad64cc141669c1927867e899054025aadaa6672b26",
    "0df40d145dd6310e8c5011536de33c5852b3487a462344676491ae5dead24422",
    "5cd03c42cc1f163feb6e780c1d66818610f132e4082a26954ca3ff2c8588378d",
    "7613fee6ade3fdfe7bc4b03669ca0e874a76899d898e162606c126099e1f6a32",
)
PHASES = ("A1", "B1", "A2", "B2")
LTU_PROFILES = ("S49B-R0-STAGE48B-BASELINE", "S49B-R1-PB-BOOST-ON-2MS", "S49B-R2-PB-BOOST-AND-EVM-MCS-CEILING")


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture(scope="module")
def saved_sources():
    return (
        json.loads((ROOT / SOURCE_51A).read_text(encoding="utf-8-sig")),
        json.loads((ROOT / SOURCE_49B).read_text(encoding="utf-8-sig")),
        (ROOT / REPORT_51A).read_bytes().decode("utf-8"),
        (ROOT / REPORT_49B).read_bytes().decode("utf-8"),
    )


@pytest.fixture
def stage51(saved_sources):
    return deepcopy(saved_sources[0])


@pytest.fixture
def stage49(saved_sources):
    return deepcopy(saved_sources[1])


@pytest.fixture
def profile(stage51):
    return stage51["rounds"][5]["phases"]["B1"]["getter_readback"]


@pytest.fixture
def source_root(tmp_path):
    for relative in (SOURCE_51A, SOURCE_49B, REPORT_51A, REPORT_49B):
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    return tmp_path


def test_exact_sweetspot_json_and_all_rounds_trials_reports_have_independent_bindings(saved_sources):
    stage51, stage49, report51, report49 = saved_sources
    assert _digest(stage51) == SOURCE_51_PIN
    assert _digest(stage49) == SOURCE_49_PIN
    assert tuple(_digest(row) for row in stage51["rounds"]) == ROUND_PINS
    assert tuple(_digest(row) for row in stage49["trials"]) == TRIAL_PINS
    assert hashlib.sha256(report51.encode()).hexdigest() == REPORT_51_PIN
    assert hashlib.sha256(report49.encode()).hexdigest() == REPORT_49_PIN
    assert isinstance(verifier.source_contract(*saved_sources), dict)


@pytest.mark.parametrize("index", range(6))
def test_each_stage51_round_is_pinned_including_rejected_rounds(stage51, saved_sources, index):
    stage51["rounds"][index]["decision"] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(stage51, *saved_sources[1:])


@pytest.mark.parametrize("index", range(9))
def test_each_stage49_trial_is_content_pinned(stage49, saved_sources, index):
    stage49["trials"][index]["bulk_tcp_mbps"] += 1
    with pytest.raises(ValueError):
        verifier.source_contract(saved_sources[0], stage49, *saved_sources[2:])


@pytest.mark.parametrize("source_index,key", ((0, "starting_champion_baseline"), (0, "safety_policy"),
                                             (1, "hardware_and_driver_discoveries"), (1, "summary_by_profile")))
def test_both_source_envelopes_are_bound_outside_rounds_and_trials(saved_sources, source_index, key):
    arguments = deepcopy(list(saved_sources))
    arguments[source_index][key] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(*arguments)


@pytest.mark.parametrize("report_index", (2, 3))
@pytest.mark.parametrize("change", ("append", "newlines"))
def test_each_report_binding_preserves_raw_bytes(saved_sources, report_index, change):
    arguments = list(saved_sources)
    report = arguments[report_index]
    arguments[report_index] = report + "\n" if change == "append" else (
        report.replace("\r\n", "\n") if "\r\n" in report else report.replace("\n", "\r\n"))
    assert arguments[report_index] != report
    with pytest.raises(ValueError):
        verifier.source_contract(*arguments)


@pytest.mark.parametrize("index", range(6))
@pytest.mark.parametrize("phase", PHASES)
def test_stage51_requires_every_one_of_twenty_four_windows(stage51, index, phase):
    del stage51["rounds"][index]["phases"][phase]
    with pytest.raises(ValueError):
        verifier.audit_stage51a(stage51)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown"))
def test_stage51_requires_six_unique_expected_rounds(stage51, change):
    if change == "missing":
        stage51["rounds"].pop()
    elif change == "extra":
        stage51["rounds"].append(deepcopy(stage51["rounds"][0]))
    else:
        stage51["rounds"][-1]["round_id"] = "S51A-R1" if change == "duplicate" else "S51A-R7"
    with pytest.raises(ValueError):
        verifier.audit_stage51a(stage51)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown_profile", "bad_rep"))
def test_stage49_requires_all_nine_unique_profile_rep_pairs(stage49, change):
    if change == "missing":
        stage49["trials"].pop()
    elif change == "extra":
        stage49["trials"].append(deepcopy(stage49["trials"][0]))
    elif change == "duplicate":
        stage49["trials"][-1] = deepcopy(stage49["trials"][0])
    elif change == "unknown_profile":
        stage49["trials"][0]["profile_id"] = "UNKNOWN"
    else:
        stage49["trials"][0]["rep"] = True
    with pytest.raises(ValueError):
        verifier.audit_stage49b(stage49)


@pytest.mark.parametrize("field", ("aggregate_goodput_mbps", "sector_p95_rtt_ms", "sector_p99_rtt_ms"))
@pytest.mark.parametrize("bad", (True, "1", float("nan"), -1))
def test_stage51_core_window_metrics_are_finite_numbers_without_boolean_coercion(stage51, field, bad):
    stage51["rounds"][0]["phases"]["A1"][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage51a(stage51)


@pytest.mark.parametrize("field", ("bulk_tcp_mbps", "bulk_tcp_retransmits", "iptv_udp_mbps", "iptv_jitter_ms",
                                   "iptv_loss_pct", "voip_udp_mbps", "voip_jitter_ms", "voip_loss_pct",
                                   "loaded_ping_p50_ms", "loaded_ping_p95_ms", "loaded_ping_p99_ms", "loaded_ping_samples"))
def test_stage49_trial_scalars_reject_boolean_coercion(stage49, field):
    stage49["trials"][0][field] = True
    with pytest.raises(ValueError):
        verifier.audit_stage49b(stage49)


def test_stage51_preserves_all_windows_failed_health_and_source_without_native_promotion(stage51):
    before = _digest(stage51)
    result = verifier.audit_stage51a(stage51)
    assert _digest(stage51) == before
    assert result["windows"] == 24 and result["udp_observations"] == 48
    assert len(result["rounds"]) == 6
    assert all(set(row["windows"]) == set(PHASES) for row in result["rounds"])
    assert all(value["consistent"] for row in result["rounds"] for window in row["windows"].values()
               for value in window["udp"].values())
    expected_failed = {(f"S51A-R{index}", phase) for index in (2, 3, 4, 5) for phase in PHASES}
    assert {(item["round"], item["phase"]) for item in result["failed_ping_windows"]} == expected_failed
    assert all(item["per_cpe_loss_pct"]["LiteBeamM5_XW"] == 100 for item in result["failed_ping_windows"])
    assert any(item["code"] == "SUMMARY_HEALTH_DOES_NOT_QUALIFY_FAILED_WINDOWS" for item in result["findings"])
    assert sum(item["code"] == "AP_QUEUE_INVENTORY_DIFFERS_FROM_FULL_BASELINE" for item in result["findings"]) == 6
    assert result["champion"]["reported_version"] == 17
    assert result["champion"]["native_promotion_accepted"] is False
    assert result["native_acceptance"] is False


def test_stage51_r6_statistics_keep_integer_loss_counts_and_adaptive_bql(stage51):
    result = verifier.audit_stage51a(stage51)
    r6 = result["rounds"][5]
    metrics = r6["metrics"]
    assert metrics["goodput"]["control"] == 39.723
    assert metrics["goodput"]["target"] == 42.349
    assert metrics["goodput"]["delta_pct"] == pytest.approx(6.611, abs=0.001)
    assert metrics["p95"]["control"] == 98.760
    assert metrics["p95"]["target"] == 92.734
    assert metrics["p95"]["delta_pct"] == pytest.approx(-6.102, abs=0.001)
    assert metrics["pareto_score_delta_pct"] == pytest.approx(8.7464, abs=0.001)
    assert (metrics["iptv"]["A"]["lost"], metrics["iptv"]["A"]["total"]) == (7, 5687)
    assert (metrics["iptv"]["B"]["lost"], metrics["iptv"]["B"]["total"]) == (4, 5698)
    assert (metrics["voip"]["B"]["lost"], metrics["voip"]["B"]["total"]) == (0, 1196)
    assert "R2 Candidate" in r6["windows"]["B1"]["getter_arm_label"]
    assert result["bql_policy"]["v17_bounded_candidate"] == {"limit_min": 3028, "limit_max": 42392, "hold_time": 1000}
    assert result["bql_policy"]["fixed_operating_limit_or_universal_optimum"] is False
    assert result["tx_bias"]["qdisc_packet_quota"] == 128
    assert result["tx_bias"]["driver_napi_weight_scaled"] is False
    assert result["design"]["pooled_rtt_quantiles_reconstructable"] is False


@pytest.mark.parametrize("raw_rate", ("4.97 Mbits/sec", "4970 Kbits/sec", "0.00497 Gbits/sec", "4970000 bits/sec"))
def test_stage51_raw_receiver_bitrate_scales_units_without_changing_typed_measurement(stage51, raw_rate):
    observation = stage51["rounds"][5]["phases"]["B1"]["iptv_dual_stream_ac_vi"]
    observation["raw_receiver_line"] = observation["raw_receiver_line"].replace("4.97 Mbits/sec", raw_rate)
    result = verifier.audit_stage51a(stage51)["rounds"][5]["windows"]["B1"]["udp"]["iptv"]
    assert result["typed"]["bitrate_mbps"] == 4.97
    assert result["raw"]["bitrate_mbps"] == pytest.approx(4.97)
    assert result["checks"]["typed_bitrate_vs_raw"] is True


@pytest.mark.parametrize("field,value,check", (("packet_loss_pct", 0.5, "typed_pct_vs_counts"),
                                              ("delivered_bitrate_mbps", 4.5, "typed_bitrate_vs_raw")))
def test_injected_udp_disagreement_is_retained_as_a_finding_not_normalized(stage51, field, value, check):
    observation = stage51["rounds"][5]["phases"]["B1"]["voip_stream_ac_vo"]
    observation[field] = value
    result = verifier.audit_stage51a(stage51)
    assert observation[field] == value
    assert any(item.get("code") == "UDP_LAYER_DISAGREEMENT" and item.get("check") == check
               for item in result["findings"])
    assert result["rounds"][5]["windows"]["B1"]["udp"]["voip"]["raw"]["lost"] == 0
    assert result["champion"]["native_promotion_accepted"] is False


@pytest.mark.parametrize("change", ("boolean_bitrate", "overflow_raw_bitrate"))
def test_stage51_bitrate_layer_still_rejects_structurally_invalid_numbers(stage51, change):
    observation = stage51["rounds"][5]["phases"]["B1"]["iptv_dual_stream_ac_vi"]
    if change == "boolean_bitrate":
        observation["delivered_bitrate_mbps"] = True
    else:
        observation["raw_receiver_line"] = observation["raw_receiver_line"].replace("4.97 Mbits/sec", "9" * 400 + " Mbits/sec")
    with pytest.raises(ValueError):
        verifier.audit_stage51a(stage51)


def _profile_paths():
    paths = []
    sysctls = ("netdev_max_backlog", "dev_weight", "dev_weight_rx_bias", "dev_weight_tx_bias", "netdev_budget",
               "netdev_budget_usecs", "tcp_early_retrans", "tcp_limit_output_bytes", "tcp_notsent_lowat",
               "tcp_pacing_ca_ratio", "tcp_pacing_ss_ratio")
    inventories = {
        "ap": ("br-lan", "eth0", "lo", "phy0-ap0", "phy0-ap0.sta1", "phy0-ap0.sta2"),
        "cpe": ("br-lan", "br-wan", "eth0", "lo", "phy0-sta0"),
    }
    for prefix, names in inventories.items():
        paths.extend((prefix + "_netdev_tx_queue_len", name) for name in names)
        paths.extend((prefix + "_sysctl", field) for field in sysctls)
        paths.extend((prefix + "_eth0_bql", field) for field in ("limit_min", "limit_max", "hold_time"))
        paths.extend((prefix + "_aqm", field) for field in ("fq_flows_cnt", "fq_memory_limit", "fq_limit", "fq_quantum"))
        paths.extend((prefix + "_aql_txq_limit", ac, field) for ac in ("VO", "VI", "BE", "BK") for field in ("low_us", "high_us"))
    paths.extend(("r5ac_m26_state", field) for field in ("br0_txqueuelen", "ath0_txqueuelen", "eth0_txqueuelen", "netdev_budget", "dev_weight"))
    paths.extend(("lbm5_m29_state", field) for field in ("br0_txqueuelen", "ath0_txqueuelen", "eth0_txqueuelen", "netdev_budget", "ewma_delegate", "no_auto_prio"))
    return paths


def _parent_and_key(value, path):
    for key in path[:-1]:
        value = value[key]
    return value, path[-1]


def test_v17_profile_validates_supplied_policy_without_freezing_operating_limit(profile):
    result = verifier.verify_v17_profile(profile)
    assert result["supplied_profile_matches"] is True
    assert result["bql"]["ap"]["limit"] == 24576
    assert result["bql"]["cpe"]["limit"] == 3028
    assert result["bql_is_adaptive_with_configured_bounds"] is True
    assert result["native_authenticated"] is False
    assert result["universal_optimum_proven"] is False


@pytest.mark.parametrize("path", _profile_paths(), ids=lambda path: "/".join(path))
def test_each_static_v17_field_rejects_drift(profile, path):
    parent, key = _parent_and_key(profile, path)
    parent[key] += 1
    with pytest.raises(ValueError):
        verifier.verify_v17_profile(profile)


@pytest.mark.parametrize("limit", (3028, 10000, 42392))
def test_v17_accepts_dynamic_bql_current_inside_configured_bounds(profile, limit):
    profile["ap_eth0_bql"]["limit"] = profile["cpe_eth0_bql"]["limit"] = limit
    assert verifier.verify_v17_profile(profile)["supplied_profile_matches"] is True


@pytest.mark.parametrize("bad", (3027, 42393, True, -1))
def test_v17_rejects_current_outside_bounds_or_boolean(profile, bad):
    profile["ap_eth0_bql"]["limit"] = bad
    with pytest.raises(ValueError):
        verifier.verify_v17_profile(profile)


@pytest.mark.parametrize("field", ("cpe_aql_txq_limit", "ap_eth0_bql", "r5ac_m26_state", "lbm5_m29_state"))
def test_v17_cannot_qualify_missing_required_getter_groups(profile, field):
    del profile[field]
    with pytest.raises(ValueError):
        verifier.verify_v17_profile(profile)


@pytest.mark.parametrize("change", ("extra_interface", "missing_interface", "bool_sysctl", "bool_cpe_aql"))
def test_v17_queue_inventory_and_numeric_types_are_explicit(profile, change):
    if change == "extra_interface":
        profile["ap_netdev_tx_queue_len"]["phy0-ap0.sta23"] = 256
    elif change == "missing_interface":
        del profile["cpe_netdev_tx_queue_len"]["eth0"]
    elif change == "bool_sysctl":
        profile["ap_sysctl"]["dev_weight_rx_bias"] = True
    else:
        profile["cpe_aql_txq_limit"]["BE"]["low_us"] = True
    with pytest.raises(ValueError):
        verifier.verify_v17_profile(profile)


def test_stage49_preserves_all_nine_trials_and_mean_median_and_stream_definitions(stage49):
    before = _digest(stage49)
    result = verifier.audit_stage49b(stage49)
    assert _digest(stage49) == before
    assert len(result["trials"]) == 9
    expected_order = [{"profile_id": LTU_PROFILES[(offset + rep - 1) % 3], "rep": rep}
                      for rep in (1, 2, 3) for offset in (0, 1, 2)]
    assert result["design"]["listed_order"] == expected_order
    assert result["design"]["cyclic_latin_square_positions"] is True
    for profile in LTU_PROFILES:
        assert all(result["profiles"][profile]["summary_checks"].values())
        means = result["profiles"][profile]["means"]
        selected = [item for item in stage49["trials"] if item["profile_id"] == profile]
        expected = round(sum(item["bulk_tcp_mbps"] + item["iptv_udp_mbps"] for item in selected) / 3, 3)
        assert means["mean_aggregate_dl_mbps"] == expected
    r2 = result["profiles"][LTU_PROFILES[2]]["means"]
    assert r2["median_loaded_ping_p95_ms"] == 8.617
    assert r2["mean_loaded_ping_p95_ms"] == 36.175
    third = next(item for item in result["trials"] if item["profile_id"] == LTU_PROFILES[2] and item["rep"] == 3)
    assert third["values"]["loaded_ping_p95_ms"] == 94.324
    assert third["values"]["iptv_jitter_ms"] == 9.761
    assert result["changes_vs_baseline_pct"][LTU_PROFILES[2]]["mean_iptv_jitter_ms"] > 400
    assert result["design"]["raw_ping_receiver_counts_and_timestamp_epochs"] == "MISSING"
    assert result["native_acceptance"] is False
    assert result["standalone_route_isolation_and_coldboot_proven"] is False


def test_stage49_summary_disagreement_remains_a_finding(stage49):
    stage49["summary_by_profile"][LTU_PROFILES[2]]["median_loaded_ping_p95_ms"] = 1
    result = verifier.audit_stage49b(stage49)
    assert result["profiles"][LTU_PROFILES[2]]["means"]["median_loaded_ping_p95_ms"] == 8.617
    assert any(item["code"] == "PROFILE_SUMMARY_DISAGREES" for item in result["findings"])
    assert result["native_acceptance"] is False


@pytest.mark.parametrize("field,bad", (("iptv_loss_pct", 101), ("voip_udp_mbps", float("inf")),
                                      ("loaded_ping_p95_ms", float("nan")), ("bulk_tcp_retransmits", 1.5)))
def test_stage49_ranges_and_counters_remain_strict(stage49, field, bad):
    stage49["trials"][0][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage49b(stage49)


@pytest.mark.parametrize("field", ("ota_verified", "cpe_watchdog_disarmed_after_verify"))
def test_stage49_apply_flags_are_explicit_booleans(stage49, field):
    stage49["trials"][0]["apply_meta"][field] = 1
    with pytest.raises(ValueError):
        verifier.audit_stage49b(stage49)


@pytest.mark.parametrize("ceiling,label", ((7, "qpsk (2x)"), (11, "16qam (4x)"), (15, "64qam (6x)"),
                                           (19, "256qam (8x)"), (23, "1024qam (10x)"),
                                           (31, "4096qam (12x)"), (32, "automatic (2x)")))
@pytest.mark.parametrize("opcode", (0, 2))
def test_rate_ceiling_is_separate_from_per_cpe_auto_rate_sentinel(ceiling, label, opcode):
    result = verifier.verify_ltu_rate_contract(auto_mcs_ceiling=ceiling, cpe_id=0, mcs_level=32, opcode=opcode)
    assert result["reported_ceiling_label"] == label
    assert result["mcs_level"] == 32
    assert result["supplied_contract_consistent"] is True
    assert result["native_abi_and_siso_recovery_authenticated"] is False


@pytest.mark.parametrize("level", (15, 23))
@pytest.mark.parametrize("opcode", (0, 2))
def test_unsafe_ceiling_index_is_rejected_as_a_cpe_auto_rate_level(level, opcode):
    with pytest.raises(ValueError, match="AUTO_REQUIRES_32"):
        verifier.verify_ltu_rate_contract(auto_mcs_ceiling=level, cpe_id=0, mcs_level=level, opcode=opcode)


@pytest.mark.parametrize("field,bad", (("auto_mcs_ceiling", 8), ("auto_mcs_ceiling", True),
                                      ("cpe_id", 1), ("cpe_id", False), ("mcs_level", True),
                                      ("opcode", 1), ("opcode", True), ("opcode", "0")))
def test_rate_contract_is_fail_closed_for_unknown_or_coerced_fields(field, bad):
    arguments = {"auto_mcs_ceiling": 23, "cpe_id": 0, "mcs_level": 32, "opcode": 0}
    arguments[field] = bad
    with pytest.raises(ValueError):
        verifier.verify_ltu_rate_contract(**arguments)


def test_frame_len_discovery_preserves_actual_period_duty_and_other_changed_field(stage49):
    result = verifier.audit_frame_len_discovery(stage49["hardware_and_driver_discoveries"])
    assert result["after_frame_len_write"]["frame_period"] == 2000
    assert result["after_frame_len_write"]["duty_cycle"] == 5000
    assert result["after_duty_cycle_restore"]["frame_period"] == 2000
    assert result["after_duty_cycle_restore"]["duty_cycle"] == 750
    assert result["cz_len_changed"] is True
    assert result["full_map_probed_by_current_runner"] is False
    assert result["handler_root_cause_or_5ms_mode_proven"] is False
    assert result["running_module_hash"] == "MISSING"


@pytest.mark.parametrize("change", ("missing_field", "duplicate_field", "negative", "non_numeric", "missing_map", "boolean_flag"))
def test_frame_len_discovery_rejects_ambiguous_incomplete_or_wrongly_typed_structure(stage49, change):
    discovery = stage49["hardware_and_driver_discoveries"]
    key = "bandwidthConfig_after_echo_5000_frame_len"
    if change == "missing_field":
        discovery[key] = discovery[key].replace("frame_period:2000,", "")
    elif change == "duplicate_field":
        discovery[key] = discovery[key].replace("frame_period:2000,", "frame_period:2000,frame_period:5000,")
    elif change == "negative":
        discovery[key] = discovery[key].replace("frame_period:2000", "frame_period:-2000")
    elif change == "non_numeric":
        discovery[key] = discovery[key].replace("duty_cycle:5000", "duty_cycle:true")
    elif change == "missing_map":
        del discovery["verified_autoMcsCeiling_map"]["31"]
    else:
        discovery["ame_core_sysfs_frame_len_bug_confirmed"] = 1
    with pytest.raises(ValueError):
        verifier.audit_frame_len_discovery(discovery)


@pytest.fixture
def audit(source_root):
    return verifier.audit_saved_sources(source_root)


def test_root_audit_keeps_report_conflicts_and_physical_acceptance_qualified(audit):
    assert audit["audit_status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert audit["source_contract"]["native_acquisition_authenticated"] is False
    reports = audit["pinned_report_qualifications"]
    assert reports["claims"]["S51A_R4_iptv_jitter_ms_A_B"] == [1.392, 1.976]
    assert reports["S51A_R4_exact_json_iptv_jitter_ms_A_B"] == [1.392, 1.652]
    assert reports["claims"]["S51A_R4_voip_jitter_ms_A_B"] == [2.838, 2.753]
    assert reports["S51A_R4_exact_json_voip_jitter_ms_A_B"] == [2.497, 1.905]
    assert len(reports["S51A_R5_failed_M5_windows"]) == 4
    assert audit["boundary"] == {"offline_only": True, "ssh": False, "hardware_access": False,
                                  "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}


def test_managed_export_roundtrip_and_refresh_are_atomic_local_json(audit, tmp_path):
    output = tmp_path / "audit.json"
    assert verifier.write_audit(audit, output) == output
    assert json.loads(output.read_text(encoding="utf-8")) == audit
    updated = deepcopy(audit)
    updated["test_refresh"] = True
    verifier.write_audit(updated, output)
    assert json.loads(output.read_text(encoding="utf-8"))["test_refresh"] is True
    assert not list(tmp_path.glob(".stage45b-*.tmp"))


@pytest.mark.parametrize("relative", (SOURCE_51A, SOURCE_49B))
def test_export_refuses_source_overwrite_and_preserves_original_bytes(audit, source_root, relative):
    output = source_root / relative
    before = output.read_bytes()
    with pytest.raises(ValueError, match="SOURCE_OVERWRITE_REJECTED"):
        verifier.write_audit(audit, output, protected_paths=(source_root / p for p in (SOURCE_51A, SOURCE_49B)))
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
def test_export_requires_literal_nondevice_json_filename_without_creating_entries(audit, tmp_path, name):
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError):
        verifier.write_audit(audit, tmp_path / name)
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("path", ("//example.invalid/share/audit.json", "https://example.invalid/audit.json",
                                  "file:///tmp/audit.json", "C:audit.json", "\\\\?\\C:\\audit.json", "bad\0.json"))
def test_export_rejects_network_uri_device_and_nul_paths_before_access(audit, path):
    with pytest.raises(ValueError):
        verifier.write_audit(audit, path)


def test_optional_real_symlink_output_does_not_modify_target(audit, tmp_path):
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


def test_failed_nonfinite_serialization_preserves_existing_managed_export(audit, tmp_path):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()
    broken = deepcopy(audit)
    broken["not_finite"] = float("nan")
    with pytest.raises(ValueError, match="FINITE_JSON_AUDIT_REQUIRED"):
        verifier.write_audit(broken, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage45b-*.tmp"))


def test_failed_atomic_replace_preserves_managed_export_and_cleans_temporary(audit, tmp_path, monkeypatch):
    output = tmp_path / "audit.json"
    verifier.write_audit(audit, output)
    before = output.read_bytes()

    def fail_replace(_source, _target):
        raise OSError("Synthetic local replace failure")

    monkeypatch.setattr(verifier.os, "replace", fail_replace)
    with pytest.raises(OSError, match="Synthetic local replace failure"):
        verifier.write_audit(audit, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage45b-*.tmp"))


CLI = ROOT / "tools/verify_stage51a_v17_and_stage49b_ltu.py"


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
    assert completed.returncode == expected_exit, completed.stdout + completed.stderr
    status = json.loads(completed.stdout)
    assert status["status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert status["rounds"] == 6 and status["windows"] == 24 and status["ltu_trials"] == 9
    assert status["native_acceptance"] is False
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["task_id"] == verifier.TASK_ID
    assert exported["stage51a"]["native_acceptance"] is False
    assert exported["stage49b"]["native_acceptance"] is False


@pytest.mark.parametrize("relative", (SOURCE_51A, SOURCE_49B))
def test_cli_source_overwrite_error_preserves_inputs(source_root, relative):
    source = source_root / relative
    before = source.read_bytes()
    completed = _run_cli(source_root, "--output", source)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert source.read_bytes() == before


def test_cli_drifted_source_exits_two_without_creating_export(source_root):
    source = source_root / SOURCE_49B
    document = json.loads(source.read_text(encoding="utf-8-sig"))
    document["stage"] = "ALTERED"
    source.write_text(json.dumps(document), encoding="utf-8")
    output = source_root / "cli-audit.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["native_dispatch_allowed"] is False
    assert not output.exists()


@pytest.mark.parametrize("relative", ("docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"))
def test_current_docs_stay_compact_with_single_doc_head_opening_at_first_line(relative):
    lines = (ROOT / relative).read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) < 250
    assert lines[0].startswith("<!-- doc-head:")
    assert sum("<!-- doc-head:" in line for line in lines) == 1
    assert sum("<!-- /doc-head -->" in line for line in lines) == 1


def test_module_and_cli_ast_have_only_pure_local_dependencies_and_no_native_dispatch():
    allowed = {"__future__", "argparse", "hashlib", "json", "math", "os", "pathlib", "re", "statistics", "sys", "tempfile",
               "controller.stage42a_netdev_txq_and_airos6_verifier",
               "controller.stage44a_champion_v15_and_ltu_beacon_verifier",
               "controller.stage46a_champion_v16_tx_bias_and_bql_verifier",
               "controller.stage51a_v17_and_stage49b_ltu_verifier"}
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



