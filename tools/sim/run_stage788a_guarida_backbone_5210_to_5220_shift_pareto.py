#!/usr/bin/env python3
"""Two-ray channel-shift sensitivity; no real backbone change is authorized."""
from pathlib import Path
import math
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
c=h.c
SCRIPT='tools/sim/run_stage788a_guarida_backbone_5210_to_5220_shift_pareto.py'
OUT='artifacts/autoresearch/stage788a_guarida_backbone_5210_to_5220_shift_pareto.json'
DOC='docs/STAGE788A_GUARIDA_BACKBONE_5210_TO_5220_SHIFT_PARETO.md'
SOURCE='artifacts/autoresearch/stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.json'
MODEL='tools/sim/run_stage457a_guarida_backbone_60_61_notch_mitigation_pareto.py'
PRODUCER='tools/observability/audit_stage737a_guarida_backbone_60_61_ampdu_and_shift_preflight.py'
SOURCES=(SOURCE,PRODUCER,MODEL,'artifacts/autoresearch/stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json')
DOC_TEXT='''<!-- doc-head: Stage788A conditional5210-to5220MHz two-ray shift Pareto and missing counter provenance -->
The +10MHz decision is a scenario;209.5M subframes and zero-outage gains are not validated.
<!-- /doc-head -->

# Stage788A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/sim/run_stage788a_guarida_backbone_5210_to_5220_shift_pareto.py`.
No channel command, SSH, RF acquisition, firmware or producer is executed.
SG-01 backbone and PoE switches remain untouched. This emits no operational commands.

## Evidence reconciliation

737 /backbone_telemetry and /expected_shift_outcome are saved synthesis fields.
Its producer constructs a literal dictionary and a preflight checklist marked PASS;
38.64dB,98.8% MCS8,+17.17Mbps and0s outage are expected/synthetic claims, not a
native before/after channel-shift measurement. The held457 simulation hardcodes
a50ns excess-delay premise and calls its baseline5705MHz. That cannot confirm
the requested physical baseline5210MHz, regulatory availability or actual center.
454 has saved EVM summaries; no calibrated transfer function or excess-delay fit.

The requested209,500,000 A-MPDU subframes has no native counter/source pointer
in these scoped inputs. It remains an UNLINKED_OPERATOR_PREMISE, not209.5M
independent trials, PPDU count, measured errors or post-shift evidence.737 instead
declares91,730,000 DL frames and3.92 MPDUs/A-MPDU PPDU without a common reset
epoch/cohort. Those quantities cannot be multiplied into the requested total.
Current absolute link frequency and authenticated acquisition chain remain UNKNOWN.

## Prespecified finite model

H(delta_f,x)=1+rho*exp(i*(phi+2*pi*(delta_f+x)*tau)). x spans[-10,+10]MHz.
For rho={0,.5,.9}, tau={0,25,50,100}ns, phi={0,pi/2,pi}, and SNR={10,20}dB,
compare center5210(stay) vs5220(+10) with assumed switch pauses{0,1,5}s.
There are216 cells, two choices per cell. No state is fitted to a desired winner.
Composite Simpson201 samples integrate log2(1+SNR_linear*abs(H)^2) per Hz.
This is an idealized frequency-selective AWGN capacity density with constant PSD,
not net WA throughput, EVM, MCS selection, latency or a calibrated RF forecast.
Effective density multiplies by(600-pause_s)/600 over an illustrative600s horizon.
Each cell's exact Pareto set maximizes effective density and minimizes pause.
Do not optimize across mutually incompatible unknown channel states.

The analytical mean power1+rho^2+2*rho*cos(phi+2*pi*delta_f*tau)*sinc(B*tau)
checks integration units. A physical spectral null stays at its absolute frequency;
shifting a20MHz window by10MHz retains50% passband overlap. It need not remove
the null, and the same shift can improve, worsen or leave modeled capacity equal.
Subcarrier51 is a saved array index; its vendor absolute-frequency map is unproven.
No assumption fixes multipath to be the actual notch cause or promises zero outage.
Channel legality/DFS/CAC/EIRP, real CSA support, remote coordination and recovery
remain unassessed. No regulatory constraints are waived by a Pareto label.
KEEP the bounded sensitivity; an actual shift remains NOT_APPROVED/UNKNOWN.
'''


def channel(delta_mhz,rho,tau_ns,phase,snr_db,width_mhz=20,points=201):
    d=c.finite(delta_mhz,'delta_mhz',-10,10);r=c.finite(rho,'rho',0,.99)
    tau=c.finite(tau_ns,'tau_ns',0,1000)*1e-9;phase=c.finite(phase,'phase',0,2*math.pi)
    snr=10**(c.finite(snr_db,'snr_db',-20,60)/10);width=c.finite(width_mhz,'width',1,40)*1e6
    c.integer(points,'points',3,2001)
    if points%2!=1:raise ValueError('odd_Simpson_points_required')
    powers=[];caps=[]
    for i in range(points):
        offset=-width/2+width*i/(points-1)
        gain=1+r*r+2*r*math.cos(phase+2*math.pi*(d*1e6+offset)*tau)
        powers.append(gain);caps.append(math.log1p(snr*gain)/math.log(2))
    integrate=lambda a:(a[0]+a[-1]+4*sum(a[1:-1:2])+2*sum(a[2:-1:2]))/(3*(points-1))
    z=math.pi*width*tau;sinc=math.sin(z)/z if z else 1
    return dict(capacity_density_bps_hz=integrate(caps),numerical_mean_power=integrate(powers),
        analytical_mean_power=1+r*r+2*r*math.cos(phase+2*math.pi*d*1e6*tau)*sinc,
        delta_mhz=d,rho=r,tau_ns=tau_ns,phase_rad=phase,snr_db=snr_db,points=points)


def compare(rho,tau_ns,phase,snr_db,pause_s,horizon_s=600):
    horizon=c.finite(horizon_s,'horizon_s',.001,1e6);pause=c.finite(pause_s,'pause_s',0,horizon)
    rows=[]
    for center,cost in ((5210,0),(5220,pause)):
        prediction=channel(center-5210,rho,tau_ns,phase,snr_db)
        effective=prediction['capacity_density_bps_hz']*(1-cost/horizon)
        rows.append(dict(center_mhz=center,pause_s=cost,effective_density_bps_hz=effective,
            minus_density=-effective,channel=prediction,regulatory_feasibility='UNKNOWN'))
    return dict(rho=rho,tau_ns=tau_ns,phase_rad=phase,snr_db=snr_db,assumed_shift_pause_s=pause,
                horizon_s=horizon,rows=rows,frontier_indices=h.pareto(rows,('minus_density','pause_s')))


def build(root=ROOT):
    payloads,sources=h.freeze(root,788,SOURCES);r=h.json_source(payloads[SOURCE])
    ap=r['backbone_telemetry']['almafuerte_60_ap'];sta=r['backbone_telemetry']['guarida_61_sta']
    cells=[compare(rho,tau,phase,snr,pause)for rho in (0,.5,.9)for tau in (0,25,50,100)
           for phase in (0,math.pi/2,math.pi)for snr in (10,20)for pause in (0,1,5)]
    differences=[x['rows'][1]['channel']['capacity_density_bps_hz']-x['rows'][0]['channel']['capacity_density_bps_hz']for x in cells]
    evidence=dict(requested_subframes=209500000,subframe_provenance='UNLINKED_OPERATOR_PREMISE',
        native_subframe_pointer=None,independent_trials=None,reported_dl_frames=ap['dl_total_frames'],
        reported_mpdus_per_ampdu_ppdu=sta['mean_mpdus_per_ampdu_ppdu'],
        saved737_expected_shift_outcome=r['expected_shift_outcome'],
        requested_centers_mhz=[5210,5220],held457_documented_baseline_mhz=5705,
        actual_current_centers_verified=False,saved737_source_is_literal_synthesis='backbone_telemetry = {' in payloads[PRODUCER].decode('utf-8'))
    return h.finish(root,788,SCRIPT,OUT,DOC,DOC_TEXT,dict(status='QUALIFIED_OFFLINE_SHIFT_SENSITIVITY',
        claim_classification='INFERRED_CONDITIONAL_MODEL',attribution='external controller / offline analyst',
        evidence=evidence,cells=cells,model=dict(method='EXACT_FINITE_GRID_SIMPSON_201',cells=len(cells),
            empirical_calibration=False,modelled_shift_can_improve=any(d>1e-8 for d in differences),
            modelled_shift_can_worsen=any(d< -1e-8 for d in differences)),
        missing_evidence=['Native209.5M counter/cohort/epoch source.','Calibrated channel response and actual centers.',
                         'Matched guarded before/after shift and outage traces; no shift authorized.']),sources)


if __name__=='__main__':raise SystemExit(h.cli(build))
