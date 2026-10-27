"""PB050/PB060 offline conditional GP, Pareto acquisition and variable discovery.

Read retained JSON only. Never import bench recipes or provide an actuation API.
The GP models f(treatment)-f(control), with explicit AQL interactions and unknown
masks. Predictions, hypothetical priors and hardware acceptance are separate.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import numpy as np
from scipy.linalg import cho_factor, cho_solve

ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "T-PB-CODEX-050-060-BAYESIAN-SEARCH"
OUTPUT = "artifacts/physical_boundary/pb060_epistasis_surrogate_frontier_20261025.json"
STAGE13 = "orchestration/autoresearch/stage13_sync_20261025/"
PINS = {
    "orchestration/autoresearch/firmware_knob_candidates.json":
        "54cdcc8213bfdc8e909c0daae236c48a930a739bbe57153de619f6a7cd3a2f8a",
    STAGE13 + "normalized_measurements_stage13.json":
        "9cff9e62f08e575f4d6311552afcff463f1cb365961d945fae49812c46bef040",
    STAGE13 + "multiradio_110_packages.json":
        "0d5eedd210a9ec593ea4ba633c101c1258afc716a1a27ad572f057705cff4e3c",
    "artifacts/autoresearch/stage15_ltu_ptmp_sector_20261025.json":
        "2b72ba012e8a769c0dc40b1af9b175c862f2a647f9c6ed34281e94ce7cc91367",
    "artifacts/autoresearch/stage16_ltu_cross_gen_tdd_audit_20261025.json":
        "71fe59212811908abaeac126ce902f576cf22635045f5c7d92246b2d69f1940e",
    "artifacts/autoresearch/stage16_ltu_to_openwrt_feature_port_20261025.json":
        "23c6d3e8007fdc5ad8d56e2bd25b56fadb9403a48339656810b5c9cf0b1af233",
}
OBJECTIVES = ("relative_throughput_gain", "relative_p95_reduction")
REFERENCE = (-0.20, -0.50)
PRIOR_SD = (0.10, 0.30)
NOISE_SD = (0.04, 0.12)
SEED = 60050


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def finite(value: Any, label: str, *, positive: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"Finite numeric {label} required")
    if positive and value <= 0:
        raise ValueError(f"Positive {label} required")
    return float(value)


def _no_duplicate_keys(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"Duplicate JSON key: {key}")
        out[key] = value
    return out


def read_bound(root: Path, relative: str, expected_sha256: str):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Input outside repository")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected_sha256:
        raise ValueError(f"Input digest mismatch: {relative}")
    data = json.loads(raw, object_pairs_hook=_no_duplicate_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    return data, dict(path=relative, bytes=len(raw), sha256=digest)


def flatten(value, prefix=""):
    out = {}
    if isinstance(value, dict):
        for key, item in sorted(value.items()):
            out.update(flatten(item, f"{prefix}.{key}" if prefix else key))
    elif isinstance(value, (list, tuple)):
        for i, item in enumerate(value):
            out.update(flatten(item, f"{prefix}.{i}"))
    elif value is None or type(value) in (str, int, float, bool):
        if type(value) in (int, float):
            finite(value, prefix)
        out[prefix] = value
    else:
        raise ValueError("Unsupported control coordinate")
    return out


def _wa_policy(record):
    """Unify declared controls without promoting recipes to effective readback."""
    audit = record.get("recipe_control_audit", {}).get("actual_declared_controls")
    if audit:
        result = flatten({"endpoint": audit["endpoint_controls"],
                          "lower": audit.get("lower_controls"),
                          "htt": audit.get("recipe_declared_endpoint_htt_pairs"),
                          "rts": audit.get("recipe_declared_rts_threshold")})
    else:
        canonical_endpoints = json.loads(record["policy_key"]) if record.get("policy_key") else None
        if canonical_endpoints is not None and (not isinstance(canonical_endpoints, list) or len(canonical_endpoints) != 2):
            raise ValueError("Historical complete AP/CPE policy pair required")
        endpoints = {}
        for index, endpoint in enumerate(("ap", "cpe")):
            # The canonical source-bound package retains lower controls omitted
            # by the older ap_policy/cpe_policy convenience views.
            policy = deepcopy(canonical_endpoints[index] if canonical_endpoints is not None
                              else record.get(endpoint + "_policy"))
            if policy is None:
                endpoints[endpoint] = None
                continue
            aql = policy.pop("aql_by_ac", None)
            if aql is not None:
                # OfflineWirelessPolicy's canonical order is VO/VI/BE/BK.
                for ac, pair in zip(("vo", "vi", "be", "bk"), aql):
                    policy[ac + "_low_us"], policy[ac + "_high_us"] = pair
            for context_key in ("distance_meters", "encryption_mode"):
                policy.pop(context_key, None)
            endpoints[endpoint] = policy
        result = flatten({"endpoint": endpoints})
        # These literal-coordinate records are additional source-bound controls;
        # never substitute narrative source_candidate_metadata or outcome fields.
        for key in ("literal_control_coordinates", "new_source_controls", "compound_recipe_controls"):
            if key in record:
                result.update(flatten(record[key], key))
    return result


def _round_order(round_id):
    match = re.fullmatch(r"(.*?)(\d+)", round_id)
    if not match:
        raise ValueError("Numbered round identity required")
    return match[1], int(match[2])


@dataclass(frozen=True)
class Comparison:
    round_id: str
    context: str
    baseline: dict
    treatment: dict
    outcome: tuple[float, float]
    baseline_metrics: tuple[float, float]
    treatment_metrics: tuple[float, float]
    source: dict
    quality: dict
    evidence_kind: str

    @property
    def package_id(self):
        return canonical(self.treatment)

    @property
    def model_outcome(self):
        # Exact additive latent contrasts are log-ratios, not relative ratios.
        return (math.log1p(self.outcome[0]), -math.log1p(-self.outcome[1]))

    @property
    def front_eligible(self):
        return (self.quality.get("loss_pct") == 0
                and self.quality.get("restoration_reported") is True
                and self.quality.get("station_drops") == 0
                and not self.quality.get("disqualified", False))


def comparison(round_id, context, baseline, treatment, a, b, source, quality, kind):
    ag, ap = (finite(x, "baseline response", positive=True) for x in a)
    bg, bp = (finite(x, "treatment response", positive=True) for x in b)
    return Comparison(round_id, canonical(context), baseline, treatment,
                      (bg / ag - 1, 1 - bp / ap), (ag, ap), (bg, bp),
                      source, quality, kind)


def _wa_context(row):
    return dict(radio="WA_LAP120_LOCO195", firmware="SAVED_BUILD_UNVERIFIED",
                firmware_join_verified=False, metric="SAVED_IP_GOODPUT_MBPS",
                workload=row["workload_regime"], flows=row.get("active_flow_count"),
                bidirectional=row.get("bidirectional"), distance_m=row.get("distance_meters"),
                coverage_class=row.get("coverage_class"), slot_us=row.get("slot_time_us"),
                ack_us=row.get("ack_timeout_us"), cipher=row.get("encryption_mode", "psk2"),
                cpe_count=1, topology="INFERRED_SINGLE_LINK_NOT_LIVE_READBACK")


def _phase_metrics(phase):
    """Keep SSH, OTA payload and HTTP timing in different objective spaces."""
    p95 = next((phase[k] for k in ("p95_ms", "ota_p95_ms", "p95_rtt_ms") if k in phase), None)
    for key, factor, semantics in (
        ("ssh_stream_mbps", 1, "SSH_STREAM_NOT_OTA_MBPS"),
        ("aggregate_goodput_mbps", 1, "THREE_HOST_SSH_STREAM_NOT_SECTOR_CAPACITY"),
        ("ota_payload_kbps", .001, "OTA_PAYLOAD_MBPS"),
        ("ota_kbps", .001, "OTA_PAYLOAD_MBPS"),
        ("ota_http_5req_s", None, "HTTP_FIVE_REQUESTS_PER_SECOND_DERIVED"),
    ):
        if key in phase:
            value = finite(phase[key], key, positive=True)
            return (5 / value if factor is None else factor * value,
                    finite(p95, "p95", positive=True)), semantics
    raise ValueError("No comparable throughput proxy in phase")


def _aggregate_comparison(item, *, source, context):
    phases = item.get("phases", item)
    metrics = [_phase_metrics(phases[k]) for k in ("A1", "A2", "B1", "B2")]
    if len({x[1] for x in metrics}) != 1:
        raise ValueError("Incompatible phase metric semantics")
    context = dict(context, metric=metrics[0][1])
    a = np.mean([x[0] for x in metrics[:2]], axis=0).tolist()
    b = np.mean([x[0] for x in metrics[2:]], axis=0).tolist()
    declared = item.get("declared_controls", item)
    # Opaque recipe text is never executed or semantically equated to another API.
    base = {"source_package": canonical({k: declared.get(k) for k in
            ("knob", "baseline_val", "cmd_a", "ap_revert", "cpe_revert")})}
    target = {"source_package": canonical({k: declared.get(k) for k in
              ("knob", "candidate_val", "cmd_b", "ap_apply", "cpe_apply")})}
    losses = [phases[k].get("loss_pct", phases[k].get("ota_loss_pct")) for k in ("A1", "A2", "B1", "B2")]
    quality = dict(loss_pct=max(losses) if all(x is not None for x in losses) else None,
                   restoration_reported=None, station_drops=None,
                   raw_trial_samples=False, effective_control_verified=False)
    return comparison(item["round_id"], context, base, target, a, b, source, quality,
                      "FOUR_PHASE_AGGREGATES_ONE_ROUND_NOT_FOUR_TRIALS")


def load_search_evidence(root: Path = ROOT):
    data, bindings = {}, []
    for path, digest in PINS.items():
        data[path], pin = read_bound(root, path, digest)
        bindings.append(pin)
    catalog = data["orchestration/autoresearch/firmware_knob_candidates.json"]["knobs"]
    if len(catalog) != 571 or len({k["id"] for k in catalog}) != 571:
        raise ValueError("Expected571 unique catalog IDs")
    if any(k.get("enabled") is not False for k in catalog):
        raise ValueError("This offline frontier requires a disabled source catalog")
    saved = data[STAGE13 + "normalized_measurements_stage13.json"]
    records = saved["records"]
    by_round = defaultdict(list)
    for row in records:
        if row.get("window_kind", "primary") == "primary":
            by_round[row["round_id"]].append(row)
    sources = {(r["round_id"] if "round_id" in r else f"R{r['round']}"): r
               for r in saved["source_refs"] if "round_id" in r or "round" in r}
    comparisons, excluded = [], []
    for rid, rows in sorted(by_round.items(), key=lambda kv: _round_order(kv[0])):
        baseline = rows[0]
        for row in rows[1:]:
            if _wa_context(row) != _wa_context(baseline):
                excluded.append(dict(round_id=rid, source_pointer=row["source_position"],
                                     reason="WITHIN_ROUND_CONTEXT_CHANGED_NO_MATCHED_BASELINE",
                                     baseline_context=_wa_context(baseline), treatment_context=_wa_context(row)))
                continue
            try:
                comparisons.append(comparison(
                    rid, _wa_context(row), _wa_policy(baseline), _wa_policy(row),
                    (baseline["goodput_mbps"], baseline["p95_ms"]),
                    (row["goodput_mbps"], row["p95_ms"]),
                    dict(sources[rid], baseline_pointer=baseline["source_position"],
                         treatment_pointer=row["source_position"]),
                    dict(loss_pct=max(baseline["packet_loss_pct"], row["packet_loss_pct"])
                         if None not in (baseline.get("packet_loss_pct"), row.get("packet_loss_pct")) else None,
                         restoration_reported=baseline.get("restoration_verified") is True
                         and row.get("restoration_verified") is True,
                         station_drops=max(baseline.get("station_drops", 0), row.get("station_drops", 0)),
                         disqualified=row.get("source_failure_metadata", {}).get("disqualified", False),
                         effective_control_verified=False, raw_trial_samples=bool(row.get("repetition_blocks"))),
                    "SAVED_WINDOWS_ONE_ROUND_CLUSTER"))
            except (ValueError, KeyError, TypeError) as exc:
                excluded.append(dict(round_id=rid, reason=str(exc), source_pointer=row.get("source_position")))
    multi = data[STAGE13 + "multiradio_110_packages.json"]["packages"]
    stage15 = data["artifacts/autoresearch/stage15_ltu_ptmp_sector_20261025.json"]
    for item in multi:
        radio = item["round_id"].split("-R")[0]
        context = dict(radio=radio, firmware="SAVED_BUILD_UNVERIFIED",
                       firmware_join_verified=False, workload="SAVED_PHASE_PROXY",
                       acquisition_source=item["source"]["sha256"], cpe_count=None)
        try:
            comparisons.append(_aggregate_comparison(item, source=dict(item["source"], pointer=item["source_pointer"]), context=context))
        except (ValueError, KeyError, TypeError) as exc:
            excluded.append(dict(round_id=item["round_id"], reason=str(exc)))
    for i, item in enumerate(stage15["rounds"]):
        context = dict(radio="LTU-S15", firmware=[x["firmware"] for x in stage15["units"]],
                       firmware_join_verified=False, workload="THREE_WIRED_HOST_PROXY_NO_ASSOCIATED_LINK",
                       cpe_count=2, associated_cpe_count=0, frequency_mhz=5825, width_mhz=20)
        try:
            comparisons.append(_aggregate_comparison(item, source=dict(bindings[3], pointer=f"/rounds/{i}"), context=context))
        except (ValueError, KeyError, TypeError) as exc:
            excluded.append(dict(round_id=item["round_id"], reason=str(exc)))
    observed = set(by_round) | {x["round_id"] for x in multi} | {x["round_id"] for x in stage15["rounds"]}
    requested = {f"R{i}" for i in range(1, 195)}
    for prefix, end in (("PBM5", 36), ("R5AC", 21), ("R2AC", 21), ("LTU", 20), ("LTU-S15", 8), ("AF4X", 20)):
        requested.update(f"{prefix}-R{i}" for i in range(1, end + 1))
    if observed - requested:
        raise ValueError("Unexpected round identities")
    audit = dict(requested_rounds=len(requested), observed_unique_rounds=len(observed),
                 observed_round_ids=sorted(observed, key=_round_order),
                 missing_round_ids=sorted(requested - observed, key=_round_order),
                 family_counts=dict(Counter(r.split("-R")[0] if "-R" in r else "WA" for r in observed)),
                 normalized_windows=len(records), comparisons=len(comparisons), excluded_comparisons=excluded,
                 phase_aggregates_expanded_to_raw_trials=False,
                 stage16_new_measurement_rounds=0,
                 stage16_role="AUDIT_AND_PORT_REPORTS_EXCLUDED_FROM_TRAINING",
                 input_validation="EXACT_SEALED_STAGE13_SNAPSHOTS_AND_RAW_STAGE15_STAGE16_SHA256",
                 effective_firmware_control_verified=False)
    return dict(catalog=catalog, comparisons=comparisons, records=records, audit=audit, inputs=bindings)


class StateEncoder:
    """Training-only encoding, separate AP/CPE values and known/unknown masks."""
    def __init__(self, states):
        self.keys = sorted(set().union(*(s.keys() for s in states)))
        self.spec = {}
        for key in self.keys:
            values = [s[key] for s in states if s.get(key) is not None]
            kinds = {"number" if type(v) in (int, float, bool) else "category" for v in values}
            if len(kinds) > 1:
                # An API may use 'off' beside numeric RTS values. Treat all as categories.
                kinds = {"category"}
            kind = next(iter(kinds), "unknown")
            if kind == "number":
                array = np.asarray(values, dtype=float)
                self.spec[key] = kind, float(array.mean()), max(float(array.std()), 1.0)
            else:
                self.spec[key] = kind, sorted({canonical(v) for v in values}), None

    def encode(self, state):
        if set(state) - set(self.keys):
            raise ValueError("Unseen control coordinate; use prior-only research priority")
        values, numeric = [], {}
        for key in self.keys:
            item = state.get(key)
            kind, center, scale = self.spec[key]
            values.append(float(item is not None))
            if kind == "number":
                z = 0.0 if item is None else (finite(float(item), key) - center) / scale
                values.append(z)
                numeric[key] = z if item is not None else None
            elif kind == "category":
                encoded = canonical(item)
                if item is not None and encoded not in center:
                    raise ValueError("Unseen categorical value; unsupported posterior")
                values.extend(float(item is not None and encoded == v) for v in center)
            elif item is not None:
                raise ValueError("Previously unknown control has no observed value")
        # These state products preserve the baseline dependence lost by delta-only models.
        for endpoint in ("ap", "cpe"):
            prefix = f"endpoint.{endpoint}."
            aql = numeric.get(prefix + "be_low_us")
            for knob in ("fq_quantum_bytes", "fq_target_us", "fq_interval_us"):
                other = numeric.get(prefix + knob)
                values.extend((float(aql is not None and other is not None),
                               aql * other if aql is not None and other is not None else 0.0))
        return np.asarray(values, dtype=float)


class EpistasisSurrogate:
    """Zero-mean contrast GP with a PSD RBF+linear state kernel.

    Independent objective GPs; fixed declared priors/noise, no hidden fitting on
    held-out outcomes. Covariance is latent response uncertainty, not a hardware CI.
    """
    def __init__(self, observations, *, prior_sd=PRIOR_SD, noise_sd=NOISE_SD):
        if not observations or len(observations) > 1024:
            raise ValueError("Bounded nonempty training observations required")
        if len({x.context for x in observations}) != 1:
            raise ValueError("Fit one exact radio/workload/timing/metric context")
        self.context = observations[0].context
        self.observations = list(observations)
        self.encoder = StateEncoder([s for x in observations for s in (x.baseline, x.treatment)])
        self.a = np.asarray([self.encoder.encode(x.baseline) for x in observations])
        self.b = np.asarray([self.encoder.encode(x.treatment) for x in observations])
        self.y = np.asarray([x.model_outcome for x in observations])
        self.prior_sd = np.asarray([finite(v, "prior SD", positive=True) for v in prior_sd])
        self.noise_sd = np.asarray([finite(v, "noise SD", positive=True) for v in noise_sd])
        if self.prior_sd.shape != (2,) or self.noise_sd.shape != (2,) or not np.isfinite(self.y).all():
            raise ValueError("Two finite objectives required")
        gram = self._contrast_kernel(self.a, self.b, self.a, self.b)
        self.factors, self.weights = [], []
        # Aggregates receive larger declared noise; failures remain training evidence.
        factor = np.asarray([2.0 if "AGGREGATES" in x.evidence_kind else 1.0 for x in observations])
        for j in range(2):
            covariance = self.prior_sd[j] ** 2 * gram + np.diag((factor * self.noise_sd[j]) ** 2 + 1e-10)
            chol = cho_factor(covariance, lower=True, check_finite=True)
            self.factors.append(chol)
            self.weights.append(cho_solve(chol, self.y[:, j]))

    @staticmethod
    def _state_kernel(x, y):
        dimension = max(x.shape[1], 1)
        distance = np.maximum(0, (x * x).sum(1)[:, None] + (y * y).sum(1)[None, :] - 2 * x @ y.T)
        return .6 * np.exp(-distance / (2 * dimension)) + .4 * (x @ y.T) / dimension

    def _contrast_kernel(self, a, b, c, d):
        kernel = self._state_kernel
        return kernel(b, d) - kernel(b, c) - kernel(a, d) + kernel(a, c)

    def posterior(self, baseline, treatment, *, context):
        """Return latent log-ratio means/SDs; transform draws before EHVI."""
        if context != self.context:
            raise ValueError("Cross-context posterior is forbidden")
        a, b = self.encoder.encode(baseline)[None, :], self.encoder.encode(treatment)[None, :]
        cross = self._contrast_kernel(a, b, self.a, self.b)[0]
        self_cov = float(self._contrast_kernel(a, b, a, b)[0, 0])
        means, variances = [], []
        for j in range(2):
            k = self.prior_sd[j] ** 2 * cross
            means.append(float(k @ self.weights[j]))
            variance = self.prior_sd[j] ** 2 * self_cov - k @ cho_solve(self.factors[j], k)
            if variance < -1e-8:
                raise ValueError("Invalid posterior covariance")
            variances.append(max(0.0, float(variance)))
        return np.asarray(means), np.sqrt(variances)


def fit_context_surrogates(observations, **options):
    groups = defaultdict(list)
    for item in observations:
        groups[item.context].append(item)
    return {key: EpistasisSurrogate(rows, **options) for key, rows in sorted(groups.items())}


def pareto_front(points):
    array = np.asarray(points, dtype=float).reshape(-1, 2)
    if not np.isfinite(array).all():
        raise ValueError("Finite two-objective Pareto points required")
    array = np.unique(array, axis=0)
    return np.asarray([p for p in array if not np.any(np.all(array >= p, axis=1) & np.any(array > p, axis=1))]).reshape(-1, 2)


def hypervolume(points, reference=REFERENCE):
    """Exact union area for two maximization objectives."""
    ref = np.asarray(reference, dtype=float)
    if ref.shape != (2,) or not np.isfinite(ref).all():
        raise ValueError("Finite two-objective reference required")
    front = pareto_front(points)
    front = front[np.all(front > ref, axis=1)]
    area, previous = 0.0, ref[0]
    for x, y in sorted(front.tolist()):
        area += (x - previous) * (y - ref[1])
        previous = x
    return float(area)


def relative_posterior_moments(mean, sd):
    mean, variance = np.asarray(mean, float), np.asarray(sd, float) ** 2
    response_mean = np.asarray([np.expm1(mean[0] + variance[0] / 2),
                                -np.expm1(-mean[1] + variance[1] / 2)])
    response_sd = np.sqrt(np.expm1(variance) * np.exp(np.asarray([2 * mean[0], -2 * mean[1]]) + variance))
    return response_mean, response_sd


def expected_hypervolume_improvement(mean, sd, front, *, reference=REFERENCE, samples=2048, seed=SEED,
                                    log_ratio_posterior=False):
    """q=1 MC EHVI with common random numbers; no novelty heuristic in score."""
    mean, sd = np.asarray(mean, float), np.asarray(sd, float)
    if mean.shape != (2,) or sd.shape != (2,) or not np.isfinite([mean, sd]).all() or np.any(sd < 0):
        raise ValueError("Two finite posterior means/nonnegative SDs required")
    if type(samples) is not int or not 32 <= samples <= 65536:
        raise ValueError("32..65536 posterior draws required")
    front = pareto_front(front)
    ref = np.asarray(reference, dtype=float)
    base = hypervolume(front, reference)
    draws = mean + sd * np.random.default_rng(seed).standard_normal((samples, 2))
    if log_ratio_posterior:
        with np.errstate(over="raise", invalid="raise"):
            try:
                draws = np.column_stack((np.expm1(draws[:, 0]), -np.expm1(-draws[:, 1])))
            except FloatingPointError as exc:
                raise ValueError("Nonfinite transformed posterior draws") from exc
    # Partition the area under a candidate into x strips cut by the fixed front.
    # Within each strip the incumbent dominated height is constant.
    eligible = front[np.all(front > ref, axis=1)]
    xs = sorted({float(ref[0])} | {float(p[0]) for p in eligible})
    improvement = np.zeros(samples)
    for left, right in zip(xs, xs[1:] + [math.inf]):
        ceiling = max([ref[1]] + [float(p[1]) for p in eligible if p[0] > left])
        width = np.maximum(0, np.minimum(draws[:, 0], right) - left)
        improvement += width * np.maximum(0, draws[:, 1] - ceiling)
    return dict(ehvi=float(improvement.mean()), mc_standard_error=float(improvement.std(ddof=1) / math.sqrt(samples)),
                samples=samples, seed=seed, reference=ref.tolist(), baseline_hypervolume=base,
                objective_units="PRODUCT_OF_FRACTIONAL_RESPONSE_CHANGES", q=1,
                posterior_space="LOG_RATIOS_TRANSFORMED_TO_RELATIVE_RESPONSES" if log_ratio_posterior else "RELATIVE_RESPONSES",
                estimator="POSTERIOR_MONTE_CARLO_HYPERVOLUME_IMPROVEMENT")


def grouped_validation(observations, *, max_folds=32):
    """Whole-round holdout AND purge both test packages, with training-only scaling."""
    if type(max_folds) is not int or not 1 <= max_folds <= 64:
        raise ValueError("Bounded validation folds required")
    groups = defaultdict(list)
    for item in observations:
        groups[item.context].append(item)
    folds = []
    # Interleave contexts so large early R2 factorials do not consume every fold.
    rounds = []
    by_context = [sorted({x.round_id for x in rows}, key=_round_order) for rows in groups.values()]
    for index in range(max((len(x) for x in by_context), default=0)):
        rounds.extend((key, ids[index]) for key, ids in zip(groups, by_context) if index < len(ids))
    for key, rid in rounds[:max_folds]:
        test = [x for x in groups[key] if x.round_id == rid]
        held = {canonical(s) for x in test for s in (x.baseline, x.treatment)}
        train = [x for x in groups[key] if x.round_id != rid and not held.intersection((canonical(x.baseline), x.package_id))]
        fold = dict(round_id=rid, context=json.loads(key), train_rounds=sorted({x.round_id for x in train}, key=_round_order),
                    test_comparisons=len(test), purge="BOTH_COMPLETE_PACKAGES_AND_WHOLE_ROUND", predictions=[])
        if len(train) < 2:
            fold.update(status="UNSUPPORTED_AFTER_PACKAGE_PURGE", reason="No independent package support; no in-sample replacement")
        else:
            model = EpistasisSurrogate(train)
            for x in test:
                try:
                    mean, sd = model.posterior(x.baseline, x.treatment, context=x.context)
                    response_mean, response_sd = relative_posterior_moments(mean, sd)
                    fold["predictions"].append(dict(actual=list(x.outcome), mean=response_mean.tolist(), sd=response_sd.tolist(),
                                                   log_ratio_mean=mean.tolist(), log_ratio_sd=sd.tolist(),
                                                   absolute_error=np.abs(response_mean - x.outcome).tolist()))
                except ValueError as exc:
                    fold["predictions"].append(dict(status="UNSUPPORTED_FEATURE", reason=str(exc)))
            fold["status"] = "PREDICTED" if any("mean" in p for p in fold["predictions"]) else "UNSUPPORTED_FEATURES"
        folds.append(fold)
    predictions = [p for f in folds for p in f["predictions"] if "mean" in p]
    return dict(folds=folds, evaluated_folds=len(folds), predicted_comparisons=len(predictions),
                mean_absolute_error=np.mean([p["absolute_error"] for p in predictions], axis=0).tolist() if predictions else None,
                acceptance="EXPLORATORY_NO_EMPIRICAL_CALIBRATION_ACCEPTANCE",
                unsupported_folds_retained=True, hardware_generalization_verified=False)


def conditional_epistasis_report(observations, records=()):
    selected = [x for x in observations if x.round_id in {f"R{i}" for i in range(166, 175)}]
    result = []
    for x in selected:
        source_rows = [r for r in records if r["round_id"] == x.round_id]
        result.append(dict(round_id=x.round_id, baseline=x.baseline, treatment=x.treatment,
                           goodput_gain_pct=100 * x.outcome[0], p95_reduction_pct=100 * x.outcome[1],
                           saved_treatment_directional_jain=source_rows[-1].get("jain_fairness") if source_rows else None,
                           quality=x.quality, source=x.source))
    cells = {}
    for x in selected:
        for state in (x.baseline, x.treatment):
            fields = ("endpoint.ap.be_low_us", "endpoint.ap.be_high_us", "endpoint.cpe.be_low_us",
                      "endpoint.cpe.be_high_us", "endpoint.ap.fq_quantum_bytes", "endpoint.ap.fq_target_us",
                      "endpoint.ap.fq_interval_us")
            config = {k: state.get(k) for k in fields}
            cells.setdefault(canonical(config), dict(configuration=config, rounds=[]))["rounds"].append(x.round_id)
    return dict(status="EXPLORATORY_CONDITIONAL_INTERACTION_NOT_CAUSALLY_IDENTIFIED",
                observed_contrasts=result, observed_configurations=list(cells.values()),
                literal_zero_percent_inertness="REFUTED_AS_EXACT_NUMERIC_CLAIM_NO_EQUIVALENCE_TEST",
                combined_4_13_percent_and_0_9520_same_round="REFUTED_R174_GOODPUT_R173_JAIN",
                requested_900_1500_be_setting="NOT_THE_R171_R174_SAVED_BE_VALUES",
                codel_factorial_complete=False, causal_interaction_identified=False,
                missing_evidence=["Repeated randomized matched AQL x FQ x CoDel factorial at one exact context",
                                  "Effective AP/CPE control/readback and queue-path authority",
                                  "Independent hardware/sector repetitions and adequate loss/tail observations"],
                mechanism="INFERRED: AQL may expose host queue effects; lower-layer queue ownership remains UNKNOWN")


PIVOT_MATCHES = {
    "PB-030_SUBCHANNEL_5_10_MHZ": ("chanbw", "chwidth", "STA_TXBW_MASK", "BW_DISABLE_MASK"),
    "PB-031_LDPC_STBC_CCA_AGC": ("ldpc", "stbc", "THRESH62", "CCA", "AGC", "NOISE_IMMUNITY"),
    "ASYMMETRIC_CHAINMASK_RESCUE": ("CHAIN_MASK", "DYNTXCHAIN", "chainmask"),
    "PB-050_TARGET_TIMER_GATING": ("metimer", "hbrtimer", "SCHEDULER_AIR_TIME", "SWBA"),
}


def pivot_dimensions(catalog):
    groups = []
    for name, tokens in PIVOT_MATCHES.items():
        matches = [k for k in catalog if any(t.lower() in (k["id"] + " " + k["name"]).lower() for t in tokens)]
        groups.append(dict(dimension=name, matched_catalog_ids=[k["id"] for k in matches],
                           excluded_catalog_ids=[k["id"] for k in matches if k["classification"] == "excluded"],
                           state="RESEARCH_ONLY_BLOCKED", direct_control_equivalence_verified=False,
                           required_evidence=("Exact 5/10MHz PHY support and spectral/regulatory validation" if "030" in name else
                                              "Target TSF release/completion jitter, queue ownership and missed-slot safety" if "050" in name else
                                              "Exact board/build hook, contained legal RF characterization and readback"),
                           requested_values_mhz=[5, 10] if "030" in name else None))
    return groups


def regime_switch(observations, catalog):
    from controller.stage14_ptmp_ap_shootout_controller import WallDetectorGate, RoundDeltaRecord
    grouped = defaultdict(list)
    for item in observations:
        grouped[item.context].append(item)
    reports = []
    for key, rows in sorted(grouped.items()):
        context = json.loads(key)
        if context.get("cpe_count") != 1:
            continue
        by_round = defaultdict(list)
        for row in rows:
            by_round[row.round_id].append(row)
        entries, trailing = [], []
        for rid in sorted(by_round, key=_round_order):
            candidates = by_round[rid]
            # Saturation needs one comparison, finite positive baselines, known zero
            # loss, restoration and no drops. A failed treatment interrupts the streak.
            valid = len(candidates) == 1 and candidates[0].front_eligible
            row = candidates[0]
            entry = RoundDeltaRecord(rid, context["workload"], context.get("distance_m") or 0,
                                     *[row.baseline_metrics[0], row.treatment_metrics[0],
                                       row.baseline_metrics[1], row.treatment_metrics[1]], "SAVED_COMPARISON")
            entries.append(dict(round_id=rid, eligible=valid, goodput_gain_pct=100 * row.outcome[0],
                                p95_change_pct=-100 * row.outcome[1]))
            # Use unrounded values to reject near-threshold rounding false positives.
            within = valid and abs(100 * row.outcome[0]) < 1.5 and abs(100 * row.outcome[1]) < 5.0
            trailing = trailing + [entry] if within else []
        verdict = WallDetectorGate().evaluate_series(trailing)
        hit = verdict.wall_reached and len(trailing) >= 2
        reports.append(dict(context=context, wall_reached=hit,
                            trailing_round_ids=[x.round_id for x in trailing], evaluations=entries,
                            pivot_dimensions=pivot_dimensions(catalog) if hit else [],
                            action="PIVOT_SEARCH_QUESTIONS_ONLY" if hit else "CONTINUE_CONTEXT_CONDITIONED_SEARCH",
                            automatic_execution_allowed=False))
    return reports


# Catalog bindings identify declared coordinates, never API interchangeability.
# codel_target/codel_interval describe policy metadata in ms, not authenticated
# aliases for the retained fq_*_us hook. Those catalog IDs remain prior-only.
BINDINGS = {
    "aql_txq_limit": ("be_low_us", "be_high_us"),
    "aql_threshold": ("aql_threshold_us",),
    "fq_quantum": ("fq_quantum_bytes",),
    "ct_special_7": ("rc_per_thresh",),
    "ct_special_10": ("ct_baseband_rifs",),
    "ct_special_12": ("ct_pshack",),
    "htt_aggr_size": ("htt_max_amsdu", "htt_max_ampdu"),
    "rts_threshold": ("rts_threshold",),
}


def _binding_values(state, names):
    keys = [f"endpoint.{endpoint}.{name}" for endpoint in ("ap", "cpe") for name in names]
    return keys, tuple(state.get(k) for k in keys)


def rank_frontier(catalog, observations, *, anchor_round="R174", limit=15, samples=2048, seed=SEED):
    """Rank defined conditional candidates, then explicitly tied prior-only questions.

    Null evidence EHVI is not replaced by a synthetic performance observation.
    A hypothetical generic prior is disclosed separately, never mixed into rank.
    """
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("1..50 ranked variables required")
    anchors = [x for x in observations if x.round_id == anchor_round]
    if len(anchors) != 1:
        raise ValueError("One unambiguous anchor comparison required")
    anchor = anchors[0]
    rows = [x for x in observations if x.context == anchor.context]
    model = EpistasisSurrogate(rows)
    front = pareto_front([[0.0, 0.0]] + [list(x.outcome) for x in rows if x.front_eligible])
    pivot = pivot_dimensions(catalog)
    requested_order = {kid: i for i, group in enumerate(pivot) for kid in group["matched_catalog_ids"]}
    hypothetical = expected_hypervolume_improvement([0, 0], PRIOR_SD, front, samples=samples, seed=seed, log_ratio_posterior=True)
    prior_sensitivity = {str(mult): expected_hypervolume_improvement([0, 0], np.asarray(PRIOR_SD) * mult, front,
                          samples=samples, seed=seed, log_ratio_posterior=True)["ehvi"] for mult in (.5, 1.0, 2.0)}
    results = []
    for knob in catalog:
        item = dict(id=knob["id"], name=knob["name"], classification=knob["classification"],
                    family=knob["family"], boundary=knob["boundary"], platform_scope=knob["platform_scope"],
                    automatic_execution_allowed=False, physical_status="BLOCKED_UNQUALIFIED",
                    enabled=False, evidence_based_ehvi=None, uncertainty=None, intervention=None,
                    encoding_domain=knob["encoding_domain"], observed_change_rounds=[],
                    gates=["Exact board/build and API join", "Approved physical range and effective readback",
                           "Verified restoration/recovery", "Applicable regulatory and original experiment gates"])
        if knob["classification"] in ("excluded", "observation_only"):
            item["status"] = "EXCLUDED_FROM_SEARCH" if knob["classification"] == "excluded" else "OBSERVATION_ONLY"
            results.append(item)
            continue
        names = BINDINGS.get(knob["id"])
        alternatives = {}
        if names:
            keys, old = _binding_values(anchor.baseline, names)
            changed = [x for x in observations if _binding_values(x.baseline, names)[1] != _binding_values(x.treatment, names)[1]]
            item["observed_change_rounds"] = sorted({x.round_id for x in changed}, key=_round_order)
            for row in rows:
                for state in (row.baseline, row.treatment):
                    _, value = _binding_values(state, names)
                    if value != old and all(v is not None for v in value) and all(k in anchor.baseline for k in keys):
                        alternatives[value] = dict(zip(keys, value))
        item["tested_scope"] = "SAVED_DECLARED_CONTROL_ONLY_NOT_EFFECTIVE_HOOK"
        item["exploration_status"] = "UNDEREXPLORED_EXACT_CONTEXT_OR_INTERACTION" if names and item["observed_change_rounds"] else "UNTESTED_EXACT_CATALOG_HOOK"
        scored = []
        for updates in alternatives.values():
            target = dict(anchor.baseline, **updates)
            try:
                mean, sd = model.posterior(anchor.baseline, target, context=anchor.context)
                acquisition = expected_hypervolume_improvement(mean, sd, front, samples=samples, seed=seed, log_ratio_posterior=True)
                scored.append((acquisition["ehvi"], updates, mean, sd, acquisition))
            except ValueError:
                continue
        if scored:
            _, updates, mean, sd, acquisition = max(scored, key=lambda x: (x[0], canonical(x[1])))
            item.update(status="SUPPORTED_CONDITIONAL_EHVI", evidence_based_ehvi=acquisition["ehvi"],
                        acquisition=acquisition, posterior_log_ratio_mean=mean.tolist(), uncertainty=sd.tolist(),
                        uncertainty_units="LATENT_LOG_RATIO_SD",
                        intervention=dict(baseline_round=anchor_round, baseline_source=anchor.source,
                                          changed_declared_coordinates=updates, all_other_controls="ANCHOR_BASELINE_HELD_FIXED",
                                          unit_conversion="NONE_NATIVE_SAVED_COORDINATE_UNITS",
                                          API_equivalence_verified=False),
                        candidate_values_considered=len(scored),
                        support="CONDITIONAL_MODEL_NOT_CAUSAL_OR_INDEPENDENT_HARDWARE_ACCEPTANCE")
        else:
            item.update(status="PRIOR_ONLY_RESEARCH_PRIORITY", hypothetical_prior_ehvi=hypothetical["ehvi"],
                        hypothetical_prior_sd=list(PRIOR_SD), hypothetical_prior_sensitivity=prior_sensitivity,
                        hypothetical_prior_mean=[0.0, 0.0], tie_group="ALL_UNDEFINED_INTERVENTIONS_SAME_HYPOTHETICAL_PRIOR",
                        reason="No defined catalog-hook intervention with supported native coordinate values in this exact context")
        results.append(item)
    eligible = [x for x in results if x["status"] in ("SUPPORTED_CONDITIONAL_EHVI", "PRIOR_ONLY_RESEARCH_PRIORITY")]
    eligible.sort(key=lambda x: (0 if x["status"] == "SUPPORTED_CONDITIONAL_EHVI" else 1,
                                -(x["evidence_based_ehvi"] or 0),
                                requested_order.get(x["id"], 99), x["id"]))
    top = [dict(item, rank=i + 1) for i, item in enumerate(eligible[:limit])]
    return dict(anchor_round=anchor_round, context=json.loads(anchor.context), objectives=list(OBJECTIVES),
                reference=list(REFERENCE), eligible_observed_front=front.tolist(), all_catalog_evaluations=results,
                top15=top, catalog_counts=dict(Counter(x["status"] for x in results)),
                ranking_contract="SUPPORTED_CONDITIONAL_EHVI_DESCENDING_THEN_PRIOR_ONLY_TIES",
                prior_only_tiebreak="REQUESTED_PIVOT_DIMENSION_ORDER_THEN_STABLE_ID_NOT_EXPECTED_BENEFIT",
                no_empirical_571_variable_performance_ranking_possible=True,
                posterior_acceptance="EXPLORATORY_UNCALIBRATED", hypothetical_prior_sensitivity=prior_sensitivity)


def validate_search_artifact(report):
    if report.get("task_id") != TASK_ID or report.get("automatic_execution_allowed") is not False:
        raise ValueError("Offline task boundary violated")
    if report.get("physical_acceptance") is not False or report.get("E2") != "NOT_ACCEPTED":
        raise ValueError("Saved evidence cannot grant hardware acceptance")
    frontier = report["frontier"]
    all_rows = frontier["all_catalog_evaluations"]
    if len(all_rows) != 571 or len({x["id"] for x in all_rows}) != 571 or len(frontier["top15"]) != 15:
        raise ValueError("Exact571/Top15 coverage required")
    known = {x["id"]: x for x in all_rows}
    if len({x["id"] for x in frontier["top15"]}) != 15:
        raise ValueError("Unique Top15 required")
    for item in all_rows:
        if item["enabled"] is not False or item["automatic_execution_allowed"] is not False:
            raise ValueError("Catalog actuation must remain disabled")
        if item["status"] == "SUPPORTED_CONDITIONAL_EHVI":
            finite(item["evidence_based_ehvi"], "EHVI")
            if item["evidence_based_ehvi"] < 0 or not item["intervention"]:
                raise ValueError("Defined intervention/nonnegative EHVI required")
        elif item["evidence_based_ehvi"] is not None:
            raise ValueError("Unsupported controls must not get empirical EHVI")
    eligible_statuses = ("SUPPORTED_CONDITIONAL_EHVI", "PRIOR_ONLY_RESEARCH_PRIORITY")
    for index, item in enumerate(frontier["top15"], start=1):
        copy = dict(item)
        rank = copy.pop("rank", None)
        if (rank != index or copy != known.get(item["id"])
                or item["status"] not in eligible_statuses
                or item["classification"] in ("excluded", "observation_only")):
            raise ValueError("Top15 must exactly match eligible catalog evaluations and consecutive ranks")
    requested_order = {kid: i for i, group in enumerate(pivot_dimensions(all_rows))
                       for kid in group["matched_catalog_ids"]}
    expected = sorted([x for x in all_rows if x["status"] in eligible_statuses],
                      key=lambda x: (0 if x["status"] == "SUPPORTED_CONDITIONAL_EHVI" else 1,
                                     -(x["evidence_based_ehvi"] or 0),
                                     requested_order.get(x["id"], 99), x["id"]))
    if [x["id"] for x in frontier["top15"]] != [x["id"] for x in expected[:15]]:
        raise ValueError("Top15 must be the exact acquisition-ranked prefix")
    canonical(report)
    return True


def build_report(root: Path = ROOT, *, samples=2048, seed=SEED):
    evidence = load_search_evidence(root)
    observations = evidence["comparisons"]
    models = fit_context_surrogates(observations)
    report = dict(schema_version="FMX_PB060_EPISTASIS_FRONTIER_V1", task_id=TASK_ID,
                  automatic_execution_allowed=False, actuation="NONE", physical_acceptance=False,
                  E2="NOT_ACCEPTED", boundary="EXTERNAL_CONTROLLER_OFFLINE_ANALYSIS",
                  input_bindings=evidence["inputs"], corpus_audit=evidence["audit"],
                  model=dict(kind="CONTRAST_GAUSSIAN_PROCESS_RBF_PLUS_LINEAR_EXPLICIT_AQL_PRODUCTS",
                             contrast_kernel="k(t,t')-k(t,a')-k(a,t')+k(a,a')",
                             response_transform="log(GP_B/GP_A), -log(p95_B/p95_A); EHVI draws transformed back",
                             objective_prior_sd=list(PRIOR_SD), objective_noise_sd=list(NOISE_SD),
                             aggregate_noise_multiplier=2, prior_mean=[0.0, 0.0],
                             independent_objectives=True, noise_estimated_from_raw_trials=False,
                             hyperparameters="PRESPECIFIED_NO_OUTCOME_TUNING", posterior_is_hardware_ci=False,
                             contexts=len(models), seed=seed,
                             context_support=[dict(context=json.loads(k), comparisons=len(m.observations),
                                                   rounds=len({x.round_id for x in m.observations})) for k, m in models.items()]),
                  validation=grouped_validation(observations),
                  epistasis=conditional_epistasis_report(observations, evidence["records"]),
                  regime_switches=regime_switch(observations, evidence["catalog"]),
                  requested_pivot_dimensions=pivot_dimensions(evidence["catalog"]),
                  frontier=rank_frontier(evidence["catalog"], observations, samples=samples, seed=seed),
                  software_evidence="SEE_COMPANION_DOCUMENT_FOR_REQUESTED_PYTEST_AND_INDEPENDENT_REVIEW_RECEIPTS",
                  limitations=["Adaptive sequential single-link measurements are not independent sector trials",
                               "Loss/failed treatments retained in training, excluded from acceptable incumbent frontier",
                               "Jain in saved bidirectional data is directional fairness, not multi-CPE fairness",
                               "Jain/packet-loss are descriptive guards, not imputed objectives",
                               "Unknown firmware identity blocks deployment and cross-build transfer claims",
                               "Prior-only EHVI is a hypothetical scale-sensitive research question, not predicted hardware improvement",
                               "PB050 synthetic timing fixtures and Stage16 report defaults are not training measurements"],
                  method_sources=["https://arxiv.org/abs/2006.05078",
                                  "https://botorch.org/docs/v0.14.0/acquisition",
                                  "https://scikit-learn.org/stable/modules/gaussian_process.html"])
    for path in ("orchestration/autoresearch/pb060_epistasis_surrogate_optimizer.py",
                 "tests/test_pb060_epistasis_surrogate_optimizer.py"):
        raw = (root / path).read_bytes()
        report.setdefault("implementation_bindings", []).append(dict(path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    validate_search_artifact(report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / OUTPUT)
    parser.add_argument("--samples", type=int, default=2048)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)
    if not 32 <= args.samples <= 65536:
        parser.error("samples must be32..65536")
    report = build_report(samples=args.samples, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(status="OFFLINE_FRONTIER_WRITTEN", output=str(args.output),
                          observed_rounds=report["corpus_audit"]["observed_unique_rounds"],
                          top15=len(report["frontier"]["top15"]), automatic_execution_allowed=False)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
