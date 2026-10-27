"""Stage36B: exact AP multicast/AQL readbacks and receiver IPTV canary gate.

No device access or default executor. Compose this gate after Stage35B onboarding;
qualified adapters implement the same independent device-resident RAM lease. The
Stage35A source describes a compound AP+CPE result, not a universal AP-only gain.
"""
from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import math
import re
import time
from typing import Callable, Protocol

from controller import openwisp_uisp_unified_canary_provisioner as base

TASK_ID = "T-S36B-CODEX-IPTV-AC-VI-DMS-AND-HLS-PACING-CONTROLLER-INTEGRATION"
STAGE35A_PATH = base.ROOT / "artifacts/autoresearch/stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json"
STAGE35A_SHA256 = "779d29dc9d6e330a932ff3ecea0b779d73e378fcc8f4a6494239be8d9dc68ebb"
AC_INDEX = {"VO": 0, "VI": 1, "BE": 2, "BK": 3}
AQL_TARGETS = {"VO": [600, 1200], "VI": [1200, 2400], "BE": [1000, 2000], "BK": [500, 1000]}
AQL_PATH = "/sys/kernel/debug/ieee80211/phy0/aql_txq_limit"
BRIDGE_PATH = "/sys/class/net/br-lan/bridge/"
PORT_PATH = "/sys/class/net/br-lan/brif/"
LEASE_S = 60
RESTORE_TIMEOUT_S = 5
SETTLE_S = 10
POLL_S = 5
METRIC_KINDS = {"udp_receiver_jitter_ms": "udp_datagrams", "hls_intersegment_jitter_ms": "hls_segments"}


def _need(condition, code):
    if not condition:
        raise ValueError(code)


def _number(value, *, minimum=0):
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and value >= minimum
    except (OverflowError, TypeError):
        valid = False
    _need(valid, "FINITE_NUMBER_REQUIRED")
    return value


def _uint(value, *, minimum=0, maximum=2**32 - 1):
    if type(value) is str:
        _need(re.fullmatch(r"[0-9]+", value.strip()), "UNSIGNED_INTEGER_REQUIRED")
        value = int(value.strip())
    _need(type(value) is int and minimum <= value <= maximum, "UNSIGNED_INTEGER_REQUIRED")
    return value


def _bit(value):
    return _uint(value, maximum=1)


def _port(value):
    _need(type(value) is str and re.fullmatch(r"phy0-ap0(?:\.sta[0-9]+)?", value), "AP_WDS_PORT_REQUIRED")
    return value


def parse_aql_readback(raw: str) -> dict:
    """Parse kernel label output; BC/MC and an optional appended threshold are separate.

    The combined form is present in saved bench receipts. Native upstream6.6
    prints the four named AC rows without BC/MC; never infer any absent field.
    """
    _need(type(raw) is str and 0 < len(raw) <= 8192 and "\x00" not in raw, "AQL_READBACK_REQUIRED")
    lines = [line.split() for line in raw.splitlines() if line.strip()]
    _need(lines and lines.pop(0) == ["AC", "AQL", "limit", "low", "AQL", "limit", "high"], "AQL_HEADER_REQUIRED")
    limits, bcmc, threshold = {}, None, None
    for index, row in enumerate(lines):
        if len(row) == 3 and row[0] in AC_INDEX:
            label = row[0]
            _need(label not in limits and bcmc is None and threshold is None, "AQL_DUPLICATE_OR_ORDER")
            low, high = _uint(row[1]), _uint(row[2])
            _need(low <= high, "AQL_LOW_EXCEEDS_HIGH")
            limits[label] = [low, high]
        elif len(row) == 2 and row[0] == "BC/MC":
            _need(set(limits) == set(AC_INDEX) and bcmc is None and threshold is None, "AQL_BCMC_INVALID")
            bcmc = _uint(row[1])
        elif len(row) == 1:
            _need(set(limits) == set(AC_INDEX) and threshold is None and index == len(lines) - 1,
                  "AQL_THRESHOLD_INVALID")
            threshold = _uint(row[0])
        else:
            raise ValueError("AQL_ROW_INVALID")
    _need(set(limits) == set(AC_INDEX), "FOUR_AQL_QUEUES_REQUIRED")
    return {"limits": {ac: limits[ac] for ac in AC_INDEX}, "bcmc_limit": bcmc, "combined_threshold": threshold}


@dataclass(frozen=True)
class JitterPolicy:
    """Caller must prespecify budgets; no empirical/modelled default QoE threshold."""
    max_jitter_ms: float
    max_increase_pct: float | None
    max_loss_pct: float
    min_received_units: int
    min_window_s: float

    def __post_init__(self):
        _need(_number(self.max_jitter_ms) > 0, "POSITIVE_JITTER_CEILING_REQUIRED")
        if self.max_increase_pct is not None:
            _number(self.max_increase_pct)
        _need(_number(self.max_loss_pct) <= 100, "LOSS_CEILING_INVALID")
        _uint(self.min_received_units, minimum=1)
        _need(_number(self.min_window_s) > 0, "POSITIVE_RECEIVER_WINDOW_REQUIRED")


def _source_binding() -> dict:
    raw = base.bridge._read(STAGE35A_PATH)
    _need(hashlib.sha256(raw).hexdigest() == STAGE35A_SHA256, "STAGE35A_SOURCE_DRIFT")
    source = base.bridge._json(raw)
    rows = [r for r in source.get("rounds", []) if r.get("round_id") == "S35A-R1"]
    _need(len(rows) == 1 and rows[0].get("decision") == "PROMOTE_NEW_CHAMPION", "V9_SOURCE_REQUIRED")
    for phase in ("B1", "B2"):
        text = rows[0]["phases"][phase]["getter_readback"]["ap_bridge_multicast_readback"]
        _need(text.splitlines()[:2] == ["1", "1"] and "phy0-ap0.sta" in text, "V9_AP_SOURCE_READBACK_REQUIRED")
    return {"path": str(STAGE35A_PATH.relative_to(base.ROOT)), "sha256": STAGE35A_SHA256,
            "round_id": "S35A-R1", "claim_scope": "SOURCE_REPORTED_COMPOUND_AP_AND_CPE_RESULT"}


def build_iptv_plan(*, device_id: str, run_id: str, expected_station_macs: list[str],
                    streams: list[dict], jitter_policy: JitterPolicy) -> dict:
    device_id, run_id = base.bridge._uuid(device_id), base._identifier(run_id)
    _need(type(expected_station_macs) is list and 1 <= len(expected_station_macs) <= 256,
          "NONEMPTY_STATION_INVENTORY_REQUIRED")
    macs = [base._mac(m) for m in expected_station_macs]
    _need(len(set(macs)) == len(macs), "DUPLICATE_STATION")
    _need(type(jitter_policy) is JitterPolicy, "EXPLICIT_JITTER_POLICY_REQUIRED")
    _need(type(streams) is list and 1 <= len(streams) <= 256, "NONEMPTY_IPTV_STREAM_INVENTORY_REQUIRED")
    checked, ids = [], set()
    for row in streams:
        _need(type(row) is dict and set(row) == {"stream_id", "station_mac", "metric_kind", "baseline_jitter_ms"},
              "EXACT_STREAM_SPEC_REQUIRED")
        ident = row["stream_id"]
        _need(type(ident) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", ident) and ident not in ids,
              "UNIQUE_STREAM_ID_REQUIRED")
        ids.add(ident)
        mac = base._mac(row["station_mac"])
        _need(mac in macs and row["metric_kind"] in METRIC_KINDS, "IPTV_STREAM_IDENTITY_INVALID")
        baseline = _number(row["baseline_jitter_ms"])
        _need(jitter_policy.max_increase_pct is None or baseline > 0, "POSITIVE_PAIRED_JITTER_BASELINE_REQUIRED")
        checked.append({**row, "station_mac": mac})
    parent = base.bridge.load_template_pack()["manifest"]["source_profiles"][base.PROFILE_ID]
    plan = {"schema_version": 1, "task_id": TASK_ID, "device_id": device_id, "run_id": run_id,
            "expected_station_macs": sorted(macs), "streams": sorted(checked, key=lambda r: r["stream_id"]),
            "jitter_policy": asdict(jitter_policy), "v9_source": _source_binding(),
            "parent_v8_profile_sha256": base.digest(parent), "aql_targets": copy.deepcopy(AQL_TARGETS),
            "bridge_targets": {"multicast_snooping": 1, "multicast_querier": 1},
            "dms_target": 1, "lease_s": LEASE_S, "stable_s": SETTLE_S, "minimum_healthy_samples": 3,
            "scope": "AP_ONLY_RAM_IPTV_READBACK_GATE", "cpe_actions": [], "runtime_dispatch_allowed": False,
            "physical_acceptance": False, "hls_policy": "observe receiver delivery; preserve existing pacing and classifier"}
    plan["plan_sha256"] = base.digest(plan)
    return plan


def validate_plan(plan: dict) -> None:
    _need(type(plan) is dict and type(plan.get("jitter_policy")) is dict, "IPTV_PLAN_REQUIRED")
    policy = JitterPolicy(**plan["jitter_policy"])
    expected = build_iptv_plan(device_id=plan.get("device_id"), run_id=plan.get("run_id"),
        expected_station_macs=plan.get("expected_station_macs"), streams=plan.get("streams"), jitter_policy=policy)
    _need(base._json_bytes(expected) == base._json_bytes(plan), "IPTV_PLAN_INTEGRITY_FAILED")


def normalize_readback(raw: dict, plan: dict, *, now: datetime, after: datetime | None = None,
                       require_station_health: bool = True) -> dict:
    """Normalize effective controls, retaining whole boot/netns/bridge/port identities."""
    _need(type(raw) is dict and raw.get("run_id") == plan["run_id"]
          and raw.get("device_id") == plan["device_id"]
          and raw.get("source") == "kernel_sysfs_debugfs_and_iw"
          and raw.get("platform") == "openwrt" and raw.get("role") == "ap"
          and raw.get("four_address_wds") is True and raw.get("wiphy") == "phy0"
          and raw.get("driver") in {"ath10k", "ath10k_pci"}, "EFFECTIVE_AP_WDS_READBACK_REQUIRED")
    base._fresh(raw.get("observed_at"), now, after=after)
    all_peers = raw.get("wiphy_station_macs")
    _need(raw.get("wiphy_station_inventory_complete") is True and type(all_peers) is list
          and len(all_peers) == len(plan["expected_station_macs"])
          and sorted(base._mac(mac) for mac in all_peers) == plan["expected_station_macs"],
          "COMPLETE_AFFECTED_WIPHY_STATION_SET_REQUIRED")
    boot_id = base.bridge._uuid(raw.get("boot_id"))
    netns = _uint(raw.get("netns_inode"), minimum=1, maximum=2**64 - 1)
    br, parent, ports, stations = (raw.get(k) for k in ("bridge", "parent", "ports", "stations"))
    _need(type(br) is dict and br.get("name") == "br-lan" and type(parent) is dict
          and parent.get("name") == "phy0-ap0", "BRIDGE_AND_PARENT_REQUIRED")
    bridge_index, parent_index = _uint(br.get("ifindex"), minimum=1), _uint(parent.get("ifindex"), minimum=1)
    _need(bridge_index != parent_index and type(ports) is dict and "phy0-ap0" in ports
          and 1 <= len(ports) <= 257 and type(stations) is list
          and len(stations) == len(plan["expected_station_macs"]), "COMPLETE_PORT_STATION_INVENTORY_REQUIRED")
    identities, flags = {}, {}
    for name, port in ports.items():
        _port(name)
        _need(type(port) is dict, "PORT_READBACK_REQUIRED")
        index = _uint(port.get("ifindex"), minimum=1)
        _need(port.get("bridge_ifindex") == bridge_index and type(port.get("bridge_ifindex")) is int
              and port.get("parent_ifindex") == parent_index and type(port.get("parent_ifindex")) is int,
              "PORT_PARENT_OR_BRIDGE_IDENTITY_MISMATCH")
        _need(index != bridge_index and (name != "phy0-ap0" or index == parent_index), "PORT_IFINDEX_MISMATCH")
        identities[name] = index
        flags[name] = _bit(port.get("multicast_to_unicast"))
    _need(len(set(identities.values())) == len(identities), "DUPLICATE_PORT_IFINDEX")
    aql = parse_aql_readback(raw.get("aql_txq_limit"))
    bindings, seen, used_ports, station_aql = [], set(), {"phy0-ap0"}, {}
    for station in stations:
        _need(type(station) is dict, "STATION_READBACK_REQUIRED")
        mac, iface = base._mac(station.get("mac")), _port(station.get("interface"))
        _need(mac in plan["expected_station_macs"] and mac not in seen and iface in ports
              and type(station.get("ifindex")) is int and station["ifindex"] == identities[iface],
              "STATION_PORT_BINDING_CHANGED")
        _need(station.get("four_address_wds") is True, "STATION_FOUR_ADDRESS_REQUIRED")
        if require_station_health:
            _need(station.get("associated") is True and station.get("authorized") is True, "STATION_HEALTH_FAILED")
        peer_limits = station.get("aql_limits")
        _need(type(peer_limits) is dict and set(peer_limits) == set(AC_INDEX), "STATION_AQL_READBACK_REQUIRED")
        for ac in AC_INDEX:
            pair = peer_limits[ac]
            _need(type(pair) is list and len(pair) == 2 and all(type(v) is int for v in pair)
                  and pair == aql["limits"][ac], "CUSTOM_OR_UNKNOWN_STATION_AQL_BLOCKS_EXACT_GLOBAL_RESTORE")
        station_aql[mac] = copy.deepcopy(peer_limits)
        seen.add(mac); used_ports.add(iface)
        bindings.append({"mac": mac, "interface": iface, "ifindex": identities[iface]})
    _need(used_ports == set(ports), "UNBOUND_DYNAMIC_PORT")
    threshold = _uint(raw.get("aql_threshold"))
    _need(aql["combined_threshold"] is None or threshold == aql["combined_threshold"], "AQL_THRESHOLD_DISAGREEMENT")
    return {"identity": {"boot_id": boot_id, "netns_inode": netns, "bridge_ifindex": bridge_index,
                "parent_ifindex": parent_index, "ports": identities,
                "stations": sorted(bindings, key=lambda r: r["mac"])},
            "bridge": {k: _bit(br.get(k)) for k in ("multicast_snooping", "multicast_querier")},
            "multicast_to_unicast": flags, "aql_limits": aql["limits"],
            "station_aql_limits": station_aql,
            "bcmc_limit": aql["bcmc_limit"], "aql_threshold": threshold}


def candidate_state(snapshot: dict) -> dict:
    state = copy.deepcopy(snapshot)
    state["bridge"] = {"multicast_snooping": 1, "multicast_querier": 1}
    state["multicast_to_unicast"] = {name: 1 for name in snapshot["multicast_to_unicast"]}
    state["aql_limits"] = copy.deepcopy(AQL_TARGETS)
    state["station_aql_limits"] = {mac: copy.deepcopy(AQL_TARGETS) for mac in snapshot["station_aql_limits"]}
    return state


def state_writes(state: dict) -> list[dict]:
    """Typed single-coordinate writes; no shell/glob, defaults or non-AP controls."""
    _need(type(state) is dict and set(state.get("bridge", {})) == {"multicast_snooping", "multicast_querier"}
          and type(state.get("multicast_to_unicast")) is dict and state["multicast_to_unicast"]
          and set(state.get("aql_limits", {})) == set(AC_INDEX), "EXACT_CONTROL_STATE_REQUIRED")
    writes = [{"path": BRIDGE_PATH + name, "value": str(_bit(state["bridge"][name]))}
              for name in ("multicast_snooping", "multicast_querier")]
    for name in sorted(state["multicast_to_unicast"]):
        writes.append({"path": PORT_PATH + _port(name) + "/multicast_to_unicast",
                       "value": str(_bit(state["multicast_to_unicast"][name]))})
    for label, index in AC_INDEX.items():
        pair = state["aql_limits"][label]
        _need(type(pair) is list and len(pair) == 2, "EXACT_AQL_PAIR_REQUIRED")
        low, high = _uint(pair[0]), _uint(pair[1])
        _need(low <= high, "AQL_LOW_EXCEEDS_HIGH")
        writes.append({"path": AQL_PATH, "value": f"{index} {low} {high}"})
    return writes


def verify_effective_readbacks(raw: dict, plan: dict, snapshot: dict, *, now: datetime,
                              after: datetime | None = None) -> dict:
    state = normalize_readback(raw, plan, now=now, after=after)
    _need(base._json_bytes(state["identity"]) == base._json_bytes(snapshot["identity"]), "DYNAMIC_STATION_OR_PORT_CHANGED")
    _need(base._json_bytes(state) == base._json_bytes(candidate_state(snapshot)), "IPTV_EFFECTIVE_CONTROL_MISMATCH")
    return state


def evaluate_iptv_jitter(metrics: dict, plan: dict, *, now: datetime, after: datetime) -> dict:
    """Receiver jitter, not ping RTT variation or a modelled rebuffering label."""
    _need(type(metrics) is dict and metrics.get("run_id") == plan["run_id"]
          and metrics.get("device_id") == plan["device_id"], "IPTV_RECEIVER_RECEIPT_REQUIRED")
    base._fresh(metrics.get("observed_at"), now, after=after)
    rows = metrics.get("streams")
    expected = {r["stream_id"]: r for r in plan["streams"]}
    _need(type(rows) is list and len(rows) == len(expected), "COMPLETE_IPTV_STREAM_SET_REQUIRED")
    policy = JitterPolicy(**plan["jitter_policy"])
    results, seen, ends = [], set(), {}
    for row in rows:
        _need(type(row) is dict and type(row.get("stream_id")) is str, "IPTV_STREAM_RECEIPT_REQUIRED")
        ident = row["stream_id"]
        _need(ident in expected and ident not in seen, "UNKNOWN_OR_DUPLICATE_IPTV_STREAM")
        seen.add(ident); spec = expected[ident]
        _need(base._mac(row.get("station_mac")) == spec["station_mac"]
              and row.get("metric_kind") == spec["metric_kind"] and row.get("source") == "receiver_report"
              and row.get("denominator_kind") == METRIC_KINDS[spec["metric_kind"]]
              and row.get("under_bulk_load") is True, "IPTV_METRIC_OR_WORKLOAD_MISMATCH")
        _need(row.get("observed_ac") == "VI" and type(row.get("observed_tid")) is int
              and row["observed_tid"] in (4, 5) and type(row.get("dscp_codepoint")) is int
              and row["dscp_codepoint"] in (32, 34), "OBSERVED_AC_VI_CLASSIFICATION_REQUIRED")
        start, end = base._utc(row.get("window_start")), base._utc(row.get("window_end"))
        base._fresh(end, now, after=after)
        _need(start >= after and start <= end <= base._utc(metrics["observed_at"])
              and (end - start).total_seconds() >= policy.min_window_s, "IPTV_POST_APPLY_WINDOW_REQUIRED")
        sent = _uint(row.get("sent_units"), minimum=1)
        received = _uint(row.get("received_units"), minimum=policy.min_received_units)
        _need(received <= sent, "IPTV_DENOMINATOR_INVALID")
        loss = (sent - received) * 100.0 / sent
        jitter = _number(row.get("jitter_ms"))
        ceiling = policy.max_jitter_ms
        if policy.max_increase_pct is not None:
            ceiling = min(ceiling, spec["baseline_jitter_ms"] * (1 + policy.max_increase_pct / 100.0))
        _need(jitter <= ceiling and loss <= policy.max_loss_pct, "IPTV_JITTER_OR_LOSS_GATE_FAILED")
        ends[ident] = end.isoformat()
        results.append({"stream_id": ident, "jitter_ms": jitter, "jitter_ceiling_ms": ceiling,
                        "loss_pct": loss, "received_units": received})
    return {"accepted": True, "streams": results, "window_ends": ends}


class IPTVRuntime(Protocol):
    """Qualified device adapter: no default transport is supplied.

    write() must atomically recheck expected_identity with the guarded setter;
    coordinator readback alone cannot close TOCTOU. The independent resident guard
    owns the snapshot and restore_writes before READY, survives coordinator loss,
    and fences all setters on failure or its60s monotonic deadline. Restore checks
    boot/netns/bridge/MAC/interface/ifindex before every write; never touch a recycled
    or missing port. Leave the restoration journal/guard armed when unverified.
    Per-station AQL readbacks must be uniform with the global limits: the upstream
    global setter preserves custom limits selectively, so a global default rollback
    cannot prove restoration of arbitrary pre-existing per-station overrides.
    The same atomic section checks expected_aql_limits, uniformity and the full
    affected wiphy station set; no other VAP peer may be silently left unobserved.
    """
    evidence_kind: str
    qualification_sha256: str
    def preflight(self, plan: dict, *, timeout_s: float) -> dict: ...
    def readback(self, *, timeout_s: float) -> dict: ...
    def arm_guard(self, *, run_id: str, snapshot: dict, restore_writes: list[dict], lease_s: int, timeout_s: float) -> dict: ...
    def write(self, mutation: dict, *, token: str, expected_identity: dict,
              expected_aql_limits: dict, timeout_s: float) -> None: ...
    def measure_iptv(self, *, timeout_s: float) -> dict: ...
    def commit_guard(self, *, token: str, expected_state: dict, timeout_s: float) -> dict: ...
    def fence_and_restore(self, *, token: str, snapshot: dict, restore_writes: list[dict], timeout_s: float) -> None: ...
    def release_guard(self, *, token: str, timeout_s: float) -> None: ...


def execute_iptv_canary(plan: dict, runtime: IPTVRuntime, *, fixture_only: bool = True,
        qualification_sha256: str | None = None, monotonic: Callable = time.monotonic,
        utcnow: Callable = lambda: datetime.now(timezone.utc), sleep: Callable = time.sleep) -> dict:
    validate_plan(plan)
    _need(type(fixture_only) is bool, "BOOLEAN_RUNTIME_POLICY_REQUIRED")
    _need(runtime.evidence_kind == ("disposable_fixture" if fixture_only else "qualified_device_adapter"),
          "IPTV_RUNTIME_BOUNDARY_NOT_AUTHORIZED")
    if not fixture_only:
        _need(base._hash(qualification_sha256) == runtime.qualification_sha256, "QUALIFIED_IPTV_ADAPTER_REQUIRED")
    preflight = runtime.preflight(copy.deepcopy(plan), timeout_s=5)
    _need(type(preflight) is dict and preflight.get("plan_sha256") == plan["plan_sha256"]
          and preflight.get("device_id") == plan["device_id"] and preflight.get("cpe_actions") == []
          and preflight.get("persistent_writes") is False
          and preflight.get("v8_effective_readback_profile_sha256") == plan["parent_v8_profile_sha256"]
          and all(preflight.get(k) is True for k in ("exact_board_build_module_qualified", "regulatory_unchanged",
              "independent_device_guard_qualified", "exact_restore_qualified", "atomic_identity_setter_fencing_qualified")),
          "IPTV_PREFLIGHT_UNQUALIFIED")
    snapshot = normalize_readback(runtime.readback(timeout_s=5), plan, now=utcnow())
    restore = state_writes(snapshot)
    target = candidate_state(snapshot)
    snapshot_sha = base.digest(snapshot)
    deadline = monotonic() + LEASE_S
    token, phase = None, "ARM_GUARD"
    result = {"task_id": TASK_ID, "run_id": plan["run_id"], "device_id": plan["device_id"],
              "plan_sha256": plan["plan_sha256"], "snapshot_sha256": snapshot_sha, "lease_s": LEASE_S,
              "evidence_kind": runtime.evidence_kind, "physical_acceptance": False,
              "runtime_dispatch_allowed": False, "cpe_actions": [], "events": []}

    def remaining():
        left = deadline - monotonic() - RESTORE_TIMEOUT_S
        _need(left > 0, "IPTV_CANARY_DEADLINE_EXPIRED")
        return min(left, 5.0)

    def read_current(*, healthy=True, after=None):
        raw = runtime.readback(timeout_s=remaining())
        state = normalize_readback(raw, plan, now=utcnow(), after=after, require_station_health=healthy)
        _need(base._json_bytes(state["identity"]) == base._json_bytes(snapshot["identity"]),
              "DYNAMIC_STATION_OR_PORT_CHANGED")
        return raw, state

    try:
        guard = runtime.arm_guard(run_id=plan["run_id"], snapshot=copy.deepcopy(snapshot),
            restore_writes=copy.deepcopy(restore), lease_s=LEASE_S, timeout_s=5)
        _need(type(guard) is dict, "IPTV_GUARD_NOT_READY")
        token = guard.get("token")
        _need(type(token) is str and re.fullmatch(r"[0-9a-f]{64}", token)
              and guard.get("run_id") == plan["run_id"] and guard.get("snapshot_sha256") == snapshot_sha
              and guard.get("lease_s") == LEASE_S and guard.get("armed") is True
              and guard.get("independent") is True and guard.get("fencing") is True, "IPTV_GUARD_NOT_READY")
        result["events"].append("INDEPENDENT_60S_GUARD_ARMED")
        phase = "AP_MULTICAST_AND_FOUR_AQL_WRITES"
        for mutation in state_writes(target):
            _, current = read_current()
            runtime.write(copy.deepcopy(mutation), token=token,
                          expected_identity=copy.deepcopy(snapshot["identity"]),
                          expected_aql_limits=copy.deepcopy(current["aql_limits"]), timeout_s=remaining())
        after = utcnow()
        first_mono, first_radio, previous_radio, first_windows, previous_windows = None, None, None, None, None
        samples = 0
        while True:
            phase = "EFFECTIVE_READBACK_AND_IPTV_RECEIVER_GATE"
            raw, current = read_current(after=after)
            _need(base._json_bytes(current) == base._json_bytes(target), "IPTV_EFFECTIVE_CONTROL_MISMATCH")
            observed = base._utc(raw["observed_at"])
            _need(previous_radio is None or observed > previous_radio, "REPLAYED_IPTV_RADIO_READBACK")
            previous_radio = observed
            metrics = runtime.measure_iptv(timeout_s=remaining())
            health = evaluate_iptv_jitter(metrics, plan, now=utcnow(), after=after)
            ends = {k: base._utc(v) for k, v in health["window_ends"].items()}
            _need(previous_windows is None or all(ends[k] > previous_windows[k] for k in ends),
                  "REPLAYED_IPTV_RECEIVER_WINDOW")
            previous_windows = ends
            now_mono = monotonic()
            if first_mono is None:
                first_mono, first_radio, first_windows = now_mono, observed, ends
            samples += 1
            result["events"].append({"healthy_sample": samples, "iptv": health})
            remaining()
            if samples >= 3 and now_mono - first_mono >= SETTLE_S \
                    and (observed - first_radio).total_seconds() >= SETTLE_S \
                    and all((ends[k] - first_windows[k]).total_seconds() >= SETTLE_S for k in ends):
                phase = "FINAL_IDENTITY_READBACK_AND_COMMIT"
                _, final = read_current(after=after)
                _need(base._json_bytes(final) == base._json_bytes(target), "FINAL_IPTV_READBACK_CHANGED")
                committed = runtime.commit_guard(token=token, expected_state=copy.deepcopy(target), timeout_s=remaining())
                _need(type(committed) is dict and committed.get("committed") is True
                      and committed.get("token") == token, "IPTV_GUARD_COMMIT_FAILED")
                remaining()
                result.update(state="FIXTURE_ACCEPTED" if fixture_only else "QUALIFIED_CANARY_ACCEPTED",
                              healthy_samples=samples, stable_s=now_mono - first_mono)
                return result
            sleep(min(POLL_S, remaining()))
    except BaseException as exc:
        result.update(failure_type=type(exc).__name__, failure_phase=phase)
        if token is None:
            result["state"] = "GUARD_STATUS_UNKNOWN_NO_APPLY"
            return result
        result["events"].append("FENCE_AND_EXACT_SNAPSHOT_RESTORE_REQUIRED")
        try:
            runtime.fence_and_restore(token=token, snapshot=copy.deepcopy(snapshot),
                                      restore_writes=copy.deepcopy(restore), timeout_s=RESTORE_TIMEOUT_S)
            raw = runtime.readback(timeout_s=RESTORE_TIMEOUT_S)
            restored = normalize_readback(raw, plan, now=utcnow(), require_station_health=False)
            _need(base._json_bytes(restored) == base._json_bytes(snapshot), "IPTV_EXACT_RESTORE_READBACK_FAILED")
            runtime.release_guard(token=token, timeout_s=RESTORE_TIMEOUT_S)
            result["state"] = "ROLLED_BACK_EXACT"
        except BaseException:
            result["state"] = "ROLLBACK_UNVERIFIED_GUARD_RETAINED"
        return result
