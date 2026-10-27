"""Versioned saved Stage13 corpus. No acquisition, recipe execution or promotion.

R147-R169 objects remain the exact accepted prefix. MultiRadio phase aggregates
have a separate schema; their labels never create packet/block observations.
"""
from copy import deepcopy
from dataclasses import dataclass,asdict
from fractions import Fraction
from pathlib import Path,PurePosixPath
import ast
import hashlib
import json
import math
import re
import numpy as np
from orchestration.autoresearch import fmx_full_hmac_dataset as full

ROOT=full.ROOT
BASE=ROOT/'orchestration/autoresearch/stage13_sync_20261025'
MANIFEST_SHA256='916904d8d37512dfdbb1eb84de3d911731c45cf61ab3cc826b2a3b9240f258a9'
PREFIX_PINS={
    'records':('3ebf4653a8f52e4716d6a425887851282fbdeaec7b943506fa995723ad5dca96',21430452),
    'blocks':('e93a8c45b42300ad45664ebb25509c1c04e63ae915c03d4a56b5413353efe1a2',14158474),
    'packages':('13863cbbe3b9bddf33d8eeb69bc4e3a1544bd7587c3defbb1e9209a2ca16c2ca',688538),
    'context_matrix':('df71d2299766c443bf8441762bbc94e94a63a2b15f9b8d14eae30dadaa236ef3',22962830)}
CONTEXT_KEYS=('traffic_regime','active_flow_count','bidirectional','distance_m','coverage_class','slot_time_us','ack_timeout_us')
LOWER_KEYS=('airtime_flags','fq_limit','force_tx_status','short_retry_limit','long_retry_limit','rts_threshold','ap_ack_clocking','tx_aggr_factor','fq_flows')
METADATA={'name','description','complexity_cost'}
METRIC_KEYS={'goodput_mbps':'goodput_rx_mbps','p50_ms':'p50_rtt_ms','p95_ms':'p95_rtt_ms','p99_ms':'p99_rtt_ms','jain_fairness':'jain_fairness'}
_TEMPLATE_SHAPES={'29ea60f6f7cd2887848bea6492550fcda780f91de231102aaa2881635eecb8ef',
                  'd70920dc3291a16f6fb4fd2f8e060b72a5097adf84105c54f1786358aa5174a8'}


class UnsupportedSetterAttribution(ValueError):
    """Keep measurements while refusing an unrecognized control identity."""


def binding(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix()if path.is_relative_to(ROOT)else str(path),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def finite(value,label,*,optional=False,nonnegative=True):
    if optional and value is None:return None
    if type(value)not in (int,float)or not math.isfinite(value)or(nonnegative and value<0):
        raise ValueError('Finite typed numeric '+label+' required')
    return value


def integer(value,label,minimum=0,maximum=10**12):
    if type(value)is not int or not minimum<=value<=maximum:raise ValueError('Exact bounded integer '+label+' required')
    return value


def _finite_tree(value):
    if isinstance(value,dict):
        for item in value.values():_finite_tree(item)
    elif isinstance(value,list):
        for item in value:_finite_tree(item)
    elif type(value)is float and not math.isfinite(value):raise ValueError('Nonfinite saved JSON value')


def _bound(path,pin):
    path=full._safe_path(path);raw=path.read_bytes()
    if type(pin.get('bytes'))is not int or len(raw)!=pin['bytes']or hashlib.sha256(raw).hexdigest()!=pin.get('sha256'):
        raise ValueError('Frozen source bytes/SHA256 differ')
    return raw


def authenticate(*,manifest_path,expected_manifest_sha256):
    """Authenticate all names then all160 members, four prefix files and metadata."""
    if expected_manifest_sha256!=MANIFEST_SHA256:raise ValueError('Exact Stage13 pre-implementation manifest pin required')
    path=full._safe_path(manifest_path);raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:raise ValueError('Stage13 manifest SHA256 mismatch')
    manifest=full._json(raw)
    if (manifest.get('planned_rounds')!=list(range(147,195))or len(manifest.get('members',[]))!=160
            or [r.get('round_id')for r in manifest.get('available',[])]!=[f'R{n}'for n in range(147,195)]):
        raise ValueError('Exact frozen48-round cutoff and160members required')
    refs={};paths={}
    for row in manifest['members']:
        logical=row.get('path');kind=row.get('kind')
        if (not isinstance(logical,str)or not logical or '\\'in logical or ':'in logical or PurePosixPath(logical).is_absolute()
                or '..'in PurePosixPath(logical).parts or logical in refs):raise ValueError('Unique safe logical member path required')
        if kind not in ('receipt','tsv','recipe','multiradio','recipe_dependency'):raise ValueError('Unknown frozen member kind')
        expected=BASE/'frozen_inputs'/kind/PurePosixPath(logical).name
        if row.get('frozen_path')!=expected.relative_to(ROOT).as_posix():raise ValueError('Exact frozen local member location required')
        integer(row.get('bytes'),'member bytes',1,30_000_000)
        if not isinstance(row.get('sha256'),str)or not re.fullmatch('[0-9a-f]{64}',row['sha256']):raise ValueError('Typed exact member digest required')
        if kind in ('receipt','tsv','recipe')and row.get('round_id')not in {f'R{n}'for n in range(147,195)}:
            raise ValueError('Future or mismatched member round')
        paths[logical]=full._safe_path(expected);refs[logical]=deepcopy(row)
    used=[]
    for item in manifest['available']:
        for key,kind in [('receipt','receipt'),('tsv','tsv'),('recipe','recipe')]:
            if item.get(key)not in refs or refs[item[key]]['kind']!=kind or refs[item[key]]['round_id']!=item['round_id']:
                raise ValueError('Complete unique per-round triple required')
            used.append(item[key])
    if len(set(used))!=144:raise ValueError('Duplicate bench triple member')
    prefix_paths={}
    for key,(sha,size)in PREFIX_PINS.items():
        row=manifest.get('prefix',{}).get(key,{})
        if (row.get('sha256'),row.get('bytes'))!=(sha,size):raise ValueError('Accepted R169 prefix pin is immutable')
        expected=BASE/'frozen_prefix'/PurePosixPath(row.get('path','')).name
        if row.get('frozen_path')!=expected.relative_to(ROOT).as_posix():raise ValueError('Exact prefix-copy path required')
        prefix_paths[key]=full._safe_path(expected)
    for key,name in [('multiradio_mapping','multiradio_source_mapping.json'),('statistical_family_recipe','statistical_family_recipe.json')]:
        if manifest[key].get('path')!=(BASE/name).relative_to(ROOT).as_posix():raise ValueError('Bounded metadata path required')
    contents={name:_bound(path,refs[name])for name,path in paths.items()}
    prefix={key:full._json(_bound(path,manifest['prefix'][key]))for key,path in prefix_paths.items()}
    mapping=full._json(_bound(BASE/'multiradio_source_mapping.json',manifest['multiradio_mapping']))
    family=full._json(_bound(BASE/'statistical_family_recipe.json',manifest['statistical_family_recipe']))
    for row in refs.values():row.update(original_path=row['path'],path=row['frozen_path'])
    return manifest,refs,contents,prefix,mapping,family,binding(path=full._safe_path(manifest_path))


def _context(number,payload,item):
    expected_regime='bidir_8flow_voip_hmac'if number<=188 else'unidir_ul_8flow_hammer'
    expected={k:payload.get(k)for k in CONTEXT_KEYS}
    if expected['traffic_regime']!=expected_regime or type(expected['bidirectional'])is not bool or expected['bidirectional']!=(number<=188):
        raise ValueError('Exact round-specific direction/regime required')
    for key in CONTEXT_KEYS[1:]:
        if key!='bidirectional':integer(expected[key],key,0 if key=='coverage_class'else 1,31 if key=='coverage_class'else 10**6)
    if expected['active_flow_count']!=8:raise ValueError('Saved eight-flow workload required')
    for obj in (item,item.get('candidate_knobs')):
        if not isinstance(obj,dict):raise ValueError('Explicit shared package context required')
        if any(type(obj.get(k))is not type(v)or obj[k]!=v for k,v in expected.items()):raise ValueError('Shared source context conflict')
        if number<=188 and obj.get('voip_probe_tos')not in ('0xb8','0xb8 (DSCP EF -> AC_VO Queue 0 TID 6)'):
            raise ValueError('Explicit saved voice-probe declaration required, not effective classification proof')
    return expected


def _strip_metadata(value):
    if isinstance(value,dict):return {k:_strip_metadata(v)for k,v in sorted(value.items())if k not in METADATA}
    if isinstance(value,list):return [_strip_metadata(v)for v in value]
    return value


def _recipe_audit(number,text,payload,dependency_texts):
    """Use the established literal endpoint/tuple comparator, never recipe import."""
    tree=ast.parse(text);is_hmac=number<=188
    packages=full.live._hmac_recipe_packages(text,payload,max_round=194)if is_hmac else full.live._literal_recipe_packages(text,payload)
    templates=[];ranges=[];verified_callers=False
    if is_hmac:
        appliers=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==f'apply_r{number}_hmac_state']
        if len(appliers)!=1:raise ValueError('Unique declared hMAC applier required')
        extras=[n for n in appliers[0].body if isinstance(n,ast.FunctionDef)and n.name=='_peer_extra']
        if len(extras)!=1:raise ValueError('Unique endpoint control template required')
        returns=[n for n in extras[0].body if isinstance(n,ast.Return)]
        if len(returns)!=1:raise ValueError('One endpoint template return required')
        template=full._template(returns[0].value);templates=[template];ranges=[[extras[0].lineno,extras[0].end_lineno]]
        shape=re.sub(r'echo "3 (16|32|64)" > '+re.escape(full.HTT_NODE),'echo "3 <DECLARED_HTT>" > '+full.HTT_NODE,template)
        if hashlib.sha256(shape.encode()).hexdigest()not in _TEMPLATE_SHAPES:
            raise UnsupportedSetterAttribution('Unknown endpoint setter template; candidate labels cannot supply missing attribution')
        callers=[]
        for node in appliers[0].body:
            if isinstance(node,ast.Assign)and isinstance(node.value,ast.Call):
                call=node.value
                if isinstance(call.func,ast.Name)and call.func.id=='rpc'and len(call.args)>1:
                    callers.append((ast.unparse(call.args[0]),ast.unparse(call.args[1])))
        verified_callers=sorted(callers)==[('b.ap','_r11_node_cmd(pair.ap_state) + _peer_extra(pair.ap_state)'),('b.client','_r11_node_cmd(pair.cpe_state) + _peer_extra(pair.cpe_state)')]
        if not verified_callers:raise ValueError('Separate exact AP/CPE template callers required')
    else:
        calls=[n for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='apply_r122_state']
        if not calls or not any(len(n.args)==9 for n in calls):raise ValueError('Literal delegated UL package caller required')
        if not all(any(f'apply_r{n}_state'in t for t in dependency_texts.values())for n in (26,122)):
            raise ValueError('Authenticated transitive UL control text required')
    outputs=[]
    for item,package in zip(payload['iterations'],packages):
        knobs=item['candidate_knobs'];controls={k:deepcopy(knobs.get(k))for k in LOWER_KEYS}
        for key in LOWER_KEYS:
            value=controls[key]
            if value is None:continue
            if key=='ap_ack_clocking':
                if type(value)is not bool:raise ValueError('Typed ACK clocking declaration required')
            elif key=='rts_threshold'and value=='off':pass
            else:integer(value,key,0,10**7)
            if key in item and(type(item[key])is not type(value)or item[key]!=value):raise ValueError('Lower control declaration conflict')
        endpoint_pairs=None;readback_match=None;rts_from_branch=None
        if is_hmac:
            pattern=r'if \[ "\{force_tx_status\}" = "1" \]; then\s+echo "(\d+) (\d+)" > '+re.escape(full.HTT_NODE)+r'[^\n]*\s+else\s+echo "(\d+) (\d+)" > '+re.escape(full.HTT_NODE)+r'[^\n]*\s+fi'
            matches=list(re.finditer(pattern,templates[0]))
            if len(matches)!=1:raise ValueError('Explicit static HTT branch required')
            values=tuple(map(int,matches[0].groups()))
            if values not in ((3,32,3,64),(3,16,3,64),(3,64,3,64)):raise ValueError('Unsupported literal HTT branch')
            force=integer(controls['force_tx_status'],'HTT branch',0,1);pair=list(values[:2]if force else values[2:])
            endpoint_pairs={end:list(pair)for end in ('ap','cpe')};readback_match={}
            for end in ('ap','cpe'):
                saved=item.get('readback',{}).get(end+'_readback')
                if saved is not None and not isinstance(saved,str):raise ValueError('Saved endpoint readback text or unknown required')
                found=[[int(a),int(b)]for a,b in re.findall(r'^[ \t]*(\d+)[ \t]+(\d+)[ \t]*\r?$',saved or'',re.M)]
                readback_match[end]=len(found)==1 and found[0]==pair
            if 'iw phy phy0 set rts'in templates[0]:
                if 'then iw phy phy0 set rts 256 'not in templates[0]or'else iw phy phy0 set rts off 'not in templates[0]:raise ValueError('Unsupported conditional RTS grammar')
                rts_from_branch=256 if force else'off'
        identity=dict(endpoint_controls={end:_strip_metadata(knobs[end+'_state'])for end in ('ap','cpe')},
            lower_controls=controls,recipe_declared_endpoint_htt_pairs=endpoint_pairs,recipe_declared_rts_threshold=rts_from_branch,
            workload={k:payload[k]for k in CONTEXT_KEYS})
        _finite_tree(identity)
        for state in identity['endpoint_controls'].values():
            for key,value in state.items():
                if key in ('dscp_micro_vo_steering',):integer(value,key,0,1)
                elif key not in CONTEXT_KEYS:integer(value,'endpoint '+key,0,2**32-1)
        outputs.append(dict(stage13_policy_key=json.dumps(identity,sort_keys=True,separators=(',',':'),allow_nan=False),
            actual_declared_controls=identity,recipe_literal_package=package,source_lines=ranges,
            endpoint_template_sha256=[hashlib.sha256(t.encode()).hexdigest()for t in templates],
            control_attribution='LITERAL_DECLARATIONS_AND_DELEGATION_ONLY',htt_saved_text_matches=readback_match,
            delegated_sources=list(dependency_texts)if not is_hmac else[],
            effective_control_verified=False,causal_isolation_verified=False,recipe_imported_or_executed=False))
    return outputs


def _array(value,label):
    if not isinstance(value,list):raise ValueError('Saved sample array required: '+label)
    return [finite(v,label)for v in value]


def _pool_audit(pool,reported):
    result={}
    for probability,key in ((.5,'p50_rtt_ms'),(.95,'p95_rtt_ms'),(.99,'p99_rtt_ms')):
        value=finite(reported.get(key),key);computed=float(np.quantile(pool,probability,method='linear'))if pool else None
        result[key]=dict(saved=value,recomputed=computed,delta=None if computed is None else computed-value)
        if computed is not None and not math.isclose(computed,value,abs_tol=1e-9,rel_tol=1e-12):raise ValueError('Saved RTT quantile conflicts with raw pool')
    return result


def parse_bench_round(number,payload,ref,recipe,text,tsv_text,dependency_texts):
    if type(number)is not int or not 147<=number<=194:raise ValueError('Fixed Stage13 bench cutoff only')
    if full.old._physical_round_number(payload,max_round=194)!=number:raise ValueError('Round source identity conflict')
    _finite_tree(payload)
    items=payload.get('iterations')
    if not isinstance(items,list)or len(items)!=2 or len({i.get('commit')for i in items})!=2:raise ValueError('Two uniquely identified source arms required')
    full.live._audit_tsv134(tsv_text,payload)
    try:recipes=_recipe_audit(number,text,payload,dependency_texts)
    except UnsupportedSetterAttribution as error:
        recipes=[dict(stage13_policy_key=None,control_attribution='UNSUPPORTED_SETTER_ATTRIBUTION',reason=str(error),
            raw_candidate_controls=_strip_metadata(item['candidate_knobs']),effective_control_verified=False,
            causal_isolation_verified=False,recipe_imported_or_executed=False)for item in items]
    records=[];crossed=[];ids=[i['commit']for i in items];contexts=[];ids_expected=set(range(16))if number<=188 else set(range(1,17))
    for position,(item,control_audit)in enumerate(zip(items,recipes)):
        context=_context(number,payload,item);contexts.append(context);rawblocks=item.get('repetition_blocks')
        if not isinstance(rawblocks,list)or len(rawblocks)!=16:raise ValueError('Exactly16 genuine saved blocks per arm required')
        if {b.get('block_index')for b in rawblocks}!=ids_expected:raise ValueError('Exact schema-specific source block IDs required')
        own=[];pool=[]
        for source_position,raw in enumerate(rawblocks):
            index=integer(raw.get('block_index'),'source block index',0,16)
            if number<=188:
                step=integer(raw.get('crossover_step'),'source crossover step',0,1);samples=_array(raw.get('rtts_ms'),'block RTT')
                step_metadata={}
            else:
                if 'crossover_step'in raw:raise ValueError('Mixed binary/one-based source step schema')
                source_step=integer(raw.get('step_in_block'),'source step_in_block',1,2);step=source_step-1
                samples=_array(raw.get('raw_rtts_ms'),'UL source raw RTT')
                if raw.get('rtts_ms')not in (None,[])and raw['rtts_ms']!=samples:raise ValueError('Conflicting raw sample aliases')
                step_metadata=dict(source_step_in_block=source_step,source_step_field='step_in_block',crossover_step_mapping='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE',source_block_index_origin=1,schedule_lookup_index=index-1)
            sent=integer(raw.get('pings_sent'),'pings sent',1,10000);received=integer(raw.get('pings_rcvd'),'pings received',0,sent)
            if len(samples)!=received:raise ValueError('Received count and retained RTT count differ')
            dl=finite(raw.get('dl_goodput_mbps'),'block DL');ul=finite(raw.get('ul_goodput_mbps'),'block UL');total=finite(raw.get('total_goodput_mbps'),'block total')
            if dl+ul!=total:raise ValueError('Saved directional total conflict')
            jain=finite(raw.get('bidir_jain_fairness'),'block Jain')
            if not 0<=jain<=1:raise ValueError('Jain outside numeric domain')
            if number>=189 and(dl!=0 or ul!=total):raise ValueError('Unidirectional active/inactive alias not identified')
            counters={k:integer(raw[k],k)if k in raw else None for k in ('mac_tx_packets_delta','mac_tx_retries_delta')}
            retry=None if not counters['mac_tx_packets_delta']or counters['mac_tx_retries_delta']is None else counters['mac_tx_retries_delta']/counters['mac_tx_packets_delta']
            observation=raw.get('observation')
            if observation is not None and not isinstance(observation,dict):raise ValueError('Block observation object or absent required')
            health={k:None if observation is None else observation.get(k)for k in ('restoration_ok','station_reset_count')}
            if health['restoration_ok']is not None and type(health['restoration_ok'])is not bool:raise ValueError('Typed reported restoration or unknown required')
            if health['station_reset_count']is not None:integer(health['station_reset_count'],'station reset count')
            tid=None if number>=189 else{k:integer(raw[k],k)if k in raw else None for k in ('tid0_be_tx_pkts_delta','tid0_be_drops_delta','tid6_vo_tx_pkts_delta','tid6_vo_drops_delta')}
            q=_pool_audit(samples,raw)
            row=dict(round_id=f'R{number}',block_index=index,crossover_step=step,treatment_id=item['commit'],
                source_position=f'/iterations/{position}/repetition_blocks/{source_position}',
                observation=dict(goodput_rx_mbps=total,p50_ms=raw['p50_rtt_ms'],p95_ms=raw['p95_rtt_ms'],p99_ms=raw['p99_rtt_ms'],
                    jain_fairness=jain,packet_loss_pct=100*(sent-received)/sent),
                dl_goodput_mbps=dl,ul_goodput_mbps=ul,total_bidir_goodput_mbps=total,rtts_ms=samples,pings_sent=sent,pings_rcvd=received,
                **counters,mac_retry_rate=raw.get('mac_retry_rate'),mac_retry_rate_from_counters=retry,
                counter_interface='phy0-ap0.sta1',counter_interface_authority='RECIPE_TEXT_DECLARATION_NOT_INDEPENDENT_HARDWARE_PROOF',
                workload_regime=context['traffic_regime'],active_flow_count=8,bidirectional=context['bidirectional'],
                tid_counters=tid,reported_block_health=health,hmac_source_controls={k:item.get(k)for k in ('tx_aggr_factor','fq_flows')},
                source_missingness=dict(block_observation=observation is None,TID=tid is None,fq_flows='fq_flows'not in item),
                quantile_audit=q,stage13_policy_key=control_audit['stage13_policy_key'],**step_metadata)
            own.append(row);pool.extend(samples)
        summary=item.get('observation')
        if not isinstance(summary,dict):raise ValueError('Recorded window observation required')
        if pool!=_array(item.get('raw_rtts_ms'),'window RTT'):raise ValueError('Retained chronological block/window RTT pools differ')
        if integer(item.get('rtt_sample_count'),'window RTT count')!=len(pool):raise ValueError('Window sample count conflict')
        quantiles=_pool_audit(pool,summary)
        sent=sum(b['pings_sent']for b in own);received=sum(b['pings_rcvd']for b in own);loss=finite(summary.get('packet_loss_pct'),'reported loss')
        if loss!=100*(sent-received)/sent:raise ValueError('Saved window loss conflicts with retained counters')
        if type(summary.get('restoration_verified'))is not bool:raise ValueError('Typed reported window restoration required')
        drops=integer(summary.get('station_drops'),'window station drops')
        evaluation=item.get('evaluation')
        if not isinstance(evaluation,dict):raise ValueError('Saved optimizer evaluation object required')
        if evaluation.get('disqualified')is not None and type(evaluation['disqualified'])is not bool:raise ValueError('Typed disqualification or unknown required')
        record=dict(round_id=f'R{number}',iteration=item['commit'],source_position=f'/iterations/{position}',window_kind='primary',
            workload_regime=context['traffic_regime'],active_flow_count=8,bidirectional=context['bidirectional'],
            distance_meters=context['distance_m'],coverage_class=context['coverage_class'],slot_time_us=context['slot_time_us'],ack_timeout_us=context['ack_timeout_us'],
            **{name:finite(summary.get(key),name)for name,key in METRIC_KEYS.items()},
            dl_goodput_mbps=finite(item.get('dl_goodput_mbps'),'window DL'),ul_goodput_mbps=finite(item.get('ul_goodput_mbps'),'window UL'),
            packet_loss_pct=loss,rtts_ms=pool,restoration_verified=summary['restoration_verified'],station_drops=drops,
            source_failure_metadata=dict(disqualified=evaluation.get('disqualified'),reported_optimizer_decision=evaluation.get('decision'),
                optimizer_reason=evaluation.get('reason'),acquisition_failure_inferred_from_optimizer_label=False),
            policy_key=control_audit['stage13_policy_key'],stage13_policy_key=control_audit['stage13_policy_key'],
            source_candidate_metadata={k:deepcopy(item['candidate_knobs'].get(k))for k in sorted(METADATA)},
            recipe_control_audit=control_audit,voip_evidence=dict(probe_tos='0xb8'if number<=188 else None,
                applicable=number<=188,latency_ms=None,jitter_ms=None,packet_loss_pct=None,mos=None,effective_AC_mapping_verified=False),
            hmac_source_controls={k:item.get(k)for k in ('tx_aggr_factor','fq_flows')},
            source_receipt=ref,source_recipe=recipe,quantile_audit=quantiles,repetition_blocks=deepcopy(own),
            physical_distance_verified=False,effective_timing_independently_verified=False)
        if number>=189 and(record['dl_goodput_mbps']!=0 or record['ul_goodput_mbps']!=record['goodput_mbps']):raise ValueError('Window directional alias conflict')
        record['block_mean_consistency']={name:dict(reported=record[name],computed=sum(Fraction(str(b['observation'][key]))for b in own)/16==Fraction(str(record[name])))
            for name,key in [('goodput_mbps','goodput_rx_mbps'),('jain_fairness','jain_fairness')]}
        records.append(record);crossed.extend(own)
    schedule=payload.get('crossover_schedule')
    if not isinstance(schedule,list)or len(schedule)!=16:raise ValueError('Explicit saved source schedule required')
    for index in sorted(ids_expected):
        group=sorted([r for r in crossed if r['block_index']==index],key=lambda r:r['crossover_step'])
        if len(group)!=2 or [r['crossover_step']for r in group]!=[0,1]:raise ValueError('One control and target per genuine block/step required')
        if ['AB'[ids.index(r['treatment_id'])]for r in group]!=schedule[index if number<=188 else index-1]:raise ValueError('Source schedule/coordinate conflict')
    return records,crossed


def _pointer(value,pointer):
    if not isinstance(pointer,str)or not pointer.startswith('/'):raise ValueError('Explicit bounded JSON pointer required')
    for part in pointer[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        value=value[integer(int(part),'array index')]if isinstance(value,list)and part.isdigit()else value[part]
    return value


@dataclass(frozen=True)
class MultiRadioAggregatePackage:
    round_id:str
    source:dict
    source_pointer:str
    phases:dict
    declared_controls:dict
    saved_summary:dict
    source_metadata:dict
    raw_rtts_ms:None=None
    paired_unit_ids:None=None
    inference_status:str='UNAVAILABLE_PHASE_AGGREGATES_NOT_RAW_INDEPENDENT_TRIALS'
    physical_acceptance:bool=False

    def __post_init__(self):
        if not isinstance(self.round_id,str)or not self.round_id or set(self.phases)!={'A1','B1','A2','B2'}:
            raise ValueError('Explicit MultiRadio identity and four phase aggregates required')
        if any(not isinstance(p,dict)for p in self.phases.values()):raise ValueError('Phase aggregates must remain objects')
        for phase in self.phases.values():
            for key,value in phase.items():
                if value is None:continue
                if key=='ubnt_poll_stats'and isinstance(value,str):continue
                if isinstance(value,list):
                    for v in value:finite(v,'phase '+key,nonnegative=False)
                else:finite(value,'phase '+key,nonnegative=False)
        _finite_tree(asdict(self))


def _multiradio(refs,contents,mapping):
    if len(mapping.get('rounds',[]))!=110 or len({r.get('round_id')for r in mapping['rounds']})!=110:
        raise ValueError('Exact110 mapped MultiRadio source IDs required')
    files={row['path']:row for row in mapping['files']}
    if len(files)!=13 or set(files)!={k for k,r in refs.items()if r['kind']=='multiradio'}:raise ValueError('Exact13-source mapping contract required')
    for name,pin in files.items():
        if any(refs[name][k]!=pin[k]for k in ('bytes','sha256')):raise ValueError('MultiRadio mapping/source pin conflict')
    decoded={name:full._json(contents[name])for name in files};packages=[]
    for row in mapping['rounds']:
        source=_pointer(decoded[row['path']],row['pointer']);_finite_tree(source)
        if source.get('round_id')!=row['round_id']:raise ValueError('MultiRadio pointer/source round identity conflict')
        phases=source.get('subphases')if isinstance(source.get('subphases'),dict)else{k:source.get(k)for k in ('A1','B1','A2','B2')}
        if set(phases)!={'A1','B1','A2','B2'}:raise ValueError('No inferred or repeated phase IDs')
        controls={k:deepcopy(v)for k,v in source.items()if k in ('knob','baseline_val','candidate_val','apply_cmd','revert_cmd','cmd_a','cmd_b')}
        summary=deepcopy(source.get('summary',{}))
        package=MultiRadioAggregatePackage(row['round_id'],deepcopy(refs[row['path']]),row['pointer'],deepcopy(phases),controls,summary,
            {k:deepcopy(v)for k,v in source.items()if k not in ('A1','B1','A2','B2','subphases','summary')})
        packages.append(asdict(package))
    return packages


def _build(*,manifest_path,expected_manifest_sha256):
    manifest,refs,contents,prefix,mapping,family,pin=authenticate(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)
    dependencies={name:contents[name].decode('utf-8')for name in manifest['supplementary_recipe_sources']}
    old_records=prefix['records']['records'];old_blocks=prefix['blocks'];old_refs=prefix['records']['source_refs']
    prior_refs={r.get('round_id'):r for r in old_refs};cohort=[];new=[];blocks=[];sources=[];overlap=[]
    for item in manifest['available']:
        number=int(item['round_id'][1:]);ref=refs[item['receipt']];recipe=refs[item['recipe']]
        parsed,observations=parse_bench_round(number,full._json(contents[item['receipt']]),ref,recipe,
            contents[item['recipe']].decode('utf-8'),contents[item['tsv']].decode('utf-8'),dependencies)
        if number<=169:
            previous=prior_refs[item['round_id']]
            for before,after in [(previous,ref),(previous['source_recipe'],recipe),(previous['source_tsv'],refs[item['tsv']])]:
                if any(before[k]!=after[k]for k in ('bytes','sha256')):raise ValueError('Frozen overlap differs from accepted R169 source')
            overlap.append(item['round_id'])
        else:
            new.extend(parsed);blocks.extend(observations);sources.append({**ref,'round_id':item['round_id'],'source_recipe':recipe,'source_tsv':refs[item['tsv']]})
        cohort.extend(parsed)
    return manifest,prefix,cohort,new,blocks,sources,overlap,_multiradio(refs,contents,mapping),pin,family


def load_stage13_sync_dataset(**options):
    manifest,prefix,cohort,new,blocks,sources,overlap,multi,pin,family=_build(**options)
    return dict(schema_version='STAGE13_SYNC_V1',records=deepcopy(prefix['records']['records'])+new,
        source_refs=deepcopy(prefix['records']['source_refs'])+sources,bench_cohort=cohort,multiradio_packages=multi,
        unsupported_packages=[dict(round_id=r['round_id'],iteration=r['iteration'],source_recipe=r['source_recipe'],reason=r['recipe_control_audit']['reason'])
            for r in cohort if r['recipe_control_audit']['control_attribution']=='UNSUPPORTED_SETTER_ATTRIBUTION'],
        overlap_rounds_verified=overlap,input_manifest=pin,family_recipe=manifest['statistical_family_recipe'],
        prefix_bindings=manifest['prefix'],missing_historical_rounds=[110,111,112,113],
        physical_acceptance=False,automatic_execution_allowed=False)


def load_stage13_sync_blocks(**options):
    _,prefix,cohort,new,blocks,sources,overlap,multi,pin,family=_build(**options)
    return dict(crossed=deepcopy(prefix['blocks']['crossed'])+blocks,sequential=deepcopy(prefix['blocks']['sequential']),
        source_refs=deepcopy(prefix['blocks']['source_refs'])+sources,bench_cohort_crossed=[b for r in cohort for b in r['repetition_blocks']],
        overlap_rounds_verified=overlap,input_manifest=pin,physical_acceptance=False,automatic_execution_allowed=False)


def load_stage13_multiradio_packages(**options):
    manifest,refs,contents,prefix,mapping,family,pin=authenticate(**options)
    return dict(schema_version='STAGE13_MULTIRADIO_AGGREGATES_V1',packages=_multiradio(refs,contents,mapping),input_manifest=pin,
        raw_packet_or_trial_samples_available=False,shared_hardware_independence_verified=False,physical_acceptance=False,automatic_execution_allowed=False)
