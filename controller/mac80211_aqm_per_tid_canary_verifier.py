"""Stage37B: strict Linux6.6.110 internal AQM/TXQ triple-play verifier.

Offline parsers plus a qualified-adapter canary. No default transport, shell,
traffic generator, station-stat writes, counter resets or device access.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import re
import time
from typing import Callable, Protocol

from controller import iptv_dms_ac_vi_canary_gate as iptv

base = iptv.base
TASK_ID = "T-S37B-CODEX-CHAMPION-V10-MAC80211-AQM-AND-TRIPLE-PLAY-CANARY-VERIFIER"
AQM_PATH = "/sys/kernel/debug/ieee80211/phy0/aqm"
SOURCE = base.ROOT / "artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json"
SOURCE_R2_SHA256 = "b51d0e5e932bc403250e4e3c066451e0b717c04c4fadeadea22a8869d94c1310"
RW_FIELDS = ("fq_memory_limit", "fq_limit", "fq_quantum")
GLOBAL_FIELDS = {"fq_flows_cnt": "R", "fq_backlog": "R", "fq_overlimit": "R",
    "fq_overmemory": "R", "fq_collisions": "R", "fq_memory_usage": "R",
    **{name: "RW" for name in RW_FIELDS}}
TID_AC = {0: 2, 1: 3, 2: 3, 3: 2, 4: 1, 5: 1, 6: 0, 7: 0}
TABLE_COLUMNS = ("tid", "ac", "backlog-bytes", "backlog-packets", "new-flows", "drops",
                 "marks", "overlimit", "collisions", "tx-bytes", "tx-packets", "flags")
COUNTERS = ("new-flows", "drops", "marks", "overlimit", "collisions", "tx-bytes", "tx-packets")
SERVICES = {"iptv": (4, 1, "udp"), "voip": (6, 0, "udp"), "bulk": (0, 2, "tcp")}
LEASE_S, RESTORE_TIMEOUT_S, PROBE_WINDOW_S = 60, 5, 5


def _need(value, code):
    if not value:
        raise ValueError(code)


def _u32(value):
    return iptv._uint(value)


def _positive(value):
    return iptv._uint(value, minimum=1, maximum=2**64 - 1)


def parse_global_aqm(raw: str) -> dict:
    """Exact nine-field R/RW ABI; no directories, defaults or partial parsing.

    Keep raw labels: upstream6.6.110 swaps the arguments backing fq_overlimit and
    fq_overmemory. This parser does not silently reinterpret an installed build.
    """
    _need(type(raw) is str and 0 < len(raw) <= 8192 and "\x00" not in raw, "GLOBAL_AQM_TEXT_REQUIRED")
    _need(raw.endswith("\n"), "GLOBAL_AQM_UNTERMINATED_OR_TRUNCATED")
    lines = [line.split() for line in raw.splitlines() if line.strip()]
    _need(lines and lines.pop(0) == ["access", "name", "value"], "GLOBAL_AQM_HEADER_REQUIRED")
    result = {}
    for row in lines:
        _need(len(row) == 3, "GLOBAL_AQM_ROW_INVALID")
        access, name, value = row
        _need(name in GLOBAL_FIELDS and access == GLOBAL_FIELDS[name] and name not in result,
              "GLOBAL_AQM_ACCESS_NAME_OR_DUPLICATE")
        result[name] = _u32(value)
    _need(set(result) == set(GLOBAL_FIELDS), "GLOBAL_AQM_TRUNCATED_OR_MISSING")
    _need(result["fq_flows_cnt"] > 0, "ALLOCATED_FQ_FLOWS_REQUIRED")
    return {"values": result, "rw": {name: result[name] for name in RW_FIELDS},
            "global_event_label_semantics": "RAW_LABELS_UPSTREAM_6_6_110_ARGUMENT_SWAP_REQUIRES_BUILD_QUALIFICATION"}


def parse_station_aqm(raw: str) -> dict:
    _need(type(raw) is str and 0 < len(raw) <= 32768 and "\x00" not in raw, "STATION_AQM_TEXT_REQUIRED")
    _need(raw.endswith("\n"), "STATION_AQM_UNTERMINATED_OR_TRUNCATED")
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    _need(len(lines) >= 3, "STATION_AQM_TRUNCATED")
    codel = re.fullmatch(r"target ([0-9]+)us interval ([0-9]+)us ecn (yes|no)", lines[0])
    _need(codel and tuple(lines[1].split()) == TABLE_COLUMNS, "STATION_AQM_HEADER_REQUIRED")
    rows = {}
    for line in lines[2:]:
        fields = line.split(maxsplit=11)
        _need(len(fields) == 12, "STATION_AQM_ROW_TRUNCATED")
        numbers = [_u32(v) for v in fields[:11]]
        tid, ac = numbers[:2]
        _need(tid in (*range(8), 16) and tid not in rows and ac == (0 if tid == 16 else TID_AC[tid]),
              "TID_AC_MAPPING_OR_DUPLICATE")
        flags = re.fullmatch(r"0x([0-9a-fA-F]+)\((RUN|STOP)((?: (?:AMPDU|NO-AMSDU|DIRTY))*)\)", fields[11])
        _need(flags and len(set(flags[3].split())) == len(flags[3].split()), "TXQ_FLAGS_INVALID")
        _u32(int(flags[1], 16))
        rows[tid] = {**dict(zip(TABLE_COLUMNS[:11], numbers)), "flags": fields[11]}
    _need(set(range(8)) <= set(rows), "ALL_EIGHT_DATA_TIDS_REQUIRED")
    return {"codel": {"target_us": _u32(codel[1]), "interval_us": _u32(codel[2]), "ecn": codel[3] == "yes"},
            "tids": {tid: rows[tid] for tid in sorted(rows)}}


def split_combined_readback(raw: str) -> tuple[dict, dict]:
    """Explicitly split saved AP aqm+AQL captures; ordinary parsers stay strict."""
    _need(type(raw) is str and len(raw) <= 16384, "COMBINED_READBACK_REQUIRED")
    lines = raw.splitlines()
    starts = [i for i, line in enumerate(lines) if line.split() == ["AC", "AQL", "limit", "low", "AQL", "limit", "high"]]
    _need(len(starts) == 1, "ONE_AQL_BOUNDARY_REQUIRED")
    index = starts[0]
    return parse_global_aqm("\n".join(lines[:index]) + "\n"), iptv.parse_aql_readback("\n".join(lines[index:]))


def _v10_source() -> dict:
    raw = base.bridge._json(base.bridge._read(SOURCE))
    rounds = [r for r in raw.get("rounds", []) if r.get("round_id") == "S36A-R2"]
    _need(len(rounds) == 1 and base.digest(rounds[0]) == SOURCE_R2_SHA256, "V10_R2_SOURCE_DRIFT")
    for phase in ("B1", "B2"):
        getters = rounds[0]["phases"][phase]["getter_readback"]
        ap, aql = split_combined_readback(getters["ap_aqm_and_aql"])
        # Historical JSON used stripped command output; live snapshots must retain EOF newline.
        cpe = parse_global_aqm(getters["loco_aqm"].rstrip("\n") + "\n")
        _need(ap["rw"] == {"fq_quantum": 3028, "fq_memory_limit": 4194304, "fq_limit": 8192}
              and cpe["rw"] == {"fq_quantum": 1514, "fq_memory_limit": 4194304, "fq_limit": 8192}
              and aql["limits"]["BE"] == [1500, 3000] and aql["combined_threshold"] == 5000,
              "V10_SOURCE_CONTRACT_MISMATCH")
    return {"path": str(SOURCE.relative_to(base.ROOT)), "round_id": "S36A-R2", "round_sha256": SOURCE_R2_SHA256,
            "claim_scope": "SOURCE_REPORTED_V10_NO_SAVED_TID6_VOIP_PROOF"}


def build_canary_plan(*, device_id: str, run_id: str, role: str,
                      expected_station_macs: list[str], flows: list[dict]) -> dict:
    device_id, run_id = base.bridge._uuid(device_id), base._identifier(run_id)
    _need(role in ("ap", "cpe"), "EXPLICIT_AP_OR_CPE_ROLE_REQUIRED")
    _need(type(expected_station_macs) is list and 1 <= len(expected_station_macs) <= 256, "STATION_INVENTORY_REQUIRED")
    macs = sorted(base._mac(m) for m in expected_station_macs)
    _need(len(set(macs)) == len(macs), "DUPLICATE_STATION")
    _need(type(flows) is list and 3 <= len(flows) <= 256, "TRIPLE_PLAY_FLOW_INVENTORY_REQUIRED")
    checked, seen = [], set()
    for flow in flows:
        _need(type(flow) is dict and set(flow) == {"flow_id", "service", "station_mac"}, "EXACT_FLOW_SPEC_REQUIRED")
        ident, service = flow["flow_id"], flow["service"]
        _need(type(ident) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", ident) and ident not in seen
              and service in SERVICES, "FLOW_ID_OR_SERVICE_INVALID")
        seen.add(ident)
        mac = base._mac(flow["station_mac"])
        _need(mac in macs, "FLOW_STATION_NOT_IN_INVENTORY")
        checked.append({**flow, "station_mac": mac})
    _need({f["service"] for f in checked} == set(SERVICES), "IPTV_VOIP_AND_BULK_REQUIRED")
    aql = {"VO": [600, 1200], "VI": [1200, 2400], "BE": [1500, 3000] if role == "ap" else [900, 1500], "BK": [500, 1000]}
    plan = {"schema_version": 1, "task_id": TASK_ID, "device_id": device_id, "run_id": run_id,
        "role": role, "expected_station_macs": macs, "flows": sorted(checked, key=lambda f: f["flow_id"]),
        "openwrt_release": "24.10.4", "kernel_release": "6.6.110", "v10_source": _v10_source(),
        "aqm_target": {"fq_quantum": 3028 if role == "ap" else 1514, "fq_memory_limit": 4194304, "fq_limit": 8192},
        "fq_flows_cnt": 4096, "aql_limits": aql, "aql_threshold": 5000 if role == "ap" else 4000,
        "zero_event_policy": "ZERO_DROP_AND_OVERLIMIT_TOTALS_AND_DELTAS_ALL_OBSERVED_TIDS",
        "probe_window_s": PROBE_WINDOW_S, "lease_s": LEASE_S, "restore_scope": "ONLY_THREE_GLOBAL_AQM_RW_PARAMETERS",
        "runtime_dispatch_allowed": False, "physical_acceptance": False}
    plan["plan_sha256"] = base.digest(plan)
    return plan


def validate_plan(plan: dict) -> None:
    _need(type(plan) is dict, "AQM_PLAN_REQUIRED")
    expected = build_canary_plan(device_id=plan.get("device_id"), run_id=plan.get("run_id"),
        role=plan.get("role"), expected_station_macs=plan.get("expected_station_macs"), flows=plan.get("flows"))
    _need(base._json_bytes(plan) == base._json_bytes(expected), "AQM_PLAN_INTEGRITY_FAILED")


def _global_identity(raw: dict, plan: dict, *, now: datetime, max_age_s=10) -> dict:
    _need(type(raw) is dict and raw.get("device_id") == plan["device_id"] and raw.get("run_id") == plan["run_id"]
          and raw.get("role") == plan["role"] and raw.get("openwrt_release") == "24.10.4"
          and raw.get("kernel_release") == "6.6.110" and raw.get("wiphy") == "phy0"
          and raw.get("driver") in ("ath10k", "ath10k_pci") and raw.get("source") == "qualified_debugfs_txq_collector"
          and raw.get("global_aqm_path") == AQM_PATH and raw.get("global_aqm_is_file") is True,
          "EXACT_BUILD_GLOBAL_AQM_FILE_REQUIRED")
    base._fresh(raw.get("observed_at"), now, max_age_s=max_age_s)
    return {"device_id": plan["device_id"], "role": plan["role"],
        "boot_id": base.bridge._uuid(raw.get("boot_id")), "netns_inode": _positive(raw.get("netns_inode")),
        "wiphy_epoch": base._hash(raw.get("wiphy_epoch")), "aqm_inode": _positive(raw.get("aqm_inode")),
        "module_sha256": base._hash(raw.get("module_sha256"))}


def normalize_snapshot(raw: dict, plan: dict, *, now: datetime, max_age_s=10) -> dict:
    identity = _global_identity(raw, plan, now=now, max_age_s=max_age_s)
    global_aqm = parse_global_aqm(raw.get("global_aqm"))
    _need(global_aqm["values"]["fq_flows_cnt"] == plan["fq_flows_cnt"], "ALLOCATED_FLOW_COUNT_MISMATCH")
    aql = iptv.parse_aql_readback(raw.get("aql_txq_limit"))
    threshold = _u32(raw.get("aql_threshold"))
    _need(aql["limits"] == plan["aql_limits"] and threshold == plan["aql_threshold"]
          and (aql["combined_threshold"] is None or aql["combined_threshold"] == threshold), "V10_ROLE_AQL_MISMATCH")
    _need(raw.get("station_inventory_complete") is True and type(raw.get("stations")) is list
          and len(raw["stations"]) == len(plan["expected_station_macs"]), "COMPLETE_STATION_TXQ_INVENTORY_REQUIRED")
    stations = {}
    for station in raw["stations"]:
        _need(type(station) is dict and station.get("associated") is True and station.get("authorized") is True,
              "STATION_HEALTH_REQUIRED")
        path = station.get("path")
        match = re.fullmatch(r"/sys/kernel/debug/ieee80211/phy0/netdev:([A-Za-z0-9_.-]{1,15})/stations/([0-9a-f]{2}(?::[0-9a-f]{2}){5})/aqm", path) if type(path) is str else None
        _need(match and station.get("aqm_is_file") is True, "EXACT_STATION_AQM_PATH_REQUIRED")
        netdev, mac = match.groups()
        _need(mac in plan["expected_station_macs"] and mac not in stations, "AMBIGUOUS_OR_UNKNOWN_STATION_TXQ")
        table = parse_station_aqm(station.get("aqm"))
        station_identity = {"path": path, "netdev": netdev, "mac": mac,
            "ifindex": _positive(station.get("ifindex")), "aqm_inode": _positive(station.get("aqm_inode")),
            "station_epoch": base._hash(station.get("station_epoch"))}
        stations[mac] = {"identity": station_identity, **table}
    return {"identity": identity, "global_aqm": global_aqm, "stations": stations,
        "aql": aql, "aql_threshold": threshold, "capture_seq": _positive(raw.get("capture_seq")),
        "monotonic_ns": _positive(raw.get("monotonic_ns")), "observed_at": base._utc(raw["observed_at"]).isoformat()}


def verify_zero_events(snapshot: dict) -> None:
    _need(snapshot["global_aqm"]["values"]["fq_overlimit"] == 0
          and snapshot["global_aqm"]["values"]["fq_overmemory"] == 0, "GLOBAL_AQM_EVENT_TOTAL_NOT_ZERO")
    for peer in snapshot["stations"].values():
        _need(all(row["drops"] == 0 and row["overlimit"] == 0 for row in peer["tids"].values()),
              "PER_TID_DROP_OR_OVERLIMIT_TOTAL_NOT_ZERO")


def verify_champion(snapshot: dict, plan: dict) -> None:
    _need(snapshot["global_aqm"]["rw"] == plan["aqm_target"], "V10_INTERNAL_AQM_READBACK_MISMATCH")
    verify_zero_events(snapshot)


def _same_epochs(before: dict, after: dict) -> None:
    _need(base._json_bytes(before["identity"]) == base._json_bytes(after["identity"]), "GLOBAL_AQM_DEVICE_EPOCH_CHANGED")
    _need(set(before["stations"]) == set(after["stations"]), "STATION_SET_CHANGED")
    for mac, old in before["stations"].items():
        new = after["stations"][mac]
        _need(base._json_bytes(old["identity"]) == base._json_bytes(new["identity"])
              and old["codel"] == new["codel"] and set(old["tids"]) == set(new["tids"]),
              "STATION_OR_TXQ_COUNTER_EPOCH_CHANGED")


def counter_deltas(before: dict, after: dict) -> dict:
    _same_epochs(before, after)
    _need(after["capture_seq"] > before["capture_seq"] and after["monotonic_ns"] > before["monotonic_ns"]
          and base._utc(after["observed_at"]) > base._utc(before["observed_at"]), "REPLAYED_OR_REORDERED_TXQ_SNAPSHOT")
    deltas = {}
    for mac, old in before["stations"].items():
        deltas[mac] = {}
        for tid, row in old["tids"].items():
            new = after["stations"][mac]["tids"][tid]
            _need(all(new[k] >= row[k] for k in COUNTERS), "COUNTER_RESET_OR_WRAP_NO_DELTA")
            deltas[mac][tid] = {k: new[k] - row[k] for k in COUNTERS}
    return deltas


def verify_triple_play(before_raw: dict, after_raw: dict, witnesses: dict, plan: dict, *, now: datetime) -> dict:
    validate_plan(plan)
    before = normalize_snapshot(before_raw, plan, now=now, max_age_s=LEASE_S)
    after = normalize_snapshot(after_raw, plan, now=now)
    verify_champion(before, plan); verify_champion(after, plan)
    deltas = counter_deltas(before, after)
    elapsed = (after["monotonic_ns"] - before["monotonic_ns"]) / 1e9
    _need(PROBE_WINDOW_S <= elapsed <= LEASE_S - RESTORE_TIMEOUT_S, "BOUNDED_TRIPLE_PLAY_WINDOW_REQUIRED")
    _need(type(witnesses) is dict and witnesses.get("device_id") == plan["device_id"]
          and witnesses.get("run_id") == plan["run_id"] and witnesses.get("plan_sha256") == plan["plan_sha256"]
          and witnesses.get("before_seq") == before["capture_seq"] and type(witnesses.get("before_seq")) is int
          and witnesses.get("after_seq") == after["capture_seq"] and type(witnesses.get("after_seq")) is int,
          "FLOW_TRACE_WINDOW_BINDING_REQUIRED")
    rows = witnesses.get("flows")
    expected = {flow["flow_id"]: flow for flow in plan["flows"]}
    _need(type(rows) is list and len(rows) == len(expected), "ALL_TRIPLE_PLAY_FLOW_WITNESSES_REQUIRED")
    seen, evidence, counted, trace_ids = set(), [], {}, set()
    for row in rows:
        _need(type(row) is dict and type(row.get("flow_id")) is str, "FLOW_WITNESS_REQUIRED")
        ident = row["flow_id"]
        _need(ident in expected and ident not in seen, "UNKNOWN_OR_DUPLICATE_FLOW_WITNESS")
        seen.add(ident); spec = expected[ident]
        mac, service = spec["station_mac"], spec["service"]
        tid, ac, transport = SERVICES[service]
        peer = after["stations"][mac]
        _need(row.get("service") == service and row.get("station_mac") == mac
              and row.get("path") == peer["identity"]["path"]
              and row.get("station_epoch") == peer["identity"]["station_epoch"]
              and row.get("source") == "qualified_txq_flow_trace" and row.get("transport") == transport
              and type(row.get("observed_tid")) is int and row["observed_tid"] == tid
              and type(row.get("observed_ac")) is int and row["observed_ac"] == ac,
              "FLOW_QOS_CLASSIFICATION_NOT_PROVEN")
        trace_id = (mac, tid, base._hash(row.get("evidence_sha256")))
        _need(trace_id not in trace_ids, "DUPLICATE_CLASS_FLOW_EVIDENCE")
        trace_ids.add(trace_id)
        start, end = base._utc(row.get("window_start")), base._utc(row.get("window_end"))
        _need(base._utc(before["observed_at"]) <= start < end <= base._utc(after["observed_at"])
              and (end - start).total_seconds() >= PROBE_WINDOW_S, "FLOW_TRACE_OUTSIDE_MEASURED_WINDOW")
        packets, octets = _positive(row.get("matched_packets")), _positive(row.get("matched_bytes"))
        change = deltas[mac][tid]
        _need(change["tx-packets"] > 0 and change["tx-bytes"] > 0 and change["drops"] == 0
              and change["overlimit"] == 0, "POSITIVE_ZERO_LOSS_TXQ_ACTIVITY_REQUIRED")
        # Qualified flow traces count disjoint packets at this same FQ dequeue boundary.
        totals = counted.setdefault((mac, tid), [0, 0])
        totals[0] += packets; totals[1] += octets
        _need(totals[0] <= change["tx-packets"] and totals[1] <= change["tx-bytes"],
              "FLOW_COUNTS_EXCEED_TXQ_DEQUEUE_DELTA")
        evidence.append({"flow_id": ident, "service": service, "tid": tid, "ac": ac,
            "trace_matched_packets": packets, "trace_matched_bytes": octets,
            "txq_dequeue_delta": change, "receiver_delivery_proven": False})
    return {"accepted": True, "plan_sha256": plan["plan_sha256"],
            "before_snapshot_sha256": base.digest(before), "after_snapshot_sha256": base.digest(after),
            "classification": evidence, "counter_deltas": deltas,
            "receiver_delivery_proven": False, "physical_acceptance": False}


def aqm_writes(parameters: dict) -> list[dict]:
    _need(type(parameters) is dict and set(parameters) == set(RW_FIELDS), "ONLY_THREE_GLOBAL_RW_AQM_FIELDS")
    return [{"path": AQM_PATH, "value": f"{name} {_u32(parameters[name])}"} for name in RW_FIELDS]


class AQMRuntime(Protocol):
    """Qualified device-resident fencing/restore boundary; not an implementation of SSH.

    Guard survives coordinator loss; typed global setters atomically recheck device
    identity under exclusive ownership. Per-station aqm tables are read-only.
    Explicit flow trace qualification links actual flow/QoS observations to epochs.
    Commit must atomically recheck identity/station epochs and complete membership,
    all zero-event totals, AQL/three RW targets and unexpired lease under the fence.
    Plan/proof hashes bind its stored device-side acquisition journal before disarm;
    a commit rejection must retain the guard and leave fenced restoration available.
    """
    evidence_kind: str
    qualification_sha256: str
    def preflight(self, plan: dict, *, timeout_s: float) -> dict: ...
    def readback(self, *, timeout_s: float) -> dict: ...
    def arm_guard(self, *, run_id: str, snapshot: dict, restore_writes: list[dict], lease_s: int, timeout_s: float) -> dict: ...
    def write(self, mutation: dict, *, token: str, expected_identity: dict, timeout_s: float) -> None: ...
    def probe_triple_play(self, plan: dict, *, before: dict, timeout_s: float) -> dict: ...
    def commit_guard(self, *, token: str, expected_parameters: dict, plan_sha256: str,
                     proof_sha256: str, timeout_s: float) -> dict: ...
    def fence_and_restore(self, *, token: str, snapshot: dict, restore_writes: list[dict], timeout_s: float) -> None: ...
    def release_guard(self, *, token: str, timeout_s: float) -> None: ...


def execute_aqm_canary(plan: dict, runtime: AQMRuntime, *, fixture_only: bool = True,
        qualification_sha256: str | None = None, monotonic: Callable = time.monotonic,
        utcnow: Callable = lambda: datetime.now(timezone.utc)) -> dict:
    validate_plan(plan)
    _need(type(fixture_only) is bool and runtime.evidence_kind ==
          ("disposable_fixture" if fixture_only else "qualified_device_adapter"), "AQM_RUNTIME_NOT_AUTHORIZED")
    if not fixture_only:
        _need(base._hash(qualification_sha256) == runtime.qualification_sha256, "QUALIFIED_AQM_ADAPTER_REQUIRED")
    preflight = runtime.preflight(copy.deepcopy(plan), timeout_s=5)
    _need(type(preflight) is dict and preflight.get("plan_sha256") == plan["plan_sha256"]
          and preflight.get("device_id") == plan["device_id"] and preflight.get("persistent_writes") is False
          and all(preflight.get(k) is True for k in ("exact_build_source_qualified", "counter_epochs_qualified",
              "independent_device_guard_qualified", "exact_rw_restore_qualified", "atomic_setter_fencing_qualified",
              "flow_trace_qualified", "atomic_commit_gate_qualified")), "AQM_PREFLIGHT_UNQUALIFIED")
    before_raw = runtime.readback(timeout_s=5)
    before = normalize_snapshot(before_raw, plan, now=utcnow())
    verify_zero_events(before)
    saved = {"identity": copy.deepcopy(before["identity"]), "parameters": copy.deepcopy(before["global_aqm"]["rw"]),
             "fq_flows_cnt": before["global_aqm"]["values"]["fq_flows_cnt"]}
    restore = aqm_writes(saved["parameters"])
    saved_sha = base.digest(saved)
    deadline, token, phase = monotonic() + LEASE_S, None, "ARM_GUARD"
    result = {"task_id": TASK_ID, "device_id": plan["device_id"], "run_id": plan["run_id"],
        "snapshot_sha256": saved_sha, "evidence_kind": runtime.evidence_kind, "physical_acceptance": False,
        "runtime_dispatch_allowed": False, "receiver_delivery_proven": False,
        "restore_scope": "ONLY_THREE_GLOBAL_AQM_RW_PARAMETERS", "events": []}

    def remaining():
        left = deadline - monotonic() - RESTORE_TIMEOUT_S
        _need(left > 0, "AQM_CANARY_DEADLINE_EXPIRED")
        return min(left, 10.0)

    def current():
        raw = runtime.readback(timeout_s=remaining())
        parsed = normalize_snapshot(raw, plan, now=utcnow())
        _same_epochs(before, parsed); verify_zero_events(parsed)
        return raw, parsed

    try:
        guard = runtime.arm_guard(run_id=plan["run_id"], snapshot=copy.deepcopy(saved),
            restore_writes=copy.deepcopy(restore), lease_s=LEASE_S, timeout_s=5)
        _need(type(guard) is dict, "AQM_GUARD_NOT_READY")
        token = guard.get("token")
        _need(type(token) is str and re.fullmatch(r"[0-9a-f]{64}", token)
              and guard.get("run_id") == plan["run_id"] and guard.get("snapshot_sha256") == saved_sha
              and guard.get("lease_s") == LEASE_S and guard.get("armed") is True
              and guard.get("independent") is True and guard.get("fencing") is True, "AQM_GUARD_NOT_READY")
        phase = "THREE_GLOBAL_AQM_PARAMETER_WRITES"
        for mutation in aqm_writes(plan["aqm_target"]):
            current()
            runtime.write(copy.deepcopy(mutation), token=token,
                          expected_identity=copy.deepcopy(saved["identity"]), timeout_s=remaining())
        applied_raw, applied = current(); verify_champion(applied, plan)
        phase = "TRIPLE_PLAY_COUNTER_AND_FLOW_PROOF"
        probe = runtime.probe_triple_play(copy.deepcopy(plan), before=copy.deepcopy(applied_raw), timeout_s=remaining())
        _need(type(probe) is dict, "TRIPLE_PLAY_PROBE_REQUIRED")
        proof = verify_triple_play(applied_raw, probe.get("after"), probe.get("witnesses"), plan, now=utcnow())
        remaining()
        phase = "FINAL_READBACK_AND_COMMIT"
        _, final = current(); verify_champion(final, plan)
        probe_after = normalize_snapshot(probe["after"], plan, now=utcnow())
        counter_deltas(probe_after, final)
        proof_sha = base.digest(proof)
        committed = runtime.commit_guard(token=token, expected_parameters=copy.deepcopy(plan["aqm_target"]),
            plan_sha256=plan["plan_sha256"], proof_sha256=proof_sha, timeout_s=remaining())
        _need(type(committed) is dict and committed.get("committed") is True
              and committed.get("token") == token and committed.get("plan_sha256") == plan["plan_sha256"]
              and committed.get("proof_sha256") == proof_sha, "AQM_GUARD_COMMIT_FAILED")
        remaining()
        result.update(state="FIXTURE_ACCEPTED" if fixture_only else "QUALIFIED_CANARY_ACCEPTED", proof=proof)
        return result
    except BaseException as exc:
        result.update(failure_type=type(exc).__name__, failure_phase=phase)
        if token is None:
            result["state"] = "GUARD_STATUS_UNKNOWN_NO_APPLY"
            return result
        result["events"].append("FENCE_AND_CAPTURED_RW_RESTORE_REQUIRED")
        try:
            runtime.fence_and_restore(token=token, snapshot=copy.deepcopy(saved),
                restore_writes=copy.deepcopy(restore), timeout_s=RESTORE_TIMEOUT_S)
            raw = runtime.readback(timeout_s=RESTORE_TIMEOUT_S)
            identity = _global_identity(raw, plan, now=utcnow())
            restored = parse_global_aqm(raw.get("global_aqm"))
            _need(base._json_bytes(identity) == base._json_bytes(saved["identity"])
                  and restored["rw"] == saved["parameters"]
                  and restored["values"]["fq_flows_cnt"] == saved["fq_flows_cnt"], "AQM_RW_RESTORE_READBACK_FAILED")
            runtime.release_guard(token=token, timeout_s=RESTORE_TIMEOUT_S)
            result["state"] = "ROLLED_BACK_AQM_PARAMETERS_EXACT"
        except BaseException:
            result["state"] = "AQM_RESTORE_UNVERIFIED_GUARD_RETAINED"
        return result
