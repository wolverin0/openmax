"""Read frozen local measurements without importing or invoking bench code."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
from fractions import Fraction
import argparse
import hashlib
from importlib import metadata
import json
import math
from pathlib import Path
import platform
import re

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts/autoresearch/waves_abcd_20261024"
INPUTS = ARTIFACTS / "inputs"
EFGH_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_efgh_20261024"
EFGH_INPUTS = EFGH_ARTIFACTS / "inputs"
IJKL_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_ijkl_20261024"
IJKL_INPUTS = IJKL_ARTIFACTS / "inputs"
MNOP_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_mnop_20261024"
MNOP_INPUTS = MNOP_ARTIFACTS / "inputs"
R15_RECEIPT = MNOP_INPUTS / "lap120_loco195_r15_wpa2_asym_n40_20261024.json"
R14_NORMALIZED_SNAPSHOT = MNOP_INPUTS / "normalized_r1_to_r14_measurements_20261024.json"
QRST_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_qrst_20261024"
QRST_INPUTS = QRST_ARTIFACTS / "inputs"
R15_NORMALIZED_OUTPUT = MNOP_ARTIFACTS / "normalized_r1_to_r15_measurements_20261024.json"
R16_TO_R21_NAMES = (
    "lap120_loco195_r16_abba_n80_20261024.json",
    "lap120_loco195_r17_crypto_crossover_20261024.json",
    "lap120_loco195_r18_coverage_factorial_20261024.json",
    "lap120_loco195_r19_3tier_wmm_20261024.json",
    "lap120_loco195_r20_paced_ack_20261024.json",
    "lap120_loco195_r21_micro_paced_ack_20261024.json",
)
R16_TO_R21_RECEIPTS = tuple(QRST_INPUTS / name for name in R16_TO_R21_NAMES)
UVWX_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_uvwx_20261024"
UVWX_INPUTS = UVWX_ARTIFACTS / "inputs"
R21_NORMALIZED_OUTPUT = QRST_ARTIFACTS / "normalized_r1_to_r21_measurements_20261024.json"
R21_BLOCK_OUTPUT = QRST_ARTIFACTS / "normalized_r16_to_r21_block_observations_20261024.json"
R22_TO_R26_NAMES = (
    "lap120_loco195_r22_retry_ftx_20261024.json",
    "lap120_loco195_r23_ani_af_fql_20261024.json",
    "lap120_loco195_r24_factorial_af_fql_20261024.json",
    "lap120_loco195_r25_abba12_n120_20261024.json",
    "lap120_loco195_r26_ftx_retry_synthesis_20261024.json",
)
R22_TO_R26_RECEIPTS = tuple(UVWX_INPUTS / name for name in R22_TO_R26_NAMES)
YZAB_ARTIFACTS = ROOT / "artifacts/autoresearch/waves_yzab_20261024"
YZAB_INPUTS = YZAB_ARTIFACTS / "inputs"
R26_NORMALIZED_OUTPUT = UVWX_ARTIFACTS / "normalized_r1_to_r26_measurements_20261024.json"
R26_BLOCK_OUTPUT = UVWX_ARTIFACTS / "normalized_r16_to_r26_block_observations_20261024.json"
R27_TO_R32_NAMES = (
    "lap120_loco195_r27_certified_wds_crossover_20261024.json",
    "lap120_loco195_r28_abba12_certified_wds_20261024.json",
    "lap120_loco195_r29_abba14_holm324_wds_20261024.json",
    "lap120_loco195_r30_2flow_bidir_certified_wds_20261024.json",
    "lap120_loco195_r31_unidir_dl_2flow_certified_wds_20261024.json",
    "lap120_loco195_r32_abba16_holm500_wds_20261024.json",
)
R27_TO_R32_RECEIPTS = tuple(YZAB_INPUTS / name for name in R27_TO_R32_NAMES)
ACAF_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_ac_to_af_20261024'
ACAF_INPUTS = ACAF_ARTIFACTS / 'inputs'
R32_NORMALIZED_OUTPUT = YZAB_ARTIFACTS / 'normalized_r1_to_r32_measurements_20261024.json'
R32_BLOCK_OUTPUT = YZAB_ARTIFACTS / 'normalized_r16_to_r32_block_observations_20261024.json'
R33_TO_R42_NAMES = (
    'lap120_loco195_r33_covclass6_3km_certified_wds_20261024.json',
    'lap120_loco195_r34_covclass6_af3_synthesis_certified_wds_20261024.json',
    'lap120_loco195_r35_covclass13_6km_certified_wds_20261024.json',
    'lap120_loco195_r36_12flow_heavy_bidir_certified_wds_20261024.json',
    'lap120_loco195_r37_8flow_heavy_bidir_certified_wds_20261024.json',
    'lap120_loco195_r38_8flow_af3_synthesis_certified_wds_20261024.json',
    'lap120_loco195_r39_unidir_ul_2flow_certified_wds_20261024.json',
    'lap120_loco195_r40_abba16_all4_exact_holm500_wds_20261024.json',
    'lap120_loco195_r41_abba16_retry53_all4_exact_holm500_wds_20261024.json',
    'lap120_loco195_r42_abba16_retry74_all4_exact_zero_loss_holm500_wds_20261024.json',
)
R33_TO_R42_RECEIPTS = tuple(ACAF_INPUTS / name for name in R33_TO_R42_NAMES)
AGAJ_ARTIFACTS = ROOT / 'artifacts/autoresearch/waves_ag_to_aj_20261024'
AGAJ_INPUTS = AGAJ_ARTIFACTS / 'inputs'
R42_NORMALIZED_OUTPUT = ACAF_ARTIFACTS / 'normalized_r1_to_r42_measurements_20261024.json'
R42_BLOCK_OUTPUT = ACAF_ARTIFACTS / 'normalized_r16_to_r42_block_observations_20261024.json'
# This additive catalog is intentionally limited to the newly authorized rounds.
ROUND_SPECS = {
    43: ('lap120_loco195_r43_unidir_dl_2flow_abba16_all4_exact_holm500_wds_20261024.json', 'unidir_dl_2flow', 2, False),
    44: ('lap120_loco195_r44_unidir_dl_2flow_symaf1_retry53_abba16_dyadic_wds_20261024.json', 'unidir_dl_2flow', 2, False),
    45: ('lap120_loco195_r45_bidir_6flow_retry74_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_6flow', 6, True),
    46: ('lap120_loco195_r46_unidir_ul_2flow_abba16_dyadic_zero_loss_wds_20261024.json', 'unidir_ul_2flow', 2, False),
    47: ('lap120_loco195_r47_bidir_8flow_af3_abba16_dyadic_zero_loss_wds_20261024.json', 'bidir_8flow', 8, True),
}
R43_TO_R47_RECEIPTS = tuple(AGAJ_INPUTS / spec[0] for spec in ROUND_SPECS.values())
LOWER_MAC_BOUNDS = {
    'short_retry_limit': (0, 255), 'long_retry_limit': (0, 255),
    'force_tx_status': (0, 1), 'ani_enable': (0, 1),
    'airtime_flags': (0, 3), 'fq_limit': (1, 2**32 - 1),
}
ALL_ROUND_NAMES = (
    "lap120_loco195_live_autoresearch_20261024.json",
    "lap120_loco195_r2_factorial_20261024.json",
    "lap120_loco195_r3_catalog_20261024.json",
    "lap120_loco195_r4_subquantum_20261024.json",
    "lap120_loco195_r5_bidir_20261024.json",
    "lap120_loco195_r6_nsga3_refinement_20261024.json",
    "lap120_loco195_r7_multiflow_shootout_20261024.json",
    "lap120_loco195_r8_per_ac_6flow_20261024.json",
    "lap120_loco195_r9_per_ac_dscp_20261024.json",
)
ALL_ROUND_RECEIPTS = tuple(EFGH_INPUTS / name for name in ALL_ROUND_NAMES)
ALL14_ROUND_NAMES = ALL_ROUND_NAMES + (
    "lap120_loco195_r10_aqm_codel_20261024.json",
    "lap120_loco195_r11_tcp_stack_regime_20261024.json",
    "lap120_loco195_r12_high_power_n40_20261024.json",
    "lap120_loco195_r13_coverage_distance_20261024.json",
    "lap120_3cpe_ptmp_r14_20261024.json",
)
ALL14_ROUND_RECEIPTS = tuple(IJKL_INPUTS / name for name in ALL14_ROUND_NAMES)
AC_ORDER = ("VO", "VI", "BE", "BK")
REGIMES = ("bulk_unidirectional", "bidir_2flow", "bidir_6flow")
DEFAULT_RECEIPTS = (
    INPUTS / "lap120_loco195_live_autoresearch_20261024.json",
    INPUTS / "lap120_loco195_r2_factorial_20261024.json",
)
KNOB_FIELDS = (
    "aql_low_us", "aql_high_us", "aql_threshold_us", "ct_rc_per_thresh",
    "ct_baseband_rifs", "fq_quantum_bytes", "htt_max_amsdu", "htt_max_ampdu",
)


def finite_number(value, name, low=None, high=None):
    try:
        valid = type(value) in {int, float} and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{name} must be a finite number")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} outside [{low}, {high}]")
    return value


def local_json(path):
    path = Path(path)
    if "://" in str(path) or str(path).startswith(("\\\\", "//")):
        raise ValueError("Only local files are accepted")
    if not path.is_file() or path.stat().st_size > 10_000_000:
        raise ValueError("Missing or oversized local input")
    def reject(value):
        raise ValueError(f"Non-finite JSON: {value}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject,
                      parse_float=lambda value: finite_number(float(value), "JSON number"))


def write_json(path, value):
    path = Path(path)
    # An offline output is a local ordinary file, never a device/UNC destination.
    if "://" in str(path) or str(path).startswith(("\\\\", "//")):
        raise ValueError("Only local outputs are accepted")
    resolved = path.resolve()
    simulation_output=(ROOT/'artifacts/autoresearch/simpy_ptmp_predictions_20261024.json').resolve()
    in_owned_outputs=any(resolved.is_relative_to(folder.resolve()) and not resolved.is_relative_to(frozen.resolve())
                         for folder,frozen in ((ARTIFACTS,INPUTS),(EFGH_ARTIFACTS,EFGH_INPUTS),
                                               (IJKL_ARTIFACTS,IJKL_INPUTS),
                                               (MNOP_ARTIFACTS,MNOP_INPUTS),
                                               (QRST_ARTIFACTS,QRST_INPUTS),
                                               (UVWX_ARTIFACTS,UVWX_INPUTS),
                                               (YZAB_ARTIFACTS,YZAB_INPUTS),
                                               (ACAF_ARTIFACTS,ACAF_INPUTS),
                                               (AGAJ_ARTIFACTS,AGAJ_INPUTS)))
    if not in_owned_outputs and resolved!=simulation_output:
        raise ValueError("Generated datasets must stay in owned wave outputs, never frozen inputs or live receipts")
    reserved={"CON","PRN","AUX","NUL",*(f"COM{i}" for i in range(1,10)),*(f"LPT{i}" for i in range(1,10))}
    if any(part.split('.')[0].upper() in reserved or ':' in part for part in resolved.parts[1:]):
        raise ValueError("Device paths and alternate data streams are forbidden")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def software_versions():
    versions = {"python": platform.python_version()}
    for package in ("numpy", "scipy", "pymoo", "simpy"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return versions


@dataclass(frozen=True)
class Measurement:
    round_id: str
    iteration: str
    knobs: tuple[int, ...]
    goodputs_mbps: tuple[float, ...]
    rtts_ms: tuple[float, ...]
    goodput_mbps: float
    p50_ms: float
    p95_ms: float
    p99_ms: float
    packet_loss_pct: float
    retransmits: int | None
    flags: tuple[str, ...]

    @property
    def policy_key(self):
        return self.knobs

    def knob_dict(self):
        return dict(zip(KNOB_FIELDS, self.knobs))


def load_measurements(paths=DEFAULT_RECEIPTS):
    records, provenance = [], []
    for round_number, path in enumerate(paths, 1):
        path = Path(path)
        payload = local_json(path)
        provenance.append(dict(path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                               sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                               experiment_id=payload["experiment_id"], timestamp_utc=payload.get("timestamp_utc")))
        iterations = payload.get("iterations")
        if not isinstance(iterations, list) or not 1 <= len(iterations) <= 1000:
            raise ValueError("Bounded nonempty iterations required")
        seen = set()
        for iteration in iterations:
            name = iteration["commit"]
            if name in seen:
                raise ValueError("Duplicate iteration identity")
            seen.add(name)
            settings = iteration["candidate_knobs"]
            knobs = tuple(settings[field] for field in KNOB_FIELDS)
            if any(type(value) is not int for value in knobs):
                raise ValueError("Knob values must be exact integers")
            low, high, threshold, rc, rifs, quantum, amsdu, ampdu = knobs
            if not (0 < low <= high <= 1_000_000 and 0 < threshold <= 2_000_000
                    and 0 <= rc <= 256 and rifs in {0, 1} and 0 < quantum <= 65536
                    and 1 <= amsdu <= 31 and 1 <= ampdu <= 64):
                raise ValueError("Malformed recorded knob tuple")
            obs = iteration["observation"]
            gp = tuple(finite_number(x, "receiver repetition", 0, 10000)
                       for x in iteration.get("goodputs_per_rep", []))
            rtt = tuple(finite_number(x, "RTT sample", 0, 1_000_000)
                        for x in iteration.get("rtts_ms", []))
            if not gp or len(gp) > 10000 or len(rtt) > 100000:
                raise ValueError("Missing or unbounded repetition arrays")
            goodput = finite_number(obs["goodput_rx_mbps"], "goodput", 0, 10000)
            if not math.isclose(float(np.mean(gp)), goodput, abs_tol=0.001):
                raise ValueError("Aggregate goodput disagrees with receiver repetitions")
            p50, p95, p99 = (finite_number(obs[key], key, 0, 1_000_000)
                             for key in ("p50_rtt_ms", "p95_rtt_ms", "p99_rtt_ms"))
            if not p50 <= p95 <= p99:
                raise ValueError("Nonmonotone recorded quantiles")
            if obs.get("repetitions") != len(gp):
                raise ValueError("Reported repetition count disagrees with samples")
            flags = ["single_link_no_independent_sector_replication", "sequential_adaptive_order",
                     "ct_help_not_effective_readback", "restoration_flag_not_independent_CT_proof",
                     "RTT_samples_not_independent_experimental_units", "retry_rate_is_TCP_proxy"]
            if len(rtt) < 100:
                flags.append("tail_quantiles_sparse")
            records.append(Measurement(f"R{round_number}", name, knobs, gp, rtt, goodput,
                                       p50, p95, p99, finite_number(obs["packet_loss_pct"], "loss", 0, 100),
                                       iteration.get("retransmits"), tuple(flags)))
    return records, provenance


def descriptive_dataset(records, provenance):
    return dict(schema_version=1, evidence="reported_physical_measurements_not_independently_reacquired",
                automatic_execution_allowed=False, source_refs=provenance,
                experimental_unit="link/time-window; within-window pings are subsamples",
                records=[asdict(row) for row in records])


def policy_features(knobs):
    """Fixed engineering scales, not learned from held-out target outcomes."""
    low, high, threshold, rc, rifs, quantum, amsdu, ampdu = knobs
    return np.array([low/5000, high/12000, threshold/24000, rc/50, rifs,
                     quantum/1514, amsdu/3, ampdu/64], dtype=float)


def training_arrays(records):
    if len(records) < 3:
        raise ValueError("At least three treatment windows are needed")
    x = np.array([policy_features(row.knobs) for row in records])
    y = np.array([[row.goodput_mbps, row.p95_ms, row.p99_ms] for row in records])
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Finite training arrays required")
    return x, y


def exact_integer(value, name, low=0, high=1_000_000):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


@dataclass(frozen=True)
class EndpointPolicy:
    """A declared treatment, with omitted baseline controls retained as unknown.

    Encoding/model bounds here are not hardware-approved ranges. AC order is
    always VO, VI, BE, BK; a DSCP flag does not prove effective TID/AC mapping.
    """
    aql_by_ac: tuple[tuple[int, int], ...]
    aql_threshold_us: int
    fq_quantum_bytes: int
    rc_per_thresh: int
    rts_threshold: int | None = None
    ct_baseband_rifs: int | None = None
    ct_pshack: int | None = None
    htt_max_amsdu: int | None = None
    htt_max_ampdu: int | None = None
    dscp_micro_vo_steering: bool = False

    def __post_init__(self):
        if not isinstance(self.aql_by_ac, tuple) or len(self.aql_by_ac) != 4:
            raise ValueError("Require four immutable AQL pairs in VO/VI/BE/BK order")
        for ac,pair in zip(AC_ORDER,self.aql_by_ac):
            if not isinstance(pair,tuple) or len(pair)!=2:
                raise ValueError("Each AC requires a low/high pair")
            low,high=(exact_integer(v,ac+" AQL",1) for v in pair)
            if low>high:raise ValueError("AQL low exceeds high")
        exact_integer(self.aql_threshold_us,'threshold',1,2_000_000)
        exact_integer(self.fq_quantum_bytes,'quantum',1,65536)
        exact_integer(self.rc_per_thresh,'raw RC threshold',0,256)
        for name,low,high in [('rts_threshold',0,65535),('ct_baseband_rifs',0,1),
                              ('ct_pshack',0,255),('htt_max_amsdu',1,31),('htt_max_ampdu',1,64)]:
            value=getattr(self,name)
            if value is not None:exact_integer(value,name,low,high)
        if type(self.dscp_micro_vo_steering) is not bool:
            raise ValueError("DSCP treatment flag must be boolean")

    def as_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class RegimeMeasurement:
    round_id: str
    iteration: str
    workload_regime: str
    active_flow_count: int
    bidirectional: bool
    ap_policy: EndpointPolicy
    cpe_policy: EndpointPolicy | None
    goodput_mbps: float
    dl_goodput_mbps: float | None
    ul_goodput_mbps: float | None
    goodputs_mbps: tuple[float,...]
    repetitions_reported: int
    rtts_ms: tuple[float,...]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    packet_loss_pct: float
    jain_fairness: float
    mac_retry_rate: float | None
    reported_retry_rate: float
    retransmits: int | None
    mac_tx_packets: int | None
    mac_tx_retries: int | None
    restoration_verified: bool
    station_drops: int
    flags: tuple[str,...]

    @property
    def policy_key(self):
        # Workload is deliberately NOT part of this key: a held-out joint policy
        # must disappear across every round/regime in a transfer assessment.
        return json.dumps([asdict(self.ap_policy),asdict(self.cpe_policy) if self.cpe_policy else None],
                          sort_keys=True,separators=(',',':'))


def _rts(value):
    if value in (None,'off'):
        return None
    if type(value) is str and re.fullmatch(r'\d{1,5}',value):value=int(value)
    return exact_integer(value,'RTS recorded threshold',0,65535)


def _endpoint(settings, round_number, endpoint):
    if round_number==15:
        # R15's endpoints are intentionally different; never collapse to AP.
        settings=settings[endpoint+'_state']
    if round_number <= 4:
        if endpoint=='cpe':return None  # AP-only recipe; CPE baseline not captured.
        pairs=((settings['aql_low_us'],settings['aql_high_us']),)*4
        threshold,quantum,rc=(settings[k] for k in ('aql_threshold_us','fq_quantum_bytes','ct_rc_per_thresh'))
        rts=settings.get('rts_threshold')
    elif round_number <= 7:
        prefix=endpoint+'_'
        pairs=((settings[prefix+'aql_low_us'],settings[prefix+'aql_high_us']),)*4
        threshold,quantum,rc=(settings[prefix+k] for k in ('aql_threshold_us','fq_quantum_bytes','rc_per_thresh'))
        rts=settings.get(prefix+'rts')
    else:
        pairs=tuple((settings[ac.lower()+'_low_us'],settings[ac.lower()+'_high_us']) for ac in AC_ORDER)
        threshold,quantum,rc=(settings[k] for k in ('aql_threshold_us','fq_quantum_bytes','rc_per_thresh'))
        rts=None
    dscp=settings.get('dscp_micro_vo_steering',0)
    exact_integer(dscp,'DSCP treatment flag',0,1)
    return EndpointPolicy(pairs,threshold,quantum,rc,_rts(rts),
                          settings.get('ct_baseband_rifs'),settings.get('ct_pshack'),
                          settings.get('htt_max_amsdu'),settings.get('htt_max_ampdu'),bool(dscp))


def load_all_measurements(paths=ALL_ROUND_RECEIPTS):
    """Normalize R1..R9 without importing acquisition code or fabricating samples.

    Custom local subsets are supported; round identity comes from experiment_id,
    never the caller's path ordering. The default corpus is the nine frozen files.
    """
    return _load_primary_measurements(paths, max_round=9)


def _load_primary_measurements(paths, *, max_round):
    paths=tuple(paths)
    if not 1<=len(paths)<=max_round:raise ValueError(f'Require1..{max_round} round receipts')
    records,provenance,seen_rounds=[],[],set()
    for path in paths:
        path=Path(path); payload=local_json(path)
        if not isinstance(payload,dict) or not isinstance(payload.get('experiment_id'),str):
            raise ValueError('A named round receipt object is required')
        match=re.fullmatch(r'FMX-AUTORESEARCH-LIVE-(\d{3})(?:-[A-Z0-9-]+)?',payload.get('experiment_id',''))
        if not match or not 1<=int(match[1])<=max_round:raise ValueError('Unrecognized round experiment identity')
        number=int(match[1]); round_id=f'R{number}'
        if round_id in seen_rounds:raise ValueError('Duplicate round identity')
        seen_rounds.add(round_id)
        provenance.append({'round_id':round_id,'path':path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                           'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'experiment_id':payload['experiment_id'],
                           'timestamp_utc':payload.get('timestamp_utc')})
        iterations=payload.get('iterations')
        if not isinstance(iterations,list) or not 1<=len(iterations)<=1000:raise ValueError('Bounded nonempty windows required')
        seen=set()
        for item in iterations:
            if not isinstance(item,dict):raise ValueError('Window object required')
            name=item.get('commit')
            if not isinstance(name,str) or not name or name in seen:raise ValueError('Duplicate or invalid window identity')
            seen.add(name); settings=item.get('candidate_knobs'); obs=item.get('observation')
            if not isinstance(settings,dict) or not isinstance(obs,dict):raise ValueError('Recorded policy/observation objects required')
            if number==15:
                required={'ap_state','cpe_state'}
                if any(not isinstance(settings.get(end+'_state'),dict) for end in ('ap','cpe')):
                    raise ValueError('R15 requires separate AP/CPE state objects')
            elif number<=4:
                required={'aql_low_us','aql_high_us','aql_threshold_us','fq_quantum_bytes','ct_rc_per_thresh'}
            elif number<=7:
                required={end+'_'+key for end in ('ap','cpe') for key in
                          ('aql_low_us','aql_high_us','aql_threshold_us','fq_quantum_bytes','rc_per_thresh')}
            else:
                required={ac.lower()+'_'+side+'_us' for ac in AC_ORDER for side in ('low','high')} | {
                    'aql_threshold_us','fq_quantum_bytes','rc_per_thresh'}
            if not required<=settings.keys():raise ValueError('Recorded policy fields missing')
            observation_keys={'repetitions','goodput_rx_mbps','p50_rtt_ms','p95_rtt_ms','p99_rtt_ms',
                              'packet_loss_pct','jain_fairness','retry_rate','restoration_verified','station_drops'}
            if not observation_keys<=obs.keys():raise ValueError('Observation fields missing')
            ap,cpe=(_endpoint(settings,number,end) for end in ('ap','cpe'))
            gp_raw,rtt_raw=item.get('goodputs_per_rep',[]),item.get('rtts_ms',[])
            if not isinstance(gp_raw,list) or not isinstance(rtt_raw,list) or len(gp_raw)>10000 or not (0 if number==14 else 1)<=len(rtt_raw)<=100000:
                raise ValueError('Missing or unbounded sample arrays')
            gp=tuple(finite_number(v,'receiver repetition',0,10000) for v in gp_raw)
            rtts=tuple(finite_number(v,'RTT sample',0,1_000_000) for v in rtt_raw)
            rep=exact_integer(obs['repetitions'],'reported repetitions',1,10000)
            goodput=finite_number(obs['goodput_rx_mbps'],'receiver goodput',0,10000)
            if gp and (len(gp)!=rep or not math.isclose(float(np.mean(gp)),goodput,abs_tol=.001)):
                raise ValueError('Receiver repetition count or mean disagrees')
            if number<=4 and not gp:raise ValueError('Unidirectional receiver repetitions missing')
            if 'rtt_sample_count' in item:
                count=exact_integer(item['rtt_sample_count'],'RTT count',0,100000)
                if rtts and count!=len(rtts):raise ValueError('RTT sample count disagrees')
            quantiles=tuple(finite_number(obs[k],k,0,1_000_000) for k in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms'))
            if not quantiles[0]<=quantiles[1]<=quantiles[2]:raise ValueError('Nonmonotone quantiles')
            # Receipts store RTT arrays rounded to0.01ms after computing quantiles.
            # Keep recorded values; never replace them to make a model look better.
            delta=np.asarray(quantiles)-np.percentile(rtts,[50,95,99]) if rtts else np.zeros(3)
            if np.max(np.abs(delta))>.0101:raise ValueError('Recorded quantiles disagree beyond stored RTT precision')
            flags=['single_link_sequential_adaptive_windows','reported_restoration_not_independent_acceptance',
                   'sparse_RTT_tail_estimates','declared_policy_not_effective_firmware_readback']
            if not rtts:flags.append('raw_RTT_samples_absent_summary_quantiles_only')
            if number<=4:flags.append('CPE_baseline_policy_not_recorded_AP_only_treatment')
            else:flags.append('raw_directional_per_repetition_samples_not_retained')
            if np.max(np.abs(delta))>.001:flags.append('RTT_array_quantization_difference_retained')
            dl=ul=None
            if number>=5:
                dl=finite_number(item['dl_goodput_mbps'],'DL goodput',0,10000)
                ul=finite_number(item['ul_goodput_mbps'],'UL goodput',0,10000)
                total=finite_number(item['total_bidir_goodput_mbps'],'bidir goodput',0,10000)
                if not math.isclose(total,goodput,abs_tol=.011) or not math.isclose(dl+ul,total,abs_tol=.021):
                    raise ValueError('Rounded directional means disagree with aggregate')
                if abs(total-goodput)>.001:flags.append('aggregate_goodput_serialization_rounding_retained')
                flags.append('DL_UL_means_rounded_not_repetitions')
            loss=finite_number(obs['packet_loss_pct'],'packet loss percent',0,100)
            fairness=finite_number(obs['jain_fairness'],'reported fairness',0,1)
            reported_retry=finite_number(obs['retry_rate'],'reported retry metric',0,100)
            packets=retries=mac=None
            if 'mac_tx_packets_delta' in item or 'mac_tx_retries_delta' in item:
                packets=exact_integer(item['mac_tx_packets_delta'],'MAC TX packets',1,10**12)
                retries=exact_integer(item['mac_tx_retries_delta'],'MAC retries',0,10**12)
                mac=finite_number(item['mac_retry_rate'],'MAC retry events per TX packet',0,100)
                if abs(mac-retries/packets)>.000051:raise ValueError('MAC retry fraction disagrees with counters')
                flags.append('MAC_retry_events_per_TX_packet_not_PER')
            else:flags.append('reported_retry_metric_is_TCP_proxy_not_MAC_PER')
            retrans=item.get('retransmits')
            if retrans is not None:exact_integer(retrans,'TCP retransmits',0,10**12)
            restoration=obs['restoration_verified']
            if type(restoration) is not bool:raise ValueError('Restoration must be a recorded boolean')
            drops=exact_integer(obs['station_drops'],'station drops',0,10**8)
            if loss or drops or not restoration:flags.append('not_eligible_for_controller_promotion')
            if number>=9:flags.append('DSCP_EF_to_AC_VO_mapping_not_independently_verified')
            regime=REGIMES[0 if number<=4 else 1 if number<=6 else 2]
            records.append(RegimeMeasurement(round_id,name,regime,2 if number<=6 else 6,number>=5,
                ap,cpe,goodput,dl,ul,gp,rep,rtts,*quantiles,loss,fairness,mac,reported_retry,
                retrans,packets,retries,restoration,drops,tuple(flags)))
    records.sort(key=lambda r:(int(r.round_id[1:]),r.iteration))
    provenance.sort(key=lambda r:int(r['round_id'][1:]))
    return records,provenance


def normalized_regime_dataset(records=None,provenance=None):
    if records is None:records,provenance=load_all_measurements()
    if not records or provenance is None:raise ValueError('Records and source provenance required')
    manifest=local_json(EFGH_ARTIFACTS/'inputs_manifest.json')
    return {'schema_version':2,'evidence':'reported_saved_physical_windows_not_reacquired',
            'automatic_execution_allowed':False,'physical_acceptance_claim':False,
            'software_versions':software_versions(),'source_refs':provenance,
            'recipe_refs':[item for item in manifest if item['kind']=='recipe'],'ac_order':list(AC_ORDER),
            'experimental_unit':'one link/treatment window; RTTs are subsamples, not independent replications',
            'workload_provenance':'Round recipes frozen in inputs/recipes;2DL R1-R4,1DL+1UL R5-R6,3DL+3UL R7-R9',
            'round_counts':{f'R{i}':sum(r.round_id==f'R{i}' for r in records) for i in range(1,10)},
            'regime_counts':{regime:sum(r.workload_regime==regime for r in records) for regime in REGIMES},
            'historical_checks':[{'question':'exact LTU2.4.0 D2 causal attribution',
                                  'status':'UNKNOWN_LOCAL_ARTIFACT_ABSENT','check_complete':True,
                                  'authority':'Operator E-H instruction: missing historical artifacts do not block'}],
            'records':[{**asdict(row),'policy_key':row.policy_key} for row in records]}


@dataclass(frozen=True)
class CrossLayerEndpointPolicy(EndpointPolicy):
    """Additive R1-R14 declaration; None means unrecorded, never a default.

    Distance denotes the programmed coverage/timing setting, not physical range.
    Encryption is annotated context, with its evidence on the measurement.
    """
    fq_target_us: int | None = None
    fq_interval_us: int | None = None
    tcp_limit_output_bytes: int | None = None
    tcp_notsent_lowat: int | None = None
    distance_meters: int | None = None
    encryption_mode: str | None = None

    def __post_init__(self):
        super().__post_init__()
        for name,low,high in (
            ('fq_target_us',1,10**8),('fq_interval_us',1,10**8),
            ('tcp_limit_output_bytes',1,2**32-1),('tcp_notsent_lowat',0,2**32-1),
            ('distance_meters',0,1_000_000),
        ):
            value=getattr(self,name)
            if value is not None:exact_integer(value,name,low,high)
        if self.fq_target_us is not None and self.fq_interval_us is not None:
            if self.fq_target_us>self.fq_interval_us:raise ValueError('CoDel target exceeds interval')
        if self.encryption_mode not in {None,'psk2','none'}:raise ValueError('Unknown encryption mode')


@dataclass(frozen=True)
class CrossLayerMeasurement(RegimeMeasurement):
    window_kind: str = 'primary'
    source_position: str = ''
    associated_cpes: tuple[str,...] = ()
    topology_evidence: str = 'UNKNOWN'
    encryption_mode: str | None = None
    encryption_evidence: str = 'UNKNOWN'
    distance_meters: int | None = None
    raw_rtt_sample_count_reported: int | None = None


def _cross_layer_policy(policy, settings, mode):
    if policy is None:return None
    values=asdict(policy)
    values.update({name:settings.get(name) for name in (
        'fq_target_us','fq_interval_us','tcp_limit_output_bytes','tcp_notsent_lowat','distance_meters')})
    values['encryption_mode']=mode
    return CrossLayerEndpointPolicy(**values)


def _encryption_context(number, payload):
    # R14's frozen recipe explicitly switches both endpoints to none. Its
    # precondition says WPA2-PSK and the receipt records WPA2 restoration.
    # Earlier rounds inherit an INFERRED baseline, never cipher readback proof.
    if number==14:
        return 'none','DECLARED_BY_FROZEN_RECIPE_NOT_EFFECTIVE_READBACK'
    return 'psk2','INFERRED_PRIOR_WPA2_CONTEXT_NOT_PER_WINDOW_READBACK'


def load_all14_measurements(paths=ALL14_ROUND_RECEIPTS, *, include_auxiliary=True):
    """83 primary + two R11 summary-only windows, with additive provenance.

    Existing R1-R9 APIs and their policy serialization remain unchanged. Missing
    local round artifacts complete an UNKNOWN check rather than gate this task.
    Summary-only windows retain missing quality/RTT fields and cannot be promoted.
    """
    paths=tuple(Path(path) for path in paths)
    if not 1<=len(paths)<=14:raise ValueError('Require1..14 local round paths')
    present=[]; missing=[]
    for path in paths:
        if '://' in str(path) or str(path).startswith(('\\\\','//')):raise ValueError('Only local files are accepted')
        if path.is_file():present.append(path)
        else:
            number=ALL14_ROUND_NAMES.index(path.name)+1 if path.name in ALL14_ROUND_NAMES else None
            missing.append(dict(round_id=f'R{number}' if number else None,path=str(path),
                status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',check_complete=True))
    if not present:return [],missing
    primary,refs=_load_primary_measurements(present,max_round=14)
    by_round={}
    for path in present:
        payload=local_json(path)
        number=int(re.fullmatch(r'FMX-AUTORESEARCH-LIVE-(\d{3})(?:-[A-Z0-9-]+)?',payload['experiment_id'])[1])
        by_round[f'R{number}']=(path,payload)
    records=[]
    for row in primary:
        number=int(row.round_id[1:]); path,payload=by_round[row.round_id]
        index,item=next((i,item) for i,item in enumerate(payload['iterations']) if item['commit']==row.iteration)
        mode,crypto_evidence=_encryption_context(number,payload)
        declared=item['candidate_knobs'].get('encryption_mode',mode)
        if declared not in {'psk2','none'} or declared!=mode:raise ValueError('Conflicting recorded encryption context')
        settings=item['candidate_knobs']
        if number==14:
            peers=payload.get('cpes_associated')
            if not isinstance(peers,dict) or any(not isinstance(key,str) or not key for key in peers):
                raise ValueError('R14 associated peer names required')
            associated=tuple(sorted(peers)); topology='RECEIPT_ASSOCIATED_PEERS_NOT_TITLE'
        else:
            associated=('Loco195',); topology='INFERRED_SINGLE_LINK_RECIPE_ENDPOINTS_NOT_ASSOCIATION_READBACK'
        values={name:getattr(row,name) for name in RegimeMeasurement.__dataclass_fields__}
        values.update(ap_policy=_cross_layer_policy(row.ap_policy,settings,mode),
            cpe_policy=_cross_layer_policy(row.cpe_policy,settings,mode),
            source_position=f'/iterations/{index}',associated_cpes=associated,
            topology_evidence=topology,encryption_mode=mode,encryption_evidence=crypto_evidence,
            distance_meters=settings.get('distance_meters'),
            raw_rtt_sample_count_reported=item.get('rtt_sample_count',len(row.rtts_ms)))
        flags=list(row.flags)+['encryption_context_not_per_window_cipher_readback']
        if number==12:flags+=['RTT_repetition_membership_and_pairing_not_retained','high_power_means_more_samples_not_RF_txpower']
        if number==13:flags.append('distance_is_declared_coverage_timing_not_physical_range')
        if number==14:
            flags+=['three_CPE_title_not_observed_topology','MAC_counters_sparse_measurement_scope_uncertain']
            stats=item.get('loco195_rtt_stats',{})
            if stats.get('count')!=values['raw_rtt_sample_count_reported']:
                raise ValueError('R14 peer and aggregate received RTT counts disagree')
            for key,expected in zip(('p50_ms','p95_ms','p99_ms'),(row.p50_ms,row.p95_ms,row.p99_ms)):
                if stats.get(key)!=expected:raise ValueError('R14 peer quantiles disagree')
        values['flags']=tuple(flags)
        records.append(CrossLayerMeasurement(**values))
    if include_auxiliary and 'R11' in by_round:
        _,payload=by_round['R11']; aux=payload.get('cross_regime_validation',{})
        if aux:
            winners=[row for row in records if row.round_id=='R11' and row.iteration==aux.get('incumbent_name')]
            if len(winners)!=1:raise ValueError('Auxiliary policy reference is missing or ambiguous')
            winner=winners[0]
            for name,regime,bidir in (('regime_b_2flow_bidir','bidir_2flow',True),
                                     ('regime_c_unidir_bulk','bulk_unidirectional',False)):
                item=aux.get(name)
                if not isinstance(item,dict):raise ValueError('Missing auxiliary summary')
                q=tuple(finite_number(item[key],key,0,1_000_000) for key in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms'))
                if not q[0]<=q[1]<=q[2]:raise ValueError('Auxiliary quantiles nonmonotone')
                g=finite_number(item['total_bidir_goodput_mbps' if bidir else 'goodput_rx_mbps'],'auxiliary goodput',0,10000)
                dl=finite_number(item['dl_goodput_mbps'],'DL',0,10000) if bidir else None
                ul=finite_number(item['ul_goodput_mbps'],'UL',0,10000) if bidir else None
                if bidir and not math.isclose(dl+ul,g,abs_tol=.021):raise ValueError('Auxiliary directional means disagree')
                values={key:getattr(winner,key) for key in CrossLayerMeasurement.__dataclass_fields__}
                values.update(iteration=f'R11_aux_{name}',window_kind='summary_validation',
                    source_position=f'/cross_regime_validation/{name}',workload_regime=regime,active_flow_count=2,
                    bidirectional=bidir,goodput_mbps=g,dl_goodput_mbps=dl,ul_goodput_mbps=ul,
                    goodputs_mbps=(),repetitions_reported=2,rtts_ms=(),p50_ms=q[0],p95_ms=q[1],p99_ms=q[2],
                    packet_loss_pct=None,jain_fairness=None,mac_retry_rate=finite_number(item['mac_retry_rate'],'MAC retry',0,100),
                    reported_retry_rate=None,retransmits=None,mac_tx_packets=None,mac_tx_retries=None,
                    restoration_verified=None,station_drops=None,raw_rtt_sample_count_reported=None,
                    flags=('summary_only_validation_missing_quality_and_raw_samples','not_eligible_for_controller_promotion',
                           'repetitions_from_frozen_recipe_not_retained_samples','encryption_context_not_per_window_cipher_readback'))
                records.append(CrossLayerMeasurement(**values))
    records.sort(key=lambda row:(int(row.round_id[1:]),row.window_kind,row.iteration))
    return records,sorted(refs+missing,key=lambda ref:int(ref['round_id'][1:]) if ref['round_id'] else 999)


def normalized_cross_layer_dataset(records=None,provenance=None):
    if records is None:records,provenance=load_all14_measurements()
    if provenance is None:raise ValueError('Source provenance required')
    manifest=local_json(IJKL_ARTIFACTS/'inputs_manifest.json')
    return dict(schema_version=3,evidence='reported_saved_windows_plus_summary_only_validation',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=software_versions(),
        ac_order=list(AC_ORDER),source_refs=provenance,recipe_refs=[row for row in manifest if row['kind']=='recipe'],
        experimental_unit='one sequential link/treatment window; pings are subsamples, no independent sector trials',
        encryption_context='R1-R13 psk2 INFERRED from prior WPA2 context; R14 none DECLARED by recipe; no per-window cipher readback',
        distance_semantics='programmed coverage/timing meters; actual physical separation UNKNOWN',
        round_counts={f'R{i}':sum(row.round_id==f'R{i}' for row in records) for i in range(1,15)},
        primary_window_count=sum(row.window_kind=='primary' for row in records),
        auxiliary_window_count=sum(row.window_kind=='summary_validation' for row in records),
        historical_checks=[dict(question='missing historical local evidence',status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',
            check_complete=True,authority='Operator I-L instruction: absence does not stall delivery')],
        records=[{**asdict(row),'policy_key':row.policy_key} for row in records])


def _verified_mnop_json(path):
    """Verify owned snapshots without reading their changing live originals."""
    path=Path(path)
    if path.resolve().is_relative_to(MNOP_INPUTS.resolve()):
        manifest=local_json(MNOP_ARTIFACTS/'inputs_manifest.json')
        matches=[row for row in manifest if (ROOT/row['path']).resolve()==path.resolve()]
        if len(matches)!=1:raise ValueError('Owned snapshot must have one manifest entry')
        if not path.is_file():return None
        if hashlib.sha256(path.read_bytes()).hexdigest()!=matches[0].get('sha256'):
            raise ValueError('Frozen MNOP snapshot checksum mismatch')
    return local_json(path)


def _measurement_from_normalized(item):
    values={name:item[name] for name in CrossLayerMeasurement.__dataclass_fields__}
    for end in ('ap_policy','cpe_policy'):
        if values[end] is not None:
            policy=dict(values[end]);policy['aql_by_ac']=tuple(tuple(pair) for pair in policy['aql_by_ac'])
            values[end]=CrossLayerEndpointPolicy(**policy)
    for name in ('goodputs_mbps','rtts_ms','flags','associated_cpes'):values[name]=tuple(values[name])
    row=CrossLayerMeasurement(**values)
    if row.policy_key!=item['policy_key']:raise ValueError('Prior normalized policy identity disagrees')
    return row


def load_all15_measurements(r15_path=R15_RECEIPT, *, base_dataset_path=R14_NORMALIZED_SNAPSHOT,
                            include_auxiliary=True):
    """Extend the frozen I-L output with actual R15 windows (85+4=89).

    The operator requested90 records, but both frozen R15 JSON and TSV contain
    four windows. Count evidence wins; no fifth record or trial is synthesized.
    Neither this API nor its default dependencies import acquisition recipes.
    """
    if type(include_auxiliary) is not bool:raise ValueError('Auxiliary selector must be boolean')
    base=_verified_mnop_json(base_dataset_path)
    if base is None:raise ValueError('Prior normalized base output required')
    if base.get('schema_version')!=3 or not isinstance(base.get('records'),list):
        raise ValueError('Expected the frozen I-L normalized schema3 output')
    try:records=[_measurement_from_normalized(item) for item in base['records']]
    except (KeyError,TypeError) as error:raise ValueError('Malformed prior normalized record') from error
    if any(not re.fullmatch(r'R(?:[1-9]|1[0-4])',row.round_id) for row in records):
        raise ValueError('Prior normalized corpus must contain only R1-R14')
    if len({(r.round_id,r.iteration) for r in records})!=len(records):raise ValueError('Duplicate prior window')
    refs=deepcopy(base['source_refs'])
    path=Path(r15_path)
    if not path.is_file():
        refs.append(dict(round_id='R15',path=str(path),status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',check_complete=True))
        return ([row for row in records if include_auxiliary or row.window_kind=='primary'],refs)
    payload=_verified_mnop_json(path)
    if payload.get('experiment_id')!='FMX-AUTORESEARCH-LIVE-015-WPA2-HIGH-POWER-ASYMMETRIC-UL':
        raise ValueError('Exact R15 experiment identity required')
    try:primary,source_refs=_load_primary_measurements([path],max_round=15)
    except (KeyError,TypeError) as error:raise ValueError('R15 endpoint/observation fields incomplete') from error
    if len(source_refs)!=1 or source_refs[0]['round_id']!='R15':raise ValueError('R15 source required')
    for row in primary:
        item=next(item for item in payload['iterations'] if item['commit']==row.iteration)
        settings=item['candidate_knobs'];values={name:getattr(row,name) for name in RegimeMeasurement.__dataclass_fields__}
        if any(settings[end+'_state'].get('encryption_mode','psk2')!='psk2' for end in ('ap','cpe')):
            raise ValueError('R15 endpoint encryption conflicts with declared WPA2 context')
        values.update(ap_policy=_cross_layer_policy(row.ap_policy,settings['ap_state'],'psk2'),
            cpe_policy=_cross_layer_policy(row.cpe_policy,settings['cpe_state'],'psk2'),
            source_position=f'/iterations/{next(i for i,r in enumerate(payload["iterations"]) if r["commit"]==row.iteration)}',
            associated_cpes=('Loco195',),topology_evidence='INFERRED_SINGLE_LINK_RECIPE_ENDPOINTS_NOT_ASSOCIATION_READBACK',
            encryption_mode='psk2',encryption_evidence='DECLARED_WPA2_PSK_CCMP_RECIPE_CONTEXT_NOT_EFFECTIVE_READBACK',
            distance_meters=None,raw_rtt_sample_count_reported=item.get('rtt_sample_count',len(row.rtts_ms)),
            flags=row.flags+('asymmetric_endpoint_states_preserved',
                'WPA2_CCMP_context_declared_not_per_window_cipher_or_offload_readback',
                'RTT_repetition_membership_and_pairing_not_retained'))
        # Context may be unknown but cannot disagree between declared endpoints.
        distances={values[end].distance_meters for end in ('ap_policy','cpe_policy')}
        if len(distances)!=1:raise ValueError('Endpoint timing-distance contexts disagree')
        values['distance_meters']=distances.pop()
        records.append(CrossLayerMeasurement(**values))
    if not include_auxiliary:records=[row for row in records if row.window_kind=='primary']
    records.sort(key=lambda row:(int(row.round_id[1:]),row.window_kind,row.iteration))
    return records,refs+source_refs


def normalized_asymmetric_dataset():
    records,refs=load_all15_measurements()
    manifest=local_json(MNOP_ARTIFACTS/'inputs_manifest.json')
    return dict(schema_version=4,evidence='frozen_I_L_output_plus_four_saved_R15_windows',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=software_versions(),
        source_refs=refs,input_manifest=manifest,ac_order=list(AC_ORDER),
        requested_record_count=90,observed_record_count=len(records),
        count_discrepancy='R15 JSON and TSV each contain4 windows;85+4=89, no fifth measurement fabricated',
        primary_window_count=sum(row.window_kind=='primary' for row in records),
        auxiliary_window_count=sum(row.window_kind=='summary_validation' for row in records),
        round_counts={f'R{i}':sum(row.round_id==f'R{i}' for row in records) for i in range(1,16)},
        experimental_unit='sequential treatment window; pooled RTTs are subsamples without block membership',
        historical_checks=[dict(status='UNKNOWN_LOCAL_ARTIFACT_ABSENT',check_complete=True,does_not_block=True)],
        records=[{**asdict(row),'policy_key':row.policy_key} for row in records])


def load_blocked_crossover_blocks(receipt_dict_or_path):
    """Extract genuine supplied (block_index,crossover_step) units, never pings.

    Accepted envelopes are top-level repetition_blocks or iteration-local
    repetition_blocks. A treatment ID/step can inherit an explicit iteration
    value. Missing block collections return[]; missing IDs within blocks fail.
    This schema is fixture-tested, not inferred from any live R16 file.
    """
    payload=deepcopy(receipt_dict_or_path) if isinstance(receipt_dict_or_path,dict) else local_json(receipt_dict_or_path)
    if not isinstance(payload,dict):raise ValueError('Crossover receipt must be an object')
    collections=[]
    if 'repetition_blocks' in payload:collections.append((payload['repetition_blocks'],payload,'/repetition_blocks'))
    iterations=payload.get('iterations',[])
    if not isinstance(iterations,list) or len(iterations)>1000:raise ValueError('Bounded iterations required')
    for index,iteration in enumerate(iterations):
        if not isinstance(iteration,dict):raise ValueError('Iteration object required')
        if 'repetition_blocks' in iteration:
            collections.append((iteration['repetition_blocks'],iteration,f'/iterations/{index}/repetition_blocks'))
    result=[];seen=set()
    aliases={'goodput_mbps':'goodput_rx_mbps','p50_ms':'p50_rtt_ms','p95_ms':'p95_rtt_ms','p99_ms':'p99_rtt_ms'}
    measured=('goodput_rx_mbps','p50_rtt_ms','p95_rtt_ms','p99_rtt_ms','packet_loss_pct','jain_fairness','retry_rate')
    for collection,parent,pointer in collections:
        if not isinstance(collection,list) or len(collection)>10000:raise ValueError('Bounded repetition_blocks list required')
        for index,item in enumerate(collection):
            if not isinstance(item,dict):raise ValueError('Block observation object required')
            block=exact_integer(item.get('block_index'),'genuine block_index',0,1_000_000)
            step=exact_integer(item.get('crossover_step',parent.get('crossover_step')),'genuine crossover_step',0,1_000_000)
            if 'crossover_step' in item and 'crossover_step' in parent and item['crossover_step']!=parent['crossover_step']:
                raise ValueError('Conflicting explicit crossover step')
            identity=(block,step)
            if identity in seen:raise ValueError('Duplicate block/step experimental unit')
            seen.add(identity)
            treatment=next((obj[key] for obj in (item,parent) for key in ('treatment_id','policy_id','commit') if key in obj),None)
            if not isinstance(treatment,str) or not treatment or treatment.strip()!=treatment:
                raise ValueError('Explicit treatment identity required')
            observation=deepcopy(item.get('observation',{}))
            if not isinstance(observation,dict):raise ValueError('Block observation must be object')
            # Validate the nested representation before a direct field can
            # overwrite it (bool==1 must not hide malformed numeric evidence).
            for key in measured:
                if key in observation:
                    upper=100 if key=='packet_loss_pct' else 1 if key=='jain_fairness' else 1_000_000
                    finite_number(observation[key],key,0,upper)
            for key,value in item.items():
                canonical=aliases.get(key,key)
                if canonical in measured:
                    if canonical in observation and observation[canonical]!=value:raise ValueError('Conflicting block metric')
                    observation[canonical]=value
            for key in measured:
                if key in observation:
                    upper=100 if key=='packet_loss_pct' else 1 if key=='jain_fairness' else 1_000_000
                    observation[key]=finite_number(observation[key],key,0,upper)
            quantiles=[observation.get(key) for key in ('p50_rtt_ms','p95_rtt_ms','p99_rtt_ms')]
            if all(value is not None for value in quantiles) and not quantiles[0]<=quantiles[1]<=quantiles[2]:
                raise ValueError('Block quantiles must be monotone')
            if not any(key in observation for key in measured):raise ValueError('Block requires a measured outcome')
            raw=item.get('rtts_ms',[])
            if not isinstance(raw,list) or len(raw)>100000:raise ValueError('Bounded block RTT list required')
            rtts=[finite_number(v,'block RTT',0,1_000_000) for v in raw]
            entry=dict(block_index=block,crossover_step=step,treatment_id=treatment,observation=observation,
                rtts_ms=rtts,source_position=f'{pointer}/{index}')
            for key in ('dl_goodput_mbps','ul_goodput_mbps','total_bidir_goodput_mbps'):
                if key in item:entry[key]=finite_number(item[key],key,0,10000)
            if all(key in entry for key in ('dl_goodput_mbps','ul_goodput_mbps','total_bidir_goodput_mbps')):
                if not math.isclose(entry['dl_goodput_mbps']+entry['ul_goodput_mbps'],entry['total_bidir_goodput_mbps'],abs_tol=.021):
                    raise ValueError('Block directional sum disagrees')
            if 'period_index' in item:entry['period_index']=exact_integer(item['period_index'],'period_index',0,1_000_000)
            for key in ('station_drops','restoration_verified'):
                if key in item or key in observation:
                    declared=[]
                    for source in (item,observation):
                        if key not in source:continue
                        value=source[key]
                        if key=='station_drops':value=exact_integer(value,key,0,1_000_000)
                        elif type(value) is not bool:raise ValueError('Block restoration must be boolean')
                        declared.append(value)
                    if len(declared)==2 and declared[0]!=declared[1]:
                        raise ValueError('Conflicting block quality evidence')
                    entry['observation'][key]=declared[0]
            result.append(entry)
            if len(result)>10000:raise ValueError('Too many block observations')
    return sorted(result,key=lambda item:(item['block_index'],item['crossover_step']))


@dataclass(frozen=True)
class ThreeTierMeasurement(CrossLayerMeasurement):
    """R16-R21 declarations; unknown ACK controls never become disabled defaults."""
    ap_ack_pps: int | None = None
    cpe_ack_pps: int | None = None
    ap_tcp_ack_vi: bool | None = None
    cpe_tcp_ack_vi: bool | None = None
    ap_ack_burst: int | None = None
    cpe_ack_burst: int | None = None
    ack_policy_evidence: str = 'UNKNOWN'
    cpu_telemetry: dict | None = None
    summary_consistency: dict | None = None
    block_design_kind: str = 'UNKNOWN'
    repetition_blocks: tuple[dict, ...] = ()

    def __post_init__(self):
        for name in ('ap_ack_pps', 'cpe_ack_pps', 'ap_ack_burst', 'cpe_ack_burst'):
            value = getattr(self, name)
            if value is not None:
                exact_integer(value, name, 0, 1_000_000)
        for name in ('ap_tcp_ack_vi', 'cpe_tcp_ack_vi'):
            if getattr(self, name) is not None and type(getattr(self, name)) is not bool:
                raise ValueError(f'{name} must be boolean or unknown')
        for end in ('ap', 'cpe'):
            rate, enabled = getattr(self, end + '_ack_pps'), getattr(self, end + '_tcp_ack_vi')
            if rate is not None and enabled is not None and enabled != (rate > 0):
                raise ValueError('ACK rate and VI declaration conflict')

    @property
    def policy_key(self):
        endpoints = []
        for end in ('ap', 'cpe'):
            policy = getattr(self, end + '_policy')
            if policy is None:
                endpoints.append(None)
                continue
            values = asdict(policy)
            values.update({key: getattr(self, end + '_' + key)
                           for key in ('ack_pps', 'tcp_ack_vi', 'ack_burst')})
            endpoints.append(values)
        return json.dumps(endpoints, sort_keys=True, separators=(',', ':'))


def _offline_path(path):
    value = str(path)
    if '://' in value or value.startswith(('\\\\', '//')):
        raise ValueError('Only offline local paths are accepted')
    return Path(path)


def _verified_qrst_json(path):
    """Read owned copies, checking the manifest without reopening originals."""
    path = _offline_path(path)
    if not path.is_file():
        return None
    if path.stat().st_size > 10_000_000:
        raise ValueError('Oversized offline input')
    if path.resolve().is_relative_to(QRST_INPUTS.resolve()):
        manifest = local_json(QRST_ARTIFACTS / 'inputs_manifest.json')
        matches = [row for row in manifest if (ROOT / row['path']).resolve() == path.resolve()]
        if len(matches) != 1:
            raise ValueError('Owned QRST input requires one manifest entry')
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != matches[0]['sha256'] or len(data) != matches[0]['bytes']:
            raise ValueError('Frozen QRST input checksum or size mismatch')
    return local_json(path)


def _physical_round_number(payload, *, max_round=21):
    if not isinstance(payload, dict):
        raise ValueError('Physical round receipt must be an object')
    match = re.fullmatch(r'FMX-AUTORESEARCH-LIVE-(\d{3})(?:-[A-Z0-9-]+)?', payload.get('experiment_id', ''))
    if not match or not 16 <= int(match[1]) <= max_round:
        raise ValueError(f'R16-R{max_round} experiment identity required')
    return int(match[1])


def _physical_block_rows(payload, *, max_round=21):
    """Adapt saved aliases, retaining genuine IDs and unknown per-block quality."""
    number = _physical_round_number(payload, max_round=max_round)
    iterations = payload.get('iterations')
    if not isinstance(iterations, list) or not 1 <= len(iterations) <= 1000:
        raise ValueError('Bounded nonempty physical windows required')
    result, seen, treatments = [], set(), set()
    for position, item in enumerate(iterations):
        if not isinstance(item, dict):
            raise ValueError('Physical treatment must be an object')
        treatment = item.get('commit')
        if not isinstance(treatment, str) or not treatment.strip() or treatment != treatment.strip() or treatment in treatments:
            raise ValueError('Unique explicit physical treatment ID required')
        treatments.add(treatment)
        blocks = item.get('repetition_blocks')
        if not isinstance(blocks, list) or not 1 <= len(blocks) <= 10000:
            raise ValueError('Saved physical repetition_blocks required')
        for index, raw in enumerate(blocks):
            if not isinstance(raw, dict):
                raise ValueError('Physical block observation must be an object')
            block = exact_integer(raw.get('block_index'), 'physical block_index')
            crossed = number != 17
            if crossed:
                step = exact_integer(raw.get('crossover_step'), 'physical crossover_step')
                identity = (block, step)
            else:
                if 'crossover_step' in raw:
                    raise ValueError('R17 sequential repetitions must not acquire crossover_step')
                step, identity = None, (treatment, block)
            if identity in seen:
                raise ValueError('Duplicate physical block/step or sequential repetition')
            seen.add(identity)
            observation = {}
            for source, target, upper in (
                ('total_goodput_mbps', 'goodput_rx_mbps', 10000),
                ('p50_rtt_ms', 'p50_rtt_ms', 1_000_000),
                ('p95_rtt_ms', 'p95_rtt_ms', 1_000_000),
                ('p99_rtt_ms', 'p99_rtt_ms', 1_000_000),
                ('bidir_jain_fairness', 'jain_fairness', 1),
            ):
                observation[target] = finite_number(raw.get(source), source, 0, upper)
            quantiles = [observation[k] for k in ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms')]
            if not quantiles[0] <= quantiles[1] <= quantiles[2]:
                raise ValueError('Physical block quantiles must be monotone')
            rtts = raw.get('rtts_ms')
            if not isinstance(rtts, list) or not 1 <= len(rtts) <= 100000:
                raise ValueError('Saved bounded received block RTTs required')
            rtts = [finite_number(v, 'physical block RTT', 0, 1_000_000) for v in rtts]
            if np.max(np.abs(np.percentile(rtts, [50, 95, 99]) - quantiles)) > .0011:
                raise ValueError('Physical block RTT quantiles disagree beyond recorded precision')
            sent = received = None
            if 'pings_sent' in raw or 'pings_rcvd' in raw:
                sent = exact_integer(raw.get('pings_sent'), 'block pings sent', 1, 1_000_000)
                received = exact_integer(raw.get('pings_rcvd'), 'block pings received', 0, sent)
                if received != len(rtts):
                    raise ValueError('Block received ping count disagrees with RTTs')
                observation['packet_loss_pct'] = 100 * (sent - received) / sent
            # A window's successful restoration is not a per-block health readback.
            for key in ('restoration_verified', 'station_drops'):
                if key in raw:
                    value = raw[key]
                    if key == 'restoration_verified' and type(value) is not bool:
                        raise ValueError('Block restoration must be boolean')
                    if key == 'station_drops':
                        value = exact_integer(value, key)
                    observation[key] = value
            dl, ul = (finite_number(raw.get(k), k, 0, 10000) for k in ('dl_goodput_mbps', 'ul_goodput_mbps'))
            if abs(dl + ul - observation['goodput_rx_mbps']) > .021:
                raise ValueError('Physical block directional sum disagrees')
            row = dict(round_id=f'R{number}', block_index=block, treatment_id=treatment,
                       observation=observation, rtts_ms=rtts, dl_goodput_mbps=dl,
                       ul_goodput_mbps=ul, total_bidir_goodput_mbps=observation['goodput_rx_mbps'],
                       pings_sent=sent, pings_rcvd=received,
                       source_position=f'/iterations/{position}/repetition_blocks/{index}',
                       design_kind='COUNTERBALANCED_CROSSOVER_DECLARED' if crossed else 'SEQUENTIAL_REPETITIONS_NO_CROSSOVER_STEP',
                       window_quality=deepcopy(item.get('observation', {})),
                       quality_evidence='PING_COUNTS_RECORDED_OTHER_BLOCK_HEALTH_UNKNOWN_UNLESS_EXPLICIT')
            if crossed:
                row['crossover_step'] = step
            for key in ('ap_cpu_busy_pct', 'ap_cpu_softirq_pct', 'ap_cpu_sys_pct'):
                if key in raw:
                    row[key] = finite_number(raw[key], key, 0, 100)
            if 'encryption_mode' in raw:
                if raw['encryption_mode'] not in ('psk2', 'none'):
                    raise ValueError('Unknown block encryption mode')
                if raw['encryption_mode'] != item.get('encryption_mode'):
                    raise ValueError('Block and treatment encryption modes disagree')
                row['encryption_mode'] = raw['encryption_mode']
            result.append(row)
            if len(result) > 10000:
                raise ValueError('Too many physical repetition observations')
    return result


def load_all21_block_observations(receipt_paths=R16_TO_R21_RECEIPTS):
    """Return88 crossed rows and16 unpaired R17 rows for the default snapshots.

    Crossed rows belong to24 round-scoped block IDs, not88 independent trials.
    This loader does not claim that deterministic schedules prove randomization.
    """
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 6:
        raise ValueError('Require1..6 frozen R16-R21 receipts')
    crossed, sequential, refs, seen = [], [], [], set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_qrst_json(path)
        if payload is None:
            refs.append(dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True))
            continue
        number = _physical_round_number(payload)
        if number in seen:
            raise ValueError('Duplicate physical round')
        seen.add(number)
        rows = _physical_block_rows(payload)
        (sequential if number == 17 else crossed).extend(rows)
        refs.append(dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest(), experiment_id=payload['experiment_id']))
    crossed.sort(key=lambda r: (int(r['round_id'][1:]), r['block_index'], r['crossover_step']))
    sequential.sort(key=lambda r: (int(r['round_id'][1:]), r['treatment_id'], r['block_index']))
    return dict(crossed=crossed, sequential=sequential, source_refs=refs)


def _ack_declarations(item):
    values = {}
    settings = item['candidate_knobs']
    for end in ('ap', 'cpe'):
        for suffix in ('ack_pps', 'ack_burst', 'tcp_ack_vi'):
            name = end + '_' + suffix
            declared = []
            for source in (item, settings, item.get('readback', {})):
                if name not in source:
                    continue
                value = source[name]
                if suffix == 'tcp_ack_vi':
                    if type(value) is not bool:
                        raise ValueError(f'{name} must be a boolean declaration')
                else:
                    value = exact_integer(value, name)
                declared.append(value)
            if declared and any(value != declared[0] for value in declared):
                raise ValueError('Conflicting ACK treatment declarations')
            values[name] = declared[0] if declared else None
        rate = values[end + '_ack_pps']
        if rate is not None and values[end + '_tcp_ack_vi'] is None:
            # The frozen R20/R21 recipes install a size-based VI marking rule
            # only for a positive declared rate. This is not effective AC proof.
            values[end + '_tcp_ack_vi'] = rate > 0
    return values


def _physical_window(item, number, position, blocks, *, allow_sorted_pool=False):
    settings, obs = item.get('candidate_knobs'), item.get('observation')
    if not isinstance(settings, dict) or not isinstance(obs, dict):
        raise ValueError('Physical window requires policy and observation objects')
    mode = item.get('encryption_mode', 'psk2')
    if mode not in ('psk2', 'none'):
        raise ValueError('Unknown physical window encryption mode')
    distance = item.get('distance_meters')
    if distance is not None:
        exact_integer(distance, 'programmed timing distance')
    endpoints = {}
    for end in ('ap', 'cpe'):
        state = settings.get(end + '_state')
        if not isinstance(state, dict):
            raise ValueError('Physical windows require separate AP/CPE states')
        if state.get('encryption_mode', mode) != mode or state.get('distance_meters', distance) != distance:
            raise ValueError('Endpoint and window context conflict')
        declared = dict(state, distance_meters=distance)
        endpoints[end + '_policy'] = _cross_layer_policy(_endpoint(settings, 15, end), declared, mode)
    raw = item.get('raw_rtts_ms')
    if not isinstance(raw, list) or not 1 <= len(raw) <= 100000:
        raise ValueError('Saved bounded pooled RTTs required')
    rtts = tuple(finite_number(v, 'received window RTT', 0, 1_000_000) for v in raw)
    concatenated = [v for block in blocks for v in block['rtts_ms']]
    sorted_pool = list(rtts) != concatenated and allow_sorted_pool and list(rtts) == sorted(concatenated)
    if list(rtts) != concatenated and not sorted_pool:
        raise ValueError('Pooled RTTs must retain their actual repetition membership')
    count = exact_integer(item.get('rtt_sample_count'), 'physical window RTT count', 1, 100000)
    if count != len(rtts):
        raise ValueError('Window RTT count disagrees')
    quantiles = tuple(finite_number(obs.get(k), k, 0, 1_000_000) for k in ('p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms'))
    if not quantiles[0] <= quantiles[1] <= quantiles[2] or np.max(np.abs(np.percentile(rtts, [50, 95, 99]) - quantiles)) > .0101:
        raise ValueError('Window RTT quantiles disagree beyond recorded precision')
    repetitions = exact_integer(obs.get('repetitions'), 'physical repetitions', 1, 10000)
    if repetitions != len(blocks):
        raise ValueError('Window repetitions disagree with saved block observations')
    goodput, dl, ul, total = (finite_number(value, name, 0, 10000) for value, name in (
        (obs.get('goodput_rx_mbps'), 'reported goodput'), (item.get('dl_goodput_mbps'), 'reported DL'),
        (item.get('ul_goodput_mbps'), 'reported UL'), (item.get('total_bidir_goodput_mbps'), 'reported total')))
    if abs(goodput - total) > .011:
        raise ValueError('Two reported aggregate goodput fields disagree')
    gp = tuple(block['observation']['goodput_rx_mbps'] for block in blocks)
    means = {key: float(np.mean([b[key] for b in blocks])) for key in ('dl_goodput_mbps', 'ul_goodput_mbps')}
    deltas = dict(reported_total_minus_directional_sum=goodput - dl - ul,
                  reported_total_minus_block_mean=goodput - float(np.mean(gp)),
                  reported_dl_minus_block_mean=dl - means['dl_goodput_mbps'],
                  reported_ul_minus_block_mean=ul - means['ul_goodput_mbps'])
    consistency = dict(consistent=all(abs(value) <= .021 for value in deltas.values()),
        tolerance_mbps=.021, reported_total_mbps=goodput, reported_directional_sum_mbps=dl + ul,
        block_mean_total_mbps=float(np.mean(gp)), block_mean_dl_mbps=means['dl_goodput_mbps'],
        block_mean_ul_mbps=means['ul_goodput_mbps'], deltas_mbps=deltas,
        handling='ORIGINAL_SUMMARIES_AND_BLOCKS_RETAINED_WITHOUT_REPAIR')
    loss = finite_number(obs.get('packet_loss_pct'), 'window packet loss', 0, 100)
    if all(b['pings_sent'] is not None for b in blocks):
        sent, received = sum(b['pings_sent'] for b in blocks), sum(b['pings_rcvd'] for b in blocks)
        if abs(loss - 100 * (sent - received) / sent) > .0101:
            raise ValueError('Window packet loss disagrees with saved ping counts')
    restoration = obs.get('restoration_verified')
    if type(restoration) is not bool:
        raise ValueError('Recorded window restoration boolean required')
    drops = exact_integer(obs.get('station_drops'), 'window station drops')
    packets = exact_integer(item.get('mac_tx_packets_delta'), 'MAC packets', 0, 10**12)
    retries = exact_integer(item.get('mac_tx_retries_delta'), 'MAC retry events', 0, 10**12)
    reported_retry = finite_number(obs.get('retry_rate'), 'reported retry metric', 0, 100)
    mac = None
    if packets:
        mac = finite_number(item.get('mac_retry_rate', retries / packets), 'MAC retry fraction', 0, 100)
        if abs(mac - retries / packets) > .000051:
            raise ValueError('MAC retry fraction disagrees with valid counters')
    flags = ['physical_repetition_membership_retained', 'within_link_repetitions_not_independent_sector_trials',
             'reported_restoration_not_independent_acceptance', 'sparse_received_RTT_tails',
             'declared_marking_not_verified_effective_AC_mapping']
    if sorted_pool:
        flags.append('pooled_RTTs_sorted_chronology_lost_block_arrays_preserved')
    if not consistency['consistent']:
        flags.append('reported_summary_disagrees_with_repetition_blocks')
    if not packets:
        flags.append('zero_MAC_denominator_retry_fraction_UNKNOWN')
    if loss or drops or not restoration:
        flags.append('not_eligible_for_controller_promotion')
    cpu = None
    if number == 17:
        reported_cpu = {key: finite_number(item.get(key), key, 0, 100) for key in
                        ('ap_cpu_busy_pct_median', 'ap_cpu_softirq_pct_median')}
        cpu = dict(reported_window_medians=reported_cpu,
                   repetitions=[{key: b[key] for key in ('block_index', 'ap_cpu_busy_pct', 'ap_cpu_softirq_pct', 'ap_cpu_sys_pct')}
                                for b in blocks],
                   evidence='RECORDED_AP_CPU_SAMPLES_SEQUENTIAL_NOT_CRYPTO_CYCLE_OR_OFFLOAD_MEASUREMENTS')
    return ThreeTierMeasurement(round_id=f'R{number}', iteration=item['commit'], workload_regime='bidir_6flow',
        active_flow_count=6, bidirectional=True, **endpoints, goodput_mbps=goodput,
        dl_goodput_mbps=dl, ul_goodput_mbps=ul, goodputs_mbps=gp, repetitions_reported=repetitions,
        rtts_ms=rtts, p50_ms=quantiles[0], p95_ms=quantiles[1], p99_ms=quantiles[2], packet_loss_pct=loss,
        jain_fairness=finite_number(obs.get('jain_fairness'), 'reported fairness', 0, 1), mac_retry_rate=mac,
        reported_retry_rate=reported_retry, retransmits=exact_integer(item.get('retransmits'), 'TCP retransmits', 0, 10**12),
        mac_tx_packets=packets, mac_tx_retries=retries, restoration_verified=restoration, station_drops=drops,
        flags=tuple(flags), source_position=f'/iterations/{position}', associated_cpes=('Loco195',),
        topology_evidence='DECLARED_SINGLE_LINK_FROZEN_RECIPE_NOT_INDEPENDENT_TOPOLOGY_ACCEPTANCE',
        encryption_mode=mode, encryption_evidence='RECORDED_WINDOW_MODE_AND_FROZEN_RECIPE_NOT_EFFECTIVE_CIPHER_OR_OFFLOAD_PROOF' if number == 17 else 'DECLARED_WPA2_RECIPE_CONTEXT_NOT_PER_WINDOW_CIPHER_READBACK',
        distance_meters=distance, raw_rtt_sample_count_reported=count,
        **_ack_declarations(item), ack_policy_evidence='DECLARED_FIELDS_OR_PPS_ENABLE_RULE_NOT_VERIFIED_PURE_ACK_OR_AC_MAPPING',
        cpu_telemetry=cpu, summary_consistency=consistency, block_design_kind=blocks[0]['design_kind'],
        repetition_blocks=tuple(deepcopy(blocks)))


def load_all21_measurements(receipt_paths=R16_TO_R21_RECEIPTS, *, base_dataset_path=R15_NORMALIZED_OUTPUT,
                            include_auxiliary=True):
    """Extend the unchanged89-record M-P output with23 saved physical windows."""
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base_path = _offline_path(base_dataset_path)
    if base_path.resolve() == R15_NORMALIZED_OUTPUT.resolve():
        previous = local_json(MNOP_ARTIFACTS / 'final_validation.json')
        matches = [entry for entry in previous['bindings'] if (ROOT / entry['path']).resolve() == base_path.resolve()]
        if len(matches) != 1 or hashlib.sha256(base_path.read_bytes()).hexdigest() != matches[0]['sha256']:
            raise ValueError('Prior M-P normalized output checksum mismatch')
    base = local_json(base_path)
    if not isinstance(base, dict) or base.get('schema_version') != 4 or not isinstance(base.get('records'), list):
        raise ValueError('Frozen M-P normalized schema4 output required')
    try:
        records = [_measurement_from_normalized(item) for item in base['records']]
    except (KeyError, TypeError) as error:
        raise ValueError('Malformed prior M-P normalized record') from error
    if any(not re.fullmatch(r'R(?:[1-9]|1[0-5])', row.round_id) for row in records):
        raise ValueError('Prior M-P corpus must contain only R1-R15')
    if len({(r.round_id, r.iteration) for r in records}) != len(records):
        raise ValueError('Duplicate prior M-P window')
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 6:
        raise ValueError('Require1..6 R16-R21 receipts')
    refs, seen = deepcopy(base['source_refs']), set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_qrst_json(path)
        if payload is None:
            refs.append(dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True))
            continue
        number = _physical_round_number(payload)
        if number in seen:
            raise ValueError('Duplicate R16-R21 round')
        seen.add(number)
        blocks = _physical_block_rows(payload)
        for index, item in enumerate(payload['iterations']):
            treatment_blocks = [b for b in blocks if b['treatment_id'] == item['commit']]
            records.append(_physical_window(item, number, index, treatment_blocks))
        refs.append(dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                         sha256=hashlib.sha256(path.read_bytes()).hexdigest(), experiment_id=payload['experiment_id'],
                         timestamp_utc=payload.get('timestamp_utc')))
    if not include_auxiliary:
        records = [row for row in records if row.window_kind == 'primary']
    records.sort(key=lambda row: (int(row.round_id[1:]), row.window_kind, row.iteration))
    return records, refs


def normalized_real_crossover_dataset():
    records, refs = load_all21_measurements()
    blocks = load_all21_block_observations()
    return dict(schema_version=5, evidence='frozen_M_P_output_plus_R16_R21_physical_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False, software_versions=software_versions(),
        source_refs=refs, input_manifest=local_json(QRST_ARTIFACTS / 'inputs_manifest.json'), ac_order=list(AC_ORDER),
        observed_record_count=len(records), requested_record_count=112,
        primary_window_count=sum(row.window_kind == 'primary' for row in records),
        auxiliary_window_count=sum(row.window_kind == 'summary_validation' for row in records),
        round_counts={f'R{i}': sum(row.round_id == f'R{i}' for row in records) for i in range(1, 22)},
        crossed_observation_count=len(blocks['crossed']),
        matched_round_scoped_block_count=len({(b['round_id'], b['block_index']) for b in blocks['crossed']}),
        sequential_repetition_count=len(blocks['sequential']),
        experimental_units='Matched within-link round-scoped blocks forR16/R18-R21; R17sequentialunpaired; pings are subsamples',
        summary_inconsistency_handling='Preserve recorded summaries and block outcomes; explicitflags; no silent repair or candidate promotion',
        historical_checks=[dict(status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True, does_not_block=True)],
        records=[{**asdict(row), 'policy_key': row.policy_key} for row in records])


@dataclass(frozen=True)
class LowerMACMeasurement(ThreeTierMeasurement):
    """Shared AP/CPE lower-MAC declarations, not verified actuation authority.

    Bounds encode values and masks; they are not hardware-approved safe ranges.
    None remains unknown and never implies a stock default.
    """
    short_retry_limit: int | None = None
    long_retry_limit: int | None = None
    force_tx_status: int | None = None
    ani_enable: int | None = None
    airtime_flags: int | None = None
    fq_limit: int | None = None
    lower_mac_evidence: str = 'UNKNOWN'
    rtt_pool_order: str = 'UNKNOWN'

    def __post_init__(self):
        super().__post_init__()
        for name, (low, high) in LOWER_MAC_BOUNDS.items():
            value = getattr(self, name)
            if value is not None:
                exact_integer(value, name, low, high)

    @property
    def policy_key(self):
        endpoints = json.loads(super().policy_key)
        for values in endpoints:
            if values is not None:
                values.update({name: getattr(self, name) for name in LOWER_MAC_BOUNDS})
        return json.dumps(endpoints, sort_keys=True, separators=(',', ':'))


def _verified_uvwx_json(path):
    path = _offline_path(path)
    if not path.is_file():
        return None
    if path.stat().st_size > 10_000_000:
        raise ValueError('Oversized offline input')
    if path.resolve().is_relative_to(UVWX_INPUTS.resolve()):
        manifest = local_json(UVWX_ARTIFACTS / 'inputs_manifest.json')
        matches = [r for r in manifest if (ROOT / r['path']).resolve() == path.resolve()]
        if len(matches) != 1:
            raise ValueError('Owned UVWX input requires one manifest entry')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != matches[0]['sha256'] or len(raw) != matches[0]['bytes']:
            raise ValueError('Frozen UVWX checksum or size mismatch')
    return local_json(path)


def _verified_prior_qrst_output(path, expected_path):
    path = _offline_path(path)
    if path.resolve() == expected_path.resolve():
        previous = local_json(QRST_ARTIFACTS / 'final_validation.json')
        matches = [r for r in previous['bindings'] if (ROOT / r['path']).resolve() == path.resolve()]
        if len(matches) != 1 or hashlib.sha256(path.read_bytes()).hexdigest() != matches[0]['sha256']:
            raise ValueError('Prior Q-T output checksum mismatch')
    return local_json(path)


def _measurement_from_normalized21(item):
    if 'summary_consistency' not in item:
        return _measurement_from_normalized(item)
    values = {name: item[name] for name in ThreeTierMeasurement.__dataclass_fields__}
    for end in ('ap_policy', 'cpe_policy'):
        if values[end] is not None:
            policy = dict(values[end])
            policy['aql_by_ac'] = tuple(tuple(pair) for pair in policy['aql_by_ac'])
            values[end] = CrossLayerEndpointPolicy(**policy)
    for name in ('goodputs_mbps', 'rtts_ms', 'flags', 'associated_cpes', 'repetition_blocks'):
        values[name] = tuple(values[name])
    row = ThreeTierMeasurement(**values)
    if row.policy_key != item['policy_key']:
        raise ValueError('Prior Q-T normalized policy identity disagrees')
    return row


def _new_lower_mac_receipts(receipt_paths):
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 5:
        raise ValueError('Require1..5 frozen R22-R26 receipts')
    seen = set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_uvwx_json(path)
        if payload is None:
            yield None, None, dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True)
            continue
        number = _physical_round_number(payload, max_round=26)
        if not 22 <= number <= 26 or number in seen:
            raise ValueError('Unique R22-R26 receipt identities required')
        seen.add(number)
        ref = dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest(), experiment_id=payload['experiment_id'],
                   timestamp_utc=payload.get('timestamp_utc'))
        yield number, payload, ref


def _lower_mac_declarations(item):
    settings = item['candidate_knobs']
    readback = item.get('readback', {})
    if not isinstance(readback, dict):
        raise ValueError('Lower-MAC readback envelope must be an object')
    values = {}
    for name, (low, high) in LOWER_MAC_BOUNDS.items():
        declared = [exact_integer(source[name], name, low, high)
                    for source in (item, settings, readback) if name in source]
        if declared and any(value != declared[0] for value in declared):
            raise ValueError('Conflicting shared lower-MAC declarations')
        values[name] = declared[0] if declared else None
    return values


def load_all26_measurements(receipt_paths=R22_TO_R26_RECEIPTS, *, base_dataset_path=R21_NORMALIZED_OUTPUT,
                            include_auxiliary=True):
    """Preserve the112-record Q-T output and add19 R22-R26 saved windows."""
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _verified_prior_qrst_output(base_dataset_path, R21_NORMALIZED_OUTPUT)
    if not isinstance(base, dict) or base.get('schema_version') != 5 or not isinstance(base.get('records'), list):
        raise ValueError('Frozen Q-T normalized schema5 required')
    try:
        records = [_measurement_from_normalized21(item) for item in base['records']]
    except (KeyError, TypeError) as error:
        raise ValueError('Malformed prior Q-T normalized record') from error
    if any(not re.fullmatch(r'R(?:[1-9]|1\d|2[01])', row.round_id) for row in records):
        raise ValueError('Prior Q-T corpus must contain only R1-R21')
    if len({(r.round_id, r.iteration) for r in records}) != len(records):
        raise ValueError('Duplicate prior Q-T window')
    refs = deepcopy(base['source_refs'])
    for number, payload, ref in _new_lower_mac_receipts(receipt_paths):
        refs.append(ref)
        if payload is None:
            continue
        blocks = _physical_block_rows(payload, max_round=26)
        for index, item in enumerate(payload['iterations']):
            treatment_blocks = [b for b in blocks if b['treatment_id'] == item['commit']]
            window = _physical_window(item, number, index, treatment_blocks, allow_sorted_pool=number >= 24)
            values = {name: getattr(window, name) for name in ThreeTierMeasurement.__dataclass_fields__}
            concatenated = [v for b in treatment_blocks for v in b['rtts_ms']]
            order = 'CONCATENATED_BLOCK_ORDER' if list(window.rtts_ms) == concatenated else 'SORTED_POOL_BLOCK_ARRAYS_RETAINED'
            records.append(LowerMACMeasurement(**values, **_lower_mac_declarations(item),
                lower_mac_evidence='SHARED_AP_CPE_RECIPE_FIELDS_NOT_EFFECTIVE_FIRMWARE_TIMING_OR_CONTROL_PROOF',
                rtt_pool_order=order))
    if not include_auxiliary:
        records = [row for row in records if row.window_kind == 'primary']
    records.sort(key=lambda row: (int(row.round_id[1:]), row.window_kind, row.iteration))
    return records, refs


def load_all26_block_observations(receipt_paths=R22_TO_R26_RECEIPTS, *, base_dataset_path=R21_BLOCK_OUTPUT):
    """Return188 crossed rows in52 round-scoped IDs plus16 sequential R17 rows."""
    base = _verified_prior_qrst_output(base_dataset_path, R21_BLOCK_OUTPUT)
    if not isinstance(base, dict) or not all(isinstance(base.get(key), list) for key in ('crossed', 'sequential', 'source_refs')):
        raise ValueError('Frozen Q-T crossed/sequential block output required')
    crossed, sequential, refs = (deepcopy(base[key]) for key in ('crossed', 'sequential', 'source_refs'))
    seen = set()
    for rows, is_crossed in ((crossed, True), (sequential, False)):
        if len(rows) > 10000:
            raise ValueError('Bounded prior block output required')
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError('Prior block row object required')
            round_id = row.get('round_id')
            allowed = {'R16', 'R18', 'R19', 'R20', 'R21'} if is_crossed else {'R17'}
            if round_id not in allowed:
                raise ValueError('Prior physical block round identity conflicts')
            block = exact_integer(row.get('block_index'), 'prior block_index')
            if is_crossed:
                step = exact_integer(row.get('crossover_step'), 'prior crossover_step')
                identity = (round_id, block, step)
            else:
                if 'crossover_step' in row:
                    raise ValueError('Prior R17 sequential row must not acquire a crossover step')
                identity = (round_id, row.get('treatment_id'), block)
            if identity in seen:
                raise ValueError('Duplicate prior physical unit')
            seen.add(identity)
    for number, payload, ref in _new_lower_mac_receipts(receipt_paths):
        refs.append(ref)
        if payload is not None:
            crossed.extend(_physical_block_rows(payload, max_round=26))
    crossed.sort(key=lambda r: (int(r['round_id'][1:]), r['block_index'], r['crossover_step']))
    sequential.sort(key=lambda r: (int(r['round_id'][1:]), r['treatment_id'], r['block_index']))
    return dict(crossed=crossed, sequential=sequential, source_refs=refs)


def normalized_lower_mac_dataset():
    records, refs = load_all26_measurements()
    blocks = load_all26_block_observations()
    return dict(schema_version=6, evidence='frozen_Q_T_output_plus_R22_R26_physical_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False, software_versions=software_versions(),
        source_refs=refs, input_manifest=local_json(UVWX_ARTIFACTS / 'inputs_manifest.json'), ac_order=list(AC_ORDER),
        observed_record_count=len(records), requested_record_count=131,
        primary_window_count=sum(row.window_kind == 'primary' for row in records),
        auxiliary_window_count=sum(row.window_kind == 'summary_validation' for row in records),
        round_counts={f'R{i}': sum(row.round_id == f'R{i}' for row in records) for i in range(1, 27)},
        crossed_observation_count=len(blocks['crossed']),
        matched_round_scoped_block_count=len({(b['round_id'], b['block_index']) for b in blocks['crossed']}),
        sequential_repetition_count=len(blocks['sequential']),
        lower_mac_bounds_semantics='Parser representation domains only, not safe hardware ranges or effective control proof',
        experimental_units='Matched round-scoped within-link blocks; R17 sequential unpaired; RTTs are subsamples',
        summary_inconsistency_handling='Reported summaries and original block outcomes retained; no score repair or automatic promotion',
        sorted_pool_handling='R24-R26 sorted pools verified against block sample multisets; chronology never reconstructed',
        historical_checks=[dict(status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True, does_not_block=True)],
        records=[{**asdict(row), 'policy_key': row.policy_key} for row in records])


@dataclass(frozen=True)
class CertifiedWDSMeasurement(LowerMACMeasurement):
    """Observed certification checks, including refutations of claimed equality.

    The label identifies the source campaign, not successful physical acceptance.
    Exact rational decimal equality is separate from rounding compatibility.
    """
    block_mean_consistent: bool = False
    raw_rtts_matches_blocks: bool = False
    certified_wds_evidence: dict | None = None

    def __post_init__(self):
        super().__post_init__()
        if type(self.block_mean_consistent) is not bool or type(self.raw_rtts_matches_blocks) is not bool:
            raise ValueError('Certification checks must be explicit booleans')
        if not isinstance(self.certified_wds_evidence, dict):
            raise ValueError('Certification provenance must be an object')


def _verified_yzab_json(path):
    path = _offline_path(path)
    if not path.is_file():
        return None
    if path.stat().st_size > 10_000_000:
        raise ValueError('Oversized offline input')
    if path.resolve().is_relative_to(YZAB_INPUTS.resolve()):
        manifest = local_json(YZAB_ARTIFACTS / 'inputs_manifest.json')
        matches = [r for r in manifest if (ROOT / r['path']).resolve() == path.resolve()]
        raw = path.read_bytes()
        if (len(matches) != 1 or hashlib.sha256(raw).hexdigest() != matches[0]['sha256']
                or len(raw) != matches[0]['bytes']):
            raise ValueError('Frozen YZAB input checksum or size mismatch')
    return local_json(path)


def _verified_prior_uvwx_output(path, expected_path):
    path = _offline_path(path)
    if path.resolve() == expected_path.resolve():
        previous = local_json(UVWX_ARTIFACTS / 'final_validation.json')
        matches = [r for r in previous['bindings'] if (ROOT / r['path']).resolve() == path.resolve()]
        raw = path.read_bytes()
        if (len(matches) != 1 or hashlib.sha256(raw).hexdigest() != matches[0]['sha256']
                or len(raw) != matches[0]['bytes']):
            raise ValueError('Prior U-X output checksum or size mismatch')
    return local_json(path)


def _measurement_from_normalized26(item):
    if 'lower_mac_evidence' not in item:
        return _measurement_from_normalized21(item)
    values = {name: item[name] for name in LowerMACMeasurement.__dataclass_fields__}
    for end in ('ap_policy', 'cpe_policy'):
        if values[end] is not None:
            policy = dict(values[end])
            policy['aql_by_ac'] = tuple(tuple(pair) for pair in policy['aql_by_ac'])
            values[end] = CrossLayerEndpointPolicy(**policy)
    for name in ('goodputs_mbps', 'rtts_ms', 'flags', 'associated_cpes', 'repetition_blocks'):
        values[name] = tuple(values[name])
    row = LowerMACMeasurement(**values)
    if row.policy_key != item['policy_key']:
        raise ValueError('Prior U-X normalized policy identity disagrees')
    return row


def _new_certified_receipts(receipt_paths):
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 6:
        raise ValueError('Require 1..6 frozen R27-R32 receipts')
    seen = set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_yzab_json(path)
        if payload is None:
            yield None, None, dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True)
            continue
        number = _physical_round_number(payload, max_round=32)
        if not 27 <= number <= 32 or number in seen:
            raise ValueError('Unique R27-R32 receipt identities required')
        seen.add(number)
        ref = dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size,
                   experiment_id=payload['experiment_id'], timestamp_utc=payload.get('timestamp_utc'))
        yield number, payload, ref


def _certified_recipe_ref(number):
    matches = [r for r in local_json(YZAB_ARTIFACTS / 'inputs_manifest.json')
               if r['round'] == number and r['path'].endswith('.py')]
    if len(matches) != 1:
        raise ValueError('One frozen recipe provenance entry per certified round required')
    ref = deepcopy(matches[0])
    path = (ROOT / ref['path']).resolve()
    if not path.is_relative_to(YZAB_INPUTS.resolve()):
        raise ValueError('Recipe provenance must stay in frozen inputs')
    raw = path.read_bytes()
    if len(raw) != ref['bytes'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('Frozen certified recipe checksum or size mismatch')
    text = raw.decode('utf-8')
    return ref, 'phy0-ap0.sta1' in text


def _certified_regime(number, payload, item):
    expected = ('bidir_2flow', 2, True) if number == 30 else (
        ('unidir_dl_2flow', 2, False) if number == 31 else ('bidir_6flow', 6, True))
    for source in (payload, item):
        if 'workload_regime' in source and source['workload_regime'] != expected[0]:
            raise ValueError('Certified workload regime conflicts with round recipe')
        if 'active_flow_count' in source and exact_integer(source['active_flow_count'], 'active flows', 1, 1000) != expected[1]:
            raise ValueError('Certified active flow count conflicts with regime')
        if 'bidirectional' in source and (type(source['bidirectional']) is not bool or source['bidirectional'] != expected[2]):
            raise ValueError('Certified direction conflicts with regime')
    return expected


def _certified_block_rows(payload, *, max_round=32):
    rows = _physical_block_rows(payload, max_round=max_round)
    raw_by_identity = {(item['commit'], raw['block_index'], raw['crossover_step']): raw
                       for item in payload['iterations'] for raw in item['repetition_blocks']}
    for row in rows:
        raw = raw_by_identity[row['treatment_id'], row['block_index'], row['crossover_step']]
        packets = exact_integer(raw.get('mac_tx_packets_delta'), 'block MAC packets', 0, 10**12)
        retries = exact_integer(raw.get('mac_tx_retries_delta'), 'block MAC retry events', 0, 10**12)
        reported = finite_number(raw.get('mac_retry_rate'), 'block MAC retry fraction', 0, 100)
        computed = retries / packets if packets else None
        if computed is not None and abs(reported - computed) > .00000501:
            raise ValueError('Block MAC retry fraction conflicts with five-decimal source precision')
        row.update(mac_tx_packets_delta=packets, mac_tx_retries_delta=retries,
                   mac_retry_rate=reported, mac_retry_rate_from_counters=computed,
                   counter_interface='phy0-ap0.sta1',
                   counter_interface_evidence='NAMED_IN_FROZEN_RECIPE_NOT_INDEPENDENT_DEVICE_READBACK')
    return rows


def _certified_summary_evidence(window, item, blocks, ref, recipe_ref, interface_named):
    comparisons = {
        'goodput_mbps': (window.goodput_mbps, [b['observation']['goodput_rx_mbps'] for b in blocks]),
        'dl_goodput_mbps': (window.dl_goodput_mbps, [b['dl_goodput_mbps'] for b in blocks]),
        'ul_goodput_mbps': (window.ul_goodput_mbps, [b['ul_goodput_mbps'] for b in blocks]),
        'jain_fairness': (window.jain_fairness, [b['observation']['jain_fairness'] for b in blocks]),
    }
    exact_deltas = {key: Fraction(str(reported)) - sum(Fraction(str(v)) for v in values) / len(values)
                    for key, (reported, values) in comparisons.items()}
    # The source serializes summaries to three decimals and block fairness to four.
    # This is a diagnostic of source precision, never a replacement exact gate.
    rounded_compatible = all(abs(delta) <= (Fraction('0.001') if key != 'jain_fairness' else Fraction('0.00055'))
                             for key, delta in exact_deltas.items())
    return dict(
        block_mean_consistent=all(delta == 0 for delta in exact_deltas.values()),
        block_mean_exact_delta_fractions={key: str(value) for key, value in exact_deltas.items()},
        block_mean_deltas={key: float(value) for key, value in exact_deltas.items()},
        block_mean_numpy_deltas={key: float(reported - np.mean(values)) for key, (reported, values) in comparisons.items()},
        exact_equality_definition='Exact rational values of the recorded decimal numbers; reported*n == sum(block values), no tolerance',
        rounded_summary_compatible=rounded_compatible,
        rounded_summary_diagnostic_tolerance={'Mbps': .001, 'Jain': .00055},
        rounded_summary_diagnostic_is_not_certification=True,
        raw_rtts_matches_blocks=list(window.rtts_ms) == [v for b in blocks for v in b['rtts_ms']],
        mac_block_sums_match_window=(sum(b['mac_tx_packets_delta'] for b in blocks) == window.mac_tx_packets
                                    and sum(b['mac_tx_retries_delta'] for b in blocks) == window.mac_tx_retries),
        mac_counters_valid=window.mac_tx_packets > 0 and all(b['mac_tx_packets_delta'] > 0 for b in blocks),
        counter_interface='phy0-ap0.sta1' if interface_named else None,
        counter_interface_evidence='NAMED_IN_FROZEN_RECIPE_NOT_INDEPENDENT_DEVICE_READBACK',
        source_receipt=deepcopy(ref), source_recipe=deepcopy(recipe_ref),
        declared_endpoint_states={end: deepcopy(item['candidate_knobs'][end + '_state']) for end in ('ap', 'cpe')},
        wmm_edca_provenance='UNKNOWN_NOT_RECORDED_IN_RECEIPT_OR_RECIPE',
        recipe_execution_allowed=False, effective_hardware_control_accepted=False)


def load_all32_measurements(receipt_paths=R27_TO_R32_RECEIPTS, *, base_dataset_path=R26_NORMALIZED_OUTPUT,
                            include_auxiliary=True):
    """Preserve 131 prior records; add the 19 observed R27-R32 arms, not 20."""
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _verified_prior_uvwx_output(base_dataset_path, R26_NORMALIZED_OUTPUT)
    if not isinstance(base, dict) or base.get('schema_version') != 6 or not isinstance(base.get('records'), list):
        raise ValueError('Frozen U-X normalized schema6 required')
    try:
        records = [_measurement_from_normalized26(item) for item in base['records']]
    except (KeyError, TypeError) as error:
        raise ValueError('Malformed prior U-X normalized record') from error
    if any(not re.fullmatch(r'R(?:[1-9]|1\d|2[0-6])', r.round_id) for r in records):
        raise ValueError('Prior U-X corpus must contain only R1-R26')
    if len({(r.round_id, r.iteration) for r in records}) != len(records):
        raise ValueError('Duplicate prior U-X window')
    refs = deepcopy(base['source_refs'])
    for number, payload, ref in _new_certified_receipts(receipt_paths):
        refs.append(ref)
        if payload is None:
            continue
        blocks = _certified_block_rows(payload)
        recipe_ref, interface_named = _certified_recipe_ref(number)
        for index, item in enumerate(payload['iterations']):
            selected = [b for b in blocks if b['treatment_id'] == item['commit']]
            window = _physical_window(item, number, index, selected)
            values = {name: getattr(window, name) for name in ThreeTierMeasurement.__dataclass_fields__}
            regime, flows, bidirectional = _certified_regime(number, payload, item)
            values.update(workload_regime=regime, active_flow_count=flows, bidirectional=bidirectional)
            evidence = _certified_summary_evidence(window, item, selected, ref, recipe_ref, interface_named)
            flags = list(values['flags'])
            if not evidence['block_mean_consistent']:
                flags.append('literal_exact_block_mean_certification_FAILED')
            if not evidence['mac_block_sums_match_window']:
                flags.append('window_MAC_counters_disagree_with_block_sums')
            if not evidence['mac_counters_valid'] and not any('zero_MAC_denominator' in flag for flag in flags):
                flags.append('zero_MAC_denominator_retry_fraction_UNKNOWN')
            values['flags'] = tuple(flags)
            records.append(CertifiedWDSMeasurement(**values, **_lower_mac_declarations(item),
                lower_mac_evidence='SHARED_AP_CPE_RECIPE_FIELDS_NOT_EFFECTIVE_FIRMWARE_TIMING_OR_CONTROL_PROOF',
                rtt_pool_order='CONCATENATED_BLOCK_ORDER',
                block_mean_consistent=evidence['block_mean_consistent'],
                raw_rtts_matches_blocks=evidence['raw_rtts_matches_blocks'], certified_wds_evidence=evidence))
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    records.sort(key=lambda r: (int(r.round_id[1:]), r.window_kind, r.iteration))
    return records, refs


def load_all32_block_observations(receipt_paths=R27_TO_R32_RECEIPTS, *, base_dataset_path=R26_BLOCK_OUTPUT):
    """Retain 188 old crossed rows and 16 sequential rows; append 144 new rows."""
    base = _verified_prior_uvwx_output(base_dataset_path, R26_BLOCK_OUTPUT)
    if not isinstance(base, dict) or not all(isinstance(base.get(k), list) for k in ('crossed', 'sequential', 'source_refs')):
        raise ValueError('Frozen U-X crossed/sequential block output required')
    crossed, sequential, refs = (deepcopy(base[k]) for k in ('crossed', 'sequential', 'source_refs'))
    seen = set()
    for group, crossed_kind in ((crossed, True), (sequential, False)):
        if len(group) > 10000:
            raise ValueError('Bounded prior block output required')
        for row in group:
            if not isinstance(row, dict) or row.get('round_id') not in (
                    {f'R{i}' for i in range(16, 27) if i != 17} if crossed_kind else {'R17'}):
                raise ValueError('Prior U-X block identity conflicts')
            block = exact_integer(row.get('block_index'), 'prior block_index')
            if crossed_kind:
                identity = (row['round_id'], block, exact_integer(row.get('crossover_step'), 'prior crossover_step'))
            else:
                if 'crossover_step' in row:
                    raise ValueError('R17 sequential row cannot acquire crossover step')
                identity = ('R17', row.get('treatment_id'), block)
            if identity in seen:
                raise ValueError('Duplicate prior U-X block identity')
            seen.add(identity)
    for _, payload, ref in _new_certified_receipts(receipt_paths):
        refs.append(ref)
        if payload is not None:
            crossed.extend(_certified_block_rows(payload))
    crossed.sort(key=lambda b: (int(b['round_id'][1:]), b['block_index'], b['crossover_step']))
    return dict(crossed=crossed, sequential=sequential, source_refs=refs)


def load_normalized_records(*args, **kwargs):
    """Latest frozen corpus API; returns (records, source_refs). Older APIs stay fixed."""
    return load_all47_measurements(*args, **kwargs)


def load_crossed_block_records(*args, **kwargs):
    """Latest block corpus API; returns crossed/sequential/source_refs collections."""
    return load_all47_block_observations(*args, **kwargs)


def normalized_certified_wds_dataset():
    records, refs = load_all32_measurements()
    blocks = load_all32_block_observations()
    new = [r for r in records if isinstance(r, CertifiedWDSMeasurement)]
    return dict(schema_version=7, evidence='Frozen_U_X_output_plus_R27_R32_saved_WDS_campaign_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False, software_versions=software_versions(),
        source_refs=refs, input_manifest=local_json(YZAB_ARTIFACTS / 'inputs_manifest.json'), ac_order=list(AC_ORDER),
        observed_record_count=len(records), requested_record_count=151,
        primary_window_count=sum(r.window_kind == 'primary' for r in records),
        auxiliary_window_count=sum(r.window_kind == 'summary_validation' for r in records),
        round_counts={f'R{i}': sum(r.round_id == f'R{i}' for r in records) for i in range(1, 33)},
        new_arm_count=len(new), requested_new_arm_count=20,
        crossed_observation_count=len(blocks['crossed']), requested_crossed_observation_count=328,
        matched_round_scoped_block_count=len({(b['round_id'], b['block_index']) for b in blocks['crossed']}),
        requested_matched_block_count=108, sequential_repetition_count=len(blocks['sequential']),
        literal_exact_block_mean_pass_count=sum(r.block_mean_consistent for r in new),
        raw_rtt_chronology_pass_count=sum(r.raw_rtts_matches_blocks for r in new),
        positive_MAC_denominator_count=sum(r.mac_tx_packets > 0 for r in new),
        certification='Source checks are explicit observed results, never inferred from campaign labels',
        experimental_units='Matched round-scoped within-link blocks; R17 separate; RTTs are subsamples',
        records=[{**asdict(r), 'policy_key': r.policy_key} for r in records])


@dataclass(frozen=True)
class ExactCampaignMeasurement(CertifiedWDSMeasurement):
    """Saved timing declarations; scoped R75 class33 is not firmware/range proof."""
    coverage_class: int | None = None
    source_failure_metadata: dict | None = None

    def __post_init__(self):
        super().__post_init__()
        if self.coverage_class is not None:
            evidence = self.certified_wds_evidence or {}
            declared_r75_only = (
                self.round_id == 'R75' and self.coverage_class == 33
                and type(self.distance_meters) is int and self.distance_meters == 15000
                and type(self.active_flow_count) is int and self.active_flow_count == 6
                and self.bidirectional is True
                and self.workload_regime == 'bidir_6flow'
                and all(type(evidence.get(k)) is int for k in ('coverage_class','slot_time_us','ack_timeout_us'))
                and evidence.get('coverage_class') == 33
                and evidence.get('slot_time_us') == 108 and evidence.get('ack_timeout_us') == 216
                and evidence.get('slot_ack_source') == 'SHARED_PAYLOAD_TREATMENT_KNOBS'
                and evidence.get('frozen_recipe_coverage_command_declared') is True
                and evidence.get('physical_distance_verified') is False
                and evidence.get('effective_timing_independently_verified') is False
                and evidence.get('coverage_command_execution_or_readback_independently_verified') is False)
            if declared_r75_only:
                exact_integer(self.coverage_class, 'coverage class', 33, 33)
            else:
                exact_integer(self.coverage_class, 'coverage class', 0, 31)
        if not isinstance(self.source_failure_metadata, dict):
            raise ValueError('Explicit source failure metadata required')


def _verified_acaf_json(path):
    """Accept a recorded Infinity only as a tagged, disqualified CRASH loss.

    Measurement numbers retain the strict finite contract. The four R36 loss
    sentinels are metadata, serialized safely without changing frozen bytes.
    """
    path = _offline_path(path)
    match = re.search(r'(?:^|_)r(\d+)(?:_|\.)', path.name)
    if match and int(match[1]) > 42:
        raise ValueError('R43+ inputs are outside this frozen campaign')
    if not path.is_file():
        return None
    if path.stat().st_size > 10_000_000:
        raise ValueError('Oversized offline input')
    raw = path.read_bytes()
    if path.resolve().is_relative_to(ACAF_INPUTS.resolve()):
        matches = [entry for entry in local_json(ACAF_ARTIFACTS / 'inputs_manifest.json')['entries']
                   if (ROOT / entry['path']).resolve() == path.resolve()]
        if len(matches) != 1 or matches[0]['bytes'] != len(raw) or matches[0]['sha256'] != hashlib.sha256(raw).hexdigest():
            raise ValueError('Frozen AC-AF checksum or size mismatch')
    class NonfiniteToken(str):
        pass
    payload = json.loads(raw.decode('utf-8'), parse_constant=NonfiniteToken)
    allowed = set()
    if isinstance(payload, dict):
        for i, item in enumerate(payload.get('iterations', [])):
            evaluation = item.get('evaluation', {}) if isinstance(item, dict) else {}
            value = evaluation.get('fmx_loss')
            if isinstance(value, NonfiniteToken):
                if value != 'Infinity' or evaluation.get('decision') != 'crash' or evaluation.get('disqualified') is not True:
                    raise ValueError('Only positive Infinity for a disqualified CRASH loss is permitted')
                allowed.add(('iterations', i, 'evaluation', 'fmx_loss'))
    def sanitize(value, position=()):
        if isinstance(value, NonfiniteToken):
            if position not in allowed:
                raise ValueError('Non-finite measurement or unqualified loss')
            return {'nonfinite_source_token': str(value), 'meaning': 'DISQUALIFIED_CRASH_LOSS_NOT_A_MEASUREMENT'}
        if isinstance(value, float):
            finite_number(value, 'JSON number')
        if isinstance(value, list):
            return [sanitize(v, position + (i,)) for i, v in enumerate(value)]
        if isinstance(value, dict):
            return {k: sanitize(v, position + (k,)) for k, v in value.items()}
        return value
    return sanitize(payload)


def _verified_prior_yzab_output(path, expected):
    path = _offline_path(path)
    if path.resolve() == expected.resolve():
        entries = local_json(YZAB_ARTIFACTS / 'final_validation.json')['bindings']
        matches = [e for e in entries if (ROOT / e['path']).resolve() == path.resolve()]
        raw = path.read_bytes()
        if len(matches) != 1 or matches[0]['sha256'] != hashlib.sha256(raw).hexdigest() or matches[0]['bytes'] != len(raw):
            raise ValueError('Prior Y-AB output checksum or size mismatch')
    return local_json(path)


def _measurement_from_normalized32(item):
    if 'certified_wds_evidence' not in item:
        return _measurement_from_normalized26(item)
    values = {name: item[name] for name in CertifiedWDSMeasurement.__dataclass_fields__}
    for end in ('ap_policy', 'cpe_policy'):
        if values[end] is not None:
            policy = dict(values[end])
            policy['aql_by_ac'] = tuple(tuple(pair) for pair in policy['aql_by_ac'])
            values[end] = CrossLayerEndpointPolicy(**policy)
    for name in ('goodputs_mbps', 'rtts_ms', 'flags', 'associated_cpes', 'repetition_blocks'):
        values[name] = tuple(values[name])
    row = CertifiedWDSMeasurement(**values)
    if row.policy_key != item['policy_key']:
        raise ValueError('Prior Y-AB policy identity disagrees')
    return row


def _new_exact_campaign_receipts(receipt_paths):
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 10:
        raise ValueError('Require 1..10 frozen R33-R42 receipts')
    seen = set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_acaf_json(path)
        if payload is None:
            yield None, None, dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True)
            continue
        number = _physical_round_number(payload, max_round=42)
        if not 33 <= number <= 42 or number in seen:
            raise ValueError('Unique R33-R42 receipt identities required')
        seen.add(number)
        ref = dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size,
                   experiment_id=payload['experiment_id'], timestamp_utc=payload.get('timestamp_utc'))
        yield number, payload, ref


def _exact_campaign_recipe_ref(number):
    matches = [e for e in local_json(ACAF_ARTIFACTS / 'inputs_manifest.json')['entries']
               if e['round'] == number and e['path'].endswith('.py')]
    if len(matches) != 1:
        raise ValueError('One frozen campaign recipe required')
    entry = deepcopy(matches[0])
    path = (ROOT / entry['path']).resolve()
    if not path.is_relative_to(ACAF_INPUTS.resolve()):
        raise ValueError('Recipe must remain inside frozen inputs')
    raw = path.read_bytes()
    if entry['bytes'] != len(raw) or entry['sha256'] != hashlib.sha256(raw).hexdigest():
        raise ValueError('Frozen campaign recipe checksum or size mismatch')
    return entry, 'phy0-ap0.sta1' in raw.decode('utf-8')


def _exact_campaign_context(number, payload, item):
    expected = ('bidir_12flow', 12, True) if number == 36 else (
        ('bidir_8flow', 8, True) if number in (37, 38) else (
        ('unidir_ul_2flow', 2, False) if number == 39 else ('bidir_6flow', 6, True)))
    for source in (payload, item, item['candidate_knobs']):
        for key in ('traffic_regime', 'workload_regime'):
            if key in source and source[key] != expected[0]:
                raise ValueError('Campaign workload conflicts with frozen round recipe')
        if 'active_flow_count' in source and exact_integer(source['active_flow_count'], 'active flows', 1, 1000) != expected[1]:
            raise ValueError('Campaign flow count conflicts')
        if 'bidirectional' in source and (type(source['bidirectional']) is not bool or source['bidirectional'] != expected[2]):
            raise ValueError('Campaign direction conflicts')
    distance, coverage = ((3000, 6) if number in (33, 34) else (6000, 13) if number == 35 else (None, None))
    for source in (item, item['candidate_knobs']):
        for key, value in (('distance_m', distance), ('distance_meters', distance), ('coverage_class', coverage)):
            if key in source and (value is None or exact_integer(source[key], key, 0, 100000) != value):
                raise ValueError('Campaign programmed timing context conflicts')
    return expected, distance, coverage


def _exact_campaign_block_rows(payload, *, max_round=42):
    # R81/R82 saved the same crossover coordinate under an explicit alias.
    # Adapt a copy, retain provenance, and never invent a missing coordinate.
    number = _physical_round_number(payload, max_round=max_round)
    step_alias = number in (81, 82, 87) or 103 <= number <= 134
    if step_alias:
        payload = deepcopy(payload)
        schemas = set()
        for item in payload.get('iterations', []):
            for block in item.get('repetition_blocks', []):
                step = exact_integer(block.get('step_in_block'), 'recorded step_in_block', 1, 2)
                schemas.add('crossover_step' in block)
                if 'crossover_step' in block and exact_integer(block['crossover_step'], 'crossover_step', 0, 1) != step - 1:
                    raise ValueError('Conflicting recorded crossover coordinates')
                block['crossover_step'] = step - 1
        if len(schemas) != 1:
            raise ValueError('Mixed recorded crossover coordinate schemas')
    rows = _certified_block_rows(payload, max_round=max_round)
    items = {a['commit']: a for a in payload['iterations']}
    raw_blocks = {(a['commit'], b['block_index'], b['crossover_step']): b
                  for a in payload['iterations'] for b in a['repetition_blocks']}
    for row in rows:
        if step_alias:
            row.update(source_step_field='step_in_block', source_step_in_block=row['crossover_step'] + 1,
                       crossover_step_mapping='EXPLICIT_ONE_BASED_SOURCE_MINUS_ONE')
        raw = raw_blocks[row['treatment_id'], row['block_index'], row['crossover_step']]
        if 'observation' in raw:
            observation = raw['observation']
            if not isinstance(observation, dict):
                raise ValueError('Recorded block observation must be an object')
            for key, value in row['observation'].items():
                if key in observation and finite_number(observation[key], key) != value:
                    raise ValueError('Nested block observation conflicts with recorded block metrics')
            for key in ('station_drops', 'restoration_verified'):
                if key in observation:
                    value = observation[key]
                    if key == 'station_drops':
                        exact_integer(value, key)
                    elif type(value) is not bool:
                        raise ValueError('Recorded block restoration must be boolean')
                    row['observation'][key] = value
            row['recorded_block_observation'] = deepcopy(observation)
            row['quality_evidence'] = 'RECORDED_NESTED_BLOCK_OBSERVATION_NOT_INDEPENDENT_DEVICE_ACCEPTANCE'
        evaluation = items[row['treatment_id']].get('evaluation', {})
        row['source_evaluation'] = deepcopy(evaluation)
        row['source_failure_metadata'] = dict(
            crash=evaluation.get('decision') == 'crash', disqualified=evaluation.get('disqualified'),
            reason=evaluation.get('reason'), fmx_loss=deepcopy(evaluation.get('fmx_loss')),
            oom_cause='OPERATOR_NARRATIVE_NOT_ESTABLISHED_BY_RECEIPT_EVENT_LOG')
    return rows


def load_all42_measurements(receipt_paths=R33_TO_R42_RECEIPTS, *, base_dataset_path=R32_NORMALIZED_OUTPUT,
                            include_auxiliary=True):
    """Preserve all150 prior records and add the actual34 campaign arms."""
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _verified_prior_yzab_output(base_dataset_path, R32_NORMALIZED_OUTPUT)
    if not isinstance(base, dict) or base.get('schema_version') != 7 or not isinstance(base.get('records'), list):
        raise ValueError('Frozen Y-AB normalized schema7 required')
    try:
        records = [_measurement_from_normalized32(a) for a in base['records']]
    except (TypeError, KeyError) as error:
        raise ValueError('Malformed prior Y-AB record') from error
    if any(not 1 <= int(r.round_id[1:]) <= 32 for r in records) or len({(r.round_id, r.iteration) for r in records}) != len(records):
        raise ValueError('Prior Y-AB record identities conflict')
    refs = deepcopy(base['source_refs'])
    for number, payload, ref in _new_exact_campaign_receipts(receipt_paths):
        refs.append(ref)
        if payload is None:
            continue
        blocks = _exact_campaign_block_rows(payload)
        recipe_ref, interface_named = _exact_campaign_recipe_ref(number)
        for index, source_item in enumerate(payload['iterations']):
            (regime, flows, bidirectional), distance, coverage = _exact_campaign_context(number, payload, source_item)
            item = deepcopy(source_item)
            item['distance_meters'] = distance
            selected = [b for b in blocks if b['treatment_id'] == item['commit']]
            window = _physical_window(item, number, index, selected)
            values = {name: getattr(window, name) for name in ThreeTierMeasurement.__dataclass_fields__}
            values.update(workload_regime=regime, active_flow_count=flows, bidirectional=bidirectional)
            evidence = _certified_summary_evidence(window, item, selected, ref, recipe_ref, interface_named)
            comparisons = {'goodput_mbps': (window.goodput_mbps, [b['observation']['goodput_rx_mbps'] for b in selected]),
                'dl_goodput_mbps': (window.dl_goodput_mbps, [b['dl_goodput_mbps'] for b in selected]),
                'ul_goodput_mbps': (window.ul_goodput_mbps, [b['ul_goodput_mbps'] for b in selected]),
                'jain_fairness': (window.jain_fairness, [b['observation']['jain_fairness'] for b in selected])}
            float_deltas = {key: reported - sum(vs) / len(vs) for key, (reported, vs) in comparisons.items()}
            quantile_deltas = [float(a - b) for a, b in zip(
                (window.p50_ms, window.p95_ms, window.p99_ms), np.percentile(window.rtts_ms, [50, 95, 99]))]
            failure = deepcopy(selected[0]['source_failure_metadata'])
            evidence.update(block_mean_float_deltas=float_deltas,
                block_mean_float_consistent=all(v == 0 for v in float_deltas.values()),
                block_mean_float_definition='Python sum(recorded floats)/number of blocks, in saved order',
                block_mean_numpy_consistent=all(v == 0 for v in evidence['block_mean_numpy_deltas'].values()),
                numpy_quantile_deltas=quantile_deltas, exact_numpy_quantiles=all(v == 0 for v in quantile_deltas),
                source_evaluation=deepcopy(item.get('evaluation', {})), source_failure_metadata=failure,
                recorded_window_observation=deepcopy(item['observation']),
                programmed_distance_source_field='distance_m' if distance is not None else 'NOT_RECORDED',
                physical_distance_verified=False, coverage_class=coverage)
            flags = list(values['flags'])
            if not evidence['block_mean_consistent']:
                flags.append('literal_exact_block_mean_certification_FAILED')
            if not evidence['block_mean_float_consistent']:
                flags.append('literal_Python_float_block_mean_certification_FAILED')
            if not evidence['mac_block_sums_match_window']:
                flags.append('window_MAC_counters_disagree_with_block_sums')
            if failure['crash'] or failure['disqualified']:
                flags.extend(('source_CRASH_or_disqualification_preserved', 'not_eligible_for_controller_promotion'))
            values['flags'] = tuple(dict.fromkeys(flags))
            records.append(ExactCampaignMeasurement(**values, **_lower_mac_declarations(item),
                lower_mac_evidence='SHARED_AP_CPE_RECIPE_FIELDS_NOT_EFFECTIVE_FIRMWARE_TIMING_OR_CONTROL_PROOF',
                rtt_pool_order='CONCATENATED_BLOCK_ORDER', block_mean_consistent=evidence['block_mean_consistent'],
                raw_rtts_matches_blocks=evidence['raw_rtts_matches_blocks'], certified_wds_evidence=evidence,
                coverage_class=coverage, source_failure_metadata=failure))
    if not include_auxiliary:
        records = [r for r in records if r.window_kind == 'primary']
    records.sort(key=lambda r: (int(r.round_id[1:]), r.window_kind, r.iteration))
    return records, refs


def load_all42_block_observations(receipt_paths=R33_TO_R42_RECEIPTS, *, base_dataset_path=R32_BLOCK_OUTPUT):
    base = _verified_prior_yzab_output(base_dataset_path, R32_BLOCK_OUTPUT)
    if not isinstance(base, dict) or not all(isinstance(base.get(k), list) for k in ('crossed', 'sequential', 'source_refs')):
        raise ValueError('Frozen Y-AB crossed/sequential collections required')
    crossed, sequential, refs = (deepcopy(base[k]) for k in ('crossed', 'sequential', 'source_refs'))
    seen = set()
    for row in crossed:
        if not isinstance(row, dict) or row.get('round_id') not in {f'R{i}' for i in range(16, 33) if i != 17}:
            raise ValueError('Prior Y-AB crossed identity conflicts')
        identity = (row['round_id'], exact_integer(row.get('block_index'), 'block index'),
                    exact_integer(row.get('crossover_step'), 'crossover step'))
        if identity in seen:
            raise ValueError('Duplicate prior Y-AB crossed identity')
        seen.add(identity)
    seq_ids = [(row.get('round_id'), row.get('treatment_id'), row.get('block_index')) for row in sequential]
    if any(row.get('round_id') != 'R17' or 'crossover_step' in row for row in sequential) or len(set(seq_ids)) != len(seq_ids):
        raise ValueError('Prior R17 sequential identity conflicts')
    for _, payload, ref in _new_exact_campaign_receipts(receipt_paths):
        refs.append(ref)
        if payload is not None:
            crossed.extend(_exact_campaign_block_rows(payload))
    crossed.sort(key=lambda b: (int(b['round_id'][1:]), b['block_index'], b['crossover_step']))
    return dict(crossed=crossed, sequential=sequential, source_refs=refs)


def normalized_exact_campaign_dataset():
    records, refs = load_all42_measurements()
    blocks = load_all42_block_observations()
    new = [r for r in records if isinstance(r, ExactCampaignMeasurement)]
    return dict(schema_version=8, evidence='Frozen_Y_AB_output_plus_R33_R42_saved_campaign_receipts',
        automatic_execution_allowed=False, physical_acceptance_claim=False, software_versions=software_versions(),
        source_refs=refs, input_manifest=local_json(ACAF_ARTIFACTS / 'inputs_manifest.json'), ac_order=list(AC_ORDER),
        observed_record_count=len(records), requested_record_count=182, new_arm_count=len(new), requested_new_arm_count=32,
        primary_window_count=sum(r.window_kind == 'primary' for r in records), auxiliary_window_count=sum(r.window_kind != 'primary' for r in records),
        round_counts={f'R{i}': sum(r.round_id == f'R{i}' for r in records) for i in range(1, 43)},
        crossed_observation_count=len(blocks['crossed']), requested_crossed_observation_count=540,
        matched_round_scoped_block_count=len({(b['round_id'], b['block_index']) for b in blocks['crossed']}),
        requested_matched_block_count=186, sequential_repetition_count=len(blocks['sequential']),
        literal_exact_block_mean_pass_count=sum(r.block_mean_consistent for r in new),
        Python_float_block_mean_pass_count=sum(r.certified_wds_evidence['block_mean_float_consistent'] for r in new),
        exact_numpy_quantile_pass_count=sum(r.certified_wds_evidence['exact_numpy_quantiles'] for r in new),
        raw_rtt_chronology_pass_count=sum(r.raw_rtts_matches_blocks for r in new),
        positive_MAC_denominator_count=sum(r.mac_tx_packets > 0 for r in new),
        crash_arm_count=sum(r.source_failure_metadata['crash'] for r in new),
        experimental_units='Matched round-scoped within-link blocks; R17 separate; RTTs are subsamples',
        records=[{**asdict(r), 'policy_key': r.policy_key} for r in records])


def float_ulp_distance(left, right):
    """IEEE-754 binary64 representable-step distance; signed zeros compare equal."""
    left, right = finite_number(left, 'left float'), finite_number(right, 'right float')
    if left == right:
        return 0
    def ordered(value):
        bits = int(np.float64(value).view(np.uint64))
        return (~bits & ((1 << 64) - 1)) if bits & (1 << 63) else bits | (1 << 63)
    return abs(ordered(left) - ordered(right))


def audit_dyadic_block_means(record):
    """Audit four recorded-decimal means and actual NumPy binary64 results.

    This function is read-only and accepts a normalized dictionary or dataclass.
    Dyadic input granularity and exact binary-rational arithmetic are separate
    diagnostics, so zero reported float subtraction never conceals a real delta.
    """
    item = record if isinstance(record, dict) else asdict(record)
    blocks = item.get('repetition_blocks')
    if not isinstance(blocks, (list, tuple)) or not 1 <= len(blocks) <= 10000:
        raise ValueError('Bounded nonempty saved blocks required for mean audit')
    getters = {
        'goodput_mbps': lambda b: b['observation']['goodput_rx_mbps'],
        'dl_goodput_mbps': lambda b: b['dl_goodput_mbps'],
        'ul_goodput_mbps': lambda b: b['ul_goodput_mbps'],
        'jain_fairness': lambda b: b['observation']['jain_fairness'],
    }
    fractions, floats, ulps, binary_deltas = {}, {}, {}, {}
    decimal_inputs_dyadic = True
    for name, getter in getters.items():
        reported = finite_number(item.get(name), name)
        values = [finite_number(getter(b), 'block ' + name) for b in blocks]
        decimal = [Fraction(str(v)) for v in values]
        literal = Fraction(str(reported))
        fractions[name] = str(literal - sum(decimal, Fraction(0)) / len(values))
        mean = float(np.mean(np.asarray(values, dtype=np.float64)))
        floats[name] = reported - mean
        ulps[name] = float_ulp_distance(reported, mean)
        binary_deltas[name] = str(Fraction.from_float(float(reported))
            - sum((Fraction.from_float(float(v)) for v in values), Fraction(0)) / len(values))
        decimal_inputs_dyadic &= all((v.denominator & (v.denominator - 1)) == 0 for v in [literal, *decimal])
    rational_exact = all(v == '0' for v in fractions.values())
    float_exact = all(v == 0.0 for v in floats.values())
    zero_ulp = all(v == 0 for v in ulps.values())
    exact = rational_exact and float_exact and zero_ulp
    status = ('DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' if decimal_inputs_dyadic else
              'FLOAT_AND_RATIONAL_EXACT_ZERO_ULP_NON_DYADIC_INPUTS') if exact else 'NOT_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP'
    return dict(status=status, fraction_deltas=fractions, numpy_float_deltas=floats,
        ulp_errors=ulps, binary_rational_deltas=binary_deltas,
        all_fraction_zero=rational_exact, all_float_zero=float_exact, all_zero_ulp=zero_ulp,
        all_recorded_decimal_inputs_dyadic=bool(decimal_inputs_dyadic),
        all_binary_rational_means_equal=all(v == '0' for v in binary_deltas.values()),
        block_count=len(blocks), float_reference='np.mean(dtype=float64) in saved block order',
        rational_reference='Fraction of recorded decimal values; no rounding or tolerance',
        physical_or_causal_certification=False)


@dataclass(frozen=True)
class DyadicCampaignMeasurement(ExactCampaignMeasurement):
    dyadic_mean_audit: dict | None = None

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.dyadic_mean_audit, dict):
            raise ValueError('Explicit dyadic mean audit required')
        context = {
            'R81': ('unidir_dl_2flow', 2, False, 100, 0),
            'R82': ('unidir_ul_2flow', 2, False, 100, 0),
            'R83': ('bidir_4flow', 4, True, 3000, 6),
            'R84': ('bidir_4flow', 4, True, 6000, 13),
            'R85': ('bidir_6flow', 6, True, 7500, 16),
            'R86': ('bidir_4flow', 4, True, 9000, 20),
            'R87': ('unidir_dl_2flow', 2, False, 100, 0),
            'R88': ('bidir_4flow', 4, True, 12000, 27),
            'R89': ('bidir_4flow', 4, True, 14000, 31),
            'R90': ('bidir_6flow', 6, True, 14000, 31),
            'R91': ('bidir_2flow', 2, True, 3000, 6),
            'R92': ('bidir_2flow', 2, True, 6000, 13),
        }.get(self.round_id)
        if context is not None:
            regime, flows, direction, distance, coverage = context
            if (self.workload_regime != regime or self.bidirectional is not direction
                    or type(self.active_flow_count) is not int or self.active_flow_count != flows
                    or type(self.distance_meters) is not int or self.distance_meters != distance
                    or self.coverage_class != coverage
                    or self.ap_policy.distance_meters != distance
                    or self.cpe_policy is None or self.cpe_policy.distance_meters != distance):
                raise ValueError('Typed new campaign workload/direction/context conflicts')
            applicability = audit_directional_throughput(regime, total=self.goodput_mbps,
                dl=self.dl_goodput_mbps, ul=self.ul_goodput_mbps, jain=self.jain_fairness,
                blocks=self.repetition_blocks)
            if self.certified_wds_evidence.get('directional_applicability') != applicability:
                raise ValueError('Typed directional applicability must match recorded metrics')


def _verified_agaj_json(path):
    path = _offline_path(path)
    identity = re.search(r'(?:^|_)r(\d+)(?:_|\.)', path.name)
    if identity and int(identity[1]) > 47:
        raise ValueError('R48+ inputs are outside this frozen campaign')
    if not path.is_file():
        return None
    if path.resolve().is_relative_to(AGAJ_INPUTS.resolve()):
        entries = local_json(AGAJ_ARTIFACTS / 'inputs_manifest.json')['entries']
        matches = [e for e in entries if (ROOT / e['path']).resolve() == path.resolve()]
        raw = path.read_bytes()
        if len(matches) != 1 or matches[0]['bytes'] != len(raw) or matches[0]['sha256'] != hashlib.sha256(raw).hexdigest():
            raise ValueError('Frozen AG-AJ input checksum or size mismatch')
    return local_json(path)


def _verified_prior_acaf_output(path, expected):
    path = _offline_path(path)
    if path.resolve() == expected.resolve():
        matches = [e for e in local_json(ACAF_ARTIFACTS / 'final_validation.json')['bindings']
                   if (ROOT / e['path']).resolve() == path.resolve()]
        raw = path.read_bytes()
        if len(matches) != 1 or matches[0]['bytes'] != len(raw) or matches[0]['sha256'] != hashlib.sha256(raw).hexdigest():
            raise ValueError('Prior AC-AF output checksum or size mismatch')
    return local_json(path)


def _measurement_from_normalized42(item):
    if 'source_failure_metadata' not in item:
        return _measurement_from_normalized32(item)
    values = {name: item[name] for name in ExactCampaignMeasurement.__dataclass_fields__}
    for end in ('ap_policy', 'cpe_policy'):
        if values[end] is not None:
            policy = dict(values[end])
            policy['aql_by_ac'] = tuple(tuple(pair) for pair in policy['aql_by_ac'])
            values[end] = CrossLayerEndpointPolicy(**policy)
    for name in ('goodputs_mbps', 'rtts_ms', 'flags', 'associated_cpes', 'repetition_blocks'):
        values[name] = tuple(values[name])
    record = ExactCampaignMeasurement(**values)
    if record.policy_key != item['policy_key']:
        raise ValueError('Prior AC-AF policy identity disagrees')
    return record


def _new_dyadic_campaign_receipts(receipt_paths):
    paths = tuple(receipt_paths)
    if not 1 <= len(paths) <= 5:
        raise ValueError('Require 1..5 frozen R43-R47 receipts')
    seen = set()
    for path in paths:
        path = _offline_path(path)
        payload = _verified_agaj_json(path)
        if payload is None:
            yield None, None, dict(path=str(path), status='UNKNOWN_LOCAL_ARTIFACT_ABSENT', check_complete=True)
            continue
        number = _physical_round_number(payload, max_round=47)
        if number not in ROUND_SPECS or number in seen:
            raise ValueError('Unique R43-R47 identities required')
        seen.add(number)
        spec = ROUND_SPECS[number]
        for source in (payload, *payload.get('iterations', [])):
            declarations = [source]
            if 'candidate_knobs' in source:
                declarations.append(source['candidate_knobs'])
            for declared in declarations:
                for name in ('traffic_regime', 'workload_regime'):
                    if name in declared and declared[name] != spec[1]:
                        raise ValueError('Dyadic campaign workload conflicts')
                if 'active_flow_count' in declared and exact_integer(declared['active_flow_count'], 'active flows', 1, 1000) != spec[2]:
                    raise ValueError('Dyadic campaign flow count conflicts')
                if 'bidirectional' in declared and (type(declared['bidirectional']) is not bool or declared['bidirectional'] != spec[3]):
                    raise ValueError('Dyadic campaign direction conflicts')
        yield number, payload, dict(round_id=f'R{number}', path=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(), bytes=path.stat().st_size,
            experiment_id=payload['experiment_id'], timestamp_utc=payload.get('timestamp_utc'))


def _dyadic_campaign_recipe_ref(number):
    matches = [e for e in local_json(AGAJ_ARTIFACTS / 'inputs_manifest.json')['entries']
               if e['round'] == number and e['path'].endswith('.py')]
    if len(matches) != 1:
        raise ValueError('One frozen dyadic campaign recipe required')
    entry = deepcopy(matches[0]); path = (ROOT / entry['path']).resolve()
    if not path.is_relative_to(AGAJ_INPUTS.resolve()):
        raise ValueError('Recipe must stay in frozen dyadic inputs')
    raw = path.read_bytes()
    if entry['bytes'] != len(raw) or entry['sha256'] != hashlib.sha256(raw).hexdigest():
        raise ValueError('Frozen dyadic recipe checksum or size mismatch')
    return entry, 'phy0-ap0.sta1' in raw.decode('utf-8')


def load_all47_measurements(receipt_paths=R43_TO_R47_RECEIPTS, *, base_dataset_path=R42_NORMALIZED_OUTPUT,
                            include_auxiliary=True):
    """Preserve all184 prior dictionaries and append ten new saved arm summaries."""
    if type(include_auxiliary) is not bool:
        raise ValueError('Auxiliary selector must be boolean')
    base = _verified_prior_acaf_output(base_dataset_path, R42_NORMALIZED_OUTPUT)
    if not isinstance(base, dict) or base.get('schema_version') != 8 or not isinstance(base.get('records'), list):
        raise ValueError('Frozen AC-AF normalized schema8 required')
    try:
        records = [_measurement_from_normalized42(item) for item in base['records']]
    except (TypeError, KeyError) as error:
        raise ValueError('Malformed prior AC-AF record') from error
    if any(not 1 <= int(r.round_id[1:]) <= 42 for r in records) or len({(r.round_id, r.iteration) for r in records}) != len(records):
        raise ValueError('Prior AC-AF record identity conflicts')
    refs = deepcopy(base['source_refs'])
    for number, payload, ref in _new_dyadic_campaign_receipts(receipt_paths):
        refs.append(ref)
        if payload is None:
            continue
        blocks = _exact_campaign_block_rows(payload, max_round=47)
        recipe, interface_named = _dyadic_campaign_recipe_ref(number)
        for position, item in enumerate(payload['iterations']):
            selected = [b for b in blocks if b['treatment_id'] == item['commit']]
            window = _physical_window(item, number, position, selected)
            values = {name: getattr(window, name) for name in ThreeTierMeasurement.__dataclass_fields__}
            spec = ROUND_SPECS[number]
            values.update(workload_regime=spec[1], active_flow_count=spec[2], bidirectional=spec[3])
            audit = audit_dyadic_block_means(window)
            evidence = _certified_summary_evidence(window, item, selected, ref, recipe, interface_named)
            comparisons = {'goodput_mbps': [b['observation']['goodput_rx_mbps'] for b in selected],
                'dl_goodput_mbps': [b['dl_goodput_mbps'] for b in selected],
                'ul_goodput_mbps': [b['ul_goodput_mbps'] for b in selected],
                'jain_fairness': [b['observation']['jain_fairness'] for b in selected]}
            floats = {name: getattr(window, name) - sum(vs) / len(vs) for name, vs in comparisons.items()}
            qd = [float(a-b) for a,b in zip((window.p50_ms,window.p95_ms,window.p99_ms), np.percentile(window.rtts_ms,[50,95,99]))]
            failure = deepcopy(selected[0]['source_failure_metadata'])
            evidence.update(block_mean_float_deltas=floats, block_mean_float_consistent=all(v==0 for v in floats.values()),
                block_mean_float_definition='Python sum(recorded floats)/number of blocks, in saved order',
                block_mean_numpy_consistent=audit['all_float_zero'], dyadic_mean_audit=audit,
                numpy_quantile_deltas=qd, exact_numpy_quantiles=all(v==0 for v in qd),
                source_evaluation=deepcopy(item.get('evaluation',{})), source_failure_metadata=failure,
                recorded_window_observation=deepcopy(item['observation']),coverage_class=None,
                physical_distance_verified=False,programmed_distance_source_field='NOT_RECORDED')
            flags=list(values['flags'])
            if not evidence['block_mean_consistent']:
                flags.append('literal_exact_block_mean_certification_FAILED')
            if not audit['all_float_zero'] or not audit['all_zero_ulp']:
                flags.append('literal_NumPy_float_zero_ULP_mean_certification_FAILED')
            if not evidence['mac_block_sums_match_window']:
                flags.append('window_MAC_counters_disagree_with_block_sums')
            if failure['crash'] or failure['disqualified']:
                flags.extend(('source_CRASH_or_disqualification_preserved','not_eligible_for_controller_promotion'))
            values['flags']=tuple(dict.fromkeys(flags))
            records.append(DyadicCampaignMeasurement(**values,**_lower_mac_declarations(item),
                lower_mac_evidence='SHARED_AP_CPE_RECIPE_FIELDS_NOT_EFFECTIVE_FIRMWARE_TIMING_OR_CONTROL_PROOF',
                rtt_pool_order='CONCATENATED_BLOCK_ORDER',block_mean_consistent=evidence['block_mean_consistent'],
                raw_rtts_matches_blocks=evidence['raw_rtts_matches_blocks'],certified_wds_evidence=evidence,
                coverage_class=None,source_failure_metadata=failure,dyadic_mean_audit=audit))
    if not include_auxiliary:
        records=[r for r in records if r.window_kind=='primary']
    records.sort(key=lambda r:(int(r.round_id[1:]),r.window_kind,r.iteration))
    return records,refs


def load_all47_block_observations(receipt_paths=R43_TO_R47_RECEIPTS, *, base_dataset_path=R42_BLOCK_OUTPUT):
    base = _verified_prior_acaf_output(base_dataset_path,R42_BLOCK_OUTPUT)
    if not isinstance(base,dict) or not all(isinstance(base.get(k),list) for k in ('crossed','sequential','source_refs')):
        raise ValueError('Frozen AC-AF crossed/sequential collections required')
    crossed,sequential,refs=(deepcopy(base[k]) for k in ('crossed','sequential','source_refs'))
    identities=set()
    for row in crossed:
        if not isinstance(row,dict) or row.get('round_id') not in {f'R{i}' for i in range(16,43) if i!=17}:
            raise ValueError('Prior AC-AF crossed identity conflicts')
        key=(row['round_id'],exact_integer(row.get('block_index'),'block index'),exact_integer(row.get('crossover_step'),'crossover step'))
        if key in identities:
            raise ValueError('Duplicate prior AC-AF crossed identity')
        identities.add(key)
    seqids=[(b.get('round_id'),b.get('treatment_id'),b.get('block_index')) for b in sequential]
    if any(b.get('round_id')!='R17' or 'crossover_step' in b for b in sequential) or len(set(seqids))!=len(seqids):
        raise ValueError('Prior R17 sequential identity conflicts')
    for _,payload,ref in _new_dyadic_campaign_receipts(receipt_paths):
        refs.append(ref)
        if payload is not None:
            crossed.extend(_exact_campaign_block_rows(payload,max_round=47))
    crossed.sort(key=lambda b:(int(b['round_id'][1:]),b['block_index'],b['crossover_step']))
    return dict(crossed=crossed,sequential=sequential,source_refs=refs)


def normalized_dyadic_campaign_dataset():
    records,refs=load_all47_measurements();blocks=load_all47_block_observations()
    new=[r for r in records if isinstance(r,DyadicCampaignMeasurement)]
    return dict(schema_version=9,evidence='Frozen_AC_AF_output_plus_R43_R47_saved_dyadic_campaign',
        automatic_execution_allowed=False,physical_acceptance_claim=False,software_versions=software_versions(),
        source_refs=refs,input_manifest=local_json(AGAJ_ARTIFACTS/'inputs_manifest.json'),ac_order=list(AC_ORDER),
        observed_record_count=len(records),primary_window_count=sum(r.window_kind=='primary' for r in records),
        auxiliary_window_count=sum(r.window_kind!='primary' for r in records),new_arm_count=len(new),
        round_counts={f'R{i}':sum(r.round_id==f'R{i}' for r in records) for i in range(1,48)},
        crossed_observation_count=len(blocks['crossed']),
        matched_round_scoped_block_count=len({(b['round_id'],b['block_index']) for b in blocks['crossed']}),
        sequential_repetition_count=len(blocks['sequential']),
        dyadic_exact_arm_count=sum(r.dyadic_mean_audit['status']=='DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP' for r in new),
        raw_rtt_chronology_pass_count=sum(r.raw_rtts_matches_blocks for r in new),
        positive_MAC_denominator_count=sum(r.mac_tx_packets>0 for r in new),
        records=[{**asdict(r),'policy_key':r.policy_key} for r in records])


def main(argv=None):
    parser=argparse.ArgumentParser(description='Normalize frozenR1..R9 offline measurement windows')
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--all-rounds14',action='store_true',help='Additive R1-R14 cross-layer corpus, with auxiliary summaries')
    group.add_argument('--all-rounds15',action='store_true',help='Add R15 separate AP/CPE states from owned snapshots')
    group.add_argument('--all-rounds21',action='store_true',help='Add frozen R16-R21 genuine blocks, ACK policies and CPU telemetry')
    group.add_argument('--all-rounds26',action='store_true',help='Add frozen R22-R26 lower-MAC declarations and physical blocks')
    group.add_argument('--all-rounds32',action='store_true',help='Add frozen R27-R32 saved WDS campaign with explicit certification checks')
    group.add_argument('--all-rounds42',action='store_true',help='Add frozen R33-R42 exact campaign and preserved failure metadata')
    group.add_argument('--all-rounds47',action='store_true',help='Add frozen R43-R47 dyadic float/rational and zero-ULP audit')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(argv)
    data=normalized_dyadic_campaign_dataset() if args.all_rounds47 else normalized_exact_campaign_dataset() if args.all_rounds42 else normalized_certified_wds_dataset() if args.all_rounds32 else normalized_lower_mac_dataset() if args.all_rounds26 else normalized_real_crossover_dataset() if args.all_rounds21 else normalized_asymmetric_dataset() if args.all_rounds15 else normalized_cross_layer_dataset() if args.all_rounds14 else normalized_regime_dataset()
    output=args.output or (AGAJ_ARTIFACTS/'normalized_r1_to_r47_measurements_20261024.json' if args.all_rounds47 else ACAF_ARTIFACTS/'normalized_r1_to_r42_measurements_20261024.json' if args.all_rounds42 else YZAB_ARTIFACTS/'normalized_r1_to_r32_measurements_20261024.json' if args.all_rounds32 else UVWX_ARTIFACTS/'normalized_r1_to_r26_measurements_20261024.json' if args.all_rounds26 else QRST_ARTIFACTS/'normalized_r1_to_r21_measurements_20261024.json' if args.all_rounds21 else MNOP_ARTIFACTS/'normalized_r1_to_r15_measurements_20261024.json' if args.all_rounds15 else IJKL_ARTIFACTS/'normalized_r1_to_r14_measurements_20261024.json' if args.all_rounds14 else EFGH_ARTIFACTS/'normalized_r1_to_r9_measurements_20261024.json')
    write_json(output,data)
    print(f'NORMALIZED_OFFLINE_WINDOWS={len(data["records"])}: {output}')
    return 0


if __name__=='__main__':
    raise SystemExit(main())


def audit_directional_throughput(regime, *, total, dl, ul, jain, blocks):
    """Source arithmetic/applicability, not an extra directional QoE observation.

    Unidirectional total and active throughput are one hypothesis. Require exact
    recorded equality and explicit zero on the inactive leg for every saved
    arm/block; retain Jain literally while marking it inapplicable to inference.
    """
    supported = ('unidir_dl_2flow', 'unidir_ul_2flow', 'unidir_ul_8flow_hammer', 'bidir_2flow',
                 'bidir_4flow', 'bidir_6flow', 'bidir_8flow')
    if type(regime) is not str or regime not in supported:
        raise ValueError('Explicit supported workload regime required')
    if not isinstance(blocks, (list, tuple)) or not 1 <= len(blocks) <= 10000:
        raise ValueError('Bounded recorded blocks required for directional audit')
    total, dl, ul = (finite_number(v, name, 0, 10000) for v, name in
                     ((total, 'total'), (dl, 'DL'), (ul, 'UL')))
    jain = finite_number(jain, 'literal recorded Jain', 0, 1)
    active = 'DL' if regime == 'unidir_dl_2flow' else 'UL' if regime in ('unidir_ul_2flow', 'unidir_ul_8flow_hammer') else None
    sources = [(total, dl, ul)]
    for block in blocks:
        if not isinstance(block, dict) or not isinstance(block.get('observation'), dict):
            raise ValueError('Recorded block metrics required')
        sources.append(tuple(finite_number(v, name, 0, 10000) for v, name in (
            (block['observation'].get('goodput_rx_mbps'), 'block total'),
            (block.get('dl_goodput_mbps'), 'block DL'), (block.get('ul_goodput_mbps'), 'block UL'))))
        finite_number(block['observation'].get('jain_fairness'), 'literal block Jain', 0, 1)
    if active:
        for recorded_total, recorded_dl, recorded_ul in sources:
            current, inactive = (recorded_dl, recorded_ul) if active == 'DL' else (recorded_ul, recorded_dl)
            if Fraction(str(current)) != Fraction(str(recorded_total)) or inactive != 0:
                raise ValueError('Unidirectional active throughput must exactly equal total with explicit inactive zero')
    return dict(regime=regime, active_direction=active,
        active_direction_equals_total_every_arm_and_block=True if active else None,
        inactive_direction_zero_every_arm_and_block=True if active else None,
        active_total_alias_definition='EXACT_RECORDED_DECIMAL_FRACTION_EQUALITY' if active else 'NOT_UNIDIRECTIONAL',
        jain_applicable_for_QoE_inference=active is None,
        inactive_direction_applicable_for_QoE_inference=False if active else None,
        literal_recorded_jain=jain,
        required_QoE_metrics=['p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'goodput_rx_mbps'] if active else
            ['p50_rtt_ms', 'p95_rtt_ms', 'p99_rtt_ms', 'ul_goodput_mbps', 'jain_fairness'],
        duplicate_active_throughput_hypothesis=False, physical_direction_independently_verified=False)


@dataclass(frozen=True)
class SourcePackageMeasurement(DyadicCampaignMeasurement):
    """Additional literal saved controls; neither firmware effect nor actuation."""
    new_source_controls: dict | None = None

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.new_source_controls, dict) or set(self.new_source_controls) - {'rts_threshold','ap_ack_clocking'}:
            raise ValueError('Explicit supported source-control object required')
        controls = self.new_source_controls
        if 'rts_threshold' in controls:
            value = controls['rts_threshold']
            if type(value) is not str or not (value == 'off' or value.isascii() and value.isdecimal() and str(int(value)) == value and 1 <= int(value) <= 65535):
                raise ValueError('RTS must be literal off or canonical positive decimal <=65535')
            expected = None if value == 'off' else int(value)
            if self.cpe_policy is None or any(p.rts_threshold != expected for p in (self.ap_policy,self.cpe_policy)):
                raise ValueError('Shared RTS source declaration must match both endpoints')
        if 'ap_ack_clocking' in controls and type(controls['ap_ack_clocking']) is not bool:
            raise ValueError('AP ACK-clocking declaration must be an exact boolean')
        contexts = {'R93': ('bidir_6flow', 6, True, 14000, 31),
         'R94': ('bidir_2flow', 2, True, 9000, 20),
         'R95': ('bidir_2flow', 2, True, 12000, 27),
         'R96': ('bidir_2flow', 2, True, 14000, 31),
         'R97': ('bidir_2flow', 2, True, 9000, 20),
         'R98': ('bidir_8flow', 8, True, 3000, 6),
         'R99': ('bidir_8flow', 8, True, 6000, 13),
         'R100': ('bidir_8flow', 8, True, 9000, 20),
         'R101': ('bidir_8flow', 8, True, 12000, 27),
         'R102': ('bidir_8flow', 8, True, 14000, 31),
         'R103': ('unidir_dl_2flow', 2, False, 3000, 6),
         'R104': ('unidir_dl_2flow', 2, False, 6000, 13),
         'R105': ('unidir_dl_2flow', 2, False, 9000, 20),
         'R106': ('unidir_dl_2flow', 2, False, 12000, 27),
         'R107': ('unidir_dl_2flow', 2, False, 14000, 31),
         'R108': ('unidir_ul_2flow', 2, False, 1000, 2),
         'R109': ('unidir_ul_2flow', 2, False, 3000, 6),
         'R114': ('unidir_ul_2flow', 2, False, 1000, 2),
         'R115': ('unidir_ul_2flow', 2, False, 1000, 2),
         'R116': ('unidir_ul_2flow', 2, False, 1000, 2),
         'R117': ('unidir_ul_2flow', 2, False, 3000, 6),
         'R118': ('unidir_ul_2flow', 2, False, 6000, 13),
         'R119': ('unidir_ul_2flow', 2, False, 9000, 20),
         'R120': ('unidir_ul_2flow', 2, False, 12000, 26),
         'R121': ('unidir_ul_2flow', 2, False, 14000, 31),
         'R122': ('unidir_ul_8flow_hammer', 8, False, 3000, 6),
         'R123': ('unidir_ul_8flow_hammer', 8, False, 1000, 2),
         'R124': ('unidir_ul_8flow_hammer', 8, False, 6000, 13),
         'R125': ('unidir_ul_8flow_hammer', 8, False, 9000, 20),
         'R126': ('unidir_ul_8flow_hammer', 8, False, 12000, 26),
         'R127': ('unidir_ul_8flow_hammer', 8, False, 14000, 31),
         'R128': ('unidir_ul_8flow_hammer', 8, False, 1000, 2),
         'R129': ('unidir_ul_8flow_hammer', 8, False, 3000, 6),
         'R130': ('unidir_ul_8flow_hammer', 8, False, 6000, 13),
         'R131': ('unidir_ul_8flow_hammer', 8, False, 9000, 20),
         'R132': ('unidir_ul_8flow_hammer', 8, False, 12000, 26),
         'R133': ('unidir_ul_8flow_hammer', 8, False, 14000, 31),
         'R134': ('unidir_ul_8flow_hammer', 8, False, 1000, 2)}
        if self.round_id not in contexts:
            raise ValueError('Source-package round must be an available frozen R93-R134 identity')
        regime,flows,direction,distance,coverage = contexts[self.round_id]
        if (self.workload_regime != regime or type(self.active_flow_count) is not int
                or self.active_flow_count != flows or self.bidirectional is not direction
                or type(self.distance_meters) is not int or self.distance_meters != distance
                or type(self.coverage_class) is not int or self.coverage_class != coverage
                or self.cpe_policy is None or any(type(p.distance_meters) is not int or p.distance_meters != distance for p in (self.ap_policy,self.cpe_policy))):
            raise ValueError('Typed source-package round/context/direction conflicts')
        evidence = self.certified_wds_evidence
        slot,ack = {2:(15,30),6:(27,54),13:(48,96),20:(69,138),26:(87,174),27:(90,180),31:(102,204)}[coverage]
        if (any(type(evidence.get(k)) is not int or evidence[k]!=v
                for k,v in (('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)))
                or evidence.get('physical_distance_verified') is not False
                or evidence.get('effective_timing_independently_verified') is not False
                or evidence.get('source_package_effective_actuation_verified') is not False):
            raise ValueError('Saved source context must not claim effective control or physical range')
        provenance = evidence.get('new_source_control_provenance')
        if not isinstance(provenance,dict) or provenance.get('controls')!=controls:
            raise ValueError('Typed new controls must match saved JSON/AST provenance')
        applicability = audit_directional_throughput(self.workload_regime,total=self.goodput_mbps,
                dl=self.dl_goodput_mbps,ul=self.ul_goodput_mbps,jain=self.jain_fairness,blocks=self.repetition_blocks)
        if self.certified_wds_evidence.get('directional_applicability') != applicability:
            raise ValueError('Source-package directional applicability mismatch')

    @property
    def policy_key(self):
        result = json.loads(super().policy_key)
        if self.new_source_controls:
            result[0]['new_source_controls'] = deepcopy(self.new_source_controls)
            if 'rts_threshold' in self.new_source_controls:
                result[1]['new_source_controls'] = {'rts_threshold':self.new_source_controls['rts_threshold']}
        return json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)


def recorded_uplink_package(row):
    """Describe literal R116-R134 packages after the caller authenticates input.

    This additive view leaves every historical serialization and policy key
    unchanged. A batch label, DSCP boolean or filename cannot supply a formula,
    packet-size classifier, effective actuator or general distance law.
    """
    if (not isinstance(row, dict) or type(row.get('round_id')) is not str or
            not re.fullmatch(r'R(?:11[6-9]|12[0-9]|13[0-4])', row['round_id'])):
        raise ValueError('A recorded R116-R134 uplink package is required')
    number = int(row['round_id'][1:])
    regime, flows = ('unidir_ul_2flow', 2) if number <= 121 else ('unidir_ul_8flow_hammer', 8)
    if (row.get('workload_regime') != regime or type(row.get('active_flow_count')) is not int
            or row['active_flow_count'] != flows or row.get('bidirectional') is not False):
        raise ValueError('Exact uplink workload identity required')
    evidence = row.get('certified_wds_evidence')
    if not isinstance(evidence, dict):
        raise ValueError('Source evidence must be an object')
    controls = row.get('new_source_controls')
    provenance = evidence.get('new_source_control_provenance')
    if (not isinstance(provenance, dict) or not isinstance(controls, dict)
            or set(controls) - {'rts_threshold', 'ap_ack_clocking'}
            or controls != provenance.get('controls')):
        raise ValueError('Literal controls must match bound source provenance')
    if number >= 122 and set(controls) != {'rts_threshold', 'ap_ack_clocking'}:
        raise ValueError('UL8 needs explicit RTS and ACK-clocking declarations')
    rts = controls.get('rts_threshold')
    if 'rts_threshold' in controls and (type(rts) is not str or not (rts == 'off' or
            rts.isascii() and rts.isdecimal() and str(int(rts)) == rts and 1 <= int(rts) <= 65535)):
        raise ValueError('Canonical RTS declaration required')
    clock = controls.get('ap_ack_clocking')
    if 'ap_ack_clocking' in controls and type(clock) is not bool:
        raise ValueError('ACK-clocking declaration must be an exact boolean')
    contexts = {116:(1000,2),117:(3000,6),118:(6000,13),119:(9000,20),120:(12000,26),121:(14000,31),
        122:(3000,6),123:(1000,2),124:(6000,13),125:(9000,20),126:(12000,26),127:(14000,31),
        128:(1000,2),129:(3000,6),130:(6000,13),131:(9000,20),132:(12000,26),133:(14000,31),134:(1000,2)}
    meters, coverage = contexts[number]
    if (type(row.get('distance_meters')) is not int or row['distance_meters'] != meters
            or type(row.get('coverage_class')) is not int or row['coverage_class'] != coverage
            or type(evidence.get('coverage_class')) is not int or evidence['coverage_class'] != coverage
            or type(row.get('iteration')) is not str or not row['iteration']):
        raise ValueError('Exact recorded round distance, coverage and arm identity required')
    for endpoint in ('ap_policy', 'cpe_policy'):
        policy = row.get(endpoint)
        if (not isinstance(policy, dict) or type(policy.get('distance_meters')) is not int
                or policy['distance_meters'] != meters):
            raise ValueError('Endpoint must agree with the recorded distance context')
        pairs = policy.get('aql_by_ac')
        if (not isinstance(pairs, (list, tuple)) or len(pairs) != 4 or any(
                not isinstance(pair, (list, tuple)) or len(pair) != 2 or
                any(type(v) is not int or v <= 0 for v in pair) or pair[0] > pair[1] for pair in pairs)):
            raise ValueError('Four literal ordered AQL pairs required')
        if rts is not None and policy.get('rts_threshold') != (None if rts == 'off' else int(rts)):
            raise ValueError('RTS declaration conflicts with endpoint policy')
        for name in ('fq_target_us', 'tcp_limit_output_bytes'):
            if type(policy.get(name)) is not int or policy[name] <= 0:
                raise ValueError('Positive literal endpoint controls required')
    if (evidence.get('physical_distance_verified') is not False or
            evidence.get('source_package_effective_actuation_verified') is not False):
        raise ValueError('Saved package cannot establish physical control')
    return dict(round_id=row['round_id'], iteration=row['iteration'], workload_regime=regime,
        distance_meters=row['distance_meters'], coverage_class=row['coverage_class'],
        ap_be_us=list(row['ap_policy']['aql_by_ac'][2]), cpe_be_us=list(row['cpe_policy']['aql_by_ac'][2]),
        cpe_tcp_limit_output_bytes=row['cpe_policy']['tcp_limit_output_bytes'],
        cpe_fq_target_us=row['cpe_policy']['fq_target_us'], rts_declared=rts,
        ap_ack_clocking_declared=clock, source_controls=deepcopy(controls),
        source_receipt=deepcopy(evidence.get('source_receipt')),
        source_recipe=deepcopy(evidence.get('source_recipe')),
        logarithmic_formula=None, interpolation_allowed=False,
        pure_ac_vo_max_packet_bytes=None, pure_ac_vo_160_verified=False,
        traffic_classifier_status='UNKNOWN_NOT_QUALIFIED_BY_NORMALIZED_RECEIPT',
        adaptive_rts_control_law_verified=False, physical_acceptance=False,
        automatic_execution_allowed=False)


@dataclass(frozen=True)
class HmacVoIPMeasurement(DyadicCampaignMeasurement):
    """Separate saved hMAC-labelled workload; not a firmware scheduler proof."""
    hmac_source_controls: dict | None = None
    voip_probe_tos: str | None = None
    voip_evidence: dict | None = None

    def __post_init__(self):
        super().__post_init__()
        contexts={'R135':(1000,2,15,30),'R136':(3000,6,27,48),'R137':(6000,13,48,69),
                  'R138':(9000,20,69,90),'R139':(12000,26,87,108)}
        if self.round_id not in contexts:raise ValueError('Round absent from fixed available hMAC cutoff')
        distance,coverage,slot,ack=contexts[self.round_id]
        if (self.workload_regime!='bidir_8flow_voip_hmac' or type(self.active_flow_count)is not int
                or self.active_flow_count!=8 or self.bidirectional is not True
                or type(self.distance_meters)is not int or self.distance_meters!=distance
                or type(self.coverage_class)is not int or self.coverage_class!=coverage
                or self.cpe_policy is None or any(type(p.distance_meters)is not int or p.distance_meters!=distance for p in (self.ap_policy,self.cpe_policy))
                or self.voip_probe_tos!='0xb8'):
            raise ValueError('Exact hMAC/VoIP saved context required; ordinary bidir8 is not an alias')
        evidence=self.certified_wds_evidence
        for name,value in (('coverage_class',coverage),('slot_time_us',slot),('ack_timeout_us',ack)):
            if type(evidence.get(name))is not int or evidence[name]!=value:raise ValueError('Typed shared timing conflict')
        if evidence.get('physical_distance_verified')is not False or evidence.get('effective_timing_independently_verified')is not False:
            raise ValueError('Saved declarations cannot certify physical or effective timing')
        if not isinstance(self.hmac_source_controls,dict)or set(self.hmac_source_controls)!={'tx_aggr_factor','fq_flows'}:
            raise ValueError('Explicit hMAC-labelled package coordinates required')
        exact_integer(self.hmac_source_controls['tx_aggr_factor'],'tx_aggr_factor',0,255)
        exact_integer(self.hmac_source_controls['fq_flows'],'fq_flows',1,1_000_000)
        if not isinstance(self.voip_evidence,dict)or self.voip_evidence.get('effective_AC_mapping_verified')is not False:
            raise ValueError('VoIP evidence is distinct from effective queue mapping')
        if any(self.voip_evidence.get(k)is not None for k in ('latency_ms','jitter_ms','packet_loss_pct','mos')):
            raise ValueError('No separately identified voice metrics exist in this frozen schema')
        if len(self.repetition_blocks)!=16:raise ValueError('Exactly16 saved within-link blocks required')
        if type(self.restoration_verified)is not bool:raise ValueError('Window restoration must be a reported boolean')
        exact_integer(self.station_drops,'window station drops')
        if self.source_failure_metadata.get('disqualified')is not None and type(self.source_failure_metadata['disqualified'])is not bool:
            raise ValueError('Disqualification must be boolean or unknown')

    @property
    def policy_key(self):
        endpoints=json.loads(super().policy_key)
        for endpoint in endpoints:
            if endpoint is not None:
                endpoint.update(self.hmac_source_controls)
                endpoint.update(workload_identity='bidir_8flow_voip_hmac',voip_probe_tos=self.voip_probe_tos)
        return json.dumps(endpoints,sort_keys=True,separators=(',',':'))


# Stage13 is additive. Historical constructors, loaders and default CLI stay intact.
def load_stage13_sync_dataset(*,manifest_path,expected_manifest_sha256):
    from orchestration.autoresearch.fmx_stage13_sync import load_stage13_sync_dataset as load
    return load(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)


def load_stage13_sync_blocks(*,manifest_path,expected_manifest_sha256):
    from orchestration.autoresearch.fmx_stage13_sync import load_stage13_sync_blocks as load
    return load(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)


def load_stage13_multiradio_packages(*,manifest_path,expected_manifest_sha256):
    from orchestration.autoresearch.fmx_stage13_sync import load_stage13_multiradio_packages as load
    return load(manifest_path=manifest_path,expected_manifest_sha256=expected_manifest_sha256)
