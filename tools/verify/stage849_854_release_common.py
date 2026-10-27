"""Public offline release contracts, distinct from physical acceptance."""
from __future__ import annotations

from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.stage779_822_offline_common import local, read_json, snapshot

STEMS = {
    849: 'stage849a_universal_wa_xc_xw_v22_release_matrix',
    850: 'stage850a_ltu_safe_kit_v22_atpc_and_dfs_guard',
    851: 'stage851a_guarida_tower_v11_gps_sync_and_pb080_pareto',
    852: 'stage852a_1050window_cross_lane_master_scorecard',
    853: 'stage853a_public_git_sync_and_push_v2',
    854: 'stage854a_ground_up_v14_854stage_gate',
}
CODE = {
    n: f'tools/{folder}/{verb}_{stem}.py'
    for n, folder, verb, stem in (
        (849, 'firmware', 'build', STEMS[849]),
        (850, 'firmware', 'build', STEMS[850]),
        (851, 'sim', 'run', STEMS[851]),
        (852, 'verify', 'build', STEMS[852]),
        (853, 'verify', 'verify', STEMS[853]),
        (854, 'verify', 'verify', STEMS[854]),
    )
}
PRIVACY_PATHS = [
    'artifacts/autoresearch/stage901a_provenance_remediation_receipt.json',
    'artifacts/autoresearch/stage902a_full_corpus_provenance_audit.json',
    'artifacts/autoresearch/stage903a_provenance_restoration_registry.json',
    'docs/CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md',
    'docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md',
    'tools/verify/remediate_stage901a_undeclared_provenance_receipts.py',
]


def artifact(stage: int) -> str:
    return f'artifacts/autoresearch/{STEMS[stage]}.json'


def audit_stage(root: Path, stage: int) -> dict:
    """Recheck actual local bytes; pillar presence alone is not acceptance."""
    failures = []
    try:
        data = read_json(root, artifact(stage))
        if data.get('stage') != f'{stage}A':
            failures.append('stage identity')
        allowed = {'INFERRED'} if stage == 851 else {'CONFIRMED'}
        if data.get('status') not in allowed:
            failures.append('offline construction status')
        boundary = data.get('boundary', {})
        for key in ('network_access', 'ssh_executed', 'device_writes', 'flash_approved'):
            if boundary.get(key) is not False:
                failures.append('offline boundary: ' + key)
        if boundary.get('physical_acceptance') != 'UNKNOWN':
            failures.append('physical acceptance must remain UNKNOWN')
        if not audit_stage_receipt_5pillars(data)['compliant']:
            failures.append('five-pillar structure')
        sources = data.get('sources')
        if not isinstance(sources, list) or not sources:
            failures.append('source provenance required')
        else:
            for source in sources:
                current = snapshot(root, source['path'])
                if (current.get('available') is not True or
                        any(source.get(key) != value for key, value in current.items())):
                    failures.append('source drift: ' + source['path'])
        doc = local(root, f'docs/{STEMS[stage].upper()}.md').read_text(encoding='utf-8')
        if (len(doc.splitlines()) >= 180 or doc.count('<!-- doc-head:') != 1
                or doc.count('<!-- /doc-head -->') != 1):
            failures.append('document budget/header')
        for path in (CODE[stage],):
            if not local(root, path).is_file():
                failures.append('missing code: ' + path)
        if data.get('manifest_writer_sha256') and snapshot(
                root, data['manifest_writer_source']).get('sha256') != data['manifest_writer_sha256']:
            failures.append('manifest writer drift')
        if data.get('producer_sha256') and snapshot(root, CODE[stage]).get('sha256') != data['producer_sha256']:
            failures.append('producer drift')
    except (OSError, ValueError, TypeError, KeyError) as exc:
        failures.append(type(exc).__name__ + ': ' + str(exc))
    return {'stage': f'{stage}A', 'compliant': not failures, 'failures': failures}


def publication_paths() -> list[str]:
    paths = ['README.md', 'docs/CURRENT_STATE.md', 'requirements-release-v22.txt',
             'tools/verify/stage849_854_release_common.py',
             'tests/test_stage849a_to_854a_suite.py']
    for n in STEMS:
        paths.extend([CODE[n], artifact(n), f'docs/{STEMS[n].upper()}.md'])
    paths.extend(f'tests/test_stage{n}a.py' for n in range(849, 855))
    return sorted(paths + PRIVACY_PATHS)
