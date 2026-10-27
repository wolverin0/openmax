#!/usr/bin/env python3
"""AirSelect-inspired coordination model, not an implementation of vendor TDD."""
from __future__ import annotations
import argparse
from collections import deque
from dataclasses import asdict,dataclass
from importlib.metadata import version
import math
from pathlib import Path
import random
import statistics
import sys
import numpy as np
import simpy
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.re import ground_up_release_common as c

OUT='artifacts/autoresearch/stage355a_airselect_hopping_evasion_pareto.json'
DOC='docs/STAGE355A_AIRSELECT_HOPPING_EVASION_PARETO.md'
FAMILIES={'WA':(8,60.),'XC':(12,60.),'XW':(18,24.)}
SEEDS=(355,1355,2355)
CHANNELS=('C0','C1','C2')  # Abstract model states, not authorized RF frequencies.
CONTROL_LATENCY_MS=5
SCAN_WAIT_MS=60


@dataclass(frozen=True)
class Policy:
    kind:str='coordinated'
    dwell_ms:int=100
    guard_ms:int=2
    lead_ms:int=25
    def __post_init__(self):
        if self.kind not in ('static','reactive','coordinated'):raise ValueError('policy_kind')
        c.integer(self.dwell_ms,'dwell_ms',40,400)
        c.integer(self.guard_ms,'guard_ms',0,20)
        c.integer(self.lead_ms,'lead_ms',1,40)
        if self.lead_ms+self.guard_ms>=self.dwell_ms:raise ValueError('coordination_exceeds_dwell')
    @property
    def policy_id(self):return f'{self.kind}_d{self.dwell_ms}_g{self.guard_ms}_l{self.lead_ms}'


def policies():
    return [Policy('static'),Policy('reactive')]+[Policy('coordinated',d,g,l) for d in (100,200) for g in (2,5) for l in (20,40)]


def interference_trace(scenario,seed,horizon):
    if scenario not in ('quiet','rotating_interference'):raise ValueError('scenario')
    rng=random.Random(seed^0xC17);rows=[]
    for tick in range(horizon):
        if scenario=='quiet':row=(.05,.05,.05)
        else:
            noisy=(tick//140)%3
            row=tuple(min(.98,max(.02,(.85 if ch==noisy else .12)+rng.uniform(-.03,.03))) for ch in range(3))
        rows.append(row)
    return rows


def percentile(values,q=.95):
    if not values:return None
    a=sorted(values);index=(len(a)-1)*q;lo=int(index)
    return a[lo]+(a[min(lo+1,len(a)-1)]-a[lo])*(index-lo)


def handoff_schedule(kind,now,lead_ms,control_latency_ms,retune_ms):
    if kind not in ('reactive','coordinated'):raise ValueError('handoff_kind')
    c.finite(now,'now',0,10000)
    for key,val in [('lead',lead_ms),('control_latency',control_latency_ms),('retune',retune_ms)]:c.integer(val,key,0,100)
    switch_at=now+(lead_ms if kind=='coordinated' else 0)
    start=max(switch_at,now+control_latency_ms)
    return {'ap_switch_at_ms':switch_at,'peer_retune_start_ms':start,'peer_ready_ms':start+retune_ms}


def simulate(policy,family,scenario,seed,*,horizon_ms=800,announcement_loss=.1,
             clock_skew_ms=0,observation_delay_ms=12,eligible_channels=CHANNELS):
    if not isinstance(policy,Policy):raise ValueError('typed_policy')
    if family not in FAMILIES and family!='MIXED':raise ValueError('family')
    c.integer(seed,'seed',0,2**31-1);c.integer(horizon_ms,'horizon_ms',100,4000)
    c.integer(clock_skew_ms,'clock_skew_ms',0,3);c.integer(observation_delay_ms,'observation_delay_ms',0,100)
    c.finite(announcement_loss,'announcement_loss',0,1)
    if not isinstance(eligible_channels,tuple) or not eligible_channels or len(set(eligible_channels))!=len(eligible_channels) or any(x not in CHANNELS for x in eligible_channels):raise ValueError('eligible_abstract_channels')
    ids=[CHANNELS.index(x) for x in eligible_channels]
    families=list(FAMILIES) if family=='MIXED' else [family]*3
    env=simpy.Environment();noise=interference_trace(scenario,seed,horizon_ms)
    traffic=random.Random(seed^0x11A);control=random.Random(seed^0x22B)
    ap_channel=ids[0];peer_channels=[ids[0]]*3;peer_busy=[0.]*3;ap_busy=0.
    mismatched_since=[None]*3;queues=[[deque(),deque()] for _ in range(3)]
    qbits=[[0.,0.] for _ in range(3)];offered=dropped=delivered=attempted=0.
    delays=[];hops=announcements=misses=0;blackouts=[0,0,0];tdm_mismatch=[0,0,0]
    link_delivered=[0.,0.,0.];events=[];coordination_events=[];capacity=96000.;last_service_end=0.

    def peer_switch(peer,target,when):
        yield env.timeout(max(0.,when-env.now))
        peer_busy[peer]=max(peer_busy[peer],env.now+FAMILIES[families[peer]][0])
        peer_channels[peer]=target
        coordination_events.append({'kind':'announced_retune','peer':peer,'retune_start_ms':env.now,'ready_ms':peer_busy[peer]})

    def apply_ap_switch(target):
        nonlocal ap_channel,ap_busy,hops
        if last_service_end>env.now+1e-8:raise ValueError('hop_overlaps_already_charged_service')
        ap_channel=target;ap_busy=env.now+policy.guard_ms;hops+=1
        events.append({'time_ms':env.now,'abstract_channel':CHANNELS[target]})

    def delayed_ap_switch(target,switch_at):
        yield env.timeout(switch_at-env.now)
        apply_ap_switch(target)

    def hop(target):
        nonlocal announcements,misses
        switch_at=env.now+(policy.lead_ms if policy.kind=='coordinated' else 0)
        for peer in range(3):
            announcements+=1
            missed=control.random()<announcement_loss
            if missed:misses+=1;continue
            schedule=handoff_schedule(policy.kind,env.now,policy.lead_ms,CONTROL_LATENCY_MS,FAMILIES[families[peer]][0])
            env.process(peer_switch(peer,target,schedule['peer_retune_start_ms']))
        if switch_at==env.now:apply_ap_switch(target)
        else:env.process(delayed_ap_switch(target,switch_at))

    def tick_loop():
        nonlocal offered,dropped,delivered,attempted,last_service_end
        for tick in range(horizon_ms):
            if policy.kind!='static' and tick>0 and tick%policy.dwell_ms==0:
                observed=noise[max(0,tick-observation_delay_ms)]
                target=min(ids,key=lambda ch:(observed[ch],ch))
                # Hysteresis avoids gratuitous hops when all observations tie.
                if observed[ap_channel]-observed[target]>.1:hop(target)
            direction=0 if tick%10<7 else 1  # Synthetic70/30 TDD, not vendor slots.
            for peer in range(3):
                for d in (0,1):
                    arrival=(1800. if d==0 else 600.)*(.8+.4*traffic.random())
                    offered+=arrival;accepted=min(arrival,capacity-qbits[peer][d]);dropped+=arrival-accepted
                    if accepted>0:queues[peer][d].append([accepted,float(tick)]);qbits[peer][d]+=accepted
                if peer_channels[peer]!=ap_channel:
                    if mismatched_since[peer] is None:mismatched_since[peer]=tick
                    # Explicit synthetic scan/reacquisition; not an AirSelect protocol claim.
                    if tick-mismatched_since[peer]>=SCAN_WAIT_MS:
                        coordination_events.append({'kind':'scan_retune','peer':peer,'mismatch_start_ms':mismatched_since[peer],
                                                    'retune_start_ms':tick,'ready_ms':tick+FAMILIES[families[peer]][0]})
                        peer_channels[peer]=ap_channel;peer_busy[peer]=tick+FAMILIES[families[peer]][0];mismatched_since[peer]=None
                else:mismatched_since[peer]=None
                peer_direction=0 if (tick+clock_skew_ms)%10<7 else 1
                if peer_direction!=direction:tdm_mismatch[peer]+=1;continue
                if peer_channels[peer]!=ap_channel or tick<peer_busy[peer] or tick<ap_busy:
                    blackouts[peer]+=1;continue
                rate=FAMILIES[families[peer]][1]*1000/3  # Equal1/3 airtime, units bits/ms.
                budget=rate*(1-noise[tick][ap_channel]);attempted+=rate
                queue=queues[peer][direction]
                while budget>1e-8 and queue:
                    chunk=queue[0];bits=min(chunk[0],budget)
                    chunk[0]-=bits;qbits[peer][direction]-=bits;budget-=bits
                    delivered+=bits;link_delivered[peer]+=bits
                    if bits>0:last_service_end=tick+1
                    if chunk[0]<=1e-8:delays.append(tick+1-chunk[1]);queue.popleft()
            yield env.timeout(1)

    process=env.process(tick_loop());steps=0;cap=horizon_ms*12+100
    # Process the terminating event, including service through [horizon-1,horizon).
    while not process.processed:
        if steps>=cap or env.peek()>horizon_ms:raise ValueError('simulation_event_or_time_cap')
        env.step();steps+=1
    outstanding=sum(sum(pair) for pair in qbits)
    if not math.isclose(offered,delivered+dropped+outstanding,rel_tol=1e-9,abs_tol=1e-5):raise ValueError('bit_conservation')
    if delivered>attempted+1e-6 or any(x>horizon_ms for x in blackouts):raise ValueError('service_bounds')
    return {'policy_id':policy.policy_id,'family':family,'scenario':scenario,'seed':seed,'horizon_ms':horizon_ms,
            'offered_bits':offered,'delivered_expected_bits':delivered,'overflow_dropped_bits':dropped,
            'outstanding_bits':outstanding,'attempt_capacity_bits':attempted,
            'goodput_mbps':delivered/(horizon_ms*1000),'undelivered_fraction_at_horizon':(dropped+outstanding)/offered,
            'completed_chunk_p95_ms':percentile(delays),'completed_chunks':len(delays),
            'hops':hops,'announcements':announcements,'missed_announcements':misses,
            'blackout_link_ms':blackouts,'tdd_mismatch_link_ms':tdm_mismatch,'link_delivered_expected_bits':link_delivered,
            'hop_events':events,'coordination_events':coordination_events,'event_steps':steps,'event_cap':cap,'eligible_abstract_channels':list(eligible_channels),
            'service_hop_boundary_guard':True,
            'claim_status':'SYNTHETIC_FLUID_SERVICE_NOT_RF_MEASUREMENT'}


def analyze():
    groups=[]
    for family in (*FAMILIES,'MIXED'):
        for scenario in ('quiet','rotating_interference'):
            rows=[]
            for policy in policies():
                runs=[simulate(policy,family,scenario,seed) for seed in SEEDS]
                p95s=[r['completed_chunk_p95_ms'] for r in runs]
                objectives=[-statistics.mean(r['goodput_mbps'] for r in runs),
                            statistics.mean(x if x is not None else 800. for x in p95s),
                            statistics.mean(r['undelivered_fraction_at_horizon'] for r in runs)]
                rows.append({'policy':asdict(policy),'policy_id':policy.policy_id,'objectives':objectives,'runs':runs})
            ranks=NonDominatedSorting().do(np.array([r['objectives'] for r in rows]))
            for rank,indices in enumerate(ranks):
                for index in indices:rows[int(index)]['pareto_rank']=rank
            groups.append({'family':family,'scenario':scenario,'policies':rows,'pareto_ids':[r['policy_id'] for r in rows if r['pareto_rank']==0]})
    return groups


def build(root=ROOT):
    root=Path(root);groups=analyze()
    sources=[c.binding(root/'artifacts/autoresearch/stage353a_sub20mhz_pll_ofdm_timing_matrix.json',root)]
    manifest=c.load(root/'artifacts/verification/stage355a_sources/source_manifest.json')
    c.read(root/manifest['path'],manifest['sha256']);sources.append(manifest)
    sources.append(c.binding(root/'artifacts/verification/stage355a_sources/airselect_pages.json',root))
    result={'stage':'355A','task_id':'T-S355A-AIRSELECT-INSPIRED-HOPPING','static_sources':sources,
            'groups':groups,'summary':{'strata':8,'policies_per_stratum':10,'seeds':3,'replications':240,'hardware_results':0},
            'assumptions':{'model':'Bounded SimPy discrete-time fluid queues,1ms ticks,800ms horizon, no vendor wire protocol',
                           'family_switch_ms_and_rate_mbps':FAMILIES,'parameters_are_measured':False,
                           'announcement_loss':.1,'clock_skew_ms_default':0,'clock_skew_sensitivity_supported':True,
                           'clock_skew_parameter_is_fixed_phase_offset_not_ppm_drift':True,
                           'scanning_and_announcement_airtime':'Not modeled separately; all abstract channels have delayed synthetic observations',
                           'observation_delay_ms':12,'control_message_latency_ms':CONTROL_LATENCY_MS,'scan_wait_ms':SCAN_WAIT_MS,
                           'reacquisition_ms':'60ms scan wait + one family retune duration',
                           'tdd':'70/30 synthetic10ms frame, equal modeled peer airtime, not airMAX TDD'},
            'limitations':['airOS6 M-series guide is not proof of WA/XC airOS8 feature support.',
                           'No decoded vendor AirSelect announcement/CSA/TDD state machine or firmware API is implemented.',
                           'Abstract C0/C1/C2 are not legal channel approvals; DFS/CAC/nonoccupancy/region/EIRP require separate qualification.',
                           'Fluid expected-bit service is not packet PER, TCP throughput, or a calibrated propagation model.',
                           'Completed-chunk p95 is censored by unfinished chunks; horizon-undelivered objective is not packet loss.',
                           'Means of per-run p95 are not pooled percentiles; no cross-family global champion.'],
            'dependencies':{key:version(key) for key in ('simpy','pymoo','numpy')},
            'boundary':{'hardware_access':False,'native_channel_or_TDD_executor':False,'physical_acceptance':False,'regulatory_override':False}}
    text='''<!-- doc-head: Stage355A qualified AirSelect-inspired frequency coordination model -->
Bounded synthetic SimPy queues and finite pymoo fronts are not vendor firmware or RF results.
<!-- /doc-head -->

# Stage355A

Parent: offline RE1/control-boundary hypotheses after353/354.
Run `python tools/sim/build_stage355a_airselect_hopping_evasion_pareto.py`.
The dedicated JSON retains240 runs:10 policies,3 seeds,4 family strata and2 scenarios.
WA,XC,XW and a mixed three-peer stratum are modeled separately, never ranked globally.

The [vendor airOS6 M-series guide](https://dl.ui.com/guides/airOS/airOS_6_UG.pdf)
describes a frequency list, hop interval and advance announcements, with timing-drift
concerns. Pages11/21 and full PDF hash are cached. This source does not qualify
AirSelect on WA/XC airOS8, nor does it expose a vendor announcement wire format.
This is an AirSelect-inspired coordination experiment, not reverse-engineered TDD.

## Fixed conceptual model

One terminating SimPy process advances800 one-millisecond ticks. Six bounded fluid
queues represent DL/UL for three peers. Arrivals, stale interference observations,
handoff messages and service are modeled without any network or target executor.
Three abstract channels C0/C1/C2 carry quiet or rotating synthetic interference.
Family rate/switch-time presets are explicit UNMEASURED assumptions.
Every direction shares a synthetic70/30 TDD frame. Clock-skew sensitivity can
misalign peer/AP directions. AP and peers cannot serve during switch guards or
channel mismatch. Missed announcements incur scan/reacquisition blackout.
Static, reactive and coordinated alternatives share fixed seeded inputs.
The clock_skew_ms parameter is a fixed phase offset, not oscillator ppm drift.
Hop lead, switch guards, peer retunes and lost notices affect service; quiet
scenarios may favor staying put. Observations are delayed, not a future oracle.
Control delivery takes5ms; peers start tuning at max(AP-hop time, message receipt),
then pay ONE family retune duration. A missed notice incurs60ms scan wait followed
by ONE retune. Reactive AP changes occur before that tick's fluid service; future
coordinated changes are scheduled at their announced boundary. An overlap guard
rejects a hop inside an interval whose service was already charged.
Scanning and announcement airtime are not charged separately; this remains an
explicit model limitation, not a measurement or vendor protocol characteristic.

Offered bits=delivered expected bits+overflow drops+outstanding backlog.
Finite horizon/event/queue limits and no service while mismatched are enforced.
This is expected fluid service, not exact packets, PHY PER or TCP/BA recovery.
Completed-chunk p95 excludes unfinished chunks; undelivered-at-horizon includes
backlog and is not packet loss. Both limitations remain next to the objectives.

pymoo ranks all finite policies separately in each family/scenario. It minimizes
negative mean goodput, mean per-run completed-chunk p95, and horizon-undelivered
fraction. No completion maps to the800ms horizon penalty. A mean of percentiles
is not a pooled percentile, and three seeds do not validate physical performance.
No AirSync compatibility, sub20 enablement, legal RF frequency, DFS/CAC bypass,
PLL setting or firmware support is inferred. Regulatory eligibility and actual
control/announcement APIs remain UNKNOWN. Decision: KEEP offline model only.
'''
    c.write_doc(root/DOC,text);result['outputs']={DOC:c.binding(root/DOC,root)}
    result['implementation']=c.binding(root/'tools/sim/build_stage355a_airselect_hopping_evasion_pareto.py',root)
    c.write_json(root/OUT,result);return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args(argv);print(build(args.root)['summary']);return 0


if __name__=='__main__':raise SystemExit(main())
