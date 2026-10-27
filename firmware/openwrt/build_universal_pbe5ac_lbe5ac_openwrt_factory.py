#!/usr/bin/env python3
"""Local, source-bound OpenWrt factory candidates; inspection never runs tools.

Only the documented unsigned OPEN/kernel/rootfs layout is supported. A candidate
is not a signed vendor image, physical compatibility proof, or permission to flash.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import atomic_write, receipt, save, snapshot

STEM = 'stage983a_squashfs_factory_fail_closed_contract'
SELF = 'firmware/openwrt/' + Path(__file__).name
PROFILES = ('ubnt,powerbeam-5ac-gen2', 'ubnt,litebeam-ac-gen2')
REQUIRED = (
    'etc/uci-defaults/99-fmx-pbe5ac-ptp',
    'usr/sbin/fmx_ptp_rollback_watchdog.sh',
    'usr/sbin/fmx_pbe_lbe_runtime_transaction.sh',
    'etc/rc.local',
)
ROOTFS_HEADER = 0x10014C
ROOTFS_DATA = ROOTFS_HEADER + 56
SQUASHFS_OFFSET = 0x280184
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_SOURCE_BYTES = 1024 * 1024


def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def strict_object(blob: bytes) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('duplicate recipe key')
            result[key] = value
        return result
    def reject(value):
        raise ValueError('nonfinite recipe value')
    result = json.loads(blob, object_pairs_hook=unique, parse_constant=reject)
    if not isinstance(result, dict):
        raise ValueError('recipe object required')
    return result


def local_path(value) -> Path:
    text = os.fspath(value)
    if (not isinstance(text, str) or text.replace('/', '\\').startswith('\\\\')
            or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*://', text)):
        raise ValueError('local filesystem path required')
    path = Path(text).absolute()
    for node in (path, *path.parents):
        try:
            info = node.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise ValueError('symlink or reparse point forbidden')
    if os.name == 'nt':
        import ctypes
        if ctypes.windll.kernel32.GetDriveTypeW(path.anchor) == 4:
            raise ValueError('network drive forbidden')
    return path


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def regular_bytes(path: Path, maximum=MAX_SOURCE_BYTES) -> bytes:
    path = local_path(path)
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not 0 < info.st_size <= maximum:
        raise ValueError('bounded single-link regular file required')
    data = path.read_bytes()
    if len(data) != info.st_size:
        raise ValueError('file changed during read')
    return data


def _reachable_launch(text: str, binary: str, *, background=False) -> dict:
    """Accept only a complete, straight-line template; never interpret shell flow."""
    lines = text.splitlines()
    expected_lines = 4 if background else 3
    if (not text.endswith('\n') or len(lines) != expected_lines
            or lines[:2] != ['#!/bin/sh', 'set -eu']
            or (background and lines[-1] != 'exit 0')):
        raise ValueError('unsupported reachable launch template')
    line = lines[2]
    prefix = binary + ' ' if background else 'exec ' + binary + ' '
    if not line.startswith(prefix):
        raise ValueError('exact reachable launch required')
    if background:
        if not line.endswith(' &'):
            raise ValueError('watchdog must launch in background')
        line = line[:-2]
    elif line.startswith('exec '):
        line = line[5:]
    # No quoting, expansion, chaining, redirects, functions, comments or control flow.
    if not re.fullmatch(r'[A-Za-z0-9_./: -]+', line):
        raise ValueError('literal straight-line launch required')
    tokens = shlex.split(line, comments=False, posix=True)
    if line != ' '.join(tokens) or tokens[0] != binary:
        raise ValueError('canonical literal launch required')
    return _arguments(tokens)


def _arguments(tokens: list[str]) -> dict:
    args = {}
    index = 1
    while index < len(tokens):
        key = tokens[index]
        if key == '&' and index == len(tokens)-1:
            break
        if key in args or not key.startswith('--'):
            raise ValueError('duplicate or unsupported launch token')
        if key == '--apply':
            args[key] = True
            index += 1
        else:
            if index+1 >= len(tokens) or not re.fullmatch(r'[A-Za-z0-9_./:-]+', tokens[index+1]):
                raise ValueError('literal launch argument required')
            args[key] = tokens[index+1]
            index += 2
    return args


def validate_payload_tree(tree, expected_sha256: dict, *, channel_class=None) -> dict:
    tree = local_path(tree)
    if not tree.is_dir() or set(expected_sha256) != set(REQUIRED):
        raise ValueError('complete exact payload hash contract required')
    texts, members = {}, []
    for label in REQUIRED:
        expected = expected_sha256[label]
        if not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected):
            raise ValueError('payload SHA256 required')
        path = local_path(tree / label)
        blob = regular_bytes(path)
        if sha(blob) != expected:
            raise ValueError('payload hash mismatch: ' + label)
        if _mode(path) != 0o755:
            raise ValueError('payload must have executable0755 mode: ' + label)
        text = blob.decode('utf-8')
        if not text.startswith('#!/bin/sh\n') or '\0' in text:
            raise ValueError('POSIX shell payload required')
        if 'PLANNED_RETIRED' in text or 'Legacy actuator retired' in text:
            raise ValueError('retired payload cannot produce an image candidate')
        texts[label] = text
        members.append(dict(path=label, bytes=len(blob), sha256=sha(blob), mode='0755'))
    for label in (REQUIRED[1], REQUIRED[2]):
        canonical = ROOT/'firmware/openwrt/pbe5ac_gen2_ptp_kit'/Path(label).name
        if texts[label].encode('utf-8') != regular_bytes(canonical):
            raise ValueError('payload differs from reviewed canonical repository source: ' + label)
    helper = '/usr/sbin/fmx_pbe_lbe_runtime_transaction.sh'
    bootstrap_args = _reachable_launch(texts[REQUIRED[0]], helper)
    if (set(bootstrap_args) != {'--apply', '--identity', '--state-dir', '--qdisc-mode'}
            or bootstrap_args.get('--qdisc-mode') != 'auto'
            or bootstrap_args.get('--apply') is not True or any(
            not str(bootstrap_args.get(key, '')).startswith('/') for key in ('--identity', '--state-dir'))):
        raise ValueError('bootstrap requires explicit apply and absolute identity/state arguments')
    watchdog = '/usr/sbin/fmx_ptp_rollback_watchdog.sh'
    launch = _reachable_launch(texts[REQUIRED[3]], watchdog, background=True)
    required_args = {'--apply', '--identity', '--state-dir', '--watch-state-dir', '--peer',
                     '--channel-class', '--transaction-sha256', '--qdisc-mode'}
    if (not required_args <= set(launch) or set(launch)-required_args-{'--uci-mode'}
            or launch.get('--uci-mode', 'disabled') not in ('disabled', 'ram')
            or launch.get('--apply') is not True):
        raise ValueError('rc.local must explicitly launch the guarded watchdog with --apply')
    if 'SOURCE_STAGE984_WATCHDOG_V1' not in texts[REQUIRED[1]]:
        raise ValueError('reviewed watchdog contract marker required')
    if (launch.get('--qdisc-mode') != 'auto'
            or launch.get('--transaction-sha256') != expected_sha256[REQUIRED[2]]
            or any(launch.get(key) != bootstrap_args[key] for key in ('--identity', '--state-dir'))
            or not str(launch.get('--watch-state-dir', '')).startswith('/')
            or launch['--watch-state-dir'] == launch['--state-dir']
            or not launch.get('--peer') or launch.get('--channel-class') not in ('non-dfs', 'dfs')):
        raise ValueError('complete identity-bound watchdog wiring required')
    if channel_class is not None and launch['--channel-class'] != channel_class:
        raise ValueError('explicit watchdog channel class wiring required')
    return dict(state='PAYLOAD_TREE_VALIDATED', members=members,
                physical_acceptance='UNKNOWN', qdisc_mode='auto')


def squashfs_structure(blob: bytes) -> dict:
    """Structural rejection only; this is never a substitute for native readback."""
    if len(blob) < 96 or blob[:4] != b'hsqs':
        raise ValueError('complete SquashFSv4 superblock required')
    block_size = struct.unpack_from('<I', blob, 12)[0]
    block_log = struct.unpack_from('<H', blob, 22)[0]
    major, minor = struct.unpack_from('<HH', blob, 28)
    used = struct.unpack_from('<Q', blob, 40)[0]
    if ((major, minor) != (4, 0) or not 12 <= block_log <= 20
            or block_size != 1 << block_log or not 96 < used <= len(blob)):
        raise ValueError('invalid SquashFS layout or bounds')
    for offset in (64, 72):
        table = struct.unpack_from('<Q', blob, offset)[0]
        if not 96 <= table < used:
            raise ValueError('invalid SquashFS table offset')
    return dict(bytes_used=used, block_size=block_size, native_verified=False)


def factory_structure(blob: bytes) -> dict:
    if not SQUASHFS_OFFSET + 96 <= len(blob) <= MAX_IMAGE_BYTES or blob[:4] != b'OPEN':
        raise ValueError('bounded supported OPEN factory layout required')
    if struct.unpack_from('>I', blob, 260)[0] != zlib.crc32(blob[:260]) & 0xFFFFFFFF:
        raise ValueError('OPEN header CRC mismatch')
    if any(blob[264:268]):
        raise ValueError('OPEN reserved CRC word must be zero')
    if blob[0x10C:0x116] != b'PARTkernel' or blob[ROOTFS_HEADER:ROOTFS_HEADER+10] != b'PARTrootfs':
        raise ValueError('only kernel and rootfs PART layout is supported')
    if struct.unpack_from('>I', blob, 0x10C+48)[0] != ROOTFS_HEADER-8-(0x10C+56):
        raise ValueError('kernel PART extent mismatch')
    kernel_crc = struct.unpack_from('>II', blob, ROOTFS_HEADER-8)
    if kernel_crc != (zlib.crc32(blob[0x10C:ROOTFS_HEADER-8]) & 0xFFFFFFFF, 0):
        raise ValueError('kernel PART CRC mismatch')
    size = struct.unpack_from('>I', blob, ROOTFS_HEADER+48)[0]
    end = ROOTFS_DATA + size
    if end <= SQUASHFS_OFFSET + 96 or end + 8 + 264 != len(blob):
        raise ValueError('rootfs PART extent mismatch')
    if struct.unpack_from('>II', blob, end) != (zlib.crc32(blob[ROOTFS_HEADER:end]) & 0xFFFFFFFF, 0):
        raise ValueError('rootfs PART CRC mismatch')
    if blob[end-4:end] != b'\xde\xad\xc0\xde':
        raise ValueError('rootfs EOF marker missing')
    if blob[end+8:end+12] != b'ENDS' or any(blob[end+12:]):
        raise ValueError('only unsigned OpenWrt ENDS trailer is supported')
    fs = squashfs_structure(blob[SQUASHFS_OFFSET:end])
    return dict(rootfs_end=end, squashfs=fs, layout='UNSIGNED_OPEN_KERNEL_ROOTFS',
                vendor_signature_verified=False, hardware_acceptance='UNKNOWN')


def _rebuild_factory(original: bytes, fs: bytes) -> bytes:
    old = factory_structure(original)
    squashfs_structure(fs)
    slot = max(0x410000, (len(fs) + 0xFFFF) // 0x10000 * 0x10000)
    body = original[ROOTFS_DATA:SQUASHFS_OFFSET] + fs + b'\xff'*(slot-len(fs)) + b'\xde\xad\xc0\xde'
    header = bytearray(original[ROOTFS_HEADER:ROOTFS_DATA])
    struct.pack_into('>I', header, 48, len(body))
    part = bytes(header) + body
    result = original[:ROOTFS_HEADER] + part + struct.pack('>II', zlib.crc32(part) & 0xFFFFFFFF, 0) + original[old['rootfs_end']+8:]
    factory_structure(result)
    return result


@dataclass(frozen=True)
class Toolchain:
    mksquashfs: str
    mksquashfs_sha256: str
    unsquashfs: str
    unsquashfs_sha256: str

    def verify(self):
        for path, expected in ((self.mksquashfs, self.mksquashfs_sha256),
                               (self.unsquashfs, self.unsquashfs_sha256)):
            source = local_path(path)
            if not re.fullmatch('[0-9a-f]{64}', expected) or sha(regular_bytes(source, 64*1024*1024)) != expected:
                raise ValueError('native tool hash mismatch')
            if not _mode(source) & 0o111:
                raise ValueError('native executable tool required')


def _run(argv: list[str], tools: Toolchain):
    tools.verify()
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True,
                            timeout=180, env={'PATH': os.defpath, 'LANG': 'C', 'LC_ALL': 'C'})
    tools.verify()
    if result.returncode != 0:
        raise RuntimeError('native SquashFS tool failed')
    if len(result.stdout) + len(result.stderr) > 1024*1024:
        raise RuntimeError('native tool output bound exceeded')


def _native_posix() -> bool:
    return os.name == 'posix' and os.geteuid() == 0


def filesystem_manifest(tree: Path) -> dict:
    """Hash all unaffected files and metadata without following image symlinks."""
    result = {}
    hardlinks = {}
    total = 0
    for directory, subdirs, files in os.walk(tree, followlinks=False):
        for name in sorted(subdirs + files):
            path = Path(directory)/name
            info = path.lstat()
            label = path.relative_to(tree).as_posix()
            if len(result) >= 100000:
                raise ValueError('filesystem entry bound exceeded')
            item = {'type': stat.S_IFMT(info.st_mode), 'mode': stat.S_IMODE(info.st_mode),
                    'uid': info.st_uid, 'gid': info.st_gid}
            if hasattr(os, 'listxattr'):
                item['xattrs'] = {key:sha(os.getxattr(path,key,follow_symlinks=False))
                                 for key in sorted(os.listxattr(path,follow_symlinks=False))}
            elif _native_posix():
                raise ValueError('native xattr readback support required')
            if stat.S_ISLNK(info.st_mode):
                item['target'] = os.readlink(path)
            elif stat.S_ISREG(info.st_mode):
                total += info.st_size
                if total > 256*1024*1024:
                    raise ValueError('uncompressed filesystem size bound exceeded')
                item.update(bytes=info.st_size, sha256=sha(path.read_bytes()), links=info.st_nlink)
                if info.st_nlink > 1:
                    hardlinks.setdefault((info.st_dev,info.st_ino), []).append(label)
            elif stat.S_ISCHR(info.st_mode) or stat.S_ISBLK(info.st_mode):
                item['device'] = info.st_rdev
            elif not stat.S_ISDIR(info.st_mode):
                raise ValueError('unsupported filesystem node type')
            result[label] = item
    for labels in hardlinks.values():
        for label in labels:
            result[label]['hardlink_group'] = sorted(labels)
    return result


def pack_factory(*, base_factory, base_sha256: str, payload_tree, payload_sha256: dict,
                 profile: str, output, channel_class: str, toolchain: Toolchain | None = None,
                 execute: bool = False, root: Path = ROOT) -> dict:
    result = dict(state='PLANNED', image_emitted=False, native_tools_executed=False,
                  physical_acceptance='UNKNOWN', flash_approved=False)
    if type(execute) is not bool:
        raise ValueError('explicit boolean build authorization required')
    if not execute:
        return result
    destination = local_path(output)
    root = local_path(root)
    allowed = (root / '.git').resolve(), (root/'artifacts/verification').resolve()
    if not any(destination.is_relative_to(folder) for folder in allowed) or destination.exists():
        raise ValueError('new private output path required')
    if profile not in PROFILES:
        raise ValueError('explicit supported board profile required')
    if not _native_posix() or toolchain is None:
        raise ValueError('local POSIX root native toolchain required; no remote fallback')
    original = regular_bytes(local_path(base_factory), MAX_IMAGE_BYTES)
    if not re.fullmatch('[0-9a-f]{64}', base_sha256) or sha(original) != base_sha256:
        raise ValueError('base factory SHA256 mismatch')
    layout = factory_structure(original)
    payload = validate_payload_tree(payload_tree, payload_sha256, channel_class=channel_class)
    toolchain.verify()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fmx983-', dir=destination.parent) as work:
        work = Path(work)
        base_fs, repacked = work/'base.sqfs', work/'repacked.sqfs'
        base_fs.write_bytes(original[SQUASHFS_OFFSET:layout['rootfs_end']])
        unpacked, checked = work/'rootfs', work/'readback'
        _run([toolchain.unsquashfs, '-d', str(unpacked), str(base_fs)], toolchain)
        before = filesystem_manifest(unpacked)
        for label in REQUIRED:
            source = local_path(Path(payload_tree)/label)
            target = local_path(unpacked/label)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not target.is_file():
                raise ValueError('payload target collision')
            target.write_bytes(regular_bytes(source))
            target.chmod(0o755)
        validate_payload_tree(unpacked, payload_sha256, channel_class=channel_class)
        _run([toolchain.mksquashfs, str(unpacked), str(repacked), '-noappend',
              '-comp', 'xz', '-b', '262144', '-no-xattrs', '-all-root', '-processors', '1'], toolchain)
        fs = regular_bytes(repacked, MAX_IMAGE_BYTES)
        squashfs_structure(fs)
        _run([toolchain.unsquashfs, '-s', str(repacked)], toolchain)
        _run([toolchain.unsquashfs, '-d', str(checked), str(repacked)], toolchain)
        readback = validate_payload_tree(checked, payload_sha256, channel_class=channel_class)
        if readback['members'] != payload['members']:
            raise ValueError('native extracted payload differs')
        after = filesystem_manifest(checked)
        for label, item in before.items():
            if label not in REQUIRED and after.get(label) != item:
                raise ValueError('unapproved non-payload filesystem change')
        allowed_dirs = {str(Path(label).parent).replace('\\', '/') for label in REQUIRED}
        allowed_dirs |= {str(Path(label).parent).replace('\\', '/') for label in allowed_dirs}
        for label in set(after)-set(before)-set(REQUIRED):
            if label not in allowed_dirs or after[label]['type'] != stat.S_IFDIR:
                raise ValueError('unexpected generated filesystem entry')
        if sha(regular_bytes(local_path(base_factory), MAX_IMAGE_BYTES)) != base_sha256:
            raise ValueError('base changed during build')
        validate_payload_tree(payload_tree, payload_sha256, channel_class=channel_class)
        image = _rebuild_factory(original, fs)
        # Publish complete bytes atomically without overwriting a concurrently created path.
        staged = work/'checked-factory.bin'
        with staged.open('xb') as stream:
            stream.write(image)
            stream.flush()
            os.fsync(stream.fileno())
        readback_bytes = regular_bytes(staged, MAX_IMAGE_BYTES)
        if sha(readback_bytes) != sha(image):
            raise ValueError('staged factory byte readback mismatch')
        factory_structure(readback_bytes)
        os.link(staged, destination)
    actual = regular_bytes(destination, MAX_IMAGE_BYTES)
    if sha(actual) != sha(image):
        raise ValueError('emitted factory byte readback mismatch')
    factory_structure(actual)
    result.update(state='TOOL_VALIDATED_FACTORY_CANDIDATE', image_emitted=True,
                  native_tools_executed=True, profile_declared=profile, sha256=sha(image),
                  channel_class_declared=channel_class, watchdog_budget_s=120 if channel_class=='dfs' else 45,
                  payload=readback, bytes=len(image), vendor_signature_verified=False)
    atomic_write(destination.with_suffix(destination.suffix+'.json'), json.dumps(result, indent=2)+'\n')
    return result


def build_source_receipt(root: Path = ROOT) -> dict:
    sources = [snapshot(root, label) for label in (
        SELF, 'tests/test_stage983a_squashfs_factory_contract.py',
        'tools/verify/stage779_822_offline_common.py')]
    if not all(source['available'] for source in sources):
        raise ValueError('required source contract missing')
    payload_sources = [snapshot(root, 'firmware/openwrt/pbe5ac_gen2_ptp_kit/' + name)
                       for name in ('99-fmx-pbe5ac-ptp', 'fmx_ptp_rollback_watchdog.sh',
                                    'fmx_pbe_lbe_runtime_transaction.sh')]
    payload_notes = ''.join(f"- {Path(item['path']).name}: {item.get('sha256', 'UNAVAILABLE')}.\n"
                            for item in payload_sources)
    data = receipt(983, 'Local SquashFS factory fail-closed source contract', sources)
    data.update(evidence_provenance_class='CONFIRMED_STATIC_BINARY',
                provenance_scope='executable source and synthetic contract tests only',
                native_image_emission='NOT_EXECUTED', packaging_readiness='BLOCKED',
                blockers=['REVIEWED_ACTIVE_BOOTSTRAP_REQUIRED', 'BOUND_LOCAL_NATIVE_TOOLCHAIN_REQUIRED',
                          'PINNED_LOCAL_BASE_AND_COMPLETE_PAYLOAD_TREE_REQUIRED'],
                supported_declared_profiles=list(PROFILES), required_payload=list(REQUIRED),
                payload_source_inspection=payload_sources,
                payload_source_inspection_scope='current source hashes only; no executable-mode, rootfs wiring, native image or physical acceptance',
                qdisc_mode='auto', physical_acceptance='UNKNOWN', vendor_signature_verified=False,
                source_only_release=True, deployment_authorized=False)
    return save(root, STEM, data,
         'This is a local source contract; no native image was emitted or installed in this stage.\n'
         'The requested generator path was absent; the older remote backend is not imported or executed.\n'
         'Inspection is the default and never invokes an executable, resolves a radio or reads firmware.\n'
         'Explicit build requires local POSIX root, a pinned SquashFS toolchain, base SHA256, declared board profile and private new output.\n'
         'Four exact rootfs paths, single-link regular files,0755 modes and source hashes are mandatory.\n'
         'Bootstrap must execute the runtime helper with --qdisc-mode auto; comments/string presence do not satisfy wiring.\n'
         'Bootstrap and rc.local accept only complete straight-line launch templates; unreachable commands are rejected.\n'
         'Watchdog and transaction bytes must equal the current reviewed canonical repository sources; caller hashes cannot approve alternatives.\n'
         'rc.local must launch the guarded watchdog explicitly with --apply. Retired payloads are rejected.\n'
         'Native unsquashfs extraction, repack and independent extraction readback are mandatory before candidate emission.\n'
         'Unchanged filesystem entries retain hashes, types, modes, owners, symlinks, hardlinks and device metadata.\n'
         'OPEN/kernel/rootfs CRCs, bounded SquashFSv4 structure and unsigned ENDS layout are checked.\n'
         'Magic-only buffers and ZIP overlays cannot be accepted as SquashFS filesystems.\n'
         'PowerBeam/LiteBeam profile names are declared input metadata, not hardware identity attestation.\n'
         'Vendor RSA signature, native bootstrap interoperability, OTA rollback and physical compatibility are not accepted.\n'
         'Current retired bootstrap and absent bound native toolchain keep actual emission BLOCKED.\n'
         'No network/SSH, device operation, protected-partition write or memory ingestion occurs.\n'
         '\nCurrent payload source snapshots (static hashes only; no rootfs or mode acceptance):\n' + payload_notes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--recipe', type=Path, help='Local JSON with all explicit pack_factory parameters')
    args = parser.parse_args(argv)
    if not args.build:
        print(json.dumps(dict(state='PLANNED', native_tools_executed=False, image_emitted=False)))
        return 0
    try:
        if args.recipe is None:
            raise ValueError('explicit local recipe required')
        values = strict_object(regular_bytes(local_path(args.recipe)))
        values['toolchain'] = Toolchain(**values.pop('toolchain'))
        values['execute'] = True
        if 'root' in values:
            raise ValueError('CLI output scope cannot replace repository root')
        result = pack_factory(**values)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.SubprocessError):
        result = dict(state='FAILED_CLOSED', image_emitted=False, flash_approved=False,
                      physical_acceptance='UNKNOWN')
        atomic_write(ROOT/'.git/stage983a/last_factory_build.json', json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
