"""Offline tester-bundle evidence checks. Never contacts or configures a target."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import struct
import subprocess
import sys
import tempfile
import tarfile
import threading
import time

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.firmware import preflight_validate_user_board_info as board
from tools.firmware.verify_all_openmax_kit_checksums_and_headers import inspect_image, trailers
from tools.re import ground_up_release_common as common

OUT = 'artifacts/autoresearch/stage356a_tester_bundle_verifier.json'
DOC = 'docs/STAGE356A_TESTER_BUNDLE_VERIFIER.md'
TOOL_ID = 'OPENMAX_TESTER_BUNDLE_DATA_ONLY_VERIFIER'
PARTITIONS = ('mtd0', 'mtd1', 'mtd4', 'mtd5')
MAX_JSON = 256 * 1024
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_AGE = 150.
MAX_SKEW = 5.
WA_PAYLOAD_CAP = 0xf60000
MAX_TAR = 8 * 1024 * 1024
BOUNDARY = dict(target_access=False, network_access=False, target_commands_executed=False,
                flash_approved=False, physical_acceptance=False, zero_brick_guarantee=False,
                trust_is_signature_or_hardware_authentication=False)


class BundleError(ValueError):
    """Errors are fixed codes, never submitted data, paths or credentials."""


def require(ok, code):
    if not ok:
        raise BundleError(code)


def object_fields(value, allowed, required=()):
    require(type(value) is dict, 'OBJECT_REQUIRED')
    require(set(value) <= set(allowed) and set(required) <= set(value), 'SCHEMA_FIELDS')
    return value


def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None, 'SHA256_REQUIRED')
    return value


def number(value, low=0., high=1e12):
    try:
        return common.finite(value, 'bounded_number', low, high)
    except (ValueError, OverflowError) as exc:
        raise BundleError('FINITE_BOUNDED_NUMBER_REQUIRED') from exc


def uint(value, maximum=2**64-1):
    require(type(value) is int and 0 <= value <= maximum, 'BOUNDED_UINT_REQUIRED')
    return value


def label(value, maximum=100):
    require(type(value) is str and 1 <= len(value) <= maximum
            and re.fullmatch(r'[A-Za-z0-9_,.():+/-]+(?:[ A-Za-z0-9_,.():+/-]*)', value) is not None,
            'BOUNDED_ASCII_LABEL_REQUIRED')
    return value


def local_path(path):
    try:
        text = os.fspath(path)
        require(type(text) is str, 'TEXT_PATH_REQUIRED')
        win = PureWindowsPath(text)
        require(not (text.replace('\\', '/').startswith('//') or '://' in text
                     or (win.drive and not win.root) or '..' in win.parts), 'LEXICAL_LOCAL_PATH_REQUIRED')
        for part in win.parts:
            if part == win.anchor:
                continue
            require(not (':' in part or part.endswith(('.', ' ')) or PureWindowsPath(part).is_reserved()),
                    'NORMAL_LOCAL_PATH_REQUIRED')
        return common.local_path(text)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise BundleError('SAFE_LOCAL_PATH_REQUIRED') from exc


def read(path, limit=MAX_FILE):
    path = local_path(path)
    require(stat.S_ISREG(path.stat().st_mode), 'REGULAR_LOCAL_FILE_REQUIRED')
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, 'FILE_SIZE_LIMIT')
    return data


def strict_json(data):
    require(type(data) is bytes and len(data) <= MAX_JSON, 'JSON_SIZE_LIMIT')
    try:
        result = json.loads(data.decode('utf-8-sig'), object_pairs_hook=common.pairs,
                            parse_constant=common.invalid_constant)
        json.dumps(result, allow_nan=False)
    except (ValueError, UnicodeError, OverflowError, RecursionError) as exc:
        raise BundleError('STRICT_FINITE_UNIQUE_JSON_REQUIRED') from exc
    require(type(result) is dict, 'JSON_OBJECT_REQUIRED')
    return result


@dataclass(frozen=True)
class Identity:
    family: str
    model: str
    sysid: str
    profile: str
    device_id_sha256: str

    @classmethod
    def parse(cls, obj):
        object_fields(obj, cls.__dataclass_fields__, cls.__dataclass_fields__)
        require(obj['family'] in ('WA', 'XC', 'XW', 'LTU'), 'FAMILY_REQUIRED')
        for key in ('model', 'profile'):
            label(obj[key])
        require(type(obj['sysid']) is str and re.fullmatch('0x[0-9a-f]{4}', obj['sysid']) is not None,
                'CANONICAL_SYSID_REQUIRED')
        digest(obj['device_id_sha256'])
        identity = cls(**obj)
        if identity.family == 'WA':
            specs = [s for s in board.BOARDS.values() if s['profile'] == identity.profile]
            require(len(specs) == 1 and identity.model == specs[0]['model']
                    and identity.sysid in specs[0]['sysids'], 'WA_MODEL_SYSID_PROFILE_MISMATCH')
        return identity


@dataclass(frozen=True)
class FileSpec:
    path: str
    bytes: int
    sha256: str

    @classmethod
    def parse(cls, obj):
        object_fields(obj, cls.__dataclass_fields__, cls.__dataclass_fields__)
        text = obj['path']
        require(type(text) is str and 1 <= len(text) <= 240 and '\\' not in text
                and re.fullmatch(r'[A-Za-z0-9_./-]+', text) is not None, 'RELATIVE_FILE_PATH_REQUIRED')
        posix = PurePosixPath(text)
        require(not posix.is_absolute() and '..' not in posix.parts and '.' not in text.split('/')
                and posix.as_posix() == text, 'RELATIVE_CANONICAL_FILE_PATH_REQUIRED')
        require(0 < uint(obj['bytes'], MAX_FILE), 'POSITIVE_FILE_SIZE_REQUIRED')
        return cls(text, obj['bytes'], digest(obj['sha256']))


def load_manifest(path, trusted_manifest_sha256):
    # Validate the independent caller anchor BEFORE opening any supplied path.
    trusted = digest(trusted_manifest_sha256)
    raw = read(path, MAX_JSON)
    require(common.sha(raw) == trusted, 'OUT_OF_BAND_MANIFEST_HASH_MISMATCH')
    obj = strict_json(raw)
    object_fields(obj, ('schema_version', 'target', 'image', 'protected_backups', 'watchdog',
                        'rollback', 'saved_evidence_sha256'), ('schema_version', 'target', 'image'))
    require(type(obj['schema_version']) is int and obj['schema_version'] == 1, 'MANIFEST_VERSION')
    target = Identity.parse(obj['target'])
    image = obj['image']
    object_fields(image, ('file', 'kind', 'identity', 'build_id'), ('file', 'kind', 'identity', 'build_id'))
    require(image['kind'] in ('factory', 'sysupgrade'), 'IMAGE_KIND_REQUIRED')
    require(Identity.parse(image['identity']) == target, 'IMAGE_IDENTITY_MISMATCH')
    label(image['build_id'])
    specs = [FileSpec.parse(image['file'])]
    backups = object_fields(obj.get('protected_backups', {}), PARTITIONS)
    for row in backups.values():
        object_fields(row, ('file', 'identity', 'boot_id'), ('file', 'identity', 'boot_id'))
        Identity.parse(row['identity'])
        label(row['boot_id'])
        specs.append(FileSpec.parse(row['file']))
    watchdog = obj.get('watchdog')
    if watchdog is not None:
        object_fields(watchdog, ('file', 'installed_path'), ('file', 'installed_path'))
        require(type(watchdog['installed_path']) is str and re.fullmatch(r'/usr/sbin/[A-Za-z0-9_.-]+', watchdog['installed_path']) is not None,
                'WATCHDOG_INSTALLED_PATH_REQUIRED')
        specs.append(FileSpec.parse(watchdog['file']))
    rollback = obj.get('rollback')
    if rollback is not None:
        object_fields(rollback, ('file', 'kind', 'identity', 'build_id'), ('file', 'kind', 'identity', 'build_id'))
        require(rollback['kind'] in ('factory', 'sysupgrade'), 'ROLLBACK_IMAGE_KIND_REQUIRED')
        Identity.parse(rollback['identity'])
        label(rollback['build_id'])
        specs.append(FileSpec.parse(rollback['file']))
    if obj.get('saved_evidence_sha256') is not None:
        digest(obj['saved_evidence_sha256'])
    resolved = [local_path(local_path(path).parent / s.path) for s in specs]
    require(len({str(p).casefold() for p in resolved}) == len(specs), 'DUPLICATE_INPUT_FILE_PATH')
    existing = [p for p in resolved if p.exists()]
    for i, first in enumerate(existing):
        require(not any(first.samefile(other) for other in existing[i+1:]), 'ALIASED_INPUT_FILES')
    require(sum(s.bytes for s in specs) <= MAX_TOTAL, 'TOTAL_INPUT_SIZE_LIMIT')
    return obj, target, specs


def verify_file(root, spec, *, reject_erased=False):
    path = local_path(root / spec.path)
    try:
        data = read(path, MAX_FILE)
    except FileNotFoundError:
        return dict(present=False, size_matches=False, hash_matches=False, non_erased=False), None
    erased = bool(data) and (data.count(0) == len(data) or data.count(255) == len(data))
    result = dict(present=True, bytes=len(data), sha256=common.sha(data),
                  size_matches=len(data) == spec.bytes, hash_matches=common.sha(data) == spec.sha256,
                  non_erased=bool(data) and (not reject_erased or not erased))
    return result, data


def verify_runtime(snapshot, target, *, now_s, watchdog_sha256, rollback_sha256):
    """Check saved assertions. Their independent manifest binding is checked by verify()."""
    if snapshot is None:
        return {'snapshot_present': False}
    allowed = ('identity', 'boot_id', 'boot_started_s', 'timestamp_s', 'build_id', 'image_sha256',
               'protected_sha256', 'management_ok', 'rf_associated', 'counters', 'watchdog')
    object_fields(snapshot, allowed)
    checks = dict(snapshot_present=True)
    checks['identity_matches'] = Identity.parse(snapshot['identity']) == target if snapshot.get('identity') is not None else False
    for key in ('boot_id', 'build_id'):
        if snapshot.get(key) is not None:
            label(snapshot[key])
    for key in ('management_ok', 'rf_associated'):
        if snapshot.get(key) is not None:
            require(type(snapshot[key]) is bool, 'RUNTIME_BOOLEAN_REQUIRED')
        checks[key] = snapshot.get(key) is True
    checks['boot_id_present'] = snapshot.get('boot_id') is not None
    start = number(snapshot['boot_started_s']) if snapshot.get('boot_started_s') is not None else None
    stamp = number(snapshot['timestamp_s']) if snapshot.get('timestamp_s') is not None else None
    checks['snapshot_fresh'] = start is not None and stamp is not None and start <= stamp <= now_s + MAX_SKEW and now_s - stamp <= MAX_AGE
    counters = object_fields(snapshot.get('counters', {}), ('start_s', 'end_s', 'tx_before', 'tx_after', 'rx_before', 'rx_after'))
    for key in ('tx_before', 'tx_after', 'rx_before', 'rx_after'):
        if counters.get(key) is not None:
            uint(counters[key])
    checks['separate_tx_rx_progress'] = (all(counters.get(k) is not None for k in ('tx_before', 'tx_after', 'rx_before', 'rx_after'))
                                         and counters['tx_after'] > counters['tx_before'] and counters['rx_after'] > counters['rx_before'])
    t0 = number(counters['start_s']) if counters.get('start_s') is not None else None
    t1 = number(counters['end_s']) if counters.get('end_s') is not None else None
    checks['counter_interval_fresh'] = (start is not None and stamp is not None and t0 is not None and t1 is not None
                                         and start <= t0 < t1 <= stamp and now_s - t1 <= MAX_AGE)
    wd = object_fields(snapshot.get('watchdog', {}), ('installed', 'armed', 'boot_id', 'heartbeat_s',
                      'script_sha256', 'rollback_image_sha256', 'installed_path'))
    for key in ('installed', 'armed'):
        if wd.get(key) is not None:
            require(type(wd[key]) is bool, 'WATCHDOG_BOOLEAN_REQUIRED')
    for key in ('script_sha256', 'rollback_image_sha256'):
        if wd.get(key) is not None:
            digest(wd[key])
    heartbeat = number(wd['heartbeat_s']) if wd.get('heartbeat_s') is not None else None
    checks.update(watchdog_installed=wd.get('installed') is True, watchdog_armed=wd.get('armed') is True,
                  watchdog_current_boot=snapshot.get('boot_id') is not None and wd.get('boot_id') == snapshot['boot_id'],
                  watchdog_heartbeat_fresh=start is not None and stamp is not None and heartbeat is not None
                    and start <= heartbeat <= stamp and now_s - heartbeat <= MAX_AGE,
                  watchdog_script_matches=watchdog_sha256 is not None and wd.get('script_sha256') == watchdog_sha256,
                  watchdog_rollback_matches=rollback_sha256 is not None and wd.get('rollback_image_sha256') == rollback_sha256)
    return checks


def audit_watchdog_tar(data, installed_path, expected_sha256):
    """Inspect TAR bytes only; never restore members or execute their contents."""
    require(len(data) <= MAX_TAR, 'TAR_SIZE_LIMIT')
    expected = installed_path.lstrip('/')
    seen, found = set(), None
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:') as archive:
        for count, member in enumerate(archive, 1):
            require(count <= 2048, 'TAR_MEMBER_LIMIT')
            name = member.name
            if name.startswith('./'):
                name = name[2:]
            if name == '.':
                name = ''
            posix = PurePosixPath(name)
            require(not posix.is_absolute() and '..' not in posix.parts and '\\' not in name
                    and ':' not in name and (not name or posix.as_posix() == name), 'UNSAFE_TAR_NAME')
            require(name not in seen, 'DUPLICATE_TAR_MEMBER')
            seen.add(name)
            require(member.isdir() or member.isfile() or member.issym(), 'UNSUPPORTED_TAR_MEMBER')
            # Other stock symlinks are not followed. The declared watchdog must be a regular file.
            if name == expected:
                require(member.isfile() and not member.islnk() and 0 < member.size <= MAX_JSON,
                        'WATCHDOG_REGULAR_FILE_REQUIRED')
                stream = archive.extractfile(member)
                require(stream is not None, 'WATCHDOG_TAR_CONTENT_REQUIRED')
                body = stream.read(MAX_JSON + 1)
                require(len(body) == member.size, 'WATCHDOG_TAR_CONTENT_SIZE')
                found = dict(sha256=common.sha(body), bytes=len(body), mode=oct(member.mode & 0o7777),
                             hash_matches=common.sha(body) == expected_sha256,
                             safe_executable_mode=bool(member.mode & 0o111) and not bool(member.mode & 0o6022)
                                and member.uid == 0 and member.gid == 0)
    return dict(present=found is not None, verified=found is not None and found['hash_matches']
                and found['safe_executable_mode'], content=found)


def decode_watchdog(rootfs, installed_path, expected_sha256):
    """Only a pinned local decoder; bounded stdout, fixed argv, no target executor."""
    from firmware.openwrt.pbe5ac_gen2_ptp_kit import build_public_openmax_release as core
    tools_dir = local_path(core.DEFAULT_TOOLS)
    tools = core._toolchain(tools_dir)
    executable = local_path(tools['sqfs2tar'])
    work = local_path(ROOT / 'artifacts/verification/stage356a')
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='decode-', dir=work) as directory:
        source = local_path(Path(directory) / 'image.squashfs')
        source.write_bytes(rootfs)
        # Only /usr/sbin is exported, and only TAR bytes are read. No archive extraction.
        process = subprocess.Popen([str(executable), '-d', 'usr/sbin', '-k', '-r', '.', '-s', str(source)],
                                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, cwd=str(executable.parent),
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        output = bytearray()
        failures = []
        def consume():
            try:
                while len(output) <= MAX_TAR:
                    chunk = process.stdout.read(min(65536, MAX_TAR + 1 - len(output)))
                    if not chunk:
                        break
                    output.extend(chunk)
                if len(output) > MAX_TAR:
                    process.kill()
            except OSError:
                failures.append('DECODER_PIPE_FAILURE')
        reader = threading.Thread(target=consume, daemon=True)
        reader.start()
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired as exc:
            process.kill(); process.wait(timeout=5)
            raise BundleError('DECODER_TIMEOUT') from exc
        finally:
            reader.join(timeout=5)
            process.stdout.close()
        require(not reader.is_alive() and not failures and len(output) <= MAX_TAR and process.returncode == 0,
                'PINNED_DECODER_FAILED_OR_LIMIT')
        return audit_watchdog_tar(bytes(output), installed_path, expected_sha256)


def _image_checks(data, manifest_image, target, watchdog=None):
    result = dict(container_verified=False, board_kernel_join_verified=False, watchdog_embedding='UNKNOWN_FILESYSTEM_NOT_DECODED')
    if data is None:
        return result
    try:
        parsed = inspect_image(data)
    except (ValueError, IndexError, KeyError, OverflowError, TypeError):
        return result
    expected = 'OPEN_factory' if manifest_image['kind'] == 'factory' else 'uImage_sysupgrade'
    result['container_verified'] = parsed.get('format') == expected
    if result['container_verified'] and target.family == 'WA':
        spec = next(s for s in board.BOARDS.values() if s['profile'] == target.profile)
        try:
            payload = board._factory(data) if manifest_image['kind'] == 'factory' else trailers(data)[0]
            require(len(payload) <= WA_PAYLOAD_CAP, 'WA_PAYLOAD_CAPACITY')
            if manifest_image['kind'] == 'sysupgrade':
                require(any(t.get('supported_devices') == [target.profile] for t in parsed['FWx0']), 'IMAGE_METADATA_PROFILE_MISMATCH')
            board._kernel(payload, spec)
            result['board_kernel_join_verified'] = True
        except (ValueError, IndexError, KeyError, OverflowError, TypeError):
            pass
        if result['board_kernel_join_verified'] and watchdog is not None:
            try:
                rootfs = payload[0x280000:]
                used = struct.unpack_from('<Q', rootfs, 40)[0]
                proof = decode_watchdog(rootfs[:used], watchdog['installed_path'], watchdog['file']['sha256'])
                result['watchdog_content'] = proof
                result['watchdog_embedding'] = 'VERIFIED_LOCAL_IMAGE_BYTES' if proof['verified'] else 'MISSING_OR_MISMATCHED'
            except (ValueError, OSError, tarfile.TarError, subprocess.SubprocessError):
                result['watchdog_embedding'] = 'UNKNOWN_DECODER_FAILED_OR_LIMIT'
    return result


def verify(manifest_path, *, trusted_manifest_sha256, evidence_path=None, mode='preflight', now_s=None):
    require(mode in ('preflight', 'postflash'), 'MODE_REQUIRED')
    now = number(time.time() if now_s is None else now_s)
    manifest, target, specs = load_manifest(manifest_path, trusted_manifest_sha256)
    root = local_path(manifest_path).parent
    checks, files, blobs = {}, {}, {}
    for spec in specs:
        info, blob = verify_file(root, spec, reject_erased=spec.path in {
            row['file']['path'] for row in manifest.get('protected_backups', {}).values()})
        files[spec.path], blobs[spec.path] = info, blob
        require(sum(x.get('bytes', 0) for x in files.values()) <= MAX_TOTAL, 'ACTUAL_TOTAL_INPUT_SIZE_LIMIT')
    checks['local_files_match_trusted_references'] = all(
        x['present'] and x['size_matches'] and x['hash_matches'] and x['non_erased'] for x in files.values())
    image = _image_checks(blobs[manifest['image']['file']['path']], manifest['image'], target, manifest.get('watchdog'))
    checks['image_container_verified'] = image['container_verified']
    checks['image_board_kernel_join_verified'] = image['board_kernel_join_verified']
    checks['image_watchdog_embedded_verified'] = image['watchdog_embedding'] == 'VERIFIED_LOCAL_IMAGE_BYTES'
    evidence = None
    if evidence_path is not None and manifest.get('saved_evidence_sha256') is not None:
        try:
            raw = read(evidence_path, MAX_JSON)
            if common.sha(raw) == manifest['saved_evidence_sha256']:
                evidence = strict_json(raw)
        except FileNotFoundError:
            pass
    checks['saved_evidence_hash_bound'] = evidence is not None
    if evidence is None:
        evidence = {}
    object_fields(evidence, ('schema_version', 'source_kind', 'pre', 'post', 'backups'))
    if evidence:
        require(type(evidence.get('schema_version')) is int and evidence['schema_version'] == 1, 'EVIDENCE_VERSION')
        require(evidence.get('source_kind') in ('SAVED_RUNTIME_READBACK', 'SYNTHETIC_FIXTURE'), 'EVIDENCE_SOURCE_KIND')
    wd = manifest.get('watchdog')
    rollback = manifest.get('rollback')
    checks['watchdog_file_reference_present'] = wd is not None
    checks['rollback_reference_present'] = rollback is not None
    checks['rollback_identity_matches'] = rollback is not None and Identity.parse(rollback['identity']) == target
    rollback_image = _image_checks(blobs[rollback['file']['path']], rollback, target) if rollback else {}
    checks['rollback_container_verified'] = rollback_image.get('container_verified') is True
    checks['rollback_board_kernel_join_verified'] = rollback_image.get('board_kernel_join_verified') is True
    watchdog_sha = wd['file']['sha256'] if wd else None
    rollback_sha = rollback['file']['sha256'] if rollback else None
    pre, post = evidence.get('pre'), evidence.get('post')
    snapshots = {'pre': verify_runtime(pre, target, now_s=now, watchdog_sha256=watchdog_sha, rollback_sha256=rollback_sha)}
    if mode == 'postflash':
        snapshots['post'] = verify_runtime(post, target, now_s=now, watchdog_sha256=watchdog_sha, rollback_sha256=rollback_sha)
    actual_backups = object_fields(evidence.get('backups', {}), PARTITIONS)
    protected = {}
    for partition in PARTITIONS:
        reference = manifest.get('protected_backups', {}).get(partition)
        observed = actual_backups.get(partition)
        valid = reference is not None and type(observed) is dict and type(pre) is dict
        if observed is not None:
            object_fields(observed, ('identity', 'boot_id', 'bytes', 'sha256'), ('identity', 'boot_id', 'bytes', 'sha256'))
            Identity.parse(observed['identity']); uint(observed['bytes'], MAX_FILE); digest(observed['sha256'])
        if valid:
            info = files[reference['file']['path']]
            valid = (Identity.parse(reference['identity']) == target == Identity.parse(observed['identity'])
                     and reference['boot_id'] == observed['boot_id'] == pre.get('boot_id')
                     and reference['file']['bytes'] == observed['bytes']
                     and reference['file']['sha256'] == observed['sha256']
                     and info['hash_matches'] and info['size_matches'] and info['non_erased'])
        protected[partition] = dict(consistent=bool(valid), expected_sha256=reference['file']['sha256'] if reference else None,
                                    actual_sha256=files[reference['file']['path']].get('sha256') if reference else None)
        checks[partition + '_backup_consistent'] = bool(valid)
    for phase, snapshot in [('pre', pre)] + ([('post', post)] if mode == 'postflash' else []):
        present = type(snapshot) is dict
        hashes = snapshot.get('protected_sha256', {}) if present else {}
        object_fields(hashes, PARTITIONS)
        checks[phase + '_protected_match_backups'] = all(
            manifest.get('protected_backups', {}).get(p) is not None
            and hashes.get(p) == manifest['protected_backups'][p]['file']['sha256'] for p in PARTITIONS)
        expected = rollback if phase == 'pre' else manifest['image']
        checks[phase + '_build_and_image_match'] = present and expected is not None and snapshot.get('build_id') == expected['build_id'] and snapshot.get('image_sha256') == expected['file']['sha256']
        checks[phase + '_watchdog_path_matches'] = present and wd is not None and snapshot.get('watchdog', {}).get('installed_path') == wd['installed_path']
    if mode == 'postflash':
        checks['boot_id_changed'] = (type(pre) is dict and type(post) is dict and pre.get('boot_id') is not None
                                     and post.get('boot_id') is not None and pre['boot_id'] != post['boot_id'])
        checks['post_boot_after_pre_snapshot'] = (type(pre) is dict and type(post) is dict
            and post.get('boot_started_s') is not None and pre.get('timestamp_s') is not None
            and number(post['boot_started_s']) > number(pre['timestamp_s']))
    contract_ok = all(checks.values()) and all(all(row.values()) for row in snapshots.values())
    reasons = [key for key, ok in checks.items() if not ok]
    reasons += [phase + '_' + key for phase, row in snapshots.items() for key, ok in row.items() if not ok]
    return dict(tool_id=TOOL_ID, schema_version=1, mode=mode,
                status='SAVED_EVIDENCE_CONSISTENT_NOT_FLASH_APPROVAL' if contract_ok else 'BLOCKED',
                data_contract_status='SAVED_EVIDENCE_CONSISTENT_NOT_FLASH_APPROVAL' if contract_ok else 'MISSING_OR_INCONSISTENT_SAVED_EVIDENCE',
                as_of_s=now, evaluation_is_live_observation=False,
                trusted_manifest_sha256=trusted_manifest_sha256,
                source_kind=evidence.get('source_kind', 'MISSING'), family=target.family,
                checks=checks, runtime_checks=snapshots, protected_backup_checks=protected,
                image_checks=image, rollback_image_checks=rollback_image, reason_codes=reasons, boundary=BOUNDARY.copy(),
                qualification='Externally supplied hash binds local assertions, not physical truth. Image embedding is distinct from saved installation/armed assertions; no flash approval.')


def write_report(path, report, *, protected_paths=()):
    target = local_path(path)
    require(target.suffix == '.json', 'JSON_OUTPUT_REQUIRED')
    protected = {str(local_path(p)).casefold() for p in protected_paths}
    require(str(target).casefold() not in protected, 'INPUT_OVERWRITE_FORBIDDEN')
    if target.exists():
        old = strict_json(read(target, MAX_JSON * 8))
        require(old.get('tool_id') == TOOL_ID and type(old.get('schema_version')) is int
                and old['schema_version'] == 1, 'UNOWNED_OUTPUT_OVERWRITE_FORBIDDEN')
    text = json.dumps(report, allow_nan=False, indent=2, sort_keys=True) + '\n'
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=target.name + '.', suffix='.tmp', dir=target.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
        temp.replace(target)
    finally:
        if temp.exists():
            temp.unlink()


def inventory(root=ROOT):
    root = local_path(root)
    rows = []
    sources = []
    for family, relative in [('WA', 'artifacts/autoresearch/stage170a_public_wa_4board_release_v4_receipt.json'),
                             ('XC_XW_XM', 'artifacts/autoresearch/stage171a_public_xc_xw_tester_release_receipt.json'),
                             ('LTU', 'artifacts/autoresearch/stage251a_ltu_safe_champion_v2_receipt.json')]:
        path = root / relative
        try:
            raw = read(path, MAX_JSON)
            saved = strict_json(raw)
            sources.append(dict(path=relative, sha256=common.sha(raw), bytes=len(raw)))
            output = []
            references = saved.get('outputs', {})
            if family == 'LTU':
                references = {'safe_shell': dict(path=saved['script_path'], sha256=saved['script_sha256'])}
            for record in references.values():
                obj = object_fields(record, ('path', 'sha256', 'bytes', 'size_bytes'), ('path', 'sha256'))
                target = root / FileSpec.parse(dict(path=obj['path'], sha256=obj['sha256'], bytes=obj.get('bytes', obj.get('size_bytes', 1)))).path
                actual = read(target)
                output.append(dict(path=obj['path'], bytes=len(actual), sha256=common.sha(actual),
                                   matches_recorded_hash=common.sha(actual) == obj['sha256']))
            rows.append(dict(family=family, status='BLOCKED', source_receipt=relative, files=output,
                             role='FIRMWARE_IMAGES_REQUIRE_BOARD_GATES' if family == 'WA' else 'DIAGNOSIS_OR_SAFE_SHELL_ONLY_NOT_FLASH_IMAGE',
                             reason_codes=['NO_OUT_OF_BAND_TRUST_ANCHOR_FOR_INVENTORY', 'DEVICE_PROTECTED_BACKUPS_MISSING',
                                           'FRESH_TRUSTED_RUNTIME_EVIDENCE_MISSING', 'IMAGE_WATCHDOG_EMBEDDING_UNKNOWN', 'POSTFLASH_EVIDENCE_MISSING']))
        except FileNotFoundError:
            rows.append(dict(family=family, status='BLOCKED', reason_codes=['LOCAL_INVENTORY_INPUT_MISSING']))
    return dict(tool_id=TOOL_ID, schema_version=1, stage='356A', task_id='T-S356A-TESTER-BUNDLE-VERIFIER',
                status='BLOCKED_CURRENT_KITS_NOT_FLASH_APPROVED', inventory=rows,
                static_sources=sources + [common.binding(root / p, root) for p in (
                    'tools/firmware/verify_openmax_tester_bundle.py', 'tests/test_stage356a.py',
                    'tools/firmware/preflight_validate_user_board_info.py',
                    'tools/firmware/verify_all_openmax_kit_checksums_and_headers.py',
                    'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py',
                    'firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py')],
                summary=dict(kits=len(rows), actual_target_access=False, current_kits_flash_approved=0),
                gaps=['No complete externally anchored per-device manifest, original protected backups or fresh target readback supplied.',
                      'WA watchdog embedding has a bounded pinned SquashFS decoder; no complete trusted device manifest was supplied for existing kits.'],
                boundary=BOUNDARY.copy())


def build(root=ROOT):
    report = inventory(root)
    text = '''<!-- doc-head: Stage356A offline tester bundle preflight and postflash evidence verifier -->
Local hashes and saved assertions never authorize a flash or prove physical acceptance.
WA watchdog embedding uses a pinned offline decoder; unsupported formats remain UNKNOWN.
<!-- /doc-head -->

# Stage356A

Parent: offline release safety and evidence boundaries, after Stage355.
This program only reads bounded local JSON/files and writes a JSON report.
It has no target/radio/SSH/WAN/flash/configuration executor. Its only native execution
is the pinned local sqfs2tar decoder, fixed argv, no shell,30s timeout,8MiB TAR cap.

Build inventory: `python tools/firmware/verify_openmax_tester_bundle.py inventory --build`.
Tests: `python -m pytest -q -o addopts= tests/test_stage356a.py`.
`--help`, `preflight --help` and `postflash --help` document the CLI.

## Independent trust and schema1

Both verification modes require --manifest, --trusted-manifest-sha256 and
--evidence. The trusted SHA256 MUST arrive through an independent caller channel;
a manifest cannot establish its own trusted hash. The tool validates the anchor
before opening evidence or referenced files. A hash is not a signature or proof
that the saved observations occurred on hardware. Outputs never contain backup bytes.

Manifest JSON has schema_version=1; target; image; protected_backups; watchdog;
rollback; saved_evidence_sha256. Unknown keys, duplicate keys, nonfinite values,
unsafe paths, oversized files and invalid field types reject with fixed error codes.
Target/image/rollback identity fields are family,model,sysid,profile,device_id_sha256.
Family is WA/XC/XW/LTU. WA additionally checks the known exact model/profile/sysid
matrix; other families are not silently promoted to supported firmware platforms.
An identity hash is a caller assertion, not a physical serial-number readback.

File references are {path,bytes,sha256}: canonical relative POSIX paths within the
manifest directory, never UNC/URI/device/ADS/traversal/symlink/reparse aliases.
Image and rollback each contain file,kind(factory|sysupgrade),identity,build_id.
Protected backups map EXACT mtd0,mtd1,mtd4,mtd5 to file,identity,boot_id records.
The four actual original files must match independently anchored expected sizes
and hashes, belong to the same identity/preboot, and not consist entirely of00/FF.
Matching erased bytes is rejected even when the expected hash was supplied.
Watchdog contains file and installed_path (/usr/sbin/safe-name); bundled file
matching does NOT mean embedded, installed, armed or safe to execute.

Evidence JSON has schema_version=1, source_kind(SAVED_RUNTIME_READBACK or
SYNTHETIC_FIXTURE), pre, optional post, and backups. The entire evidence file must
match saved_evidence_sha256 inside the independently anchored manifest.
Each backups entry contains identity,boot_id,bytes,sha256 and binds the actual file.
Snapshot fields: identity,boot_id,boot_started_s,timestamp_s,build_id,image_sha256,
protected_sha256,management_ok,rf_associated,counters,watchdog.
Counters: start_s,end_s,tx_before,tx_after,rx_before,rx_after; unsigned and separately
increasing within a fresh same-boot observation, never compared across boot resets.
Snapshot watchdog: installed,armed,boot_id,heartbeat_s,script_sha256,
rollback_image_sha256,installed_path. True booleans are required; missing/unknown/
false is never pass. Heartbeat must be within this boot, not future and <=150s old.
Snapshots allow at most5s clock skew and are <=150s old at --now-s (default local
wall clock). An explicit historical --now-s checks saved consistency only.

## Postflash comparison and image boundary

Postflash additionally requires changed boot IDs, post boot after the pre snapshot,
exact expected new build/image hash, unchanged four protected hashes, management,
RF, counter progress and installed/armed/current-boot/fresh-heartbeat watchdog.
Actual backup file bytes are hashed only; never printed, copied or executed.
Stage264 pure container CRC checks are reused. WA also checks the known official
kernel/DTB profile using Stage232's pure parser, without its UNSET v5 trust path.
CRC and metadata are not signature authentication. Unsupported container/board
joins remain UNKNOWN or mismatched, including unsupported XC/XW/LTU images.

After WA board/kernel/capacity validation, the exact rootfs bytes are passed to
pinned squashfs-tools-ng1.3.2. Only usr/sbin is streamed to bounded TAR bytes.
No files are restored. The declared watchdog must be a unique root-owned regular
executable with no group/world writes or set-ID bits, and match the trusted hash.
Unsafe TAR names, watchdog links, duplicates, oversize or decoder failure block.
Other stock links are ignored, never followed. Unsupported families keep embedding
UNKNOWN. Saved installed/armed assertions alone never prove image embedding.
data_contract_status/status may be SAVED_EVIDENCE_CONSISTENT_NOT_FLASH_APPROVAL
when every gate passes, including explicit synthetic fixtures; never flash approval.
Both image and rollback require exact board/kernel joins; WA payload<=0xf60000.
Current verifier modes exit1 when blocked; malformed/untrusted inputs exit2.
Exit0 means only complete consistent saved evidence, including verified image
embedding. It must never imply flash approval or independent hardware validation.

## Actual existing kits and reproducibility

The generated inventory hashes actual WA publicv4 files, Stage171 XC/XW/XM
diagnostic starter files and the LTU safe shell, comparing historical receipt
references where present. Drift is retained. No backups/runtime/postflash evidence
is invented. All three kit entries remain BLOCKED and target_access=false.
Historical inventory hashes are observations, not independent trust anchors.
Deterministic inventory/build output contains no current timestamps. Runtime
verification records the caller's as-of time and never claims fresh target access.
Outputs are finite atomic JSON; source/evidence/referenced-file collisions and
unowned existing output files are rejected. Public reports contain only hashes,
sizes, status/reason codes and check booleans, without raw configuration contents.
Decision: KEEP as an offline evidence checker; no deployment or zero-brick claim.
'''
    common.write_doc(local_path(root) / DOC, text)
    report['outputs'] = {DOC: common.binding(local_path(root) / DOC, local_path(root))}
    write_report(local_path(root) / OUT, report,
                 protected_paths=[local_path(root) / s['path'] for s in report['static_sources']])
    return report


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise BundleError('CLI_ARGUMENTS_REQUIRED')


def main(argv=None):
    try:
        parser = Parser(description=__doc__)
        sub = parser.add_subparsers(dest='mode', required=True, parser_class=Parser)
        inv = sub.add_parser('inventory', help='Observe local kit files; never approve flash')
        inv.add_argument('--root', default=str(ROOT))
        inv.add_argument('--build', action='store_true', help='Write the owned Stage356 inventory and documentation')
        for mode in ('preflight', 'postflash'):
            p = sub.add_parser(mode, help='Check locally saved data only')
            p.add_argument('--manifest', required=True)
            p.add_argument('--trusted-manifest-sha256', required=True)
            p.add_argument('--evidence', required=True)
            p.add_argument('--now-s', type=float)
            p.add_argument('--output')
        args = parser.parse_args(argv)
        if args.mode == 'inventory':
            result = build(args.root) if args.build else inventory(args.root)
        else:
            result = verify(args.manifest, trusted_manifest_sha256=args.trusted_manifest_sha256,
                            evidence_path=args.evidence, mode=args.mode, now_s=args.now_s)
            if args.output:
                manifest, _, specs = load_manifest(args.manifest, args.trusted_manifest_sha256)
                protected = [args.manifest, args.evidence] + [local_path(args.manifest).parent / s.path for s in specs]
                write_report(args.output, result, protected_paths=protected)
        print(json.dumps(result, allow_nan=False, sort_keys=True))
        return 1 if result['status'].startswith('BLOCKED') else 0
    except (BundleError, OSError, ValueError, TypeError, UnicodeError, OverflowError, RecursionError):
        print(json.dumps(dict(tool_id=TOOL_ID, status='ERROR', error_code='INVALID_OR_UNTRUSTED_LOCAL_INPUT', boundary=BOUNDARY)))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
