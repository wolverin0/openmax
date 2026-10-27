"""Pure saved-source frontier for the pinned ORIGINAL248 controls, not first248."""
from __future__ import annotations

from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/'artifacts/autoresearch/waves_abcd_20261024/inputs/firmware_knob_candidates.json'
ORIGINAL_SHA='b2810269d0a7afb8715ebbeb901e169a2fd0b5cf61c3d667f91d7aae15585c07'
CURRENT=ROOT/'orchestration/autoresearch/firmware_knob_candidates.json'
RECORDS=ROOT/'artifacts/autoresearch/waves_bq_to_cf_20261024/normalized_r1_to_r134_measurements_20261024.json'
RECORDS_SHA='ded87ff26e14138236b156919bb809805b9398bfe6f501e2dd74e6809b70bf7b'
MISSING_ROUNDS=(110,111,112,113)
AVAILABLE_ROUNDS=set(range(1,135))-set(MISSING_ROUNDS)
OUTPUT=ROOT/'artifacts/autoresearch/knob_248_untested_matrix_20261024.json'

# Explicit identity contracts. No substring/fuzzy-name joins or WMI/ioctl aliases.
MAPPINGS={
    'aql_txq_limit':('AC low high','phy*/aql_txq_limit','aql_by_ac'),
    'aql_threshold':('threshold','phy*/aql_threshold','aql_threshold_us'),
    'fq_quantum':('fq_quantum_bytes','phy*/aqm fq_quantum','fq_quantum_bytes'),
    'ct_special_7':('7','phy*/ath10k/ct_special; base0u64 high32ID/low32value','rc_per_thresh'),
    'ct_special_10':('10','phy*/ath10k/ct_special; base0u64 high32ID/low32value','ct_baseband_rifs'),
    'ct_special_12':('12','phy*/ath10k/ct_special; base0u64 high32ID/low32value','ct_pshack'),
    'htt_aggr_size':('htt_max_amsdu_ampdu','phy*/ath10k/htt_max_amsdu_ampdu textAMSDU AMPDU','htt_pair'),
    'rts_threshold':('rts_threshold_bytes','supported iw RTS API; no rawWMI injector','rts_threshold'),
    'coverage_class':('coverage_class','supported iw coverage only, no directMMIO','coverage_class'),
}


def binding(path):
    path=Path(path).resolve();raw=path.read_bytes()
    return dict(path=path.relative_to(ROOT).as_posix(),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def read_pinned(path,expected):
    raw=Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Pinned source bytes differ: '+str(path))
    return json.loads(raw)


def original_catalog():
    catalog=read_pinned(ORIGINAL,ORIGINAL_SHA)
    if len(catalog['knobs'])!=248 or len(catalog['sources'])!=33 or len({k['id']for k in catalog['knobs']})!=248:
        raise ValueError('Exact historical248unique identities/33sources required')
    if any(k['enabled']is not False for k in catalog['knobs']):raise ValueError('Historical informational disabled catalog required')
    return catalog


def round_number(ref):
    number=ref.get('round');rid=ref.get('round_id')
    if number is not None and(type(number)is not int or number not in AVAILABLE_ROUNDS):raise ValueError('Only explicit saved rounds1..134, not missing/future')
    if rid is not None:
        if not isinstance(rid,str)or not re.fullmatch(r'R[1-9]\d*',rid):raise ValueError('Invalid round ID')
        parsed=int(rid[1:])
        if parsed not in AVAILABLE_ROUNDS or number is not None and number!=parsed:raise ValueError('Conflicting/missing/future round identity')
        number=parsed
    if number is None:raise ValueError('Missing source identity')
    return number


def frozen_receipts(refs):
    """Preflight every explicit identity/path before opening any source copy."""
    selected=[];seen=set()
    for ref in refs:
        number=round_number(ref);logical=ref.get('copy',ref.get('path'))
        if not isinstance(logical,str)or not logical or '://'in logical:raise ValueError('Explicit frozen local source required')
        path=Path(logical)
        if path.is_absolute()or'..'in path.parts or '/inputs/'not in path.as_posix()or path.suffix!='.json':
            raise ValueError('Only retained frozen input JSON copies, never original/live pointers')
        actual=(ROOT/path).resolve()
        if not actual.is_relative_to((ROOT/'artifacts/autoresearch').resolve())or number in seen:
            raise ValueError('Duplicate or outside-scope source')
        if not re.fullmatch('[0-9a-f]{64}',ref.get('sha256','')):raise ValueError('Source SHA required')
        seen.add(number);selected.append((number,actual,ref))
    if seen!=AVAILABLE_ROUNDS:raise ValueError('Exactly130available round receipts;110..113 remain absent')
    result={};pins={}
    for number,path,ref in selected:
        pin=binding(path)
        if pin['sha256']!=ref['sha256']or'bytes'in ref and pin['bytes']!=ref['bytes']:raise ValueError('Frozen receipt hash/size mismatch')
        # R36 has an archived nonstandard evaluation Infinity. It is not a knob
        # value and is not exported; reject nonfinite mapped coordinates below.
        result[number]=json.loads(path.read_text(encoding='utf-8'));pins[number]=pin
    return result,pins


def pointer_value(value,pointer):
    if not isinstance(pointer,str)or not pointer.startswith('/'):raise ValueError('Explicit source JSON pointer required')
    current=value
    for token in pointer.split('/')[1:]:
        token=token.replace('~1','/').replace('~0','~')
        current=current[int(token)]if isinstance(current,list)else current[token]
    return current


def typed_value(value):
    if value is None or isinstance(value,str):return value
    if type(value)in(int,float)and math.isfinite(value):return value
    if isinstance(value,(list,tuple)):return [typed_value(v)for v in value]
    raise ValueError('No bool/nonfinite/object substitution for numeric control')


def source_coordinate(arm,endpoint,key):
    """Explicit old flat, endpoint-prefixed and endpoint-state schema adapters."""
    knobs=arm.get('candidate_knobs')
    if not isinstance(knobs,dict):return None
    if isinstance(knobs.get(endpoint+'_state'),dict):
        obj=knobs[endpoint+'_state'];base='/candidate_knobs/'+endpoint+'_state';prefix=''
    elif any(name.startswith(endpoint+'_')for name in knobs):
        obj=knobs;base='/candidate_knobs';prefix=endpoint+'_'
    else:obj=knobs;base='/candidate_knobs';prefix=''
    def get(name):
        k=prefix+name
        if k not in obj or obj[k]is None:return None
        value=typed_value(obj[k])
        if key!='rts_threshold'and type(value)not in(int,float):raise ValueError('Explicit numeric coordinate required')
        return value,base+'/'+k
    if key=='coverage_class':
        for value,base in ((arm,''),(knobs,'/candidate_knobs')):
            if 'coverage_class'in value:
                v=value['coverage_class']
                if type(v)is not int or v<0:raise ValueError('Typed literal coverage class required')
                return dict(value=v,raw_coordinates=[dict(pointer=base+'/coverage_class',value=v)],transform='IDENTITY_SHARED_DECLARATION')
        return None
    if key=='aql_by_ac':
        names=[f'{ac}_{bound}_us'for ac in ('vo','vi','be','bk')for bound in ('low','high')]
        allac=[get(n)for n in names]
        if all(v is not None for v in allac):
            values=[v[0]for v in allac];out=[values[i:i+2]for i in range(0,8,2)]
            return dict(value=out,raw_coordinates=[dict(pointer=v[1],value=v[0])for v in allac],transform='EXPLICIT_VO_VI_BE_BK_PAIRS')
        pair=[get('aql_low_us'),get('aql_high_us')]
        if all(v is not None for v in pair):
            return dict(value=[[v[0]for v in pair]for _ in range(4)],raw_coordinates=[dict(pointer=v[1],value=v[0])for v in pair],transform='EXPLICIT_UNIFORM_FOUR_AC_PAIR')
        return None
    if key=='htt_pair':
        pair=[get('htt_max_amsdu'),get('htt_max_ampdu')]
        if not all(v is not None for v in pair):return None
        return dict(value=[v[0]for v in pair],raw_coordinates=[dict(pointer=v[1],value=v[0])for v in pair],transform='EXPLICIT_AMSDU_AMPDU_ORDERED_PAIR')
    candidates={'rc_per_thresh':('rc_per_thresh','ct_rc_per_thresh'),'rts_threshold':('rts_threshold','rts')}.get(key,(key,))
    matches=[get(k)for k in candidates if get(k)is not None]
    # Later RTS is an explicit shared source declaration, not an endpoint default.
    if not matches and key=='rts_threshold'and knobs.get('rts_threshold')is not None:
        matches=[(typed_value(knobs['rts_threshold']),'/candidate_knobs/rts_threshold')]
    if not matches:return None
    if len(matches)>1 and any(v[0]!=matches[0][0]for v in matches):raise ValueError('Conflicting explicit coordinate aliases')
    value=matches[0][0]
    if key=='rts_threshold':
        if value=='off':value=None
        elif isinstance(value,str)and value.isdigit():value=int(value)
        elif type(value)is not int:raise ValueError('Explicit RTS bytes/off required')
    return dict(value=value,raw_coordinates=[dict(pointer=p,value=v)for v,p in matches],transform='EXPLICIT_RTS_OFF_OR_BYTES'if key=='rts_threshold'else'EXPLICIT_KEY_ALIAS')


def normalized_coordinate(record,endpoint,key):
    if key=='coverage_class':return record.get('coverage_class')
    policy=record.get(endpoint+'_policy')
    if not isinstance(policy,dict):return None
    if key=='htt_pair':return [policy.get('htt_max_amsdu'),policy.get('htt_max_ampdu')]
    return policy.get(key)


def evidence_for_control(knob,records,receipts,pins):
    spec=MAPPINGS.get(knob['id'])
    if spec is None:return []
    selector,surface,key=spec
    if knob['interface']['selector']!=selector or knob['interface']['surface']!=surface:
        raise ValueError('Historical control ID cannot be reused for a different interface/selector')
    evidence=[]
    for index,record in enumerate(records):
        if record['window_kind']!='primary':continue
        number=round_number(dict(round_id=record['round_id']))
        arm=pointer_value(receipts[number],record['source_position'])
        if arm.get('commit')!=record['iteration']:raise ValueError('Arm commit/source pointer mismatch')
        endpoints=('shared',)if key=='coverage_class'else('ap','cpe')
        for endpoint in endpoints:
            if endpoint!='shared'and not isinstance(record.get(endpoint+'_policy'),dict):continue
            raw=source_coordinate(arm,'ap'if endpoint=='shared'else endpoint,key)
            if raw is None:continue # Unknown or unrecorded is never a baseline write.
            normalized=normalized_coordinate(record,'ap'if endpoint=='shared'else endpoint,key)
            if raw['value']!=normalized:raise ValueError('Raw and normalized control coordinate conflict: '+knob['id']+'/'+record['round_id'])
            if key=='htt_pair':
                normalized_coordinates=[dict(pointer=f'/records/{index}/{endpoint}_policy/{name}',value=value)
                    for name,value in zip(('htt_max_amsdu','htt_max_ampdu'),normalized)]
                normalized_transform='EXPLICIT_AMSDU_AMPDU_ORDERED_PAIR'
            else:
                path=f'/records/{index}/'+('coverage_class'if key=='coverage_class'else endpoint+'_policy/'+key)
                normalized_coordinates=[dict(pointer=path,value=normalized)]
                normalized_transform='IDENTITY'
            # Every exported locator must resolve to the saved document, including transformed pairs.
            for coordinate in raw['raw_coordinates']:
                if pointer_value(arm,coordinate['pointer'])!=coordinate['value']:raise ValueError('Raw coordinate pointer/value mismatch')
            for coordinate in normalized_coordinates:
                if pointer_value(dict(records=records),coordinate['pointer'])!=coordinate['value']:raise ValueError('Normalized coordinate pointer/value mismatch')
            evidence.append(dict(round_id=record['round_id'],arm_id=record['iteration'],endpoint=endpoint,value=raw['value'],
                source=pins[number],source_arm_pointer=record['source_position'],raw_coordinates=raw['raw_coordinates'],transform=raw['transform'],
                normalized_coordinates=normalized_coordinates,normalized_transform=normalized_transform,
                normalized_value=normalized,workload=record['workload_regime'],active_flow_count=record['active_flow_count'],
                declared_distance_meters=record.get('distance_meters'),declared_coverage_class=record.get('coverage_class'),
                window_kind='primary',saved_health={k:record.get(k)for k in ('packet_loss_pct','station_drops','restoration_verified')},
                source_failure_metadata=record.get('source_failure_metadata'),
                evidence_level='MEASURED_PACKAGE_WITH_DECLARED_COORDINATE_NOT_EFFECTIVE_BUILD_READBACK',
                exact_runtime_build_bound=False,effective_control_application_verified=False,isolated_effect_qualified=False))
    return evidence


def classify_control(knob,evidence):
    excluded=knob['classification']=='excluded'
    closed=any(s.startswith(('xc_','wa_','ltu_'))for s in knob['platform_scope'])
    unknown=knob['confidence']=='UNKNOWN'or'*'in knob['interface']['selector']
    variations=[]
    grouped=defaultdict(list)
    for row in evidence:grouped[row['round_id'],row['endpoint']].append(row)
    for (rid,endpoint),rows in grouped.items():
        values={json.dumps(r['value'],sort_keys=True)for r in rows}
        if len(values)>1:variations.append(dict(round_id=rid,endpoint=endpoint,distinct_declared_values=len(values)))
    if excluded:status='PROTECTED_OR_EXCLUDED_NO_TREATMENT_AUTHORITY'
    elif unknown:status='UNKNOWN_OR_UNRESOLVED_ORIGINAL_INTERFACE'
    elif closed:status='INAPPLICABLE_CLOSED_FIRMWARE_BUILD_TO_OPENWRT_CORPUS'
    elif evidence:status='TESTED_AS_DECLARED_PACKAGE'if variations else'PACKAGE_VALUE_RECORDED_NO_VARIED_TREATMENT'
    else:status='UNTESTED_EXACT_INTERFACE_IN_SAVED_CORPUS'
    if evidence and(excluded or closed or unknown):raise ValueError('Evidence may not override excluded, unknown or different-build identity')
    return dict(status=status,package_evidence_count=len(evidence),rounds=sorted({e['round_id']for e in evidence},key=lambda r:int(r[1:])),
        knowledge_status='ORIGINAL_INTERFACE_UNKNOWN_OR_UNRESOLVED'if unknown else'ORIGINAL_STATIC_INTERFACE_IDENTIFIED_RUNTIME_UNKNOWN',
        within_round_declared_variations=variations,isolated_effect_status='NO_QUALIFIED_ISOLATED_CAUSAL_EFFECT_ESTABLISHED',
        runtime_build_and_effect_status='UNKNOWN_NOT_BOUND_TO_EXACT_RUNNING_MODULE_OR_EFFECTIVE_STATE',
        treatment_authorized=False,approved_safe_range=None)


def build_frontier():
    original=original_catalog();current=json.loads(CURRENT.read_text(encoding='utf-8'))
    if len(current['knobs'])!=571 or len(current['sources'])!=42:raise ValueError('Current571/42 catalog required; not original248')
    by_id={k['id']:k for k in current['knobs']}
    if len(by_id)!=571:raise ValueError('Unique current IDs required')
    data=read_pinned(RECORDS,RECORDS_SHA);records=data['records']
    if len(records)!=360:raise ValueError('Pinned R1-R134 saved corpus360records')
    receipts,pins=frozen_receipts(data['source_refs'])
    if any(round_number(dict(round_id=r['round_id']))not in receipts for r in records):raise ValueError('Record missing authenticated receipt')
    sources={s['id']:s for s in original['sources']};rows=[]
    for knob in original['knobs']:
        evidence=evidence_for_control(knob,records,receipts,pins);new=by_id.get(knob['id'])
        relation='HISTORICAL_ID_NOT_PRESENT_IN_CURRENT'if new is None else'UNCHANGED_ORIGINAL_ROW'if knob==new else'REVISED_CURRENT_ROW_SAME_STABLE_ID'
        rows.append(dict(id=knob['id'],name=knob['name'],family=knob['family'],boundary=knob['boundary'],
            original_row_sha256=canonical_sha(knob),interface=knob['interface'],build_scope=knob['platform_scope'],
            original_classification=knob['classification'],original_confidence=knob['confidence'],
            original_source_refs=[dict(**ref,source=sources[ref['source_id']])for ref in knob['source_refs']],
            current_catalog_relation=relation,current_row_sha256=None if new is None else canonical_sha(new),
            classification=classify_control(knob,evidence),evidence=evidence,
            limitations=knob['limitations']+['Recorded full-package coordinates do not identify isolated control response or exact runtime firmware authority.'],
            automatic_execution_allowed=False))
    if len(rows)!=248 or len({r['id']for r in rows})!=248:raise ValueError('Exactly original248 stable identities required')
    return dict(schema_version=1,status='IMPLEMENTED_SOURCE_BOUND_FRONTIER_PENDING_INDEPENDENT_ACCEPTANCE',
        original_catalog=binding(ORIGINAL),original_catalog_identity_proof=[binding(ROOT/'artifacts/autoresearch/firmware_knob_audit_20261024/validation.json'),
            binding(ROOT/'artifacts/autoresearch/firmware_knob_audit_20261024/review_closed_catalog.md')],
        current_catalog=binding(CURRENT),measurement_corpus=binding(RECORDS),source_receipts=list(pins.values()),
        count=248,current_count=571,source_count=33,current_source_count=42,rows=rows,
        summary=dict(classifications=dict(Counter(r['classification']['status']for r in rows)),
            knowledge_statuses=dict(Counter(r['classification']['knowledge_status']for r in rows)),
            current_relations=dict(Counter(r['current_catalog_relation']for r in rows)),
            qualified_isolated_effects=0,available_rounds=130,primary_windows=sum(r['window_kind']=='primary'for r in records),
            auxiliary_windows_excluded=sum(r['window_kind']!='primary'for r in records)),
        missing_rounds=[dict(round_id=f'R{n}',status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',measurement_invented=False)for n in MISSING_ROUNDS],
        non_alias_rules=['No matching by name substring or arbitrary first248.','WMI retry/RTS/ANI descriptors are not the same namespace as raw short/long retry or host iw controls.',
            'Original codel_target/interval are Linux_qdisc policy metadata, not automatically the later mac80211 fq_target/interval interfaces.',
            'XC/WAairOS8.7.25 and LTU2.4.2 sources are not OpenWrt/CT installed-build matches.',
            'R116-R121UL2 log-law and R122-R134RTS/VO/TSQ treatments are cochanged full packages, not isolated causal laws.'],
        physical_acceptance=False,automatic_execution_allowed=False,actuation='none')


if __name__=='__main__':
    if OUTPUT.exists():raise FileExistsError(OUTPUT)
    result=build_frontier()
    with OUTPUT.open('x',encoding='utf-8',newline='\n')as stream:json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps(dict(count=result['count'],summary=result['summary'],output=binding(OUTPUT))))
