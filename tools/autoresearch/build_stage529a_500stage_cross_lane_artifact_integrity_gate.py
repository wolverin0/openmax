#!/usr/bin/env python3
"""Bounded repository-wide stage JSON and Markdown policy audit; no remediation."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import time
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.autoresearch import stage525_530_common as h
from tools.re import ground_up_release_common as c

SCRIPT='tools/autoresearch/build_stage529a_500stage_cross_lane_artifact_integrity_gate.py'
OUT='artifacts/autoresearch/stage529a_500stage_cross_lane_artifact_integrity_gate.json'
DOC='docs/STAGE529A_500STAGE_CROSS_LANE_ARTIFACT_INTEGRITY_GATE.md'
EXCLUDED_DIRS={'.git','node_modules','.venv','venv','__pycache__','.pytest_cache'}
MAX_ENTRIES=600000;MAX_FILES=25000;MAX_BYTES=2*1024**3;MAX_FILE=32*1024**2
STAGE_NAME=re.compile(r'(?:^|[_-])stage[_-]?(\d{1,5})([a-z]*)',re.I)
DOC_TEXT='''<!-- doc-head: Stage529A repository-wide held-stage JSON and Markdown integrity audit -->
Strict local syntax, identity, header and line metrics retain historical and cross-lane findings.
<!-- /doc-head -->

# Stage529A

Parent: fixed525A..530A offline reconciliation queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage529a_500stage_cross_lane_artifact_integrity_gate.py`.
Exit0 means the scoped audit policy has no findings or unassessed inputs; exit1
retains findings/incomplete evidence. A generated receipt is not a compliance pass.

## Scope and fixed policy

Walk the whole local repository, including ignored artifacts, firmware, research,
third-party/reference clones and Markdown outside docs. Exclude only .git,
node_modules, .venv, venv, __pycache__ and .pytest_cache directory names.
Do not follow symlink/reparse entries. They remain reported, not traversed.
The output receipt cannot hash itself and is the single explicit self exclusion.
Stage530 outputs created after this scan are checked separately by its master gate.

All Markdown gets UTF8/hash/line/header metrics. The audit policy is strictly fewer
than220 lines and one paired doc-head at line1 with at most six summary lines.
Actual comments in fenced code or inline-code examples are excluded from active
header counting. Third-party and archived/reference roles are reported separately;
their policy deviations are not assertions that upstream docs are defective.
The strict all-scoped policy still reports those deviations, without editing files.

Every local JSON file within the read budget is examined to find stage declarations
even when its basename is generic. Stage-named files and JSON under stage-named
directories remain candidates if parsing fails or identity is absent. Duplicate
keys, nonfinite numbers and invalid JSON fail closed. Recognized stage envelopes,
command captures and raw data snapshots are distinguished. A minimal structural
envelope checks stage identity and known container types; it is not a universal
versioned domain schema, five-pillar research acceptance or native provenance.
Unknown schemas stay UNASSESSED. Missing letter suffixes are compatible, while
different numeric IDs or explicit conflicting suffixes are findings.

## Bounds and interpretation

At most600000 directory entries,25000 candidate files,32MiB per file and2GiB total
read bytes including rechecks bound one run. Failed reads conservatively charge
their reserved cap. Limit/read/decode issues are explicit and prevent a complete
pass. Other JSON files are counted as examined non-stage inputs, not experiments.
The captured Markdown/stage-JSON hashes are rechecked before return. Source drift
is reported; concurrent work is preserved. The inventory is a held-file cutoff,
not a transactionally immutable archive or acceptance of500/530 experiments.

Current525..528 receipts and the local policy/helper bytes are independently pinned.
The scanner performs no import/execution of acquisition producers, no networking,
radio access, firmware extraction, flash, publication or mass document rewrite.
Final counts and exact locations live in the JSON. Master530 separates pytest and
repository wiring success from repository-wide schema/header/budget findings.
Decision: KEEP the auditor; preserve every finding and unresolved schema.
'''


def identify(value):
    if type(value) is int:return str(value) if 1<=value<=99999 else None
    if not isinstance(value,str):return None
    m=re.match(r'^(?:stage[ _-]*)?(\d{1,5})([a-z]*)(?:\b|_)',value,re.I)
    return str(int(m[1]))+m[2].upper() if m and int(m[1])>0 else None


def compatible(a,b):
    x=re.fullmatch(r'(\d+)([A-Z]*)',a);y=re.fullmatch(r'(\d+)([A-Z]*)',b)
    return x[1]==y[1] and (not x[2] or not y[2] or x[2]==y[2])


def json_schema(obj,filename):
    findings=[];declared=[]
    if not isinstance(obj,dict):return {'kind':'UNASSESSED_DATA','findings':['NONOBJECT_STAGE_DATA_SCHEMA_UNDECLARED'],'declared_stage_ids':[]}
    candidates=[obj.get('stage')]
    if 'meta' in obj and not isinstance(obj['meta'],dict):findings.append('META_NOT_OBJECT')
    if isinstance(obj.get('meta'),dict):candidates.append(obj['meta'].get('stage'))
    for value in candidates:
        if value is not None:
            parsed=identify(value)
            if parsed is None:findings.append('UNRECOGNIZED_STAGE_ID')
            else:declared.append(parsed)
    match=STAGE_NAME.search(Path(filename).name)
    file_id=identify(match[1]+match[2]) if match else None
    for i,a in enumerate(declared):
        if file_id and not compatible(file_id,a):findings.append('FILENAME_DECLARED_STAGE_CONFLICT')
        if any(not compatible(a,b) for b in declared[i+1:]):findings.append('DECLARED_STAGE_CONFLICT')
    if declared:
        kind='MINIMAL_STAGE_ENVELOPE'
        for key in ('boundary','boundaries','summary','meta','outputs'):
            if key in obj and not isinstance(obj[key],dict):findings.append(key.upper()+'_NOT_OBJECT')
        if 'static_sources' in obj and not isinstance(obj['static_sources'],list):findings.append('STATIC_SOURCES_NOT_ARRAY')
    elif 'command' in obj and 'exit_code' in obj:
        kind='COMMAND_CAPTURE'
        if not isinstance(obj['command'],list) or not all(isinstance(s,str) for s in obj['command']):findings.append('COMMAND_NOT_ARGV_ARRAY')
        if obj['exit_code'] is not None and type(obj['exit_code']) is not int:findings.append('EXIT_CODE_NOT_INT_OR_NULL')
    else:kind='UNASSESSED_OBJECT_SCHEMA';findings.append('NO_RECOGNIZED_RECEIPT_ENVELOPE')
    return {'kind':kind,'findings':sorted(set(findings)),'declared_stage_ids':sorted(set(declared)),'filename_stage_id':file_id}


def without_inline_code(line):
    """Remove matched code spans; escaped opening ticks remain literal text."""
    runs=list(re.finditer(r'`+',line));parts=[];cursor=0;index=0
    while index<len(runs):
        opening=runs[index];before=line[:opening.start()]
        escaped=(len(before)-len(before.rstrip('\\')))%2
        if escaped:index+=1;continue
        closing=next((j for j in range(index+1,len(runs)) if len(runs[j][0])==len(opening[0])),None)
        if closing is None:index+=1;continue
        parts.append(line[cursor:opening.start()]);cursor=runs[closing].end();index=closing+1
    return ''.join(parts)+line[cursor:]


def markdown_policy(text):
    lines=text.splitlines();opens=[];closes=[];fence=None;bad_close=False
    for index,line in enumerate(lines,1):
        marker=re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$',line)
        if marker:
            token=marker[1]
            if fence is None:
                if token[0]!='`' or '`' not in marker[2]:fence=token;continue
            else:
                if token[0]==fence[0] and len(token)>=len(fence) and not marker[2].strip():fence=None
                continue
        if fence is not None:continue
        active=without_inline_code(line)
        if re.search(r'<!--\s*doc-head(?:\s*:|\s*-->)',active):opens.append(index)
        if re.search(r'<!--\s*/doc-head\s*-->',active):
            closes.append(index)
            if not re.fullmatch(r'<!-- /doc-head -->',active):bad_close=True
    errors=[]
    if len(lines)>=220:errors.append('LINE_BUDGET_GE220')
    if opens!=[1]:errors.append('SINGLE_DOC_HEAD_AT_LINE1_REQUIRED')
    if len(closes)!=1 or not 2<=closes[0]<=8:errors.append('SINGLE_INITIAL_PAIRED_CLOSE_REQUIRED')
    if bad_close:errors.append('PAIRED_CLOSE_LINE_FORMAT')
    if not lines or not re.fullmatch(r'<!-- doc-head: [^<>]+ -->',lines[0]):errors.append('INITIAL_HEADER_FORMAT')
    return {'lines':len(lines),'active_open_lines':opens,'active_close_lines':closes,'findings':errors}


def enumerate_files(root):
    pending=[root];files=[];issues=[];excluded=Counter();entries_seen=0
    while pending:
        directory=pending.pop()
        try:
            directory=c.local_path(directory)
            entries=[]
            with os.scandir(directory) as stream:
                for entry in stream:
                    entries_seen+=1
                    if entries_seen>MAX_ENTRIES:return files,issues+[{'reason':'ENTRY_LIMIT'}],dict(excluded)
                    entries.append(entry)
            entries.sort(key=lambda e:e.name)
        except (OSError,ValueError):
            issues.append({'path':directory.relative_to(root).as_posix(),'reason':'DIRECTORY_READ_ERROR'});continue
        for entry in entries:
            path=Path(entry.path);label=path.relative_to(root).as_posix()
            try:info=entry.stat(follow_symlinks=False)
            except OSError:issues.append({'path':label,'reason':'STAT_ERROR'});continue
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&0x400:
                issues.append({'path':label,'reason':'REPARSE_OR_SYMLINK_NOT_FOLLOWED'});continue
            if stat.S_ISDIR(info.st_mode):
                if entry.name in EXCLUDED_DIRS:excluded[entry.name]+=1
                else:pending.append(path)
            elif stat.S_ISREG(info.st_mode) and path.suffix.lower() in ('.json','.md'):
                if label==OUT:continue
                if len(files)>=MAX_FILES:return files,issues+[{'reason':'FILE_LIMIT'}],dict(excluded)
                files.append(path)
    return sorted(files),issues,dict(excluded)


def parse_float(value):
    result=float(value)
    if not math.isfinite(result):raise ValueError('NONFINITE_JSON_NUMBER')
    return result


def read_bounded(path,maximum=None):
    path=c.local_path(path)
    cap=MAX_FILE if maximum is None else min(MAX_FILE,maximum)
    if path.stat().st_size>cap:raise ValueError('FILE_SIZE_OR_READ_BUDGET_LIMIT')
    with path.open('rb') as stream:data=stream.read(cap)
    if path.stat().st_size!=len(data):raise ValueError('SOURCE_SIZE_CHANGED_DURING_READ')
    return data


def role(label):
    if '/archive/' in label.lower():return 'ARCHIVED_REFERENCE'
    if label.startswith(('repos/','tools/research/srccache/','infra_openwisp_official/')):return 'THIRD_PARTY_REFERENCE'
    return 'PROJECT_OR_SAVED_ARTIFACT'


def audit(root=ROOT):
    root=c.local_path(root).resolve();paths,issues,excluded=enumerate_files(root)
    docs=[];receipts=[];total=0;nonstage=0;unclassified=0;pins=[]
    for path in paths:
        label=path.relative_to(root).as_posix();candidate=any(STAGE_NAME.search(p) for p in path.relative_to(root).parts)
        try:
            path=c.local_path(path)
            size=path.stat().st_size
            if total+size>MAX_BYTES:raise ValueError('TOTAL_READ_BUDGET')
            allowance=min(size,MAX_FILE,MAX_BYTES-total)
            try:data=read_bounded(path,maximum=allowance)
            except (OSError,ValueError):total+=allowance;raise
            total+=len(data)
            pin={'path':label,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
            try:text=data.decode('utf-8')
            except UnicodeError:
                issues.append({**pin,'reason':'UTF8_DECODE_ERROR'});pins.append(pin)
                if path.suffix.lower()=='.md':docs.append({**pin,'role':role(label),'lines':None,'active_open_lines':[],
                    'active_close_lines':[],'findings':['UTF8_DECODE_ERROR']})
                elif candidate:receipts.append({**pin,'role':role(label),'schema':{'kind':'INVALID_ENCODING','findings':['UTF8_DECODE_ERROR'],'declared_stage_ids':[]}})
                else:unclassified+=1
                continue
            if path.suffix.lower()=='.md':
                docs.append({**pin,'role':role(label),**markdown_policy(text)});pins.append(pin);continue
            try:obj=json.loads(text,object_pairs_hook=c.pairs,parse_constant=c.invalid_constant,parse_float=parse_float)
            except (ValueError,RecursionError):
                if candidate:receipts.append({**pin,'role':role(label),'schema':{'kind':'INVALID_JSON','findings':['INVALID_DUPLICATE_NONFINITE_OR_TOO_DEEP_JSON'],'declared_stage_ids':[]}});pins.append(pin)
                else:unclassified+=1
                continue
            declared=(obj.get('stage') if isinstance(obj,dict) else None)
            meta=obj.get('meta',{}) if isinstance(obj,dict) else {}
            found=identify(declared) or (identify(meta.get('stage')) if isinstance(meta,dict) else None)
            if candidate or found:
                receipts.append({**pin,'role':role(label),'schema':json_schema(obj,label)});pins.append(pin)
            else:nonstage+=1
        except (OSError,ValueError,UnicodeError) as exc:
            issues.append({'path':label,'reason':str(exc) if isinstance(exc,ValueError) else type(exc).__name__})
    drift=[];recheck_bytes=0;checked=set()
    for index,pin in enumerate(pins):
        try:
            path=c.local_path(root/pin['path'])
            size=path.stat().st_size;remaining=MAX_BYTES-total-recheck_bytes
            if size>remaining:
                issues.append({'reason':'RECHECK_READ_BUDGET','unrechecked_files':len(pins)-index});break
            allowance=min(size,MAX_FILE,remaining)
            try:data=read_bounded(path,maximum=allowance)
            except (OSError,ValueError):recheck_bytes+=allowance;raise
            recheck_bytes+=len(data);checked.add(pin['path'])
            if c.sha(data)!=pin['sha256']:drift.append(pin['path'])
        except (OSError,ValueError):
            drift.append(pin['path']);issues.append({'path':pin['path'],'reason':'RECHECK_READ_ERROR'})
    doc_findings=sum(bool(r['findings']) for r in docs);json_findings=sum(bool(r['schema']['findings']) for r in receipts)
    statuses=Counter(f for r in docs for f in r['findings']);schemas=Counter(f for r in receipts for f in r['schema']['findings'])
    numbers=sorted({int(re.match(r'\d+',sid)[0]) for r in receipts for sid in r['schema']['declared_stage_ids']})
    summary={'markdown_files':len(docs),'stage_json_candidates':len(receipts),'nonstage_json_examined':nonstage,
             'unclassified_invalid_nonstage_json':unclassified,'markdown_with_findings':doc_findings,'stage_json_with_findings':json_findings,
             'scan_issues':len(issues),'source_drift':len(drift),'distinct_declared_numeric_stage_ids':len(numbers),'new_hardware_results':0}
    clear=bool(docs and receipts) and not(doc_findings or json_findings or issues or drift or unclassified)
    return {'summary':summary,'status':'PASS_SCOPED_STRUCTURAL_POLICY' if clear else 'FAIL_OR_UNASSESSED_REPOSITORY_ARTIFACT_POLICY',
            'markdown_inventory':docs,'stage_json_inventory':receipts,'scan_issues':issues,'source_drift':drift,
            'markdown_finding_counts':dict(statuses),'schema_finding_counts':dict(schemas),'declared_numeric_stage_ids':numbers,
            'snapshot':{'read_bytes':total+recheck_bytes,'initial_read_bytes':total,'recheck_read_bytes':recheck_bytes,
                        'read_budget_accounting':'Returned bytes, conservatively reserved cap on failed reads.',
                        'candidate_files_enumerated':len(paths),'excluded_directory_counts':excluded,
                        'excluded_directory_names':sorted(EXCLUDED_DIRS),'self_exclusion':[OUT],
                        'file_hashes_rechecked':len(checked)==len(pins),
                        'unrechecked_paths':[p['path'] for p in pins if p['path'] not in checked]},
            'scope_checks':{'has_markdown':bool(docs),'has_stage_json':bool(receipts)},
            'gaps':['Minimal structural schemas are not domain/scientific/provenance validation.',
                    'All-scoped Markdown policy includes separately labeled third-party/archived deviations, without declaring upstream defects.',
                    'The held-file cutoff is not transactional; newly created files after enumeration are outside this run.',
                    'No500/530-stage experiment completion or physical acceptance is inferred from file/ID counts.']}


def build(root=ROOT):
    root=c.local_path(root).resolve();c.write_doc(root/DOC,DOC_TEXT);result=audit(root)
    sources=[]
    for name in ('stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler',
                 'stage526a_xtensa_ram_canary_pb040_pb050_abi_auditor',
                 'stage527a_guarida_subcarrier51_notch_and_mcs2_audit',
                 'stage528a_ltu_dcxo_gps_tcxo_and_144window_reconciler'):
        sources.append(h.snapshot(root,'artifacts/autoresearch/'+name+'.json')[1])
    sources.append(h.snapshot(root,'AGENTS.md')[1])
    return h.finish(root,529,SCRIPT,OUT,DOC,DOC_TEXT,result,sources)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    a=p.parse_args(argv);r=build(a.root);print(json.dumps({'status':r['status'],'summary':r['summary']},sort_keys=True))
    return 0 if r['status']=='PASS_SCOPED_STRUCTURAL_POLICY' else 1


if __name__=='__main__':raise SystemExit(main())
