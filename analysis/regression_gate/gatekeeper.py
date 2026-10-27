"""
Autonomous A/B/A/B Regression Gatekeeper and Lexicographic Evaluator.
Implements Decision D-0009, AGENTS.md Section 7-8, and Phase 0 Workstream D.

Evaluation Rules:
1. Hard validity check (watchdog / firmware reset / excessive packet loss).
2. Temporal drift check across baseline (A) sentinel/sequential blocks.
3. Full lexicographic hierarchy:
   - Priority 1: Loaded latency p99 (must not regress beyond max_p99_regression_pct)
   - Priority 2: Loaded latency p95 (must not regress beyond max_p95_regression_pct)
   - Priority 3: Jain fairness index & worst-peer service (must not drop beyond max_fairness_drop_pct)
   - Priority 4: Spectral efficiency goodput_per_mhz (must gain at least min_goodput_gain_pct)
4. Predeclared latency/capacity/robustness objective; exact sign flips or a
   conservative Monte Carlo bound, paired intervals and single-step Sidak family.
5. One canonical evaluate/evaluate_paired API. SYNTHETIC_PASS is never physical
   promotion. Physical confirmation requires source bytes, readback binding and
   an independent receipt whose objective/family was frozen before acquisition.
"""

from __future__ import annotations

import itertools
import hashlib
import json
import math
import random
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from analysis.metrics.schema import validate_channel_width_mhz


class EvidenceState(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    STATIC_VERIFIED = "STATIC_VERIFIED"
    BENCH_EXECUTED = "BENCH_EXECUTED"
    BENCH_REPLICATED = "BENCH_REPLICATED"
    FIELD_CANARY = "FIELD_CANARY"
    PRODUCTION_ACCEPTED = "PRODUCTION_ACCEPTED"


OBJECTIVES = ("LATENCY_WITH_CAPACITY_NONINFERIORITY", "CAPACITY_WITH_QOE_CONSTRAINTS",
              "ROBUSTNESS", "CAPABILITY_DISCOVERY")


def _number(value, name, minimum=0.0, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name} outside admissible range")
    return value


@dataclass
class RunMetrics:
    run_id: str
    arm: str  # 'A' (Baseline) or 'B' (Candidate)
    goodput_mbps: float
    p95_lat_ms: float
    p99_lat_ms: float
    loss_pct: float
    jain_fairness: float
    firmware_resets: int = 0
    channel_width_mhz: Optional[int] = None
    goodput_per_mhz: Optional[float] = None
    block_index: Optional[int] = None
    is_sentinel: bool = False
    worst_peer_goodput_mbps: Optional[float] = None
    evidence_state: Optional[str] = None
    raw_sha256: Optional[str] = None
    raw_evidence_path: Optional[str] = None
    session_id: Optional[str] = None
    peer_id: Optional[str] = None
    window_start_s: Optional[float] = None
    window_end_s: Optional[float] = None
    applied_config_sha256: Optional[str] = None

    def __setattr__(self,name,value):
        if name=='evidence_state' and '_origin_state' in self.__dict__:
            normalized=EvidenceState(value).value if value is not None else None
            if normalized!=self.__dict__['_origin_state']:
                raise ValueError('evidence origin is immutable; copying a metric cannot promote its source')
        object.__setattr__(self,name,value)

    def __post_init__(self) -> None:
        # 30MHz is a real PowerBeam/M5 width; never substitute a20MHz carrier.
        if type(self.channel_width_mhz) is not int or self.channel_width_mhz != 30:
            validate_channel_width_mhz(self.channel_width_mhz)
        if not isinstance(self.run_id, str) or not self.run_id.strip() or self.arm not in ('A','B'):
            raise ValueError('run_id and A/B arm are required')
        for name in ('goodput_mbps','p95_lat_ms','p99_lat_ms'):
            _number(getattr(self,name),name)
        _number(self.loss_pct,'loss_pct',maximum=100)
        _number(self.jain_fairness,'jain_fairness',maximum=1)
        if self.p95_lat_ms > self.p99_lat_ms:
            raise ValueError('p95 cannot exceed p99')
        if type(self.firmware_resets) is not int or self.firmware_resets < 0:
            raise ValueError('firmware_resets must be a nonnegative integer')
        if self.block_index is not None and (type(self.block_index) is not int or self.block_index < 0):
            raise ValueError('block_index must be a nonnegative integer')
        if self.is_sentinel and self.arm != 'A':
            raise ValueError('sentinel must be an A baseline')
        if type(self.is_sentinel) is not bool:raise ValueError('is_sentinel must be boolean')
        if self.worst_peer_goodput_mbps is not None:
            _number(self.worst_peer_goodput_mbps,'worst_peer_goodput_mbps',maximum=self.goodput_mbps)
        expected = self.goodput_mbps / self.channel_width_mhz
        if self.goodput_per_mhz is None:
            self.goodput_per_mhz = round(expected, 4)
        else:
            _number(self.goodput_per_mhz,'goodput_per_mhz')
            if not math.isclose(self.goodput_per_mhz,expected,rel_tol=1e-5,abs_tol=5.1e-5):
                raise ValueError('goodput_per_mhz disagrees with receiver goodput/channel width')
        if self.evidence_state is not None:
            self.evidence_state = EvidenceState(self.evidence_state).value
        for name in ('raw_sha256','applied_config_sha256'):
            value=getattr(self,name)
            if value is not None and not re.fullmatch('[0-9a-f]{64}',value):
                raise ValueError(f'{name} must be a SHA256')
        if self.window_start_s is not None or self.window_end_s is not None:
            _number(self.window_start_s,'window_start_s');_number(self.window_end_s,'window_end_s')
            if self.window_end_s <= self.window_start_s:
                raise ValueError('window end must follow start')
        if '_origin_state' not in self.__dict__:
            object.__setattr__(self,'_origin_state',self.evidence_state)


@dataclass
class PairedBlockDiff:
    block_index: int
    run_a: RunMetrics
    run_b: RunMetrics
    goodput_per_mhz_delta_pct: float
    goodput_mbps_delta_pct: float
    p99_delta_pct: float
    p95_delta_pct: float
    fairness_delta_pct: float
    worst_peer_delta_pct: Optional[float]


@dataclass
class GateDecision:
    verdict: str  # REJECT, INCONCLUSIVE, SYNTHETIC_PASS, KEEP_FOR_REPLICATION, PROMOTE
    rationale: str
    p99_delta_pct: float
    goodput_delta_pct: float
    p_value: float
    summary: str
    promotion_stage: str = "INCONCLUSIVE"
    p95_delta_pct: float = 0.0
    fairness_delta_pct: float = 0.0
    goodput_per_mhz_delta_pct: float = 0.0
    paired_permutation_p_value: float = 1.0
    ci_95_goodput_per_mhz_delta_pct: Tuple[float, float] = (0.0, 0.0)
    ci_95_p99_delta_pct: Tuple[float, float] = (0.0, 0.0)
    drift_detected: bool = False
    drift_pct: float = 0.0
    paired_blocks_count: int = 0
    adjusted_alpha: float = 0.05
    evidence_state: Optional[str] = None
    objective: str = "LATENCY_WITH_CAPACITY_NONINFERIORITY"
    promotion_eligible: bool = False


def _read_evidence(root: Path, label: str):
    """Read only a bounded, explicitly named local receipt under its evidence root."""
    if not isinstance(label,str) or not label or '\\' in label or ':' in label or label.startswith('/'):
        raise ValueError('relative evidence path required')
    if any(p in ('','.','..') for p in label.split('/')):
        raise ValueError('invalid evidence path')
    root=Path(root).resolve()
    if str(root).startswith('\\\\'):
        raise ValueError('network evidence root forbidden')
    path=root/label
    for parent in (path, *path.parents):
        if parent==root:break
        if parent.is_symlink() or getattr(parent,'is_junction',lambda:False)():
            raise ValueError('reparse evidence paths forbidden')
    if not path.resolve().is_relative_to(root) or path.stat().st_size>8*1024*1024:
        raise ValueError('evidence outside root or size limit')
    with path.open('rb') as stream:blob=stream.read(8*1024*1024+1)
    if len(blob)>8*1024*1024:raise ValueError('evidence read size limit')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('duplicate evidence JSON key')
            result[key]=value
        return result
    def invalid(value):raise ValueError('nonfinite evidence JSON')
    data=json.loads(blob.decode('utf-8'),object_pairs_hook=unique,parse_constant=invalid)
    if not isinstance(data,dict):raise ValueError('evidence object required')
    return data,hashlib.sha256(blob).hexdigest()


def validate_run_provenance(runs, evidence_root=None):
    """Bind normalized measurements to actual supplied acquisition-receipt bytes.

    This validates source integrity and arithmetic, not honesty of an instrument
    or physical execution. Synthetic/static records cannot enter physical promotion.
    """
    root=Path(evidence_root or Path(__file__).resolve().parents[2]);errors=[]
    seen_ids=set();seen_raw=set()
    metrics=('goodput_mbps','p95_lat_ms','p99_lat_ms','loss_pct','jain_fairness',
             'channel_width_mhz','worst_peer_goodput_mbps','firmware_resets')
    for run in runs:
        try:
            run.__post_init__()
            if run.evidence_state not in {s.value for s in EvidenceState if s not in (EvidenceState.SYNTHETIC,EvidenceState.STATIC_VERIFIED)}:
                raise ValueError('nonphysical or unclassified evidence')
            if not all((run.raw_sha256,run.raw_evidence_path,run.session_id,run.peer_id,run.applied_config_sha256)) or run.window_start_s is None:
                raise ValueError('missing primary source/readback/window identity')
            if run.run_id in seen_ids or run.raw_sha256 in seen_raw:
                raise ValueError('duplicate run/raw identity')
            seen_ids.add(run.run_id);seen_raw.add(run.raw_sha256)
            record,digest=_read_evidence(root,run.raw_evidence_path)
            if digest!=run.raw_sha256:raise ValueError('raw receipt SHA mismatch')
            for name in ('run_id','arm','block_index','is_sentinel','session_id','peer_id',
                         'window_start_s','window_end_s','evidence_state'):
                if name not in record or record[name]!=getattr(run,name):raise ValueError('raw identity/window/type mismatch')
            if type(record['is_sentinel']) is not bool or (record['block_index'] is not None and type(record['block_index']) is not int):
                raise ValueError('raw schedule labels have invalid types')
            for name in metrics:_number(record.get('metrics',{}).get(name),'raw '+name)
            if any(record.get('metrics',{}).get(k)!=getattr(run,k) for k in metrics):
                raise ValueError('raw normalized metrics mismatch')
            config=record.get('config_readback')
            if not isinstance(config,dict):raise ValueError('config readback missing')
            if config.get('channel_width_mhz')!=run.channel_width_mhz:
                raise ValueError('readback width differs from normalized observation')
            canonical=json.dumps(config,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
            if hashlib.sha256(canonical).hexdigest()!=run.applied_config_sha256:
                raise ValueError('applied readback fingerprint mismatch')
            acquisition=record.get('acquisition',{})
            sent=acquisition.get('packets_sent');received=acquisition.get('packets_received')
            if type(sent) is not int or type(received) is not int or not 0<received<=sent:
                raise ValueError('missing actual sent/received counts')
            if type(acquisition.get('capture_drops')) is not int or acquisition['capture_drops']!=0 or acquisition.get('goodput_source')!='receiver':
                raise ValueError('unverified capture coverage or sender-only rate')
            if not math.isclose(run.loss_pct,100*(sent-received)/sent,abs_tol=1e-6):
                raise ValueError('packet-loss/count mismatch')
            latencies=acquisition.get('latencies_ms',[])
            if len(latencies)!=received:raise ValueError('latency sample coverage mismatch')
            for value in latencies:_number(value,'raw latency')
            ordered=sorted(latencies)
            if acquisition.get('percentile_method')!='nearest_rank':raise ValueError('unfrozen percentile method')
            for fraction,name in ((.95,'p95_lat_ms'),(.99,'p99_lat_ms')):
                if not math.isclose(ordered[math.ceil(fraction*received)-1],getattr(run,name),abs_tol=1e-6):
                    raise ValueError('raw percentile mismatch')
            duration=acquisition.get('duration_seconds');byte_count=acquisition.get('receiver_bytes')
            _number(duration,'duration_seconds',minimum=1e-12)
            if type(byte_count) is not int or byte_count<0:raise ValueError('receiver bytes missing')
            if not math.isclose(duration,run.window_end_s-run.window_start_s,rel_tol=.01):
                raise ValueError('acquisition/window coverage mismatch')
            if not math.isclose(byte_count*8/duration/1e6,run.goodput_mbps,rel_tol=.0001,abs_tol=.001):
                raise ValueError('receiver byte/time rate mismatch')
            peers=acquisition.get('peer_goodput_mbps',{})
            roster=acquisition.get('expected_peers',[])
            if (not isinstance(peers,dict) or not peers or not isinstance(roster,list)
                    or len(set(roster))!=len(roster) or any(not isinstance(peer,str) or not peer for peer in roster)
                    or set(peers)!=set(roster)):
                raise ValueError('missing configured peer denominator')
            values=list(peers.values())
            for value in values:_number(value,'peer goodput')
            if sum(values)<=0:raise ValueError('no received service')
            fairness=sum(values)**2/(len(values)*sum(v*v for v in values))
            if (not math.isclose(sum(values),run.goodput_mbps,rel_tol=1e-5,abs_tol=.001)
                    or not math.isclose(min(values),run.worst_peer_goodput_mbps,abs_tol=.001)
                    or not math.isclose(fairness,run.jain_fairness,abs_tol=1e-4)):
                raise ValueError('peer aggregation/fairness/worst-peer mismatch')
        except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
            errors.append(f'{run.run_id}:UNAVAILABLE_TO_THIS_REVIEW_OR_INVALID:{exc}')
    if len({r.peer_id for r in runs})>1:errors.append('peer set identity changed within acquisition cohort')
    if len({r.applied_config_sha256 for r in runs if r.arm=='A'})>1:
        errors.append('baseline readback changed within acquisition cohort')
    return errors


def validate_holdout_evidence(discovery,holdout,candidate_fingerprint,evidence_root=None,
                              replication_receipt_path=None,contract=None):
    errors=validate_run_provenance(discovery,evidence_root)+validate_run_provenance(holdout,evidence_root)
    if not discovery or not holdout:return errors+['empty discovery or holdout']
    if errors:return errors
    for name in ('run_id','raw_sha256','session_id'):
        if {getattr(r,name) for r in discovery}&{getattr(r,name) for r in holdout}:
            errors.append('discovery/holdout overlap:'+name)
    if any(r.window_end_s is None for r in discovery+holdout):
        errors.append('missing independent time windows')
    elif max(r.window_end_s for r in discovery)>min(r.window_start_s for r in holdout):
        errors.append('discovery/holdout temporal overlap')
    if not candidate_fingerprint or any(r.applied_config_sha256!=candidate_fingerprint for r in discovery+holdout if r.arm=='B'):
        errors.append('candidate and treatment readback differ')
    baseline={r.applied_config_sha256 for r in discovery+holdout if r.arm=='A'}
    if len(baseline)!=1 or candidate_fingerprint in baseline:
        errors.append('baseline changed or no applied treatment contrast')
    if len({r.peer_id for r in discovery+holdout})!=1:errors.append('discovery/holdout peer identity changed')
    if errors:return errors
    try:
        receipt,_=_read_evidence(Path(evidence_root or Path(__file__).resolve().parents[2]),replication_receipt_path)
        if receipt.get('evidence_state')!='BENCH_REPLICATED':raise ValueError('independent replication receipt required')
        if receipt.get('candidate_fingerprint')!=candidate_fingerprint:raise ValueError('replication candidate mismatch')
        for key,rows in (('discovery',discovery),('holdout',holdout)):
            expected=[dict(run_id=r.run_id,raw_sha256=r.raw_sha256) for r in rows]
            if receipt.get(key)!=expected:raise ValueError('replication receipt dataset binding mismatch')
        plan=receipt.get('frozen_plan',{})
        _number(plan.get('created_at_s'),'frozen_plan.created_at_s')
        if plan['created_at_s']>=min(r.window_start_s for r in discovery):
            raise ValueError('plan not frozen before acquisition')
        if candidate_fingerprint not in plan.get('family_fingerprints',[]):raise ValueError('candidate outside frozen family')
        if contract is not None and plan.get('contract')!=contract:raise ValueError('objective/family contract changed')
        family=plan.get('family_fingerprints',[])
        if (len(set(family))!=len(family) or any(not re.fullmatch('[0-9a-f]{64}',str(fp)) for fp in family)
                or (contract is not None and len(family)!=contract['num_hypotheses_tested'])):
            raise ValueError('frozen family count/identity mismatch')
    except (OSError,ValueError,TypeError,KeyError) as exc:
        errors.append('replication proof:'+str(exc))
    return errors


def compute_mean_and_variance(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return mean, var


def welch_t_test(group_a: List[float], group_b: List[float]) -> float:
    """Computes approximate two-sided p-value using Welch's t-test."""
    n_a = len(group_a)
    n_b = len(group_b)
    if n_a < 2 or n_b < 2:
        return 1.0

    mean_a, var_a = compute_mean_and_variance(group_a)
    mean_b, var_b = compute_mean_and_variance(group_b)

    denom = math.sqrt((var_a / n_a) + (var_b / n_b))
    if denom < 1e-12:
        return 1.0 if abs(mean_a - mean_b) < 1e-6 else 0.0

    t_stat = abs(mean_a - mean_b) / denom

    num_dof = ((var_a / n_a) + (var_b / n_b)) ** 2
    den_dof = ((var_a / n_a) ** 2 / (n_a - 1)) + ((var_b / n_b) ** 2 / (n_b - 1))
    dof = max(1.0, num_dof / max(den_dof, 1e-12))

    z = t_stat / math.sqrt(1.0 + (t_stat ** 2) / (2.0 * dof))
    p_val = math.erfc(z / math.sqrt(2.0))
    return max(0.0, min(1.0, p_val))


def paired_sign_flip_p_value(
    paired_diffs: List[float],
    max_exact_blocks: int = 16,
    n_permutations: int = 4096,
    seed: int = 42,
) -> float:
    """Exact sign flips, or a conservative99.9% upper bound for Monte Carlo.

    Equal-magnitude differences use the exact binomial distribution for any N.
    A Monte Carlo estimate alone never grants a promotion near the alpha boundary.
    """
    if type(n_permutations) is not int or n_permutations<1 or type(max_exact_blocks) is not int or not 0<=max_exact_blocks<=20:
        raise ValueError('positive permutation budget and bounded exact enumeration required')
    for value in paired_diffs:
        if not math.isfinite(value):raise ValueError('nonfinite paired difference')
    n = len(paired_diffs)
    if n < 2:
        return 1.0
    observed = abs(sum(paired_diffs) / n)
    if observed < 1e-12:
        return 1.0
    magnitude=abs(paired_diffs[0])
    if magnitude and all(math.isclose(abs(d),magnitude,rel_tol=1e-12,abs_tol=1e-12) for d in paired_diffs):
        extreme=sum(math.comb(n,k) for k in range(n+1)
                    if abs(n-2*k)*magnitude/n>=observed-1e-12)
        return extreme/(1<<n)

    if n <= max_exact_blocks:
        total = 1 << n
        extreme = 0
        for signs in itertools.product((-1.0, 1.0), repeat=n):
            perm_mean = abs(sum(s * d for s, d in zip(signs, paired_diffs)) / n)
            if perm_mean >= observed - 1e-12:
                extreme += 1
        return max(0.0, min(1.0, extreme / float(total)))

    rng = random.Random(seed)
    extreme = 0
    for _ in range(n_permutations):
        perm_mean = abs(sum((1.0 if rng.random() < 0.5 else -1.0) * d for d in paired_diffs) / n)
        if perm_mean >= observed - 1e-12:
            extreme += 1
    from scipy.stats import beta
    upper=1.0 if extreme==n_permutations else float(beta.ppf(.999,extreme+1,n_permutations-extreme))
    return max((extreme+1)/(n_permutations+1),upper)


def paired_bootstrap_ci_95(
    paired_diffs: List[float],
    n_boot: int = 2000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Computes 95% bootstrap confidence interval for the mean paired block difference."""
    if type(n_boot) is not int or n_boot<1 or any(not math.isfinite(d) for d in paired_diffs):
        raise ValueError('positive bootstrap budget and finite differences required')
    n = len(paired_diffs)
    if n == 0:
        return (0.0, 0.0)
    if n == 1:
        val = round(paired_diffs[0], 4)
        return (val, val)
    if all(abs(d - paired_diffs[0]) < 1e-12 for d in paired_diffs):
        val = round(paired_diffs[0], 4)
        return (val, val)

    rng = random.Random(seed)
    means: List[float] = []
    for _ in range(n_boot):
        sample = [paired_diffs[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo_idx = max(0, min(n_boot - 1, int(0.025 * n_boot)))
    hi_idx = max(0, min(n_boot - 1, int(0.975 * n_boot)))
    return (round(means[lo_idx], 4), round(means[hi_idx], 4))


def compute_adjusted_alpha(alpha: float = 0.05, num_hypotheses: int = 1) -> float:
    """Single-step Sidak for the predeclared family; this is not Holm-Sidak."""
    if type(num_hypotheses) is not int or num_hypotheses<1 or not 0<alpha<1:
        raise ValueError('invalid frozen hypothesis family or alpha')
    m = num_hypotheses
    if m == 1:
        return alpha
    return -math.expm1(math.log1p(-alpha)/m)


def build_paired_blocks(runs: List[RunMetrics]) -> List[PairedBlockDiff]:
    """Require unique explicit paired identities; never zip, drop or repair arms."""
    runs_a = [r for r in runs if r.arm.upper() == "A" and not r.is_sentinel]
    runs_b = [r for r in runs if r.arm.upper() == "B" and not r.is_sentinel]

    if len({r.run_id for r in runs})!=len(runs):raise ValueError('duplicate run IDs')
    if any(r.block_index is None for r in runs_a+runs_b):raise ValueError('explicit block_index required')
    by_index_a = {r.block_index:r for r in runs_a}
    by_index_b = {r.block_index:r for r in runs_b}
    if len(by_index_a)!=len(runs_a) or len(by_index_b)!=len(runs_b):raise ValueError('duplicate block IDs')
    if set(by_index_a)!=set(by_index_b):raise ValueError('unmatched paired block IDs')
    pairs=[(idx,by_index_a[idx],by_index_b[idx]) for idx in sorted(by_index_a)]
    sequence=[(r.block_index,r.arm) for r in runs if not r.is_sentinel]
    if sequence!=[(idx,arm) for idx,_,_ in pairs for arm in ('A','B')]:
        raise ValueError('reordered or incomplete A/B event sequence')

    diffs: List[PairedBlockDiff] = []
    for idx, ra, rb in pairs:
        if ra.channel_width_mhz != rb.channel_width_mhz:
            raise ValueError(
                f"Block {idx} channel_width_mhz mismatch: arm A has {ra.channel_width_mhz} MHz "
                f"while arm B has {rb.channel_width_mhz} MHz."
            )
        ra.__post_init__();rb.__post_init__()
        gpm_a = float(ra.goodput_per_mhz or (ra.goodput_mbps / ra.channel_width_mhz))
        gpm_b = float(rb.goodput_per_mhz or (rb.goodput_mbps / rb.channel_width_mhz))
        gpm_delta = ((gpm_b - gpm_a) / max(gpm_a, 1e-6)) * 100.0
        gp_delta = ((rb.goodput_mbps - ra.goodput_mbps) / max(ra.goodput_mbps, 1e-6)) * 100.0
        p99_delta = ((rb.p99_lat_ms - ra.p99_lat_ms) / max(ra.p99_lat_ms, 1e-6)) * 100.0
        p95_delta = ((rb.p95_lat_ms - ra.p95_lat_ms) / max(ra.p95_lat_ms, 1e-6)) * 100.0
        fair_delta = ((rb.jain_fairness - ra.jain_fairness) / max(ra.jain_fairness, 1e-6)) * 100.0
        if ra.worst_peer_goodput_mbps is not None and rb.worst_peer_goodput_mbps is not None:
            wp_delta = (
                (rb.worst_peer_goodput_mbps - ra.worst_peer_goodput_mbps)
                / max(ra.worst_peer_goodput_mbps, 1e-6)
            ) * 100.0
        else:
            wp_delta = None
        diffs.append(
            PairedBlockDiff(
                block_index=idx,
                run_a=ra,
                run_b=rb,
                goodput_per_mhz_delta_pct=gpm_delta,
                goodput_mbps_delta_pct=gp_delta,
                p99_delta_pct=p99_delta,
                p95_delta_pct=p95_delta,
                fairness_delta_pct=fair_delta,
                worst_peer_delta_pct=wp_delta,
            )
        )
    observations=[r for r in runs if not r.is_sentinel]
    if any(r.window_start_s is not None for r in observations):
        if any(r.window_start_s is None or r.window_end_s is None for r in observations):
            raise ValueError('missing paired acquisition windows')
        if any(previous.window_end_s>following.window_start_s
               for previous,following in zip(observations,observations[1:])):
            raise ValueError('paired acquisition windows overlap or are chronologically reordered')
    return diffs


def detect_baseline_drift(
    runs: List[RunMetrics],
    max_drift_pct: float = 20.0,
) -> Tuple[bool, float, str]:
    """Detects non-stationary RF/environment drift across baseline (A) and sentinel blocks."""
    baseline_all = [r for r in runs if r.arm.upper() == "A"]
    if len(baseline_all) < 2:
        return False, 0.0, "Insufficient baseline runs for drift check."

    # Every baseline matters, including an intermediate dip between equal endpoints.
    gpms=[r.goodput_per_mhz for r in baseline_all]
    latencies=[r.p99_lat_ms for r in baseline_all]
    gpm_drift_pct=(max(gpms)-min(gpms))/max(min(gpms),1e-6)*100
    p99_drift_pct=(max(latencies)-min(latencies))/max(min(latencies),1e-6)*100

    worst_drift = max(gpm_drift_pct, p99_drift_pct)
    if worst_drift > max_drift_pct:
        return (
            True,
            round(worst_drift, 2),
            f"Temporal baseline drift of {worst_drift:.1f}% exceeds {max_drift_pct:.1f}% threshold "
            f"(gpm drift={gpm_drift_pct:.1f}%, p99 drift={p99_drift_pct:.1f}%).",
        )
    return False, round(worst_drift, 2), "Baseline stationary within drift bounds."


class RegressionGatekeeper:
    """Evaluates A/B/A/B experimental trial blocks against the openMAX lexicographic objective."""

    def __init__(
        self, max_p99_regression_pct=10.0, min_goodput_gain_pct=5.0,
        max_p95_regression_pct=10.0, max_fairness_drop_pct=5.0,
        max_worst_peer_drop_pct=15.0, max_loss_pct=10.0, max_drift_pct=25.0,
        alpha=0.05, num_hypotheses_tested=1, min_blocks_for_keep=4,
        min_blocks_for_promote=6, *, objective="LATENCY_WITH_CAPACITY_NONINFERIORITY",
        max_capacity_loss_pct=2.0, min_latency_gain_pct=5.0,
        min_loss_reduction_pp=0.5, evidence_root=None,
    ):
        if objective not in OBJECTIVES:
            raise ValueError("Select a declared objective before acquisition")
        for name,value in locals().copy().items():
            if name.endswith('_pct') or name=='min_loss_reduction_pp':
                _number(value,name,maximum=100)
        compute_adjusted_alpha(alpha,num_hypotheses_tested)
        if type(min_blocks_for_keep) is not int or min_blocks_for_keep<4:
            raise ValueError('strict evaluation requires at least4 paired blocks')
        if type(min_blocks_for_promote) is not int or min_blocks_for_promote<6:
            raise ValueError('replication requires at least6 paired blocks')
        self.max_p99_regress=max_p99_regression_pct
        self.min_goodput_gain=min_goodput_gain_pct
        self.max_p95_regress=max_p95_regression_pct
        self.max_fairness_drop=max_fairness_drop_pct
        self.max_worst_peer_drop=max_worst_peer_drop_pct
        self.max_loss_pct=max_loss_pct;self.max_drift_pct=max_drift_pct
        self.alpha=alpha;self.num_hypotheses_tested=num_hypotheses_tested
        self.min_blocks_for_keep=min_blocks_for_keep;self.min_blocks_for_promote=min_blocks_for_promote
        self.objective=objective;self.max_capacity_loss_pct=max_capacity_loss_pct
        self.min_latency_gain_pct=min_latency_gain_pct;self.min_loss_reduction_pp=min_loss_reduction_pp
        self.evidence_root=Path(evidence_root or Path(__file__).resolve().parents[2])

    @property
    def frozen_contract(self):
        return dict(objective=self.objective, alpha=self.alpha,
                    num_hypotheses_tested=self.num_hypotheses_tested,
                    max_p99_regression_pct=self.max_p99_regress,
                    min_goodput_gain_pct=self.min_goodput_gain,
                    max_p95_regression_pct=self.max_p95_regress,
                    max_fairness_drop_pct=self.max_fairness_drop,
                    max_worst_peer_drop_pct=self.max_worst_peer_drop,
                    max_loss_pct=self.max_loss_pct,max_drift_pct=self.max_drift_pct,
                    min_blocks_for_keep=self.min_blocks_for_keep,
                    min_blocks_for_promote=self.min_blocks_for_promote,
                    max_capacity_loss_pct=self.max_capacity_loss_pct,
                    min_latency_gain_pct=self.min_latency_gain_pct,
                    min_loss_reduction_pp=self.min_loss_reduction_pp)

    def evaluate_paired(self,runs,holdout_replicated=False,*,discovery_runs=None,
                        replication_receipt_path=None,candidate_fingerprint=None):
        """Canonical strict evaluator. A boolean is never replication evidence."""
        return self._evaluate_core(list(runs),holdout_replicated,discovery_runs,
                                   replication_receipt_path,candidate_fingerprint)

    def evaluate(self,runs,use_four_state_verdicts=True,holdout_replicated=False,**evidence):
        """Compatibility entrypoint using exactly the same strict paired decision.

        The old flag remains accepted for callers, but cannot restore Welch/KEEP.
        """
        return self.evaluate_paired(runs,holdout_replicated=holdout_replicated,**evidence)

    def _evaluate_core(self,runs,holdout_replicated,discovery_runs,
                       replication_receipt_path,candidate_fingerprint):
        adjusted_alpha=compute_adjusted_alpha(self.alpha,self.num_hypotheses_tested)
        values=dict(p99_delta_pct=0.0,goodput_delta_pct=0.0,p_value=1.0,
                    adjusted_alpha=adjusted_alpha,objective=self.objective)
        def decision(verdict,reason,*,state=None,eligible=False):
            result=GateDecision(verdict=verdict,promotion_stage=verdict,
                                rationale=reason,summary=verdict+': '+reason,**values)
            result.evidence_state=state;result.promotion_eligible=eligible
            return result
        for run in runs:run.__post_init__()
        a=[r for r in runs if r.arm=='A' and not r.is_sentinel]
        b=[r for r in runs if r.arm=='B' and not r.is_sentinel]
        for run in b:
            if run.firmware_resets:
                return decision('REJECT','Firmware instability: candidate firmware reset')
            if run.loss_pct>self.max_loss_pct:
                return decision('REJECT','Excessive packet loss in candidate')
        if any(r.firmware_resets or r.loss_pct>self.max_loss_pct for r in runs if r.arm=='A'):
            return decision('INCONCLUSIVE','Invalid baseline health/loss')
        if len(a)<2 or len(b)<2:
            return decision('INCONCLUSIVE','Insufficient complete paired blocks')
        try:pairs=build_paired_blocks(runs)
        except ValueError as exc:return decision('INCONCLUSIVE','Invalid paired observations: '+str(exc))
        n=len(pairs)
        values['paired_blocks_count']=n
        drift,drift_pct,message=detect_baseline_drift(runs,self.max_drift_pct)
        values.update(drift_detected=drift,drift_pct=drift_pct)
        if drift:return decision('INCONCLUSIVE',message)
        if any(r.goodput_mbps<=0 or r.p99_lat_ms<=0 for r in a):
            return decision('INCONCLUSIVE','Zero baseline rate/latency cannot establish relative improvement')
        if any(r.worst_peer_goodput_mbps is None for r in a+b):
            return decision('INCONCLUSIVE','Worst-peer service observation is missing')
        def mean(items):return sum(items)/len(items)
        gp=[p.goodput_per_mhz_delta_pct for p in pairs]
        p99=[p.p99_delta_pct for p in pairs];p95=[p.p95_delta_pct for p in pairs]
        fair=[p.fairness_delta_pct for p in pairs];worst=[p.worst_peer_delta_pct for p in pairs]
        gp_delta=mean(gp);p99_delta=mean(p99);p95_delta=mean(p95)
        values.update(goodput_delta_pct=mean([p.goodput_mbps_delta_pct for p in pairs]),
                      goodput_per_mhz_delta_pct=gp_delta,p99_delta_pct=p99_delta,
                      p95_delta_pct=p95_delta,fairness_delta_pct=mean(fair))
        if p99_delta>self.max_p99_regress:return decision('REJECT','Bufferbloat p99 regression')
        if p95_delta>self.max_p95_regress:return decision('REJECT','p95 latency regression')
        if mean(fair)<-self.max_fairness_drop or mean(worst)<-self.max_worst_peer_drop:
            return decision('REJECT','Fairness or worst-peer service regression')
        if n<self.min_blocks_for_keep:return decision('INCONCLUSIVE','Insufficient paired blocks; N=2 never approves')
        ci_gp=paired_bootstrap_ci_95(gp);ci_p99=paired_bootstrap_ci_95(p99)
        values.update(ci_95_goodput_per_mhz_delta_pct=ci_gp,ci_95_p99_delta_pct=ci_p99)
        if self.objective=='CAPACITY_WITH_QOE_CONSTRAINTS':
            if gp_delta<self.min_goodput_gain:return decision('REJECT','Insufficient throughput gain for capacity objective')
            primary=gp;ci_primary=ci_gp;effect_supported=ci_primary[0]>0
        elif self.objective=='LATENCY_WITH_CAPACITY_NONINFERIORITY':
            if p99_delta>-self.min_latency_gain_pct:return decision('REJECT','Insufficient p99 improvement for latency objective')
            if ci_gp[0]<-self.max_capacity_loss_pct:
                return decision('INCONCLUSIVE','Capacity non-inferiority interval not established')
            primary=p99;ci_primary=ci_p99;effect_supported=ci_primary[1]<0
        elif self.objective=='ROBUSTNESS':
            primary=[p.run_b.loss_pct-p.run_a.loss_pct for p in pairs]
            ci_primary=paired_bootstrap_ci_95(primary);effect_supported=ci_primary[1]<0
            if mean(primary)>-self.min_loss_reduction_pp:
                return decision('REJECT','Insufficient loss reduction for robustness objective')
            if ci_gp[0]<-self.max_capacity_loss_pct:
                return decision('INCONCLUSIVE','Robustness capacity non-inferiority not established')
        else:
            return decision('INCONCLUSIVE','Capability discovery needs its separate capability witness gate')
        # Endpoint non-inferiority uses declared intervals, not only favorable means.
        if (ci_p99[1]>self.max_p99_regress or paired_bootstrap_ci_95(p95)[1]>self.max_p95_regress
                or paired_bootstrap_ci_95(fair)[0]<-self.max_fairness_drop
                or paired_bootstrap_ci_95(worst)[0]<-self.max_worst_peer_drop):
            return decision('INCONCLUSIVE','QoE/fairness non-inferiority interval not established')
        nonzero=sum(abs(d)>1e-12 for d in primary)
        exact_floor=min(1.0,2.0**(1-nonzero))
        if exact_floor>adjusted_alpha:
            return decision('INCONCLUSIVE',f'Inferential resolution unattainable: min_p={exact_floor:g}, alpha={adjusted_alpha:g}; acquire more pairs')
        permutations=min(200000,max(4096,math.ceil(10/adjusted_alpha)))
        probability=paired_sign_flip_p_value(primary,n_permutations=permutations)
        values.update(p_value=probability,paired_permutation_p_value=probability)
        if probability>adjusted_alpha or not effect_supported:
            return decision('INCONCLUSIVE','Paired inference/interval not significant under frozen single-step Sidak family')
        if all(r.evidence_state=='SYNTHETIC' for r in runs):
            return decision('SYNTHETIC_PASS','Numerical fixture passes; not physical evidence',state='SYNTHETIC')
        provenance=validate_run_provenance(runs,self.evidence_root)
        if provenance:return decision('INCONCLUSIVE','Physical source evidence unavailable or invalid: '+'; '.join(provenance))
        if replication_receipt_path is None:
            if holdout_replicated:
                return decision('INCONCLUSIVE','holdout_replicated boolean lacks independent receipt authority')
            return decision('KEEP_FOR_REPLICATION','Valid discovery needs an independent frozen holdout receipt',state='BENCH_EXECUTED')
        if n<self.min_blocks_for_promote:
            return decision('INCONCLUSIVE','Insufficient holdout paired blocks')
        discovery_decision=self.evaluate_paired(list(discovery_runs or []),
                                                candidate_fingerprint=candidate_fingerprint)
        if discovery_decision.verdict!='KEEP_FOR_REPLICATION':
            return decision('INCONCLUSIVE','Discovery did not pass the same frozen health/statistical contract: '+discovery_decision.rationale)
        proof=validate_holdout_evidence(list(discovery_runs or []),runs,candidate_fingerprint,
                                      self.evidence_root,replication_receipt_path,contract=self.frozen_contract)
        if proof:return decision('INCONCLUSIVE','Independent holdout proof failed: '+'; '.join(proof))
        return decision('PROMOTE','Hash-bound independent holdout confirms the frozen objective; no device execution authorized',
                        state='BENCH_REPLICATED',eligible=True)


def run_aa_null_replay_validation(
    baseline_pool: List[RunMetrics],
    gatekeeper: Optional[RegressionGatekeeper] = None,
    pairs_per_trial: int = 6,
    num_trials: int = 300,
    seed: int = 20261024,
) -> Dict[str, Any]:
    """Replays baseline-only (A/A) logs under random A/B block assignment to measure false-positive rate."""
    if len(baseline_pool) < 4:
        raise ValueError("baseline_pool must contain at least 4 baseline RunMetrics samples for A/A replay.")

    gk = gatekeeper or RegressionGatekeeper()
    if type(num_trials) is not int or num_trials<=0 or type(pairs_per_trial) is not int or pairs_per_trial<4:
        raise ValueError('positive trials and at least4 pairs per replay required')
    rng = random.Random(seed)
    verdict_counts: Dict[str, int] = {
        "REJECT": 0,
        "INCONCLUSIVE": 0,
        "KEEP_FOR_REPLICATION": 0,
        "PROMOTE": 0,
    }

    for trial_idx in range(num_trials):
        trial_runs: List[RunMetrics] = []
        for block_idx in range(pairs_per_trial):
            sample_a = rng.choice(baseline_pool)
            sample_b = rng.choice(baseline_pool)
            trial_runs.append(
                RunMetrics(
                    run_id=f"aa_t{trial_idx}_b{block_idx}_A",
                    arm="A",
                    goodput_mbps=sample_a.goodput_mbps,
                    p95_lat_ms=sample_a.p95_lat_ms,
                    p99_lat_ms=sample_a.p99_lat_ms,
                    loss_pct=sample_a.loss_pct,
                    jain_fairness=sample_a.jain_fairness,
                    firmware_resets=0,
                    channel_width_mhz=sample_a.channel_width_mhz,
                    block_index=block_idx,
                    worst_peer_goodput_mbps=sample_a.worst_peer_goodput_mbps,
                    evidence_state='SYNTHETIC',
                )
            )
            trial_runs.append(
                RunMetrics(
                    run_id=f"aa_t{trial_idx}_b{block_idx}_B",
                    arm="B",
                    goodput_mbps=sample_b.goodput_mbps,
                    p95_lat_ms=sample_b.p95_lat_ms,
                    p99_lat_ms=sample_b.p99_lat_ms,
                    loss_pct=sample_b.loss_pct,
                    jain_fairness=sample_b.jain_fairness,
                    firmware_resets=0,
                    channel_width_mhz=sample_b.channel_width_mhz,
                    block_index=block_idx,
                    worst_peer_goodput_mbps=sample_b.worst_peer_goodput_mbps,
                    evidence_state='SYNTHETIC',
                )
            )
        decision = gk.evaluate_paired(trial_runs, holdout_replicated=True)
        verdict_counts[decision.verdict] = verdict_counts.get(decision.verdict, 0) + 1

    false_positives = (verdict_counts["KEEP_FOR_REPLICATION"] + verdict_counts["PROMOTE"]
                       + verdict_counts.get('SYNTHETIC_PASS',0))
    fp_rate = false_positives / float(num_trials)
    return {
        "num_trials": num_trials,
        "pairs_per_trial": pairs_per_trial,
        "verdict_counts": verdict_counts,
        "false_positives": false_positives,
        "false_positive_rate": round(fp_rate, 4),
        "target_alpha": gk.alpha,
        "passes_null_calibration": fp_rate <= gk.alpha,
        "evidence_state": "SYNTHETIC",
    }
