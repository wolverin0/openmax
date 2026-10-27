"""Authenticated, additive R135-R146 saved-package view; never acquisition.

R1-R139 is copied from its sealed normalized outputs without changing a field
or source reference. New recipes are parsed as AST/text only. Declared HTT pairs
and their saved textual readbacks are distinct from effective firmware authority.
"""
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import re
import stat

from orchestration.autoresearch import fmx_live_dataset as live

old=live.old
ROOT=live.ROOT
OUT=ROOT/'artifacts/autoresearch/waves_co_to_cr_20261024'
MANIFEST=OUT/'inputs_manifest.json'
MANIFEST_SHA256='327e7c5ea498500f5ebe13bc0909616ee0e6bbd5a465fb7f890d4c7444062e6d'
PRIOR_RECORDS=live.HMAC_ARTIFACTS/'normalized_r1_to_r139_available_hmac_measurements_20261024.json'
PRIOR_BLOCKS=live.HMAC_ARTIFACTS/'normalized_r16_to_r139_available_hmac_block_observations_20261024.json'
PRIOR_PINS={PRIOR_RECORDS.name:'9fc910ec6ffe216e31762d6e8a6c5471eb3776b1fb9a0913d75fff257ff51248',
            PRIOR_BLOCKS.name:'61ac495ed78c4a804d6af04338ee4bd071fbe878fc02cbd8970b44d485fcf2ca'}
CONTEXTS={**live.HMAC_CONTEXTS,140:(14000,31,102,123),141:(1000,2,15,36),
          142:(3000,6,27,48),143:(6000,13,48,69),144:(9000,20,69,90),
          145:(12000,26,87,108),146:(14000,31,102,123)}
REGIME='bidir_8flow_voip_hmac'
HTT_NODE='/sys/kernel/debug/ieee80211/phy0/ath10k/htt_max_amsdu_ampdu'


def _json(raw):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('Duplicate frozen JSON key')
            result[key]=value
        return result
    def reject(value):raise ValueError('Nonfinite frozen JSON: '+value)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=reject)


def _safe_path(value):
    """Reject reparse ancestors before traversing them, then recheck resolution."""
    if not isinstance(value,(str,Path)):raise ValueError('Explicit local path required')
    text=str(value)
    if not text or text.startswith(('\\\\','//'))or '://'in text or any(c in text for c in ('\0','\n','\r')):
        raise ValueError('Only local, non-reparse paths are accepted')
    parsed=Path(text)
    if parsed.drive.startswith(('\\\\','//'))or parsed.anchor.startswith(('\\\\','//')):
        raise ValueError('Canonical UNC source paths are forbidden before filesystem probes')
    if parsed.drive and not parsed.is_absolute():raise ValueError('No drive-relative source path')
    path=ROOT/parsed
    if '..'in path.parts:raise ValueError('No parent traversal in source paths')
    for part in [*reversed(path.parents),path]:
        try:info=part.lstat()
        except FileNotFoundError:continue
        if stat.S_ISLNK(info.st_mode)or getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024):
            raise ValueError('Source path has a symlink or reparse ancestor')
    resolved=path.resolve()
    if str(resolved).startswith(('\\\\','//')):raise ValueError('Resolved source is not local')
    return resolved


def _binding(path,raw):
    return dict(path=path.relative_to(ROOT).as_posix()if path.is_relative_to(ROOT)else str(path),
                bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def _inputs(manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    if expected_manifest_sha256!=MANIFEST_SHA256:raise ValueError('Exact full-cohort manifest pin required')
    path=_safe_path(manifest_path);raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_manifest_sha256:raise ValueError('Manifest hash mismatch')
    manifest=_json(raw)
    if ([a.get('round_id')for a in manifest.get('available',[])]!=[f'R{n}'for n in CONTEXTS]
            or manifest.get('missing_at_cutoff')!=[]or manifest.get('historical_missing_rounds')!=[110,111,112,113]
            or len(manifest.get('bindings',[]))!=37):
        raise ValueError('Exact twelve-round cutoff and37members required')
    refs={};paths={}
    # Validate ALL names/paths before any member content is opened.
    for ref in manifest['bindings']:
        name=ref.get('path');copy=ref.get('frozen_path')
        if (not isinstance(name,str)or not name or '\\'in name or ':'in name
                or PurePosixPath(name).is_absolute()or '..'in PurePosixPath(name).parts or name in refs):
            raise ValueError('Unique safe logical source path required')
        number=re.search(r'(?:^|_)r(\d+)(?:_|\.)',PurePosixPath(name).name)
        if number and int(number[1])not in CONTEXTS:raise ValueError('Source round outside fixed full cohort')
        expected=OUT/'inputs'/name
        if copy!=expected.relative_to(ROOT).as_posix():raise ValueError('Frozen path differs from the fixed input tree')
        if type(ref.get('bytes'))is not int or not 0<ref['bytes']<=10_000_000:
            raise ValueError('Bounded exact source size required')
        if not isinstance(ref.get('sha256'),str)or not re.fullmatch('[0-9a-f]{64}',ref['sha256']):
            raise ValueError('Exact source SHA256 required')
        paths[name]=_safe_path(expected);refs[name]=deepcopy(ref)
    for item in manifest['available']:
        if (not isinstance(item.get('recipe_paths'),list)or len(item['recipe_paths'])!=1
                or any(item.get(k)not in refs for k in ('receipt','tsv_path'))
                or item['recipe_paths'][0]not in refs):raise ValueError('Complete authenticated per-round triple required')
    contents={}
    for name,path in paths.items():
        data=path.read_bytes();ref=refs[name]
        if len(data)!=ref['bytes']or hashlib.sha256(data).hexdigest()!=ref['sha256']:
            raise ValueError('Frozen source hash or size mismatch')
        contents[name]=data
        refs[name].update(original_path=name,path=path.relative_to(ROOT).as_posix())
    return manifest,refs,contents,_binding(path=_safe_path(manifest_path),raw=raw)


def _template(node):
    if isinstance(node,ast.Constant)and isinstance(node.value,str):return node.value
    if isinstance(node,ast.JoinedStr):
        result=''
        for part in node.values:
            if isinstance(part,ast.Constant)and isinstance(part.value,str):result+=part.value
            elif isinstance(part,ast.FormattedValue)and isinstance(part.value,ast.Name)and part.format_spec is None:
                result+='{'+part.value.id+'}'
            else:raise ValueError('Unsupported compound command interpolation')
        return result
    raise ValueError('Literal compound command template required')


def recipe_compound_controls(text,payload):
    """Identify the static HTT branch and both endpoint callers without executing."""
    number=old._physical_round_number(payload,max_round=146)
    if number not in CONTEXTS:raise ValueError('Recipe round outside fixed full cohort')
    tree=ast.parse(text)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name==f'apply_r{number}_hmac_state']
    if len(functions)!=1:raise ValueError('Unique round-specific applier required')
    fn=functions[0];nested=[n for n in fn.body if isinstance(n,ast.FunctionDef)and n.name=='_peer_extra']
    if len(nested)!=1:raise ValueError('Unique endpoint command template required')
    returns=[n for n in nested[0].body if isinstance(n,ast.Return)]
    if len(returns)!=1:raise ValueError('Explicit endpoint command return required')
    template=_template(returns[0].value)
    result={}
    if HTT_NODE not in template:
        for item in payload['iterations']:
            result[item['commit']]=dict(status='NO_HTT_PAIR_DECLARATION_IN_THIS_RECIPE',
                declared_endpoint_pairs=None,readback_text_pairs=None,effective_control_verified=False,
                feedback_adaptive_control_verified=False,GI_LDPC_STBC_setter_verified=False)
        return result
    condition=r'if \[ "\{force_tx_status\}" = "1" \]; then\s+echo "(\d+) (\d+)" > '+re.escape(HTT_NODE)+r'[^\n]*\s+else\s+echo "(\d+) (\d+)" > '+re.escape(HTT_NODE)+r'[^\n]*\s+fi'
    matches=list(re.finditer(condition,template))
    if len(matches)!=1 or len(re.findall(r'echo "\d+ \d+" > '+re.escape(HTT_NODE),template))!=2:
        raise ValueError('Exact static force_tx_status HTT branch required')
    values=tuple(int(v)for v in matches[0].groups())
    if values not in ((3,32,3,64),(3,16,3,64)):raise ValueError('Unknown compound HTT tuple; no inferred range')
    callers=[]
    for node in fn.body:
        if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            call=node.value
            if isinstance(call,ast.Call)and isinstance(call.func,ast.Name)and call.func.id=='rpc'and len(call.args)>=2:
                expr=call.args[1]
                if isinstance(expr,ast.BinOp)and isinstance(expr.op,ast.Add)and isinstance(expr.right,ast.Call):
                    right=expr.right
                    if isinstance(right.func,ast.Name)and right.func.id=='_peer_extra'and len(right.args)==1:
                        callers.append((ast.unparse(call.args[0]),ast.unparse(right.args[0])))
    if sorted(callers)!=[('b.ap','pair.ap_state'),('b.client','pair.cpe_state')]:
        raise ValueError('Same compound template must be declared for separate AP and CPE')
    for item in payload['iterations']:
        force=item['candidate_knobs'].get('force_tx_status')
        old.exact_integer(force,'compound branch force_tx_status',0,1)
        pair=list(values[:2]if force==1 else values[2:]);observed={};matches_text={}
        readback=item.get('readback')
        if not isinstance(readback,dict):raise ValueError('Readback container must be an object')
        for endpoint in ('ap','cpe'):
            saved=readback.get(endpoint+'_readback')
            if saved is not None and not isinstance(saved,str):raise ValueError('Saved endpoint readback text required')
            parsed=[[int(x),int(y)]for x,y in re.findall(r'^[ \t]*(\d+)[ \t]+(\d+)[ \t]*\r?$',saved or'',re.M)]
            observed[endpoint]=parsed;matches_text[endpoint]=len(parsed)==1 and parsed[0]==pair
        result[item['commit']]=dict(status='STATIC_RECIPE_HTT_PAIR_DECLARATION_NOT_ADAPTIVE_QUALIFICATION',
            declared_endpoint_pairs={e:list(pair)for e in ('ap','cpe')},
            source_branch=dict(field='force_tx_status',value=force),
            source_lines=[nested[0].lineno,nested[0].end_lineno],
            readback_text_pairs=observed,readback_text_matches_declaration=matches_text,
            readback_status='MATCHED_SAVED_TEXT_ONLY'if all(matches_text.values())else'UNKNOWN_OR_CONFLICTING_SAVED_TEXT',
            effective_control_verified=False,feedback_adaptive_control_verified=False,
            GI_LDPC_STBC_setter_verified=False)
    return result


@dataclass(frozen=True)
class FullHmacMeasurement(old.DyadicCampaignMeasurement):
    hmac_source_controls: dict | None=None
    voip_probe_tos: str | None=None
    voip_evidence: dict | None=None
    compound_recipe_controls: dict | None=None

    def __post_init__(self):
        super().__post_init__()
        if self.round_id not in {f'R{n}'for n in range(140,147)}:raise ValueError('New typed rows only R140-R146')
        distance,coverage,slot,ack=CONTEXTS[int(self.round_id[1:])]
        if (self.workload_regime!=REGIME or type(self.active_flow_count)is not int or self.active_flow_count!=8
                or self.bidirectional is not True or type(self.distance_meters)is not int or self.distance_meters!=distance
                or type(self.coverage_class)is not int or self.coverage_class!=coverage or self.voip_probe_tos!='0xb8'
                or self.cpe_policy is None or any(type(p.distance_meters)is not int or p.distance_meters!=distance for p in (self.ap_policy,self.cpe_policy))):
            raise ValueError('Exact full hMAC/VoIP context required; ordinary bidir8 is not an alias')
        evidence=self.certified_wds_evidence
        for key,value in (('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)):
            if type(evidence.get(key))is not int or evidence[key]!=value:raise ValueError('Typed timing conflict')
        if evidence.get('physical_distance_verified')is not False or evidence.get('effective_timing_independently_verified')is not False:
            raise ValueError('Saved timing declarations are not physical/effective proof')
        if not isinstance(self.hmac_source_controls,dict)or set(self.hmac_source_controls)!={'tx_aggr_factor','fq_flows'}:
            raise ValueError('Exact labelled source controls required')
        old.exact_integer(self.hmac_source_controls['tx_aggr_factor'],'tx_aggr_factor',0,255)
        old.exact_integer(self.hmac_source_controls['fq_flows'],'fq_flows',1,1_000_000)
        if self.hmac_source_controls['tx_aggr_factor']!=self.airtime_flags:raise ValueError('Recipe derives aggregation factor from airtime_flags')
        if (not isinstance(self.voip_evidence,dict)or self.voip_evidence.get('effective_AC_mapping_verified')is not False
                or any(self.voip_evidence.get(k)is not None for k in ('latency_ms','jitter_ms','packet_loss_pct','mos'))):
            raise ValueError('No separately identified voice metrics or effective AC qualification')
        if len(self.repetition_blocks)!=16 or type(self.restoration_verified)is not bool:raise ValueError('Exact saved block count and window health required')
        old.exact_integer(self.station_drops,'saved window station drops')
        if self.source_failure_metadata.get('disqualified')is not None and type(self.source_failure_metadata['disqualified'])is not bool:
            raise ValueError('Disqualification must be boolean or unknown')
        c=self.compound_recipe_controls
        if (not isinstance(c,dict)or c.get('effective_control_verified')is not False
                or c.get('feedback_adaptive_control_verified')is not False or c.get('GI_LDPC_STBC_setter_verified')is not False):
            raise ValueError('Explicit unqualified compound provenance required')
        pairs=c.get('declared_endpoint_pairs')
        if self.round_id=='R140':
            if pairs is not None:raise ValueError('No inferred HTT tuple for R140')
        else:
            if not isinstance(pairs,dict)or set(pairs)!={'ap','cpe'}:raise ValueError('Separate declared AP/CPE HTT pairs required')
            old.exact_integer(self.force_tx_status,'source compound force_tx_status',0,1)
            expected=[3,64]if self.force_tx_status==0 else[3,32 if int(self.round_id[1:])<=143 else 16]
            branch=c.get('source_branch')
            if (not isinstance(branch,dict)or branch.get('field')!='force_tx_status'
                    or type(branch.get('value'))is not int or branch['value']!=self.force_tx_status):
                raise ValueError('Exact static recipe branch identity required')
            for pair in pairs.values():
                if not isinstance(pair,list)or len(pair)!=2 or any(type(x)is not int for x in pair)or pair!=expected:
                    raise ValueError('Exact declared HTT tuple required, not a qualified range')

    @property
    def policy_key(self):
        endpoints=json.loads(super().policy_key)
        pairs=self.compound_recipe_controls['declared_endpoint_pairs']
        for endpoint,name in zip(endpoints,('ap','cpe')):
            endpoint.update(self.hmac_source_controls)
            endpoint.update(workload_identity=REGIME,voip_probe_tos=self.voip_probe_tos)
            if pairs is not None:endpoint['recipe_declared_htt_max_amsdu_ampdu']=pairs[name]
        return json.dumps(endpoints,sort_keys=True,separators=(',',':'))


def convert_full_hmac_payload(number,payload,ref,recipe,text,tsv_text):
    if type(number)is not int or number not in range(140,147):raise ValueError('New fixed R140-R146 only; no future payload access')
    compound=recipe_compound_controls(text,payload)
    def measurement(**values):
        return FullHmacMeasurement(**values,compound_recipe_controls=compound[values['iteration']])
    records,blocks,audit=live._convert_available_hmac_payload(number,payload,ref,recipe,text,tsv_text,
        contexts=CONTEXTS,max_round=146,measurement_type=measurement)
    by_id={item['commit']:item for item in payload['iterations']}
    for row in records:
        source=by_id[row['iteration']]
        row.update(reported_batch=payload.get('batch'),reported_batch_id=payload.get('batch_id'),
            source_reported_experiment_ref=source.get('experiment_ref'),source_recipe_filename=Path(recipe['path']).name,
            compound_treatment_effect_qualified=False)
        row['certified_wds_evidence']['compound_recipe_controls']=deepcopy(row['compound_recipe_controls'])
    for block in blocks:block['compound_recipe_controls']=deepcopy(compound[block['treatment_id']])
    audit.update(compound_recipe_controls=compound,reported_batch=payload.get('batch'),
        batch_title_is_not_control_authority=True,feedback_adaptive_aggregation_qualified=False)
    return records,blocks,audit


def _prior(path):
    path=_safe_path(path);raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PRIOR_PINS[path.name]:raise ValueError('Sealed R139 output hash mismatch')
    return _json(raw)


def _new(manifest_path,expected_manifest_sha256):
    manifest,refs,contents,binding=_inputs(manifest_path,expected_manifest_sha256)
    records=[];blocks=[];sources=[];audits=[]
    for item in manifest['available']:
        number=int(item['round_id'][1:])
        if number<140:continue  # Preserve the complete sealed prefix, including its original source references.
        ref=refs[item['receipt']];recipe=refs[item['recipe_paths'][0]];tsv=refs[item['tsv_path']]
        new,crossed,audit=convert_full_hmac_payload(number,_json(contents[item['receipt']]),ref,recipe,
            contents[item['recipe_paths'][0]].decode('utf-8'),contents[item['tsv_path']].decode('utf-8'))
        records.extend(new);blocks.extend(crossed);audits.append(audit)
        sources.append({**ref,'round_id':item['round_id'],'source_recipe':recipe,'source_tsv':tsv})
    probe=[r for r in refs.values()if r['original_path'].endswith('/pb_021_031_050_live_lap120_silicon_qualification_20261024.json')]
    if len(probe)!=1:raise ValueError('Exactly one authenticated saved silicon receipt required')
    return records,blocks,sources,audits,binding,probe[0]


def load_full_hmac_dataset(*,manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    new,blocks,refs,audits,binding,probe=_new(manifest_path,expected_manifest_sha256)
    prior=_prior(PRIOR_RECORDS);records=deepcopy(prior['records'])+new
    return dict(schema_version=20,evidence='SEALED_R139_PREFIX_PLUS_FROZEN_R140_R146_SAVED_PACKAGES',
        records=records,source_refs=deepcopy(prior['source_refs'])+refs,input_manifest=binding,
        available_at_cutoff=list(CONTEXTS),missing_at_cutoff=[],historical_missing_rounds=[110,111,112,113],
        new_round_audits=audits,observed_record_count=len(records),
        primary_window_count=sum(r['window_kind']=='primary'for r in records),
        auxiliary_window_count=sum(r['window_kind']!='primary'for r in records),
        new_crossed_observation_count=len(blocks),silicon_receipt_binding=probe,
        physical_acceptance=False,automatic_execution_allowed=False,software_versions=old.software_versions())


def load_full_hmac_blocks(*,manifest_path=MANIFEST,expected_manifest_sha256=MANIFEST_SHA256):
    _,new,refs,audits,binding,probe=_new(manifest_path,expected_manifest_sha256)
    prior=_prior(PRIOR_BLOCKS)
    return dict(crossed=deepcopy(prior['crossed'])+new,sequential=deepcopy(prior['sequential']),
        source_refs=deepcopy(prior['source_refs'])+refs,input_manifest=binding,
        available_at_cutoff=list(CONTEXTS),missing_at_cutoff=[],historical_missing_rounds=[110,111,112,113],
        new_round_audits=audits,silicon_receipt_binding=probe,
        physical_acceptance=False,automatic_execution_allowed=False)
