"""Bounded synthetic four-series retry study; no native WMI transport or RF claim."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from importlib.metadata import version
import math
from pathlib import Path
import random
import statistics
import struct
import sys

import numpy as np
import simpy
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import Problem
from pymoo.optimize import minimize

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tools.re import ground_up_release_common as c
from controller.stage18_wmi_rate_schedule_and_sub20mhz_controller import (
    HEADER_SHA256, NativeWmiAbiUnqualified, PeerCapabilities,
    SeriesBwDescriptor, verify_series_header,
)

OUT = 'artifacts/autoresearch/stage354a_wmi_4series_retry_fallback_pareto.json'
DOC = 'docs/STAGE354A_WMI_4SERIES_RETRY_FALLBACK_PARETO.md'
SERIES_HEADER = 'artifacts/verification/stage354a/series_bw.h'
SEEDS = (354, 1354, 2354)
SCENARIOS = {
    'balanced_control': dict(chain_snr_db=(27., 27.), burst_probability=.02,
                             burst_persistence=.3, burst_penalty_db=8., multipath_penalty_db=.5),
    'foliage_chain0_stronger': dict(chain_snr_db=(23., 12.), burst_probability=.12,
                                  burst_persistence=.7, burst_penalty_db=9., multipath_penalty_db=2.),
    'foliage_chain1_stronger': dict(chain_snr_db=(12., 23.), burst_probability=.12,
                                  burst_persistence=.7, burst_penalty_db=9., multipath_penalty_db=2.),
    'multipath_bursts': dict(chain_snr_db=(23., 23.), burst_probability=.18,
                            burst_persistence=.8, burst_penalty_db=13., multipath_penalty_db=5.),
}
# Illustrative link abstraction, not fitted SNR/EVM thresholds or receiver PER data.
MCS_RATE_MBPS_1SS_LGI = (6.5, 13., 19.5, 26., 39., 52., 58.5, 65., 78.)
ILLUSTRATIVE_SNR_THRESHOLD_DB = (4., 7., 10., 13., 16., 19., 21., 23., 26.)


@dataclass(frozen=True)
class RetryPolicy:
    policy_id: str
    kind: str
    series: tuple[SeriesBwDescriptor, ...]
    attempts: tuple[int, ...]
    final_branch: str
    cdd_model_assumption: bool = False

    def __post_init__(self):
        if type(self.policy_id) is not str or not self.policy_id or len(self.policy_id) > 100:
            raise ValueError('policy_id_required')
        if self.kind not in ('CANDIDATE', 'MODELED_BASELINE_PROXY'):
            raise ValueError('unknown_policy_kind')
        if type(self.series) is not tuple or len(self.series) != 4:
            raise ValueError('four_series_required')
        if type(self.attempts) is not tuple or len(self.attempts) != 4:
            raise ValueError('four_attempt_budgets_required')
        for n in self.attempts:
            c.integer(n, 'attempt_count', 1, 4)
        if sum(self.attempts) > 12:
            raise ValueError('attempt_budget_exceeded')
        if any(not isinstance(s, SeriesBwDescriptor) for s in self.series):
            raise ValueError('typed_VHT20_series_required')
        # The shared descriptor supports more hardware combinations than this finite model.
        if any(s.bandwidth_mhz != 20 or s.preamble_type != 3 or not 0 <= s.rate <= 8
               or s.nss not in (1, 2) or s.chain_mask not in (1, 2, 3)
               or s.ldpc != 1 or s.sgi not in (0, 1) or s.txbf or s.tpc != 0
               or s.legacy_vht_bw or s.rts_enable or s.cts_enable for s in self.series):
            raise ValueError('series_outside_simulated_VHT20_twoTX_MCS0_to8_domain')
        if type(self.cdd_model_assumption) is not bool:
            raise ValueError('explicit_CDD_model_boolean_required')
        if self.final_branch not in ('chain0', 'chain1', 'cdd_hypothesis', 'baseline_2ss'):
            raise ValueError('unknown_final_branch')
        if self.final_branch == 'cdd_hypothesis' and not self.cdd_model_assumption:
            raise ValueError('CDD_requires_explicit_model_assumption_not_STBC_bit')
        if self.kind == 'MODELED_BASELINE_PROXY':
            if (self.final_branch != 'baseline_2ss' or self.cdd_model_assumption
                    or any(s.nss != 2 or s.chain_mask != 3 or s.stbc or s.sgi != 0 for s in self.series)):
                raise ValueError('baseline_requires_twoSS_twoTX_LGI_LDPC_without_STBC_or_CDD')
        if self.kind == 'CANDIDATE':
            a, b, s, final = self.series
            if (tuple(x.nss for x in self.series) != (2, 2, 1, 1)
                    or tuple(x.stbc for x in self.series) != (False, False, True, False)
                    or tuple(x.chain_mask for x in self.series[:3]) != (3, 3, 3)
                    or not a.rate >= b.rate >= s.rate >= final.rate == 0
                    or tuple(x.sgi for x in self.series) != (1, 0, 0, 0)
                    or not all(x.ldpc == 1 and x.preamble_type == 3 for x in self.series)):
                raise ValueError('candidate_ladder_invariant')
            expected = {'chain0': 1, 'chain1': 2, 'cdd_hypothesis': 3}.get(self.final_branch)
            if final.chain_mask != expected:
                raise ValueError('final_chain_invariant')

    def native_payload(self):
        raise NativeWmiAbiUnqualified('BLOCKED: no vendor188B binding, packet fields or transport qualification')

    def as_dict(self):
        return dict(policy_id=self.policy_id, kind=self.kind, attempts=list(self.attempts),
                    series=[asdict(s) for s in self.series], final_branch=self.final_branch,
                    cdd_model_assumption=self.cdd_model_assumption,
                    cdd_effective_hardware_support_verified=False,
                    cdd_configuration_encoded_by_stbc_bit=False,
                    descriptor_templates_are_deploy_payloads=False)


def make_policy(initial_mcs=6, attempts=(1, 1, 2, 2), final_branch='chain0',
                capabilities=None, cdd_model_assumption=False):
    cap = PeerCapabilities() if capabilities is None else capabilities
    if not isinstance(cap, PeerCapabilities):
        raise ValueError('typed_peer_capabilities_required')
    c.integer(initial_mcs, 'initial_mcs', 0, 8)
    if (cap.max_nss != 2 or cap.tx_chain_mask != 3 or not cap.ldpc or not cap.stbc
            or not cap.sgi or initial_mcs > cap.max_vht_mcs):
        raise ValueError('declared_peer_2SS_twoTX_LDPC_STBC_GI_capability_required')
    if final_branch not in ('chain0', 'chain1', 'cdd_hypothesis'):
        raise ValueError('unknown_final_branch')
    mask = {'chain0': 1, 'chain1': 2, 'cdd_hypothesis': 3}[final_branch]
    series = (SeriesBwDescriptor(initial_mcs, 2, 3, sgi=1),
              SeriesBwDescriptor(max(0, initial_mcs - 1), 2, 3),
              SeriesBwDescriptor(min(3, max(0, initial_mcs - 2)), 1, 3, stbc=True),
              SeriesBwDescriptor(0, 1, mask))
    name = 'mcs{}_a{}_{}'.format(initial_mcs, ''.join(map(str, attempts)), final_branch)
    return RetryPolicy(name, 'CANDIDATE', series, attempts, final_branch, cdd_model_assumption)


def policies():
    candidates = [make_policy(mcs, attempts, branch, cdd_model_assumption=branch == 'cdd_hypothesis')
                  for mcs in (4, 6, 8) for attempts in ((1, 1, 1, 1), (1, 1, 2, 2))
                  for branch in ('chain0', 'chain1', 'cdd_hypothesis')]
    for name, rates in [('FIXED_2SS_PROXY', (6, 6, 6, 6)),
                        ('DESCENDING_2SS_PROXY', (8, 6, 4, 2))]:
        candidates.append(RetryPolicy(name, 'MODELED_BASELINE_PROXY',
                                     tuple(SeriesBwDescriptor(r, 2, 3) for r in rates),
                                     (1, 1, 2, 2), 'baseline_2ss'))
    return sorted(candidates, key=lambda x: x.policy_id)


def _percentile(values, quantile):
    if not values:
        return None
    ordered = sorted(values)
    point = (len(ordered) - 1) * quantile
    low = int(point)
    return ordered[low] + (ordered[min(low + 1, len(ordered) - 1)] - ordered[low]) * (point - low)


def _trace(scenario, seed, packets, interval):
    traffic = random.Random(seed ^ 0x19B7)
    channel = random.Random(seed ^ 0x45E3)
    rows, now, in_burst = [], 0., False
    for packet_id in range(packets):
        now += traffic.expovariate(1 / interval)
        in_burst = channel.random() < (scenario['burst_persistence'] if in_burst else scenario['burst_probability'])
        penalty = scenario['burst_penalty_db'] if in_burst else 0.
        snr = tuple(v - penalty + channel.gauss(0, 1.5) for v in scenario['chain_snr_db'])
        # Separate deterministic per-packet draw streams; every policy sees the same rows.
        outcomes = random.Random((seed << 20) ^ packet_id ^ 0xA001)
        backoff = random.Random((seed << 20) ^ packet_id ^ 0xB002)
        rows.append((now, snr, tuple(outcomes.random() for _ in range(12)),
                     tuple(backoff.random() for _ in range(12))))
    return rows


def _success_probability(series, snr, multipath, cdd=False):
    effective = min(snr) - 2. if series.nss == 2 else max(snr)
    if series.nss == 1 and series.chain_mask in (1, 2):
        effective = snr[0 if series.chain_mask == 1 else 1]
    effective += 1. if series.ldpc else 0.
    effective += 3. if series.stbc else 1. if cdd else 0.
    effective -= multipath * (1. if series.sgi else .15)
    exponent = max(-60., min(60., (effective - ILLUSTRATIVE_SNR_THRESHOLD_DB[series.rate]) / 2.))
    return 1. / (1. + math.exp(-exponent))


def simulate(policy, scenario, seed, *, packets=128, queue_limit=32, payload_bytes=1200,
             arrival_interval_ms=.18, success_override=None):
    if not isinstance(policy, RetryPolicy):
        raise ValueError('typed_policy_required')
    if type(scenario) is not str or scenario not in SCENARIOS:
        raise ValueError('unknown_synthetic_scenario')
    c.integer(seed, 'seed', 0, 2 ** 31 - 1)
    c.integer(packets, 'packets', 0, 1024)
    c.integer(queue_limit, 'queue_limit', 0, 1024)
    c.integer(payload_bytes, 'payload_bytes', 64, 1500)
    interval = c.finite(arrival_interval_ms, 'arrival_interval_ms', 1e-6, 100.)
    if success_override is not None:
        success_override = c.finite(success_override, 'success_override', 0, 1)
    settings = SCENARIOS[scenario]
    trace = _trace(settings, seed, packets, interval)
    env = simpy.Environment()
    medium = simpy.Resource(env, capacity=1)
    delivered = exhausted = queue_dropped = attempts_total = 0
    busy_ms = 0.
    terminal_delays, delivered_delays, used_series = [], [], [0, 0, 0, 0]

    def packet(row):
        nonlocal delivered, exhausted, queue_dropped, attempts_total, busy_ms
        arrival, snr, draws, backoffs = row
        yield env.timeout(arrival)
        if medium.count and len(medium.queue) >= queue_limit:
            queue_dropped += 1
            terminal_delays.append(0.)
            return
        with medium.request() as request:
            yield request
            attempt_index = 0
            for index, (series, budget) in enumerate(zip(policy.series, policy.attempts)):
                rate = MCS_RATE_MBPS_1SS_LGI[series.rate] * series.nss * (10 / 9 if series.sgi else 1.)
                for _ in range(budget):
                    probability = _success_probability(series, snr, settings['multipath_penalty_db'],
                                                       policy.final_branch == 'cdd_hypothesis' and index == 3)
                    if success_override is not None:
                        probability = success_override
                    success = draws[attempt_index] < probability
                    # Synthetic per-attempt preamble + data + ACK/timeout + bounded exponential backoff.
                    cw = min(1023, 15 * 2 ** attempt_index)
                    duration = .04 + payload_bytes * 8 / (rate * 1000.) + .044 + backoffs[attempt_index] * cw * .009
                    yield env.timeout(duration)
                    busy_ms += duration
                    attempts_total += 1
                    used_series[index] += 1
                    attempt_index += 1
                    if success:
                        delivered += 1
                        delay = env.now - arrival
                        terminal_delays.append(delay)
                        delivered_delays.append(delay)
                        return
            exhausted += 1
            terminal_delays.append(env.now - arrival)

    jobs = [env.process(packet(row)) for row in trace]
    event_cap = packets * (sum(policy.attempts) + 12) * 4 + 100
    horizon_cap = (trace[-1][0] if trace else 0.) + packets * sum(policy.attempts) * 15. + 1.
    steps = 0
    if jobs:
        done = simpy.AllOf(env, jobs)
        while not done.triggered:
            if steps >= event_cap or env.peek() > horizon_cap:
                raise ValueError('simulation_event_or_horizon_cap')
            env.step()
            steps += 1
    elapsed = float(env.now)
    dropped = exhausted + queue_dropped
    if delivered + dropped != packets or len(terminal_delays) != packets:
        raise ValueError('packet_conservation_failure')
    if busy_ms > elapsed + 1e-8 or attempts_total > packets * sum(policy.attempts):
        raise ValueError('airtime_or_attempt_conservation_failure')
    return dict(policy_id=policy.policy_id, scenario=scenario, seed=seed,
                generated=packets, delivered=delivered, retry_exhausted=exhausted,
                queue_dropped=queue_dropped, outstanding=0, payload_bytes=payload_bytes,
                offered_bytes=packets * payload_bytes, delivered_bytes=delivered * payload_bytes,
                dropped_bytes=dropped * payload_bytes, attempts_total=attempts_total,
                attempts_by_series=used_series, elapsed_ms=elapsed, busy_ms=busy_ms,
                goodput_mbps=delivered * payload_bytes * 8 / (elapsed * 1000.) if elapsed else 0.,
                loss_ratio=dropped / packets if packets else 0.,
                terminal_delay_p99_ms=_percentile(terminal_delays, .99),
                delivered_delay_p50_ms=_percentile(delivered_delays, .5),
                delivered_delay_p99_ms=_percentile(delivered_delays, .99),
                event_steps=steps, event_cap=event_cap, horizon_cap_ms=horizon_cap,
                input_kind='SYNTHETIC_NOT_CALIBRATED_RF', success_override=success_override)


def rank_pareto(rows, *, seed=354):
    c.integer(seed, 'optimizer_seed', 0, 2 ** 31 - 1)
    if type(rows) is not list or not 1 <= len(rows) <= 64:
        raise ValueError('finite_population_1_to_64_required')
    ordered = sorted(rows, key=lambda r: r['policy_id'] if type(r) is dict and type(r.get('policy_id')) is str else '')
    ids, objectives = [], []
    for row in ordered:
        if type(row) is not dict or type(row.get('policy_id')) is not str or not row['policy_id']:
            raise ValueError('policy_id_required')
        if row['policy_id'] in ids:
            raise ValueError('duplicate_policy_id')
        ids.append(row['policy_id'])
        f = row.get('objectives')
        if type(f) is not list or len(f) != 3:
            raise ValueError('three_objectives_required')
        objectives.append([c.finite(x, 'objective', -1e9, 1e9) for x in f])

    class FiniteProblem(Problem):
        def __init__(self):
            super().__init__(n_var=1, n_obj=3, xl=0, xu=len(ids) - 1)

        def _evaluate(self, x, out, *args, **kwargs):
            out['F'] = np.asarray([objectives[int(i)] for i in x[:, 0]], dtype=float)

    result = minimize(FiniteProblem(), NSGA2(pop_size=len(ids), sampling=np.arange(len(ids)).reshape(-1, 1),
                                            eliminate_duplicates=False), ('n_gen', 1), seed=seed, verbose=False)
    ranked = []
    for item in result.pop:
        i = int(item.X[0])
        crowding = float(item.get('crowding'))
        ranked.append(dict(policy_id=ids[i], rank=int(item.get('rank')),
                           crowding=crowding if math.isfinite(crowding) else None,
                           crowding_is_extreme=not math.isfinite(crowding), objectives=objectives[i]))
    ranked.sort(key=lambda x: (x['rank'], x['policy_id']))
    return dict(algorithm='pymoo.NSGA2_FULL_FINITE_POPULATION_ENVIRONMENTAL_RANKING',
                n_evaluated=len(ids), n_generations=1, seed=seed, ranked=ranked,
                pareto_ids=[r['policy_id'] for r in ranked if r['rank'] == 0],
                objective_labels=['negative_mean_goodput_mbps', 'mean_terminal_p99_ms', 'mean_loss_ratio'],
                continuous_or_global_optimum_claim=False)


def analyze(*, packets=128):
    c.integer(packets, 'analysis_packets', 1, 1024)
    rows = []
    for policy in policies():
        runs = [simulate(policy, scenario, seed, packets=packets) for scenario in SCENARIOS for seed in SEEDS]
        per_scenario = {}
        for scenario in SCENARIOS:
            subset = [r for r in runs if r['scenario'] == scenario]
            per_scenario[scenario] = {key: dict(mean=statistics.mean(r[key] for r in subset),
                                                replication_sd=statistics.stdev(r[key] for r in subset),
                                                minimum=min(r[key] for r in subset), maximum=max(r[key] for r in subset))
                                      for key in ('goodput_mbps', 'loss_ratio', 'terminal_delay_p99_ms')}
        objectives = [-statistics.mean(r['goodput_mbps'] for r in runs),
                      statistics.mean(r['terminal_delay_p99_ms'] for r in runs),
                      statistics.mean(r['loss_ratio'] for r in runs)]
        rows.append(dict(**policy.as_dict(), objectives=objectives, per_scenario=per_scenario, runs=runs))
    return dict(policies=rows, pareto=rank_pareto(rows),
                summary=dict(candidates=18, modeled_baseline_proxies=2, scenarios=4, seeds=3,
                             replications=len(rows) * len(SCENARIOS) * len(SEEDS), packets_per_replication=packets,
                             hardware_results=0))


def binary_sender(root):
    path = root / 'artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/umac.ko'
    data = c.read(path, '660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6')
    evidence = c.elf_symbols(path, '^wmi_send_node_rate_sched$', root)
    if len(evidence['symbols']) != 1:
        raise ValueError('one_pinned_rate_schedule_sender_required')
    symbol = evidence['symbols'][0]
    if symbol['section_offset'] != 0xb0120 or symbol['bytes'] != 160:
        raise ValueError('pinned_sender_boundary_changed')
    checks = []
    for relative, expected in ((0x24, 0x240500bc), (0x44, 0x240600bc),
                               (0x60, 0x240600bc), (0x64, 0x34079044)):
        offset = symbol['file_offset'] + relative
        word = struct.unpack_from('>I', data, offset)[0]
        if word != expected:
            raise ValueError('pinned_sender_instruction_changed')
        checks.append(dict(symbol_relative_offset=relative, file_offset=offset, mips_word_hex=f'{word:08x}'))
    return dict(**evidence, bounded_instruction_checks=checks, declared_length_bytes=188,
                declared_command_id=0x9044, native_series_layout_authenticated=False,
                installed_build_acceptance_verified=False)


def build(root=ROOT):
    root = c.local_path(root)
    header = verify_series_header(root / SERIES_HEADER)
    header['source'] = c.binding(root / SERIES_HEADER, root, expected=HEADER_SHA256)
    study = analyze()
    report = dict(stage='354A', task_id='T-S354A-WMI-4SERIES-RETRY-FALLBACK-PARETO',
                  status='COMPLETE_SYNTHETIC_STUDY_NATIVE_ABI_BLOCKED', model_version=1,
                  libraries={n: version(n) for n in ('simpy', 'pymoo', 'numpy')},
                  static_sources=[c.binding(root / p, root) for p in (
                      'tools/sim/build_stage354a_wmi_4series_retry_fallback_pareto.py',
                      'tests/test_stage354a.py', 'tools/re/ground_up_release_common.py',
                      'controller/stage18_wmi_rate_schedule_and_sub20mhz_controller.py',
                      'controller/airmax_wire.py')], primary_descriptor_header=header,
                  binary_sender=binary_sender(root),
                  scenarios=SCENARIOS, seed_manifest=list(SEEDS), **study,
                  model_assumptions=dict(
                      medium='one FIFO SimPy Resource; retries retain reservation; no competing stations',
                      time_unit='milliseconds', payload_bytes=1200, queue_limit=32, arrival_interval_ms=.18,
                      traffic='128 finite exponential arrivals; empty initial queue; terminate after all terminal outcomes',
                      snr_thresholds_db=list(ILLUSTRATIVE_SNR_THRESHOLD_DB),
                      rate_1ss_lgi_vht20_mbps=list(MCS_RATE_MBPS_1SS_LGI),
                      decoder='illustrative logistic success width2dB; twoSS min-chain SNR minus2dB',
                      diversity_assumptions_db=dict(ldpc=1, stbc_1ss_two_tx=3, cdd_hypothesis=1),
                      delay='p99 of terminal packet sojourn; immediate queue drops contribute0; loss objective retained',
                      averaging='equal scenario/seed weights; mean of per-run p99 is NOT pooled p99',
                      inference='replication SD descriptive only; no confidence or causal hardware claim',
                      common_random_numbers='separate traffic/channel/outcome/backoff RNG streams shared across policies'),
                  limitations=[
                      'Baselines are fixed/descending twoSS modeled proxies, not Minstrel or ath10k implementations or measurements.',
                      'SNR/PER, diversity gains, burst correlation, preamble/ACK/backoff and traffic are illustrative uncalibrated inputs.',
                      'No A-MPDU, BA recovery, TCP dynamics, airMAX TDMA, actual fading waveform, regulatory or peer interoperability validation.',
                      'CDD requires an explicit model assumption; chain_mask=3 and STBC=0 do not configure or prove hardware CDD.',
                      'Finite enumeration and library ranking validate this model only; no physical RF gain or optimal native schedule follows.'],
                  boundary=dict(hardware_access=False, network_access=False, module_execution=False,
                                deployment_allowed=False, automatic_execution_allowed=False, physical_acceptance=False,
                                measured_rf_improvement=False, native_188b_wmi_abi='BLOCKED',
                                native_wmi_payload_hex=None, packet_fields_complete=False,
                                transport_endianness_verified=False, peer_capabilities_runtime_verified=False),
                  primary_documentation=[
                      'https://simpy.readthedocs.io/en/stable/simpy_intro/shared_resources.html',
                      'https://pymoo.org/algorithms/moo/nsga2.html'],
                  summary_qualification='SIMULATION_SOFTWARE_EVIDENCE_ONLY_NOT_RF_IMPROVEMENT')
    text = '''<!-- doc-head: Stage354A bounded synthetic four-series retry and finite Pareto study -->
Actual SimPy scheduling and pymoo ranking use uncalibrated synthetic inputs.
Native188-byte WMI ABI, packet fields, transport and physical acceptance stay blocked.
<!-- /doc-head -->

# Stage354A

Parent: offline RE1 retry/control-boundary analysis following Stage353.
Question: what tradeoffs does an explicit four-series model produce under the
same finite synthetic channel traces? No new device experiment is performed.

Run `python tools/sim/build_stage354a_wmi_4series_retry_fallback_pareto.py`, then
`python -m pytest -q -o addopts= tests/test_stage354a.py`.
The JSON binds the implementation, tests, helper, Stage18 codec and held header.
The exact header is frozen at artifacts/verification/stage354a/series_bw.h;
its pinned SHA256 is verified before simulation, without a temporary-directory dependency.

## Control boundary

The18 candidates use initial2SS SGI, retry2SS LGI, then1SS STBC across TWO TX
chains, followed by1SS LGI on chain0/chain1 or an explicit CDD hypothesis.
STBC is not one TX chain. CDD is not the STBC bit; enabling two chains with
STBC=0 does not establish a cyclic-delay configuration or target support.
Peer2SS/twoTX/LDPC/STBC/GI declarations are required by the candidate builder.
These declarations and the CDD assumption are model inputs, not runtime readbacks.
Every model series is VHT20/MCS0..8 with at most2SS/twoTX; proxy baselines require
2SS/mask3/LGI/LDPC and no STBC, CDD or beamforming. Other shared-codec modes reject.
The source-pinned16-byte descriptor template is not a complete PPDU or a native
188-byte WMI message. No transport endianness or retry-array binding is qualified.
No deploy payload is emitted; native_payload() always raises the ABI blocker.
Held WA8.7.25 umac wmi_send_node_rate_sched (.text+0xb0120,160B) has bounded
MIPS immediates0xbc and opcode0x9044. Its symbol/instruction hashes are retained.
This confirms a static sender length/opcode, not four-series payload semantics.

## Conceptual model and bounds

Twenty policies include two fixed/descending2SS PROXY baselines. Neither baseline
implements or measures Minstrel, ath10k, proprietary firmware rate control or airMAX.
Four scenarios are balanced control, mirrored asymmetric foliage, and correlated
multipath bursts. Each uses three fixed seeds and128 finite packet arrivals.
The240 replications start empty and drain every generated packet to a recorded
delivery, retry exhaustion or queue drop. This is a terminating transient study.
One SimPy FIFO resource serializes modeled transmissions; retries retain ownership.
SNR thresholds, diversity offsets, logistic PER, arrivals and timing overheads are
illustrative assumptions disclosed in JSON, not receiver calibration or RF evidence.
Independent RNG streams provide common random inputs across policies.
Packet/entity, attempt, event and simulated-horizon caps prevent open-ended runs.

Generated=delivered+retry_exhausted+queue_dropped, outstanding=0; payload bytes are
conserved. Goodput counts delivered bytes once over elapsed simulation time.
Busy time cannot exceed elapsed time. Every failed attempt consumes modeled service.
Queue drops have zero terminal delay; delivered-only delays and loss are separately
reported so a low delay from discarding packets cannot be read as healthy service.

## Finite Pareto interpretation

pymoo NSGA-II evaluates ALL20 finite policies as one complete initial generation.
Objectives minimize negative mean goodput, mean per-run terminal p99, and mean loss.
There is no continuous search, unseen-policy optimum or convergence claim.
Means give equal weight to the12 fixed scenario/seed combinations. A mean of p99s
is not a pooled p99. Per-scenario replication SD and ranges are descriptive, not
confidence intervals or statistical evidence of a causal radio improvement.
Results can expose tradeoffs in the chosen model, including negative outcomes.

Missing validation: measured per-chain quality/PER and burst statistics, actual
retry traces, CDD configuration, peer capabilities, aggregate/BA/TCP interactions,
packet-dependent duration/padding/symbol fields, vendor188-byte ABI and legal RF
characterization. No physical acceptance, measured gain or deployment follows.
Decision: KEEP as a reproducible offline hypothesis model; native execution BLOCKED.

Primary APIs: [SimPy Resource](https://simpy.readthedocs.io/en/stable/simpy_intro/shared_resources.html),
[pymoo NSGA-II](https://pymoo.org/algorithms/moo/nsga2.html).
'''
    c.write_doc(root / DOC, text)
    report['outputs'] = {DOC: c.binding(root / DOC, root)}
    c.write_json(root / OUT, report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    print(build(args.root)['summary'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
