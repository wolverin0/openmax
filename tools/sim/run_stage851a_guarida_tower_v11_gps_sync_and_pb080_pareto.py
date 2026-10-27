#!/usr/bin/env python3
"""Bounded Guarida v11 sensitivity model; GPS/PB080 effects are assumptions."""
from __future__ import annotations

import itertools
import math
from pathlib import Path
import random
import sys

import numpy as np
import pymoo
from pymoo.algorithms.moo.nsga3 import NSGA3
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
from pymoo.util.ref_dirs import get_reference_directions
import simpy

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.verify import stage779_822_offline_common as c

STEM = 'stage851a_guarida_tower_v11_gps_sync_and_pb080_pareto'
TOPOLOGY = ((1, 4, 3, 60.0), (2, 22, 22, 100.0), (3, 6, 6, 75.0))
GPS_PHASE_US = (200, 100, 50, 25, 10, 5, 0)
PB080_BATCHES = (1, 2, 4, 8, 16)
ARRIVAL_COMPRESSIONS = (0.7, 1.0, 1.3)
REPLICATIONS = 10
SEED_BASE = 851000
HORIZON_S = 0.008
PACKET_CAP = 128
EVENT_CAP = 2000
QUEUE_CAP = 12


def configurations() -> list[dict]:
    return [dict(config_id=f'C{index:03d}', gps_phase_error_us=gps,
                 pb080_batch=batch, arrival_compression_scale=load)
            for index, (load, gps, batch) in enumerate(
                itertools.product(ARRIVAL_COMPRESSIONS, GPS_PHASE_US, PB080_BATCHES))]


def packet_trace(seed: int, arrival_compression: float) -> list[dict]:
    """Independent local arrival/jitter streams; every active CPE has four packets."""
    if type(seed) is not int or not 0 <= seed < 2**32 or arrival_compression not in ARRIVAL_COMPRESSIONS:
        raise ValueError('bounded seed and declared arrival compression required')
    arrivals = random.Random(seed)
    jitter = random.Random(seed ^ 0x851)
    packets = []
    for panel, _, active, _ in TOPOLOGY:
        for client in range(active):
            offset = arrivals.uniform(0, 0.002) / arrival_compression
            for position, (kind, size) in enumerate((('bulk', 1500), ('iptv', 1316),
                                                    ('voip', 160), ('bulk', 1500))):
                packets.append(dict(packet_id=len(packets), panel=panel,
                    cpe_id=f'P{panel}-C{client:02d}', kind=kind, bytes=size,
                    arrival_s=offset + position * 0.0005 / arrival_compression,
                    service_jitter=jitter.uniform(0.8, 1.2)))
    if len(packets) > PACKET_CAP:
        raise ValueError('packet cap exceeded')
    return packets


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def simulate_window(config: dict, seed: int, *, horizon_s=HORIZON_S,
                    event_cap=EVENT_CAP, queue_cap=QUEUE_CAP) -> dict:
    if (not isinstance(config, dict) or type(config.get('gps_phase_error_us')) is not int
            or type(config.get('pb080_batch')) is not int
            or type(config.get('arrival_compression_scale')) not in (int, float)
            or config.get('gps_phase_error_us') not in GPS_PHASE_US
            or config.get('pb080_batch') not in PB080_BATCHES
            or config.get('arrival_compression_scale') not in ARRIVAL_COMPRESSIONS
            or type(event_cap) is not int or not 1 <= event_cap <= EVENT_CAP
            or type(queue_cap) is not int or not 1 <= queue_cap <= 32
            or type(horizon_s) not in (int, float) or not math.isfinite(horizon_s)
            or not 0 < horizon_s <= 0.1):
        raise ValueError('declared simulation bounds required')
    packets = packet_trace(seed, config['arrival_compression_scale'])
    env = simpy.Environment()
    servers = {panel: simpy.PriorityResource(env, capacity=1) for panel, _, _, _ in TOPOLOGY}
    rates = {panel: capacity for panel, _, _, capacity in TOPOLOGY}
    arrived = []
    dropped = []
    completed = []
    per_cpe_bytes = {spec['cpe_id']: 0 for spec in packets}

    def transmit(spec):
        yield env.timeout(spec['arrival_s'])
        arrived.append(spec)
        if spec['kind'] == 'bulk':
            yield env.timeout(config['pb080_batch'] * 0.00004)
        server = servers[spec['panel']]
        if len(server.queue) >= queue_cap:
            dropped.append(spec)
            return
        priority = {'voip': 0, 'iptv': 1, 'bulk': 2}[spec['kind']]
        with server.request(priority=priority) as request:
            yield request
            # Hypothesized sync penalty and batch overhead; no hardware fit.
            service_s = (spec['bytes'] * 8 / (rates[spec['panel']] * 1e6)
                         + config['gps_phase_error_us'] * 1e-6 * spec['service_jitter']
                         + 0.00005 / config['pb080_batch'])
            yield env.timeout(service_s)
        per_cpe_bytes[spec['cpe_id']] += spec['bytes']
        completed.append(dict(packet_id=spec['packet_id'], bytes=spec['bytes'],
                              latency_ms=(env.now - spec['arrival_s']) * 1000))

    for spec in packets:
        env.process(transmit(spec))
    events = 0
    while env.peek() < horizon_s:
        if events >= event_cap:
            raise ValueError('event cap exceeded')
        env.step()
        events += 1
    sent_bytes = sum(spec['bytes'] for spec in arrived)
    delivered = sum(spec['bytes'] for spec in completed)
    drop_bytes = sum(spec['bytes'] for spec in dropped)
    unfinished = len(arrived) - len(dropped) - len(completed)
    unfinished_bytes = sent_bytes - delivered - drop_bytes
    if unfinished < 0 or unfinished_bytes < 0:
        raise RuntimeError('packet/byte conservation failure')
    latencies = [spec['latency_ms'] for spec in completed]
    finished_ids = {spec['packet_id'] for spec in completed + dropped}
    lower_bounds = [(horizon_s - spec['arrival_s']) * 1000 for spec in arrived
                    if spec['packet_id'] not in finished_ids]
    denominator = sum(value * value for value in per_cpe_bytes.values())
    fairness = delivered**2 / (len(per_cpe_bytes) * denominator) if denominator else None
    sent_count = len(arrived)
    completed_p99 = _percentile(latencies, .99)
    return dict(evidence_type='SYNTHETIC', config_id=config['config_id'], seed=seed,
        duration_s=horizon_s, goodput_mbps=delivered * 8 / horizon_s / 1e6,
        offered_window_mbps=sent_bytes * 8 / horizon_s / 1e6,
        p50_latency_ms=_percentile(latencies, .50), p95_latency_ms=_percentile(latencies, .95),
        p99_latency_ms=_percentile(latencies, .99),
        latency_objective_ms=max([completed_p99 if completed_p99 is not None else horizon_s * 1000] + lower_bounds),
        drop_pct=100 * len(dropped) / sent_count if sent_count else None,
        unserved_pct=100 * (len(dropped) + unfinished) / sent_count if sent_count else None,
        jain_fairness=fairness, expected_active_cpes=len(per_cpe_bytes),
        per_cpe_goodput_mbps={name: value * 8 / horizon_s / 1e6 for name, value in per_cpe_bytes.items()},
        latency_censored=unfinished > 0,
        conservation=dict(scheduled_packets=len(packets), sent_packets=sent_count,
            not_sent_packets=len(packets) - sent_count, completed_packets=len(completed),
            dropped_packets=len(dropped), unfinished_packets=unfinished,
            scheduled_bytes=sum(spec['bytes'] for spec in packets), sent_bytes=sent_bytes,
            completed_bytes=delivered, dropped_bytes=drop_bytes, unfinished_bytes=unfinished_bytes),
        events_processed=events)


def nondominated_indices(objectives) -> list[int]:
    array = np.array(objectives, dtype=float)
    if array.ndim != 2 or not array.size or not np.isfinite(array).all():
        raise ValueError('finite objective matrix required')
    return NonDominatedSorting().do(array, only_non_dominated_front=True).tolist()


def optimize_scenario(rows: list[dict]) -> dict:
    if not rows or len({row['arrival_compression_scale'] for row in rows}) != 1:
        raise ValueError('Pareto candidates must have matched arrival compression')
    objective_matrix = np.array([row['objectives'] for row in rows])

    class FiniteProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(n_var=1, n_obj=4, xl=0, xu=len(rows) - 1)
        def _evaluate(self, x, out, *args, **kwargs):
            index = int(np.clip(np.rint(x[0]), 0, len(rows) - 1))
            out['F'] = objective_matrix[index]

    algorithm = NSGA3(ref_dirs=get_reference_directions('das-dennis', 4, n_partitions=3),
                      pop_size=len(rows), sampling=np.arange(len(rows), dtype=float).reshape(-1, 1))
    result = minimize(FiniteProblem(), algorithm, ('n_gen', 3), seed=SEED_BASE, verbose=False)
    if result.X is None:
        raise RuntimeError('optimizer returned no feasible candidates')
    exact = nondominated_indices(objective_matrix)
    returned = sorted({int(np.clip(np.rint(x[0]), 0, len(rows) - 1)) for x in np.atleast_2d(result.X)})
    if not set(returned).issubset(exact):
        raise RuntimeError('optimizer returned dominated profiles')
    return dict(arrival_compression_scale=rows[0]['arrival_compression_scale'],
        algorithm='pymoo.NSGA3', generations=3, optimizer_evaluations=int(result.algorithm.evaluator.n_eval),
        exact_front_config_ids=[rows[index]['config_id'] for index in exact],
        optimizer_config_ids=[rows[index]['config_id'] for index in returned])


def build(root: Path = ROOT) -> dict:
    configs = configurations()
    windows = []
    summary = []
    for config in configs:
        replicas = []
        for replication in range(REPLICATIONS):
            row = simulate_window(config, SEED_BASE + replication)
            row.update(window_id=f"S851-{config['config_id']}-R{replication:02d}", replication=replication)
            replicas.append(row)
        windows.extend(replicas)
        def mean(key):
            values = [row[key] for row in replicas]
            if any(value is None for value in values):
                raise RuntimeError('missing model estimand; no perfect-zero substitution')
            return sum(values) / len(values)
        summary.append(dict(**config, replications=REPLICATIONS,
            offered_window_mbps=mean('offered_window_mbps'),
            mean_goodput_mbps=mean('goodput_mbps'), mean_p99_latency_ms=mean('p99_latency_ms'),
            mean_drop_pct=mean('drop_pct'), mean_jain_fairness=mean('jain_fairness'),
            objectives=[-mean('goodput_mbps'), mean('latency_objective_ms'),
                        mean('unserved_pct'), -mean('jain_fairness')]))
    fronts = [optimize_scenario([row for row in summary if row['arrival_compression_scale'] == load])
              for load in ARRIVAL_COMPRESSIONS]
    sources = [c.snapshot(root, label) for label in (
        'tools/sim/run_stage851a_guarida_tower_v11_gps_sync_and_pb080_pareto.py',
        'tools/verify/stage779_822_offline_common.py')]
    data = c.receipt(851, 'Guarida tower v11 GPS/PB080 synthetic sensitivity Pareto', sources)
    data.update(status='INFERRED', evidence_type='SYNTHETIC', execution_mode='OFFLINE_SIMULATION',
        claim_scope='bounded uncalibrated model; no measured RF effects or causal acceptance',
        model_scope='burst timing sensitivity, not mean offered load',
        windows=windows, scenario_count=len(configs), configuration_count=len(configs), arrival_compression_scenario_count=3,
        replication_count=len(windows), replications_per_configuration=REPLICATIONS,
        measured_windows_added=0, new_live_windows=0, historical_live_windows_added=0,
        accepted_live_windows=None, hardware_acceptance='UNKNOWN',
        topology=dict(panels=3, registered_cpes=32, active_cpes=31,
                      registered_by_panel=[4,22,6], active_by_panel=[3,22,6], pending_panel1=1),
        configurations=summary, pareto_by_arrival_compression=fronts,
        dependencies=dict(simpy=simpy.__version__, pymoo=pymoo.__version__, numpy=np.__version__),
        bounds=dict(window_duration_s=HORIZON_S, packet_cap=PACKET_CAP, event_cap=EVENT_CAP,
                    queue_cap_per_panel=QUEUE_CAP, windows=1050),
        seeds=dict(replication_seeds=list(range(SEED_BASE, SEED_BASE+REPLICATIONS)),
                   purpose='common random numbers across configurations; independent workload seeds across replicates'),
        assumptions=['GPS phase error0..200us and PB080 batch1..16 are hypotheses, not applied parameters.',
            'Assumed panel rates60/100/75Mbps;3 independent priority servers omit real RF interference/TDMA.',
            'Hypothesized sync service penalty,50us/batch overhead and40us*batch bulk holdoff are uncalibrated.',
            'Pending CPE is explicit; fairness denominator contains all31 active CPEs including zero receivers.',
            'Completed-packet percentiles use nearest-rank; unfinished lower bounds penalize the optimizer.',
            'No causal confidence interval, effect attribution, target code execution or historical-window addition.'])
    data['five_pillar_compliance'][c.PILLARS[3]] = dict(status='LOCAL_MODEL_EXECUTED',
        method='bounded SimPy priority scheduling; matched-load NSGA-III; exact finite nondominance audit')
    return c.save(root, STEM, data,
        'INFERRED synthetic sensitivity study:105 configurations x10 replications =1050 modeled windows.\n'
        'Three panels:32 registered CPEs(4/22/6),31 active(3/22/6),one pending on panel1.\n'
        'GPS phase and PB080 batching are hypotheses with uncalibrated timing coefficients.\n'
        'Actual SimPy priority resources and pymoo NSGA-III execute offline; fronts compare matched arrival compressions.\n'
        'Per-window IDs,seeds,duration,goodput,completed latency percentiles,drops,fairness and conservation are retained.\n'
        'Queue drops and unfinished traffic are separate; active zero receivers remain in the fairness denominator.\n'
        'Bounds:8ms,128 entities,2000 events,12 queued packets per panel per window.\n'
        'Ten independent workload seeds are shared across profiles for matched comparisons.\n'
            'Arrival compression changes burst timing only; offered_window_mbps is constant138.756Mbps over8ms.\n'
        '1050 model windows add0 historical/live windows. Hardware acceptance remains UNKNOWN.\n'
        'Scholar/reactor and durable MemoryMaster ingestion are deferred; no remote calls or claims are fabricated.\n')


def main() -> int:
    result = build()
    print(f"851A SYNTHETIC windows={result['replication_count']} configs={result['scenario_count']} live=0 hardware=UNKNOWN")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
