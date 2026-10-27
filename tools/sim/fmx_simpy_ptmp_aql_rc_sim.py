"""Bounded offline SimPy PtMP airtime/queue sensitivity model.

Calibration is phenomenological and single-link. Vendor efficiency, RTS collision
reduction and TXOP behavior are explicit scenario assumptions, not measured gains.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random

import numpy as np
from scipy.stats import t as student_t

from orchestration.autoresearch.fmx_offline_data import (
    ROOT, finite_number, load_measurements, policy_features, software_versions, write_json,
)


@dataclass(frozen=True)
class Scenario:
    vendors: tuple[str, ...] = ("WA",)
    calibration_round: str = "R2"
    aql_low_us: int = 2000
    aql_high_us: int = 4000
    aql_threshold_us: int = 8000
    rc_per: int = 28
    dynamic_bw_rts: bool = False
    txop_us: int = 0
    offered_mbps: float = 120.0
    horizon_s: float = 0.5
    warmup_s: float = 0.1
    packet_bytes: int = 1500
    collision_probability: float = 0.0
    rts_collision_multiplier: float = 0.5
    legacy_efficiency: float = 0.5
    max_packets: int = 20000
    max_events: int = 300000
    seed: int = 20261024

    def validate(self):
        if not 1 <= len(self.vendors) <= 16 or any(v not in {"WA","XC","SXT","LBM5"} for v in self.vendors):
            raise ValueError("1..16 CPEs of the declared vendor scenario classes required")
        if self.calibration_round not in {'R1','R2'}:
            raise ValueError('Unknown calibration round')
        for field in ("aql_low_us","aql_high_us","aql_threshold_us","rc_per","txop_us","packet_bytes","max_packets","max_events","seed"):
            if type(getattr(self,field)) is not int:
                raise ValueError(f"{field} must be an exact integer")
        if not (1000 <= self.aql_low_us <= self.aql_high_us <= 12000
                and 4000 <= self.aql_threshold_us <= 24000 and 0 <= self.rc_per <= 256
                and 0 <= self.txop_us <= 4000 and 64 <= self.packet_bytes <= 1500
                and 1 <= self.max_packets <= 100000 and 1 <= self.max_events <= 2000000):
            raise ValueError("Outside the bounded model domain; these are not device safety limits")
        if type(self.dynamic_bw_rts) is not bool:
            raise ValueError("RTS assumption must be boolean")
        finite_number(self.horizon_s,'horizon',0.01,10)
        finite_number(self.warmup_s,'warmup',0,self.horizon_s-0.001)
        finite_number(self.offered_mbps,'load',0,1000)
        finite_number(self.collision_probability,'collision',0,0.8)
        finite_number(self.rts_collision_multiplier,'RTS collision multiplier',0,1)
        finite_number(self.legacy_efficiency,'legacy efficiency',0.1,1)
        return self


def calibrate(records):
    # Keep rounds separate. R1 can diagnose drift; predictions use stated R2 context.
    r2 = [row for row in records if row.round_id == 'R2']
    r1 = [row for row in records if row.round_id == 'R1']
    if len(r2) < 3 or len(r1)<3:
        raise ValueError("At least three windows in EACH of R1 and R2 are required")
    return dict(method='round_stratified_local_kernel_calibration',reference_round='R2',
                training=[dict(iteration=row.iteration,round_id=row.round_id,knobs=list(row.knobs),
                               goodput_mbps=row.goodput_mbps,p50_ms=row.p50_ms,
                               p95_ms=row.p95_ms,p99_ms=row.p99_ms) for row in records],
                R1_goodput_range=[min(r.goodput_mbps for r in records if r.round_id=='R1'),max(r.goodput_mbps for r in records if r.round_id=='R1')],
                scope='Single observed link. Queue/service decomposition, vendor effects and PtMP transfer are not identifiable.',
                physical_validation=False)


def response_for_policy(calibration, scenario):
    query=policy_features((scenario.aql_low_us,scenario.aql_high_us,scenario.aql_threshold_us,
                           scenario.rc_per,0,300,3,64))
    rows=[row for row in calibration['training'] if row['round_id']==scenario.calibration_round]
    if not rows:
        raise ValueError('No calibration data for requested round')
    distances=np.array([np.linalg.norm(policy_features(row['knobs'])-query) for row in rows])
    # Interpolate local measured response; do not fit a spurious causal RC slope.
    weights=np.exp(-(distances-distances.min())**2/(2*0.35**2))
    weights/=weights.sum()
    response={key:float(weights@np.array([row[key] for row in rows])) for key in ('goodput_mbps','p50_ms','p95_ms','p99_ms')}
    response['distance_to_calibration']=float(distances.min())
    return response


def replication_interval(values, confidence=0.95):
    array=np.asarray(values,dtype=float)
    if array.ndim!=1 or len(array)<2 or not np.isfinite(array).all():
        raise ValueError("Two or more independent finite replication statistics required")
    finite_number(confidence,'confidence',0.01,0.999)
    mean=float(array.mean())
    half=float(student_t.ppf((1+confidence)/2,len(array)-1)*array.std(ddof=1)/np.sqrt(len(array)))
    return dict(mean=mean,lower=mean-half,upper=mean+half,replications=len(array),
                scope='Monte Carlo uncertainty conditional on this model; not physical prediction coverage')


def simulate(scenario, calibration):
    scenario.validate()
    try:
        import simpy
    except ImportError as error:
        raise RuntimeError('SimPy required; supply an offline installed environment/wheel. No substitute engine or network fallback.') from error
    env=simpy.Environment()
    n=len(scenario.vendors)
    queues=[deque() for _ in range(n)]
    pending=[0.0]*n
    service_rng=random.Random(scenario.seed+1)
    arrival_rng=random.Random(scenario.seed+2)
    calibrated=response_for_policy(calibration,scenario)
    capacity=calibrated['goodput_mbps']
    if not capacity>0:
        raise ValueError('Calibration has no positive service capacity')
    # Separate an unexplained latency component from modeled airtime. This is an
    # explicit phenomenological delay, not a decoded firmware queue or RF distance.
    fixed_delay_s=max(0,calibrated['p50_ms']/1000 - scenario.aql_high_us/1e6)
    counts=dict(arrivals=0,rejected=0,delivered=0,collision_lost=0)
    window=dict(arrivals=0,rejected=0,delivered=0,collision_lost=0)
    per_cpe=[0]*n
    rtts=[]
    changed=env.event()
    busy=False
    max_pending=0.0

    def notify():
        nonlocal changed
        if not changed.triggered:
            changed.succeed()
        changed=env.event()

    def airtime(peer):
        efficiency=1.0 if scenario.vendors[peer] in {'WA','XC'} else scenario.legacy_efficiency
        return scenario.packet_bytes*8/(capacity*1e6*efficiency)

    def arrivals():
        nonlocal max_pending
        if scenario.offered_mbps==0:
            return
        interval=scenario.packet_bytes*8/(scenario.offered_mbps*1e6)
        for serial in range(scenario.max_packets):
            # Independent stream, bounded positive delays, no timeout(0) loop.
            delay=interval*arrival_rng.uniform(0.9,1.1)
            if env.now+delay>=scenario.horizon_s:
                return
            yield env.timeout(delay)
            peer=serial%n
            duration=airtime(peer)
            counts['arrivals']+=1
            in_window=env.now>=scenario.warmup_s
            if in_window:window['arrivals']+=1
            limit=scenario.aql_low_us if sum(pending)*1e6>=scenario.aql_threshold_us else scenario.aql_high_us
            # Include the in-flight packet in pending airtime. Admission loss is
            # explicitly modeled; there is no unbounded external TCP reservoir.
            if pending[peer]+duration>limit/1e6:
                counts['rejected']+=1
                if in_window:window['rejected']+=1
                continue
            queues[peer].append((env.now,duration,in_window))
            pending[peer]+=duration
            max_pending=max(max_pending,sum(pending))
            notify()
        if env.now<scenario.horizon_s-interval:
            raise RuntimeError('Packet cap reached before horizon; report aborted, not completed')

    def server():
        nonlocal busy,max_pending
        peer=0
        while True:
            if not any(queues):
                yield changed
                continue
            if not queues[peer]:
                peer=(peer+1)%n
                continue  # At most16 such rotations before positive service work.
            txop_budget=scenario.txop_us/1e6
            used=0.0
            while queues[peer]:
                arrival,duration,in_window=queues[peer].popleft()
                busy=True
                max_pending=max(max_pending,sum(pending))
                collision=scenario.collision_probability*(scenario.rts_collision_multiplier if scenario.dynamic_bw_rts else 1)
                yield env.timeout(duration)
                lost=service_rng.random()<collision
                pending[peer]=max(0,pending[peer]-duration)
                counts['collision_lost' if lost else 'delivered']+=1
                if env.now>=scenario.warmup_s:
                    window['collision_lost' if lost else 'delivered']+=1
                    if not lost:per_cpe[peer]+=1
                if in_window and not lost:
                    # RTT approximation: modeled queue/service + unexplained delay.
                    rtts.append((env.now-arrival+fixed_delay_s)*1000)
                busy=False
                used+=duration
                if txop_budget==0 or used>=txop_budget:
                    break
            peer=(peer+1)%n

    env.process(arrivals())
    env.process(server())
    events=0
    while env.peek()<scenario.horizon_s:
        if events>=scenario.max_events:
            raise RuntimeError('Event cap reached before horizon; report aborted, not completed')
        env.step()
        events+=1
    remaining=sum(map(len,queues))+int(busy)
    if counts['arrivals']!=counts['rejected']+counts['delivered']+counts['collision_lost']+remaining:
        raise AssertionError('Packet conservation failed')
    duration=scenario.horizon_s-scenario.warmup_s
    rates=np.array(per_cpe)*scenario.packet_bytes*8/(duration*1e6)
    fairness=float(rates.sum()**2/(n*np.sum(rates*rates))) if np.any(rates) else None
    quantiles=np.percentile(rtts,[50,95,99]).tolist() if rtts else [None]*3
    return dict(scenario=asdict(scenario),seed_streams={'arrivals':scenario.seed+2,'collisions':scenario.seed+1},
                counts=counts,window_counts=window,unfinished_at_horizon=remaining,events=events,
                goodput_mbps=float(rates.sum()),per_cpe_mbps=rates.tolist(),jain_fairness=fairness,
                p50_ms=quantiles[0],p95_ms=quantiles[1],p99_ms=quantiles[2],completed_latency_samples=len(rtts),
                max_pending_airtime_us=max_pending*1e6,calibrated_response=calibrated,
                completion_censoring=True,measurement_window='[warmup,horizon); departed throughput; post-warmup admitted/completed RTT',
                physical_measurement=False,automatic_execution_allowed=False)


def predict_grid(replications=3):
    if type(replications) is not int or not 2<=replications<=10:
        raise ValueError('2..10 bounded independent replications required')
    records,refs=load_measurements()
    calibration=calibrate(records)
    predictions=[]
    for round_id in ('R1','R2'):
      for count in range(1,17):
        vendors=tuple(('WA','XC','SXT','LBM5')[i%4] for i in range(count))
        for low,high,threshold in ((1000,2000,4000),(2000,4000,8000),(5000,12000,24000)):
            for rc,rts,txop in ((28,False,0),(50,False,0),(28,True,1500),(28,True,4000)):
                config=Scenario(vendors=vendors,aql_low_us=low,aql_high_us=high,aql_threshold_us=threshold,rc_per=rc,
                                dynamic_bw_rts=rts,txop_us=txop,collision_probability=0.1,calibration_round=round_id)
                runs=[simulate(Scenario(**{**asdict(config),'seed':20261024+1009*i}),calibration) for i in range(replications)]
                predictions.append(dict(cpes=count,scenario=asdict(config),runs=runs,
                                        goodput_mc_interval=replication_interval([r['goodput_mbps'] for r in runs])))
    return dict(schema_version=1,evidence='SIMULATED_SENSITIVITY_NOT_PHYSICAL_VALIDATION',sources=refs,
                software_versions=software_versions(),
                calibration=calibration,automatic_execution_allowed=False,predictions=predictions,
                assumptions=['WA/XC efficiency1 and SXT/LBM5 efficiency0.5 are user-visible scenario assumptions, not calibrated vendor measurements',
                             'Collision probability0.1 and RTS multiplier0.5 are assumed; no hidden-node traces available',
                             'RTS conceptual switch is not ct_special6, which is MAX_TXPOWER and excluded',
                             'TXOP batch service is conceptual, without exact WMM/firmware actuation mapping',
                             'Receiver goodput/p50 set phenomenological capacity/delay; no identifiable RF or firmware-queue decomposition',
                             'AQL admission losses do not model TCP feedback; tail samples are completion-censored',
                             '1..16CPE transport is extrapolation from one link; Monte Carlo intervals exclude model/parameter uncertainty'])


AC_ORDER = ('VO', 'VI', 'BE', 'BK')
WAVE_G_DIR = ROOT / 'artifacts/autoresearch/waves_efgh_20261024'


@dataclass(frozen=True)
class QueuePolicy:
    """Numerical model domain, not an actuator or a physically safe RAM range."""
    aql_by_ac: tuple = ((2000,4000),)*4
    aql_threshold_us: int = 8000
    fq_quantum_bytes: int = 300
    dscp_micro_vo_steering: bool = False

    @classmethod
    def from_endpoint(cls, endpoint):
        if endpoint is None:
            raise ValueError('Endpoint policy is unrecorded; do not invent UL policy')
        return cls(tuple(tuple(x) for x in endpoint.aql_by_ac), endpoint.aql_threshold_us,
                   endpoint.fq_quantum_bytes, endpoint.dscp_micro_vo_steering).validate()

    def validate(self):
        if (len(self.aql_by_ac)!=4 or any(len(pair)!=2 or any(type(v)is not int for v in pair)
                or not 1<=pair[0]<=pair[1]<=50000 for pair in self.aql_by_ac)
                or type(self.aql_threshold_us)is not int or not 1<=self.aql_threshold_us<=200000
                or type(self.fq_quantum_bytes)is not int or not 16<=self.fq_quantum_bytes<=65536
                or type(self.dscp_micro_vo_steering)is not bool):
            raise ValueError('Invalid bounded per-AC model policy')
        return self


@dataclass(frozen=True)
class FlowSpec:
    name: str
    peer: int
    direction: str
    protocol: str
    packet_bytes: int
    offered_mbps: float
    base_ac: str = 'BE'
    dscp: int = 0


@dataclass(frozen=True)
class PerACScenario:
    vendors: tuple = ('WA',)
    ap_policy: QueuePolicy = QueuePolicy()
    cpe_policy: QueuePolicy | None = QueuePolicy()
    horizon_s: float = .5
    warmup_s: float = .1
    collision_probability: float = .1
    legacy_efficiency: float = .5
    ac_weights: tuple = (4,3,2,1)
    max_packets: int = 20000
    max_events: int = 300000
    seed: int = 20261024

    def validate(self, flows):
        if not 1<=len(self.vendors)<=16 or any(v not in {'WA','XC','SXT','LBM5'} for v in self.vendors):
            raise ValueError('1..16 declared vendor classes required')
        self.ap_policy.validate()
        if self.cpe_policy is not None:self.cpe_policy.validate()
        for name,lo,hi in (('max_packets',1,100000),('max_events',1,2000000)):
            if type(getattr(self,name))is not int or not lo<=getattr(self,name)<=hi:raise ValueError('Invalid cap')
        if type(self.seed)is not int or not 0<=self.seed<=2**53 or len(self.ac_weights)!=4 or any(type(v)is not int or not 1<=v<=16 for v in self.ac_weights):
            raise ValueError('Integer seed and bounded positive AC weights required')
        finite_number(self.horizon_s,'horizon',.01,10)
        finite_number(self.warmup_s,'warmup',0,self.horizon_s-.001)
        finite_number(self.collision_probability,'collision',0,.8)
        finite_number(self.legacy_efficiency,'efficiency',.1,1)
        if not 1<=len(flows)<=256 or len({f.name for f in flows})!=len(flows):raise ValueError('Bounded unique flows required')
        for f in flows:
            if (not isinstance(f.name,str) or not f.name or type(f.peer)is not int or not 0<=f.peer<len(self.vendors)
                    or f.direction not in {'DL','UL'} or f.protocol not in {'TCP','UDP','ICMP'} or f.base_ac not in AC_ORDER
                    or type(f.packet_bytes)is not int or not 64<=f.packet_bytes<=1500
                    or type(f.dscp)is not int or not 0<=f.dscp<=63):raise ValueError('Malformed flow')
            finite_number(f.offered_mbps,'flow load',0,1000)
            if f.direction=='UL' and self.cpe_policy is None:raise ValueError('UL requires recorded CPE policy')
        if sum(f.offered_mbps for f in flows)>2000:raise ValueError('Sector offered-load model cap')
        return self


def classify_micro(flow, policy):
    """EF marking and its VO mapping are explicit MODEL assumptions, not driver proof."""
    micro=flow.protocol in {'UDP','ICMP'} and flow.packet_bytes<256
    effective_dscp=46 if micro and policy.dscp_micro_vo_steering else flow.dscp
    return ('VO' if micro and effective_dscp==46 else flow.base_ac),effective_dscp


def simulate_per_ac(scenario, flows, response, variant='per_ac'):
    """Shared half-open-horizon server, per-sender/peer/AC AQL and flow DRR.

    pooled_uniform is a deliberately uniform BE/FIFO baseline using the same
    traffic, horizon, collision probability, seeds and train-only response seam.
    Neither variant is a calibrated mac80211/firmware scheduler implementation.
    """
    scenario.validate(flows)
    if variant not in {'per_ac','pooled_uniform'}:raise ValueError('Unknown variant')
    capacity=finite_number(response['goodput_mbps'],'capacity',.001,10000)
    delay=finite_number(response['p50_ms'],'latency anchor',0,1000000)/1000
    import simpy
    env=simpy.Environment();n=len(flows)
    policies=[scenario.ap_policy if f.direction=='DL' else scenario.cpe_policy for f in flows]
    classes=[classify_micro(f,p)[0] if variant=='per_ac' else 'BE' for f,p in zip(flows,policies)]
    keys=[(f.direction,f.peer,ac) for f,ac in zip(flows,classes)]
    queues=[deque() for _ in flows];pending={k:0.0 for k in keys};max_pending=0.0
    counts=[dict(arrivals=0,rejected=0,delivered=0,collision_lost=0) for _ in flows]
    departures=[0]*n;latencies=[[] for _ in flows];busy=None;arrived=0;changed=env.event()
    # Disjoint integer blocks for every allowed scenario seed: role1 collision,
    # roles1000..1255 arrival streams (at most256 TOTAL flows across all16peers).
    seed_block=scenario.seed*10000
    arrival_seeds=[seed_block+1000+i for i in range(n)]
    collision_seed=seed_block+1
    collision_rng=random.Random(collision_seed)
    cycle=[ac for ac,w in zip(AC_ORDER,scenario.ac_weights) for _ in range(w)] if variant=='per_ac' else ['BE']
    cursor=0;flow_cursor={ac:0 for ac in AC_ORDER};deficits=[0]*n
    def notify():
        nonlocal changed
        if not changed.triggered:changed.succeed()
        changed=env.event()
    def sender_total(index):
        f=flows[index]
        return sum(v for (direction,peer,_),v in pending.items() if direction==f.direction and (direction=='DL' or peer==f.peer))
    def arrival(index):
        nonlocal arrived,max_pending
        f,p=flows[index],policies[index]
        if f.offered_mbps==0:return
        rng=random.Random(arrival_seeds[index]);interval=f.packet_bytes*8/(f.offered_mbps*1e6)
        while True:
            wait=interval*rng.uniform(.9,1.1)
            if env.now+wait>=scenario.horizon_s:return
            yield env.timeout(wait)
            if arrived>=scenario.max_packets:raise RuntimeError('Packet cap before horizon; aborted')
            arrived+=1;counts[index]['arrivals']+=1
            efficiency=1.0 if scenario.vendors[f.peer] in {'WA','XC'} else scenario.legacy_efficiency
            duration=f.packet_bytes*8/(capacity*1e6*efficiency)
            ac_index=AC_ORDER.index(classes[index]);lo,hi=p.aql_by_ac[ac_index]
            limit=(lo if sender_total(index)*1e6>=p.aql_threshold_us else hi)/1e6
            if pending[keys[index]]+duration>limit:
                counts[index]['rejected']+=1;continue
            queues[index].append((env.now,duration));pending[keys[index]]+=duration
            max_pending=max(max_pending,sum(pending.values()));notify()
    def next_flow():
        nonlocal cursor
        # Positive DRR credit bounds every internal selection loop. Empty flows
        # lose old credit, so an idle microflow cannot accumulate an unbounded burst.
        for _ in range(len(cycle)):
            ac=cycle[cursor%len(cycle)];cursor+=1
            eligible=[i for i in range(n) if classes[i]==ac and queues[i]]
            if not eligible:continue
            if variant=='pooled_uniform':
                i=eligible[flow_cursor[ac]%len(eligible)];flow_cursor[ac]+=1;return i
            for _ in range(96*n):
                i=flow_cursor[ac]%n;flow_cursor[ac]+=1
                if classes[i]!=ac:continue
                if not queues[i]:deficits[i]=0;continue
                deficits[i]+=policies[i].fq_quantum_bytes
                if deficits[i]>=flows[i].packet_bytes:
                    deficits[i]-=flows[i].packet_bytes;return i
            raise AssertionError('Bounded DRR selection failed')
        raise AssertionError('Nonempty queue not selected')
    def server():
        nonlocal busy
        while True:
            if not any(queues):yield changed;continue
            i=next_flow();arrival_time,duration=queues[i].popleft();busy=i
            yield env.timeout(duration)
            pending[keys[i]]-=duration
            if pending[keys[i]] < -1e-10:raise AssertionError('Negative pending airtime')
            pending[keys[i]]=max(0.0,pending[keys[i]])
            lost=collision_rng.random()<scenario.collision_probability
            counts[i]['collision_lost' if lost else 'delivered']+=1
            if not lost and env.now>=scenario.warmup_s:departures[i]+=1
            if not lost and arrival_time>=scenario.warmup_s:
                latencies[i].append((env.now-arrival_time+delay)*1000)
            busy=None
    for i in range(n):env.process(arrival(i))
    env.process(server());events=0
    while env.peek()<scenario.horizon_s:
        if events>=scenario.max_events:raise RuntimeError('Event cap before horizon; aborted')
        env.step();events+=1
    per_flow=[];totals=dict.fromkeys(('arrivals','rejected','delivered','collision_lost','unfinished'),0)
    all_micro=[];all_latency=[]
    for i,f in enumerate(flows):
        unfinished=len(queues[i])+int(busy==i);c=counts[i]
        assert c['arrivals']==sum(c[k] for k in ('rejected','delivered','collision_lost'))+unfinished
        for k,v in c.items():totals[k]+=v
        totals['unfinished']+=unfinished
        rate=departures[i]*f.packet_bytes*8/((scenario.horizon_s-scenario.warmup_s)*1e6)
        micro=f.protocol in {'UDP','ICMP'} and f.packet_bytes<256
        if micro:all_micro.extend(latencies[i])
        all_latency.extend(latencies[i])
        per_flow.append(dict(flow=asdict(f),admission_ac=classes[i],effective_dscp=classify_micro(f,policies[i])[1],
                             counts=c,unfinished=unfinished,goodput_mbps=rate,completed_latency_samples=len(latencies[i])))
    assert abs(sum(pending.values())-sum(p[1] for q in queues for p in q)-(0 if busy is None else flows[busy].packet_bytes*8/(capacity*1e6*(1 if scenario.vendors[flows[busy].peer] in {'WA','XC'} else scenario.legacy_efficiency))))<1e-8
    micro_configured=any(f.protocol in {'UDP','ICMP'} and f.packet_bytes<256 for f in flows)
    samples=all_micro if micro_configured else all_latency
    quant=np.percentile(samples,[50,95,99]).tolist() if samples else [None]*3
    bulk=sum(x['goodput_mbps'] for x in per_flow if x['flow']['protocol']=='TCP')
    return dict(variant=variant,scenario=asdict(scenario),flows=per_flow,counts=totals,events=events,
                goodput_mbps=bulk,total_including_probes_mbps=sum(x['goodput_mbps'] for x in per_flow),
                p50_ms=quant[0],p95_ms=quant[1],p99_ms=quant[2],micro_latency_samples=len(all_micro),
                latency_sample_population='micro_only' if micro_configured else 'all_packets_no_micro_configured',
                max_pending_airtime_us=max_pending*1e6,pending_airtime_us=sum(pending.values())*1e6,
                seed_manifest=dict(arrivals=dict(zip((f.name for f in flows),arrival_seeds)),collisions=collision_seed),
                latency_scope='Post-warmup completed micro-packet queue/service plus train-only RTT anchor; not a two-leg packet trace',
                completion_censoring=True,horizon_scope='[warmup,horizon); departures and birth cohort differ',
                EF46_to_AC_VO='MODEL_ASSUMPTION_UNVERIFIED',physical_measurement=False,automatic_execution_allowed=False)


def _endpoint_features(policy, pooled=False):
    if policy is None:return np.zeros(25)
    pairs=policy.aql_by_ac if not pooled else (policy.aql_by_ac[2],)*4
    values=[v/scale for pair in pairs for v,scale in zip(pair,(5000,12000))]
    values.extend((policy.aql_threshold_us/24000,policy.fq_quantum_bytes/1514,policy.rc_per_thresh/50,
                   0 if policy.rts_threshold is None else policy.rts_threshold/2347,int(policy.dscp_micro_vo_steering)))
    for name,scale in (('ct_baseband_rifs',1),('ct_pshack',1),('htt_max_amsdu',3),('htt_max_ampdu',64)):
        value=getattr(policy,name,None);values.extend((0 if value is None else value/scale,int(value is not None)))
    values.extend((1,0,0,0))
    return np.array(values,dtype=float)


def _policy_key(row):
    return row.policy_key


def multiflow_response(training, query, variant):
    """Fixed engineering scales/bandwidth; no target outcomes or tuned RMSE."""
    if variant not in {'per_ac','pooled_uniform'}:raise ValueError('Unknown variant')
    if not training:raise ValueError('No same-regime training data after held-policy exclusion')
    pooled=variant=='pooled_uniform'
    def features(row):return np.concatenate((_endpoint_features(row.ap_policy,pooled),_endpoint_features(row.cpe_policy,pooled)))
    x=features(query);dist=np.array([np.linalg.norm(features(r)-x) for r in training])
    weights=np.exp(-(dist-dist.min())**2/(2*.5**2));weights/=weights.sum()
    result={key:float(weights@np.array([getattr(r,key) for r in training])) for key in ('goodput_mbps','p50_ms','p95_ms','p99_ms')}
    result.update(nearest_training_distance=float(dist.min()),training_ids=[r.round_id+':'+r.iteration for r in training])
    return result


def scenario_flows(peers, active_flow_count=6, bidirectional=True, offered_mbps=120):
    """Declared synthetic traffic, never reconstructed from aggregate receipts."""
    if type(peers)is not int or not 1<=peers<=16 or active_flow_count not in (2,6):raise ValueError('Unsupported synthetic flow layout')
    flows=[]
    for peer in range(peers):
        for j in range(active_flow_count):
            direction='UL' if bidirectional and j%2 else 'DL'
            flows.append(FlowSpec(f'p{peer}-tcp{j}',peer,direction,'TCP',1500,offered_mbps/(peers*active_flow_count)))
        flows.append(FlowSpec(f'p{peer}-icmp',peer,'DL','ICMP',64,.02))
        if bidirectional:flows.append(FlowSpec(f'p{peer}-udp',peer,'UL','UDP',128,.02))
    return flows


def wave_g_heldout(rows, replications=3, horizon=.5):
    if type(replications)is not int or not 2<=replications<=10:raise ValueError('2..10 replications')
    comparisons=[]
    for query in rows:
        if query.round_id not in {'R7','R8','R9'}:continue
        training=[r for r in rows if r.workload_regime==query.workload_regime and _policy_key(r)!=_policy_key(query)]
        if len(training)<3:raise ValueError('Insufficient held-policy same-regime training')
        for variant in ('per_ac','pooled_uniform'):
            response=multiflow_response(training,query,variant)
            runs=[]
            for i in range(replications):
                s=PerACScenario(ap_policy=QueuePolicy.from_endpoint(query.ap_policy),cpe_policy=QueuePolicy.from_endpoint(query.cpe_policy),
                                horizon_s=horizon,warmup_s=horizon/5,seed=20261024+1009*i,collision_probability=0)
                run=simulate_per_ac(s,scenario_flows(1,query.active_flow_count,query.bidirectional),response,variant)
                if run['p95_ms'] is None:raise ValueError('No completed micro samples; latency prediction incomplete')
                runs.append(run)
            prediction=[float(np.mean([r[k] for r in runs])) for k in ('goodput_mbps','p95_ms','p99_ms')]
            actual=[query.goodput_mbps,query.p95_ms,query.p99_ms]
            comparisons.append(dict(round=query.round_id,iteration=query.iteration,variant=variant,held_policy_key=_policy_key(query),
                                    training_ids=response['training_ids'],training_policy_keys=[_policy_key(r) for r in training],
                                    observed_packet_loss_pct=query.packet_loss_pct,reported_restoration=query.restoration_verified,
                                    actual=actual,prediction=prediction,error=(np.array(prediction)-actual).tolist(),runs=runs))
    rmse={v:np.sqrt(np.mean(np.array([r['error'] for r in comparisons if r['variant']==v])**2,axis=0)).tolist() for v in ('per_ac','pooled_uniform')}
    return dict(status='EXECUTED_NATIVE_SIMPY_HELD_POLICY_OUT_NOT_PHYSICAL_VALIDATION',comparisons=comparisons,
                rmse_goodput_p95_p99=rmse,metric_order=['goodput_mbps','p95_ms','p99_ms'],
                comparison='Same targets/train IDs, whole joint AP+CPE policy excluded across rounds; same synthetic loads/seeds/horizon',
                limits=['No held-out response used in calibration; all losses/errors including worse model errors retained',
                        'Reported repetitions without raw per-repetition arrays do not create independent calibration units',
                        'No measured offered-load/per-AC/per-packet trace, EF-to-VO or station WFQ proof; queue parameters are assumptions'],
                automatic_execution_allowed=False,physical_accuracy_accepted=False)


def wave_g_main(replications=3):
    from orchestration.autoresearch.fmx_offline_data import load_all_measurements
    rows,refs=load_all_measurements();heldout=wave_g_heldout(rows,replications)
    reference=next(r for r in rows if r.round_id=='R7')
    training=[r for r in rows if r.workload_regime=='bidir_6flow']
    grid=[]
    for peers in range(1,17):
        for differentiated in (False,True):
            for steering in (False,True):
                policy=QueuePolicy(((500,1000),(1000,2000),(2000,4000),(5000,12000)) if differentiated else ((2000,4000),)*4,
                                   8000,300,steering)
                # Capacity/anchor held fixed for scenario sensitivity; vendor/AC
                # assumptions do not manufacture a learned multivendor coefficient.
                response=multiflow_response(training,reference,'per_ac')
                for variant in ('per_ac','pooled_uniform'):
                    runs=[simulate_per_ac(PerACScenario(tuple(('WA','XC','SXT','LBM5')[j%4] for j in range(peers)),policy,policy,
                                                       seed=20261024+1009*i),scenario_flows(peers),response,variant) for i in range(replications)]
                    grid.append(dict(cpes=peers,differentiated=differentiated,steering=steering,variant=variant,runs=runs,
                                     mc_interval=replication_interval([r['goodput_mbps'] for r in runs])))
    dataset=dict(schema_version=1,status='EXECUTED_WITH_NATIVE_SIMPY_MULTIFLOW',sources=refs,software_versions=software_versions(),
                 scenarios=grid,assumptions=['Weighted AC visits4/3/2/1 plus flow byte-DRR, not measured EDCA/firmware scheduling',
                   'Synthetic TCP bulk120Mbps total plus20kbps ICMP/UDP microflow per direction/peer; no measured trace',
                   'WA/XC efficiency1; SXT/LBM5 efficiency.5; collision probability.1 scenario only',
                   'EF46 micro-to-VO mapping is unverified; DSCP marking alone is not driver/airtime authority',
                   'Fixed synthetic grid profiles not selected by measured outcome; intervals conditional model MC only'],
                 physical_accuracy_accepted=False,automatic_execution_allowed=False)
    WAVE_G_DIR.mkdir(parents=True,exist_ok=True)
    for name,value in (('wave_g_predictions_20261024.json',dataset),('wave_g_heldout_validation_20261024.json',heldout)):
        encoded=(json.dumps(value,indent=2,allow_nan=False)+'\n').encode();path=WAVE_G_DIR/name
        if path.exists():
            if path.read_bytes()!=encoded:raise ValueError('Preserve existing differing WaveG output: '+name)
        else:
            with path.open('xb') as stream:stream.write(encoded)
    return dict(scenarios=len(grid),heldout_targets=len(heldout['comparisons'])//2,rmse=heldout['rmse_goodput_p95_p99'])


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/autoresearch/simpy_ptmp_predictions_20261024.json')
    parser.add_argument('--replications',type=int,default=3)
    parser.add_argument('--wave-g',action='store_true',help='Separate E-H multiflow/per-AC datasets; never overwrite legacy output')
    args=parser.parse_args(argv)
    if args.wave_g:
        print(json.dumps(wave_g_main(args.replications)))
        return 0
    try:
        dataset=predict_grid(args.replications)
    except RuntimeError as error:
        if not isinstance(error.__cause__,ImportError):
            raise
        records,refs=load_measurements()
        dataset=dict(schema_version=1,status='BLOCKED_OFFLINE_SIMPY_DEPENDENCY',
                     evidence='NO_SIMULATIONS_EXECUTED',automatic_execution_allowed=False,
                     sources=refs,calibration=calibrate(records),predictions=[],
                     pending_scenarios=384,required_replications=args.replications,
                     missing_dependency=str(error))
        write_json(args.output,dataset)
        print(f"{dataset['status']}: {args.output}")
        return 2
    dataset['status']='EXECUTED_WITH_SIMPY'
    write_json(args.output,dataset)
    print(f'OFFLINE_SIMULATION: {args.output}')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
