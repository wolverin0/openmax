#!/usr/bin/env python3
"""Reviewable public index audit; publication requires an explicit --publish."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot
from tools.verify.stage849_854_release_common import STEMS, PRIVACY_PATHS, publication_paths
from tools.verify.verify_stage826a_public_git_hygiene_and_push_gate import audit, git

STEM = STEMS[853]
REMOTE = 'https://github.com/wolverin0/openmax.git'
HEADING = '## Stages849A..854A: offline v22 release'
BLOCK = f'''{HEADING}

WA/XC/XW and LTU v22 source manifests, a Guarida v11 GPS/PB080 sensitivity model,
and a 1050-window synthetic scorecard are packaged with explicit acceptance boundaries.
No new radio measurements or native ATPC/DFS/GPS/PB080 acceptance is claimed.
The five-pillar audit checks local wiring and source provenance; external studies remain deferred.
See [release gate](docs/STAGE854A_GROUND_UP_V14_854STAGE_GATE.md) and
[publication gate](docs/STAGE853A_PUBLIC_GIT_SYNC_AND_PUSH_V2.md).
'''


def update_text(text: str, doc: bool = False) -> str:
    text = re.sub(r'(?ms)^' + re.escape(HEADING) + r'\n.*?(?=^## |\Z)', '', text)
    text = re.sub(r'<!-- doc-head:.*?-->',
                  '<!-- doc-head: Source-qualified milestones and offline v22 release through854A -->',
                  text, count=1, flags=re.S)
    block = BLOCK.replace('(docs/', '(') if doc else BLOCK
    result = text.rstrip() + '\n\n' + block
    if len(result.splitlines()) >= 180 or result.count('<!-- doc-head:') != 1:
        raise ValueError('document line/header budget')
    return result


def private_policy(root: Path) -> tuple[Path, list]:
    gitdir = Path(git(root, 'rev-parse', '--absolute-git-dir').decode().strip())
    policy = gitdir / 'stage826a/private_terms.json'
    return gitdir, json.loads(policy.read_text()) if policy.is_file() else []


def check_index(root: Path = ROOT) -> dict:
    gitdir, terms = private_policy(root)
    result, selected, findings = audit(root, private_terms=terms)
    destination = gitdir / 'stage853a'
    destination.mkdir(parents=True, exist_ok=True)
    atomic_write(destination / 'index_audit.json',
                 json.dumps(dict(result=result, selected=selected, findings=findings), indent=2))
    return result


def redact_public_text(text: str, terms: list[str]) -> str:
    """Stable distinct aliases preserve JSON key uniqueness and disclose no identifiers."""
    if re.search(r'PRIVATE_(?:ADDRESS|DEVICE|LABEL)_\d+', text):
        raise ValueError('reserved privacy alias already present in original')
    patterns = [r'\b(?:10\.10\.\d{1,3}\.\d{1,3}|192\.168\.(?:100|200)\.\d{1,3})\b',
                r'\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b']
    for kind, pattern in zip(('ADDRESS', 'DEVICE'), patterns):
        values = sorted(set(re.findall(pattern, text, flags=re.I)))
        mapping = {value: f'PRIVATE_{kind}_{n:03d}' for n, value in enumerate(values, 1)}
        text = re.sub(pattern, lambda match: mapping[match[0]], text, flags=re.I)
    for n, term in enumerate(sorted(set(terms)), 1):
        if len(term) >= 4:
            text = re.sub(r'\b' + re.escape(term) + r'\b', f'PRIVATE_LABEL_{n:03d}', text, flags=re.I)
    return text


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key after public redaction')
        result[key] = value
    return result


def prepare_privacy_derivatives(root: Path) -> list[str]:
    """Repair only known baseline identifiers in the index, preserving local originals."""
    gitdir, terms = private_policy(root)
    _, _, findings = audit(root, private_terms=terms)
    affected = sorted({row['path'] for row in findings})
    if set(affected) - set(PRIVACY_PATHS) or any(row['rule'] not in {
            'operational_address', 'device_identifier', 'private_operator_term'} for row in findings):
        raise ValueError('unexpected sensitive finding requires a scoped review')
    archive = gitdir / 'stage853a/private_originals'
    for label in affected:
        raw = git(root, 'show', ':' + label)
        backup = archive / label
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            atomic_write(backup, raw.decode('utf-8'))
        text = redact_public_text(raw.decode('utf-8'), terms)
        if label.endswith('.json'):
            data = json.loads(text, object_pairs_hook=unique_object)
            data['publication_redaction'] = {
                'state': 'PUBLIC_REDACTED_DERIVATIVE', 'original_retained_locally': True,
                'original_source_bindings': 'require private originals; derivative is not original evidence'}
            text = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
        elif label.endswith('.md'):
            text = re.sub(r'<!-- doc-head:.*?-->',
                          '<!-- doc-head: Historical references with private identifiers redacted for publication -->',
                          text, count=1, flags=re.S)
            text += '\nPublic derivative: private identifiers removed; original evidence retained locally.\n'
            while len(text.splitlines()) >= 180 and '\n\n' in text:
                text = text.replace('\n\n', '\n', 1)
        else:
            text = '# Public derivative: private evidence keys redacted; unmatched inputs fail closed.\n' + text
        oid = git(root, 'hash-object', '-w', '--stdin', input=text.encode('utf-8')).decode().strip()
        git(root, 'update-index', '--cacheinfo', '100644,' + oid + ',' + label)
    return affected


def build(root: Path = ROOT) -> dict:
    hygiene = check_index(root)
    derivatives = []
    if not hygiene['compliant']:
        derivatives = prepare_privacy_derivatives(root)
        hygiene = check_index(root)
    gitdir, _ = private_policy(root)
    derivatives = sorted(set(derivatives) | {
        label for label in PRIVACY_PATHS
        if (gitdir / 'stage853a/private_originals' / label).is_file()})
    if not hygiene['compliant']:
        raise ValueError('public index hygiene failed; details retained in Git metadata')
    for label in ('README.md', 'docs/CURRENT_STATE.md'):
        path = root / label
        atomic_write(path, update_text(path.read_text(encoding='utf-8'), label.startswith('docs/')))
    data = receipt(853, 'Public Git sync and push v2',
                   [snapshot(root, 'tools/verify/' + Path(__file__).name),
                    snapshot(root, 'tools/verify/stage849_854_release_common.py')])
    data.update(index_hygiene={'compliant': True, 'findings': 0,
                              'ignore_probes_passed': all(hygiene['ignore_probes'].values()),
                              'scope': 'current indexed blobs; final publication rechecks selected bytes'},
                publication={'state': 'PREPARED', 'push_executed': False,
                             'receipt_location': 'local Git metadata: stage853a/push.json'},
                history_rewritten=False,
                public_privacy_derivatives=derivatives,
                physical_acceptance='UNKNOWN')
    return save(root, STEM, data,
                'Prepared release; default execution audits the index and updates the two public reading routes.\n'
                'Publication command: `python tools/verify/verify_stage853a_public_git_sync_and_push_v2.py --publish`.\n'
                'Only the explicit849A..854A source/doc/test/receipt selection is staged.\n'
                'Unrelated local edits are preserved; no broad git add is used.\n'
                'The actual index is rescanned for restricted paths, binary dumps and sensitive content before commit.\n'
                'Repository five-pillar gate and release854A receipt are mandatory.\n'
                'Known baseline identifiers are redacted in public derivatives; private originals remain local.\n'
                'Derivative source bindings require those originals and are not recertified as original evidence.\n'
                'The push result and exact remote hash are stored in local Git metadata after publication.\n'
                'This committed preparation record never certifies its own future push.\n'
                'No history rewrite and no physical operation. Physical acceptance: UNKNOWN.\n')


def stage_selection(root: Path, paths: list[str]) -> None:
    staged = set(git(root, 'diff', '--cached', '--name-only', '-z').decode().split('\0')) - {''}
    if staged - set(paths):
        raise ValueError('unrelated staged work; refusing to include it')
    for label in paths:
        path = root / label
        if not path.is_file() or path.is_symlink():
            raise ValueError('required regular publication source missing: ' + label)
        blob = path.read_bytes()
        if label in PRIVACY_PATHS:
            # The reviewed index derivative is public; the working original stays local.
            continue
        if label in ('README.md', 'docs/CURRENT_STATE.md'):
            # Preserve pre-existing working edits while publishing only our document delta.
            base = git(root, 'show', 'HEAD:' + label).decode('utf-8')
            blob = update_text(base, label.startswith('docs/')).encode('utf-8')
        oid = git(root, 'hash-object', '-w', '--stdin', input=blob).decode().strip()
        git(root, 'update-index', '--add', '--cacheinfo', '100644,' + oid + ',' + label)


def assert_tested_index(root: Path, gate: dict) -> None:
    for source in gate['verification_sources'] + gate['sources']:
        blob = git(root, 'show', ':' + source['path'])
        if hashlib.sha256(blob).hexdigest() != source['sha256']:
            raise ValueError('indexed tested revision drift: ' + source['path'])


def publish(root: Path = ROOT) -> dict:
    from tools.verify.enforce_5pillar_research_gate import audit_repo_deterministic_gates
    from tools.verify.stage849_854_release_common import artifact, audit_stage
    from tools.verify.stage779_822_offline_common import read_json
    if git(root, 'branch', '--show-current').decode().strip() != 'main':
        raise ValueError('publication requires main')
    if git(root, 'remote', 'get-url', 'origin').decode().strip() != REMOTE:
        raise ValueError('unexpected origin URL')
    if not audit_repo_deterministic_gates(root)['compliant']:
        raise ValueError('repository five-pillar gate failed')
    for n in range(849, 855):
        if not audit_stage(root, n)['compliant']:
            raise ValueError(f'{n}A receipt acceptance failed')
    gate = read_json(root, artifact(854))
    if gate.get('all_gates_passed') is not True or gate.get('pytest', {}).get('returncode') != 0:
        raise ValueError('854A executed pytest acceptance required')
    paths = publication_paths()
    # The gate pins these source/test bytes; stale test success cannot authorize a new revision.
    for source in gate['verification_sources']:
        if snapshot(root, source['path']) != source:
            raise ValueError('tested revision drift: ' + source['path'])
    head = git(root, 'rev-parse', 'HEAD').decode().strip()
    remote = git(root, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    if remote != head:
        raise ValueError('remote main changed; no automatic rebase or force push')
    stage_selection(root, paths)
    # Compare actual staged blobs to the revision tested by854A, not merely working files.
    assert_tested_index(root, gate)
    hygiene = check_index(root)
    if not hygiene['compliant']:
        raise ValueError('selected index failed privacy; see local index_audit.json')
    gitdir, _ = private_policy(root)
    hooks = gitdir / 'stage853a/hooks'
    hooks.mkdir(parents=True, exist_ok=True)
    # Retain deterministic gates without invoking unrelated memory-ingestion side effects.
    atomic_write(hooks / 'pre-commit', '#!/bin/sh\nset -eu\n'
                 'python tools/verify/enforce_5pillar_research_gate.py --check-repo\n'
                 'python tools/verify/verify_stage853a_public_git_sync_and_push_v2.py --check-index\n'
                 'python tools/verify/verify_stage853a_public_git_sync_and_push_v2.py --check-tested-index\n')
    subprocess.run(['git', '-c', 'core.hooksPath=' + str(hooks), 'commit', '-m',
                    'feat(openmax): Stages 849A-854A offline v22 kits and synthetic scorecard'],
                   cwd=root, check=True)
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    state = {'stage': '853A', 'commit': commit, 'push_verified': False,
             'radio_access': False, 'history_rewritten': False}
    atomic_write(gitdir / 'stage853a/push.json', json.dumps(state, indent=2))
    subprocess.run(['git', 'push', 'origin', 'main'], cwd=root, check=True)
    actual = git(root, 'ls-remote', 'origin', 'refs/heads/main').decode().split()[0]
    if actual != commit:
        raise RuntimeError('push remote hash mismatch')
    state.update(remote_main=actual, push_verified=True)
    atomic_write(gitdir / 'stage853a/push.json', json.dumps(state, indent=2))
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--publish', action='store_true')
    group.add_argument('--check-index', action='store_true')
    group.add_argument('--check-tested-index', action='store_true')
    args = parser.parse_args()
    if args.publish:
        print(json.dumps(publish(), indent=2))
    elif args.check_tested_index:
        from tools.verify.stage779_822_offline_common import read_json
        from tools.verify.stage849_854_release_common import artifact
        assert_tested_index(ROOT, read_json(ROOT, artifact(854)))
        print('tested index matches854A')
    elif args.check_index:
        result = check_index()
        print(json.dumps({'compliant': result['compliant'], 'findings': result['findings_by_rule']}))
        return 0 if result['compliant'] else 1
    else:
        print(json.dumps(build()['publication']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
