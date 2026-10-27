#!/usr/bin/env python3
"""Account for actual simulation windows, without promoting imported claims."""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify.stage779_822_offline_common import read_json, receipt, save, snapshot
from tools.verify.stage849_854_release_common import STEMS, artifact, audit_stage

STEM = STEMS[852]
TARGET = 1050


def validate_window(row: dict) -> None:
    if not isinstance(row, dict):
        raise ValueError('window object required')
    if (not isinstance(row.get('config_id'), str) or not row['config_id']
            or type(row.get('seed')) is not int or not 0 <= row['seed'] < 2**32):
        raise ValueError('configuration and bounded seed required')
    duration = row.get('duration_s')
    if type(duration) not in (int, float) or not math.isfinite(duration) or not 0 < duration <= .1:
        raise ValueError('finite bounded duration required')
    counts = row.get('conservation', {})
    if not isinstance(counts, dict):
        raise ValueError('counter object required')
    keys = ['scheduled_packets', 'sent_packets', 'not_sent_packets', 'completed_packets',
            'dropped_packets', 'unfinished_packets', 'scheduled_bytes', 'sent_bytes',
            'completed_bytes', 'dropped_bytes', 'unfinished_bytes']
    if any(type(counts.get(k)) is not int or counts[k] < 0 for k in keys):
        raise ValueError('actual nonnegative packet and byte counters required')
    if (counts['scheduled_packets'] != counts['sent_packets'] + counts['not_sent_packets']
            or counts['sent_packets'] != sum(counts[k] for k in (
                'completed_packets', 'dropped_packets', 'unfinished_packets'))
            or counts['sent_bytes'] != sum(counts[k] for k in (
                'completed_bytes', 'dropped_bytes', 'unfinished_bytes'))
            or counts['scheduled_bytes'] < counts['sent_bytes']):
        raise ValueError('packet or byte conservation failed')
    def finite(key, low, high):
        value = row.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError('invalid finite metric: ' + key)
        return value
    actual = finite('goodput_mbps', 0, 1e6)
    if not math.isclose(actual, counts['completed_bytes'] * 8 / duration / 1e6, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError('receiver byte/time goodput mismatch')
    if counts['completed_packets']:
        latency = [finite(key, 0, duration * 1000) for key in (
            'p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms')]
        if latency != sorted(latency):
            raise ValueError('latency quantile order')
    elif any(row.get(key) is not None for key in ('p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms')):
        raise ValueError('missing replies cannot report perfect latency')
    if counts['sent_packets']:
        loss = finite('drop_pct', 0, 100)
        if not math.isclose(loss, 100 * counts['dropped_packets'] / counts['sent_packets'], abs_tol=1e-9):
            raise ValueError('drop denominator mismatch')
    elif row.get('drop_pct') is not None:
        raise ValueError('no probes cannot mean zero loss')
    per_cpe = row.get('per_cpe_goodput_mbps', {})
    n = row.get('expected_active_cpes')
    if type(n) is not int or n <= 0 or not isinstance(per_cpe, dict) or len(per_cpe) != n:
        raise ValueError('complete active-station denominator required')
    values = list(per_cpe.values())
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError('invalid station throughput')
    if not math.isclose(sum(values), actual, abs_tol=1e-9):
        raise ValueError('aggregate/station goodput mismatch')
    squared = sum(v*v for v in values)
    if squared:
        fairness = finite('jain_fairness', 0, 1 + 1e-12)
        if not math.isclose(fairness, sum(values)**2 / (n * squared), abs_tol=1e-9):
            raise ValueError('fairness denominator mismatch')
    elif row.get('jain_fairness') is not None:
        raise ValueError('no receivers cannot mean perfect fairness')


def summarize(windows: list[dict]) -> dict:
    if not isinstance(windows, list):
        raise ValueError('window list required')
    ids = []
    replicas = set()
    for row in windows:
        identity = row.get('window_id')
        if not isinstance(identity, str) or not identity:
            raise ValueError('explicit window ID required')
        if row.get('evidence_type') != 'SYNTHETIC':
            raise ValueError('851A contains non-synthetic evidence')
        validate_window(row)
        replica = (row['config_id'], row['seed'])
        if replica in replicas:
            raise ValueError('duplicate configuration/seed replication')
        replicas.add(replica)
        ids.append(identity)
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate windows cannot be counted twice')
    return {'target_windows': TARGET, 'actual_synthetic_windows': len(ids),
            'physical_windows_executed': 0, 'imported_windows_added': 0,
            'target_met': len(ids) >= TARGET,
            'evidence_counts': dict(Counter(row['evidence_type'] for row in windows)),
            'window_ids': ids, 'promotion_allowed': False}


def build(root: Path = ROOT) -> dict:
    audits = [audit_stage(root, n) for n in (849, 850, 851)]
    if not all(row['compliant'] for row in audits):
        raise ValueError('dependency acceptance failed: ' + json.dumps(audits))
    model = read_json(root, artifact(851))
    accounting = summarize(model['windows'])
    data = receipt(852, '1050-window cross-lane master scorecard',
                   [snapshot(root, artifact(n)) for n in (849, 850, 851)] +
                   [snapshot(root, 'tools/verify/' + Path(__file__).name),
                    snapshot(root, 'tools/verify/stage849_854_release_common.py')])
    data.update(accounting=accounting, dependency_audits=audits,
                release_version='v22', physical_acceptance='UNKNOWN',
                completion_scope='offline release accounting; no historical campaign certification',
                blockers=['ATPC/DFS native guard validation', 'GPS synchronization measured readback',
                          'PB080 target execution witness', 'independent physical holdout'])
    return save(root, STEM, data,
                f"Actual unique synthetic windows: {accounting['actual_synthetic_windows']}; "
                f"target {TARGET}; target met: {accounting['target_met']}.\n\n"
                'Measured windows executed here: 0. Imported window counts added: 0.\n'
                'No physical champion or statistical campaign is promoted.\n'
                'WA/XC/XW and LTU packages are source manifests; GPS/PB080 model inputs are hypotheses.\n'
                'Five-pillar structural coverage is checked; external research and durable ingestion remain deferred.\n'
                'Attribution: external controller. Physical acceptance: UNKNOWN.\n')


if __name__ == '__main__':
    result = build()
    print(json.dumps({key: value for key, value in result['accounting'].items()
                      if key != 'window_ids'}, indent=2))
