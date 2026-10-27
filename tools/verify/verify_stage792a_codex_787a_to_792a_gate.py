#!/usr/bin/env python3
"""Explicit seven-suite offline gate for787A..792A, with frozen input evidence."""
import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
from tools.verify.run_stage358a_ground_up_regression import capture
c=h.c
SCRIPT='tools/verify/verify_stage792a_codex_787a_to_792a_gate.py'
OUT='artifacts/autoresearch/stage792a_codex_787a_to_792a_gate_receipt.json'
DOC='docs/STAGE792A_CODEX_787A_TO_792A_GATE.md'
STAGES={
    787:('tools/sim/run_stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.py','wa_vht20_78mbps_vs_vht40_channel_efficiency_sim'),
    788:('tools/sim/run_stage788a_guarida_backbone_5210_to_5220_shift_pareto.py','guarida_backbone_5210_to_5220_shift_pareto'),
    789:('tools/observability/build_stage789a_bench_and_tower_rogue_dhcp_audit_ledger.py','bench_and_tower_rogue_dhcp_audit_ledger'),
    790:('tools/sim/run_stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.py','panel1_guarida_84_20h_zero_drop_reliability_model'),
    791:('tools/verify/build_stage791a_800stage_horizon_readiness_audit.py','800stage_horizon_readiness_audit')}
STAGES={n:(p,f'artifacts/autoresearch/stage{n}a_{name}.json',f'docs/STAGE{n}A_{name.upper()}.md')for n,(p,name)in STAGES.items()}
SUITES=tuple(f'tests/test_stage{n}a.py'for n in range(787,793))+('tests/test_stage787a_to_792a_suite.py',)
REVIEWS=tuple(f'artifacts/verification/stage{n}a/independent_review.json'for n in STAGES)
CAPTURE='tools/verify/run_stage358a_ground_up_regression.py'
GATE=['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo']
CONTINUITY=tuple('docs/'+p for p in ('CURRENT_STATE.md','MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md','BENCH_PLAN.md','DECISIONS.md','RESEARCH_LEDGER.md'))
INPUTS=tuple(p for group in STAGES.values()for p in group)+SUITES+(SCRIPT,DOC,CAPTURE,GATE[1])+h.DEPS+CONTINUITY
DOC_TEXT='''<!-- doc-head: Stage792A seven-suite offline787..792 gate with frozen provenance and explicit limits -->
Local software validation is separate from DHCP, RF, reliability and800-stage acceptance.
<!-- /doc-head -->

# Stage792A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/verify/verify_stage792a_codex_787a_to_792a_gate.py`.
Each stage has its own script, JSON, compact initial-header doc and dedicated suite.
The seventh suite checks the consolidated contracts. No hardware, network,
producer/helper/firmware execution, DHCP probes, configuration, channel change,
flash, deployment, remote access or RF load is performed.

## Reproducible local gate

Each invocation gets an exclusive artifacts/verification/stage792a/run_NNN folder.
Retain actual subprocess commands, stdout/stderr, exits, JUnit and before/after pins.
Run only the seven explicit pytest files, with addopts cleared and xunit1 file
attributes required. All seven files need nonzero collected cases, no unexpected
file, skip, failure or error, and a real zero child exit. Missing suites, reviews,
frozen copies, invalid manifests, drift or malformed containers cannot pass.
No absent-file fallback invokes an unscoped pytest or recursively runs this gate.
PYTEST_ADDOPTS/PYTEST_PLUGINS are removed from child environment by the capture helper.

Independent787..791 reviews must explicitly PASS with empty blocking findings
and bind the current four stage deliverables, three analysis dependencies and
source manifest. Every manifest must match the receipt and its frozen copy hashes.
Original source paths are diagnostic; immutable copies define the analyzed cutoff.
Source-origin changes are recorded separately and never silently repinned.
This is neither current runtime proof nor authenticated historical acquisition.
The final792 receipt cannot hash itself or be required by its own inner pytest;
its creation/pin and independent792 review are checked after the run.

Run the literal second command:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
Its zero exit is wiring/budget evidence only, not every receipt's five-pillar
scientific acceptance. Historical529 findings and530's205PASS/2FAIL remain in791.
No inherited failures are overwritten or reclassified as passing this new queue.

PASS_LOCAL_TOOLING_ONLY/exit0 requires all local checks and revision-bound reviews.
Other outcomes retain INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE/exit1 with exact gaps.
Even a local pass leaves physical acceptance UNKNOWN, E2 NOT_ACCEPTED and800
readiness HOLD_EVIDENCE_GAPS. No fixture count or hypothetical bound promotes RF.
787 is conditional nominal-channel efficiency,788 is an uncalibrated two-ray/AWGN
capacity integral,789 cannot prove runtime DHCP eradication,790 cannot establish
20h zero-outage surveillance, and791's catalog is filename presence only.
All six new documents stay below200 lines with one initial paired doc-head.
Decision: KEEP verified local tools and unresolved empirical evidence explicitly.
'''


def document_contract(text):
    lines=text.splitlines()
    if (not lines or len(lines)>=200 or not re.fullmatch(r'<!-- doc-head: [^<>]+ -->',lines[0])
            or text.count('<!-- doc-head:')!=1 or text.count('<!-- /doc-head -->')!=1
            or '<!-- /doc-head -->'not in lines[1:8]):raise ValueError('document_contract')
    return dict(lines=len(lines),initial_paired_head=True)


def stage_evidence(root,stage):
    script,label,doc=STAGES[stage];r=h.json_source(h.snapshot(root,label)[0])
    if r.get('stage')!=f'{stage}A' or not str(r.get('status','')).startswith('QUALIFIED_OFFLINE_'):
        raise ValueError('qualified_stage_identity_required')
    boundary=r.get('boundary')
    if (not isinstance(boundary,dict) or set(boundary)!=set(h.BOUNDARY) or any(boundary[k]is not False for k in h.BOUNDARY)
            or type(r.get('new_hardware_results'))is not int or r['new_hardware_results']!=0):
        raise ValueError('offline_boundary_required')
    deps=r.get('analysis_dependencies')
    if (not isinstance(deps,list) or len(deps)!=3 or any(not isinstance(p,dict)for p in deps)
            or {p.get('path')for p in deps}!=set(h.DEPS)):raise ValueError('three_dependencies_required')
    outputs=r.get('outputs')
    if not isinstance(outputs,dict):raise ValueError('output_map_required')
    for pin in [r.get('implementation'),*deps,outputs.get(doc)]:
        if not isinstance(pin,dict) or h.snapshot(root,pin['path'])[1]!=pin:raise ValueError('current_owned_pin_mismatch')
    if r['implementation']['path']!=script:raise ValueError('wrong_implementation_path')
    if outputs[doc]['path']!=doc:raise ValueError('wrong_document_path')
    metrics=document_contract(h.snapshot(root,doc)[0].decode('utf-8'))
    manifest_label=f'artifacts/verification/stage{stage}a/frozen_sources.json'
    data,manifest_pin=h.snapshot(root,manifest_label);manifest=h.json_source(data)
    sources=r.get('static_sources')
    if (not isinstance(sources,list) or not 1<=len(sources)<=100 or manifest.get('stage')!=f'{stage}A'
            or manifest.get('sources')!=sources):raise ValueError('frozen_manifest_receipt_mismatch')
    bindings=[manifest_pin];seen=set();total=0
    for source in sources:
        if not isinstance(source,dict):raise ValueError('source_object_required')
        origin=h.relative(source['origin_path'])
        if origin in seen:raise ValueError('duplicate_origin')
        seen.add(origin);digest=source['sha256']
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('digest_required')
        expected=f'artifacts/verification/stage{stage}a/sources/{digest}/{Path(origin).name}'
        frozen=source['frozen']
        if not isinstance(frozen,dict) or frozen.get('path')!=expected:raise ValueError('frozen_path_required')
        _,pin=h.snapshot(root,expected);total+=pin['bytes']
        if (total>h.MAX_TOTAL or pin!=frozen or pin['sha256']!=digest
                or type(source['bytes'])is not int or pin['bytes']!=source['bytes']):raise ValueError('frozen_pin_mismatch')
        bindings.append(pin)
    return dict(stage=f'{stage}A',status=r['status'],doc=metrics,frozen_bindings=bindings,
                origin_diagnostics=h.origins(root,sources),origin_cutoff_bindings=[dict(origin_path=p['origin_path'],sha256=p['sha256'])for p in sources],
                physical_acceptance='NOT_ASSESSED')


def review(root,stage):
    row=dict(stage=f'{stage}A',status='MISSING_INVALID_OR_STALE_REVIEW')
    try:
        data,pin=h.snapshot(root,f'artifacts/verification/stage{stage}a/independent_review.json');r=h.json_source(data)
        bindings=[]
        for key in ('reviewed_files','frozen_review_files','analysis_dependencies'):
            values=r.get(key,[])
            if not isinstance(values,list):raise ValueError('review_binding_list')
            bindings.extend(values)
        for key in ('source_manifest','input_manifest'):
            if key in r:bindings.append(r[key])
        required=set(STAGES[stage])|set(h.DEPS)|{f'tests/test_stage{stage}a.py',f'artifacts/verification/stage{stage}a/frozen_sources.json'}
        checked=set();drift=[]
        for source in bindings:
            if not isinstance(source,dict):raise ValueError('review_pin_required')
            if h.snapshot(root,source['path'])[1]!=source:drift.append(source['path'])
            checked.add(source['path'])
        row.update(binding=pin,verdict=r.get('verdict'),drift=drift,missing_bindings=sorted(required-checked))
        if (str(r.get('verdict','')).startswith('PASS') and r.get('blocking_findings')==[] and not drift and not required-checked):
            row['status']='PASS_REVISION_BOUND_REVIEW'
    except (OSError,ValueError,TypeError,KeyError)as exc:row['error']=type(exc).__name__
    return row


def junit(path):
    data=c.read(path,maximum=8*1024**2)
    if b'<!'in data:raise ValueError('JUnit_DTD_forbidden')
    root=ET.fromstring(data)
    if root.tag not in ('testsuite','testsuites'):raise ValueError('JUnit_root')
    cases=list(root.iter('testcase'));counts=dict(tests=len(cases),passed=0,failures=0,errors=0,skipped=0);files=set();missing=0
    states={}
    for case in cases:
        marks=[k for k in ('failure','error','skipped')if case.find(k)is not None]
        if len(marks)>1 or any(len(case.findall(k))>1 for k in marks):raise ValueError('JUnit_conflicting_status')
        state={'failure':'failures','error':'errors','skipped':'skipped'}[marks[0]]if marks else 'passed'
        states[case]=state;counts[state]+=1
        label=case.attrib.get('file','').replace('\\','/')
        if label.startswith('./'):label=label[2:]
        if not label or ':'in label or label.startswith('/')or '..'in Path(label).parts:missing+=1
        else:files.add(label)
    for suite in root.iter():
        if suite.tag not in ('testsuite','testsuites'):continue
        descendants=list(suite.iter('testcase'))
        observed={key:sum(states[case]==key for case in descendants)for key in ('errors','failures','skipped')}
        observed['tests']=len(descendants)
        for key,value in observed.items():
            if key in suite.attrib:
                declared=suite.attrib[key]
                if not re.fullmatch(r'\d+',declared)or int(declared)!=value:raise ValueError('JUnit_count_mismatch:'+key)
    return dict(counts=counts,suite_files=sorted(files),missing_file_attributes=missing,
                missing_suites=sorted(set(SUITES)-files),unexpected_suites=sorted(files-set(SUITES)))


def run(root=ROOT,timeout=300,execute=None):
    root=c.local_path(root).resolve();c.integer(timeout,'timeout_seconds',1,900);execute=execute or capture
    c.write_doc(root/DOC,DOC_TEXT);document_contract(DOC_TEXT)
    base=c.local_path(root/'artifacts/verification/stage792a');base.mkdir(parents=True,exist_ok=True);index=1
    while True:
        work=base/f'run_{index:03d}'
        try:work.mkdir();break
        except FileExistsError:index+=1
    result=dict(stage='792A',schema_version='1.0.0',status='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE',
        run_directory=work.relative_to(root).as_posix(),gaps=[],stage_evidence=[],pytest_counts=None,
        boundary=dict(h.BOUNDARY),new_hardware_results=0,physical_acceptance='UNKNOWN_NOT_ASSESSED',
        E2='NOT_ACCEPTED',milestone800_acceptance='NOT_ACCEPTED',readiness800='HOLD_EVIDENCE_GAPS')
    before={};missing=[]
    for label in INPUTS+REVIEWS:
        try:before[label]=h.snapshot(root,label)[1]
        except(OSError,ValueError):missing.append(label)
    for n in STAGES:
        try:
            row=stage_evidence(root,n);result['stage_evidence'].append(row)
            for pin in row['frozen_bindings']:before[pin['path']]=pin
        except(OSError,ValueError,TypeError,KeyError)as exc:result['gaps'].append(f'STAGE_{n}_EVIDENCE:{type(exc).__name__}:{exc}')
    result['independent_reviews']=[review(root,n)for n in STAGES]
    if any(row['status']!='PASS_REVISION_BOUND_REVIEW'for row in result['independent_reviews']):
        result['gaps'].append('MISSING_FAILED_OR_STALE_REVIEW')
    if missing:result['gaps'].append('MISSING_INPUTS_NO_CHILD_EXECUTION')
    result['missing_inputs']=missing
    if not missing and not result['gaps']:
        xml=work/'pytest.xml'
        command=[sys.executable,'-m','pytest','-q','-o','addopts=','-o','junit_family=xunit1',*SUITES,'--junitxml='+str(xml)]
        test=execute(command,root,timeout);c.write_json(work/'pytest.json',test);result['pytest']=test
        try:
            evidence=junit(xml);result['junit_coverage']=evidence;result['pytest_counts']=evidence['counts']
            if any(evidence[k]for k in ('missing_suites','unexpected_suites','missing_file_attributes')):
                result['gaps'].append('INCOMPLETE_PYTEST_COLLECTION')
        except(OSError,ValueError,ET.ParseError):result['gaps'].append('MISSING_OR_INVALID_JUNIT')
        gate=execute(GATE,root,timeout);c.write_json(work/'repo_gate.json',gate);result['repo_gate']=gate
        counts=result['pytest_counts']or{}
        if (test.get('exit_code')!=0 or test.get('timed_out')is not False or counts.get('passed',0)<1
                or any(counts.get(k,0)for k in ('errors','failures','skipped'))):result['gaps'].append('PYTEST_FAILED_OR_INCOMPLETE')
        if gate.get('exit_code')!=0 or gate.get('timed_out')is not False:result['gaps'].append('WIRING_GATE_FAILED')
    elif not missing:result['gaps'].append('PREFLIGHT_FAILED_NO_CHILD_EXECUTION')
    drift=[]
    for label,pin in before.items():
        try:same=h.snapshot(root,label)[1]==pin
        except(OSError,ValueError):same=False
        if not same:drift.append(label)
    result['input_drift']=drift;result['static_sources']=list(before.values())
    result['origin_diagnostics_after_run']=[dict(stage=row['stage'],changes=h.origins(root,row['origin_cutoff_bindings']))for row in result['stage_evidence']]
    if drift:result['gaps'].append('OWNED_OR_FROZEN_INPUT_DRIFT_DURING_RUN')
    if not result['gaps']:result['status']='PASS_LOCAL_TOOLING_ONLY'
    result['self_reference']='Final792 receipt excluded from own hash and inner pytest; verify after creation.'
    result['outputs']={DOC:h.snapshot(root,DOC)[1]}
    c.write_json(work/'result.json',result);c.write_json(root/OUT,result);return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--timeout',type=int,default=300);a=p.parse_args(argv);r=run(a.root,a.timeout)
    print(json.dumps({k:r[k]for k in ('status','pytest_counts','gaps','readiness800')},sort_keys=True))
    return 0 if r['status']=='PASS_LOCAL_TOOLING_ONLY'else 1


if __name__=='__main__':raise SystemExit(main())
