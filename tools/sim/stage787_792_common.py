"""Offline787..792 utilities: bounded immutable inputs and qualified outputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.re import ground_up_release_common as c

MAX_FILE=16*1024**2
MAX_TOTAL=64*1024**2
DEPS=('tools/sim/stage787_792_common.py','tools/re/ground_up_release_common.py',
      'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py')
BOUNDARY=dict(target_access=False,network_access=False,producer_execution=False,
              target_commands_executed=False,flash_approved=False,physical_acceptance=False)


def relative(label):
    if (not isinstance(label,str) or not label or '\\' in label or ':' in label
            or label.startswith('/') or any(p in ('.','..','') for p in label.split('/'))):
        raise ValueError('local_repo_relative_path_required')
    return label


def snapshot(root,label):
    label=relative(label);root=c.local_path(root).resolve();path=c.local_path(root/label)
    with path.open('rb') as stream:data=stream.read(MAX_FILE+1)
    if len(data)>MAX_FILE:raise ValueError('file_read_limit')
    return data,dict(path=label,bytes=len(data),sha256=c.sha(data))


def strict(data):
    obj=json.loads(data.decode('utf-8'),object_pairs_hook=c.pairs,parse_constant=c.invalid_constant)
    json.dumps(obj,allow_nan=False)
    return obj


def json_source(data):
    obj=strict(data)
    if not isinstance(obj,dict):raise ValueError('object_required')
    return obj


def freeze(root,stage,labels):
    """Reuse original cutoff copies; never repin a mutable producer on replay."""
    c.integer(stage,'stage',787,792);root=c.local_path(root).resolve()
    labels=list(labels)
    for label in labels:relative(label)
    if not labels or len(labels)>100 or len(set(labels))!=len(labels):raise ValueError('source_labels')
    base=f'artifacts/verification/stage{stage}a'
    manifest=f'{base}/frozen_sources.json';path=c.local_path(root/manifest)
    sources=[];payloads={};total=0
    if path.exists():
        obj=json_source(snapshot(root,manifest)[0])
        if obj.get('stage')!=f'{stage}A' or not isinstance(obj.get('sources'),list):raise ValueError('frozen_manifest')
        sources=obj['sources']
        if [p.get('origin_path') for p in sources]!=labels:raise ValueError('frozen_source_set_changed')
        for source in sources:
            label=source['origin_path'];digest=source['sha256']
            if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('source_digest')
            expected=f'{base}/sources/{digest}/{Path(label).name}'
            if source['frozen']['path']!=expected:raise ValueError('frozen_path_mismatch')
            data,pin=snapshot(root,expected);total+=len(data)
            if total>MAX_TOTAL:raise ValueError('total_source_limit')
            if pin!=source['frozen'] or pin['sha256']!=digest or pin['bytes']!=source['bytes']:
                raise ValueError('frozen_source_corrupted')
            payloads[label]=data
    else:
        for label in labels:
            data,pin=snapshot(root,label);total+=len(data)
            if total>MAX_TOTAL:raise ValueError('total_source_limit')
            frozen=f"{base}/sources/{pin['sha256']}/{Path(label).name}"
            target=c.local_path(root/frozen);target.parent.mkdir(parents=True,exist_ok=True)
            try:
                with target.open('xb') as stream:stream.write(data)
            except FileExistsError:
                if snapshot(root,frozen)[0]!=data:raise ValueError('existing_snapshot_corrupted')
            sources.append(dict(origin_path=label,sha256=pin['sha256'],bytes=pin['bytes'],
                                frozen=dict(path=frozen,sha256=pin['sha256'],bytes=pin['bytes'])))
            payloads[label]=data
        for source in sources:
            if snapshot(root,source['origin_path'])[0]!=payloads[source['origin_path']]:raise ValueError('source_changed_during_capture')
        c.write_json(path,dict(stage=f'{stage}A',sources=sources,
            meaning='Immutable current-byte cutoff, not authenticated historical acquisition or execution.'))
    return payloads,sources


def origins(root,sources):
    rows=[]
    for source in sources:
        try:
            pin=snapshot(root,source['origin_path'])[1]
            if pin['sha256']!=source['sha256']:rows.append(dict(path=source['origin_path'],status='CHANGED_SINCE_FROZEN_CUTOFF',current=pin))
        except (OSError,ValueError):rows.append(dict(path=source['origin_path'],status='CURRENT_ORIGIN_UNAVAILABLE'))
    return rows


def finish(root,stage,script,out,doc,text,result,sources):
    root=c.local_path(root).resolve()
    if len(text.splitlines())>=200:raise ValueError('doc_line_budget_GE200')
    for source in sources:
        if snapshot(root,source['frozen']['path'])[1]!=source['frozen']:raise ValueError('frozen_source_drift')
    c.write_doc(root/doc,text)
    result.update(schema_version='1.0.0',stage=f'{stage}A',task_id=f'T-S{stage}A-OFFLINE-RESEARCH',
        static_sources=sources,implementation=snapshot(root,script)[1],
        analysis_dependencies=[snapshot(root,p)[1]for p in DEPS],outputs={doc:snapshot(root,doc)[1]},
        boundary=dict(BOUNDARY),new_hardware_results=0,physical_acceptance='UNKNOWN_NOT_ASSESSED',E2='NOT_ACCEPTED',
        source_binding_meaning='Frozen held-byte cutoff only; original mutable paths are diagnostic, not replay inputs.',
        method_scope=dict(binary_re='Held source/receipt analysis only, no new binary execution.',
            literature='Offline only; no online scholar/web invocation.',experiment='No new RF campaign or counterbalanced acquisition.',
            analysis='Declared finite analytical sensitivity or evidence ledger; pytest validates tooling.',
            continuity='Repository plan/ledger/index and local evidence checkpoint.'))
    c.write_json(root/out,result);return result


def pareto(rows,objectives):
    """Exact nondominance; all named objectives minimize, preserving ties."""
    if len(rows)>5000:raise ValueError('pareto_row_limit')
    for row in rows:
        for key in objectives:c.finite(row[key],key,-1e12,1e12)
    return [i for i,a in enumerate(rows) if not any(
        all(b[k]<=a[k] for k in objectives) and any(b[k]<a[k] for k in objectives)
        for j,b in enumerate(rows) if i!=j)]


def cli(build,argv=None):
    p=argparse.ArgumentParser(description=build.__module__);p.add_argument('--root',type=Path,default=ROOT)
    result=build(p.parse_args(argv).root)
    print(json.dumps(dict(stage=result['stage'],status=result['status'],new_hardware_results=0),sort_keys=True))
    return 0
