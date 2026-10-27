# PUBLIC_REDACTED_DERIVATIVE; original_sha256=f32b4cb263fd5241db2273116f530e0ee0e3d3de962115b7d3b8a43da1d63064
# Private originals are required for native replay.
"""Offline v6 candidate manifest; never builds, copies or approves firmware."""
from __future__ import annotations
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.re import ground_up_release_common as c
SCRIPT = 'tools/firmware/build_stage865a_pbe5ac_lbe5ac_tester_release_package_v6.py'
TEST = 'tests/test_stage865a.py'
DOC = 'docs/STAGE865A_PBE5AC_LBE5AC_TESTER_RELEASE_PACKAGE_V6.md'
OUT = 'artifacts/autoresearch/stage865a_pbe5ac_lbe5ac_tester_release_package_v6.json'
BASE = 'firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4'
SUMS = BASE + '/SHA256SUMS.txt'
SUMS_PIN = '864f2a958e1b50e42386a981a6bf16a76484bdf5b942b228cbac4d9467c76752'
PB070 = 'artifacts/autoresearch/stage806a_pb070_xtensa_rc_probe_per_sgmt_patch.json'
ROUTES = ('firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py', 'tools/firmware/package_public_wa_tester_release.py')
BOARDS = {'pbe5ac-gen2': {'board_id': '0xe3d6', 'profile': 'ubnt,powerbeam-5ac-gen2'}, 'lbe5ac-gen2': {'board_id': '0xe7f9', 'profile': 'ubnt,litebeam-ac-gen2'}}
REQUIRED = {f'openwrt-24.10.4-ubnt-{board}-openmax-public-{kind}.bin': (board, kind) for board in BOARDS for kind in ('factory', 'sysupgrade')}
BLOCKERS = ['NATIVE_QUAD_NOT_VALIDATED', 'V5_BASELINE_NOT_VALIDATED', 'PBE5AC_RUNTIME_AND_RECOVERY_NOT_VALIDATED', 'LBE5AC_RUNTIME_AND_RECOVERY_NOT_VALIDATED']
MAX_IMAGE = 32 * 1024 ** 2
DOC_TEXT = '<!-- doc-head: Stage865A blocked PBE5AC/LBE5AC v6 candidate manifest and verified held baseline hashes -->\nManifest version6 is not a new firmware image or runtime compatibility claim.\n<!-- /doc-head -->\n\n# Stage865A\n\nThis offline step prepares a deterministic public candidate manifest for\nPowerBeam5AC Gen2 and LiteBeam5AC Gen2. It neither builds nor copies firmware.\nRun `python tools/firmware/build_stage865a_pbe5ac_lbe5ac_tester_release_package_v6.py`.\nExit1 means the receipt was prepared but release gates remain BLOCKED; exit2\nmeans invalid local evidence and leaves the prior receipt unchanged.\n\n## Reused routes and selected baseline\n\nThe existing OpenWrt core builder and Stage170 WA public packager are inspected\nand hashed as source references only, never imported or executed by this tool.\nThe four selected factory/sysupgrade images come from public_release_v4.\nThe complete SHA256SUMS.txt text is pinned; every line is parsed for safe names,\nwhile only the four selected binary references are read and hash-checked.\nOther manifest members are not claimed verified. Paths, duplicate/case aliases,\ndevice names, symlinks, remote paths and oversized reads fail closed.\n\nEach board retains its own profile and identity metadata: PBE0xe3d6 with\nubnt,powerbeam-5ac-gen2; LBE0xe7f9 with ubnt,litebeam-ac-gen2. These mappings\nare declared selection metadata, not newly decoded image/DTB or device proof.\nThe v4 images remain BASELINE_REFERENCE_ONLY: they are never relabeled as v5/v6.\nLocal checksum agreement is held-byte integrity, not an authenticated release,\nvalid-container audit, embedded configuration audit or proof of safe flashing.\n\n## Candidate public material\n\nThe receipt embeds a canonical JSON manifest and its SHA256. Public material is\nconstructed from fixed fields, board identities, selected filenames, sizes and\nhashes only. No source configuration, credentials, shell script, proprietary\nmodule, internal address or raw evidence payload is copied into the candidate.\nThe existing binary files are hashed but not included in a new package. No ZIP,\nrelease directory, install/apply script or export of firmware bytes is created.\nNative firmware export and publication remain prohibited in this step.\n\n## Gates and evidence limits\n\nThe manifest is unconditionally BLOCKED pending independently validated native\nquad support, a qualified v5 baseline and runtime/recovery evidence for BOTH\nexact board revisions. Metadata, a PASS label or copied getters cannot unlock it.\nThe saved Stage806 PB-070 receipt is hashed and parsed if present; its patch\ncount is recorded as a reported field, not accepted native behavior. Missing\noptional evidence stays MISSING. No target access, network, flash, deployment,\nregulatory change, boot test or firmware producer invocation occurs here.\n\nThe result demonstrates bounded local manifest construction and checksum\nvalidation only. It does not establish performance gains,100% compatibility,\nwatchdog installation, protected backup/restore or physical acceptance.\n'

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')

def member_name(value):
    if not isinstance(value, str) or len(value) > 240 or (not re.fullmatch('[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', value)):
        raise ValueError('safe_relative_member_required')
    for part in value.split('/'):
        if part in ('.', '..') or part.endswith('.') or re.fullmatch('(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\\..*)?', part, re.I):
            raise ValueError('unsafe_member_component')
    return value

def parse_checksums(text):
    if not isinstance(text, str) or not 1 <= len(text) <= 256 * 1024:
        raise ValueError('bounded_checksum_text_required')
    rows = {}
    folded = set()
    lines = text.splitlines()
    if not 1 <= len(lines) <= 512:
        raise ValueError('checksum_line_limit')
    for line in lines:
        match = re.fullmatch('([0-9a-f]{64}) [ *]([^\\r\\n]+)', line)
        if not match:
            raise ValueError('sha256sum_line_required')
        name = member_name(match[2])
        if name.casefold() in folded:
            raise ValueError('duplicate_checksum_member')
        folded.add(name.casefold())
        rows[name] = match[1]
    return rows

def read_pin(root, label, maximum):
    member_name(label)
    path = c.local_path(c.local_path(root) / label)
    with path.open('rb') as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise ValueError('bounded_input_limit')
    return (data, dict(path=label, bytes=len(data), sha256=c.sha(data)))

def audit_checksums(base, text):
    base = c.local_path(base)
    sums = parse_checksums(text)
    if not set(REQUIRED) <= sums.keys():
        raise ValueError('four_selected_images_required')
    verified = []
    for name, (board, kind) in sorted(REQUIRED.items()):
        data, p = read_pin(base, name, MAX_IMAGE)
        if not data or p['sha256'] != sums[name]:
            raise ValueError('selected_image_checksum_mismatch:' + name)
        verified.append(dict(board=board, image_kind=kind, **BOARDS[board], source_path=BASE + '/' + name, bytes=p['bytes'], sha256=p['sha256']))
    return verified

def candidate_manifest(references):
    if not isinstance(references, list) or len(references) not in (0, 4):
        raise ValueError('zero_or_four_references_required')
    clean = []
    seen = set()
    for row in references:
        if not isinstance(row, dict):
            raise ValueError('reference_object_required')
        board = row.get('board')
        kind = row.get('image_kind')
        if not isinstance(board, str) or board not in BOARDS or kind not in ('factory', 'sysupgrade'):
            raise ValueError('known_board_and_image_kind_required')
        name = f'openwrt-24.10.4-ubnt-{board}-openmax-public-{kind}.bin'
        if name in seen or row.get('source_path') != BASE + '/' + name:
            raise ValueError('unique_exact_baseline_path_required')
        seen.add(name)
        if any((row.get(k) != v for k, v in BOARDS[board].items())):
            raise ValueError('board_identity_metadata_mismatch')
        c.integer(row.get('bytes'), 'image_bytes', 1, MAX_IMAGE)
        digest = row.get('sha256')
        if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('sha256_required')
        clean.append({k: row[k] for k in ('board', 'board_id', 'profile', 'image_kind', 'source_path', 'bytes', 'sha256')})
    if clean and seen != set(REQUIRED):
        raise ValueError('complete_board_kind_inventory_required')
    result = dict(manifest_version=6, status='BLOCKED', boards=BOARDS, baseline='HELD_PUBLIC_V4_REFERENCE_ONLY', baseline_references=sorted(clean, key=lambda x: x['source_path']), blockers=list(BLOCKERS), native_quad_verified=False, v5_baseline_verified=False, both_board_runtime_verified=False, images_included=False, new_firmware_built=False, approved_for_flash=False, approved_for_publish=False, runtime_compatibility='UNKNOWN')
    public = canonical(result).decode('ascii')
    for token in re.findall('\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b', public):
        address = ipaddress.ip_address(token)
        if address.is_private or address.is_loopback or address.is_link_local:
            raise ValueError('nonpublic_address_in_manifest')
    return result

def build(root=ROOT):
    root = c.local_path(root)
    sources = []
    references = []
    gaps = list(BLOCKERS)
    try:
        raw, sums_pin = read_pin(root, SUMS, 256 * 1024)
    except FileNotFoundError:
        baseline_status = 'MISSING'
        gaps.append('PUBLIC_V4_CHECKSUM_MANIFEST_MISSING')
    else:
        if sums_pin['sha256'] != SUMS_PIN:
            raise ValueError('pinned_public_v4_checksum_manifest_drift')
        sources.append(sums_pin)
        references = audit_checksums(root / BASE, raw.decode('ascii'))
        baseline_status = 'SELECTED_FOUR_LOCAL_HASHES_MATCH'
    pb070 = dict(availability='MISSING', native_quad_verified=False)
    try:
        raw, p = read_pin(root, PB070, 1024 ** 2)
    except FileNotFoundError:
        pass
    else:
        sources.append(p)
        report = json.loads(raw, object_pairs_hook=c.pairs, parse_constant=c.invalid_constant)
        canonical(report)
        if not isinstance(report, dict) or not isinstance(report.get('summary'), dict):
            raise ValueError('pb070_summary_object_required')
        count = c.integer(report['summary'].get('patch_emitted'), 'patch_emitted', 0, 1000000)
        pb070.update(availability='PRESENT_UNQUALIFIED', reported_patch_emitted=count)
    for route in ROUTES:
        try:
            _, p = read_pin(root, route, 1024 ** 2)
        except FileNotFoundError:
            gaps.append('SOURCE_ROUTE_MISSING:' + route)
        else:
            sources.append(p)
    manifest = candidate_manifest(references)
    result = dict(stage='865A', schema_version=1, status='BLOCKED', baseline_status=baseline_status, baseline_references=references, checksum_scope='SELECTED_FOUR_BASELINE_REFERENCE_FILES_ONLY', all_manifest_members_checked=False, pb070=pb070, blockers=gaps, candidate_manifest=manifest, candidate_manifest_sha256=c.sha(canonical(manifest)), package_format='CANONICAL_JSON_MANIFEST_ONLY', package_exported=False, source_bindings=sources, implementation=read_pin(root, SCRIPT, 1024 ** 2)[1], analysis_dependencies=[read_pin(root, p, 1024 ** 2)[1] for p in ('tools/re/ground_up_release_common.py', 'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py')], boundary=dict(target_access=False, network_access=False, producer_execution=False, firmware_build=False, firmware_export=False, release_published=False, flash_approved=False, physical_acceptance=False), new_hardware_results=0, five_pillar_compliance={'pillar_a_ground_up_re_and_knob_catalog': 'Existing WA routes and exact board/profile metadata are held-byte references; no native quad ABI accepted.', 'pillar_b_hyperresearch_and_scholar_reactor': 'Offline source inspection only; no new literature or RF causal evidence.', 'pillar_c_karpathy_autoresearch_and_watchdog': 'Deterministic failclosed manifest construction; no target watchdog installation or experiment.', 'pillar_d_scientific_pareto_validation': 'Local checksum and fixture validation only; both-board runtime/recovery and v5 baseline remain BLOCKED.', 'pillar_e_memory_master_claim_id': 'No new empirical claim or memory write; Stage865A local evidence only.'})
    for p in sources + [dict(path=r['source_path'], bytes=r['bytes'], sha256=r['sha256']) for r in references]:
        if read_pin(root, p['path'], MAX_IMAGE)[1] != p:
            raise ValueError('input_changed_during_build')
    c.write_doc(root / DOC, DOC_TEXT)
    result['outputs'] = {DOC: read_pin(root, DOC, 1024 ** 2)[1], TEST: read_pin(root, TEST, 1024 ** 2)[1]}
    c.write_json(root / OUT, result)
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = build(args.root)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps(dict(status='ERROR', error=type(exc).__name__)), file=sys.stderr)
        return 2
    print(json.dumps(dict(status=result['status'], manifest_sha256=result['candidate_manifest_sha256'], package_exported=False), sort_keys=True))
    return 1
if __name__ == '__main__':
    raise SystemExit(main())
