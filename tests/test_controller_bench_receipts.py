"""Integration with sanitized, SHA-bound held receipts (not a new RF test)."""
import hashlib
import json
from pathlib import Path

import pytest

from controller.cooperative_sensor import CpeTelemetrySample, compute_airtime_tax
from controller.distributed_compute import verify_worker_shard
from telemetry.station_monitor import StationMonitor

FIXTURE = json.loads((Path(__file__).parent / 'fixtures/controller_bench_20261022.json').read_text())


def test_held_run17_station_parser_and_counter_continuity():
    row = FIXTURE['run17']
    assert row['exit_code'] == 0 and row['association_accepted']
    assert row['stability_seconds'] >= 60
    assert hashlib.sha256(row['station_dump'].encode()).hexdigest() == row['station_sha256']
    stations = StationMonitor.parse_iw_station_dump(row['station_dump'])
    assert set(stations) == {'fc:ec:da:c2:54:0a'}
    station = next(iter(stations.values()))
    assert station.rx_bytes == row['samples'][0]['rx_bytes']
    assert station.tx_bytes == row['samples'][0]['tx_bytes']
    assert all(row['samples'][1][k] > row['samples'][0][k]
               for k in ('connected_seconds', 'rx_bytes', 'tx_bytes'))


def test_held_run25_and_four_cpe_do_not_invent_airtime_measurements():
    row = FIXTURE['run25']
    assert row['exit_code'] == 0 and row['simultaneous_WPA2_WDS_60s_pass']
    assert row['WA_survived_repulse'] and row['stability_seconds'] >= 60
    for mac, before in row['stations'][0].items():
        assert all(row['stations'][1][mac][k] > before[k] for k in before)
    four = FIXTURE['four']
    assert four['exit_code'] == 0 and not four['failures'] and not four['cleanup_errors']
    assert four['four_way_stability_seconds'] >= 60 and four['sample_count'] == 41
    samples = []
    for name, s in four['telemetry'].items():
        assert s['ping_received'] == s['ping_transmitted'] == s['radio_request_reply_pairs'] == 64
        # Receipts do not supply measured airtime. Exercise the explicit fallback,
        # rather than translating ping success into airtime/performance proof.
        samples.append(CpeTelemetrySample(name, s['mac'], useful_bytes=s['tx_bytes_delta'] + s['rx_bytes_delta']))
    results = compute_airtime_tax(samples)
    assert len(results) == 4
    assert all(s.used_6mbps_fallback_warning for s in results)
    assert sum(s.airtime_share for s in results) == pytest.approx(1)


@pytest.mark.parametrize('device', list(FIXTURE['compute']))
def test_held_hardware_shards_and_safety_exits(device):
    row = FIXTURE['compute'][device]
    assert row['hashes_identical'] and FIXTURE['ram'][device] >= 16384
    for name in ('test_5pct_duty', 'test_10pct_duty'):
        output = row[name]['output']
        assert row[name]['exit_code'] == 0 and output['status'] == 'OK'
        assert verify_worker_shard(opcode=output['opcode'], seed=output['seed'],
            iterations=output['done_iters'], reported_accum=output['accum'])
    for name, code in [('test_lease_ttl_expiry', 73), ('test_kill_switch', 72), ('test_traffic_preemption', 74)]:
        assert row[name]['exit_code'] == code


def test_held_triage_summary_is_internally_consistent_not_new_acceptance():
    row = FIXTURE['triage']
    correct = sum(s['predicted'] == s['expected'] for s in row['cases'])
    assert correct == row['correct_predictions']
    assert len(row['cases']) == row['total_cases']
    assert row['accuracy_pct'] == pytest.approx(100 * correct / row['total_cases'])
    assert all(FIXTURE['recorded_shards'].values())
