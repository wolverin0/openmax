"""Bounded offline AP/DL versus CPE/UL SimPy conceptual model; no actuator.

Seconds, bytes and airtime-us are explicit. Three TCP-like opportunity sources
per endpoint feed per-flow host queues, serialized endpoint preparation, AQL
driver queues and one contended link. CoDel is a persistent-sojourn approximation,
TSQ/notsent suppress source opportunities (not measured network loss). FQ is DRR.
CCMP preparation costs and offered traffic are hypotheses, not hardware facts.
"""
from collections import deque
from dataclasses import asdict, dataclass
import math
import random

import simpy


def real(value, name, low, high):
    if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError('Invalid '+name)
    return value


def integer(value, name, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('Invalid '+name)
    return value


class SimulationBudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class Endpoint:
    be_low_us: int = 1800
    be_high_us: int = 3600
    aql_threshold_us: int = 7200
    fq_quantum_bytes: int = 256
    fq_target_us: int = 10000
    fq_interval_us: int = 50000
    tcp_limit_output_bytes: int = 262144
    tcp_notsent_lowat: int = 131072

    def validate(self):
        for name, value in asdict(self).items():
            integer(value, name, 0 if name == 'tcp_notsent_lowat' else 1, 2**32-1)
        if not self.be_low_us <= self.be_high_us <= self.aql_threshold_us:
            raise ValueError('AQL low/high/threshold order')
        if self.fq_target_us > self.fq_interval_us:
            raise ValueError('CoDel target exceeds interval')
        return self


@dataclass(frozen=True)
class Scenario:
    horizon_s: float = .12
    warmup_s: float = .02
    drain_s: float = .03
    offered_dl_mbps: float = 120
    offered_ul_mbps: float = 45
    capacity_mbps: float = 120
    flows_per_endpoint: int = 3
    packet_bytes: int = 1500
    ccmp_dl_preparation_us: float = 4
    ccmp_ul_preparation_us: float = 15
    encryption_mode: str = 'psk2'
    max_packets: int = 20000
    max_events: int = 250000

    def validate(self):
        real(self.horizon_s, 'horizon', .02, 2)
        real(self.warmup_s, 'warmup', 0, self.horizon_s-.001)
        real(self.drain_s, 'drain', 0, 1)
        for name in ('offered_dl_mbps','offered_ul_mbps','capacity_mbps'):
            real(getattr(self,name),name,.01,1000)
        for name in ('ccmp_dl_preparation_us','ccmp_ul_preparation_us'):
            real(getattr(self,name),name,0,10000)
        integer(self.flows_per_endpoint,'flows per endpoint',1,8)
        integer(self.packet_bytes,'packet bytes',64,9000)
        integer(self.max_packets,'packet cap',1,50000)
        integer(self.max_events,'event cap',1,1000000)
        if self.encryption_mode not in ('none','psk2'):
            raise ValueError('Unsupported declared cipher')
        return self


def seed_manifest(seed, flows_per_endpoint):
    integer(seed,'seed',0,2**31-1)
    integer(flows_per_endpoint,'flows per endpoint',1,8)
    # Disjoint bounded blocks for independent replications and roles. Candidate
    # comparisons deliberately reuse a block (common random numbers).
    block=seed*10000
    return dict(seed=seed,block_width=10000,
                arrivals=[block+100+i for i in range(2*flows_per_endpoint)],
                backoff=[block+10,block+11],service=[block+20,block+21])


def percentile(values,p):
    if not values:
        return None
    data=sorted(values);position=(len(data)-1)*p;lo=math.floor(position);hi=math.ceil(position)
    return data[lo]+(data[hi]-data[lo])*(position-lo)


def simulate(ap=Endpoint(),cpe=Endpoint(),scenario=Scenario(),*,seed=20261024):
    """Finite, terminating SimPy run; outcomes describe this model only.

    Goodput counts completions in [warmup,horizon). Queue latency uses arrivals
    in that interval completed before horizon, with explicit right censoring.
    Drain outcomes never enter main-window metrics. SimPy events at the exact
    cut are excluded; no arbitrary zero-delay polling processes are used.
    """
    if not isinstance(ap,Endpoint) or not isinstance(cpe,Endpoint) or not isinstance(scenario,Scenario):
        raise ValueError('Endpoint/Scenario instances required')
    policies=[ap.validate(),cpe.validate()];s=scenario.validate()
    seeds=seed_manifest(seed,s.flows_per_endpoint)
    env=simpy.Environment();changed=env.event();events=0
    arrival_rng=[random.Random(v) for v in seeds['arrivals']]
    backoff_rng=[random.Random(v) for v in seeds['backoff']]
    service_rng=[random.Random(v) for v in seeds['service']]
    host=[[deque() for _ in range(s.flows_per_endpoint)] for _ in range(2)]
    driver=[deque(),deque()];preparing=[None,None];inflight=[None,None]
    pending_us=[0.,0.];peak_us=[0.,0.];outstanding=[[0]*s.flows_per_endpoint for _ in range(2)]
    aql_audit=[dict(low_window=0,high_window=0,low_below_local_threshold=0) for _ in range(2)]
    host_bytes=[[0]*s.flows_per_endpoint for _ in range(2)]
    deficit=[[0]*s.flows_per_endpoint for _ in range(2)];cursor=[0,0]
    first_above=[None,None];next_drop=[0.,0.];drop_count=[0,0]
    packets=[];offered=[0,0];backpressured=[0,0];collisions=0
    airtime_est=s.packet_bytes*8/s.capacity_mbps+20

    def notify():
        nonlocal changed
        old=changed;changed=env.event()
        if not old.triggered:old.succeed()

    def arrivals(d,f):
        rng=arrival_rng[d*s.flows_per_endpoint+f]
        mbps=(s.offered_dl_mbps if d==0 else s.offered_ul_mbps)/s.flows_per_endpoint
        while True:
            delay=rng.expovariate(mbps*1e6/(s.packet_bytes*8))
            if env.now+delay >= s.horizon_s:return
            yield env.timeout(delay)
            offered[d]+=1
            if sum(offered)>s.max_packets:raise SimulationBudgetExceeded('Packet opportunity cap')
            p=policies[d]
            if (outstanding[d][f]+s.packet_bytes>p.tcp_limit_output_bytes
                    or host_bytes[d][f]+s.packet_bytes>p.tcp_notsent_lowat):
                backpressured[d]+=1
                continue
            packet=dict(id=len(packets),direction=d,flow=f,arrival=env.now,
                        state='host',completed=None,bytes=s.packet_bytes)
            packets.append(packet);host[d][f].append(packet)
            host_bytes[d][f]+=s.packet_bytes;outstanding[d][f]+=s.packet_bytes
            notify()

    def choose(d):
        p=policies[d]
        # At most ceil(packet/quantum)+1 visits per nonempty flow. Pure bounded
        # credit operations, not zero-time SimPy busy-polling events.
        for _ in range(s.flows_per_endpoint*(math.ceil(s.packet_bytes/p.fq_quantum_bytes)+1)):
            f=cursor[d];cursor[d]=(f+1)%s.flows_per_endpoint
            if not host[d][f]:deficit[d][f]=0;continue
            deficit[d][f]+=p.fq_quantum_bytes
            if deficit[d][f]>=s.packet_bytes:
                deficit[d][f]-=s.packet_bytes
                packet=host[d][f].popleft();host_bytes[d][f]-=s.packet_bytes
                return packet
        raise RuntimeError('DRR bounded credit invariant')

    def dispatch(d):
        p=policies[d]
        while True:
            if not any(host[d]):
                yield changed;continue
            # AQL threshold belongs to THIS host/radio across its own flows;
            # the competing peer's queue is on a different machine.
            low_window=pending_us[d]>=p.aql_threshold_us
            aql_audit[d]['low_window' if low_window else 'high_window']+=1
            if low_window and pending_us[d]<p.aql_threshold_us:aql_audit[d]['low_below_local_threshold']+=1
            limit=p.be_low_us if low_window else p.be_high_us
            # One packet may exceed the configured airtime window; record this
            # bounded overshoot rather than deadlock a valid small AQL setting.
            if pending_us[d] and pending_us[d]+airtime_est>limit:
                yield changed;continue
            packet=choose(d);wait=env.now-packet['arrival']
            if wait*1e6>p.fq_target_us:
                if first_above[d] is None:first_above[d]=env.now+p.fq_interval_us/1e6
            else:first_above[d]=None;drop_count[d]=0
            if first_above[d] is not None and env.now>=first_above[d] and env.now>=next_drop[d]:
                packet['state']='codel_drop';outstanding[d][packet['flow']]-=packet['bytes']
                drop_count[d]+=1;next_drop[d]=env.now+p.fq_interval_us/1e6/math.sqrt(drop_count[d])
                notify();continue
            packet['state']='preparing';preparing[d]=packet
            cost=(s.ccmp_dl_preparation_us if d==0 else s.ccmp_ul_preparation_us) if s.encryption_mode=='psk2' else 0
            if cost:yield env.timeout(cost/1e6)
            preparing[d]=None;packet['state']='driver';driver[d].append(packet)
            pending_us[d]+=airtime_est;peak_us[d]=max(peak_us[d],pending_us[d]);notify()

    def service():
        nonlocal collisions
        while True:
            available=[d for d in range(2) if driver[d]]
            if not available:
                yield changed;continue
            backoffs={d:backoff_rng[d].randrange(16) for d in available}
            if len(available)==2 and backoffs[0]==backoffs[1]:
                collisions+=1;yield env.timeout((36+9*backoffs[0])/1e6);continue
            d=min(available,key=lambda k:backoffs[k]);packet=driver[d].popleft()
            packet['state']='inflight';inflight[d]=packet
            # Link is exclusively occupied through contention and service.
            duration=(backoffs[d]*9+airtime_est*service_rng[d].uniform(.9,1.1))/1e6
            yield env.timeout(duration)
            packet['state']='completed';packet['completed']=env.now;inflight[d]=None
            pending_us[d]=max(0.,pending_us[d]-airtime_est)
            outstanding[d][packet['flow']]-=packet['bytes'];notify()

    def run_until(cut):
        nonlocal events
        while env.peek()<cut:
            if events>=s.max_events:raise SimulationBudgetExceeded('Scheduled event cap')
            env.step();events+=1

    def snapshot(cut):
        counts={state:sum(p['state']==state for p in packets) for state in
                ('host','preparing','driver','inflight','completed','codel_drop')}
        pending=sum(counts[k] for k in ('host','preparing','driver','inflight'))
        assert sum(counts.values())==len(packets)
        assert sum(offered)==sum(backpressured)+len(packets)
        assert sum(sum(x) for x in outstanding)==pending*s.packet_bytes
        assert sum(sum(x) for x in host_bytes)==counts['host']*s.packet_bytes
        return dict(cut_s=cut,states=counts,pending=pending,
                    offered=sum(offered),backpressured=sum(backpressured),admitted=len(packets),
                    offered_bytes=sum(offered)*s.packet_bytes,
                    backpressured_bytes=sum(backpressured)*s.packet_bytes,
                    completed_bytes=counts['completed']*s.packet_bytes,
                    codel_dropped_bytes=counts['codel_drop']*s.packet_bytes,
                    pending_bytes=pending*s.packet_bytes,
                    right_censored_measurement_cohort=sum(s.warmup_s<=p['arrival']<s.horizon_s
                        and p['state'] not in ('completed','codel_drop') for p in packets),
                    packet_and_byte_conservation=True)

    for d in range(2):
        for f in range(s.flows_per_endpoint):env.process(arrivals(d,f))
        env.process(dispatch(d))
    env.process(service());run_until(s.horizon_s);at_horizon=snapshot(s.horizon_s)
    duration=s.horizon_s-s.warmup_s;metrics=[]
    for d in range(2):
        completed=[p for p in packets if p['direction']==d and p['completed'] is not None
                   and s.warmup_s<=p['completed']<s.horizon_s]
        delays=[(p['completed']-p['arrival'])*1000 for p in completed if p['arrival']>=s.warmup_s]
        metrics.append(dict(goodput_mbps=len(completed)*s.packet_bytes*8/duration/1e6,
            cohort_completed=len(delays),delay_p50_ms=percentile(delays,.5),
            delay_p95_ms=percentile(delays,.95),delay_p99_ms=percentile(delays,.99)))
    run_until(s.horizon_s+s.drain_s);after_drain=snapshot(s.horizon_s+s.drain_s)
    dl,ul=[m['goodput_mbps'] for m in metrics];fairness=(dl+ul)**2/(2*(dl*dl+ul*ul)) if dl+ul else None
    return dict(status='MODEL_ONLY_SIMPY_EXECUTED',automatic_execution_allowed=False,
        endpoints=dict(AP=asdict(ap),CPE=asdict(cpe)),scenario=asdict(s),seeds=seeds,
        DL=metrics[0],UL=metrics[1],total_goodput_mbps=dl+ul,jain_directional=fairness,
        rtt_p95_proxy_ms=(metrics[0]['delay_p95_ms']+metrics[1]['delay_p95_ms'])
            if all(m['delay_p95_ms'] is not None for m in metrics) else None,
        rtt_proxy_limit='SUM_OF_DIRECTIONAL_P95_NOT_MEASURED_RTT_QUANTILE',
        horizon=at_horizon,after_drain=after_drain,peak_driver_airtime_us=peak_us,
        aql_decision_audit=aql_audit,
        collisions=collisions,events_processed=events,
        limits=['No PHY, driver/firmware, CCMP offload, per-AC or Linux CoDel/TSQ conformance validation.',
                'Three opportunity sources per endpoint; TSQ/notsent source suppression is not network packet loss.',
                'Unknown actual offered traffic, ACK dynamics, serial RTT sampling and hardware CPU costs.',
                'Delay cohort is right-censored at horizon; drain completions excluded from main metrics.'])
