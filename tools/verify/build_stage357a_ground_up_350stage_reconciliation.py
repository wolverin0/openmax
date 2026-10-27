#!/usr/bin/env python3
"""Reconcile held stage1..350 receipts; file counts never establish RF acceptance."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import re
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from tools.re import ground_up_release_common as c
from tools.bench import export_cumulative_autoresearch_leaderboard as saved
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

OUT = 'artifacts/autoresearch/stage357a_ground_up_350stage_reconciliation.json'
DOC = 'docs/STAGE357A_GROUND_UP_350STAGE_RECONCILIATION.md'
MAX_FILE = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_FILES = 2000
MAX_REFERENCES = 12000
PREFIX = re.compile(r'^stage(\d{1,3})([a-z]*)(?:_|\.|-)', re.I)
CONTEXT = {
    '353A': 'artifacts/autoresearch/stage353a_sub20mhz_pll_ofdm_timing_matrix.json',
    '354A': 'artifacts/autoresearch/stage354a_wmi_4series_retry_fallback_pareto.json',
    '355A': 'artifacts/autoresearch/stage355a_airselect_hopping_evasion_pareto.json',
    '356A': 'artifacts/autoresearch/stage356a_tester_bundle_verifier.json',
}


def stage_id(name):
    match = PREFIX.match(name)
    if not match or not 1 <= int(match[1]) <= 350: return None
    return str(int(match[1])) + match[2].upper()


def walk(root):
    """Never descend into symlinks/reparse points, including mapped shares."""
    base = c.local_path(root) / 'artifacts'
    pending = [c.local_path(base)]; count = 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                count += 1
                if count > 200000: raise ValueError('inventory_entry_limit')
                info = entry.stat(follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
                    yield Path(entry.path), 'UNSAFE_REPARSE_SKIPPED'
                elif stat.S_ISDIR(info.st_mode): pending.append(c.local_path(entry.path))
                elif stat.S_ISREG(info.st_mode) and entry.name.lower().endswith('.json') and stage_id(entry.name):
                    yield c.local_path(entry.path), None


def nodes(obj, depth=0, budget=None):
    if budget is None: budget = [0]
    budget[0] += 1
    if depth > 40 or budget[0] > 250000: raise ValueError('json_structure_limit')
    yield obj
    values = obj.values() if isinstance(obj, dict) else obj if isinstance(obj, list) else ()
    for value in values: yield from nodes(value, depth + 1, budget)


def declared_ids(obj):
    values = [obj.get('stage')]
    if isinstance(obj.get('meta'), dict): values.append(obj['meta'].get('stage'))
    found = set()
    for value in values:
        if not isinstance(value, str): continue
        match = re.match(r'^(?:stage[ _-]*)?(\d{1,3})([a-z]*)(?:\b|_)', value, re.I)
        if match: found.add(str(int(match[1])) + match[2].upper())
    return sorted(found)


def role_for(path):
    # Location is only a provenance role. It cannot establish first-hand acquisition.
    parts = set(path.lower().split('/'))
    return 'SUPPORT_OR_COPY' if parts & {'verification', 'inputs', 'snapshots', 'repro', 'cache'} else 'REPORTED_RECEIPT'


def identity_relation(filename_id, declared):
    a = re.fullmatch(r'(\d+)([A-Z]*)', filename_id)
    b = re.fullmatch(r'(\d+)([A-Z]*)', declared)
    if a[1] != b[1] or (a[2] and b[2] and a[2] != b[2]): return 'CONFLICT'
    return 'MATCH' if a[2] == b[2] else 'COMPATIBLE_UNDERSPECIFIED_SUFFIX'


def reference_rows(all_nodes):
    for node in all_nodes:
        if isinstance(node, dict) and isinstance(node.get('path'), str) and isinstance(node.get('sha256'), str):
            if re.fullmatch('[0-9a-f]{64}', node['sha256']): yield node['path'], node['sha256']


def order_provenance(obj, pointer):
    node = obj
    for token in pointer.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        node = node[int(token)] if isinstance(node, list) else node[token]
    if isinstance(node, list):
        return {'order_provenance': 'REPORTED_ORDERED_ARRAY_NOT_AUTHENTICATED', 'source_array_pointers': [pointer]}
    if isinstance(node, dict) and all(k in node for k in ('A1', 'B1', 'A2', 'B2')):
        return {'order_provenance': 'NAMED_PHASE_KEYS_ORDER_ASSUMED',
                'source_array_pointers': [pointer+'/'+k for k in ('A1', 'B1', 'A2', 'B2')]}
    if isinstance(node, dict) and 'arm_a_windows' in node and 'arm_b_windows' in node:
        return {'order_provenance': 'RECONSTRUCTED_FROM_SEPARATE_ARM_ARRAYS',
                'source_array_pointers': [pointer+'/arm_a_windows', pointer+'/arm_b_windows']}
    return {'order_provenance': 'UNKNOWN', 'source_array_pointers': [pointer]}


def check_references(root, refs, byte_budget=256*1024*1024):
    root = c.local_path(root); rows = []; cache = {}; consumed = 0
    for label, expected in sorted(refs):
        row = {'path': label, 'expected_sha256': expected}
        if not label or '\\' in label or ':' in label or label.startswith('/') or '..' in Path(label).parts:
            row['status'] = 'UNRESOLVED_NON_REPO_RELATIVE_REFERENCE'; rows.append(row); continue
        try:
            target = c.local_path(root / label)
            target.relative_to(root)
            if target not in cache:
                size = target.stat().st_size
                if size > MAX_FILE or consumed + size > byte_budget:
                    row['status'] = 'UNVERIFIED_READ_BUDGET'; rows.append(row); continue
                data = c.read(target, maximum=MAX_FILE); consumed += len(data)
                cache[target] = c.sha(data)
            row['actual_sha256'] = cache[target]
            row['status'] = 'MATCH' if cache[target] == expected else 'DRIFT'
        except (OSError, ValueError): row['status'] = 'MISSING_OR_UNSAFE'
        rows.append(row)
    return {'rows': rows, 'unique_files_read': len(cache), 'bytes_read': consumed,
            'status_counts': dict(Counter(r['status'] for r in rows)),
            'qualification': 'Referenced bytes at this snapshot only; not provenance, trust, restore or hardware acceptance.'}


def reconcile(root=ROOT):
    root = c.local_path(root); rows = []; issues = []; by_hash = defaultdict(list)
    refs = set(); comparisons = {}; rejected = []; total = 0; arrays_seen = 0
    for path, issue in sorted(walk(root), key=lambda pair: pair[0].as_posix()):
        rel = path.relative_to(root).as_posix()
        if issue:
            issues.append({'path': rel, 'status': issue}); continue
        if len(rows) >= MAX_FILES: raise ValueError('receipt_file_limit')
        row = {'path': rel, 'filename_stage': stage_id(path.name), 'role': role_for(rel),
               'empirical_acceptance': 'NOT_INDEPENDENTLY_ASSESSED'}
        rows.append(row)
        try:
            data = c.read(path, maximum=MAX_FILE); total += len(data)
            if total > MAX_TOTAL: raise ValueError('receipt_total_limit')
            row.update(sha256=c.sha(data), bytes=len(data)); by_hash[row['sha256']].append(rel)
            obj = json.loads(data, object_pairs_hook=c.pairs, parse_constant=c.invalid_constant)
            json.dumps(obj, allow_nan=False)
            if not isinstance(obj, dict): raise ValueError('non_object_receipt')
            all_nodes = list(nodes(obj))
            row['parse_status'] = 'VALID_OBJECT'; row['declared_stage_ids'] = declared_ids(obj)
            row['declared_identity_relations'] = {v: identity_relation(row['filename_stage'], v) for v in row['declared_stage_ids']}
            row['stage_identity_conflict'] = 'CONFLICT' in row['declared_identity_relations'].values()
            row['structural_five_pillar_gate'] = audit_stage_receipt_5pillars(obj)
            # Tags describe field/name hints, never authenticated acquisition.
            row['evidence_hints'] = sorted(set(
                ['SIMULATION_HINT'] if any(k in obj for k in ('model_assumptions', 'simulation', 'scenarios')) or 'simul' in path.name else []
            ) | ({'COUNTERBALANCE_FIELD_PRESENT'} if any(isinstance(n, dict) and ('windows' in n or 'A1' in n) for n in all_nodes) else set()))
            refs.update(reference_rows(all_nodes))
            if len(refs) > MAX_REFERENCES: raise ValueError('reference_count_limit')
            family = saved.family_for(path.name) or 'UNRESOLVED_TOPOLOGY'
            for pointer, windows, context in saved.arrays(obj):
                arrays_seen += 1
                if arrays_seen > 12000: raise ValueError('comparison_array_limit')
                for rid, candidate in saved.comparisons(windows, context):
                    location = {'path': rel, 'pointer': pointer, 'reported_round_id': str(rid)[:100],
                                **order_provenance(obj, pointer)}
                    try:
                        normalized, basis = saved.normalize(candidate)
                        a, b, delta = saved.summarize(normalized)
                        # Identical values are ambiguous copies, NOT proven independent/duplicate experiments.
                        fingerprint = c.sha(json.dumps([family, str(rid), basis, normalized], sort_keys=True, allow_nan=False).encode())
                        if fingerprint not in comparisons:
                            comparisons[fingerprint] = {'fingerprint': fingerprint, 'family_name_hint': family,
                                'goodput_basis': basis, 'windows': normalized, 'arm_a_means': a, 'arm_b_means': b,
                                'percent_change': delta, 'source_locations': [],
                                'qualification': 'SAVED_SUMMARY_ARITHMETIC_ONLY_NOT_NATIVE_ACQUISITION_OR_RF_ACCEPTANCE'}
                        comparisons[fingerprint]['source_locations'].append(location)
                    except (ValueError, TypeError, KeyError, OverflowError) as exc:
                        rejected.append({**location, 'reason': str(exc)[:100]})
        except (OSError, ValueError, UnicodeError, TypeError, RecursionError, OverflowError) as exc:
            if str(exc) in ('receipt_total_limit', 'reference_count_limit', 'comparison_array_limit'): raise
            row['parse_status'] = 'INVALID_OR_UNSAFE'; row['error_type'] = type(exc).__name__
    present = sorted({int(re.match(r'\d+', r['filename_stage'])[0]) for r in rows if r.get('parse_status') == 'VALID_OBJECT'})
    summary = {'receipt_files': len(rows), 'valid_objects': sum(r.get('parse_status') == 'VALID_OBJECT' for r in rows),
               'unique_content_hashes': len(by_hash), 'numeric_stage_ids_present': len(present),
               'numeric_stage_ids_missing': sorted(set(range(1, 351)) - set(present)),
               'stage_identity_conflicts': sum(r.get('stage_identity_conflict', False) for r in rows),
               'saved_comparison_fingerprints': len(comparisons),
               'saved_comparison_locations': sum(len(r['source_locations']) for r in comparisons.values()),
               'rejected_comparison_groups': len(rejected), 'new_hardware_results': 0}
    return {'cutoff_stage': 350, 'summary': summary, 'receipt_inventory': rows, 'scan_issues': issues,
            'numeric_stage_ids_present': present,
            'identical_content_groups': [{'sha256': h, 'paths': p} for h, p in sorted(by_hash.items()) if len(p) > 1],
            'saved_comparisons': sorted(comparisons.values(), key=lambda r: r['fingerprint']),
            'rejected_comparisons': rejected, 'reference_integrity': check_references(root, refs),
            'structural_gate_meaning': 'PRESENCE_HEURISTIC_ONLY_NOT_FIVE_PILLAR_SCIENTIFIC_ACCEPTANCE',
            'coverage_meaning': 'Valid held JSON filenames, not 350 completed stages or unique physical experiments.',
            'snapshot': {'receipt_bytes_read': total, 'timestamps_excluded': True, 'receipt_bindings_rechecked_in_build': True},
            'boundary': {'target_access': False, 'network_access': False, 'physical_acceptance': False, 'gain_summing': False}}


def build(root=ROOT):
    root = c.local_path(root); report = reconcile(root)
    # Detect in-scan receipt drift; never silently accept a mixed byte snapshot.
    drift = []
    for row in report['receipt_inventory']:
        if row.get('sha256') and c.sha(c.read(root / row['path'], maximum=MAX_FILE)) != row['sha256']: drift.append(row['path'])
    report['snapshot']['receipt_drift_during_scan'] = drift
    report.update(stage='357A', task_id='T-S357A-GROUND-UP-350STAGE-RECONCILIATION',
                  static_sources=[c.binding(root / p, root) for p in CONTEXT.values()],
                  status='QUALIFIED_OFFLINE_RECONCILIATION_NOT_350_STAGE_ACCEPTANCE')
    report['architecture'] = [
        {'owner': 'Linux/ath9k', 'evidence': '353A', 'finding': 'Source-backed conditional5/10MHz timing and PLL CLKSEL; exact installed board support UNKNOWN.'},
        {'owner': 'ath10k/QCA firmware', 'evidence': '353A', 'finding': 'No ordinary upstream5/10MHz phymode mapping; host QCA955x does not identify radio control.'},
        {'owner': 'proprietary airMAX/WMI', 'evidence': '354A', 'finding': 'Held sender0x9044/188B and descriptor source are static; native payload/endianness remains BLOCKED.'},
        {'owner': 'external controller/simulation', 'evidence': '354A/355A', 'finding': 'Synthetic retry/hopping Pareto fronts; not measured Minstrel collapse or vendor AirSelect TDD.'},
        {'owner': 'Linux/mac80211', 'evidence': '356A', 'finding': 'WA kernel/DTB and local watchdog bytes can be checked; neither proves installed runtime behavior.'},
        {'owner': 'LTU/hardware', 'evidence': '356A', 'finding': 'No qualified LTU image join or physical restore proof; existing kits remain BLOCKED.'},
    ]
    report['gaps'] = ['Missing numeric IDs are explicit; letters/copies are not additional unique stages.',
        'Filename family hints and identical summaries do not authenticate topology or independent measurements.',
        'Source hash drift/missing references are retained; bounded unread references remain unverified.',
        'No unified hardware/build/configuration/topology/RF acquisition chain was independently accepted.',
        'E2 remains NOT_ACCEPTED; no native payload, PLL recipe, channel executor or flash approval.']
    s = report['summary']
    doc = f'''<!-- doc-head: Stage357A qualified ground-up architecture and held350-stage ledger reconciliation -->
Counts describe held evidence, not completed experiments or hardware acceptance.
<!-- /doc-head -->

# Stage357A

Parent: original control-boundary/RE1 deliverable after353A..356A.
Run `python tools/verify/build_stage357a_ground_up_350stage_reconciliation.py`.
The scan reads only local regular JSON files under artifacts with stage1..350 names.
Symlinks/reparse paths are not followed. Size, count, JSON-depth and reference
budgets bound the scan; malformed/nonfinite/duplicate-key JSON stays invalid.
Missing numbers are retained, not filled with invented receipts.

## Frozen receipt snapshot

| Observation | Count |
| --- | ---: |
| Receipt files | {s['receipt_files']} |
| Valid object receipts | {s['valid_objects']} |
| Distinct content hashes | {s['unique_content_hashes']} |
| Numeric stage IDs present of350 | {s['numeric_stage_ids_present']} |
| Filename/declared identity conflicts | {s['stage_identity_conflicts']} |
| Saved comparison fingerprints | {s['saved_comparison_fingerprints']} |
| Saved comparison locations | {s['saved_comparison_locations']} |
| New physical results | 0 |

Each receipt retains its hash, location role and unresolved empirical acceptance.
Support snapshots/copies are distinguished by location, not treated as independent
measurements. Identical-content aliases remain visible. Parsed stage/meta IDs are
compared with filename IDs; unknown declaration formats are not guessed. A missing
letter suffix is compatible but underspecified, not a conflicting numeric stage.

The existing five-pillar function is invoked as a STRUCTURAL PRESENCE HEURISTIC.
Its acceptance of a summary/boundary/meta field does not prove binary provenance,
scholar verification, counterbalanced acquisition, inference or durable memory.
Its booleans are retained without promoting them to scientific acceptance.

Saved ABAB arrays reuse Stage266's finite metric/order/quantile normalization and
recompute arm means and changes. These are summary arithmetic, not authenticated
native measurements. Each source location preserves order provenance and exact
array pointers: reported array order, assumed named-phase order, or ABAB
reconstructed from separate A/B arm arrays. Reconstruction is not observed order.
Fingerprints group equal round/family-hint/metric summaries;
genuine equal observations and copied summaries cannot be distinguished here.
No count is called a unique physical experiment; gains are never added or pooled
across radios/topologies. Unresolved filename family hints remain unresolved.
Rejected arrays keep their locations and reasons. No raw device config is emitted.

Recognized repo-relative path/SHA256 references are checked within a256MiB read
budget and32MiB per file. Missing, drifted, unsafe and budget-skipped bindings stay
visible. Hash agreement authenticates current bytes only, not original acquisition.
Receipt hashes are rechecked after the scan to expose concurrent source drift.
This is a reproducible held-file snapshot, not an immutable historical archive.

## Architecture boundaries

| Owner | Established offline | Remaining gap |
| --- | --- | --- |
| Linux/ath9k | Conditional half/quarter timing and PLL source paths | Exact board/runtime support |
| ath10k/QCA firmware | No normal upstream5/10MHz phymode cases | Native capability/control |
| Proprietary WMI | Held0x9044 sender/188-byte copy; descriptor bits | Native ABI and peer acceptance |
| External simulator | Finite seeded retry/hopping fronts | Calibrated RF/vendor protocol |
| Linux/mac80211 | Exact WA kernel/DTB and watchdog byte checks | Installed/armed semantics |
| LTU/hardware | Local kit inventory | Image join, boot, restore, RF |

353A..356A receipts are separately pinned as current architecture context and are
outside the1..350 ledger cutoff. Simulation is not physical acceptance. Manifest
trust anchors are caller-selected, saved watchdog assertions are not fresh device
proof, and no verifier can guarantee zero bricks. Decision: KEEP qualified offline
reconciliation. E2 NOT_ACCEPTED. No live radio, SSH, flash or target execution.
'''
    c.write_doc(root / DOC, doc); report['outputs'] = {DOC: c.binding(root / DOC, root)}
    report['implementation'] = c.binding(root / 'tools/verify/build_stage357a_ground_up_350stage_reconciliation.py', root)
    c.write_json(root / OUT, report); return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--root', type=Path, default=ROOT)
    args = p.parse_args(argv); print(json.dumps(build(args.root)['summary'], sort_keys=True)); return 0


if __name__ == '__main__': raise SystemExit(main())
