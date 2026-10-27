"""Offline DOE and bounded, non-actuating pymoo Pareto proposals.

The catalog is a coverage/eligibility inventory, not a 248-dimensional calibrated
model. Only measured controls enter the surrogate; other controls stay explicitly
unmodeled. No bench runner, dynamic plugin, shell or network API is used.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
from itertools import combinations, product
import math
from pathlib import Path

import numpy as np

from orchestration.autoresearch.fmx_offline_data import (
    ARTIFACTS, ROOT, finite_number, load_measurements, local_json, policy_features,
    software_versions, training_arrays, write_json,
    AC_ORDER, EFGH_ARTIFACTS, EndpointPolicy, REGIMES, load_all_measurements,
)


@dataclass(frozen=True)
class Factor:
    name: str
    levels: tuple[int, ...]
    catalog_ids: tuple[str, ...]


# These are model-study domains, not certified device/RAM safety limits.
FACTORS = (
    Factor("aql_low_us", (1000, 1200, 1500, 2000, 5000), ("aql_txq_limit", "aql_threshold")),
    Factor("ct_rc_per_thresh", (28, 35, 50), ("ct_special_7",)),
    Factor("ct_baseband_rifs", (0, 1), ("ct_special_10",)),
    Factor("fq_quantum_bytes", (300, 1514), ("fq_quantum",)),
    Factor("htt_max_amsdu", (2, 3), ("htt_aggr_size",)),
    Factor("htt_max_ampdu", (32, 48, 64), ("htt_aggr_size",)),
)


def validate_factors(factors):
    if not 1 <= len(factors) <= 10 or len({f.name for f in factors}) != len(factors):
        raise ValueError("Require 1..10 uniquely named factors")
    for factor in factors:
        if not 2 <= len(factor.levels) <= 32 or len(set(factor.levels)) != len(factor.levels):
            raise ValueError("Finite distinct factor levels required")
        if any(type(value) is not int for value in factor.levels):
            raise ValueError("Factor levels must be exact integers")
        if tuple(sorted(factor.levels)) != factor.levels:
            raise ValueError("Factor levels must be ordered")


def catalog_coverage(catalog):
    if catalog.get("automatic_execution_allowed") is not False or catalog.get("actuation") != "none":
        raise ValueError("Catalog must remain non-actuating")
    entries = catalog["knobs"]
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Duplicate catalog identity")
    known = {name for factor in FACTORS for name in factor.catalog_ids}
    if not known <= {entry["id"] for entry in entries}:
        raise ValueError("Missing measured control identity")
    result = []
    for entry in entries:
        if entry.get("enabled") is not False or entry["ram_safety"]["approved_range"] is not None:
            raise ValueError("Catalog activation/safety promotion forbidden")
        disposition = ("excluded_by_source_or_scope" if entry["classification"] == "excluded"
                       else "measured_model_domain_only" if entry["id"] in known
                       else "unmodeled_no_empirical_response")
        result.append(dict(id=entry["id"], disposition=disposition,
                           automatic_execution_allowed=False))
    return result


def policy_from_levels(values):
    if len(values) != len(FACTORS):
        raise ValueError("Six modeled factors required")
    for value, factor in zip(values, FACTORS):
        if type(value) is not int or value not in factor.levels:
            raise ValueError(f"Outside model domain: {factor.name}")
    low, rc, rifs, quantum, amsdu, ampdu = values
    high = 12000 if low == 5000 else 2 * low
    threshold = 24000 if low == 5000 else 4 * low
    return (low, high, threshold, rc, rifs, quantum, amsdu, ampdu)


def candidate_grid(factors=FACTORS):
    validate_factors(factors)
    size = math.prod(len(f.levels) for f in factors)
    if size > 10000:
        raise ValueError("Candidate grid exceeds 10000 rows")
    return np.array(list(product(*(factor.levels for factor in factors))), dtype=int)


def model_matrix(rows, factors=FACTORS, interactions=False):
    rows = np.asarray(rows, dtype=float)
    validate_factors(factors)
    if rows.ndim != 2 or rows.shape[1] != len(factors) or not np.isfinite(rows).all():
        raise ValueError("Finite factor matrix required")
    low = np.array([min(f.levels) for f in factors])
    high = np.array([max(f.levels) for f in factors])
    if np.any(rows < low) or np.any(rows > high):
        raise ValueError("Design lies outside model bounds")
    coded = 2 * (rows-low)/(high-low)-1
    columns = [np.ones(len(rows)), *coded.T]
    terms = ["intercept", *(f.name for f in factors)]
    if interactions:
        for a, b in combinations(range(len(factors)), 2):
            columns.append(coded[:, a]*coded[:, b])
            terms.append(factors[a].name+":"+factors[b].name)
    return np.column_stack(columns), terms


def fractional_factorial(factors=FACTORS, seed=20261024):
    """Regular half fraction, last coded factor = product of preceding factors.

    Uses endpoint levels. Defining word has length k, hence resolution k;
    explicitly reports main/2-way aliases rather than claiming full factorial.
    """
    validate_factors(factors)
    k = len(factors)
    if k < 3:
        raise ValueError("At least three factors for estimable half-fraction mains")
    base = np.array(list(product((-1, 1), repeat=k-1)), dtype=int)
    coded = np.column_stack((base, np.prod(base, axis=1)))
    rows = np.array([[factor.levels[0] if sign < 0 else factor.levels[-1]
                      for factor, sign in zip(factors, row)] for row in coded])
    matrix, terms = model_matrix(rows, factors, interactions=True)
    aliases = []
    for a, b in combinations(range(1, len(terms)), 2):
        if np.array_equal(matrix[:, a], matrix[:, b]):
            aliases.append([terms[a], terms[b], 1])
        elif np.array_equal(matrix[:, a], -matrix[:, b]):
            aliases.append([terms[a], terms[b], -1])
    order = np.random.default_rng(seed).permutation(len(rows))
    main, _ = model_matrix(rows, factors)
    return dict(design="regular_half_fraction", defining_relation="I="+"*".join(f.name for f in factors),
                resolution=k, seed=seed, rows=rows[order].tolist(),
                main_effect_rank=int(np.linalg.matrix_rank(main)),
                main_effect_columns=k+1, main_and_two_way_aliases=aliases,
                independent_replications=0, automatic_execution_allowed=False)


def d_optimal_design(candidates=None, n_runs=14, factors=FACTORS, seed=20261024):
    candidates = candidate_grid(factors) if candidates is None else np.asarray(candidates)
    matrix, terms = model_matrix(candidates, factors)
    p = matrix.shape[1]
    if type(n_runs) is not int or not p <= n_runs <= min(256, len(candidates)):
        raise ValueError("Design needs at least p runs and at most256")
    if np.linalg.matrix_rank(matrix) < p or len(np.unique(candidates, axis=0)) != len(candidates):
        raise ValueError("Candidate set must be unique and full rank")
    rng = np.random.default_rng(seed)
    priority = rng.permutation(len(candidates))
    remaining = list(priority)
    selected = []
    information = np.eye(p)*1e-9
    history = []
    for _ in range(n_runs):
        scores = [np.linalg.slogdet(information + np.outer(matrix[i], matrix[i]))[1]
                  for i in remaining]
        index = remaining.pop(int(np.argmax(scores)))
        selected.append(index)
        information += np.outer(matrix[index], matrix[index])
        history.append(float(np.linalg.slogdet(information)[1]))
    chosen = matrix[selected]
    rank = int(np.linalg.matrix_rank(chosen))
    if rank != p:
        raise ValueError("Greedy D-design failed to span the specified main-effect model")
    selected = np.array(selected)[rng.permutation(n_runs)]
    return dict(design="greedy_D_optimal_approximation", seed=seed,
                rows=candidates[selected].tolist(), model_terms=terms, model_rank=rank,
                log_determinant=float(np.linalg.slogdet(chosen.T@chosen)[1]),
                regularized_selection_logdet_history=history,
                optimality_certificate=False, independent_replications=0,
                automatic_execution_allowed=False)


class KernelSurrogate:
    """Small-sample RBF ridge response model with an explicit round nuisance axis."""

    def __init__(self, records, ridge=0.1, length_scale=0.5):
        finite_number(ridge, "ridge", 1e-8, 100)
        finite_number(length_scale, "length_scale", 1e-3, 100)
        self.records = tuple(records)
        if any(row.round_id not in {"R1", "R2"} for row in self.records):
            raise ValueError("Unknown training round")
        x, self.y = training_arrays(self.records)
        self.x = np.column_stack((x, [2.0 if row.round_id == "R2" else 0.0 for row in records]))
        self.length_scale = length_scale
        squared = np.sum((self.x[:, None, :]-self.x[None, :, :])**2, axis=2)
        self.round_means = {}
        for round_id in ("R1", "R2"):
            rows = [i for i,row in enumerate(records) if row.round_id == round_id]
            self.round_means[round_id] = self.y[rows].mean(axis=0) if rows else self.y.mean(axis=0)
        nuisance = np.array([self.round_means[row.round_id] for row in records])
        self.coefficients = np.linalg.solve(np.exp(-squared/(2*length_scale**2)) + ridge*np.eye(len(x)), self.y-nuisance)

    def predict(self, knobs, round_id="R2"):
        if round_id not in {"R1", "R2"}:
            raise ValueError("Unknown calibration round")
        query = np.append(policy_features(knobs), 2.0 if round_id == "R2" else 0.0)
        distances = np.linalg.norm(self.x-query, axis=1)
        weights = np.exp(-distances**2/(2*self.length_scale**2))
        raw = self.round_means[round_id] + weights@self.coefficients
        if not np.isfinite(raw).all():
            raise ValueError("Non-finite surrogate response")
        # Projection enforces output geometry only, not physical plausibility.
        projected = np.maximum(raw, 0)
        projected[2] = max(projected[1], projected[2])
        return dict(goodput_mbps=float(projected[0]), p95_ms=float(projected[1]),
                    p99_ms=float(projected[2]), distance_to_training=float(distances.min()),
                    nonnegative_quantile_projection=not np.array_equal(raw, projected),
                    prediction_kind="exploratory_surrogate_not_physical_measurement")


def grouped_validation(records):
    """Leave the entire policy out, including its instances in another round."""
    rows = []
    for policy in sorted({row.policy_key for row in records}):
        train = [row for row in records if row.policy_key != policy]
        test = [row for row in records if row.policy_key == policy]
        if len(train) < 3:
            raise ValueError("Too few held-out policy groups")
        model = KernelSurrogate(train)
        for row in test:
            estimate = model.predict(row.knobs, row.round_id)
            same_round = [r for r in train if r.round_id == row.round_id] or train
            baseline = np.mean([[r.goodput_mbps, r.p95_ms, r.p99_ms] for r in same_round], axis=0)
            actual = np.array([row.goodput_mbps, row.p95_ms, row.p99_ms])
            predicted = np.array([estimate['goodput_mbps'], estimate['p95_ms'], estimate['p99_ms']])
            rows.append(dict(iteration=row.iteration, held_out_policy=list(policy), train_policies=[list(r.policy_key) for r in train],
                             error=(predicted-actual).tolist(), mean_baseline_error=(baseline-actual).tolist()))
    errors = np.array([row['error'] for row in rows])
    baselines = np.array([row['mean_baseline_error'] for row in rows])
    return dict(method="leave_whole_policy_out_across_rounds", rows=rows,
                rmse=np.sqrt(np.mean(errors**2,axis=0)).tolist(),
                mean_baseline_rmse=np.sqrt(np.mean(baselines**2,axis=0)).tolist(),
                interpretation="Prediction diagnostics only; small sequential single-link data do not identify causal effects")


def nondominated_indices(objectives):
    values = np.asarray(objectives, dtype=float)
    if values.ndim != 2 or values.shape[1] < 2 or not np.isfinite(values).all():
        raise ValueError("Finite minimization objective matrix required")
    return [i for i, value in enumerate(values)
            if not np.any(np.all(values <= value, axis=1) & np.any(values < value, axis=1))]


def optimize_pareto(records, algorithm="nsga2", seed=20261024, population=32, generations=20):
    if algorithm not in {"nsga2", "nsga3"} or not 16 <= population <= 256 or not 2 <= generations <= 200:
        raise ValueError("Bounded NSGA-II/III budget required")
    try:
        from pymoo.algorithms.moo.nsga2 import NSGA2
        from pymoo.algorithms.moo.nsga3 import NSGA3
        from pymoo.core.problem import ElementwiseProblem
        from pymoo.operators.crossover.sbx import SBX
        from pymoo.operators.mutation.pm import PM
        from pymoo.operators.repair.rounding import RoundingRepair
        from pymoo.operators.sampling.rnd import IntegerRandomSampling
        from pymoo.optimize import minimize
        from pymoo.util.ref_dirs import get_reference_directions
    except ImportError as error:
        raise RuntimeError("pymoo is required: supply an offline installed environment/wheel; no network fallback") from error
    model = KernelSurrogate(records)
    class ModelProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=len(FACTORS), n_obj=3, n_ieq_constr=1,
                             xl=np.zeros(len(FACTORS)), xu=np.array([len(f.levels)-1 for f in FACTORS]), vtype=int)
        def _evaluate(self, indices, out, *args, **kwargs):
            values = tuple(f.levels[int(index)] for f,index in zip(FACTORS,indices))
            prediction = model.predict(policy_from_levels(values))
            out['F'] = [-prediction['goodput_mbps']/100, prediction['p95_ms']/20, prediction['p99_ms']/20]
            out['G'] = [prediction['distance_to_training']-0.75]
    operators = dict(pop_size=population, sampling=IntegerRandomSampling(),
                     crossover=SBX(prob=0.9, eta=15, vtype=float, repair=RoundingRepair()),
                     mutation=PM(eta=20, vtype=float, repair=RoundingRepair()), eliminate_duplicates=True)
    search = NSGA2(**operators) if algorithm == "nsga2" else NSGA3(ref_dirs=get_reference_directions("das-dennis",3,n_partitions=4), **operators)
    result = minimize(ModelProblem(),search,('n_gen',generations),seed=seed,verbose=False)
    if result.X is None or result.F is None or (result.CV is not None and np.any(result.CV > 1e-8)):
        raise RuntimeError("No model-feasible Pareto result; do not return least-infeasible as accepted")
    candidates = []
    for indices in np.atleast_2d(result.X):
        values = tuple(f.levels[int(index)] for f,index in zip(FACTORS,indices))
        knobs = policy_from_levels(values)
        candidates.append(dict(model_knob_tuple=list(knobs), factors=dict(zip((f.name for f in FACTORS),values)),
                               prediction=model.predict(knobs), automatic_execution_allowed=False,
                               physical_safety_qualified=False))
    unique = {tuple(c['model_knob_tuple']):c for c in candidates}
    candidates = [unique[key] for key in sorted(unique)]
    objective = [[-c['prediction']['goodput_mbps'],c['prediction']['p95_ms'],c['prediction']['p99_ms']] for c in candidates]
    return dict(algorithm=algorithm,seed=seed,population=population,generations=generations,
                evaluations=int(result.algorithm.evaluator.n_eval),pareto=[candidates[i] for i in nondominated_indices(objective)],
                model_support_radius=0.75,global_optimality_claim=False,physical_feasibility_claim=False)


def build_dataset(algorithm="both", seed=20261024):
    records, provenance = load_measurements()
    catalog = local_json(INPUTS_CATALOG)
    expanded_path = ROOT/'orchestration/autoresearch/firmware_knob_candidates.json'
    expanded_catalog = local_json(expanded_path)
    validation = grouped_validation(records)
    algorithms = ("nsga2","nsga3") if algorithm=="both" else (algorithm,)
    dataset = dict(schema_version=1,evidence="OFFLINE_MODEL_PROPOSALS",automatic_execution_allowed=False,
                sources=provenance,software_versions=software_versions(),catalog_coverage=catalog_coverage(catalog),
                expanded_catalog_coverage=catalog_coverage(expanded_catalog),
                catalog_sources=[dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in (INPUTS_CATALOG,expanded_path)],
                modeled_factors=[dict(name=f.name,levels=list(f.levels),catalog_ids=list(f.catalog_ids)) for f in FACTORS],
                limits=["13 treatment windows on one link, sequential/adaptive, not248 empirically identifiable factors",
                        "Dynamic BW RTS and WMM TXOP have no measured response in these receipts; no fabricated coefficients",
                        "Coupled AQL fields are one treatment package; individual effects not identified",
                        "Round nuisance separation does not remove time/environment confounding"],
                fractional_factorial=fractional_factorial(seed=seed),d_optimal=d_optimal_design(seed=seed),
                surrogate_validation=validation,optimizations=[],native_integration_status="PENDING")
    for name in algorithms:
        try:
            dataset['optimizations'].append(optimize_pareto(records,name,seed=seed))
        except RuntimeError as error:
            if not isinstance(error.__cause__,ImportError):
                raise
            dataset.update(native_integration_status="BLOCKED_OFFLINE_PYMOO_DEPENDENCY",missing_dependency=str(error),
                           required_pending_algorithms=list(algorithms))
            return dataset
    dataset['native_integration_status']="EXECUTED_WITH_PYMOO"
    return dataset


INPUTS_CATALOG = ARTIFACTS / "inputs/firmware_knob_candidates.json"


def endpoint_features(policy):
    """Fixed declared-policy scales with explicit masks for unknown controls."""
    if policy is None:return np.zeros(23)
    if not isinstance(policy,EndpointPolicy):raise ValueError('EndpointPolicy required')
    values=[value/scale for pair in policy.aql_by_ac for value,scale in zip(pair,(5000,12000))]
    values += [policy.aql_threshold_us/24000,policy.fq_quantum_bytes/300,policy.rc_per_thresh/50,
               int(policy.rts_threshold is not None),(policy.rts_threshold or 0)/2347,
               int(policy.dscp_micro_vo_steering)]
    for name,scale in [('ct_baseband_rifs',1),('ct_pshack',3),('htt_max_amsdu',3),('htt_max_ampdu',64)]:
        value=getattr(policy,name); values += [0 if value is None else value/scale, .25*int(value is not None)]
    return np.array([1,*values],dtype=float)


def regime_features(row):
    return np.concatenate((endpoint_features(row.ap_policy),endpoint_features(row.cpe_policy)))


def _core_policy_key(row):
    # Unknown optional controls must not permit a nearly identical core policy
    # into a held-out fold. Group more broadly than the complete policy tuple.
    def core(p):
        if p is None:return None
        return (p.aql_by_ac,p.aql_threshold_us,p.fq_quantum_bytes,p.rc_per_thresh,
                p.rts_threshold,p.dscp_micro_vo_steering)
    return repr((core(row.ap_policy),core(row.cpe_policy)))


class RegimeSurrogate:
    """Three separate RBF response models; all nuisance means are training-only.

    Outcome-derived retry, achieved UL/DL ratio and fairness are deliberately not
    predictors. They would leak held-out outcomes into a policy response model.
    """
    def __init__(self,records,ridge=.2,length_scale=.75):
        finite_number(ridge,'ridge',1e-8,100);finite_number(length_scale,'length_scale',.001,100)
        self.records=tuple(records);self.models={};self.length_scale=length_scale
        if not self.records or any(r.workload_regime not in REGIMES for r in records):
            raise ValueError('Known nonempty workload regimes required')
        for regime in REGIMES:
            subset=[r for r in self.records if r.workload_regime==regime]
            if not subset:continue
            if len(subset)<2:raise ValueError('At least2 training windows per fitted regime')
            x=np.array([regime_features(r) for r in subset])
            y=np.array([[r.goodput_mbps,r.p95_ms,r.p99_ms] for r in subset])
            if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Finite training arrays required')
            mean=y.mean(axis=0)
            by_round={rid:np.mean([y[i] for i,r in enumerate(subset) if r.round_id==rid],axis=0)
                      for rid in {r.round_id for r in subset}}
            residual=y-np.array([by_round[r.round_id] for r in subset])
            squared=np.sum((x[:,None]-x[None,:])**2,axis=2)
            coeff=np.linalg.solve(np.exp(-squared/(2*length_scale**2))+ridge*np.eye(len(x)),residual)
            self.models[regime]={'rows':subset,'x':x,'mean':mean,'round_means':by_round,'coefficients':coeff}

    def predict(self,ap_policy,cpe_policy,workload_regime,round_id=None):
        if workload_regime not in self.models:raise ValueError('Workload regime has no training support')
        if workload_regime==REGIMES[0] and cpe_policy is not None:
            raise ValueError('Bulk data have no recorded CPE policy')
        if workload_regime!=REGIMES[0] and cpe_policy is None:
            raise ValueError('Bidirectional prediction requires both endpoint policies')
        model=self.models[workload_regime]
        query=np.concatenate((endpoint_features(ap_policy),endpoint_features(cpe_policy)))
        distances=np.linalg.norm(model['x']-query,axis=1)
        weights=np.exp(-distances**2/(2*self.length_scale**2))
        nuisance=model['round_means'].get(round_id,model['mean'])
        raw=nuisance+weights@model['coefficients']
        if not np.isfinite(raw).all():raise ValueError('Non-finite response')
        response=np.maximum(raw,0);response[2]=max(response[1],response[2])
        nearest=int(np.argmin(distances))
        unseen_dscp=[]
        for endpoint,policy in (('AP',ap_policy),('CPE',cpe_policy)):
            if policy is None:continue
            observed={p.dscp_micro_vo_steering for r in model['rows']
                      if (p:=getattr(r,endpoint.lower()+'_policy')) is not None}
            if policy.dscp_micro_vo_steering not in observed:unseen_dscp.append(endpoint)
        return {'goodput_mbps':float(response[0]),'p95_ms':float(response[1]),'p99_ms':float(response[2]),
                'distance_to_training':float(distances[nearest]),
                'nearest_training_window':model['rows'][nearest].iteration,
                'round_context':round_id,'round_context_seen':round_id in model['round_means'],
                'unseen_DSCP_treatment':bool(unseen_dscp),'unseen_DSCP_endpoints':unseen_dscp,
                'quantile_projection_applied':not np.array_equal(raw,response),
                'prediction_kind':'exploratory_regime_model_not_physical_measurement'}


def regime_validation(records,method='leave_core_policy_out'):
    if method not in {'leave_core_policy_out','leave_round_out'}:raise ValueError('Unknown holdout method')
    records=tuple(records);group=(lambda r:_core_policy_key(r)) if method=='leave_core_policy_out' else (lambda r:r.round_id)
    groups=sorted({group(r) for r in records});results=[]
    for key in groups:
        train=[r for r in records if group(r)!=key];test=[r for r in records if group(r)==key]
        model=RegimeSurrogate(train)
        for row in test:
            same=[r for r in train if r.workload_regime==row.workload_regime]
            if len(same)<2:raise ValueError('Insufficient independent holdout support')
            prediction=model.predict(row.ap_policy,row.cpe_policy,row.workload_regime,row.round_id)
            actual=np.array([row.goodput_mbps,row.p95_ms,row.p99_ms])
            estimate=np.array([prediction[k] for k in ('goodput_mbps','p95_ms','p99_ms')])
            baseline=np.mean([[r.goodput_mbps,r.p95_ms,r.p99_ms] for r in same],axis=0)
            results.append({'round_id':row.round_id,'iteration':row.iteration,'regime':row.workload_regime,
                            'held_out_group':key,'training_windows':[r.iteration for r in train],
                            'prediction':prediction,'actual':actual.tolist(),
                            'error':(estimate-actual).tolist(),'regime_mean_baseline_error':(baseline-actual).tolist()})
    per_regime={}
    for regime in REGIMES:
        subset=[r for r in results if r['regime']==regime]
        if subset:
            per_regime[regime]={'windows':len(subset),'rmse':np.sqrt(np.mean(np.array([r['error'] for r in subset])**2,axis=0)).tolist(),
                               'mean_baseline_rmse':np.sqrt(np.mean(np.array([r['regime_mean_baseline_error'] for r in subset])**2,axis=0)).tolist()}
    return {'method':method,'targets':['goodput_mbps','p95_ms','p99_ms'],'rows':results,'per_regime':per_regime,
            'leakage_boundary':'Entire core AP+CPE policy removed across all rounds/regimes; or entire round removed. Training-only means and fixed feature scales.',
            'limits':'Retrospective adaptive single-link data; no causal identification, independent sector or physical prediction acceptance'}


def _policy_package_key(policy):
    # FQ/rawRC/DSCP vary separately; the remaining declared profile is a package
    # so dependent AQL low/high/threshold and unknown baseline fields stay intact.
    return repr(replace(policy,fq_quantum_bytes=1,rc_per_thresh=0,dscp_micro_vo_steering=False))


def regime_search_space(records,regime):
    subset=[r for r in records if r.workload_regime==regime]
    if len(subset)<3:raise ValueError('At least3 windows define a regime search space')
    endpoints=('ap',) if regime==REGIMES[0] else ('ap','cpe')
    space=[]
    for endpoint in endpoints:
        policies=[getattr(r,endpoint+'_policy') for r in subset]
        packages={_policy_package_key(p):p for p in policies}
        space.extend([(endpoint+'_profile',tuple(packages[k] for k in sorted(packages))),
                      (endpoint+'_fq_quantum',tuple(sorted({p.fq_quantum_bytes for p in policies}))),
                      (endpoint+'_raw_rc',tuple(sorted({p.rc_per_thresh for p in policies}))),
                      (endpoint+'_dscp',tuple(sorted({p.dscp_micro_vo_steering for p in policies})))])
    return space


def _regime_candidate(space,indices):
    if len(indices)!=len(space):raise ValueError('Search-space index count mismatch')
    values={}
    for index,(name,levels) in zip(indices,space):
        if not np.isfinite(index) or int(index)!=index or not 0<=int(index)<len(levels):
            raise ValueError('Invalid repaired model index')
        values[name]=levels[int(index)]
    policies=[]
    for endpoint in ('ap','cpe'):
        if endpoint+'_profile' not in values:policies.append(None);continue
        policies.append(replace(values[endpoint+'_profile'],fq_quantum_bytes=values[endpoint+'_fq_quantum'],
                                rc_per_thresh=values[endpoint+'_raw_rc'],
                                dscp_micro_vo_steering=values[endpoint+'_dscp']))
    return tuple(policies)


def optimize_regime_pareto(records,regime,algorithm='nsga2',seed=20261024,population=40,generations=24):
    if regime not in REGIMES or algorithm not in {'nsga2','nsga3'}:raise ValueError('Known regime and NSGA algorithm required')
    if type(population)is not int or type(generations)is not int or not 16<=population<=256 or not 2<=generations<=200:
        raise ValueError('Bounded optimization budget required')
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.algorithms.moo.nsga3 import NSGA3
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.repair.rounding import RoundingRepair
    from pymoo.operators.sampling.rnd import IntegerRandomSampling
    from pymoo.optimize import minimize
    from pymoo.util.ref_dirs import get_reference_directions
    space=regime_search_space(records,regime);model=RegimeSurrogate(records)
    subset=[r for r in records if r.workload_regime==regime]
    eligible=[r for r in subset if r.packet_loss_pct==0 and r.station_drops==0 and r.restoration_verified]
    if not eligible:raise ValueError('No reported stable reference policy')
    stable_x=np.array([regime_features(r) for r in eligible])
    # Exact known failed policies never get promoted by interpolation smoothing.
    bad={(r.ap_policy,r.cpe_policy) for r in subset if r.packet_loss_pct or r.station_drops or not r.restoration_verified}
    radius=.9
    def evaluate(indices):
        ap,cpe=_regime_candidate(space,indices);prediction=model.predict(ap,cpe,regime)
        x=np.concatenate((endpoint_features(ap),endpoint_features(cpe)))
        support=float(np.linalg.norm(stable_x-x,axis=1).min())
        return ap,cpe,prediction,support,(ap,cpe) in bad
    class RegimeProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=len(space),n_obj=3,n_ieq_constr=2,xl=np.zeros(len(space)),
                             xu=np.array([len(levels)-1 for _,levels in space]),vtype=int)
        def _evaluate(self,indices,out,*args,**kwargs):
            ap,cpe,prediction,support,failed=evaluate(indices)
            out['F']=[-prediction['goodput_mbps']/100,prediction['p95_ms']/20,prediction['p99_ms']/20]
            out['G']=[support-radius,1 if failed else -1]
    operators=dict(pop_size=population,sampling=IntegerRandomSampling(),
                   crossover=SBX(prob=.9,eta=15,vtype=float,repair=RoundingRepair()),
                   mutation=PM(eta=20,vtype=float,repair=RoundingRepair()),eliminate_duplicates=True)
    search=NSGA2(**operators) if algorithm=='nsga2' else NSGA3(ref_dirs=get_reference_directions('das-dennis',3,n_partitions=4),**operators)
    result=minimize(RegimeProblem(),search,('n_gen',generations),seed=seed,verbose=False)
    if result.X is None or result.F is None or (result.CV is not None and np.any(result.CV>1e-8)):
        raise RuntimeError('No model-feasible regime frontier; least-infeasible results are not accepted')
    proposals={}
    for indices in np.atleast_2d(result.X):
        ap,cpe,prediction,support,failed=evaluate(indices)
        if failed or support>radius+1e-8:raise RuntimeError('Invalid final model constraint')
        key=repr((ap,cpe))
        proposals[key]={'ap_policy':ap.as_dict(),'cpe_policy':cpe.as_dict() if cpe else None,
                        'prediction':prediction,'stable_reference_distance':support,
                        'joint_policy_previously_measured':any(r.ap_policy==ap and r.cpe_policy==cpe for r in subset),
                        'automatic_execution_allowed':False,'physical_safety_qualified':False}
    proposals=[proposals[k] for k in sorted(proposals)]
    objectives=[[-p['prediction']['goodput_mbps'],p['prediction']['p95_ms'],p['prediction']['p99_ms']] for p in proposals]
    return {'regime':regime,'algorithm':algorithm,'seed':seed,'population':population,'generations':generations,
            'evaluations':int(result.algorithm.evaluator.n_eval),'model_support_radius':radius,
            'search_dimensions':[{'name':name,'levels':len(levels)} for name,levels in space],
            'search_space_combinations':math.prod(len(levels) for _,levels in space),
            'pareto':[proposals[i] for i in nondominated_indices(objectives)],
            'global_optimality_claim':False,'physical_feasibility_claim':False}


def build_all_rounds_dataset(algorithm='both',seed=20261024):
    if algorithm not in {'both','nsga2','nsga3'}:raise ValueError('Known NSGA algorithm required')
    records,refs=load_all_measurements()
    algorithms=('nsga2','nsga3') if algorithm=='both' else (algorithm,)
    catalog=local_json(ROOT/'orchestration/autoresearch/firmware_knob_candidates.json')
    return {'schema_version':2,'evidence':'OFFLINE_REGIME_MODEL_PROPOSALS','automatic_execution_allowed':False,
            'software_versions':software_versions(),'sources':refs,'training_windows':len(records),
            'catalog_coverage':catalog_coverage(catalog),
            'validation':{method:regime_validation(records,method) for method in ('leave_core_policy_out','leave_round_out')},
            'optimizations':[optimize_regime_pareto(records,regime,name,seed) for regime in REGIMES for name in algorithms],
            'native_integration_status':'EXECUTED_WITH_PYMOO',
            'limits':['Three separate workload response models; no pooling of bulk and bidirectional contention',
                      'Outcome-derived retry/ULratio/fairness are not surrogate inputs',
                      'All58 windows, including5lossful windows, retained for model diagnostics; exact failed policy pairs excluded from proposals',
                      'Per-AC threshold/low/high stay observed packages; FQ/rawRC/DSCP combinations may be unmeasured',
                      'DSCP EF source flag does not verify actual TID/AC mapping or establish causal improvement',
                      'Model support and reported restoration are not device-safe qualification or physical accuracy acceptance']}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--algorithm',choices=['nsga2','nsga3','both'],default='both')
    parser.add_argument('--seed',type=int,default=20261024)
    parser.add_argument('--all-rounds',action='store_true',help='Use frozenR1..R9 and three workload regimes')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    dataset=build_all_rounds_dataset(args.algorithm,args.seed) if args.all_rounds else build_dataset(args.algorithm,args.seed)
    output=args.output or (EFGH_ARTIFACTS/'pareto_r1_to_r9_candidates_20261024.json' if args.all_rounds else ARTIFACTS/'doe_pymoo_candidate_batches_20261024.json')
    write_json(output,dataset)
    print(f"{dataset['native_integration_status']}: {output}")
    return 0 if dataset['native_integration_status']=="EXECUTED_WITH_PYMOO" else 2


if __name__=='__main__':
    raise SystemExit(main())
