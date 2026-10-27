"""Local packaging/evidence utilities; never import or execute radio producers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PILLARS = (
    'pillar_a_ground_up_re_and_knob_catalog',
    'pillar_b_hyperresearch_and_scholar_reactor',
    'pillar_c_karpathy_autoresearch_and_watchdog',
    'pillar_d_scientific_pareto_validation',
    'pillar_e_memory_master_claim_id',
)
BOUNDARY = dict(network_access=False, ssh_executed=False, producer_execution=False,
                device_writes=False, flash_approved=False, physical_acceptance='UNKNOWN')


def local(root: Path, label: str) -> Path:
    if not label or '\\' in label or ':' in label or label.startswith('/') or any(
        p in ('', '.', '..') for p in label.split('/')
    ):
        raise ValueError('repository-relative path required')
    if str(root.resolve()).startswith('\\\\'):
        raise ValueError('network repository paths forbidden')
    path = (root / label).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('path escapes repository')
    return path


def snapshot(root: Path, label: str) -> dict:
    path = local(root, label)
    if not path.is_file():
        return dict(path=label, available=False)
    blob = path.read_bytes()
    return dict(path=label, available=True, bytes=len(blob),
                sha256=hashlib.sha256(blob).hexdigest())


def read_json(root: Path, label: str) -> dict:
    def reject(value):
        raise ValueError('nonfinite JSON: ' + value)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    result = json.loads(local(root, label).read_text(encoding='utf-8-sig'),
                        parse_constant=reject, object_pairs_hook=unique)
    if not isinstance(result, dict):
        raise ValueError('JSON object required')
    return result


def receipt(stage: int, title: str, sources: list[dict]) -> dict:
    return dict(schema_version='1.0.0', stage=f'{stage}A', title=title,
                status='CONFIRMED', claim_scope='offline software/package construction only',
                attribution=['external controller'], boundary=dict(BOUNDARY), sources=sources,
                five_pillar_compliance=dict(zip(PILLARS, [
                    {'status': 'LOCAL_REFERENCE_ONLY', 'sources': sources},
                    {'status': 'DEFERRED_OFFLINE', 'scholar_executed': False},
                    {'status': 'PLAN_ONLY', 'protocol': 'A1 -> B1 -> A2 -> B2',
                     'watchdog_non_dfs_s': 45, 'watchdog_dfs_s': 120, 'live_windows_executed': 0},
                    {'status': 'OFFLINE_ANALYSIS', 'hardware_validation': 'UNKNOWN'},
                    {'status': 'LOCAL_LEDGER_ONLY', 'scope': 'project:futuramax',
                     'ingested': False, 'claim_key': f'stage{stage}a-offline'},
                ])))


def save(root: Path, stem: str, data: dict, body: str) -> dict:
    from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
    data['five_pillar_audit'] = audit_stage_receipt_5pillars(data)
    if not data['five_pillar_audit']['compliant']:
        raise ValueError('five-pillar structural audit failed')
    doc = f'<!-- doc-head: {data["stage"]} offline evidence and acceptance boundaries -->\n<!-- /doc-head -->\n\n# {data["title"]}\n\n' + body
    if len(doc.splitlines()) >= 180 or doc.count('<!-- doc-head:') != 1:
        raise ValueError('document budget')
    for label, content in [
        (f'artifacts/autoresearch/{stem}.json', json.dumps(data, indent=2, allow_nan=False) + '\n'),
        (f'docs/{stem.upper()}.md', doc),
    ]:
        path = local(root, label); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='\n')
    return data


def package(root: Path, label: str, sources: list[dict]) -> dict:
    """Byte-identical ZIP for identical inputs; verify bytes against their snapshots."""
    path = local(root, label); path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as archive:
        for source in sorted(sources, key=lambda x: x['path']):
            if not source['available']:
                continue
            blob = local(root, source['path']).read_bytes()
            if hashlib.sha256(blob).hexdigest() != source['sha256']:
                raise ValueError('source changed while packaging')
            archive.writestr(zipfile.ZipInfo(source['path'], (1980, 1, 1, 0, 0, 0)), blob)
    return snapshot(root, label)


def pareto(rows: list[dict], objectives: tuple[str, ...]) -> list[dict]:
    return [a for a in rows if not any(
        all(b[k] <= a[k] for k in objectives) and any(b[k] < a[k] for k in objectives)
        for b in rows)]


def verify_stage(root: Path, stage: int, script: str, stem: str, test: str) -> dict:
    """Check existing artifacts and provenance; never run a stage producer."""
    failures = []
    labels = [script, test, f'docs/{stem.upper()}.md']
    sources = [snapshot(root, label) for label in labels]
    for source in sources:
        if not source['available']:
            failures.append('missing ' + source['path'])
    doc = local(root, labels[2])
    text = doc.read_text(encoding='utf-8-sig') if doc.is_file() else ''
    if len(text.splitlines()) >= 180 or text.count('<!-- doc-head:') != 1:
        failures.append('document budget/header')
    evidence_scope = 'SOURCE_ONLY_NOT_EXECUTED' if stage == 779 else 'OFFLINE_ARTIFACT'
    # Stage779 is a pre-existing live runner, explicitly outside this lane's execution scope.
    if stage != 779:
        label = f'artifacts/autoresearch/{stem}.json'
        sources.append(snapshot(root, label))
        try:
            data = read_json(root, label)
            if str(data.get('stage', '')).removeprefix('STAGE-') != f'{stage}A':
                failures.append('stage identity')
            if data.get('status') not in ('CONFIRMED', 'INFERRED', 'PREPARED', 'PREPARED_WITH_GAPS'):
                failures.append('receipt status')
            if stage == 780 and data.get('execution_mode') != 'OFFLINE_SIMULATION':
                failures.append('780A must be qualified as offline simulation')
            from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
            if not audit_stage_receipt_5pillars(data)['compliant']:
                failures.append('five-pillar receipt structure')
            boundaries = [data.get('boundary', {})]
            for boundary in boundaries:
                if not isinstance(boundary, dict):
                    failures.append('invalid offline boundary'); continue
                if boundary.get('network_access') is not False:
                    failures.append('explicit offline network boundary required')
                for key in ('network_access', 'ssh_executed', 'device_writes', 'live_devices_touched',
                            'radio_commands_executed', 'flash_approved'):
                    if boundary.get(key, False) is not False:
                        failures.append('incompatible offline boundary: ' + key)
                if boundary.get('physical_acceptance', 'UNKNOWN') not in ('UNKNOWN', False, None):
                    failures.append('incompatible physical acceptance')
            if data.get('physical_acceptance', 'UNKNOWN') not in ('UNKNOWN', False, None):
                failures.append('incompatible physical acceptance')
            provenance = (data.get('sources', []) + data.get('source_evidence', [])
                          + data.get('code_sources', []) + data.get('package_files', []))
            for source in provenance:
                if not isinstance(source, dict) or not source.get('path'):
                    failures.append('invalid source record'); continue
                current = snapshot(root, source['path'])
                expected_available = source.get('available', source.get('status') != 'MISSING')
                if current.get('available') != expected_available:
                    failures.append('source availability changed: ' + source['path'])
                if expected_available and not re.fullmatch('[0-9a-f]{64}', str(source.get('sha256', ''))):
                    failures.append('source hash required: ' + source['path'])
                if source.get('sha256') and current.get('sha256') != source['sha256']:
                    failures.append('source hash mismatch: ' + source['path'])
            for module in data.get('module_provenance', []):
                if (not module.get('matches_saved_re') or
                        snapshot(root, module['path']).get('sha256') != module.get('sha256')):
                    failures.append('module provenance mismatch: ' + module['path'])
            helper = data.get('helper_script')
            if helper and snapshot(root, helper).get('sha256') != data.get('helper_sha256'):
                failures.append('helper hash mismatch')
            for image in data.get('images', []):
                if snapshot(root, image['path']).get('sha256') != image['sha256']:
                    failures.append('image hash mismatch: ' + image['path'])
                if snapshot(root, image['source']).get('sha256') != image['source_sha256']:
                    failures.append('image input hash mismatch: ' + image['source'])
            bundle = data.get('package')
            if isinstance(bundle, dict) and bundle.get('sha256'):
                if snapshot(root, bundle['path']).get('sha256') != bundle['sha256']:
                    failures.append('package hash mismatch')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            failures.append(type(exc).__name__ + ': ' + str(exc))
    return dict(stage=f'{stage}A', compliant=not failures, failures=failures,
                evidence_scope=evidence_scope, doc_lines=len(text.splitlines()),
                doc_heads=text.count('<!-- doc-head:'), files=sources)
