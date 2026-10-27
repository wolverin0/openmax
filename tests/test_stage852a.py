import pytest

from tools.verify.build_stage852a_1050window_cross_lane_master_scorecard import summarize


def window(i=0):
    return {'window_id': str(i), 'evidence_type': 'SYNTHETIC',
            'config_id': 'C' + str(i // 10), 'seed': i % 10, 'duration_s': .008,
            'conservation': {'scheduled_packets': 1, 'sent_packets': 1, 'not_sent_packets': 0,
                'completed_packets': 1, 'dropped_packets': 0, 'unfinished_packets': 0,
                'scheduled_bytes': 100, 'sent_bytes': 100, 'completed_bytes': 100,
                'dropped_bytes': 0, 'unfinished_bytes': 0},
            'goodput_mbps': .1, 'p50_latency_ms': 1, 'p95_latency_ms': 1,
            'p99_latency_ms': 1, 'drop_pct': 0, 'expected_active_cpes': 1,
            'per_cpe_goodput_mbps': {'CPE': .1}, 'jain_fairness': 1}


def test_no_padding_or_physical_promotion():
    result = summarize([window()])
    assert result['actual_synthetic_windows'] == 1
    assert result['target_met'] is False
    assert result['physical_windows_executed'] == 0
    assert result['promotion_allowed'] is False


def test_target_requires_real_rows():
    result = summarize([window(i) for i in range(1050)])
    assert result['actual_synthetic_windows'] == 1050 and result['target_met']


@pytest.mark.parametrize('rows', [
    [{'window_id': 'same', 'evidence_type': 'SYNTHETIC'}] * 2,
    [{'window_id': 'one', 'evidence_type': 'PHYSICAL'}],
    [{'evidence_type': 'SYNTHETIC'}],
])
def test_invalid_count_rejected(rows):
    with pytest.raises(ValueError):
        summarize(rows)


@pytest.mark.parametrize('field,value', [('seed', None), ('goodput_mbps', 0),
    ('p95_latency_ms', float('nan')), ('jain_fairness', 0), ('drop_pct', 100)])
def test_invalid_measurements_cannot_count(field, value):
    row = window()
    row[field] = value
    with pytest.raises(ValueError):
        summarize([row])


def test_duplicate_replication_cannot_be_relabelled():
    first, second = window(), window()
    second['window_id'] = 'relabelled'
    with pytest.raises(ValueError, match='duplicate configuration'):
        summarize([first, second])
