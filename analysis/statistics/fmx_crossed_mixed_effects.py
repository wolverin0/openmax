"""Saved block-level modeling table and bounded descriptive crossover fits.

One row is one recorded arm/block window, not one RTT or independent sector.
Full endpoint packages and workload/timing/crypto/topology are retained. The
default diagnostic is block-fixed-effects OLS; no random-effect, causal or
physical acceptance is inferred. A proposed random intercept for round/block
requires exchangeable independent clusters, which these saved IDs cannot prove.
"""
from __future__ import annotations

from copy import deepcopy
import json
import math
import re

import numpy as np

OUTCOMES = ("goodput_rx_mbps", "p50_rtt_ms", "p95_rtt_ms", "p99_rtt_ms",
            "jain_fairness", "dl_goodput_mbps", "ul_goodput_mbps")
HOOKS = ("short_retry_limit", "long_retry_limit", "force_tx_status", "ani_enable",
         "airtime_flags", "fq_limit")


def canonical(value):
    """Finite canonical JSON also rejects bool-as-number at numeric call sites."""
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("Finite JSON data required") from exc


def number(value, name, *, optional=False, minimum=0):
    if value is None and optional:
        return None
    try:
        valid = type(value) in (int, float) and math.isfinite(value) and value >= minimum
    except (OverflowError, TypeError, ValueError):
        valid = False
    if not valid:
        raise ValueError(f"Invalid finite {name}")
    return float(value)


def record_identity(record):
    if not isinstance(record, dict):
        raise ValueError("Record object required")
    rid, iteration = record.get("round_id"), record.get("iteration")
    if not isinstance(rid, str) or not re.fullmatch(r"R(?:[1-9]|[1-6][0-9]|7[0-5])", rid):
        raise ValueError("Only saved R1..R75 allowed")
    if not isinstance(iteration, str) or not iteration.strip():
        raise ValueError("Nonempty iteration required")
    return rid, iteration


def full_package(record):
    """Match normalized endpoint identity: ACK fields and shared hooks included."""
    record_identity(record)
    endpoints = []
    for side in ("ap", "cpe"):
        raw = record.get(side + "_policy")
        if raw is not None and not isinstance(raw, dict):
            raise ValueError("Endpoint policy must be object or unknown")
        policy = deepcopy(raw)
        if policy is not None:
            for name in ("ack_pps", "tcp_ack_vi", "ack_burst"):
                if side + "_" + name in record:
                    policy[name] = record[side + "_" + name]
            for name in HOOKS:
                if name in record:
                    policy[name] = record[name]
            pairs = policy.get("aql_by_ac")
            if not isinstance(pairs, (list, tuple)) or len(pairs) != 4 or any(
                not isinstance(pair, (list, tuple)) or len(pair) != 2
                or any(type(x) is not int or x < 0 for x in pair) or pair[0] > pair[1]
                for pair in pairs
            ):
                raise ValueError("Four exact nonnegative ordered AQL pairs required")
            if type(policy.get("dscp_micro_vo_steering")) is not bool:
                raise ValueError("Declared DSCP bool required")
            for name, value in policy.items():
                if name in ("aql_by_ac", "dscp_micro_vo_steering") or value is None:
                    continue
                if name == "encryption_mode":
                    if not isinstance(value, str):
                        raise ValueError("Encryption declaration must be string")
                elif name == "tcp_ack_vi":
                    if type(value) is not bool:
                        raise ValueError("ACK VI declaration must be bool")
                elif type(value) is not int or value < 0:
                    raise ValueError("Declared control must be exact nonnegative integer")
        endpoints.append(policy)
    canonical(endpoints)
    return endpoints


def context(record):
    regime = record.get("workload_regime")
    if not isinstance(regime, str) or not regime:
        raise ValueError("Workload regime required")
    flows = record.get("active_flow_count")
    if type(flows) is not int or not 1 <= flows <= 64:
        raise ValueError("Exact positive flow count required")
    if type(record.get("bidirectional")) is not bool:
        raise ValueError("Bidirectional must be bool")
    distance, coverage = record.get("distance_meters"), record.get("coverage_class")
    for value in (distance, coverage):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("Exact nonnegative timing settings or unknown required")
    cipher = record.get("encryption_mode")
    if cipher is not None and not isinstance(cipher, str):
        raise ValueError("Encryption context must be string or unknown")
    peers = record.get("associated_cpes", [])
    if not isinstance(peers, (list, tuple)) or any(not isinstance(x, str) for x in peers):
        raise ValueError("Declared peer list required")
    return dict(workload_regime=regime, active_flow_count=flows,
                bidirectional=record["bidirectional"], distance_meters=distance,
                coverage_class=coverage, encryption_mode=cipher,
                associated_cpes=list(peers))


def quality_reasons(value, prefix="window"):
    if not isinstance(value, dict):
        raise ValueError("Quality object required")
    reasons = []
    restored = value.get("restoration_verified")
    if restored is not None and type(restored) is not bool:
        raise ValueError("Restoration must be bool or unknown")
    drops = value.get("station_drops")
    if drops is not None and (type(drops) is not int or drops < 0):
        raise ValueError("Station drops must be exact nonnegative integer")
    loss = number(value.get("packet_loss_pct"), "packet loss", optional=True)
    if loss is not None and loss > 100:
        raise ValueError("Packet loss exceeds100")
    if restored is not True:
        reasons.append(prefix + "_restoration_false_or_unknown")
    if drops != 0:
        reasons.append(prefix + "_drops_positive_or_unknown")
    if loss != 0:
        reasons.append(prefix + "_loss_positive_or_unknown")
    failure = value.get("source_failure_metadata")
    if failure is not None:
        if not isinstance(failure, dict):
            raise ValueError("Failure metadata object required")
        for key in ("crash", "disqualified"):
            flag = failure.get(key)
            if flag is not None and type(flag) is not bool:
                raise ValueError("Failure flag must be bool or unknown")
            if flag is True:
                reasons.append(prefix + "_" + key)
    return reasons


def build_crossed_table(dataset, blocks):
    """Join without silently dropping source-negative, unknown or sequential rows."""
    if not isinstance(dataset, dict) or not isinstance(dataset.get("records"), list):
        raise ValueError("Canonical records object required")
    if not isinstance(blocks, dict) or not isinstance(blocks.get("crossed"), list) or not isinstance(blocks.get("sequential"), list):
        raise ValueError("Crossed/sequential lists required")
    if len(dataset["records"]) > 512 or len(blocks["crossed"]) > 4096:
        raise ValueError("Bounded saved corpus exceeded")
    lookup = {}
    for record in dataset["records"]:
        key = record_identity(record)
        if key in lookup:
            raise ValueError("Duplicate record identity")
        lookup[key] = record
    rows, seen = [], set()
    for block in blocks["crossed"]:
        if not isinstance(block, dict):
            raise ValueError("Block object required")
        key = (block.get("round_id"), block.get("treatment_id"))
        if key not in lookup:
            raise ValueError("Unbound block treatment")
        index = block.get("block_index")
        if type(index) is not int or not 0 <= index <= 1024:
            raise ValueError("Exact bounded block index required")
        identity = (*key, index)
        if identity in seen:
            raise ValueError("Duplicate arm/block identity")
        seen.add(identity)
        record = lookup[key]
        package = full_package(record)
        ctx = context(record)
        observation = block.get("observation")
        if not isinstance(observation, dict):
            raise ValueError("Block observation required")
        step = block.get("crossover_step")
        if step is not None and (type(step) is not int or not 0 <= step <= 15):
            raise ValueError("Crossover step must be bounded exact integer or unknown")
        values = {name: number(block.get(name) if name in ("dl_goodput_mbps", "ul_goodput_mbps") else observation.get(name), name, optional=True) for name in OUTCOMES}
        reasons = quality_reasons(record)
        # Some older blocks do not carry health. Keep unknown instead of copying
        # window health into a supposed independently measured block observation.
        reasons += quality_reasons(observation, "block")
        if isinstance(record.get("summary_consistency"), dict) and record["summary_consistency"].get("consistent") is False:
            reasons.append("source_summary_inconsistent")
        rows.append(dict(round_id=key[0], treatment_id=key[1], block_index=index,
                         round_scoped_block_id=[key[0], index], period=step,
                         policy_id=canonical(package), endpoint_policies=package,
                         context=ctx, context_id=canonical(ctx), outcomes=values,
                         source_position=block.get("source_position"),
                         window_source_position=record.get("source_position"),
                         quality_reasons=reasons, descriptive_fit_eligible=not reasons,
                         source_block=deepcopy(block)))
    return dict(schema_version=1, rows=rows,
                sequential_rows_excluded_from_crossed_model=deepcopy(blocks["sequential"]),
                counts=dict(records=len(lookup), crossed_rows=len(rows),
                            matched_round_scoped_ids=len({tuple(x["round_scoped_block_id"]) for x in rows}),
                            sequential_rows=len(blocks["sequential"])),
                random_effects_specification={"candidate": "round/block-within-round intercepts", "fitted": False,
                    "assumptions_unverified": ["Independent exchangeable rounds/clusters", "Random-effect distribution", "Randomization/washout", "Independent sector replication"]},
                limits=["Timing distance is not verified physical range", "Policies are packages, not separately randomized knobs", "RTT subsamples are not independent windows"],
                automatic_execution_allowed=False, physical_acceptance=False)


def crossover_design(table, round_id, treatment_id, *, include_carryover=True):
    if type(include_carryover) is not bool:
        raise ValueError("Explicit carryover bool required")
    rows = [x for x in table["rows"] if x["round_id"] == round_id]
    arms = {x["treatment_id"] for x in rows}
    if len(arms) != 2 or treatment_id not in arms:
        raise ValueError("One exact two-arm round required")
    indices = sorted({x["block_index"] for x in rows})
    if not 2 <= len(indices) <= 128:
        raise ValueError("Bounded2..128 blocks required")
    ordered, matrix = [], []
    for index in indices:
        pair = sorted((x for x in rows if x["block_index"] == index), key=lambda x: -1 if x["period"] is None else x["period"])
        if len(pair) != 2 or [x["period"] for x in pair] != [0, 1] or len({x["treatment_id"] for x in pair}) != 2:
            raise ValueError("Both actual periods and arms required in every block")
        for position, row in enumerate(pair):
            fixed = [1.0] + [float(index == k) for k in indices[1:]]
            fixed += [float(position), float(row["treatment_id"] == treatment_id)]
            if include_carryover:
                fixed += [float(position == 1 and pair[0]["treatment_id"] == treatment_id)]
            ordered.append(row)
            matrix.append(fixed)
    x = np.asarray(matrix)
    rank = int(np.linalg.matrix_rank(x))
    return ordered, x, dict(rows=len(x), columns=x.shape[1], rank=rank,
                           estimable=rank == x.shape[1], include_carryover=include_carryover,
                           terms=["intercept"] + [f"block:{k}" for k in indices[1:]] + ["period", "current_treatment"] + (["lag_treatment"] if include_carryover else []))


def fit_descriptive_crossover(table, round_id, treatment_id, outcome="p95_rtt_ms", *, include_carryover=True):
    if outcome not in OUTCOMES:
        raise ValueError("Unknown outcome")
    rows, x, diagnostic = crossover_design(table, round_id, treatment_id, include_carryover=include_carryover)
    result = dict(status="NOT_ESTIMABLE" if not diagnostic["estimable"] else "SOURCE_QUALITY_BLOCKED",
                  diagnostic=diagnostic, coefficients=None, causal_acceptance=False,
                  random_effects_fitted=False, automatic_execution_allowed=False,
                  assumptions=["Restricted model assumes no differential carryover" if not include_carryover else "Full model requires separable current/lag effects", "Saved order is not proof of randomization", "No independent sector inference or causal p values"])
    if not diagnostic["estimable"]:
        return result
    if any(not row["descriptive_fit_eligible"] or row["outcomes"][outcome] is None for row in rows):
        return result
    y = np.asarray([row["outcomes"][outcome] for row in rows])
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    result.update(status="FITTED_DESCRIPTIVE_RESTRICTED_OLS", coefficients=dict(zip(diagnostic["terms"], beta.tolist())), residual_rmse=float(np.sqrt(np.mean((x @ beta - y) ** 2))), p_values=None)
    return result
