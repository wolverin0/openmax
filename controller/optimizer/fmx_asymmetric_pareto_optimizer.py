"""Offline native NSGA-II/III over a bounded, explicitly hypothetical SimPy model.

Run: python -B -m controller.optimizer.fmx_asymmetric_pareto_optimizer
Only four frozen local inputs are read; recipes are hashed, never imported.
Candidates are disabled model proposals, not observed/physically safe packages.
"""
from dataclasses import asdict, replace
import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.repair import Repair
from pymoo.optimize import minimize
from pymoo.util.ref_dirs import get_reference_directions

from analysis.simulation.fmx_asymmetric_ap_cpe_sim import Endpoint, Scenario, simulate, integer


ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'artifacts/autoresearch/waves_mnop_20261024'
SEED=20261024
# Encoding/proposed search box only, never hardware-safe ranges. Six coordinates
# per endpoint: BE-low us, FQ bytes, target us, interval us, TSQ KiB, notsent KiB.
LOWER=np.array([1000,200,5000,30000,96,48]*2,dtype=int)
UPPER=np.array([2500,400,20000,100000,512,256]*2,dtype=int)
COORDINATES=['be_low_us','fq_quantum_bytes','fq_target_us','fq_interval_us',
             'tcp_limit_output_KiB','tcp_notsent_lowat_KiB']


def repaired(vector):
    if any(isinstance(x,(bool,np.bool_)) for x in vector):
        raise ValueError('Boolean search coordinates are not numeric measurements')
    a=np.asarray(vector)
    if a.shape!=(12,) or a.dtype.kind not in 'iuf' or not np.isfinite(a).all():
        raise ValueError('Twelve finite real coordinates required')
    x=np.clip(np.rint(a),LOWER,UPPER).astype(int)
    for start in (0,6):
        x[start+3]=max(x[start+3],x[start+2])
        x[start+5]=min(x[start+5],x[start+4])
    return tuple(int(i) for i in x)


def decode(vector):
    if (not isinstance(vector,(tuple,list)) or len(vector)!=12
            or any(type(x) is not int for x in vector)):
        raise ValueError('Exactly twelve repaired integer coordinates required')
    if any(not lo<=x<=hi for x,lo,hi in zip(vector,LOWER,UPPER)):
        raise ValueError('Outside declared model search box')
    endpoints=[]
    for start in (0,6):
        lo,fq,target,interval,tsq,notsent=vector[start:start+6]
        if notsent>tsq:raise ValueError('Outside proposed notsent<=TSQ search constraint')
        endpoints.append(Endpoint(lo,lo*2,lo*4,fq,target,interval,tsq*1024,notsent*1024).validate())
    return tuple(endpoints)


def mean(values):return math.fsum(values)/len(values)


class CaseBank:
    """One global unique-case cap, including calibration/validation/search.

    Replications are fixed at three, with identical arrival/backoff/service seed
    blocks across candidates. These are model MC replicates, not physical trials.
    """
    def __init__(self,*,max_cases=128,seed=SEED,scenario=Scenario()):
        integer(max_cases,'case cap',1,128);integer(seed,'base seed',0,2**31-4)
        self.max_cases=max_cases;self.seed=seed;self.scenario=scenario.validate();self.cache={}

    def evaluate(self,ap,cpe,*,capacity=None):
        ap.validate();cpe.validate();s=self.scenario if capacity is None else replace(self.scenario,capacity_mbps=capacity).validate()
        key=json.dumps([asdict(ap),asdict(cpe),asdict(s)],sort_keys=True,allow_nan=False)
        if key not in self.cache:
            if len(self.cache)>=self.max_cases:raise RuntimeError('Global model case budget exhausted')
            runs=[simulate(ap,cpe,s,seed=self.seed+i) for i in range(3)]
            if any(r['DL']['delay_p95_ms'] is None or r['UL']['delay_p95_ms'] is None for r in runs):
                raise ValueError('No completed delay cohort; model objective unavailable')
            metrics=dict(dl_goodput_mbps=mean([r['DL']['goodput_mbps'] for r in runs]),
                ul_goodput_mbps=mean([r['UL']['goodput_mbps'] for r in runs]),
                rtt_p95_proxy_ms=mean([r['rtt_p95_proxy_ms'] for r in runs]),
                jain_directional=mean([r['jain_directional'] for r in runs]))
            metrics['total_goodput_mbps']=metrics['dl_goodput_mbps']+metrics['ul_goodput_mbps']
            self.cache[key]=dict(metrics=metrics,runs=runs,case_id=hashlib.sha256(key.encode()).hexdigest())
        return self.cache[key]


class IntegerRepair(Repair):
    def _do(self,problem,X,**kwargs):
        return np.asarray([repaired(x) for x in X],dtype=int)


def objective(metrics):
    return [-metrics['dl_goodput_mbps'],-metrics['ul_goodput_mbps'],
            metrics['rtt_p95_proxy_ms'],1-metrics['jain_directional']]


class AsymmetricProblem(ElementwiseProblem):
    def __init__(self,bank,capacity):
        self.bank=bank;self.capacity=capacity
        super().__init__(n_var=12,n_obj=4,n_ieq_constr=4,xl=LOWER,xu=UPPER)

    def _evaluate(self,x,out,*args,**kwargs):
        # Recheck exact integer encoding AND original feasibility after repair.
        vector=tuple(int(v) for v in x)
        if not np.equal(np.asarray(vector),x).all():raise ValueError('Unrepaired noninteger search coordinate')
        ap,cpe=decode(vector)
        out['F']=objective(self.bank.evaluate(ap,cpe,capacity=self.capacity)['metrics'])
        out['G']=[ap.fq_target_us-ap.fq_interval_us,ap.tcp_notsent_lowat-ap.tcp_limit_output_bytes,
                  cpe.fq_target_us-cpe.fq_interval_us,cpe.tcp_notsent_lowat-cpe.tcp_limit_output_bytes]


def nondominated(F):
    a=np.asarray(F,dtype=float)
    if a.ndim!=2 or a.shape[1]!=4 or not np.isfinite(a).all():raise ValueError('Four finite objectives required')
    return [i for i in range(len(a)) if not any(np.all(a[j]<=a[i]) and np.any(a[j]<a[i])
                                              for j in range(len(a)) if i!=j)]


def optimize(bank,capacity,*,population=12,generations=3):
    integer(population,'population',10,32);integer(generations,'generations',1,10)
    problem=AsymmetricProblem(bank,capacity);outputs=[]
    for name,algorithm in [('NSGA-II',NSGA2(pop_size=population,repair=IntegerRepair())),
        ('NSGA-III',NSGA3(ref_dirs=get_reference_directions('das-dennis',4,n_partitions=2),
                         pop_size=population,repair=IntegerRepair()))]:
        result=minimize(problem,algorithm,('n_gen',generations),seed=bank.seed,verbose=False)
        if result.X is None:raise RuntimeError(name+' returned no feasible solution')
        candidates=[]
        for x,stored_f,stored_g in zip(np.atleast_2d(result.X),np.atleast_2d(result.F),np.atleast_2d(result.G)):
            vector=tuple(int(v) for v in x)
            if not np.equal(x,vector).all():raise ValueError('Returned coordinates not integral')
            ap,cpe=decode(vector);case=bank.evaluate(ap,cpe,capacity=capacity);fresh=objective(case['metrics'])
            if any(g>0 for g in stored_g) or not np.allclose(fresh,stored_f,rtol=0,atol=1e-10):
                raise ValueError('Repaired feasibility/objective verification failed')
            candidates.append(dict(vector=list(vector),AP=asdict(ap),CPE=asdict(cpe),
                objectives=fresh,metrics=case['metrics'],case_id=case['case_id'],enabled=False,
                automatic_execution_allowed=False,physical_safety_qualified=False,
                provenance='UNMEASURED_MODEL_PROPOSAL_IN_ASSUMED_SEARCH_BOX'))
        keep=nondominated([c['objectives'] for c in candidates])
        if len(keep)!=len(candidates):raise ValueError('Native returned dominated solution')
        outputs.append(dict(algorithm=name,population=population,generations=generations,
                            evaluations=int(result.algorithm.evaluator.n_eval),candidates=candidates))
    return outputs


def endpoint_from_observed(p):
    if p is None:raise ValueError('Endpoint policy absent')
    low=p.get('be_low_us',p.get('aql_by_ac',[[None,None]]*3)[2][0])
    high=p.get('be_high_us',p.get('aql_by_ac',[[None,None]]*3)[2][1])
    return Endpoint(low,high,*(p.get(k) for k in ('aql_threshold_us','fq_quantum_bytes','fq_target_us',
        'fq_interval_us','tcp_limit_output_bytes','tcp_notsent_lowat'))).validate()


def frozen_inputs():
    manifest=json.loads((BASE/'inputs_manifest.json').read_text(encoding='utf-8'));refs=[];raw={}
    if len(manifest)!=4:raise ValueError('Expected exactly four frozen inputs')
    for entry in manifest:
        path=(ROOT/entry['path']).resolve()
        if not path.is_relative_to((BASE/'inputs').resolve()):raise ValueError('Input escape')
        data=path.read_bytes()
        if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('Frozen input mismatch')
        refs.append({k:entry[k] for k in ('path','bytes','sha256')})
        if path.suffix=='.json':raw[path.name]=json.loads(data)
        else:data.decode('utf-8')  # recipe/TSV validation as TEXT only
    r15=next(v for k,v in raw.items() if 'r15_' in k)
    prior=next(v for k,v in raw.items() if 'normalized_r1_to_r14' in k)
    return r15['iterations'],prior['records'],refs


def policy_key(ap,cpe):
    return json.dumps([asdict(ap),asdict(cpe),'psk2'],sort_keys=True)


def model_assessment(bank):
    training,prior,refs=frozen_inputs()
    if len(training)!=4 or len(prior)!=85:raise ValueError('Expected four R15 and85 prior records; do not fabricate90th')
    train=[];keys=set()
    for row in training:
        ap=endpoint_from_observed(row['candidate_knobs']['ap_state']);cpe=endpoint_from_observed(row['candidate_knobs']['cpe_state'])
        keys.add(policy_key(ap,cpe));train.append((row,ap,cpe))
    # One predeclared scalar capacity fitted on four windows only. Hypothesized
    # CPU costs, load and structural scheduling are NOT tuned against holdouts.
    trials=[]
    for cap in (90,120,150):
        errors=[bank.evaluate(ap,cpe,capacity=cap)['metrics']['total_goodput_mbps']-r['total_bidir_goodput_mbps'] for r,ap,cpe in train]
        trials.append(dict(capacity_mbps=cap,in_sample_rmse_mbps=math.sqrt(mean([e*e for e in errors]))))
    chosen=min(trials,key=lambda t:(t['in_sample_rmse_mbps'],t['capacity_mbps']))['capacity_mbps']
    fitted=[dict(iteration=r['commit'],prediction=bank.evaluate(ap,cpe,capacity=chosen)['metrics'],
                 observed_total_mbps=r['total_bidir_goodput_mbps'],
                 observed_DL_UL_mbps=[r['dl_goodput_mbps'],r['ul_goodput_mbps']],
                 interpretation='IN_SAMPLE_ONLY_NOT_INDEPENDENT_VALIDATION') for r,ap,cpe in train]
    assessed=[];excluded=[]
    for row in prior:
        reason=None
        if row.get('window_kind')!='primary':reason='SUMMARY_ONLY'
        elif row.get('encryption_mode')!='psk2':reason='OUTSIDE_DECLARED_WPA2_MODEL_DOMAIN'
        elif row.get('distance_meters') not in (None,0):reason='COVERAGE_TIMING_NOT_MODELED'
        try:
            ap=endpoint_from_observed(row['ap_policy']);cpe=endpoint_from_observed(row['cpe_policy'])
        except (ValueError,TypeError,KeyError):reason=reason or 'MODEL_INPUT_COORDINATES_UNRECORDED'
        if reason is None and policy_key(ap,cpe) in keys:reason='WHOLE_MODELED_JOINT_POLICY_SEEN_IN_R15_CALIBRATION'
        identity=dict(round_id=row['round_id'],iteration=row['iteration'])
        if reason:excluded.append(dict(**identity,reason=reason));continue
        metrics=bank.evaluate(ap,cpe,capacity=chosen)['metrics']
        assessed.append(dict(**identity,kind='WHOLE_MODELED_POLICY_HELD_OUT_EARLIER_ROUND',
            quality_accepted=False,quality_negative_observation=bool(row['packet_loss_pct'] or row['station_drops'] or not row['restoration_verified']),
            prediction=metrics,observed=dict(dl_goodput_mbps=row['dl_goodput_mbps'],ul_goodput_mbps=row['ul_goodput_mbps'],
                total_goodput_mbps=row['goodput_mbps'],rtt_p95_proxy_ms=row['p95_ms'],jain_directional=row['jain_fairness']),
            training_policy_overlap=False))
    errors={}
    for name in ('dl_goodput_mbps','ul_goodput_mbps','total_goodput_mbps','rtt_p95_proxy_ms','jain_directional'):
        errors[name]=math.sqrt(mean([(a['prediction'][name]-a['observed'][name])**2 for a in assessed])) if assessed else None
    return chosen,dict(calibration_kind='IN_SAMPLE_GLOBAL_CAPACITY_GRID_ON_FOUR_R15_WINDOWS_ONLY',
        calibration_window_ids=[r['commit'] for r,_,_ in train],capacity_grid=trials,selected_capacity_mbps=chosen,
        selected_grid_boundary=chosen in (90,150),in_sample_assessment=fitted,
        training_windows=4,heldout_windows=len(assessed),heldout=assessed,excluded_prior=excluded,
        heldout_rmse=errors,physical_predictive_accuracy_accepted=False,
        comparison_limits=['RTT proxy is sum of model directional95ths, not an ICMP RTT quantile.',
                           'Whole MODELED policy excluded; omitted driver/AC/RC coordinates still unmodeled confounders.',
                           'Earlier sequential windows are not prospective randomized validation.',
                           'No R14 open-crypto accuracy projection; no independent per-rep RTT arrays invented.']),refs


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--population',type=int,default=12)
    parser.add_argument('--generations',type=int,default=3);args=parser.parse_args()
    bank=CaseBank();capacity,assessment,refs=model_assessment(bank)
    results=optimize(bank,capacity,population=args.population,generations=args.generations)
    output=dict(schema_version=1,status='OFFLINE_NATIVE_SIMPY_AND_PYMOO_EXECUTED_MODEL_ONLY',
        automatic_execution_allowed=False,physical_acceptance_claim=False,source_refs=refs,
        software_versions={k:importlib.metadata.version(k) for k in ('simpy','pymoo','numpy','scipy')},
        observed_total_records=89,requested90_discrepancy='Only four frozen R15 windows; missing fifth not fabricated',
        model=asdict(bank.scenario),assessment=assessment,algorithms=results,
        bounds=dict(kind='PROPOSED_MODEL_ENCODING_ONLY_NOT_SAFE_RAM_RANGE',coordinates=COORDINATES,
                    lower=LOWER.tolist(),upper=UPPER.tolist(),be_high='2*low',aql_threshold='4*low'),
        budgets=dict(unique_cases=len(bank.cache),maximum_unique_cases=128,replications_per_case=3,
                     simulated_replications=3*len(bank.cache),seeds=[bank.seed+i for i in range(3)]),
        units=dict(objectives=['negative_DL_Mbps','negative_UL_Mbps','sum_directional_p95_delay_ms','1-Jain_DL_UL'],
                   tsq='KiB encoded search coordinates converted to bytes; per-flow source opportunity suppression',
                   airtime='microseconds',clock='seconds'),
        limits=['Disabled unmeasured proposals; no objective/global Pareto optimum or hardware-safe claim.',
                'CCMP4usDL/15usUL are hypothesized CPU-preparation costs, not observed offload.',
                'Single-link abstract BE queues, no multivendor/PHY/ACK/Linux conformance proof.'])
    BASE.mkdir(parents=True,exist_ok=True)
    path=BASE/'asymmetric_pareto_candidates_20261024.json'
    with path.open('x',encoding='utf-8',newline='\n') as f:json.dump(output,f,indent=2,allow_nan=False);f.write('\n')
    runs=BASE/'wave_n_simpy_runs.json'
    with runs.open('x',encoding='utf-8',newline='\n') as f:json.dump(list(bank.cache.values()),f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(dict(status=output['status'],cases=len(bank.cache),path=str(path))))


if __name__=='__main__':main()
