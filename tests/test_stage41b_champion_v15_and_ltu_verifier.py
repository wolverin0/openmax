"""Offline regressions for Stage41B; fixtures never dispatch a native operation."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from statistics import mean

import pytest

from controller import stage44a_champion_v15_and_ltu_beacon_verifier as verifier


ROOT = Path(__file__).resolve().parents[1]
PHASES = ("A1", "B1", "A2", "B2")
ROUND_PINS = {
    "S44A-R1": "df9d67092974d4ce5d2aeb6d1e7032c529c14820915a31a87665622ab672ade9",
    "S44A-R2": "6035781a56da19b1b46f5913e0a32d97ceecbdde51ce3869b33acfe47a345907",
    "S44A-R3": "2f1bdde2f7a124c19de2a645cd93696bf8b913bb33d86e1756c1ef1b0a1818f3",
    "S44A-R4": "41934234df98e04383c4eae221846c9540124bc0138020fff8c7a9a4e88ccbf8",
    "S44A-R5": "cd827aafa15f227a5fe30ae7dac5c468920408055bbf5df75efffbedb86a9606",
}
AP_INTERFACES = ("br-lan", "eth0", "lo", "phy0-ap0", "phy0-ap0.sta1", "phy0-ap0.sta2")
CPE_INTERFACES = ("br-lan", "br-wan", "eth0", "lo", "phy0-sta0")
SYSCTLS = {
    "netdev_max_backlog": 1000, "dev_weight": 64, "dev_weight_rx_bias": 1,
    "dev_weight_tx_bias": 1, "netdev_budget": 600, "netdev_budget_usecs": 20000,
    "tcp_early_retrans": 3, "tcp_limit_output_bytes": 98304,
    "tcp_notsent_lowat": 8192, "tcp_pacing_ca_ratio": 105, "tcp_pacing_ss_ratio": 140,
}
AP_AQL = {"VO": (300, 600), "VI": (1200, 2400), "BE": (1500, 3000), "BK": (500, 1000)}


def _digest(value):
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(serialized.encode()).hexdigest()


@pytest.fixture(scope="module")
def saved_sources():
    paths = (
        "artifacts/autoresearch/stage44a_m26_m27_napi_and_r5ac_txq_bench_20261025.json",
        "artifacts/autoresearch/stage43a_ltu_rocket_ram_module_injection_20261025.json",
    )
    return tuple(json.loads((ROOT / path).read_text(encoding="utf-8-sig")) for path in paths)


@pytest.fixture
def stage44(saved_sources):
    return deepcopy(saved_sources[0])


@pytest.fixture
def stage43(saved_sources):
    return deepcopy(saved_sources[1])


@pytest.fixture
def profile(stage44):
    return stage44["rounds"][4]["phases"]["B1"]["getter_readback"]


def _profile_check(profile, ap=AP_INTERFACES, cpe=CPE_INTERFACES):
    return verifier.verify_asymmetric_profile(profile, ap_interfaces=ap, cpe_interfaces=cpe)


def _profile_integer_paths():
    paths = []
    for prefix, interfaces in (("ap", AP_INTERFACES), ("cpe", CPE_INTERFACES)):
        paths.extend((prefix + "_netdev_tx_queue_len", name) for name in interfaces)
        for field in ("napi_defer_hard_irqs", "gro_flush_timeout_ns"):
            paths.extend((prefix + "_" + field, name) for name in interfaces)
        paths.extend((prefix + "_sysctl", field) for field in SYSCTLS)
        paths.extend((prefix + "_aqm", field)
                     for field in ("fq_flows_cnt", "fq_memory_limit", "fq_limit", "fq_quantum"))
    paths.extend(("ap_aql_txq_limit", ac, field)
                 for ac in AP_AQL for field in ("low_us", "high_us"))
    paths.extend(("r5ac_m26_state", field) for field in
                 ("br0_txqueuelen", "ath0_txqueuelen", "eth0_txqueuelen", "netdev_budget", "dev_weight"))
    paths.extend(("lbm5_m24_state", field) for field in
                 ("br0_txqueuelen", "ath0_txqueuelen", "eth0_txqueuelen", "ewma_delegate", "no_auto_prio"))
    return paths


PROFILE_INTEGERS = _profile_integer_paths()


def _parent_and_key(value, path):
    for key in path[:-1]:
        value = value[key]
    return value, path[-1]


@pytest.fixture
def readback():
    return {
        "device_id": "synthetic-ltu-bench", "boot_id": "synthetic-boot-001",
        "module_sha256": "a" * 64, "evidence_sha256": "b" * 64,
        "board_ssid": 0xAE08, "intmode": 1, "irq_gpio": "GPIO_8", "irq_registered": True,
    }


def _calibrations(readback, count=4):
    return [
        dict(readback, sequence=index, monotonic_ns=1000 + index,
             frequency_mhz=(5500, 5520)[index % 2],
             freq_list=[(5500, 5520)[index % 2]] * 4,
             dcxo_before=42, dcxo_after=42, crystal_locked=True, calibration_complete=True)
        for index in range(count)
    ]


@pytest.fixture
def calibrations(readback):
    return _calibrations(readback)


def _calibration_check(samples, readback, frequencies=(5500, 5520)):
    return verifier.verify_alternating_dcxo(
        samples, declared_frequencies=frequencies, expected_identity=readback)


def _candidate(ssid, readback, samples):
    return verifier.prepare_ini_candidate(
        ssid, readback=readback, calibration_samples=samples, declared_frequencies=(5500, 5520))


def test_saved_sources_have_five_exact_round_pins_and_whole_object_bindings(saved_sources):
    stage44, stage43 = saved_sources
    assert {row["round_id"]: _digest(row) for row in stage44["rounds"]} == ROUND_PINS
    assert _digest(stage44) == "67c803852ee7a10b111a13b5536115eb8263249b944310afb22506b7dc475ee6"
    assert _digest(stage43) == "c5443bb806b6d229fea5ddba22068951b414edcd121f98af11464521e59dc820"
    result = verifier.source_contract(stage44, stage43)
    assert result["round_bindings"] == ROUND_PINS
    assert result["source_authenticated"] is True
    assert result["authentication_scope"] == "CANONICAL_SAVED_OBJECTS_NOT_NATIVE_ACQUISITION"


@pytest.mark.parametrize("index", range(5))
def test_every_round_is_content_pinned(stage44, stage43, index):
    stage44["rounds"][index]["decision"] = "ALTERED_SAVED_DECISION"
    with pytest.raises(ValueError, match="PINNED_ROUND_DRIFT"):
        verifier.source_contract(stage44, stage43)


@pytest.mark.parametrize("key", ("stage", "safety_policy", "starting_champion_baseline"))
def test_stage44_envelope_is_pinned_outside_rounds(stage44, stage43, key):
    stage44[key] = "ALTERED_ENVELOPE"
    with pytest.raises(ValueError, match="PINNED_STAGE44_ENVELOPE_DRIFT"):
        verifier.source_contract(stage44, stage43)


@pytest.mark.parametrize("key", (
    "stage", "target_unit", "binary_patches", "test1_rocket_ame_core_intmode1",
    "test2_ltu_ame_core_intmode1", "final_active_state_on_ltu1", "additional_evidence",
))
def test_stage43_entire_object_is_pinned(stage44, stage43, key):
    stage43[key] = {"altered": True}
    with pytest.raises(ValueError, match="PINNED_STAGE43_DRIFT"):
        verifier.source_contract(stage44, stage43)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown"))
def test_all_five_unique_expected_rounds_are_required(stage44, change):
    if change == "missing":
        stage44["rounds"].pop()
    elif change == "extra":
        stage44["rounds"].append(deepcopy(stage44["rounds"][0]))
    else:
        stage44["rounds"][-1]["round_id"] = "S44A-R1" if change == "duplicate" else "S44A-R6"
    with pytest.raises(ValueError):
        verifier.audit_stage44a(stage44)


@pytest.mark.parametrize("index", range(5))
@pytest.mark.parametrize("phase", PHASES)
def test_every_one_of_twenty_windows_is_required(stage44, index, phase):
    del stage44["rounds"][index]["phases"][phase]
    with pytest.raises(ValueError, match="ALL_FOUR_PHASES_REQUIRED"):
        verifier.audit_stage44a(stage44)


def test_audit_recomputes_twenty_windows_without_promoting_physical_acceptance(stage44):
    result = verifier.audit_stage44a(stage44)
    assert result["windows"] == 20
    assert [row["round_id"] for row in result["rounds"]] == list(ROUND_PINS)
    assert [row["promoted"] for row in result["rounds"]] == [False] * 4 + [True]
    for original, audited in zip(stage44["rounds"], result["rounds"]):
        assert set(audited["udp_windows"]) == set(PHASES)
        for short, field in (("goodput", "aggregate_goodput_mbps"),
                             ("p95", "sector_p95_rtt_ms"), ("p99", "sector_p99_rtt_ms")):
            control = round(mean(original["phases"][p][field] for p in ("A1", "A2")), 3)
            target = round(mean(original["phases"][p][field] for p in ("B1", "B2")), 3)
            assert audited["recomputed"][short] == {
                "control": control, "target": target,
                "delta_pct": round(100 * (target - control) / control, 3),
            }
    champion = result["champion"]
    assert champion["reported_version"] == 15
    assert champion["reported_promotion"] is True
    assert champion["complete_champion_qualified"] is False
    assert champion["new_hardware_measurement"] is False
    assert champion["universal_txq_rule_proven"] is False
    assert champion["bql_causal_explanation"] == "INFERRED_NOT_ISOLATED"


@pytest.mark.parametrize("field", (
    "goodput_delta_pct", "p95_rtt_delta_pct", "pareto_score_delta_pct",
    "iptv_jitter_delta_pct", "voip_jitter_delta_pct",
))
def test_reported_deltas_cannot_override_recomputed_values(stage44, field):
    stage44["rounds"][0][field] += 1
    with pytest.raises(ValueError, match="RECOMPUTED_"):
        verifier.audit_stage44a(stage44)


@pytest.mark.parametrize("value", (0, 1, "false", None))
def test_promotion_must_be_a_real_boolean(stage44, value):
    stage44["rounds"][0]["promoted"] = value
    with pytest.raises(ValueError, match="EXPLICIT_PROMOTION_BOOL_REQUIRED"):
        verifier.audit_stage44a(stage44)


@pytest.mark.parametrize("field,value", (
    ("lost_datagrams", True), ("total_datagrams", 0), ("lost_datagrams", 10**8),
    ("packet_loss_pct", True), ("packet_loss_pct", 101), ("jitter_ms", float("nan")),
    ("raw_receiver_line", "0/1 (0%) receiver"),
))
def test_udp_counts_percent_and_raw_receiver_are_consistent(stage44, field, value):
    stage44["rounds"][0]["phases"]["A1"]["iptv_dual_stream_ac_vi"][field] = value
    with pytest.raises(ValueError):
        verifier.audit_stage44a(stage44)


def test_saved_asymmetric_profile_is_consistent_but_incomplete(profile):
    result = _profile_check(profile)
    assert result["profile_matches"] is True
    assert result["ap_queues"]["eth0"] == result["cpe_queues"]["eth0"] == 1000
    assert result["ap_queues"]["phy0-ap0.sta1"] == 256
    for key in ("driver_bql_status", "cpe_aql_status", "station_airtime_weights_status"):
        assert result[key] == "UNKNOWN"
    assert result["native_authenticated"] is result["complete_champion_qualified"] is False


@pytest.mark.parametrize("path", PROFILE_INTEGERS, ids=lambda p: "/".join(p))
def test_every_profile_integer_rejects_drift(profile, path):
    parent, key = _parent_and_key(profile, path)
    parent[key] += 1
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("path", PROFILE_INTEGERS, ids=lambda p: "/".join(p))
@pytest.mark.parametrize("bad", (False, True, "0", 0.0))
def test_profile_integers_reject_bool_string_and_float_coercion(profile, path, bad):
    parent, key = _parent_and_key(profile, path)
    parent[key] = bad
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("field,value", (
    ("ff_mcast_airtime_limit", "5 0"), ("txop_params", "0 1"), ("no_ack_rate", "0 0"),
))
def test_profile_vectors_are_exact(profile, field, value):
    group = "r5ac_m26_state" if field == "ff_mcast_airtime_limit" else "lbm5_m24_state"
    profile[group][field] = value
    with pytest.raises(ValueError):
        _profile_check(profile)


@pytest.mark.parametrize("prefix", ("ap", "cpe"))
@pytest.mark.parametrize("field", ("netdev_tx_queue_len", "napi_defer_hard_irqs", "gro_flush_timeout_ns"))
def test_every_interface_inventory_must_be_complete(profile, prefix, field):
    del profile[prefix + "_" + field]["eth0"]
    with pytest.raises(ValueError):
        _profile_check(profile)


def test_dynamic_ap_vlan_is_supported_only_when_explicitly_inventoried(profile):
    for field in ("netdev_tx_queue_len", "napi_defer_hard_irqs", "gro_flush_timeout_ns"):
        profile["ap_" + field]["phy0-ap0.sta23"] = 256 if field == "netdev_tx_queue_len" else 0
    with pytest.raises(ValueError, match="COMPLETE_INTERFACE_INVENTORY_REQUIRED"):
        _profile_check(profile)
    result = _profile_check(profile, ap=(*AP_INTERFACES, "phy0-ap0.sta23"))
    assert result["ap_queues"]["phy0-ap0.sta23"] == 256


@pytest.mark.parametrize("name", ("phy0-ap0.sta0", "phy0-ap0.sta01", "phy0-ap0.sta*", "eth1"))
def test_dynamic_inventory_does_not_admit_wildcard_or_wrong_device(profile, name):
    for field in ("netdev_tx_queue_len", "napi_defer_hard_irqs", "gro_flush_timeout_ns"):
        profile["ap_" + field][name] = 256 if field == "netdev_tx_queue_len" else 0
    with pytest.raises(ValueError):
        _profile_check(profile, ap=(*AP_INTERFACES, name))


@pytest.mark.parametrize("inventory", ((), None, ("eth0", "eth0"), ("eth0", True)))
def test_inventory_must_be_explicit_nonempty_and_unique(profile, inventory):
    with pytest.raises(ValueError):
        _profile_check(profile, ap=inventory)


@pytest.mark.parametrize("ac", tuple(AP_AQL))
def test_ap_aql_requires_every_access_category(profile, ac):
    del profile["ap_aql_txq_limit"][ac]
    with pytest.raises(ValueError, match="COMPLETE_AP_AQL_REQUIRED"):
        _profile_check(profile)


@pytest.fixture
def bql():
    return {"driver": "ag71xx", "interface": "eth0", "expected_queues": ["tx-0"],
            "queues": {"tx-0": {"limit_min": 0, "limit": 54250, "limit_max": 262144}}}


@pytest.mark.parametrize("limit", (0, 1780, 54250, 65536, 262144))
def test_bql_accepts_dynamic_bounds_without_a_fixed_byte_target(bql, limit):
    bql["queues"]["tx-0"]["limit"] = limit
    result = verifier.validate_bql_evidence(bql)
    assert result["supplied_evidence_consistent"] is True
    assert result["native_authenticated"] is result["hardware_offload_proven"] is False
    assert result["bql_causality"] == "UNKNOWN"


@pytest.mark.parametrize("field,value", (
    ("driver", "ath10k"), ("driver", "unknown"), ("interface", "br-lan"),
    ("expected_queues", None), ("expected_queues", ["tx-1"]),
    ("expected_queues", ["tx-0", "tx-0"]), ("expected_queues", []),
))
def test_bql_needs_real_driver_interface_and_complete_declared_inventory(bql, field, value):
    bql[field] = value
    with pytest.raises(ValueError):
        verifier.validate_bql_evidence(bql)


@pytest.mark.parametrize("field,value", (
    ("limit_min", 54251), ("limit", 262145), ("limit_max", 0),
    ("limit", True), ("limit_min", False), ("limit_max", "262144"),
    ("limit", -1), ("limit", 1.0), ("limit_max", 2**32),
))
def test_bql_bounds_are_strict_unsigned_integers(bql, field, value):
    bql["queues"]["tx-0"][field] = value
    with pytest.raises(ValueError):
        verifier.validate_bql_evidence(bql)


@pytest.mark.parametrize("count", (0, 65))
def test_bql_queue_count_is_bounded(bql, count):
    bql["queues"] = {f"tx-{n}": {"limit_min": 0, "limit": 1, "limit_max": 2} for n in range(count)}
    bql["expected_queues"] = list(bql["queues"])
    with pytest.raises(ValueError):
        verifier.validate_bql_evidence(bql)


@pytest.mark.parametrize("ssid", ("a", "a" * 16, "é" * 8, "😀" * 4, "e\u0301" * 5))
def test_ssid_preserves_exact_utf8_bytes_with_no_normalization(ssid):
    assert verifier.validate_ssid(ssid) == ssid.encode("utf-8")


@pytest.mark.parametrize("ssid", ("", "a" * 17, "é" * 9, "😀" * 5, None, b"abc", 16))
def test_ssid_enforces_sixteen_utf8_bytes_without_truncation(ssid):
    with pytest.raises(ValueError):
        verifier.validate_ssid(ssid)


@pytest.mark.parametrize("control", ("\0", "\n", "\r", "\t", "\x1b", "\x7f", "\x85", "\u200b",
                                     "\u2028", "\u2029", "\ud800", "\udfff"))
def test_ssid_rejects_nul_controls_and_surrogates(control):
    with pytest.raises(ValueError):
        verifier.validate_ssid("a" + control + "b")


@pytest.mark.parametrize("delimiter", tuple("=;#\"'\\[]"))
def test_ini_candidate_rejects_ambiguous_payload_delimiters(readback, calibrations, delimiter):
    with pytest.raises(ValueError, match="AMBIGUOUS_INI_SSID_NOT_ALLOWED"):
        _candidate("a" + delimiter + "b", readback, calibrations)


@pytest.mark.parametrize("ssid", ("a" * 17, "é" * 9, "😀" * 5, "a\0b", "a=b", "a\nb"))
def test_ssid_is_validated_before_any_evidence_handling(monkeypatch, ssid):
    def forbidden_readback(_):
        pytest.fail("Invalid SSID reached evidence handling")
    monkeypatch.setattr(verifier, "verify_ltu_readback", forbidden_readback)
    with pytest.raises(ValueError):
        _candidate(ssid, object(), object())


@pytest.mark.parametrize("ssid", ("FuturaMAX-LTU-Be", "a" * 16, "é" * 8, "😀" * 4))
def test_candidate_is_exact_sealed_review_fragment_and_never_native(readback, calibrations, ssid):
    result = _candidate(ssid, readback, calibrations)
    expected = b"ssid=" + ssid.encode("utf-8") + b"\n"
    assert result["payload_utf8"] == expected
    assert result["payload_sha256"] == hashlib.sha256(expected).hexdigest()
    assert result["ssid_bytes"] == 16
    assert result["evidence_binding"] == _digest({
        "readback": readback, "samples": calibrations, "frequencies": [5500, 5520]})
    assert result["native_dispatch_allowed"] is False
    assert result["complete_native_ini"] is False
    assert result["native_buffer_termination_qualified"] is False


@pytest.mark.parametrize("field,value", (
    ("board_ssid", 0xAE05), ("board_ssid", "0xae08"), ("board_ssid", True),
    ("intmode", 0), ("intmode", True), ("intmode", "1"), ("intmode", 1.0),
    ("irq_gpio", "GPIO_9"), ("irq_gpio", 8), ("irq_registered", 1), ("irq_registered", False),
))
def test_ltu_readback_requires_ae08_intmode_one_and_gpio8_irq(readback, field, value):
    readback[field] = value
    with pytest.raises(ValueError):
        verifier.verify_ltu_readback(readback)


def test_ltu_readback_is_synthetic_consistency_only(readback):
    result = verifier.verify_ltu_readback(readback)
    assert result["supplied_readback_consistent"] is True
    assert result["native_authenticated"] is False
    assert (result["board_ssid"], result["intmode"], result["irq_gpio"]) == (0xAE08, 1, "GPIO_8")


@pytest.mark.parametrize("field", ("device_id", "boot_id", "module_sha256", "evidence_sha256"))
@pytest.mark.parametrize("value", (None, "", True, "bad\nidentity", "x" * 129))
def test_readback_needs_explicit_valid_identity_and_hashes(readback, field, value):
    readback[field] = value
    with pytest.raises(ValueError):
        verifier.verify_ltu_readback(readback)


@pytest.mark.parametrize("field", ("module_sha256", "evidence_sha256"))
@pytest.mark.parametrize("value", ("A" * 64, "g" * 64, "a" * 63, "a" * 65, "a" * 64 + "\n"))
def test_identity_hash_is_exact_lowercase_sha256(readback, field, value):
    readback[field] = value
    with pytest.raises(ValueError):
        verifier.verify_ltu_readback(readback)


@pytest.mark.parametrize("count", (4, 6, 64))
def test_complete_abab_calibration_is_bounded_and_need_not_change_dcxo_code(readback, count):
    samples = _calibrations(readback, count)
    result = _calibration_check(samples, readback)
    assert result["calibration_samples"] == count
    assert result["last_frequency_mhz"] == 5520
    assert result["native_authenticated"] is False


@pytest.mark.parametrize("count", (0, 1, 2, 3, 5, 63, 65, 66))
def test_calibration_rejects_partial_odd_or_unbounded_recipe(readback, count):
    with pytest.raises(ValueError, match="BOUNDED_COMPLETE_ABAB_CALIBRATION_REQUIRED"):
        _calibration_check(_calibrations(readback, count), readback)


@pytest.mark.parametrize("frequencies", (None, [], [5500], [5500, 5520, 5540], [5500, 5500],
                                        [0, 5520], [True, 5520], [5500.0, 5520],
                                        ["5500", 5520], [5500, 10001]))
def test_frequencies_must_be_two_predeclared_distinct_positive_integers(readback, calibrations, frequencies):
    with pytest.raises(ValueError):
        _calibration_check(calibrations, readback, frequencies)


@pytest.mark.parametrize("field,value", (
    ("sequence", 4), ("sequence", True), ("monotonic_ns", -1), ("monotonic_ns", True),
    ("monotonic_ns", 2**64), ("frequency_mhz", 5520), ("frequency_mhz", "5500"),
    ("freq_list", [5500] * 3), ("freq_list", [5500, 5500, 5520, 5500]),
    ("freq_list", [True] * 4), ("freq_list", (5500,) * 4),
    ("crystal_locked", 1), ("crystal_locked", False), ("calibration_complete", 1),
    ("calibration_complete", False), ("dcxo_before", -1), ("dcxo_after", float("nan")),
    ("dcxo_before", True), ("dcxo_after", float("inf")),
    ("device_id", "different-device"), ("boot_id", "different-boot"),
    ("module_sha256", "c" * 64), ("evidence_sha256", "invalid"),
))
def test_every_calibration_sample_is_validated(readback, calibrations, field, value):
    calibrations[0][field] = value
    with pytest.raises(ValueError):
        _calibration_check(calibrations, readback)


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("field", ("sequence", "monotonic_ns", "frequency_mhz", "freq_list",
                                   "crystal_locked", "calibration_complete", "dcxo_before", "dcxo_after",
                                   "device_id", "boot_id", "module_sha256", "evidence_sha256"))
def test_no_calibration_row_may_omit_required_evidence(readback, calibrations, index, field):
    del calibrations[index][field]
    with pytest.raises(ValueError):
        _calibration_check(calibrations, readback)


@pytest.mark.parametrize("stamp", (1000, 999))
def test_calibration_timestamps_must_strictly_increase(readback, calibrations, stamp):
    calibrations[1]["monotonic_ns"] = stamp
    with pytest.raises(ValueError, match="STRICT_CALIBRATION_TIMESTAMPS_REQUIRED"):
        _calibration_check(calibrations, readback)


def test_monotonic_origin_may_be_zero(readback, calibrations):
    for index, sample in enumerate(calibrations):
        sample["monotonic_ns"] = index
    assert _calibration_check(calibrations, readback)["calibration_samples"] == 4


def test_saved_zero_peers_and_failed_ping_do_not_qualify_ota(stage43):
    result = verifier.audit_stage43a(stage43)
    assert {test["stations"] for test in result["tests"].values()} == {0}
    assert {test["reported_ssid"] for test in result["tests"].values()} == {"FuturaMAX-LTU-Be"}
    for test in result["tests"].values():
        assert test["reported_ssid_bytes"] == 16
        for key in ("intmode_getter", "gpio8_irq", "alternating_freq_list_dcxo", "native_module_identity"):
            assert test[key] == "UNKNOWN"
    assert result["final_remote_info"] == "Total: 0\nTOTAL LINKS: 0"
    assert result["final_ping"] == "PING_111_NO_REPLY"
    assert result["ota_link_qualified"] is False
    assert result["native_ini_admitted"] is False
    assert result["abi_compatibility_from_vermagic_proven"] is False
    assert result["patched_success_return_proves_hardware_success"] is False
    assert result["original_input_ssid_available"] is False


def test_saved_audit_has_explicit_offline_and_unaccepted_boundaries():
    result = verifier.audit_saved_sources(ROOT)
    assert result["windows"] == 20
    assert result["boundaries"] == {
        "offline_only": True, "ssh": False, "hardware_access": False,
        "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED",
    }


def test_module_ast_has_no_runner_network_subprocess_or_native_callback():
    tree = ast.parse(Path(verifier.__file__).read_text(encoding="utf-8"))
    allowed_imports = {"__future__", "hashlib", "pathlib", "re", "unicodedata",
                       "controller.stage42a_netdev_txq_and_airos6_verifier"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name in allowed_imports for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module in allowed_imports
        if isinstance(node, ast.Call):
            function = node.func
            name = function.id if isinstance(function, ast.Name) else getattr(function, "attr", "")
            if isinstance(function, ast.Name):
                assert name not in {"__import__", "eval", "exec", "compile"}
            assert name not in {"system", "popen",
                                "Popen", "run", "check_call", "check_output", "spawn", "socket",
                                "connect", "request", "urlopen", "CDLL", "WinDLL", "dlopen"}
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names = {arg.arg for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)}
            assert not names.intersection({"callback", "runner", "executor", "loader", "transport"})
