#!/usr/bin/env python3
"""Run available Stage231..268 tests and literal repo gate; expose missing coverage."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
RECEIPT='artifacts/autoresearch/stage268a_full_pytest_and_gate_receipt.json'
EXTRA={'tests/test_preflight_validate_user_board_info.py':{232}}
REVIEWED_SUITES={
 'test_preflight_validate_user_board_info.py',
 'test_stage241a_to_246a_guarida_stage0_and_irq33.py',
 'test_stage247a_to_252a_ltu_6stage_loop.py',
 'test_stage253a_hal_calling_convention.py','test_stage254a_knobs_1_85_hal_vtable.py',
 'test_stage255a_knobs_86_170_hal_vtable.py','test_stage256a_knobs_171_255_hal_vtable.py',
 'test_stage257a_reltext_rodata_knob_vtable_join.py','test_stage258a_ubnt_poll_reloc_sysctl_proc_trees.py',
 'test_stage259a_xw_ath_rate_atheros_re.py','test_stage263a_docs_budget_audit.py',
 'test_stage264a_all_firmware_crc32.py','test_stage265a_tester_recovery_matrix.py',
 'test_stage266a_cumulative_leaderboard.py','test_stage267a_human_context.py',
 'test_stage268a_full_release_regression.py'}


def stages_in_name(name):
    stages={int(n) for n in re.findall(r'stage(\d+)',name,re.I)}
    for first,last in re.findall(r'stage(\d+)[a-z]?_to_(\d+)[a-z]?',name,re.I):
        if int(first)<=int(last) and int(last)-int(first)<=100:
            stages.update(range(int(first),int(last)+1))
    return stages & set(range(231,269))


def catalog(root=ROOT):
    root=Path(root);rows=[];covered=set()
    for path in sorted((root/'tests').glob('test_*.py')):
        rel=path.relative_to(root).as_posix()
        stages=stages_in_name(path.name)|EXTRA.get(rel,set())
        if not stages:continue
        data=path.read_bytes()
        tree=ast.parse(data,filename=rel)
        # A combined filename covers its explicit stage range; test names add
        # only directly declared stages, without executing or importing tests.
        for node in ast.walk(tree):
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                stages|=stages_in_name(node.name)
        rows.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'stage_numbers':sorted(stages)})
        covered|=stages
    return {'suites':rows,'covered_stage_numbers':sorted(covered),
            'missing_stage_numbers':sorted(set(range(231,269))-covered),
            'unreviewed_suites':[r['path'] for r in rows if Path(r['path']).name not in REVIEWED_SUITES],
            'coverage_meaning':'Suite naming/declarations only; not completion or scientific acceptance.'}


def junit_counts(path):
    tree=ET.parse(path).getroot()
    suites=[tree] if tree.tag=='testsuite' else list(tree.findall('testsuite'))
    if not suites:raise ValueError('JUnit missing testsuite')
    counts={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
    counts['passed']=counts['tests']-sum(counts[k] for k in ('failures','errors','skipped'))
    if counts['passed']<0:raise ValueError('Invalid JUnit counts')
    return counts


def capture(command,root,timeout):
    try:
        r=subprocess.run(command,cwd=root,capture_output=True,text=True,encoding='utf-8',errors='replace',
                         timeout=timeout,shell=False)
        return {'command':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'timed_out':False}
    except subprocess.TimeoutExpired as exc:
        def text(v):return v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
        return {'command':command,'exit_code':None,'stdout':text(exc.stdout),'stderr':text(exc.stderr),'timed_out':True}
    except OSError as exc:
        return {'command':command,'exit_code':None,'stdout':'','stderr':str(exc),'timed_out':False}


def run(root=ROOT,timeout=600):
    root=Path(root).resolve();inventory=catalog(root)
    work=root/'artifacts/verification/stage268a';work.mkdir(parents=True,exist_ok=True)
    # New numbered directory preserves all previous attempts without retrying them.
    index=1
    while (work/f'run_{index}').exists():index+=1
    work=work/f'run_{index}';work.mkdir()
    backups=[]
    for path in sorted((root/'artifacts/autoresearch').glob('stage25*.json')):
        match=re.match(r'stage(\d+)',path.name)
        if not match or not 253<=int(match[1])<=259:continue
        data=path.read_bytes();saved=work/'inputs'/path.name;saved.parent.mkdir(exist_ok=True)
        saved.write_bytes(data)
        backups.append({'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),
                        'preserved_at':saved.relative_to(root).as_posix()})
    junit=work/'pytest.xml'
    command=['python','-m','pytest','-q',*[r['path'] for r in inventory['suites']],
             '--junitxml',str(junit)]
    blocked=('NO_SCOPED_SUITES' if not inventory['suites'] else
             'Unreviewed suites: '+str(inventory['unreviewed_suites']) if inventory['unreviewed_suites'] else None)
    pytest=(capture(command,root,timeout) if blocked is None else
            {'command':command,'exit_code':None,'stdout':'','stderr':blocked,'timed_out':False})
    counts=None
    if junit.exists():
        try:counts=junit_counts(junit)
        except (ET.ParseError,ValueError) as exc:pytest['junit_error']=str(exc)
    gate=capture(['python','tools/verify/enforce_5pillar_research_gate.py','--check-repo'],root,120)
    for name,record in (('pytest',pytest),('repo_gate',gate)):
        (work/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    unchanged=all(hashlib.sha256((root/r['path']).read_bytes()).hexdigest()==r['sha256'] for r in inventory['suites'])
    passed=(bool(counts) and counts['passed']>0 and pytest['exit_code']==0
            and not any(counts[k] for k in ('failures','errors','skipped')))
    complete=passed and gate['exit_code']==0 and not inventory['missing_stage_numbers'] and unchanged
    outputs={}
    for path in sorted(work.rglob('*')):
        if not path.is_file():continue
        outputs[path.relative_to(root).as_posix()]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size}
    result={'stage':'268A','task_id':'T-S268A-FULL-AVAILABLE-PYTEST-AND-GATE',
            'implementation':{'path':'tools/verify/run_stage268a_release_regression.py',
                              'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'static_sources':inventory['suites'],'coverage':inventory,'outputs':outputs,
            'preserved_legacy_receipts':[{**row,'unchanged_after':hashlib.sha256((root/row['path']).read_bytes()).hexdigest()==row['sha256']} for row in backups],
            'summary':{'pytest':counts,'pytest_exit_code':pytest['exit_code'],'repo_gate_exit_code':gate['exit_code'],
                       'all_available_tests_passed':passed,'suite_sources_unchanged':unchanged,
                       'full_requested_range_accepted':complete},
            'status':'PASS_LOCAL_SOFTWARE' if complete else 'INCOMPLETE_OR_FAILED_SEE_COVERAGE_AND_RUNS',
            'boundary':{'hardware_access':False,'scientific_five_pillar_truth_verified':False,
                        'repo_gate_is_wiring_check_not_audit_of_all_receipts':True,'missing_is_not_pass':True}}
    receipt_path=root/RECEIPT
    receipt_path.parent.mkdir(parents=True,exist_ok=True)
    receipt_path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--list',action='store_true');p.add_argument('--timeout',type=int,default=600)
    args=p.parse_args(argv)
    if args.list:print(json.dumps(catalog(args.root),indent=2));return 0
    if not 1<=args.timeout<=1800:p.error('timeout must be1..1800 seconds')
    result=run(args.root,args.timeout);print(json.dumps(result['summary']))
    return 0 if result['summary']['full_requested_range_accepted'] else 1


if __name__=='__main__':raise SystemExit(main())
