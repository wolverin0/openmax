"""Source-bound, non-actuating information-gain campaign planning.

An ideal hypothetical observation is an information ceiling, not a calibrated
expectation or physical authority. No device or acquisition module is imported.
"""
from dataclasses import dataclass
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import math

ROOT=Path(__file__).resolve().parents[2]
DEFAULT_MATRIX=ROOT/'artifacts/autoresearch/knob_248_untested_matrix_20261024.json'
DEFAULT_ORIGINAL_CATALOG=ROOT/'artifacts/autoresearch/waves_abcd_20261024/inputs/firmware_knob_candidates.json'
DEFAULT_ARTIFACT=ROOT/'artifacts/autoresearch/top50_next_bench_campaigns_20261024.json'
FRONTIER_SHA256='59f27678b65aeb04ba97f7e51bc499496c6cd1c7cf6e3d921b47ecf02f7ec834'
ORIGINAL_SHA256='b2810269d0a7afb8715ebbeb901e169a2fd0b5cf61c3d667f91d7aae15585c07'
UNTESTED='UNTESTED_EXACT_INTERFACE_IN_SAVED_CORPUS'
COUNTS={'TESTED_AS_DECLARED_PACKAGE':8,'PACKAGE_VALUE_RECORDED_NO_VARIED_TREATMENT':1,
        UNTESTED:81,'INAPPLICABLE_CLOSED_FIRMWARE_BUILD_TO_OPENWRT_CORPUS':96,
        'PROTECTED_OR_EXCLUDED_NO_TREATMENT_AUTHORITY':62}
PREREQUISITES=('EXACT_RUNTIME_BUILD','EXACT_CONTROL_HOOK_AND_EFFECTIVE_READBACK','APPROVED_TREATMENT_RANGE',
               'UNCHANGED_CONTROL_PACKAGE_AND_BASELINE','VERIFIED_RESTORATION_AND_RECOVERY',
               'EXPLICIT_DEVICE_AND_CAMPAIGN_AUTHORITY','PREDECLARED_PAIRING_POWER_AND_MULTIPLICITY')
ENVELOPE_KEYS={'plan','status','task_id','created_utc','software_verification','independent_reviews','bindings'}


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _json(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate JSON key')
            result[key]=value
        return result
    def reject(token):raise ValueError('Nonfinite JSON token: '+token)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)


def _path(value):
    if not isinstance(value,(str,Path)):raise ValueError('Explicit local path required')
    text=str(value)
    if not text or text.startswith(('\\\\','//'))or '://'in text or any(c in text for c in ('\n','\r','\0')):
        raise ValueError('Only explicit local filesystem paths are accepted')
    resolved=(ROOT/Path(text)).resolve()
    if str(resolved).startswith(('\\\\','//')):
        raise ValueError('Resolved paths must remain local; remote reparse targets are forbidden')
    return resolved


def _display(path):
    path=_path(path)
    return path.relative_to(ROOT).as_posix()if path.is_relative_to(ROOT)else str(path)


def _binding(path,raw):return dict(path=_display(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def _vector(values,label):
    if not isinstance(values,(list,tuple))or not 1<=len(values)<=256:raise ValueError(label+' must have1..256 entries')
    result=[]
    for value in values:
        if type(value)not in (int,float):raise ValueError('Probability must be a finite number, not bool')
        try:number=float(value)
        except (OverflowError,ValueError)as error:raise ValueError('Probability overflow')from error
        if not math.isfinite(number)or not 0<=number<=1:raise ValueError('Probability outside[0,1]')
        result.append(number)
    if abs(math.fsum(result)-1)>1e-12:raise ValueError(label+' must sum to1')
    return result


def _model(prior,likelihoods):
    prior=_vector(prior,'prior')
    if not isinstance(likelihoods,(list,tuple))or len(likelihoods)!=len(prior):raise ValueError('One likelihood row per hypothesis required')
    rows=[_vector(row,'likelihood row')for row in likelihoods]
    if len({len(row)for row in rows})!=1:raise ValueError('Outcome dimensions must match')
    return dict(prior=prior,likelihoods=rows)


def expected_information_gain(prior,likelihoods):
    """Mutual information in bits: hypotheses x outcomes row-stochastic channel.

    This is exact for the supplied probabilistic model up to binary64 arithmetic;
    its calibration and usefulness for a physical control are separate unknowns.
    """
    model=_model(prior,likelihoods);p=model['prior'];rows=model['likelihoods']
    marginal=[math.fsum(p[s]*rows[s][o]for s in range(len(p)))for o in range(len(rows[0]))]
    terms=[p[s]*q*(math.log2(q)-math.log2(marginal[o]))for s,row in enumerate(rows)for o,q in enumerate(row)if p[s]*q>0]
    gain=math.fsum(terms);entropy=-math.fsum(x*math.log2(x)for x in p if x)
    if not math.isfinite(gain)or gain < -1e-10 or gain>entropy+1e-10:raise ValueError('Invalid computed information')
    return min(entropy,max(0.0,gain))


@dataclass(frozen=True)
class BoundFrontier:
    matrix_path: str
    original_catalog_path: str
    matrix_bytes: bytes
    original_catalog_bytes: bytes

    def __post_init__(self):
        if type(self.matrix_bytes)is not bytes or type(self.original_catalog_bytes)is not bytes:
            raise ValueError('Immutable source bytes required')
        if hashlib.sha256(self.matrix_bytes).hexdigest()!=FRONTIER_SHA256 or hashlib.sha256(self.original_catalog_bytes).hexdigest()!=ORIGINAL_SHA256:
            raise ValueError('Unrecognized historical frontier/catalog bytes')
        matrix=_json(self.matrix_bytes);original=_json(self.original_catalog_bytes)
        rows=matrix['rows'];knobs=original['knobs']
        if len(rows)!=248 or len(knobs)!=248 or len({r['id']for r in rows})!=248 or [r['id']for r in rows]!=[k['id']for k in knobs]:
            raise ValueError('Exactly original248 unique identities in original order required')
        if matrix['original_catalog']['sha256']!=ORIGINAL_SHA256 or matrix['original_catalog']['bytes']!=len(self.original_catalog_bytes):
            raise ValueError('Original catalog binding mismatch')
        if Counter(r['classification']['status']for r in rows)!=COUNTS:raise ValueError('Exact248 classification counts required')
        for row,knob in zip(rows,knobs):
            if row['original_row_sha256']!=canonical_sha(knob)or row['interface']!=knob['interface']or row['build_scope']!=knob['platform_scope']:
                raise ValueError('Exact source identity/interface/build mismatch')
            if row['classification']['treatment_authorized']is not False or row['classification']['approved_safe_range']is not None or row['automatic_execution_allowed']is not False:
                raise ValueError('No physical authority or safe range exists in this frontier')

    @property
    def matrix(self):return _json(self.matrix_bytes)  # Fresh copy; caller mutations cannot change the bound view.

    @property
    def original_catalog(self):return _json(self.original_catalog_bytes)


def load_frontier(matrix_path=DEFAULT_MATRIX,expected_sha256=FRONTIER_SHA256,original_catalog_path=DEFAULT_ORIGINAL_CATALOG):
    """Read only caller-explicit paths; never follow paths embedded in metadata."""
    if expected_sha256!=FRONTIER_SHA256:raise ValueError('This task requires the exact pinned248 frontier')
    matrix_path=_path(matrix_path);original_catalog_path=_path(original_catalog_path)
    raw=matrix_path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('Frontier checksum mismatch')
    return BoundFrontier(_display(matrix_path),_display(original_catalog_path),raw,original_catalog_path.read_bytes())


def build_campaign_schedule(frontier,limit=50,models=None,*,artifact_path=DEFAULT_ARTIFACT):
    if type(frontier)is not BoundFrontier:raise ValueError('Authenticated immutable frontier required')
    if type(limit)is not int or not 1<=limit<=50:raise ValueError('Campaign limit must be an exact integer1..50')
    matrix=frontier.matrix;original={k['id']:k for k in frontier.original_catalog['knobs']}
    rows=[r for r in matrix['rows']if r['classification']['status']==UNTESTED]
    ids={r['id']for r in rows}
    if models is not None and(not isinstance(models,dict)or set(models)!=ids):
        raise ValueError('Caller hypothetical models must cover all81eligible controls, without unknown IDs')
    parsed=None
    if models is not None:
        parsed={}
        for key,model in models.items():
            if not isinstance(model,dict)or set(model)!={'prior','likelihoods'}:raise ValueError('Model shape must be prior+likelihoods only')
            parsed[key]=_model(model['prior'],model['likelihoods'])
    ideal=dict(prior=[.5,.5],likelihoods=[[1.,0.],[0.,1.]])
    ranking=[]
    for row in rows:
        model=ideal if parsed is None else parsed[row['id']]
        ranking.append(dict(control_id=row['id'],hypothetical_information_gain_bits=expected_information_gain(**model),expected_information_gain_bits=None))
    ranking.sort(key=lambda r:(-r['hypothetical_information_gain_bits'],r['control_id']))
    by_id={r['id']:r for r in rows};campaigns=[];artifact=_display(artifact_path)
    for rank,entry in enumerate(ranking[:limit],1):
        key=entry['control_id'];row=by_id[key];campaign_id='FMX-KNOB-'+key
        command=['python','-B','-m','orchestration.autoresearch.fmx_knob_campaign_scheduler','--matrix',frontier.matrix_path,
                 '--expected-sha256',FRONTIER_SHA256,'--original-catalog',frontier.original_catalog_path,
                 '--validate',artifact,'--campaign-id',campaign_id]
        campaigns.append(dict(campaign_id=campaign_id,rank=rank,control_id=key,status='BLOCKED',physical_ready=False,
            expected_information_gain_bits=None,hypothetical_information_gain_bits=entry['hypothetical_information_gain_bits'],
            source_identity=dict(original_row_sha256=row['original_row_sha256'],frontier_row_sha256=canonical_sha(row),
                interface=row['interface'],build_scope=row['build_scope'],boundary=row['boundary'],family=row['family'],
                source_unit=original[key]['encoding_domain'].get('unit'),unit_is_static_metadata_not_approved_range=True,
                original_source_refs=row['original_source_refs']),
            prerequisites=[dict(requirement=p,status='MISSING_UNQUALIFIED',satisfied=False)for p in PREREQUISITES],
            treatment_value=None,restore_value=None,physical_command=None,approved_safe_range=None,
            treatment_authorized=False,automatic_execution_allowed=False,
            prospective_recipe=dict(kind='FUTURE_SINGLE_CONTROL_RANDOMIZED_PAIRED_DESIGN_NOT_EXECUTABLE',
                exactly_one_varied_control=key,all_other_controls_must_be_held_fixed=True,
                independent_pair_ids='MUST_BE_DECLARED_BEFORE_ACQUISITION_NOT_PING_INDICES',
                treatment_order='RANDOMIZED_AB_BA_WITH_SOURCE_BOUND_SCHEDULE_REQUIRED',
                randomization_seed=None,pair_count=None,washout=None,baseline_package=None,
                power=dict(effect_size=None,target_power=None,alpha=None,unit='GENUINE_INDEPENDENT_PAIRED_BLOCK'),
                multiplicity=dict(family_id=None,hypotheses=None,FWER_alpha=None,method='PREDECLARE_COMPLETE_FAMILY_BEFORE_DATA'),
                acceptance_and_rollback_thresholds=None,physical_execution_authorized=False),
            offline_validation_command=command))
    return dict(schema_version=1,status='PROSPECTIVE_OFFLINE_PLAN_ALL_PHYSICAL_CAMPAIGNS_BLOCKED',
        frontier=_binding(frontier.matrix_path,frontier.matrix_bytes),original_catalog=_binding(frontier.original_catalog_path,frontier.original_catalog_bytes),
        artifact_path=artifact,limit=limit,models=parsed,
        model_mode='DEFAULT_HYPOTHETICAL_IDEAL_BINARY_CEILING'if parsed is None else'CALLER_COMPLETE_HYPOTHETICAL_MODEL_MAP',
        assumptions=['Actual/calibrated expected information gain UNKNOWN for every control.',
            'Default p=.5/perfect availability observation is a1bit hypothetical ceiling, not predicted benefit.',
            'Supplied models are also hypothetical; none supplies build, range, recovery or authority.',
            'Help-only, host shadows, WMI enumeration and qdisc metadata are not firmware effect/readback qualification.',
            'No isolated effect, physical safe range, wireless gain or actuation is inferred.'],
        ranking_rule='HYPOTHETICAL_EIG_DESCENDING_THEN_STABLE_ID_ASCENDING_NO_BENEFIT_TIE_CLAIM',
        original_control_count=248,eligible_control_count=81,excluded_control_count=167,
        ranked_controls=ranking,excluded_control_ids=sorted(r['id']for r in matrix['rows']if r['classification']['status']!=UNTESTED),
        campaign_count=len(campaigns),physical_ready_count=0,physical_acceptance=False,automatic_execution_allowed=False,campaigns=campaigns)


def validate_schedule(schedule,frontier,*,artifact_path=None):
    if not isinstance(schedule,dict):raise ValueError('Schedule object required')
    if 'plan'in schedule:
        if set(schedule)-ENVELOPE_KEYS:raise ValueError('Unknown envelope fields; no authority override accepted')
        def metadata(value):
            if isinstance(value,dict):
                for key,item in value.items():
                    if key in ('physical_ready','physical_acceptance','automatic_execution_allowed','treatment_authorized')and item is not False:
                        raise ValueError('Metadata cannot grant physical authority')
                    if key in ('physical_command','treatment_value','restore_value','approved_safe_range')and item is not None:
                        raise ValueError('Metadata cannot inject a physical treatment')
                    metadata(item)
            elif isinstance(value,list):
                for item in value:metadata(item)
        try:canonical_sha(schedule)
        except (TypeError,ValueError,OverflowError)as error:raise ValueError('Envelope must be finite JSON metadata')from error
        metadata({k:v for k,v in schedule.items()if k!='plan'})
        schedule=schedule['plan']
    if not isinstance(schedule,dict):raise ValueError('Plan object required')
    if artifact_path is not None and schedule.get('artifact_path')!=_display(artifact_path):raise ValueError('Artifact path differs from explicit validation input')
    try:expected=build_campaign_schedule(frontier,schedule['limit'],schedule['models'],artifact_path=schedule['artifact_path'])
    except (KeyError,TypeError,OverflowError)as error:raise ValueError('Malformed declared plan')from error
    if canonical_sha(schedule)!=canonical_sha(expected):raise ValueError('Schedule differs from source/model-bound regeneration')
    return True


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix',default=str(DEFAULT_MATRIX));parser.add_argument('--expected-sha256',default=FRONTIER_SHA256)
    parser.add_argument('--original-catalog',default=str(DEFAULT_ORIGINAL_CATALOG));parser.add_argument('--campaign-id')
    action=parser.add_mutually_exclusive_group(required=True);action.add_argument('--generate');action.add_argument('--validate')
    args=parser.parse_args(argv);frontier=load_frontier(args.matrix,args.expected_sha256,args.original_catalog)
    if args.generate:
        if args.campaign_id:raise ValueError('campaign-id is a validation selector only')
        path=_path(args.generate);plan=build_campaign_schedule(frontier,artifact_path=path)
        with path.open('x',encoding='utf-8',newline='\n')as f:json.dump(plan,f,indent=2,allow_nan=False);f.write('\n')
        print(json.dumps(dict(status='GENERATED_OFFLINE_ONLY',campaigns=50,physical_ready=0,path=_display(path))))
    else:
        path=_path(args.validate);schedule=_json(path.read_bytes());validate_schedule(schedule,frontier,artifact_path=path)
        plan=schedule['plan']if 'plan'in schedule else schedule
        if args.campaign_id and args.campaign_id not in {c['campaign_id']for c in plan['campaigns']}:raise ValueError('Unknown campaign identity')
        print(json.dumps(dict(status='VALID_OFFLINE_PLAN_ONLY',campaigns=len(plan['campaigns']),physical_ready=0,campaign_id=args.campaign_id)))
    return 0


if __name__=='__main__':raise SystemExit(main())
