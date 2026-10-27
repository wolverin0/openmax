"""Offline Stage43B evidence checks; saved contradictions remain findings."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from controller import stage46a_champion_v16_tx_bias_and_bql_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "artifacts/autoresearch/stage46a_m28_m29_bql_and_tx_bias_bench_20261025.json"
REPORT = "docs/STAGE46A_M28_M29_AG71XX_BQL_AND_NAPI_TX_BIAS_BENCHMARK.md"
PREVIOUS = "artifacts/autoresearch/stage44a_m26_m27_napi_and_r5ac_txq_bench_20261025.json"
SOURCE_PIN = "33bf3b1b7be59abb2adf680d579c0cc51bec917eec83155143f0dc2d03c2e76d"
REPORT_PIN = "be3a52f8c5499c0bdc71a2d1cdea9cf2decc53e6f05b4a73a29e98bb05a2267c"
PREVIOUS_PIN = "67c803852ee7a10b111a13b5536115eb8263249b944310afb22506b7dc475ee6"
ROUND_PINS = {
    "S46A-R1": "fc56a525d7fd75d370e93852387a10627fed76a3ea9366cfdc2c6ff0f171f041",
    "S46A-R2": "b83be6dd1d69b0823d101c49d2d85557606cec9af622db1e59cb9bf80b92e2d1",
    "S46A-R3": "7624254769640759e29f928431526b2c78c4ab99db49c8e1f29a30ababe2a178",
    "S46A-R4": "3ff7b66e9e4777d0817c71fd644c246c153b447960ab9cc419f7cf2a1e90a64b",
    "S46A-R5": "f3aae92124fd36678eac9a39712de63a0384acf597c49bc0b41e7548bdc3a113",
    "S46A-R6": "574fd7fe754601c2248bacfcf8042471fa4cdf3236cc0b5dafba10ab8073e02e",
}
PHASES = ("A1", "B1", "A2", "B2")
AP_INTERFACES = ("br-lan", "eth0", "lo", "phy0-ap0", "phy0-ap0.sta1", "phy0-ap0.sta2")
CPE_INTERFACES = ("br-lan", "br-wan", "eth0", "lo", "phy0-sta0")


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture(scope="module")
def saved_sources():
    return (
        json.loads((ROOT / SOURCE).read_text(encoding="utf-8-sig")),
        (ROOT / REPORT).read_bytes().decode("utf-8"),
        json.loads((ROOT / PREVIOUS).read_text(encoding="utf-8-sig")),
    )


@pytest.fixture
def document(saved_sources):
    return deepcopy(saved_sources[0])


@pytest.fixture
def previous(saved_sources):
    return deepcopy(saved_sources[2])


@pytest.fixture
def profile(document):
    return document["rounds"][2]["phases"]["B1"]["getter_readback"]


def _profile_check(profile, ap=AP_INTERFACES, cpe=CPE_INTERFACES):
    return verifier.verify_champion_profile(profile, ap_interfaces=ap, cpe_interfaces=cpe)


def test_saved_sources_and_all_six_rounds_have_independent_exact_bindings(saved_sources):
    document, report, previous = saved_sources
    assert _digest(document) == SOURCE_PIN
    assert hashlib.sha256(report.encode()).hexdigest() == REPORT_PIN
    assert _digest(previous) == PREVIOUS_PIN
    assert {row["round_id"]: _digest(row) for row in document["rounds"]} == ROUND_PINS
    assert isinstance(verifier.source_contract(document, report, previous), dict)


@pytest.mark.parametrize("index", range(6))
def test_every_round_is_pinned_including_rejected_or_inconsistent_rounds(document, saved_sources, index):
    document["rounds"][index]["decision"] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1], saved_sources[2])


@pytest.mark.parametrize("key", ("safety_policy", "starting_champion_baseline", "generated_at", "extra_field"))
def test_source_envelope_is_pinned_outside_rounds(document, saved_sources, key):
    document[key] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(document, saved_sources[1], saved_sources[2])


@pytest.mark.parametrize("change", ("append", "newlines", "claim"))
def test_report_is_pinned_as_original_bytes(saved_sources, change):
    document, report, previous = saved_sources
    altered = {
        "append": report + "\n",
        "newlines": report.replace("\r\n", "\n") if "\r\n" in report else report.replace("\n", "\r\n"),
        "claim": report.replace("-70.136", "-60.136"),
    }[change]
    assert altered != report
    with pytest.raises(ValueError):
        verifier.source_contract(document, altered, previous)


def test_previous_stage44_context_is_content_bound(previous, saved_sources):
    previous["rounds"][2]["decision"] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(saved_sources[0], saved_sources[1], previous)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown"))
def test_audit_requires_all_six_unique_expected_rounds(document, change):
    if change == "missing":
        document["rounds"].pop()
    elif change == "extra":
        document["rounds"].append(deepcopy(document["rounds"][0]))
    else:
        document["rounds"][-1]["round_id"] = "S46A-R1" if change == "duplicate" else "S46A-R7"
    with pytest.raises(ValueError):
        verifier.audit_stage46a(document)


@pytest.mark.parametrize("index", range(6))
@pytest.mark.parametrize("phase", PHASES)
def test_all_twenty_four_windows_are_mandatory(document, index, phase):
    del document["rounds"][index]["phases"][phase]
    with pytest.raises(ValueError):
        verifier.audit_stage46a(document)


def test_audit_keeps_all_windows_and_source_conflicts_without_promoting_or_mutating(document):
    original_digest = _digest(document)
    result = verifier.audit_stage46a(document)
    assert _digest(document) == original_digest
    assert result["windows"] == 24
    assert result["udp_observations"] == 48
    assert [row["round_id"] for row in result["rounds"]] == list(ROUND_PINS)
    assert all(set(row["windows"]) == set(PHASES) for row in result["rounds"])
    assert sum(len(window["udp"]) for row in result["rounds"] for window in row["windows"].values()) == 48
    assert result["research_evidence_status"] == "INCONSISTENT_SAVED_EVIDENCE"
    assert result["champion"]["reported_version"] == 16
    assert result["champion"]["reported_promoted_round"] == "S46A-R3"
    assert result["champion"]["native_promotion_accepted"] is False
    assert result["champion"]["raw_qoe_qualified"] is False
    findings = result["discrepancies"]
    assert any(item.get("round") == "S46A-R3" and item.get("phase") == "B1" and
               item.get("stream") == "voip" and item.get("check") == "typed_pct_vs_counts"
               for item in findings)
    assert any(item.get("round") == "S46A-R3" and item.get("phase") == "B2" and
               item.get("stream") == "iptv" and item.get("check") == "typed_pct_vs_counts"
               for item in findings)
    bql_findings = [item for item in findings if item["code"] == "BQL_CURRENT_OUTSIDE_CONFIGURED_BOUNDS"]
    assert {(item["round"], item["phase"], item["endpoint"]) for item in bql_findings} == {
        ("S46A-R5", "B1", "cpe"), ("S46A-R5", "B2", "cpe"),
    }


def test_known_typed_and_raw_udp_conflicts_remain_separate_observations(document):
    result = verifier.audit_stage46a(document)
    r1, r3 = result["rounds"][0], result["rounds"][2]
    assert r1["metrics"]["iptv"]["typed_jitter_delta_pct"] == -70.136
    assert r1["metrics"]["iptv"]["raw_jitter_delta_pct"] > 0
    voice = r3["windows"]["B1"]["udp"]["voip"]
    assert voice["typed"]["pct"] == 0.5
    assert (voice["typed"]["lost"], voice["typed"]["total"]) == (0, 600)
    assert (voice["raw"]["lost"], voice["raw"]["total"]) == (0, 600)
    assert voice["count_loss_pct"] == 0
    assert voice["checks"]["typed_pct_vs_counts"] is False
    iptv = r3["windows"]["B2"]["udp"]["iptv"]
    assert iptv["typed"]["pct"] == 0.2105
    assert (iptv["raw"]["lost"], iptv["raw"]["total"]) == (14, 2847)
    assert iptv["count_loss_pct"] == pytest.approx(100 * 14 / 2847)
    assert iptv["checks"]["typed_pct_vs_counts"] is False
    assert iptv["checks"]["raw_pct_vs_raw_counts"] is True
    # Pooled loss from integer counts is distinct from the mean of saved percentages.
    assert (r3["metrics"]["iptv"]["A"]["lost"], r3["metrics"]["iptv"]["A"]["total"]) == (48, 5691)
    assert (r3["metrics"]["iptv"]["B"]["lost"], r3["metrics"]["iptv"]["B"]["total"]) == (14, 5694)
    assert (r3["metrics"]["voip"]["A"]["lost"], r3["metrics"]["voip"]["A"]["total"]) == (1, 1200)
    assert (r3["metrics"]["voip"]["B"]["lost"], r3["metrics"]["voip"]["B"]["total"]) == (0, 1200)
    assert r3["metrics"]["voip"]["B"]["pooled_count_loss_pct"] == 0
    assert r3["metrics"]["voip"]["B"]["mean_typed_pct"] > 0


@pytest.mark.parametrize("field", ("aggregate_goodput_mbps", "sector_p95_rtt_ms", "sector_p99_rtt_ms"))
@pytest.mark.parametrize("bad", (True, "1", float("nan"), -1, 0))
def test_primary_window_metrics_reject_malformed_numbers(document, field, bad):
    document["rounds"][0]["phases"]["A1"][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage46a(document)


@pytest.mark.parametrize("bad", (0, 1, "false", None))
def test_reported_promotion_requires_boolean(document, bad):
    document["rounds"][0]["promoted"] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage46a(document)


@pytest.mark.parametrize("field,bad", (
    ("lost_datagrams", True), ("total_datagrams", False), ("total_datagrams", 0),
    ("packet_loss_pct", True), ("jitter_ms", False), ("jitter_ms", float("inf")),
    ("raw_receiver_line", None), ("raw_receiver_line", "missing receiver counts"),
))
def test_udp_discrepancies_do_not_relax_required_structure_and_numeric_types(document, field, bad):
    document["rounds"][0]["phases"]["A1"]["iptv_dual_stream_ac_vi"][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage46a(document)


@pytest.mark.parametrize("change", ("raw_jitter_overflow", "raw_counter_overflow"))
def test_raw_udp_parser_rejects_nonfinite_jitter_and_counts_above_uint64(document, change):
    observation = document["rounds"][0]["phases"]["A1"]["iptv_dual_stream_ac_vi"]
    if change == "raw_jitter_overflow":
        observation["raw_receiver_line"] = "[SUM] 0.00-6.04 sec 4.90 Mbits/sec " + "9" * 400 + " ms 0/2814 (0%) receiver"
    else:
        observation["raw_receiver_line"] = f"[SUM] 0.00-6.04 sec 4.90 Mbits/sec 1.696 ms 0/{2**64} (0%) receiver"
    with pytest.raises(ValueError):
        verifier.audit_udp_observation(observation)


@pytest.fixture
def bql():
    return {"limit_min": 0, "limit_max": 1879048192, "limit": 54250, "hold_time": 1000, "inflight": 0}


def test_transient_current_below_minimum_is_a_finding_not_discarded_data(document):
    snapshot = document["rounds"][4]["phases"]["B1"]["getter_readback"]["cpe_eth0_bql"]
    result = verifier.audit_bql_snapshot(snapshot)
    assert result["limit"] == 3028
    assert result["limit_min"] == 4542
    assert result["current_within_configured_bounds"] is False
    assert result["converged_same_epoch_readback_qualified"] is False
    assert result["native_authenticated"] is False


@pytest.mark.parametrize("limit", (0, 1780, 24576, 54250, 65536, 1879048192))
def test_default_dynamic_bql_accepts_adaptation_instead_of_fixed_current_targets(bql, limit):
    bql["limit"] = limit
    result = verifier.verify_default_dynamic_bql(bql)
    assert result["dynamic_default_configuration"] is True
    assert result["current_within_configured_bounds"] is True
    assert result["limit"] == limit


@pytest.mark.parametrize("field,value", (("limit_min", 3028), ("limit_max", 65536), ("hold_time", 500)))
def test_champion_bql_rejects_static_clamps(bql, field, value):
    bql[field] = value
    with pytest.raises(ValueError, match="STATIC_BQL_CLAMP_REJECTED"):
        verifier.verify_default_dynamic_bql(bql)


def test_default_guard_rejects_current_outside_default_bounds(bql):
    bql["limit"] = bql["limit_max"] + 1
    assert verifier.audit_bql_snapshot(bql)["current_within_configured_bounds"] is False
    with pytest.raises(ValueError, match="CURRENT_BQL_LIMIT_OUTSIDE_CONFIGURED_BOUNDS"):
        verifier.verify_default_dynamic_bql(bql)


@pytest.mark.parametrize("field", ("limit_min", "limit_max", "limit", "hold_time", "inflight"))
@pytest.mark.parametrize("bad", (True, "0", 0.0, -1, 2**32))
def test_every_bql_field_requires_bounded_unsigned_integer(bql, field, bad):
    bql[field] = bad
    with pytest.raises(ValueError):
        verifier.audit_bql_snapshot(bql)


@pytest.mark.parametrize("field", ("limit_min", "limit_max", "limit", "hold_time", "inflight"))
def test_every_bql_field_must_be_present(bql, field):
    del bql[field]
    with pytest.raises(ValueError):
        verifier.audit_bql_snapshot(bql)


@pytest.mark.parametrize("change", ("reversed", "zero_max"))
def test_bql_configuration_has_ordered_nonzero_upper_bound(bql, change):
    if change == "reversed":
        bql["limit_min"] = bql["limit_max"] + 1
    else:
        bql["limit_max"] = 0
    with pytest.raises(ValueError):
        verifier.audit_bql_snapshot(bql)


def _profile_integer_paths():
    paths = []
    sysctls = ("netdev_max_backlog", "dev_weight", "dev_weight_rx_bias", "dev_weight_tx_bias",
               "netdev_budget", "netdev_budget_usecs", "tcp_early_retrans", "tcp_limit_output_bytes",
               "tcp_notsent_lowat", "tcp_pacing_ca_ratio", "tcp_pacing_ss_ratio")
    for prefix, interfaces in (("ap", AP_INTERFACES), ("cpe", CPE_INTERFACES)):
        paths.extend((prefix + "_netdev_tx_queue_len", name) for name in interfaces)
        paths.extend((prefix + "_sysctl", name) for name in sysctls)
        paths.extend((prefix + "_aqm", name) for name in ("fq_flows_cnt", "fq_memory_limit", "fq_limit", "fq_quantum"))
    paths.extend(("ap_aql_txq_limit", ac, field) for ac in ("VO", "VI", "BE", "BK")
                 for field in ("low_us", "high_us"))
    paths.extend(("r5ac_m26_state", field) for field in ("br0_txqueuelen", "ath0_txqueuelen",
                 "eth0_txqueuelen", "netdev_budget", "dev_weight"))
    paths.extend(("lbm5_m29_state", field) for field in ("br0_txqueuelen", "ath0_txqueuelen",
                 "eth0_txqueuelen", "netdev_budget", "ewma_delegate", "no_auto_prio"))
    return paths


PROFILE_INTEGER_PATHS = _profile_integer_paths()


def _parent_and_key(value, path):
    for key in path[:-1]:
        value = value[key]
    return value, path[-1]


def test_v16_profile_checks_saved_fields_without_inventing_missing_napi_readbacks(profile):
    before = _digest(profile)
    assert "ap_napi_defer_hard_irqs" not in profile
    assert "cpe_gro_flush_timeout_ns" not in profile
    result = _profile_check(profile)
    assert _digest(profile) == before
    assert result["supplied_profile_matches"] is True
    assert result["queues"]["ap"]["eth0"] == result["queues"]["cpe"]["eth0"] == 1000
    assert result["napi_defer_gro_readback"] == "UNKNOWN"
    assert result["cpu_identity"] == "UNKNOWN"
    assert result["cpe_aql_and_threshold"] == "UNKNOWN"
    assert result["native_authenticated"] is False
    assert result["complete_champion_qualified"] is False
    assert result["m5_exception_fallback_excluded"] is False


@pytest.mark.parametrize("path", PROFILE_INTEGER_PATHS, ids=lambda path: "/".join(path))
def test_every_v16_static_profile_field_rejects_drift(profile, path):
    parent, key = _parent_and_key(profile, path)
    parent[key] += 1
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("path", (
    ("ap_sysctl", "dev_weight_tx_bias"), ("cpe_sysctl", "dev_weight_tx_bias"),
    ("ap_netdev_tx_queue_len", "eth0"), ("cpe_netdev_tx_queue_len", "phy0-sta0"),
    ("ap_aqm", "fq_quantum"), ("ap_aql_txq_limit", "VI", "low_us"),
    ("r5ac_m26_state", "netdev_budget"), ("lbm5_m29_state", "netdev_budget"),
    ("lbm5_m29_state", "ewma_delegate"), ("lbm5_m29_state", "no_auto_prio"),
))
def test_profile_never_treats_booleans_as_integers(profile, path):
    parent, key = _parent_and_key(profile, path)
    parent[key] = True
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("field", ("ap_sysctl", "cpe_eth0_bql", "ap_aqm", "ap_aql_txq_limit", "r5ac_m26_state", "lbm5_m29_state"))
def test_profile_mandatory_evidence_cannot_be_omitted(profile, field):
    del profile[field]
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("field,value", (
    ("ff_mcast_airtime_limit", "5 0"), ("txop_params", "0 1"), ("no_ack_rate", "0 0"),
))
def test_profile_vendor_vectors_are_exact(profile, field, value):
    group = "r5ac_m26_state" if field == "ff_mcast_airtime_limit" else "lbm5_m29_state"
    profile[group][field] = value
    with pytest.raises(ValueError):
        _profile_check(profile)


def test_profile_accepts_current_dynamic_bql_variation_without_rewriting_defaults(profile):
    profile["ap_eth0_bql"]["limit"] = 54250
    profile["cpe_eth0_bql"]["limit"] = 1780
    assert _profile_check(profile)["supplied_profile_matches"] is True


def test_dynamic_ap_vlan_requires_complete_explicit_inventory(profile):
    profile["ap_netdev_tx_queue_len"]["phy0-ap0.sta23"] = 256
    with pytest.raises(ValueError, match="COMPLETE_INTERFACE_INVENTORY_REQUIRED"):
        _profile_check(profile)
    result = _profile_check(profile, ap=(*AP_INTERFACES, "phy0-ap0.sta23"))
    assert result["queues"]["ap"]["phy0-ap0.sta23"] == 256


@pytest.mark.parametrize("name", ("phy0-ap0.sta0", "phy0-ap0.sta01", "phy0-ap0.sta*", "eth1"))
def test_dynamic_ap_inventory_rejects_wildcard_and_unexpected_interfaces(profile, name):
    profile["ap_netdev_tx_queue_len"][name] = 256
    with pytest.raises(ValueError):
        _profile_check(profile, ap=(*AP_INTERFACES, name))


@pytest.mark.parametrize("inventory", (None, (), ("eth0", "eth0")))
def test_profile_inventory_is_explicit_nonempty_and_unique(profile, inventory):
    with pytest.raises(ValueError):
        _profile_check(profile, ap=inventory)


@pytest.fixture
def cpu_inventory():
    return [
        {"id": "LAP-120", "cpu_class": "MIPS74Kc_560MHz", "netdev_budget": 600},
        {"id": "Loco5AC", "cpu_class": "MIPS74Kc_560MHz", "netdev_budget": 600},
        {"id": "R5AC-Prism", "cpu_class": "Scorpion", "netdev_budget": 600},
        {"id": "LiteBeamM5", "cpu_class": "AR934x_400MHz", "netdev_budget": 300},
    ]


def test_cpu_budget_inventory_is_supplied_policy_not_a_universal_frequency_law(cpu_inventory):
    result = verifier.verify_cpu_budget_ceiling(cpu_inventory)
    assert result["supplied_policy_consistent"] is True
    assert result["endpoints"]["LiteBeamM5"]["policy_ceiling"] == 300
    assert result["endpoints"]["R5AC-Prism"]["policy_ceiling"] == 600
    assert result["native_cpu_identity_authenticated"] is False
    assert result["universal_cpu_frequency_limit_proven"] is False
    for endpoint in cpu_inventory:
        endpoint["netdev_budget"] = 1
    assert verifier.verify_cpu_budget_ceiling(cpu_inventory)["supplied_policy_consistent"] is True


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("change", ("over_ceiling", "zero", "boolean", "unknown_class", "missing_class"))
def test_every_cpu_policy_endpoint_requires_known_class_and_bounded_integer_budget(cpu_inventory, index, change):
    endpoint = cpu_inventory[index]
    if change == "over_ceiling":
        endpoint["netdev_budget"] += 1
    elif change == "zero":
        endpoint["netdev_budget"] = 0
    elif change == "boolean":
        endpoint["netdev_budget"] = True
    elif change == "unknown_class":
        endpoint["cpu_class"] = "unknown"
    else:
        del endpoint["cpu_class"]
    with pytest.raises(ValueError):
        verifier.verify_cpu_budget_ceiling(cpu_inventory)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown_id"))
def test_cpu_inventory_requires_all_four_unique_known_endpoints(cpu_inventory, change):
    if change == "missing":
        cpu_inventory.pop()
    elif change == "extra":
        cpu_inventory.append(dict(cpu_inventory[0]))
    else:
        cpu_inventory[-1]["id"] = "LAP-120" if change == "duplicate" else "UnknownRadio"
    with pytest.raises(ValueError):
        verifier.verify_cpu_budget_ceiling(cpu_inventory)


@pytest.mark.parametrize("weight,bias,napi", ((64, 1, 64), (64, 2, 64), (128, 2, 16)))
def test_tx_bias_changes_qdisc_packet_quota_without_scaling_driver_napi(weight, bias, napi):
    result = verifier.tx_bias_effect(dev_weight=weight, tx_bias=bias, driver_napi_weight=napi)
    assert result["qdisc_packet_quota"] == weight * bias
    assert result["driver_napi_weight"] == napi
    assert result["driver_napi_weight_scaled"] is False
    assert result["direct_htt_completion_multiplier_proven"] is False


@pytest.mark.parametrize("field,bad", (
    ("dev_weight", True), ("tx_bias", True), ("driver_napi_weight", True),
    ("dev_weight", 0), ("tx_bias", 0), ("driver_napi_weight", 0),
    ("dev_weight", 4097), ("tx_bias", 65), ("driver_napi_weight", 4097),
    ("dev_weight", "64"), ("tx_bias", 2.0),
))
def test_tx_quota_inputs_require_bounded_positive_unsigned_integers(field, bad):
    inputs = {"dev_weight": 64, "tx_bias": 2, "driver_napi_weight": 64}
    inputs[field] = bad
    with pytest.raises(ValueError):
        verifier.tx_bias_effect(**inputs)


def test_stage44_contrast_preserves_budget_time_and_queue_confounders(document, previous):
    result = verifier.compare_stage44a(document, previous)
    r3 = result["prior_rounds"]["S44A-R3"]
    assert r3["ap_treatment_sysctl"]["netdev_budget"] == 300
    # The Stage46 report says 8000; both pinned Stage44 B getters say 20000.
    assert r3["ap_treatment_sysctl"]["netdev_budget_usecs"] == 20000
    assert result["prior_rounds"]["S44A-R4"]["ap_treatment_eth0_txq"] == 256
    for ident, declared in (("S44A-R3", 8000), ("S44A-R4", 12000)):
        contrast = result["prior_rounds"][ident]
        assert contrast["declared_time_slice_us"] == declared
        assert contrast["declared_time_slice_matches_getter"] is False
        assert contrast["ap_treatment_sysctl"]["netdev_budget_usecs"] == 20000
        assert contrast["ap_treatment_sysctl_B2"]["netdev_budget_usecs"] == 20000
    assert result["changed_budget_time_slice_or_eth0_are_confounders"] is True
    assert result["isolated_cross_round_causal_explanation_proven"] is False
    assert result["tx_bias_doubles_driver_htt_napi_weight"] == "REFUTED_FOR_PRIMARY_LINUX_6_6_110"
    assert result["native_qdisc_or_aql_causal_benefit"] == "UNKNOWN"


def test_saved_root_audit_remains_offline_and_physically_unaccepted():
    result = verifier.audit_saved_sources(ROOT)
    assert result["source_contract"]["native_acquisition_authenticated"] is False
    assert result["stage46a"]["windows"] == 24
    assert result["stage46a"]["research_evidence_status"] == "INCONSISTENT_SAVED_EVIDENCE"
    assert result["boundaries"] == {
        "offline_only": True, "native_dispatch_allowed": False, "ssh": False,
        "hardware_access": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED",
    }


def test_verifier_ast_has_no_runner_native_or_network_dispatch():
    tree = ast.parse(Path(verifier.__file__).read_text(encoding="utf-8"))
    allowed = {"__future__", "hashlib", "math", "pathlib", "re",
               "controller.stage42a_netdev_txq_and_airos6_verifier",
               "controller.stage44a_champion_v15_and_ltu_beacon_verifier"}
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

