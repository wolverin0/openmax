"""Offline Stage47B evidence tests; backup contents never appear in test output."""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tools.verify import verify_stage52a_and_pbe5ac_ptp_ota as verifier


ROOT = Path(__file__).resolve().parents[1]
SOURCE_51 = "artifacts/autoresearch/stage51a_m30_m31_bql_sweetspot_and_aql_bench_20261025.json"
SOURCE_52 = "artifacts/autoresearch/stage52a_m32_m33_budget_usecs_and_bql_min_bench_20261025.json"
REPORT_51 = "docs/STAGE51A_M30_M31_BQL_SWEETSPOT_AND_AQL_BENCHMARK.md"
REPORT_52 = "docs/STAGE52A_M32_M33_BUDGET_USECS_AND_BQL_MIN_BENCHMARK.md"
BACKUP_DIR = "artifacts/autoresearch/pbe5ac_original_configs_backup_20261025"
BOOST_RECEIPT = "artifacts/autoresearch/pbe5ac_ota_boost_receipt_20261025.json"
INPUT_PINS = {
    SOURCE_51: "835e1a9dd62fb6633efb5cfd1fa7b612921a4c54d54c4f99ecb6e37ea7f093a8",
    REPORT_51: "85988021fc99c8b2c3bfbc41fcb905332c303d08a20f0554621df11dc69ac2e8",
    SOURCE_52: "c01d6e8c7cff042b5f3bd627e3942767c7bd6fc2654b079fd07ab394c00bfc26",
    REPORT_52: "f43d2a3d702a784a2ca98eeb7c059557bd97913d17813ee448161c464b0c37fb",
    BACKUP_DIR + "/pbe_8773_ptp_guarida_ap_system.cfg": "c191599f63bc4da51707d631ae01f25a0ebcb46d16f7ab71aafecd0300b6412e",
    BACKUP_DIR + "/pbe_8a01_ptp_alma_sta_system.cfg": "39e2d58499c800e33bb2cdd534735bf76e497ae88388760b44013422220c5069",
    BOOST_RECEIPT: "5f1236612fac5de70a27a0e992c65f6aa846705d718f059a6f44b542647d128b",
}
ROUND_52_PINS = (
    "beb4c35ee838f153bb31500beaa83d8fa283347d5e512b1f7a303cd3f5d64e14",
    "78797d88effddd01166fe44fa852428cf7446eb4a9be038a839d1bf310b5146d",
    "fabc84ea960e5485e68b20d4325dbce4b901b14e471f6e24b91e7e0d3e9fc2aa",
    "daaa81f55f44137fb34cb89f5d9f4186322ea162c2d3e266ded0aa61d3d980b5",
)
PHASES = ("A1", "B1", "A2", "B2")


def _digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def stage52():
    return json.loads((ROOT / SOURCE_52).read_text(encoding="utf-8-sig"))


@pytest.fixture
def profile(stage52):
    return stage52["rounds"][2]["phases"]["B1"]["getter_readback"]


@pytest.fixture
def source_root(tmp_path):
    # Copy opaque backup bytes without decoding them or including them in assertions.
    for relative in INPUT_PINS:
        destination = tmp_path / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / relative).read_bytes())
    return tmp_path


@pytest.fixture
def pbe_receipt():
    return json.loads((ROOT / BOOST_RECEIPT).read_text(encoding="utf-8-sig"))


def test_all_requested_inputs_have_independent_whole_file_pins_and_exact_stage52_rounds(stage52):
    for relative, expected in INPUT_PINS.items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected
    assert _digest(stage52) == "d0dc006a27201ff2dbc22aa453058f6ddfb4a7fb187e81bfe8d1df1b69de8d11"
    assert tuple(_digest(row) for row in stage52["rounds"]) == ROUND_52_PINS


@pytest.mark.parametrize("relative", (SOURCE_51, SOURCE_52))
def test_json_source_drift_is_rejected_without_replacing_saved_evidence(source_root, relative):
    path = source_root / relative
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    document["rounds"][0]["decision"] = "ALTERED"
    path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        verifier.audit_saved_sources(source_root)


@pytest.mark.parametrize("relative", (REPORT_51, REPORT_52))
def test_report_bytes_drift_is_rejected(source_root, relative):
    path = source_root / relative
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ValueError):
        verifier.audit_saved_sources(source_root)


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("phase", PHASES)
def test_stage52_requires_each_of_sixteen_windows(stage52, index, phase):
    del stage52["rounds"][index]["phases"][phase]
    with pytest.raises(ValueError):
        verifier.audit_stage52a(stage52)


@pytest.mark.parametrize("field", ("aggregate_goodput_mbps", "sector_p50_rtt_ms", "sector_p95_rtt_ms", "sector_p99_rtt_ms"))
@pytest.mark.parametrize("bad", (True, "1", float("nan"), -1))
def test_stage52_core_metrics_require_finite_numbers_without_boolean_coercion(stage52, field, bad):
    stage52["rounds"][0]["phases"]["A1"][field] = bad
    with pytest.raises(ValueError):
        verifier.audit_stage52a(stage52)


@pytest.mark.parametrize("change", ("missing", "extra", "duplicate", "unknown"))
def test_stage52_requires_four_unique_expected_rounds(stage52, change):
    if change == "missing":
        stage52["rounds"].pop()
    elif change == "extra":
        stage52["rounds"].append(deepcopy(stage52["rounds"][0]))
    else:
        stage52["rounds"][-1]["round_id"] = "S52A-R1" if change == "duplicate" else "S52A-R5"
    with pytest.raises(ValueError):
        verifier.audit_stage52a(stage52)


def _synthetic_consistent_profile(profile):
    # The saved CPE limit is below its configured minimum. This creates only a
    # local consistency fixture; the original saved evidence is left unchanged.
    supplied = deepcopy(profile)
    supplied["cpe_eth0_bql"]["limit"] = 4542
    return supplied


def test_actual_v18_profile_fails_strict_current_bound_guard_without_mutation(profile):
    before = _digest(profile)
    with pytest.raises(ValueError):
        verifier.verify_v18_profile(profile)
    assert _digest(profile) == before
    assert profile["cpe_eth0_bql"]["limit"] == 3028
    assert profile["cpe_eth0_bql"]["limit_min"] == 4542


@pytest.mark.parametrize("prefix", ("ap", "cpe"))
@pytest.mark.parametrize("field,value", (("limit_min", 4543), ("limit_max", 42393), ("hold_time", 1001),
                                        ("limit", 4541), ("inflight", False)))
def test_v18_profile_strict_bql_contract_rejects_drift_or_unconverged_current(profile, prefix, field, value):
    supplied = _synthetic_consistent_profile(profile)
    supplied[prefix + "_eth0_bql"][field] = value
    with pytest.raises(ValueError):
        verifier.verify_v18_profile(supplied)


@pytest.mark.parametrize("prefix", ("ap", "cpe"))
@pytest.mark.parametrize("field,value", (("netdev_budget", 300), ("netdev_budget_usecs", 6000),
                                        ("dev_weight_tx_bias", 1), ("dev_weight_tx_bias", True)))
def test_v18_profile_checks_observed_budget_fields_without_boolean_coercion(profile, prefix, field, value):
    supplied = _synthetic_consistent_profile(profile)
    supplied[prefix + "_sysctl"][field] = value
    with pytest.raises(ValueError):
        verifier.verify_v18_profile(supplied)


def test_synthetic_consistent_v18_policy_is_narrow_and_never_native_acceptance(profile):
    supplied = _synthetic_consistent_profile(profile)
    before = _digest(supplied)
    result = verifier.verify_v18_profile(supplied)
    assert _digest(supplied) == before
    assert result["supplied_policy_matches"] is True
    assert result["scope"] == "BQL_AND_RECORDED_SYSCTL_POLICY_ONLY"
    assert result["complete_profile_or_native_acceptance"] is False
    assert result["bql"]["cpe"]["limit"] == 4542


@pytest.mark.parametrize("prefix", ("ap", "cpe"))
@pytest.mark.parametrize("group", ("eth0_bql", "sysctl"))
def test_v18_policy_rejects_missing_endpoint_group(profile, prefix, group):
    supplied = _synthetic_consistent_profile(profile)
    del supplied[prefix + "_" + group]
    with pytest.raises(ValueError):
        verifier.verify_v18_profile(supplied)


@pytest.mark.parametrize("hz,expected", ((100, 20000), (250, 8000), (1000, 2000)))
def test_supplied_hz_upstream_minimum_is_not_running_kernel_or_hardware_proof(hz, expected):
    result = verifier.kernel_budget_floor(hz=hz)
    assert result["minimum_us"] == expected
    assert result["below_minimum_write_is_rejected_not_clamped"] is True
    assert result["native_hz_build_or_write_error_proven"] is False
    assert result["hardware_minimum_proven"] is False


@pytest.mark.parametrize("hz", (False, 0, -1, 100.0, "100", 1_000_001))
def test_supplied_hz_requires_bounded_positive_integer(hz):
    with pytest.raises(ValueError):
        verifier.kernel_budget_floor(hz=hz)


@pytest.fixture
def stage51():
    return json.loads((ROOT / SOURCE_51).read_text(encoding="utf-8-sig"))


@pytest.mark.parametrize("index", range(6))
def test_each_stage51_round_remains_pinned(stage51, stage52, index):
    stage51["rounds"][index]["decision"] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(stage51, stage52, (ROOT / REPORT_51).read_bytes().decode(),
                                 (ROOT / REPORT_52).read_bytes().decode())


@pytest.mark.parametrize("index", range(4))
def test_each_stage52_round_remains_pinned(stage51, stage52, index):
    stage52["rounds"][index]["decision"] = "ALTERED"
    with pytest.raises(ValueError):
        verifier.source_contract(stage51, stage52, (ROOT / REPORT_51).read_bytes().decode(),
                                 (ROOT / REPORT_52).read_bytes().decode())


@pytest.mark.parametrize("index", range(4))
def test_stage52_recomputes_all_arm_means_and_raw_udp_layers(stage52, index):
    row = stage52["rounds"][index]
    audited = verifier.audit_stage52a(stage52)["rounds"][index]
    assert audited["round_id"] == row["round_id"]
    assert list(audited["windows"]) == list(PHASES)
    for metric, field in (("goodput", "aggregate_goodput_mbps"), ("p50", "sector_p50_rtt_ms"),
                          ("p95", "sector_p95_rtt_ms"), ("p99", "sector_p99_rtt_ms")):
        means = {}
        for arm, output_key in (("A", "control"), ("B", "target")):
            means[arm] = round(sum(row["phases"][arm + str(n)][field] for n in (1, 2)) / 2, 3)
            assert audited["metrics"][metric][output_key] == pytest.approx(means[arm])
        expected_delta = round(100 * (means["B"] - means["A"]) / means["A"], 4)
        assert audited["metrics"][metric]["delta_pct"] == pytest.approx(expected_delta)
    for stream, field in (("iptv", "iptv_dual_stream_ac_vi"), ("voip", "voip_stream_ac_vo")):
        for phase in PHASES:
            saved = row["phases"][phase][field]
            observed = audited["windows"][phase]["udp"][stream]
            match = re.search(r"([0-9.]+) ([KMG]?)bits/sec\s+([0-9.]+) ms\s+(\d+)/(\d+) \(([0-9.]+)%\)",
                              saved["raw_receiver_line"])
            assert match is not None
            assert observed["consistent"] is True
            assert all(observed["checks"].values())
            assert observed["raw"]["bitrate_mbps"] == pytest.approx(float(match[1]) * {"": 1e-6, "K": .001, "M": 1, "G": 1000}[match[2]])
            assert observed["raw"]["jitter_ms"] == pytest.approx(float(match[3]))
            assert observed["raw"]["lost"] == int(match[4])
            assert observed["raw"]["total"] == int(match[5])
        for arm in ("A", "B"):
            samples = [row["phases"][arm + str(n)][field] for n in (1, 2)]
            summary = audited["metrics"][stream][arm]
            assert summary["typed_mean_jitter_ms"] == pytest.approx(round(sum(x["jitter_ms"] for x in samples) / 2, 3))
            assert summary["typed_mean_bitrate_mbps"] == pytest.approx(round(sum(x["delivered_bitrate_mbps"] for x in samples) / 2, 3))
            assert summary["mean_typed_loss_pct"] == pytest.approx(round(sum(x["packet_loss_pct"] for x in samples) / 2, 4))
            assert summary["lost"] == sum(x["lost_datagrams"] for x in samples)
            assert summary["total"] == sum(x["total_datagrams"] for x in samples)
            assert summary["pooled_count_loss_pct"] == pytest.approx(100 * summary["lost"] / summary["total"])


def test_stage52_preserves_all_anomalies_and_champion_tradeoffs(stage52):
    result = verifier.audit_stage52a(stage52)
    assert result["windows"] == 16 and result["udp_observations"] == 32
    assert len(result["findings"]) == 11
    unconverged = result["unconverged_bql_snapshots"]
    assert {(x["round"], x["phase"], x["endpoint"]) for x in unconverged} == {
        (f"S52A-R{n}", phase, "cpe") for n in (2, 3, 4) for phase in ("B1", "B2")}
    assert all(x["snapshot"]["limit"] == 3028 and x["snapshot"]["limit_min"] == 4542 for x in unconverged)
    assert len(result["failed_ping_windows"]) == 1
    failed = result["failed_ping_windows"][0]
    assert (failed["round"], failed["phase"]) == ("S52A-R4", "B2")
    assert failed["received_counts"]["LiteBeamM5_XW"] == 0
    assert failed["per_cpe_loss_pct"]["LiteBeamM5_XW"] == 100
    assert all(not v["accepted"] and "CURRENT_BQL" in v["error"] for v in result["champion"]["strict_profile_results"].values())
    assert result["champion"]["native_promotion_accepted"] is False
    champion = result["rounds"][2]["metrics"]
    assert champion["goodput"]["delta_pct"] == pytest.approx(7.0221)
    assert champion["p95"]["delta_pct"] == pytest.approx(-1.7951)
    assert champion["p99"]["delta_pct"] == pytest.approx(5.333)
    assert champion["iptv"]["typed_jitter_delta_pct"] == pytest.approx(51.3548)
    assert champion["voip"]["typed_jitter_delta_pct"] == pytest.approx(69.7531)
    assert result["native_acceptance"] is False


def test_all_time_budget_readbacks_remain_20000_without_claiming_hz_or_write_errors(stage52):
    records = verifier.audit_stage52a(stage52)["declared_vs_observed_time_budget"]
    assert len(records) == 32
    assert {x["observed_us"] for x in records} == {20000}
    assert sum(not x["request_matches_observation"] for x in records) == 12
    for record in records:
        assert record["native_error_or_hz_proven"] is False
        if record["phase"].startswith("B") and record["round"] in ("S52A-R1", "S52A-R3", "S52A-R4"):
            assert record["declared_requested_us"] == (8000 if record["round"] == "S52A-R4" else 6000)
            assert record["request_matches_observation"] is False


@pytest.mark.parametrize("field", ("promoted", "all_radios_healthy", "rounds_executed", "promoted_count"))
def test_stage52_summary_and_promotion_types_are_strict(stage52, field):
    if field == "promoted":
        stage52["rounds"][0][field] = 1
    else:
        stage52["summary"][field] = 1 if field == "all_radios_healthy" else True
    with pytest.raises(ValueError):
        verifier.audit_stage52a(stage52)


@pytest.mark.parametrize("change", ("missing_peer", "wrong_mac", "count_bool", "loss_over100"))
def test_stage52_peer_identity_completeness_and_loss_types(stage52, change):
    peers = stage52["rounds"][0]["phases"]["A1"]["per_cpe"]
    peer = peers["LiteBeamM5_XW"]
    if change == "missing_peer":
        del peers["LiteBeamM5_XW"]
    elif change == "wrong_mac":
        peer["mac"] = "00:00:00:00:00:00"
    else:
        peer["latency"]["count" if change == "count_bool" else "loss_pct"] = True if change == "count_bool" else 101
    with pytest.raises(ValueError):
        verifier.audit_stage52a(stage52)


def test_pure_audit_retains_disagreement_instead_of_repairing_typed_or_raw_data(stage52):
    row = stage52["rounds"][0]
    row["arm_a_mean_goodput_mbps"] += 1
    row["phases"]["A1"]["iptv_dual_stream_ac_vi"]["jitter_ms"] += 1
    before = _digest(stage52)
    result = verifier.audit_stage52a(stage52)
    assert _digest(stage52) == before
    assert any(x["code"] == "SUMMARY_MEAN_DISAGREES" for x in result["findings"])
    assert any(x["code"] == "UDP_LAYER_DISAGREEMENT" for x in result["findings"])
    assert result["native_acceptance"] is False


@pytest.fixture
def verification(source_root):
    return verifier.audit_saved_sources(source_root)


def test_combined_audit_preserves_exact_51_52_sources_and_distinct_pbe_scope(verification):
    assert verification["status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert verification["input_raw_sha256"] == {p: INPUT_PINS[p] for p in (SOURCE_51, SOURCE_52, REPORT_51, REPORT_52)}
    contract = verification["source_contract"]
    assert contract["saved_objects_authenticated"] is True
    assert contract["native_acquisition_authenticated"] is False
    assert len(contract["stage51_round_bindings"]) == 6
    assert len(contract["stage52_round_bindings"]) == 4
    assert verification["stage51a"]["windows"] == 24
    assert verification["stage51a"]["udp_observations"] == 48
    assert len(verification["stage51a"]["failed_ping_windows"]) == 16
    assert len(verification["pinned_stage52_report_conflicts"]) == 7
    assert all(c["pinned_report"] != c["exact_json_recomputed"] for c in verification["pinned_stage52_report_conflicts"])
    assert verification["pinned_stage51_report_qualifications"]["R5_three_CPE_verified_claim_not_supported"] is True
    assert verification["pbe5ac"]["separate_from_three_CPE_sector"] is True
    assert verification["pbe5ac"]["receipt_raw_sha256"] == INPUT_PINS[BOOST_RECEIPT]
    assert verification["pbe5ac"]["native_acceptance"] is False
    assert verification["boundary"] == {"offline_only": True, "hardware_access": False, "ssh": False,
                                        "native_dispatch_allowed": False, "physical_acceptance": "UNKNOWN", "e2": "NOT_ACCEPTED"}


def test_pbe_receipt_rf_arithmetic_does_not_authenticate_physical_experiment(pbe_receipt):
    before = _digest(pbe_receipt)
    result = verifier.audit_pbe_receipt(pbe_receipt)
    assert _digest(pbe_receipt) == before
    assert result["availability"] == "PRESENT"
    assert result["canonical_sha256"] == "76fd9f57d33dea3ba5c090e209c212edbf16e4439bca3667cac59c4c241c66df"
    arithmetic = result["rf_arithmetic"]
    assert arithmetic["reported_ap_txpower_delta_db"] == 20
    assert arithmetic["reported_sta_txpower_delta_db"] == 20
    assert arithmetic["reported_ap_rx_gain_db"] == 11
    assert arithmetic["reported_sta_rx_gain_db"] == 9
    assert arithmetic["reported_rx_mean_dbm"] == -67.5
    assert arithmetic["reported_chain_imbalance_db"] == 1
    assert arithmetic["rx_mean_matches"] is True and arithmetic["chain_imbalance_matches"] is True
    assert result["ota_bringup_accepted"] is False
    assert result["physical_acceptance"] == "UNKNOWN"
    assert result["raw_receipt_exported"] is False
    assert result["pair_macs_disjoint_from_three_CPE_sector"] is True
    assert result["cross_node_mgmt_address_reuses_sector_M5_address"] is True
    assert result["cross_node_hardware_identity_bound"] is False


def test_pbe_embedded_benchmark_summaries_are_internal_arithmetic_only(pbe_receipt):
    result = verifier.audit_pbe_receipt(pbe_receipt)
    summaries = result["embedded_summaries"]
    assert len(summaries) == 4
    for name, summary in summaries.items():
        saved = pbe_receipt["verified_ota_benchmarks"][name]
        values = summary["reported_values"]
        assert values["aggregate_goodput_mbps"] == saved["aggregate_goodput_mbps"]
        assert values["bulk_tcp_mbps"] + values["iptv_udp_mbps"] == pytest.approx(values["aggregate_goodput_mbps"], abs=.0011)
        assert summary["aggregate_bulk_plus_iptv_matches"] is True
        assert summary["referenced_source_opened_or_verified"] is False
    assert summaries["stage53a_champion_r4"]["reported_values"]["aggregate_goodput_mbps"] < summaries["stage53a_stock_baseline"]["reported_values"]["aggregate_goodput_mbps"]
    assert summaries["stage54a_cross_node_champion_r3"]["reported_values"]["voip_jitter_ms"] > summaries["stage54a_cross_node_stock_baseline"]["reported_values"]["voip_jitter_ms"]
    persistence = result["persistence"]
    assert persistence["both_claim_active_and_backup100"] is True
    assert persistence["native_exit_codes_and_progress_logs"] == "MISSING"
    assert persistence["script_saved_echo_is_exit_status_proof"] is False
    assert persistence["cold_boot_and_content_readback_proven"] is False
    assert persistence["ap_cfgmtd_in_referenced_boost_script"] is False


@pytest.mark.parametrize("change", ("unknown_schema", "boolean_rf", "changed_summary", "extra_claim"))
def test_pbe_receipt_unknown_or_drifted_claims_are_rejected_without_echo(pbe_receipt, change):
    sentinel = "SYNTHETIC_PRIVACY_SENTINEL"
    if change == "unknown_schema":
        pbe_receipt = {"unknown": sentinel}
    elif change == "boolean_rf":
        pbe_receipt["ota_rf_observations"]["after_boost"]["ap_txpower_dbm"] = True
    elif change == "changed_summary":
        pbe_receipt["verified_ota_benchmarks"]["stage53a_champion_r4"]["aggregate_goodput_mbps"] += 1
    else:
        pbe_receipt[sentinel] = sentinel
    with pytest.raises(ValueError, match="PINNED_PBE_RECEIPT_DRIFT") as caught:
        verifier.audit_pbe_receipt(pbe_receipt)
    assert sentinel not in str(caught.value)


def test_missing_requested_receipt_stays_missing_despite_backups_and_other_sources(source_root):
    (source_root / BOOST_RECEIPT).unlink()
    result = verifier.audit_saved_sources(source_root)
    assert result["pbe5ac"]["receipt"]["availability"] == "MISSING"
    assert result["pbe5ac"]["receipt"]["ota_bringup_accepted"] is False
    assert result["pbe5ac"]["receipt_raw_sha256"] is None
    assert result["pbe5ac"]["backups"]["availability"] == "PRESENT"
    assert result["stage52a"]["windows"] == 16


def test_explicit_local_receipt_uses_exact_basename_and_still_requires_pin(source_root):
    alternate = source_root / "alternate" / Path(BOOST_RECEIPT).name
    alternate.parent.mkdir()
    alternate.write_bytes((source_root / BOOST_RECEIPT).read_bytes())
    assert verifier.audit_saved_sources(source_root, pbe_receipt=alternate)["pbe5ac"]["receipt"]["availability"] == "PRESENT"
    wrong = alternate.with_name("substitute.json")
    wrong.write_bytes(alternate.read_bytes())
    with pytest.raises(ValueError, match="EXACT_REQUESTED_RECEIPT_FILENAME_REQUIRED"):
        verifier.audit_saved_sources(source_root, pbe_receipt=wrong)


def test_backups_export_only_pinned_metadata_and_explicit_safe_topology_fields(source_root):
    result = verifier.audit_backups(source_root)
    assert result["availability"] == "PRESENT"
    assert result["restore_proven"] is False and result["native_original_identity_proven"] is False
    assert result["secret_fields_exported"] is False
    allowed = {"radio.1.chanbw", "radio.1.mode", "radio.1.txpower", "wireless.1.ssid", "wireless.1.wds.status"}
    allowed.update(f"netconf.{n}.{key}" for n in range(1, 10) for key in ("devname", "ip", "netmask"))
    assert len(result["files"]) == 2
    sizes = {"pbe_8773_ptp_guarida_ap_system.cfg": 5731, "pbe_8a01_ptp_alma_sta_system.cfg": 5898}
    for entry in result["files"]:
        # Check closed keys before inspecting values; failure output must never echo cfg text.
        if set(entry) != {"name", "availability", "bytes", "sha256", "safe_fields", "local_integrity_verified"}:
            pytest.fail("Backup export contains an unexpected metadata field")
        if not set(entry["safe_fields"]).issubset(allowed):
            pytest.fail("Backup export contains an unapproved configuration key")
        assert entry["bytes"] == sizes[entry["name"]]
        assert entry["sha256"] == INPUT_PINS[BACKUP_DIR + "/" + entry["name"]]
        assert entry["local_integrity_verified"] is True


def test_missing_backup_directory_has_no_restore_or_identity_proof(tmp_path):
    result = verifier.audit_backups(tmp_path)
    assert result["availability"] == "MISSING"
    assert result["files"] == [] and result["restore_proven"] is False
    assert result["native_original_identity_proven"] is False


@pytest.mark.parametrize("name", ("pbe_8773_ptp_guarida_ap_system.cfg", "pbe_8a01_ptp_alma_sta_system.cfg"))
def test_one_missing_backup_remains_incomplete(source_root, name):
    (source_root / BACKUP_DIR / name).unlink()
    result = verifier.audit_backups(source_root)
    assert result["availability"] == "INCOMPLETE"
    assert sum(x["local_integrity_verified"] for x in result["files"]) == 1
    assert result["restore_proven"] is False


@pytest.mark.parametrize("name", ("pbe_8773_ptp_guarida_ap_system.cfg", "pbe_8a01_ptp_alma_sta_system.cfg"))
def test_changed_backup_bytes_fail_before_any_raw_config_export(source_root, name):
    path = source_root / BACKUP_DIR / name
    path.write_bytes(path.read_bytes() + b"\nSYNTHETIC_PRIVACY_SENTINEL=x\n")
    with pytest.raises(ValueError, match="PINNED_BACKUP_BYTES_DRIFT") as caught:
        verifier.audit_backups(source_root)
    assert "SYNTHETIC_PRIVACY_SENTINEL" not in str(caught.value)


@pytest.mark.parametrize("bad_id", ([], {}))
def test_source_contract_unhashable_stage51_round_id_is_structural_value_error(stage51, stage52, bad_id):
    stage51["rounds"][0]["round_id"] = bad_id
    with pytest.raises(ValueError):
        verifier.source_contract(stage51, stage52, (ROOT / REPORT_51).read_bytes().decode(),
                                 (ROOT / REPORT_52).read_bytes().decode())


def test_atomic_export_roundtrip_and_managed_refresh(verification, tmp_path):
    output = tmp_path / "verification.json"
    assert verifier.write_verification(verification, output) == output
    assert json.loads(output.read_text()) == verification
    refreshed = deepcopy(verification)
    refreshed["synthetic_refresh"] = True
    verifier.write_verification(refreshed, output)
    assert json.loads(output.read_text())["synthetic_refresh"] is True
    assert not list(tmp_path.glob(".stage47b-*.tmp"))


@pytest.mark.parametrize("relative", (SOURCE_51, SOURCE_52, BOOST_RECEIPT))
def test_export_refuses_protected_input_overwrite(verification, source_root, relative):
    output = source_root / relative
    before = hashlib.sha256(output.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="SOURCE_OVERWRITE_REJECTED"):
        verifier.write_verification(verification, output, protected_paths=(output,))
    assert hashlib.sha256(output.read_bytes()).hexdigest() == before


def test_export_refuses_creating_verification_at_missing_receipt_input_path(source_root):
    missing_input = source_root / BOOST_RECEIPT
    missing_input.unlink()
    verification = verifier.audit_saved_sources(source_root)
    assert verification["pbe5ac"]["receipt"]["availability"] == "MISSING"
    before = set(missing_input.parent.iterdir())
    with pytest.raises(ValueError, match="SOURCE_OVERWRITE_REJECTED"):
        verifier.write_verification(verification, missing_input, protected_paths=(missing_input,))
    assert set(missing_input.parent.iterdir()) == before
    assert not missing_input.exists()


@pytest.mark.parametrize("content", ({"unowned": True}, {"task_id": verifier.TASK_ID, "verification_version": True}))
def test_export_refuses_existing_unowned_json(verification, tmp_path, content):
    output = tmp_path / "unowned.json"
    output.write_text(json.dumps(content))
    before = output.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_verification(verification, output)
    assert output.read_bytes() == before


@pytest.mark.parametrize("field,value", (("task_id", "OTHER"), ("verification_version", True), ("verification_version", 2)))
def test_export_rejects_unmanaged_verification_before_writing(verification, tmp_path, field, value):
    verification[field] = value
    output = tmp_path / "verification.json"
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError):
        verifier.write_verification(verification, output)
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("name", ("output.txt", "bad name.json", "NUL.json", "CON.json", "COM1.json", "LPT9.json"))
def test_export_requires_literal_nondevice_json_name_and_preserves_directory(verification, tmp_path, name):
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError):
        verifier.write_verification(verification, tmp_path / name)
    assert set(tmp_path.iterdir()) == before


@pytest.mark.parametrize("path", ("//example.invalid/share/audit.json", "https://example.invalid/audit.json",
                                  "file:///tmp/audit.json", "C:audit.json", "\\\\?\\C:\\audit.json", "bad\0.json"))
def test_export_rejects_network_uri_device_and_nul_paths_without_access(verification, path):
    with pytest.raises(ValueError):
        verifier.write_verification(verification, path)


def test_optional_local_symlink_output_is_rejected_without_modifying_target(verification, tmp_path):
    target = tmp_path / "target.json"
    target.write_text(json.dumps(verification))
    link = tmp_path / "link.json"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"Local symlink creation unavailable: {error}")
    before = target.read_bytes()
    with pytest.raises(ValueError):
        verifier.write_verification(verification, link)
    assert target.read_bytes() == before


@pytest.mark.parametrize("bad", (float("nan"), float("inf"), {1, 2}))
def test_nonfinite_or_nonjson_export_preserves_managed_file_and_leaves_no_temp(verification, tmp_path, bad):
    output = tmp_path / "verification.json"
    verifier.write_verification(verification, output)
    before = output.read_bytes()
    verification["bad_value"] = bad
    with pytest.raises(ValueError, match="FINITE_VERIFICATION_JSON_REQUIRED"):
        verifier.write_verification(verification, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage47b-*.tmp"))


def test_failed_replace_preserves_previous_file_and_cleans_temporary(verification, tmp_path, monkeypatch):
    output = tmp_path / "verification.json"
    verifier.write_verification(verification, output)
    before = output.read_bytes()

    def fail_replace(_source, _target):
        raise OSError("Synthetic local replace failure")

    monkeypatch.setattr(verifier.os, "replace", fail_replace)
    with pytest.raises(OSError, match="Synthetic local replace failure"):
        verifier.write_verification(verification, output)
    assert output.read_bytes() == before
    assert not list(tmp_path.glob(".stage47b-*.tmp"))


CLI = ROOT / "tools/verify/verify_stage52a_and_pbe5ac_ptp_ota.py"


def _run_cli(source_root, *arguments):
    return subprocess.run([sys.executable, str(CLI), "--root", str(source_root), *map(str, arguments)],
                          cwd=ROOT, capture_output=True, text=True, timeout=20, check=False)


@pytest.mark.parametrize("strict,expected_exit", ((False, 0), (True, 1)))
def test_cli_default_and_strict_modes_export_qualified_local_verification(source_root, strict, expected_exit):
    output = source_root / "cli-verification.json"
    arguments = ["--output", output]
    if strict:
        arguments.append("--strict")
    completed = _run_cli(source_root, *arguments)
    assert completed.returncode == expected_exit, completed.stdout + completed.stderr
    status = json.loads(completed.stdout)
    assert status["status"] == "COMPLETE_WITH_QUALIFICATIONS"
    assert status["sector_windows"] == 40
    assert status["pbe_receipt"] == "PRESENT"
    assert status["native_acceptance"] is False
    exported = json.loads(output.read_text())
    assert exported["stage52a"]["native_acceptance"] is False
    assert exported["pbe5ac"]["physical_path_route_isolation_and_coldboot_accepted"] is False


def test_cli_missing_receipt_exports_missing_without_substitution(source_root):
    (source_root / BOOST_RECEIPT).unlink()
    output = source_root / "missing-receipt.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 0
    assert json.loads(completed.stdout)["pbe_receipt"] == "MISSING"
    assert json.loads(output.read_text())["pbe5ac"]["receipt"]["ota_bringup_accepted"] is False


def test_cli_cannot_create_verification_at_the_missing_receipt_input_path(source_root):
    missing_input = source_root / BOOST_RECEIPT
    missing_input.unlink()
    before = set(missing_input.parent.iterdir())
    completed = _run_cli(source_root, "--output", missing_input)
    assert completed.returncode == 2
    status = json.loads(completed.stdout)
    assert status["status"] == "ERROR"
    assert status["native_dispatch_allowed"] is False
    assert "SOURCE_OVERWRITE_REJECTED" in status["error"]
    assert set(missing_input.parent.iterdir()) == before
    assert not missing_input.exists()


def test_cli_rejects_dotdot_alias_of_missing_receipt_without_creating_output_or_temp(source_root):
    missing_input = source_root / BOOST_RECEIPT
    missing_input.unlink()
    aliased_output = source_root / "docs" / ".." / BOOST_RECEIPT
    assert ".." in aliased_output.parts
    before = set(source_root.rglob("*"))
    completed = _run_cli(source_root, "--output", aliased_output)
    assert completed.returncode == 2
    status = json.loads(completed.stdout)
    assert status["status"] == "ERROR"
    assert status["native_dispatch_allowed"] is False
    assert "SOURCE_OVERWRITE_REJECTED" in status["error"]
    assert not missing_input.exists() and not aliased_output.exists()
    assert not list(source_root.rglob(".stage47b-*.tmp"))
    assert set(source_root.rglob("*")) == before


@pytest.mark.parametrize("relative", (SOURCE_51, SOURCE_52, BOOST_RECEIPT))
def test_cli_refuses_source_or_receipt_overwrite_without_touching_input(source_root, relative):
    source = source_root / relative
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    completed = _run_cli(source_root, "--output", source)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("bad_id", ([], {}))
def test_cli_malformed_stage51_round_id_is_json_error_exit2_without_export(source_root, bad_id):
    source = source_root / SOURCE_51
    document = json.loads(source.read_text(encoding="utf-8-sig"))
    document["rounds"][0]["round_id"] = bad_id
    source.write_text(json.dumps(document))
    output = source_root / "invalid-verification.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert json.loads(completed.stdout)["native_dispatch_allowed"] is False
    assert "Traceback" not in completed.stderr
    assert not output.exists()


def test_cli_unknown_receipt_is_error_without_exporting_untrusted_body(source_root):
    sentinel = "SYNTHETIC_PRIVACY_SENTINEL"
    (source_root / BOOST_RECEIPT).write_text(json.dumps({"unknown": sentinel}))
    output = source_root / "unknown-receipt.json"
    completed = _run_cli(source_root, "--output", output)
    assert completed.returncode == 2
    assert json.loads(completed.stdout)["status"] == "ERROR"
    assert sentinel not in completed.stdout + completed.stderr
    assert not output.exists()


@pytest.mark.parametrize("relative", ("docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"))
def test_current_docs_stay_compact_with_single_first_line_doc_head(relative):
    lines = (ROOT / relative).read_text(encoding="utf-8-sig").splitlines()
    assert len(lines) < 250
    assert lines[0].startswith("<!-- doc-head:")
    assert sum("<!-- doc-head:" in line for line in lines) == 1
    assert sum("<!-- /doc-head -->" in line for line in lines) == 1


def test_verifier_ast_has_only_local_pure_dependencies_and_no_native_dispatch():
    tree = ast.parse(CLI.read_text(encoding="utf-8-sig"))
    allowed = {"__future__", "argparse", "hashlib", "json", "math", "os", "pathlib", "re", "sys", "tempfile",
               "controller.stage42a_netdev_txq_and_airos6_verifier",
               "controller.stage46a_champion_v16_tx_bias_and_bql_verifier",
               "controller.stage51a_v17_and_stage49b_ltu_verifier"}
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "__import__", "compile"}
            elif isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"system", "popen", "Popen", "run", "check_call", "check_output", "connect", "urlopen"}
    assert imports.issubset(allowed)


