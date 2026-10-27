#!/usr/bin/env python3
"""Build a v22 source-reference matrix; never build, load or install firmware."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage849a_universal_wa_xc_xw_v22_release_matrix'
REQUIRED_SOURCES = (
    'firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh',
    'firmware/openwrt/common/fmx_pb060_triple_patch_loader.sh',
    'controller/powerbeam_m5_and_5ac_bench_harness.py',
    'tools/verify/stage779_822_offline_common.py',
)
OPTIONAL_REFERENCES = (
    'artifacts/autoresearch/stage797a_universal_wa_xc_xw_v21_squashfs_bake.json',
    'artifacts/autoresearch/stage817a_universal_pb060_triple_patch_openwrt_airos_kit.json',
)


def git_read(root: Path, *args: str):
    """Only local read-only Git operations are used by this builder."""
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode != 0:
        raise ValueError('Git source inspection failed or source is dirty')
    return result.stdout


def clean_source(root: Path, label: str) -> dict:
    """Require an ordinary tracked file identical to both index and HEAD."""
    path = c.local(root, label)
    lexical = Path(root) / label
    if (not path.is_file() or lexical.is_symlink()
            or any(getattr(p, 'is_junction', lambda: False)() or p.is_symlink()
                   for p in (lexical, *lexical.parents) if p != Path(root))):
        raise ValueError('Required regular local source missing or indirect: ' + label)
    entry = git_read(root, 'ls-files', '--stage', '--', label).decode('utf-8').strip()
    if not entry or '\n' in entry:
        raise ValueError('Required source must be tracked without conflicts: ' + label)
    metadata, tracked_path = entry.split('\t', 1)
    fields = metadata.split()
    if (len(fields) != 3 or fields[0] not in ('100644', '100755') or fields[2] != '0'
            or tracked_path != label or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', fields[1])):
        raise ValueError('Required source is not a regular index blob: ' + label)
    git_read(root, 'diff', '--quiet', '--', label)
    git_read(root, 'diff', '--cached', '--quiet', 'HEAD', '--', label)
    data = path.read_bytes()
    if len(data) > 8 * 1024 * 1024 or b'\0' in data:
        raise ValueError('Only bounded text source references are allowed: ' + label)
    data.decode('utf-8-sig')
    size = int(git_read(root, 'cat-file', '-s', fields[1]).strip())
    if not 0 <= size <= 8 * 1024 * 1024:
        raise ValueError('Indexed source exceeds text read bound: ' + label)
    indexed = git_read(root, 'cat-file', 'blob', fields[1])
    if len(indexed) != size or indexed.replace(b'\r\n', b'\n') != data.replace(b'\r\n', b'\n'):
        raise ValueError('Tracked source content differs from Git blob: ' + label)
    return dict(path=label, available=True, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
                git_blob_oid=fields[1], tracked=True, index_clean=True, head_clean=True)


def required_sources(root: Path, labels: tuple[str, ...]) -> list[dict]:
    return [clean_source(root, label) for label in labels]


def optional_references(root: Path, labels: tuple[str, ...]) -> list[dict]:
    rows = []
    for label in labels:
        if not c.local(root, label).is_file():
            rows.append(dict(path=label, available=False, reason='MISSING_OPTIONAL'))
            continue
        try:
            row = clean_source(root, label)
            c.read_json(root, label)
        except (OSError, UnicodeError, ValueError):
            rows.append(dict(path=label, available=False, reason='EXCLUDED_NOT_CLEAN_TRACKED_JSON'))
            continue
        row.update(claim_scope='Historical reference only; not revalidated as compatibility evidence')
        rows.append(row)
    return rows


def verify_unchanged(root: Path, snapshots: list[dict]) -> None:
    for previous in snapshots:
        if clean_source(root, previous['path']) != previous:
            raise ValueError('Source changed during manifest construction: ' + previous['path'])


def emit(root: Path, stage: int, stem: str, title: str, sources: list[dict], payload: dict, body: str) -> dict:
    snapshots = [{key: row[key] for key in ('path', 'available', 'bytes', 'sha256')} for row in sources]
    git_checks = [{key: row[key] for key in ('path', 'git_blob_oid', 'tracked', 'index_clean', 'head_clean')} for row in sources]
    data = c.receipt(stage, title, snapshots)
    data.update(payload)
    data['source_git_checks'] = git_checks
    data.update(execution_mode='OFFLINE_SOURCE_MANIFEST', release_version='v22',
                compatibility_acceptance='UNKNOWN', physical_acceptance='UNKNOWN',
                built_firmware_images=0, proprietary_binary_bytes_packaged=0,
                source_producers_executed=False, device_commands_executed=False,
                hardware_champion=False, automatic_execution_allowed=False,
                manifest_writer_source='tools/firmware/build_stage849a_universal_wa_xc_xw_v22_release_matrix.py',
                manifest_writer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    text = f'<!-- doc-head: Stage{stage}A v22 source manifest only; runtime and compatibility UNKNOWN -->\n<!-- /doc-head -->\n\n# {title}\n\n' + body
    if len(text.splitlines()) >= 180 or text.count('<!-- doc-head:') != 1 or text.count('<!-- /doc-head -->') != 1:
        raise ValueError('document contract')
    verify_unchanged(root, sources)
    c.atomic_write(c.local(root, f'artifacts/autoresearch/{stem}.json'), json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')
    c.atomic_write(c.local(root, f'docs/{stem.upper()}.md'), text)
    return data


def build(root: Path = ROOT) -> dict:
    root = Path(root).resolve()
    sources = required_sources(root, REQUIRED_SOURCES)
    optional = optional_references(root, OPTIONAL_REFERENCES)
    rows = [
        dict(family='WA', source=REQUIRED_SOURCES[0], scope='Identity-bound transient queue helper reference'),
        dict(family='XC', source=REQUIRED_SOURCES[1], scope='Static patch loader reference; activation blocked'),
        dict(family='XW', source=REQUIRED_SOURCES[2], scope='Synthetic bench-plan and hardware metadata reference'),
    ]
    for row in rows:
        row.update(manifest_membership='CONFIRMED', runtime_compatibility='UNKNOWN',
                   source_execution_allowed=False, firmware_image=None)
    return emit(root, 849, STEM, 'WA/XC/XW v22 source release matrix', sources,
                dict(artifact_type='SOURCE_RELEASE_MATRIX', families=rows,
                     optional_references=optional,
                     optional_availability_definition='Eligible clean tracked JSON, not mere local presence'),
                'v22 identifies this source-reference release matrix, not a physical champion or firmware image.\n'
                'WA, XC and XW membership is confirmed only as metadata mapped to existing source files.\n'
                'Each mandatory input must be a tracked regular text file, clean against index and HEAD.\n'
                'SHA256 values describe actual local bytes; content also matches the indexed blob with CRLF-to-LF normalization only.\n'
                'WA points to the identity-bound queue transaction; XC points to the activation-blocked patch loader;\n'
                'XW points to a synthetic bench-plan source. No source producer or helper is executed.\n'
                'Optional old receipts may be missing or excluded; no substitute result or image is fabricated.\n'
                'No board-wide compatibility, performance, ATPC, DFS or GPS claim is accepted by this manifest.\n'
                'No proprietary binary, ZIP, loader action, network connection, Git mutation or MemoryMaster write occurs.\n')


def main() -> int:
    result = build()
    print(f'{STEM}: source_families={len(result["families"])}; runtime=UNKNOWN')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
