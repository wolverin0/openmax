#!/usr/bin/env python3
"""Offline 525A..530A evidence gate; repository findings remain failures."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from tools.autoresearch import stage525_530_common as h
from tools.re import ground_up_release_common as c
from tools.verify.run_stage358a_ground_up_regression import capture

SCRIPT = 'tools/verify/verify_stage530a_codex_530stage_master_gate.py'
OUT = 'artifacts/verification/stage530a_codex_530stage_master_gate_receipt.json'
DOC = 'docs/STAGE530A_CODEX_530STAGE_MASTER_GATE.md'
NAMES = {
    525: 'pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler',
    526: 'xtensa_ram_canary_pb040_pb050_abi_auditor',
    527: 'guarida_subcarrier51_notch_and_mcs2_audit',
    528: 'ltu_dcxo_gps_tcxo_and_144window_reconciler',
    529: '500stage_cross_lane_artifact_integrity_gate',
}
STAGES = {n: (f'tools/autoresearch/build_stage{n}a_{name}.py',
              f'artifacts/autoresearch/stage{n}a_{name}.json',
              f'docs/STAGE{n}A_{name.upper()}.md') for n, name in NAMES.items()}
SUITES = tuple(f'tests/test_stage{n}a.py' for n in range(525, 531)) + (
    'tests/test_stage525a_to_530a_codex_master_gate.py',)
DEPS = ('tools/autoresearch/stage525_530_common.py', 'tools/re/ground_up_release_common.py',
        'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py',
        'tools/verify/run_stage358a_ground_up_regression.py',
        'tools/verify/enforce_5pillar_research_gate.py')
INPUTS = tuple(p for group in STAGES.values() for p in group) + SUITES + (SCRIPT, DOC) + DEPS
REVIEWS = tuple(f'artifacts/verification/stage{n}a/independent_review.json' for n in STAGES)
GATE = ['python', 'tools/verify/enforce_5pillar_research_gate.py', '--check-repo']
DOC_TEXT = '''<!-- doc-head: Stage530A offline525..530 master gate with retained repository findings -->
Seven explicit suites, revision-bound independent reviews and the literal repo gate.
Tool validation, repository policy and physical acceptance have separate outcomes.
<!-- /doc-head -->

# Stage530A — master evidence gate

Parent: fixed525A..530A offline RE1/control-boundary reconciliation in BENCH_PLAN.
Run `python tools/verify/verify_stage530a_codex_530stage_master_gate.py`.
The runner creates an exclusive artifacts/verification/stage530a/run_NNN directory.
It retains actual commands, stdout/stderr, exits, JUnit cases and before/after hashes.
Failures survive subsequent runs. No producer, radio, target code, firmware,
SSH, ping, configuration, patch, flash or load acquisition is executed.

Each525..529 receipt is checked against its held implementation/dependencies/doc.
Declared original sources are also pinned before/after this run. Changes since
the stage cutoff and changes during this run are separate INCOMPLETE findings;
neither is repaired by rewriting evidence or repeating acquisition producers.
Each independent review must bind the four current stage deliverables and have
an explicit PASS verdict with an explicit empty blocking_findings list.
Seven exact pytest files must all appear in xunit1 JUnit, with at least one case
each, no unexpected files, no missing file attributes, no skips/errors/failures,
and a real zero process exit. Missing files never trigger unscoped pytest.
The final530 receipt cannot include its own hash or require itself inside pytest;
its creation, pin and independent530 review are checked after this runner.

The second child command is literal:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
That command checks repository wiring. A zero exit does not authenticate every
receipt, validate every scientific pillar or establish physical acceptance.

Stage529's entire scoped JSON/Markdown inventory is a bounded held-file cutoff,
including labeled historical/vendor deviations. It is not a transactional live
snapshot or proof of500/530 completed experiments. Its self-exclusion and the
later-created530 files are explicit; this gate separately checks its own docs.
No historical/vendor documents are rewritten to manufacture global compliance.

Exit0 requires all local checks AND Stage529 PASS_SCOPED_STRUCTURAL_POLICY.
Exit1 with VALIDATED_TOOLING_WITH_REPOSITORY_FINDINGS means pytest and wiring
passed, but Stage529 retained FAIL/UNASSESSED findings. Missing/stale evidence,
drift or failed checks have a distinct INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE status.
Exact counts and policy findings are in the JSON, not copied into this document.

525 separates24.83Mbps aggregate and9.96Mbps UL profiles and the unrelated R45
pktlog delta.526 distinguishes register text from firmware-load/ABI causality.
527 recomputes6.453125dB and a cumulative99.1972% counter ratio, not storm rate.
528 finds38 dcxo/tcxo symbols (11bbp_rf_dcxo),12 direct windows vs144 cumulative
claims, loopback probe/default risks and no DCXO-to-OTA causal proof.
All are saved/static evidence with qualifications. E2 remains NOT_ACCEPTED.
Decision: KEEP reproducible local audits; no new hardware or performance acceptance.
'''


def junit_evidence(path):
    data = c.read(path, maximum=8*1024*1024)
    if b'<!' in data: raise ValueError('JUnit_DTD_or_entity_forbidden')
    root = ET.fromstring(data)
    if root.tag not in ('testsuite', 'testsuites'): raise ValueError('JUnit_root')
    cases = list(root.iter('testcase'))
    counts = dict(tests=len(cases), passed=0, failures=0, errors=0, skipped=0)
    files = set(); missing = 0
    for case in cases:
        marks = [k for k in ('failure', 'error', 'skipped') if case.find(k) is not None]
        if len(marks) > 1: raise ValueError('JUnit_conflicting_case_status')
        counts[{'failure': 'failures', 'error': 'errors', 'skipped': 'skipped'}[marks[0]] if marks else 'passed'] += 1
        label = case.attrib.get('file', '').replace('\\', '/')
        if label.startswith('./'): label = label[2:]
        if not label or ':' in label or label.startswith('/') or '..' in Path(label).parts: missing += 1
        else: files.add(label)
    for suite in root.iter('testsuite'):
        direct = suite.findall('testcase')
        if direct and 'tests' in suite.attrib and int(suite.attrib['tests']) != len(direct):
            raise ValueError('JUnit_declared_count_mismatch')
    return dict(counts=counts, suite_files=sorted(files), missing_file_attributes=missing,
                missing_suites=sorted(set(SUITES)-files), unexpected_suites=sorted(files-set(SUITES)))


def reviewed(root, stage):
    row = dict(stage=str(stage)+'A', status='MISSING_INVALID_OR_STALE_REVIEW')
    try:
        report, pin = h.json_source(root, f'artifacts/verification/stage{stage}a/independent_review.json')
        bindings = report.get('frozen_review_files', report.get('reviewed_files'))
        if not isinstance(bindings, list): raise ValueError('review_bindings_required')
        required = set(STAGES[stage]) | {f'tests/test_stage{stage}a.py'}
        checked = set(); drift = []
        for source in bindings + report.get('analysis_dependencies', []):
            if not isinstance(source, dict): raise ValueError('review_pin_required')
            actual = h.snapshot(root, source['path'])[1]
            if actual != source: drift.append(source['path'])
            checked.add(source['path'])
        row.update(binding=pin, verdict=report.get('verdict'), drift=drift,
                   missing_bindings=sorted(required-checked))
        if (str(report.get('verdict', '')).startswith('PASS') and report.get('blocking_findings') == []
                and not drift and not required-checked): row['status'] = 'PASS_REVISION_BOUND_REVIEW'
    except (OSError, ValueError, TypeError, KeyError) as exc: row['error'] = type(exc).__name__
    return row


def stage_evidence(root, stage):
    script, label, doc = STAGES[stage]
    receipt, pin = h.json_source(root, label)
    if receipt.get('stage') != str(stage)+'A': raise ValueError('stage_identity')
    boundary = receipt.get('boundary', {})
    if not isinstance(boundary, dict): raise ValueError('boundary_object_required')
    for key in ('target_access', 'network_access', 'target_commands_executed', 'physical_acceptance', 'flash_approved'):
        if boundary.get(key) is not False: raise ValueError('boundary:'+key)
    if receipt.get('implementation') != h.snapshot(root, script)[1]: raise ValueError('stale_implementation')
    dependencies = receipt.get('analysis_dependencies')
    if not isinstance(dependencies, list) or not dependencies: raise ValueError('dependencies_required')
    if (any(not isinstance(p, dict) for p in dependencies)
            or len(dependencies) != 3 or {p.get('path') for p in dependencies} != set(DEPS[:3])):
        raise ValueError('exact_three_analysis_dependencies_required')
    for source in dependencies:
        if h.snapshot(root, source['path'])[1] != source: raise ValueError('stale_dependency')
    outputs = receipt.get('outputs')
    if not isinstance(outputs, dict): raise ValueError('outputs_object_required')
    if outputs.get(doc) != h.snapshot(root, doc)[1]: raise ValueError('stale_doc')
    sources = receipt.get('static_sources')
    if not isinstance(sources, list) or not sources: raise ValueError('declared_static_sources_required')
    labels = set()
    for source in sources:
        if not isinstance(source, dict) or set(source) != {'path', 'bytes', 'sha256'}:
            raise ValueError('source_pin_required')
        label = source['path']
        if not isinstance(label, str) or label in labels: raise ValueError('unique_source_paths_required')
        labels.add(label)
    return dict(stage=str(stage)+'A', binding=pin, status=receipt.get('status'),
                summary=receipt.get('summary'), declared_sources=sources, acceptance='SAVED_STATIC_AUDIT_ONLY')


def run(root=ROOT, timeout=300, execute=None):
    root = c.local_path(root).resolve(); c.integer(timeout, 'timeout_seconds', 1, 900)
    execute = execute or capture; c.write_doc(root/DOC, DOC_TEXT)
    base = c.local_path(root/'artifacts/verification/stage530a'); base.mkdir(parents=True, exist_ok=True)
    index = 1
    while True:
        work = base/f'run_{index:03d}'
        try: work.mkdir(); break
        except FileExistsError: index += 1
    before = []; missing = []
    for label in INPUTS + REVIEWS:
        try: before.append(h.snapshot(root, label)[1])
        except (OSError, ValueError): missing.append(label)
    result = dict(stage='530A', task_id='T-S530A-CODEX-530STAGE-MASTER-GATE',
                  run_directory=work.relative_to(root).as_posix(), static_sources=before, missing_inputs=missing,
                  status='INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE', pytest_counts=None, gaps=[], stage_audits=[],
                  boundary=dict(target_access=False, network_access=False, target_commands_executed=False,
                                physical_acceptance=False, flash_approved=False), E2='NOT_ACCEPTED',
                  stage_source_drift_since_audit=[])
    captured = {p['path']: p for p in before}
    for stage in STAGES:
        try:
            row = stage_evidence(root, stage); result['stage_audits'].append(row)
            for source in row['declared_sources']:
                actual = h.snapshot(root, source['path'])[1]
                if actual != source:
                    result['stage_source_drift_since_audit'].append(dict(stage=row['stage'], audited=source, current=actual))
                if source['path'] not in captured:
                    before.append(actual); captured[source['path']] = actual
                elif actual != captured[source['path']]: result['gaps'].append('SOURCE_CHANGED_DURING_CAPTURE')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            result['gaps'].append(f'STAGE_{stage}_EVIDENCE:{type(exc).__name__}:{exc}')
    if result['stage_source_drift_since_audit']: result['gaps'].append('SOURCE_DRIFT_SINCE_STAGE_AUDIT')
    result['independent_reviews'] = [reviewed(root, n) for n in STAGES]
    if any(r['status'] != 'PASS_REVISION_BOUND_REVIEW' for r in result['independent_reviews']):
        result['gaps'].append('MISSING_FAILED_OR_STALE_INDEPENDENT_REVIEW')
    if not missing:
        junit = work/'pytest.xml'
        command = [sys.executable, '-m', 'pytest', '-q', '-o', 'addopts=', '-o', 'junit_family=xunit1',
                   *SUITES, '--junitxml='+str(junit)]
        test = execute(command, root, timeout); c.write_json(work/'pytest.json', test); result['pytest'] = test
        try:
            evidence = junit_evidence(junit); result['junit_coverage'] = evidence; result['pytest_counts'] = evidence['counts']
            if any(evidence[k] for k in ('missing_suites', 'unexpected_suites', 'missing_file_attributes')):
                result['gaps'].append('INCOMPLETE_OR_UNEXPECTED_PYTEST_COLLECTION')
        except (OSError, ValueError, ET.ParseError): result['gaps'].append('MISSING_OR_INVALID_JUNIT')
        gate = execute(GATE, root, timeout); c.write_json(work/'repo_gate.json', gate); result['repo_gate'] = gate
        counts = result['pytest_counts'] or {}
        if (test.get('exit_code') != 0 or test.get('timed_out') is not False or counts.get('passed', 0) < 1
                or any(counts.get(k, 0) for k in ('failures', 'errors', 'skipped'))):
            result['gaps'].append('PYTEST_FAILED_OR_INCOMPLETE')
        if gate.get('exit_code') != 0 or gate.get('timed_out') is not False: result['gaps'].append('REPOSITORY_WIRING_GATE_FAILED')
    else: result['gaps'].append('MISSING_INPUTS_NO_CHILD_EXECUTION')
    result['input_drift'] = []
    for source in before:
        try: same = h.snapshot(root, source['path'])[1] == source
        except (OSError, ValueError): same = False
        if not same: result['input_drift'].append(source['path'])
    if result['input_drift']: result['gaps'].append('INPUT_DRIFT_DURING_RUN')
    policy = next((r for r in result['stage_audits'] if r['stage'] == '529A'), {})
    result['repository_artifact_policy'] = dict(status=policy.get('status', 'UNASSESSED'), summary=policy.get('summary'))
    if not result['gaps']:
        result['status'] = ('PASS_LOCAL_TOOLING_AND_SCOPED_ARTIFACT_POLICY' if policy.get('status') == 'PASS_SCOPED_STRUCTURAL_POLICY'
                            else 'VALIDATED_TOOLING_WITH_REPOSITORY_FINDINGS')
    result['physical_acceptance'] = 'NOT_ASSESSED_NO_NEW_HARDWARE_RESULTS'
    result['source_binding_meaning'] = 'Held-file revisions, not authenticated historical native acquisition.'
    result['self_reference'] = 'Final receipt excluded from self-hash and inner pytest; verify after creation.'
    result['outputs'] = {DOC: h.snapshot(root, DOC)[1]}
    c.write_json(work/'result.json', result); c.write_json(root/OUT, result)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=ROOT)
    p.add_argument('--timeout', type=int, default=300); a = p.parse_args(argv)
    result = run(a.root, a.timeout)
    print(json.dumps({k: result[k] for k in ('status', 'pytest_counts', 'repository_artifact_policy', 'gaps')}, sort_keys=True))
    return 0 if result['status'] == 'PASS_LOCAL_TOOLING_AND_SCOPED_ARTIFACT_POLICY' else 1


if __name__ == '__main__': raise SystemExit(main())
