"""Stage38B: offline v11/v12 readbacks, UPH/IGMP guards and exact restore recipes.

No transport, device executor, native guard installer or traffic generator.
Generated scripts require an independently qualified, already armed native guard.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import re
import shlex

from controller import mac80211_aqm_per_tid_canary_verifier as aqm

base, iptv = aqm.base, aqm.iptv
TASK_ID = "T-S38B-CODEX-CHAMPION-V12-UPH-SYSCTL-CLOBBER-AND-IGMPV2-CANARY-VERIFIER"
ROLES = ("ap", "cpe", "rocket")
UPH_PATH = "/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit"
UPH_ALIASES = ("ff_mcast_airtime_limit", "voip_bias", "fixed_frame", "atpc", "cms_bias", "evm_meas_config")
GUARD_PATH = "/usr/libexec/fmx-stage38b-restore-guard"
SOURCE_ROUNDS = (
    ("artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json", "S37A-R2",
     "69fec2437b2e13c6a9bcf4296b7827c920fa2902d997b9a3024d6f62995be131"),
    ("artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json", "S39A-R3",
     "4b3153a2305c35b4770b6a9db0bd01b85558cf5507d7898722a633eb38a1ac26"),
)


def _need(condition, code):
    if not condition:
        raise ValueError(code)


def _name(value):
    _need(type(value) is str and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.-]{0,14}", value), "LITERAL_NETDEV_REQUIRED")
    return value


def _wifi(name):
    return bool(re.fullmatch(r"phy0-ap0(?:\.sta[0-9]+)?", name))


def _core_target(role):
    return {"fq_memory_limit": 4194304, "fq_limit": 2048 if role == "ap" else 1024,
            "fq_quantum": 4542 if role == "ap" else 1514}


def _aql_target(role):
    return {"VO": [300, 600], "VI": [1200, 2400],
            "BE": [1500, 3000] if role == "ap" else [900, 1500], "BK": [500, 1000]}


def source_contract() -> list[dict]:
    """Pinned historical positive rounds; never fill absent native getters."""
    result = []
    for path, round_id, expected in SOURCE_ROUNDS:
        source = base.bridge._json(base.bridge._read(base.ROOT / path))
        rounds = [row for row in source.get("rounds", []) if row.get("round_id") == round_id]
        _need(len(rounds) == 1 and base.digest(rounds[0]) == expected, "CHAMPION_SOURCE_ROUND_DRIFT")
        row = rounds[0]
        _need(row["decision"] == "PROMOTE_NEW_CHAMPION" and row["promoted"] is True, "SOURCE_PROMOTION_REQUIRED")
        for phase in ("B1", "B2"):
            getters = row["phases"][phase]["getter_readback"]
            if round_id == "S37A-R2":
                for role, field in (("ap", "ap_aqm_and_aql"), ("cpe", "loco_aqm")):
                    observed, aql = aqm.split_combined_readback(getters[field])
                    _need(observed["rw"] == _core_target(role) and aql["limits"] == _aql_target(role),
                          "V11_SOURCE_READBACK_MISMATCH")
            else:
                observed = getters["ap_m20_readback"]
                _need(observed["bridge/multicast_igmp_version"] == 2
                      and getters["r198_m19_readback"]["uph_wifi0/ff_mcast_airtime_limit"] == 5,
                      "V12_SOURCE_READBACK_MISMATCH")
                for path_name, value in observed.items():
                    if path_name.startswith("brif/phy0-ap0"):
                        _need(value == 1, "V12_SOURCE_WDS_MISMATCH")
        result.append({"path": path, "round_id": round_id, "round_sha256": expected})
    return result


def build_plan(*, run_id: str, device_ids: dict, station_macs: dict, ports: dict, flows: list[dict]) -> dict:
    run_id = base._identifier(run_id)
    _need(type(device_ids) is dict and set(device_ids) == set(ROLES), "THREE_EXPLICIT_DEVICE_ROLES_REQUIRED")
    ids = {role: base.bridge._uuid(device_ids[role]) for role in ROLES}
    _need(len(set(ids.values())) == 3, "DISTINCT_DEVICE_IDENTITIES_REQUIRED")
    _need(type(station_macs) is dict and set(station_macs) == {"ap", "cpe"}, "BOTH_STATION_INVENTORIES_REQUIRED")
    peers = {}
    for role in ("ap", "cpe"):
        values = station_macs[role]
        _need(type(values) is list and 1 <= len(values) <= 256, "STATION_INVENTORY_REQUIRED")
        peers[role] = sorted(base._mac(mac) for mac in values)
        _need(len(set(peers[role])) == len(peers[role]), "DUPLICATE_STATION")
    _need(type(ports) is dict and set(ports) == set(ROLES), "COMPLETE_PORT_PLAN_REQUIRED")
    checked_ports = {}
    for role in ROLES:
        _need(type(ports[role]) is list and 1 <= len(ports[role]) <= 256, "PORT_INVENTORY_REQUIRED")
        checked_ports[role] = sorted(_name(name) for name in ports[role])
        _need(len(set(checked_ports[role])) == len(checked_ports[role]), "DUPLICATE_PORT")
    _need("phy0-ap0" in checked_ports["ap"], "AP_PARENT_PORT_REQUIRED")
    _need(type(flows) is list and 3 <= len(flows) <= 256, "TRIPLE_PLAY_FLOW_PLAN_REQUIRED")
    checked_flows, seen = [], set()
    for flow in flows:
        _need(type(flow) is dict and set(flow) == {"flow_id", "service", "station_mac"}, "EXACT_FLOW_SPEC_REQUIRED")
        ident, service = flow["flow_id"], flow["service"]
        _need(type(ident) is str and re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", ident)
              and ident not in seen and service in aqm.SERVICES, "FLOW_SPEC_INVALID")
        mac = base._mac(flow["station_mac"])
        _need(mac in peers["ap"], "FLOW_NOT_IN_AP_INVENTORY")
        checked_flows.append({**flow, "station_mac": mac}); seen.add(ident)
    _need({flow["service"] for flow in checked_flows} == set(aqm.SERVICES), "ALL_THREE_SERVICES_REQUIRED")
    plan = {"schema_version": 1, "task_id": TASK_ID, "run_id": run_id, "device_ids": ids,
            "station_macs": peers, "ports": checked_ports, "flows": sorted(checked_flows, key=lambda f: f["flow_id"]),
            "source_rounds": source_contract(), "min_window_s": 5, "max_window_s": 55,
            "runtime_dispatch_allowed": False, "physical_acceptance": False}
    plan["plan_sha256"] = base.digest(plan)
    return plan


def validate_plan(plan):
    _need(type(plan) is dict, "PLAN_REQUIRED")
    expected = build_plan(**{k: plan.get(k) for k in ("run_id", "device_ids", "station_macs", "ports", "flows")})
    _need(base._json_bytes(plan) == base._json_bytes(expected), "PLAN_INTEGRITY_FAILED")


def parse_uph_vector(raw: str) -> list[int]:
    _need(type(raw) is str and len(raw) <= 8192 and raw.endswith("\n") and len(raw.splitlines()) == 1,
          "COMPLETE_UPH_VECTOR_TEXT_REQUIRED")
    values = raw.split()
    _need(len(values) == 16 and all(re.fullmatch(r"-?[0-9]+", value) for value in values), "EXACTLY_SIXTEEN_UPH_INTEGERS_REQUIRED")
    numbers = [int(value) for value in values]
    _need(all(-2**31 <= value < 2**31 for value in numbers), "UPH_SIGNED32_RANGE_REQUIRED")
    return numbers


def _uph(raw, module_sha):
    _need(type(raw) is dict, "UPH_READBACK_REQUIRED")
    scalar = iptv._uint(raw.get("ff_mcast_airtime_limit"))
    capture = raw.get("vector_capture")
    _need(type(capture) is dict and capture.get("alias_inventory_complete") is True
          and capture.get("write_semantics") == "qualified_full_vector"
          and capture.get("module_sha256") == module_sha, "QUALIFIED_FULL_UPH_CAPTURE_REQUIRED")
    qualification = base._hash(capture.get("qualification_sha256"))
    vector = parse_uph_vector(capture.get("vector"))
    aliases = capture.get("aliases")
    _need(type(aliases) is dict and set(aliases) == set(UPH_ALIASES), "COMPLETE_QUALIFIED_UPH_ALIAS_MAP_REQUIRED")
    _need(all(parse_uph_vector(value) == vector for value in aliases.values()) and vector[0] == scalar,
          "UPH_ALIAS_BUFFER_CLOBBER_OR_INCONSISTENT_CAPTURE")
    return {"vector": vector, "scalar": scalar, "aliases": sorted(aliases), "qualification_sha256": qualification}


def _bridge(raw, role, plan):
    _need(type(raw) is dict, "BRIDGE_READBACK_REQUIRED")
    name = "br0" if role == "rocket" else "br-lan"
    path = f"/sys/devices/virtual/net/{name}"
    _need(raw.get("path") == path and raw.get("ports_complete") is True, "COMPLETE_EXACT_BRIDGE_INVENTORY_REQUIRED")
    identity = {"path": path, "ifindex": aqm._positive(raw.get("ifindex")), "epoch": base._hash(raw.get("epoch"))}
    fields = ("multicast_snooping", "multicast_querier")
    values = {field: iptv._uint(raw.get(field), maximum=1) for field in fields}
    if role != "rocket":
        values["multicast_igmp_version"] = iptv._uint(raw.get("multicast_igmp_version"), minimum=2, maximum=3)
    ports = raw.get("ports")
    _need(type(ports) is list and len(ports) == len(plan["ports"][role]), "WHOLE_BRIDGE_PORT_SET_REQUIRED")
    result = {}
    for port in ports:
        _need(type(port) is dict, "PORT_READBACK_REQUIRED")
        port_name = _name(port.get("name"))
        _need(port_name in plan["ports"][role] and port_name not in result, "UNKNOWN_OR_DUPLICATE_BRIDGE_PORT")
        flags = {"multicast_fast_leave": iptv._uint(port.get("multicast_fast_leave"), maximum=1)}
        dms = port.get("multicast_to_unicast")
        if dms is not None:
            flags["multicast_to_unicast"] = iptv._uint(dms, maximum=1)
        _need(not (role == "ap" and _wifi(port_name)) or "multicast_to_unicast" in flags, "WDS_DMS_READBACK_REQUIRED")
        result[port_name] = {"identity": {"name": port_name, "ifindex": aqm._positive(port.get("ifindex")),
                              "epoch": base._hash(port.get("epoch"))}, "values": flags}
    return {"identity": identity, "values": values, "ports": result}


def normalize_bundle(raw: dict, plan: dict, *, now: datetime, max_age_s=10) -> dict:
    _need(type(raw) is dict and raw.get("run_id") == plan["run_id"]
          and raw.get("source") == "qualified_stage38b_collector" and raw.get("inventory_complete") is True,
          "QUALIFIED_COMPLETE_BUNDLE_REQUIRED")
    devices = raw.get("devices")
    _need(type(devices) is dict and set(devices) == set(ROLES), "EXACT_THREE_DEVICE_BUNDLE_REQUIRED")
    result, times = {}, []
    for role in ROLES:
        device = devices[role]
        _need(type(device) is dict and device.get("device_id") == plan["device_ids"][role]
              and device.get("role") == role and device.get("run_id") == plan["run_id"], "DEVICE_ROLE_BINDING_REQUIRED")
        base._fresh(device.get("observed_at"), now, max_age_s=max_age_s)
        times.append(base._utc(device["observed_at"]))
        if role != "rocket":
            observed_aql = iptv.parse_aql_readback(device.get("aql_txq_limit"))
            capture_plan = {"device_id": plan["device_ids"][role], "run_id": plan["run_id"], "role": role,
                "expected_station_macs": plan["station_macs"][role], "fq_flows_cnt": 4096,
                "aql_limits": observed_aql["limits"], "aql_threshold": iptv._uint(device.get("aql_threshold"))}
            parsed = aqm.normalize_snapshot(device, capture_plan, now=now, max_age_s=max_age_s)
            for station in device["stations"]:
                mac = station["path"].split("/")[-2]
                limits = station.get("aql_limits")
                _need(type(limits) is dict and base._json_bytes(limits) == base._json_bytes(observed_aql["limits"]),
                      "COMPLETE_UNIFORM_PEER_AQL_REQUIRED")
                parsed["stations"][mac]["aql_limits"] = copy.deepcopy(limits)
        else:
            _need(device.get("source") == "qualified_uph_bridge_collector"
                  and device.get("firmware_release") == "8.7.11"
                  and device.get("hardware_model") == "Rocket Prism 5AC Gen2", "EXACT_ROCKET_BUILD_REQUIRED")
            parsed = {"identity": {"device_id": device["device_id"], "role": role,
                "boot_id": base.bridge._uuid(device.get("boot_id")), "netns_inode": aqm._positive(device.get("netns_inode")),
                "module_sha256": base._hash(device.get("module_sha256"))},
                "capture_seq": aqm._positive(device.get("capture_seq")),
                "monotonic_ns": aqm._positive(device.get("monotonic_ns")), "observed_at": times[-1].isoformat()}
            parsed["uph"] = _uph(device.get("uph"), parsed["identity"]["module_sha256"])
        parsed["bridge"] = _bridge(device.get("bridge"), role, plan)
        result[role] = parsed
    _need((max(times) - min(times)).total_seconds() <= 1, "SYNCHRONIZED_DEVICE_READBACKS_REQUIRED")
    return {"run_id": plan["run_id"], "devices": result}


def _check_profile(bundle, *, champion):
    _need(champion in ("v11", "v12"), "V11_OR_V12_REQUIRED")
    for role, device in bundle["devices"].items():
        if role != "rocket":
            _need(device["global_aqm"]["rw"] == _core_target(role)
                  and device["aql"]["limits"] == _aql_target(role)
                  and device["aql_threshold"] == (5000 if role == "ap" else 4000), "V11_AQM_OR_AQL_READBACK_MISMATCH")
            aqm.verify_zero_events(device)
        else:
            _need(device["uph"]["scalar"] == 5, "UPH_MCAST_LIMIT_CLOBBERED")
        bridge = device["bridge"]
        expected = {"multicast_snooping": int(role == "ap"), "multicast_querier": int(role == "ap")}
        if role != "rocket": expected["multicast_igmp_version"] = 2
        _need(bridge["values"] == expected, "IGMPV2_SINGLE_QUERIER_READBACK_MISMATCH")
        for name, port in bridge["ports"].items():
            if role == "ap" and _wifi(name):
                _need(port["values"].get("multicast_to_unicast") == 1, "AP_WDS_DMS_REQUIRED")
            if champion == "v12" and (role != "ap" or _wifi(name)):
                _need(port["values"]["multicast_fast_leave"] == 1, "V12_FAST_LEAVE_READBACK_MISMATCH")


def verify_readbacks(raw, plan, *, now: datetime, champion="v12") -> dict:
    validate_plan(plan)
    parsed = normalize_bundle(raw, plan, now=now)
    _check_profile(parsed, champion=champion)
    return {"accepted": True, "champion": champion, "snapshot_sha256": base.digest(parsed),
            "physical_acceptance": False, "receiver_delivery_proven": False}


def _same_devices(before, after):
    for role in ROLES:
        old, new = before["devices"][role], after["devices"][role]
        _need(old["identity"] == new["identity"] and old["bridge"]["identity"] == new["bridge"]["identity"]
              and set(old["bridge"]["ports"]) == set(new["bridge"]["ports"]), "DEVICE_OR_BRIDGE_EPOCH_CHANGED")
        for name, port in old["bridge"]["ports"].items():
            _need(port["identity"] == new["bridge"]["ports"][name]["identity"]
                  and set(port["values"]) == set(new["bridge"]["ports"][name]["values"]), "DYNAMIC_PORT_EPOCH_CHANGED")
        if role != "rocket": aqm._same_epochs(old, new)
        else:
            _need(old["uph"]["qualification_sha256"] == new["uph"]["qualification_sha256"], "UPH_QUALIFICATION_CHANGED")
            _need(old["uph"]["vector"][1:] == new["uph"]["vector"][1:], "UNOWNED_UPH_VECTOR_COMPONENT_CHANGED")


def _bound_trace(trace, before, after, plan, *, source):
    old, new = before["devices"]["ap"], after["devices"]["ap"]
    _need(type(trace) is dict and trace.get("source") == source and trace.get("complete") is True
          and trace.get("run_id") == plan["run_id"] and trace.get("plan_sha256") == plan["plan_sha256"]
          and trace.get("device_id") == plan["device_ids"]["ap"]
          and type(trace.get("before_seq")) is int and trace["before_seq"] == old["capture_seq"]
          and type(trace.get("after_seq")) is int and trace["after_seq"] == new["capture_seq"]
          and trace.get("window_start") == old["observed_at"] and trace.get("window_end") == new["observed_at"],
          "COMPLETE_POST_APPLY_TRACE_BINDING_REQUIRED")
    base._hash(trace.get("evidence_sha256"))


def verify_canary(baseline, before, after, plan, *, flow_witnesses, igmp_trace, write_journal, now: datetime):
    """Baseline is pre-canary; before/after are separately acquired post-apply endpoints."""
    validate_plan(plan)
    saved = normalize_bundle(baseline, plan, now=now, max_age_s=60)
    first = normalize_bundle(before, plan, now=now, max_age_s=60)
    last = normalize_bundle(after, plan, now=now)
    _check_profile(saved, champion="v11"); _check_profile(first, champion="v12"); _check_profile(last, champion="v12")
    _same_devices(saved, first); _same_devices(first, last)
    for role in ROLES:
        _need(restoration_writes(first, role) == restoration_writes(last, role),
              "ACTIVE_WINDOW_CAPTURED_PARAMETER_DRIFT")
    _need(first["devices"]["rocket"]["uph"]["vector"] == last["devices"]["rocket"]["uph"]["vector"],
          "ACTIVE_WINDOW_UPH_BUFFER_CHANGED")
    deltas = {}
    for role in ROLES:
        saved_dev, old, new = saved["devices"][role], first["devices"][role], last["devices"][role]
        _need(old["capture_seq"] > saved_dev["capture_seq"] and old["monotonic_ns"] > saved_dev["monotonic_ns"]
              and base._utc(old["observed_at"]) > base._utc(saved_dev["observed_at"]), "POST_APPLY_START_REQUIRED")
        elapsed = (new["monotonic_ns"] - old["monotonic_ns"]) / 1e9
        _need(new["capture_seq"] > old["capture_seq"] and base._utc(new["observed_at"]) > base._utc(old["observed_at"])
              and plan["min_window_s"] <= elapsed <= plan["max_window_s"], "BOUNDED_INCREASING_CANARY_WINDOW_REQUIRED")
        if role != "rocket": deltas[role] = aqm.counter_deltas(old, new)
    for device_deltas in deltas.values():
        for peer in device_deltas.values():
            _need(peer[7]["tx-packets"] == 0 and peer[7]["tx-bytes"] == 0, "TID7_AC_VO_QUERY_PREEMPTION")
    _bound_trace(igmp_trace, first, last, plan, source="qualified_igmp_tx_trace")
    queries = igmp_trace.get("queries")
    _need(type(queries) is list, "EXPLICIT_IGMP_QUERY_COVERAGE_REQUIRED")
    for query in queries:
        _need(type(query) is dict, "QUERY_OBSERVATION_REQUIRED")
        version = iptv._uint(query.get("igmp_version"), minimum=1, maximum=3)
        dscp = iptv._uint(query.get("dscp"), maximum=63)
        tid, ac = iptv._uint(query.get("tid"), maximum=7), iptv._uint(query.get("ac"), maximum=3)
        length = iptv._uint(query.get("length_bytes"), minimum=1, maximum=65535)
        _need(ac == aqm.TID_AC[tid], "QUERY_TID_AC_MAPPING_INVALID")
        _need(version != 3 and not (dscp == 48 and tid == 7 and ac == 0 and length == 72), "IGMPV3_CS6_QUERY_PREEMPTION")
    _bound_trace(flow_witnesses, first, last, plan, source="qualified_txq_flow_trace")
    rows = flow_witnesses.get("flows")
    _need(type(rows) is list and len(rows) == len(plan["flows"]), "ALL_FLOW_WITNESSES_REQUIRED")
    expected = {flow["flow_id"]: flow for flow in plan["flows"]}
    seen, trace_ids, counted = set(), set(), {}
    for row in rows:
        _need(type(row) is dict and row.get("flow_id") in expected and row["flow_id"] not in seen, "FLOW_WITNESS_INVALID")
        spec = expected[row["flow_id"]]; seen.add(row["flow_id"])
        mac, service = spec["station_mac"], spec["service"]
        tid, ac, transport = aqm.SERVICES[service]
        identity = last["devices"]["ap"]["stations"][mac]["identity"]
        _need(row.get("service") == service and row.get("station_mac") == mac and row.get("transport") == transport
              and type(row.get("observed_tid")) is int and row["observed_tid"] == tid
              and type(row.get("observed_ac")) is int and row["observed_ac"] == ac
              and row.get("path") == identity["path"] and row.get("station_epoch") == identity["station_epoch"],
              "FLOW_QOS_CLASSIFICATION_NOT_PROVEN")
        key = (mac, tid, base._hash(row.get("evidence_sha256")))
        _need(key not in trace_ids, "DUPLICATE_CLASS_FLOW_EVIDENCE"); trace_ids.add(key)
        totals = counted.setdefault((mac, tid), [0, 0])
        totals[0] += aqm._positive(row.get("matched_packets")); totals[1] += aqm._positive(row.get("matched_bytes"))
        change = deltas["ap"][mac][tid]
        _need(totals[0] <= change["tx-packets"] and totals[1] <= change["tx-bytes"], "FLOW_COUNTS_EXCEED_DEQUEUE")
    _verify_write_journal(write_journal, saved, first, last, plan)
    return {"accepted": True, "champion": "v12", "plan_sha256": plan["plan_sha256"],
            "baseline_sha256": base.digest(saved), "before_sha256": base.digest(first), "after_sha256": base.digest(last),
            "counter_deltas": deltas, "tid7_packets": 0, "receiver_delivery_proven": False,
            "physical_acceptance": False, "runtime_dispatch_allowed": False}


def restoration_writes(snapshot, role):
    """Typed captured parameters, not counters or a profile reapplier."""
    device = snapshot["devices"][role]
    writes = []
    if role != "rocket":
        writes.extend({"kind": "aqm", **write} for write in aqm.aqm_writes(device["global_aqm"]["rw"]))
        for label, index in iptv.AC_INDEX.items():
            low, high = device["aql"]["limits"][label]
            writes.append({"kind": "aql", "path": iptv.AQL_PATH, "value": f"{index} {low} {high}"})
        writes.append({"kind": "numeric", "path": "/sys/kernel/debug/ieee80211/phy0/aql_threshold",
                       "value": str(device["aql_threshold"])})
    bridge = device["bridge"]
    root = bridge["identity"]["path"]
    writes.extend({"kind": "numeric", "path": f"{root}/bridge/{field}", "value": str(value)}
                  for field, value in sorted(bridge["values"].items()))
    for name, port in sorted(bridge["ports"].items()):
        writes.extend({"kind": "numeric", "path": f"{root}/brif/{name}/{field}", "value": str(value)}
                      for field, value in sorted(port["values"].items()))
    if role == "rocket":
        writes.append({"kind": "uph_vector", "path": UPH_PATH, "value": " ".join(map(str, device["uph"]["vector"]))})
    return writes


def _verify_write_journal(journal, saved, first, last, plan):
    _need(type(journal) is dict and journal.get("source") == "qualified_fenced_write_journal"
          and journal.get("complete") is True and journal.get("run_id") == plan["run_id"]
          and journal.get("plan_sha256") == plan["plan_sha256"]
          and journal.get("baseline_sha256") == base.digest(saved)
          and journal.get("after_sha256") == base.digest(last), "COMPLETE_WRITE_JOURNAL_REQUIRED")
    base._hash(journal.get("evidence_sha256"))
    entries = journal.get("entries")
    _need(type(entries) is list and 1 <= len(entries) <= 4096, "INITIALIZATION_WRITE_JOURNAL_REQUIRED")
    latest, shared, final_values = {}, [], {}
    allowed = {role: {w["path"]: w["kind"] for w in restoration_writes(saved, role)} for role in ROLES}
    for event in entries:
        _need(type(event) is dict and event.get("role") in ROLES, "WRITE_EVENT_REQUIRED")
        role = event["role"]; dev = saved["devices"][role]
        stamp, seq = aqm._positive(event.get("monotonic_ns")), aqm._positive(event.get("write_seq"))
        previous = latest.get(role, (0, 0))
        _need(event.get("device_id") == plan["device_ids"][role] and event.get("boot_id") == dev["identity"]["boot_id"]
              and event.get("kind") == "numeric_write" and seq > previous[0] and stamp >= previous[1]
              and dev["monotonic_ns"] < stamp < first["devices"][role]["monotonic_ns"],
              "ACTIVE_WINDOW_WRITE_OR_UNBOUND_EVENT")
        latest[role] = (seq, stamp)
        path = event.get("path")
        _need(type(path) is str, "WRITE_PATH_REQUIRED")
        alias = path.removeprefix("/proc/sys/dev/uph_wifi0/") if path.startswith("/proc/sys/dev/uph_wifi0/") else None
        _need(path in allowed[role] or (role == "rocket" and alias in UPH_ALIASES), "UNOWNED_OR_QDISC_WRITE_FORBIDDEN")
        value = event.get("value")
        _need(type(value) is str and len(value) <= 256, "TYPED_NUMERIC_WRITE_REQUIRED")
        if alias is not None:
            _need(re.fullmatch(r"-?[0-9]+", value) and -2**31 <= int(value) < 2**31, "UPH_SCALAR_WRITE_REQUIRED")
        elif allowed[role][path] == "aqm":
            parts = value.split()
            _need(len(parts) == 2 and parts[0] in aqm.RW_FIELDS, "AQM_SETTER_ABI_REQUIRED")
            _need(iptv._uint(parts[1]) == _core_target(role)[parts[0]], "V11_FOUNDATION_JOURNAL_DRIFT")
        elif allowed[role][path] == "aql":
            parts = value.split()
            _need(len(parts) == 3, "AQL_SETTER_ABI_REQUIRED")
            iptv._uint(parts[0], maximum=3)
            low, high = iptv._uint(parts[1]), iptv._uint(parts[2])
            _need(low <= high, "AQL_SETTER_ORDER_INVALID")
            label = next(label for label, index in iptv.AC_INDEX.items() if index == int(parts[0]))
            _need([low, high] == _aql_target(role)[label], "V11_FOUNDATION_JOURNAL_DRIFT")
        else:
            maximum = 3 if path.endswith("multicast_igmp_version") else (2**32 - 1 if path.endswith("aql_threshold") else 1)
            minimum = 2 if path.endswith("multicast_igmp_version") else 0
            iptv._uint(value, minimum=minimum, maximum=maximum)
            final_values[(role, path)] = value
        if alias is not None: shared.append(event)
    _need(shared and shared[-1]["path"] == UPH_PATH and shared[-1]["value"] == "5", "UPH_FIVE_MUST_BE_WRITTEN_LAST")
    for role in ROLES:
        previous = {w["path"]: w["value"] for w in restoration_writes(saved, role) if w["kind"] == "numeric"}
        current = {w["path"]: w["value"] for w in restoration_writes(first, role) if w["kind"] == "numeric"}
        for (logged_role, path), value in final_values.items():
            if logged_role == role:
                _need(current.get(path) == value, "WRITE_JOURNAL_FINAL_READBACK_MISMATCH")
        for path, value in current.items():
            if value != previous.get(path):
                _need(final_values.get((role, path)) == value, "CHANGED_CONTROL_MISSING_FROM_WRITE_JOURNAL")


def generate_restoration_scripts(baseline, plan, *, qualification: dict,
                                 approved_qualification_sha256: str, now: datetime) -> dict:
    """Emit guarded per-device shell; never invoke it or install the required guard.

    The native guard's restore-exact operation skips identical controls, then
    atomically checks fenced ownership, generations and typed setter/readback.
    It restores all peer AQL effects and refuses missing/recycled objects. Final
    verify-and-release checks every captured parameter, the full UPH alias vector
    and whole inventories before releasing the independent recovery journal.
    """
    validate_plan(plan)
    saved = normalize_bundle(baseline, plan, now=now, max_age_s=60)
    saved_sha = base.digest(saved)
    _need(type(qualification) is dict and base.digest(qualification) == base._hash(approved_qualification_sha256)
          and qualification.get("source") == "independent_stage38b_restore_qualification"
          and qualification.get("plan_sha256") == plan["plan_sha256"]
          and qualification.get("baseline_sha256") == saved_sha and qualification.get("guard_path") == GUARD_PATH
          and all(qualification.get(key) is True for key in ("exclusive_independent_fence", "atomic_identity_setter_readback",
              "whole_uph_vector_and_alias_restore", "uniform_peer_aql_restore", "quiesced_traffic",
              "parameter_only_restore", "failure_retains_guard")), "RESTORE_QUALIFICATION_REQUIRED")
    guard_sha = base._hash(qualification.get("guard_sha256"))
    scripts, manifests = {}, {}
    for role in ROLES:
        writes = restoration_writes(saved, role)
        manifest = {"plan_sha256": plan["plan_sha256"], "baseline_sha256": saved_sha, "role": role,
                    "device_id": plan["device_ids"][role], "identity": saved["devices"][role]["identity"],
                    "bridge": saved["devices"][role]["bridge"], "writes": writes}
        manifest_sha = base.digest(manifest)
        manifests[role] = {**manifest, "manifest_sha256": manifest_sha}
        prefix = f"{shlex.quote(GUARD_PATH)} \"$token\" {shlex.quote(manifest_sha)}"
        lines = ["#!/bin/sh", "set -eu", "umask 077", "# Generated only. Requires pre-armed, qualified device-local recovery journal.",
                 "[ \"$#\" -eq 1 ] || exit 64", "token=$1",
                 "[ \"${#token}\" -eq 64 ] || exit 64", "case \"$token\" in *[!0-9a-f]*) exit 64;; esac",
                 f"[ -x {shlex.quote(GUARD_PATH)} ] || exit 69",
                 f"actual=$(sha256sum {shlex.quote(GUARD_PATH)})",
                 f"[ \"${{actual%% *}}\" = {shlex.quote(guard_sha)} ] || exit 69",
                 f"{prefix} assert-prearmed-quiesced {shlex.quote(saved_sha)} {shlex.quote(role)}"]
        lines.extend(f"{prefix} restore-exact {shlex.quote(w['kind'])} {shlex.quote(w['path'])} {shlex.quote(w['value'])}" for w in writes)
        lines.append(f"{prefix} verify-and-release {shlex.quote(saved_sha)}")
        scripts[role] = "\n".join(lines) + "\n"
    return {"baseline_sha256": saved_sha, "scripts": scripts, "manifests": manifests,
            "script_sha256": {role: hashlib.sha256(text.encode()).hexdigest() for role, text in scripts.items()},
            "scope": "EXACT_CAPTURED_NUMERIC_PARAMETERS_NOT_QUEUES_COUNTERS_OR_MDB_HISTORY",
            "runtime_dispatch_allowed": False, "physical_acceptance": False}
