#!/usr/bin/env python3
"""Inventory Git privately and quarantine only proven ignored atomic-report leftovers.

No Git index mutation or irreversible deletion is provided. Ambiguous files are
retained. Detailed filenames, contents and restoration maps remain in Git metadata.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot

STEM = 'stage987a_repo_status_and_orphan_artifacts'
SELF = 'tools/verify/' + Path(__file__).name
TEST = 'tests/test_stage987a_repo_hygiene.py'
PRIVATE = 'stage983_988/stage987a'
ARTIFACT_ROOTS = ('artifacts/autoresearch/', 'artifacts/verification/')
TEMP_NAME = re.compile(r'(?P<stage>stage\d{2,5}[a-z])_[A-Za-z0-9_.-]+\.json\.[A-Za-z0-9_-]{6,32}\.tmp')
FORBIDDEN = re.compile(r'(?i)(?:capture|raw|window|measurement|pcap|original|snapshot|backup|payload|firmware|image)')
RAW_KEYS = frozenset(('stdout', 'stderr', 'raw_bytes', 'raw_capture', 'native_capture',
                      'pcap', 'packet_bytes', 'firmware_bytes', 'image_bytes'))
MIN_AGE_S = 24 * 60 * 60
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_MOVE_FILES = 64
MAX_MOVE_BYTES = 32 * 1024 * 1024
MAX_INVENTORY_BYTES = 64 * 1024 * 1024
MAX_REFERENCE_BYTES = 256 * 1024 * 1024


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def checked(path: Path, boundary: Path) -> Path:
    path, boundary = Path(path).absolute(), Path(boundary).absolute()
    if str(path).replace('/', '\\').startswith('\\\\') or not path.is_relative_to(boundary):
        raise ValueError('path outside explicit local boundary')
    for node in (path, *path.parents):
        try:
            metadata = node.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(metadata.st_mode) or getattr(metadata, 'st_file_attributes', 0) & 0x400:
            raise ValueError('symlink or reparse point forbidden')
        if node == boundary:
            break
    if not path.resolve().is_relative_to(boundary.resolve()):
        raise ValueError('resolved path outside explicit boundary')
    return path


def repo_path(root: Path, label: str) -> Path:
    if (not isinstance(label, str) or not label or '\\' in label or ':' in label
            or label.startswith('/') or any(x in ('', '.', '..') for x in label.split('/'))):
        raise ValueError('safe repository-relative path required')
    return checked(root / label, root)


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError('Git inventory command failed: ' + args[0])
    if len(result.stdout) > MAX_INVENTORY_BYTES:
        raise ValueError('Git inventory exceeds declared bound')
    return result.stdout


def status_rows(blob: bytes) -> list[dict]:
    items, rows, index = blob.split(b'\0'), [], 0
    while index < len(items):
        item = items[index]
        index += 1
        if not item:
            continue
        if len(item) < 4 or item[2:3] != b' ':
            raise ValueError('malformed porcelain inventory')
        code, label = item[:2].decode('ascii'), item[3:].decode('utf-8')
        row = {'status': code, 'path': label}
        if 'R' in code or 'C' in code:
            if index >= len(items) or not items[index]:
                raise ValueError('missing rename/copy source')
            row['original_path'] = items[index].decode('utf-8')
            index += 1
        rows.append(row)
    return rows


def contains_raw(node) -> bool:
    if isinstance(node, dict):
        return any(key.lower() in RAW_KEYS or contains_raw(value) for key, value in node.items())
    return isinstance(node, list) and any(contains_raw(value) for value in node)


def summary_json(blob: bytes) -> dict:
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('duplicate summary field')
            value[key] = item
        return value
    def finite(text):
        value = float(text)
        if not math.isfinite(value):
            raise ValueError('nonfinite summary number')
        return value
    def invalid(text):
        raise ValueError('nonfinite summary literal')
    value = json.loads(blob.decode('utf-8'), object_pairs_hook=pairs, parse_float=finite,
                       parse_constant=invalid)
    if not isinstance(value, dict):
        raise ValueError('summary object required')
    return value


@contextmanager
def exclusive_read(path: Path):
    """Deny concurrent writers on Windows; use a nonblocking advisory lock on POSIX."""
    if os.name == 'nt':
        import ctypes
        import msvcrt
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        create = kernel.CreateFileW
        create.argtypes = (wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                           wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE)
        create.restype = wintypes.HANDLE
        # Sharing DELETE permits our verified rename; sharing READ/WRITE is denied.
        handle = create(str(path), 0x80000000, 0x4, None, 3, 0x00200080, None)
        if handle == ctypes.c_void_p(-1).value:
            raise OSError(ctypes.get_last_error(), 'exclusive candidate read unavailable')
        try:
            fd = msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
        except BaseException:
            kernel.CloseHandle(handle)
            raise
        with os.fdopen(fd, 'rb') as stream:
            yield stream
    else:
        import fcntl
        flags = os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0)
        with os.fdopen(os.open(path, flags), 'rb') as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield stream
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def candidate(root: Path, label: str, *, ignored: set[str], tracked: set[str], now_s: float) -> dict:
    """A filename alone never proves orphanhood; content and references follow."""
    row = {'path': label, 'eligible': False, 'reason': 'not_allowed_atomic_report_temp'}
    name = PurePosixPath(label).name
    match = TEMP_NAME.fullmatch(name)
    if (not label.startswith(ARTIFACT_ROOTS) or not match or FORBIDDEN.search(label)):
        return row
    if label in tracked or label not in ignored:
        row['reason'] = 'tracked_or_nonignored_user_file'
        return row
    try:
        path = repo_path(root, label)
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise ValueError('regular single-link candidate required')
        if not 0 < metadata.st_size <= MAX_FILE_BYTES:
            raise ValueError('candidate size outside bound')
        if now_s - metadata.st_mtime < MIN_AGE_S:
            row['reason'] = 'younger_than_24h_or_future_timestamp'
            return row
        with exclusive_read(path) as stream:
            current = os.fstat(stream.fileno())
            blob = stream.read(MAX_FILE_BYTES + 1)
            if (current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns) != (
                    metadata.st_dev, metadata.st_ino, metadata.st_size, metadata.st_mtime_ns):
                raise ValueError('candidate changed during inspection')
        value = summary_json(blob)
        expected_stage = match['stage'].upper().removeprefix('STAGE')
        declared = str(value.get('stage', '')).upper().replace('STAGE ', '').replace('STAGE-', '')
        if not isinstance(value, dict) or not value.get('schema_version') or declared != expected_stage or contains_raw(value):
            raise ValueError('not a recognized generated summary receipt')
        intended = path.with_name(name.rsplit('.', 2)[0])
        checked(intended, root)
        if (not intended.is_file() or intended.stat().st_mtime_ns < metadata.st_mtime_ns
                or summary_json(intended.read_bytes()).get('stage') != value['stage']):
            row['reason'] = 'newer_completed_summary_not_available'
            return row
        row.update(eligible=True, reason='awaiting_complete_reference_scan', bytes=len(blob),
                   sha256=sha(blob), mtime_ns=metadata.st_mtime_ns,
                   device=metadata.st_dev, inode=metadata.st_ino)
    except (OSError, ValueError, TypeError, UnicodeError, AttributeError):
        row['reason'] = 'unclassifiable_linked_busy_or_changed_candidate'
    return row


def reference_scan(root: Path, rows: list[dict], labels: set[str]) -> tuple[bool, dict[str, bool]]:
    wanted = {row['path']: (row['path'].encode(), PurePosixPath(row['path']).name.encode())
              for row in rows if row['eligible']}
    found = dict.fromkeys(wanted, False)
    if not wanted:
        return True, found
    used = 0
    for label in sorted(labels - set(wanted)):
        if label.startswith('.git/'):
            continue
        try:
            path = repo_path(root, label)
            if path.suffix.lower() not in ('.py', '.sh', '.md', '.json', '.yaml', '.yml', '.toml', '.txt', '.csv'):
                continue
            metadata = path.lstat()
            if not stat.S_ISREG(metadata.st_mode):
                continue
            if metadata.st_size > MAX_FILE_BYTES or used + metadata.st_size > MAX_REFERENCE_BYTES:
                return False, found
            blob = path.read_bytes()
            used += len(blob)
            for name, needles in wanted.items():
                if any(needle in blob for needle in needles):
                    found[name] = True
        except (OSError, ValueError):
            return False, found
    return True, found


def apply_quarantine(root: Path, run_dir: Path, rows: list[dict], *, move=os.rename) -> dict:
    """Revalidate each candidate and retain a durable, reversible move journal."""
    boundary = checked(run_dir, run_dir.parent)
    destination = checked(boundary / 'quarantine', boundary)
    destination.mkdir(parents=True, exist_ok=True)
    journal = boundary / 'restore_map.json'
    moved, failed, restored = [], 0, 0
    atomic_write(journal, json.dumps({'state': 'PLANNED', 'moves': []}, indent=2))
    if len(rows) > MAX_MOVE_FILES or sum(row['bytes'] for row in rows) > MAX_MOVE_BYTES:
        raise ValueError('quarantine batch exceeds declared bounds')
    try:
        for row in rows:
            tracked_blob = git(root, 'ls-files', '-z')
            ignored_blob = git(root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z')
            others_blob = git(root, 'ls-files', '--others', '--exclude-standard', '-z')
            tracked = {value.decode('utf-8') for value in tracked_blob.split(b'\0') if value}
            ignored = {value.decode('utf-8') for value in ignored_blob.split(b'\0') if value}
            others = {value.decode('utf-8') for value in others_blob.split(b'\0') if value}
            fresh = candidate(root, row['path'], ignored=ignored, tracked=tracked, now_s=time.time())
            if not fresh['eligible'] or any(fresh.get(key) != row.get(key) for key in (
                    'bytes', 'sha256', 'mtime_ns', 'device', 'inode')):
                raise ValueError('orphan proof no longer matches current candidate')
            complete, referenced = reference_scan(root, [fresh], tracked | others | {
                label for label in ignored if label.startswith(ARTIFACT_ROOTS)})
            if not complete or referenced.get(row['path'], True):
                raise ValueError('current reference inventory does not authorize move')
            source = repo_path(root, row['path'])
            target = checked(destination / (uuid.uuid4().hex + '.orphan'), boundary)
            if target.exists():
                raise ValueError('quarantine target unexpectedly exists')
            with exclusive_read(source) as stream:
                metadata = os.fstat(stream.fileno())
                blob = stream.read(MAX_FILE_BYTES + 1)
                if ((metadata.st_dev, metadata.st_ino, metadata.st_mtime_ns, metadata.st_size, metadata.st_nlink)
                        != (row['device'], row['inode'], row['mtime_ns'], row['bytes'], 1)
                        or sha(blob) != row['sha256']):
                    raise ValueError('candidate changed after private plan')
                current = source.lstat()
                if (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino):
                    raise ValueError('candidate path identity changed')
                item = dict(original_path=row['path'], quarantine_path=target.relative_to(boundary).as_posix(),
                            sha256=row['sha256'], bytes=row['bytes'])
                atomic_write(journal, json.dumps({'state': 'MOVING', 'moves': moved, 'pending': item}, indent=2))
                move(source, target)
                moved.append(item)
                actual = target.lstat()
                stream.seek(0)
                if ((actual.st_dev, actual.st_ino) != (metadata.st_dev, metadata.st_ino)
                        or sha(stream.read(MAX_FILE_BYTES + 1)) != row['sha256']):
                    raise ValueError('quarantine move verification failed')
                atomic_write(journal, json.dumps({'state': 'MOVING', 'moves': moved}, indent=2))
        state = 'QUARANTINED' if moved else 'NO_PROVEN_ORPHANS'
    except (OSError, ValueError):
        failed = 1
        state = 'FAILED_ROLLED_BACK'
        for item in reversed(moved):
            try:
                source = checked(boundary / item['quarantine_path'], boundary)
                target = repo_path(root, item['original_path'])
                if target.exists() or sha(source.read_bytes()) != item['sha256']:
                    raise ValueError('restoration target occupied or changed')
                os.rename(source, target)
                if sha(target.read_bytes()) != item['sha256']:
                    raise ValueError('restored bytes differ')
                restored += 1
            except (OSError, ValueError):
                state = 'ROLLBACK_FAILED'
    atomic_write(journal, json.dumps({'state': state, 'moves': moved, 'restored_after_failure': restored}, indent=2))
    return {'transaction_state': state, 'quarantined': len(moved) if not failed else len(moved)-restored,
            'failed': failed, 'restored_after_failure': restored, 'restore_map_retained': True,
            'complete': not failed}


def build(root: Path = ROOT, *, quarantine: bool = False, now_s: float | None = None) -> dict:
    root = checked(Path(root).resolve(), Path(root).resolve())
    if type(quarantine) is not bool:
        raise ValueError('explicit boolean quarantine required')
    labels = (SELF, TEST, 'tools/verify/stage779_822_offline_common.py')
    source_pins = [snapshot(root, label) for label in labels]
    if not all(source['available'] for source in source_pins):
        raise ValueError('mandatory audit source or test missing')
    if source_pins[0]['sha256'] != sha(Path(__file__).read_bytes()):
        raise ValueError('executing audit source differs from declared checkout source')
    top = Path(git(root, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
    if top != root:
        raise ValueError('exact Git checkout root required')
    gitdir = Path(git(root, 'rev-parse', '--absolute-git-dir').decode().strip()).resolve()
    private_base = checked(gitdir / PRIVATE, gitdir)
    run_dir = checked(private_base / 'runs' / uuid.uuid4().hex, gitdir)
    run_dir.mkdir(parents=True)
    status_blob = git(root, 'status', '--porcelain=v1', '-z', '--untracked-files=all')
    index_blob = git(root, 'ls-files', '--stage', '-z')
    ignored_blob = git(root, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z')
    others_blob = git(root, 'ls-files', '--others', '--exclude-standard', '-z')
    for name, blob in [('git_status_porcelain.z', status_blob), ('git_index.z', index_blob),
                       ('git_ignored.z', ignored_blob), ('git_untracked.z', others_blob)]:
        (run_dir / name).write_bytes(blob)
    rows = status_rows(status_blob)
    ignored = {label.decode('utf-8') for label in ignored_blob.split(b'\0') if label}
    tracked = {entry.split(b'\t', 1)[1].decode('utf-8') for entry in index_blob.split(b'\0') if entry}
    others = {label.decode('utf-8') for label in others_blob.split(b'\0') if label}
    now_s = time.time() if now_s is None else now_s
    candidates = [candidate(root, label, ignored=ignored, tracked=tracked, now_s=now_s)
                  for label in sorted(ignored | tracked | others) if label.endswith('.tmp') and label.startswith(ARTIFACT_ROOTS)]
    references = tracked | others | {label for label in ignored if label.startswith(ARTIFACT_ROOTS)}
    scanned, found = reference_scan(root, candidates, references)
    proven = []
    for row in candidates:
        if row['eligible']:
            row['reason'] = 'referenced_temporary' if found.get(row['path']) else 'proven_ignored_atomic_summary_orphan' if scanned else 'reference_scan_incomplete'
            row['eligible'] = scanned and not found.get(row['path'], False)
        if row['eligible']:
            proven.append(row)
    inventory = {'git_status': rows, 'tracked_paths': sorted(tracked), 'ignored_paths': sorted(ignored),
                 'untracked_paths': sorted(others), 'candidates': candidates, 'reference_scan_complete': scanned}
    atomic_write(run_dir / 'inventory.json', json.dumps(inventory, indent=2))
    cleanup = {'mode': 'QUARANTINE' if quarantine else 'AUDIT_ONLY', 'proven_orphans': len(proven),
               'retained_candidates': len(candidates)-len(proven), 'quarantined': 0, 'failed': 0,
               'restored_after_failure': 0, 'irreversible_deletions': 0,
               'tracked_or_user_files_moved': 0, 'all_moves_within_bounds': True,
               'restore_map_retained': True, 'complete': True, 'transaction_state': 'NOT_REQUESTED'}
    if quarantine:
        cleanup.update(apply_quarantine(root, run_dir, proven))
    else:
        atomic_write(run_dir / 'restore_map.json', json.dumps({'state': 'NOT_REQUESTED', 'moves': []}))
    unchanged = index_blob == git(root, 'ls-files', '--stage', '-z')
    audit = {'complete': True, 'index_unchanged': unchanged,
             'head': git(root, 'rev-parse', 'HEAD').decode().strip(),
             'branch': git(root, 'branch', '--show-current').decode().strip(),
             'status_counts': {'staged': sum(row['status'][0] not in (' ', '?', '!') for row in rows),
                               'unstaged': sum(row['status'][1] not in (' ', '?', '!') for row in rows),
                               'untracked': len(others), 'ignored': len(ignored)},
             'tracked_index_count': len(tracked), 'index_signature_sha256': sha(index_blob)}
    evidence = []
    for path in sorted(run_dir.iterdir()):
        if path.is_file():
            blob = path.read_bytes()
            evidence.append({'path': path.relative_to(gitdir).as_posix(), 'bytes': len(blob), 'sha256': sha(blob)})
    source_unchanged = source_pins == [snapshot(root, label) for label in labels]
    data = receipt(987, 'Private Git status audit and reversible orphan quarantine', source_pins)
    passed = unchanged and cleanup['complete'] and source_unchanged
    data.update(status='CONFIRMED' if passed else 'FAILED', all_gates_passed=passed,
                evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                provenance_scope='local software inventory and disposable-fixture verification; no native hardware evidence',
                physical_acceptance='UNKNOWN', audit=audit, cleanup=cleanup,
                source_revision_unchanged=source_unchanged,
                candidate_reason_counts=dict(Counter(row['reason'] for row in candidates)),
                private_evidence=evidence, private_inventory_public_contents_emitted=False,
                private_evidence_available_to_public_checkout=False, unrelated_dirty_work_preserved=True)
    return save(root, STEM, data,
                'Git status, index, untracked and ignored inventories are retained in local Git metadata.\n'
                'The public record contains aggregate counts and private inventory hashes only.\n'
                'Default execution audits only; --quarantine authorizes reversible moves of proven ignored report temporaries.\n'
                'Eligibility requires a generated stage JSON temporary name, age of at least24h, single-link regular file,\n'
                'bounded size, exclusive reader, recognizable summary content and a complete negative reference scan.\n'
                'A newer completed summary must already exist; orphan proof and references are rechecked before each move.\n'
                'Raw captures, firmware, images, backups, tracked files and nonignored user work are never candidates.\n'
                'Every move is revalidated, hash checked and journaled; a failed batch attempts reverse-order restoration.\n'
                'There is no delete, reset, clean, stash, Git index mutation, network or device operation.\n'
                f"Proven orphans: {len(proven)}; quarantined: {cleanup['quarantined']}; state: {cleanup['transaction_state']}.\n"
                'Zero proven orphans is an explicit no-op, not a claim that unrelated work was removed.\n'
                'Private inventory bindings cannot be replayed from the public checkout.\n'
                'Physical acceptance: UNKNOWN.\n')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--quarantine', action='store_true')
    args = parser.parse_args(argv)
    data = build(args.root, quarantine=args.quarantine)
    print(json.dumps({'stage': '987A', 'all_gates_passed': data['all_gates_passed'],
                      'audit': data['audit'], 'cleanup': data['cleanup']}, indent=2))
    return 0 if data['all_gates_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
