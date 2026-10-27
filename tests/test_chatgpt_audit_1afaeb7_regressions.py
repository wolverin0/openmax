"""Proposed adversarial regression tests for the real openMAX checkout.

Written for commit 1afaeb7712161068044238755166dff3a7043248.
NOT RUN against the full repository in this audit environment. Several are
expected to fail on that commit; they specify desired fail-closed behavior.
Pure Python evaluation only: no SSH, shell execution, radio access, or writes.
Run from the repository root after reviewing import-time behavior:
    python -m pytest /path/to/test_audit_regressions.py -q
"""
import math
import pytest

from analysis.regression_gate.gatekeeper import (
    RegressionGatekeeper, RunMetrics, build_paired_blocks,
)
from controller.pb_060_070_autonomous_search_and_phy_gate import (
    SearchCandidateConfig, evaluate_pb060_search_campaign,
)


def metric(run_id, arm, block, gp=100.0, p99=20.0, **overrides):
    args = dict(run_id=run_id, arm=arm, block_index=block,
                goodput_mbps=gp, p95_lat_ms=p99 * .75, p99_lat_ms=p99,
                loss_pct=0., jain_fairness=.9, channel_width_mhz=20,
                worst_peer_goodput_mbps=20.)
    args.update(overrides)
    return RunMetrics(**args)


def winning_runs(prefix="d", n=8):
    return [m for i in range(n) for m in
            (metric(f"{prefix}-A-{i}", "A", i),
             metric(f"{prefix}-B-{i}", "B", i, gp=120., p99=10.))]


def null_runs(prefix="null", n=8):
    return [m for i in range(n) for m in
            (metric(f"{prefix}-A-{i}", "A", i),
             metric(f"{prefix}-B-{i}", "B", i))]


def candidate(name="candidate", negative=False):
    return SearchCandidateConfig(
        candidate_id=name, channel_width_mhz=20, tx_power_dbm=18,
        ldpc_enabled=True, stbc_enabled=False, sgi_enabled=True,
        rts_threshold_bytes=256, aql_be_limit_us=4000,
        is_negative_control=negative,
    )


@pytest.mark.parametrize("field", ["goodput_mbps", "p95_lat_ms", "p99_lat_ms", "loss_pct", "jain_fairness"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_nonfinite_metrics_are_rejected(field, value):
    with pytest.raises((ValueError, TypeError)):
        metric("bad", "B", 0, **{field: value})


def test_missing_channel_width_is_not_assumed_20mhz():
    with pytest.raises((ValueError, TypeError)):
        RunMetrics(run_id="bad", arm="A", goodput_mbps=100.,
                   p95_lat_ms=10., p99_lat_ms=20., loss_pct=0., jain_fairness=.9)


def test_goodput_per_mhz_must_match_receiver_goodput_and_width():
    with pytest.raises((ValueError, TypeError)):
        metric("bad", "B", 0, goodput_per_mhz=999.)


def test_disjoint_block_ids_are_not_silently_zipped():
    runs = [metric("a1", "A", 1), metric("b10", "B", 10),
            metric("a2", "A", 2), metric("b11", "B", 11)]
    with pytest.raises(ValueError):
        build_paired_blocks(runs)


def test_duplicate_block_ids_are_not_silently_repaired():
    runs = [metric("a1", "A", 1), metric("a2", "A", 1),
            metric("b1", "B", 1), metric("b2", "B", 1)]
    with pytest.raises(ValueError):
        build_paired_blocks(runs)


def test_latency_first_objective_does_not_require_a_throughput_increase():
    runs = [m for i in range(8) for m in
            (metric(f"a{i}", "A", i, gp=100., p99=100.),
             metric(f"b{i}", "B", i, gp=100., p99=10.))]
    verdict = RegressionGatekeeper().evaluate_paired(runs).verdict
    assert verdict != "REJECT", "A latency-only research objective must be selectable explicitly"


def test_default_api_cannot_keep_two_constant_pairs():
    decision = RegressionGatekeeper().evaluate(winning_runs(n=2))
    assert decision.verdict not in {"KEEP", "PROMOTE", "KEEP_FOR_REPLICATION"}


def test_campaign_requires_a_measured_negative_control():
    result = evaluate_pb060_search_campaign(
        [candidate()], {"candidate": winning_runs("disc")},
        {"candidate": winning_runs("hold")})
    assert not result["campaign_passed"]


def test_declared_control_with_no_observations_is_not_a_control():
    result = evaluate_pb060_search_campaign(
        [candidate(), candidate("negative", negative=True)],
        {"candidate": winning_runs("disc")},
        {"candidate": winning_runs("hold")})
    assert not result["campaign_passed"]


def test_holdout_cannot_reuse_discovery_measurements():
    discovery = winning_runs("same")
    controls = null_runs()
    result = evaluate_pb060_search_campaign(
        [candidate(), candidate("negative", negative=True)],
        {"candidate": discovery, "negative": controls},
        {"candidate": discovery})
    assert not result["campaign_passed"]


def test_missing_ping_observations_never_look_perfect():
    from workloads.flent_orchestrator import FlentWorkloadConfig, FlentWorkloadOrchestrator
    orch=FlentWorkloadOrchestrator(FlentWorkloadConfig(server_host='server',station_hosts=['one','two']))
    report=orch.synthesize_report({'one':{'goodput_mbps':40},'two':{'goodput_mbps':40}}, {'one':[],'two':[]})
    assert report.fleet_p99_latency_ms is None
    assert report.status=='INVALID'
    assert all(row.packet_loss_pct is None for row in report.station_results.values())
    assert all(row.total_packets_sent is None for row in report.station_results.values())


def test_iperf_error_and_sender_only_are_invalid():
    from workloads.flent_orchestrator import FlentWorkloadOrchestrator as f
    for text in ['{"error":"unable to connect"}', '{"end":{"sum_sent":{"bits_per_second":80000000}}}']:
        with pytest.raises(ValueError):
            f.parse_iperf3_json(text)


def test_powerbeam_30mhz_never_changes_to_20mhz():
    from controller.powerbeam_m5_and_5ac_bench_harness import PowerBeamBlockSample
    sample=PowerBeamBlockSample(run_id='m5-30',arm='A',block_index=0,channel_width_mhz=30,
        goodput_mbps=90,p50_lat_ms=1,p95_lat_ms=2,p99_lat_ms=3,loss_pct=0,
        jain_fairness=.9,worst_peer_goodput_mbps=10,family='XW')
    assert sample.to_gatekeeper_run_metrics().channel_width_mhz==30


def test_null_channel_matrix_is_not_rank_two():
    from tools.qca988x.channel_capture_and_sdr_correlator import summarize_2x2_subcarrier_matrices
    with pytest.raises(ValueError):
        summarize_2x2_subcarrier_matrices('null',[(0j,0j,0j,0j)]*4)


def test_capture_correlation_requires_same_unique_state_ids():
    from tools.qca988x.channel_capture_and_sdr_correlator import (
        summarize_2x2_subcarrier_matrices, evaluate_pb_022_and_pb_024_sdr_correlation)
    a=[summarize_2x2_subcarrier_matrices(f'a-{i}',[(1+0j,0j,0j,complex(.9/(i+1))) ]*4) for i in range(5)]
    b=[summarize_2x2_subcarrier_matrices(f'b-{i}',[(1+0j,0j,0j,complex(.9/(i+1))) ]*4) for i in range(5)]
    with pytest.raises(ValueError):
        evaluate_pb_022_and_pb_024_sdr_correlation(a,b)


@pytest.mark.parametrize('overrides',[dict(p95_lat_ms=30,p99_lat_ms=20),dict(loss_pct=-1),
                                     dict(jain_fairness=1.1),dict(goodput_mbps=-1)])
def test_impossible_measurements_are_rejected(overrides):
    with pytest.raises(ValueError):metric('invalid','B',0,**overrides)


def test_intermediate_drift_cannot_hide_between_equal_endpoints():
    from analysis.regression_gate.gatekeeper import detect_baseline_drift
    runs=winning_runs()
    runs[6].goodput_mbps=50;runs[6].goodput_per_mhz=2.5
    detected,_,_=detect_baseline_drift(runs)
    assert detected


def test_missing_worst_peer_and_boolean_holdout_never_promote():
    runs=winning_runs()
    for run in runs:run.worst_peer_goodput_mbps=None
    result=RegressionGatekeeper().evaluate_paired(runs,holdout_replicated=True)
    assert result.verdict=='INCONCLUSIVE' and not result.promotion_eligible


def test_synthetic_evidence_origin_cannot_be_promoted_by_mutation():
    row=metric('synthetic','A',0,evidence_state='SYNTHETIC')
    with pytest.raises(ValueError):row.evidence_state='BENCH_REPLICATED'


def test_500_hypotheses_resolution_is_checked_without_relaxing_alpha():
    from analysis.regression_gate.gatekeeper import compute_adjusted_alpha,paired_sign_flip_p_value
    alpha=compute_adjusted_alpha(.05,500)
    assert 2/(2**14)>alpha>2/(2**15)
    assert paired_sign_flip_p_value([-10.0]*15)==pytest.approx(2/(2**15))
    runs=winning_runs(n=15)
    # Rebuild typed fixture rows; never relabel an existing source.
    runs=[metric(r.run_id,r.arm,r.block_index,gp=r.goodput_mbps,p99=r.p99_lat_ms,evidence_state='SYNTHETIC') for r in runs]
    gate=RegressionGatekeeper(num_hypotheses_tested=500)
    result=gate.evaluate_paired(runs)
    assert result.verdict=='SYNTHETIC_PASS' and not result.promotion_eligible
    assert result.adjusted_alpha==alpha and result.p_value<alpha
    assert gate.evaluate_paired(runs[:28]).verdict=='INCONCLUSIVE'


def test_actual_sent_count_and_receiver_rate_stay_separate():
    import json
    from workloads.flent_orchestrator import FlentWorkloadConfig,FlentWorkloadOrchestrator as f
    iperf=f.parse_iperf3_json(json.dumps({'end':{'sum_received':{'bits_per_second':10e6},
                                              'sum_sent':{'bits_per_second':80e6,'retransmits':0}}}))
    assert iperf['goodput_mbps']==10 and iperf['sender_mbps']==80
    orch=f(FlentWorkloadConfig(server_host='server',station_hosts=['one']))
    result=orch.synthesize_report({'one':iperf},{'one':dict(sent=10,received=2,latencies_ms=[.001,.002],duplicates=0)})
    row=result.station_results['one']
    assert row.total_packets_sent==10 and row.packets_received==2 and row.packet_loss_pct==80
    assert row.rtt_p99_ms==.002


def test_missing_station_stays_in_denominator():
    from workloads.flent_orchestrator import FlentWorkloadConfig,FlentWorkloadOrchestrator as f
    report=f(FlentWorkloadConfig(server_host='server',station_hosts=['one','two'])).synthesize_report(
        {'one':{'goodput_mbps':10}}, {'one':[1,2]})
    assert set(report.station_results)=={'one','two'}
    assert report.aggregate_goodput_mbps is None and report.jain_fairness_index is None
    assert report.fleet_p99_latency_ms is None and report.status=='INVALID'


@pytest.mark.parametrize('attack',['unhealthy_discovery','overlapping_holdout','false_channel_width'])
def test_consistent_receipts_cannot_hide_invalid_experimental_design(tmp_path,attack):
    import hashlib,json,runpy
    from pathlib import Path
    fixture=runpy.run_path(str(Path(__file__).with_name('test_chatgpt_audit_pb_campaign.py')))['physical_schema_fixture']
    configs,disc,hold=fixture(tmp_path)
    rows=disc['candidate'] if attack=='unhealthy_discovery' else hold['candidate']
    if attack=='false_channel_width':rows=disc['candidate']+hold['candidate']
    for row in rows:
        if attack=='unhealthy_discovery' and row.arm!='B':continue
        path=tmp_path/row.raw_evidence_path;record=json.loads(path.read_text())
        if attack=='unhealthy_discovery':
            row.firmware_resets=1;record['metrics']['firmware_resets']=1
        elif attack=='overlapping_holdout':
            row.window_start_s=200;row.window_end_s=201
            record.update(window_start_s=200,window_end_s=201)
        else:
            row.channel_width_mhz=30;row.goodput_per_mhz=None
            record['metrics']['channel_width_mhz']=30
        blob=json.dumps(record,sort_keys=True).encode();path.write_bytes(blob)
        row.raw_sha256=hashlib.sha256(blob).hexdigest()
    receipt=json.loads((tmp_path/'replication.json').read_text())
    for key,cohort in [('discovery',disc['candidate']),('holdout',hold['candidate'])]:
        receipt[key]=[dict(run_id=r.run_id,raw_sha256=r.raw_sha256) for r in cohort]
    (tmp_path/'replication.json').write_text(json.dumps(receipt))
    result=RegressionGatekeeper(evidence_root=tmp_path).evaluate_paired(hold['candidate'],
        discovery_runs=disc['candidate'],replication_receipt_path='replication.json',
        candidate_fingerprint=configs[0].fingerprint())
    assert result.verdict!='PROMOTE' and not result.promotion_eligible


def test_channel_rank_is_invariant_under_nonzero_scalar_attenuation():
    from tools.qca988x.channel_capture_and_sdr_correlator import summarize_2x2_subcarrier_matrices as summarize
    large=summarize('large',[(1+0j,0j,0j,0j)]*4)
    small=summarize('small',[(1e-8+0j,0j,0j,0j)]*4)
    assert small.rank_classification==large.rank_classification
    assert small.mean_sigma1>0


def test_failed_sentinel_cannot_be_discarded_from_campaign_health(tmp_path):
    import hashlib,json,runpy
    from dataclasses import replace
    from pathlib import Path
    fixture=runpy.run_path(str(Path(__file__).with_name('test_chatgpt_audit_pb_campaign.py')))['physical_schema_fixture']
    configs,disc,hold=fixture(tmp_path)
    original=hold['candidate'][0]
    sentinel=replace(original,run_id='failed-sentinel',block_index=None,is_sentinel=True,
        firmware_resets=1,window_start_s=217.,window_end_s=218.,raw_evidence_path='sentinel.json')
    record=json.loads((tmp_path/original.raw_evidence_path).read_text())
    record.update(run_id=sentinel.run_id,window_start_s=217.,window_end_s=218.,
                  arm='A',block_index=None,is_sentinel=True)
    record['metrics']['firmware_resets']=1
    blob=json.dumps(record,sort_keys=True).encode();(tmp_path/'sentinel.json').write_bytes(blob)
    sentinel.raw_sha256=hashlib.sha256(blob).hexdigest();hold['candidate'].append(sentinel)
    receipt=json.loads((tmp_path/'replication.json').read_text())
    receipt['holdout']=[dict(run_id=r.run_id,raw_sha256=r.raw_sha256) for r in hold['candidate']]
    (tmp_path/'replication.json').write_text(json.dumps(receipt))
    result=RegressionGatekeeper(evidence_root=tmp_path).evaluate_paired(hold['candidate'],
        discovery_runs=disc['candidate'],replication_receipt_path='replication.json',
        candidate_fingerprint=configs[0].fingerprint())
    assert result.verdict!='PROMOTE' and not result.promotion_eligible


@pytest.mark.parametrize('created_at',[True,False,-1.0])
def test_frozen_plan_timestamp_is_a_real_nonnegative_number(tmp_path,created_at):
    import json,runpy
    from pathlib import Path
    fixture=runpy.run_path(str(Path(__file__).with_name('test_chatgpt_audit_pb_campaign.py')))['physical_schema_fixture']
    configs,disc,hold=fixture(tmp_path)
    path=tmp_path/'replication.json';receipt=json.loads(path.read_text())
    receipt['frozen_plan']['created_at_s']=created_at;path.write_text(json.dumps(receipt))
    result=RegressionGatekeeper(evidence_root=tmp_path).evaluate_paired(hold['candidate'],
        discovery_runs=disc['candidate'],replication_receipt_path='replication.json',
        candidate_fingerprint=configs[0].fingerprint())
    assert result.verdict!='PROMOTE' and not result.promotion_eligible


@pytest.mark.parametrize('threshold',[float('-inf'),float('inf'),float('nan'),-1,0,1.1,True])
def test_invalid_capture_threshold_cannot_approve_anticorrelation(threshold):
    from tools.qca988x.channel_capture_and_sdr_correlator import (
        summarize_2x2_subcarrier_matrices as summarize,evaluate_pb_022_and_pb_024_sdr_correlation as evaluate)
    ratios=[1,2,4,8,16]
    internal=[summarize(str(i),[(1+0j,0j,0j,complex(1/r))]*4) for i,r in enumerate(ratios)]
    external=[summarize(str(i),[(1+0j,0j,0j,complex(1/r))]*4) for i,r in enumerate(reversed(ratios))]
    with pytest.raises(ValueError):evaluate(internal,external,min_pearson_r=threshold)


@pytest.mark.parametrize('budget',[0,-2,True])
def test_invalid_resampling_budget_never_emits_negative_p_or_confidence(budget):
    from analysis.regression_gate.gatekeeper import paired_sign_flip_p_value,paired_bootstrap_ci_95
    with pytest.raises(ValueError):paired_sign_flip_p_value(list(range(1,18)),n_permutations=budget)
    with pytest.raises(ValueError):paired_bootstrap_ci_95([1,2,3],n_boot=budget)
