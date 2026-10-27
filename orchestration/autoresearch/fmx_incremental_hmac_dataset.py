"""Authenticated saved R147-R169 append and exact-context abstention.

Recipes are AST/text evidence, never executable inputs. Source declarations,
saved readbacks, optimizer labels and physical/causal qualification stay separate.
All older serializers are reused without changing their code or saved objects.
"""
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import re

from orchestration.autoresearch import fmx_full_hmac_dataset as full

live=full.live
old=live.old
ROOT=full.ROOT
REGIME=full.REGIME
OUT=ROOT/'artifacts/autoresearch/waves_auto_codex_01_20261024'
MANIFEST=OUT/'inputs_manifest.json'
MANIFEST_SHA256='2411da881e8b507457d3cc4e091d983cc5ac1ccfc45992850cb34ba695070720'
PREFIX_RECORDS=full.OUT/'normalized_r1_to_r146_measurements_20261024.json'
PREFIX_BLOCKS=full.OUT/'normalized_r16_to_r146_block_observations_20261024.json'
PREFIX={
    'records':dict(path=PREFIX_RECORDS.relative_to(ROOT).as_posix(),bytes=16815876,sha256='34944672ce2d30f8f94e57f13357a12567c5833a15d3cbd60472c2631ece10f3'),
    'blocks':dict(path=PREFIX_BLOCKS.relative_to(ROOT).as_posix(),bytes=10378696,sha256='fd1ced8a11e348d1d80b3c3aacabffaafb1b76a2498e7d950aabfc167ab31118'),
    'package_audit':dict(path=(full.OUT/'full_hmac_package_audit.json').relative_to(ROOT).as_posix(),bytes=88378,sha256='7f7f31b5d3d41fda821fa39cb8e1afe22e45f3dec73978082fe51307a32985bb'),
    'context_matrix':dict(path=(full.OUT/'complete_regime_matrix.json').relative_to(ROOT).as_posix(),bytes=22610885,sha256='b20826d3ce5baaa8ed1958b89a1eb88807d92bfa53f525680acaf85cbe256474')}
_SIX=((1000,2,15,36),(3000,6,27,48),(6000,13,48,69),
      (9000,20,69,90),(12000,26,87,108),(14000,31,102,123))
CONTEXTS={n:_SIX[(n-147)%6] for n in range(147,165)}
CONTEXTS.update({n:(6000,13,48,69) for n in range(165,170)})
_METADATA={'name','description','complexity_cost'}
_ENDPOINT_FIELDS=set('vo_low_us vo_high_us vi_low_us vi_high_us be_low_us be_high_us bk_low_us bk_high_us aql_threshold_us fq_quantum_bytes fq_target_us fq_interval_us rc_per_thresh dscp_micro_vo_steering tcp_limit_output_bytes tcp_notsent_lowat'.split())
_KNOB_FIELDS=_METADATA|set('ap_state cpe_state traffic_regime active_flow_count bidirectional voip_probe_tos distance_m coverage_class slot_time_us ack_timeout_us airtime_flags tx_aggr_factor fq_limit fq_flows force_tx_status short_retry_limit long_retry_limit'.split())
_TEMPLATE_SHAPE_SHA='29ea60f6f7cd2887848bea6492550fcda780f91de231102aaa2881635eecb8ef'


def _read_bound(path,pin):
    raw=full._safe_path(path).read_bytes()
    if len(raw)!=pin['bytes'] or hashlib.sha256(raw).hexdigest()!=pin['sha256']:
        raise ValueError('Authenticated source bytes or SHA256 differ')
    return raw


def _inputs(manifest_path,expected_manifest_sha256):
    if expected_manifest_sha256!=MANIFEST_SHA256:
        raise ValueError('Exact incremental cutoff manifest pin required before content access')
    path=full._safe_path(manifest_path);raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:raise ValueError('Manifest SHA256 mismatch')
    manifest=full._json(raw)
    if (manifest.get('planned_rounds')!=list(CONTEXTS) or manifest.get('prefix')!=PREFIX
            or [a.get('round_id') for a in manifest.get('available',[])]!=[f'R{n}' for n in CONTEXTS]
            or len(manifest.get('members',[]))!=69):raise ValueError('Exact 23-round/69-member cutoff required')
    refs={};paths={}
    for ref in manifest['members']:
        name=ref.get('path');frozen=ref.get('frozen_path')
        if (not isinstance(name,str) or not name or '\\' in name or ':' in name
                or PurePosixPath(name).is_absolute() or '..' in PurePosixPath(name).parts or name in refs):
            raise ValueError('Unique safe logical source path required')
        number=re.search(r'(?:^|_)r(\d+)(?:_|\.)',PurePosixPath(name).name)
        if not number or int(number[1])not in CONTEXTS or ref.get('round_id')!=f'R{int(number[1])}':
            raise ValueError('No future or mismatched source round')
        if ref.get('kind')not in ('receipt','tsv','recipe_text'):raise ValueError('Unknown member role')
        expected=OUT/'inputs'/name
        if frozen!=expected.relative_to(ROOT).as_posix():raise ValueError('Fixed frozen-copy tree required')
        if type(ref.get('bytes'))is not int or not 0<ref['bytes']<=10_000_000:
            raise ValueError('Bounded exact input size required')
        if not isinstance(ref.get('sha256'),str)or not re.fullmatch('[0-9a-f]{64}',ref['sha256']):
            raise ValueError('Exact member SHA256 required')
        refs[name]=deepcopy(ref);paths[name]=full._safe_path(expected)
    used=[]
    for item in manifest['available']:
        recipes=item.get('recipe_paths')
        if not isinstance(recipes,list)or len(recipes)!=1:raise ValueError('One authenticated recipe per round required')
        for key,name,kind in [('receipt',item.get('receipt'),'receipt'),('tsv_path',item.get('tsv_path'),'tsv'),('recipe',recipes[0],'recipe_text')]:
            if name not in refs or refs[name]['kind']!=kind or refs[name]['round_id']!=item['round_id']:
                raise ValueError('Per-round member identity conflict: '+key)
            used.append(name)
    if len(set(used))!=69:raise ValueError('Every member must belong to one complete triple')
    # All names/paths and ALL 69 hashes plus four sealed prefix hashes precede conversion.
    contents={name:_read_bound(path,refs[name])for name,path in paths.items()}
    prefixes={key:_read_bound(ROOT/pin['path'],pin)for key,pin in PREFIX.items()}
    for name,ref in refs.items():ref.update(original_path=name,path=paths[name].relative_to(ROOT).as_posix())
    return manifest,refs,contents,prefixes,full._binding(path,raw)


def recipe_incremental_controls(text,payload):
    """Bounded literal static-branch grammar; no title-driven defaults or execution."""
    number=old._physical_round_number(payload,max_round=169)
    if number not in CONTEXTS:raise ValueError('Only new fixed rounds R147-R169')
    tree=ast.parse(text)
    funcs=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==f'apply_r{number}_hmac_state']
    if len(funcs)!=1:raise ValueError('Unique round-specific recipe applier required')
    fn=funcs[0];nested=[n for n in fn.body if isinstance(n,ast.FunctionDef)and n.name=='_peer_extra']
    if len(nested)!=1:raise ValueError('Unique endpoint command template required')
    returns=[n for n in nested[0].body if isinstance(n,ast.Return)]
    if len(returns)!=1:raise ValueError('Single literal endpoint command return required')
    template=full._template(returns[0].value)
    shape=re.sub(r'echo "3 (16|32|64)" > '+re.escape(full.HTT_NODE),
                 'echo "3 <DECLARED_HTT>" > '+full.HTT_NODE,template)
    if hashlib.sha256(shape.encode()).hexdigest()!=_TEMPLATE_SHAPE_SHA:
        raise ValueError('Unsupported source command grammar; no silent extra control omission')
    pattern=r'if \[ "\{force_tx_status\}" = "1" \]; then\s+echo "(\d+) (\d+)" > '+re.escape(full.HTT_NODE)+r'[^\n]*\s+else\s+echo "(\d+) (\d+)" > '+re.escape(full.HTT_NODE)+r'[^\n]*\s+fi'
    matches=list(re.finditer(pattern,template))
    if len(matches)!=1:raise ValueError('Exact static HTT branch required')
    values=tuple(map(int,matches[0].groups()))
    if values not in ((3,32,3,64),(3,16,3,64),(3,64,3,64)):raise ValueError('Unsupported literal HTT pair')
    callers=[]
    for node in fn.body:
        if not isinstance(node,ast.Assign):continue
        call=node.value
        if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='rpc'and len(call.args)>=2:
            expr=call.args[1]
            if isinstance(expr,ast.BinOp)and isinstance(expr.op,ast.Add):
                callers.append((ast.unparse(call.args[0]),ast.unparse(expr.left),ast.unparse(expr.right)))
    if sorted(callers)!=[('b.ap','_r11_node_cmd(pair.ap_state)','_peer_extra(pair.ap_state)'),
                          ('b.client','_r11_node_cmd(pair.cpe_state)','_peer_extra(pair.cpe_state)')]:
        raise ValueError('Exact separate AP/CPE command callers required')
    result={}
    for item in payload['iterations']:
        knobs=item['candidate_knobs']
        if set(knobs)-_KNOB_FIELDS:raise ValueError('Unsupported source control fields')
        for endpoint in ('ap_state','cpe_state'):
            state=knobs[endpoint]
            if not isinstance(state,dict)or set(state)-(_ENDPOINT_FIELDS|_METADATA)or _ENDPOINT_FIELDS-set(state):
                raise ValueError('Complete supported endpoint control coordinates required')
        force=old.exact_integer(knobs.get('force_tx_status'),'literal HTT branch',0,1)
        pair=list(values[:2]if force==1 else values[2:]);observed={};matched={}
        readback=item.get('readback')
        if not isinstance(readback,dict):raise ValueError('Saved readback object required')
        for end in ('ap','cpe'):
            saved=readback.get(end+'_readback')
            if saved is not None and not isinstance(saved,str):raise ValueError('Saved readback must be text or unknown')
            parsed=[[int(x),int(y)]for x,y in re.findall(r'^[ \t]*(\d+)[ \t]+(\d+)[ \t]*\r?$',saved or'',re.M)]
            observed[end]=parsed;matched[end]=len(parsed)==1 and parsed[0]==pair
        result[item['commit']]=dict(status='STATIC_RECIPE_DECLARATION_NOT_EFFECTIVE_OR_ADAPTIVE_QUALIFICATION',
            declared_endpoint_pairs={e:list(pair)for e in ('ap','cpe')},
            literal_branch_pairs=dict(then_pair=list(values[:2]),else_pair=list(values[2:])),
            source_branch=dict(field='force_tx_status',value=force),
            source_lines=[nested[0].lineno,nested[0].end_lineno],
            readback_text_pairs=observed,readback_text_matches_declaration=matched,
            readback_status='MATCHED_SAVED_TEXT_ONLY'if all(matched.values())else'UNKNOWN_OR_CONFLICTING_SAVED_TEXT',
            effective_control_verified=False,feedback_adaptive_control_verified=False,GI_LDPC_STBC_setter_verified=False)
    return result


@dataclass(frozen=True)
class IncrementalHmacMeasurement(old.DyadicCampaignMeasurement):
    hmac_source_controls:dict|None=None
    voip_probe_tos:str|None=None
    voip_evidence:dict|None=None
    compound_recipe_controls:dict|None=None

    def __post_init__(self):
        super().__post_init__()
        if self.round_id not in {f'R{n}'for n in CONTEXTS}:raise ValueError('Typed incremental round outside cutoff')
        distance,coverage,slot,ack=CONTEXTS[int(self.round_id[1:])]
        if (self.workload_regime!=REGIME or type(self.active_flow_count)is not int or self.active_flow_count!=8
                or self.bidirectional is not True or type(self.distance_meters)is not int or self.distance_meters!=distance
                or type(self.coverage_class)is not int or self.coverage_class!=coverage or self.voip_probe_tos!='0xb8'
                or self.cpe_policy is None or any(type(p.distance_meters)is not int or p.distance_meters!=distance for p in (self.ap_policy,self.cpe_policy))):
            raise ValueError('Exact distinct hMAC/VoIP context required')
        evidence=self.certified_wds_evidence
        for key,value in [('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)]:
            if type(evidence.get(key))is not int or evidence[key]!=value:raise ValueError('Typed timing identity conflict')
        if any(evidence.get(k)is not False for k in ('physical_distance_verified','effective_timing_independently_verified')):
            raise ValueError('Declared timing is not independently qualified')
        if not isinstance(self.hmac_source_controls,dict)or set(self.hmac_source_controls)!={'tx_aggr_factor','fq_flows'}:
            raise ValueError('Exact labelled hMAC controls required')
        old.exact_integer(self.hmac_source_controls['tx_aggr_factor'],'tx_aggr_factor',0,255)
        old.exact_integer(self.hmac_source_controls['fq_flows'],'fq_flows',1,1_000_000)
        if self.hmac_source_controls['tx_aggr_factor']!=self.airtime_flags:raise ValueError('Derived AF alias conflict')
        if (not isinstance(self.voip_evidence,dict)or self.voip_evidence.get('effective_AC_mapping_verified')is not False
                or any(self.voip_evidence.get(k)is not None for k in ('latency_ms','jitter_ms','packet_loss_pct','mos'))):
            raise ValueError('Missing voice evidence cannot be fabricated')
        if len(self.repetition_blocks)!=16 or type(self.restoration_verified)is not bool:raise ValueError('Exact blocks and typed window restoration required')
        old.exact_integer(self.station_drops,'station drops')
        if self.source_failure_metadata.get('disqualified')is not None and type(self.source_failure_metadata['disqualified'])is not bool:
            raise ValueError('Disqualified must be bool or unknown')
        c=self.compound_recipe_controls
        if not isinstance(c,dict)or any(c.get(k)is not False for k in ('effective_control_verified','feedback_adaptive_control_verified','GI_LDPC_STBC_setter_verified')):
            raise ValueError('Explicit unqualified compound provenance required')
        branch=c.get('source_branch');pairs=c.get('declared_endpoint_pairs');literal=c.get('literal_branch_pairs')
        old.exact_integer(self.force_tx_status,'force_tx_status',0,1)
        if (not isinstance(branch,dict)or branch!={'field':'force_tx_status','value':self.force_tx_status}
                or type(branch['value'])is not int or not isinstance(literal,dict)):
            raise ValueError('Exact selected branch identity required')
        both=[literal.get('then_pair'),literal.get('else_pair')]
        if (not all(isinstance(p,list)and len(p)==2 and all(type(v)is int for v in p)for p in both)
                or tuple(both[0]+both[1])not in ((3,32,3,64),(3,16,3,64),(3,64,3,64))):
            raise ValueError('Exact supported declared branch pairs required')
        selected=both[0]if self.force_tx_status else both[1]
        if not isinstance(pairs,dict)or set(pairs)!={'ap','cpe'}or any(p!=selected or any(type(v)is not int for v in p)for p in pairs.values()):
            raise ValueError('Both endpoint pairs must match the actual static branch')

    @property
    def policy_key(self):
        endpoints=json.loads(super().policy_key)
        for endpoint,name in zip(endpoints,('ap','cpe')):
            endpoint.update(self.hmac_source_controls)
            endpoint.update(workload_identity=REGIME,voip_probe_tos=self.voip_probe_tos)
            endpoint['recipe_declared_htt_max_amsdu_ampdu']=self.compound_recipe_controls['declared_endpoint_pairs'][name]
        return json.dumps(endpoints,sort_keys=True,separators=(',',':'))


def _control_coordinates(item,compound):
    knobs=item['candidate_knobs'];result={}
    for end in ('ap','cpe'):
        for key in sorted(_ENDPOINT_FIELDS):result[f'/candidate_knobs/{end}_state/{key}']=deepcopy(knobs[end+'_state'][key])
        result[f'/recipe_declared_htt_max_amsdu_ampdu/{end}']=compound['declared_endpoint_pairs'][end]
    for key in ('airtime_flags','tx_aggr_factor','fq_limit','fq_flows','force_tx_status','short_retry_limit','long_retry_limit'):
        result['/candidate_knobs/'+key]=knobs[key]
    return result


def convert_incremental_hmac_payload(number,payload,ref,recipe,text,tsv_text):
    if type(number)is not int or number not in CONTEXTS:raise ValueError('No future payload access outside fixed incremental cutoff')
    compound=recipe_incremental_controls(text,payload)
    def measurement(**values):return IncrementalHmacMeasurement(**values,compound_recipe_controls=compound[values['iteration']])
    records,blocks,audit=live._convert_available_hmac_payload(number,payload,ref,recipe,text,tsv_text,
        contexts=CONTEXTS,max_round=169,measurement_type=measurement)
    items=payload['iterations'];coordinates=[_control_coordinates(i,compound[i['commit']])for i in items]
    deltas=[dict(coordinate=key,control=coordinates[0][key],target=coordinates[1][key],
                 derived_alias_of='airtime_flags'if key.endswith('/tx_aggr_factor')else None)
            for key in coordinates[0]if coordinates[0][key]!=coordinates[1][key]]
    for row,item in zip(records,items):
        row.update(reported_batch=payload.get('batch'),reported_batch_id=payload.get('batch_id'),
            source_reported_experiment_ref=item.get('experiment_ref'),source_recipe_filename=Path(recipe['path']).name,
            source_candidate_metadata={k:deepcopy(item['candidate_knobs'].get(k))for k in sorted(_METADATA)},
            literal_control_coordinates=coordinates[items.index(item)],compound_treatment_effect_qualified=False)
        row['certified_wds_evidence']['compound_recipe_controls']=deepcopy(row['compound_recipe_controls'])
    for block in blocks:block['compound_recipe_controls']=deepcopy(compound[block['treatment_id']])
    audit.update(compound_recipe_controls=compound,literal_control_deltas=deltas,
        reported_experiment_refs=[i.get('experiment_ref')for i in items],
        reported_candidate_labels=[{k:deepcopy(i['candidate_knobs'].get(k))for k in sorted(_METADATA)}for i in items],
        syntactic_changed_coordinate_count=len(deltas),physical_or_causal_isolation_qualified=False,
        titles_and_descriptions_are_not_control_coordinates=True,recipe_executed=False)
    return records,blocks,audit


def _new(manifest_path,expected_manifest_sha256):
    manifest,refs,contents,prefixes,binding=_inputs(manifest_path,expected_manifest_sha256)
    records=[];blocks=[];sources=[];audits=[];rejected=[]
    for item in manifest['available']:
        number=int(item['round_id'][1:]);ref=refs[item['receipt']];recipe=refs[item['recipe_paths'][0]];tsv=refs[item['tsv_path']]
        try:
            new,crossed,audit=convert_incremental_hmac_payload(number,full._json(contents[item['receipt']]),ref,recipe,
                contents[item['recipe_paths'][0]].decode('utf-8'),contents[item['tsv_path']].decode('utf-8'))
        except (ValueError,TypeError,KeyError,IndexError,AttributeError,OverflowError,SyntaxError)as error:
            rejected.append(dict(round_id=item['round_id'],status='REJECTED_UNSUPPORTED_OR_MALFORMED_SAVED_PACKAGE',
                error_type=type(error).__name__,reason=str(error),receipt=ref,recipe=recipe,tsv=tsv));continue
        records.extend(new);blocks.extend(crossed);audits.append(audit)
        sources.append({**ref,'round_id':item['round_id'],'source_recipe':recipe,'source_tsv':tsv})
    return records,blocks,sources,audits,rejected,prefixes,binding


def load_incremental_hmac_dataset(*,manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    new,blocks,refs,audits,rejected,prefixes,binding=_new(manifest_path,expected_manifest_sha256)
    prior=full._json(prefixes['records'])
    return dict(schema_version=21,evidence='SEALED_R146_PREFIX_PLUS_AUTHENTICATED_SAVED_R147_R169',
        records=deepcopy(prior['records'])+new,source_refs=deepcopy(prior['source_refs'])+refs,
        input_manifest=binding,prefix_bindings=deepcopy(PREFIX),new_round_audits=audits,rejected_rounds=rejected,
        available_at_cutoff=list(CONTEXTS),historical_missing_rounds=[110,111,112,113],
        missing_at_cutoff=[],physical_acceptance=False,automatic_execution_allowed=False)


def load_incremental_hmac_blocks(*,manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    _,new,refs,audits,rejected,prefixes,binding=_new(manifest_path,expected_manifest_sha256)
    prior=full._json(prefixes['blocks'])
    return dict(crossed=deepcopy(prior['crossed'])+new,sequential=deepcopy(prior['sequential']),
        source_refs=deepcopy(prior['source_refs'])+refs,input_manifest=binding,prefix_bindings=deepcopy(PREFIX),
        new_round_audits=audits,rejected_rounds=rejected,available_at_cutoff=list(CONTEXTS),
        missing_at_cutoff=[],historical_missing_rounds=[110,111,112,113],
        physical_acceptance=False,automatic_execution_allowed=False)


def _utility(control,target):
    a=Fraction(str(control));b=Fraction(str(target))
    if a<=0 or b<0:raise ValueError('Nonnegative saved GP and positive control required')
    drop=(a-b)/a*100
    return dict(observed_total_goodput_drop_pct=float(drop),exact_drop_pct=dict(numerator=drop.numerator,denominator=drop.denominator),
        observed_total_goodput_drop_strictly_below_2pct=drop<2,causal_noninferiority_established=False)


def audit_incremental_hmac_packages(*,manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    new,blocks,refs,audits,rejected,prefixes,binding=_new(manifest_path,expected_manifest_sha256)
    prior=full._json(prefixes['package_audit']);packages=deepcopy(prior['packages']);added=[]
    for audit in audits:
        own=[r for r in new if r['round_id']==audit['round_id']];control,target=own
        distance,coverage,slot,ack=CONTEXTS[int(audit['round_id'][1:])]
        utility=_utility(control['goodput_mbps'],target['goodput_mbps'])
        reasons=['NO_ACCEPTED_SAME_REGIME_STATISTICAL_RECEIPT','EFFECTIVE_HMAC_QUEUE_GATING_UNQUALIFIED',
            'VOIP_SERVICE_METRICS_AND_EFFECTIVE_TID_ATTRIBUTION_UNQUALIFIED','STATIC_SOURCE_PACKAGE_IS_NOT_CAUSAL_ISOLATION']
        if not utility['observed_total_goodput_drop_strictly_below_2pct']:reasons.append('OBSERVED_TOTAL_GOODPUT_DROP_NOT_BELOW_2PCT')
        added.append(dict(round_id=audit['round_id'],status='BLOCKED',reasons=reasons,
            control_policy_id=control['iteration'],policy_id=target['iteration'],
            control_policy_key=control['policy_key'],policy_key=target['policy_key'],
            distance_meters=distance,coverage_class=coverage,declared_slot_time_us=slot,declared_ack_timeout_us=ack,
            control_saved_health={k:control[k]for k in ('packet_loss_pct','station_drops','restoration_verified','source_failure_metadata')},
            target_saved_health={k:target[k]for k in ('packet_loss_pct','station_drops','restoration_verified','source_failure_metadata')},
            voip_evidence=target['voip_evidence'],hmac_source_controls=target['hmac_source_controls'],
            compound_recipe_controls=target['compound_recipe_controls'],literal_control_deltas=audit['literal_control_deltas'],
            reported_experiment_refs=audit['reported_experiment_refs'],utility=utility,
            physical_acceptance=False,automatic_execution_allowed=False))
    return dict(status='BLOCKED',regime=REGIME,packages=packages+added,new_packages=added,
        prior_package_count=len(packages),rejected_rounds=rejected,recommended_policy=None,
        input_manifest=binding,prefix_bindings=deepcopy(PREFIX),
        independently_accepted_same_regime_statistics=False,physical_acceptance=False,automatic_execution_allowed=False)


def select_incremental_hmac_policy(*,distance_meters,coverage_class,slot_time_us,ack_timeout_us,
        manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    context=(distance_meters,coverage_class,slot_time_us,ack_timeout_us)
    if any(type(v)is not int for v in context)or context not in set(CONTEXTS.values())|set(full.CONTEXTS.values()):
        raise ValueError('Four exact observed typed timing coordinates required; no imputation or interpolation')
    report=audit_incremental_hmac_packages(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)
    return dict(status='ABSTAIN',recommended_policy=None,regime=REGIME,
        distance_meters=distance_meters,coverage_class=coverage_class,slot_time_us=slot_time_us,ack_timeout_us=ack_timeout_us,
        recorded_packages=[p for p in report['packages']if (p['distance_meters'],p['coverage_class'],p['declared_slot_time_us'],p['declared_ack_timeout_us'])==context],
        reasons=['NO_QUALIFIED_PACKAGE_FOR_EXACT_HMAC_CONTEXT'],rejected_rounds=report['rejected_rounds'],
        physical_acceptance=False,automatic_execution_allowed=False)
