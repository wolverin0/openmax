"""Synthetic protocol/layout tests only; never emit or certify a native image."""
import json
from pathlib import Path
import struct
import subprocess
import zlib

import pytest

from firmware.openwrt import build_universal_pbe5ac_lbe5ac_openwrt_factory as s


@pytest.fixture
def payload(tmp_path, monkeypatch):
    tree = tmp_path/'payload'
    canonical = s.ROOT/'firmware/openwrt/pbe5ac_gen2_ptp_kit'
    helper = (canonical/'fmx_pbe_lbe_runtime_transaction.sh').read_bytes()
    contents = {
        s.REQUIRED[0]: b'#!/bin/sh\nset -eu\nexec /usr/sbin/fmx_pbe_lbe_runtime_transaction.sh --apply --identity /etc/fmx/identity --state-dir /tmp/native --qdisc-mode auto\n',
        s.REQUIRED[1]: (canonical/'fmx_ptp_rollback_watchdog.sh').read_bytes(),
        s.REQUIRED[2]: helper,
        s.REQUIRED[3]: ('#!/bin/sh\nset -eu\n/usr/sbin/fmx_ptp_rollback_watchdog.sh --apply --identity /etc/fmx/identity --state-dir /tmp/native --watch-state-dir /tmp/watchdog --peer test-peer --channel-class non-dfs --transaction-sha256 '+s.sha(helper)+' --qdisc-mode auto &\nexit 0\n').encode(),
    }
    for label, blob in contents.items():
        path = tree/label
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
    # Windows cannot attest POSIX image modes; model the native readback contract.
    monkeypatch.setattr(s, '_mode', lambda path: 0o755)
    return tree, {label:s.sha(blob) for label,blob in contents.items()}


def rewrite(payload, label, blob):
    tree, hashes = payload
    (tree/label).write_bytes(blob)
    hashes[label] = s.sha(blob)


def protocol_fs():
    blob = bytearray(256)
    blob[:4] = b'hsqs'
    struct.pack_into('<I', blob, 12, 262144)
    struct.pack_into('<HH', blob, 20, 4, 18)
    struct.pack_into('<HH', blob, 28, 4, 0)
    struct.pack_into('<Q', blob, 40, 128)
    struct.pack_into('<QQ', blob, 64, 96, 112)
    return bytes(blob)


@pytest.fixture(scope='module')
def protocol_factory():
    fs = protocol_fs()
    slot = 0x410000
    end = s.SQUASHFS_OFFSET+slot+4
    blob = bytearray(end+8+264)
    blob[:4] = b'OPEN'
    struct.pack_into('>I', blob, 260, zlib.crc32(blob[:260]) & 0xFFFFFFFF)
    blob[0x10C:0x116] = b'PARTkernel'
    struct.pack_into('>I', blob, 0x10C+48, s.ROOTFS_HEADER-8-(0x10C+56))
    struct.pack_into('>II', blob, s.ROOTFS_HEADER-8, zlib.crc32(blob[0x10C:s.ROOTFS_HEADER-8]) & 0xFFFFFFFF, 0)
    blob[s.ROOTFS_HEADER:s.ROOTFS_HEADER+10] = b'PARTrootfs'
    struct.pack_into('>I', blob, s.ROOTFS_HEADER+48, end-s.ROOTFS_DATA)
    blob[s.SQUASHFS_OFFSET:s.SQUASHFS_OFFSET+len(fs)] = fs
    blob[s.SQUASHFS_OFFSET+len(fs):end-4] = b'\xff'*(slot-len(fs))
    blob[end-4:end] = b'\xde\xad\xc0\xde'
    struct.pack_into('>II', blob, end, zlib.crc32(blob[s.ROOTFS_HEADER:end]) & 0xFFFFFFFF, 0)
    blob[end+8:end+12] = b'ENDS'
    return bytes(blob)


def test_inspect_never_calls_tools_or_reads_inputs(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(s.subprocess, 'run', lambda *a,**k: pytest.fail('tool invoked'))
    assert s.main([]) == 0
    assert json.loads(capsys.readouterr().out)['state'] == 'PLANNED'
    assert s.pack_factory(base_factory=tmp_path/'absent', base_sha256='bad', payload_tree=tmp_path,
        payload_sha256={}, profile='wrong', output=tmp_path/'absent.bin', channel_class='wrong')['image_emitted'] is False


def test_exact_payload_contract_and_linked_watchdog(payload):
    result = s.validate_payload_tree(*payload, channel_class='non-dfs')
    assert result['state'] == 'PAYLOAD_TREE_VALIDATED'
    assert len(result['members']) == 4
    assert result['physical_acceptance'] == 'UNKNOWN'


@pytest.mark.parametrize('label', [s.REQUIRED[0], s.REQUIRED[3]])
@pytest.mark.parametrize('wrapper', ['exit 0\n{launch}', 'return 0\n{launch}',
                                   'unused() {{\n{launch}\n}}', 'if false; then\n{launch}\nfi'])
def test_unreachable_launch_is_rejected_even_with_matching_hash(payload, label, wrapper):
    original = (payload[0]/label).read_text()
    launch = next(line for line in original.splitlines() if '/usr/sbin/' in line)
    rewrite(payload, label, ('#!/bin/sh\n'+wrapper.format(launch=launch)+'\n').encode())
    with pytest.raises(ValueError):
        s.validate_payload_tree(*payload)


@pytest.mark.parametrize('label', [s.REQUIRED[1], s.REQUIRED[2]])
def test_caller_hash_cannot_approve_inert_watchdog_or_transaction(payload, label):
    old_hash = payload[1][label]
    rewrite(payload, label, b'#!/bin/sh\n# SOURCE_STAGE984_WATCHDOG_V1\nexit 0\n')
    if label == s.REQUIRED[2]:
        text = (payload[0]/s.REQUIRED[3]).read_text().replace(old_hash, payload[1][label])
        rewrite(payload, s.REQUIRED[3], text.encode())
    with pytest.raises(ValueError):
        s.validate_payload_tree(*payload)


@pytest.mark.parametrize('label', s.REQUIRED)
def test_missing_file_rejected(payload, label):
    (payload[0]/label).unlink()
    with pytest.raises((ValueError, OSError)):
        s.validate_payload_tree(*payload)


def test_content_drift_and_hash_contract_completeness(payload):
    tree, hashes = payload
    (tree/s.REQUIRED[2]).write_bytes(b'#!/bin/sh\nexit 1\n')
    with pytest.raises(ValueError, match='hash mismatch'):
        s.validate_payload_tree(tree, hashes)
    hashes.pop(s.REQUIRED[2])
    with pytest.raises(ValueError, match='complete exact'):
        s.validate_payload_tree(tree, hashes)


def test_non_executable_mode_is_not_accepted(payload, monkeypatch):
    monkeypatch.setattr(s, '_mode', lambda path: 0o644)
    with pytest.raises(ValueError, match='executable0755'):
        s.validate_payload_tree(*payload)


def test_hardlinked_payload_is_not_accepted(payload, tmp_path):
    (tmp_path/'second-link').hardlink_to(payload[0]/s.REQUIRED[2])
    with pytest.raises(ValueError, match='single-link'):
        s.validate_payload_tree(*payload)


def test_symlink_or_reparse_metadata_is_not_followed(payload, monkeypatch):
    real = Path.lstat
    target = payload[0]/s.REQUIRED[2]
    def metadata(path, *a, **k):
        info = real(path, *a, **k)
        if path == target:
            class Reparse:
                st_mode = info.st_mode
                st_file_attributes = 0x400
            return Reparse()
        return info
    monkeypatch.setattr(Path, 'lstat', metadata)
    with pytest.raises(ValueError, match='symlink or reparse'):
        s.validate_payload_tree(*payload)


@pytest.mark.parametrize('text', [
    '#!/bin/sh\n# /usr/sbin/fmx_pbe_lbe_runtime_transaction.sh --qdisc-mode auto\nexit 0\n',
    '#!/bin/sh\necho /usr/sbin/fmx_pbe_lbe_runtime_transaction.sh --qdisc-mode auto\n',
    '#!/bin/sh\nexec /usr/sbin/fmx_pbe_lbe_runtime_transaction.sh --qdisc-mode tc\n',
    '#!/bin/sh\n# PLANNED_RETIRED\nexit 0\n'])
def test_flag_presence_comments_echo_or_retired_payloads_cannot_pass(payload, text):
    rewrite(payload, s.REQUIRED[0], text.encode())
    with pytest.raises(ValueError):
        s.validate_payload_tree(*payload)


@pytest.mark.parametrize('mutation', [
    ('--apply', '--dry-run'), ('--transaction-sha256 ', '--transaction-sha256 invalid'),
    ('--identity /etc/fmx/identity', '--identity /etc/other'),
    ('--state-dir /tmp/native', '--state-dir /tmp/other'),
    ('--channel-class non-dfs', '--channel-class dfs'),
    ('--watch-state-dir /tmp/watchdog', '--watch-state-dir /tmp/native')])
def test_watchdog_arguments_and_native_helper_hash_are_bound(payload, mutation):
    tree, _ = payload
    old = (tree/s.REQUIRED[3]).read_text()
    rewrite(payload, s.REQUIRED[3], old.replace(*mutation).encode())
    with pytest.raises(ValueError):
        s.validate_payload_tree(*payload, channel_class='non-dfs')


def test_magic_only_or_bad_superblock_is_not_native_proof():
    for blob in [b'hsqs', b'hsqs'+b'\0'*200]:
        with pytest.raises(ValueError):
            s.squashfs_structure(blob)
    assert s.squashfs_structure(protocol_fs())['native_verified'] is False


def test_factory_crc_and_layout_without_hardware_claim(protocol_factory):
    info = s.factory_structure(protocol_factory)
    assert info['hardware_acceptance'] == 'UNKNOWN'
    assert not info['vendor_signature_verified']
    rebuilt = s._rebuild_factory(protocol_factory, protocol_fs())
    assert s.factory_structure(rebuilt)['squashfs']['native_verified'] is False
    assert rebuilt[:s.ROOTFS_HEADER] == protocol_factory[:s.ROOTFS_HEADER]


@pytest.mark.parametrize('offset', [1, 260, 0x10C+48, s.ROOTFS_HEADER+48, s.SQUASHFS_OFFSET+1])
def test_corrupt_crc_layout_is_rejected(protocol_factory, offset):
    blob = bytearray(protocol_factory)
    blob[offset] ^= 1
    with pytest.raises(ValueError):
        s.factory_structure(bytes(blob))


def test_no_toolchain_or_public_output_never_emits_image(payload, tmp_path):
    kwargs = dict(base_factory=tmp_path/'base.bin', base_sha256='a'*64,
                  payload_tree=payload[0], payload_sha256=payload[1], profile=s.PROFILES[0],
                  output=tmp_path/'.git/candidate.bin', channel_class='non-dfs', execute=True, root=tmp_path)
    with pytest.raises(ValueError, match='toolchain'):
        s.pack_factory(**kwargs)
    kwargs['output'] = tmp_path/'public.bin'
    with pytest.raises(ValueError, match='private output'):
        s.pack_factory(**kwargs)
    assert not kwargs['output'].exists()


def test_native_tool_nonzero_exit_is_propagated(monkeypatch):
    class Tool:
        calls = 0
        def verify(self): self.calls += 1
    tools = Tool()
    monkeypatch.setattr(s.subprocess, 'run', lambda *a,**k: subprocess.CompletedProcess(a[0],17,b'',b'failure'))
    with pytest.raises(RuntimeError, match='tool failed'):
        s._run(['unused-native-tool'], tools)
    assert tools.calls == 2


def test_explicit_build_missing_recipe_has_failed_closed_json(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(s, 'ROOT', tmp_path)
    assert s.main(['--build']) == 1
    assert json.loads(capsys.readouterr().out)['state'] == 'FAILED_CLOSED'
    record=json.loads((tmp_path/'.git/stage983a/last_factory_build.json').read_text())
    assert record['image_emitted'] is False and record['flash_approved'] is False


@pytest.mark.parametrize('blob', [b'{"profile":1,"profile":2}', b'{"size":NaN}', b'[]'])
def test_duplicate_nonfinite_or_nonobject_recipe_rejected(blob):
    with pytest.raises(ValueError):
        s.strict_object(blob)


def test_truthy_nonboolean_execute_cannot_start_tools(tmp_path):
    with pytest.raises(ValueError, match='boolean'):
        s.pack_factory(base_factory=tmp_path/'none', base_sha256='a'*64,
            payload_tree=tmp_path,payload_sha256={},profile=s.PROFILES[0],
            output=tmp_path/'.git/out.bin',channel_class='non-dfs',execute=1,root=tmp_path)


def test_unaffected_filesystem_manifest_detects_content_and_hardlink_changes(tmp_path):
    tree=tmp_path/'tree';tree.mkdir()
    first=tree/'first';first.write_bytes(b'original')
    (tree/'second').hardlink_to(first)
    before=s.filesystem_manifest(tree)
    assert before['first']['hardlink_group']==['first','second']
    first.write_bytes(b'changed')
    after=s.filesystem_manifest(tree)
    assert before['first']['sha256']!=after['first']['sha256']


def test_source_receipt_repeated_generation_retains_current_payload_hashes(tmp_path):
    source_names = (s.SELF, 'tests/test_stage983a_squashfs_factory_contract.py',
                    'tools/verify/stage779_822_offline_common.py')
    payload_names = tuple('firmware/openwrt/pbe5ac_gen2_ptp_kit/' + name for name in
                         ('99-fmx-pbe5ac-ptp', 'fmx_ptp_rollback_watchdog.sh',
                          'fmx_pbe_lbe_runtime_transaction.sh'))
    for name in source_names + payload_names:
        target = tmp_path/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(name.encode())
    first = s.build_source_receipt(tmp_path)
    doc = tmp_path/'docs'/f'{s.STEM.upper()}.md'
    first_doc = doc.read_bytes()
    assert s.build_source_receipt(tmp_path) == first
    assert doc.read_bytes() == first_doc
    assert [item['path'] for item in first['payload_source_inspection']] == list(payload_names)
    for item in first['payload_source_inspection']:
        assert item['sha256'] == s.sha((tmp_path/item['path']).read_bytes())
    (tmp_path/payload_names[1]).write_bytes(b'changed watchdog source')
    refreshed = s.build_source_receipt(tmp_path)
    assert refreshed['payload_source_inspection'][1]['sha256'] == s.sha(b'changed watchdog source')
    assert refreshed['payload_source_inspection'][1] != first['payload_source_inspection'][1]
    assert refreshed['native_image_emission'] == 'NOT_EXECUTED'
    assert refreshed['packaging_readiness'] == 'BLOCKED'
    assert refreshed['physical_acceptance'] == 'UNKNOWN'
