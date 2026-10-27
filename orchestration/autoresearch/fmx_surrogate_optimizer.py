"""Exploratory saved-package surrogate, grouped validation and disabled proposals.

Reuses the established DOE module's nondominance routine, not its R1/R2-only
training adapter. All declared numeric endpoint fields enter an RBF ridge model
with unknown masks; exact context partitions prevent workload/crypto/timing
mixing. Outcomes/retry telemetry never enter predictors. No synthesized policy,
statistical promotion, actuation, or independent-sector accuracy claim.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import math

import numpy as np

from analysis.statistics.fmx_crossed_mixed_effects import (
    canonical, context, full_package, number, quality_reasons, record_identity,
)
from orchestration.autoresearch.fmx_doe_and_pymoo_optimizer import nondominated_indices

METRICS = ("goodput_mbps", "p95_ms", "p99_ms")


def _flatten(value, prefix=""):
    out = {}
    if isinstance(value, dict):
        for key, item in sorted(value.items()):
            if not isinstance(key, str):
                raise ValueError("String policy keys required")
            out.update(_flatten(item, prefix + "." + key))
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            out.update(_flatten(item, prefix + f"[{i}]"))
    elif value is None or type(value) in (bool, int, float, str):
        if type(value) in (int, float):
            number(value, "policy coordinate")
        out[prefix] = value
    else:
        raise ValueError("Unsupported policy coordinate")
    return out


def _response(record):
    return np.asarray([number(record.get(k), k) for k in METRICS])


def _eligible(record):
    record_identity(record)
    context(record)
    full_package(record)
    reasons = quality_reasons(record)
    if record.get("window_kind", "primary") != "primary":
        reasons.append("not_primary_window")
    consistency = record.get("summary_consistency")
    if consistency is not None:
        if not isinstance(consistency, dict) or type(consistency.get("consistent")) is not bool:
            raise ValueError("Typed summary consistency required")
        if consistency["consistent"] is False:
            reasons.append("source_summary_inconsistent")
    if any(record.get(k) is None for k in METRICS):
        reasons.append("missing_response")
    else:
        _response(record)
    return reasons


def _package_id(record):
    return canonical(full_package(record))


def _context_id(record):
    return canonical(context(record))


class SavedPackageSurrogate:
    """Training-only feature encoding/scaling, no outcome-derived covariates."""
    def __init__(self, records, *, ridge=0.2, length_scale=1.0):
        ridge = number(ridge, "ridge", minimum=1e-8)
        length_scale = number(length_scale, "length_scale", minimum=1e-3)
        if ridge > 100 or length_scale > 100 or not 2 <= len(records) <= 256:
            raise ValueError("Bounded2..256 records and hyperparameters required")
        self.records = deepcopy(list(records))
        identities = [record_identity(r) for r in self.records]
        if len(set(identities)) != len(identities):
            raise ValueError("Duplicate training identities")
        if any(_eligible(r) for r in self.records):
            raise ValueError("Ineligible training data")
        ids = {_context_id(r) for r in self.records}
        if len(ids) != 1:
            raise ValueError("Fit one exact workload/timing/crypto/topology context")
        self.context_id = ids.pop()
        flat = [_flatten(full_package(r)) for r in self.records]
        self.keys = sorted(set().union(*(x.keys() for x in flat)))
        self.types = {}
        self.categories = {}
        for key in self.keys:
            values = [x.get(key) for x in flat if x.get(key) is not None]
            kinds = {"str" if isinstance(x, str) else "bool" if type(x) is bool else "number" for x in values}
            if len(kinds) > 1:
                raise ValueError("Inconsistent policy coordinate type")
            self.types[key] = next(iter(kinds), "unknown")
            self.categories[key] = sorted(set(values)) if kinds == {"str"} else []
        raw = np.asarray([self._encode_flat(x) for x in flat])
        self.mean = raw.mean(axis=0)
        self.scale = raw.std(axis=0)
        self.scale[self.scale == 0] = 1
        self.x = (raw - self.mean) / self.scale
        self.y = np.asarray([_response(r) for r in self.records])
        self.y_mean = self.y.mean(axis=0)
        self.length_scale = length_scale
        dist = np.sum((self.x[:, None] - self.x[None, :]) ** 2, axis=2)
        self.coefficients = np.linalg.solve(np.exp(-dist / (2 * length_scale ** 2)) + ridge * np.eye(len(self.x)), self.y - self.y_mean)

    def _encode_flat(self, flat):
        values = []
        for key in self.keys:
            item = flat.get(key)
            kind = self.types[key]
            if item is not None:
                if kind == "str" and (not isinstance(item, str) or item not in self.categories[key]):
                    raise ValueError("Unseen categorical coordinate")
                if kind == "bool" and type(item) is not bool:
                    raise ValueError("Boolean coordinate required")
                if kind == "number" and type(item) not in (int, float):
                    raise ValueError("Numeric coordinate required")
                if kind == "unknown":
                    raise ValueError("Previously unknown coordinate has no training support")
            values.append(float(item is not None))
            if kind == "str":
                values.extend(float(item == cat) for cat in self.categories[key])
            else:
                values.append(0 if item is None else float(item))
        if set(flat) - set(self.keys):
            raise ValueError("Unseen policy coordinate")
        return values

    def predict(self, record):
        record_identity(record)
        if _context_id(record) != self.context_id:
            raise ValueError("Unsupported context")
        raw = np.asarray(self._encode_flat(_flatten(full_package(record))))
        query = (raw - self.mean) / self.scale
        distance = np.linalg.norm(self.x - query, axis=1)
        weights = np.exp(-distance ** 2 / (2 * self.length_scale ** 2))
        prediction = self.y_mean + weights @ self.coefficients
        if not np.isfinite(prediction).all():
            raise ValueError("Nonfinite prediction")
        # Do not silently project poor fits into plausible radio measurements.
        return dict(zip(METRICS, map(float, prediction)),
                    nearest_feature_distance=float(distance.min()),
                    prediction_kind="EXPLORATORY_NOT_PHYSICAL_OR_PROMOTION",
                    output_geometry_valid=bool(np.all(prediction >= 0) and prediction[2] >= prediction[1]),
                    automatic_execution_allowed=False)


def grouped_validation(records, *, max_rounds=75):
    """Hold out whole rounds AND every package appearing in that test round.

    A fold with no support is reported, not replaced by an in-sample score.
    Exact context and full package identities include every observed hook.
    """
    if type(max_rounds) is not int or not 1 <= max_rounds <= 75:
        raise ValueError("Bounded1..75 folds required")
    if len(records) > 256:
        raise ValueError("Bounded corpus required")
    eligible, excluded = [], []
    seen = set()
    for record in records:
        identity = record_identity(record)
        if identity in seen:
            raise ValueError("Duplicate observation")
        seen.add(identity)
        reasons = _eligible(record)
        if reasons:
            excluded.append(dict(identity=list(identity), reasons=reasons))
        else:
            eligible.append(record)
    rounds = sorted({r["round_id"] for r in eligible}, key=lambda x: int(x[1:]))
    if len(rounds) > max_rounds:
        raise ValueError("Round budget exceeded; do not silently truncate validation")
    folds, errors, baselines = [], [], []
    for rid in rounds:
        test_all = [r for r in eligible if r["round_id"] == rid]
        held_packages = {_package_id(r) for r in test_all}
        train_all = [r for r in eligible if r["round_id"] != rid and _package_id(r) not in held_packages]
        for ctx in sorted({_context_id(r) for r in test_all}):
            train = [r for r in train_all if _context_id(r) == ctx]
            test = [r for r in test_all if _context_id(r) == ctx]
            fold = dict(held_out_round=rid, context_id=ctx,
                        held_out_package_ids=sorted(held_packages),
                        train_ids=[list(record_identity(r)) for r in train],
                        test_ids=[list(record_identity(r)) for r in test],
                        training_package_ids=sorted({_package_id(r) for r in train}))
            assert not held_packages.intersection(fold["training_package_ids"])
            if len(train) < 2 or len({_package_id(r) for r in train}) < 2:
                fold.update(status="NO_LEAK_FREE_TRAINING_SUPPORT", predictions=[])
            else:
                try:
                    model = SavedPackageSurrogate(train)
                    predictions, fold_errors, fold_baselines = [], [], []
                    for row in test:
                        prediction = model.predict(row)
                        error = np.asarray([prediction[k] for k in METRICS]) - _response(row)
                        baseline_error = model.y_mean - _response(row)
                        predictions.append(dict(identity=list(record_identity(row)), prediction=prediction,
                                                error=error.tolist(), training_mean_error=baseline_error.tolist()))
                        fold_errors.append(error)
                        fold_baselines.append(baseline_error)
                    errors.extend(fold_errors)
                    baselines.extend(fold_baselines)
                    fold.update(status="PREDICTED_HELD_OUT", predictions=predictions)
                except ValueError as exc:
                    fold.update(status="UNSUPPORTED_TRAINING_FEATURE", reason=str(exc), predictions=[])
            folds.append(fold)
    return dict(method="LEAVE_ROUND_AND_ALL_TEST_PACKAGES_OUT_EXACT_CONTEXT", folds=folds,
                excluded=excluded, outcome_order=list(METRICS), predicted_windows=len(errors),
                rmse=np.sqrt(np.mean(np.asarray(errors) ** 2, axis=0)).tolist() if errors else None,
                training_mean_rmse=np.sqrt(np.mean(np.asarray(baselines) ** 2, axis=0)).tolist() if errors else None,
                independent_sector_replications=0, automatic_execution_allowed=False,
                limitation="Conditional exploratory prediction error; no independent sector, causal or policy acceptance")


def propose_observed(records, *, max_candidates=16):
    """Disabled empirical Pareto inventory; no interpolation/optimizer enrollment."""
    if type(max_candidates) is not int or not 1 <= max_candidates <= 64 or len(records) > 256:
        raise ValueError("Bounded proposal budget required")
    groups, excluded, negative = {}, [], {}
    seen = set()
    for record in records:
        identity = record_identity(record)
        if identity in seen:
            raise ValueError("Duplicate observation")
        seen.add(identity)
        _eligible(record)  # Type-check unknown and negative metadata first.
        reasons = quality_reasons(record)
        actual_negative = [x for x in reasons if x.endswith(("_crash", "_disqualified"))]
        if record.get("restoration_verified") is False:
            actual_negative.append("reported_restore_failed")
        if record.get("station_drops") is not None and record["station_drops"] > 0:
            actual_negative.append("reported_station_drops")
        if record.get("packet_loss_pct") is not None and record["packet_loss_pct"] > 0:
            actual_negative.append("reported_packet_loss")
        if actual_negative:
            negative.setdefault((_context_id(record), _package_id(record)), []).append(
                dict(identity=list(identity), reasons=actual_negative))
    for record in records:
        reasons = _eligible(record)
        history = negative.get((_context_id(record), _package_id(record)), [])
        if history:
            reasons.append("known_negative_package_context")
        if any(p is None for p in full_package(record)):
            reasons.append("endpoint_package_unknown")
        if reasons:
            excluded.append(dict(identity=list(record_identity(record)), reasons=reasons,
                                 known_negative_evidence=deepcopy(history)))
        else:
            groups.setdefault(_context_id(record), []).append(record)
    proposals = []
    for ctx, group in sorted(groups.items()):
        objectives = [[-r["goodput_mbps"], r["p95_ms"], r["p99_ms"]] for r in group]
        for index in nondominated_indices(np.asarray(objectives)):
            r = group[index]
            proposals.append(dict(source_identity=list(record_identity(r)), context_id=ctx,
                                  policy_id=_package_id(r), endpoint_policies=full_package(r),
                                  observed={k: r[k] for k in METRICS}, enabled=False,
                                  recorded_secondary_metrics={k: r.get(k) for k in ("dl_goodput_mbps", "ul_goodput_mbps", "jain_fairness", "mac_retry_rate")},
                                  automatic_execution_allowed=False,
                                  qualification="OBSERVED_EMPIRICAL_FRONTIER_NOT_SIGNIFICANCE_OR_SAFETY"))
    proposals.sort(key=lambda x: (x["context_id"], x["observed"]["p95_ms"], x["policy_id"], x["source_identity"]))
    return dict(proposals=proposals[:max_candidates], total_empirical_frontier=len(proposals),
                truncated=len(proposals) > max_candidates, excluded=excluded,
                source_windows=len(records), automatic_execution_allowed=False,
                physical_acceptance=False, synthesized_packages=0)
