# PUBLIC_REDACTED_DERIVATIVE; original_sha256=c258e18a33b10a8bf844006488f2402a36b052a40336e72c82e45f834c8d8cb3
# Private originals are required for native replay.
"""Verify held PBE/LBE kit references; withhold v7 until native Quad is qualified."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.firmware import build_stage865a_pbe5ac_lbe5ac_tester_release_package_v6 as baseline
SCRIPT = 'tools/firmware/build_stage883a_pbe5ac_lbe5ac_verified_quad_patch_tester_kit_v7.py'
TEST = 'tests/test_stage883a.py'
DOC = 'docs/STAGE883A_PBE5AC_LBE5AC_VERIFIED_QUAD_PATCH_TESTER_KIT_V7.md'
OUT = 'artifacts/autoresearch/stage883a_pbe5ac_lbe5ac_verified_quad_patch_tester_kit_v7.json'
UPSTREAM = 'artifacts/autoresearch/stage879a_verified_pb070_and_pb080_native_sgmt_binaries.json'
OLD_RECEIPT = 'artifacts/autoresearch/stage865a_pbe5ac_lbe5ac_tester_release_package_v6.json'
REQUIRED_GATES = ('NATIVE_QUAD_CONTAINER_AND_PATCH_BYTES', 'INDEPENDENT_LOADABILITY_REVIEW', 'PBE5AC_RUNTIME_AND_45S_RECOVERY', 'LBE5AC_RUNTIME_AND_45S_RECOVERY', 'ZERO_ROGUE_DHCP_RUNTIME_AND_COLD_BOOT', 'BOARD_SPECIFIC_IMAGE_AND_ROLLBACK_VALIDATION')
DOC_TEXT = "<!-- doc-head: Stage883A held PBE/LBE hash verification and blocked v7 Quad-Patch tester kit -->\nFour v4 images are baseline references only. No v7 firmware is emitted.\n<!-- /doc-head -->\n\n# Stage883A: tester kit BLOCKED\n\nQuestion: can the verified native Quad-Patch be included in a compatible\nPowerBeam5AC Gen2 and LiteBeam5AC Gen2 public tester release?\nAnswer UNKNOWN; Stage879 has not emitted the native Quad binary.\nAttribution: external controller; future native behavior belongs to QCA firmware.\n\nThe verifier reuses Stage865's bounded checksum/path validation without invoking\nits producer. The pinned public_release_v4/SHA256SUMS.txt is checked, then the\nfour selected factory/sysupgrade files are freshly SHA256-verified.\nTheir bytes, names and labels remain HELD_PUBLIC_V4_REFERENCE_ONLY. They are\nnot renamed v7, copied to a release directory, placed in an archive or flashed.\nHashes prove local held-byte integrity only, not image configuration or ABI.\n\nPBE board0xe3d6 selects ubnt,powerbeam-5ac-gen2; LBE board0xe7f9 selects\nubnt,litebeam-ac-gen2. These are explicit selection metadata, not newly decoded\nDTB identity or runtime acceptance of every board revision.\n\nThe source865 receipt's canonical manifest hash and selected baseline references\nmust agree with the fresh checksum audit. Source879 is parsed and pinned, and\nits declared blockers are retained. Even quad_emitted=true or status=CONFIRMED\nalone cannot approve a kit: emitted native bytes, independent review and actual\nruntime/recovery on BOTH boards are required. Raw SGMT is not a flashable image\nor a complete QCA-ATH10K container and cannot be relabeled firmware-5.bin.\n\nRequired missing evidence also includes45-second rollback, zero-rogue-DHCP\nruntime plus cold-boot behavior, exact image matching and board-specific\nrollback validation. No '100% compatible' claim follows from metadata/tests.\n\nPublic candidate material consists only of a canonical JSON manifest embedded\nin the receipt: fixed board/profile fields, baseline filenames, sizes and hashes.\nNo configuration, credentials, internal addresses, native binary bytes, scripts\nor private evidence payload are exported. No ZIP/bin or release is created.\n\nRun `python tools/firmware/build_stage883a_pbe5ac_lbe5ac_verified_quad_patch_tester_kit_v7.py`.\nExit2 records BLOCKED; exit1 means invalid input and preserves the previous\nreceipt. Tests use disposable files and do not contact devices or producers.\nNext: resolve879's native PB070/PB080 contracts, independently qualify the\nQuad container, execute guarded RAM tests, then validate both-board recovery.\n"

def read_json(root, label):
    raw, pin = baseline.read_pin(root, label, 1024 ** 2)
    value = json.loads(raw, object_pairs_hook=baseline.c.pairs, parse_constant=baseline.c.invalid_constant)
    if not isinstance(value, dict):
        raise ValueError('receipt_object_required')
    baseline.canonical(value)
    return (value, pin)

def evaluate_upstream(report):
    if not isinstance(report, dict) or report.get('stage') != '879A':
        raise ValueError('stage879_receipt_required')
    if type(report.get('quad_emitted')) is not bool or not isinstance(report.get('emitted_binaries'), list):
        raise ValueError('explicit_quad_emission_and_inventory_required')
    return dict(status=report.get('status', 'UNKNOWN'), reported_quad_emitted=report['quad_emitted'], reported_binary_count=len(report['emitted_binaries']), native_quad_verified=False, independent_review_accepted=False, reported_blockers=report.get('blockers', []), limitation='Reported emission is not byte binding, native ABI, loadability or physical acceptance')

def build(root=ROOT):
    root = baseline.c.local_path(root)
    sums, sums_pin = baseline.read_pin(root, baseline.SUMS, 256 * 1024)
    if sums_pin['sha256'] != baseline.SUMS_PIN:
        raise ValueError('pinned_public_v4_checksum_manifest_drift')
    references = baseline.audit_checksums(root / baseline.BASE, sums.decode('ascii'))
    old, old_pin = read_json(root, OLD_RECEIPT)
    old_manifest = old.get('candidate_manifest')
    if not isinstance(old_manifest, dict) or baseline.c.sha(baseline.canonical(old_manifest)) != old.get('candidate_manifest_sha256'):
        raise ValueError('stage865_canonical_manifest_binding_mismatch')
    if old.get('baseline_references') != references:
        raise ValueError('stage865_reference_drift')
    upstream, upstream_pin = read_json(root, UPSTREAM)
    quad = evaluate_upstream(upstream)
    manifest = baseline.candidate_manifest(references)
    manifest['manifest_version'] = 7
    manifest['blockers'] = list(REQUIRED_GATES)
    manifest['purpose'] = 'BLOCKED_V7_KIT_PREPARATION_NOT_FIRMWARE'
    manifest['native_quad_verified'] = False
    sources = [sums_pin, old_pin, upstream_pin]
    result = dict(stage='883A', schema_version=1, status='BLOCKED', acceptance='NOT_ACCEPTED', source_bindings=sources, baseline_status='SELECTED_FOUR_LOCAL_HASHES_MATCH', baseline_references=references, checksum_scope='SELECTED_FOUR_HELD_V4_IMAGES_ONLY', upstream_native_quad=quad, blockers=list(REQUIRED_GATES), candidate_manifest=manifest, candidate_manifest_sha256=baseline.c.sha(baseline.canonical(manifest)), package_format='CANONICAL_JSON_MANIFEST_ONLY', package_exported=False, firmware_emitted=False, native_quad_verified=False, both_board_runtime_verified=False, approved_for_flash=False, approved_for_publish=False, runtime_compatibility='UNKNOWN', target_writes=False, network_access=False, implementation=baseline.read_pin(root, SCRIPT, 1024 ** 2)[1], analysis_dependencies=[baseline.read_pin(root, label, 1024 ** 2)[1] for label in (baseline.SCRIPT, 'tools/re/ground_up_release_common.py', 'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py')])
    for pin in sources + [dict(path=r['source_path'], bytes=r['bytes'], sha256=r['sha256']) for r in references]:
        if baseline.read_pin(root, pin['path'], baseline.MAX_IMAGE)[1] != pin:
            raise ValueError('input_changed_during_build')
    return result

def durable_json(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        root = baseline.c.local_path(args.root)
        result = build(root)
        baseline.c.write_doc(root / DOC, DOC_TEXT)
        result['outputs'] = {label: baseline.read_pin(root, label, 1024 ** 2)[1] for label in (DOC, TEST)}
        durable_json(root / OUT, result)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps(dict(status='ERROR', error=type(exc).__name__)), file=sys.stderr)
        return 1
    print(json.dumps(dict(stage='883A', status='BLOCKED', selected_baselines=4, package_exported=False, manifest_sha256=result['candidate_manifest_sha256'])))
    return 2
if __name__ == '__main__':
    raise SystemExit(main())
