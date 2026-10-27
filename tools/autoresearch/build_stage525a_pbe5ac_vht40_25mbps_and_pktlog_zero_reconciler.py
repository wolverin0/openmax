#!/usr/bin/env python3
"""Stage525A saved PBE sweep vs separate WA pktlog experiment; no acquisition."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.autoresearch import stage525_530_common as h
from tools.re import ground_up_release_common as c

SCRIPT='tools/autoresearch/build_stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler.py'
OUT='artifacts/autoresearch/stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler.json'
DOC='docs/STAGE525A_PBE5AC_VHT40_25MBPS_AND_PKTLOG_ZERO_RECONCILER.md'
S487='artifacts/autoresearch/stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json'
S403='artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json'
P487='tools/benchmarks/run_stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.py'
P403='tools/benchmarks/run_stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.py'
P311='tools/benchmarks/run_stage311a_to_316a_wa_megamission.py'


def audit_profiles(obj):
    profiles=obj['profiles']
    if not isinstance(profiles,list) or not 1<=len(profiles)<=64:raise ValueError('profile_count')
    rows=[];ids=set();conflicts=[]
    for i,row in enumerate(profiles):
        if not isinstance(row,dict):raise ValueError('profile_object')
        pid=row['id']
        if not isinstance(pid,str) or not pid or pid in ids or len(pid)>160:raise ValueError('profile_id')
        ids.add(pid)
        dl=h.number(row['dl_mbps'],'dl');ul=h.number(row['ul_mbps'],'ul')
        aggregate=h.number(row['aggregate_mbps'],'aggregate')
        width=c.integer(row['width_mhz'],'width',5,160)
        index=c.integer(row['ap_nss'],'ap_nss_override',0,3)
        ping=row['ping_1472b'];count=c.integer(ping['count'],'ping_count',1,1000000)
        loss=h.number(ping['loss_pct'],'loss',0,100)
        values=[h.number(ping[k],k) for k in ('min_ms','p50_ms','p95_ms','max_ms')] if count else []
        if values!=sorted(values):raise ValueError('ping_quantile_order')
        small=row['ping_64b'];c.integer(small['count'],'small_ping_count',1,1000000)
        h.number(small['loss_pct'],'small_loss',0,100)
        small_values=[h.number(small[k],k) for k in ('min_ms','p50_ms','p95_ms','max_ms')]
        if small_values!=sorted(small_values):raise ValueError('small_ping_quantile_order')
        if abs(aggregate-(dl+ul))>.011:conflicts.append({'pointer':f'/profiles/{i}/aggregate_mbps','reason':'DL_UL_SUM_MISMATCH'})
        rows.append({'id':pid,'source_pointer':f'/profiles/{i}','dl_mbps':dl,'ul_mbps':ul,
                     'aggregate_mbps':aggregate,'computed_aggregate_mbps':round(dl+ul,8),'width_mhz':width,
                     'producer_ap_nss_override_index':index,'producer_intended_ap_streams':index+1,
                     'runtime_nss_verified':False,'ping_1472b':dict(count=count,loss_pct=loss),
                     'conditional_iid_95pct_loss_upper_bound':1-.05**(1/count) if count and loss==0 else None,
                     'source_role':'HARDCODED_REFERENCE_IN_PRODUCER' if row['htmode']=='VHT20' else 'SAVED_SWEEP_SUMMARY'})
    best=max(rows,key=lambda row:(row['ping_1472b']['loss_pct']<=10,row['aggregate_mbps']));peak=max(rows,key=lambda row:row['ul_mbps'])
    declared=obj['champion']
    if not isinstance(declared,dict):raise ValueError('champion_object')
    matched=next((p for p in profiles if p['id']==declared.get('id')),None)
    if matched is None or declared!=matched:conflicts.append({'pointer':'/champion','reason':'CHAMPION_COPY_MISMATCH'})
    if declared.get('id')!=best['id']:conflicts.append({'pointer':'/champion/id','reason':'NOT_MAX_SAVED_AGGREGATE'})
    return {'profiles':rows,'champion':best,'peak_ul':peak,'summary_conflicts':conflicts,
            'selection_policy':'PRODUCER_LOSS_LE10_THEN_REPORTED_AGGREGATE_NOT_ACCEPTANCE',
            'topology':'REPORTED_PBE5AC_192.168.100.241_TO_242_NOT_REACQUIRED',
            'sta_vht80_capability_proof':'UNSUPPORTED_UNCONDITIONAL_PRODUCER_TRUE_LITERAL',
            'vht40_association_proof':'PING_MARKER_ONLY_NO_SAVED_IW_OR_WPA_TRANSCRIPT',
            'measurement_basis':'Sequential DL/UL interface RX byte deltas over truncated uptime, not simultaneous application throughput',
            'loss_bound_assumption':'Conditional on n transmitted IID Bernoulli trials with zero loss; saved count is replies, raw transmitted count absent.'}


def audit_pktlog_round(round_obj):
    windows=round_obj['windows']
    if not isinstance(windows,list) or not all(isinstance(w,dict) for w in windows) or [w.get('window') for w in windows]!=['A1','B1','A2','B2']:raise ValueError('ABAB_order')
    rows=[];conflicts=[]
    for i,w in enumerate(windows):
        arm=w['window'][0]
        if w.get('arm')!=arm:raise ValueError('arm_conflict')
        app=sum(h.number(w[k],k) for k in ('tcp_dl_mbps','tcp_ul_mbps','iptv_mbps','voip_mbps'))
        ota=h.number(w['ota_wire_air_mbps'],'ota');goodput=h.number(w['goodput_mbps'],'goodput')
        metrics={'goodput_mbps':goodput,'app_mbps':app,'ota_mbps':ota,
                 'voip_jitter_ms':h.number(w['voip_jitter_ms'],'voip_jitter'),
                 **{k:h.number(w['under_load_rtt'][k],k) for k in ('p50_ms','p95_ms','p99_ms')}}
        if not metrics['p50_ms']<=metrics['p95_ms']<=metrics['p99_ms']:raise ValueError('rtt_quantile_order')
        if abs(goodput-max(app,ota))>.003:conflicts.append({'pointer':f'/rounds/2/windows/{i}/goodput_mbps','reason':'PRODUCER_MAX_LAYER_MISMATCH'})
        expected='0x40' if arm=='A' else '0x0'
        configured=w['knob_readback'].get('pktlog_filter')
        if configured!=expected:conflicts.append({'pointer':f'/rounds/2/windows/{i}/knob_readback/pktlog_filter','reason':'CONFIGURED_ARM_MISMATCH'})
        rows.append({'window':w['window'],'arm':arm,'metrics':metrics,'configured_pktlog_filter':configured,
                     'getter_status':'NOT_RETAINED_CONFIGURED_VALUES_ONLY','goodput_layer':'app' if app>=ota else 'ota'})
    keys=list(rows[0]['metrics'])
    means={a:{k:statistics.mean(r['metrics'][k] for r in rows if r['arm']==a) for k in keys} for a in ('A','B')}
    deltas={k:h.delta(means['A'][k],means['B'][k]) for k in keys}
    for a in ('A','B'):
        for k,field in [('goodput_mbps','goodput_mbps'),('p50_ms','p50_rtt_ms'),('p95_ms','p95_rtt_ms'),('p99_ms','p99_rtt_ms'),('voip_jitter_ms','voip_jitter_ms')]:
            key=f'arm_{a.lower()}_mean_{field}'
            if key in round_obj and abs(h.number(round_obj[key],key)-means[a][k])>.0011:
                conflicts.append({'pointer':'/rounds/2/'+key,'reason':'SAVED_MEAN_MISMATCH'})
    if abs(h.number(round_obj['goodput_delta_pct'],'delta',-100,100000)-deltas['goodput_mbps'])>.02:
        conflicts.append({'pointer':'/rounds/2/goodput_delta_pct','reason':'SAVED_DELTA_MISMATCH'})
    return {'round_id':round_obj['round_id'],'rows':rows,'means':means,'deltas':deltas,'summary_conflicts':conflicts,
            'pair_goodput_changes_pct':[h.delta(rows[i]['metrics']['goodput_mbps'],rows[i+1]['metrics']['goodput_mbps']) for i in (0,2)],
            'layer_metrics':{'definition':'max(application TCP+IPTV+VoIP sum, OTA interface byte rate)',
                             'is_pure_application_goodput':False,'application_and_ota_recomputed_separately':True},
            'topology':'REPORTED_WA_192.168.100.20_TO_250_NOT_PBE_PAIR',
            'attribution':'ath10k/host and QCA firmware hypothesis; no CE DMA causal isolation',
            'tail_qualification':'Mean per-window quantiles, not pooled RTT quantiles; p95/p99 equal in all saved windows.'}


def reconcile(obj487,obj403):
    selected=[r for r in obj403['rounds'] if r['round_id']=='S403A-R45']
    if len(selected)!=1:raise ValueError('unique_R45_required')
    return {'pbe5ac':audit_profiles(obj487),'pktlog':audit_pktlog_round(selected[0]),
            'cross_topology_effect_combination_allowed':False,
            'boundary':{'target_access':False,'physical_acceptance':False},
            'promotion_contract':{'R45_window_tcp_streams':[w['knob_readback']['tcp_streams'] for w in selected[0]['windows']],
                                  'promoted_tcp_streams':obj403.get('promoted_r45_knobs',{}).get('tcp_streams'),
                                  'post_promotion_application_proof':'NOT_RETAINED_WINNER_DICT_IS_NOT_APPLY_PROOF'},
            'summary':{'pbe_profiles':len(obj487['profiles']),'pktlog_windows':4,'new_hardware_results':0},
            'gaps':['No native SSH exit/transcript, packet capture, route/interface proof or binary/build-bound acquisition chain is retained for487.',
                    'VHT80 flag is unconditional; ping alone does not prove width negotiation or the WPA handshake.',
                    '487 DL+UL are sequential interface-rate sums and its20MHz reference is hardcoded in the producer.',
                    'AirOS22.80/3.60 reference occurs in prose only, not the487 JSON; width/topology/workload differ.',
                    '403 getter text is dropped by the measurement serializer; configured values are not observed getter success.',
                    'R45 has two windows per arm with large A1/A2 variation and a p50 regression; no causal transfer to PBE is established.'],
            'status':'QUALIFIED_SAVED_ARITHMETIC_WITH_PROVENANCE_GAPS'}


def build(root=ROOT):
    a,pa=h.json_source(root,S487);b,pb=h.json_source(root,S403);result=reconcile(a,b)
    sources=[pa,pb]+[h.snapshot(root,p)[1] for p in (P487,P403,P311,
        'docs/STAGE487A_LIVE_PBE5AC_STA_VHT80_CAP_AND_VHT40_UNLOCK.md',
        'docs/STAGE403A_LIVE_WA_PB040_RAM_CANARY_AND_NFCAL_R43_45.md')]
    result['producer_anchors']=[c.anchors(Path(root)/P487,['"sta_vht80_cap_unlock_verified": True','vht40_assoc =','vht20_ref =','DL_B='],root),
                                c.anchors(Path(root)/P311,['goodput_mbps = round(max(app_mbps, ota_mbps), 3)','"knob_readback": cfg'],root)]
    text='''<!-- doc-head: Stage525A saved PBE VHT40 and separate WA pktlog reconciliation -->
Saved arithmetic and producer semantics, never new radio acquisition or pooled gains.
<!-- /doc-head -->

# Stage525A

Parent: fixed525A..530A offline RE1/control-boundary queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage525a_pbe5ac_vht40_25mbps_and_pktlog_zero_reconciler.py`.
Input JSON, producer source and source docs are SHA256-bound and rechecked.
Producer scripts are read as text, never imported or executed.
Their current hashes do not establish the historically executed source revision.

## Separate result contracts

| Held source | Reproduced values | Qualification |
| --- | --- | --- |
|487 .241/.242 champion |16.74DL+8.09UL=24.83Mbps |Sequential interface rates, not concurrent TCP aggregate |
|487 different profile |10.81DL+9.96UL=20.77Mbps |PeakUL9.96 is not championUL8.09 |
|403 R45 .20/.250 |55.816 to71.252Mbps,+27.65515% |max(app sum,OTA), not one pure goodput layer |
|403 R45 p50 |17.633 to19.0515ms |Regression survives the goodput improvement |

487's nss=1 is the producer AP override index, intended2SS; STA command uses nss=0.
No native NSS readback is retained. PHY rates are reported values, not measured
per-frame MCS/NSS distributions. The VHT80 verification flag is an unconditional
True literal. VHT40_ASSOC comes from a ping marker, not an iw width getter or WPA
handshake transcript. The20MHz reference row is hardcoded historical input.
The source's22.80Mbps/3.60Mbps airOS comparison appears only in prose, without a
native matched baseline. No8.9% cross-width acceptance follows from these records.

Champion1472-byte ping reports8 replies and0.0% loss. This is not a persistent
zero-loss guarantee or path/OTA proof. Under the explicit additional assumption of
eight independent transmitted trials with zero failures, the one-sided95% loss
upper bound is about31.23%; the transmitted count and IID assumptions are unproven.
With8 samples the producer's p95 calculation selects the maximum. Raw replies,
management-vs-OTA routing, clock/byte counters and native command exits are absent.

R45 preserves orderedA1,B1,A2,B2 summary windows. Their metric is the maximum of
an application TCP+IPTV+VoIP sum and an OTA byte rate. Both component layers are
recomputed separately. Its generic knob_readback field serializes configured
values only; the actual AP/CPE extra getter strings are dropped by the helper.
A1=36.393 versusA2=75.239Mbps and opposite paired effect directions limit causal
confidence. Per-window RTT quantile means are not pooled quantiles; p95=p99 in all
four windows. Neither the claimed16-stream count nor a CE DMA relief mechanism
is independently established by these summaries. No gains are added/multiplied
onto24.83Mbps. R45 windows use tcp_streams4, but the promoted dictionary records2;
choosing a winner dict is not proof it was applied or persisted after the trial.
Decision: KEEP qualified saved reconciliation; E2 NOT_ACCEPTED.
No target, SSH, configuration, firmware/module execution, flash or load action.
'''
    return h.finish(root,525,SCRIPT,OUT,DOC,text,result,sources)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args(argv);print(json.dumps(build(args.root)['summary']));return 0


if __name__=='__main__':raise SystemExit(main())
