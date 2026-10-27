#!/usr/bin/env python3
"""Finite bandwidth/edge-interference sensitivity, not a new VHT40 benchmark."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from tools.sim import stage787_792_common as h
c=h.c
SCRIPT='tools/sim/run_stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.py'
OUT='artifacts/autoresearch/stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.json'
DOC='docs/STAGE787A_WA_VHT20_78MBPS_VS_VHT40_CHANNEL_EFFICIENCY_SIM.md'
SOURCE='artifacts/autoresearch/stage676a_live_wa_77round_312window_milestone_r74_77.json'
PRODUCER='tools/bench/run_stage676a_live_wa_77round_312window_milestone_r74_77.py'
MEASURE='tools/benchmarks/run_stage311a_to_316a_wa_megamission.py'
SOURCES=(SOURCE,PRODUCER,MEASURE,'docs/STAGE676A_LIVE_WA_77ROUND_312WINDOW_MILESTONE_R74_77.md')
DOC_TEXT='''<!-- doc-head: Stage787A saved VHT20 anchor and conditional VHT40 edge-interference sensitivity -->
78.513Mbps is a selected saved window; bandwidth scaling and interference are assumptions.
<!-- /doc-head -->

# Stage787A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN, forward-plan reproducibility.
Run `python tools/sim/run_stage787a_wa_vht20_78mbps_vs_vht40_channel_efficiency_sim.py`.
Inputs are frozen on first run and reused byte-for-byte; producer files are text only.
No radio, network, target code, RF load, channel/configuration or firmware is executed.

## Saved anchor and units

676 /rounds[S676A-R77]/windows[B1] reports78.513Mbps over3.844s, with
41.041DL +33.918UL +3.430IPTV +0.124VoIP =78.513Mbps, OTA byte rate71.024.
The held measurement helper takes max(application sum, OTA byte rate); it does
not consistently define application-only goodput across all windows. Parse/default
and native acquisition provenance are not authenticated by current producer bytes.
R77 B2 reports74.578; the two-B arithmetic mean is76.5455Mbps. The selected B1
peak is neither a long-run average nor an independent replication distribution.
20MHz is a saved document/profile premise; per-window iw width readback is absent.

78.513Mbps /20MHz =3.92565 bit/s/Hz. Rounded to two decimals this is3.93,
not3.92; requested78.51 gives3.9255. Rates are aggregate bidirectional composite
service per nominal channel width, not PHY constellation or spatial-stream efficiency.

## Prespecified finite sensitivity

R=78.513 reference Mbps. For b20 in{0,.2,.5}, incremental edge busy fraction
e in{0,.1,.3,.5,.8}, and clean40/20 multiplier k in{1,1.5,2}:
G20=R*(1-b20); b40=min(1,b20+e); G40=R*k*(1-b40).
Efficiency is G/nominal_width_MHz. Forty-five assumption cells compare two widths.
Each cell gets an exact two-objective Pareto set (maximize G and G/width).
Do not pool different interference cells as if they were alternative controls.
G40>G20 iff b40<1-(1-b20)/k. Efficiency40>efficiency20 requires
k*(1-b40)>2*(1-b20). For k<=2 and b40>=b20,40MHz never has greater efficiency.

These busy fractions/multipliers are illustrative, not measured FFT occupancy,
PER, interference statistics, CPU headroom or equal-EIRP PHY scaling. No SimPy
queue or NSGA search is needed for this fully enumerated algebraic grid.
Noise-bandwidth/power-density, retries, hidden nodes, MAC scheduling and latency
are omitted. k=2 is a hypothetical scaling endpoint, not a guaranteed40MHz gain.
No confidence interval is invented from two B-windows or grid cells.
KEEP the sensitivity tool; physical width/interference superiority remains UNKNOWN.
The JSON includes exact pointers, arithmetic, assumptions and qualified boundaries.
'''


def anchor(receipt):
    rounds=receipt['rounds'];matches=[r for r in rounds if r.get('round_id')=='S676A-R77']
    if len(matches)!=1:raise ValueError('unique_R77_required')
    windows=matches[0]['windows']
    if [w['window']for w in windows]!=['A1','B1','A2','B2']:raise ValueError('ABAB_window_order')
    rows=[]
    for w in windows:
        rates={k:c.finite(w[k],k,0,1000)for k in ('goodput_mbps','tcp_dl_mbps','tcp_ul_mbps','iptv_mbps','voip_mbps','ota_wire_air_mbps')}
        app=sum(rates[k]for k in ('tcp_dl_mbps','tcp_ul_mbps','iptv_mbps','voip_mbps'))
        rows.append(dict(window=w['window'],reported_mbps=rates['goodput_mbps'],application_sum_mbps=app,
            ota_mbps=rates['ota_wire_air_mbps'],expected_max_mbps=round(max(app,rates['ota_wire_air_mbps']),3),
            metric_consistent=abs(rates['goodput_mbps']-round(max(app,rates['ota_wire_air_mbps']),3))<.0001,
            elapsed_s=c.finite(w['elapsed_s'],'elapsed_s',.001,300)))
    b=[r for r in rows if r['window'].startswith('B')];peak=max(b,key=lambda r:r['reported_mbps'])
    return dict(pointer='/rounds/3/windows/1',round_id='S676A-R77',peak_window=peak['window'],
        peak_reported_mbps=peak['reported_mbps'],peak_efficiency_bps_hz=peak['reported_mbps']/20,
        b_mean_mbps=sum(x['reported_mbps']for x in b)/2,windows=rows,
        nominal_width_mhz=20,width_readback_proven=False,reported_requested_mbps=78.51)


def compare(reference_mbps,busy20,edge_busy,clean_multiplier):
    r=c.finite(reference_mbps,'reference_mbps',.001,1000)
    b=c.finite(busy20,'busy20',0,1);e=c.finite(edge_busy,'edge_busy',0,1)
    k=c.finite(clean_multiplier,'clean_multiplier',1,2);b40=min(1,b+e)
    rows=[]
    for width,gp in ((20,r*(1-b)),(40,r*k*(1-b40))):
        rows.append(dict(width_mhz=width,goodput_mbps=gp,efficiency_bps_hz=gp/width,
                         minus_goodput=-gp,minus_efficiency=-gp/width))
    return dict(busy20=b,edge_busy=e,busy40=b40,clean_multiplier=k,rows=rows,
                frontier_indices=h.pareto(rows,('minus_goodput','minus_efficiency')),
                throughput_break_even_busy40=1-(1-b)/k)


def build(root=ROOT):
    payloads,sources=h.freeze(root,787,SOURCES);a=anchor(h.json_source(payloads[SOURCE]))
    text=payloads[MEASURE].decode('utf-8')
    if 'max(app_mbps, ota_mbps)' not in text:raise ValueError('held_measurement_semantics_changed')
    cells=[compare(a['peak_reported_mbps'],b,e,k)for b in (0,.2,.5)for e in (0,.1,.3,.5,.8)for k in (1,1.5,2)]
    return h.finish(root,787,SCRIPT,OUT,DOC,DOC_TEXT,dict(status='QUALIFIED_OFFLINE_SENSITIVITY_MODEL',
        claim_classification='INFERRED_CONDITIONAL_MODEL',attribution='external controller / offline analyst',
        saved_anchor=a,cells=cells,model=dict(method='EXACT_FINITE_GRID',cells=45,randomness='NONE',
            empirical_calibration=False,physical_gain_accepted=False),
        gaps=['No native width/interference trace or matched VHT40 treatment.',
              'Saved peak is not the treatment mean; max(app,OTA) is not a uniform payload metric.']),sources)


if __name__=='__main__':raise SystemExit(h.cli(build))
