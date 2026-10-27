"""Offline Stage12 PtP evidence parser. No acquisition, image selection or flash.

CLI (all inputs are local files; JSON output to stdout)::
    python -B tools/bench/stage12_ptp_powerbeam_harness.py detect board.info
    python -B tools/bench/stage12_ptp_powerbeam_harness.py parse --iperf run.json --latency ping.txt
    python -B tools/bench/stage12_ptp_powerbeam_harness.py compare manifest.json

Comparison manifest schema ``stage12-ptp-comparison-v1`` has ``trials``. Each trial:
  mode: one of MODES; repetition: positive paired integer; order: unique positive integer;
  iperf, latency: relative local paths; mode_evidence: {path, sha256};
  metadata: {scenario_id, topology, rf: {frequency_mhz, width_mhz, country,
             tx_power_dbm: {a, b}}, peers: {a, b: {identity, sysid}},
             builds: {a, b: {os: airos|openwrt, version, sha256}},
             load: {protocol: TCP|UDP, direction: a_to_b|b_to_a, duration_s,
                    parallel_streams, latency_context: loaded|idle,
                    udp_target_bps (UDP only)}}.
Optional functional_checks {wds,vlan,ipv6_nd,uisp: unknown|observed_pass|observed_fail}
are author-reported coverage, not automatic qualification. A comparison covers ONE
protocol/direction/context; it does not imply the other TCP/UDP or reverse tests.

Mode evidence is a saved JSON observation, not the scenario label:
  {observed: {ptp: true, airmax_tdma: bool, csma_ca: bool},
   raw_sources: [{path, sha256}, ...]}.
The normalized observation's vendor interpretation remains the evidence author's
responsibility. Hashes prove binding, not that an observation was made on hardware.
For OpenWrt, fouraddr_evidence: {a: {path, sha256}, b: ...} must contain actual
saved iw output with a whole ``4addr: on`` line; builds must be exactly 24.10.4.

iperf3 receiver summaries only: TCP end.sum_received; UDP sum_received or
end.sum with sender=false. Units are bits/s (output also decimal Mbit/s), seconds,
and ms. Latency is ping text or {unit: "ms", samples: [...], transmitted?, received?}.
``time<...`` is censored and rejected rather than invented as a point sample.

Comparable requires all three modes, >=3 paired repetitions, >=2 RTT samples per
trial, matching RF/topology/peers/offered load, stock builds identical across stock
modes, and measured durations within 2% of the declared duration. Missing evidence
yields INCONCLUSIVE, never a rescued result. Percentiles use linear interpolation;
deltas are descriptive means, no significance, performance gain or causal claim.
The proposed two-PowerBeam bench remains deferred: family detection does not
qualify its model. Exit codes: 0 parsed/comparable, 1 inconclusive, 2 invalid input.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
from typing import Any


MODES = ("stock_airmax_tdma_ptp", "stock_hybrid_csma_ca_ptp",
         "openwrt_24_10_4_4addr_wds_ptp")
FAMILIES = {0xE7F7: "WA", 0xE7F9: "WA", 0xE7E8: "XC"}
HEX64 = re.compile(r"[0-9a-fA-F]{64}\Z")


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def number(value: Any, name: str, minimum: float = 0) -> float:
    require(not isinstance(value, bool) and isinstance(value, (int, float)), name)
    try:
        result = float(value)
    except OverflowError:
        raise ValueError(name) from None
    require(math.isfinite(result) and result >= minimum, name)
    return result


def positive_int(value: Any, name: str) -> int:
    require(type(value) is int and value > 0, name)
    return value


def strict_json(text: str) -> Any:
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_JSON")))


def board_id(value: Any) -> int:
    if type(value) is int:
        result = value
    else:
        require(isinstance(value, str), "MALFORMED_BOARD_ID")
        text = value.strip()
        require(bool(re.fullmatch(r"(?:0[xX][0-9a-fA-F]+|[0-9]+|[0-9a-fA-F]*[a-fA-F][0-9a-fA-F]*)", text)),
                "MALFORMED_BOARD_ID")
        result = int(text, 16 if text.lower().startswith("0x") or re.search("[a-fA-F]", text) else 10)
    require(0 < result <= 0xFFFF, "MALFORMED_BOARD_ID")
    return result


def detect_board(data: Any) -> dict:
    """Strict identity -> family only; never deduce PowerBeam or an image."""
    entries = []
    if isinstance(data, str):
        text = data.strip()
        if text.startswith(("{", "[")):
            return detect_board(strict_json(text))
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            match = re.fullmatch(r"\s*([\w.]+)\s*[:=]\s*(.*?)\s*", line)
            require(match is not None, "MALFORMED_BOARD_LINE")
            entries.append((match[1].lower(), match[2]))
    else:
        require(isinstance(data, dict), "BOARD_OBJECT_REQUIRED")
        for key, value in data.items():
            require(isinstance(key, str), "BOARD_KEY_MUST_BE_STRING")
            key = key.strip().lower()
            if key == "board" and isinstance(value, dict):
                require(all(isinstance(k, str) for k in value), "BOARD_KEY_MUST_BE_STRING")
                entries.extend(("board." + k.strip().lower(), v) for k, v in value.items())
            else:
                entries.append((key, value))
    ids = [board_id(v) for k, v in entries if k in ("sysid", "board.sysid", "board_id")]
    require(bool(ids), "MISSING_BOARD_ID")
    require(len(set(ids)) == 1, "CONFLICTING_BOARD_ID")
    require(ids[0] in FAMILIES, "UNKNOWN_BOARD_ID")
    family = FAMILIES[ids[0]]
    for key, value in entries:
        if key in ("family", "board.family", "firmware_family"):
            require(isinstance(value, str) and value.strip().upper() == family,
                    "CONFLICTING_FIRMWARE_FAMILY")
        if key in ("version", "firmware_version", "board.version") and isinstance(value, str):
            prefix = re.match(r"\s*(WA|XC)(?:\.|\s|$)", value, re.I)
            require(not prefix or prefix[1].upper() == family, "CONFLICTING_FIRMWARE_FAMILY")
    models = [v.strip() for k, v in entries if k in ("model", "board.model", "board.name")
              and isinstance(v, str) and v.strip()]
    known = {0xE7E8: "PS-5AC / PrismStation (held XC table)",
             0xE7F9: "LiteBeam (historical evidence; revision unqualified)"}.get(ids[0])
    mismatch = any(re.search(r"power\s*beam|\bpbe[-\s]", m, re.I) for m in models) and known is not None
    return {"status": "FAMILY_ONLY_MODEL_UNQUALIFIED", "sysid": f"0x{ids[0]:04x}",
            "family": family, "model_claims": models, "known_model_hint": known,
            "model_mismatch": bool(mismatch), "powerbeam_qualified": False,
            "image_auto_selection_allowed": False, "flash_allowed": False}


def percentile(samples: list[float], q: float) -> float:
    ordered = sorted(samples)
    position = (len(ordered) - 1) * q
    left = int(position)
    right = min(left + 1, len(ordered) - 1)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


def parse_iperf3(data: dict) -> dict:
    require(isinstance(data, dict) and not data.get("error"), "IPERF_ERROR_OR_OBJECT")
    start = data.get("start")
    require(isinstance(start, dict), "IPERF_START_OBJECT")
    test_start = start.get("test_start")
    require(isinstance(test_start, dict), "IPERF_TEST_START_OBJECT")
    bidirectional = test_start.get("bidirectional", False)
    require(type(bidirectional) in (bool, int) and bidirectional == 0,
            "BIDIRECTIONAL_SUMMARIES_UNSUPPORTED")
    protocol = test_start.get("protocol")
    require(protocol in ("TCP", "UDP"), "IPERF_PROTOCOL")
    end = data.get("end", {})
    require(isinstance(end, dict), "IPERF_END_OBJECT")
    summary = end.get("sum_received")
    if summary is None and protocol == "UDP":
        summary = end.get("sum")
        require(isinstance(summary, dict) and summary.get("sender") is False,
                "UDP_RECEIVER_SUMMARY_REQUIRED")
    require(isinstance(summary, dict), "RECEIVER_SUMMARY_REQUIRED")
    sender = summary.get("sender")
    require(sender is None or sender is False, "SENDER_IS_NOT_GOODPUT")
    bps = number(summary.get("bits_per_second"), "IPERF_BPS")
    seconds = number(summary.get("seconds"), "IPERF_SECONDS")
    require(seconds > 0, "IPERF_SECONDS")
    loss = jitter = None
    if protocol == "UDP":
        if "jitter_ms" in summary:
            jitter = number(summary["jitter_ms"], "UDP_JITTER")
        if "lost_packets" in summary or "packets" in summary:
            lost, packets = summary.get("lost_packets"), summary.get("packets")
            require(type(lost) is int and type(packets) is int and 0 <= lost <= packets,
                    "UDP_PACKET_COUNTS")
            loss = 100 * lost / packets if packets else None
        if "lost_percent" in summary:
            reported = number(summary["lost_percent"], "UDP_LOSS")
            require(reported <= 100 and (loss is None or abs(reported - loss) <= 0.01), "UDP_LOSS")
            loss = reported
    return {"protocol": protocol, "receiver_goodput_bps": bps, "receiver_goodput_mbps": bps / 1e6,
            "duration_s": seconds, "loss_percent": loss, "jitter_ms": jitter}


def parse_latency(data: Any) -> dict:
    if isinstance(data, str) and data.lstrip().startswith("{"):
        return parse_latency(strict_json(data))
    tx = rx = None
    if isinstance(data, dict):
        require(data.get("unit") == "ms", "LATENCY_UNIT_MUST_BE_MS")
        samples = data.get("samples")
        tx, rx = data.get("transmitted"), data.get("received")
    else:
        require(isinstance(data, str), "LATENCY_INPUT")
        require(not re.search(r"time\s*<", data), "CENSORED_LATENCY")
        samples = []
        for line in data.splitlines():
            if re.search(r"\btime\s*=", line):
                match = re.search(r"\btime\s*=\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*ms\b", line)
                require(match is not None, "MALFORMED_PING_LATENCY_OR_UNIT")
                samples.append(float(match[1]))
        counts = re.findall(r"(\d+) packets transmitted,\s*(\d+) (?:packets )?received", data)
        require(len(counts) <= 1, "MULTIPLE_PING_SUMMARIES")
        if counts:
            tx, rx = map(int, counts[0])
    require(isinstance(samples, list) and bool(samples), "LATENCY_SAMPLES_REQUIRED")
    samples = [number(x, "LATENCY_SAMPLE") for x in samples]
    loss = None
    if tx is not None or rx is not None:
        require(type(tx) is int and type(rx) is int and 0 <= rx <= tx and tx > 0,
                "PING_PACKET_COUNTS")
        require(rx == len(samples), "PING_SAMPLE_COUNT_MISMATCH")
        loss = (tx - rx) / tx * 100
    return {"unit": "ms", "sample_count": len(samples), "p50_ms": percentile(samples, .5),
            "p95_ms": percentile(samples, .95), "p99_ms": percentile(samples, .99),
            "loss_percent": loss}


def local_file(base: Path, name: Any) -> Path:
    require(isinstance(name, str) and bool(name) and not re.match(r"^(?:[a-zA-Z]+://|[/\\]{2})", name),
            "LOCAL_PATH_REQUIRED")
    path = Path(name)
    path = path if path.is_absolute() else base / path
    require(not any(p.is_symlink() for p in (path, *path.parents)), "SYMLINK_INPUT_REFUSED")
    require(path.is_file() and path.stat().st_size <= 16 * 1024 * 1024, "MISSING_OR_OVERSIZE_LOCAL_FILE")
    return path


def bound_file(base: Path, reference: dict) -> Path:
    require(isinstance(reference, dict) and isinstance(reference.get("sha256"), str)
            and HEX64.fullmatch(reference["sha256"]) is not None, "EVIDENCE_SHA256_REQUIRED")
    path = local_file(base, reference.get("path"))
    require(hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"].lower(), "EVIDENCE_HASH_MISMATCH")
    return path


def validate_metadata(trial: dict, base: Path) -> dict:
    mode, meta = trial["mode"], trial["metadata"]
    require(isinstance(meta, dict), "METADATA_REQUIRED")
    for key in ("scenario_id", "topology"):
        require(isinstance(meta.get(key), str) and bool(meta[key].strip()), "MISSING_" + key.upper())
    rf, peers, builds, load = (meta[k] for k in ("rf", "peers", "builds", "load"))
    require(all(isinstance(v, dict) for v in (rf, peers, builds, load)), "METADATA_NESTED_OBJECTS")
    require(number(rf["frequency_mhz"], "RF_FREQUENCY") > 0, "RF_FREQUENCY")
    require(number(rf["width_mhz"], "RF_WIDTH") > 0, "RF_WIDTH")
    require(isinstance(rf["country"], str) and re.fullmatch(r"[A-Z]{2}", rf["country"]) is not None, "RF_COUNTRY")
    require(isinstance(rf["tx_power_dbm"], dict)
            and set(peers) == set(builds) == set(rf["tx_power_dbm"]) == {"a", "b"}, "EXACT_TWO_PEERS_REQUIRED")
    identities = []
    for label in ("a", "b"):
        require(isinstance(peers[label], dict) and isinstance(builds[label], dict), "PEER_BUILD_OBJECTS")
        number(rf["tx_power_dbm"][label], "RF_POWER", -100)
        require(isinstance(peers[label]["identity"], str) and bool(peers[label]["identity"].strip()), "PEER_IDENTITY")
        identities.append(peers[label]["identity"])
        detect_board({"sysid": peers[label]["sysid"]})
        build = builds[label]
        require(isinstance(build["version"], str) and bool(build["version"].strip())
                and isinstance(build["sha256"], str) and HEX64.fullmatch(build["sha256"]) is not None, "BUILD_REQUIRED")
        expected_os = "openwrt" if mode == MODES[2] else "airos"
        require(build["os"] == expected_os, "WRONG_BUILD_OS")
        if expected_os == "openwrt":
            require(build["version"] == "24.10.4", "WRONG_OPENWRT_VERSION")
    require(identities[0] != identities[1], "DUPLICATE_PEER_IDENTITY")
    require(load["protocol"] in ("TCP", "UDP") and load["direction"] in ("a_to_b", "b_to_a"), "LOAD_PROTOCOL_DIRECTION")
    require(load["latency_context"] in ("loaded", "idle"), "LATENCY_CONTEXT_REQUIRED")
    require(number(load["duration_s"], "LOAD_DURATION") > 0, "LOAD_DURATION")
    positive_int(load["parallel_streams"], "LOAD_STREAMS")
    if load["protocol"] == "UDP":
        require(number(load["udp_target_bps"], "UDP_OFFERED_RATE") > 0, "UDP_OFFERED_RATE")
    proof_path = bound_file(base, trial["mode_evidence"])
    proof = strict_json(proof_path.read_text(encoding="utf-8"))
    require(isinstance(proof, dict) and isinstance(proof.get("observed"), dict), "MODE_OBSERVATION_OBJECT")
    observed = proof["observed"]
    expected = {"ptp": True, "airmax_tdma": mode == MODES[0], "csma_ca": mode != MODES[0]}
    require(all(observed.get(k) is value for k, value in expected.items()), "MODE_NOT_PROVEN")
    require(isinstance(proof.get("raw_sources"), list) and bool(proof["raw_sources"]), "RAW_MODE_PROVENANCE_REQUIRED")
    for source in proof["raw_sources"]:
        require(bound_file(proof_path.parent, source).stat().st_size > 0, "EMPTY_MODE_SOURCE")
    if mode == MODES[2]:
        fouraddr = trial["fouraddr_evidence"]
        require(isinstance(fouraddr, dict) and set(fouraddr) == {"a", "b"}, "BOTH_FOURADDR_PROOFS_REQUIRED")
        for label in ("a", "b"):
            text = bound_file(base, fouraddr[label]).read_text(encoding="utf-8")
            require(re.search(r"(?m)^\s*4addr:\s*on\s*$", text) is not None, "ACTUAL_FOURADDR_ON_REQUIRED")
    signature = {k: meta[k] for k in ("scenario_id", "topology", "rf", "load")}
    signature["peers"] = {label: {"identity": peers[label]["identity"],
                                 "sysid": f"0x{board_id(peers[label]['sysid']):04x}"}
                          for label in ("a", "b")}
    return signature


def compare_manifest(manifest: dict, base: Path) -> dict:
    reasons, parsed, signatures, keys, orders = [], [], [], set(), set()
    require(isinstance(manifest, dict) and manifest.get("schema") == "stage12-ptp-comparison-v1", "MANIFEST_SCHEMA")
    require(isinstance(manifest.get("trials"), list), "TRIALS_REQUIRED")
    for index, trial in enumerate(manifest["trials"]):
        try:
            require(isinstance(trial, dict), "TRIAL_OBJECT_REQUIRED")
            require(trial["mode"] in MODES, "UNKNOWN_MODE")
            rep = positive_int(trial["repetition"], "REPETITION_REQUIRED")
            order = positive_int(trial["order"], "TREATMENT_ORDER_REQUIRED")
            key = (trial["mode"], rep)
            require(key not in keys and order not in orders, "DUPLICATE_REPETITION_OR_ORDER")
            keys.add(key)
            orders.add(order)
            signature = validate_metadata(trial, base)
            iperf = parse_iperf3(strict_json(local_file(base, trial["iperf"]).read_text(encoding="utf-8")))
            latency = parse_latency(local_file(base, trial["latency"]).read_text(encoding="utf-8"))
            require(iperf["protocol"] == trial["metadata"]["load"]["protocol"], "MEASURED_PROTOCOL_MISMATCH")
            duration = trial["metadata"]["load"]["duration_s"]
            require(abs(iperf["duration_s"] - duration) <= duration * .02, "MEASURED_DURATION_MISMATCH")
            require(latency["sample_count"] >= 2, "SINGLE_LATENCY_SAMPLE")
            functional = trial["metadata"].get("functional_checks", {})
            require(isinstance(functional, dict), "FUNCTIONAL_CHECKS_OBJECT")
            checks = {name: functional.get(name, "unknown")
                      for name in ("wds", "vlan", "ipv6_nd", "uisp")}
            require(all(value in ("unknown", "observed_pass", "observed_fail") for value in checks.values()),
                    "FUNCTIONAL_CHECK_STATUS")
            signatures.append(signature)
            parsed.append({"mode": key[0], "repetition": rep, "order": order,
                           "iperf": iperf, "latency": latency, "builds": trial["metadata"]["builds"],
                           "functional_checks_author_reported": checks})
        except (KeyError, TypeError, ValueError, OSError) as exc:
            reasons.append({"trial_index": index, "reason": str(exc)})
    if signatures and any(s != signatures[0] for s in signatures[1:]):
        reasons.append({"reason": "UNMATCHED_RF_TOPOLOGY_PEERS_OR_LOAD"})
    repetitions = [{x["repetition"] for x in parsed if x["mode"] == mode} for mode in MODES]
    if len(repetitions[0]) < 3 or any(x != repetitions[0] for x in repetitions[1:]):
        reasons.append({"reason": "THREE_MODES_REQUIRE_THREE_OR_MORE_PAIRED_REPETITIONS"})
    for mode in MODES:
        builds = [x["builds"] for x in parsed if x["mode"] == mode]
        if builds and any(b != builds[0] for b in builds):
            reasons.append({"reason": "BUILD_CHANGED_WITHIN_MODE", "mode": mode})
    stock = [x["builds"] for x in parsed if x["mode"] in MODES[:2]]
    if stock and any(b != stock[0] for b in stock):
        reasons.append({"reason": "STOCK_BUILDS_DIFFER_BETWEEN_TDMA_AND_HYBRID"})
    means = {mode: statistics.mean(x["iperf"]["receiver_goodput_bps"] for x in parsed if x["mode"] == mode)
             for mode in MODES if any(x["mode"] == mode for x in parsed)}
    baseline = means.get(MODES[0])
    if baseline == 0:
        reasons.append({"reason": "ZERO_TDMA_BASELINE_DELTA_UNDEFINED"})
    comparable = not reasons
    # No comparative delta when even one scenario is incomplete or unmatched.
    deltas = {mode: (value / baseline - 1) * 100 for mode, value in means.items()} if comparable and baseline else None
    if deltas is not None and any(not math.isfinite(value) for value in deltas.values()):
        reasons.append({"reason": "NONFINITE_DERIVED_DELTA"})
        comparable, deltas = False, None
    return {"status": "COMPARABLE_DESCRIPTIVE_ONLY" if comparable else "INCONCLUSIVE",
            "comparable": comparable, "reasons": reasons, "trials": parsed,
            "receiver_goodput_mean_bps": means, "delta_percent_vs_tdma": deltas,
            "paired_repetitions": len(repetitions[0]) if comparable else None,
            "matrix_coverage": signatures[0]["load"] if comparable else None,
            "limits": ["Saved evidence only; hardware provenance and vendor mode semantics require independent review.",
                       "Descriptive samples, no confidence interval, causal gain or live qualification.",
                       "PowerBeam models/images remain unqualified; acquisition and flashing are disabled."]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("detect").add_argument("file")
    metrics = sub.add_parser("parse")
    metrics.add_argument("--iperf", required=True)
    metrics.add_argument("--latency", required=True)
    sub.add_parser("compare").add_argument("file")
    args = parser.parse_args(argv)
    try:
        if args.command == "detect":
            result = detect_board(local_file(Path.cwd(), args.file).read_text(encoding="utf-8"))
        elif args.command == "parse":
            result = {"iperf": parse_iperf3(strict_json(local_file(Path.cwd(), args.iperf).read_text(encoding="utf-8"))),
                      "latency": parse_latency(local_file(Path.cwd(), args.latency).read_text(encoding="utf-8"))}
        else:
            file = local_file(Path.cwd(), args.file)
            result = compare_manifest(strict_json(file.read_text(encoding="utf-8")), file.parent)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if result.get("status") == "INCONCLUSIVE" else 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"status": "INVALID_INPUT", "reason": str(exc)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
