#!/usr/bin/env python3
"""Panel1 snapshot reconciliation and explicitly conditional outage-rate bounds."""
import ast
import math
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
c=h.c
SCRIPT='tools/sim/run_stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.py'
OUT='artifacts/autoresearch/stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.json'
DOC='docs/STAGE790A_PANEL1_GUARIDA_84_20H_ZERO_DROP_RELIABILITY_MODEL.md'
SNAP='artifacts/autoresearch/stage678a_live_panel1_guarida_84_v12_audit.json'
COUNTERS='artifacts/autoresearch/stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.json'
SP='tools/bench/run_stage678a_live_panel1_guarida_84_v12_audit.py'
CP='tools/observability/audit_stage683a_panel1_guarida_84_per_tid_aql_and_atf_20h.py'
SOURCES=(SNAP,COUNTERS,SP,CP)
DOC_TEXT='''<!-- doc-head: Stage790A Panel1 saved-time and packet reconciliation with conditional Poisson reliability -->
WDS connected snapshots, cumulative queue drops and hypothetical zero-event bounds stay separate.
<!-- /doc-head -->

# Stage790A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/sim/run_stage790a_panel1_guarida_84_20h_zero_drop_reliability_model.py`.
Reads immutable local files only; no network, producer, shell, radio or load execution.

## Actual scope of saved observations

678 /before_telemetry/stations and /after_telemetry/stations contain three matching
MACs and connected times72265->72267,72261->72264,72146->72149 seconds.
The saved execution elapsed3.869s. Its producer defines zero_drop by equal MAC
sets and at least3 stations. This is snapshot membership, not20h outage surveillance.
The raw station dump connected times72267/72263/72148s span20.0411..20.0742h;
20.07 is a rounded longest-link value, not the exact minimum of all three links.
Association timers and low-time-resolution snapshots do not exclude brief WDS
dataplane interruptions or all intermediate reconnects. No boot/event-log epoch,
packet continuity capture or detection probability is available. Join by MAC;
saved prose/alias assignments conflict, so they are not authoritative identity joins.

The raw678 dump totals40,482,795 TX packets,500,366 retries,2,473 TX failed,
32,586 RX drop misc. Those are cumulative counters with unproven common reset
epochs and distinct semantics, not measured loss probabilities or WDS disconnects.
Consequently zero packet drops is not supported by these saved fields.

683 /stations_per_tid has3*8 queue rows with39,405,365 TX packets (39.405365M),
1,412 TID0 CoDel drops,30 marks, zero other TID drops/overlimit/backlog. Its
producer contains the full24-row dictionary as literals, sums it, and declares
20.12h literally. We compare the literal data with the JSON without executing it.
Pillar prose instead says39,343,195, an internal headline discrepancy. These rows
are a saved literal-data ledger, not a fresh sysfs trace. Do not pool their count
with678 TX packets or pair20.07h with39.41M as a single validated exposure.
Intentional CoDel queue drops and WDS link failures are different outcomes.

## Prespecified conditional reliability sensitivity

Illustration only: suppose0 detected WDS events over T=20.07 AP-hours and
a homogeneous Poisson event rate lambda, with independent known detection q.
P(Nobserved=0)=exp(-lambda*T*q). One-sided95% upper lambda=-ln(.05)/(T*q).
Lower survival over h hours is exp(-lambda_upper*h); lower MTBF=1/lambda_upper.
Evaluate q={.1,.5,1} and h={1,24,168}. q=0 gives no finite identifiable upper rate.
These are conditional frequentist model bounds, not probability that the true
rate lies in an interval or proof of future reliability. Detection sensitivity,
homogeneity, event independence and complete surveillance are unverified here.
Actual q is UNKNOWN; no empirical outage bound or MTBF acceptance is produced.
Packet counts supply no independent WDS-trial denominator. Correlated CPEs share
an AP and channel; summing three connection ages does not triple AP exposure.
Nonzero failure-count intervals are outside this zero-event model's contract.
KEEP the conditional tool; sustained zero-outage physical acceptance remains UNKNOWN.
'''


def zero_event_bound(hours,confidence=.95,detection_probability=1,future_hours=24):
    t=c.finite(hours,'hours',1e-9,1e6);q=c.finite(detection_probability,'detection',0,1)
    conf=c.finite(confidence,'confidence',1e-12,1-1e-12);future=c.finite(future_hours,'future_hours',0,1e6)
    rate=-math.log1p(-conf)/(t*q) if q else None
    return dict(assumed_observed_events=0,assumed_ap_hours=t,confidence=conf,assumed_detection_probability=q,
        future_hours=future,outage_rate_upper_per_hour=rate,mtbf_lower_hours=1/rate if rate else None,
        survival_lower=math.exp(-rate*future) if rate else (1.0 if not future else 0.0),
        identifiable_under_assumptions=bool(q),empirical_eligibility=False)


def station_dump(text):
    if not isinstance(text,str) or len(text)>500000:raise ValueError('bounded_station_text')
    matches=list(re.finditer(r'(?m)^Station ([0-9a-fA-F:]{17}) \(on ([^)]+)\)',text))
    if not 1<=len(matches)<=100:raise ValueError('station_blocks_required')
    rows=[];seen=set();fields=('tx packets','tx retries','tx failed','rx drop misc','connected time')
    for i,match in enumerate(matches):
        mac=match[1].lower()
        if mac in seen:raise ValueError('duplicate_station_mac')
        seen.add(mac);block=text[match.end():matches[i+1].start() if i+1<len(matches) else len(text)]
        row=dict(mac=mac,iface=match[2])
        for field in fields:
            vals=re.findall(r'(?m)^\s*'+re.escape(field)+r':\s*(\d+)(?: seconds)?\s*$',block)
            if len(vals)!=1:raise ValueError('required_station_counter:'+field)
            row[field.replace(' ','_')]=c.integer(int(vals[0]),field,0,10**15)
        rows.append(row)
    return dict(stations=rows,totals={field.replace(' ','_'):sum(r[field.replace(' ','_')]for r in rows)
        for field in fields if field!='connected time'},min_connected_hours=min(r['connected_time']for r in rows)/3600,
        max_connected_hours=max(r['connected_time']for r in rows)/3600,common_epoch_verified=False)


def tid_counts(stations):
    if not isinstance(stations,dict) or not 1<=len(stations)<=100:raise ValueError('bounded_station_map')
    packets=drops0=drops_other=marks=overlimit=backlog=0;macs=set();rows=0
    for station in stations.values():
        mac=station['mac'].lower()
        if mac in macs:raise ValueError('duplicate_station_mac')
        macs.add(mac);tids=station['tids']
        if sorted(t['tid']for t in tids)!=list(range(8)):raise ValueError('unique_eight_tids_required')
        for t in tids:
            c.integer(t['tid'],'tid',0,7)
            vals={k:c.integer(t[k],k,0,10**15)for k in ('tx_packets','drops','marks','overlimit','backlog_b')}
            packets+=vals['tx_packets'];marks+=vals['marks'];overlimit+=vals['overlimit'];backlog+=vals['backlog_b'];rows+=1
            if t['tid']==0:drops0+=vals['drops']
            else:drops_other+=vals['drops']
    return dict(stations=len(macs),rows=rows,tx_packets=packets,tid0_codel_drops=drops0,
        non_tid0_codel_drops=drops_other,marks=marks,overlimit=overlimit,backlog_bytes=backlog,
        packet_trial_denominator_for_WDS=None,common_epoch_verified=False)


def literal_stations(text):
    tree=ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='stations_per_tid'for t in node.targets):
            value=ast.literal_eval(node.value)
            if isinstance(value,dict):return value
    raise ValueError('literal_station_dictionary_required')


def snapshot_membership(r):
    before=r['before_telemetry']['stations'];after=r['after_telemetry']['stations']
    if not isinstance(before,dict) or not isinstance(after,dict):raise ValueError('station_maps_required')
    rows=[]
    for mac in sorted(set(before)&set(after)):
        a=c.integer(before[mac]['connected_time_s'],'before_connected',0,10**9)
        b=c.integer(after[mac]['connected_time_s'],'after_connected',0,10**9)
        rows.append(dict(mac=mac,before_s=a,after_s=b,delta_s=b-a,nondecreasing=b>=a))
    return dict(same_mac_set=set(before)==set(after),station_count=len(after),rows=rows,
        saved_execution_elapsed_s=c.finite(r['elapsed_seconds'],'elapsed',0,300),
        continuous_zero_WDS_events_proven=False)


def build(root=ROOT):
    payloads,sources=h.freeze(root,790,SOURCES);snap=h.json_source(payloads[SNAP]);counter=h.json_source(payloads[COUNTERS])
    raw=station_dump(snap['live_3cpe_20h_uptime_and_station_audit']['raw_3cpe_station_dump'])
    stats=tid_counts(counter['stations_per_tid']);literal=literal_stations(payloads[CP].decode('utf-8'))
    model=[zero_event_bound(20.07,detection_probability=q,future_hours=f)for q in (.1,.5,1)for f in (1,24,168)]
    return h.finish(root,790,SCRIPT,OUT,DOC,DOC_TEXT,dict(status='QUALIFIED_OFFLINE_CONDITIONAL_RELIABILITY',
        claim_classification='INFERRED_MODEL_UNKNOWN_EMPIRICAL_OUTAGE_RATE',attribution='external offline analyst / Linux counters',
        saved_membership=snapshot_membership(snap),raw678=raw,tid683=stats,
        literal_source_matches_saved_rows=literal==counter['stations_per_tid'],
        saved_counter_summary=counter['sector_summary_20h'],
        actual_event_surveillance='MISSING',actual_detection_probability=None,empirical_outage_rate_bound=None,
        requested_packet_count_rounded_million=39.41,requested_hours=20.07,
        cohorts_joined=False,conditional_sensitivity=model,
        gaps=['Snapshot association ages are not complete outage surveillance.',
              '683 literal data/prose and678 counters are not a common epoch/cohort.',
              'No packet-count denominator for independent WDS trials; packet drops are nonzero.']),sources)


if __name__=='__main__':raise SystemExit(h.cli(build))
