"""Disposable local files only: no services, target calls, real configs or firmware."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SOURCE = Path(__file__).resolve().parents[1] / "tools/bench/stage12_ptp_powerbeam_harness.py"
SPEC = importlib.util.spec_from_file_location("stage12_ptp_harness", SOURCE)
h = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h)


@pytest.mark.parametrize("source,sysid,family", [
    (" BOARD.SYSID = 0xE7F7 \nboard.model=PBE-unknown", 0xE7F7, "WA"),
    ({"board": {"sysid": " e7f9 "}}, 0xE7F9, "WA"),
    ({"sysid": str(0xE7E8)}, 0xE7E8, "XC"),
    ({"BOARD_ID": 0xE7F7, "family": " wa "}, 0xE7F7, "WA"),
    ('{"Board":{"SysId":"0XE7E8"},"version":"XC.v8.7.25"}', 0xE7E8, "XC"),
])
def test_exact_family_identity_formats_never_select_image(source, sysid, family):
    result = h.detect_board(source)
    assert result["family"] == family and result["sysid"] == f"0x{sysid:04x}"
    assert not result["powerbeam_qualified"]
    assert not result["image_auto_selection_allowed"] and not result["flash_allowed"]


@pytest.mark.parametrize("source", [
    {}, {"sysid": True}, {"sysid": 0xE7F7 + .5}, {"sysid": "0xe7f7 garbage"},
    {"sysid": "0x10000"}, {"sysid": "-1"}, {"sysid": "0xe7fd"},
    {"sysid": "0xe7f7", "board.sysid": "0xe7e8"},
    {"sysid": "0xe7f9", "version": "XC.v8.7.25"},
    {"sysid": "0xe7e8", "family": "WA"},
    "sysid=0xe7f7\nsysid=0xe7e8", "sysid=0xe7f7\nbroken line",
    '{"sysid":"0xe7f7","sysid":"0xe7f7"}', "[]",
])
def test_unknown_malformed_or_conflicting_identity_fails_closed(source):
    with pytest.raises(ValueError):
        h.detect_board(source)


def test_model_name_does_not_rebrand_prismstation_or_litebeam_as_powerbeam():
    for sysid in ("0xe7e8", "0xe7f9"):
        result = h.detect_board({"sysid": sysid, "board.model": "PowerBeam 5AC"})
        assert result["model_mismatch"] and not result["powerbeam_qualified"]
    assert "PS-5AC" in h.detect_board({"sysid": "0xe7e8"})["known_model_hint"]


def iperf(protocol="TCP", bps=100_000_000):
    receiver = {"bits_per_second": bps, "seconds": 30, "sender": False}
    if protocol == "UDP":
        receiver.update(jitter_ms=.25, lost_packets=1, packets=100, lost_percent=1)
    return {"start": {"test_start": {"protocol": protocol}},
            "end": {"sum_received": receiver,
                    "sum_sent": {"bits_per_second": bps * 2, "seconds": 30, "sender": True}}}


def test_tcp_uses_receiver_not_sum_of_both_directions_and_units_are_decimal_mbps():
    assert h.parse_iperf3(iperf())["receiver_goodput_mbps"] == 100
    assert h.parse_iperf3(iperf(bps=0))["receiver_goodput_bps"] == 0


@pytest.mark.parametrize("sender", [1, 0, "true", "false"])
def test_receiver_summary_rejects_non_boolean_sender_flags(sender):
    data = iperf()
    data["end"]["sum_received"]["sender"] = sender
    with pytest.raises(ValueError, match="SENDER"):
        h.parse_iperf3(data)


def test_udp_actual_receiver_loss_jitter_and_sum_fallback():
    data = iperf("UDP")
    result = h.parse_iperf3(data)
    assert result["loss_percent"] == 1 and result["jitter_ms"] == .25
    data["end"]["sum"] = data["end"].pop("sum_received")
    assert h.parse_iperf3(data) == result
    data["end"]["sum"]["sender"] = True
    with pytest.raises(ValueError, match="RECEIVER"):
        h.parse_iperf3(data)


@pytest.mark.parametrize("field,value", [("bits_per_second", True), ("bits_per_second", -1),
    ("bits_per_second", float("nan")), ("bits_per_second", float("inf")),
    ("bits_per_second", "100 Mbps"), ("bits_per_second", 10 ** 1000),
    ("seconds", 0), ("seconds", False)])
def test_invalid_metrics_do_not_become_zero_or_valid_measurements(field, value):
    data = iperf()
    data["end"]["sum_received"][field] = value
    with pytest.raises(ValueError):
        h.parse_iperf3(data)


def test_incomplete_sender_only_and_inconsistent_udp_counts_rejected():
    data = iperf()
    del data["end"]["sum_received"]
    with pytest.raises(ValueError, match="RECEIVER"):
        h.parse_iperf3(data)
    data = iperf("UDP")
    data["end"]["sum_received"]["lost_packets"] = 101
    with pytest.raises(ValueError):
        h.parse_iperf3(data)
    data["end"]["sum_received"].update(lost_packets=1, lost_percent=2)
    with pytest.raises(ValueError, match="UDP_LOSS"):
        h.parse_iperf3(data)


@pytest.mark.parametrize("data", [
    {"start": [], "end": {}}, {"start": {"test_start": []}, "end": {}},
    {"start": {"test_start": {"protocol": "TCP"}}, "end": []},
])
def test_malformed_nested_iperf_objects_raise_validation_error_not_attribute_error(data):
    with pytest.raises(ValueError):
        h.parse_iperf3(data)


@pytest.mark.parametrize("key", [1, None, False])
def test_nonstring_identity_keys_fail_as_validation_errors(key):
    with pytest.raises(ValueError, match="KEY_MUST_BE_STRING"):
        h.detect_board({key: "bad", "sysid": "0xe7f7"})
    with pytest.raises(ValueError, match="KEY_MUST_BE_STRING"):
        h.detect_board({"board": {key: "bad", "sysid": "0xe7f7"}})


@pytest.mark.parametrize("value", [True, 1, "true"])
def test_bidirectional_iperf_is_not_misreported_as_one_direction(value):
    data = iperf()
    data["start"]["test_start"]["bidirectional"] = value
    with pytest.raises(ValueError, match="BIDIRECTIONAL"):
        h.parse_iperf3(data)


def test_ping_percentiles_loss_and_ms_json_units():
    text = "\n".join(f"64 bytes seq={i} ttl=64 time={i} ms" for i in range(1, 5))
    text += "\n5 packets transmitted, 4 packets received, 20% packet loss"
    result = h.parse_latency(text)
    assert result["p50_ms"] == 2.5 and result["p95_ms"] == pytest.approx(3.85)
    assert result["p99_ms"] == pytest.approx(3.97) and result["loss_percent"] == 20
    assert h.parse_latency({"unit": "ms", "samples": [0, 1]})["p50_ms"] == .5


@pytest.mark.parametrize("data", [
    "64 bytes time<1 ms", "64 bytes time=-1 ms", "64 bytes time=NaN ms",
    "64 bytes time=1 s", {"unit": "s", "samples": [1, 2]},
    {"unit": "ms", "samples": [True, 1]}, {"unit": "ms", "samples": []},
    {"unit": "ms", "samples": [float("inf"), 1]},
    {"unit": "ms", "samples": [1, 2], "transmitted": 2, "received": 1},
])
def test_censored_malformed_or_wrong_unit_latency_never_invented(data):
    with pytest.raises(ValueError):
        h.parse_latency(data)


def save_json(root, name, data):
    path = root / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return name


def reference(root, name):
    return {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}


@pytest.fixture
def comparison(tmp_path):
    (tmp_path / "native.txt").write_text("Synthetic saved native observation, NOT a hardware result\n", encoding="utf-8")
    for label in ("a", "b"):
        (tmp_path / f"iw-{label}.txt").write_text("Interface test0\n\ttype AP\n\t4addr: on\n", encoding="utf-8")
    trials = []
    for mode_index, mode in enumerate(h.MODES):
        proof = {"observed": {"ptp": True, "airmax_tdma": mode_index == 0, "csma_ca": mode_index != 0},
                 "raw_sources": [reference(tmp_path, "native.txt")]}
        save_json(tmp_path, f"proof-{mode_index}.json", proof)
        for rep in (1, 2, 3):
            name = f"{mode_index}-{rep}"
            save_json(tmp_path, name + "-iperf.json", iperf(bps=(100 + 10 * mode_index) * 1_000_000))
            save_json(tmp_path, name + "-ping.json", {"unit": "ms", "samples": [1, 2, 3, 4]})
            meta = {"scenario_id": "synthetic-indoor-fixed", "topology": "isolated-two-peer-ptp",
                    "rf": {"frequency_mhz": 5180, "width_mhz": 20, "country": "AR", "tx_power_dbm": {"a": 0, "b": 0}},
                    "peers": {"a": {"identity": "test-unit-a", "sysid": "0xe7f7"},
                              "b": {"identity": "test-unit-b", "sysid": "0xe7f9"}},
                    "builds": {label: {"os": "openwrt" if mode_index == 2 else "airos",
                                       "version": "24.10.4" if mode_index == 2 else "WA.v8.7.25",
                                       "sha256": str(mode_index == 2 and 2 or 1) * 64} for label in ("a", "b")},
                    "load": {"protocol": "TCP", "direction": "a_to_b", "duration_s": 30,
                             "parallel_streams": 1, "latency_context": "loaded"}}
            trial = {"mode": mode, "repetition": rep, "order": (rep - 1) * 3 + mode_index + 1,
                     "iperf": name + "-iperf.json", "latency": name + "-ping.json", "metadata": meta,
                     "mode_evidence": reference(tmp_path, f"proof-{mode_index}.json")}
            if mode_index == 2:
                trial["fouraddr_evidence"] = {label: reference(tmp_path, f"iw-{label}.txt") for label in ("a", "b")}
            trials.append(trial)
    return {"schema": "stage12-ptp-comparison-v1", "trials": trials}, tmp_path


def test_three_modes_paired_synthetic_comparison_is_only_descriptive(comparison):
    manifest, root = comparison
    result = h.compare_manifest(manifest, root)
    assert result["status"] == "COMPARABLE_DESCRIPTIVE_ONLY" and result["paired_repetitions"] == 3
    assert result["delta_percent_vs_tdma"][h.MODES[1]] == pytest.approx(10)
    assert result["delta_percent_vs_tdma"][h.MODES[2]] == pytest.approx(20)
    assert len(result["trials"]) == 9
    assert result["matrix_coverage"]["direction"] == "a_to_b"
    assert result["trials"][0]["functional_checks_author_reported"]["ipv6_nd"] == "unknown"


@pytest.mark.parametrize("case,reason", [
    ("single", "PAIRED_REPETITIONS"), ("mode_missing", "PAIRED_REPETITIONS"),
    ("rf", "UNMATCHED_RF"), ("peers", "UNMATCHED_RF"), ("topology", "UNMATCHED_RF"),
    ("direction", "UNMATCHED_RF"), ("idle_latency", "UNMATCHED_RF"),
    ("order", "TREATMENT_ORDER"), ("duplicate", "DUPLICATE_REPETITION"),
    ("version", "WRONG_OPENWRT_VERSION"), ("stock_build", "STOCK_BUILDS_DIFFER"),
    ("wds_missing", "fouraddr_evidence"), ("wds_off", "ACTUAL_FOURADDR_ON"),
    ("mode_proof", "MODE_NOT_PROVEN"), ("tamper", "HASH_MISMATCH"),
    ("single_rtt", "SINGLE_LATENCY_SAMPLE"), ("duration", "MEASURED_DURATION"),
    ("protocol", "MEASURED_PROTOCOL"), ("missing_iperf", "MISSING_OR_OVERSIZE"),
])
def test_incomplete_unmatched_or_unproven_evidence_never_yields_comparative_delta(comparison, case, reason):
    manifest, root = comparison
    first, last = manifest["trials"][0], manifest["trials"][-1]
    if case == "single":
        manifest["trials"] = [t for t in manifest["trials"] if t["repetition"] == 1]
    elif case == "mode_missing":
        manifest["trials"] = manifest["trials"][:6]
    elif case == "rf":
        first["metadata"]["rf"]["width_mhz"] = 40
    elif case == "peers":
        first["metadata"]["peers"]["a"]["identity"] = "another-unit"
    elif case == "topology":
        first["metadata"]["topology"] = "other-position"
    elif case == "direction":
        first["metadata"]["load"]["direction"] = "b_to_a"
    elif case == "idle_latency":
        first["metadata"]["load"]["latency_context"] = "idle"
    elif case == "order":
        del first["order"]
        reason = "order"
    elif case == "duplicate":
        manifest["trials"].append(copy.deepcopy(first))
    elif case == "version":
        last["metadata"]["builds"]["a"]["version"] = "24.10.5"
    elif case == "stock_build":
        manifest["trials"][3]["metadata"]["builds"]["a"]["sha256"] = "a" * 64
    elif case == "wds_missing":
        del last["fouraddr_evidence"]
    elif case == "wds_off":
        (root / "iw-a.txt").write_text("Interface test0\n4addr: off\n", encoding="utf-8")
        for trial in manifest["trials"][6:]:
            trial["fouraddr_evidence"]["a"] = reference(root, "iw-a.txt")
    elif case == "mode_proof":
        save_json(root, "wrong-proof.json", {"observed": {"ptp": True, "airmax_tdma": False, "csma_ca": True},
                                            "raw_sources": [reference(root, "native.txt")]})
        first["mode_evidence"] = reference(root, "wrong-proof.json")
    elif case == "tamper":
        (root / "proof-0.json").write_text("{}", encoding="utf-8")
    elif case == "single_rtt":
        save_json(root, first["latency"], {"unit": "ms", "samples": [1]})
    elif case == "duration":
        data = iperf()
        data["end"]["sum_received"]["seconds"] = 10
        save_json(root, first["iperf"], data)
    elif case == "protocol":
        save_json(root, first["iperf"], iperf("UDP"))
    elif case == "missing_iperf":
        (root / first["iperf"]).unlink()
    result = h.compare_manifest(manifest, root)
    assert result["status"] == "INCONCLUSIVE" and result["delta_percent_vs_tdma"] is None
    assert any(reason in r["reason"] for r in result["reasons"]), result["reasons"]


def test_zero_tdma_is_preserved_without_division_or_fake_gain(comparison):
    manifest, root = comparison
    for trial in manifest["trials"][:3]:
        save_json(root, trial["iperf"], iperf(bps=0))
    result = h.compare_manifest(manifest, root)
    assert not result["comparable"] and result["receiver_goodput_mean_bps"][h.MODES[0]] == 0
    assert result["delta_percent_vs_tdma"] is None


def test_finite_extreme_input_cannot_export_infinite_comparative_gain(comparison):
    manifest, root = comparison
    for trial in manifest["trials"]:
        save_json(root, trial["iperf"], iperf(bps=1e-308 if trial["mode"] == h.MODES[0] else 1e307))
    result = h.compare_manifest(manifest, root)
    assert not result["comparable"] and result["delta_percent_vs_tdma"] is None
    assert any(r["reason"] == "NONFINITE_DERIVED_DELTA" for r in result["reasons"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("case", ["proof_observed", "metadata_rf", "functional", "trial"])
def test_malformed_nested_comparison_is_inconclusive_without_traceback(comparison, case):
    manifest, root = comparison
    if case == "proof_observed":
        save_json(root, "proof-malformed.json", {"observed": [], "raw_sources": []})
        manifest["trials"][0]["mode_evidence"] = reference(root, "proof-malformed.json")
    elif case == "metadata_rf":
        manifest["trials"][0]["metadata"]["rf"] = []
    elif case == "functional":
        manifest["trials"][0]["metadata"]["functional_checks"] = []
    else:
        manifest["trials"][0] = []
    result = h.compare_manifest(manifest, root)
    assert result["status"] == "INCONCLUSIVE" and result["delta_percent_vs_tdma"] is None


def test_cli_malformed_nested_json_returns_invalid_input_no_stacktrace(tmp_path):
    file = tmp_path / "bad-iperf.json"
    save_json(tmp_path, file.name, {"start": [], "end": {}})
    latency = tmp_path / "latency.json"
    save_json(tmp_path, latency.name, {"unit": "ms", "samples": [1, 2]})
    completed = subprocess.run([sys.executable, "-B", str(SOURCE), "parse", "--iperf", str(file),
                                "--latency", str(latency)], capture_output=True, text=True, timeout=10)
    assert completed.returncode == 2 and not completed.stderr
    assert json.loads(completed.stdout)["status"] == "INVALID_INPUT"


def test_udp_and_reverse_are_separate_valid_scenario_not_inferred_from_tcp(comparison):
    manifest, root = comparison
    for trial in manifest["trials"]:
        trial["metadata"]["load"].update(protocol="UDP", direction="b_to_a", udp_target_bps=120_000_000)
        save_json(root, trial["iperf"], iperf("UDP"))
    result = h.compare_manifest(manifest, root)
    assert result["comparable"] and result["matrix_coverage"]["protocol"] == "UDP"
    assert result["trials"][0]["iperf"]["loss_percent"] == 1


def test_family_equivalent_hex_and_decimal_peer_ids_match(comparison):
    manifest, root = comparison
    manifest["trials"][0]["metadata"]["peers"]["a"]["sysid"] = str(0xE7F7)
    assert h.compare_manifest(manifest, root)["comparable"]


@pytest.mark.parametrize("name", ["ssh://target/status", "https://example/status", "//host/share/a", "\\\\host\\share\\a"])
def test_network_inputs_are_refused_before_read(tmp_path, name):
    with pytest.raises(ValueError, match="LOCAL_PATH"):
        h.local_file(tmp_path, name)


def test_cli_local_contract_and_no_target_options(comparison):
    manifest, root = comparison
    file = root / "manifest.json"
    file.write_text(json.dumps(manifest), encoding="utf-8")
    completed = subprocess.run([sys.executable, "-B", str(SOURCE), "compare", str(file)],
                               capture_output=True, text=True, timeout=10)
    assert completed.returncode == 0 and json.loads(completed.stdout)["comparable"]
    manifest["trials"] = manifest["trials"][:1]
    file.write_text(json.dumps(manifest), encoding="utf-8")
    completed = subprocess.run([sys.executable, "-B", str(SOURCE), "compare", str(file)],
                               capture_output=True, text=True, timeout=10)
    assert completed.returncode == 1 and json.loads(completed.stdout)["status"] == "INCONCLUSIVE"
    completed = subprocess.run([sys.executable, "-B", str(SOURCE), "detect", "--hostname", "target"],
                               capture_output=True, text=True, timeout=10)
    assert completed.returncode == 2
