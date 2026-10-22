"""PRE-PROD2 local-only package. No production execution implementation exists.

Reuses the existing rollback scaffold exclusively with recording stubs. Historical
file integrity is not current device identity, recovery qualification or authority.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import tempfile
import time
import zlib

from safety.preprod.rollback_snapshot import (RecoveryVerification, RollbackManager,
                                             TransferOutcome)

REPO = Path(__file__).resolve().parents[2]
EVIDENCE = REPO / 'artifacts/canary_panel1_guarida'
DEFAULT_OUT = EVIDENCE / 'preprod_guarida_20261022'
PROFILE = 'panel1_native_profile_20261019.json'
PROFILE_SHA = '05337f1b670fe850d78b8c00433fae2ef6d55f64bb7c94283c08f2de0479aaee'
BASELINE = 'panel1_native_baseline_20261019_ready'
BASELINE_SHA = '8f900a3f8803f8b79eca76655804e8620232d3a1ab3aee4a396ebc478f897924'
CANDIDATE = 'panel1_firmware_lap120_proven_v3_20261019.bin'
CANDIDATE_SHA = '2b34379d62cff6738e769c1dd613b6e82bd3b19092be936a54d1b55d416e69a5'
PACKAGE = 'lap120_stock_cycle_20261019_package/lap120-wa8725-full-region.sysupgrade.bin.gz'
PACKAGE_SHA = '8f640047424a946596de7125781b67bc3b8d52f78deb8793b195ce11c0b3d231'
STOCK_SHA = '92a5986bf2b809a355e5c17a5a444fa35d07cbbbc95a348778ca44f4896237aa'
OUTCOME = 'panel1_production_canary_20261020_outcome_verification.json'
OUTCOME_SHA = 'ea955878ac345ce5dfe6561571c5f92d614291eacde0cbfa946c926209757763'
IMAGE_BYTES, STOCK_BYTES = 7077888, 16121856
sha = lambda b: hashlib.sha256(b).hexdigest()


def require(ok, gate):
    if not ok:
        raise ValueError(gate)


def read_bound(root, name, digest, size=None):
    root, path = Path(root), Path(root) / name
    require(path.resolve().is_relative_to(root.resolve()) and not path.is_symlink()
            and path.is_file(), 'INPUT_NOT_REGULAR_OR_ESCAPES')
    data = path.read_bytes()
    require(sha(data) == digest and (size is None or len(data) == size), 'INPUT_HASH_OR_SIZE_MISMATCH')
    return data


def candidate_format(data):
    require(len(data) == IMAGE_BYTES, 'CANDIDATE_SIZE')
    f = struct.unpack('>7I4B32s', data[:64])
    header = bytearray(data[:64]); header[4:8] = b'\0' * 4
    require(f[0] == 0x27051956 and zlib.crc32(header) == f[1], 'UIMAGE_HEADER_CRC')
    require(0 < f[3] <= 0x290000 - 64 and zlib.crc32(data[64:64 + f[3]]) == f[6], 'UIMAGE_PAYLOAD_CRC')
    require(f[4:6] == (0x80060000, 0x80060000) and f[7:11] == (5, 5, 2, 3), 'UIMAGE_PLATFORM')
    require(data[0x290000:0x290004] == b'hsqs' and data[0x6b0000:0x6b0004] == bytes.fromhex('deadc0de'), 'SQUASHFS_GEOMETRY')
    return dict(uimage_header_crc=True, uimage_payload_crc=True, kernel_payload_bytes=f[3],
                squashfs_offset=0x290000, rootfs_data_marker_offset=0x6b0000,
                install_blocks=108, immutable_postboot_prefix_bytes=0x6b0000)


def inventory(evidence=EVIDENCE):
    """Read ONLY held local files; never import a device/credential adapter."""
    profile = json.loads(read_bound(evidence, PROFILE, PROFILE_SHA))
    baseline = json.loads(read_bound(evidence, BASELINE + '/receipt.json', BASELINE_SHA))
    outcome = json.loads(read_bound(evidence, OUTCOME, OUTCOME_SHA))
    require(profile['candidate_sha256'] == CANDIDATE_SHA
            and profile['ethernet_mac'] == '78:45:58:a1:34:a2', 'HISTORICAL_TARGET_PROFILE')
    require(outcome['canary_decision'] == 'REJECT' and outcome['production_candidate_accepted'] is False
            and outcome['stock_restored_verified'] is True, 'HISTORICAL_OUTCOME_MUST_REMAIN_REJECT')
    blobs, captures = {}, {}
    for name, row in baseline['capture'].items():
        data = read_bound(evidence, BASELINE + '/' + name, row['sha256'], row['bytes'])
        blobs[name] = data
        captures[name] = dict(bytes=len(data), sha256=sha(data), historical_only=True)
    require(sha(blobs['board.info']) == profile['board_sha256'], 'BOARD_HASH_BINDING')
    # Load only the already existing, inspected pure offline stock validator.
    path = REPO / 'safety/recovery/prepare_panel1_stock_restore.py'
    spec = importlib.util.spec_from_file_location('_preprod_stock_validator', path)
    validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
    board = validator.parse_board(blobs['board.info'])
    validator.validate_layout(blobs['mtd.txt'])
    stock_kernel = validator.validate_uimage(blobs['mtd2.bin'])
    require(board['board.sysid'] == '0xe8e5' and board['board.model'] == 'LAP-120', 'BOARD_PROFILE')
    require(blobs['system.cfg'] == blobs['running.cfg'] and blobs['mtd4.bin'] == blobs['mtd4.recheck'], 'HELD_CONFIG_BRACKET')
    raw = blobs['mtd2.bin'] + blobs['mtd3.bin']
    require(len(raw) == STOCK_BYTES and sha(raw) == STOCK_SHA, 'OWN_STOCK_REGION')
    package = read_bound(evidence, PACKAGE, PACKAGE_SHA)
    decoder = zlib.decompressobj(31)
    decoded = decoder.decompress(package, STOCK_BYTES + 1)
    require(decoder.eof and not decoder.unconsumed_tail and decoded == raw, 'STOCK_PACKAGE_DECODE')
    candidate = read_bound(evidence, CANDIDATE, CANDIDATE_SHA, IMAGE_BYTES)
    writer = read_bound(evidence, 'fmx_flash_writer_panel1_native_20261019', profile['binary_sha256'])
    references = [PROFILE, BASELINE + '/receipt.json', OUTCOME, PACKAGE,
                  'panel1_return_own_stock_20261020.py', 'fmx_flash_writer_panel1_native_20261019.c',
                  'fmx_flash_writer_panel1_native_20261019.build.json']
    sources = {n: sha((Path(evidence) / n).read_bytes()) for n in references}
    sources.update({n: sha((REPO / n).read_bytes()) for n in (
        'orchestration/rollback/workflow.py', 'orchestration/power/smart_power.py',
        'safety/recovery/prepare_panel1_stock_restore.py', 'safety/preprod/rollback_snapshot.py')})
    return dict(target=dict(label='Panel1-Guarida', board_sysid='0xe8e5', board_model='LAP-120',
                           ethernet_mac=profile['ethernet_mac'], board_sha256=profile['board_sha256']),
                historical_candidate=dict(status='DRAFT_REJECTED_NOT_QUALIFIED', sha256=CANDIDATE_SHA,
                    bytes=IMAGE_BYTES, geometry=candidate_format(candidate)),
                historical_backup=dict(status='VERIFIED_LOCAL_FILES_NOT_FRESH_DEVICE_STATE', captures=captures,
                    firmware_sha256=STOCK_SHA, firmware_bytes=STOCK_BYTES, stock_kernel=stock_kernel,
                    return_package_sha256=PACKAGE_SHA, return_package_bytes=len(package)),
                historical_writer=dict(sha256=sha(writer), bytes=len(writer), armed=False), sources=sources,
                candidate=candidate, package=package)


class RecordingPower:
    """Only an action recorder. Has no driver, target or connector."""
    def __init__(self, actions): self.actions = actions
    def trigger_tftp_recovery(self, *args, **kwargs):
        self.actions.append('SIMULATED_POWER_RESET'); return True


def rollback_dry_run(image_path, image_sha):
    """Failure injection into existing scaffold; NO real power/transfer adapters."""
    results = []
    for case in ('health_failure', 'transfer_timeout', 'no_write_then_tftp', 'postboot_failure', 'bad_image'):
        actions = []
        manager = RollbackManager('DRY_RUN_NOT_A_HOST', 0, Path(image_path),
                                  '0' * 64 if case == 'bad_image' else image_sha, RecordingPower(actions))
        def soft(path):
            actions.append('SIMULATED_SOFT_TRANSFER')
            if case == 'transfer_timeout': raise TimeoutError('fixture timeout')
            return TransferOutcome.NO_WRITE if case == 'no_write_then_tftp' else TransferOutcome.DELIVERED
        def tftp(path):
            actions.append('SIMULATED_TFTP_TRANSFER'); return TransferOutcome.DELIVERED
        def verify(context):
            actions.append('SIMULATED_POSTBOOT_VERIFICATION')
            return RecoveryVerification(context.target_host, True, True, True, True,
                case != 'postboot_failure', 'SIMULATION_NOT_HARDWARE_EVIDENCE', context.attempt_id,
                context.image_sha256, time.time())
        # Expired/failed watchdog condition dispatches directly to the existing
        # rollback state machine; no scheduler/service/deployment is installed.
        incident = manager.execute_recovery('SIMULATED_WATCHDOG_HEALTH_FAILURE', soft, tftp,
            reset_hold_sec=0, settle_delay_sec=0, verify_recovery_fn=verify)
        first_actions = list(actions)
        if case in ('transfer_timeout', 'postboot_failure'):
            manager.execute_recovery('SIMULATED_RETRY_MUST_BE_BLOCKED', soft, tftp, verify_recovery_fn=verify)
            require(actions == first_actions, 'DRY_RUN_AMBIGUOUS_ACTION_RETRIED')
        expected = case in ('health_failure', 'no_write_then_tftp')
        require(incident.success is expected, 'DRY_RUN_UNEXPECTED_RESULT')
        if case == 'bad_image': require(not actions, 'DRY_RUN_BAD_IMAGE_ACTION')
        if case == 'transfer_timeout': require(actions == ['SIMULATED_SOFT_TRANSFER'], 'DRY_RUN_TIMEOUT_ESCALATION')
        results.append(dict(case=case, actions=actions, simulated_recovery_confirmed=incident.success,
                            recovery_uncertain=manager.recovery_uncertain, expected_result_verified=True))
    return dict(status='PASS_RECORDING_STUB_FAILURE_PATHS_ONLY', scenarios=results,
                device_operations=False, physical_recovery_qualified=False)


def _write(path, data):
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0), 0o600), 'wb') as f:
        f.write(data); f.flush(); os.fsync(f.fileno())


def prepare(output=DEFAULT_OUT, evidence=EVIDENCE):
    output = Path(output)
    require(not output.exists() and not output.is_symlink(), 'OUTPUT_ALREADY_EXISTS')
    data = inventory(evidence)
    output.mkdir(mode=0o700)
    # Copies are byte-identical held inputs, not rebuilt firmware. They contain
    # production config/auth material within the draft filesystem: KEEP PRIVATE.
    _write(output / 'draft-v3.REJECTED.bin', data.pop('candidate'))
    _write(output / 'own-stock.return.bin.gz', data.pop('package'))
    dry = rollback_dry_run(output / 'own-stock.return.bin.gz', PACKAGE_SHA)
    manifest = dict(schema='preprod-guarida-offline-v1', status='HOLD',
        preparation_status='PASS_OFFLINE_INTEGRITY_AND_RECORDING_DRY_RUN',
        production_execution_enabled=False, selected_deployment_candidate=None,
        publish_bundle=False, contains_sensitive_firmware=True, device_operations=False,
        prohibited_writes=['bootloader', 'u-boot-env', 'ART', 'factory', 'calibration', 'MAC', 'cfg'],
        historical_firmware_region=dict(start=0x50000, end_exclusive=0xfb0000),
        protected_regions=[dict(name=n, start=a, end_exclusive=b) for n,a,b in (
            ('bootloader',0,0x40000),('environment',0x40000,0x50000),('cfg',0xfb0000,0xff0000),('EEPROM',0xff0000,0x1000000))],
        rollback_dry_run=dry, blockers=[
            'No deployment candidate has been selected; historical v3 production service was REJECTED.',
            'Bench image773f is a different radio-off/LAN bench configuration, not production qualification.',
            'Current production identity/config/backups/management route/health are UNKNOWN: no production reads authorized.',
            'Historical successful reachable own-stock return is not failed-boot/TFTP/power-cycle recovery proof.',
            'Automatic real rollback watchdog and boot-loss recovery for exact target remain UNQUALIFIED.',
            'A new exact candidate/profile/runtime admission and independent review are required before any execution order.'
        ], source_sha256=sha(Path(__file__).read_bytes()), **data)
    _write(output / 'manifest.json', json.dumps(manifest, indent=2).encode())
    checklist = ('PRE-PROD2: HOLD. LOCAL PREPARATION ONLY. DO NOT UPLOAD OR EXECUTE.\n'
        'PRIVATE BUNDLE: draft firmware embeds production configuration/auth material; never publish.\n'
        'No production installer or credential loader is included. --execute is always refused.\n'
        '1. Select and independently qualify an exact production candidate; keep v3 REJECT unchanged.\n'
        '2. Under a separate authorized order, obtain fresh exact identity/layout/all-backup/health/route evidence.\n'
        '3. Prove usable failed-boot recovery and an independent bounded rollback watchdog on exact hardware.\n'
        '4. Bind image/size/SHA/own-stock return and protected partition exclusion to that new order.\n'
        '5. Require traffic/service acceptance, not association alone; retain all failure receipts.\n'
        'Legacy install_openwrt_ddunlock is NOT a Panel1 installer and must never be reused.\n'
        'Recording stubs prove control flow only. No real rollback/recovery/deployment was performed.\n')
    _write(output / 'CHECKLIST.txt', checklist.encode())
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-local', action='store_true')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args(argv)
    if args.execute:
        parser.error('PRODUCTION_EXECUTION_DISABLED_BY_PREPROD2_ORDER')
    if not args.prepare_local:
        print(json.dumps(dict(status='PLAN_ONLY', production_execution_enabled=False,
            selected_deployment_candidate=None, deployment_readiness='HOLD')))
        return 0
    result = prepare(args.output)
    print(json.dumps({k: result[k] for k in ('status', 'preparation_status', 'production_execution_enabled')}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
