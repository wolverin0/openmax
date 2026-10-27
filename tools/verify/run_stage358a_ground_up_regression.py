#!/usr/bin/env python3
"""Run only the six authorized local suites plus consolidated353..358 contract."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from tools.re import ground_up_release_common as c

OUT = 'artifacts/autoresearch/stage358a_ground_up_regression.json'
DOC = 'docs/STAGE358A_GROUND_UP_REGRESSION.md'
STAGES = {
    353: ('tools/re/build_stage353a_sub20mhz_pll_ofdm_timing_matrix.py', 'stage353a_sub20mhz_pll_ofdm_timing_matrix.json', 'STAGE353A_SUB20MHZ_PLL_OFDM_TIMING_MATRIX.md'),
    354: ('tools/sim/build_stage354a_wmi_4series_retry_fallback_pareto.py', 'stage354a_wmi_4series_retry_fallback_pareto.json', 'STAGE354A_WMI_4SERIES_RETRY_FALLBACK_PARETO.md'),
    355: ('tools/sim/build_stage355a_airselect_hopping_evasion_pareto.py', 'stage355a_airselect_hopping_evasion_pareto.json', 'STAGE355A_AIRSELECT_HOPPING_EVASION_PARETO.md'),
    356: ('tools/firmware/verify_openmax_tester_bundle.py', 'stage356a_tester_bundle_verifier.json', 'STAGE356A_TESTER_BUNDLE_VERIFIER.md'),
    357: ('tools/verify/build_stage357a_ground_up_350stage_reconciliation.py', 'stage357a_ground_up_350stage_reconciliation.json', 'STAGE357A_GROUND_UP_350STAGE_RECONCILIATION.md'),
}
SUITES = tuple(f'tests/test_stage{n}a.py' for n in range(353, 359)) + ('tests/test_stage353a_to_358a_ground_up_suite.py',)
SCRIPT = 'tools/verify/run_stage358a_ground_up_regression.py'
INPUTS = tuple(p for n, (script, receipt, doc) in STAGES.items() for p in
               (script, 'artifacts/autoresearch/' + receipt, 'docs/' + doc)) + SUITES + (
    SCRIPT, DOC, 'tools/re/ground_up_release_common.py', 'tools/verify/enforce_5pillar_research_gate.py')
GATE = ['python', 'tools/verify/enforce_5pillar_research_gate.py', '--check-repo']


def junit_evidence(path):
    data = c.read(path, maximum=8*1024*1024)
    if b'<!' in data: raise ValueError('JUnit_DTD_or_entity_forbidden')
    root = ET.fromstring(data)
    if root.tag not in ('testsuite', 'testsuites'): raise ValueError('JUnit_root')
    cases = list(root.iter('testcase'))
    counts = dict(tests=len(cases), failures=0, errors=0, skipped=0, passed=0)
    files = set(); missing_file_attributes = 0
    for case in cases:
        marks = [k for k in ('failure', 'error', 'skipped') if case.find(k) is not None]
        if len(marks) > 1: raise ValueError('JUnit_conflicting_case_status')
        counts[{'failure': 'failures', 'error': 'errors', 'skipped': 'skipped'}.get(marks[0], 'passed') if marks else 'passed'] += 1
        label = case.attrib.get('file', '').replace('\\', '/')
        if label.startswith('./'): label = label[2:]
        if not label or ':' in label or label.startswith('/') or '..' in Path(label).parts:
            missing_file_attributes += 1
        else: files.add(label)
    for suite in root.iter('testsuite'):
        direct = suite.findall('testcase')
        if direct and 'tests' in suite.attrib and int(suite.attrib['tests']) != len(direct):
            raise ValueError('JUnit_declared_count_mismatch')
    return dict(counts=counts, suite_files=sorted(files), missing_file_attributes=missing_file_attributes,
                missing_suites=sorted(set(SUITES)-files), unexpected_suites=sorted(files-set(SUITES)))


def junit_counts(path):
    return junit_evidence(path)['counts']


def capture(command, root, timeout):
    started = time.monotonic()
    try:
        env = dict(os.environ)
        for key in ('PYTEST_ADDOPTS', 'PYTEST_PLUGINS'): env.pop(key, None)
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=timeout, shell=False, env=env,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        return dict(command=command, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr,
                    timed_out=False, elapsed_seconds=time.monotonic()-started)
    except subprocess.TimeoutExpired as exc:
        text = lambda v: v.decode('utf-8', errors='replace') if isinstance(v, bytes) else v or ''
        return dict(command=command, exit_code=None, stdout=text(exc.stdout), stderr=text(exc.stderr),
                    timed_out=True, elapsed_seconds=time.monotonic()-started)
    except OSError as exc:
        return dict(command=command, exit_code=None, stdout='', stderr=str(exc), timed_out=False,
                    elapsed_seconds=time.monotonic()-started)


def review_status(root):
    rows = []
    for stage in STAGES:
        path = root/f'artifacts/verification/stage{stage}a/independent_review.json'
        row = dict(stage=stage, status='MISSING_OR_INVALID')
        try:
            report = c.load(path)
            if not isinstance(report, dict): raise ValueError('review_object_required')
            row['binding'] = c.binding(path, root)
            required = {STAGES[stage][0], f'tests/test_stage{stage}a.py',
                        'docs/'+STAGES[stage][2], 'artifacts/autoresearch/'+STAGES[stage][1]}
            checked = set(); drift = []
            for source in report.get('reviewed_files', []):
                label = source['path']
                if ':' in label or '\\' in label or label.startswith('/') or '..' in Path(label).parts:
                    raise ValueError('unsafe_review_binding')
                if c.sha(c.read(root/label)) != source['sha256']: drift.append(label)
                checked.add(label)
            row.update(verdict=report.get('verdict'), binding_drift=drift, missing_required_bindings=sorted(required-checked))
            if str(report.get('verdict', '')).startswith('PASS') and not report.get('blocking_findings') and not drift and not required-checked:
                row['status'] = 'PASS_QUALIFIED_REVISION_BOUND_REVIEW'
            else: row['status'] = 'FAIL_OR_STALE_REVIEW'
        except (OSError, ValueError, TypeError, KeyError): pass
        rows.append(row)
    return rows


def document(root):
    c.write_doc(root/DOC, '''<!-- doc-head: Stage358A local353..358 regression gate and evidence boundaries -->
Seven explicit pytest files and the literal repository gate; no radio actions.
<!-- /doc-head -->

# Stage358A

Parent: fixed353A..358A offline RE1/control-boundary queue.
Run `python tools/verify/run_stage358a_ground_up_regression.py`.
Each stage has its own script, JSON, compact document and dedicated pytest file.
The seventh suite checks their shared no-hardware and evidence contracts.
The runner never invokes an unscoped pytest when a suite is absent.

Tests use disposable files, saved modules, finite simulations and pinned native
SquashFS host tools. No device code, SSH, ping, flash, radio configuration or
hardware acquisition is invoked. Native host decompression is explicitly distinct
from prohibited execution of the held firmware/modules or target commands.

Each invocation gets an exclusive numbered directory under
artifacts/verification/stage358a. Stdout, stderr, commands, actual process exits,
JUnit cases, before/after input hashes and revision-bound353..357 reviews are
retained. A missing/failed/stale review prevents closure. Skips, zero tests,
missing files, source drift, process failure or missing JUnit cannot pass.
PYTEST_ADDOPTS/PYTEST_PLUGINS are removed from the child environment and configured
addopts is overridden. xunit1 file attributes must cover all seven exact suites;
missing/unexpected files or absent file attributes prevent a partial-collection pass.
Failures are not overwritten by a retry; an evidence-led changed fix requires a
new invocation. No runner executes itself recursively from its own unit tests.

The literal second command is:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
Its exit and output are captured separately. This command checks repository wiring
and document budgets. It does not validate every receipt, physical provenance or
five-pillar scientific acceptance. Stage357 retains that distinction explicitly.

The final JSON is the source for exact pass/fail/skip counts and qualified status.
353 conditional source timing is not QCA988x5/10MHz runtime support. 354 retry
plans emit no native188B WMI payload. 355 is an uncalibrated AirSelect-inspired
fluid model. 356 saved evidence consistency never approves a flash or guarantees
zero bricks. 357 file coverage is not350 accepted experiments. E2 NOT_ACCEPTED.
Decision: KEEP verified local tooling; physical/regulatory acceptance remains open.
''')


def run(root=ROOT, timeout=300, execute=None):
    root = c.local_path(root); c.integer(timeout, 'timeout_seconds', 1, 900)
    execute = execute or capture; document(root)
    base = c.local_path(root/'artifacts/verification/stage358a'); base.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        work = base/f'run_{index:03d}'
        try: work.mkdir(); break
        except FileExistsError: index += 1
    before = []; missing = []
    for label in INPUTS:
        try: before.append(c.binding(root/label, root))
        except (OSError, ValueError): missing.append(label)
    result = dict(stage='358A', task_id='T-S358A-GROUND-UP-REGRESSION', run_directory=work.relative_to(root).as_posix(),
                  static_sources=before, missing_inputs=missing, boundary=dict(target_access=False, physical_acceptance=False,
                  network_access=False, target_commands_executed=False, native_host_decoder_allowed=True),
                  status='INCOMPLETE_MISSING_INPUTS', pytest_counts=None, gaps=[])
    if not missing:
        junit = work/'pytest.xml'
        command = [sys.executable, '-m', 'pytest', '-q', '-o', 'addopts=', '-o', 'junit_family=xunit1',
                   *SUITES, '--junitxml='+str(junit)]
        test = execute(command, root, timeout); c.write_json(work/'pytest.json', test)
        result['pytest'] = {**test, 'log': (work/'pytest.json').relative_to(root).as_posix()}
        try:
            result['junit_coverage'] = junit_evidence(junit)
            result['pytest_counts'] = result['junit_coverage']['counts']
            if any(result['junit_coverage'][k] for k in ('missing_suites', 'unexpected_suites', 'missing_file_attributes')):
                result['gaps'].append('INCOMPLETE_OR_UNEXPECTED_PYTEST_COLLECTION')
        except (OSError, ValueError, ET.ParseError): result['gaps'].append('MISSING_OR_INVALID_JUNIT')
        gate = execute(GATE, root, timeout); c.write_json(work/'repo_gate.json', gate)
        result['repo_gate'] = {**gate, 'log': (work/'repo_gate.json').relative_to(root).as_posix()}
        counts = result['pytest_counts'] or {}
        passed = (test['exit_code'] == 0 and not test.get('timed_out') and counts.get('passed', 0) > 0
                  and not any(counts.get(k, 0) for k in ('failures', 'errors', 'skipped'))
                  and gate['exit_code'] == 0 and not gate.get('timed_out') and not result['gaps'])
        result['status'] = 'PASS_LOCAL_TOOLING_ONLY' if passed else 'FAIL_LOCAL_REGRESSION'
    result['independent_reviews'] = review_status(root)
    if any(r['status'] != 'PASS_QUALIFIED_REVISION_BOUND_REVIEW' for r in result['independent_reviews']):
        result['gaps'].append('MISSING_FAILED_OR_STALE_INDEPENDENT_REVIEW')
    result['input_drift'] = []
    for source in before:
        try: actual = c.binding(root/source['path'], root)
        except (OSError, ValueError): actual = None
        if actual != source: result['input_drift'].append(source['path'])
    if result['input_drift']: result['gaps'].append('INPUT_DRIFT_DURING_RUN')
    if result['gaps'] and result['status'] == 'PASS_LOCAL_TOOLING_ONLY': result['status'] = 'INCOMPLETE_EVIDENCE'
    result['outputs'] = {DOC: c.binding(root/DOC, root)}
    c.write_json(work/'result.json', result); c.write_json(root/OUT, result)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--timeout', type=int, default=300); args = p.parse_args(argv)
    result = run(args.root, args.timeout)
    print(json.dumps({k: result[k] for k in ('status', 'pytest_counts', 'run_directory', 'gaps')}, sort_keys=True))
    return 0 if result['status'] == 'PASS_LOCAL_TOOLING_ONLY' else 1


if __name__ == '__main__': raise SystemExit(main())
